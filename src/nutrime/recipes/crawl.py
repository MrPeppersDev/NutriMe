"""Corpus expansion crawler (issue #32, direction reset item 7).

Crawls public recipe sites the household chooses, extracts schema.org
Recipe JSON-LD through the existing adapter, and writes each page as a
recipe in its own collection ("web" — distinct from the household's own
saved pins and from the curated public-health sources, so the source
facet keeps them apart).

Politeness and safety, all non-negotiable:

- **robots.txt** is fetched per host and obeyed for our User-Agent; a
  ``Crawl-delay`` raises the pause between requests (never lowers it).
  An unreadable robots.txt means *don't crawl that host*.
- **Pacing** — one request at a time, at least ``delay_s`` apart.
- **SSRF guard** — every fetch goes through ``check_url_safety``.
- **Scope** — only URLs on the source's own hosts and matching its
  include pattern are ever fetched.
- **Budget** — ``max_pages`` caps fetches per run; state is saved so the
  next run resumes where this one stopped.

Attribution + link-back (#23): every crawled recipe stores the site name
and page URL, and every render surface shows them. Crawled pages are
the publishers' copyrighted work, kept for household use with a link to
the original — not redistributed.

Sources (household decision 2026-10-06): crawl the major public recipe
sites that allow third-party bots, plus Pinterest's top food pins. The
bundled list is ``default_crawl_sources.toml``; "allows bots" is decided
at run time by each site's own robots.txt, never by this list — a site
that disallows NutriMe is skipped and reported, every run. Sites known
to forbid bots or paywall recipes (NYT Cooking, America's Test Kitchen)
are not listed at all. A household ``<data_dir>/crawl_sources.toml``
replaces the bundled list entirely.

Pinterest is a *discovery* source (``kind = "pinterest"``): its public
food pages are read for pins' outbound links, and the recipe itself is
fetched from the original site — robots.txt checked on Pinterest AND on
every destination host. These land in their own collection ("Pinterest
top pins"), distinct from the household's own saved pins. No robots
bypass exists here: if Pinterest's robots.txt disallows NutriMe, the run
says so and fetches nothing from Pinterest.
"""

from __future__ import annotations

import json
import re
import tomllib
import urllib.parse
import urllib.robotparser
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from nutrime.recipes.jsonld import (
    INGESTION_METHOD as PINS_METHOD,
)
from nutrime.recipes.jsonld import (
    convert_recipe_node,
    extract_recipe_jsonld,
    normalize_url,
)
from nutrime.recipes.web import (
    USER_AGENT,
    Pacer,
    TextFetcher,
    _urllib_fetch_text,
)

INGESTION_METHOD = "crawl_jsonld_v1"
PINTEREST_TOP_METHOD = "pinterest_top_jsonld_v1"
DEFAULT_SOURCES_PATH = Path(__file__).with_name("default_crawl_sources.toml")
# Hosts a Pinterest pin may link to that are never recipe pages.
_NON_RECIPE_HOSTS = frozenset({
    "pinterest.com", "pin.it", "instagram.com", "facebook.com", "youtube.com",
    "youtu.be", "tiktok.com", "twitter.com", "x.com", "amazon.com", "etsy.com",
})
SOURCE_LICENSE = (
    "© the publisher — crawled for household use; attribution and"
    " link-back shown, not redistributed"
)
DEFAULT_DELAY_S = 5.0
STATE_FILE = "crawl_state.json"
SOURCES_FILE = "crawl_sources.toml"



class CrawlConfigError(ValueError):
    """crawl_sources.toml is missing, malformed, or names an unknown key."""


