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
    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(CrawlConfigError, match="no crawl sources"):
            load_sources(tmp_path / "crawl_sources.toml")

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


def test_cli_without_config_explains(tmp_path: Path, capsys) -> None:
    from nutrime.cli import main

    rc = main(["recipes", "crawl", "--data-dir", str(tmp_path)])
    assert rc == 2
    assert "no crawl sources configured" in capsys.readouterr().out
