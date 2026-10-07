"""Periodic check-ins (intake-pattern.md Mode 2) — per household member.

Genesis direction: "periodic check-ins that are 5 to 15 minutes that
revise the initial clinical data". A check-in revisits the baseline and
catches drift: life-stage changes, new or outgrown allergies, preference
shifts, cooking-skill growth, how the screening answers have moved.

Cadence (the spec leaves it open; these are the defaults, each member can
change theirs): every 28 days, or every 14 days during pregnancy or
breastfeeding, when needs change quickly. "Not now" snoozes a week. A
check-in only becomes due once the member has a profile — the first
intake comes first.

Nothing here is a daily prompt (Tension #3): it is a scheduled,
skippable revision, surfaced on Home when due.

What completing one does:
- saves the revised profile (the previous version goes to
  ``intake_profile_history`` — revisions never overwrite the record)
- appends a new screener batch for each instrument answered
- records cooking confidence + weeknight time as ``self_assessment`` atoms
  and the cuisines to try as ``cuisine_interest`` atoms (replacing the
  previous picks)
- re-runs the derivation, so removed allergies leave the household
  avoid-list unless another active member still has them
- stores a summary of what changed, shown back to the member
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from nutrime.db import maybe_commit
from nutrime.intake.store import IntakeProfile, load_member_profile, save_member_profile

DEFAULT_INTERVAL_DAYS = 28
FAST_CHANGE_INTERVAL_DAYS = 14
FAST_CHANGE_LIFE_STAGES = frozenset({"pregnant", "lactating"})
SNOOZE_DAYS = 7
INTERVAL_CHOICES = (14, 28, 56, 91)

CONFIDENCE_LABELS = {
    1: "I avoid cooking when I can",
    2: "I can follow simple recipes",
    3: "I'm comfortable with most everyday recipes",
    4: "I enjoy trying new techniques",
    5: "I could cook almost anything",
}
WEEKNIGHT_MINUTES = (15, 30, 45, 60, 90)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def new_checkin_id() -> str:
    from nutrime.knowledge.ids import uuid7

    return f"chk-{uuid7()}"


# -- schedule -------------------------------------------------------------------


@dataclass(frozen=True)
class CheckinStatus:
    member_id: str
    has_profile: bool
    due: bool
    due_at: str | None
    last_at: str | None
    interval_days: int
    interval_source: str  # "default" | "life_stage" | "custom"
    snoozed_until: str | None = None


def _schedule_row(conn, tenant_id: str, member_id: str) -> tuple[int | None, str | None]:
    row = conn.execute(
        "SELECT interval_days, snoozed_until FROM checkin_schedule"
        " WHERE tenant_id = ? AND member_id = ?",
        (tenant_id, member_id),
    ).fetchone()
    return (row[0], row[1]) if row else (None, None)


def checkin_status(
    conn: sqlite3.Connection, tenant_id: str, member_id: str, *, now: datetime | None = None
) -> CheckinStatus:
    now = now or _now()
    profile = load_member_profile(conn, tenant_id, member_id)
    custom, snoozed = _schedule_row(conn, tenant_id, member_id)
    if custom:
        interval, source = custom, "custom"
    elif profile is not None and profile.life_stage in FAST_CHANGE_LIFE_STAGES:
        interval, source = FAST_CHANGE_INTERVAL_DAYS, "life_stage"
    else:
        interval, source = DEFAULT_INTERVAL_DAYS, "default"
    if profile is None:
        return CheckinStatus(member_id, False, False, None, None, interval, source)

    last = conn.execute(
        "SELECT MAX(completed_at) FROM checkin WHERE tenant_id = ? AND member_id = ?",
        (tenant_id, member_id),
    ).fetchone()[0]
    if last is None:
        last = conn.execute(
            "SELECT created_at FROM intake_profile_v2 WHERE tenant_id = ? AND member_id = ?",
            (tenant_id, member_id),
        ).fetchone()[0]
    due_at = (_parse(last) or now) + timedelta(days=interval)
    snooze_dt = _parse(snoozed)
    if snooze_dt and snooze_dt > now:
        due_at = max(due_at, snooze_dt)
    return CheckinStatus(
        member_id=member_id,
        has_profile=True,
        due=now >= due_at,
        due_at=_iso(due_at),
        last_at=last,
        interval_days=interval,
        interval_source=source,
        snoozed_until=snoozed if snooze_dt and snooze_dt > now else None,
    )


def set_interval(
    conn: sqlite3.Connection, tenant_id: str, member_id: str, days: int | None
) -> None:
    """Custom cadence in days (7-180), or None to go back to the default."""
    if days is not None and not 7 <= int(days) <= 180:
        raise ValueError("check-ins can be every 7 to 180 days")
    conn.execute(
        "INSERT INTO checkin_schedule (tenant_id, member_id, interval_days)"
        " VALUES (?, ?, ?) ON CONFLICT(tenant_id, member_id)"
        " DO UPDATE SET interval_days = excluded.interval_days",
        (tenant_id, member_id, days),
    )
    maybe_commit(conn)


def snooze(
    conn: sqlite3.Connection, tenant_id: str, member_id: str,
    *, days: int = SNOOZE_DAYS, now: datetime | None = None,
) -> str:
    until = _iso((now or _now()) + timedelta(days=days))
    conn.execute(
        "INSERT INTO checkin_schedule (tenant_id, member_id, snoozed_until)"
        " VALUES (?, ?, ?) ON CONFLICT(tenant_id, member_id)"
        " DO UPDATE SET snoozed_until = excluded.snoozed_until",
        (tenant_id, member_id, until),
    )
    maybe_commit(conn)
    return until


# -- content ----------------------------------------------------------------------


def _latest_self_assessments(conn, tenant_id: str, member_id: str) -> dict[str, int]:
    from nutrime.knowledge.store import list_atoms
    from nutrime.members import subject_ids_for

    subjects = subject_ids_for(conn, tenant_id, member_id)
    out: dict[str, int] = {}
    for atom in list_atoms(conn, tenant_id, atom_type="self_assessment"):
        if atom.subject_id in subjects:
            out[str(atom.payload.get("measure"))] = atom.payload.get("value")
    return out


def current_cuisine_interests(conn, tenant_id: str, member_id: str) -> list[str]:
    from nutrime.knowledge.store import list_atoms
    from nutrime.members import subject_ids_for

    subjects = subject_ids_for(conn, tenant_id, member_id)
    return sorted({
        str(a.payload.get("cuisine"))
        for a in list_atoms(conn, tenant_id, atom_type="cuisine_interest")
        if a.subject_id in subjects
    })


def _latest_scores(conn, tenant_id: str, member_id: str) -> dict[str, dict]:
    """instrument_id → {score, positive, administered_at} of the latest batch."""
    from nutrime.knowledge.derivation import _KNOWN_INSTRUMENTS

    rows = conn.execute(
        "SELECT instrument_id, administered_at, item_id, response_value"
        " FROM intake_screener_response WHERE tenant_id = ? AND member_id = ?"
        " ORDER BY administered_at",
        (tenant_id, member_id),
    ).fetchall()
    batches: dict[tuple[str, str], dict[str, int]] = {}
    for inst, at, item, value in rows:
        batches.setdefault((inst, at), {})[item] = value
    latest: dict[str, dict] = {}
    for (inst, at), responses in batches.items():
        instrument = _KNOWN_INSTRUMENTS.get(inst)
        if instrument is None:
            continue
        try:
            result = instrument.score(responses)
        except ValueError:
            continue
        latest[inst] = {"score": result.score, "positive": result.positive,
                        "administered_at": at}
    return latest


def checkin_questions(
    conn: sqlite3.Connection, tenant_id: str, member_id: str,
    *, cuisine_options: list[str] | None = None,
) -> dict:
    """Everything the check-in form needs, prefilled with current answers."""
    from nutrime.intake.baseline import MVP_INSTRUMENTS
    from nutrime.intake.store import profile_to_dict

    profile = load_member_profile(conn, tenant_id, member_id)
    assessed = _latest_self_assessments(conn, tenant_id, member_id)
    return {
        "profile": profile_to_dict(profile) if profile else None,
        "instruments": [
            {
                "instrument_id": inst.instrument_id,
                "full_name": inst.full_name,
                "disclosure": inst.disclosure,
                "items": [{"item_id": i.item_id, "prompt": i.prompt} for i in inst.items],
                "options": [{"label": o.label, "value": o.value} for o in inst.scale.options],
            }
            for inst in MVP_INSTRUMENTS
        ],
        "last_scores": _latest_scores(conn, tenant_id, member_id),
        "cooking_confidence": {
            "current": assessed.get("cooking_confidence"),
            "options": [{"value": k, "label": v} for k, v in CONFIDENCE_LABELS.items()],
        },
        "weeknight_minutes": {
            "current": assessed.get("weeknight_minutes"),
            "options": list(WEEKNIGHT_MINUTES),
        },
        "cuisines": {
            "current": current_cuisine_interests(conn, tenant_id, member_id),
            "options": cuisine_options or [],
        },
    }


# -- completing ------------------------------------------------------------------


@dataclass
class CheckinResult:
    checkin_id: str
    changes: list[str] = field(default_factory=list)
    screener_changes: list[dict] = field(default_factory=list)
    next_due_at: str | None = None
    constraints_added: int = 0
    constraints_retracted: int = 0


def _profile_changes(old: IntakeProfile | None, new: IntakeProfile) -> list[str]:
    if old is None:
        return ["profile created"]
    out: list[str] = []
    labels = {"life_stage": "life stage", "weight_kg": "weight", "height_cm": "height",
              "year_of_birth": "year of birth", "sex_assigned_at_birth": "sex at birth"}
    for attr, label in labels.items():
        a, b = getattr(old, attr), getattr(new, attr)
        if a != b:
            out.append(f"{label}: {a if a is not None else '—'} → {b if b is not None else '—'}")
    for attr, noun in (("allergens", "allergy"), ("dietary_preferences", "preference"),
                       ("conditions", "condition"), ("avoid_foods", "avoided food")):
        before = {x.lower() for x in getattr(old, attr)}
        after = {x.lower() for x in getattr(new, attr)}
        out += [f"added {noun}: {x}" for x in sorted(after - before)]
        out += [f"removed {noun}: {x}" for x in sorted(before - after)]
    return out


def complete_checkin(
    conn: sqlite3.Connection,
    tenant_id: str,
    member_id: str,
    *,
    profile: IntakeProfile,
    screeners: dict[str, dict[str, int]] | None = None,
    cooking_confidence: int | None = None,
    weeknight_minutes: int | None = None,
    cuisines_to_try: list[str] | None = None,
    now: datetime | None = None,
) -> CheckinResult:
    """Apply a check-in. Validates everything before writing anything;
    all writes land in one transaction so a crash can't leave the revised
    profile saved with constraints underived (fail-open window,
    2026-10-06 audit)."""
    from nutrime.db import transaction

    with transaction(conn):
        return _complete_checkin(
            conn, tenant_id, member_id,
            profile=profile, screeners=screeners,
            cooking_confidence=cooking_confidence,
            weeknight_minutes=weeknight_minutes,
            cuisines_to_try=cuisines_to_try, now=now,
        )


def _complete_checkin(
    conn: sqlite3.Connection,
    tenant_id: str,
    member_id: str,
    *,
    profile: IntakeProfile,
    screeners: dict[str, dict[str, int]] | None = None,
    cooking_confidence: int | None = None,
    weeknight_minutes: int | None = None,
    cuisines_to_try: list[str] | None = None,
    now: datetime | None = None,
) -> CheckinResult:
    from nutrime.consent import require_consent
    from nutrime.intake.baseline import MVP_INSTRUMENTS
    from nutrime.intake.store import save_screener_responses
    from nutrime.knowledge.derivation import sync_from_intake
    from nutrime.knowledge.store import (
        Provenance,
        RetractionReason,
        insert_atom,
        list_atoms,
        retract_entry,
    )
    from nutrime.members import get_member, subject_ids_for

    get_member(conn, tenant_id, member_id)  # active member or MemberError
    screeners = screeners or {}
    instruments = {i.instrument_id: i for i in MVP_INSTRUMENTS}
    unknown = sorted(set(screeners) - set(instruments))
    if unknown:
        raise ValueError(f"unknown instrument(s): {', '.join(unknown)}")
    for inst_id, responses in screeners.items():
        instruments[inst_id].score(responses)  # raises on bad answers
    if cooking_confidence is not None and cooking_confidence not in CONFIDENCE_LABELS:
        raise ValueError("cooking confidence must be 1-5")
    if weeknight_minutes is not None and not 5 <= int(weeknight_minutes) <= 240:
        raise ValueError("weeknight time must be 5-240 minutes")
    cuisines = sorted({c.strip().lower() for c in (cuisines_to_try or []) if c.strip()})

    require_consent(conn, tenant_id, "intake_profile", member_id=member_id)
    if screeners:
        require_consent(conn, tenant_id, "intake_screener", member_id=member_id)
    consent_derived = None
    if cooking_confidence is not None or weeknight_minutes is not None or cuisines_to_try is not None:
        consent_derived = require_consent(
            conn, tenant_id, "knowledge_derived", member_id=member_id
        )

    before_scores = _latest_scores(conn, tenant_id, member_id)
    old_profile = load_member_profile(conn, tenant_id, member_id)
    result = CheckinResult(checkin_id=new_checkin_id())
    result.changes = _profile_changes(old_profile, profile)
    save_member_profile(conn, tenant_id, member_id, profile)

    for inst_id, responses in screeners.items():
        save_screener_responses(
            conn, tenant_id, instruments[inst_id], responses, member_id=member_id
        )
        new = instruments[inst_id].score(responses)
        prev = before_scores.get(inst_id)
        result.screener_changes.append({
            "instrument_id": inst_id,
            "name": instruments[inst_id].full_name,
            "previous": prev["score"] if prev else None,
            "now": new.score,
            "positive": new.positive,
        })

    assessed = _latest_self_assessments(conn, tenant_id, member_id)
    for measure, value in (("cooking_confidence", cooking_confidence),
                           ("weeknight_minutes", weeknight_minutes)):
        if value is None:
            continue
        if assessed.get(measure) != value:
            if assessed.get(measure) is not None:
                result.changes.append(f"{measure.replace('_', ' ')}: {assessed[measure]} → {value}")
            insert_atom(
                conn, tenant_id, atom_type="self_assessment",
                provenance=Provenance.CONVERSATIONAL_ELICITATION,
                payload={"measure": measure, "value": int(value), "source": "checkin"},
                subject_id=member_id, consent_record_id=consent_derived,
            )

    if cuisines_to_try is not None:
        subjects = subject_ids_for(conn, tenant_id, member_id)
        current = {
            str(a.payload.get("cuisine")): a
            for a in list_atoms(conn, tenant_id, atom_type="cuisine_interest")
            if a.subject_id in subjects
        }
        for cuisine, atom in current.items():
            if cuisine not in cuisines:
                retract_entry(conn, tenant_id, atom.id, RetractionReason.USER_CORRECTION)
        for cuisine in cuisines:
            if cuisine not in current:
                insert_atom(
                    conn, tenant_id, atom_type="cuisine_interest",
                    provenance=Provenance.CONVERSATIONAL_ELICITATION,
                    payload={"cuisine": cuisine, "source": "checkin"},
                    subject_id=member_id, consent_record_id=consent_derived,
                )
                result.changes.append(f"wants to try: {cuisine}")

    outcome = sync_from_intake(conn, tenant_id)
    result.constraints_added = outcome.constraints_added
    result.constraints_retracted = outcome.constraints_retracted

    completed = now or _now()
    conn.execute(
        "INSERT INTO checkin (id, tenant_id, member_id, completed_at, status, summary)"
        " VALUES (?, ?, ?, ?, 'completed', ?)",
        (result.checkin_id, tenant_id, member_id, _iso(completed), json.dumps({
            "changes": result.changes,
            "screener_changes": result.screener_changes,
            "constraints_added": result.constraints_added,
            "constraints_retracted": result.constraints_retracted,
        })),
    )
    conn.execute(
        "UPDATE checkin_schedule SET snoozed_until = NULL"
        " WHERE tenant_id = ? AND member_id = ?",
        (tenant_id, member_id),
    )
    maybe_commit(conn)
    result.next_due_at = checkin_status(conn, tenant_id, member_id, now=completed).due_at
    return result


def checkin_history(
    conn: sqlite3.Connection, tenant_id: str, member_id: str, *, limit: int = 12
) -> list[dict]:
    rows = conn.execute(
        "SELECT id, completed_at, status, summary FROM checkin"
        " WHERE tenant_id = ? AND member_id = ? ORDER BY completed_at DESC LIMIT ?",
        (tenant_id, member_id, limit),
    ).fetchall()
    return [
        {"id": r[0], "completed_at": r[1], "status": r[2], **json.loads(r[3])}
        for r in rows
    ]


def cuisine_options(vault, limit: int = 24) -> list[str]:
    """Cuisines present in the collection, most common first."""
    from nutrime.recipes.search import canonical_cuisine

    counts: dict[str, int] = {}
    for record in vault.iter_recipes():
        if record.frontmatter.get("vetting_status") in ("quarantined", "duplicate"):
            continue
        for tag in record.frontmatter.get("cuisine_tradition_tags") or []:
            tag = canonical_cuisine(str(tag))
            if tag and tag not in ("unknown", "other"):
                counts[tag] = counts.get(tag, 0) + 1
    return [c for c, _ in sorted(counts.items(), key=lambda kv: -kv[1])][:limit]


# -- interactive (CLI) -------------------------------------------------------------


def run_checkin_interactive(
    conn: sqlite3.Connection, tenant_id: str, member_id: str,
    *, prompter, emitter, vault=None,
) -> CheckinResult | None:
    """Terminal check-in: show each current answer, Enter keeps it."""
    from dataclasses import replace as _replace

    from nutrime.intake.baseline import MVP_INSTRUMENTS, _administer_instrument

    profile = load_member_profile(conn, tenant_id, member_id)
    if profile is None:
        emitter("No profile yet — run `nutrime intake` first; check-ins revise it.")
        return None
    emitter("Check-in — about 10 minutes. Press Enter to keep an answer.")

    def keep(prompt: str, current) -> str:
        shown = "—" if current in (None, "", ()) else current
        answer = prompter(f"{prompt} [{shown}]: ").strip()
        return answer

    stage = keep("Life stage (adult, pregnant, lactating, older_adult, child…)", profile.life_stage)
    weight = keep("Weight in kg (optional)", profile.weight_kg)
    allergens = keep("Allergies, comma-separated ('none' to clear)", ", ".join(profile.allergens))
    prefs = keep("Dietary preferences, comma-separated ('none' to clear)",
                 ", ".join(profile.dietary_preferences))

    def as_list(answer: str, current: tuple[str, ...]) -> tuple[str, ...]:
        if not answer:
            return current
        if answer.lower() == "none":
            return ()
        return tuple(x.strip() for x in answer.split(",") if x.strip())

    revised = _replace(
        profile,
        life_stage=stage or profile.life_stage,
        weight_kg=float(weight) if weight else profile.weight_kg,
        allergens=as_list(allergens, profile.allergens),
        dietary_preferences=as_list(prefs, profile.dietary_preferences),
    )
    screeners = {}
    if prompter("Retake the screening questions? [Y/n]: ").strip().lower() not in ("n", "no"):
        for inst in MVP_INSTRUMENTS:
            screeners[inst.instrument_id] = dict(
                _administer_instrument(prompter, emitter, inst).responses
            )
    emitter("How do you feel about cooking these days?")
    for value, label in CONFIDENCE_LABELS.items():
        emitter(f"  {value}. {label}")
    conf = prompter("Choose 1-5 (Enter to skip): ").strip()
    mins = prompter("Weeknight cooking time in minutes (Enter to skip): ").strip()
    options = cuisine_options(vault) if vault is not None else []
    if options:
        emitter("Cuisines in the collection: " + ", ".join(options))
    current = current_cuisine_interests(conn, tenant_id, member_id)
    cuisines = keep("Cuisines to try more of, comma-separated", ", ".join(current))
    result = complete_checkin(
        conn, tenant_id, member_id,
        profile=revised, screeners=screeners,
        cooking_confidence=int(conf) if conf else None,
        weeknight_minutes=int(mins) if mins else None,
        cuisines_to_try=list(as_list(cuisines, tuple(current))),
    )
    emitter("Check-in saved.")
    for change in result.changes or ["nothing changed"]:
        emitter(f"  - {change}")
    emitter(f"Next check-in around {str(result.next_due_at)[:10]}.")
    return result
