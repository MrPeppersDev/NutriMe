"""Persistence for the baseline intake profile + screener responses.

Per-member since #29 (migration 0006):

- :func:`save_member_profile` upserts one ``intake_profile_v2`` row per
  (tenant, member) — scalar demographics + life-stage + JSON-encoded
  preference/allergen lists. :func:`save_profile` is the member-unaware
  form and writes the household's default member. The legacy
  single-row ``intake_profile`` table is no longer written.
- :func:`save_screener_responses` appends raw item responses to
  ``intake_screener_response`` for a given (tenant, member, instrument,
  administered_at) batch. Scoring is not persisted here — instruments
  compute it at read time.

Both tables are substrate-side per S1 (personal state, F9 multi-tenant).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from typing import Mapping

from nutrime.intake.instruments import Instrument
from nutrime.tenancy import _now_iso

_LIFE_STAGES = frozenset(
    {
        "infant",
        "child",
        "adolescent",
        "adult",
        "pregnant",
        "lactating",
        "older_adult",
    }
)
_SEX_ASSIGNED = frozenset(
    {"female", "male", "intersex", "prefer_not_to_say"}
)


@dataclass(frozen=True)
class IntakeProfile:
    year_of_birth: int
    sex_assigned_at_birth: str
    life_stage: str
    height_cm: int | None = None
    weight_kg: float | None = None
    dietary_preferences: tuple[str, ...] = field(default_factory=tuple)
    allergens: tuple[str, ...] = field(default_factory=tuple)
    # Disclosed health conditions (sweep #10) — free text; gating behavior
    # is computed from nutrime.conditions at use time, never stored.
    conditions: tuple[str, ...] = field(default_factory=tuple)
    # Non-allergen foods this member won't eat (hard exclusions, like
    # allergens) — distinct from dietary_preferences (soft boosts).
    avoid_foods: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not 1900 <= self.year_of_birth <= 2100:
            raise ValueError(
                f"year_of_birth {self.year_of_birth} outside allowed range"
            )
        if self.sex_assigned_at_birth not in _SEX_ASSIGNED:
            raise ValueError(
                f"sex_assigned_at_birth {self.sex_assigned_at_birth!r} not in"
                f" {sorted(_SEX_ASSIGNED)}"
            )
        if self.life_stage not in _LIFE_STAGES:
            raise ValueError(
                f"life_stage {self.life_stage!r} not in {sorted(_LIFE_STAGES)}"
            )
        if self.height_cm is not None and not 30 <= self.height_cm <= 275:
            raise ValueError(
                f"height_cm {self.height_cm} outside allowed range"
            )
        if self.weight_kg is not None and not 1 <= self.weight_kg <= 500:
            raise ValueError(
                f"weight_kg {self.weight_kg} outside allowed range"
            )


def _resolve_member(
    conn: sqlite3.Connection, tenant_id: str, member_id: str | None
) -> str:
    from nutrime.members import default_member_id, get_member

    if member_id is None:
        return default_member_id(conn, tenant_id)
    return get_member(conn, tenant_id, member_id).id


def save_member_profile(
    conn: sqlite3.Connection,
    tenant_id: str,
    member_id: str | None,
    profile: IntakeProfile,
) -> str:
    """Upsert this member's profile; returns the member id written."""
    member_id = _resolve_member(conn, tenant_id, member_id)
    now = _now_iso()
    previous = load_member_profile(conn, tenant_id, member_id)
    if previous is not None and previous != profile:
        # Append-only record of revisions (check-ins revise the baseline).
        conn.execute(
            "INSERT INTO intake_profile_history"
            " (tenant_id, member_id, replaced_at, profile) VALUES (?, ?, ?, ?)",
            (tenant_id, member_id, now, json.dumps(profile_to_dict(previous))),
        )
    conn.execute(
        """
        INSERT INTO intake_profile_v2 (
            tenant_id, member_id, year_of_birth, sex_assigned_at_birth,
            height_cm, weight_kg, life_stage,
            dietary_preferences, allergens, conditions, avoid_foods,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(tenant_id, member_id) DO UPDATE SET
            year_of_birth         = excluded.year_of_birth,
            sex_assigned_at_birth = excluded.sex_assigned_at_birth,
            height_cm             = excluded.height_cm,
            weight_kg             = excluded.weight_kg,
            life_stage            = excluded.life_stage,
            dietary_preferences   = excluded.dietary_preferences,
            allergens             = excluded.allergens,
            conditions            = excluded.conditions,
            avoid_foods           = excluded.avoid_foods,
            updated_at            = excluded.updated_at
        """,
        (
            tenant_id,
            member_id,
            profile.year_of_birth,
            profile.sex_assigned_at_birth,
            profile.height_cm,
            profile.weight_kg,
            profile.life_stage,
            json.dumps(list(profile.dietary_preferences)),
            json.dumps(list(profile.allergens)),
            json.dumps(list(profile.conditions)),
            json.dumps(list(profile.avoid_foods)),
            now,
            now,
        ),
    )
    conn.commit()
    return member_id


