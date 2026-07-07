"""MyPlate-via-Wayback adapter — CDX enumeration, parse, convert, seed."""

from __future__ import annotations

import json

import pytest

from nutrime.recipes.myplate_wayback import (
    CDX_URL,
    SOURCE_NAME,
    SOURCE_REMOVED_AT,
    ArchivedRecipeRef,
    convert_recipe,
    list_archived_recipes,
    parse_recipe_page,
    seed_recipes,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer

_NOP_PACER = Pacer(delay_s=0.0)


def _cdx_payload(rows: list[list[str]]) -> str:
    header = [
        "urlkey", "timestamp", "original",
        "mimetype", "statuscode", "digest", "length",
    ]
    return json.dumps([header] + rows)


def _cdx_row(original: str, timestamp: str = "20241126235234") -> list[str]:
    return [
        "gov,myplate)/x", timestamp, original,
        "text/html", "200", "DIGEST", "19954",
    ]


def _recipe_html(
    name: str = "2-Step Chicken",
    recipe_yield: str = "4",
    calories: str = "153.97",
) -> str:
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [{
            "@type": "Recipe",
            "name": name,
            "description": "The ultimate in simplicity.",
            "recipeYield": recipe_yield,
            "nutrition": {
                "@type": "NutritionInformation",
                "calories": calories,
            },
        }],
    })
    return f"""<html><head>
<script type="application/ld+json">{jsonld}</script>
</head><body>
<div class="field field--name-field-ingredients field--label-above">
<h2>Ingredients</h2>
<ul class="field__items ingredients">
<li class="field__item">1 tablespoon vegetable oil <span class="notes">(or cooking oil of choice)</span></li>
<li class="field__item">2 chicken breasts <span class="notes">(boneless, skinless)</span></li>
<li class="field__item">1 can (10.75 ounces) cream of chicken soup</li>
</ul></div>
<div class="field field--name-field-instructions field--label-above">
<h2>Directions</h2>
<div class="field__item"><ol>
<li>Wash hands with soap and water.</li>
<li>Heat oil in a skillet.</li>
</ol></div></div>
<div class="field field--name-field-notes field--label-above">
<h2>Notes</h2>
<div class="field__item"><p>Use reduced sodium soup.</p></div>
<div class="field field--name-field-recipe-serving-size field--label-inline">
<span><strong>Serving Size:</strong></span> <span class="field__item">1/2 chicken breast</span>
</div>
<div class="field field--name-field-source field--label-inline">
<span>Source:</span> <span class="field__item"><p>ONIE Project</p></span>
</div>
</body></html>"""


_REF = ArchivedRecipeRef(
    slug="2-step-chicken",
    original_url="https://www.myplate.gov/recipes/2-step-chicken",
    timestamp="20241126235234",
)


class TestListArchivedRecipes:
    def test_filters_to_clean_recipe_urls(self):
        payload = _cdx_payload([
            _cdx_row("https://www.myplate.gov/recipes/2-step-chicken"),
            _cdx_row("https://www.myplate.gov/recipes/2-step-chicken?ajax_form=1"),
            _cdx_row("https://www.myplate.gov/recipes-cookbooks-and-menus"),
            _cdx_row("https://myplate.gov/recipes/apple-crisp", "20250101000000"),
        ])
        refs = list_archived_recipes(lambda url: payload)
        assert [r.slug for r in refs] == ["2-step-chicken", "apple-crisp"]

    def test_first_snapshot_wins_per_slug(self):
        payload = _cdx_payload([
            _cdx_row("https://www.myplate.gov/recipes/apple-crisp", "20240101000000"),
            _cdx_row("https://www.myplate.gov/recipes/apple-crisp", "20250101000000"),
        ])
        refs = list_archived_recipes(lambda url: payload)
        assert len(refs) == 1
        assert refs[0].timestamp == "20240101000000"

    def test_snapshot_url_uses_id_form(self):
        assert _REF.snapshot_url == (
            "https://web.archive.org/web/20241126235234id_/"
            "https://www.myplate.gov/recipes/2-step-chicken"
        )

    def test_cdx_url_bounded_to_pre_retirement(self):
        assert "to=20260107" in CDX_URL


