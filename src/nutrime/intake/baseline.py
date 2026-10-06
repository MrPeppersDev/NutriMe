"""First-run baseline intake flow — one-shot administration of the MVP trio + profile capture.

The flow is I/O-parameterized so tests can drive it without stdin/stdout: a
:class:`Prompter` callable receives a message and returns the raw user string.
The CLI wires ``builtins.input`` + ``print``; tests inject a pre-scripted
prompter.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable, Iterable

from nutrime.intake.instruments import (
    ENERGY_CHECK,
    SLEEP_CHECK,
    GAD2,
    HUNGER_VITAL_SIGN,
    PHQ2,
    Instrument,
    ScreenerResult,
)
from nutrime.intake.store import IntakeProfile, save_profile, save_screener_responses

Prompter = Callable[[str], str]
Emitter = Callable[[str], None]

# Direction reset 2026-10-06: physical-health spine. The mental-health
# pair (PHQ-2/GAD-2) stays importable for opt-in use but leaves the
# default flow — this product assesses physical/nutritional needs.
MVP_INSTRUMENTS: tuple[Instrument, ...] = (
    HUNGER_VITAL_SIGN,
    SLEEP_CHECK,
    ENERGY_CHECK,
)


@dataclass(frozen=True)
class BaselineOutcome:
    profile: IntakeProfile
    results: tuple[ScreenerResult, ...]


def _ask_choice(
    prompter: Prompter, emitter: Emitter, prompt: str, choices: Iterable[str]
) -> str:
    choice_list = list(choices)
    while True:
        emitter(prompt)
        for i, choice in enumerate(choice_list, start=1):
            emitter(f"  {i}) {choice}")
        raw = prompter("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choice_list):
            return choice_list[int(raw) - 1]
        if raw in choice_list:
            return raw
        emitter(
            f"Please pick a number 1–{len(choice_list)} or one of the labels."
        )


def _ask_int(
    prompter: Prompter,
    emitter: Emitter,
    prompt: str,
    *,
    minimum: int,
    maximum: int,
) -> int:
    while True:
        emitter(prompt)
        raw = prompter("> ").strip()
        try:
            value = int(raw)
        except ValueError:
            emitter(f"Please enter an integer between {minimum} and {maximum}.")
            continue
        if minimum <= value <= maximum:
            return value
        emitter(f"Value must be between {minimum} and {maximum}.")


def _ask_optional_int(
    prompter: Prompter,
    emitter: Emitter,
    prompt: str,
    *,
    minimum: int,
    maximum: int,
) -> int | None:
    while True:
        emitter(prompt + " (leave blank to skip)")
        raw = prompter("> ").strip()
        if raw == "":
            return None
        try:
            value = int(raw)
        except ValueError:
            emitter(f"Please enter an integer between {minimum} and {maximum}.")
            continue
        if minimum <= value <= maximum:
            return value
        emitter(f"Value must be between {minimum} and {maximum}.")


def _ask_optional_float(
    prompter: Prompter,
    emitter: Emitter,
    prompt: str,
    *,
    minimum: float,
    maximum: float,
) -> float | None:
    while True:
        emitter(prompt + " (leave blank to skip)")
        raw = prompter("> ").strip()
        if raw == "":
            return None
        try:
            value = float(raw)
        except ValueError:
            emitter(
                f"Please enter a number between {minimum} and {maximum}."
            )
            continue
        if minimum <= value <= maximum:
            return value
        emitter(f"Value must be between {minimum} and {maximum}.")


def _ask_list(prompter: Prompter, emitter: Emitter, prompt: str) -> tuple[str, ...]:
    emitter(prompt + " (comma-separated; leave blank for none)")
    raw = prompter("> ").strip()
    if not raw:
        return ()
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _collect_profile(prompter: Prompter, emitter: Emitter) -> IntakeProfile:
    emitter("— demographics —")
    year_of_birth = _ask_int(
        prompter,
        emitter,
        "What year were you born?",
        minimum=1900,
        maximum=2100,
    )
    sex_assigned_at_birth = _ask_choice(
        prompter,
        emitter,
        "Sex assigned at birth (used for DRI band lookup):",
        ("female", "male", "intersex", "prefer_not_to_say"),
    )
    life_stage = _ask_choice(
        prompter,
        emitter,
        "Current life stage (used for DRI band lookup):",
        (
            "infant",
            "child",
            "adolescent",
            "adult",
            "pregnant",
            "lactating",
            "older_adult",
        ),
    )
    height_cm = _ask_optional_int(
        prompter,
        emitter,
        "Height in centimeters?",
        minimum=30,
        maximum=275,
    )
    weight_kg = _ask_optional_float(
        prompter,
        emitter,
        "Weight in kilograms?",
        minimum=1,
        maximum=500,
    )
    emitter("— dietary preferences + allergens —")
    dietary_preferences = _ask_list(
        prompter,
        emitter,
        "Dietary preferences (e.g. vegetarian, vegan, halal, kosher):",
    )
    allergens = _ask_list(
        prompter,
        emitter,
        "Food allergens to avoid (e.g. peanut, shellfish, gluten):",
    )
    return IntakeProfile(
        year_of_birth=year_of_birth,
        sex_assigned_at_birth=sex_assigned_at_birth,
        life_stage=life_stage,
        height_cm=height_cm,
        weight_kg=weight_kg,
        dietary_preferences=dietary_preferences,
        allergens=allergens,
    )


def _administer_instrument(
    prompter: Prompter, emitter: Emitter, instrument: Instrument
) -> ScreenerResult:
    emitter(f"— {instrument.full_name} —")
    # Honest-disclosure: consult-professional callout up-front, per
    # constitutional-rules.md Rule 4 (honest disclosure surfacing).
    emitter(instrument.disclosure)
    labels = tuple(o.label for o in instrument.scale.options)
    responses: dict[str, int] = {}
    for item in instrument.items:
        chosen = _ask_choice(prompter, emitter, item.prompt, labels)
        responses[item.item_id] = instrument.scale.value_for_label(chosen)
    result = instrument.score(responses)
    if result.positive:
        emitter(
            f"Score: {result.score} — above the {instrument.instrument_id.upper()}"
            f" cutoff (≥{instrument.positive_threshold})."
        )
    else:
        emitter(
            f"Score: {result.score} — below the {instrument.instrument_id.upper()}"
            f" cutoff (≥{instrument.positive_threshold})."
        )
    return result


def run_baseline_intake(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    prompter: Prompter,
    emitter: Emitter = print,
) -> BaselineOutcome:
    """Run the full one-shot baseline intake and persist the results."""
    emitter(
        "First-run baseline intake — one-shot; you can update this later."
    )
    profile = _collect_profile(prompter, emitter)
    save_profile(conn, tenant_id, profile)

    results: list[ScreenerResult] = []
    for instrument in MVP_INSTRUMENTS:
        result = _administer_instrument(prompter, emitter, instrument)
        save_screener_responses(conn, tenant_id, instrument, result.responses)
        results.append(result)

    emitter("Baseline intake saved. You can re-run this to update anytime.")
    return BaselineOutcome(profile=profile, results=tuple(results))
