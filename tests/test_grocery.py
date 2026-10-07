"""Grocery engine (6.1) — parsing, merge gate, provenance, netting, export."""

from pathlib import Path

import pytest

from nutrime.grocery.aggregate import (
    aggregate,
    display_amount,
    needs_from_recipe_body,
)
from nutrime.grocery.build import build_grocery_list, render_markdown, render_text
from nutrime.grocery.parse import (
    normalize_food,
    parse_cooklang_line,
    parse_quantity,
    refine,
)
from nutrime.grocery.units import (
    best_display,
    find_unit,
    resolve_oz_ambiguity,
    to_base,
)


class TestParseQuantity:
    def test_mixed_number(self) -> None:
        assert parse_quantity("1 1/2") == 1.5

    def test_unicode_fraction(self) -> None:
        assert parse_quantity("½") == 0.5
        assert parse_quantity("1½") == 1.5

    def test_range_takes_low_end(self) -> None:
        assert parse_quantity("3-4") == 3.0

    def test_text_is_none(self) -> None:
        assert parse_quantity("to taste") is None
        assert parse_quantity("") is None


class TestUnits:
    def test_aliases(self) -> None:
        assert find_unit("Tablespoons") == "tbsp"
        assert find_unit("tins") == "can"
        assert find_unit("nonsense") is None

    def test_oz_ambiguity(self) -> None:
        assert resolve_oz_ambiguity("oz", "cup") == ("fl_oz", "cup")
        assert resolve_oz_ambiguity("oz", "g") == ("oz", "g")

    def test_to_base(self) -> None:
        amount, dim = to_base(2, "cup")
        assert dim == "volume" and abs(amount - 473.176) < 0.01
        assert to_base(1, "can") is None

    def test_best_display_prefers_readable(self) -> None:
        shown = best_display(591.47, "volume", ("cup", "tbsp"))
        assert shown.unit == "cup" and abs(shown.quantity - 2.5) < 0.01


class TestRefine:
    def test_comma_note(self) -> None:
        line = refine("onion, finely diced", "1", "")
        assert line.food == "onion"
        assert line.note == "finely diced"

    def test_parenthetical_to_note(self) -> None:
        line = refine("flour (sifted)", "2", "cups")
        assert line.food == "flour"
        assert line.unit == "cup"
        assert "sifted" in line.note

    def test_unit_promoted_from_name(self) -> None:
        line = refine("can crushed tomatoes", "1", "")
        assert line.unit == "can"
        assert line.food == "crushed tomatoes"

    def test_of_connective_dropped(self) -> None:
        line = refine("cups of flour", "2", "")
        assert line.unit == "cup" and line.food == "flour"

    def test_unknown_unit_kept_in_note(self) -> None:
        line = refine("sugar", "1", "heaping scoop")
        assert line.unit == ""
        assert "heaping scoop" in line.note


class TestParseCooklang:
    def test_braced(self) -> None:
        line = parse_cooklang_line("@soy sauce{3/4%cup}")
        assert line.food == "soy sauce"
        assert line.quantity == 0.75
        assert line.unit == "cup"

    def test_bare(self) -> None:
        line = parse_cooklang_line("@salt")
        assert line.food == "salt" and line.quantity is None

    def test_non_ingredient(self) -> None:
        assert parse_cooklang_line("Simmer gently.") is None


class TestNormalizeFood:
    def test_plural_and_case(self) -> None:
        assert normalize_food("Carrots") == normalize_food("carrot")

    def test_distinct_foods_stay_distinct(self) -> None:
        assert normalize_food("green onion") != normalize_food("onion")

    def test_accents(self) -> None:
        assert normalize_food("jalapeño") == normalize_food("jalapeno")


def _need(recipe_id: str, title: str, *lines: str):
    body = "\n".join(lines)
    return needs_from_recipe_body(recipe_id, title, body)


