"""Scoring rules verified 2026-06-30 against Kroenke originals, USPSTF 2023,
and Children's HealthWatch canonical source. See ``stage3-plan.md`` §
"Component verification log — Step 2 sub-commit 2.1"."""

import pytest

from nutrime.intake.instruments import (
    GAD2,
    HUNGER_VITAL_SIGN,
    PHQ2,
    Instrument,
)


class TestPHQ2:
    def test_all_zero_negative(self) -> None:
        result = PHQ2.score({"anhedonia": 0, "depressed_mood": 0})
        assert result.score == 0
        assert not result.positive

    def test_cutoff_at_3_is_positive(self) -> None:
        result = PHQ2.score({"anhedonia": 2, "depressed_mood": 1})
        assert result.score == 3
        assert result.positive

    def test_below_cutoff_is_negative(self) -> None:
        result = PHQ2.score({"anhedonia": 1, "depressed_mood": 1})
        assert result.score == 2
        assert not result.positive

    def test_maximum_score(self) -> None:
        result = PHQ2.score({"anhedonia": 3, "depressed_mood": 3})
        assert result.score == 6
        assert result.positive

    def test_disclosure_present_and_non_diagnostic(self) -> None:
        result = PHQ2.score({"anhedonia": 0, "depressed_mood": 0})
        assert "not a diagnosis" in result.disclosure

    def test_missing_item_raises(self) -> None:
        with pytest.raises(ValueError, match="missing response"):
            PHQ2.score({"anhedonia": 1})

    def test_unknown_item_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown item"):
            PHQ2.score({"anhedonia": 1, "depressed_mood": 1, "bogus": 0})

    def test_out_of_scale_value_raises(self) -> None:
        with pytest.raises(ValueError, match="outside"):
            PHQ2.score({"anhedonia": 4, "depressed_mood": 1})


class TestGAD2:
    def test_cutoff_at_3_is_positive(self) -> None:
        result = GAD2.score({"nervousness": 2, "uncontrollable_worry": 1})
        assert result.score == 3
        assert result.positive

    def test_below_cutoff_is_negative(self) -> None:
        result = GAD2.score({"nervousness": 1, "uncontrollable_worry": 1})
        assert result.score == 2
        assert not result.positive

    def test_alternative_threshold_2_exposed(self) -> None:
        """USPSTF 2023 sensitivity-favoring alternative surfaced but not applied."""
        assert 2 in GAD2.alternative_thresholds


class TestHungerVitalSign:
    def test_both_never_true_negative(self) -> None:
        result = HUNGER_VITAL_SIGN.score(
            {"worry_food_would_run_out": 0, "food_did_not_last": 0}
        )
        assert result.score == 0
        assert not result.positive

    def test_sometimes_true_on_one_item_positive(self) -> None:
        result = HUNGER_VITAL_SIGN.score(
            {"worry_food_would_run_out": 1, "food_did_not_last": 0}
        )
        assert result.score == 1
        assert result.positive

    def test_often_true_on_one_item_positive(self) -> None:
        result = HUNGER_VITAL_SIGN.score(
            {"worry_food_would_run_out": 0, "food_did_not_last": 2}
        )
        assert result.score == 2
        assert result.positive

    def test_both_affirmative_positive(self) -> None:
        result = HUNGER_VITAL_SIGN.score(
            {"worry_food_would_run_out": 2, "food_did_not_last": 1}
        )
        assert result.positive


def test_scale_label_roundtrip() -> None:
    """value_for_label ↔ label_for_value are inverse for each option."""
    for instrument in (PHQ2, GAD2, HUNGER_VITAL_SIGN):
        for option in instrument.scale.options:
            assert (
                instrument.scale.value_for_label(option.label) == option.value
            )
            assert (
                instrument.scale.label_for_value(option.value) == option.label
            )


def test_instrument_ids_unique() -> None:
    trio: tuple[Instrument, ...] = (PHQ2, GAD2, HUNGER_VITAL_SIGN)
    ids = [i.instrument_id for i in trio]
    assert len(ids) == len(set(ids))
