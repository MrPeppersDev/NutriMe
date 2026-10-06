"""End-to-end browser tests (#33): every main flow, phone-sized, real page.

Runs when Playwright is installed (`uv sync --group e2e`, then once
`uv run --group e2e playwright install chromium`); skipped otherwise, so
the default `uv run pytest` stays fast and dependency-free.

The local model is replaced by a fake client so plan-making works
without Ollama; everything else is the real server and page.
"""

import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

from nutrime.llm.base import ProviderResult  # noqa: E402
from nutrime.llm.client import LlmClient  # noqa: E402
from nutrime.recipes.store import RecipeVault  # noqa: E402
from nutrime.recipes.themealdb import convert_meal  # noqa: E402

pytestmark = pytest.mark.e2e


def _meal(meal_id, name, ingredients, category="Chicken", area="British"):
    meal = {"idMeal": meal_id, "strMeal": name, "strCategory": category, "strArea": area,
            "strTags": "", "strInstructions": "Prepare everything.\r\nCook until done.",
            "strSource": f"https://example.com/{meal_id}"}
    for i in range(1, 21):
        meal[f"strIngredient{i}"] = ""
        meal[f"strMeasure{i}"] = ""
    for i, (ing, measure) in enumerate(ingredients, start=1):
        meal[f"strIngredient{i}"] = ing
        meal[f"strMeasure{i}"] = measure
    return meal


class PickFirst:
    name = "fake"
    model = "fake-model"
    capabilities = frozenset({"reasoning", "local-private"})

    def complete(self, request):
        ids = [line.split("id=")[1].split(" |")[0]
               for line in request.messages[0].content.splitlines() if "id=" in line]
        return ProviderResult(
            text=json.dumps({"recipe_id": ids[0], "reason": "quick and uses what you have"}),
            model="fake-model", stop_reason="end_turn", prompt_tokens=1,
            completion_tokens=1, request_payload="{}", response_payload="{}",
        )


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"no Playwright browser available: {exc}")
        yield p, b
        b.close()


@pytest.fixture
def site(tmp_path: Path):
    from nutrime.app import initialize
    from nutrime.webui import serve

    app = initialize(data_dir=tmp_path)
    vault = RecipeVault(app.corpus_dir)
    for meal in (
        _meal("1", "Chicken Spinach Bake", [("chicken breast", "2"), ("spinach", "200 g"), ("olive oil", "2 tbsp")]),
        _meal("2", "Beef Stew", [("beef", "500 g"), ("potato", "3"), ("olive oil", "1 tbsp")], "Beef"),
        _meal("3", "Peanut Noodles", [("noodles", "200 g"), ("peanut butter", "3 tbsp")], "Pasta", "Thai"),
        _meal("4", "Lamb Curry", [("lamb", "500 g"), ("onion", "1")], "Lamb", "Indian"),
        _meal("5", "Tomato Soup", [("tomatoes", "6"), ("onion", "1"), ("garlic", "2 cloves")], "Vegetarian"),
    ):
        c = convert_meal(meal, ingested_at="2026-10-06T00:00:00Z")
        vault.write(c.recipe_id, c.frontmatter, c.cooklang_body)
    app.substrate.close(); app.operational.close()
    srv = serve(data_dir=tmp_path, port=0)
    srv.llm_client_factory = lambda a: LlmClient((PickFirst(),), a.rule_engine, a.audit)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv, tmp_path, f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown(); t.join(timeout=5); srv.server_close()


@pytest.fixture
def page(browser, site):
    p, b = browser
    ctx = b.new_context(**p.devices["iPhone 13"])
    pg = ctx.new_page()
    errors: list[str] = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.errors = errors
    pg.set_default_timeout(8000)
    yield pg
    assert errors == [], f"page errors: {errors}"
    ctx.close()


def _intake(pg, allergen="peanuts"):
    pg.click("#welcomeStart")
    pg.fill("#inYob", "1990")
    pg.select_option("#inSex", "female")
    pg.select_option("#inStage", "adult")
    pg.click("#intakeNext")
    if allergen:
        pg.click(f'#allergenPills [data-allergen="{allergen}"]')
    pg.click("#intakeNext")        # → screeners
    pg.click("#intakeNext")        # → privacy
    pg.click("#intakeNext")        # save
    pg.wait_for_selector("#welcomeCard", state="hidden")


def test_layout_is_phone_ready(page, site) -> None:
    _, _, url = site
    page.goto(url + "/#home")
    page.wait_for_selector("#homeGreet")
    assert page.is_visible(".tabs")
    box = page.locator(".tabs").bounding_box()
    vh = page.viewport_size["height"]
    assert box["y"] + box["height"] >= vh - 2         # tab bar sits at the bottom
    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    assert overflow <= 1                               # no sideways scrolling
    for view in ("recipes", "plans", "grocery", "profile", "activity"):
        page.goto(f"{url}/#{view}")
        page.wait_for_selector(f"#view-{view}:not([hidden])")
        assert page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 1


def test_intake_derives_avoid_list(page, site) -> None:
    _, _, url = site
    page.goto(url + "/#home")
    _intake(page, "peanuts")
    page.click('.tabs [data-view="profile"]')
    page.wait_for_selector("#derivedBody .tag")
    assert "avoids peanuts" in page.text_content("#derivedBody")


def test_members_add_switch_without_popups(page, site) -> None:
    _, _, url = site
    page.goto(url + "/#home")
    page.wait_for_selector("#memberPicker option", state="attached")
    page.select_option("#memberPicker", "__add")
    page.fill("#fs_name", "Sam")
    page.click("#fsOk")
    page.wait_for_function("document.querySelector('#memberPicker').selectedOptions[0].text === 'Sam'")
    page.wait_for_selector("#welcomeCard:not([style*='none'])")
    assert "Sam" in page.text_content("#welcomeWho")


