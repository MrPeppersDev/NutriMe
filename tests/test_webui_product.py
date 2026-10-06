"""#33 product surfaces: plans, reorient tonight, consent, derived."""

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from nutrime.llm.base import ProviderResult
from nutrime.llm.client import LlmClient
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.themealdb import convert_meal
from nutrime.webui import serve


def _meal(meal_id: str, name: str, ingredients, category="Chicken"):
    meal = {
        "idMeal": meal_id, "strMeal": name, "strCategory": category,
        "strArea": "British", "strTags": "",
        "strInstructions": "Cook it well.\r\nServe it hot.",
        "strSource": f"https://example.com/{meal_id}",
    }
    for i in range(1, 21):
        meal[f"strIngredient{i}"] = ""
        meal[f"strMeasure{i}"] = ""
    for i, ing in enumerate(ingredients, start=1):
        meal[f"strIngredient{i}"] = ing
        meal[f"strMeasure{i}"] = "1"
    return meal


class PickFirst:
    name = "fake"
    model = "fake-model"
    capabilities = frozenset({"reasoning", "local-private"})

    def complete(self, request):
        ids = [
            line.split("id=")[1].split(" |")[0]
            for line in request.messages[0].content.splitlines() if "id=" in line
        ]
        return ProviderResult(
            text=json.dumps({"recipe_id": ids[0], "reason": "quick and easy"}),
            model="fake-model", stop_reason="end_turn",
            prompt_tokens=1, completion_tokens=1,
            request_payload="{}", response_payload="{}",
        )


@pytest.fixture
def server(tmp_path: Path):
    from nutrime.app import initialize

    app = initialize(data_dir=tmp_path)
    vault = RecipeVault(app.corpus_dir)
    vault.ensure()
    for meal in (
        _meal("1", "Chicken Bake", ["chicken", "spinach"]),
        _meal("2", "Beef Stew", ["beef", "potato"], category="Beef"),
        _meal("3", "Peanut Noodles", ["noodles", "peanut butter"], category="Pasta"),
        _meal("4", "Lamb Curry", ["lamb", "onion"], category="Lamb"),
    ):
        c = convert_meal(meal, ingested_at="2026-10-06T00:00:00Z")
        vault.write(c.recipe_id, c.frontmatter, c.cooklang_body)
    app.substrate.close()
    app.operational.close()
    srv = serve(data_dir=tmp_path, port=0)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv
    srv.shutdown()
    thread.join(timeout=5)
    srv.server_close()


