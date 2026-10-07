"""Shared pantry↔ingredient matcher — the 2026-10-08 consolidation.

Covers the cases that motivated hoisting the matcher out of search.py:
the household's REAL inventory ("seedy bread", "EVOO", "kewpie mayo",
"2% milk") versus the generic names recipes use, plus the food-family
fallback (member↔family-name) and its precision guards (sibling foods
never match, modified compounds keep their guards).
"""

from nutrime.foods.matching import (
    FOOD_FAMILIES,
    exclusion_match,
    normalize_term,
    terms_match,
)


class TestTermsMatchFamilies:
    def test_variety_satisfies_family_name(self) -> None:
        # The reported bug: "seedy bread" on the countertop, recipes
        # still said bread was missing.
        for member, family in (
            ("seedy bread", "bread"),
            ("sourdough", "bread"),
            ("cheddar", "cheese"),
            ("shredded cheddar", "cheese"),
            ("greek yogurt", "yogurt"),
            ("basmati", "rice"),
            ("spaghetti", "pasta"),
            ("romaine", "lettuce"),
            ("russet", "potato"),
            ("granny smith", "apple"),
            ("white vinegar", "vinegar"),
        ):
            assert terms_match(member, family), f"{member} should satisfy {family}"
            assert terms_match(family, member), f"{family} should satisfy {member}"

    def test_family_name_with_modifier_still_generic(self) -> None:
        assert terms_match("sourdough", "crusty bread")
        assert terms_match("cheddar", "shredded cheese")

    def test_siblings_never_match(self) -> None:
        # Same family on both sides is NOT equivalence.
        for a, b in (
            ("cheddar", "gouda"),
            ("sourdough", "baguette"),
            ("basmati", "arborio"),
            ("spaghetti", "penne"),
            ("granny smith", "honeycrisp"),
        ):
            assert not terms_match(a, b), f"{a} must not satisfy {b}"
            assert not terms_match(b, a), f"{b} must not satisfy {a}"

    def test_family_fallback_keeps_distinct_food_guard(self) -> None:
        # The family table must not reopen holes the compound guards
        # closed: milk-family membership never bridges to coconut milk.
        assert not terms_match("whole milk", "coconut milk")
        assert not terms_match("2% milk", "buttermilk")

    def test_compound_head_guard_survives(self) -> None:
        assert not terms_match("rice", "rice vinegar")
        assert terms_match("vinegar", "rice vinegar")
        assert not terms_match("peanut butter", "peanut")

    def test_families_table_is_normalized_shapes(self) -> None:
        # Guard against table rot: members must already be in
        # normalize_term shape or lookups silently miss.
        for family, members in FOOD_FAMILIES.items():
            assert normalize_term(family) == family, family
            for m in members:
                assert normalize_term(m) == m, f"{family}: {m!r}"


class TestTermsMatchSynonyms:
    def test_household_abbreviations(self) -> None:
        # Straight from the live inventory table.
        assert terms_match("EVOO", "olive oil")
        assert terms_match("kewpie mayo", "mayonnaise")
        assert terms_match("beef bullion", "beef bouillon")
        assert terms_match("chicken bullion", "bouillon")

    def test_word_level_synonym_inside_phrase(self) -> None:
        # Single-word synonyms apply mid-phrase; phrase synonyms only
        # whole ("mince" → "ground beef" must not fire inside
        # "minced garlic").
        assert terms_match("kewpie mayo", "kewpie mayonnaise")
        assert not terms_match("minced garlic", "ground beef")


class TestTermsMatchModifiers:
    def test_percent_and_fat_modifiers(self) -> None:
        assert terms_match("2% milk", "milk")
        assert terms_match("milk", "whole milk")
        assert terms_match("Eggs (dozen)", "eggs")

    def test_plurals_and_case(self) -> None:
        assert terms_match("eggs", "egg")
        assert terms_match("Strawberries", "strawberry")


class TestExclusionMatch:
    def test_family_members_excluded_by_family_avoid(self) -> None:
        # "avoids bread" has to catch sourdough: safety direction.
        assert exclusion_match("bread", "sourdough loaf")
        assert exclusion_match("cheese", "cheddar")

    def test_compound_recall_kept(self) -> None:
        assert exclusion_match("peanut", "peanut butter")
        assert exclusion_match("onion", "onion powder")
        assert exclusion_match("milk", "coconut milk")

    def test_token_boundaries_still_hold(self) -> None:
        assert not exclusion_match("egg", "eggplant")
        assert not exclusion_match("apple", "pineapple")
