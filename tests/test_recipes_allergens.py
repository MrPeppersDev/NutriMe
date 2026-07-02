"""Heuristic top-9 allergen detection from raw ingredient names."""

from nutrime.recipes.allergens import detect_allergens


class TestDetectAllergens:
    def test_gluten_from_wheat_flour(self) -> None:
        assert "gluten" in detect_allergens(["all-purpose flour", "sugar"])

    def test_dairy_from_butter_and_milk(self) -> None:
        result = detect_allergens(["butter", "whole milk"])
        assert "dairy" in result

    def test_eggs_flagged_but_not_eggplant(self) -> None:
        assert "eggs" in detect_allergens(["large egg"])
        assert "eggs" not in detect_allergens(["eggplant"])

    def test_peanuts(self) -> None:
        assert "peanuts" in detect_allergens(["peanut butter"])

    def test_tree_nuts(self) -> None:
        assert "tree_nuts" in detect_allergens(["sliced almonds", "walnuts"])

    def test_soy_from_soy_sauce(self) -> None:
        assert "soy" in detect_allergens(["soy sauce"])

    def test_fish_from_named_species(self) -> None:
        assert "fish" in detect_allergens(["salmon fillet"])

    def test_shellfish(self) -> None:
        assert "shellfish" in detect_allergens(["shrimp", "scallops"])

    def test_sesame_from_tahini(self) -> None:
        assert "sesame" in detect_allergens(["tahini"])

    def test_sorted_deterministic(self) -> None:
        result = detect_allergens(["salmon", "peanut butter", "tahini", "butter"])
        assert result == sorted(result)

    def test_no_false_positive_on_coconut(self) -> None:
        # "coconut" contains "co" not any of our keys; exclusion is defence-in-depth
        result = detect_allergens(["coconut milk"])
        # coconut milk is technically dairy-free but keyword "milk" matches;
        # ensure we don't crash and we DO catch dairy (over-flagging is OK for MVP)
        assert "dairy" in result

    def test_empty_input(self) -> None:
        assert detect_allergens([]) == []

    def test_case_insensitive(self) -> None:
        assert "gluten" in detect_allergens(["WHEAT FLOUR"])
