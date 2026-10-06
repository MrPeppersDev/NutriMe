"""Periodic check-ins (intake-pattern.md Mode 2)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.checkins import (
    FAST_CHANGE_INTERVAL_DAYS,
    checkin_history,
    checkin_questions,
    checkin_status,
    complete_checkin,
    set_interval,
    snooze,
)
from nutrime.consent import ConsentError, record_decision
from nutrime.intake.instruments import HUNGER_VITAL_SIGN
from nutrime.intake.store import IntakeProfile, save_member_profile
from nutrime.knowledge.derivation import sync_from_intake
from nutrime.knowledge.store import list_synthesized_entries
from nutrime.members import add_member, archive_member

NOW = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)


def _profile(**kw) -> IntakeProfile:
    base = dict(year_of_birth=1990, sex_assigned_at_birth="female", life_stage="adult")
    base.update(kw)
    return IntakeProfile(**base)


def _constraints(app) -> set[str]:
    return {
        e.payload["abstracted_text"]
        for e in list_synthesized_entries(app.substrate, app.tenant_id, entry_type="abstracted_constraint")
    }


@pytest.fixture
def app(tmp_path: Path):
    a = initialize(data_dir=tmp_path)
    yield a
    a.substrate.close()
    a.operational.close()


def _backdate_profile(app, member_id: str, days: int) -> None:
    ts = (NOW - timedelta(days=days)).isoformat().replace("+00:00", "Z")
    app.substrate.execute(
        "UPDATE intake_profile_v2 SET created_at = ? WHERE member_id = ?", (ts, member_id)
    )
    app.substrate.commit()


class TestSchedule:
    def test_not_due_without_profile(self, app) -> None:
        status = checkin_status(app.substrate, app.tenant_id, app.default_member_id, now=NOW)
        assert not status.has_profile and not status.due

    def test_due_after_28_days(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        _backdate_profile(app, me, 27)
        assert not checkin_status(app.substrate, app.tenant_id, me, now=NOW).due
        _backdate_profile(app, me, 29)
        status = checkin_status(app.substrate, app.tenant_id, me, now=NOW)
        assert status.due and status.interval_days == 28 and status.interval_source == "default"

    def test_pregnancy_shortens_interval(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile(life_stage="pregnant"))
        status = checkin_status(app.substrate, app.tenant_id, me, now=NOW)
        assert status.interval_days == FAST_CHANGE_INTERVAL_DAYS
        assert status.interval_source == "life_stage"

    def test_custom_interval_and_validation(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        set_interval(app.substrate, app.tenant_id, me, 56)
        assert checkin_status(app.substrate, app.tenant_id, me, now=NOW).interval_days == 56
        with pytest.raises(ValueError):
            set_interval(app.substrate, app.tenant_id, me, 3)
        set_interval(app.substrate, app.tenant_id, me, None)
        assert checkin_status(app.substrate, app.tenant_id, me, now=NOW).interval_source == "default"

    def test_snooze_pushes_due_date(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        _backdate_profile(app, me, 40)
        assert checkin_status(app.substrate, app.tenant_id, me, now=NOW).due
        snooze(app.substrate, app.tenant_id, me, now=NOW)
        status = checkin_status(app.substrate, app.tenant_id, me, now=NOW)
        assert not status.due and status.snoozed_until
        later = NOW + timedelta(days=8)
        assert checkin_status(app.substrate, app.tenant_id, me, now=later).due

    def test_completing_resets_the_clock(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        _backdate_profile(app, me, 40)
        result = complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(), now=NOW)
        assert not checkin_status(app.substrate, app.tenant_id, me, now=NOW).due
        assert result.next_due_at.startswith("2026-11-03")


class TestCompleting:
    def test_removed_allergy_leaves_the_avoid_list(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me,
                            _profile(allergens=("peanuts", "milk")))
        sync_from_intake(app.substrate, app.tenant_id)
        assert {"avoids peanuts", "avoids milk"} <= _constraints(app)
        result = complete_checkin(
            app.substrate, app.tenant_id, me, profile=_profile(allergens=("peanuts",)), now=NOW
        )
        assert "removed allergy: milk" in result.changes
        assert result.constraints_retracted == 1
        assert "avoids milk" not in _constraints(app)
        assert "avoids peanuts" in _constraints(app)

    def test_shared_allergy_stays_while_anyone_has_it(self, app) -> None:
        me = app.default_member_id
        sam = add_member(app.substrate, app.tenant_id, "Sam").id
        save_member_profile(app.substrate, app.tenant_id, me, _profile(allergens=("milk",)))
        save_member_profile(app.substrate, app.tenant_id, sam, _profile(allergens=("milk",)))
        sync_from_intake(app.substrate, app.tenant_id)
        complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(), now=NOW)
        assert "avoids milk" in _constraints(app)  # Sam still has it

    def test_archived_member_allergy_retracted(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam").id
        save_member_profile(app.substrate, app.tenant_id, sam, _profile(allergens=("sesame",)))
        sync_from_intake(app.substrate, app.tenant_id)
        assert "avoids sesame" in _constraints(app)
        archive_member(app.substrate, app.tenant_id, sam)
        outcome = sync_from_intake(app.substrate, app.tenant_id)
        assert outcome.constraints_retracted == 1
        assert "avoids sesame" not in _constraints(app)

    def test_profile_history_is_kept(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile(life_stage="adult"))
        complete_checkin(app.substrate, app.tenant_id, me,
                         profile=_profile(life_stage="pregnant"), now=NOW)
        rows = app.substrate.execute(
            "SELECT profile FROM intake_profile_history WHERE member_id = ?", (me,)
        ).fetchall()
        assert len(rows) == 1 and '"life_stage": "adult"' in rows[0][0]

    def test_screener_change_reported(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        first = {i.item_id: 0 for i in HUNGER_VITAL_SIGN.items}
        complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(),
                         screeners={"hunger_vital_sign": first}, now=NOW)
        worse = {i.item_id: 2 for i in HUNGER_VITAL_SIGN.items}
        result = complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(),
                                  screeners={"hunger_vital_sign": worse},
                                  now=NOW + timedelta(days=30))
        [change] = result.screener_changes
        assert change["previous"] == 0 and change["now"] > 0 and change["positive"]

    def test_cooking_and_cuisines_recorded_and_boost_ranking(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        result = complete_checkin(
            app.substrate, app.tenant_id, me, profile=_profile(),
            cooking_confidence=3, weeknight_minutes=30, cuisines_to_try=["Thai", "korean"], now=NOW,
        )
        assert "wants to try: thai" in result.changes
        assert {"prefers thai", "prefers korean"} <= _constraints(app)
        q = checkin_questions(app.substrate, app.tenant_id, me)
        assert q["cooking_confidence"]["current"] == 3
        assert q["weeknight_minutes"]["current"] == 30
        assert q["cuisines"]["current"] == ["korean", "thai"]
        # next check-in drops korean → its preference leaves
        complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(),
                         cuisines_to_try=["thai"], now=NOW + timedelta(days=30))
        assert "prefers korean" not in _constraints(app)
        assert "prefers thai" in _constraints(app)

    def test_invalid_answers_write_nothing(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        with pytest.raises(ValueError):
            complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(life_stage="adult"),
                             screeners={"hunger_vital_sign": {"bogus": 1}}, now=NOW)
        assert checkin_history(app.substrate, app.tenant_id, me) == []

    def test_member_consent_decline_blocks(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        record_decision(app.substrate, app.tenant_id, data_category="intake_profile",
                        purpose="local_operation", granted=False, member_id=me)
        with pytest.raises(ConsentError):
            complete_checkin(app.substrate, app.tenant_id, me, profile=_profile(), now=NOW)

    def test_history(self, app) -> None:
        me = app.default_member_id
        save_member_profile(app.substrate, app.tenant_id, me, _profile())
        complete_checkin(app.substrate, app.tenant_id, me,
                         profile=_profile(weight_kg=70.0), now=NOW)
        [h] = checkin_history(app.substrate, app.tenant_id, me)
        assert h["status"] == "completed"
        assert any(c.startswith("weight") for c in h["changes"])


def test_cuisine_aliases_match_country_tags() -> None:
    from nutrime.recipes.search import canonical_cuisine

    assert canonical_cuisine("France") == "french"
    assert canonical_cuisine("United States") == "american"
    assert canonical_cuisine("thai") == "thai"


# -- CLI + web --------------------------------------------------------------------


def test_cli_interactive_checkin(tmp_path: Path, monkeypatch, capsys) -> None:
    from nutrime.cli import main

    app = initialize(data_dir=tmp_path)
    save_member_profile(app.substrate, app.tenant_id, None, _profile(allergens=("milk",)))
    app.substrate.close(); app.operational.close()
    answers = iter([
        "", "72", "none", "",   # stage keep, weight 72, clear allergies, prefs keep
        "n",                    # skip screeners
        "4", "30", "thai",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    assert main(["checkin", "--data-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "removed allergy: milk" in out and "wants to try: thai" in out
    assert main(["checkin", "--status", "--data-dir", str(tmp_path)]) == 0
    assert "next due" in capsys.readouterr().out


class TestWeb:
    @pytest.fixture
    def server(self, tmp_path: Path):
        import threading

        from nutrime.webui import serve

        srv = serve(data_dir=tmp_path, port=0)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        yield srv
        srv.shutdown(); t.join(timeout=5); srv.server_close()

    def _call(self, srv, path, payload=None):
        import json
        import urllib.error
        import urllib.request

        req = urllib.request.Request(
            f"http://127.0.0.1:{srv.server_address[1]}{path}",
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json"},
            method="POST" if payload is not None else "GET",
        )
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    PROFILE = {"year_of_birth": 1990, "sex_assigned_at_birth": "female",
               "life_stage": "adult", "allergens": ["peanuts", "milk"]}

    def test_status_questions_save(self, server) -> None:
        status, st = self._call(server, "/api/checkin/status")
        assert status == 200 and st["has_profile"] is False
        self._call(server, "/api/intake", {"profile": self.PROFILE, "screeners": {}})
        _, st = self._call(server, "/api/checkin/status")
        assert st["has_profile"] and not st["due"] and st["interval_days"] == 28
        _, q = self._call(server, "/api/checkin/questions")
        assert q["profile"]["allergens"] == ["peanuts", "milk"]
        assert q["instruments"] and q["cooking_confidence"]["options"]
        status, res = self._call(server, "/api/checkin", {
            "profile": {**self.PROFILE, "allergens": ["peanuts"]},
            "screeners": {}, "cooking_confidence": 3, "weeknight_minutes": 45,
            "cuisines": ["thai"],
        })
        assert status == 200
        assert "removed allergy: milk" in res["changes"]
        assert res["constraints_retracted"] == 1
        _, derived = self._call(server, "/api/derived")
        assert "avoids milk" not in derived["constraints"]
        _, st = self._call(server, "/api/checkin/status")
        assert st["history"][0]["status"] == "completed"

    def test_interval_snooze_and_errors(self, server) -> None:
        self._call(server, "/api/intake", {"profile": self.PROFILE, "screeners": {}})
        _, st = self._call(server, "/api/checkin/interval", {"days": 56})
        assert st["interval_days"] == 56 and st["interval_source"] == "custom"
        assert self._call(server, "/api/checkin/interval", {"days": 2})[0] == 400
        status, res = self._call(server, "/api/checkin/snooze", {})
        assert status == 200 and res["snoozed_until"]
        status, res = self._call(server, "/api/checkin", {
            "profile": self.PROFILE, "screeners": {"hunger_vital_sign": [1]}})
        assert status == 400

    def test_page_has_checkin_surfaces(self, server) -> None:
        import urllib.request

        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/") as r:
            body = r.read().decode()
        for marker in ('id="checkinCard"', 'id="checkinSettings"', "async function openCheckin",
                       "async function saveCheckin"):
            assert marker in body
