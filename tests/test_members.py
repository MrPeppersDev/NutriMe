"""Household members (#29): identity, per-member state, household union."""

import json
import shutil
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.consent import (
    ConsentError,
    current_decision,
    list_current,
    record_decision,
    require_consent,
)
from nutrime.db import apply_migrations, connect
from nutrime.feedback import meal_history, record_body_response, record_meal_event
from nutrime.intake.instruments import HUNGER_VITAL_SIGN
from nutrime.intake.store import (
    IntakeProfile,
    household_profiles,
    load_member_profile,
    save_member_profile,
    save_screener_responses,
)
from nutrime.knowledge.derivation import sync_from_intake
from nutrime.knowledge.store import list_atoms, list_synthesized_entries
from nutrime.members import (
    MemberError,
    add_member,
    archive_member,
    bootstrap_default_member,
    get_member,
    list_members,
    rename_member,
)
from nutrime.paths import default_substrate_migrations_dir
from nutrime.tenancy import bootstrap_tenant


def _profile(**kw) -> IntakeProfile:
    base = dict(year_of_birth=1988, sex_assigned_at_birth="female", life_stage="adult")
    base.update(kw)
    return IntakeProfile(**base)


@pytest.fixture
def app(tmp_path: Path):
    application = initialize(data_dir=tmp_path)
    yield application
    application.substrate.close()
    application.operational.close()


class TestMemberLifecycle:
    def test_install_has_one_default_member(self, app) -> None:
        members = list_members(app.substrate, app.tenant_id)
        assert [m.display_name for m in members] == ["Me"]
        assert app.default_member_id == members[0].id
        assert members[0].id.startswith("mem-")

    def test_bootstrap_is_idempotent(self, app) -> None:
        first = app.default_member_id
        assert bootstrap_default_member(app.substrate, app.tenant_id) == first
        assert len(list_members(app.substrate, app.tenant_id)) == 1

    def test_add_rename_archive(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "  Sam  ")
        assert sam.display_name == "Sam"
        rename_member(app.substrate, app.tenant_id, sam.id, "Samira")
        assert get_member(app.substrate, app.tenant_id, sam.id).display_name == "Samira"
        archive_member(app.substrate, app.tenant_id, sam.id)
        assert [m.display_name for m in list_members(app.substrate, app.tenant_id)] == ["Me"]
        everyone = list_members(app.substrate, app.tenant_id, include_archived=True)
        assert len(everyone) == 2  # archived, never deleted
        with pytest.raises(MemberError, match="archived"):
            get_member(app.substrate, app.tenant_id, sam.id)

    def test_names_unique_case_insensitive(self, app) -> None:
        add_member(app.substrate, app.tenant_id, "Sam")
        with pytest.raises(MemberError, match="already exists"):
            add_member(app.substrate, app.tenant_id, "sam")

    def test_blank_name_rejected(self, app) -> None:
        with pytest.raises(MemberError):
            add_member(app.substrate, app.tenant_id, "   ")

    def test_last_member_cannot_be_archived(self, app) -> None:
        with pytest.raises(MemberError, match="at least one"):
            archive_member(app.substrate, app.tenant_id, app.default_member_id)

    def test_unknown_member(self, app) -> None:
        with pytest.raises(MemberError):
            get_member(app.substrate, app.tenant_id, "mem-nope")


