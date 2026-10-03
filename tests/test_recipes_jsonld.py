"""schema.org/Recipe JSON-LD adapter — extraction, conversion, seed driver."""

import json
from pathlib import Path

from nutrime.recipes.frontmatter import validate_frontmatter
from nutrime.recipes.jsonld import (
    convert_recipe_node,
    extract_recipe_jsonld,
    normalize_url,
    parse_iso_duration_minutes,
    read_urls_file,
    seed_recipes,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer


def _recipe_node() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": "Lemon Garlic Salmon",
        "recipeIngredient": [
            "1½ lb salmon fillet",
            "2 cloves garlic",
            "1 lemon",
            "Cooking spray",
        ],
        "recipeInstructions": [
            {"@type": "HowToStep", "text": "Preheat oven to 400°F."},
            {"@type": "HowToStep", "text": "Roast salmon 12 minutes."},
        ],
        "recipeYield": "4 servings",
        "totalTime": "PT25M",
        "prepTime": "PT10M",
        "recipeCuisine": "Mediterranean",
        "recipeCategory": ["Dinner", "Seafood"],
    }


def _page(node_payload) -> str:
    return (
        "<html><head><script type=\"application/ld+json\">"
        + json.dumps(node_payload)
        + "</script></head><body>recipe page</body></html>"
    )


class TestParseIsoDuration:
    def test_hours_and_minutes(self) -> None:
        assert parse_iso_duration_minutes("PT1H30M") == 90

    def test_minutes_only(self) -> None:
        assert parse_iso_duration_minutes("PT45M") == 45

    def test_days(self) -> None:
        assert parse_iso_duration_minutes("P1DT2H") == 26 * 60

    def test_garbage_and_empty(self) -> None:
        assert parse_iso_duration_minutes("soon") is None
        assert parse_iso_duration_minutes("") is None
        assert parse_iso_duration_minutes(None) is None
        assert parse_iso_duration_minutes("PT0M") is None


class TestNormalizeUrl:
    def test_strips_fragment_and_trailing_slash(self) -> None:
        assert (
            normalize_url("https://Example.com/recipe/#reviews")
            == "https://example.com/recipe"
        )

    def test_keeps_query(self) -> None:
        assert (
            normalize_url("https://example.com/r?id=7")
            == "https://example.com/r?id=7"
        )


class TestExtractRecipeJsonld:
    def test_plain_node(self) -> None:
        node = extract_recipe_jsonld(_page(_recipe_node()))
        assert node is not None
        assert node["name"] == "Lemon Garlic Salmon"

    def test_graph_wrapped(self) -> None:
        payload = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "WebPage", "name": "blog"},
                _recipe_node(),
            ],
        }
        node = extract_recipe_jsonld(_page(payload))
        assert node is not None
        assert node["@type"] == "Recipe"

    def test_type_list(self) -> None:
        node_payload = _recipe_node()
        node_payload["@type"] = ["Recipe", "NewsArticle"]
        assert extract_recipe_jsonld(_page(node_payload)) is not None

    def test_malformed_sibling_block_skipped(self) -> None:
        html = (
            "<script type='application/ld+json'>{not json]</script>"
            + _page(_recipe_node())
        )
        assert extract_recipe_jsonld(html) is not None

    def test_no_recipe_returns_none(self) -> None:
        payload = {"@type": "NewsArticle", "headline": "no recipe here"}
        assert extract_recipe_jsonld(_page(payload)) is None


class TestConvertRecipeNode:
    def test_frontmatter_validates_and_maps_fields(self) -> None:
        converted = convert_recipe_node(
            _recipe_node(),
            source_url="https://www.tastyblog.com/salmon/",
            ingested_at="2026-10-03T00:00:00Z",
        )
        fm = converted.frontmatter
        validate_frontmatter(fm)
        assert fm["title"] == "Lemon Garlic Salmon"
        assert fm["attribution"]["source_name"] == "tastyblog.com"
        assert fm["attribution"]["ingestion_method"] == "schema_org_jsonld_v1"
        assert fm["estimated_total_time_min"] == 25
        assert fm["estimated_active_time_min"] == 10
        assert fm["cuisine_tradition_tags"] == ["mediterranean"]
        assert fm["meal_categories"] == ["dinner", "seafood"]
        assert fm["yields"]["count"] == 4
        # salmon → fish allergen via the heuristic detector
        assert "fish" in fm["top_allergens_present"]

    def test_cooklang_body_has_ingredients_and_steps(self) -> None:
        converted = convert_recipe_node(
            _recipe_node(), source_url="https://example.com/r"
        )
        assert "@salmon fillet{1 1/2%lb}" in converted.cooklang_body
        assert "Roast salmon 12 minutes." in converted.cooklang_body

    def test_prep_plus_cook_fallback_when_no_total(self) -> None:
        node = _recipe_node()
        del node["totalTime"]
        node["cookTime"] = "PT15M"
        converted = convert_recipe_node(
            node, source_url="https://example.com/r"
        )
        assert converted.frontmatter["estimated_total_time_min"] == 25

    def test_string_instructions(self) -> None:
        node = _recipe_node()
        node["recipeInstructions"] = "<p>Mix everything. Bake.</p>"
        converted = convert_recipe_node(
            node, source_url="https://example.com/r"
        )
        assert "Mix everything. Bake." in converted.cooklang_body

    def test_howtosection_flattened(self) -> None:
        node = _recipe_node()
        node["recipeInstructions"] = [
            {
                "@type": "HowToSection",
                "name": "Sauce",
                "itemListElement": [
                    {"@type": "HowToStep", "text": "Whisk the sauce."}
                ],
            }
        ]
        converted = convert_recipe_node(
            node, source_url="https://example.com/r"
        )
        assert "Whisk the sauce." in converted.cooklang_body


