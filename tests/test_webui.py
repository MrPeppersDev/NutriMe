"""Localhost web UI — JSON API over the application core.

The server runs single-threaded in a background thread; the Application
initializes lazily on first request so every sqlite touch stays on the
serving thread (sqlite3 default check_same_thread discipline).
"""

import json
import threading
import urllib.request
from pathlib import Path

import pytest

from nutrime.recipes.store import RecipeVault
from nutrime.recipes.themealdb import convert_meal
from nutrime.recipes.web import Pacer
from nutrime.webui import render_ingredient_line, serve


def _sample_meal(meal_id: str, name: str, ingredients: list[tuple[str, str]]) -> dict:
    meal = {
        "idMeal": meal_id,
        "strMeal": name,
        "strCategory": "Chicken",
        "strArea": "Japanese",
        "strTags": "",
        "strInstructions": "Cook it. Serve.",
        "strSource": f"https://example.com/{meal_id}",
    }
    for i in range(1, 21):
        meal[f"strIngredient{i}"] = ""
        meal[f"strMeasure{i}"] = ""
    for i, (ing, measure) in enumerate(ingredients, start=1):
        meal[f"strIngredient{i}"] = ing
        meal[f"strMeasure{i}"] = measure
    return meal


@pytest.fixture
def server(tmp_path: Path):
    from nutrime.app import initialize

    # Seed a small corpus directly via the vault before the server starts.
    app = initialize(data_dir=tmp_path)
    vault = RecipeVault(app.corpus_dir)
    vault.ensure()
    for meal in (
        _sample_meal(
            "1", "Chicken Spinach Bake",
            [("chicken breast", "2"), ("spinach", "200 g"), ("lemon", "1")],
        ),
        _sample_meal(
            "2", "Beef Stew",
            [("beef", "500 g"), ("potato", "3"), ("carrot", "2")],
        ),
    ):
        converted = convert_meal(meal, ingested_at="2026-10-03T00:00:00Z")
        vault.write(
            converted.recipe_id, converted.frontmatter, converted.cooklang_body
        )
    app.substrate.close()
    app.operational.close()

    srv = serve(data_dir=tmp_path, port=0)  # port 0 → OS-assigned
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv
    srv.shutdown()
    thread.join(timeout=5)
    srv.server_close()


def _get(srv, path: str) -> dict:
    port = srv.server_address[1]
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post(srv, path: str, payload: dict) -> dict:
    port = srv.server_address[1]
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return json.loads(err.read().decode("utf-8"))


class TestRenderIngredientLine:
    def test_braced_with_qty_unit(self) -> None:
        assert (
            render_ingredient_line("@salmon fillet{1 1/2%lb}")
            == "1 1/2 lb salmon fillet"
        )

    def test_bare(self) -> None:
        assert render_ingredient_line("@salt") == "salt"

    def test_non_ingredient(self) -> None:
        assert render_ingredient_line("Cook it.") is None


class TestPage:
    def test_root_serves_html(self, server) -> None:
        port = server.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
            body = resp.read().decode("utf-8")
        assert "What can we make" in body


class TestSearchApi:
    def test_on_hand_ranking(self, server) -> None:
        data = _get(server, "/api/search?have=spinach,chicken")
        assert data["corpus_count"] == 2
        titles = [r["title"] for r in data["results"]]
        assert titles[0] == "Chicken Spinach Bake"
        top = data["results"][0]
        assert set(top["on_hand_matches"]) == {"spinach", "chicken"}
        assert "Source:" in top["attribution"]

    def test_phase_boost_and_note(self, server) -> None:
        data = _get(server, "/api/search?phase=menstrual")
        assert data["phase"]["label"] == "Menstrual"
        assert "well-supported" in data["phase"]["evidence_note"]
        by_title = {r["title"]: r for r in data["results"]}
        # spinach + beef are menstrual boost terms
        assert by_title["Chicken Spinach Bake"]["prefer_matches"]
        assert by_title["Beef Stew"]["prefer_matches"]

    def test_unknown_phase_harmless(self, server) -> None:
        data = _get(server, "/api/search?phase=nonsense")
        assert data["phase"] is None
        assert len(data["results"]) == 2


class TestInventoryApi:
    def test_add_list_remove_roundtrip(self, server) -> None:
        added = _post(server, "/api/inventory", {"name": "spinach", "location": "fridge"})
        assert added["id"]
        items = _get(server, "/api/inventory")["items"]
        assert any(i["name"] == "spinach" for i in items)

        # inventory folds into search when use_inventory=1
        data = _get(server, "/api/search?use_inventory=1")
        top = data["results"][0]
        assert top["title"] == "Chicken Spinach Bake"
        assert "spinach" in top["on_hand_matches"]

        removed = _post(server, "/api/inventory/remove", {"id": added["id"]})
        assert removed["removed"] is True

    def test_add_requires_name(self, server) -> None:
        err = _post(server, "/api/inventory", {"name": "  "})
        assert "error" in err