class TestParseRecipePage:
    def test_jsonld_fields(self):
        parsed = parse_recipe_page(_recipe_html(), _REF)
        assert parsed.title == "2-Step Chicken"
        assert parsed.description == "The ultimate in simplicity."
        assert parsed.yields_count == 4
        assert parsed.calories_per_serving == "153.97"

    def test_ingredients_flattened_with_notes(self):
        parsed = parse_recipe_page(_recipe_html(), _REF)
        assert parsed.ingredients == (
            "1 tablespoon vegetable oil (or cooking oil of choice)",
            "2 chicken breasts (boneless, skinless)",
            "1 can (10.75 ounces) cream of chicken soup",
        )

    def test_steps_and_side_fields(self):
        parsed = parse_recipe_page(_recipe_html(), _REF)
        assert parsed.steps == (
            "Wash hands with soap and water.",
            "Heat oil in a skillet.",
        )
        assert parsed.serving_size == "1/2 chicken breast"
        assert parsed.contributor == "ONIE Project"
        assert "reduced sodium" in parsed.notes

    def test_missing_jsonld_falls_back_to_slug_title(self):
        parsed = parse_recipe_page("<html></html>", _REF)
        assert parsed.title == "2 Step Chicken"
        assert parsed.yields_count is None


class TestConvertRecipe:
    def _converted(self):
        parsed = parse_recipe_page(_recipe_html(), _REF)
        return convert_recipe(parsed, ingested_at="2026-07-07T00:00:00Z")

    def test_preservation_layer_fields(self):
        fm = self._converted().frontmatter
        assert fm["source_status"] == "archived_nutrime_preserved"
        assert fm["source_removed_at"] == SOURCE_REMOVED_AT
        assert "RealFood.gov" in fm["material_implication_note"]

    def test_attribution_carries_original_and_snapshot(self):
        attribution = self._converted().frontmatter["attribution"]
        assert attribution["source_name"] == SOURCE_NAME
        assert attribution["source_url"] == _REF.original_url
        assert attribution["archived_snapshot_url"] == _REF.snapshot_url
        assert attribution["upstream_id"] == "2-step-chicken"

    def test_yields_and_serving_note(self):
        fm = self._converted().frontmatter
        assert fm["yields"]["count"] == 4
        assert fm["yields"]["yield_note"] == "1/2 chicken breast"

    def test_cooklang_metadata_extras(self):
        body = self._converted().cooklang_body
        assert ">> calories_per_serving: 153.97" in body
        assert ">> original_contributor: ONIE Project" in body
        assert ">> notes: Use reduced sodium soup." in body

    def test_ingredient_split_in_body(self):
        body = self._converted().cooklang_body
        assert "@vegetable oil (or cooking oil of choice){1%tablespoon}" in body
        assert "@chicken breasts (boneless, skinless){2}" in body


class TestSeedRecipes:
    @pytest.fixture()
    def vault(self, tmp_path):
        return RecipeVault(tmp_path / "corpus")

    def _fetcher(self, slugs: list[str]):
        rows = [
            _cdx_row(f"https://www.myplate.gov/recipes/{slug}")
            for slug in slugs
        ]
        payload = _cdx_payload(rows)

        def fetch(url: str) -> str:
            if url == CDX_URL:
                return payload
            slug = url.rstrip("/").rsplit("/", 1)[-1]
            return _recipe_html(name=slug.replace("-", " ").title())

        return fetch

    def test_writes_each_new_recipe(self, vault):
        outcome = seed_recipes(
            vault, fetcher=self._fetcher(["a-dish", "b-dish"]),
            pacer=_NOP_PACER,
        )
        assert outcome.written == 2
        assert vault.count() == 2

    def test_second_seed_skips_by_upstream_id(self, vault):
        fetcher = self._fetcher(["a-dish"])
        seed_recipes(vault, fetcher=fetcher, pacer=_NOP_PACER)
        outcome = seed_recipes(vault, fetcher=fetcher, pacer=_NOP_PACER)
        assert outcome.written == 0
        assert outcome.skipped_upstream_ids == ("a-dish",)

    def test_limit_caps_writes(self, vault):
        outcome = seed_recipes(
            vault,
            fetcher=self._fetcher(["a-dish", "b-dish", "c-dish"]),
            pacer=_NOP_PACER,
            limit=1,
        )
        assert outcome.written == 1
        assert vault.count() == 1
