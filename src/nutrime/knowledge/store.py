"""Atom + synthesized_entry persistence — insert / list / retract.

The 24 shared base columns per schema.md S1 Q1.2 are represented as required
+ optional keyword arguments on the insert helpers. Type-specific fields live
in the JSON ``payload``; validation is Python-side (application code primary)
with SQLite CHECK constraints as the safety net.

Immutability discipline: atoms are append-only; changes model as
retract-and-reinsert. :func:`retract_entry` sets ``valid_until`` +
``retraction_reason`` on a specific row so it stops appearing in
"currently valid" queries but stays in the record.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Mapping

from nutrime import __version__
from nutrime.knowledge.ids import new_atom_id, new_synthesized_entry_id
from nutrime.phi import PhiCategory
from nutrime.tenancy import _now_iso

SYSTEM_VERSION = __version__


class Provenance(StrEnum):
    """schema.md S1 Q1.2 `provenance` enumeration."""

    VALIDATED_INSTRUMENT = "validated-instrument"
    CONVERSATIONAL_ELICITATION = "conversational-elicitation"
    PASSIVE_OBSERVATION = "passive-observation"


class SubjectType(StrEnum):
    """schema.md F2 subject-axis enumeration."""

    USER = "user"
    HOUSEHOLD = "household"
    MEMBER_SUBSET = "member_subset"


class RetractionReason(StrEnum):
    """schema.md S1 Q1.2 `retraction_reason` enumeration (F4)."""

    SUPERSEDED = "superseded"
    USER_CORRECTION = "retracted_user_correction"
    SOURCE_REVISION = "retracted_source_revision"
    VALIDATION_FAILURE = "retracted_validation_failure"
    CONSENT_WITHDRAWN = "retracted_consent_withdrawn"


@dataclass(frozen=True)
class KnowledgeRecord:
    """Loaded row — atom or synthesized_entry share the same base columns."""

    id: str
    tenant_id: str
    type: str
    subject_id: str | None
    subject_type: str | None
    provenance: str
    source_identity: str | None
    valid_from: str
    valid_until: str | None
    recorded_at: str
    retraction_reason: str | None
    phi_categories: tuple[str, ...]
    payload: dict


def _insert(
    conn: sqlite3.Connection,
    table: str,
    entry_id: str,
    tenant_id: str,
    *,
    type: str,
    provenance: Provenance,
    payload: Mapping,
    payload_schema_version: str,
    subject_id: str | None,
    subject_type: SubjectType | None,
    source_identity: str | None,
    phi_categories: Iterable[PhiCategory],
    valid_from: str,
) -> None:
    now = _now_iso()
    conn.execute(
        f"""
        INSERT INTO {table} (
            id, tenant_id, type, subject_id, subject_type,
            provenance, source_identity,
            valid_from, recorded_at,
            system_version, payload_schema_version,
            phi_categories, payload
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry_id,
            tenant_id,
            type,
            subject_id,
            subject_type.value if subject_type is not None else None,
            provenance.value,
            source_identity,
            valid_from,
            now,
            SYSTEM_VERSION,
            payload_schema_version,
            json.dumps(sorted(c.value for c in phi_categories)),
            json.dumps(payload),
        ),
    )
    conn.commit()


def insert_atom(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    atom_type: str,
    provenance: Provenance,
    payload: Mapping,
    payload_schema_version: str = "v1",
    subject_id: str | None = None,
    subject_type: SubjectType | None = SubjectType.USER,
    source_identity: str | None = None,
    phi_categories: Iterable[PhiCategory] = (),
    valid_from: str | None = None,
) -> str:
    """Insert an atom row; returns the generated ``atm-...`` id."""
    entry_id = new_atom_id()
    _insert(
        conn,
        "atom",
        entry_id,
        tenant_id,
        type=atom_type,
        provenance=provenance,
        payload=payload,
        payload_schema_version=payload_schema_version,
        subject_id=subject_id if subject_id is not None else tenant_id,
        subject_type=subject_type,
        source_identity=source_identity,
        phi_categories=phi_categories,
        valid_from=valid_from or _now_iso(),
    )
    return entry_id