class TestRecipeDetailApi:
    def test_detail_fields(self, server) -> None:
        data = _get(server, "/api/search?have=beef")
        recipe_id = data["results"][0]["recipe_id"]
        detail = _get(server, f"/api/recipes/{recipe_id}")
        assert detail["title"] == "Beef Stew"
        assert "500 g beef" in detail["ingredients"]
        assert any("Cook it." in s for s in detail["steps"])
        assert "Source:" in detail["attribution"]

    def test_missing_recipe_404(self, server) -> None:
        port = server.server_address[1]
        try:
            urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/recipes/rcp-nope"
            )
        except urllib.error.HTTPError as err:
            assert err.code == 404
        else:
            pytest.fail("expected 404")


class TestImportApi:
    def test_import_via_stubbed_fetcher(self, server) -> None:
        node = {
            "@type": "Recipe",
            "name": "Pinned Salmon",
            "recipeIngredient": ["1 lb salmon"],
            "recipeInstructions": "Bake it.",
            "recipeYield": "2",
        }
        page = (
            '<script type="application/ld+json">'
            + json.dumps(node)
            + "</script>"
        )
        server.ingest_fetcher = lambda url: page
        server.ingest_pacer = Pacer(delay_s=0, sleep=lambda _: None)
        data = _post(
            server, "/api/import", {"urls": "https://pin.example.com/salmon"}
        )
        assert data["written"] == 1
        assert data["corpus_count"] == 3

        found = _get(server, "/api/search?q=Pinned")
        assert found["results"][0]["title"] == "Pinned Salmon"

    def test_import_rejects_non_http(self, server) -> None:
        err = _post(server, "/api/import", {"urls": "file:///etc/passwd"})
        assert "error" in err

    def test_import_requires_urls(self, server) -> None:
        err = _post(server, "/api/import", {"urls": ""})
        assert "error" in err


class TestPhasesApi:
    def test_phases_listed_with_disclosure(self, server) -> None:
        data = _get(server, "/api/phases")
        keys = [p["key"] for p in data["phases"]]
        assert keys == ["menstrual", "follicular", "ovulatory", "luteal"]
        assert all(p["evidence_note"] for p in data["phases"])
        assert "prototype" in data["disclosure"]


class TestPinterestApi:
    def test_status_disconnected(self, server, monkeypatch) -> None:
        monkeypatch.delenv("PINTEREST_ACCESS_TOKEN", raising=False)
        monkeypatch.setattr(
            "nutrime.recipes.pinterest.keychain_token", lambda: None
        )
        data = _get(server, "/api/pinterest/status")
        assert data["connected"] is False
        assert "nutrime pinterest connect" in data["how_to_connect"]

    def test_sync_without_token_errors(self, server, monkeypatch) -> None:
        monkeypatch.delenv("PINTEREST_ACCESS_TOKEN", raising=False)
        monkeypatch.setattr(
            "nutrime.recipes.pinterest.keychain_token", lambda: None
        )
        err = _post(server, "/api/pinterest/sync", {})
        assert "error" in err

    def test_sync_end_to_end(self, server, monkeypatch) -> None:
        monkeypatch.setenv("PINTEREST_ACCESS_TOKEN", "tkn")

        def fake_api(url: str, token: str) -> dict:
            assert token == "tkn"
            return {
                "items": [
                    {"id": "1", "link": "https://pin.example.com/soup",
                     "title": "", "board_id": "b1"},
                    {"id": "2", "link": "", "title": "", "board_id": "b1"},
                ],
                "bookmark": None,
            }

        node = {
            "@type": "Recipe",
            "name": "Synced Soup",
            "recipeIngredient": ["1 onion"],
            "recipeInstructions": "Simmer.",
            "recipeYield": "2",
        }
        page = (
            '<script type="application/ld+json">'
            + json.dumps(node)
            + "</script>"
        )
        server.pinterest_api_fetcher = fake_api
        server.ingest_fetcher = lambda url: page
        server.ingest_pacer = Pacer(delay_s=0, sleep=lambda _: None)

        data = _post(server, "/api/pinterest/sync", {})
        assert data["pins_seen"] == 2
        assert data["written"] == 1
        assert data["pins_without_links"] == 1

        found = _get(server, "/api/search?q=Synced")
        assert found["results"][0]["title"] == "Synced Soup"


