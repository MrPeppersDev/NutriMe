"""TheMealDB adapter — JSON payload → domain conversion + seed driver."""

from pathlib import Path

import pytest

from nutrime.recipes.store import RecipeVault
from nutrime.recipes.themealdb import (
    BASE_URL,
    ConvertedRecipe,
    TheMealDBClient,
    convert_meal,
    seed_recipes,
)


def _sample_meal() -> dict:
    """A pared-down TheMealDB payload; real API includes strIngredient1..20."""
    meal = {
        "idMeal": "52772",
        "strMeal": "Teriyaki Chicken Casserole",
        "strCategory": "Chicken",
        "strArea": "Japanese",
        "strTags": "Meat,Casserole",
        "strInstructions": (
            "Preheat oven to 350° F. Spray a 9x13-inch baking pan.\n\n"
            "Combine soy sauce, water, brown sugar, ginger and garlic.\n\n"
            "Serve over rice."
        ),
        "strSource": "https://example.com/teriyaki",
    }
    ingredients = [
        ("soy sauce", "3/4 cup"),
        ("water", "1/2 cup"),
        ("brown sugar", "1/4 cup"),
        ("chicken breasts", "2"),
        ("olive oil", "1 tbsp"),
    ]
    for i, (name, measure) in enumerate(ingredients, start=1):
        meal[f"strIngredient{i}"] = name
        meal[f"strMeasure{i}"] = measure
    # Fill remaining slots empty to match real API shape
    for i in range(len(ingredients) + 1, 21):
        meal[f"strIngredient{i}"] = ""
        meal[f"strMeasure{i}"] = ""
    return meal


