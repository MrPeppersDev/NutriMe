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
    SearchFilters,
    attribution_line,
    filters_from_constraints,
    search,
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
            else:
                self._json({"error": "not found"}, status=404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, status=500)

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

        filters = SearchFilters(
            query=first("q") or None,
            max_total_time_min=max_time,
            on_hand=frozenset(on_hand),
            prefer_terms=frozenset(prefer),
        )
        if first("apply_constraints") == "1":
            from nutrime.knowledge.store import list_synthesized_entries

            entries = list_synthesized_entries(
                app.substrate, app.tenant_id, entry_type="abstracted_constraint"
            )
            filters = filters_from_constraints(entries, filters)

        limit = 24
        results = search(self.server.vault, filters, limit=limit)
        self._json(
            {
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

  footer {
    max-width: 1060px; margin: 0 auto; padding: 0 24px 40px;
    font-size: 12px; color: var(--ink-soft);
  }

  @media (max-width: 560px) {
    header { padding-top: 26px; }
    .ask { padding: 16px; }
  }
</style>
</head>
<body>
<header>
  <div class="wordmark">NutriMe</div>
  <h1>What can we make with <em>what we already have?</em></h1>
  <p class="sub">Search the household recipe collection by what's in the kitchen —
  and, if you like, tilt the ranking toward foods that fit where you are in your cycle.</p>
</header>

<main>
  <section class="ask">
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

<footer id="disclosure"></footer>

<script>
const $ = id => document.getElementById(id);
let PHASE = "";

function esc(s) {
  return String(s).replace(/[&<>"']/g,
    c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

async function jget(url) { const r = await fetch(url); return r.json(); }
async function jpost(url, body) {
  const r = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"},
                              body: JSON.stringify(body)});
  return r.json();
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
async function doSearch() {
  const params = new URLSearchParams();
  const have = $("have").value.trim();
  if (have) params.set("have", have);
  if ($("useInventory").checked) params.set("use_inventory", "1");
  if ($("applyConstraints").checked) params.set("apply_constraints", "1");
  if ($("maxTime").value) params.set("max_time", $("maxTime").value);
  if (PHASE) params.set("phase", PHASE);
  const data = await jget("/api/search?" + params.toString());
  const box = $("resultsBox");
  $("resultMeta").textContent = data.results.length + " of " + data.corpus_count +
    " recipes in the collection" +
    (data.on_hand_count ? " \\u00b7 matching against " + data.on_hand_count + " ingredients you have" : "");
  if (!data.results.length) {
    box.innerHTML = '<div class="empty">Nothing matched those filters \\u2014 try fewer' +
      ' restrictions, or import more of your saved recipes below.</div>';
    return;
  }
  const grid = document.createElement("div");
  grid.className = "grid";
  for (const r of data.results) {
    const card = document.createElement("div");
    card.className = "card";
    let tags = "";
    for (const m of r.on_hand_matches) tags += '<span class="tag have">\\u2713 ' + esc(m) + "</span>";
    for (const m of r.prefer_matches) tags += '<span class="tag boost">\\u2191 ' + esc(m) + "</span>";
    for (const a of r.allergens) tags += '<span class="tag warn">' + esc(a) + "</span>";
    card.innerHTML =
      "<h3>" + esc(r.title) + "</h3>" +
      (tags ? '<div class="matchLine">' + tags + "</div>" : "") +
      '<div class="cardFoot"><span>' +
      (r.total_time_min ? "\\u23f1 " + r.total_time_min + " min" : "") +
      "</span><span>" + (r.score > 0 ? r.on_hand_matches.length + " on hand" : "") + "</span></div>" +
      '<div class="attr">' + esc(r.attribution) + "</div>";
    card.onclick = () => openDetail(r.recipe_id);
    grid.appendChild(card);
  }
  box.innerHTML = "";
  box.appendChild(grid);
}

/* -- detail -- */
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
    "<h4>Ingredients</h4><ul>" +
    d.ingredients.map(i => "<li>" + esc(i) + "</li>").join("") + "</ul>" +
    "<h4>Steps</h4><ol>" +
    d.steps.map(s => "<li>" + esc(s) + "</li>").join("") + "</ol>" +
    (d.source_url ? '<div class="srcLink"><a href="' + esc(d.source_url) +
      '" target="_blank" rel="noopener">Open the original \\u2197</a></div>' : "") +
    '<div class="attr">' + esc(d.attribution) + "</div>";
  $("overlay").classList.add("on");
}
function closeDetail() { $("overlay").classList.remove("on"); }
$("overlay").addEventListener("click", e => { if (e.target === $("overlay")) closeDetail(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeDetail(); });

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

$("go").onclick = doSearch;
$("have").addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });
["useInventory", "applyConstraints", "maxTime"].forEach(id =>
  $(id).addEventListener("change", doSearch));

loadPhases();
loadInventory();
loadPinterestStatus();
doSearch();
</script>
</body>
</html>
"""
