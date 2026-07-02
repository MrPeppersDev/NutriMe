"""Persistence for the baseline intake profile + screener responses.

Two write paths for sub-commit 2.1:

- :func:`save_profile` upserts the single ``intake_profile`` row per tenant
  (scalar demographics + life-stage + JSON-encoded preference/allergen lists).
- :func:`save_screener_responses` appends raw item responses to
  ``intake_screener_response`` for a given (tenant, instrument, administered_at)
  batch. Scoring is not persisted here — instruments compute it at read time.

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


def save_profile(
    conn: sqlite3.Connection, tenant_id: str, profile: IntakeProfile
) -> None:
    now = _now_iso()
    conn.execute(
        """
        INSERT INTO intake_profile (
            tenant_id, year_of_birth, sex_assigned_at_birth,
            height_cm, weight_kg, life_stage,
            dietary_preferences, allergens, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(tenant_id) DO UPDATE SET
            year_of_birth         = excluded.year_of_birth,
            sex_assigned_at_birth = excluded.sex_assigned_at_birth,
            height_cm             = excluded.height_cm,
            weight_kg             = excluded.weight_kg,
            life_stage            = excluded.life_stage,
            dietary_preferences   = excluded.dietary_preferences,
            allergens             = excluded.allergens,
            updated_at            = excluded.updated_at
        """,
        (
            tenant_id,
            profile.year_of_birth,
            profile.sex_assigned_at_birth,
            profile.height_cm,
            profile.weight_kg,
            profile.life_stage,
            json.dumps(list(profile.dietary_preferences)),
            json.dumps(list(profile.allergens)),
            now,
            now,
        ),
    )
    conn.commit()


def save_screener_responses(
    conn: sqlite3.Connection,
    tenant_id: str,
    instrument: Instrument,
    responses: Mapping[str, int],
    administered_at: str | None = None,
) -> str:
    """Persist raw item responses; returns the ``administered_at`` timestamp used."""
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
            tenant_id, instrument_id, instrument_version,
            item_id, response_value, administered_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return administered_at