@dataclass(frozen=True)
class CrawlSource:
    key: str
    name: str
    seeds: tuple[str, ...]
    include: str = r"."
    max_pages: int = 50
    delay_s: float = DEFAULT_DELAY_S
    kind: str = "site"  # "site" | "pinterest"

    @property
    def hosts(self) -> frozenset[str]:
        return frozenset(
            urllib.parse.urlparse(s).netloc.lower().removeprefix("www.")
            for s in self.seeds
        )

    def in_scope(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.netloc.lower().removeprefix("www.")
        if self.kind == "pinterest":
            # Candidates are the pins' destinations: any other site.
            base = ".".join(host.rsplit(".", 2)[-2:])
            return (
                bool(host)
                and host not in self.hosts
                and base not in _NON_RECIPE_HOSTS
                and not host.endswith(".pinterest.com")
            )
        if host not in self.hosts:
            return False
        return re.search(self.include, parsed.path) is not None


def load_sources(path: Path | None) -> dict[str, CrawlSource]:
    """The household's crawl_sources.toml when present, else the bundled
    defaults. ``enabled = false`` entries are dropped."""
    if path is None or not path.exists():
        path = DEFAULT_SOURCES_PATH
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise CrawlConfigError(f"{path}: {exc}") from exc
    sources: dict[str, CrawlSource] = {}
    for raw in data.get("source", []):
        try:
            key = str(raw["key"]).strip()
            seeds = tuple(str(s) for s in raw["seeds"])
            source = CrawlSource(
                key=key,
                name=str(raw.get("name") or key),
                seeds=seeds,
                include=str(raw.get("include") or "."),
                max_pages=int(raw.get("max_pages", 50)),
                delay_s=max(float(raw.get("delay_s", DEFAULT_DELAY_S)), 1.0),
                kind=str(raw.get("kind") or "site"),
            )
            re.compile(source.include)
            if source.kind not in ("site", "pinterest"):
                raise ValueError(f"kind must be 'site' or 'pinterest', not {source.kind!r}")
        except (KeyError, TypeError, ValueError, re.error) as exc:
            raise CrawlConfigError(f"{path}: bad [[source]] entry: {exc}") from exc
        if not key or not seeds:
            raise CrawlConfigError(f"{path}: every source needs a key and seeds")
        if raw.get("enabled", True) is False:
            continue
        sources[key] = source
    return sources


# -- robots -------------------------------------------------------------------


class RobotsCache:
    """Per-host robots.txt, fetched once. Unreadable → host refused."""

    def __init__(self, fetch: TextFetcher) -> None:
        self._fetch = fetch
        self._parsers: dict[str, urllib.robotparser.RobotFileParser | None] = {}

    def _parser(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        parsed = urllib.parse.urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._parsers:
            parser = urllib.robotparser.RobotFileParser()
            try:
                parser.parse(self._fetch(f"{origin}/robots.txt").splitlines())
            except Exception:  # noqa: BLE001 — can't read the rules: don't crawl
                parser = None
            self._parsers[origin] = parser
        return self._parsers[origin]

    def allowed(self, url: str) -> bool:
        parser = self._parser(url)
        return parser is not None and parser.can_fetch(USER_AGENT, url)

    def sitemaps(self, url: str) -> list[str]:
        parser = self._parser(url)
        return list(parser.site_maps() or []) if parser is not None else []

    def crawl_delay(self, url: str) -> float | None:
        parser = self._parser(url)
        if parser is None:
            return None
        delay = parser.crawl_delay(USER_AGENT)
        return float(delay) if delay is not None else None


# -- discovery ------------------------------------------------------------------

_HREF = re.compile(r"""<a\s[^>]*?href\s*=\s*["']([^"'#]+)""", re.I)


def _sitemap_locs(text: str) -> tuple[list[str], bool] | None:
    """(locs, is_index) for sitemap XML, None if the text is not a sitemap."""
    stripped = text.lstrip()
    if not stripped.startswith("<?xml") and "<urlset" not in stripped[:500] \
            and "<sitemapindex" not in stripped[:500]:
        return None
    try:
        root = ET.fromstring(stripped)
    except ET.ParseError:
        return None
    tag = root.tag.rsplit("}", 1)[-1]
    if tag not in ("urlset", "sitemapindex"):
        return None
    locs = [
        (el.text or "").strip()
        for el in root.iter()
        if el.tag.rsplit("}", 1)[-1] == "loc" and (el.text or "").strip()
    ]
    return locs, tag == "sitemapindex"


_PIN_LINK = re.compile(r'"link"\s*:\s*"(https?:[^"]+)"')


def _pin_links(text: str) -> list[str]:
    """Outbound links embedded in Pinterest page JSON (JSON-escaped)."""
    out = []
    for raw in _PIN_LINK.findall(text):
        try:
            out.append(json.loads(f'"{raw}"'))
        except json.JSONDecodeError:
            out.append(raw.replace("\\/", "/"))
    return out


def _prefer_recipe_maps(urls: list[str]) -> list[str]:
    """Big sites split sitemaps by type; follow the recipe ones if any."""
    recipe = [u for u in urls if "recipe" in u.lower()]
    return recipe or urls


@dataclass
class Discovery:
    candidates: list[str]
    listings_fetched: int = 0
    listings_blocked: int = 0


def discover(
    source: CrawlSource,
    fetch: TextFetcher,
    robots: RobotsCache,
    *,
    max_listing_pages: int = 20,
) -> Discovery:
    """Candidate recipe URLs from the source's seeds, in discovery order.

    A seed that is a site root ("https://site.example/") is expanded to the
    sitemaps its robots.txt advertises. Sitemaps, sitemap indexes (one
    level, recipe sitemaps preferred) and HTML index pages are read for
    links; Pinterest pages are read for pins' outbound links. Listing
    pages are only fetched when robots.txt allows; robots is re-checked
    per candidate page in crawl_source.
    """
    found: dict[str, None] = {}
    queue: list[str] = []
    for seed in source.seeds:
        if urllib.parse.urlparse(seed).path in ("", "/") and source.kind == "site":
            maps = robots.sitemaps(seed)
            queue.extend(_prefer_recipe_maps(maps) if maps else [seed])
        else:
            queue.append(seed)
    result = Discovery(candidates=[])
    while queue and result.listings_fetched < max_listing_pages:
        url = queue.pop(0)
        if not robots.allowed(url):
            result.listings_blocked += 1
            continue
        try:
            text = fetch(url)
        except Exception:  # noqa: BLE001 — a dead seed is skipped
            continue
        result.listings_fetched += 1
        sitemap = _sitemap_locs(text)
        if sitemap is not None:
            locs, is_index = sitemap
            if is_index:
                queue.extend(
                    loc for loc in _prefer_recipe_maps(locs) if _same_host(loc, source)
                )
            else:
                for loc in locs:
                    if source.in_scope(loc):
                        found.setdefault(loc, None)
            continue
        links = [urllib.parse.urljoin(url, h.strip()) for h in _HREF.findall(text)]
        if source.kind == "pinterest":
            links = _pin_links(text) + links
        for absolute in links:
            if source.in_scope(absolute):
                found.setdefault(absolute, None)
    result.candidates = list(found)
    return result


def _same_host(url: str, source: CrawlSource) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    return host in source.hosts


# -- state --------------------------------------------------------------------


@dataclass
class CrawlState:
    """Per-source URLs already tried (written or not a recipe), so a run
    resumes instead of re-fetching. Stored as JSON in the data dir."""

    tried: dict[str, set[str]] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "CrawlState":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls({k: set(v) for k, v in data.get("tried", {}).items()})

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps({"tried": {k: sorted(v) for k, v in self.tried.items()}},
                       indent=1),
            encoding="utf-8",
        )


# -- run ------------------------------------------------------------------------


@dataclass(frozen=True)
class CrawlOutcome:
    source: str
    discovered: int
    fetched: int
    written: int
    already_known: int
    not_recipes: int
    blocked_by_robots: int
    failures: tuple[tuple[str, str], ...] = ()
    budget_exhausted: bool = False
    listings_blocked: int = 0
    listings_fetched: int = 0


def _known_upstream_ids(vault) -> set[str]:
    """Normalized URLs already in the vault from any page-based source —
    a page the household pinned is never crawled in twice."""
    seen: set[str] = set()
    for record in vault.iter_recipes():
        attribution = record.frontmatter.get("attribution", {}) or {}
        if attribution.get("ingestion_method") in (
            PINS_METHOD, INGESTION_METHOD, PINTEREST_TOP_METHOD
        ):
            for key in ("upstream_id", "source_url"):
                value = attribution.get(key) or ""
                if value:
                    seen.add(normalize_url(value))
    return seen


def crawl_source(
    vault,
    source: CrawlSource,
    *,
    state: CrawlState | None = None,
    fetcher: TextFetcher | None = None,
    pacer: Pacer | None = None,
    max_pages: int | None = None,
    dry_run: bool = False,
    on_page: Callable[[str, str], None] | None = None,
) -> CrawlOutcome:
    """One budgeted, polite pass over a source. ``on_page(url, result)``
    reports progress ("written" / "known" / "not a recipe" / "robots" /
    "failed: …" / "would fetch")."""
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    state = state if state is not None else CrawlState()
    robots = RobotsCache(fetch)
    budget = max_pages if max_pages is not None else source.max_pages

    found = discover(source, fetch, robots)
    candidates = found.candidates
    tried = state.tried.setdefault(source.key, set())
    known = _known_upstream_ids(vault)

    delay = source.delay_s
    if candidates:
        robots_delay = robots.crawl_delay(candidates[0])
        if robots_delay is not None:
            delay = max(delay, robots_delay)
    pacer = pacer or Pacer(delay_s=delay)
    pacer.delay_s = max(pacer.delay_s, delay)  # never faster than allowed

    fetched = written = already = not_recipes = blocked = 0
    failures: list[tuple[str, str]] = []
    report = on_page or (lambda url, result: None)
    exhausted = False
    first = True
    for url in candidates:
        key = normalize_url(url)
        if key in known or key in tried:
            already += 1
            report(url, "known")
            continue
        if not robots.allowed(url):
            blocked += 1
            report(url, "robots")
            continue
        if fetched >= budget:
            exhausted = True
            break
        if dry_run:
            fetched += 1
            report(url, "would fetch")
            continue
        if not first:
            pacer.wait()
        first = False
        fetched += 1
        try:
            html_text = fetch(url)
        except Exception as exc:  # noqa: BLE001 — report and continue
            failures.append((url, str(exc)))
            report(url, f"failed: {exc}")
            continue
        tried.add(key)
        node = extract_recipe_jsonld(html_text)
        if node is None:
            not_recipes += 1
            report(url, "not a recipe")
            continue
        if source.kind == "pinterest":
            host = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
            converted = convert_recipe_node(
                node,
                source_url=url,
                ingestion_method=PINTEREST_TOP_METHOD,
                source_license=SOURCE_LICENSE + "; found via Pinterest top food pins",
                source_name=f"{host} (via Pinterest)",
            )
        else:
            converted = convert_recipe_node(
                node,
                source_url=url,
                ingestion_method=INGESTION_METHOD,
                source_license=SOURCE_LICENSE,
                source_name=source.name,
            )
        vault.write(
            converted.recipe_id, converted.frontmatter, converted.cooklang_body
        )
        known.add(key)
        written += 1
        report(url, "written")
    return CrawlOutcome(
        source=source.key,
        discovered=len(candidates),
        fetched=fetched,
        written=written,
        already_known=already,
        not_recipes=not_recipes,
        blocked_by_robots=blocked,
        failures=tuple(failures),
        budget_exhausted=exhausted,
        listings_blocked=found.listings_blocked,
        listings_fetched=found.listings_fetched,
    )


def crawl_sources(
    vault,
    sources: Iterable[CrawlSource],
    state_path: Path,
    **kwargs,
) -> list[CrawlOutcome]:
    state = CrawlState.load(state_path)
    outcomes = []
    for source in sources:
        outcomes.append(crawl_source(vault, source, state=state, **kwargs))
        if not kwargs.get("dry_run"):
            state.save(state_path)
    return outcomes
