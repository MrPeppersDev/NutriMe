"""Read step-2 intake data and derive knowledge-model rows.

Reads:
- ``intake_profile`` — allergens list, dietary_preferences list.
- ``intake_screener_response`` — grouped by (instrument_id, administered_at).

Emits atoms:
- ``clinical_disclosure`` — one per allergen (disclosure_type='allergy').
- ``preference_statement`` — one per dietary preference.
- ``screener_result`` — one per screener administration batch.

Then emits ``abstracted_constraint`` synthesized entries derived from the
currently-valid allergy + preference atoms — the Option-B constraint stub.

Idempotent: existing currently-valid rows with matching identity keys are
skipped on re-run. Retraction / supersession semantics stay unused here; the
initial derivation is add-only over stable user-declared inputs.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field

from nutrime.intake.instruments import GAD2, HUNGER_VITAL_SIGN, PHQ2, Instrument
from nutrime.knowledge.store import (
    KnowledgeRecord,
    Provenance,
    insert_atom,
    insert_synthesized_entry,
    list_atoms,
    list_synthesized_entries,
)
from nutrime.phi import PhiCategory

_MVP_INSTRUMENTS: dict[str, Instrument] = {
    PHQ2.instrument_id: PHQ2,
    GAD2.instrument_id: GAD2,
    HUNGER_VITAL_SIGN.instrument_id: HUNGER_VITAL_SIGN,
}


@dataclass
class DerivationOutcome:
    """Summary of what a sync pass added; keys are atom / entry types."""

    atoms_added: dict[str, int] = field(default_factory=dict)
    constraints_added: int = 0

    def bump_atom(self, atom_type: str) -> None:
        self.atoms_added[atom_type] = self.atoms_added.get(atom_type, 0) + 1

    @property
    def total_atoms_added(self) -> int:
        return sum(self.atoms_added.values())


def _load_profile(
    conn: sqlite3.Connection, tenant_id: str
) -> tuple[list[str], list[str]] | None:
    row = conn.execute(
        "SELECT allergens, dietary_preferences FROM intake_profile"
        " WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchone()
    if row is None:
        return None
    allergens = json.loads(row[0])
    preferences = json.loads(row[1])
    return allergens, preferences


def _load_screener_batches(
    conn: sqlite3.Connection, tenant_id: str
) -> list[tuple[str, str, str, dict[str, int]]]:
    """Return [(instrument_id, instrument_version, administered_at, {item_id: value})]."""
    rows = conn.execute(
        "SELECT instrument_id, instrument_version, administered_at,"
        " item_id, response_value FROM intake_screener_response"
        " WHERE tenant_id = ?"
        " ORDER BY instrument_id, administered_at, item_id",
        (tenant_id,),
    ).fetchall()
    grouped: dict[tuple[str, str, str], dict[str, int]] = {}
    for instrument_id, version, administered_at, item_id, value in rows:
        key = (instrument_id, version, administered_at)
        grouped.setdefault(key, {})[item_id] = value
    return [
        (instrument_id, version, administered_at, responses)
        for (instrument_id, version, administered_at), responses in grouped.items()
    ]


def _payload_matches(
    existing: list[KnowledgeRecord], **fields: object
) -> bool:
    for record in existing:
        if all(record.payload.get(k) == v for k, v in fields.items()):
            return True
    return False


def _sync_allergens(
    conn: sqlite3.Connection,
    tenant_id: str,
    allergens: list[str],
    outcome: DerivationOutcome,
) -> None:
    existing = list_atoms(conn, tenant_id, atom_type="clinical_disclosure")
    for allergen in allergens:
        if _payload_matches(
            existing, disclosure_type="allergy", disclosure_text=allergen
        ):
            continue
        insert_atom(
            conn,
            tenant_id,
            atom_type="clinical_disclosure",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={
                "disclosure_type": "allergy",
                "disclosure_text": allergen,
                "disclosure_text_format": "plain",
                "disclosure_source": "self_reported_intake",
            },
            phi_categories=(PhiCategory.ALLERGENS,),
            source_identity=f"intake_profile:{tenant_id}",
        )
        outcome.bump_atom("clinical_disclosure")


def _sync_preferences(
    conn: sqlite3.Connection,
    tenant_id: str,
    preferences: list[str],
    outcome: DerivationOutcome,
) -> None:
    existing = list_atoms(conn, tenant_id, atom_type="preference_statement")
    for preference in preferences:
        if _payload_matches(
            existing,
            preference_type="dietary_pattern_preference",
            subject_text=preference,
        ):
            continue
        insert_atom(
            conn,
            tenant_id,
            atom_type="preference_statement",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={
                "preference_type": "dietary_pattern_preference",
                "subject_text": preference,
                "strength": "strong",
                "preference_format": "plain",
            },
            phi_categories=(),
            source_identity=f"intake_profile:{tenant_id}",
        )
        outcome.bump_atom("preference_statement")


def _sync_screener_results(
    conn: sqlite3.Connection,
    tenant_id: str,
    outcome: DerivationOutcome,
) -> None:
    existing = list_atoms(conn, tenant_id, atom_type="screener_result")
    batches = _load_screener_batches(conn, tenant_id)
    for instrument_id, version, administered_at, responses in batches:
        instrument = _MVP_INSTRUMENTS.get(instrument_id)
        if instrument is None:
            continue
        if _payload_matches(
            existing,
            instrument_id=instrument_id,
            instrument_version=version,
            administered_at=administered_at,
        ):
            continue
        result = instrument.score(responses)
        insert_atom(
            conn,
            tenant_id,
            atom_type="screener_result",
            provenance=Provenance.VALIDATED_INSTRUMENT,
            payload={
                "instrument_id": instrument.instrument_id,
                "instrument_name": instrument.full_name,
                "instrument_version": instrument.instrument_version,
                "administered_at": administered_at,
                "score": result.score,
                "score_interpretation": "positive" if result.positive else "negative",
                "scoring_method": "sum_score"
                    if instrument.scorer.__name__ == "_sum_items"
                    else "max_item",
                "positive_threshold": instrument.positive_threshold,
                "per_item_responses": [
                    {"item_id": item_id, "response_value": value}
                    for item_id, value in sorted(result.responses.items())
                ],
            },
            phi_categories=(PhiCategory.INTAKE_SCREENER,),
            source_identity=(
                f"intake_screener_response:{instrument_id}:{administered_at}"
            ),
            valid_from=administered_at,
        )
        outcome.bump_atom("screener_result")


def _sync_abstracted_constraints(
    conn: sqlite3.Connection,
    tenant_id: str,
    outcome: DerivationOutcome,
) -> None:
    """Emit synthesized_entry abstracted_constraint rows from user-declared atoms.

    Life-stage / DRI-derived constraints are deferred out of the initial slice.
    """
    existing = list_synthesized_entries(
        conn, tenant_id, entry_type="abstracted_constraint"
    )

    def constraint_exists(text: str) -> bool:
        return any(r.payload.get("abstracted_text") == text for r in existing)

    def emit(abstracted_text: str, source_atom: KnowledgeRecord) -> None:
        insert_synthesized_entry(
            conn,
            tenant_id,
            entry_type="abstracted_constraint",
            provenance=Provenance(source_atom.provenance),
            payload={
                "household_id": tenant_id,
                "source_member_id": tenant_id,
                "abstracted_text": abstracted_text,
                "sharing_level": "constraint_only_automatic",
                "derived_from_atom_ids": [source_atom.id],
            },
            source_identity=source_atom.id,
            phi_categories=(),
        )
        outcome.constraints_added += 1

    for atom in list_atoms(conn, tenant_id, atom_type="clinical_disclosure"):
        if atom.payload.get("disclosure_type") != "allergy":
            continue
        allergen = atom.payload.get("disclosure_text", "")
        text = f"avoids {allergen}"
        if not constraint_exists(text):
            emit(text, atom)

    for atom in list_atoms(conn, tenant_id, atom_type="preference_statement"):
        preference = atom.payload.get("subject_text", "")
        text = f"prefers {preference}"
        if not constraint_exists(text):
            emit(text, atom)


def sync_from_intake(
    conn: sqlite3.Connection, tenant_id: str
) -> DerivationOutcome:
    """Idempotent derivation pass. Adds only what's missing."""
    outcome = DerivationOutcome()
    profile = _load_profile(conn, tenant_id)
    if profile is not None:
        allergens, preferences = profile
        _sync_allergens(conn, tenant_id, allergens, outcome)
        _sync_preferences(conn, tenant_id, preferences, outcome)
    _sync_screener_results(conn, tenant_id, outcome)
    _sync_abstracted_constraints(conn, tenant_id, outcome)
    return outcome
