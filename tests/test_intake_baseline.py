"""Baseline flow smoke — drives ``run_baseline_intake`` with a scripted prompter."""

from pathlib import Path
from typing import Callable

import pytest

from nutrime.app import initialize
from nutrime.intake.baseline import run_baseline_intake

SUBSTRATE_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "substrate"
OPERATIONAL_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "operational"


@pytest.fixture
def initialized_app(tmp_path: Path):
    data_dir = tmp_path / "nutrime-data"
    return initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )


def make_prompter(script: list[str]) -> Callable[[str], str]:
    it = iter(script)

    def prompter(_prompt: str) -> str:
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(
                "prompter script exhausted — baseline flow asked for more input"
            )

    return prompter


DEFAULT_SCRIPT: list[str] = [
    # demographics
    "1985",              # year of birth
    "female",            # sex assigned at birth
    "adult",             # life stage
    "170",               # height cm
    "68.5",              # weight kg
    # dietary + allergens
    "vegetarian",        # preferences
    "peanut, shellfish", # allergens
    # conditions + avoid-foods (parity with the web intake)
    "type 2 diabetes",   # conditions
    "cilantro",          # avoid foods
    "warfarin",          # medications (#46 drug–nutrient rails)
    # HVS (2 items) — never / sometimes → positive
    "never_true",
    "sometimes_true",
    # Sleep check (2 items) — fairly_bad + fairly_bad = 4 → positive
    "fairly_bad",
    "fairly_bad",
    # Energy check (2 items) — some_days + rarely = 1 → negative
    "some_days",
    "rarely_or_never",
]


def test_baseline_end_to_end_persists_and_scores(initialized_app) -> None:
    emitted: list[str] = []
    outcome = run_baseline_intake(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(list(DEFAULT_SCRIPT)),
        emitter=emitted.append,
    )

    assert outcome.profile.year_of_birth == 1985
    assert outcome.profile.life_stage == "adult"
    assert outcome.profile.dietary_preferences == ("vegetarian",)
    assert outcome.profile.allergens == ("peanut", "shellfish")

    by_id = {r.instrument_id: r for r in outcome.results}
    assert by_id["hunger_vital_sign"].score == 1
    assert by_id["sleep_check"].score == 4
    assert by_id["sleep_check"].positive
    assert by_id["energy_check"].score == 1
    assert not by_id["energy_check"].positive
    assert by_id["hunger_vital_sign"].positive

    (profile_count,) = initialized_app.substrate.execute(
        "SELECT COUNT(*) FROM intake_profile_v2"
    ).fetchone()
    assert profile_count == 1

    (response_count,) = initialized_app.substrate.execute(
        "SELECT COUNT(*) FROM intake_screener_response"
    ).fetchone()
    assert response_count == 6

    # Honest-disclosure surfaces at least once per instrument — every
    # disclosure says what the tool is NOT (diagnosis/assessment/instrument).
    disclosure_hits = sum(
        ("not a diagnosis" in line)
        or ("not a clinical" in line)
        or ("not a medical" in line)
        for line in emitted
    )
    assert disclosure_hits >= 3

    # 2026-10-06 audit: the CLI used to construct profiles without
    # conditions/avoid_foods, silently skipping the safety layer. The
    # scripted condition must now reach the condition-gating registry.
    assert outcome.profile.conditions == ("type 2 diabetes",)
    assert outcome.profile.avoid_foods == ("cilantro",)
    assert outcome.profile.medications == ("warfarin",)
    from nutrime.conditions import household_gates
    from nutrime.knowledge.derivation import sync_from_intake

    sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)
    gates = household_gates(
        initialized_app.substrate, initialized_app.tenant_id
    )
    assert any(
        "diabetes" in c.canonical for c in gates.conditions
    ), "CLI-disclosed condition must reach the gating registry"


def test_baseline_accepts_numeric_choice(initialized_app) -> None:
    """Users can type '1' instead of 'not_at_all' — same effect."""
    script = [
        "1985",
        "1",         # sex: female (choice 1)
        "4",         # life stage: adult (choice 4)
        "",          # skip height
        "",          # skip weight
        "",          # no preferences
        "",          # no allergens
        "",          # no conditions
        "",          # no avoid foods
        "",          # no medications
        "1", "1",    # PHQ-2 not_at_all x2
        "1", "1",    # GAD-2 not_at_all x2
        "1", "1",    # HVS never_true x2
    ]
    emitted: list[str] = []
    outcome = run_baseline_intake(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=emitted.append,
    )
    assert outcome.profile.sex_assigned_at_birth == "female"
    assert outcome.profile.life_stage == "adult"
    assert outcome.profile.height_cm is None
    assert outcome.profile.weight_kg is None
    assert all(not r.positive for r in outcome.results)


def test_baseline_reprompts_on_invalid_year(initialized_app) -> None:
    script = [
        "not-a-year",   # invalid year → reprompt
        "1985",
        "female",
        "adult",
        "", "",         # skip height + weight
        "", "",         # no preferences / allergens
        "", "", "",     # no conditions / avoid foods / medications
        "never_true", "never_true",
        "very_good", "very_good",
        "rarely_or_never", "rarely_or_never",
    ]
    emitted: list[str] = []
    outcome = run_baseline_intake(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=emitted.append,
    )
    assert outcome.profile.year_of_birth == 1985
    assert any("integer" in line for line in emitted)
