"""Corpus expansion crawler (#32) — against an in-memory fake site."""

import json
from pathlib import Path

import pytest

from nutrime.recipes.crawl import (
    CrawlConfigError,
    CrawlSource,
    CrawlState,
    crawl_source,
    crawl_sources,
    load_sources,
)
from nutrime.recipes.jsonld import convert_recipe_node
from nutrime.recipes.search import SearchFilters, search, source_collection
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer

SITE = "https://kitchen.example"


def _recipe_page(name: str) -> str:
    node = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": name,
        "recipeIngredient": ["2 cups rice", "1 onion"],
        "recipeInstructions": [
            {"@type": "HowToStep", "text": "Fry the onion until soft."},
            {"@type": "HowToStep", "text": "Add the rice and cook through."},
        ],
        "recipeYield": "4",
    }
    return (
        "<html><head><script type='application/ld+json'>"
        + json.dumps(node) + "</script></head><body></body></html>"
    )


def _site(robots: str | None = "User-agent: *\nDisallow: /recipes/secret\n"):
    pages = {
        f"{SITE}/sitemap_index.xml": (
            "<?xml version='1.0'?><sitemapindex xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
            f"<sitemap><loc>{SITE}/sitemap-recipes.xml</loc></sitemap>"
            "<sitemap><loc>https://elsewhere.example/sitemap.xml</loc></sitemap>"
            "</sitemapindex>"
        ),
        f"{SITE}/sitemap-recipes.xml": (
            "<?xml version='1.0'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
            + "".join(
                f"<url><loc>{SITE}{path}</loc></url>"
                for path in (
                    "/recipes/fried-rice", "/recipes/pilaf", "/recipes/risotto",
                    "/recipes/secret", "/recipes/not-a-recipe", "/about",
                )
            )
            + "</urlset>"
        ),
        f"{SITE}/recipes/fried-rice": _recipe_page("Fried Rice"),
        f"{SITE}/recipes/pilaf": _recipe_page("Pilaf"),
        f"{SITE}/recipes/risotto": _recipe_page("Risotto"),
        f"{SITE}/recipes/secret": _recipe_page("Secret"),
        f"{SITE}/recipes/not-a-recipe": "<html><body>Just a blog post</body></html>",
        f"{SITE}/about": "<html>about</html>",
    }
    if robots is not None:
        pages[f"{SITE}/robots.txt"] = robots
    fetched: list[str] = []

    def fetch(url: str) -> str:
        fetched.append(url)
        if url not in pages:
            raise OSError(f"404 {url}")
        return pages[url]

    return fetch, fetched


SOURCE = CrawlSource(
    key="kitchen", name="Example Kitchen",
    seeds=(f"{SITE}/sitemap_index.xml",), include=r"^/recipes/", max_pages=50,
    delay_s=2,
)


@pytest.fixture
def vault(tmp_path: Path) -> RecipeVault:
    v = RecipeVault(tmp_path / "corpus")
    v.ensure()
    return v


def _pacer():
    sleeps: list[float] = []
    return Pacer(delay_s=0, sleep=sleeps.append), sleeps


def test_crawl_writes_attributed_web_recipes(vault) -> None:
    fetch, fetched = _site()
    pacer, sleeps = _pacer()
    outcome = crawl_source(vault, SOURCE, fetcher=fetch, pacer=pacer)
    titles = sorted(r.frontmatter["title"] for r in vault.iter_recipes())
    assert titles == ["Fried Rice", "Pilaf", "Risotto"]
    assert outcome.written == 3 and outcome.not_recipes == 1
    assert outcome.blocked_by_robots == 1
    # robots-disallowed and out-of-scope pages were never fetched
    assert f"{SITE}/recipes/secret" not in fetched
    assert f"{SITE}/about" not in fetched
    assert not any("elsewhere.example" in u for u in fetched)
    rec = next(vault.iter_recipes())
    attribution = rec.frontmatter["attribution"]
    assert attribution["source_name"] == "Example Kitchen"
    assert attribution["source_url"].startswith(SITE)
    assert source_collection(rec.frontmatter) == "web"
    # paced: one wait between each pair of recipe-page fetches, at >= delay_s
    assert len(sleeps) == 3 and all(s >= 2 for s in sleeps)


def test_robots_crawl_delay_raises_pace(vault) -> None:
    fetch, _ = _site(robots="User-agent: *\nCrawl-delay: 9\n")
    pacer, sleeps = _pacer()
    crawl_source(vault, SOURCE, fetcher=fetch, pacer=pacer)
    assert sleeps and all(s == 9 for s in sleeps)