class TestAggregate:
    def test_same_unit_adds(self) -> None:
        lines = aggregate(
            [
                _need("r1", "Stew", "@carrot{2%count}" if False else "@carrots{2}"),
                _need("r2", "Soup", "@carrot{3}"),
            ]
        )
        (line,) = lines
        assert line.quantity == 5.0
        assert {c.recipe_id for c in line.contributions} == {"r1", "r2"}

    def test_convertible_units_consolidate(self) -> None:
        lines = aggregate(
            [
                _need("r1", "Bake", "@milk{1%cup}"),
                _need("r2", "Sauce", "@milk{8%tbsp}"),
            ]
        )
        (line,) = lines
        assert display_amount(line) == "1½ cups"  # kitchen fractions + plural

    def test_incompatible_units_stay_separate(self) -> None:
        lines = aggregate(
            [
                _need("r1", "Stew", "@tomatoes{2%cans}"),
                _need("r2", "Sauce", "@tomatoes{400%g}"),
            ]
        )
        assert len(lines) == 2

    def test_oz_meets_volume_merges_as_fluid(self) -> None:
        lines = aggregate(
            [
                _need("r1", "Cocktail", "@juice{4%oz}"),
                _need("r2", "Marinade", "@juice{1%cup}"),
            ]
        )
        (line,) = lines
        assert line.base_dim == "volume"

    def test_unquantified_joins(self) -> None:
        lines = aggregate(
            [
                _need("r1", "Stew", "@salt"),
                _need("r2", "Soup", "@salt"),
            ]
        )
        (line,) = lines
        assert line.quantity is None
        assert len(line.contributions) == 2

    def test_inventory_marks_on_hand_not_deleted(self) -> None:
        lines = aggregate(
            [_need("r1", "Stew", "@carrots{3}", "@beef{500%g}")],
            inventory_names=["Carrot"],
        )
        by_food = {l.food_key: l for l in lines}
        assert by_food[normalize_food("carrots")].on_hand is True
        assert by_food[normalize_food("beef")].on_hand is False
        assert len(lines) == 2  # nothing silently dropped

    def test_netting_matches_through_modifiers(self) -> None:
        # 2026-10-08: netting uses the shared matcher, not exact keys —
        # the old behavior told the household to buy milk, bread and
        # eggs they demonstrably had.
        lines = aggregate(
            [_need("r1", "Bake", "@whole milk{1%cup}", "@bread{2%slice}",
                   "@eggs{3}", "@heavy cream{1%cup}")],
            inventory_names=["milk", "seedy bread", "Eggs (dozen)"],
        )
        on_hand = {l.food: l.on_hand for l in lines}
        assert on_hand["whole milk"] is True       # generic covers modified
        assert on_hand["bread"] is True            # family: seedy bread IS bread
        assert on_hand["eggs"] is True             # parenthetical ignored
        assert on_hand["heavy cream"] is False     # still to-buy

    def test_netting_keeps_distinct_food_guard(self) -> None:
        # Pantry milk must NOT tick off coconut milk — different food.
        lines = aggregate(
            [_need("r1", "Curry", "@coconut milk{1%can}")],
            inventory_names=["milk"],
        )
        (line,) = lines
        assert line.on_hand is False


class TestBuildAndRender:
    @pytest.fixture
    def setup(self, tmp_path: Path):
        from nutrime.plans.store import PlanEntry, PlanVault, new_plan_id, render_plan_body
        from nutrime.recipes.store import RecipeVault
        from nutrime.recipes.themealdb import convert_meal

        vault = RecipeVault(tmp_path / "corpus")
        vault.ensure()
        meal = {
            "idMeal": "7",
            "strMeal": "Beef Stew",
            "strCategory": "Beef",
            "strArea": "Irish",
            "strTags": "",
            "strInstructions": "Cook.",
            "strSource": "https://example.com/stew",
        }
        for i in range(1, 21):
            meal[f"strIngredient{i}"] = ""
            meal[f"strMeasure{i}"] = ""
        meal["strIngredient1"], meal["strMeasure1"] = "beef", "500 g"
        meal["strIngredient2"], meal["strMeasure2"] = "carrots", "3"
        converted = convert_meal(meal, ingested_at="2026-10-04T00:00:00Z")
        vault.write(converted.recipe_id, converted.frontmatter, converted.cooklang_body)

        plan_vault = PlanVault(tmp_path / "corpus")
        plan_vault.ensure()
        plan_id = new_plan_id()
        entries = (
            PlanEntry(day=1, slot="dinner", recipe_id=converted.recipe_id, title="Beef Stew"),
            PlanEntry(day=2, slot="dinner", recipe_id=None, title="", note="no candidates"),
        )
        fm = {
            "plan_id": plan_id,
            "content_type": "meal_plan",
            "created_at": "2026-10-04T00:00:00Z",
            "tenant_id": "tnt-test",
            "days": 2,
            "meal_slots": ["dinner"],
            "meals_planned": 1,
            "model": "test",
            "llm_request_ids": [],
            "llm_request_log_ids": [],
            "constraints_applied": [],
            "candidate_count": 1,
        }
        plan_vault.write(plan_id, fm, render_plan_body(entries))
        return plan_vault.read(plan_id), vault

    def test_build_and_render_text(self, setup) -> None:
        plan, vault = setup
        groceries = build_grocery_list(plan, vault, inventory_names=["carrots"])
        text = render_text(groceries)
        assert "500 g beef" in text
        assert "Beef Stew" in text  # provenance rendered
        assert "Already have" in text and "carrot" in text.lower()

    def test_render_markdown(self, setup) -> None:
        plan, vault = setup
        groceries = build_grocery_list(plan, vault)
        md = render_markdown(groceries)
        assert md.startswith("# Grocery list")
        assert "- [ ]" in md

    def test_missing_recipe_reported(self, setup, tmp_path) -> None:
        from nutrime.recipes.store import RecipeVault

        plan, _ = setup
        empty_vault = RecipeVault(tmp_path / "other")
        empty_vault.ensure()
        groceries = build_grocery_list(plan, empty_vault)
        assert len(groceries.missing_recipe_ids) == 1
        assert "no longer in the vault" in render_text(groceries)