class TestConvertMeal:
    def test_recipe_id_prefix(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert converted.recipe_id.startswith("rcp-")

    def test_title_preserved(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert converted.frontmatter["title"] == "Teriyaki Chicken Casserole"

    def test_attribution_shape(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        attr = converted.frontmatter["attribution"]
        assert attr["source_name"] == "TheMealDB"
        assert attr["source_url"] == "https://example.com/teriyaki"
        assert attr["ingestion_method"] == "themealdb_api_v1"
        assert attr["ingested_at"] == "2026-07-02T12:00:00Z"

    def test_source_url_fallback_when_missing(self) -> None:
        meal = _sample_meal()
        meal["strSource"] = ""
        converted = convert_meal(meal, ingested_at="2026-07-02T12:00:00Z")
        assert (
            converted.frontmatter["attribution"]["source_url"]
            == "https://www.themealdb.com/meal/52772"
        )

    def test_cuisine_from_strArea(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert converted.frontmatter["cuisine_tradition_tags"] == ["japanese"]

    def test_meal_categories_includes_category_and_tags(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        cats = converted.frontmatter["meal_categories"]
        assert "chicken" in cats
        assert "meat" in cats
        assert "casserole" in cats

    def test_ingredient_resolution_reflects_ingredient_count(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        summary = converted.frontmatter["ingredient_resolution_summary"]
        assert summary == {"fully_resolved": 0, "partial": 0, "unresolved": 5}
        assert (
            converted.frontmatter["ingredient_resolution_status"]
            == "unresolved_pending_review"
        )

    def test_allergens_detected(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        # soy sauce → soy
        assert "soy" in converted.frontmatter["top_allergens_present"]

    def test_cooklang_body_contains_metadata(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert ">> title: Teriyaki Chicken Casserole" in converted.cooklang_body
        assert ">> servings: 4" in converted.cooklang_body

    def test_cooklang_body_contains_ingredients_with_measures(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert "@soy sauce{3/4%cup}" in converted.cooklang_body
        assert "@brown sugar{1/4%cup}" in converted.cooklang_body

    def test_cooklang_body_contains_step_paragraphs(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert "Preheat oven to 350° F. Spray a 9x13-inch baking pan." in converted.cooklang_body
        assert "Serve over rice." in converted.cooklang_body

    def test_modality_availability_defaults_to_text(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert converted.frontmatter["modality_availability"] == ["text"]

    def test_source_status_live(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert converted.frontmatter["source_status"] == "live"


class TestTheMealDBClient:
    def test_search_by_letter_builds_correct_url(self) -> None:
        seen: list[str] = []

        def fetcher(url: str) -> dict:
            seen.append(url)
            return {"meals": [_sample_meal()]}

        client = TheMealDBClient(fetcher=fetcher)
        meals = client.search_by_letter("a")
        assert seen == [f"{BASE_URL}/search.php?f=a"]
        assert len(meals) == 1

    def test_search_by_letter_lowercases(self) -> None:
        seen: list[str] = []

        def fetcher(url: str) -> dict:
            seen.append(url)
            return {"meals": None}

        client = TheMealDBClient(fetcher=fetcher)
        client.search_by_letter("B")
        assert seen == [f"{BASE_URL}/search.php?f=b"]

    def test_search_by_letter_rejects_non_letter(self) -> None:
        client = TheMealDBClient(fetcher=lambda url: {"meals": None})
        with pytest.raises(ValueError):
            client.search_by_letter("ab")
        with pytest.raises(ValueError):
            client.search_by_letter("1")

    def test_lookup_by_id_returns_single_meal(self) -> None:
        client = TheMealDBClient(
            fetcher=lambda url: {"meals": [_sample_meal()]}
        )
        meal = client.lookup_by_id("52772")
        assert meal is not None
        assert meal["idMeal"] == "52772"

    def test_lookup_by_id_returns_none_when_missing(self) -> None:
        client = TheMealDBClient(fetcher=lambda url: {"meals": None})
        assert client.lookup_by_id("99999") is None

    def test_random_returns_single_meal(self) -> None:
        client = TheMealDBClient(
            fetcher=lambda url: {"meals": [_sample_meal()]}
        )
        meal = client.random()
        assert meal is not None
        assert meal["idMeal"] == "52772"


class TestSeedRecipes:
    def test_writes_to_vault(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path / "corpus")
        client = TheMealDBClient(
            fetcher=lambda url: {"meals": [_sample_meal()]}
        )
        outcome = seed_recipes(client, vault, letters=("a",))
        assert outcome.fetched == 1
        assert outcome.written == 1
        assert vault.count() == 1

    def test_respects_limit(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path / "corpus")
        meals = []
        for i in range(5):
            meal = _sample_meal()
            meal["idMeal"] = str(52772 + i)
            meal["strMeal"] = f"Meal {i}"
            meals.append(meal)
        client = TheMealDBClient(fetcher=lambda url: {"meals": meals})
        outcome = seed_recipes(client, vault, letters=("a",), limit=2)
        assert outcome.written == 2

    def test_skips_already_ingested_by_upstream_id(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path / "corpus")
        client = TheMealDBClient(
            fetcher=lambda url: {"meals": [_sample_meal()]}
        )
        seed_recipes(client, vault, letters=("a",))
        outcome = seed_recipes(client, vault, letters=("a",))
        assert outcome.written == 0
        assert outcome.skipped_upstream_ids == ("52772",)

    def test_iterates_multiple_letters(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path / "corpus")
        calls: list[str] = []

        def fetcher(url: str) -> dict:
            calls.append(url)
            letter = url.rsplit("=", 1)[-1]
            meal = _sample_meal()
            meal["idMeal"] = f"id-{letter}"
            return {"meals": [meal]}

        client = TheMealDBClient(fetcher=fetcher)
        outcome = seed_recipes(client, vault, letters=("a", "b", "c"))
        assert outcome.written == 3
        assert len(calls) == 3

    def test_returns_typed_outcome(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path / "corpus")
        client = TheMealDBClient(fetcher=lambda url: {"meals": None})
        outcome = seed_recipes(client, vault, letters=("a",))
        assert outcome.fetched == 0
        assert outcome.written == 0

    def test_converted_recipe_is_frozen(self) -> None:
        converted = convert_meal(_sample_meal(), ingested_at="2026-07-02T12:00:00Z")
        assert isinstance(converted, ConvertedRecipe)
        with pytest.raises((AttributeError, TypeError)):
            converted.recipe_id = "new-id"  # type: ignore[misc]