class TestReadUrlsFile:
    def test_skips_blanks_and_comments(self, tmp_path: Path) -> None:
        f = tmp_path / "urls.txt"
        f.write_text(
            "# my pinterest saves\n"
            "https://example.com/a\n"
            "\n"
            "https://example.com/b\n"
        )
        assert read_urls_file(f) == [
            "https://example.com/a",
            "https://example.com/b",
        ]


class TestSeedRecipes:
    def _vault(self, tmp_path: Path) -> RecipeVault:
        vault = RecipeVault(tmp_path / "corpus")
        vault.ensure()
        return vault

    def _pacer(self) -> Pacer:
        return Pacer(delay_s=0, sleep=lambda _: None)

    def test_writes_and_dedups_within_run(self, tmp_path: Path) -> None:
        vault = self._vault(tmp_path)
        page = _page(_recipe_node())
        outcome = seed_recipes(
            vault,
            ["https://example.com/r", "https://example.com/r/"],
            fetcher=lambda url: page,
            pacer=self._pacer(),
        )
        assert outcome.written == 1
        assert len(outcome.skipped_upstream_ids) == 1
        assert vault.count() == 1

    def test_dedups_across_runs(self, tmp_path: Path) -> None:
        vault = self._vault(tmp_path)
        page = _page(_recipe_node())
        seed_recipes(
            vault,
            ["https://example.com/r"],
            fetcher=lambda url: page,
            pacer=self._pacer(),
        )
        outcome = seed_recipes(
            vault,
            ["https://example.com/r"],
            fetcher=lambda url: page,
            pacer=self._pacer(),
        )
        assert outcome.written == 0
        assert outcome.skipped_upstream_ids == ("https://example.com/r",)

    def test_no_jsonld_reported_not_fatal(self, tmp_path: Path) -> None:
        vault = self._vault(tmp_path)

        def fetch(url: str) -> str:
            if url.endswith("good"):
                return _page(_recipe_node())
            return "<html>plain page, no structured data</html>"

        outcome = seed_recipes(
            vault,
            ["https://example.com/bad", "https://example.com/good"],
            fetcher=fetch,
            pacer=self._pacer(),
        )
        assert outcome.written == 1
        assert outcome.failures == (
            ("https://example.com/bad", "no schema.org/Recipe JSON-LD found"),
        )

    def test_fetch_error_reported_not_fatal(self, tmp_path: Path) -> None:
        vault = self._vault(tmp_path)

        def fetch(url: str) -> str:
            if "down" in url:
                raise OSError("connection refused")
            return _page(_recipe_node())

        outcome = seed_recipes(
            vault,
            ["https://down.example.com/r", "https://example.com/r"],
            fetcher=fetch,
            pacer=self._pacer(),
        )
        assert outcome.written == 1
        assert outcome.failures[0][0] == "https://down.example.com/r"
        assert "fetch failed" in outcome.failures[0][1]

    def test_limit_caps_writes(self, tmp_path: Path) -> None:
        vault = self._vault(tmp_path)
        page = _page(_recipe_node())
        outcome = seed_recipes(
            vault,
            [f"https://example.com/r{i}" for i in range(5)],
            fetcher=lambda url: page,
            pacer=self._pacer(),
            limit=2,
        )
        assert outcome.written == 2
        assert vault.count() == 2


class TestUrlsSourceCLI:
    def test_fetch_urls_source(self, tmp_path: Path, capsys, monkeypatch) -> None:
        from nutrime.cli import main
        from nutrime.recipes import jsonld as jsonld_mod

        monkeypatch.setattr(
            jsonld_mod, "_urllib_fetch_text", lambda url: _page(_recipe_node())
        )
        urls_file = tmp_path / "pins.txt"
        urls_file.write_text("https://example.com/salmon\n")
        rc = main(
            [
                "recipes",
                "fetch",
                "--source",
                "urls",
                "--urls-file",
                str(urls_file),
                "--data-dir",
                str(tmp_path / "data"),
                "--delay",
                "0",
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "wrote 1" in out

    def test_urls_source_requires_file(self, tmp_path: Path, capsys) -> None:
        from nutrime.cli import main

        rc = main(
            [
                "recipes",
                "fetch",
                "--source",
                "urls",
                "--data-dir",
                str(tmp_path / "data"),
            ]
        )
        assert rc == 2
