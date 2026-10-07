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
        # #57: "coconut milk" must be removed as a WHOLE phrase — the old
        # exclusion replaced "coconut" and left " milk" behind, false-
        # flagging dairy. Coconut milk is a staple of dairy-avoiding
        # cooking; false-flagging it blocks exactly the safe recipes.
        assert "dairy" not in detect_allergens(["coconut milk"])
        assert "dairy" not in detect_allergens(["coconut cream"])
        # Real milk alongside still flags.
        assert "dairy" in detect_allergens(["coconut milk", "whole milk"])

    def test_empty_input(self) -> None:
        assert detect_allergens([]) == []

    def test_case_insensitive(self) -> None:
        assert "gluten" in detect_allergens(["WHEAT FLOUR"])

    # -- #57 gap rows: every miss from the issue's probe table ------------

    def test_egg_preparations(self) -> None:
        for ing in ("mayonnaise", "mayo", "aioli", "albumin"):
            assert "eggs" in detect_allergens([ing]), ing

    def test_dairy_cheeses_and_cultured(self) -> None:
        for ing in ("buttermilk", "parmesan", "mozzarella", "ricotta",
                    "cheddar", "paneer", "kefir", "sodium caseinate",
                    "custard"):
            assert "dairy" in detect_allergens([ing]), ing

    def test_fish_species_and_preparations(self) -> None:
        for ing in ("anchovies", "worcestershire sauce", "caesar dressing",
                    "halibut", "pollock", "catfish", "surimi", "bonito",
                    "dashi"):
            assert "fish" in detect_allergens([ing]), ing

    def test_tree_nut_preparations(self) -> None:
        for ing in ("pesto", "mixed nuts", "marzipan", "praline",
                    "filbert", "pignoli"):
            assert "tree_nuts" in detect_allergens([ing]), ing

    def test_chestnut_no_longer_tree_nut(self) -> None:
        # FDA 2025 guidance (Edition 5) removed chestnut.
        assert "tree_nuts" not in detect_allergens(["roasted chestnuts"])
        assert "tree_nuts" not in detect_allergens(["water chestnuts"])

    def test_sesame_preparations(self) -> None:
        for ing in ("hummus", "za'atar", "halva"):
            assert "sesame" in detect_allergens([ing]), ing

    def test_wheat_hidden_sources(self) -> None:
        for ing in ("breadcrumbs", "panko", "bulgur", "farro", "seitan"):
            assert "gluten" in detect_allergens([ing]), ing

    def test_soy_sauce_flags_wheat_too(self) -> None:
        result = detect_allergens(["soy sauce"])
        assert "soy" in result and "gluten" in result

    def test_shellfish_additions(self) -> None:
        for ing in ("crawfish", "langoustine", "squid", "octopus"):
            assert "shellfish" in detect_allergens([ing]), ing

    def test_plural_y_to_ies(self) -> None:
        assert "fish" in detect_allergens(["anchovies"])
        assert "eggs" not in detect_allergens(["eggplants"])

    def test_butternut_not_tree_nut(self) -> None:
        # "nut" keyword is broad; butternut squash must not flag.
        assert "tree_nuts" not in detect_allergens(["butternut squash"])
