"""Notifications (C5 Q5.2) and the activity view (Q5.4)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from nutrime.activity import (
    NOTIFICATION_CATEGORIES,
    activity_feed,
    notification_settings,
    notifications,
    set_notification,
)
from nutrime.app import initialize
from nutrime.consent import record_decision
from nutrime.feedback import record_meal_event
from nutrime.intake.store import IntakeProfile, save_member_profile


@pytest.fixture
def app(tmp_path: Path):
    a = initialize(data_dir=tmp_path)
    yield a
    a.substrate.close(); a.operational.close()


def test_defaults_are_material_only(app) -> None:
    s = notification_settings(app.substrate, app.tenant_id, app.default_member_id)
    assert s == {k: v["default"] for k, v in NOTIFICATION_CATEGORIES.items()}
    assert s["feel_prompt"] and s["checkin_due"] and s["system_warning"]
    assert not s["use_soon"] and not s["plan_gap"] and not s["new_recipes"]


def test_switches_are_per_member(app) -> None:
    from nutrime.members import add_member

    sam = add_member(app.substrate, app.tenant_id, "Sam").id
    set_notification(app.substrate, app.tenant_id, sam, "plan_gap", True)
    assert notification_settings(app.substrate, app.tenant_id, sam)["plan_gap"]
    assert not notification_settings(app.substrate, app.tenant_id, app.default_member_id)["plan_gap"]
    with pytest.raises(ValueError):
        set_notification(app.substrate, app.tenant_id, sam, "spam", True)


def test_feel_prompt_inside_its_window_only(app) -> None:
    me = app.default_member_id
    now = datetime.now(timezone.utc)
    record_meal_event(app.substrate, app.tenant_id, recipe_id="r", recipe_title="Stew",
                      cooked_at=(now - timedelta(minutes=30)).isoformat())
    assert not [n for n in notifications(app, me, now=now) if n["category"] == "feel_prompt"]
    later = now + timedelta(hours=3)
    [n] = [n for n in notifications(app, me, now=later) if n["category"] == "feel_prompt"]
    assert "Stew" in n["text"]
    assert not [n for n in notifications(app, me, now=now + timedelta(days=3))
                if n["category"] == "feel_prompt"]


def test_checkin_and_backup_warnings(app) -> None:
    me = app.default_member_id
    save_member_profile(app.substrate, app.tenant_id, me,
                        IntakeProfile(year_of_birth=1990, sex_assigned_at_birth="male", life_stage="adult"))
    later = datetime.now(timezone.utc) + timedelta(days=40)
    cats = {n["category"] for n in notifications(app, me, now=later)}
    assert {"checkin_due", "system_warning"} <= cats   # no backup yet
    set_notification(app.substrate, app.tenant_id, me, "system_warning", False)
    cats = {n["category"] for n in notifications(app, me, now=later)}
    assert "system_warning" not in cats


def test_activity_feed_in_plain_words(app) -> None:
    me = app.default_member_id
    record_decision(app.substrate, app.tenant_id, data_category="meal_feedback_semantic",
                    purpose="local_operation", granted=False, member_id=me)
    record_meal_event(app.substrate, app.tenant_id, recipe_id="r", recipe_title="Stew")
    texts = [i["text"] for i in activity_feed(app, me)]
    assert any("how meals made you feel" in t and "off" in t and "for you" in t for t in texts)
    assert any("cooked Stew" in t for t in texts)
    assert any("Set up this household" in t for t in texts)