def profile_to_dict(profile: IntakeProfile) -> dict:
    return {
        "year_of_birth": profile.year_of_birth,
        "sex_assigned_at_birth": profile.sex_assigned_at_birth,
        "life_stage": profile.life_stage,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "dietary_preferences": list(profile.dietary_preferences),
        "allergens": list(profile.allergens),
        "conditions": list(profile.conditions),
        "avoid_foods": list(profile.avoid_foods),
    }


def save_profile(
    conn: sqlite3.Connection, tenant_id: str, profile: IntakeProfile
) -> None:
    """Member-unaware form: writes the household's default member."""
    save_member_profile(conn, tenant_id, None, profile)


_PROFILE_COLS = (
    "member_id, year_of_birth, sex_assigned_at_birth, life_stage,"
    " height_cm, weight_kg, dietary_preferences, allergens, conditions,"
    " avoid_foods"
)


def _row_to_profile(row: tuple) -> IntakeProfile:
    return IntakeProfile(
        year_of_birth=row[1],
        sex_assigned_at_birth=row[2],
        life_stage=row[3],
        height_cm=row[4],
        weight_kg=row[5],
        dietary_preferences=tuple(json.loads(row[6])),
        allergens=tuple(json.loads(row[7])),
        conditions=tuple(json.loads(row[8])),
        avoid_foods=tuple(json.loads(row[9])),
    )


def load_member_profile(
    conn: sqlite3.Connection, tenant_id: str, member_id: str
) -> IntakeProfile | None:
    row = conn.execute(
        f"SELECT {_PROFILE_COLS} FROM intake_profile_v2"
        " WHERE tenant_id = ? AND member_id = ?",
        (tenant_id, member_id),
    ).fetchone()
    return _row_to_profile(row) if row else None


def household_profiles(
    conn: sqlite3.Connection, tenant_id: str
) -> dict[str, IntakeProfile]:
    """member_id → profile for every active member who has one."""
    rows = conn.execute(
        f"SELECT p.{_PROFILE_COLS.replace(', ', ', p.')}"
        " FROM intake_profile_v2 p JOIN member m ON m.id = p.member_id"
        " WHERE p.tenant_id = ? AND m.status = 'active'"
        " ORDER BY m.created_at, m.id",
        (tenant_id,),
    ).fetchall()
    return {row[0]: _row_to_profile(row) for row in rows}


def save_screener_responses(
    conn: sqlite3.Connection,
    tenant_id: str,
    instrument: Instrument,
    responses: Mapping[str, int],
    administered_at: str | None = None,
    *,
    member_id: str | None = None,
) -> str:
    """Persist raw item responses; returns the ``administered_at`` timestamp used.

    ``member_id=None`` attributes the batch to the default member.
    """
    member_id = _resolve_member(conn, tenant_id, member_id)
    administered_at = administered_at or _now_iso()
    for item in instrument.items:
        if item.item_id not in responses:
            raise ValueError(
                f"missing response for item {item.item_id!r}"
                f" of instrument {instrument.instrument_id!r}"
            )
    rows = [
        (
            tenant_id,
            member_id,
            instrument.instrument_id,
            instrument.instrument_version,
            item.item_id,
            responses[item.item_id],
            administered_at,
        )
        for item in instrument.items
    ]
    conn.executemany(
        """
        INSERT INTO intake_screener_response (
            tenant_id, member_id, instrument_id, instrument_version,
            item_id, response_value, administered_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return administered_at
