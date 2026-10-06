"""Read step-2 intake data and derive knowledge-model rows.

Reads (per household member since #29):
- ``intake_profile_v2`` — allergens list, dietary_preferences list.
- ``intake_screener_response`` — grouped by (member, instrument_id,
  administered_at).

Emits atoms:
- ``clinical_disclosure`` — one per allergen (disclosure_type='allergy').
- ``preference_statement`` — one per dietary preference.
- ``screener_result`` — one per screener administration batch.

Atoms carry the member as ``subject_id``. Then emits household-level
``abstracted_constraint`` synthesized entries derived from every member's
currently-valid allergy + preference atoms — the union of avoids/prefers
(Tension #5 constraint-only sharing; no member's raw data is exposed).

Idempotent: existing currently-valid rows with matching identity keys are
skipped on re-run.

Retraction (2026-10-06, periodic check-ins): a member's allergy or
preference atom that is no longer in their current profile is retracted
(``retracted_user_correction``), and a household constraint no active
member supports any more — the allergy was removed, or the only person
with it was archived — is retracted (``retracted_source_revision``). The
rows stay in the table with ``valid_until`` set: the honest history of
what the household once avoided is kept; only the live list changes.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field

from nutrime.intake.instruments import (
    ENERGY_CHECK,
    GAD2,
    HUNGER_VITAL_SIGN,
    PHQ2,
    SLEEP_CHECK,
    Instrument,
)
from nutrime.knowledge.store import (
    KnowledgeRecord,
    Provenance,
    RetractionReason,
    insert_atom,
    insert_synthesized_entry,
    list_atoms,
    list_synthesized_entries,
    retract_entry,
)
from nutrime.phi import PhiCategory

# Every instrument a stored batch may reference: the default flow
# (HVS + sleep/energy checks since the 2026-10-06 reset) plus the opt-in
# PHQ-2/GAD-2 pair, which stay derivable for households that use them.
_KNOWN_INSTRUMENTS: dict[str, Instrument] = {
    inst.instrument_id: inst
    for inst in (PHQ2, GAD2, HUNGER_VITAL_SIGN, SLEEP_CHECK, ENERGY_CHECK)
}


@dataclass
class DerivationOutcome:
    """Summary of what a sync pass added; keys are atom / entry types."""

    atoms_added: dict[str, int] = field(default_factory=dict)
    constraints_added: int = 0
    atoms_retracted: int = 0
    constraints_retracted: int = 0

    def bump_atom(self, atom_type: str) -> None:
        self.atoms_added[atom_type] = self.atoms_added.get(atom_type, 0) + 1

    @property
    def total_atoms_added(self) -> int:
        return sum(self.atoms_added.values())


def _load_profiles(
    conn: sqlite3.Connection, tenant_id: str
) -> dict[str, tuple[list[str], list[str]]]:
    """member_id → (allergens, preferences) for active members."""
    from nutrime.intake.store import household_profiles

    return {
        member_id: (list(p.allergens), list(p.dietary_preferences))
        for member_id, p in household_profiles(conn, tenant_id).items()
    }


def _load_screener_batches(
    conn: sqlite3.Connection, tenant_id: str, member_id: str
) -> list[tuple[str, str, str, dict[str, int]]]:
    """Return [(instrument_id, instrument_version, administered_at, {item_id: value})]."""
    rows = conn.execute(
        "SELECT instrument_id, instrument_version, administered_at,"
        " item_id, response_value FROM intake_screener_response"
        " WHERE tenant_id = ? AND member_id = ?"
        " ORDER BY instrument_id, administered_at, item_id",
        (tenant_id, member_id),
    ).fetchall()
    grouped: dict[tuple[str, str, str], dict[str, int]] = {}
    for instrument_id, version, administered_at, item_id, value in rows:
        key = (instrument_id, version, administered_at)
        grouped.setdefault(key, {})[item_id] = value
    return [
        (instrument_id, version, administered_at, responses)
        for (instrument_id, version, administered_at), responses in grouped.items()
    ]


def _member_atoms(
    conn: sqlite3.Connection, tenant_id: str, member_id: str, atom_type: str
) -> list[KnowledgeRecord]:
    from nutrime.members import subject_ids_for

    subjects = subject_ids_for(conn, tenant_id, member_id)
    return [
        a for a in list_atoms(conn, tenant_id, atom_type=atom_type)
        if a.subject_id in subjects
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
    member_id: str,
    allergens: list[str],
    outcome: DerivationOutcome,
) -> None:
    existing = _member_atoms(conn, tenant_id, member_id, "clinical_disclosure")
    wanted = {a.strip().lower() for a in allergens}
    for atom in existing:
        if atom.payload.get("disclosure_type") != "allergy":
            continue
        if str(atom.payload.get("disclosure_text", "")).strip().lower() not in wanted:
            if retract_entry(conn, tenant_id, atom.id, RetractionReason.USER_CORRECTION):
                outcome.atoms_retracted += 1
    existing = _member_atoms(conn, tenant_id, member_id, "clinical_disclosure")
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
            source_identity=f"intake_profile:{member_id}",
            subject_id=member_id,
        )
        outcome.bump_atom("clinical_disclosure")


def _sync_preferences(
    conn: sqlite3.Connection,
    tenant_id: str,
    member_id: str,
    preferences: list[str],
    outcome: DerivationOutcome,
) -> None:
    existing = _member_atoms(conn, tenant_id, member_id, "preference_statement")
    wanted = {p.strip().lower() for p in preferences}
    for atom in existing:
        if atom.payload.get("preference_type") != "dietary_pattern_preference":
            continue
        if str(atom.payload.get("subject_text", "")).strip().lower() not in wanted:
            if retract_entry(conn, tenant_id, atom.id, RetractionReason.USER_CORRECTION):
                outcome.atoms_retracted += 1
    existing = _member_atoms(conn, tenant_id, member_id, "preference_statement")
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
            source_identity=f"intake_profile:{member_id}",
            subject_id=member_id,
        )
        outcome.bump_atom("preference_statement")


def _sync_screener_results(
    conn: sqlite3.Connection,
    tenant_id: str,
    member_id: str,
    outcome: DerivationOutcome,
) -> None:
    existing = _member_atoms(conn, tenant_id, member_id, "screener_result")
    batches = _load_screener_batches(conn, tenant_id, member_id)
    for instrument_id, version, administered_at, responses in batches:
        instrument = _KNOWN_INSTRUMENTS.get(instrument_id)
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
            subject_id=member_id,
        )
        outcome.bump_atom("screener_result")


def _active_subjects(conn: sqlite3.Connection, tenant_id: str) -> set[str]:
    from nutrime.members import list_members, subject_ids_for

    out: set[str] = set()
    for member in list_members(conn, tenant_id):
        out.update(subject_ids_for(conn, tenant_id, member.id))
    return out


def _sync_abstracted_constraints(
    conn: sqlite3.Connection,
    tenant_id: str,
    outcome: DerivationOutcome,
) -> None:
    """Household abstracted_constraint rows = the union over ACTIVE members'
    currently-valid allergy + preference atoms. Adds what's missing and
    retracts what nothing supports any more.

    Life-stage / DRI-derived constraints are deferred out of the initial slice.
    """
    active = _active_subjects(conn, tenant_id)
    supporting: dict[str, KnowledgeRecord] = {}
    for atom in list_atoms(conn, tenant_id, atom_type="clinical_disclosure"):
        if atom.subject_id in active and atom.payload.get("disclosure_type") == "allergy":
            supporting.setdefault(f"avoids {atom.payload.get('disclosure_text', '')}", atom)
    for atom in list_atoms(conn, tenant_id, atom_type="preference_statement"):
        if atom.subject_id in active and atom.payload.get(
            "preference_type"
        ) == "dietary_pattern_preference":
            supporting.setdefault(f"prefers {atom.payload.get('subject_text', '')}", atom)

    # Cuisine interests chosen at a check-in nudge ranking the same way.
    for atom in list_atoms(conn, tenant_id, atom_type="cuisine_interest"):
        if atom.subject_id in active:
            supporting.setdefault(f"prefers {atom.payload.get('cuisine', '')}", atom)

    existing = list_synthesized_entries(
        conn, tenant_id, entry_type="abstracted_constraint"
    )
    present: set[str] = set()
    for entry in existing:
        text = str(entry.payload.get("abstracted_text", ""))
        if text not in supporting:
            if retract_entry(
                conn, tenant_id, entry.id, RetractionReason.SOURCE_REVISION,
                table="synthesized_entry",
            ):
                outcome.constraints_retracted += 1
        else:
            present.add(text)

    for text, source_atom in supporting.items():
        if text in present:
            continue
        insert_synthesized_entry(
            conn,
            tenant_id,
            entry_type="abstracted_constraint",
            provenance=Provenance(source_atom.provenance),
            payload={
                "household_id": tenant_id,
                "source_member_id": source_atom.subject_id,
                "abstracted_text": text,
                "sharing_level": "constraint_only_automatic",
                "derived_from_atom_ids": [source_atom.id],
            },
            source_identity=source_atom.id,
            phi_categories=(),
        )
        outcome.constraints_added += 1


def sync_from_intake(
    conn: sqlite3.Connection, tenant_id: str
) -> DerivationOutcome:
    """Idempotent derivation pass over every active member. Adds only
    what's missing."""
    from nutrime.members import list_members

    outcome = DerivationOutcome()
    profiles = _load_profiles(conn, tenant_id)
    for member in list_members(conn, tenant_id):
        if member.id in profiles:
            allergens, preferences = profiles[member.id]
            _sync_allergens(conn, tenant_id, member.id, allergens, outcome)
            _sync_preferences(conn, tenant_id, member.id, preferences, outcome)
        _sync_screener_results(conn, tenant_id, member.id, outcome)
    _sync_abstracted_constraints(conn, tenant_id, outcome)
    return outcome