def test_unreadable_robots_means_no_crawl(vault) -> None:
    fetch, fetched = _site(robots=None)
    outcome = crawl_source(vault, SOURCE, fetcher=fetch, pacer=_pacer()[0])
    assert outcome.written == 0 and outcome.discovered == 0
    assert fetched == [f"{SITE}/robots.txt"]


def test_budget_and_resume(vault, tmp_path: Path) -> None:
    fetch, _ = _site()
    state_path = tmp_path / "state.json"
    [first] = crawl_sources(vault, [SOURCE], state_path, fetcher=fetch,
                            pacer=_pacer()[0], max_pages=2)
    assert first.written == 2 and first.budget_exhausted
    [second] = crawl_sources(vault, [SOURCE], state_path, fetcher=fetch,
                             pacer=_pacer()[0], max_pages=10)
    assert second.written == 1
    assert second.already_known == 2
    # the non-recipe page is remembered and not refetched a third time
    [third] = crawl_sources(vault, [SOURCE], state_path, fetcher=fetch,
                            pacer=_pacer()[0])
    assert third.fetched == 0
    assert "kitchen" in CrawlState.load(state_path).tried


def test_page_already_pinned_is_not_crawled_again(vault) -> None:
    from nutrime.recipes.jsonld import extract_recipe_jsonld

    url = f"{SITE}/recipes/pilaf/"
    pinned = convert_recipe_node(
        extract_recipe_jsonld(_recipe_page("Pilaf")), source_url=url
    )
    vault.write(pinned.recipe_id, pinned.frontmatter, pinned.cooklang_body)
    fetch, fetched = _site()
    outcome = crawl_source(vault, SOURCE, fetcher=fetch, pacer=_pacer()[0])
    assert f"{SITE}/recipes/pilaf" not in fetched
    assert outcome.already_known == 1


def test_dry_run_fetches_no_recipe_pages(vault) -> None:
    fetch, fetched = _site()
    outcome = crawl_source(vault, SOURCE, fetcher=fetch, pacer=_pacer()[0],
                           dry_run=True)
    assert outcome.fetched == 4 and outcome.written == 0
    assert not any("/recipes/" in u for u in fetched)
    assert list(vault.iter_recipes()) == []


def test_crawled_recipes_searchable_and_render_credit(vault) -> None:
    fetch, _ = _site()
    crawl_source(vault, SOURCE, fetcher=fetch, pacer=_pacer()[0])
    results = search(vault, SearchFilters(sources=frozenset({"web"})))
    assert len(results) == 3
    assert all("Example Kitchen" in r.attribution for r in results)
    assert all(SITE in r.attribution for r in results)


class TestSourcesConfig:
    def test_missing_file_falls_back_to_bundled_defaults(self, tmp_path: Path) -> None:
        sources = load_sources(tmp_path / "crawl_sources.toml")
        assert "allrecipes" in sources and "pinterest_top" in sources
        assert sources["pinterest_top"].kind == "pinterest"
        # bot-blocking / paywalled sites are never on the list
        hosts = {h for src in sources.values() for h in src.hosts}
        assert not {"cooking.nytimes.com", "nytimes.com", "americastestkitchen.com"} & hosts

    def test_disabled_entries_dropped_and_kind_validated(self, tmp_path: Path) -> None:
        path = tmp_path / "crawl_sources.toml"
        path.write_text(
            '[[source]]\nkey = "a"\nseeds = ["https://a.example/"]\nenabled = false\n'
            '[[source]]\nkey = "b"\nseeds = ["https://b.example/"]\n'
        )
        assert list(load_sources(path)) == ["b"]
        path.write_text('[[source]]\nkey = "c"\nseeds = ["https://c.example/"]\nkind = "magic"\n')
        with pytest.raises(CrawlConfigError):
            load_sources(path)

    def test_parse_and_floor_delay(self, tmp_path: Path) -> None:
        path = tmp_path / "crawl_sources.toml"
        path.write_text(
            '[[source]]\nkey = "k"\nname = "K"\nseeds = ["https://k.example/s.xml"]\n'
            'include = "/r/"\nmax_pages = 3\ndelay_s = 0.1\n'
        )
        src = load_sources(path)["k"]
        assert src.max_pages == 3 and src.delay_s == 1.0  # floor: 1 s
        assert src.in_scope("https://www.k.example/r/x")
        assert not src.in_scope("https://k.example/blog/x")

    def test_bad_regex_rejected(self, tmp_path: Path) -> None:
        path = tmp_path / "crawl_sources.toml"
        path.write_text('[[source]]\nkey = "k"\nseeds = ["https://k.example"]\ninclude = "("\n')
        with pytest.raises(CrawlConfigError):
            load_sources(path)