def _call(srv, path, payload=None, member=None):
    headers = {"Content-Type": "application/json"}
    if member:
        headers["X-NutriMe-Member"] = member
    req = urllib.request.Request(
        f"http://127.0.0.1:{srv.server_address[1]}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers, method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def _with_model(srv):
    srv.llm_client_factory = lambda app: LlmClient(
        (PickFirst(),), app.rule_engine, app.audit
    )


class TestPlans:
    def test_generate_without_local_model_explains(self, server) -> None:
        server.llm_client_factory = lambda app: None
        status, data = _call(server, "/api/plans/generate", {"days": 2})
        assert status == 503
        assert data["code"] == "local_model_unavailable"
        assert "ollama" in data["error"].lower()

    def test_generate_list_detail(self, server) -> None:
        _with_model(server)
        status, made = _call(server, "/api/plans/generate", {"days": 2})
        assert status == 200 and made["filled"] == 2
        _, listing = _call(server, "/api/plans")
        assert listing["plans"][0]["plan_id"] == made["plan_id"]
        assert listing["plans"][0]["today_day"] == 1
        _, detail = _call(server, f"/api/plans/{made['plan_id']}")
        assert [e["day"] for e in detail["entries"]] == [1, 2]
        assert all("TheMealDB" in e["attribution"] for e in detail["entries"])

    def test_bad_requests(self, server) -> None:
        _with_model(server)
        assert _call(server, "/api/plans/generate", {"days": 30})[0] == 400
        assert _call(server, "/api/plans/generate", {"slots": ["brunch"]})[0] == 400
        assert _call(server, "/api/plans/pln-nope")[0] == 404

    def test_household_allergy_respected_by_web_generate(self, server) -> None:
        _with_model(server)
        _call(server, "/api/intake", {
            "profile": {"year_of_birth": 1990, "sex_assigned_at_birth": "male",
                        "life_stage": "adult", "allergens": ["peanuts"]},
            "screeners": {},
        })
        _, made = _call(server, "/api/plans/generate", {"days": 3})
        _, detail = _call(server, f"/api/plans/{made['plan_id']}")
        assert "Peanut Noodles" not in [e["title"] for e in detail["entries"]]


class TestReorientTonight:
    def _plan(self, server):
        _with_model(server)
        _, made = _call(server, "/api/plans/generate", {"days": 1})
        _, tonight = _call(server, "/api/tonight")
        return made["plan_id"], tonight["tonight"]

    def test_alternatives_exclude_current_and_honor_avoid(self, server) -> None:
        plan_id, tonight = self._plan(server)
        _, alts = _call(
            server,
            f"/api/tonight/alternatives?exclude={tonight['recipe_id']}&avoid=lamb",
        )
        titles = [r["title"] for r in alts["results"]]
        assert tonight["title"] not in titles
        assert "Lamb Curry" not in titles
        assert all("TheMealDB" in r["attribution"] for r in alts["results"])

    def test_swap_replaces_tonight_and_audits(self, server) -> None:
        plan_id, tonight = self._plan(server)
        _, alts = _call(server, f"/api/tonight/alternatives?exclude={tonight['recipe_id']}")
        pick = alts["results"][0]
        status, res = _call(server, "/api/plans/swap", {
            "plan_id": plan_id, "day": 1, "slot": "dinner", "recipe_id": pick["recipe_id"],
        })
        assert status == 200 and res["swapped"]
        _, after = _call(server, "/api/tonight")
        assert after["tonight"]["recipe_id"] == pick["recipe_id"]
        import sqlite3

        conn = sqlite3.connect(server.app.data_dir / "operational.db")
        try:
            (n,) = conn.execute(
                "SELECT COUNT(*) FROM op_event_log"
                " WHERE event_subkind = 'plan_slot_swapped'"
            ).fetchone()
        finally:
            conn.close()
        assert n == 1

    def test_swap_rejects_unknown_recipe(self, server) -> None:
        plan_id, _ = self._plan(server)
        status, _ = _call(server, "/api/plans/swap", {
            "plan_id": plan_id, "day": 1, "recipe_id": "rcp-nope"})
        assert status == 404


class TestConsentAndDerived:
    def test_member_toggle_is_own_and_scoped(self, server) -> None:
        _, data = _call(server, "/api/members", {"name": "Sam"})
        sam = data["added"]
        status, res = _call(server, "/api/consent", {
            "category": "meal_feedback_semantic", "purpose": "local_operation",
            "granted": False,
        }, member=sam)
        assert status == 200
        row = next(d for d in res["decisions"]
                   if d["category"] == "meal_feedback_semantic"
                   and d["purpose"] == "local_operation")
        assert row["granted"] is False and row["scope"] == "own"
        assert row["label"] == "How meals made you feel"
        _, mine = _call(server, "/api/consent")
        row = next(d for d in mine["decisions"]
                   if d["category"] == "meal_feedback_semantic"
                   and d["purpose"] == "local_operation")
        assert row["granted"] is True and row["scope"] == "household"

    def test_bad_category_400(self, server) -> None:
        status, _ = _call(server, "/api/consent", {"category": "nope", "granted": True})
        assert status == 400

    def test_derived_lists_household_constraints(self, server) -> None:
        _call(server, "/api/intake", {
            "profile": {"year_of_birth": 1990, "sex_assigned_at_birth": "male",
                        "life_stage": "adult", "allergens": ["peanuts"],
                        "dietary_preferences": ["spicy"]},
            "screeners": {},
        })
        _, data = _call(server, "/api/derived")
        assert data["constraints"] == ["avoids peanuts", "prefers spicy"]


def test_page_has_app_shell(server) -> None:
    with urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/") as resp:
        body = resp.read().decode()
    for view in ("home", "recipes", "plans", "grocery", "profile"):
        assert f'id="view-{view}"' in body
        assert f'data-view="{view}"' in body
    assert 'id="qaReorient"' in body          # C5 Q5.5 quick action
    assert "async function jcall" in body     # error surfaces
    assert "Can't reach NutriMe" in body
    # home precedes the other views so the first paint is the daily surface
    assert body.index('id="view-home"') < body.index('id="view-recipes"')