def test_search_detail_why_and_credit(page, site) -> None:
    _, _, url = site
    page.goto(url + "/#recipes")
    page.fill("#have", "beef")
    page.click("#go")
    page.wait_for_selector("#resultsBox .card")
    page.locator("#resultsBox .card", has_text="Beef Stew").click()
    page.wait_for_selector("#sheet .why")
    sheet = page.text_content("#sheet")
    assert "Uses what you have" in sheet and "beef" in sheet
    assert "TheMealDB" in sheet          # credit line (#23)


def test_plan_reorient_cook_feedback_grocery(page, site) -> None:
    srv, data_dir, url = site
    page.goto(url + "/#home")
    _intake(page, "peanuts")
    # make a plan
    page.click('.tabs [data-view="plans"]')
    page.select_option("#planDays", "3")
    page.click("#planGo")
    page.wait_for_selector("#planDetail .dayRow")
    plan_text = page.text_content("#planDetail")
    assert "Peanut Noodles" not in plan_text   # household allergy respected
    assert "Today" in plan_text and "TheMealDB" in plan_text
    # reorient tonight
    page.click('.tabs [data-view="home"]')
    page.wait_for_selector("#tonightBody .serif")
    before = page.text_content("#tonightBody .serif")
    page.click("#qaReorient")
    page.wait_for_selector("#roResults .planItem")
    page.locator("#roResults button", has_text="Cook this instead").first.click()
    page.wait_for_function(f"document.querySelector('#tonightBody .serif').textContent !== {json.dumps(before)}")
    # we cooked it — in-page form, no prompt()
    page.locator("#tonightBody button", has_text="We cooked it").click()
    page.click('[data-scale="ease"] button[data-v="4"]')
    page.click('[data-scale="enjoyment"] button[data-v="5"]')
    page.fill("#fs_minutes", "35")
    page.click("#fsOk")
    if page.is_visible("text=Used up anything?"):
        page.click("#fsCancel")
    page.wait_for_selector("#feelText")
    page.fill("#feelText", "felt great all evening")
    page.locator("#tonightBody button", has_text="Save").click()
    page.wait_for_selector("#feelText", state="detached")
    # grocery list, ticks survive a reload
    page.click('.tabs [data-view="grocery"]')
    page.wait_for_selector("#groceryBody .groc li")
    first = page.locator("#groceryBody input[data-food]").first
    food = first.get_attribute("data-food")
    first.check()
    page.reload()
    page.wait_for_selector("#groceryBody .groc li")
    assert page.locator(f'#groceryBody input[data-food="{food}"]').is_checked()


def test_checkin_end_to_end(page, site) -> None:
    import sqlite3

    _, data_dir, url = site
    page.goto(url + "/#home")
    _intake(page, "dairy")
    old = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    conn = sqlite3.connect(data_dir / "substrate.db")
    conn.execute("UPDATE intake_profile_v2 SET created_at = ?", (old,))
    conn.commit(); conn.close()
    page.reload()
    page.wait_for_selector("#checkinCard:not([hidden])")
    page.click("#checkinStart")
    page.fill("#inWeight", "64")
    page.click("#intakeNext")
    page.click('#allergenPills [data-allergen="dairy"]')   # outgrown
    page.click("#intakeNext")
    page.click("#intakeNext")
    page.check('input[name="ciConf"][value="4"]')
    page.select_option("#ciMins", "30")
    page.locator("#ciCuisines .pill", has_text="indian").click()
    page.click("#intakeNext")
    page.wait_for_selector("text=Check-in saved")
    summary = page.text_content("#intakeSheet")
    assert "removed allergy: dairy" in summary and "wants to try: indian" in summary
    page.locator("#intakeSheet button", has_text="Done").click()
    page.click('.tabs [data-view="profile"]')
    page.wait_for_selector("#derivedBody")
    page.wait_for_function("!document.querySelector('#derivedBody').textContent.includes('avoids dairy')")
    assert "prefers indian" in page.text_content("#derivedBody")


def test_privacy_notifications_activity(page, site) -> None:
    _, _, url = site
    page.goto(url + "/#home")
    _intake(page, None)
    page.click('.tabs [data-view="profile"]')
    page.wait_for_selector('#consentBody input[data-cat="meal_feedback_semantic"]')
    page.uncheck('#consentBody input[data-cat="meal_feedback_semantic"][data-purpose="local_operation"]')
    page.wait_for_function(
        "document.querySelector('#consentBody').textContent.includes('own')")
    # turn on a practical notification and see it on the bell
    page.wait_for_selector('#notifySettings input[data-notify="plan_gap"]')
    page.check('#notifySettings input[data-notify="plan_gap"]')
    page.wait_for_function("document.querySelector('#bellCount').hidden === false")
    page.click("#bellBtn")
    page.wait_for_selector("text=Nothing is planned for tomorrow.")
    page.locator("[data-dismiss]").first.click()
    page.click("#sheet .closeX")
    # activity view lists the privacy change
    page.click("#openActivity")
    page.wait_for_selector("#activityList .act")
    assert "how meals made you feel" in page.text_content("#activityList").lower()


def test_lost_server_shows_plain_error(page, site) -> None:
    _, _, url = site
    page.goto(url + "/#plans")
    page.wait_for_selector("#planList")
    page.route("**/api/plans/generate", lambda route: route.abort())
    page.click("#planGo")
    page.wait_for_selector("#toast", state="visible")
    assert "Can't reach NutriMe" in page.text_content("#toast")
