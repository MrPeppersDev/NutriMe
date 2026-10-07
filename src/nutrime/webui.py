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
    search,
    search_page,
    source_collection,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer
from nutrime.tenancy import _now_iso

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
        # Injectable for tests: app → LlmClient | None (None = local model
        # not running). Default: the local Ollama daemon.
        self.llm_client_factory = None
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
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    # -- browser-boundary checks (2026-10-07 security audit) ------------------
    # The server is localhost-only, but every website open in the same
    # browser can still *send* requests here (CSRF — verified live), and
    # a hostile site can re-resolve its own domain to 127.0.0.1 to *read*
    # responses (DNS rebinding). Host + Origin checks close both.

    _LOCAL_HOSTS = frozenset({"127.0.0.1", "localhost", "[::1]"})

    def _browser_boundary_ok(self, *, state_changing: bool) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip()
        if host not in self._LOCAL_HOSTS:
            self._json({"error": "bad host"}, status=403)
            return False
        if state_changing:
            origin = (self.headers.get("Origin") or "").strip()
            if origin:
                parsed = urllib.parse.urlparse(origin)
                if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
                    self._json({"error": "cross-origin request refused"},
                               status=403)
                    return False
        return True

    def _server_error(self, exc: Exception) -> None:
        """Generic 500: full detail to a local log, none to the client.

        Exception text can carry filesystem paths, sqlite schema, even
        credential-tool stderr — none of which belongs in a browser
        response (and before the Host check, that browser could have
        been any website via rebinding).
        """
        import traceback

        try:
            log_path = self.server.app.data_dir / "server-errors.log"
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(
                    f"{_now_iso()} {self.command} {self.path}\n"
                    f"{traceback.format_exc()}\n"
                )
        except Exception:  # noqa: BLE001 — logging must never mask the 500
            pass
        self._json(
            {"error": "Something went wrong on NutriMe's side. Details are"
                      " in server-errors.log in the data folder."},
            status=500,
        )

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
        if not self._browser_boundary_ok(state_changing=False):
            return
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
            elif route == "/api/staples":
                self._api_staples()
            elif route == "/api/members":
                self._api_members_list()
            elif route == "/api/plans":
                self._api_plans_list()
            elif route.startswith("/api/plans/"):
                self._api_plan_detail(route.removeprefix("/api/plans/"))
            elif route == "/api/tonight/alternatives":
                self._api_tonight_alternatives(query)
            elif route == "/api/consent":
                self._api_consent_list()
            elif route == "/api/derived":
                self._api_derived()
            elif route == "/api/doctor":
                self._api_doctor()
            elif route == "/api/notifications":
                self._api_notifications()
            elif route == "/api/activity":
                self._api_activity(query)
            elif route == "/api/checkin/status":
                self._api_checkin_status()
            elif route == "/api/checkin/questions":
                self._api_checkin_questions()
            elif route.startswith("/api/recipes/"):
                self._api_recipe_detail(route.removeprefix("/api/recipes/"))
            else:
                self._json({"error": "not found"}, status=404)
        except Exception as exc:  # noqa: BLE001 — surface, don't crash the server
            self._server_error(exc)

    def do_POST(self) -> None:  # noqa: N802
        if not self._browser_boundary_ok(state_changing=True):
            return
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/inventory":
                self._api_inventory_add()
            elif parsed.path == "/api/inventory/remove":
                self._api_inventory_remove()
            elif parsed.path == "/api/inventory/bulk/preview":
                self._api_inventory_bulk_preview()
            elif parsed.path == "/api/staples/toggle":
                self._api_staples_toggle()
            elif parsed.path == "/api/inventory/bulk":
                self._api_inventory_bulk_commit()
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
            elif parsed.path == "/api/plans/generate":
                self._api_plans_generate()
            elif parsed.path == "/api/plans/swap":
                self._api_plans_swap()
            elif parsed.path == "/api/consent":
                self._api_consent_set()
            elif parsed.path == "/api/notifications/settings":
                self._api_notification_settings()
            elif parsed.path == "/api/checkin":
                self._api_checkin_save()
            elif parsed.path == "/api/checkin/snooze":
                self._api_checkin_snooze()
            elif parsed.path == "/api/checkin/interval":
                self._api_checkin_interval()
            elif parsed.path == "/api/members/rename":
                self._api_members_rename()
            elif parsed.path == "/api/members/archive":
                self._api_members_archive()
            else:
                self._json({"error": "not found"}, status=404)
        except Exception as exc:  # noqa: BLE001
            self._server_error(exc)

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

    # -- plans (#33): browse, generate, swap ------------------------------------

    @staticmethod
    def _plan_day_today(plan) -> int:
        """Which plan day is today (day 1 = the day the plan was made)."""
        from datetime import date, datetime

        created = str(plan.frontmatter.get("created_at", ""))[:10]
        try:
            return (date.today() - datetime.fromisoformat(created).date()).days + 1
        except ValueError:
            return 1

    def _api_plans_list(self) -> None:
        from nutrime.plans.store import PlanVault

        vault = PlanVault(self.server.app.corpus_dir)
        plans = vault.list_plans() if vault.root.exists() else []
        self._json({
            "plans": [
                {
                    "plan_id": p.plan_id,
                    "created_at": p.frontmatter.get("created_at"),
                    "days": p.frontmatter.get("days"),
                    "meal_slots": p.frontmatter.get("meal_slots"),
                    "meals_planned": p.frontmatter.get("meals_planned"),
                    "today_day": self._plan_day_today(p),
                }
                for p in reversed(plans)
            ]
        })

    def _api_plan_detail(self, plan_id: str) -> None:
        from nutrime.plans.store import PlanVault

        vault = PlanVault(self.server.app.corpus_dir)
        if not plan_id.startswith("pln-") or not vault.exists(plan_id):
            self._json({"error": "That plan doesn't exist any more."}, status=404)
            return
        plan = vault.read(plan_id)
        entries = []
        for e in plan.entries():
            item = {
                "day": e.day, "slot": e.slot, "recipe_id": e.recipe_id,
                "title": e.title, "note": e.note,
            }
            if e.recipe_id and self.server.vault.exists(e.recipe_id):
                fm = self.server.vault.read(e.recipe_id).frontmatter
                item["attribution"] = attribution_line(fm)
                item["total_time_min"] = fm.get("estimated_total_time_min")
            entries.append(item)
        self._json({
            "plan_id": plan.plan_id,
            "created_at": plan.frontmatter.get("created_at"),
            "days": plan.frontmatter.get("days"),
            "today_day": self._plan_day_today(plan),
            "entries": entries,
        })

    def _api_plans_generate(self) -> None:
        from nutrime.plans.assemble import MEAL_SLOTS, PlanSpec
        from nutrime.plans.service import (
            LOCAL_MODEL_SETUP,
            PlanRefusedError,
            generate_and_store,
            local_client,
            plan_base_filters,
        )

        payload = self._read_json_body()
        slots = tuple(
            str(s).strip().lower() for s in (payload.get("slots") or ["dinner"])
        )
        if any(s not in MEAL_SLOTS for s in slots):
            self._json({"error": f"Meal slots must be among: {', '.join(MEAL_SLOTS)}."},
                       status=400)
            return
        try:
            spec = PlanSpec(
                days=int(payload.get("days") or 7), slots=slots,
                servings=int(payload.get("servings") or 2),
            )
        except (TypeError, ValueError) as err:
            self._json({"error": str(err)}, status=400)
            return
        if spec.days > 14:
            self._json({"error": "Plans go up to 14 days at a time."}, status=400)
            return
        app = self.server.app
        factory = self.server.llm_client_factory or local_client
        client = factory(app)
        if client is None:
            self._json({"error": LOCAL_MODEL_SETUP, "code": "local_model_unavailable"},
                       status=503)
            return
        max_time = payload.get("max_time")
        filters, applied = plan_base_filters(
            app, max_time=int(max_time) if max_time else None
        )
        try:
            plan_id, _, plan = generate_and_store(
                app, client, spec, filters, applied, actor="webui"
            )
        except PlanRefusedError as refusal:
            self._json(
                {"error": str(refusal), "code": "condition_refusal"},
                status=409,
            )
            return
        self._json({
            "plan_id": plan_id,
            "filled": plan.filled,
            "slots": spec.crossings,
            "unfilled": [o.error for o in plan.outcomes if o.error],
        })

    def _api_plans_swap(self) -> None:
        """'Reorient tonight' (C5 Q5.5): replace one slot's recipe with a
        household-chosen one. Plan files are the household's own data, so
        the swap rewrites the entry in place and is audited."""
        from nutrime.plans.store import PlanEntry, PlanVault, render_plan_body

        payload = self._read_json_body()
        plan_id = str(payload.get("plan_id") or "")
        recipe_id = str(payload.get("recipe_id") or "")
        try:
            day = int(payload.get("day"))
        except (TypeError, ValueError):
            self._json({"error": "day is required"}, status=400)
            return
        slot = str(payload.get("slot") or "dinner")
        vault = PlanVault(self.server.app.corpus_dir)
        if not plan_id.startswith("pln-") or not vault.exists(plan_id):
            self._json({"error": "That plan doesn't exist any more."}, status=404)
            return
        if not self.server.vault.exists(recipe_id):
            self._json({"error": "That recipe isn't in the collection."}, status=404)
            return
        recipe = self.server.vault.read(recipe_id)
        if recipe.frontmatter.get("vetting_status") in ("quarantined", "duplicate"):
            self._json({"error": "That recipe is hidden by vetting."}, status=400)
            return
        member_id = self._member_or_400()
        if member_id is None:
            return
        plan = vault.read(plan_id)
        entries = list(plan.entries())
        idx = next(
            (i for i, e in enumerate(entries) if e.day == day and e.slot == slot),
            None,
        )
        replaced = PlanEntry(
            day=day, slot=slot, recipe_id=recipe_id,
            title=str(recipe.frontmatter.get("title", "")),
            note="swapped in for tonight",
        )
        previous = entries[idx].recipe_id if idx is not None else None
        if idx is None:
            entries.append(replaced)
        else:
            entries[idx] = replaced
        entries.sort(key=lambda e: (e.day, e.slot))
        fm = dict(plan.frontmatter)
        fm["meals_planned"] = sum(1 for e in entries if e.filled)
        vault.write(plan_id, fm, render_plan_body(entries))
        self.server.app.audit.record_event(
            event_kind="system",
            event_subkind="plan_slot_swapped",
            actor="webui",
            subject_id=member_id,
            payload={"plan_id": plan_id, "day": day, "slot": slot,
                     "from": previous, "to": recipe_id},
        )
        self._json({"swapped": True, "title": replaced.title})

    def _api_tonight_alternatives(self, query: dict[str, list[str]]) -> None:
        """Quick, local, no-model alternatives for tonight within the
        household's constraints — the reorient affordance's candidate list."""
        from dataclasses import replace as _replace

        from nutrime.plans.service import plan_base_filters

        def first(key: str) -> str:
            return (query.get(key) or [""])[0].strip()

        app = self.server.app
        max_time = int(first("max_time")) if first("max_time").isdigit() else None
        filters, _ = plan_base_filters(app, max_time=max_time)
        skip = first("avoid")
        if skip:
            filters = _replace(
                filters,
                exclude_ingredients=filters.exclude_ingredients
                | frozenset(t.strip().lower() for t in skip.split(",") if t.strip()),
            )
        exclude = first("exclude")
        results = [
            r for r in search(self.server.vault, filters, limit=12)
            if r.recipe_id != exclude
        ][:6]
        self._json({
            "results": [
                {
                    "recipe_id": r.recipe_id, "title": r.title,
                    "total_time_min": r.total_time_min,
                    "on_hand_matches": list(r.on_hand_matches),
                    "attribution": r.attribution,
                }
                for r in results
            ]
        })

    # -- consent + derived (profile view, #33) ----------------------------------

    _CONSENT_LABELS = {
        "intake_profile": "Your profile answers",
        "intake_screener": "Screening questions",
        "inventory": "Kitchen inventory",
        "knowledge_derived": "What the app works out from your answers",
        "meal_feedback_time": "Cooking ratings and times",
        "meal_feedback_semantic": "How meals made you feel",
    }

    def _api_consent_list(self) -> None:
        from nutrime.consent import list_current

        app = self.server.app
        member_id = self._member_or_400()
        if member_id is None:
            return
        self._json({
            "decisions": [
                {
                    "category": r.data_category,
                    "label": self._CONSENT_LABELS.get(r.data_category, r.data_category),
                    "purpose": r.purpose,
                    "granted": r.granted,
                    "scope": "own" if r.subject_user == member_id else "household",
                }
                for r in list_current(app.substrate, app.tenant_id, member_id=member_id)
            ]
        })

    def _api_consent_set(self) -> None:
        from nutrime.consent import record_decision

        payload = self._read_json_body()
        app = self.server.app
        member_id = self._member_or_400()
        if member_id is None:
            return
        try:
            record_decision(
                app.substrate, app.tenant_id,
                data_category=str(payload.get("category") or ""),
                purpose=str(payload.get("purpose") or "local_operation"),
                granted=bool(payload.get("granted")),
                note="set from the profile page",
                member_id=member_id,
            )
        except ValueError as err:
            self._json({"error": str(err)}, status=400)
            return
        self._api_consent_list()

    def _api_derived(self) -> None:
        """'Show me what you know' (C5 Q5.5), household level: the
        abstracted constraints every plan and search respects."""
        from nutrime.knowledge.store import list_synthesized_entries

        from nutrime.conditions import household_gates

        app = self.server.app
        entries = list_synthesized_entries(
            app.substrate, app.tenant_id, entry_type="abstracted_constraint"
        )
        gates = household_gates(app.substrate, app.tenant_id)
        self._json({
            "constraints": sorted(
                {str(e.payload.get("abstracted_text", "")) for e in entries} - {""}
            ),
            # Sweep #10: disclosed conditions + the deterministic behavior
            # each one carries, so the household can see the rails.
            "conditions": [
                {
                    "name": c.canonical,
                    "behavior": c.behavior,
                    "note": c.note,
                    "specialties": list(c.specialties),
                }
                for c in gates.conditions
            ],
            "plans_refused": gates.refused,
        })

    # -- notifications + activity (C5 Q5.2 / Q5.4) --------------------------------

    def _notifications_payload(self, member_id: str) -> dict[str, Any]:
        from nutrime.activity import (
            NOTIFICATION_CATEGORIES,
            notification_settings,
            notifications,
        )

        app = self.server.app
        settings = notification_settings(app.substrate, app.tenant_id, member_id)
        return {
            "items": notifications(app, member_id),
            "settings": [
                {"category": cat, "label": meta["label"], "on": settings[cat],
                 "default": meta["default"]}
                for cat, meta in NOTIFICATION_CATEGORIES.items()
            ],
        }

    def _api_notifications(self) -> None:
        member_id = self._member_or_400()
        if member_id is None:
            return
        self._json(self._notifications_payload(member_id))

    def _api_notification_settings(self) -> None:
        from nutrime.activity import set_notification

        payload = self._read_json_body()
        member_id = self._member_or_400()
        if member_id is None:
            return
        try:
            set_notification(
                self.server.app.substrate, self.server.app.tenant_id, member_id,
                str(payload.get("category") or ""), bool(payload.get("on")),
            )
        except ValueError as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json(self._notifications_payload(member_id))

    def _api_activity(self, query: dict[str, list[str]]) -> None:
        from nutrime.activity import activity_feed

        member_id = self._member_or_400()
        if member_id is None:
            return
        raw = (query.get("days") or ["30"])[0]
        days = int(raw) if raw.isdigit() and 1 <= int(raw) <= 365 else 30
        self._json({"days": days, "items": activity_feed(self.server.app, member_id, days=days)})

    # -- periodic check-ins (intake-pattern.md Mode 2) ----------------------------

    def _api_checkin_status(self) -> None:
        from dataclasses import asdict

        from nutrime.checkins import INTERVAL_CHOICES, checkin_history, checkin_status

        member_id = self._member_or_400()
        if member_id is None:
            return
        app = self.server.app
        status = checkin_status(app.substrate, app.tenant_id, member_id)
        self._json({
            **asdict(status),
            "interval_choices": list(INTERVAL_CHOICES),
            "history": checkin_history(app.substrate, app.tenant_id, member_id, limit=6),
        })

    def _api_checkin_questions(self) -> None:
        from nutrime.checkins import checkin_questions, cuisine_options

        member_id = self._member_or_400()
        if member_id is None:
            return
        app = self.server.app
        if getattr(self.server, "_cuisine_options", None) is None:
            self.server._cuisine_options = cuisine_options(self.server.vault)
        self._json(checkin_questions(
            app.substrate, app.tenant_id, member_id,
            cuisine_options=self.server._cuisine_options,
        ))

    def _api_checkin_save(self) -> None:
        from dataclasses import asdict

        from nutrime.checkins import complete_checkin
        from nutrime.consent import ConsentError
        from nutrime.intake.baseline import MVP_INSTRUMENTS
        from nutrime.intake.store import IntakeProfile

        payload = self._read_json_body()
        member_id = self._member_or_400()
        if member_id is None:
            return
        raw = payload.get("profile")
        if not isinstance(raw, dict):
            self._json({"error": "profile required"}, status=400)
            return
        try:
            height, weight = raw.get("height_cm"), raw.get("weight_kg")
            profile = IntakeProfile(
                year_of_birth=int(raw.get("year_of_birth")),
                sex_assigned_at_birth=str(raw.get("sex_assigned_at_birth") or ""),
                life_stage=str(raw.get("life_stage") or ""),
                height_cm=int(height) if height not in (None, "") else None,
                weight_kg=float(weight) if weight not in (None, "") else None,
                dietary_preferences=tuple(
                    str(v).strip() for v in raw.get("dietary_preferences") or [] if str(v).strip()
                ),
                allergens=tuple(
                    str(v).strip() for v in raw.get("allergens") or [] if str(v).strip()
                ),
                conditions=tuple(
                    str(v).strip() for v in raw.get("conditions") or [] if str(v).strip()
                ),
                avoid_foods=tuple(
                    str(v).strip() for v in raw.get("avoid_foods") or [] if str(v).strip()
                ),
            )
            instruments = {i.instrument_id: i for i in MVP_INSTRUMENTS}
            screeners = {}
            for inst_id, answers in (payload.get("screeners") or {}).items():
                inst = instruments.get(inst_id)
                if inst is None or not isinstance(answers, list) or len(answers) != len(inst.items):
                    raise ValueError(f"{inst_id}: answer every question or none")
                screeners[inst_id] = {
                    item.item_id: int(v) for item, v in zip(inst.items, answers)
                }
            conf = payload.get("cooking_confidence")
            mins = payload.get("weeknight_minutes")
            cuisines = payload.get("cuisines")
            app = self.server.app
            result = complete_checkin(
                app.substrate, app.tenant_id, member_id,
                profile=profile, screeners=screeners,
                cooking_confidence=int(conf) if conf not in (None, "") else None,
                weeknight_minutes=int(mins) if mins not in (None, "") else None,
                cuisines_to_try=[str(c) for c in cuisines] if isinstance(cuisines, list) else None,
            )
        except (TypeError, ValueError, ConsentError) as err:
            self._json({"error": str(err)}, status=400)
            return
        self._json(asdict(result))

    def _api_checkin_snooze(self) -> None:
        from nutrime.checkins import snooze

        member_id = self._member_or_400()
        if member_id is None:
            return
        until = snooze(self.server.app.substrate, self.server.app.tenant_id, member_id)
        self._json({"snoozed_until": until})

    def _api_checkin_interval(self) -> None:
        from nutrime.checkins import set_interval

        payload = self._read_json_body()
        member_id = self._member_or_400()
        if member_id is None:
            return
        days = payload.get("days")
        try:
            set_interval(self.server.app.substrate, self.server.app.tenant_id, member_id,
                         int(days) if days not in (None, "") else None)
        except (TypeError, ValueError) as err:
            self._json({"error": str(err)}, status=400)
            return
        self._api_checkin_status()

    def _api_doctor(self) -> None:
        """System check for the Profile page (#34) — the same checks as
        `nutrime doctor`, so nobody has to read logs."""
        from nutrime.maintenance import run_doctor

        checks = run_doctor(self.server.app.data_dir)
        self._json({
            "checks": [
                {"name": c.name, "status": c.status, "detail": c.detail, "fix": c.fix}
                for c in checks
            ]
        })

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

        from nutrime.inventory.store import staples_out

        filters = SearchFilters(
            query=first("q") or None,
            max_total_time_min=max_time,
            on_hand=frozenset(on_hand),
            prefer_terms=frozenset(prefer),
            sources=sources,
            expiring=expiring,
            experience=experience,
            cooked_cuisines=novelty,
            out_of_staples=staples_out(app.substrate, app.tenant_id),
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
                        "missing_ingredients": list(r.missing_ingredients),
                    }
                    for r in results
                ],
                "corpus_count": self.server.vault.count(),
                "phase": phase_note,
                "on_hand_count": len(on_hand),
            }
        )

    # -- API: recipes ------------------------------------------------------------

    _RECIPE_ID = re.compile(r"^rcp-[0-9a-f-]{36}$")

    def _api_recipe_detail(self, recipe_id: str) -> None:
        vault = self.server.vault
        # Shape check before any filesystem touch (defense in depth over
        # the vault's own containment guard).
        if not self._RECIPE_ID.match(recipe_id) or not vault.exists(recipe_id):
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
                        "best_by_date": item.best_by_date,
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
        self._restock_staple(name)
        self._json({"id": item_id, "name": name, "location": location})

    def _restock_staple(self, name: str) -> None:
        """Adding an item that IS an out-of-stock staple restocks it —
        the out flag exists only until the household buys more."""
        from nutrime.inventory.store import set_staple_out, staples_out
        from nutrime.recipes.search import normalize_term

        app = self.server.app
        key = normalize_term(name)
        for out_name in staples_out(app.substrate, app.tenant_id):
            if normalize_term(out_name) == key:
                set_staple_out(app.substrate, app.tenant_id, out_name, False)

    def _api_staples(self) -> None:
        """The assumed-staples shelf: every staple + whether the
        household marked it out of stock."""
        from nutrime.inventory.store import staples_out
        from nutrime.recipes.search import PANTRY_STAPLES

        app = self.server.app
        out = staples_out(app.substrate, app.tenant_id)
        self._json({
            "staples": [
                {"name": name, "out": name in out}
                for name in sorted(PANTRY_STAPLES)
            ]
        })

    def _api_staples_toggle(self) -> None:
        from nutrime.inventory.store import set_staple_out
        from nutrime.recipes.search import PANTRY_STAPLES

        payload = self._read_json_body()
        name = str(payload.get("name") or "").strip().lower()
        if name not in PANTRY_STAPLES:
            self._json({"error": f"not an assumed staple: {name!r}"}, status=400)
            return
        out = bool(payload.get("out"))
        app = self.server.app
        set_staple_out(app.substrate, app.tenant_id, name, out)
        self._json({"name": name, "out": out})

    def _api_inventory_bulk_preview(self) -> None:
        """Paste-a-list step 1: parse + classify, nothing stored yet.

        Two tiers: the deterministic lexicon always answers; items it
        can't settle (unknown foods, preservation-state words like
        "opened"/"cured"/"cut") go through the local model in one
        batched call when Ollama is up. Model down or wrong → the
        lexicon answer stands; a paste never fails on the smart tier.
        """
        from dataclasses import asdict

        from nutrime.inventory.intake import preview
        from nutrime.inventory.llm_classify import needs_llm, refine
        from nutrime.plans.service import local_client

        payload = self._read_json_body()
        text = str(payload.get("text") or "")
        if not text.strip():
            self._json({"error": "paste a list first"}, status=400)
            return
        items = preview(text)
        llm_used = False
        if any(needs_llm(p) for p in items):
            factory = self.server.llm_client_factory or local_client
            client = factory(self.server.app)
            if client is not None:
                refined = refine(items, client)
                llm_used = refined is not items
                items = refined
        self._json({
            "items": [asdict(p) for p in items],
            "llm_refined": llm_used,
        })

    def _api_inventory_bulk_commit(self) -> None:
        """Paste-a-list step 2: store what the user confirmed.

        Each item: {name, location, quantity?, unit?, shelf_days?,
        age_days?, best_by_date?}. An explicit best_by_date wins;
        otherwise shelf_days (+ age_days freshness answer) derives one.
        """
        from nutrime.inventory.intake import best_by_from_freshness

        payload = self._read_json_body()
        raw_items = payload.get("items")
        if not isinstance(raw_items, list) or not raw_items:
            self._json({"error": "items required"}, status=400)
            return
        app = self.server.app
        added = []
        errors = []
        for raw in raw_items:
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name") or "").strip()
            if not name:
                continue
            best_by = str(raw.get("best_by_date") or "").strip() or None
            if best_by is None:
                shelf = raw.get("shelf_days")
                age = raw.get("age_days")
                best_by = best_by_from_freshness(
                    int(shelf) if shelf not in (None, "") else None,
                    int(age) if age not in (None, "") else None,
                )
            try:
                qty = raw.get("quantity")
                item = InventoryItem(
                    name=name,
                    location=str(raw.get("location") or "pantry"),
                    quantity=float(qty) if qty not in (None, "") else None,
                    unit=str(raw.get("unit") or "") or None,
                    best_by_date=best_by,
                )
            except ValueError as err:
                errors.append(f"{name}: {err}")
                continue
            item_id = add_item(app.substrate, app.tenant_id, item)
            self._restock_staple(name)
            added.append({"id": item_id, "name": name,
                          "location": item.location, "best_by_date": best_by})
        app.audit.record_event(
            event_kind="system",
            event_subkind="inventory_bulk_add",
            actor="webui",
            payload={"added": len(added), "errors": len(errors)},
        )
        self._json({"added": added, "errors": errors})

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
            latest = plans[0]  # list_plans is newest-first
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
            "conditions": list(profile.conditions),
            "avoid_foods": list(profile.avoid_foods),
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
        from nutrime.conditions import COMMON_CONDITIONS
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
                    "conditions": list(COMMON_CONDITIONS),
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
                conditions=_str_list("conditions"),
                avoid_foods=_str_list("avoid_foods"),
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

        from nutrime.db import transaction

        # save_member_profile upserts per (tenant, member), so a revision
        # from the Profile link overwrites in place; screener responses
        # append as a new administered_at batch (honest record).
        # One transaction for profile + screeners + derivation: a crash
        # after the profile write used to leave the allergy visible in
        # the profile but silently absent from search and planning
        # (2026-10-06 audit fail-open window).
        with transaction(app.substrate):
            save_member_profile(
                app.substrate, app.tenant_id, member_id, profile
            )
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
            plan_id = plans[0].plan_id  # list_plans is newest-first
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
            # and cross-source duplicates are invisible here too.
            if record.frontmatter.get("vetting_status") in (
                "quarantined", "duplicate"
            ):
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

  /* -- app shell (#33): views + nav; bottom tab bar on phones -- */
  .topRow { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
  .tabs { display: flex; gap: 4px; margin-top: 18px; border-bottom: 1px solid var(--line); }
  .tabs button {
    background: transparent; color: var(--ink-soft); padding: 10px 14px;
    border-radius: 9px 9px 0 0; font-size: 14.5px; border-bottom: 2.5px solid transparent;
  }
  .tabs button[aria-current="page"] { color: var(--ink); border-bottom-color: var(--accent); }
  .tabs button:focus-visible, .quick button:focus-visible { outline: 2px solid var(--leaf); outline-offset: 2px; }
  .tabs .ico { display: none; }
  .view[hidden] { display: none !important; }
  .greet { font-family: "Iowan Old Style", Palatino, Georgia, serif; font-size: clamp(28px, 4.6vw, 42px); line-height: 1.1; font-weight: 500; }
  .greetSub { color: var(--ink-soft); margin-top: 6px; }
  .quick { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; margin-top: 18px; }
  .quick button {
    background: var(--card); color: var(--ink); border: 1px solid var(--line);
    text-align: left; padding: 14px; border-radius: 12px; font-size: 14.5px; min-height: 64px;
  }
  .quick button small { display: block; color: var(--ink-soft); font-weight: 400; font-size: 12.5px; margin-top: 2px; }
  .quick button:hover { border-color: var(--leaf); }
  .dayRow { display: flex; gap: 12px; align-items: baseline; padding: 10px 0; border-bottom: 1px dashed var(--line); flex-wrap: wrap; }
  .dayRow:last-child { border-bottom: none; }
  .dayTag { font-size: 12px; letter-spacing: .12em; text-transform: uppercase; color: var(--ink-soft); font-weight: 600; min-width: 92px; }
  .dayTag.today { color: var(--accent); }
  .dayTitle { flex: 1 1 200px; min-width: 0; }
  .dayTitle .attr { border-top: none; padding-top: 2px; }
  .planItem { display: flex; justify-content: space-between; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--line); align-items: center; flex-wrap: wrap; }
  .formRow { display: flex; gap: 14px; flex-wrap: wrap; align-items: center; margin-top: 10px; }
  .formRow select, .formRow input[type=text] {
    font: inherit; font-size: 14.5px; padding: 8px 10px; border: 1.5px solid var(--line);
    border-radius: 8px; background: #fff; color: var(--ink);
  }
  .groc { list-style: none; }
  .groc li { display: flex; gap: 10px; align-items: flex-start; padding: 9px 0; border-bottom: 1px dashed var(--line); }
  .groc input { width: 20px; height: 20px; accent-color: var(--leaf); margin-top: 2px; flex: none; }
  .groc .done span.food { text-decoration: line-through; color: var(--ink-soft); }
  .groc small { display: block; color: var(--ink-soft); }
  .consentRow { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px dashed var(--line); flex-wrap: wrap; }
  .switch { display: inline-flex; gap: 8px; align-items: center; font-size: 14px; color: var(--ink-soft); }
  .switch input { width: 20px; height: 20px; accent-color: var(--leaf); }
  .scope { font-size: 11.5px; color: var(--ink-soft); border: 1px solid var(--line); border-radius: 999px; padding: 1px 8px; }
  .errorBox { background: #fbeee8; border: 1px solid #e7c3b4; color: #7a2e14; border-radius: 10px; padding: 12px 14px; font-size: 14.5px; margin-top: 10px; }
  .toast.err { background: #8a3417; }
  .bell { position: relative; background: transparent; color: var(--ink); padding: 8px 10px; font-size: 18px; min-height: 40px; }
  .bell .count { position: absolute; top: 2px; right: 0; background: var(--accent); color: var(--accent-ink);
    border-radius: 999px; font-size: 11px; min-width: 18px; height: 18px; line-height: 18px; text-align: center; padding: 0 4px; }
  .notice { display: flex; justify-content: space-between; gap: 10px; align-items: center; padding: 10px 0; border-bottom: 1px dashed var(--line); flex-wrap: wrap; }
  .scale { display: flex; gap: 6px; flex-wrap: wrap; }
  .scale button { background: var(--leaf-soft); color: var(--leaf); padding: 10px 0; width: 48px; border-radius: 10px; }
  .scale button.on { background: var(--leaf); color: #fff; }
  .why { background: var(--leaf-soft); border-radius: 10px; padding: 10px 14px; margin-top: 10px; font-size: 14.5px; }
  .why ul { margin: 6px 0 0 18px; }
  .act { display: flex; gap: 12px; padding: 9px 0; border-bottom: 1px dashed var(--line); font-size: 14.5px; }
  .act time { color: var(--ink-soft); min-width: 92px; font-variant-numeric: tabular-nums; font-size: 13px; }
  .act .k { font-size: 11px; text-transform: uppercase; letter-spacing: .1em; color: var(--ink-soft); min-width: 64px; }
  @media (max-width: 720px) {
    body { padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px)); }
    .tabs {
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 20; margin: 0;
      background: var(--card); border-top: 1px solid var(--line); border-bottom: none;
      justify-content: space-around; padding: 6px 4px calc(6px + env(safe-area-inset-bottom, 0px));
    }
    .tabs button { flex: 1; border-radius: 10px; border-bottom: none; padding: 6px 2px; font-size: 11.5px; display: flex; flex-direction: column; align-items: center; gap: 2px; }
    .tabs button[aria-current="page"] { background: var(--leaf-soft); color: var(--leaf); }
    .tabs .ico { display: block; font-size: 19px; line-height: 1; }
    .toast { bottom: calc(86px + env(safe-area-inset-bottom, 0px)); }
    .whoRow label { display: none; }
  }
</style>
</head>
<body>
<header>
  <div class="topRow">
    <div class="wordmark">NutriMe</div>
    <div class="whoRow">
      <label for="memberPicker">Who's using this?</label>
      <select id="memberPicker" aria-label="Household member"></select>
      <button class="bell" id="bellBtn" aria-label="Notifications">🔔<span class="count" id="bellCount" hidden>0</span></button>
    </div>
  </div>
  <nav class="tabs" aria-label="Sections">
    <button data-view="home"><span class="ico" aria-hidden="true">⌂</span>Home</button>
    <button data-view="recipes"><span class="ico" aria-hidden="true">☰</span>Recipes</button>
    <button data-view="pantry"><span class="ico" aria-hidden="true">◫</span>Pantry</button>
    <button data-view="plans"><span class="ico" aria-hidden="true">▦</span>Plans</button>
    <button data-view="grocery"><span class="ico" aria-hidden="true">✓</span>Grocery</button>
    <button data-view="profile"><span class="ico" aria-hidden="true">◉</span>Profile</button>
  </nav>
</header>

<main>
 <div class="view" id="view-home" data-view="home">
  <div class="greet" id="homeGreet">Hello</div>
  <p class="greetSub" id="homeSub"></p>

  <section class="ask welcome" id="welcomeCard" style="display:none">
    <label class="lbl">Welcome</label>
    <p style="margin-bottom:12px"><span id="welcomeWho">Set up your profile</span> &mdash; 5 minutes,
    stays on this device. It teaches the planner what to avoid and what you love.</p>
    <div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap">
      <button class="btn-go" id="welcomeStart">Set up my profile</button>
      <button class="btn-quiet" id="welcomeSkip">skip for now</button>
    </div>
  </section>

  <section class="ask welcome" id="checkinCard" hidden>
    <label class="lbl">Check-in</label>
    <p style="margin-bottom:12px" id="checkinCardText">Time for your check-in — about 10 minutes.
    Things change; this keeps NutriMe's picture of you current.</p>
    <div style="display:flex;gap:14px;align-items:center;flex-wrap:wrap">
      <button class="btn-go" id="checkinStart">Start check-in</button>
      <button class="btn-quiet" id="checkinSnooze">not now (ask in a week)</button>
    </div>
  </section>

  <section class="ask" id="tonightBox" style="margin-bottom:0">
    <label class="lbl">Tonight</label>
    <div id="tonightBody"></div>
  </section>

  <section class="ask" id="homePlan" hidden>
    <label class="lbl" id="homePlanLabel">Coming up</label>
    <div id="homePlanBody"></div>
  </section>

  <div class="quick" role="group" aria-label="Quick actions">
    <button id="qaReorient">Change tonight's meal<small>less time, missing an ingredient</small></button>
    <button data-go="plans">Plan this week<small>make or browse plans</small></button>
    <button data-go="recipes">Browse recipes<small>search what you have</small></button>
    <button data-go="grocery">Grocery list<small>from the latest plan</small></button>
    <button data-go="profile">What NutriMe knows<small>profile, privacy, avoid-list</small></button>
  </div>
 </div>

 <div class="view" id="view-recipes" data-view="recipes" hidden>
  <h1>What can we make with <em>what we already have?</em></h1>
  <p class="sub">Search the household recipe collection by what's in the kitchen —
  and, if you track a cycle, tilt the ranking toward foods that fit its current phase.</p>

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
    <p class="hint">These count toward "what we already have" when the box above is
      ticked — add or remove items in the <a href="#pantry">Pantry</a> tab.</p>
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
 </div>

 <div class="view" id="view-pantry" data-view="pantry" hidden>
  <h1>What's in <em>the kitchen?</em></h1>
  <p class="sub">The household's running list — fridge, pantry, freezer, countertop.
  Recipe search and meal plans lean on this when "include my kitchen list" is on.</p>

  <section class="ask">
    <label class="lbl" for="pantryPaste">Paste a whole list</label>
    <p class="hint" style="margin:2px 0 8px">Commas, new lines, bullets — any of it.
    NutriMe sorts each item into fridge, pantry, freezer or countertop, and asks
    how fresh the perishable things are so meal plans use them up first.</p>
    <textarea id="pantryPaste" placeholder="chicken thighs, spinach, 2 lemons, brown rice, frozen peas&#10;milk&#10;- sourdough bread"
      style="width:100%;min-height:84px;font-size:14.5px;padding:11px 14px;border:1.5px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);font-family:inherit;resize:vertical"></textarea>
    <div class="haveRow" style="margin-top:8px">
      <button class="btn-go" id="pantryPasteGo">Sort my list</button>
      <span class="hint" id="pantryPasteBusy" hidden>reading the list…</span>
    </div>
    <div id="pantryReview" style="margin-top:14px"></div>
  </section>

  <section class="ask">
    <label class="lbl" for="pantryNewItem">Or add one item</label>
    <div class="haveRow">
      <input type="text" id="pantryNewItem" placeholder="e.g. brown rice" autocomplete="off">
      <select id="pantryNewLoc"
              style="font-size:14.5px;padding:11px 14px;border:1.5px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);font-family:inherit">
        <option value="pantry">pantry</option>
        <option value="fridge">fridge</option>
        <option value="freezer">freezer</option>
        <option value="countertop">countertop</option>
      </select>
      <button class="btn-go" id="pantryAdd">Add</button>
    </div>
  </section>

  <section class="kitchen" id="pantrySections"></section>

  <section class="kitchen">
    <h2 class="serif">Staples shelf</h2>
    <p class="hint">NutriMe assumes these basics are around, so recipes never count
    them as "missing". Out of one? Tap it — recipes that need it will say so until
    you add it back (adding it to the pantry restocks it automatically).</p>
    <div class="pillRow" id="staplePills" style="margin-top:8px"></div>
  </section>
 </div>

 <div class="view" id="view-plans" data-view="plans" hidden>
  <h2 class="serif" style="font-size:30px">Meal plans</h2>
  <section class="ask">
    <label class="lbl">Make a new plan</label>
    <p class="hint">Picks from the collection only, skips everything on the household avoid-list, and favours what's in the kitchen. Runs on this computer's local model.</p>
    <div class="formRow">
      <label class="opt">Days <select id="planDays">
        <option value="3">3</option><option value="5">5</option><option value="7" selected>7</option>
      </select></label>
      <label class="opt"><input type="checkbox" id="slotBreakfast"> breakfast</label>
      <label class="opt"><input type="checkbox" id="slotLunch"> lunch</label>
      <label class="opt"><input type="checkbox" id="slotDinner" checked> dinner</label>
      <label class="opt">ready in <select id="planMaxTime">
        <option value="">any time</option><option value="30">30 min</option>
        <option value="45">45 min</option><option value="60">1 hour</option>
      </select></label>
      <button class="btn-go" id="planGo">Make plan</button>
      <span class="hint" id="planBusy" hidden>planning — one meal at a time…</span>
    </div>
    <div id="planError"></div>
  </section>
  <section class="ask" id="planDetailBox" hidden>
    <label class="lbl" id="planDetailLabel">Plan</label>
    <div id="planDetail"></div>
  </section>
  <section class="ask">
    <label class="lbl">All plans</label>
    <div id="planList"><div class="hint">Loading…</div></div>
  </section>
 </div>

 <div class="view" id="view-activity" data-view="activity" hidden>
  <h2 class="serif" style="font-size:30px">What NutriMe did with your data</h2>
  <section class="ask">
    <div class="formRow"><label class="opt">Show the last <select id="activityDays">
      <option value="7">7 days</option><option value="30" selected>30 days</option><option value="90">90 days</option>
    </select></label></div>
    <div id="activityList"><div class="hint">Loading…</div></div>
  </section>
 </div>

 <div class="view" id="view-grocery" data-view="grocery" hidden>
  <h2 class="serif" style="font-size:30px">Grocery list</h2>
  <section class="ask">
    <div id="groceryBody"><div class="hint">Loading…</div></div>
  </section>
 </div>

 <div class="view" id="view-profile" data-view="profile" hidden>
  <h2 class="serif" style="font-size:30px" id="profileHeading">Profile</h2>
  <section class="ask">
    <label class="lbl">Profile answers</label>
    <p id="profileStatus" class="hint"></p>
    <div class="formRow">
      <button class="btn-go" id="profileLink">Edit my answers</button>
    </div>
  </section>
  <section class="ask">
    <label class="lbl">Check-ins</label>
    <div id="checkinSettings"><div class="hint">Loading…</div></div>
  </section>
  <section class="ask">
    <label class="lbl">What the household avoids and prefers</label>
    <p class="hint">Worked out from everyone's answers. Every search and plan respects it. Only the list is shared, not anyone's answers.</p>
    <div id="derivedBody"></div>
  </section>
  <section class="ask">
    <label class="lbl">Privacy</label>
    <p class="hint">Everything stays on this computer. These switches decide what NutriMe may keep for you; "household" means you're using the household default.</p>
    <div id="consentBody"></div>
  </section>
  <section class="ask">
    <label class="lbl">Household</label>
    <div id="memberAdmin"></div>
  </section>
  <section class="ask">
    <label class="lbl">Notifications</label>
    <p class="hint">What's worth interrupting you for. The defaults are the important ones only.</p>
    <div id="notifySettings"></div>
  </section>
  <section class="ask">
    <label class="lbl">What NutriMe did with your data</label>
    <p class="hint">Every model request, privacy decision, safety check and change, in plain words.</p>
    <div class="formRow"><button class="btn-go" id="openActivity">Show activity</button></div>
  </section>
  <section class="ask">
    <label class="lbl">System check</label>
    <div id="doctorBody"><div class="hint">Checking…</div></div>
  </section>
 </div>
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
// The bootstrap member is literally named "Me" — address it as "you".
function isDefaultName() { return memberName().toLowerCase() === "me"; }
// "Sam's profile" once a household has several people; "Your profile" alone.
function profileLabel() {
  return MEMBERS.length > 1 && memberName() && !isDefaultName() ?
    memberName() + "\\u2019s profile" : "Your profile";
}
// Error surfaces (#33): every API failure says what went wrong in plain
// words; callers still get {error} back to render inline where it fits.
async function jcall(url, opts) {
  let r;
  try { r = await fetch(url, opts); }
  catch (e) {
    const msg = "Can't reach NutriMe on this computer. Is it still running?";
    toast(msg, true);
    return {error: msg};
  }
  let data;
  try { data = await r.json(); } catch (e) { data = {error: "NutriMe sent an unreadable reply (" + r.status + ")."}; }
  if (!r.ok && !data.error) data.error = "Something went wrong (" + r.status + ").";
  if (!r.ok && !(opts && opts.quiet)) toast(data.error, true);
  return data;
}
async function jget(url, quiet) { return jcall(url, {headers: memberHeaders(), quiet}); }
async function jpost(url, body, quiet) {
  return jcall(url, {method: "POST", quiet,
                     headers: memberHeaders({"Content-Type": "application/json"}),
                     body: JSON.stringify(body)});
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
    const got = await formSheet({title: "Add a person", submit: "Add",
      fields: [{id: "name", label: "Their name", placeholder: "e.g. Sam"}],
      validate: o => o.name ? null : "Type a name."});
    const name = got ? got.name : "";
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
  showView(currentView(), true);
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

/* -- kitchen chips (read-only strip on Recipes; managed in Pantry) -- */
async function loadInventory() {
  const data = await jget("/api/inventory");
  const box = $("chips");
  box.innerHTML = "";
  if (!data.items.length) {
    box.innerHTML = '<span class="hint">Nothing tracked yet — add what you have in the Pantry tab.</span>';
    return;
  }
  for (const item of data.items) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.innerHTML = esc(item.name) + ' <span class="loc">' + esc(item.location) + "</span>";
    box.appendChild(chip);
  }
}

/* -- pantry view -- */
const PANTRY_LOCATIONS = ["fridge", "pantry", "freezer", "countertop"];
async function loadStaples() {
  const data = await jget("/api/staples", true);
  const row = $("staplePills");
  if (!row || data.error) return;
  row.innerHTML = "";
  for (const s of data.staples) {
    const b = document.createElement("button");
    b.className = "pill" + (s.out ? "" : " on");
    b.textContent = (s.out ? "✗ " : "✓ ") + s.name;
    b.title = s.out ? "Marked out of stock — tap when restocked" :
      "Assumed on hand — tap if you're out";
    b.onclick = async () => {
      const res = await jpost("/api/staples/toggle", {name: s.name, out: !s.out}, true);
      if (res.error) { toast(res.error); return; }
      loadStaples();
      toast(res.out ? ("Noted — out of " + s.name + ". Recipes needing it will say so.") :
        (s.name + " restocked."));
    };
    row.appendChild(b);
  }
}
async function loadPantry() {
  loadStaples();
  const data = await jget("/api/inventory");
  const box = $("pantrySections");
  box.innerHTML = "";
  if (!data.items.length) {
    box.innerHTML = '<div class="empty">Nothing here yet — add your first item above.</div>';
    return;
  }
  for (const loc of PANTRY_LOCATIONS) {
    const items = data.items.filter(i => i.location === loc);
    if (!items.length) continue;
    const h = document.createElement("h2");
    h.className = "serif";
    h.textContent = loc[0].toUpperCase() + loc.slice(1) + " (" + items.length + ")";
    box.appendChild(h);
    const chips = document.createElement("div");
    chips.className = "chips";
    for (const item of items) {
      const chip = document.createElement("span");
      chip.className = "chip";
      let extra = item.quantity ? esc(String(item.quantity)) +
        (item.unit ? " " + esc(item.unit) : "") : "";
      if (item.best_by_date) {
        const days = Math.round((Date.parse(item.best_by_date) - Date.now()) / 86400000);
        extra += (extra ? " · " : "") + (days < 0 ? "past best-by" :
          days === 0 ? "use today" : days === 1 ? "use by tomorrow" : "use in " + days + "d");
      }
      chip.innerHTML = esc(item.name) + (extra ? ' <span class="loc">' + extra + "</span>" : "");
      const x = document.createElement("button");
      x.textContent = "\\u00d7"; x.title = "Remove " + item.name;
      x.onclick = async () => { await jpost("/api/inventory/remove", {id: item.id});
                                loadPantry(); loadInventory(); };
      chip.appendChild(x);
      chips.appendChild(chip);
    }
    box.appendChild(chips);
  }
}
/* -- bulk paste flow -- */
let PANTRY_PROPOSED = [];
let PANTRY_LLM_REFINED = false;
const FRESH_CHOICES = [
  {label: "fresh today", days: 0},
  {label: "a few days old", days: 3},
  {label: "about a week", days: 7},
  {label: "older", days: 14},
];
$("pantryPasteGo").onclick = async () => {
  const text = $("pantryPaste").value.trim();
  if (!text) { toast("Paste a list first."); return; }
  $("pantryPasteGo").disabled = true; $("pantryPasteBusy").hidden = false;
  const res = await jpost("/api/inventory/bulk/preview", {text}, true);
  $("pantryPasteGo").disabled = false; $("pantryPasteBusy").hidden = true;
  if (res.error) { toast(res.error); return; }
  PANTRY_PROPOSED = res.items.map(p => ({...p, age_days: null, skip: false}));
  PANTRY_LLM_REFINED = !!res.llm_refined;
  renderPantryReview();
};
function renderPantryReview() {
  const box = $("pantryReview");
  if (!PANTRY_PROPOSED.length) { box.innerHTML = ""; return; }
  const locOpts = loc => ["fridge", "pantry", "freezer", "countertop"].map(l =>
    '<option value="' + l + '"' + (l === loc ? " selected" : "") + '>' + l + '</option>').join("");
  const perishables = PANTRY_PROPOSED.filter(p => p.perishable && !p.skip).length;
  box.innerHTML =
    '<div class="hint" style="margin-bottom:8px">' + PANTRY_PROPOSED.filter(p => !p.skip).length +
    ' item(s) found' + (perishables ? " — " + perishables +
    " look perishable; say how fresh they are and plans will use them up first." : ".") +
    (PANTRY_LLM_REFINED ? " The local model helped sort the unusual ones." : "") + '</div>' +
    PANTRY_PROPOSED.map((p, i) => {
      if (p.skip) return "";
      const fresh = p.perishable ?
        '<div class="pillRow" style="margin-top:5px">' + FRESH_CHOICES.map(f =>
          '<button class="pill' + (p.age_days === f.days ? " on" : "") +
          '" data-item="' + i + '" data-age="' + f.days + '">' + f.label + '</button>').join(" ") +
        '</div>' : "";
      return '<div class="consentRow" style="flex-wrap:wrap"><span style="flex:1 1 220px"><b>' +
        esc(p.name) + '</b>' + (p.quantity ? ' <span class="hint">' + esc(String(p.quantity)) +
        (p.unit ? " " + esc(p.unit) : "") + '</span>' : "") +
        (!p.recognized ? ' <span class="hint">(new to me — check the shelf)</span>' : "") +
        fresh + '</span>' +
        '<span><select data-locitem="' + i + '" style="font-size:13px;padding:6px 8px;border:1.5px solid var(--line);border-radius:7px;background:#fff;color:var(--ink)">' +
        locOpts(p.location) + '</select> ' +
        '<button class="btn-quiet" data-skipitem="' + i + '" title="Don\\u2019t add">\\u00d7</button></span></div>';
    }).join("") +
    '<div class="haveRow" style="margin-top:10px"><button class="btn-go" id="pantryCommit">Add ' +
    PANTRY_PROPOSED.filter(p => !p.skip).length + ' item(s)</button>' +
    '<button class="btn-quiet" id="pantryCancelBulk">Cancel</button></div>';
  box.querySelectorAll("[data-age]").forEach(b => b.onclick = () => {
    const p = PANTRY_PROPOSED[parseInt(b.dataset.item)];
    p.age_days = p.age_days === parseInt(b.dataset.age) ? null : parseInt(b.dataset.age);
    renderPantryReview();
  });
  box.querySelectorAll("[data-locitem]").forEach(s => s.onchange = () => {
    PANTRY_PROPOSED[parseInt(s.dataset.locitem)].location = s.value;
  });
  box.querySelectorAll("[data-skipitem]").forEach(b => b.onclick = () => {
    PANTRY_PROPOSED[parseInt(b.dataset.skipitem)].skip = true;
    renderPantryReview();
  });
  const commit = $("pantryCommit");
  if (commit) commit.onclick = async () => {
    const items = PANTRY_PROPOSED.filter(p => !p.skip).map(p => ({
      name: p.name, location: p.location, quantity: p.quantity, unit: p.unit,
      shelf_days: p.shelf_days, age_days: p.age_days,
    }));
    commit.disabled = true;
    const res = await jpost("/api/inventory/bulk", {items}, true);
    if (res.error) { commit.disabled = false; toast(res.error); return; }
    PANTRY_PROPOSED = [];
    $("pantryReview").innerHTML = "";
    $("pantryPaste").value = "";
    const dated = res.added.filter(a => a.best_by_date).length;
    toast("Added " + res.added.length + " item(s)" +
      (dated ? " — " + dated + " with use-by dates for use-it-up planning." : "."));
    loadPantry(); loadInventory();
  };
  const cancel = $("pantryCancelBulk");
  if (cancel) cancel.onclick = () => { PANTRY_PROPOSED = []; renderPantryReview(); };
}

async function pantryAddItem() {
  const name = $("pantryNewItem").value.trim();
  if (!name) return;
  await jpost("/api/inventory", {name, location: $("pantryNewLoc").value});
  $("pantryNewItem").value = "";
  $("pantryNewItem").focus();
  loadPantry(); loadInventory();
}
$("pantryAdd").onclick = pantryAddItem;
$("pantryNewItem").addEventListener("keydown", e => {
  if (e.key === "Enter") pantryAddItem();
});

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
    const missing = r.missing_ingredients || [];
    if (r.on_hand_matches.length && !missing.length) {
      tags += '<span class="tag have" style="font-weight:700">\\u2605 cook tonight \\u2014 nothing to buy</span>';
    } else if (r.on_hand_matches.length && missing.length <= 3) {
      tags += '<span class="tag">needs ' + missing.slice(0, 3).map(esc).join(", ") + '</span>';
    }
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
    WHY[r.recipe_id] = {from: "search", r, constraints: $("applyConstraints").checked};
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
    whyHtml(WHY[id]) +
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
      '<button class="btn-quiet" data-find-soon="' + esc(names) +
      '">find recipes</button></div>'
    );
  }
  if (data.tonight) {
    const t = data.tonight;
    parts.push(
      '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap' +
      (parts.length ? ';margin-top:12px;padding-top:12px;border-top:1px dashed var(--line)' : '') + '">' +
      '<span class="serif" style="font-size:21px">' + esc(t.title) + "</span>" +
      (t.total_time_min ? '<span class="hint">\\u23f1 ' + t.total_time_min + " min</span>" : "") +
      '<button class="btn-quiet" data-view-recipe="' + esc(t.recipe_id) + '">view recipe</button>' +
      '<button class="btn-go" style="padding:9px 16px;min-height:0" data-cooked-recipe="' +
      esc(t.recipe_id) + '" data-cooked-plan="' + esc(t.plan_id) + '">We cooked it</button>' +
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
      '<button class="btn-go" style="padding:9px 16px;min-height:0" data-send-feel="' +
      esc(a.meal_event_id) + '">Save</button></div></div>'
    );
  }
  body.innerHTML = parts.join("");
  // Wire via dataset, never string-interpolated onclick (XSS audit
  // 2026-10-07: esc() is the wrong escape inside a JS string literal).
  body.querySelectorAll("[data-view-recipe]").forEach(b =>
    b.onclick = () => openDetail(b.dataset.viewRecipe));
  body.querySelectorAll("[data-cooked-recipe]").forEach(b =>
    b.onclick = () => markCooked(b.dataset.cookedRecipe, b.dataset.cookedPlan));
  body.querySelectorAll("[data-send-feel]").forEach(b =>
    b.onclick = () => sendFeel(b.dataset.sendFeel));
  body.querySelectorAll("[data-find-soon]").forEach(b =>
    b.onclick = () => { $("have").value = b.dataset.findSoon; doSearch(); });
  box.style.display = "block";
}
async function sendFeel(mealEventId) {
  const text = $("feelText").value.trim();
  if (!text) return;
  const res = await jpost("/api/meals/feel", {meal_event_id: mealEventId, response: text});
  if (!res.error) { toast("Thanks, noted."); loadTonight(); }
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
let INTAKE_MODE = "intake"; // "intake" | "checkin" (periodic revision)
let CHECKIN_Q = null;       // /api/checkin/questions payload

function toast(msg, isError) {
  const t = $("toast");
  t.classList.toggle("err", !!isError);
  t.setAttribute("role", isError ? "alert" : "status");
  t.textContent = msg; t.style.display = "block";
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { t.style.display = "none"; }, 6000);
}