class TestLegacyUpgrade:
    def test_pre_29_profile_and_screeners_move_under_default_member(
        self, tmp_path: Path
    ) -> None:
        # Build a pre-#29 database: migrations 0001-0005 only, one legacy
        # profile row, one member-less screener batch.
        old_migrations = tmp_path / "old_migrations"
        old_migrations.mkdir()
        for sql in default_substrate_migrations_dir().glob("*.sql"):
            if int(sql.name.split("_")[0]) < 6:
                shutil.copy(sql, old_migrations / sql.name)
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        conn = connect(data_dir / "substrate.db")
        apply_migrations(conn, old_migrations)
        tenant_id = bootstrap_tenant(conn)
        conn.execute(
            "INSERT INTO intake_profile (tenant_id, year_of_birth,"
            " sex_assigned_at_birth, life_stage, allergens, created_at,"
            " updated_at) VALUES (?, 1980, 'male', 'adult', '[\"peanut\"]',"
            " '2026-07-01T00:00:00Z', '2026-07-01T00:00:00Z')",
            (tenant_id,),
        )
        conn.execute(
            "INSERT INTO intake_screener_response (tenant_id, instrument_id,"
            " instrument_version, item_id, response_value, administered_at)"
            " VALUES (?, 'hunger_vital_sign', 'v1', 'hvs_1', 0,"
            " '2026-07-01T00:00:00Z')",
            (tenant_id,),
        )
        conn.commit()
        conn.close()

        upgraded = initialize(data_dir=data_dir)
        try:
            member_id = upgraded.default_member_id
            profile = load_member_profile(upgraded.substrate, tenant_id, member_id)
            assert profile is not None
            assert profile.allergens == ("peanut",)
            (orphans,) = upgraded.substrate.execute(
                "SELECT COUNT(*) FROM intake_screener_response"
                " WHERE member_id IS NULL"
            ).fetchone()
            assert orphans == 0
        finally:
            upgraded.substrate.close()
            upgraded.operational.close()

        # Second start: nothing is copied again.
        again = initialize(data_dir=data_dir)
        try:
            (rows,) = again.substrate.execute(
                "SELECT COUNT(*) FROM intake_profile_v2"
            ).fetchone()
            assert rows == 1
            assert len(list_members(again.substrate, tenant_id)) == 1
        finally:
            again.substrate.close()
            again.operational.close()

    def test_legacy_atoms_not_duplicated_for_founding_member(self, app) -> None:
        # Pre-#29 derivation wrote atoms with subject_id = tenant_id.
        from nutrime.knowledge.store import Provenance, insert_atom

        insert_atom(
            app.substrate,
            app.tenant_id,
            atom_type="clinical_disclosure",
            provenance=Provenance.CONVERSATIONAL_ELICITATION,
            payload={"disclosure_type": "allergy", "disclosure_text": "peanut"},
            subject_id=app.tenant_id,
        )
        save_member_profile(
            app.substrate, app.tenant_id, None, _profile(allergens=("peanut",))
        )
        outcome = sync_from_intake(app.substrate, app.tenant_id)
        assert outcome.atoms_added.get("clinical_disclosure", 0) == 0


