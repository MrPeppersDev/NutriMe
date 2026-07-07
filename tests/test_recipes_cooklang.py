"""Cooklang emission — the canonical body format per D4 Q4.2."""

from nutrime.recipes.cooklang import (
    Ingredient,
    Recipe,
    emit_cooklang,
    normalize_fractions,
    split_ingredient_line,
    split_measure,
)


class TestNormalizeFractions:
    def test_mixed_number(self) -> None:
        assert normalize_fractions("1½ lb salmon") == "1 1/2 lb salmon"

    def test_bare_fraction(self) -> None:
        assert normalize_fractions("½ tsp garlic powder") == (
            "1/2 tsp garlic powder"
        )

    def test_no_fractions_passthrough(self) -> None:
        assert normalize_fractions("2 cups rice") == "2 cups rice"


class TestSplitIngredientLine:
    def test_qty_unit_name(self) -> None:
        assert split_ingredient_line("1 C fat-free sour cream") == (
            "1", "C", "fat-free sour cream"
        )

    def test_unicode_fraction_with_unit(self) -> None:
        assert split_ingredient_line("1½ lb salmon fillet") == (
            "1 1/2", "lb", "salmon fillet"
        )

    def test_qty_no_unit(self) -> None:
        assert split_ingredient_line("2 chicken breasts") == (
            "2", "", "chicken breasts"
        )

    def test_no_quantity_at_all(self) -> None:
        assert split_ingredient_line("Cooking spray") == (
            "", "", "Cooking spray"
        )

    def test_fraction_quantity(self) -> None:
        assert split_ingredient_line("3/4 cup rolled oats") == (
            "3/4", "cup", "rolled oats"
        )

    def test_parenthetical_note_survives_in_name(self) -> None:
        qty, unit, name = split_ingredient_line(
            "1 tablespoon vegetable oil (or cooking oil of choice)"
        )
        assert (qty, unit) == ("1", "tablespoon")
        assert name == "vegetable oil (or cooking oil of choice)"

    def test_empty_line(self) -> None:
        assert split_ingredient_line("  ") == ("", "", "")


class TestSplitMeasure:
    def test_quantity_and_unit(self) -> None:
        assert split_measure("3/4 cup") == ("3/4", "cup")

    def test_bare_quantity(self) -> None:
        assert split_measure("2") == ("2", "")

    def test_textual_measure(self) -> None:
        assert split_measure("to taste") == ("to taste", "")

    def test_empty_measure(self) -> None:
        assert split_measure("") == ("", "")

    def test_whitespace_only(self) -> None:
        assert split_measure("   ") == ("", "")


class TestEmitCooklang:
    def test_metadata_block_present(self) -> None:
        recipe = Recipe(
            title="Test Recipe",
            ingredients=(),
            steps=(),
            servings=6,
            source_url="https://example.com/r/1",
            attribution="Example",
        )
        text = emit_cooklang(recipe)
        assert ">> title: Test Recipe" in text
        assert ">> servings: 6" in text
        assert ">> source: https://example.com/r/1" in text
        assert ">> attribution: Example" in text

    def test_single_word_ingredient_omits_braces(self) -> None:
        recipe = Recipe(
            title="Salted",
            ingredients=(Ingredient(name="salt"),),
            steps=("Salt to taste.",),
        )
        text = emit_cooklang(recipe)
        assert "@salt\n" in text or "@salt " in text or text.endswith("@salt\n") or "@salt" in text.split("\n")
        # Explicit: single-word bare ingredient must not have braces
        assert "@salt{}" not in text

    def test_multiword_ingredient_uses_braces(self) -> None:
        recipe = Recipe(
            title="Oil",
            ingredients=(Ingredient(name="olive oil", quantity="2", unit="tbsp"),),
            steps=(),
        )
        text = emit_cooklang(recipe)
        assert "@olive oil{2%tbsp}" in text

    def test_qty_only_ingredient(self) -> None:
        recipe = Recipe(
            title="Eggs",
            ingredients=(Ingredient(name="eggs", quantity="2"),),
            steps=(),
        )
        text = emit_cooklang(recipe)
        assert "@eggs{2}" in text

    def test_no_qty_multiword_uses_empty_braces(self) -> None:
        recipe = Recipe(
            title="Pepper",
            ingredients=(Ingredient(name="black pepper"),),
            steps=(),
        )
        text = emit_cooklang(recipe)
        assert "@black pepper{}" in text

    def test_steps_split_into_paragraphs(self) -> None:
        recipe = Recipe(
            title="Test",
            ingredients=(),
            steps=("Preheat oven.", "Bake for 20 minutes."),
        )
        text = emit_cooklang(recipe)
        assert "Preheat oven." in text
        assert "Bake for 20 minutes." in text

    def test_empty_recipe_still_valid_output(self) -> None:
        recipe = Recipe(title="Empty", ingredients=(), steps=())
        text = emit_cooklang(recipe)
        assert ">> title: Empty" in text
        assert "-- Ingredients" in text
        assert "-- Instructions" in text
        assert text.endswith("\n")

    def test_output_ends_with_single_newline(self) -> None:
        recipe = Recipe(
            title="Test",
            ingredients=(Ingredient(name="salt"),),
            steps=("Salt.",),
        )
        text = emit_cooklang(recipe)
        assert text.endswith("\n")
        assert not text.endswith("\n\n")
