"""Typed instrument definitions for the MVP screener trio.

Cutoffs verified 2026-06-30 against Kroenke originals (PHQ-2 2003, GAD-2 2007),
USPSTF 2023 anxiety-in-adults recommendation, Children's HealthWatch canonical
source, and PMC validation studies. See ``stage3-plan.md`` § "Component
verification log — Step 2 sub-commit 2.1" for the full refresh table.

Each instrument owns its items + response scale + scoring rule + positive-
screen threshold. Scoring is pure — no I/O. Persistence is a separate concern
(``store.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping


@dataclass(frozen=True)
class ResponseOption:
    label: str
    value: int


@dataclass(frozen=True)
class ResponseScale:
    """A shared response scale used by an instrument's items."""

    name: str
    options: tuple[ResponseOption, ...]

    def value_for_label(self, label: str) -> int:
        for option in self.options:
            if option.label == label:
                return option.value
        raise ValueError(
            f"response label {label!r} not in scale {self.name!r};"
            f" expected one of {[o.label for o in self.options]}"
        )

    def label_for_value(self, value: int) -> str:
        for option in self.options:
            if option.value == value:
                return option.label
        raise ValueError(
            f"response value {value!r} not in scale {self.name!r};"
            f" expected one of {[o.value for o in self.options]}"
        )


@dataclass(frozen=True)
class InstrumentItem:
    item_id: str
    prompt: str


@dataclass(frozen=True)
class ScreenerResult:
    instrument_id: str
    instrument_version: str
    responses: Mapping[str, int]
    score: int
    positive: bool
    disclosure: str


@dataclass(frozen=True)
class Instrument:
    instrument_id: str
    instrument_version: str
    full_name: str
    items: tuple[InstrumentItem, ...]
    scale: ResponseScale
    positive_threshold: int
    scorer: Callable[[Mapping[str, int]], int]
    disclosure: str
    # GAD-2 carries a second alternative cutoff per USPSTF 2023 — surfaced but
    # not applied by default.
    alternative_thresholds: tuple[int, ...] = field(default_factory=tuple)

    def score(self, responses: Mapping[str, int]) -> ScreenerResult:
        for item in self.items:
            if item.item_id not in responses:
                raise ValueError(
                    f"missing response for item {item.item_id!r}"
                    f" of instrument {self.instrument_id!r}"
                )
        for item_id in responses:
            if not any(i.item_id == item_id for i in self.items):
                raise ValueError(
                    f"unknown item {item_id!r}"
                    f" for instrument {self.instrument_id!r}"
                )
        for item_id, value in responses.items():
            valid_values = {o.value for o in self.scale.options}
            if value not in valid_values:
                raise ValueError(
                    f"response value {value!r} for item {item_id!r}"
                    f" outside {self.scale.name!r} scale {sorted(valid_values)}"
                )
        total = self.scorer(responses)
        return ScreenerResult(
            instrument_id=self.instrument_id,
            instrument_version=self.instrument_version,
            responses=dict(responses),
            score=total,
            positive=total >= self.positive_threshold,
            disclosure=self.disclosure,
        )


_PHQ_GAD_SCALE = ResponseScale(
    name="phq_gad_frequency_last_2_weeks",
    options=(
        ResponseOption("not_at_all", 0),
        ResponseOption("several_days", 1),
        ResponseOption("more_than_half_the_days", 2),
        ResponseOption("nearly_every_day", 3),
    ),
)

_HVS_SCALE = ResponseScale(
    name="hunger_vital_sign_frequency_last_12_months",
    options=(
        ResponseOption("never_true", 0),
        ResponseOption("sometimes_true", 1),
        ResponseOption("often_true", 2),
    ),
)


def _sum_items(responses: Mapping[str, int]) -> int:
    return sum(responses.values())


def _max_items(responses: Mapping[str, int]) -> int:
    return max(responses.values())


PHQ2 = Instrument(
    instrument_id="phq2",
    instrument_version="kroenke_2003",
    full_name="Patient Health Questionnaire-2 (depression)",
    items=(
        InstrumentItem(
            item_id="anhedonia",
            prompt=(
                "Over the last 2 weeks, how often have you been bothered by"
                " little interest or pleasure in doing things?"
            ),
        ),
        InstrumentItem(
            item_id="depressed_mood",
            prompt=(
                "Over the last 2 weeks, how often have you been bothered by"
                " feeling down, depressed, or hopeless?"
            ),
        ),
    ),
    scale=_PHQ_GAD_SCALE,
    positive_threshold=3,
    scorer=_sum_items,
    disclosure=(
        "The PHQ-2 is a screening tool, not a diagnosis. A positive result"
        " suggests a fuller assessment (PHQ-9) or a conversation with a"
        " qualified clinician would be worthwhile."
    ),
)

GAD2 = Instrument(
    instrument_id="gad2",
    instrument_version="kroenke_2007",
    full_name="Generalized Anxiety Disorder-2 (anxiety)",
    items=(
        InstrumentItem(
            item_id="nervousness",
            prompt=(
                "Over the last 2 weeks, how often have you been bothered by"
                " feeling nervous, anxious, or on edge?"
            ),
        ),
        InstrumentItem(
            item_id="uncontrollable_worry",
            prompt=(
                "Over the last 2 weeks, how often have you been bothered by"
                " not being able to stop or control worrying?"
            ),
        ),
    ),
    scale=_PHQ_GAD_SCALE,
    positive_threshold=3,
    # USPSTF 2023 anxiety-in-adults presents ≥2 as a sensitivity-favoring
    # alternative; keep ≥3 as default (standard clinical practice) but expose
    # ≥2 so future in-use tuning can raise sensitivity if under-flagging.
    alternative_thresholds=(2,),
    scorer=_sum_items,
    disclosure=(
        "The GAD-2 is a screening tool, not a diagnosis. A positive result"
        " suggests a fuller assessment (GAD-7) or a conversation with a"
        " qualified clinician would be worthwhile."
    ),
)

HUNGER_VITAL_SIGN = Instrument(
    instrument_id="hunger_vital_sign",
    instrument_version="hager_2010",
    full_name="Hunger Vital Sign (household food insecurity)",
    items=(
        InstrumentItem(
            item_id="worry_food_would_run_out",
            prompt=(
                "Within the past 12 months we worried whether our food would"
                " run out before we got money to buy more."
            ),
        ),
        InstrumentItem(
            item_id="food_did_not_last",
            prompt=(
                "Within the past 12 months the food we bought just didn't last"
                " and we didn't have money to get more."
            ),
        ),
    ),
    scale=_HVS_SCALE,
    # Hager 2010: positive if EITHER item is "often true" OR "sometimes true"
    # (i.e., any item ≥ 1). Encoded as max-of-items ≥ 1, matching the
    # positive_threshold field semantics.
    positive_threshold=1,
    scorer=_max_items,
    disclosure=(
        "The Hunger Vital Sign is a screening tool, not a diagnosis. A"
        " positive result identifies household food-insecurity risk and does"
        " not, on its own, mean a household is food insecure."
    ),
)
