import json
import sqlite3
import uuid
from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.knowledge.ids import new_atom_id, new_synthesized_entry_id, uuid7
from nutrime.knowledge.store import (
    Provenance,
    RetractionReason,
    SubjectType,
    insert_atom,
    insert_synthesized_entry,
    list_atoms,
    list_synthesized_entries,
    retract_entry,
)
from nutrime.phi import PhiCategory

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


class TestIdGeneration:
    def test_uuid7_shape(self) -> None:
        raw = uuid7()
        parsed = uuid.UUID(raw)
        assert parsed.version == 7
        assert (parsed.int >> 62) & 0x3 == 0x2  # variant 10xx

    def test_typed_prefixes(self) -> None:
        assert new_atom_id().startswith("atm-")
        assert new_synthesized_entry_id().startswith("syn-")

    def test_ids_are_unique(self) -> None:
        ids = {new_atom_id() for _ in range(200)}
        assert len(ids) == 200


class TestAtomInsertList:
    def test_insert_and_list(self, initialized_app) -> None:
        entry_id = insert_atom(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={
                "preference_type": "dietary_pattern_preference",
                "subject_text": "vegetarian",
                "strength": "strong",
                "preference_format": "plain",
            },
            phi_categories=(),
        )
        atoms = list_atoms(initialized_app.substrate, initialized_app.tenant_id)
        assert len(atoms) == 1
        assert atoms[0].id == entry_id
        assert atoms[0].type == "preference_statement"
        assert atoms[0].payload["subject_text"] == "vegetarian"
        assert atoms[0].subject_id == initialized_app.tenant_id
        assert atoms[0].subject_type == SubjectType.USER.value
        assert atoms[0].phi_categories == ()

    def test_phi_categories_persisted_sorted(self, initialized_app) -> None:
        insert_atom(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="clinical_disclosure",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={
                "disclosure_type": "allergy",
                "disclosure_text": "peanuts",
                "disclosure_text_format": "plain",
                "disclosure_source": "self_reported_intake",
            },
            phi_categories=(PhiCategory.ALLERGENS, PhiCategory.DEMOGRAPHICS),
        )
        atoms = list_atoms(initialized_app.substrate, initialized_app.tenant_id)
        assert atoms[0].phi_categories == ("allergens", "demographics")

    def test_filter_by_type(self, initialized_app) -> None:
        insert_atom(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={"preference_type": "x", "subject_text": "italian",
                     "strength": "mild", "preference_format": "plain"},
        )
        insert_atom(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="clinical_disclosure",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={"disclosure_type": "allergy", "disclosure_text": "peanuts",
                     "disclosure_text_format": "plain",
                     "disclosure_source": "self_reported_intake"},
            phi_categories=(PhiCategory.ALLERGENS,),
        )
        prefs = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
        )
        assert len(prefs) == 1
        assert prefs[0].type == "preference_statement"


class TestSynthesizedEntry:
    def test_insert_and_list(self, initialized_app) -> None:
        insert_synthesized_entry(
            initialized_app.substrate,
            initialized_app.tenant_id,
            entry_type="abstracted_constraint",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={
                "household_id": initialized_app.tenant_id,
                "source_member_id": initialized_app.tenant_id,
                "abstracted_text": "avoids peanuts",
                "sharing_level": "constraint_only_automatic",
            },
        )
        entries = list_synthesized_entries(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert len(entries) == 1
        assert entries[0].payload["abstracted_text"] == "avoids peanuts"
        assert entries[0].id.startswith("syn-")


class TestRetraction:
    def test_retract_hides_from_currently_valid(self, initialized_app) -> None:
        entry_id = insert_atom(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={"preference_type": "x", "subject_text": "italian",
                     "strength": "mild", "preference_format": "plain"},
        )
        assert retract_entry(
            initialized_app.substrate,
            initialized_app.tenant_id,
            entry_id,
            RetractionReason.USER_CORRECTION,
        )
        current = list_atoms(initialized_app.substrate, initialized_app.tenant_id)
        assert current == []
        all_rows = list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            currently_valid=False,
        )
        assert len(all_rows) == 1
        assert all_rows[0].valid_until is not None
        assert all_rows[0].retraction_reason == "retracted_user_correction"

    def test_retract_missing_returns_false(self, initialized_app) -> None:
        assert not retract_entry(
            initialized_app.substrate,
            initialized_app.tenant_id,
            "atm-does-not-exist",
            RetractionReason.SUPERSEDED,
        )


class TestSchemaEnforcement:
    def test_rejects_bad_provenance(self, initialized_app) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            initialized_app.substrate.execute(
                "INSERT INTO atom ("
                " id, tenant_id, type, provenance,"
                " valid_from, recorded_at,"
                " system_version, payload_schema_version, payload)"
                " VALUES (?, ?, 'x', 'not-a-provenance', ?, ?, '0', 'v1', '{}')",
                (
                    "atm-bad",
                    initialized_app.tenant_id,
                    "2026-06-30T00:00:00Z",
                    "2026-06-30T00:00:00Z",
                ),
            )

    def test_rejects_invalid_phi_categories_json(self, initialized_app) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            initialized_app.substrate.execute(
                "INSERT INTO atom ("
                " id, tenant_id, type, provenance,"
                " valid_from, recorded_at,"
                " system_version, payload_schema_version,"
                " phi_categories, payload)"
                " VALUES (?, ?, 'x', 'validated-instrument',"
                " ?, ?, '0', 'v1', 'not-json', '{}')",
                (
                    "atm-bad",
                    initialized_app.tenant_id,
                    "2026-06-30T00:00:00Z",
                    "2026-06-30T00:00:00Z",
                ),
            )

    def test_rejects_bad_payload_json(self, initialized_app) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            initialized_app.substrate.execute(
                "INSERT INTO atom ("
                " id, tenant_id, type, provenance,"
                " valid_from, recorded_at,"
                " system_version, payload_schema_version, payload)"
                " VALUES (?, ?, 'x', 'validated-instrument', ?, ?, '0', 'v1', 'not-json')",
                (
                    "atm-bad",
                    initialized_app.tenant_id,
                    "2026-06-30T00:00:00Z",
                    "2026-06-30T00:00:00Z",
                ),
            )

    def test_foreign_key_cascade(self, initialized_app) -> None:
        insert_atom(
            initialized_app.substrate,
            initialized_app.tenant_id,
            atom_type="preference_statement",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={"preference_type": "x", "subject_text": "italian",
                     "strength": "mild", "preference_format": "plain"},
        )
        initialized_app.substrate.execute(
            "DELETE FROM tenant WHERE id = ?", (initialized_app.tenant_id,)
        )
        initialized_app.substrate.commit()
        assert list_atoms(
            initialized_app.substrate,
            initialized_app.tenant_id,
            currently_valid=False,
        ) == []

    def test_foreign_key_prevents_orphan(self, initialized_app) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            insert_atom(
                initialized_app.substrate,
                "not-a-tenant",
                atom_type="preference_statement",
                provenance=Provenance.CONVERSATIONAL_ELICITATION,
                payload={"preference_type": "x", "subject_text": "italian",
                         "strength": "mild", "preference_format": "plain"},
            )
