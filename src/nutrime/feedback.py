"""Per-meal feedback loop (Stage 6 step 7, C5 two-stage design).

The learning half of the plan→cook cycle. A cooked meal becomes a
``meal_event`` atom; feedback lands as the three C5-split atoms:

- ``meal_feedback_cooking_experience`` (immediate): ease + enjoyment
  (1-5), per Q5.3's two questions.
- ``meal_feedback_body_response`` (later): free-text "how did this make
  your body feel" with optional 1-5 ratings the user volunteers.
- ``meal_feedback_time``: recipe's stated time vs actual.

Consent gate (#21): every write resolves a current standing grant via
``require_consent`` and stamps the atom's ``consent_record_id`` — a
declined category blocks capture, which is "consent-clean on every
capture surface" made operational. Time + cooking-experience feedback
are the ``meal_feedback_time`` category; body response is
``meal_feedback_semantic`` (the category the user can rule out globally
per E2 Q2.2 while still contributing time aggregates).

PHI posture: body-response text stays local (knowledge model, never
crosses egress — no envelope registers it). Cooking-experience + time
feedback carry no PHI categories.

Both prompts are skippable — fail-open on absence of feedback, only
fail-closed on absence of consent.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from nutrime.consent import require_consent
from nutrime.knowledge.ids import uuid7
from nutrime.knowledge.store import (
    Provenance,
    insert_atom,
    list_atoms,
)
from nutrime.tenancy import _now_iso


def new_meal_event_id() -> str:
    return f"mev-{uuid7()}"


def record_meal_event(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    recipe_id: str,
    recipe_title: str,
    plan_id: str | None = None,
    cooked_at: str | None = None,
) -> str:
    """Record "we cooked this" — the anchor the feedback atoms reference.

    Passive observation provenance: confirming a cook is inventory-grade
    observation, not a clinical statement.
    """
    consent_id = require_consent(conn, tenant_id, "meal_feedback_time")
    meal_event_id = new_meal_event_id()
    insert_atom(
        conn,
        tenant_id,
        atom_type="meal_event",
        provenance=Provenance.PASSIVE_OBSERVATION,
        payload={
            "meal_event_id": meal_event_id,
            "recipe_id": recipe_id,
            "recipe_title": recipe_title,
            "plan_id": plan_id,
            "cooked_at": cooked_at or _now_iso(),
        },
        consent_record_id=consent_id,
    )
    return meal_event_id


def record_cooking_experience(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    meal_event_id: str,
    ease_rating: int,
    enjoyment_rating: int,
    freetext_notes: str | None = None,
) -> str:
    """Immediate prompt: "How easy / how enjoyable was this to make?"."""
    for name, value in (("ease", ease_rating), ("enjoyment", enjoyment_rating)):
        if not 1 <= value <= 5:
            raise ValueError(f"{name}_rating must be 1-5, got {value}")
    consent_id = require_consent(conn, tenant_id, "meal_feedback_time")
    payload: dict[str, Any] = {
        "meal_event_id": meal_event_id,
        "ease_rating": ease_rating,
        "enjoyment_rating": enjoyment_rating,
        "prompt_responded_at": _now_iso(),
    }
    if freetext_notes:
        payload["freetext_notes"] = freetext_notes
        payload["freetext_format"] = "plain"
    return insert_atom(
        conn,
        tenant_id,
        atom_type="meal_feedback_cooking_experience",
        provenance=Provenance.CONVERSATIONAL_ELICITATION,
        payload=payload,
        consent_record_id=consent_id,
    )


def record_body_response(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    meal_event_id: str,
    freetext_response: str,
    energy_rating: int | None = None,
    digestion_rating: int | None = None,
    fullness_rating: int | None = None,
    mood_rating: int | None = None,
) -> str:
    """Later prompt: "How did this make your body feel?" (plain text is
    the data; ratings only if volunteered)."""
    if not freetext_response.strip():
        raise ValueError("freetext_response is required — the feeling is the data")
    for name, value in (
        ("energy", energy_rating),
        ("digestion", digestion_rating),
        ("fullness", fullness_rating),
        ("mood", mood_rating),
    ):
        if value is not None and not 1 <= value <= 5:
            raise ValueError(f"{name}_rating must be 1-5, got {value}")
    consent_id = require_consent(conn, tenant_id, "meal_feedback_semantic")
    payload: dict[str, Any] = {
        "meal_event_id": meal_event_id,
        "freetext_response": freetext_response.strip(),
        "freetext_format": "plain",
        "prompt_responded_at": _now_iso(),
    }
    for key, value in (
        ("energy_rating", energy_rating),
        ("digestion_rating", digestion_rating),
        ("fullness_rating", fullness_rating),
        ("mood_rating", mood_rating),
    ):
        if value is not None:
            payload[key] = value
    return insert_atom(
        conn,
        tenant_id,
        atom_type="meal_feedback_body_response",
        provenance=Provenance.CONVERSATIONAL_ELICITATION,
        payload=payload,
        consent_record_id=consent_id,
    )


def record_time_feedback(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    meal_event_id: str,
    estimated_time_min: int | None,
    actual_time_min: int,
) -> str:
    """Time-accuracy loop: stated vs actual minutes."""
    if actual_time_min <= 0:
        raise ValueError("actual_time_min must be positive")
    consent_id = require_consent(conn, tenant_id, "meal_feedback_time")
    delta = (
        actual_time_min - estimated_time_min
        if estimated_time_min is not None
        else None
    )
    return insert_atom(
        conn,
        tenant_id,
        atom_type="meal_feedback_time",
        provenance=Provenance.CONVERSATIONAL_ELICITATION,
        payload={
            "meal_event_id": meal_event_id,
            "estimated_time_min": estimated_time_min,
            "actual_time_min": actual_time_min,
            "time_delta_min": delta,
            "prompt_responded_at": _now_iso(),
        },
        consent_record_id=consent_id,
    )


# -- read side ----------------------------------------------------------------


@dataclass(frozen=True)
class MealHistoryEntry:
    meal_event_id: str
    recipe_id: str
    recipe_title: str
    cooked_at: str
    ease_rating: int | None
    enjoyment_rating: int | None
    body_response: str | None
    actual_time_min: int | None
    time_delta_min: int | None


def meal_history(
    conn: sqlite3.Connection, tenant_id: str, *, limit: int = 20
) -> list[MealHistoryEntry]:
    """Joined view of meal events + their feedback atoms, newest first."""
    events = [
        a for a in list_atoms(conn, tenant_id, atom_type="meal_event")
    ]
    by_meal: dict[str, dict[str, Any]] = {}
    for atom_type in (
        "meal_feedback_cooking_experience",
        "meal_feedback_body_response",
        "meal_feedback_time",
    ):
        for atom in list_atoms(conn, tenant_id, atom_type=atom_type):
            mev = str(atom.payload.get("meal_event_id") or "")
            by_meal.setdefault(mev, {})[atom_type] = atom.payload
    entries = []
    for event in events:
        mev = str(event.payload.get("meal_event_id") or "")
        fb = by_meal.get(mev, {})
        cooking = fb.get("meal_feedback_cooking_experience", {})
        body = fb.get("meal_feedback_body_response", {})
        time_fb = fb.get("meal_feedback_time", {})
        entries.append(
            MealHistoryEntry(
                meal_event_id=mev,
                recipe_id=str(event.payload.get("recipe_id") or ""),
                recipe_title=str(event.payload.get("recipe_title") or ""),
                cooked_at=str(event.payload.get("cooked_at") or ""),
                ease_rating=cooking.get("ease_rating"),
                enjoyment_rating=cooking.get("enjoyment_rating"),
                body_response=body.get("freetext_response"),
                actual_time_min=time_fb.get("actual_time_min"),
                time_delta_min=time_fb.get("time_delta_min"),
            )
        )
    entries.sort(key=lambda e: e.cooked_at, reverse=True)
    return entries[:limit]


def recipe_experience_summary(
    conn: sqlite3.Connection, tenant_id: str, recipe_id: str
) -> dict[str, Any] | None:
    """Aggregate signal for one recipe — the planner-boost hand-off.

    Returns {times_cooked, avg_ease, avg_enjoyment, avg_time_delta_min}
    or None if never cooked. Downstream (search boost / planner context)
    reads this, never the raw atoms — same discipline as the constraint
    seam.
    """
    history = [
        e for e in meal_history(conn, tenant_id, limit=1000)
        if e.recipe_id == recipe_id
    ]
    if not history:
        return None

    def _avg(values: list[int]) -> float | None:
        return round(sum(values) / len(values), 2) if values else None

    return {
        "times_cooked": len(history),
        "avg_ease": _avg([e.ease_rating for e in history if e.ease_rating]),
        "avg_enjoyment": _avg(
            [e.enjoyment_rating for e in history if e.enjoyment_rating]
        ),
        "avg_time_delta_min": _avg(
            [e.time_delta_min for e in history if e.time_delta_min is not None]
        ),
    }