class TestTonightAndFeedbackApi:
    def test_tonight_empty_state(self, server) -> None:
        data = _get(server, "/api/tonight")
        assert data["tonight"] is None
        assert data["awaiting_feel"] is None
        assert data["history"] == []

    def test_cook_then_feel_roundtrip(self, server) -> None:
        found = _get(server, "/api/search?have=beef")
        recipe_id = found["results"][0]["recipe_id"]

        cooked = _post(
            server, "/api/meals/cooked",
            {"recipe_id": recipe_id, "ease": 4, "enjoyment": 5,
             "actual_minutes": 35},
        )
        assert cooked["meal_event_id"].startswith("mev-")

        tonight = _get(server, "/api/tonight")
        assert tonight["awaiting_feel"] is not None
        assert tonight["history"][0]["ease_rating"] == 4

        felt = _post(
            server, "/api/meals/feel",
            {"meal_event_id": cooked["meal_event_id"],
             "response": "felt great"},
        )
        assert "recorded" in felt

        after = _get(server, "/api/tonight")
        assert after["awaiting_feel"] is None
        assert after["history"][0]["body_response"] == "felt great"

    def test_cook_unknown_recipe_404(self, server) -> None:
        err = _post(server, "/api/meals/cooked", {"recipe_id": "rcp-nope"})
        assert "error" in err


class TestSourcesApi:
    def test_sources_counts(self, server) -> None:
        data = _get(server, "/api/sources")
        by_key = {s["key"]: s for s in data["sources"]}
        assert by_key["themealdb"]["count"] == 2

    def test_search_source_filter(self, server) -> None:
        data = _get(server, "/api/search?sources=pins")
        assert data["results"] == []
        data = _get(server, "/api/search?sources=themealdb")
        assert len(data["results"]) == 2


class TestGroceryApi:
    def test_no_plans_404(self, server) -> None:
        import urllib.error
        import urllib.request as urlreq

        port = server.server_address[1]
        try:
            urlreq.urlopen(f"http://127.0.0.1:{port}/api/grocery")
        except urllib.error.HTTPError as err:
            assert err.code == 404
        else:
            pytest.fail("expected 404")


class TestVisionGapWebFlows:
    def test_cooked_returns_used_candidates_and_decrement(self, server) -> None:
        # Put matching + non-matching items in inventory
        _post(server, "/api/inventory", {"name": "beef", "location": "freezer"})
        _post(server, "/api/inventory", {"name": "chocolate", "location": "pantry"})

        found = _get(server, "/api/search?q=Beef%20Stew")
        recipe_id = found["results"][0]["recipe_id"]
        cooked = _post(server, "/api/meals/cooked", {"recipe_id": recipe_id})
        assert "beef" in cooked["used_candidates"]
        assert "chocolate" not in cooked["used_candidates"]

        removed = _post(
            server, "/api/meals/cooked/used-up",
            {"meal_event_id": cooked["meal_event_id"], "names": ["beef"]},
        )
        assert removed["removed"] == ["beef"]
        items = _get(server, "/api/inventory")["items"]
        assert all(i["name"] != "beef" for i in items)

    def test_tonight_use_soon_strip(self, server) -> None:
        from datetime import date, timedelta

        soon = (date.today() + timedelta(days=2)).isoformat()
        port = server.server_address[1]
        # add_item via API doesn't take best_by; write directly
        import sqlite3

        from nutrime.app import initialize as _init

        # go through the server's own app to share the connection thread-
        # safely: use the HTTP inventory add then update the row via a
        # second connection (safe: server is idle between requests).
        added = _post(server, "/api/inventory", {"name": "herbs", "location": "fridge"})
        import nutrime.paths  # noqa — data dir fixed by fixture

        conn = sqlite3.connect(server.app.data_dir / "substrate.db")
        conn.execute(
            "UPDATE inventory_item SET best_by_date = ? WHERE id = ?",
            (soon, added["id"]),
        )
        conn.commit()
        conn.close()

        data = _get(server, "/api/tonight")
        names = [u["name"] for u in data["use_soon"]]
        assert "herbs" in names
        entry = next(u for u in data["use_soon"] if u["name"] == "herbs")
        assert entry["days_left"] == 2

    def test_search_personal_time_and_history_chip_fields(self, server) -> None:
        found = _get(server, "/api/search?q=Beef%20Stew")
        recipe_id = found["results"][0]["recipe_id"]
        _post(server, "/api/meals/cooked",
              {"recipe_id": recipe_id, "ease": 5, "enjoyment": 5})
        data = _get(server, "/api/search?q=Beef%20Stew")
        top = data["results"][0]
        assert top["times_cooked"] == 1
        assert top["avg_enjoyment"] == 5.0
