"""Localhost web UI — the household prototype surface ("give it a whirl").

Per A2 (native macOS app primary; **localhost web acceptable for build
speed**) this is a stdlib-only single-process HTTP server over the same
application core the CLI uses. No new runtime dependencies, no framework:
``http.server`` + a hand-rolled JSON API + one embedded HTML page.

Product pull 2026-10-03 (issues #24/#25): the page answers the two
household questions directly —

- "I have xyz in my fridge, what saved recipes can I mostly make?"
  → 5.3 search with on-hand ranking (typed ingredients + stored inventory).
- "I'm in my follicular phase, what fits that phase + these ingredients?"
  → prototype phase boosts from :mod:`nutrime.cycles` (boosts only, never
  filters; evidence notes rendered honestly beside results).
- "Bring in my Pinterest pins" → paste recipe-page URLs, ingested via the
  4.4 schema.org JSON-LD adapter into the household vault.

Privacy shape: everything here is local. Recipe search is PHI-free per the
4.1 envelope; the phase selection is a request parameter mapped to local
ranking boosts and is never persisted nor sent anywhere.

Threading: the server is deliberately single-threaded (``HTTPServer``, not
``ThreadingHTTPServer``) — one household, one process, and it keeps every
sqlite access on the serving thread. The Application is initialized lazily
on first request so construction and serving can happen on different
threads (tests start the server in a background thread).

Attribution-at-render (#23): every surface that shows a recipe — result
cards and the detail view — carries the source/license line adjacent to
the content, same discipline as the CLI surfaces.
"""

from __future__ import annotations

