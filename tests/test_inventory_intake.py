"""Bulk pantry intake: splitting, classification, freshness → best-by."""

from datetime import date

from nutrime.inventory.intake import (
    best_by_from_freshness,
    classify,
    preview,
    split_list,
)
from nutrime.inventory.store import Location


class TestSplit:
    def test_commas(self) -> None:
        assert split_list("chicken, spinach, lemons") == [
            "chicken", "spinach", "lemons"
        ]

    def test_newlines_and_bullets(self) -> None:
        got = split_list("milk\n- sourdough bread\n• eggs\n* butter")
        assert got == ["milk", "sourdough bread", "eggs", "butter"]

    def test_mixed_delimiters(self) -> None:
        got = split_list("chicken thighs; 2 lemons,\nbrown rice")
        assert got == ["chicken thighs", "2 lemons", "brown rice"]

    def test_space_only_falls_back_to_lexicon_phrases(self) -> None:
        got = split_list("olive oil peanut butter rice")
        assert got == ["olive oil", "peanut butter", "rice"]

    def test_single_item_untouched(self) -> None:
        assert split_list("brown rice") == ["brown rice"]


class TestClassify:
    def test_proteins_fridge_short(self) -> None:
        loc, days, known = classify("chicken thighs")
        assert loc == Location.FRIDGE and days == 2 and known

    def test_bigram_beats_single_word(self) -> None:
        assert classify("sweet potatoes")[0] == Location.PANTRY
        assert classify("peanut butter")[1] is None  # shelf-stable

    def test_frozen_modifier_wins(self) -> None:
        loc, days, _ = classify("frozen peas")
        assert loc == Location.FREEZER and days is None

    def test_canned_modifier_wins(self) -> None:
        loc, days, _ = classify("canned tomatoes")
        assert loc == Location.PANTRY and days is None

    def test_countertop_fruit(self) -> None:
        assert classify("bananas")[0] == Location.COUNTERTOP

    def test_shelf_stable_no_question(self) -> None:
        loc, days, _ = classify("rice")
        assert loc == Location.PANTRY and days is None

    def test_unknown_defaults_pantry_unrecognized(self) -> None:
        loc, days, known = classify("xylotholo root")
        assert loc == Location.PANTRY and days is None and not known

    # -- #56: every probe-table row, against the FDA cold-storage chart --

    def test_raw_meats_fda_short_end(self) -> None:
        # FDA: raw sausage and all ground meats 1-2 days.
        for name in ("sausage", "ground pork", "ground lamb", "beef mince"):
            loc, days, _ = classify(name)
            assert loc == Location.FRIDGE and days == 2, name

    def test_ham_fda_slices(self) -> None:
        loc, days, _ = classify("sliced ham")
        assert loc == Location.FRIDGE and days == 4

    def test_egg_preparations_not_shell_egg_life(self) -> None:
        assert classify("hard boiled eggs")[1] == 7
        assert classify("egg salad")[1] == 3
        assert classify("egg whites")[1] == 2

    def test_prepared_salads_fridge_not_pantry(self) -> None:
        for name in ("potato salad", "pasta salad", "chicken salad"):
            loc, days, _ = classify(name)
            assert loc == Location.FRIDGE and days == 3, name

    def test_soft_cheese_one_week(self) -> None:
        for name in ("goat cheese", "mozzarella", "brie", "feta", "ricotta"):
            loc, days, _ = classify(name)
            assert loc == Location.FRIDGE and days == 7, name

    def test_trigram_half_and_half(self) -> None:
        loc, days, known = classify("half and half")
        assert loc == Location.FRIDGE and days == 7 and known

    def test_raw_seafood_and_meats_without_llm(self) -> None:
        # #56: these fell to pantry-no-date when the LLM tier was off.
        for name in ("cod", "tilapia", "scallops", "mussels", "lobster",
                     "squid", "duck", "veal", "hot dogs"):
            loc, days, _ = classify(name)
            assert loc == Location.FRIDGE and days is not None, name

    def test_cut_melon_and_sprouts_refrigerate(self) -> None:
        assert classify("bean sprouts")[0] == Location.FRIDGE
        # ("cut melon" carries a state word so the LLM tier may refine
        # it, but the lexicon floor must already say fridge.)
        assert classify("cut melon")[0] == Location.FRIDGE

    def test_unknown_perishable_looking_gets_fridge_short_date(self) -> None:
        # #56: unknown-but-perishable must not be pantry/no-date.
        loc, days, known = classify("wagyu picanha cutlet")
        assert loc == Location.FRIDGE and days == 2 and not known


class TestPreview:
    def test_full_paste_round(self) -> None:
        items = preview("chicken thighs, spinach, 2 lemons, brown rice, frozen peas")
        by_name = {p.name: p for p in items}
        assert len(items) == 5
        assert by_name["chicken thighs"].location == "fridge"
        assert by_name["chicken thighs"].perishable
        assert by_name["spinach"].perishable
        lemons = next(p for p in items if "lemon" in p.name)
        assert lemons.quantity == 2.0
        assert by_name["brown rice"].location == "pantry"
        assert not by_name["brown rice"].perishable
        assert by_name["frozen peas"].location == "freezer"
        assert not by_name["frozen peas"].perishable

    def test_quantities_extracted(self) -> None:
        (item,) = preview("2 lb ground beef")
        assert item.quantity == 2.0
        assert item.unit == "lb"
        assert item.location == "fridge"

    def test_duplicates_collapsed(self) -> None:
        assert len(preview("milk, milk, milk")) == 1

    def test_empty_and_junk_lines_dropped(self) -> None:
        items = preview("milk,\n\n , eggs")
        assert [p.name for p in items] == ["milk", "eggs"]

    def test_long_shelf_perishables_not_asked(self) -> None:
        (butter,) = preview("butter")
        assert butter.shelf_days == 60
        assert not butter.perishable  # 60d > ask threshold — no nag


class TestBestBy:
    def test_fresh_today(self) -> None:
        got = best_by_from_freshness(7, 0, today=date(2026, 10, 6))
        assert got == "2026-10-13"

    def test_age_subtracts(self) -> None:
        got = best_by_from_freshness(7, 3, today=date(2026, 10, 6))
        assert got == "2026-10-10"

    def test_older_than_shelf_goes_into_the_past(self) -> None:
        # #55: an item already past its shelf life is EXPIRED. Clamping
        # to today made week-old raw chicken read as "use today" and
        # promoted it into meal plans.
        got = best_by_from_freshness(4, 14, today=date(2026, 10, 6))
        assert got == "2026-09-26"

    def test_raw_chicken_aged_a_week_is_expired(self) -> None:
        # The issue's exact repro: shelf 2d, "about a week" chip (7d).
        got = best_by_from_freshness(2, 7, today=date(2026, 10, 6))
        assert got == "2026-10-01"
        assert got < "2026-10-06"

    def test_no_answer_assumes_bought_today(self) -> None:
        got = best_by_from_freshness(5, None, today=date(2026, 10, 6))
        assert got == "2026-10-11"

    def test_shelf_stable_no_date(self) -> None:
        assert best_by_from_freshness(None, None) is None
        assert best_by_from_freshness(None, 3) is None