function blankIntakeState() {
  return {
    year_of_birth: "", sex_assigned_at_birth: "", life_stage: "",
    height_cm: "", weight_kg: "",
    allergens: new Set(), dietary_preferences: [], avoid_foods: [], conditions: new Set(),
    screeners: {},  // instrument_id -> [value per item]
    cooking_confidence: null, weeknight_minutes: null, cuisines: new Set(),
  };
}

async function openIntake() {
  INTAKE_MODE = "intake";
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
    INTAKE_STATE.avoid_foods = (p.avoid_foods || []).slice();
    INTAKE_STATE.conditions = new Set(p.conditions || []);
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
  const tag = INTAKE_MODE === "checkin" ?
    (MEMBERS.length > 1 && memberName() && !isDefaultName() ? memberName() + "’s check-in" : "Check-in") :
    profileLabel();
  return '<button class="closeX" onclick="closeIntake()" aria-label="Close">×</button>' +
    '<div class="stepTag">' + esc(tag) + " · step " + INTAKE_STEP + ' of 4</div>' +
    '<h3>' + esc(title) + '</h3>';
}
function intakeNav(backLabel, nextLabel, nextFn) {
  return '<div class="stepNav">' +
    (backLabel ? '<button class="btn-quiet" onclick="intakeBack()">' + esc(backLabel) + '</button>' : '') +
    '<button class="btn-go" id="intakeNext" onclick="' + nextFn + '">' + esc(nextLabel) + '</button>' +
    (INTAKE_MODE === "checkin" ?
      '<button class="btn-quiet" onclick="snoozeCheckin()">not now</button>' :
      '<button class="btn-quiet" onclick="skipIntake()">skip for now</button>') +
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
    const avoidChips = s.avoid_foods.map((a, i) =>
      '<span class="chip">' + esc(a) +
      '<button onclick="removeAvoid(' + i + ')" title="Remove">\\u00d7</button></span>').join(" ");
    const condChips = (INTAKE_Q.profile_fields.conditions || []).map(c => {
      const on = s.conditions.has(c);
      return '<button class="pill' + (on ? ' on' : '') + '" data-condition="' + esc(c) +
        '" onclick="toggleCondition(this)">' + esc(c) + '</button>';
    }).join(" ");
    const condExtras = [...s.conditions]
      .filter(c => !(INTAKE_Q.profile_fields.conditions || []).includes(c))
      .map(c => '<span class="chip">' + esc(c) +
        '<button data-remove-condition="' + esc(c) +
        '" title="Remove">\\u00d7</button></span>').join(" ");
    sheet.innerHTML = intakeHeader("What to avoid, what you enjoy") +
      '<h4 style="margin:4px 0 2px">Never serve \\u2014 hard rules</h4>' +
      '<p class="hint" style="margin:0 0 8px">Recipes with any of these never appear. ' +
      'For everyone\\u2019s meals, not just yours.</p>' +
      '<div class="formRow"><label>Allergens (tap to toggle)</label>' +
      '<div class="pillRow" id="allergenPills">' + chips + '</div></div>' +
      '<div class="formRow"><label>Other foods you won\\u2019t eat (no cilantro, no mushrooms\\u2026)</label>' +
      '<div class="chips" id="avoidChips">' + avoidChips +
      '<span class="chipAdd"><input id="avoidInput" placeholder="add one\\u2026, press Enter"></span></div></div>' +
      '<hr style="border:none;border-top:1.5px solid var(--line);margin:16px 0">' +
      '<h4 style="margin:4px 0 2px">Preferences \\u2014 gentle nudges</h4>' +
      '<p class="hint" style="margin:0 0 8px">These boost matching recipes in search and plans; ' +
      'nothing is excluded because of them.</p>' +
      '<div class="formRow"><label>Ways of eating or foods you love (vegetarian, halal, more fish\\u2026)</label>' +
      '<div class="chips" id="prefChips">' + extras +
      '<span class="chipAdd"><input id="prefInput" placeholder="add one\\u2026, press Enter"></span></div></div>' +
      '<div class="formRow"><label>Health conditions food should respect ' +
      '(optional \\u2014 tap or type)</label>' +
      '<p class="hint" style="margin:2px 0 8px">Some conditions add guard rails to meal ' +
      'plans; a few mean NutriMe steps back and points to the right specialist instead. ' +
      'This stays on this computer like everything else.</p>' +
      '<div class="pillRow" id="conditionPills">' + condChips + '</div>' +
      '<div class="chips" id="condChips">' + condExtras +
      '<span class="chipAdd"><input id="condInput" placeholder="add one\\u2026, press Enter"></span></div></div>' +
      intakeNav("back", "Next: three quick check-ins", "intakeStep2Next()");
    $("prefInput").addEventListener("keydown", e => {
      if (e.key === "Enter" && e.target.value.trim()) {
        INTAKE_STATE.dietary_preferences.push(e.target.value.trim());
        renderIntakeStep();
        $("prefInput").focus();
      }
    });
    $("avoidInput").addEventListener("keydown", e => {
      if (e.key === "Enter" && e.target.value.trim()) {
        INTAKE_STATE.avoid_foods.push(e.target.value.trim());
        renderIntakeStep();
        $("avoidInput").focus();
      }
    });
    sheet.querySelectorAll("[data-remove-condition]").forEach(b =>
      b.onclick = () => removeCondition(b.dataset.removeCondition));
    $("condInput").addEventListener("keydown", e => {
      if (e.key === "Enter" && e.target.value.trim()) {
        INTAKE_STATE.conditions.add(e.target.value.trim());
        renderIntakeStep();
        $("condInput").focus();
      }
    });
  } else if (INTAKE_STEP === 3) {
    let html = intakeHeader("Three quick check-ins") +
      '<p class="hint" style="margin-top:6px">These are screening questions, not a diagnosis ' +
      '\\u2014 they help the planner notice when food support matters most. Optional: leave any blank.</p>';
    for (const inst of INTAKE_Q.instruments) {
      const last = INTAKE_MODE === "checkin" && CHECKIN_Q ? CHECKIN_Q.last_scores[inst.instrument_id] : null;
      html += '<h4>' + esc(inst.full_name) + '</h4>' +
        (last ? '<div class="hint">Last time (' + esc(String(last.administered_at).slice(0, 10)) +
          '): score ' + last.score + (last.positive ? ", worth watching" : "") + '</div>' : "");
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
    sheet.innerHTML = html + intakeNav("back",
      INTAKE_MODE === "checkin" ? "Next: cooking and cuisines" : "Next: privacy", "intakeStep3Next()");
  } else if (INTAKE_MODE === "checkin") {
    const q = CHECKIN_Q;
    const conf = q.cooking_confidence.options.map(o =>
      '<label><input type="radio" name="ciConf" value="' + o.value + '"' +
      (s.cooking_confidence === o.value ? " checked" : "") + '> ' + esc(o.label) + '</label>').join("");
    const mins = '<option value="">not sure</option>' + q.weeknight_minutes.options.map(m =>
      '<option value="' + m + '"' + (s.weeknight_minutes === m ? " selected" : "") + '>' +
      (m >= 90 ? "90 minutes or more" : m + " minutes") + '</option>').join("");
    const cuisines = q.cuisines.options.map(c =>
      '<button class="pill' + (s.cuisines.has(c) ? " on" : "") + '" data-cuisine="' + esc(c) + '">' +
      esc(c) + '</button>').join(" ");
    sheet.innerHTML = intakeHeader("Cooking and cuisines") +
      '<div class="formRow"><label>How do you feel about cooking these days?</label>' +
      '<div class="qOpts" style="flex-direction:column;align-items:flex-start">' + conf + '</div></div>' +
      '<div class="formRow"><label for="ciMins">On a weeknight, how long do you usually have to cook?</label>' +
      '<select id="ciMins">' + mins + '</select></div>' +
      '<div class="formRow"><label>Cuisines you’d like to try more of (tap to toggle)</label>' +
      '<div class="pillRow" id="ciCuisines">' + cuisines + '</div></div>' +
      '<p class="hint">Everything stays on this computer.</p>' +
      intakeNav("back", "Save check-in", "saveCheckin()");
    sheet.querySelectorAll("#ciCuisines .pill").forEach(b => b.onclick = () => {
      const c = b.dataset.cuisine;
      s.cuisines.has(c) ? s.cuisines.delete(c) : s.cuisines.add(c);
      b.classList.toggle("on");
    });
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
function removeAvoid(i) {
  INTAKE_STATE.avoid_foods.splice(i, 1);
  renderIntakeStep();
}
function toggleCondition(btn) {
  const c = btn.dataset.condition;
  if (INTAKE_STATE.conditions.has(c)) INTAKE_STATE.conditions.delete(c);
  else INTAKE_STATE.conditions.add(c);
  btn.classList.toggle("on");
}
function removeCondition(c) {
  INTAKE_STATE.conditions.delete(c);
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
      avoid_foods: s.avoid_foods,
      conditions: [...s.conditions],
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

/* -- in-page forms (no browser pop-ups; they are clumsy on phones) -- */
// fields: {id, label, type: "text"|"number"|"scale"|"checks", value, options, placeholder}
function formSheet(spec) {
  return new Promise(resolve => {
    const body = spec.fields.map(f => {
      if (f.type === "scale") {
        return '<div class="formRow"><label>' + esc(f.label) + '</label><div class="scale" data-scale="' + f.id + '">' +
          [1, 2, 3, 4, 5].map(n => '<button type="button" data-v="' + n + '"' + (f.value === n ? ' class="on"' : "") + ">" + n + "</button>").join("") +
          "</div>" + (f.hint ? '<div class="hint">' + esc(f.hint) + "</div>" : "") + "</div>";
      }
      if (f.type === "checks") {
        return '<div class="formRow"><label>' + esc(f.label) + "</label>" + f.options.map((o, i) =>
          '<label class="opt"><input type="checkbox" data-check="' + f.id + '" value="' + esc(o) + '" checked> ' + esc(o) + "</label>").join("") + "</div>";
      }
      return '<div class="formRow"><label for="fs_' + f.id + '">' + esc(f.label) + "</label>" +
        '<input type="' + (f.type || "text") + '" id="fs_' + f.id + '" value="' + esc(f.value == null ? "" : f.value) + '"' +
        (f.placeholder ? ' placeholder="' + esc(f.placeholder) + '"' : "") + "></div>";
    }).join("");
    $("sheet").innerHTML =
      '<button class="closeX" id="fsClose" aria-label="Close">×</button><h3>' + esc(spec.title) + "</h3>" +
      (spec.intro ? '<p class="hint">' + esc(spec.intro) + "</p>" : "") + body +
      '<div class="intakeMsg" id="fsMsg"></div><div class="stepNav">' +
      '<button class="btn-go" id="fsOk">' + esc(spec.submit || "Save") + "</button>" +
      '<button class="btn-quiet" id="fsCancel">' + esc(spec.cancel || "Cancel") + "</button></div>";
    $("sheet").querySelectorAll("[data-scale] button").forEach(b => b.onclick = () => {
      b.parentNode.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b));
    });
    const done = val => { $("overlay").classList.remove("on"); resolve(val); };
    $("fsClose").onclick = () => done(null);
    $("fsCancel").onclick = () => done(spec.cancelValue === undefined ? null : spec.cancelValue);
    $("fsOk").onclick = () => {
      const out = {};
      spec.fields.forEach(f => {
        if (f.type === "scale") {
          const on = $("sheet").querySelector('[data-scale="' + f.id + '"] button.on');
          out[f.id] = on ? parseInt(on.dataset.v) : null;
        } else if (f.type === "checks") {
          out[f.id] = [...$("sheet").querySelectorAll('input[data-check="' + f.id + '"]:checked')].map(x => x.value);
        } else {
          out[f.id] = $("fs_" + f.id).value.trim();
        }
      });
      const err = spec.validate ? spec.validate(out) : null;
      if (err) { $("fsMsg").textContent = err; return; }
      done(out);
    };
    $("overlay").classList.add("on");
    const first = $("sheet").querySelector("input");
    if (first && first.type !== "checkbox") first.focus();
  });
}

async function markCooked(recipeId, planId) {
  const v = await formSheet({
    title: "How did it go?", submit: "Save", intro: "All optional; it teaches NutriMe what works for you.",
    fields: [
      {id: "ease", label: "How easy was it to make?", type: "scale", hint: "1 = hard, 5 = easy"},
      {id: "enjoyment", label: "How enjoyable was it to make?", type: "scale", hint: "1 = a chore, 5 = loved it"},
      {id: "minutes", label: "How many minutes did it actually take?", type: "number", placeholder: "e.g. 35"},
    ],
    validate: o => (o.ease && !o.enjoyment) || (!o.ease && o.enjoyment) ?
      "Pick both ratings, or neither." : null,
  });
  if (v === null) return;
  const payload = {recipe_id: recipeId, plan_id: planId};
  if (v.ease && v.enjoyment) { payload.ease = v.ease; payload.enjoyment = v.enjoyment; }
  if (v.minutes) payload.actual_minutes = parseInt(v.minutes);
  const res = await jpost("/api/meals/cooked", payload);
  if (res.error) return;
  // V2 ask-don't-assume decrement: offer the recipe∩inventory names.
  if (res.used_candidates && res.used_candidates.length) {
    const used = await formSheet({
      title: "Used up anything?", submit: "Remove ticked items", cancel: "Keep everything",
      intro: "Ticked items come off your kitchen list.",
      fields: [{id: "names", label: "From the kitchen", type: "checks", options: res.used_candidates}],
    });
    if (used && used.names.length) {
      await jpost("/api/meals/cooked/used-up", {meal_event_id: res.meal_event_id, names: used.names});
      loadInventory();
    }
  }
  toast("Saved. Later, tell NutriMe how it made you feel.");
  loadTonight();
}

/* -- why this? (C5 Q5.4 inline drill-in) -- */
const WHY = {};   // recipe_id → context from wherever it was shown
let AVOID_COUNT = null;
function whyHtml(ctx) {
  if (!ctx) return "";
  const r = ctx.r || {}, lines = [];
  if (r.on_hand_matches && r.on_hand_matches.length) lines.push("Uses what you have: " + r.on_hand_matches.join(", "));
  if (r.expiring_matches && r.expiring_matches.length) lines.push("Uses up food that’s due soon: " + r.expiring_matches.join(", "));
  if (r.prefer_matches && r.prefer_matches.length) lines.push("Matches household preferences: " + r.prefer_matches.join(", "));
  if (r.times_cooked) lines.push("You’ve cooked it " + r.times_cooked + " time" + (r.times_cooked > 1 ? "s" : "") +
    (r.avg_enjoyment ? ", enjoyment " + r.avg_enjoyment + "/5" : ""));
  if (r.novel_cuisine) lines.push("A cuisine the household hasn’t cooked yet");
  if (ctx.note) lines.push("Planner’s note: " + ctx.note);
  if (ctx.constraints !== false && AVOID_COUNT) lines.push("Checked against the household avoid/prefer list (" + AVOID_COUNT + " item" + (AVOID_COUNT > 1 ? "s" : "") + ")");
  if (!lines.length) lines.push(ctx.from === "search" ? "It matched your search." : "It fits the plan’s limits.");
  return '<div class="why"><b>Why this?</b><ul>' + lines.map(l => "<li>" + esc(l) + "</li>").join("") + "</ul></div>";
}

/* -- notifications (C5 Q5.2) -- */
function dismissedSet() {
  try { return new Set(JSON.parse(localStorage.getItem("nutrime.dismissed." + MEMBER) || "[]")); }
  catch (e) { return new Set(); }
}
function saveDismissed(set) {
  try { localStorage.setItem("nutrime.dismissed." + MEMBER, JSON.stringify([...set].slice(-200))); } catch (e) {}
}
let NOTICES = [];
async function loadNotifications() {
  const data = await jget("/api/notifications", true);
  if (data.error) return;
  const dismissed = dismissedSet();
  NOTICES = data.items.filter(n => !dismissed.has(n.key));
  $("bellCount").textContent = NOTICES.length;
  $("bellCount").hidden = NOTICES.length === 0;
  return data;
}
function openNotifications() {
  const rows = NOTICES.length ? NOTICES.map((n, i) =>
    '<div class="notice"><span>' + esc(n.text) + '</span><span>' +
    '<button class="btn-quiet" data-go-notice="' + i + '">open</button>' +
    '<button class="btn-quiet" data-dismiss="' + i + '">dismiss</button></span></div>').join("") :
    '<div class="empty">Nothing needs you right now.</div>';
  $("sheet").innerHTML = '<button class="closeX" onclick="closeDetail()" aria-label="Close">×</button>' +
    "<h3>Notifications</h3>" + rows +
    '<p class="hint" style="margin-top:12px">Choose what shows here under Profile → Notifications.</p>';
  $("sheet").querySelectorAll("[data-dismiss]").forEach(b => b.onclick = () => {
    const set = dismissedSet(); set.add(NOTICES[+b.dataset.dismiss].key); saveDismissed(set);
    loadNotifications().then(openNotifications);
  });
  $("sheet").querySelectorAll("[data-go-notice]").forEach(b => b.onclick = () => {
    const n = NOTICES[+b.dataset.goNotice];
    closeDetail();
    if (n.action === "checkin") openCheckin(); else showView(n.action);
  });
  $("overlay").classList.add("on");
}
$("bellBtn").onclick = () => loadNotifications().then(openNotifications);
async function loadNotifySettings() {
  const data = await loadNotifications();
  if (!data) return;
  $("notifySettings").innerHTML = data.settings.map(s =>
    '<div class="consentRow"><span>' + esc(s.label) + "</span>" +
    '<label class="switch"><input type="checkbox" data-notify="' + s.category + '"' + (s.on ? " checked" : "") +
    "> " + (s.on ? "on" : "off") + "</label></div>").join("");
  $("notifySettings").querySelectorAll("input[data-notify]").forEach(cb => cb.onchange = async () => {
    const res = await jpost("/api/notifications/settings", {category: cb.dataset.notify, on: cb.checked});
    if (!res.error) { toast("Saved."); loadNotifySettings(); }
  });
}

/* -- activity (C5 Q5.4 dedicated audit view) -- */
async function loadActivity() {
  const data = await jget("/api/activity?days=" + $("activityDays").value);
  const box = $("activityList");
  if (data.error) { box.innerHTML = '<div class="errorBox">' + esc(data.error) + "</div>"; return; }
  box.innerHTML = data.items.length ? data.items.map(i =>
    '<div class="act"><time>' + esc(String(i.at).slice(0, 16).replace("T", " ")) + '</time><span class="k">' +
    esc(i.kind) + "</span><span>" + esc(i.text) + "</span></div>").join("") :
    '<div class="empty">Nothing in this period.</div>';
}
$("activityDays").onchange = loadActivity;
$("openActivity").onclick = () => showView("activity");

/* -- periodic check-ins (intake-pattern.md Mode 2) -- */
async function openCheckin() {
  if (!INTAKE_Q) INTAKE_Q = await jget("/api/intake/questions");
  CHECKIN_Q = await jget("/api/checkin/questions");
  if (CHECKIN_Q.error || !CHECKIN_Q.profile) {
    toast("Fill in your profile first; check-ins revise it.");
    return openIntake();
  }
  INTAKE_MODE = "checkin";
  const s = INTAKE_STATE = blankIntakeState();
  const p = CHECKIN_Q.profile;
  s.year_of_birth = p.year_of_birth;
  s.sex_assigned_at_birth = p.sex_assigned_at_birth;
  s.life_stage = p.life_stage;
  s.height_cm = p.height_cm == null ? "" : p.height_cm;
  s.weight_kg = p.weight_kg == null ? "" : p.weight_kg;
  s.allergens = new Set(p.allergens);
  s.dietary_preferences = p.dietary_preferences.slice();
  s.avoid_foods = (p.avoid_foods || []).slice();
  s.conditions = new Set(p.conditions || []);
  s.cooking_confidence = CHECKIN_Q.cooking_confidence.current;
  s.weeknight_minutes = CHECKIN_Q.weeknight_minutes.current;
  s.cuisines = new Set(CHECKIN_Q.cuisines.current);
  INTAKE_STEP = 1;
  renderIntakeStep();
  $("intakeOverlay").classList.add("on");
}
async function saveCheckin() {
  const s = INTAKE_STATE;
  const conf = document.querySelector('input[name="ciConf"]:checked');
  s.cooking_confidence = conf ? parseInt(conf.value) : null;
  s.weeknight_minutes = $("ciMins").value ? parseInt($("ciMins").value) : null;
  $("intakeNext").disabled = true;
  const res = await jpost("/api/checkin", {
    profile: {
      year_of_birth: parseInt(s.year_of_birth),
      sex_assigned_at_birth: s.sex_assigned_at_birth,
      life_stage: s.life_stage,
      height_cm: s.height_cm === "" ? null : parseInt(s.height_cm),
      weight_kg: s.weight_kg === "" ? null : parseFloat(s.weight_kg),
      allergens: [...s.allergens],
      dietary_preferences: s.dietary_preferences,
      avoid_foods: s.avoid_foods,
      conditions: [...s.conditions],
    },
    screeners: s.screeners,
    cooking_confidence: s.cooking_confidence,
    weeknight_minutes: s.weeknight_minutes,
    cuisines: [...s.cuisines],
  }, true);
  if (res.error) {
    $("intakeNext").disabled = false;
    $("intakeMsg").textContent = res.error;
    return;
  }
  const changes = res.changes.length ?
    "<ul>" + res.changes.map(c => "<li>" + esc(c) + "</li>").join("") + "</ul>" :
    '<p>Nothing changed. Your profile is still current.</p>';
  const scr = res.screener_changes.map(c =>
    "<li>" + esc(c.name) + ": " + (c.previous == null ? "" : c.previous + " → ") + c.now +
    (c.positive ? " (worth mentioning to a doctor or dietitian)" : "") + "</li>").join("");
  $("intakeSheet").innerHTML =
    '<button class="closeX" onclick="closeIntake()" aria-label="Close">×</button>' +
    "<h3>Check-in saved</h3>" + changes +
    (scr ? "<h4>Screening questions</h4><ul>" + scr + "</ul>" : "") +
    (res.constraints_added || res.constraints_retracted ?
      '<p class="hint">Household avoid/prefer list: ' + res.constraints_added + " added, " +
      res.constraints_retracted + " removed.</p>" : "") +
    '<p class="hint">Next check-in around ' + esc(String(res.next_due_at).slice(0, 10)) + ".</p>" +
    '<div class="stepNav"><button class="btn-go" onclick="closeIntake()">Done</button></div>';
  $("checkinCard").hidden = true;
  doSearch();
  if (currentView() === "profile") loadProfile();
}
async function snoozeCheckin() {
  const res = await jpost("/api/checkin/snooze", {});
  if (res.error) return;
  closeIntake();
  $("checkinCard").hidden = true;
  toast("OK. NutriMe will ask again in a week.");
}
async function loadCheckinCard() {
  const st = await jget("/api/checkin/status", true);
  $("checkinCard").hidden = !(st && st.due);
  if (st && st.due && st.last_at) {
    $("checkinCardText").textContent = "Time for your check-in, about 10 minutes. It’s been " +
      Math.max(1, Math.round((Date.now() - Date.parse(st.last_at)) / 86400000)) +
      " days; things change, and this keeps NutriMe’s picture of you current.";
  }
}
async function loadCheckinSettings() {
  const st = await jget("/api/checkin/status", true);
  const box = $("checkinSettings");
  if (st.error) { box.innerHTML = '<div class="errorBox">' + esc(st.error) + "</div>"; return; }
  if (!st.has_profile) { box.innerHTML = '<p class="hint">Check-ins start once your profile is filled in.</p>'; return; }
  const label = d => d % 7 === 0 ? "every " + (d / 7) + " weeks" : "every " + d + " days";
  const sourceNote = st.interval_source === "life_stage" ?
    " (more often during pregnancy and breastfeeding, when needs change quickly)" : "";
  const opts = '<option value="">default</option>' + st.interval_choices.map(d =>
    '<option value="' + d + '"' + (st.interval_source === "custom" && st.interval_days === d ? " selected" : "") +
    ">" + label(d) + "</option>").join("");
  const hist = st.history.length ? "<ul>" + st.history.map(h =>
    "<li>" + esc(String(h.completed_at).slice(0, 10)) + ": " +
    esc((h.changes || []).join("; ") || "no changes") + "</li>").join("") + "</ul>" :
    '<p class="hint">No check-ins yet.</p>';
  box.innerHTML =
    '<p class="hint">' + (st.due ? "A check-in is due now." :
      "Next check-in around " + esc(String(st.due_at).slice(0, 10)) + ".") +
    " Currently " + label(st.interval_days) + sourceNote + ".</p>" +
    '<div class="formRow"><label class="opt">How often <select id="ciInterval">' + opts + "</select></label>" +
    '<button class="btn-go" id="ciNow">Check in now</button></div>' + hist;
  $("ciInterval").onchange = async () => {
    const res = await jpost("/api/checkin/interval", {days: $("ciInterval").value || null});
    if (!res.error) { toast("Saved."); loadCheckinSettings(); }
  };
  $("ciNow").onclick = openCheckin;
}
$("checkinStart").onclick = openCheckin;
$("checkinSnooze").onclick = snoozeCheckin;

/* -- app shell (#33): views, adaptive home, plans, grocery, profile -- */
const VIEWS = ["home", "recipes", "pantry", "plans", "grocery", "profile", "activity"];
function currentView() {
  const h = (location.hash || "").replace("#", "");
  return VIEWS.includes(h) ? h : "home";
}
const LOADERS = {
  home: loadHome, recipes: () => {}, pantry: loadPantry, plans: loadPlans,
  grocery: loadGrocery, profile: loadProfile, activity: loadActivity,
};
function showView(name, reload) {
  $("overlay").classList.remove("on");  // a section change closes any open sheet
  document.querySelectorAll(".view").forEach(v => { v.hidden = v.dataset.view !== name; });
  document.querySelectorAll(".tabs button").forEach(b => {
    if (b.dataset.view === name) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
  if (location.hash.replace("#", "") !== name) history.replaceState(null, "", "#" + name);
  LOADERS[name]();
  if (!reload) window.scrollTo(0, 0);
}
document.querySelectorAll(".tabs button, .quick button[data-go]").forEach(b =>
  b.addEventListener("click", () => showView(b.dataset.view || b.dataset.go)));
window.addEventListener("hashchange", () => showView(currentView()));

function dayLabel(day, today) {
  if (day === today) return "Today";
  if (day === today + 1) return "Tomorrow";
  if (day === today - 1) return "Yesterday";
  return "Day " + day;
}
async function latestPlan() {
  const list = await jget("/api/plans", true);
  if (!list.plans || !list.plans.length) return null;
  return jget("/api/plans/" + list.plans[0].plan_id, true);
}

// C5 Q5.1: the home surface follows the time of day.
async function loadHome() {
  loadCheckinCard();
  loadNotifications();
  jget("/api/derived", true).then(d => { AVOID_COUNT = (d.constraints || []).length; });
  const hour = new Date().getHours();
  const who = MEMBERS.length > 1 && memberName() && !isDefaultName() ? ", " + memberName() : "";
  let greet, sub, show;
  if (hour < 5) { greet = "Late night" + who; sub = "Here's what's coming up tomorrow."; show = "tomorrow"; }
  else if (hour < 11) { greet = "Good morning" + who; sub = "Tonight's meal, and what's planned for tomorrow."; show = "tomorrow"; }
  else if (hour < 17) { greet = "Good afternoon" + who; sub = "Tonight's meal first. Change it if the day's gone sideways."; show = "none"; }
  else if (hour < 21) { greet = "Good evening" + who; sub = "Cooked already? Tell NutriMe how it went."; show = "none"; }
  else { greet = "Good evening" + who; sub = "How did tonight go? Tomorrow is below."; show = "tomorrow"; }
  $("homeGreet").textContent = greet;
  $("homeSub").textContent = sub;
  const box = $("homePlan");
  if (show === "none") { box.hidden = true; return; }
  const plan = await latestPlan();
  if (!plan || plan.error) { box.hidden = true; return; }
  const want = show === "tomorrow" ? [plan.today_day + 1] : [plan.today_day, plan.today_day + 1];
  const rows = plan.entries.filter(e => want.includes(e.day));
  if (!rows.length) { box.hidden = true; return; }
  $("homePlanLabel").textContent = show === "tomorrow" ? "Tomorrow" : "Today and tomorrow";
  $("homePlanBody").innerHTML = rows.map(e => planRow(e, plan.today_day, false)).join("");
  wirePlanRows($("homePlanBody"));
  box.hidden = false;
}

function wirePlanRows(container) {
  container.querySelectorAll("[data-open-recipe]").forEach(b =>
    b.onclick = () => openDetail(b.dataset.openRecipe));
}
function planRow(e, today, withActions) {
  if (e.recipe_id) WHY[e.recipe_id] = {from: "plan", note: e.note};
  const title = e.recipe_id ?
    '<button class="btn-quiet" style="padding:0;text-align:left" data-open-recipe="' +
      esc(e.recipe_id) + '">' + esc(e.title) + "</button>" :
    '<span class="hint">' + esc(e.note || "no recipe") + "</span>";
  return '<div class="dayRow"><span class="dayTag' + (e.day === today ? " today" : "") + '">' +
    esc(dayLabel(e.day, today)) + " · " + esc(e.slot) + '</span><div class="dayTitle">' + title +
    (e.total_time_min ? ' <span class="hint">' + e.total_time_min + " min</span>" : "") +
    (e.recipe_id && e.note ? '<div class="hint">' + esc(e.note) + "</div>" : "") +
    (e.attribution ? '<div class="attr">' + esc(e.attribution) + "</div>" : "") + "</div></div>";
}

/* -- reorient tonight (C5 Q5.5) -- */
let REORIENT = null;
async function openReorient() {
  const t = await jget("/api/tonight", true);
  REORIENT = t && t.tonight ? t.tonight : null;
  const plans = await jget("/api/plans", true);
  if (!REORIENT && !(plans.plans && plans.plans.length)) {
    toast("There's no plan yet, so there's nothing to change. Make one under Plans.");
    showView("plans");
    return;
  }
  $("sheet").innerHTML =
    '<button class="closeX" onclick="closeDetail()" aria-label="Close">×</button>' +
    "<h3>Change tonight's meal</h3>" +
    '<p class="hint">' + (REORIENT ? "Planned: " + esc(REORIENT.title) + ". " : "") +
    "Options stay within the household avoid-list and favour what's in the kitchen.</p>" +
    '<div class="formRow">' +
    '<label class="opt">I have <select id="roTime"><option value="">any time</option>' +
    '<option value="20">20 min</option><option value="30">30 min</option><option value="45">45 min</option></select></label>' +
    '<label class="opt">skip <input type="text" id="roAvoid" placeholder="e.g. mushrooms" style="width:150px"></label>' +
    '<button class="btn-go" id="roGo">Show options</button></div>' +
    '<div id="roResults" style="margin-top:12px"></div>';
  $("roGo").onclick = loadReorientOptions;
  $("overlay").classList.add("on");
  loadReorientOptions();
}
async function loadReorientOptions() {
  const params = new URLSearchParams();
  if ($("roTime").value) params.set("max_time", $("roTime").value);
  if ($("roAvoid").value.trim()) params.set("avoid", $("roAvoid").value.trim());
  if (REORIENT) params.set("exclude", REORIENT.recipe_id);
  const data = await jget("/api/tonight/alternatives?" + params.toString());
  const box = $("roResults");
  if (data.error) { box.innerHTML = '<div class="errorBox">' + esc(data.error) + "</div>"; return; }
  if (!data.results.length) { box.innerHTML = '<div class="empty">Nothing fits those limits. Try more time or skip fewer ingredients.</div>'; return; }
  data.results.forEach(r => { WHY[r.recipe_id] = {from: "reorient", r}; });
  box.innerHTML = data.results.map(r =>
    '<div class="planItem"><div style="min-width:0;flex:1 1 220px"><b>' + esc(r.title) + "</b>" +
    (r.total_time_min ? ' <span class="hint">' + r.total_time_min + " min</span>" : "") +
    (r.on_hand_matches.length ? '<div class="hint">uses ' + esc(r.on_hand_matches.join(", ")) + "</div>" : "") +
    '<div class="attr">' + esc(r.attribution) + "</div></div>" +
    (REORIENT ? '<button class="btn-go" style="min-height:0;padding:9px 14px" data-swap-recipe="' +
      esc(r.recipe_id) + '">Cook this instead</button>' :
      '<button class="btn-quiet" data-open-recipe="' + esc(r.recipe_id) + '">view</button>') +
    "</div>").join("");
  box.querySelectorAll("[data-swap-recipe]").forEach(b =>
    b.onclick = () => swapTonight(b.dataset.swapRecipe));
  wirePlanRows(box);
}
async function swapTonight(recipeId) {
  const res = await jpost("/api/plans/swap", {
    plan_id: REORIENT.plan_id, day: REORIENT.day, slot: REORIENT.slot, recipe_id: recipeId});
  if (res.error) return;
  closeDetail();
  toast("Tonight is now " + res.title + ".");
  loadTonight(); loadHome();
}
$("qaReorient").onclick = openReorient;

/* -- plans -- */
async function loadPlans() {
  const list = await jget("/api/plans");
  const box = $("planList");
  if (list.error) { box.innerHTML = '<div class="errorBox">' + esc(list.error) + "</div>"; return; }
  if (!list.plans.length) { box.innerHTML = '<div class="empty">No plans yet. Make one above.</div>'; $("planDetailBox").hidden = true; return; }
  box.innerHTML = list.plans.map(pl =>
    '<div class="planItem"><span>' + esc(String(pl.created_at || "").slice(0, 10)) + " · " +
    esc(pl.days) + " days · " + esc(pl.meals_planned) + " meals</span>" +
    '<button class="btn-quiet" data-show-plan="' + esc(pl.plan_id) + '">open</button></div>').join("");
  box.querySelectorAll("[data-show-plan]").forEach(b =>
    b.onclick = () => showPlan(b.dataset.showPlan));
  showPlan(list.plans[0].plan_id);
}
async function showPlan(planId) {
  const plan = await jget("/api/plans/" + planId);
  if (plan.error) return;
  $("planDetailLabel").textContent = "Plan from " + String(plan.created_at || "").slice(0, 10);
  $("planDetail").innerHTML = plan.entries.map(e => planRow(e, plan.today_day, true)).join("") ||
    '<div class="hint">This plan has no meals.</div>';
  wirePlanRows($("planDetail"));
  $("planDetailBox").hidden = false;
}
$("planGo").onclick = async () => {
  const slots = [["slotBreakfast", "breakfast"], ["slotLunch", "lunch"], ["slotDinner", "dinner"]]
    .filter(([id]) => $(id).checked).map(([, s]) => s);
  $("planError").innerHTML = "";
  if (!slots.length) { $("planError").innerHTML = '<div class="errorBox">Pick at least one meal.</div>'; return; }
  $("planGo").disabled = true; $("planBusy").hidden = false;
  const res = await jpost("/api/plans/generate", {
    days: parseInt($("planDays").value), slots,
    max_time: $("planMaxTime").value ? parseInt($("planMaxTime").value) : null}, true);
  $("planGo").disabled = false; $("planBusy").hidden = true;
  if (res.error) { $("planError").innerHTML = '<div class="errorBox">' + esc(res.error) + "</div>"; return; }
  toast("Planned " + res.filled + " of " + res.slots + " meals.");
  loadPlans(); loadTonight();
};

/* -- grocery -- */
function groceryChecked(planId) {
  try { return new Set(JSON.parse(localStorage.getItem("nutrime.groc." + planId) || "[]")); }
  catch (e) { return new Set(); }
}
function saveGroceryChecked(planId, set) {
  try { localStorage.setItem("nutrime.groc." + planId, JSON.stringify([...set])); } catch (e) {}
}
async function loadGrocery() {
  const data = await jget("/api/grocery", true);
  const box = $("groceryBody");
  if (data.error) {
    box.innerHTML = '<div class="empty">' + (data.error === "no plans yet" ?
      "No plan yet. The list builds itself from your latest plan." : esc(data.error)) + "</div>";
    return;
  }
  const checked = groceryChecked(data.plan_id);
  const item = l => {
    const key = l.food;
    return '<li class="' + (checked.has(key) ? "done" : "") + '"><input type="checkbox" data-food="' +
      esc(key) + '"' + (checked.has(key) ? " checked" : "") + ' aria-label="got ' + esc(key) + '">' +
      '<div><span class="food">' + esc(l.amount ? l.amount + " " + l.food : l.food) + "</span>" +
      "<small>" + esc(l.recipes.join(", ")) + "</small></div></li>";
  };
  box.innerHTML =
    "<p class=\\"hint\\">From your latest plan. Ticks are saved on this device.</p>" +
    (data.to_buy.length ? '<ul class="groc">' + data.to_buy.map(item).join("") + "</ul>" :
      '<div class="empty">Nothing to buy. The kitchen covers it.</div>') +
    (data.have.length ? '<details style="margin-top:14px"><summary class="hint">Already in the kitchen (' +
      data.have.length + ")</summary><ul class=\\"groc\\">" +
      data.have.map(l => "<li><div><span class=\\"food\\">" + esc(l.food) + "</span></div></li>").join("") +
      "</ul></details>" : "");
  box.querySelectorAll("input[data-food]").forEach(cb => cb.onchange = () => {
    cb.checked ? checked.add(cb.dataset.food) : checked.delete(cb.dataset.food);
    cb.closest("li").classList.toggle("done", cb.checked);
    saveGroceryChecked(data.plan_id, checked);
  });
}

/* -- profile: answers, avoid-list, privacy, household -- */
async function loadProfile() {
  $("profileHeading").textContent = profileLabel();
  const status = await jget("/api/intake/status", true);
  $("profileStatus").textContent = status.complete ?
    "Saved. Change them any time; the household avoid-list updates straight away." :
    "Not filled in yet. It takes about 5 minutes and stays on this computer.";
  $("profileLink").textContent = status.complete ? "Edit my answers" : "Fill in my answers";
  const derived = await jget("/api/derived", true);
  let derivedHtml = (derived.constraints || []).length ?
    '<div class="matchLine">' + derived.constraints.map(c =>
      '<span class="tag">' + esc(c) + "</span>").join(" ") + "</div>" :
    '<div class="hint">Nothing yet. Profile answers fill this in.</div>';
  const conds = derived.conditions || [];
  if (conds.length) {
    const behaviorLabel = {refuse: "meal plans paused", gate: "guard rails on plans",
                           disclaimer: "consult-professional notes"};
    derivedHtml += '<div style="margin-top:10px">' + conds.map(c =>
      '<div class="consentRow"><span><b>' + esc(c.name) + '</b> ' +
      '<span class="tag' + (c.behavior === "refuse" ? " warn" : "") + '">' +
      esc(behaviorLabel[c.behavior] || c.behavior) + '</span><br>' +
      '<span class="hint">' + esc(c.note || ("Typically managed by " +
        c.specialties.join(" or ") + ".")) + '</span></span></div>').join("") + "</div>";
  }
  $("derivedBody").innerHTML = derivedHtml;
  loadConsent();
  renderMemberAdmin();
  loadDoctor();
  loadCheckinSettings();
  loadNotifySettings();
}
async function loadDoctor() {
  const data = await jget("/api/doctor", true);
  if (data.error) { $("doctorBody").innerHTML = '<div class="errorBox">' + esc(data.error) + "</div>"; return; }
  const icon = {ok: "✓", warn: "!", fail: "✕"};
  $("doctorBody").innerHTML = data.checks.map(c =>
    '<div class="consentRow"><span><b>' + icon[c.status] + " " + esc(c.name) + "</b> " +
    '<span class="hint">' + esc(c.detail) + "</span>" +
    (c.fix && c.status !== "ok" ? '<br><span class="hint">Fix: ' + esc(c.fix) + "</span>" : "") +
    "</span></div>").join("");
}
async function loadConsent() {
  const data = await jget("/api/consent", true);
  if (data.error) { $("consentBody").innerHTML = '<div class="errorBox">' + esc(data.error) + "</div>"; return; }
  const local = data.decisions.filter(d => d.purpose === "local_operation");
  const pub = data.decisions.filter(d => d.purpose === "publication_aggregate");
  const row = d =>
    '<div class="consentRow"><span>' + esc(d.label) + ' <span class="scope">' + esc(d.scope) + "</span></span>" +
    '<label class="switch"><input type="checkbox" data-cat="' + esc(d.category) + '" data-purpose="' +
    esc(d.purpose) + '"' + (d.granted ? " checked" : "") + "> " + (d.granted ? "on" : "off") + "</label></div>";
  $("consentBody").innerHTML = local.map(row).join("") +
    '<details style="margin-top:12px"><summary class="hint">Contributing anonymous totals to research (off unless you turn it on)</summary>' +
    pub.map(row).join("") + "</details>";
  $("consentBody").querySelectorAll("input[data-cat]").forEach(cb => cb.onchange = async () => {
    const res = await jpost("/api/consent", {category: cb.dataset.cat, purpose: cb.dataset.purpose, granted: cb.checked});
    if (!res.error) { toast("Saved."); loadConsent(); } else cb.checked = !cb.checked;
  });
}
function renderMemberAdmin() {
  const others = MEMBERS.length > 1;
  $("memberAdmin").innerHTML =
    '<p class="hint">' + MEMBERS.map(m => esc(m.name) + (m.has_profile ? "" : " (no profile yet)")).join(" · ") + "</p>" +
    '<div class="formRow"><button class="btn-quiet" id="maRename">Rename ' + esc(memberName() || "me") + "</button>" +
    (others ? '<button class="btn-quiet" id="maArchive">Remove ' + esc(memberName()) + " from the picker</button>" : "") +
    '<button class="btn-quiet" id="maAdd">Add a person</button></div>';
  $("maRename").onclick = async () => {
    const got = await formSheet({title: "Rename", submit: "Save",
      fields: [{id: "name", label: "New name", value: memberName()}],
      validate: o => o.name ? null : "Type a name."});
    if (!got) return;
    const name = got.name;
    const res = await jpost("/api/members/rename", {id: MEMBER, name});
    if (!res.error) { renderMembers(res); loadProfile(); }
  };
  if (others) $("maArchive").onclick = async () => {
    const ok = await formSheet({title: "Remove " + memberName() + "?", submit: "Remove from the picker",
      intro: "Their history is kept, and their allergies leave the household avoid-list.", fields: []});
    if (!ok) return;
    const res = await jpost("/api/members/archive", {id: MEMBER});
    if (!res.error) { MEMBER = null; renderMembers(res); onMemberChange(); }
  };
  $("maAdd").onclick = () => { $("memberPicker").value = "__add"; onMemberChange(); };
}

loadPhases();
loadSources();
loadInventory();
loadPinterestStatus();
loadMembers().then(() => { loadTonight(); loadIntakeStatus(); showView(currentView(), true); });
doSearch();
</script>
</body>
</html>
"""
