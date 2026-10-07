"""Activity view + notifications (C5 Q5.2 / Q5.4).

``activity_feed`` is the "show me everything the system did with my data"
surface (Q5.4 dedicated audit view, Rule 8 surface-the-trail): audit
events, model calls, consent decisions, check-ins, cooked meals and
profile revisions, in plain words, newest first. It reads the existing
records — nothing here writes.

``notifications`` computes what is worth interrupting a member for right
now (Q5.2). Categories are per-member switches; the defaults are
material-only per the spec: per-meal feedback in its window, a due
check-in, and system warnings that put data at risk. Practical nudges
(use-soon items, no plan for tomorrow, new recipes collected) exist but
start switched off.
"""

from __future__ import annotations
from nutrime.db import maybe_commit

import json
import sqlite3
from datetime import date, datetime, timedelta, timezone

NOTIFICATION_CATEGORIES: dict[str, dict] = {
    "feel_prompt": {"label": "How a meal made you feel (a few hours after cooking)", "default": True},
    "checkin_due": {"label": "A check-in is due", "default": True},
    "system_warning": {"label": "Something needs fixing (backups, updates)", "default": True},
    "use_soon": {"label": "Food in the kitchen to use soon", "default": False},
    "plan_gap": {"label": "Nothing planned for tomorrow", "default": False},
    "new_recipes": {"label": "New recipes collected this week", "default": False},
}

_CONSENT_LABELS = {
    "intake_profile": "your profile answers",
    "intake_screener": "screening questions",
    "inventory": "kitchen inventory",
    "knowledge_derived": "what the app works out from your answers",
    "meal_feedback_time": "cooking ratings and times",
    "meal_feedback_semantic": "how meals made you feel",
}


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# -- settings -------------------------------------------------------------------


def notification_settings(conn, tenant_id: str, member_id: str) -> dict[str, bool]:
    stored = {
        k.removeprefix("notify."): v == "on"
        for k, v in conn.execute(
            "SELECT key, value FROM member_setting"
            " WHERE tenant_id = ? AND member_id = ? AND key LIKE 'notify.%'",
            (tenant_id, member_id),
        )
    }
    return {
        cat: stored.get(cat, meta["default"]) for cat, meta in NOTIFICATION_CATEGORIES.items()
    }


def set_notification(conn, tenant_id: str, member_id: str, category: str, on: bool) -> None:
    if category not in NOTIFICATION_CATEGORIES:
        raise ValueError(f"unknown notification category {category!r}")
    conn.execute(
        "INSERT INTO member_setting (tenant_id, member_id, key, value) VALUES (?, ?, ?, ?)"
        " ON CONFLICT(tenant_id, member_id, key) DO UPDATE SET value = excluded.value",
        (tenant_id, member_id, f"notify.{category}", "on" if on else "off"),
    )
    maybe_commit(conn)


# -- notifications ----------------------------------------------------------------


def notifications(app, member_id: str, *, now: datetime | None = None) -> list[dict]:
    """Current notices for this member, filtered by their switches. Each has
    a stable ``key`` so the page can remember dismissals."""
    from nutrime.checkins import checkin_status
    from nutrime.feedback import meal_history
    from nutrime.inventory.store import expiring_names

    now = now or datetime.now(timezone.utc)
    on = notification_settings(app.substrate, app.tenant_id, member_id)
    out: list[dict] = []

    if on["feel_prompt"]:
        for entry in meal_history(app.substrate, app.tenant_id, limit=10, member_id=member_id):
            cooked = _parse(entry.cooked_at)
            if entry.body_response is None and cooked and (
                timedelta(hours=2) <= now - cooked <= timedelta(hours=48)
            ):
                out.append({
                    "key": f"feel:{entry.meal_event_id}", "category": "feel_prompt",
                    "text": f"How did {entry.recipe_title} make you feel?",
                    "action": "home",
                })
                break

    if on["checkin_due"]:
        st = checkin_status(app.substrate, app.tenant_id, member_id, now=now)
        if st.due:
            out.append({
                "key": f"checkin:{st.due_at}", "category": "checkin_due",
                "text": "Your check-in is due (about 10 minutes).", "action": "checkin",
            })

    if on["system_warning"]:
        from nutrime.maintenance import run_doctor

        for check in run_doctor(app.data_dir, check_model=False):
            if check.status == "fail" or check.name == "Backups" and check.status == "warn":
                out.append({
                    "key": f"system:{check.name}:{check.detail}", "category": "system_warning",
                    "text": f"{check.name}: {check.detail} {check.fix}".strip(),
                    "action": "profile",
                })

    if on["use_soon"]:
        soon = expiring_names(app.substrate, app.tenant_id, today=date.today().isoformat())
        if soon:
            names = ", ".join(sorted(i.name for i in soon)[:4])
            out.append({
                "key": f"use_soon:{date.today().isoformat()}", "category": "use_soon",
                "text": f"Use soon: {names}.", "action": "home",
            })

    if on["plan_gap"]:
        from nutrime.plans.store import PlanVault

        vault = PlanVault(app.corpus_dir)
        plans = vault.list_plans() if vault.root.exists() else []
        covered = False
        if plans:
            latest = plans[0]  # list_plans is newest-first
            created = _parse(str(latest.frontmatter.get("created_at")))
            if created:
                tomorrow_day = (now.date() - created.date()).days + 2
                covered = any(e.day == tomorrow_day and e.filled for e in latest.entries())
        if not covered:
            out.append({
                "key": f"plan_gap:{now.date().isoformat()}", "category": "plan_gap",
                "text": "Nothing is planned for tomorrow.", "action": "plans",
            })

    if on["new_recipes"]:
        week_ago = (now - timedelta(days=7)).isoformat()
        from nutrime.recipes.store import RecipeVault

        fresh = sum(
            1 for r in RecipeVault(app.corpus_dir).iter_recipes()
            if str((r.frontmatter.get("attribution") or {}).get("ingested_at", "")) >= week_ago[:19]
            and r.frontmatter.get("vetting_status") not in ("quarantined", "duplicate")
        )
        if fresh:
            out.append({
                "key": f"new_recipes:{now.date().isocalendar()[1]}", "category": "new_recipes",
                "text": f"{fresh} new recipes were added this week.", "action": "recipes",
            })
    return out


