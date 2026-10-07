"""Consent records (#21) — baseline bootstrap, decisions, fail-closed gate."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.consent import (
    ConsentError,
    DATA_CATEGORIES,
    bootstrap_baseline,
    current_decision,
    list_current,
    record_decision,
    require_consent,
)


@pytest.fixture
def app(tmp_path: Path):
    application = initialize(data_dir=tmp_path)
    yield application
    application.substrate.close()
    application.operational.close()


class TestBaseline:
    def test_bootstrap_runs_at_initialize(self, app) -> None:
        rows = list_current(app.substrate, app.tenant_id)
        # every category x both purposes
        assert len(rows) == len(DATA_CATEGORIES) * 2

    def test_local_operation_granted_retroactive(self, app) -> None:
        record = current_decision(
            app.substrate, app.tenant_id, "intake_screener", "local_operation"
        )
        assert record.granted is True
        assert record.retroactive is True

    def test_publication_defaults_declined(self, app) -> None:
        record = current_decision(
            app.substrate, app.tenant_id, "meal_feedback_time",
            "publication_aggregate",
        )
        assert record.granted is False

    def test_rerun_is_idempotent(self, app) -> None:
        assert bootstrap_baseline(app.substrate, app.tenant_id) == 0


class TestDecisions:
    def test_supersede_chain(self, app) -> None:
        first = current_decision(
            app.substrate, app.tenant_id, "inventory", "publication_aggregate"
        )
        new_id = record_decision(
            app.substrate, app.tenant_id,
            data_category="inventory", purpose="publication_aggregate",
            granted=True, note="opting in",
        )
        now = current_decision(
            app.substrate, app.tenant_id, "inventory", "publication_aggregate"
        )
        assert now.id == new_id and now.granted is True
        # old row closed and linked forward
        row = app.substrate.execute(
            "SELECT valid_until, superseded_by FROM consent_record WHERE id = ?",
            (first.id,),
        ).fetchone()
        assert row[0] is not None and row[1] == new_id

    def test_unknown_category_rejected(self, app) -> None:
        with pytest.raises(ValueError):
            record_decision(
                app.substrate, app.tenant_id,
                data_category="telepathy", purpose="local_operation",
                granted=True,
            )


class TestEnforcement:
    """2026-10-06 audit: the Privacy toggles existed but inventory writes
    and knowledge derivation never consulted them."""

    def test_inventory_add_blocked_when_declined(self, app) -> None:
        from nutrime.inventory.store import InventoryItem, add_item

        record_decision(
            app.substrate, app.tenant_id,
            data_category="inventory", purpose="local_operation",
            granted=False, note="test decline",
        )
        with pytest.raises(ConsentError):
            add_item(
                app.substrate, app.tenant_id,
                InventoryItem(name="spinach", location="fridge"),
            )
        # Re-grant restores the path.
        record_decision(
            app.substrate, app.tenant_id,
            data_category="inventory", purpose="local_operation",
            granted=True, note="test re-grant",
        )
        item_id = add_item(
            app.substrate, app.tenant_id,
            InventoryItem(name="spinach", location="fridge"),
        )
        assert item_id > 0

    def _save_profile(self, app, member_id: str) -> None:
        from nutrime.intake.store import IntakeProfile, save_member_profile

        save_member_profile(
            app.substrate, app.tenant_id, member_id,
            IntakeProfile(
                year_of_birth=1990, sex_assigned_at_birth="female",
                life_stage="adult",
                dietary_preferences=("mediterranean",),
                allergens=("peanuts",),
            ),
        )

    def test_derivation_stamps_consent_and_splits_safety(self, app) -> None:
        from nutrime.knowledge.derivation import sync_from_intake
        from nutrime.knowledge.store import list_atoms

        member_id = app.default_member_id
        self._save_profile(app, member_id)

        # Decline knowledge_derived for this member: convenience
        # derivations stop; SAFETY derivation (the allergy) continues.
        record_decision(
            app.substrate, app.tenant_id,
            data_category="knowledge_derived", purpose="local_operation",
            granted=False, member_id=member_id, note="test decline",
        )
        sync_from_intake(app.substrate, app.tenant_id)

        disclosures = [
            a for a in list_atoms(
                app.substrate, app.tenant_id, atom_type="clinical_disclosure"
            )
            if a.subject_id == member_id
        ]
        assert any(
            a.payload.get("disclosure_text") == "peanuts" for a in disclosures
        ), "allergy derivation must survive a knowledge_derived decline"
        assert all(a.consent_record_id for a in disclosures), (
            "safety atoms must be stamped with the intake_profile grant"
        )
        preferences = [
            a for a in list_atoms(
                app.substrate, app.tenant_id, atom_type="preference_statement"
            )
            if a.subject_id == member_id
        ]
        assert preferences == [], (
            "preference derivation must honor the decline"
        )

        # Re-grant: preferences derive now, stamped with the new record.
        grant_id = record_decision(
            app.substrate, app.tenant_id,
            data_category="knowledge_derived", purpose="local_operation",
            granted=True, member_id=member_id, note="test re-grant",
        )
        sync_from_intake(app.substrate, app.tenant_id)
        preferences = [
            a for a in list_atoms(
                app.substrate, app.tenant_id, atom_type="preference_statement"
            )
            if a.subject_id == member_id
        ]
        assert preferences, "re-grant must resume derivation"
        assert all(a.consent_record_id == grant_id for a in preferences)


class TestGate:
    def test_granted_returns_record_id(self, app) -> None:
        consent_id = require_consent(
            app.substrate, app.tenant_id, "meal_feedback_time"
        )
        assert consent_id.startswith("cns-")

    def test_declined_blocks(self, app) -> None:
        record_decision(
            app.substrate, app.tenant_id,
            data_category="meal_feedback_semantic", purpose="local_operation",
            granted=False, note="user said no",
        )
        with pytest.raises(ConsentError):
            require_consent(
                app.substrate, app.tenant_id, "meal_feedback_semantic"
            )
