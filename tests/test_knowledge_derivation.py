"""End-to-end derivation from intake data to knowledge-model rows."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.intake.instruments import GAD2, HUNGER_VITAL_SIGN, PHQ2
from nutrime.intake.store import IntakeProfile, save_profile, save_screener_responses
from nutrime.knowledge.derivation import sync_from_intake
from nutrime.knowledge.store import list_atoms, list_synthesized_entries

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


def _seed_profile(
    app,
    *,
    allergens: tuple[str, ...] = ("peanut", "shellfish"),
    preferences: tuple[str, ...] = ("vegetarian",),
) -> None:
    save_profile(
        app.substrate,
        app.tenant_id,
        IntakeProfile(
            year_of_birth=1985,
            sex_assigned_at_birth="female",
            life_stage="adult",
            dietary_preferences=preferences,
            allergens=allergens,
        ),
    )


def _seed_positive_phq2(app, administered_at: str = "2026-06-30T12:00:00Z") -> None:
    save_screener_responses(
        app.substrate,
        app.tenant_id,
        PHQ2,
        {"anhedonia": 2, "depressed_mood": 2},
        administered_at=administered_at,
    )


def _seed_negative_gad2(app, administered_at: str = "2026-06-30T12:00:00Z") -> None:
    save_screener_responses(
        app.substrate,
        app.tenant_id,
        GAD2,
        {"nervousness": 0, "uncontrollable_worry": 0},
        administered_at=administered_at,
    )


def _seed_positive_hvs(app, administered_at: str = "2026-06-30T12:00:00Z") -> None:
    save_screener_responses(
        app.substrate,
        app.tenant_id,
        HUNGER_VITAL_SIGN,
        {"worry_food_would_run_out": 1, "food_did_not_last": 0},
        administered_at=administered_at,
    )


class TestSyncCreatesAtoms:
    def test_from_profile_and_screeners(self, initialized_app) -> None:
        _seed_profile(initialized_app)
        _seed_positive_phq2(initialized_app)
        _seed_negative_gad2(initialized_app)
        _seed_positive_hvs(initialized_app)

        outcome = sync_from_intake(
            initialized_app.substrate, initialized_app.tenant_id
        )

        assert outcome.atoms_added["clinical_disclosure"] == 2
        assert outcome.atoms_added["preference_statement"] == 1
        assert outcome.atoms_added["screener_result"] == 3
        assert outcome.constraints_added == 3  # 2 allergens + 1 preference

        disclosures = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="clinical_disclosure",
        )
        allergens_seen = {a.payload["disclosure_text"] for a in disclosures}
        assert allergens_seen == {"peanut", "shellfish"}

        preferences = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
        )
        assert preferences[0].payload["subject_text"] == "vegetarian"

        constraints = list_synthesized_entries(
            initialized_app.substrate,
            initialized_app.tenant_id,
            entry_type="abstracted_constraint",
        )
        texts = {c.payload["abstracted_text"] for c in constraints}
        assert texts == {"avoids peanut", "avoids shellfish", "prefers vegetarian"}

    def test_screener_result_captures_score_and_positive(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=(), preferences=())
        _seed_positive_phq2(initialized_app)

        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)

        screeners = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="screener_result",
        )
        assert len(screeners) == 1
        payload = screeners[0].payload
        assert payload["instrument_id"] == "phq2"
        assert payload["score"] == 4
        assert payload["score_interpretation"] == "positive"
        assert payload["positive_threshold"] == 3
        assert payload["scoring_method"] == "sum_score"
        assert len(payload["per_item_responses"]) == 2

    def test_hvs_uses_max_scoring(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=(), preferences=())
        _seed_positive_hvs(initialized_app)

        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)

        screeners = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="screener_result",
        )
        payload = screeners[0].payload
        assert payload["scoring_method"] == "max_item"
        assert payload["score"] == 1
        assert payload["score_interpretation"] == "positive"

    def test_valid_from_matches_administered_at(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=(), preferences=())
        _seed_positive_phq2(initialized_app, administered_at="2026-06-15T09:00:00Z")

        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)

        screeners = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="screener_result",
        )
        assert screeners[0].valid_from == "2026-06-15T09:00:00Z"


class TestPhiCategoryTagging:
    def test_allergen_atoms_carry_allergens(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=("peanut",), preferences=())
        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)
        atoms = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="clinical_disclosure",
        )
        assert atoms[0].phi_categories == ("allergens",)

    def test_preference_atoms_have_no_phi(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=(), preferences=("vegan",))
        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)
        atoms = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
        )
        assert atoms[0].phi_categories == ()

    def test_screener_atoms_carry_intake_screener(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=(), preferences=())
        _seed_positive_phq2(initialized_app)
        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)
        atoms = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="screener_result",
        )
        assert atoms[0].phi_categories == ("intake_screener",)


class TestIdempotency:
    def test_second_sync_is_noop(self, initialized_app) -> None:
        _seed_profile(initialized_app)
        _seed_positive_phq2(initialized_app)
        _seed_negative_gad2(initialized_app)
        _seed_positive_hvs(initialized_app)

        sync_from_intake(initialized_app.substrate, initialized_app.tenant_id)
        second = sync_from_intake(
            initialized_app.substrate, initialized_app.tenant_id
        )

        assert second.total_atoms_added == 0
        assert second.constraints_added == 0

        atoms = list_atoms(initialized_app.substrate, initialized_app.tenant_id)
        assert len(atoms) == 2 + 1 + 3
        constraints = list_synthesized_entries(
            initialized_app.substrate,
            initialized_app.tenant_id,
            entry_type="abstracted_constraint",
        )
        assert len(constraints) == 3


class TestEmptyInputs:
    def test_no_profile_no_screeners_yields_nothing(self, initialized_app) -> None:
        outcome = sync_from_intake(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert outcome.total_atoms_added == 0
        assert outcome.constraints_added == 0

    def test_profile_with_empty_lists_yields_no_atoms(self, initialized_app) -> None:
        _seed_profile(initialized_app, allergens=(), preferences=())
        outcome = sync_from_intake(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert outcome.total_atoms_added == 0
        assert outcome.constraints_added == 0

    def test_screeners_only_no_constraints(self, initialized_app) -> None:
        _seed_positive_phq2(initialized_app)
        outcome = sync_from_intake(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert outcome.atoms_added.get("screener_result") == 1
        assert outcome.constraints_added == 0