def test_cli_lists_bundled_defaults(tmp_path: Path, capsys) -> None:
    from nutrime.cli import main

    rc = main(["recipes", "crawl", "--list", "--data-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "bundled default list" in out and "pinterest_top" in out


# -- robots-advertised sitemaps -------------------------------------------------


def test_root_seed_uses_recipe_sitemaps_from_robots(vault) -> None:
    pages = {
        "https://blog.example/robots.txt": (
            "User-agent: *\nAllow: /\n"
            "Sitemap: https://blog.example/post-sitemap.xml\n"
            "Sitemap: https://blog.example/wprm_recipe-sitemap.xml\n"
        ),
        "https://blog.example/wprm_recipe-sitemap.xml": (
            "<?xml version='1.0'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
            "<url><loc>https://blog.example/lemon-pasta/</loc></url></urlset>"
        ),
        "https://blog.example/post-sitemap.xml": "<?xml version='1.0'?><urlset/>",
        "https://blog.example/lemon-pasta/": _recipe_page("Lemon Pasta"),
    }
    fetched: list[str] = []

    def fetch(url):
        fetched.append(url)
        if url not in pages:
            raise OSError(url)
        return pages[url]

    source = CrawlSource(key="blog", name="Blog", seeds=("https://blog.example/",))
    outcome = crawl_source(vault, source, fetcher=fetch, pacer=_pacer()[0])
    assert outcome.written == 1
    assert "https://blog.example/post-sitemap.xml" not in fetched  # recipe maps preferred


# -- Pinterest discovery ----------------------------------------------------------

PIN_PAGE = "https://www.pinterest.com/ideas/food-and-drink/1/"


def _pinterest_site(pinterest_robots: str):
    pin_json = json.dumps({"resource": {"data": [
        {"id": "1", "link": "https://cooks.example/recipes/tacos/"},
        {"id": "2", "link": "https://closed.example/recipes/stew/"},
        {"id": "3", "link": "https://www.instagram.com/p/xyz/"},
        {"id": "4", "link": "https://cooks.example/recipes/tacos/"},
    ]}}).replace("/", "\\/")
    pages = {
        "https://www.pinterest.com/robots.txt": pinterest_robots,
        PIN_PAGE: f"<html><script id='__PWS_DATA__'>{pin_json}</script></html>",
        "https://cooks.example/robots.txt": "User-agent: *\nAllow: /\n",
        "https://cooks.example/recipes/tacos/": _recipe_page("Tacos"),
        "https://closed.example/robots.txt": "User-agent: *\nDisallow: /\n",
        "https://closed.example/recipes/stew/": _recipe_page("Stew"),
    }
    fetched: list[str] = []

    def fetch(url):
        fetched.append(url)
        if url not in pages:
            raise OSError(url)
        return pages[url]

    return fetch, fetched


PIN_SOURCE = CrawlSource(
    key="pinterest_top", name="Pinterest top food pins", seeds=(PIN_PAGE,),
    kind="pinterest",
)


def test_pinterest_pins_lead_to_original_sites(vault) -> None:
    fetch, fetched = _pinterest_site("User-agent: *\nAllow: /ideas/\n")
    outcome = crawl_source(vault, PIN_SOURCE, fetcher=fetch, pacer=_pacer()[0])
    assert outcome.written == 1
    assert outcome.blocked_by_robots == 1          # closed.example disallows
    assert "https://closed.example/recipes/stew/" not in fetched
    assert not any("instagram" in u for u in fetched)
    rec = next(vault.iter_recipes())
    assert source_collection(rec.frontmatter) == "pinterest_top"
    attribution = rec.frontmatter["attribution"]
    assert attribution["source_name"] == "cooks.example (via Pinterest)"
    assert attribution["source_url"] == "https://cooks.example/recipes/tacos/"
    assert "Pinterest" in attribution["source_license"]


def test_pinterest_robots_disallow_means_nothing_fetched(vault) -> None:
    fetch, fetched = _pinterest_site("User-agent: *\nDisallow: /\n")
    outcome = crawl_source(vault, PIN_SOURCE, fetcher=fetch, pacer=_pacer()[0])
    assert outcome.listings_blocked == 1 and outcome.listings_fetched == 0
    assert outcome.written == 0
    assert PIN_PAGE not in fetched


def test_pinterest_top_is_its_own_search_facet(vault) -> None:
    fetch, _ = _pinterest_site("User-agent: *\nAllow: /\n")
    crawl_source(vault, PIN_SOURCE, fetcher=fetch, pacer=_pacer()[0])
    from nutrime.recipes.search import SOURCE_LABELS

    assert SOURCE_LABELS["pinterest_top"] == "Pinterest top pins"
    assert len(search(vault, SearchFilters(sources=frozenset({"pinterest_top"})))) == 1
    assert search(vault, SearchFilters(sources=frozenset({"pins"}))) == []
