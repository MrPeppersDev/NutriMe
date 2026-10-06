"""Consent records (S8 slice, issue #21) — E2 standing-consent layer.

Tiered model per E2: standing consent per (data_category, purpose)
establishes eligibility at write time; per-publication confirmation is a
separate later layer. This module owns the standing layer only.

Append-only discipline: changing a decision writes a new row and closes
the old one (``valid_until`` + ``superseded_by``) — consent history is
part of the honest record, per the same bitemporal pattern as the
knowledge model.

MVP purposes:
- ``local_operation`` — using captured data to run the household's own
  planning on this device. Granted implicitly at first run WITH an
  explicit, recorded notice (single-user local scale per E2; the record
  exists so the posture is inspectable, and `retroactive=1` marks the
  backfill covering pre-#21 captures).
- ``publication_aggregate`` — contributing anonymized aggregates to the
  publication targets. NEVER implicit: defaults to an explicit declined
  row until the user opts in (fail-closed; Rule 10 user agency).

Step-7 gate: `require_consent` is the hook feedback capture calls before
writing — a missing or declined row blocks the write, which is what
"consent-clean on every capture surface" means operationally.

Per-member decisions (#29): ``subject_user`` is ``'primary'`` for the
household-wide baseline and a ``mem-...`` id for one member's own
decision. A member's own current row, when present, wins over the
household row — so one person can decline a category (or opt in to
publication) without changing anyone else's posture.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from nutrime.knowledge.ids import uuid7
from nutrime.tenancy import _now_iso

DATA_CATEGORIES = (
    "intake_screener",
    "intake_profile",
    "inventory",
    "knowledge_derived",
    "meal_feedback_time",
    "meal_feedback_semantic",
)

PURPOSES = ("local_operation", "publication_aggregate")

HOUSEHOLD = "primary"  # subject_user of household-wide decisions


class ConsentError(Exception):
    """A capture surface asked to write without a current grant."""


def new_consent_id() -> str:
    return f"cns-{uuid7()}"


@dataclass(frozen=True)
class ConsentRecord:
    id: str
    data_category: str
    purpose: str
    granted: bool
    granted_at: str
    retroactive: bool
    note: str | None
    subject_user: str = HOUSEHOLD


def record_decision(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    data_category: str,
    purpose: str,
    granted: bool,
    note: str | None = None,
    retroactive: bool = False,
    member_id: str | None = None,
) -> str:
    """Write a decision, superseding any current row for the same key.

    ``member_id=None`` writes the household-wide decision.
    """
    if data_category not in DATA_CATEGORIES:
        raise ValueError(f"unknown data_category {data_category!r}")
    if purpose not in PURPOSES:
        raise ValueError(f"unknown purpose {purpose!r}")
    subject = member_id or HOUSEHOLD
    now = _now_iso()
    new_id = new_consent_id()
    current = conn.execute(
        "SELECT id FROM consent_record WHERE tenant_id = ?"
        " AND subject_user = ?"
        " AND data_category = ? AND purpose = ? AND valid_until IS NULL",
        (tenant_id, subject, data_category, purpose),
    ).fetchone()
    # Insert the successor before closing the predecessor: superseded_by
    # self-references consent_record(id), so the new row must exist first.
    conn.execute(
        "INSERT INTO consent_record"
        " (id, tenant_id, subject_user, data_category, purpose, granted,"
        "  granted_at, note, retroactive)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            new_id,
            tenant_id,
            subject,
            data_category,
            purpose,
            1 if granted else 0,
            now,
            note,
            1 if retroactive else 0,
        ),
    )
    if current is not None:
        conn.execute(
            "UPDATE consent_record SET valid_until = ?, superseded_by = ?"
            " WHERE id = ?",
            (now, new_id, current[0]),
        )
    conn.commit()
    return new_id


_RECORD_COLS = (
    "id, data_category, purpose, granted, granted_at, retroactive, note,"
    " subject_user"
)


def _to_record(row: tuple) -> ConsentRecord:
    return ConsentRecord(
        id=row[0],
        data_category=row[1],
        purpose=row[2],
        granted=bool(row[3]),
        granted_at=row[4],
        retroactive=bool(row[5]),
        note=row[6],
        subject_user=row[7],
    )


def current_decision(
    conn: sqlite3.Connection,
    tenant_id: str,
    data_category: str,
    purpose: str,
    *,
    member_id: str | None = None,
) -> ConsentRecord | None:
    """The decision in force: the member's own current row if one exists,
    else the household row. ``member_id=None`` reads the household row."""
    subjects = [member_id, HOUSEHOLD] if member_id else [HOUSEHOLD]
    for subject in subjects:
        row = conn.execute(
            f"SELECT {_RECORD_COLS} FROM consent_record"
            " WHERE tenant_id = ? AND subject_user = ?"
            " AND data_category = ? AND purpose = ?"
            " AND valid_until IS NULL",
            (tenant_id, subject, data_category, purpose),
        ).fetchone()
        if row is not None:
            return _to_record(row)
    return None


def require_consent(
    conn: sqlite3.Connection,
    tenant_id: str,
    data_category: str,
    purpose: str = "local_operation",
    *,
    member_id: str | None = None,
) -> str:
    """Return the current grant's consent_record_id or raise (fail-closed)."""
    record = current_decision(
        conn, tenant_id, data_category, purpose, member_id=member_id
    )
    if record is None or not record.granted:
        raise ConsentError(
            f"no current consent for ({data_category}, {purpose}) —"
            " record one via `nutrime consent` before capturing."
        )
    return record.id


def list_current(
    conn: sqlite3.Connection, tenant_id: str, *, member_id: str | None = None
) -> list[ConsentRecord]:
    """Current decisions. With ``member_id``: the decisions in force for
    that member (own rows overriding household rows, per category+purpose)."""
    rows = conn.execute(
        f"SELECT {_RECORD_COLS} FROM consent_record"
        " WHERE tenant_id = ? AND valid_until IS NULL"
        " ORDER BY data_category, purpose",
        (tenant_id,),
    ).fetchall()
    records = [_to_record(r) for r in rows]
    if member_id is None:
        return [r for r in records if r.subject_user == HOUSEHOLD]
    in_force: dict[tuple[str, str], ConsentRecord] = {}
    for r in records:
        key = (r.data_category, r.purpose)
        if r.subject_user == member_id:
            in_force[key] = r
        elif r.subject_user == HOUSEHOLD:
            in_force.setdefault(key, r)
    return [in_force[k] for k in sorted(in_force)]


def bootstrap_baseline(conn: sqlite3.Connection, tenant_id: str) -> int:
    """Idempotent first-run baseline (called from app.initialize).

    Grants local_operation for every category (retroactive — covers the
    pre-#21 captured rows) and records an explicit DECLINED row for every
    publication_aggregate pairing so the fail-closed default is a stored
    decision, not an absence. Returns rows written (0 on re-run).
    """
    written = 0
    for category in DATA_CATEGORIES:
        if current_decision(conn, tenant_id, category, "local_operation") is None:
            record_decision(
                conn,
                tenant_id,
                data_category=category,
                purpose="local_operation",
                granted=True,
                retroactive=True,
                note="first-run baseline: local household operation only",
            )
            written += 1
        if (
            current_decision(conn, tenant_id, category, "publication_aggregate")
            is None
        ):
            record_decision(
                conn,
                tenant_id,
                data_category=category,
                purpose="publication_aggregate",
                granted=False,
                note="default declined — opt in explicitly per E2",
            )
            written += 1
    return written