# -- activity --------------------------------------------------------------------


def _event_text(event) -> tuple[str, str] | None:
    p = event.payload or {}
    sub = event.event_subkind or ""
    if sub == "pre_egress_allowed":
        dest = str(p.get("destination", ""))
        where = "the local model on this computer" if dest.startswith("local") else dest
        return "model", f"Sent a request to {where} ({p.get('query_type', '')}), after the privacy checks passed."
    if sub == "pre_egress_blocked":
        return "privacy", f"Blocked a request before it left: {p.get('reason', '')}"
    if sub == "surface_rule":
        verb = "Hid" if p.get("action") == "block" else "Added a consult-a-professional note to"
        return "safety", f"{verb} a planner note ({p.get('rule')}): {p.get('reason', '')}"
    if sub == "plan_slot_swapped":
        return "plans", f"Swapped day {p.get('day')} {p.get('slot')} in a plan."
    if sub == "inventory_item_consumed":
        return "kitchen", f"Removed {p.get('name')} from the kitchen list after cooking."
    if sub == "tenant_created":
        return "setup", "Set up this household."
    return None


def activity_feed(app, member_id: str, *, days: int = 30, limit: int = 150) -> list[dict]:
    from nutrime.knowledge.store import list_atoms
    from nutrime.members import subject_ids_for

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()[:19]
    items: list[dict] = []

    for event in app.audit.events(limit=500):
        if str(event.recorded_at)[:19] < since:
            continue
        mapped = _event_text(event)
        if mapped:
            items.append({"at": event.recorded_at, "kind": mapped[0], "text": mapped[1]})

    for req in app.audit.llm_requests(limit=200):
        if str(req.recorded_at)[:19] < since:
            continue
        outcome = "answered" if req.outcome == "success" else f"failed ({req.outcome})"
        items.append({
            "at": req.recorded_at, "kind": "model",
            "text": f"Model {req.llm_model} via {req.llm_provider} {outcome}"
                    + (f" for {req.caller_context}" if req.caller_context else "") + ".",
        })

    for rid, cat, purpose, granted, at, subject in app.substrate.execute(
        "SELECT id, data_category, purpose, granted, granted_at, subject_user"
        " FROM consent_record WHERE tenant_id = ? AND (subject_user = 'primary' OR subject_user = ?)"
        " AND granted_at >= ? ORDER BY granted_at",
        (app.tenant_id, member_id, since),
    ):
        who = "for you" if subject == member_id else "household default"
        what = _CONSENT_LABELS.get(cat, cat)
        purpose_text = "research totals" if purpose == "publication_aggregate" else "use on this computer"
        items.append({
            "at": at, "kind": "privacy",
            "text": f"Privacy: {what} ({purpose_text}) turned {'on' if granted else 'off'}, {who}.",
        })

    for cid, at, summary in app.substrate.execute(
        "SELECT id, completed_at, summary FROM checkin WHERE tenant_id = ? AND member_id = ?"
        " AND completed_at >= ?",
        (app.tenant_id, member_id, since),
    ):
        changes = json.loads(summary).get("changes") or []
        items.append({
            "at": at, "kind": "check-in",
            "text": "Check-in: " + ("; ".join(changes) if changes else "no changes") + ".",
        })

    subjects = set(subject_ids_for(app.substrate, app.tenant_id, member_id))
    for atom in list_atoms(app.substrate, app.tenant_id, atom_type="meal_event"):
        if atom.subject_id in subjects and str(atom.recorded_at)[:19] >= since:
            items.append({
                "at": atom.recorded_at, "kind": "meals",
                "text": f"Recorded that you cooked {atom.payload.get('recipe_title', 'a meal')}.",
            })

    for (at,) in app.substrate.execute(
        "SELECT replaced_at FROM intake_profile_history WHERE tenant_id = ? AND member_id = ?"
        " AND replaced_at >= ?",
        (app.tenant_id, member_id, since),
    ):
        items.append({"at": at, "kind": "profile", "text": "Profile revised (the previous version is kept)."})

    items.sort(key=lambda i: str(i["at"]), reverse=True)
    return items[:limit]