class TestPerMemberProfiles:
    def test_profiles_are_isolated(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(
            app.substrate, app.tenant_id, None, _profile(allergens=("milk",))
        )
        save_member_profile(
            app.substrate, app.tenant_id, sam.id,
            _profile(year_of_birth=2015, life_stage="child", allergens=("peanut",)),
        )
        me = load_member_profile(app.substrate, app.tenant_id, app.default_member_id)
        kid = load_member_profile(app.substrate, app.tenant_id, sam.id)
        assert me.allergens == ("milk",)
        assert kid.allergens == ("peanut",) and kid.life_stage == "child"

    def test_archived_members_drop_out_of_household(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(app.substrate, app.tenant_id, sam.id, _profile())
        assert sam.id in household_profiles(app.substrate, app.tenant_id)
        archive_member(app.substrate, app.tenant_id, sam.id)
        assert sam.id not in household_profiles(app.substrate, app.tenant_id)

    def test_cannot_save_for_archived_member(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        archive_member(app.substrate, app.tenant_id, sam.id)
        with pytest.raises(MemberError):
            save_member_profile(app.substrate, app.tenant_id, sam.id, _profile())

    def test_screeners_carry_member(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        save_screener_responses(
            app.substrate, app.tenant_id, HUNGER_VITAL_SIGN,
            {item.item_id: 0 for item in HUNGER_VITAL_SIGN.items},
            member_id=sam.id,
        )
        members = {
            r[0] for r in app.substrate.execute(
                "SELECT member_id FROM intake_screener_response"
            )
        }
        assert members == {sam.id}


class TestHouseholdUnion:
    def test_constraints_union_with_member_attribution(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(allergens=("milk",), dietary_preferences=("spicy",)),
        )
        save_member_profile(
            app.substrate, app.tenant_id, sam.id,
            _profile(allergens=("peanut", "milk")),
        )
        sync_from_intake(app.substrate, app.tenant_id)

        constraints = {
            e.payload["abstracted_text"]
            for e in list_synthesized_entries(
                app.substrate, app.tenant_id, entry_type="abstracted_constraint"
            )
        }
        # union, one row per constraint even when two members share it
        assert constraints == {"avoids milk", "avoids peanut", "prefers spicy"}

        atoms = list_atoms(app.substrate, app.tenant_id, atom_type="clinical_disclosure")
        by_subject = {}
        for a in atoms:
            by_subject.setdefault(a.subject_id, set()).add(a.payload["disclosure_text"])
        assert by_subject == {
            app.default_member_id: {"milk"},
            sam.id: {"peanut", "milk"},
        }

    def test_sync_is_idempotent(self, app) -> None:
        add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(
            app.substrate, app.tenant_id, None, _profile(allergens=("egg",))
        )
        sync_from_intake(app.substrate, app.tenant_id)
        again = sync_from_intake(app.substrate, app.tenant_id)
        assert again.total_atoms_added == 0
        assert again.constraints_added == 0


class TestPerMemberConsent:
    def test_household_baseline_covers_new_members(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        assert require_consent(
            app.substrate, app.tenant_id, "intake_screener", member_id=sam.id
        )

    def test_member_decline_overrides_household_only_for_them(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        record_decision(
            app.substrate, app.tenant_id,
            data_category="meal_feedback_semantic", purpose="local_operation",
            granted=False, member_id=sam.id,
        )
        with pytest.raises(ConsentError):
            require_consent(
                app.substrate, app.tenant_id, "meal_feedback_semantic",
                member_id=sam.id,
            )
        # everyone else unaffected
        assert require_consent(
            app.substrate, app.tenant_id, "meal_feedback_semantic",
            member_id=app.default_member_id,
        )
        household = current_decision(
            app.substrate, app.tenant_id, "meal_feedback_semantic", "local_operation"
        )
        assert household.granted and household.subject_user == "primary"

    def test_list_current_resolves_per_member(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        record_decision(
            app.substrate, app.tenant_id,
            data_category="inventory", purpose="publication_aggregate",
            granted=True, member_id=sam.id,
        )
        for_sam = {
            (r.data_category, r.purpose): r
            for r in list_current(app.substrate, app.tenant_id, member_id=sam.id)
        }
        assert for_sam[("inventory", "publication_aggregate")].granted
        assert for_sam[("inventory", "publication_aggregate")].subject_user == sam.id
        assert for_sam[("intake_profile", "local_operation")].subject_user == "primary"
        household = list_current(app.substrate, app.tenant_id)
        assert all(r.subject_user == "primary" for r in household)

    def test_member_decision_supersedes_only_own_row(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        for granted in (False, True):
            record_decision(
                app.substrate, app.tenant_id,
                data_category="inventory", purpose="local_operation",
                granted=granted, member_id=sam.id,
            )
        rows = app.substrate.execute(
            "SELECT subject_user, granted FROM consent_record"
            " WHERE data_category = 'inventory' AND purpose = 'local_operation'"
            " AND valid_until IS NULL ORDER BY subject_user"
        ).fetchall()
        assert sorted(rows) == sorted([("primary", 1), (sam.id, 1)])


class TestPerMemberFeedback:
    def test_atoms_carry_member_and_body_response_is_personal(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        mev = record_meal_event(
            app.substrate, app.tenant_id, recipe_id="rcp-x", recipe_title="Stew",
        )
        record_body_response(
            app.substrate, app.tenant_id, meal_event_id=mev,
            freetext_response="sleepy after", member_id=sam.id,
        )
        event = list_atoms(app.substrate, app.tenant_id, atom_type="meal_event")[0]
        assert event.subject_id == app.default_member_id

        mine = meal_history(app.substrate, app.tenant_id, member_id=app.default_member_id)
        theirs = meal_history(app.substrate, app.tenant_id, member_id=sam.id)
        assert mine[0].body_response is None  # I still owe my answer
        assert theirs[0].body_response == "sleepy after"

    def test_member_consent_decline_blocks_their_capture(self, app) -> None:
        sam = add_member(app.substrate, app.tenant_id, "Sam")
        record_decision(
            app.substrate, app.tenant_id,
            data_category="meal_feedback_semantic", purpose="local_operation",
            granted=False, member_id=sam.id,
        )
        mev = record_meal_event(
            app.substrate, app.tenant_id, recipe_id="rcp-x", recipe_title="Stew",
        )
        with pytest.raises(ConsentError):
            record_body_response(
                app.substrate, app.tenant_id, meal_event_id=mev,
                freetext_response="fine", member_id=sam.id,
            )


# -- web surface ----------------------------------------------------------------


@pytest.fixture
def server(tmp_path: Path):
    from nutrime.webui import serve

    srv = serve(data_dir=tmp_path, port=0)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv
    srv.shutdown()
    thread.join(timeout=5)
    srv.server_close()


def _call(srv, path: str, payload: dict | None = None, member: str | None = None):
    port = srv.server_address[1]
    headers = {"Content-Type": "application/json"}
    if member:
        headers["X-NutriMe-Member"] = member
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=data, headers=headers,
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _intake_body(allergens: list[str]) -> dict:
    return {
        "profile": {
            "year_of_birth": 1990,
            "sex_assigned_at_birth": "male",
            "life_stage": "adult",
            "allergens": allergens,
        },
        "screeners": {},
    }


class TestMembersWeb:
    def test_list_add_rename_archive(self, server) -> None:
        status, data = _call(server, "/api/members")
        assert status == 200 and [m["name"] for m in data["members"]] == ["Me"]
        status, data = _call(server, "/api/members", {"name": "Sam"})
        assert status == 200
        sam = data["added"]
        assert [m["name"] for m in data["members"]] == ["Me", "Sam"]
        status, data = _call(server, "/api/members/rename", {"id": sam, "name": "Sami"})
        assert [m["name"] for m in data["members"]] == ["Me", "Sami"]
        status, data = _call(server, "/api/members/archive", {"id": sam})
        assert [m["name"] for m in data["members"]] == ["Me"]

    def test_duplicate_name_is_400(self, server) -> None:
        _call(server, "/api/members", {"name": "Sam"})
        status, data = _call(server, "/api/members", {"name": "SAM"})
        assert status == 400 and "already exists" in data["error"]

    def test_intake_is_member_scoped(self, server) -> None:
        _, data = _call(server, "/api/members", {"name": "Sam"})
        sam = data["added"]
        status, saved = _call(server, "/api/intake", _intake_body(["peanuts"]), member=sam)
        assert status == 200 and saved["saved"]

        _, theirs = _call(server, "/api/intake/status", member=sam)
        _, mine = _call(server, "/api/intake/status")
        assert theirs["complete"] and theirs["profile"]["allergens"] == ["peanuts"]
        assert theirs["member_id"] == sam
        assert mine["complete"] is False

        _, members = _call(server, "/api/members")
        assert {m["name"]: m["has_profile"] for m in members["members"]} == {
            "Me": False, "Sam": True,
        }

    def test_skip_is_per_member(self, server) -> None:
        _, data = _call(server, "/api/members", {"name": "Sam"})
        _call(server, "/api/intake/skip", {})
        _, mine = _call(server, "/api/intake/status")
        _, theirs = _call(server, "/api/intake/status", member=data["added"])
        assert mine["skipped"] is True
        assert theirs["skipped"] is False

    def test_unknown_member_header_is_400(self, server) -> None:
        status, data = _call(server, "/api/intake/status", member="mem-bogus")
        assert status == 400 and "no member" in data["error"]

    def test_page_has_member_picker(self, server) -> None:
        port = server.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
            body = resp.read().decode()
        assert 'id="memberPicker"' in body
        assert "X-NutriMe-Member" in body


# -- CLI -------------------------------------------------------------------------


class TestMembersCli:
    def _run(self, tmp_path: Path, capsys, *argv: str) -> tuple[int, str]:
        from nutrime.cli import main

        code = main([*argv, "--data-dir", str(tmp_path)])
        return code, capsys.readouterr().out

    def test_add_list_rename_archive(self, tmp_path: Path, capsys) -> None:
        code, out = self._run(tmp_path, capsys, "members", "add", "Sam")
        assert code == 0 and "added Sam" in out
        code, out = self._run(tmp_path, capsys, "members", "list")
        assert "Me" in out and "(default)" in out and "Sam" in out
        code, out = self._run(tmp_path, capsys, "members", "rename", "sam", "Sami")
        assert code == 0 and "Sami" in out
        code, out = self._run(tmp_path, capsys, "members", "archive", "Sami")
        assert code == 0
        _, out = self._run(tmp_path, capsys, "members", "list")
        assert "Sami" not in out
        _, out = self._run(tmp_path, capsys, "members", "list", "--all")
        assert "Sami" in out and "archived" in out

    def test_consent_per_member(self, tmp_path: Path, capsys) -> None:
        self._run(tmp_path, capsys, "members", "add", "Sam")
        code, _ = self._run(
            tmp_path, capsys, "consent", "set", "meal_feedback_semantic",
            "decline", "--member", "Sam",
        )
        assert code == 0
        _, out = self._run(tmp_path, capsys, "consent", "list", "--member", "Sam")
        line = next(l for l in out.splitlines()
                    if "meal_feedback_semantic" in l and "local_operation" in l)
        assert "declined" in line and "[own]" in line
        _, out = self._run(tmp_path, capsys, "consent", "list")
        line = next(l for l in out.splitlines()
                    if "meal_feedback_semantic" in l and "local_operation" in l)
        assert "granted" in line

    def test_unknown_member_exits_2(self, tmp_path: Path, capsys) -> None:
        code, out = self._run(
            tmp_path, capsys, "consent", "list", "--member", "Nobody"
        )
        assert code == 2 and "no active member named 'Nobody'" in out