import json
import re
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from nutrime.cycles import (
    PHASES,
    PHASES_BY_KEY,
    STUB_DISCLOSURE,
    phase_prefer_terms,
)
from nutrime.inventory.store import InventoryItem, add_item, list_items, remove_item
from nutrime.recipes.jsonld import seed_recipes as jsonld_seed_recipes
from nutrime.recipes.search import (
    SOURCE_LABELS,
    SearchFilters,
    attribution_line,
    filters_from_constraints,
    search_page,
    source_collection,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer

_INGREDIENT_DISPLAY = re.compile(
    r"^@(?:(?P<braced>[^@{}]+)\{(?P<qty>[^%}]*)%?(?P<unit>[^}]*)\}|(?P<bare>\S+))$"
)


def render_ingredient_line(line: str) -> str | None:
    """``@salmon fillet{1 1/2%lb}`` → ``"1 1/2 lb salmon fillet"``."""
    match = _INGREDIENT_DISPLAY.match(line.strip())
    if not match:
        return None
    if match.group("bare"):
        return match.group("bare")
    name = match.group("braced").strip()
    qty = (match.group("qty") or "").strip()
    unit = (match.group("unit") or "").strip()
    parts = [p for p in (qty, unit, name) if p]
    return " ".join(parts)


def recipe_detail(record) -> dict[str, Any]:
    """Split a Cooklang body into display-ready ingredients + steps."""
    ingredients: list[str] = []
    steps: list[str] = []
    for raw in record.body.splitlines():
        line = raw.strip()
        if not line or line.startswith(">>") or line.startswith("--"):
            continue
        rendered = render_ingredient_line(line)
        if rendered is not None:
            ingredients.append(rendered)
        else:
            steps.append(line)
    fm = record.frontmatter
    return {
        "recipe_id": record.recipe_id,
        "title": fm.get("title", "(untitled)"),
        "ingredients": ingredients,
        "steps": steps,
        "total_time_min": fm.get("estimated_total_time_min"),
        "yields": (fm.get("yields") or {}).get("count"),
        "allergens": list(fm.get("top_allergens_present", ()) or ()),
        "cuisine": list(fm.get("cuisine_tradition_tags", ()) or ()),
        "categories": list(fm.get("meal_categories", ()) or ()),
        "source_url": (fm.get("attribution") or {}).get("source_url", ""),
        "attribution": attribution_line(fm),
        "equipment": list(fm.get("equipment_required", ()) or ()),
    }


class NutriMeWebServer(HTTPServer):
    """Carries lazily-initialized app state for the handler."""

    def __init__(self, address: tuple[str, int], data_dir: Path | None = None):
        super().__init__(address, _Handler)
        self.data_dir = data_dir
        self._app = None
        self._app_lock = threading.Lock()
        # Injectable for tests: the ingest fetcher + pacer, and the
        # Pinterest JSON-API fetcher
        self.ingest_fetcher = None
        self.ingest_pacer: Pacer | None = None
        self.pinterest_api_fetcher = None
        # "Skip for now" on the first-run intake card: session-scoped only
        # (no persistence — the invitation simply returns next launch).
        # Per member (#29): member ids that skipped this session.
        self.intake_skipped: set[str] = set()

    @property
    def app(self):
        if self._app is None:
            with self._app_lock:
                if self._app is None:
                    from nutrime.app import initialize

                    self._app = initialize(data_dir=self.data_dir)
        return self._app

    @property
    def vault(self) -> RecipeVault:
        return RecipeVault(self.app.corpus_dir)


class _Handler(BaseHTTPRequestHandler):
    server: NutriMeWebServer

    # -- plumbing ------------------------------------------------------------

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass  # keep the terminal quiet; errors surface via responses

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: Any, status: int = 200) -> None:
        self._send(
            status,
            json.dumps(payload).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    # -- routing ---------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        try:
            if route == "/":
                self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            elif route == "/api/search":
                self._api_search(query)
            elif route == "/api/inventory":
                self._api_inventory_list()
            elif route == "/api/phases":
                self._api_phases()
            elif route == "/api/pinterest/status":
                self._api_pinterest_status()
            elif route == "/api/sources":
                self._api_sources()
            elif route == "/api/tonight":
                self._api_tonight()
            elif route == "/api/intake/status":
                self._api_intake_status()
            elif route == "/api/intake/questions":
                self._api_intake_questions()
            elif route == "/api/grocery":
                self._api_grocery(query)
            elif route == "/api/members":
                self._api_members_list()
            elif route.startswith("/api/recipes/"):
                self._api_recipe_detail(route.removeprefix("/api/recipes/"))
            else:
                self._json({"error": "not found"}, status=404)
        except Exception as exc:  # noqa: BLE001 — surface, don't crash the server
            self._json({"error": str(exc)}, status=500)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/inventory":
                self._api_inventory_add()
            elif parsed.path == "/api/inventory/remove":
                self._api_inventory_remove()
            elif parsed.path == "/api/import":
                self._api_import()
            elif parsed.path == "/api/pinterest/sync":
                self._api_pinterest_sync()
            elif parsed.path == "/api/meals/cooked":
                self._api_meals_cooked()
            elif parsed.path == "/api/meals/feel":
                self._api_meals_feel()
            elif parsed.path == "/api/meals/cooked/used-up":
                self._api_meals_used_up()
            elif parsed.path == "/api/intake":
                self._api_intake_save()
            elif parsed.path == "/api/intake/skip":
                self._api_intake_skip()
            elif parsed.path == "/api/members":
                self._api_members_add()
            elif parsed.path == "/api/members/rename":
                self._api_members_rename()
            elif parsed.path == "/api/members/archive":
                self._api_members_archive()
            else:
                self._json({"error": "not found"}, status=404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, status=500)

    # -- members (#29) -----------------------------------------------------------
    # One shared device, no auth: the page sends the picked member in the
    # X-NutriMe-Member header. Absent → the household's default member, so
    # member-unaware clients keep working. Unknown/archived → 400.

    def _member_id(self) -> str:
        from nutrime.members import get_member

        app = self.server.app
        raw = (self.headers.get("X-NutriMe-Member") or "").strip()
        if not raw:
            return app.default_member_id
        return get_member(app.substrate, app.tenant_id, raw).id

    def _member_or_400(self) -> str | None:
        from nutrime.members import MemberError

        try:
            return self._member_id()
        except MemberError as err:
            self._json({"error": str(err)}, status=400)
            return None

    def _members_payload(self) -> dict[str, Any]:
        from nutrime.intake.store import household_profiles
        from nutrime.members import list_members

        app = self.server.app
        profiled = household_profiles(app.substrate, app.tenant_id)
        return {
            "default_member_id": app.default_member_id,
            "members": [
                {
                    "id": m.id,
                    "name": m.display_name,
                    "has_profile": m.id in profiled,
                }
                for m in list_members(app.substrate, app.tenant_id)
            ],
        }

    def _api_members_list(self) -> None:
        self._json(self._members_payload())

    def _api_members_add(self) -> None:
        from nutrime.members import MemberError, add_member

        payload = self._read_json_body()
        app = self.server.app
        try:
            member = add_member(
                app.substrate, app.tenant_id, str(payload.get("name") or "")
            )
        except MemberError as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json({"added": member.id, **self._members_payload()})

    def _api_members_rename(self) -> None:
        from nutrime.members import MemberError, rename_member

        payload = self._read_json_body()
        app = self.server.app
        try:
            rename_member(
                app.substrate,
                app.tenant_id,
                str(payload.get("id") or ""),
                str(payload.get("name") or ""),
            )
        except MemberError as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json(self._members_payload())

    def _api_members_archive(self) -> None:
        from nutrime.members import MemberError, archive_member

        payload = self._read_json_body()
        app = self.server.app
        try:
            archive_member(
                app.substrate, app.tenant_id, str(payload.get("id") or "")
            )
        except MemberError as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json(self._members_payload())

    # -- API: search -----------------------------------------------------------

    def _api_search(self, query: dict[str, list[str]]) -> None:
        def first(key: str) -> str:
            values = query.get(key) or [""]
            return values[0].strip()

        app = self.server.app

        on_hand: set[str] = set()
        have_text = first("have")
        if have_text:
            on_hand |= {
                term.strip().lower()
                for term in re.split(r"[,;]", have_text)
                if term.strip()
            }
        use_inventory = first("use_inventory") == "1"
        if use_inventory:
            on_hand |= {
                item.name.lower()
                for item in list_items(app.substrate, app.tenant_id)
            }

        prefer: set[str] = set()
        phase_key = first("phase")
        phase_note = None
        if phase_key:
            prefer |= set(phase_prefer_terms(phase_key))
            profile = PHASES_BY_KEY.get(phase_key)
            if profile is not None:
                phase_note = {
                    "label": profile.label,
                    "emphasis": profile.emphasis,
                    "evidence_note": profile.evidence_note,
                }

        max_time = None
        if first("max_time"):
            try:
                max_time = int(first("max_time"))
            except ValueError:
                max_time = None

        sources = frozenset(
            s.strip()
            for s in (query.get("sources") or [""])[0].split(",")
            if s.strip()
        )

        # V1: cook history always consults (boosts + personal time).
        from nutrime.feedback import cooked_cuisines, experience_summaries

        experience = experience_summaries(app.substrate, app.tenant_id)

        # V2: expiring inventory names tilt ranking when inventory is in play.
        expiring: frozenset[str] = frozenset()
        if use_inventory:
            from datetime import date

            from nutrime.inventory.store import expiring_names

            expiring = frozenset(
                item.name.lower()
                for item in expiring_names(
                    app.substrate, app.tenant_id, today=date.today().isoformat()
                )
            )

        # V3: novelty is opt-in on the search surface (broaden=1).
        novelty: frozenset[str] | None = None
        if first("broaden") == "1":
            novelty = frozenset(
                cooked_cuisines(app.substrate, app.tenant_id, self.server.vault)
            )

        filters = SearchFilters(
            query=first("q") or None,
            max_total_time_min=max_time,
            on_hand=frozenset(on_hand),
            prefer_terms=frozenset(prefer),
            sources=sources,
            expiring=expiring,
            experience=experience,
            cooked_cuisines=novelty,
        )
        if first("apply_constraints") == "1":
            from nutrime.knowledge.store import list_synthesized_entries

            entries = list_synthesized_entries(
                app.substrate, app.tenant_id, entry_type="abstracted_constraint"
            )
            filters = filters_from_constraints(entries, filters)

        try:
            offset = max(0, int(first("offset") or 0))
        except ValueError:
            offset = 0
        page = search_page(
            self.server.vault, filters, limit=24, offset=offset
        )
        results = page.results
        self._json(
            {
                "total": page.total,
                "offset": offset,
                "results": [
                    {
                        "recipe_id": r.recipe_id,
                        "title": r.title,
                        "score": r.score,
                        "total_time_min": r.total_time_min,
                        "allergens": list(r.allergens),
                        "on_hand_matches": list(r.on_hand_matches),
                        "prefer_matches": list(r.prefer_matches),
                        "attribution": r.attribution,
                        "source": r.source,
                        "source_label": SOURCE_LABELS.get(r.source, r.source),
                        "times_cooked": r.times_cooked,
                        "avg_enjoyment": r.avg_enjoyment,
                        "personal_time_min": r.personal_time_min,
                        "expiring_matches": list(r.expiring_matches),
                        "novel_cuisine": r.novel_cuisine,
                    }
                    for r in results
                ],
                "corpus_count": self.server.vault.count(),
                "phase": phase_note,
                "on_hand_count": len(on_hand),
            }
        )

    # -- API: recipes ------------------------------------------------------------

    def _api_recipe_detail(self, recipe_id: str) -> None:
        vault = self.server.vault
        if not recipe_id or not vault.exists(recipe_id):
            self._json({"error": "recipe not found"}, status=404)
            return
        self._json(recipe_detail(vault.read(recipe_id)))

    # -- API: phases ---------------------------------------------------------------

    def _api_phases(self) -> None:
        self._json(
            {
                "phases": [
                    {
                        "key": p.key,
                        "label": p.label,
                        "emphasis": p.emphasis,
                        "evidence_note": p.evidence_note,
                    }
                    for p in PHASES
                ],
                "disclosure": STUB_DISCLOSURE,
            }
        )

    # -- API: inventory ---------------------------------------------------------

    def _api_inventory_list(self) -> None:
        app = self.server.app
        items = list_items(app.substrate, app.tenant_id)
        self._json(
            {
                "items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "location": item.location,
                        "quantity": item.quantity,
                        "unit": item.unit,
                    }
                    for item in items
                ]
            }
        )

    def _api_inventory_add(self) -> None:
        payload = self._read_json_body()
        name = str(payload.get("name") or "").strip()
        location = str(payload.get("location") or "fridge").strip()
        if not name:
            self._json({"error": "name required"}, status=400)
            return
        app = self.server.app
        item = InventoryItem(name=name, location=location)
        item_id = add_item(app.substrate, app.tenant_id, item)
        self._json({"id": item_id, "name": name, "location": location})

    def _api_inventory_remove(self) -> None:
        payload = self._read_json_body()
        try:
            item_id = int(payload.get("id"))
        except (TypeError, ValueError):
            self._json({"error": "id required"}, status=400)
            return
        app = self.server.app
        removed = remove_item(app.substrate, app.tenant_id, item_id)
        self._json({"removed": removed})

    # -- API: import (4.4 adapter) ----------------------------------------------

    def _api_import(self) -> None:
        payload = self._read_json_body()
        raw_urls = payload.get("urls")
        urls: list[str] = []
        if isinstance(raw_urls, list):
            urls = [str(u).strip() for u in raw_urls if str(u).strip()]
        elif isinstance(raw_urls, str):
            urls = [
                line.strip()
                for line in raw_urls.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
        urls = [u for u in urls if u.startswith(("http://", "https://"))]
        if not urls:
            self._json({"error": "no valid http(s) URLs provided"}, status=400)
            return
        if len(urls) > 50:
            self._json(
                {"error": "50 URLs max per import — split it up"}, status=400
            )
            return
        outcome = jsonld_seed_recipes(
            self.server.vault,
            urls,
            fetcher=self.server.ingest_fetcher,
            pacer=self.server.ingest_pacer or Pacer(delay_s=1.0),
        )
        self._json(
            {
                "fetched": outcome.fetched,
                "written": outcome.written,
                "skipped": len(outcome.skipped_upstream_ids),
                "failures": [
                    {"url": url, "reason": reason}
                    for url, reason in outcome.failures
                ],
                "corpus_count": self.server.vault.count(),
            }
        )


    # -- API: tonight (step 8 daily-cadence slice) + feedback (step 7) --------

    def _api_tonight(self) -> None:
        """Daily-cadence slice (C5 Q5.1): tonight's planned meal if a plan
        covers today, latest cooked meal awaiting its body-response prompt,
        and recent history — the home-screen payload."""
        from nutrime.feedback import meal_history
        from nutrime.plans.store import PlanVault, parse_plan_body

        app = self.server.app
        plan_vault = PlanVault(app.corpus_dir)
        tonight = None
        plans = plan_vault.list_plans() if plan_vault.root.exists() else []
        if plans:
            latest = plans[-1]
            entries = [e for e in latest.entries() if e.filled]
            if entries:
                from datetime import date, datetime

                created = str(latest.frontmatter.get("created_at", ""))[:10]
                try:
                    day_index = (
                        date.today() - datetime.fromisoformat(created).date()
                    ).days + 1
                except ValueError:
                    day_index = 1
                todays = [e for e in entries if e.day == day_index]
                pick = todays[0] if todays else None
                if pick is not None:
                    detail = {}
                    if self.server.vault.exists(pick.recipe_id):
                        record = self.server.vault.read(pick.recipe_id)
                        detail = {
                            "total_time_min": record.frontmatter.get(
                                "estimated_total_time_min"
                            ),
                            "attribution": attribution_line(record.frontmatter),
                        }
                    tonight = {
                        "plan_id": latest.plan_id,
                        "day": pick.day,
                        "slot": pick.slot,
                        "recipe_id": pick.recipe_id,
                        "title": pick.title,
                        **detail,
                    }
        member_id = self._member_or_400()
        if member_id is None:
            return
        history = meal_history(
            app.substrate, app.tenant_id, limit=8, member_id=member_id
        )
        awaiting_feel = next(
            (e for e in history if e.body_response is None), None
        )
        # V2: use-soon strip (expiring window, soonest first, cap 6).
        from datetime import date

        from nutrime.inventory.store import expiring_names

        today = date.today().isoformat()
        use_soon = sorted(
            expiring_names(app.substrate, app.tenant_id, today=today),
            key=lambda item: item.best_by_date or "",
        )[:6]
        self._json(
            {
                "tonight": tonight,
                "use_soon": [
                    {
                        "name": item.name,
                        "best_by_date": item.best_by_date,
                        "days_left": (
                            date.fromisoformat(item.best_by_date)
                            - date.today()
                        ).days,
                    }
                    for item in use_soon
                ],
                "awaiting_feel": (
                    {
                        "meal_event_id": awaiting_feel.meal_event_id,
                        "recipe_title": awaiting_feel.recipe_title,
                        "cooked_at": awaiting_feel.cooked_at,
                    }
                    if awaiting_feel
                    else None
                ),
                "history": [
                    {
                        "meal_event_id": e.meal_event_id,
                        "recipe_id": e.recipe_id,
                        "recipe_title": e.recipe_title,
                        "cooked_at": e.cooked_at,
                        "ease_rating": e.ease_rating,
                        "enjoyment_rating": e.enjoyment_rating,
                        "body_response": e.body_response,
                        "actual_time_min": e.actual_time_min,
                    }
                    for e in history
                ],
            }
        )

    def _api_meals_cooked(self) -> None:
        from nutrime.consent import ConsentError
        from nutrime.feedback import (
            record_cooking_experience,
            record_meal_event,
            record_time_feedback,
        )

        payload = self._read_json_body()
        recipe_id = str(payload.get("recipe_id") or "").strip()
        if not recipe_id or not self.server.vault.exists(recipe_id):
            self._json({"error": "recipe not found"}, status=404)
            return
        record = self.server.vault.read(recipe_id)
        app = self.server.app
        member_id = self._member_or_400()
        if member_id is None:
            return
        try:
            meal_event_id = record_meal_event(
                app.substrate,
                app.tenant_id,
                member_id=member_id,
                recipe_id=recipe_id,
                recipe_title=str(record.frontmatter.get("title", "")),
                plan_id=str(payload.get("plan_id") or "") or None,
            )
            ease = payload.get("ease")
            enjoyment = payload.get("enjoyment")
            if ease is not None and enjoyment is not None:
                record_cooking_experience(
                    app.substrate,
                    app.tenant_id,
                    member_id=member_id,
                    meal_event_id=meal_event_id,
                    ease_rating=int(ease),
                    enjoyment_rating=int(enjoyment),
                    freetext_notes=str(payload.get("notes") or "") or None,
                )
            actual = payload.get("actual_minutes")
            if actual is not None:
                estimated = record.frontmatter.get("estimated_total_time_min")
                record_time_feedback(
                    app.substrate,
                    app.tenant_id,
                    member_id=member_id,
                    meal_event_id=meal_event_id,
                    estimated_time_min=(
                        int(estimated) if estimated is not None else None
                    ),
                    actual_time_min=int(actual),
                )
        except (ConsentError, ValueError) as err:
            self._json({"error": str(err)}, status=400)
            return

        # V2 decrement, ask-don't-assume: if the caller confirmed names,
        # consume them; always return the recipe∩inventory candidates so
        # the surface can ask.
        from nutrime.grocery.parse import normalize_food
        from nutrime.inventory.store import list_items, remove_items_by_name

        used_up = payload.get("used_up")
        removed: list[str] = []
        if isinstance(used_up, list) and used_up:
            removed = remove_items_by_name(
                app.substrate, app.tenant_id, [str(n) for n in used_up]
            )
            for name in removed:
                app.audit.record_event(
                    event_kind="system",
                    event_subkind="inventory_item_consumed",
                    actor="webui",
                    payload={
                        "name": name,
                        "meal_event_id": meal_event_id,
                        "recipe_id": recipe_id,
                    },
                )
        from nutrime.recipes.search import ingredient_names

        recipe_foods = {
            normalize_food(n) for n in ingredient_names(record.body)
        }
        candidates = sorted(
            item.name
            for item in list_items(app.substrate, app.tenant_id)
            if normalize_food(item.name) in recipe_foods
        )
        self._json(
            {
                "meal_event_id": meal_event_id,
                "used_candidates": candidates,
                "removed": removed,
            }
        )

    def _api_meals_used_up(self) -> None:
        """V2 decrement confirmation — user ticked which items were used."""
        from nutrime.inventory.store import remove_items_by_name

        payload = self._read_json_body()
        names = payload.get("names")
        if not isinstance(names, list) or not names:
            self._json({"error": "names required"}, status=400)
            return
        app = self.server.app
        removed = remove_items_by_name(
            app.substrate, app.tenant_id, [str(n) for n in names]
        )
        for name in removed:
            app.audit.record_event(
                event_kind="system",
                event_subkind="inventory_item_consumed",
                actor="webui",
                payload={
                    "name": name,
                    "meal_event_id": str(payload.get("meal_event_id") or ""),
                },
            )
        self._json({"removed": removed})

    def _api_meals_feel(self) -> None:
        from nutrime.consent import ConsentError
        from nutrime.feedback import record_body_response

        payload = self._read_json_body()
        app = self.server.app
        member_id = self._member_or_400()
        if member_id is None:
            return
        try:
            atom_id = record_body_response(
                app.substrate,
                app.tenant_id,
                member_id=member_id,
                meal_event_id=str(payload.get("meal_event_id") or ""),
                freetext_response=str(payload.get("response") or ""),
                energy_rating=payload.get("energy"),
                digestion_rating=payload.get("digestion"),
                fullness_rating=payload.get("fullness"),
                mood_rating=payload.get("mood"),
            )
        except (ConsentError, ValueError) as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json({"recorded": atom_id})

    # -- API: intake (baseline profile + screeners over the web) --------------
    # Same store functions as the CLI wizard (`nutrime intake`): the web form
    # never reimplements scoring — instruments validate + score; persistence
    # is save_profile / save_screener_responses. PHI posture: handlers never
    # echo answer values to stdout (log_message is silenced above) and the
    # data never leaves the local sqlite substrate.

    _INTAKE_LIFE_STAGES = (
        "infant",
        "child",
        "adolescent",
        "adult",
        "pregnant",
        "lactating",
        "older_adult",
    )
    _INTAKE_SEX_OPTIONS = ("female", "male", "intersex", "prefer_not_to_say")

    def _intake_profile_row(self, member_id: str) -> dict[str, Any] | None:
        from nutrime.intake.store import load_member_profile

        app = self.server.app
        profile = load_member_profile(app.substrate, app.tenant_id, member_id)
        if profile is None:
            return None
        return {
            "year_of_birth": profile.year_of_birth,
            "sex_assigned_at_birth": profile.sex_assigned_at_birth,
            "life_stage": profile.life_stage,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
            "dietary_preferences": list(profile.dietary_preferences),
            "allergens": list(profile.allergens),
        }

    def _api_intake_status(self) -> None:
        member_id = self._member_or_400()
        if member_id is None:
            return
        profile = self._intake_profile_row(member_id)
        self._json(
            {
                "member_id": member_id,
                "complete": profile is not None,
                "skipped": member_id in self.server.intake_skipped,
                "profile": profile,
            }
        )

    def _api_intake_questions(self) -> None:
        from nutrime.intake.baseline import MVP_INSTRUMENTS
        from nutrime.recipes.allergens import TOP_ALLERGENS

        self._json(
            {
                "instruments": [
                    {
                        "instrument_id": inst.instrument_id,
                        "full_name": inst.full_name,
                        "disclosure": inst.disclosure,
                        "items": [
                            {"item_id": item.item_id, "prompt": item.prompt}
                            for item in inst.items
                        ],
                        "options": [
                            {"label": o.label, "value": o.value}
                            for o in inst.scale.options
                        ],
                    }
                    for inst in MVP_INSTRUMENTS
                ],
                "profile_fields": {
                    "life_stages": list(self._INTAKE_LIFE_STAGES),
                    "sex_options": list(self._INTAKE_SEX_OPTIONS),
                    "allergens": list(TOP_ALLERGENS),
                },
            }
        )

    def _api_intake_save(self) -> None:
        from nutrime.consent import ConsentError, require_consent
        from nutrime.intake.baseline import MVP_INSTRUMENTS
        from nutrime.intake.store import (
            IntakeProfile,
            save_member_profile,
            save_screener_responses,
        )
        from nutrime.knowledge.derivation import sync_from_intake

        payload = self._read_json_body()
        raw_profile = payload.get("profile")
        if not isinstance(raw_profile, dict):
            self._json({"error": "profile required"}, status=400)
            return
        raw_screeners = payload.get("screeners") or {}
        if not isinstance(raw_screeners, dict):
            self._json({"error": "screeners must be an object"}, status=400)
            return
        instruments = {i.instrument_id: i for i in MVP_INSTRUMENTS}
        unknown = sorted(set(raw_screeners) - set(instruments))
        if unknown:
            self._json(
                {"error": f"unknown instrument(s): {', '.join(unknown)}"},
                status=400,
            )
            return

        def _str_list(key: str) -> tuple[str, ...]:
            raw = raw_profile.get(key)
            if not isinstance(raw, list):
                return ()
            return tuple(
                str(v).strip() for v in raw if str(v).strip()
            )

        try:
            height = raw_profile.get("height_cm")
            weight = raw_profile.get("weight_kg")
            profile = IntakeProfile(
                year_of_birth=int(raw_profile.get("year_of_birth")),
                sex_assigned_at_birth=str(
                    raw_profile.get("sex_assigned_at_birth") or ""
                ),
                life_stage=str(raw_profile.get("life_stage") or ""),
                height_cm=int(height) if height not in (None, "") else None,
                weight_kg=float(weight) if weight not in (None, "") else None,
                dietary_preferences=_str_list("dietary_preferences"),
                allergens=_str_list("allergens"),
            )
        except (TypeError, ValueError) as err:
            self._json({"error": str(err)}, status=400)
            return

        # Validate every screener batch fully before any write: answers are
        # scale values ordered like the questions payload's items.
        responses_by_instrument: dict[str, dict[str, int]] = {}
        for instrument_id, answers in raw_screeners.items():
            instrument = instruments[instrument_id]
            if not isinstance(answers, list) or len(answers) != len(
                instrument.items
            ):
                self._json(
                    {
                        "error": (
                            f"{instrument_id}: expected"
                            f" {len(instrument.items)} answers"
                        )
                    },
                    status=400,
                )
                return
            if any(
                not isinstance(v, int) or isinstance(v, bool)
                for v in answers
            ):
                self._json(
                    {
                        "error": (
                            f"{instrument_id}: answers must be integer"
                            " scale values"
                        )
                    },
                    status=400,
                )
                return
            responses = {
                item.item_id: value
                for item, value in zip(instrument.items, answers)
            }
            try:
                instrument.score(responses)  # validates values; not persisted
            except ValueError as err:
                self._json({"error": str(err)}, status=400)
                return
            responses_by_instrument[instrument_id] = responses

        app = self.server.app
        member_id = self._member_or_400()
        if member_id is None:
            return
        try:
            require_consent(
                app.substrate, app.tenant_id, "intake_profile",
                member_id=member_id,
            )
            if responses_by_instrument:
                require_consent(
                    app.substrate, app.tenant_id, "intake_screener",
                    member_id=member_id,
                )
        except ConsentError as err:
            self._json({"error": str(err)}, status=400)
            return

        # save_member_profile upserts per (tenant, member), so a revision
        # from the Profile link overwrites in place; screener responses
        # append as a new administered_at batch (honest record).
        save_member_profile(app.substrate, app.tenant_id, member_id, profile)
        for instrument_id, responses in responses_by_instrument.items():
            save_screener_responses(
                app.substrate,
                app.tenant_id,
                instruments[instrument_id],
                responses,
                member_id=member_id,
            )
        outcome = sync_from_intake(app.substrate, app.tenant_id)
        self.server.intake_skipped.discard(member_id)
        self._json(
            {
                "saved": True,
                "constraints_derived": outcome.constraints_added,
                "atoms_added": outcome.total_atoms_added,
            }
        )

    def _api_intake_skip(self) -> None:
        # Session-scoped choice only — nothing persisted; the welcome card
        # simply stays away for this member for this server process.
        member_id = self._member_or_400()
        if member_id is None:
            return
        self.server.intake_skipped.add(member_id)
        self._json({"ok": True})

    def _api_grocery(self, query: dict[str, list[str]]) -> None:
        from nutrime.grocery.aggregate import display_amount
        from nutrime.grocery.build import build_grocery_list
        from nutrime.plans.store import PlanVault

        app = self.server.app
        plan_vault = PlanVault(app.corpus_dir)
        plan_id = (query.get("plan_id") or [""])[0].strip()
        plans = plan_vault.list_plans() if plan_vault.root.exists() else []
        if not plan_id:
            if not plans:
                self._json({"error": "no plans yet"}, status=404)
                return
            plan_id = plans[-1].plan_id
        if not plan_vault.exists(plan_id):
            self._json({"error": f"no such plan: {plan_id}"}, status=404)
            return
        inventory = [
            item.name for item in list_items(app.substrate, app.tenant_id)
        ]
        groceries = build_grocery_list(
            plan_vault.read(plan_id),
            self.server.vault,
            inventory_names=inventory,
        )

        def _line(line) -> dict[str, Any]:
            return {
                "food": line.food,
                "amount": display_amount(line),
                "notes": line.notes,
                "recipes": sorted(
                    {c.recipe_title for c in line.contributions}
                ),
            }

        self._json(
            {
                "plan_id": groceries.plan_id,
                "to_buy": [_line(l) for l in groceries.to_buy],
                "have": [_line(l) for l in groceries.have],
                "missing_recipe_ids": list(groceries.missing_recipe_ids),
            }
        )

    def _api_sources(self) -> None:
        counts: dict[str, int] = {}
        for record in self.server.vault.iter_recipes():
            # Facet counts mirror what search can actually surface —
            # quarantined rows (junk + the de-scoped historical corpus)
            # are invisible here too.
            if record.frontmatter.get("vetting_status") == "quarantined":
                continue
            key = source_collection(record.frontmatter)
            counts[key] = counts.get(key, 0) + 1
        self._json(
            {
                "sources": [
                    {
                        "key": key,
                        "label": SOURCE_LABELS.get(key, key),
                        "count": count,
                    }
                    for key, count in sorted(
                        counts.items(), key=lambda kv: -kv[1]
                    )
                ]
            }
        )

    # -- API: Pinterest sync (#24) ------------------------------------------------

    def _api_pinterest_status(self) -> None:
        from nutrime.recipes.pinterest import has_token

        self._json(
            {
                "connected": has_token(),
                "how_to_connect": (
                    "One-time setup in a terminal: nutrime pinterest connect"
                    " (it opens Pinterest in the browser — log in, click"
                    " Allow, done)."
                ),
            }
        )

    def _api_pinterest_sync(self) -> None:
        from nutrime.recipes.pinterest import (
            MissingTokenError,
            PinterestAuthError,
            PinterestClient,
            resolve_token,
            sync_pins,
        )

        payload = self._read_json_body()
        board = str(payload.get("board") or "").strip() or None
        try:
            token = resolve_token()
        except MissingTokenError as err:
            self._json({"error": str(err)}, status=400)
            return
        def _run(tok: str):
            client = PinterestClient(
                token=tok,
                fetcher=self.server.pinterest_api_fetcher,
                pacer=self.server.ingest_pacer,
            )
            return sync_pins(
                client,
                self.server.vault,
                board_name=board,
                page_fetcher=self.server.ingest_fetcher,
                pacer=self.server.ingest_pacer or Pacer(delay_s=1.0),
            )

        try:
            try:
                sync = _run(token)
            except PinterestAuthError:
                # 30-day access token likely expired — renew from the stored
                # refresh token and retry once before bothering the user.
                from nutrime.recipes.pinterest import refresh_access_token

                sync = _run(refresh_access_token())
        except (MissingTokenError, PinterestAuthError, ValueError) as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json(
            {
                "pins_seen": sync.pins_seen,
                "pins_with_links": sync.pins_with_links,
                "pins_without_links": sync.pins_without_links,
                "written": sync.ingest.written,
                "skipped": len(sync.ingest.skipped_upstream_ids),
                "failures": [
                    {"url": url, "reason": reason}
                    for url, reason in sync.ingest.failures
                ],
                "corpus_count": self.server.vault.count(),
            }
        )


def serve(
    data_dir: Path | None = None,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> NutriMeWebServer:
    """Construct the server (does not start serving — caller owns the loop)."""
    return NutriMeWebServer((host, port), data_dir=data_dir)


# -- the page -----------------------------------------------------------------
# Single embedded page, system fonts only, no external assets: the whole UI
# works offline on the household LAN. Warm editorial look — deliberately not
# the dark-neon/bento dashboard idiom; this is a kitchen tool.

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NutriMe — what can we make?</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='14' fill='%23476341'/%3E%3Cpath d='M16 7c-5 4-6 10-3 16 5-2 8-8 3-16z' fill='%23f7f1e5'/%3E%3C/svg%3E">
<style>
  :root {
    --paper: #f7f1e5;
    --card: #fffdf7;
    --ink: #2b2620;
    --ink-soft: #6f6557;
    --line: #e3d9c6;
    --accent: #bc4b27;
    --accent-ink: #fff6ef;
    --leaf: #47603f;
    --leaf-soft: #eef0e4;
    --gold: #b98a2e;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--paper);
    color: var(--ink);
    font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    min-height: 100vh;
  }
  .serif { font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }

  header {
    padding: 40px 24px 8px;
    max-width: 1060px; margin: 0 auto;
  }
  .wordmark {
    font-family: "Iowan Old Style", Palatino, Georgia, serif;
    font-size: 15px; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--leaf); font-weight: 600;
  }
  h1 {
    font-family: "Iowan Old Style", Palatino, Georgia, serif;
    font-size: clamp(34px, 5.4vw, 54px);
    line-height: 1.08; font-weight: 500; letter-spacing: -0.01em;
    margin-top: 10px; max-width: 17ch;
  }
  h1 em { font-style: italic; color: var(--accent); }
  .sub { color: var(--ink-soft); margin-top: 10px; max-width: 52ch; }

  main { max-width: 1060px; margin: 0 auto; padding: 20px 24px 80px; }

  /* -- ask panel -- */
  .ask {
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 22px; margin-top: 18px;
    box-shadow: 0 1px 2px rgba(60,48,30,.05), 0 12px 32px -18px rgba(60,48,30,.18);
  }
  .ask label.lbl {
    display: block; font-size: 12px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--ink-soft); font-weight: 600; margin-bottom: 7px;
  }
  .haveRow { display: flex; gap: 10px; flex-wrap: wrap; }
  .haveRow input[type=text] {
    flex: 1 1 320px; font-size: 17px; padding: 13px 16px;
    border: 1.5px solid var(--line); border-radius: 9px; background: #fff;
    color: var(--ink); font-family: inherit;
  }
  .haveRow input[type=text]:focus { outline: 2px solid var(--leaf); outline-offset: 1px; border-color: var(--leaf); }
  button {
    font-family: inherit; font-size: 15px; font-weight: 600;
    border: none; border-radius: 9px; cursor: pointer; padding: 13px 22px;
  }
  .btn-go { background: var(--accent); color: var(--accent-ink); min-height: 48px; }
  .btn-go:hover { background: #a63f1f; }
  .btn-quiet { background: transparent; color: var(--leaf); padding: 8px 10px; font-weight: 600; }
  .btn-quiet:hover { text-decoration: underline; }

  .optRow { display: flex; gap: 18px; flex-wrap: wrap; align-items: center; margin-top: 16px; }
  .opt { display: flex; align-items: center; gap: 7px; font-size: 14.5px; color: var(--ink-soft); cursor: pointer; }
  .opt input { width: 17px; height: 17px; accent-color: var(--leaf); cursor: pointer; }
  .opt select, .opt input[type=number] {
    font-family: inherit; font-size: 14.5px; padding: 6px 8px;
    border: 1px solid var(--line); border-radius: 7px; background: #fff; color: var(--ink);
  }

  /* -- phase pills -- */
  .phases { margin-top: 16px; }
  .pillRow { display: flex; gap: 8px; flex-wrap: wrap; }
  .pill {
    padding: 8px 15px; border-radius: 999px; font-size: 14px; font-weight: 600;
    background: var(--leaf-soft); color: var(--leaf); border: 1.5px solid transparent;
  }
  .pill:hover { border-color: var(--leaf); }
  .pill.on { background: var(--leaf); color: #fff; }
  .phaseNote {
    margin-top: 12px; padding: 12px 14px; border-left: 3px solid var(--gold);
    background: #faf4e4; border-radius: 0 9px 9px 0;
    font-size: 13.5px; color: var(--ink-soft); display: none;
  }
  .phaseNote strong { color: var(--ink); }

  /* -- kitchen strip -- */
  .kitchen { margin-top: 26px; }
  .kitchen h2, .results h2, .importer h2 {
    font-family: "Iowan Old Style", Palatino, Georgia, serif;
    font-size: 22px; font-weight: 600; margin-bottom: 4px;
  }
  .kitchen .hint, .importer .hint { font-size: 13.5px; color: var(--ink-soft); margin-bottom: 12px; }
  .chips { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .chip {
    display: inline-flex; align-items: center; gap: 7px;
    background: var(--card); border: 1px solid var(--line); border-radius: 999px;
    padding: 7px 8px 7px 14px; font-size: 14px;
  }
  .chip .loc { font-size: 11px; color: var(--ink-soft); text-transform: uppercase; letter-spacing: .06em; }
  .chip button {
    background: var(--paper); color: var(--ink-soft); border-radius: 999px;
    width: 24px; height: 24px; padding: 0; font-size: 13px; line-height: 1;
  }
  .chip button:hover { background: var(--accent); color: #fff; }
  .chipAdd { display: inline-flex; gap: 6px; }
  .chipAdd input {
    font-family: inherit; font-size: 14px; padding: 7px 12px; width: 150px;
    border: 1.5px dashed var(--line); border-radius: 999px; background: transparent; color: var(--ink);
  }
  .chipAdd input:focus { outline: none; border-color: var(--leaf); border-style: solid; }
  .chipAdd select {
    font-family: inherit; font-size: 13px; border: 1px solid var(--line);
    border-radius: 999px; background: var(--card); color: var(--ink-soft); padding: 0 8px;
  }

  /* -- results -- */
  .results { margin-top: 34px; }
  .resultMeta { font-size: 13.5px; color: var(--ink-soft); margin-bottom: 14px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 14px; }
  .card {
    background: var(--card); border: 1px solid var(--line); border-radius: 12px;
    padding: 18px; cursor: pointer; display: flex; flex-direction: column; gap: 10px;
    transition: transform .12s ease, box-shadow .12s ease;
  }
  .card:hover { transform: translateY(-2px); box-shadow: 0 14px 28px -16px rgba(60,48,30,.3); }
  .card h3 {
    font-family: "Iowan Old Style", Palatino, Georgia, serif;
    font-size: 18.5px; font-weight: 600; line-height: 1.25;
  }
  .matchLine { display: flex; gap: 6px; flex-wrap: wrap; }
  .tag {
    font-size: 12px; padding: 3px 9px; border-radius: 999px; font-weight: 600;
  }
  .tag.have { background: var(--leaf-soft); color: var(--leaf); }
  .tag.boost { background: #faf0dc; color: var(--gold); }
  .tag.warn { background: #f7e5de; color: var(--accent); }
  .cardFoot { margin-top: auto; font-size: 12px; color: var(--ink-soft); display: flex; justify-content: space-between; gap: 8px; }
  .attr { font-size: 11.5px; color: var(--ink-soft); border-top: 1px dashed var(--line); padding-top: 8px; overflow-wrap: anywhere; }
  .empty {
    padding: 36px 20px; text-align: center; color: var(--ink-soft);
    background: var(--card); border: 1px dashed var(--line); border-radius: 12px;
    font-size: 15px;
  }

  /* -- importer -- */
  .importer { margin-top: 44px; border-top: 1px solid var(--line); padding-top: 28px; }
  .importer textarea {
    width: 100%; min-height: 110px; font: 13.5px/1.5 ui-monospace, Menlo, monospace;
    padding: 13px 15px; border: 1.5px solid var(--line); border-radius: 10px;
    background: #fff; color: var(--ink); resize: vertical;
  }
  .importer textarea:focus { outline: 2px solid var(--leaf); outline-offset: 1px; }
  .importRow { display: flex; gap: 12px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
  .importReport { font-size: 13.5px; color: var(--ink-soft); margin-top: 10px; white-space: pre-wrap; }
  .importReport .bad { color: var(--accent); }

  /* -- detail overlay -- */
  .overlay {
    position: fixed; inset: 0; background: rgba(43,38,32,.45); display: none;
    align-items: flex-start; justify-content: center; padding: 4vh 16px; z-index: 10;
    overflow-y: auto;
  }
  .overlay.on { display: flex; }
  .sheet {
    background: var(--card); border-radius: 16px; max-width: 640px; width: 100%;
    padding: 30px 30px 24px; position: relative;
    box-shadow: 0 30px 70px -20px rgba(43,38,32,.5);
  }
  .sheet h3 {
    font-family: "Iowan Old Style", Palatino, Georgia, serif;
    font-size: 26px; font-weight: 600; line-height: 1.2; padding-right: 40px;
  }
  .sheet .meta { font-size: 13.5px; color: var(--ink-soft); margin-top: 6px; }
  .sheet h4 {
    font-size: 12px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--leaf); margin: 22px 0 8px;
  }
  .sheet ul { list-style: none; }
  .sheet ul li { padding: 5px 0; border-bottom: 1px dotted var(--line); font-size: 15px; }
  .sheet ol { padding-left: 22px; }
  .sheet ol li { padding: 6px 0 6px 4px; font-size: 15px; }
  .sheet .attr { margin-top: 18px; }
  .sheet .srcLink { font-size: 13.5px; }
  .sheet .srcLink a { color: var(--accent); }
  .closeX {
    position: absolute; top: 18px; right: 18px; width: 34px; height: 34px;
    border-radius: 999px; background: var(--paper); color: var(--ink-soft);
    font-size: 16px; padding: 0;
  }
  .closeX:hover { background: var(--accent); color: #fff; }

  /* -- intake wizard -- */
  .welcome { border-left: 4px solid var(--accent); }
  .formRow { margin: 14px 0; }
  .formRow > label {
    display: block; font-size: 12px; letter-spacing: .1em; text-transform: uppercase;
    color: var(--ink-soft); font-weight: 600; margin-bottom: 5px;
  }
  .formRow input[type=number], .formRow input[type=text], .formRow select {
    font-family: inherit; font-size: 15px; padding: 10px 13px;
    border: 1.5px solid var(--line); border-radius: 8px; background: #fff;
    color: var(--ink); width: 100%; max-width: 300px;
  }
  .formRow input:focus, .formRow select:focus { outline: 2px solid var(--leaf); outline-offset: 1px; }
  .qRow { padding: 12px 0; border-bottom: 1px dotted var(--line); }
  .qRow .q { font-size: 14.5px; margin-bottom: 8px; }
  .qOpts { display: flex; gap: 6px; flex-wrap: wrap; }
  .qOpts label {
    display: inline-flex; align-items: center; gap: 6px; cursor: pointer;
    font-size: 13px; background: var(--leaf-soft); color: var(--leaf);
    border-radius: 999px; padding: 6px 12px; border: 1.5px solid transparent;
  }
  .qOpts label:hover { border-color: var(--leaf); }
  .qOpts input { accent-color: var(--leaf); cursor: pointer; }
  .stepNav { display: flex; gap: 12px; align-items: center; margin-top: 24px; flex-wrap: wrap; }
  .stepTag { font-size: 12px; letter-spacing: .14em; text-transform: uppercase; color: var(--gold); font-weight: 600; }
  .intakeMsg { color: var(--accent); font-size: 13.5px; margin-top: 10px; min-height: 1.2em; }
  .privacyNote {
    background: var(--leaf-soft); border-left: 3px solid var(--leaf);
    border-radius: 0 9px 9px 0; padding: 14px 16px; font-size: 14px;
    color: var(--ink); margin-top: 14px;
  }
  .toast {
    position: fixed; bottom: 26px; left: 50%; transform: translateX(-50%);
    background: var(--leaf); color: #fff; padding: 13px 24px; border-radius: 10px;
    font-size: 14.5px; font-weight: 600; z-index: 30; display: none;
    box-shadow: 0 16px 40px -12px rgba(43,38,32,.5); max-width: 90vw;
  }

  footer {
    max-width: 1060px; margin: 0 auto; padding: 0 24px 40px;
    font-size: 12px; color: var(--ink-soft);
  }

  @media (max-width: 560px) {
    header { padding-top: 26px; }
    .ask { padding: 16px; }
  }
  .whoRow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .whoRow label { font-size: 12.5px; color: var(--ink-soft); }
  #memberPicker {
    font: inherit; font-size: 14px; padding: 7px 10px; min-height: 36px;
    border: 1.5px solid var(--line); border-radius: 9px;
    background: var(--card); color: var(--ink); max-width: 46vw;
  }
  #memberPicker:focus { outline: 2px solid var(--leaf); outline-offset: 1px; }
</style>
</head>
<body>
<header>
  <div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px">
    <div class="wordmark">NutriMe</div>
    <div class="whoRow">
      <label for="memberPicker">Who's using this?</label>
      <select id="memberPicker" aria-label="Household member"></select>
      <button class="btn-quiet" id="profileLink" style="font-size:13.5px">Profile</button>
    </div>
  </div>
  <h1>What can we make with <em>what we already have?</em></h1>
  <p class="sub">Search the household recipe collection by what's in the kitchen —
  and, if you track a cycle, tilt the ranking toward foods that fit its current phase.</p>
</header>

<main>
  <section class="ask welcome" id="welcomeCard" style="display:none">
    <label class="lbl">Welcome</label>
    <p style="margin-bottom:12px"><span id="welcomeWho">Set up your profile</span> &mdash; 5 minutes,
    stays on this device. It teaches the planner what to avoid and what you love.</p>
    <div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap">
      <button class="btn-go" id="welcomeStart">Set up my profile</button>
      <button class="btn-quiet" id="welcomeSkip">skip for now</button>
    </div>
  </section>

  <section class="ask" id="tonightBox" style="margin-bottom:0">
    <label class="lbl">Tonight</label>
    <div id="tonightBody"></div>
  </section>

  <section class="ask" id="searchBox">
    <label class="lbl" for="have">I have…</label>
    <div class="haveRow">
      <input type="text" id="have" placeholder="chicken, spinach, lemon"
             autocomplete="off">
      <button class="btn-go" id="go">Find recipes</button>
    </div>
    <div class="optRow">
      <label class="opt"><input type="checkbox" id="useInventory" checked>
        include my kitchen list</label>
      <label class="opt"><input type="checkbox" id="applyConstraints" checked>
        respect household avoid-list</label>
      <label class="opt"><input type="checkbox" id="broaden">
        nudge toward new cuisines</label>
      <label class="opt">ready in
        <select id="maxTime">
          <option value="">any time</option>
          <option value="30">30 min</option>
          <option value="45">45 min</option>
          <option value="60">1 hour</option>
        </select></label>
    </div>
    <div class="phases">
      <label class="lbl">Cycle phase <span style="text-transform:none;letter-spacing:0;font-weight:400">(optional — gentle boosts, never filters)</span></label>
      <div class="pillRow" id="phasePills"></div>
      <div class="phaseNote" id="phaseNote"></div>
    </div>
    <div class="phases">
      <label class="lbl">From</label>
      <div class="pillRow" id="sourcePills"></div>
    </div>
  </section>

  <section class="kitchen">
    <h2 class="serif">In my kitchen</h2>
    <p class="hint">These count toward "what we already have" when the box above is ticked.</p>
    <div class="chips" id="chips"></div>
  </section>

  <section class="results">
    <h2 class="serif">Recipes</h2>
    <div class="resultMeta" id="resultMeta">&nbsp;</div>
    <div id="resultsBox"><div class="empty">Tell me what you have, or just hit
      <b>Find recipes</b> to browse the collection.</div></div>
  </section>

  <section class="importer">
    <h2 class="serif">Your Pinterest, searchable</h2>
    <div id="pinBox">
      <p class="hint" id="pinHint"></p>
      <div class="importRow" id="pinRow" style="display:none">
        <button class="btn-go" id="pinSync">Sync my pins</button>
        <input type="text" id="pinBoard" placeholder="board name (optional — all pins if blank)"
               style="flex:1 1 220px;font-size:14.5px;padding:11px 14px;border:1.5px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);font-family:inherit">
        <span class="hint" id="pinBusy" style="display:none">syncing — about a second per new pin…</span>
      </div>
      <div class="importReport" id="pinReport"></div>
    </div>
    <details style="margin-top:18px">
      <summary class="hint" style="cursor:pointer">Or paste recipe links by hand</summary>
      <div style="margin-top:10px">
      <textarea id="importUrls" placeholder="https://..."></textarea>
      <div class="importRow">
        <button class="btn-go" id="importGo">Import recipes</button>
        <span class="hint" id="importBusy" style="display:none">fetching — about a second per link…</span>
      </div>
      <div class="importReport" id="importReport"></div>
      </div>
    </details>
  </section>
</main>

<div class="overlay" id="overlay">
  <div class="sheet" id="sheet" role="dialog" aria-modal="true"></div>
</div>

<div class="overlay" id="intakeOverlay">
  <div class="sheet" id="intakeSheet" role="dialog" aria-modal="true"></div>
</div>

<div class="toast" id="toast"></div>

<footer id="disclosure"></footer>

<script>
const $ = id => document.getElementById(id);
let PHASE = "";

function esc(s) {
  return String(s).replace(/[&<>"']/g,
    c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

/* -- household member (#29): one shared device, picker not login -- */
let MEMBER = null, MEMBERS = [];
try { MEMBER = localStorage.getItem("nutrime.member"); } catch (e) {}
function memberHeaders(extra) {
  const h = Object.assign({}, extra || {});
  if (MEMBER) h["X-NutriMe-Member"] = MEMBER;
  return h;
}
function memberName() {
  const m = MEMBERS.find(x => x.id === MEMBER);
  return m ? m.name : "";
}
// "Sam's profile" once a household has several people; "Your profile" alone.
function profileLabel() {
  return MEMBERS.length > 1 && memberName() ?
    memberName() + "\\u2019s profile" : "Your profile";
}
async function jget(url) { const r = await fetch(url, {headers: memberHeaders()}); return r.json(); }
async function jpost(url, body) {
  const r = await fetch(url, {method:"POST",
                              headers: memberHeaders({"Content-Type":"application/json"}),
                              body: JSON.stringify(body)});
  return r.json();
}
function renderMembers(data) {
  MEMBERS = data.members;
  if (!MEMBERS.some(m => m.id === MEMBER)) MEMBER = data.default_member_id;
  try { localStorage.setItem("nutrime.member", MEMBER); } catch (e) {}
  const sel = $("memberPicker");
  sel.innerHTML = MEMBERS.map(m =>
    '<option value="' + esc(m.id) + '"' + (m.id === MEMBER ? " selected" : "") + ">" +
    esc(m.name) + "</option>").join("") +
    '<option value="__add">+ Add person\u2026</option>';
}
async function loadMembers() {
  // Resolve the stored pick before anything member-scoped loads; a stale
  // id (archived member, fresh install) falls back to the default.
  const r = await fetch("/api/members");
  renderMembers(await r.json());
}
async function onMemberChange() {
  const sel = $("memberPicker");
  if (sel.value === "__add") {
    const name = (prompt("Name for the new household member?") || "").trim();
    if (name) {
      const r = await fetch("/api/members", {method: "POST",
        headers: {"Content-Type": "application/json"}, body: JSON.stringify({name})});
      const data = await r.json();
      if (data.error) { toast(data.error); renderMembers({members: MEMBERS, default_member_id: MEMBER}); return; }
      MEMBER = data.added;
      renderMembers(data);
    } else {
      sel.value = MEMBER;
      return;
    }
  } else {
    MEMBER = sel.value;
    try { localStorage.setItem("nutrime.member", MEMBER); } catch (e) {}
  }
  loadTonight();
  loadIntakeStatus();
}

/* -- source filter -- */
let SOURCES = new Set();
async function loadSources() {
  const data = await jget("/api/sources");
  const row = $("sourcePills");
  row.innerHTML = "";
  const all = document.createElement("button");
  all.className = "pill on"; all.textContent = "Everything"; all.dataset.key = "";
  all.onclick = () => { SOURCES.clear(); syncSourcePills(); doSearch(); };
  row.appendChild(all);
  for (const s of data.sources) {
    const b = document.createElement("button");
    b.className = "pill"; b.dataset.key = s.key;
    b.textContent = s.label + " (" + s.count + ")";
    b.onclick = () => {
      if (SOURCES.has(s.key)) SOURCES.delete(s.key); else SOURCES.add(s.key);
      syncSourcePills(); doSearch();
    };
    row.appendChild(b);
  }
}
function syncSourcePills() {
  document.querySelectorAll("#sourcePills .pill").forEach(p => {
    const key = p.dataset.key;
    p.classList.toggle("on", key === "" ? SOURCES.size === 0 : SOURCES.has(key));
  });
}

/* -- phases -- */
let PHASE_DATA = {};
async function loadPhases() {
  const data = await jget("/api/phases");
  $("disclosure").textContent = data.disclosure;
  const row = $("phasePills");
  row.innerHTML = "";
  const none = document.createElement("button");
  none.className = "pill on"; none.textContent = "Not using";
  none.onclick = () => setPhase("", none);
  row.appendChild(none);
  for (const p of data.phases) {
    PHASE_DATA[p.key] = p;
    const b = document.createElement("button");
    b.className = "pill"; b.textContent = p.label;
    b.onclick = () => setPhase(p.key, b);
    row.appendChild(b);
  }
}
function setPhase(key, btn) {
  PHASE = key;
  document.querySelectorAll("#phasePills .pill").forEach(x => x.classList.remove("on"));
  btn.classList.add("on");
  const note = $("phaseNote");
  if (key && PHASE_DATA[key]) {
    const p = PHASE_DATA[key];
    note.style.display = "block";
    note.innerHTML = "<strong>" + esc(p.label) + ":</strong> boosting " + esc(p.emphasis) +
      ".<br>" + esc(p.evidence_note);
  } else { note.style.display = "none"; }
  doSearch();
}

/* -- kitchen chips -- */
async function loadInventory() {
  const data = await jget("/api/inventory");
  const box = $("chips");
  box.innerHTML = "";
  for (const item of data.items) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.innerHTML = esc(item.name) + ' <span class="loc">' + esc(item.location) + "</span>";
    const x = document.createElement("button");
    x.textContent = "\\u00d7"; x.title = "Remove " + item.name;
    x.onclick = async () => { await jpost("/api/inventory/remove", {id: item.id});
                              loadInventory(); };
    chip.appendChild(x);
    box.appendChild(chip);
  }
  const add = document.createElement("span");
  add.className = "chipAdd";
  add.innerHTML = '<input id="newItem" placeholder="add an item…">' +
    '<select id="newLoc"><option value="fridge">fridge</option>' +
    '<option value="pantry">pantry</option><option value="freezer">freezer</option>' +
    '<option value="countertop">countertop</option></select>';
  box.appendChild(add);
  $("newItem").addEventListener("keydown", async e => {
    if (e.key === "Enter" && e.target.value.trim()) {
      await jpost("/api/inventory", {name: e.target.value.trim(), location: $("newLoc").value});
      loadInventory();
    }
  });
}

/* -- search -- */
let OFFSET = 0;
function searchParams() {
  const params = new URLSearchParams();
  const have = $("have").value.trim();
  if (have) params.set("have", have);
  if ($("useInventory").checked) params.set("use_inventory", "1");
  if ($("applyConstraints").checked) params.set("apply_constraints", "1");
  if ($("maxTime").value) params.set("max_time", $("maxTime").value);
  if ($("broaden").checked) params.set("broaden", "1");
  if (PHASE) params.set("phase", PHASE);
  if (SOURCES.size) params.set("sources", [...SOURCES].join(","));
  return params;
}
async function doSearch(append) {
  if (!append) OFFSET = 0;
  const params = searchParams();
  if (OFFSET) params.set("offset", OFFSET);
  const data = await jget("/api/search?" + params.toString());
  const box = $("resultsBox");
  const shown = OFFSET + data.results.length;
  $("resultMeta").textContent = "showing " + shown + " of " + data.total +
    " matching \\u00b7 " + data.corpus_count + " recipes in the collection" +
    (data.on_hand_count ? " \\u00b7 matching against " + data.on_hand_count + " ingredients you have" : "");
  if (!data.total) {
    box.innerHTML = '<div class="empty">Nothing matched those filters \\u2014 try fewer' +
      ' restrictions, or import more of your saved recipes below.</div>';
    return;
  }
  let grid;
  if (append) {
    grid = box.querySelector(".grid");
    const old = box.querySelector(".moreRow");
    if (old) old.remove();
  }
  if (!grid) { grid = document.createElement("div"); grid.className = "grid"; }
  for (const r of data.results) {
    const card = document.createElement("div");
    card.className = "card";
    let tags = "";
    for (const m of r.on_hand_matches) {
      const urgent = (r.expiring_matches || []).includes(m);
      tags += '<span class="tag have">' + (urgent ? "\\u23f3 " : "\\u2713 ") + esc(m) +
        (urgent ? " soon!" : "") + "</span>";
    }
    for (const m of r.prefer_matches) tags += '<span class="tag boost">\\u2191 ' + esc(m) + "</span>";
    if (r.times_cooked) tags += '<span class="tag boost">\\u2665 cooked ' + r.times_cooked + "x" +
      (r.avg_enjoyment ? " \\u00b7 " + r.avg_enjoyment + "/5" : "") + "</span>";
    if (r.novel_cuisine) tags += '<span class="tag boost">\\u2726 new cuisine</span>';
    for (const a of r.allergens) tags += '<span class="tag warn">' + esc(a) + "</span>";
    card.innerHTML =
      "<h3>" + esc(r.title) + "</h3>" +
      (tags ? '<div class="matchLine">' + tags + "</div>" : "") +
      '<div class="cardFoot"><span>' +
      (r.personal_time_min ? "\\u23f1 ~" + r.personal_time_min + " min for you" :
       r.total_time_min ? "\\u23f1 " + r.total_time_min + " min" : "") +
      "</span><span>" +
      (r.on_hand_matches.length ? r.on_hand_matches.length + " on hand \\u00b7 " : "") +
      esc(r.source_label || "") + "</span></div>" +
      '<div class="attr">' + esc(r.attribution) + "</div>";
    card.onclick = () => openDetail(r.recipe_id);
    grid.appendChild(card);
  }
  if (!append) { box.innerHTML = ""; box.appendChild(grid); }
  OFFSET = shown;
  if (shown < data.total) {
    const row = document.createElement("div");
    row.className = "moreRow";
    row.style.cssText = "text-align:center;margin-top:16px";
    const btn = document.createElement("button");
    btn.className = "btn-go";
    btn.textContent = "Show more (" + (data.total - shown) + " left)";
    btn.onclick = () => doSearch(true);
    row.appendChild(btn);
    box.appendChild(row);
  }
}

/* -- detail -- */
// Source URLs come from imported pages; only http(s) becomes a link.
function safeUrl(u) { return typeof u === "string" && /^https?:[/][/]/i.test(u); }
async function openDetail(id) {
  const d = await jget("/api/recipes/" + id);
  if (d.error) return;
  const meta = [];
  if (d.total_time_min) meta.push("\\u23f1 " + d.total_time_min + " min");
  if (d.yields) meta.push("serves " + d.yields);
  if (d.cuisine.length) meta.push(d.cuisine.join(", "));
  if (d.allergens.length) meta.push("contains: " + d.allergens.join(", "));
  $("sheet").innerHTML =
    '<button class="closeX" onclick="closeDetail()" aria-label="Close">\\u00d7</button>' +
    "<h3>" + esc(d.title) + "</h3>" +
    '<div class="meta">' + esc(meta.join(" \\u00b7 ")) + "</div>" +
    (d.equipment && d.equipment.length ?
      '<div class="meta" style="margin-top:8px">Equipment: ' + d.equipment.map(esc).join(", ") + "</div>" : "") +
    "<h4>Ingredients</h4><ul>" +
    d.ingredients.map(i => "<li>" + esc(i) + "</li>").join("") + "</ul>" +
    "<h4>Steps</h4><ol>" +
    d.steps.map(s => "<li>" + esc(s) + "</li>").join("") + "</ol>" +
    (safeUrl(d.source_url) ? '<div class="srcLink"><a href="' + esc(d.source_url) +
      '" target="_blank" rel="noopener">Open the original \\u2197</a></div>' : "") +
    '<div class="attr">' + esc(d.attribution) + "</div>";
  $("overlay").classList.add("on");
}
function closeDetail() { $("overlay").classList.remove("on"); }
$("overlay").addEventListener("click", e => { if (e.target === $("overlay")) closeDetail(); });
document.addEventListener("keydown", e => {
  if (e.key === "Escape") { closeDetail(); closeIntake(); }
});

/* -- import -- */
$("importGo").onclick = async () => {
  const raw = $("importUrls").value.trim();
  if (!raw) return;
  $("importBusy").style.display = "inline";
  $("importReport").textContent = "";
  const data = await jpost("/api/import", {urls: raw});
  $("importBusy").style.display = "none";
  if (data.error) { $("importReport").innerHTML = '<span class="bad">' + esc(data.error) + "</span>"; return; }
  let msg = "Saved " + data.written + " new recipe" + (data.written === 1 ? "" : "s") +
    " to the collection (" + data.corpus_count + " total).";
  if (data.skipped) msg += " " + data.skipped + " already saved.";
  $("importReport").textContent = msg;
  if (data.failures.length) {
    const lines = data.failures.map(f => f.url + " \\u2014 " + f.reason);
    $("importReport").innerHTML += '<br><span class="bad">Couldn\\u2019t read ' +
      data.failures.length + ":</span><br>" + lines.map(esc).join("<br>");
  }
  if (data.written) { $("importUrls").value = ""; doSearch(); }
};

/* -- tonight panel (step 8 slice) + feedback (step 7) -- */
async function loadTonight() {
  const data = await jget("/api/tonight");
  const box = $("tonightBox"), body = $("tonightBody");
  const parts = [];
  if (data.use_soon && data.use_soon.length) {
    const chips = data.use_soon.map(u => {
      const label = u.days_left < 0 ? "past date" :
        u.days_left === 0 ? "today" : u.days_left + "d left";
      return '<span class="tag warn">\\u23f3 ' + esc(u.name) + " \\u00b7 " + label + "</span>";
    }).join(" ");
    const names = data.use_soon.map(u => u.name).join(", ");
    parts.push(
      '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">' +
      '<span class="hint">Use soon:</span> ' + chips +
      '<button class="btn-quiet" onclick="$(\\'have\\').value=' +
      JSON.stringify(names).replace(/"/g, "&quot;") + ';doSearch()">find recipes</button></div>'
    );
  }
  if (data.tonight) {
    const t = data.tonight;
    parts.push(
      '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap' +
      (parts.length ? ';margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)' : '') + '">' +
      '<span class="serif" style="font-size:21px">' + esc(t.title) + "</span>" +
      (t.total_time_min ? '<span class="hint">\\u23f1 ' + t.total_time_min + " min</span>" : "") +
      '<button class="btn-quiet" onclick="openDetail(\\'' + esc(t.recipe_id) + '\\')">view recipe</button>' +
      '<button class="btn-go" style="padding:9px 16px;min-height:0" onclick="markCooked(\\'' +
      esc(t.recipe_id) + '\\',\\'' + esc(t.plan_id) + '\\')">We cooked it</button>' +
      "</div>" +
      (t.attribution ? '<div class="attr" style="margin-top:8px">' + esc(t.attribution) + "</div>" : "")
    );
  } else {
    // Tonight-first: the panel is always present; with no plan covering
    // today it points at the search block below.
    parts.push(
      '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap' +
      (parts.length ? ';margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)' : '') + '">' +
      '<span class="serif" style="font-size:19px;color:var(--ink-soft)">No meal planned tonight</span>' +
      '<button class="btn-go" style="padding:9px 16px;min-height:0" onclick="' +
      "document.getElementById('searchBox').scrollIntoView({behavior:'smooth'});" +
      "document.getElementById('have').focus({preventScroll:true})" +
      '">Find something to cook</button></div>'
    );
  }
  if (data.awaiting_feel) {
    const a = data.awaiting_feel;
    parts.push(
      '<div style="margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)">' +
      '<span class="hint">About ' + esc(a.recipe_title) + ' \\u2014 how did it make your body feel?</span><br>' +
      '<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">' +
      '<input type="text" id="feelText" placeholder="e.g. great energy all evening"' +
      ' style="flex:1 1 260px;font-size:14.5px;padding:10px 13px;border:1.5px solid var(--line);border-radius:9px;font-family:inherit">' +
      '<button class="btn-go" style="padding:9px 16px;min-height:0" onclick="sendFeel(\\'' +
      esc(a.meal_event_id) + '\\')">Save</button></div></div>'
    );
  }
  body.innerHTML = parts.join("");
  box.style.display = "block";
}
async function markCooked(recipeId, planId) {
  const ease = prompt("How easy was it to make? (1-5, blank to skip)");
  let payload = {recipe_id: recipeId, plan_id: planId};
  if (ease) {
    const fun = prompt("How enjoyable to make? (1-5)");
    if (fun) { payload.ease = parseInt(ease); payload.enjoyment = parseInt(fun); }
  }
  const mins = prompt("Actual minutes it took? (blank to skip)");
  if (mins) payload.actual_minutes = parseInt(mins);
  const res = await jpost("/api/meals/cooked", payload);
  if (res.error) { alert(res.error); return; }
  // V2 ask-don't-assume decrement: offer the recipe∩inventory names.
  if (res.used_candidates && res.used_candidates.length) {
    const names = res.used_candidates.join(", ");
    if (confirm("Used these up from the kitchen? " + names +
                "\\n\\nOK removes them from your inventory; Cancel keeps them.")) {
      await jpost("/api/meals/cooked/used-up",
                  {meal_event_id: res.meal_event_id, names: res.used_candidates});
      loadInventory();
    }
  }
  loadTonight();
}
async function sendFeel(mealEventId) {
  const text = $("feelText").value.trim();
  if (!text) return;
  const res = await jpost("/api/meals/feel", {meal_event_id: mealEventId, response: text});
  if (res.error) alert(res.error); else loadTonight();
}

/* -- pinterest sync -- */
async function loadPinterestStatus() {
  const s = await jget("/api/pinterest/status");
  if (s.connected) {
    $("pinHint").textContent = "Pinterest is connected. Sync pulls in any new pins" +
      " \\u2014 already-saved recipes are skipped automatically, so run it any time.";
    $("pinRow").style.display = "flex";
  } else {
    $("pinHint").textContent = "Not connected yet. One-time setup on this machine: " +
      s.how_to_connect;
  }
}
$("pinSync").onclick = async () => {
  $("pinBusy").style.display = "inline";
  $("pinReport").textContent = "";
  const data = await jpost("/api/pinterest/sync", {board: $("pinBoard").value.trim()});
  $("pinBusy").style.display = "none";
  if (data.error) { $("pinReport").innerHTML = '<span class="bad">' + esc(data.error) + "</span>"; return; }
  let msg = "Looked at " + data.pins_seen + " pin" + (data.pins_seen === 1 ? "" : "s") +
    " \\u00b7 saved " + data.written + " new recipe" + (data.written === 1 ? "" : "s") +
    " (" + data.corpus_count + " in the collection).";
  if (data.skipped) msg += " " + data.skipped + " already saved.";
  if (data.pins_without_links) msg += " " + data.pins_without_links +
    " pin" + (data.pins_without_links === 1 ? " is" : "s are") +
    " image-only (no recipe page to read yet).";
  $("pinReport").textContent = msg;
  if (data.failures.length) {
    const lines = data.failures.map(f => f.url + " \\u2014 " + f.reason);
    $("pinReport").innerHTML += '<br><span class="bad">Couldn\\u2019t read ' +
      data.failures.length + ":</span><br>" + lines.map(esc).join("<br>");
  }
  if (data.written) doSearch();
};

/* -- intake wizard (baseline profile + screeners) -- */
let INTAKE_Q = null;        // questions payload from /api/intake/questions
let INTAKE_STEP = 1;
let INTAKE_STATE = null;    // collected form state across steps

function toast(msg) {
  const t = $("toast");
  t.textContent = msg; t.style.display = "block";
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { t.style.display = "none"; }, 6000);
}

function blankIntakeState() {
  return {
    year_of_birth: "", sex_assigned_at_birth: "", life_stage: "",
    height_cm: "", weight_kg: "",
    allergens: new Set(), dietary_preferences: [],
    screeners: {},  // instrument_id -> [value per item]
  };
}

async function openIntake() {
  if (!INTAKE_Q) INTAKE_Q = await jget("/api/intake/questions");
  INTAKE_STATE = blankIntakeState();
  const status = await jget("/api/intake/status");
  if (status.profile) {
    const p = status.profile;
    INTAKE_STATE.year_of_birth = p.year_of_birth;
    INTAKE_STATE.sex_assigned_at_birth = p.sex_assigned_at_birth;
    INTAKE_STATE.life_stage = p.life_stage;
    INTAKE_STATE.height_cm = p.height_cm == null ? "" : p.height_cm;
    INTAKE_STATE.weight_kg = p.weight_kg == null ? "" : p.weight_kg;
    INTAKE_STATE.allergens = new Set(p.allergens);
    INTAKE_STATE.dietary_preferences = p.dietary_preferences.slice();
  }
  INTAKE_STEP = 1;
  renderIntakeStep();
  $("intakeOverlay").classList.add("on");
}
function closeIntake() { $("intakeOverlay").classList.remove("on"); }
$("intakeOverlay").addEventListener("click", e => {
  if (e.target === $("intakeOverlay")) closeIntake();
});

function intakeHeader(title) {
  return '<button class="closeX" onclick="closeIntake()" aria-label="Close">\\u00d7</button>' +
    '<div class="stepTag">' + esc(profileLabel()) + " \\u00b7 step " + INTAKE_STEP + ' of 4</div>' +
    '<h3>' + esc(title) + '</h3>';
}
function intakeNav(backLabel, nextLabel, nextFn) {
  return '<div class="stepNav">' +
    (backLabel ? '<button class="btn-quiet" onclick="intakeBack()">' + esc(backLabel) + '</button>' : '') +
    '<button class="btn-go" id="intakeNext" onclick="' + nextFn + '">' + esc(nextLabel) + '</button>' +
    '<button class="btn-quiet" onclick="skipIntake()">skip for now</button>' +
    '</div><div class="intakeMsg" id="intakeMsg"></div>';
}
function intakeBack() { INTAKE_STEP -= 1; renderIntakeStep(); }

function renderIntakeStep() {
  const s = INTAKE_STATE, sheet = $("intakeSheet");
  if (INTAKE_STEP === 1) {
    const sexOpts = INTAKE_Q.profile_fields.sex_options.map(o =>
      '<option value="' + esc(o) + '"' + (s.sex_assigned_at_birth === o ? ' selected' : '') + '>' +
      esc(o.replace(/_/g, " ")) + '</option>').join("");
    const stageOpts = INTAKE_Q.profile_fields.life_stages.map(o =>
      '<option value="' + esc(o) + '"' + (s.life_stage === o ? ' selected' : '') + '>' +
      esc(o.replace(/_/g, " ")) + '</option>').join("");
    sheet.innerHTML = intakeHeader("About you") +
      '<div class="formRow"><label for="inYob">Year of birth</label>' +
      '<input type="number" id="inYob" min="1900" max="2100" value="' + esc(s.year_of_birth) + '"></div>' +
      '<div class="formRow"><label for="inSex">Sex assigned at birth (used for nutrient-band lookup)</label>' +
      '<select id="inSex"><option value="">choose\\u2026</option>' + sexOpts + '</select></div>' +
      '<div class="formRow"><label for="inStage">Current life stage</label>' +
      '<select id="inStage"><option value="">choose\\u2026</option>' + stageOpts + '</select></div>' +
      '<div class="formRow"><label for="inHeight">Height in cm (optional)</label>' +
      '<input type="number" id="inHeight" min="30" max="275" value="' + esc(s.height_cm) + '"></div>' +
      '<div class="formRow"><label for="inWeight">Weight in kg (optional)</label>' +
      '<input type="number" id="inWeight" min="1" max="500" step="0.1" value="' + esc(s.weight_kg) + '"></div>' +
      intakeNav(null, "Next: food to avoid", "intakeStep1Next()");
  } else if (INTAKE_STEP === 2) {
    const chips = INTAKE_Q.profile_fields.allergens.map(a => {
      const on = s.allergens.has(a);
      return '<button class="pill' + (on ? ' on' : '') + '" data-allergen="' + esc(a) +
        '" onclick="toggleAllergen(this)">' + esc(a.replace(/_/g, " ")) + '</button>';
    }).join(" ");
    const extras = s.dietary_preferences.map((p, i) =>
      '<span class="chip">' + esc(p) +
      '<button onclick="removePref(' + i + ')" title="Remove">\\u00d7</button></span>').join(" ");
    sheet.innerHTML = intakeHeader("Allergens + preferences") +
      '<div class="formRow"><label>Food allergens to avoid (tap to toggle)</label>' +
      '<div class="pillRow" id="allergenPills">' + chips + '</div></div>' +
      '<div class="formRow"><label>Other allergens or dietary preferences ' +
      '(vegetarian, halal, no cilantro\\u2026)</label>' +
      '<div class="chips" id="prefChips">' + extras +
      '<span class="chipAdd"><input id="prefInput" placeholder="add one\\u2026, press Enter"></span></div></div>' +
      intakeNav("back", "Next: three quick check-ins", "intakeStep2Next()");
    $("prefInput").addEventListener("keydown", e => {
      if (e.key === "Enter" && e.target.value.trim()) {
        INTAKE_STATE.dietary_preferences.push(e.target.value.trim());
        renderIntakeStep();
        $("prefInput").focus();
      }
    });
  } else if (INTAKE_STEP === 3) {
    let html = intakeHeader("Three quick check-ins") +
      '<p class="hint" style="margin-top:6px">These are screening questions, not a diagnosis ' +
      '\\u2014 they help the planner notice when food support matters most. Optional: leave any blank.</p>';
    for (const inst of INTAKE_Q.instruments) {
      html += '<h4>' + esc(inst.full_name) + '</h4>';
      inst.items.forEach((item, idx) => {
        const chosen = (s.screeners[inst.instrument_id] || [])[idx];
        html += '<div class="qRow"><div class="q">' + esc(item.prompt) + '</div><div class="qOpts">' +
          inst.options.map(o =>
            '<label><input type="radio" name="' + esc(inst.instrument_id) + '-' + idx +
            '" value="' + o.value + '"' + (chosen === o.value ? ' checked' : '') + '> ' +
            esc(o.label.replace(/_/g, " ")) + '</label>').join("") +
          '</div></div>';
      });
    }
    sheet.innerHTML = html + intakeNav("back", "Next: privacy", "intakeStep3Next()");
  } else {
    sheet.innerHTML = intakeHeader("Your answers stay here") +
      '<div class="privacyNote">Everything you entered \\u2014 including the health ' +
      'check-ins \\u2014 is saved in the local database on this machine and never sent ' +
      'anywhere. NutriMe stays on this device: no cloud account, no sync, no analytics. ' +
      'You can revise or re-run this anytime from the Profile link.</div>' +
      intakeNav("back", "Save my profile", "saveIntake()");
  }
  $("intakeOverlay").scrollTop = 0;
}

function toggleAllergen(btn) {
  const a = btn.dataset.allergen;
  if (INTAKE_STATE.allergens.has(a)) INTAKE_STATE.allergens.delete(a);
  else INTAKE_STATE.allergens.add(a);
  btn.classList.toggle("on");
}
function removePref(i) {
  INTAKE_STATE.dietary_preferences.splice(i, 1);
  renderIntakeStep();
}

function intakeStep1Next() {
  const s = INTAKE_STATE;
  s.year_of_birth = $("inYob").value.trim();
  s.sex_assigned_at_birth = $("inSex").value;
  s.life_stage = $("inStage").value;
  s.height_cm = $("inHeight").value.trim();
  s.weight_kg = $("inWeight").value.trim();
  const yob = parseInt(s.year_of_birth);
  if (!yob || yob < 1900 || yob > 2100) {
    $("intakeMsg").textContent = "Please enter a year of birth between 1900 and 2100."; return;
  }
  if (!s.sex_assigned_at_birth || !s.life_stage) {
    $("intakeMsg").textContent = "Please choose both dropdowns \\u2014 they pick the right nutrient bands."; return;
  }
  INTAKE_STEP = 2; renderIntakeStep();
}
function intakeStep2Next() { INTAKE_STEP = 3; renderIntakeStep(); }
function intakeStep3Next() {
  // Collect radios; an instrument counts only when every item is answered.
  const s = INTAKE_STATE;
  s.screeners = {};
  let partial = null;
  for (const inst of INTAKE_Q.instruments) {
    const answers = [];
    inst.items.forEach((_item, idx) => {
      const picked = document.querySelector(
        'input[name="' + inst.instrument_id + '-' + idx + '"]:checked');
      if (picked) answers.push(parseInt(picked.value));
    });
    if (answers.length === inst.items.length) s.screeners[inst.instrument_id] = answers;
    else if (answers.length > 0) partial = inst.full_name;
  }
  if (partial) {
    $("intakeMsg").textContent = "Please answer both questions of \\u201c" + partial +
      "\\u201d, or clear it to skip that check-in."; return;
  }
  INTAKE_STEP = 4; renderIntakeStep();
}

async function saveIntake() {
  const s = INTAKE_STATE;
  $("intakeNext").disabled = true;
  const res = await jpost("/api/intake", {
    profile: {
      year_of_birth: parseInt(s.year_of_birth),
      sex_assigned_at_birth: s.sex_assigned_at_birth,
      life_stage: s.life_stage,
      height_cm: s.height_cm === "" ? null : parseInt(s.height_cm),
      weight_kg: s.weight_kg === "" ? null : parseFloat(s.weight_kg),
      allergens: [...s.allergens],
      dietary_preferences: s.dietary_preferences,
    },
    screeners: s.screeners,
  });
  if (res.error) {
    $("intakeNext").disabled = false;
    $("intakeMsg").textContent = res.error;
    return;
  }
  closeIntake();
  $("welcomeCard").style.display = "none";
  toast("Profile saved \\u2014 " + res.constraints_derived +
    " household constraint" + (res.constraints_derived === 1 ? "" : "s") +
    " derived. Search now respects them.");
  doSearch();
}

async function skipIntake() {
  await jpost("/api/intake/skip", {});
  closeIntake();
  $("welcomeCard").style.display = "none";
}

async function loadIntakeStatus() {
  const status = await jget("/api/intake/status");
  $("welcomeWho").textContent = "Set up " +
    (MEMBERS.length > 1 ? profileLabel() : "your profile");
  $("welcomeCard").style.display =
    (status.complete || status.skipped) ? "none" : "block";
}
$("memberPicker").addEventListener("change", onMemberChange);
$("welcomeStart").onclick = openIntake;
$("welcomeSkip").onclick = skipIntake;
$("profileLink").onclick = openIntake;

$("go").onclick = () => doSearch();
$("have").addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });
["useInventory", "applyConstraints", "maxTime", "broaden"].forEach(id =>
  $(id).addEventListener("change", () => doSearch()));

loadPhases();
loadSources();
loadInventory();
loadPinterestStatus();
loadMembers().then(() => { loadTonight(); loadIntakeStatus(); });
doSearch();
</script>
</body>
</html>
"""