def insert_synthesized_entry(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    entry_type: str,
    provenance: Provenance,
    payload: Mapping,
    payload_schema_version: str = "v1",
    subject_id: str | None = None,
    subject_type: SubjectType | None = SubjectType.USER,
    source_identity: str | None = None,
    phi_categories: Iterable[PhiCategory] = (),
    valid_from: str | None = None,
) -> str:
    """Insert a synthesized_entry row; returns the generated ``syn-...`` id."""
    entry_id = new_synthesized_entry_id()
    _insert(
        conn,
        "synthesized_entry",
        entry_id,
        tenant_id,
        type=entry_type,
        provenance=provenance,
        payload=payload,
        payload_schema_version=payload_schema_version,
        subject_id=subject_id if subject_id is not None else tenant_id,
        subject_type=subject_type,
        source_identity=source_identity,
        phi_categories=phi_categories,
        valid_from=valid_from or _now_iso(),
    )
    return entry_id


def _row_to_record(row: sqlite3.Row | tuple) -> KnowledgeRecord:
    (
        row_id,
        tenant_id,
        row_type,
        subject_id,
        subject_type,
        provenance,
        source_identity,
        valid_from,
        valid_until,
        recorded_at,
        retraction_reason,
        phi_categories,
        payload,
    ) = row
    return KnowledgeRecord(
        id=row_id,
        tenant_id=tenant_id,
        type=row_type,
        subject_id=subject_id,
        subject_type=subject_type,
        provenance=provenance,
        source_identity=source_identity,
        valid_from=valid_from,
        valid_until=valid_until,
        recorded_at=recorded_at,
        retraction_reason=retraction_reason,
        phi_categories=tuple(json.loads(phi_categories)),
        payload=json.loads(payload),
    )


_SELECT_COLS = (
    "id, tenant_id, type, subject_id, subject_type,"
    " provenance, source_identity,"
    " valid_from, valid_until, recorded_at,"
    " retraction_reason, phi_categories, payload"
)


def _list_from(
    conn: sqlite3.Connection,
    table: str,
    tenant_id: str,
    *,
    row_type: str | None,
    currently_valid: bool,
) -> list[KnowledgeRecord]:
    sql = f"SELECT {_SELECT_COLS} FROM {table} WHERE tenant_id = ?"
    params: list[str] = [tenant_id]
    if row_type is not None:
        sql += " AND type = ?"
        params.append(row_type)
    if currently_valid:
        sql += " AND valid_until IS NULL"
    sql += " ORDER BY valid_from, id"
    cursor = conn.execute(sql, tuple(params))
    return [_row_to_record(row) for row in cursor.fetchall()]


def list_atoms(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    atom_type: str | None = None,
    currently_valid: bool = True,
) -> list[KnowledgeRecord]:
    return _list_from(
        conn, "atom", tenant_id,
        row_type=atom_type, currently_valid=currently_valid,
    )


def list_synthesized_entries(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    entry_type: str | None = None,
    currently_valid: bool = True,
) -> list[KnowledgeRecord]:
    return _list_from(
        conn, "synthesized_entry", tenant_id,
        row_type=entry_type, currently_valid=currently_valid,
    )


def retract_entry(
    conn: sqlite3.Connection,
    tenant_id: str,
    entry_id: str,
    reason: RetractionReason,
    *,
    table: str = "atom",
) -> bool:
    """Mark a row retracted (valid_until = now; retraction_reason set)."""
    if table not in {"atom", "synthesized_entry"}:
        raise ValueError(f"unknown table {table!r}")
    now = _now_iso()
    cursor = conn.execute(
        f"UPDATE {table} SET valid_until = ?, retraction_reason = ?"
        " WHERE tenant_id = ? AND id = ? AND valid_until IS NULL",
        (now, reason.value, tenant_id, entry_id),
    )
    conn.commit()
    return cursor.rowcount > 0
