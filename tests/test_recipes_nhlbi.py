"""NHLBI bulk-HTML adapter — listing crawl, page parse, convert, seed."""

from __future__ import annotations

import pytest

from nutrime.recipes.nhlbi import (
    BASE_URL,
    LISTING_PATH,
    SOURCE_NAME,
    convert_recipe,
    list_recipe_urls,
    parse_recipe_page,
    seed_recipes,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer


def _listing_page(slugs: list[str]) -> str:
    links = "".join(
        f'<a href="{LISTING_PATH}/{slug}">{slug}</a>' for slug in slugs
    )
    return f"<html><body>{links}</body></html>"


def _recipe_page(
    title: str = "Baked Salmon Dijon",
    ingredients: str = (
        "<li>1 C fat-free sour cream</li>"
        "<li>1½ lb salmon fillet</li>"
        "<li>Cooking spray</li>"
    ),
    directions: str = (
        "<li>Preheat oven to 400 °F.</li>"
        "<li>Bake until opaque.</li>"
    ),
) -> str:
    return f"""<html><head><title>{title} | NHLBI, NIH</title></head><body>
<table>
<tr><th>Prep Time</th><td><div class="field field--name-field-prep-time field__item">10 minutes</div></td></tr>
<tr><th>Cook Time</th><td><div class="field field--name-field-cook-time field__item">20 minutes</div></td></tr>
<tr><th>Yields</th><td><div class="field field--name-field-yields field__item">6 servings</div></td></tr>
<tr><th>Serving Size</th><td><div class="field field--name-field-serving-size field__item">1 fillet</div></td></tr>
</table>
<h2>Ingredients</h2>
<ul>{ingredients}</ul>
<h2>Directions</h2>
<ol>{directions}</ol>
</body></html>"""


class _MappedFetcher:
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping
        self.calls: list[str] = []

    def __call__(self, url: str) -> str:
        self.calls.append(url)
        return self.mapping.get(url, "<html></html>")


_NOP_PACER = Pacer(delay_s=0.0)


class TestListRecipeUrls:
    def test_walks_pages_until_no_new_links(self):
        fetcher = _MappedFetcher({
            f"{BASE_URL}{LISTING_PATH}?page=0": _listing_page(["a-recipe", "b-recipe"]),
            f"{BASE_URL}{LISTING_PATH}?page=1": _listing_page(["c-recipe"]),
            f"{BASE_URL}{LISTING_PATH}?page=2": _listing_page(["c-recipe"]),
        })
        urls = list_recipe_urls(fetcher, pacer=_NOP_PACER)
        assert urls == [
            f"{BASE_URL}{LISTING_PATH}/a-recipe",
            f"{BASE_URL}{LISTING_PATH}/b-recipe",
            f"{BASE_URL}{LISTING_PATH}/c-recipe",
        ]
        # page=2 yielded nothing new → crawl stopped (no page=3 fetch)
        assert len(fetcher.calls) == 3

    def test_empty_listing_stops_immediately(self):
        fetcher = _MappedFetcher({})
        assert list_recipe_urls(fetcher, pacer=_NOP_PACER) == []
        assert len(fetcher.calls) == 1


class TestParseRecipePage:
    def test_full_shape(self):
        url = f"{BASE_URL}{LISTING_PATH}/baked-salmon-dijon"
        parsed = parse_recipe_page(_recipe_page(), url)
        assert parsed.title == "Baked Salmon Dijon"
        assert parsed.slug == "baked-salmon-dijon"
        assert parsed.ingredients == (
            "1 C fat-free sour cream",
            "1½ lb salmon fillet",
            "Cooking spray",
        )
        assert parsed.steps == (
            "Preheat oven to 400 °F.",
            "Bake until opaque.",
        )
        assert parsed.prep_min == 10
        assert parsed.cook_min == 20
        assert parsed.yields_count == 6
        assert parsed.serving_size == "1 fillet"

    def test_missing_sections_yield_empty(self):
        url = f"{BASE_URL}{LISTING_PATH}/sparse"
        parsed = parse_recipe_page("<html><title>Sparse |</title></html>", url)
        assert parsed.ingredients == ()
        assert parsed.steps == ()
        assert parsed.prep_min is None
        assert parsed.yields_count is None


class TestConvertRecipe:
    def _converted(self):
        url = f"{BASE_URL}{LISTING_PATH}/baked-salmon-dijon"
        parsed = parse_recipe_page(_recipe_page(), url)
        return convert_recipe(parsed, ingested_at="2026-07-07T00:00:00Z")

    def test_frontmatter_headline_fields(self):
        converted = self._converted()
        fm = converted.frontmatter
        assert fm["title"] == "Baked Salmon Dijon"
        assert fm["source_status"] == "live"
        assert fm["estimated_active_time_min"] == 10
        assert fm["estimated_total_time_min"] == 30
        assert fm["yields"]["count"] == 6
        assert fm["yields"]["yield_note"] == "1 fillet"
        assert fm["meal_categories"] == ["heart-healthy"]

    def test_attribution_and_upstream(self):
        converted = self._converted()
        attribution = converted.frontmatter["attribution"]
        assert attribution["source_name"] == SOURCE_NAME
        assert attribution["upstream_id"] == "baked-salmon-dijon"
        assert "17 USC" in attribution["source_license"]
        assert converted.upstream_id == "baked-salmon-dijon"

    def test_allergen_detection_fish(self):
        converted = self._converted()
        assert "fish" in converted.frontmatter["top_allergens_present"]

    def test_cooklang_ingredient_split(self):
        converted = self._converted()
        assert "@fat-free sour cream{1%C}" in converted.cooklang_body
        assert "@salmon fillet{1 1/2%lb}" in converted.cooklang_body
        assert "@Cooking spray{}" in converted.cooklang_body


class TestSeedRecipes:
    @pytest.fixture()
    def vault(self, tmp_path):
        return RecipeVault(tmp_path / "corpus")

    def _fetcher(self, slugs: list[str]) -> _MappedFetcher:
        mapping = {
            f"{BASE_URL}{LISTING_PATH}?page=0": _listing_page(slugs),
            f"{BASE_URL}{LISTING_PATH}?page=1": _listing_page([]),
        }
        for slug in slugs:
            mapping[f"{BASE_URL}{LISTING_PATH}/{slug}"] = _recipe_page(
                title=slug.replace("-", " ").title()
            )
        return _MappedFetcher(mapping)

    def test_writes_each_new_recipe(self, vault):
        outcome = seed_recipes(
            vault,
            fetcher=self._fetcher(["one-dish", "two-dish"]),
            pacer=_NOP_PACER,
        )
        assert outcome.written == 2
        assert vault.count() == 2

    def test_second_seed_skips_by_upstream_id(self, vault):
        fetcher = self._fetcher(["one-dish"])
        seed_recipes(vault, fetcher=fetcher, pacer=_NOP_PACER)
        outcome = seed_recipes(vault, fetcher=fetcher, pacer=_NOP_PACER)
        assert outcome.written == 0
        assert outcome.skipped_upstream_ids == ("one-dish",)
        assert vault.count() == 1

    def test_limit_caps_writes(self, vault):
        outcome = seed_recipes(
            vault,
            fetcher=self._fetcher(["a-dish", "b-dish", "c-dish"]),
            pacer=_NOP_PACER,
            limit=2,
        )
        assert outcome.written == 2
        assert vault.count() == 2

    def test_pacer_used_between_requests(self, vault):
        sleeps: list[float] = []
        pacer = Pacer(delay_s=1.5, sleep=sleeps.append)
        seed_recipes(vault, fetcher=self._fetcher(["a-dish"]), pacer=pacer)
        assert sleeps  # listing pagination + per-recipe fetches paced
        assert all(delay == 1.5 for delay in sleeps)
