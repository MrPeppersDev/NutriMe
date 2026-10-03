"""Minimal CLI for the deployment shell + first-run baseline intake + inventory.

Subcommands ship with the components that require them; each new sub-commit
adds only the subparser it needs. Current surface:

- ``nutrime init``               — open DBs, apply migrations, ensure tenant row
- ``nutrime intake``             — first-run baseline intake (step 2 s.c. 2.1)
- ``nutrime inventory add``      — add pantry/fridge/freezer items (2.2)
- ``nutrime inventory list``     — show current inventory grouped by location (2.2)
- ``nutrime knowledge sync``     — derive atoms + constraint stub from intake (step 3)
- ``nutrime knowledge list``     — show currently-valid atoms + constraints (step 3)
- ``nutrime recipes fetch``      — seed corpus from an external source (step 4 s.c. 4.1/4.2)
- ``nutrime recipes list``       — show recipes in the local vault (step 4 s.c. 4.1)
- ``nutrime audit list``         — show recent operational audit events (step 5 s.c. 5.1)
- ``nutrime llm ping``           — end-to-end LLM pipeline smoke test (step 5 s.c. 5.2)
- ``nutrime recipes search``     — query the vault with filters + ranking (step 5 s.c. 5.3)
- ``nutrime plans generate``     — assemble a meal plan, one crossing per meal (5.4)
- ``nutrime plans list``         — show plans in the local vault (5.4)
- ``nutrime plans show``         — render a plan with per-recipe attribution (5.4)
- ``nutrime serve``              — localhost web UI prototype (product pull 2026-10-03)
"""

from __future__ import annotations

import argparse
from pathlib import Path

from nutrime import __version__
from nutrime.app import initialize
from nutrime.intake.baseline import run_baseline_intake
from nutrime.inventory.capture import capture_items
from nutrime.inventory.store import by_location, list_items
from nutrime.knowledge.derivation import sync_from_intake
from nutrime.knowledge.store import list_atoms, list_synthesized_entries
from nutrime.recipes.gutenberg import seed_recipes as gutenberg_seed_recipes
from nutrime.recipes.jsonld import (
    read_urls_file,
    seed_recipes as jsonld_seed_recipes,
)
from nutrime.recipes.myplate_wayback import seed_recipes as myplate_seed_recipes
from nutrime.recipes.nhlbi import seed_recipes as nhlbi_seed_recipes
from nutrime.recipes.search import attribution_line
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.themealdb import TheMealDBClient, seed_recipes
from nutrime.recipes.web import Pacer


def _cmd_init(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    print(f"data_dir:    {app.data_dir}")
    print(f"substrate:   {app.data_dir / 'substrate.db'}")
    print(f"operational: {app.data_dir / 'operational.db'}")
    print(f"tenant_id:   {app.tenant_id}")
    return 0


def _cmd_intake(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    run_baseline_intake(
        app.substrate,
        app.tenant_id,
        prompter=input,
        emitter=print,
    )
    return 0


def _cmd_inventory_add(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    capture_items(app.substrate, app.tenant_id, prompter=input, emitter=print)
    return 0


def _cmd_inventory_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    items = list_items(app.substrate, app.tenant_id)
    if not items:
        print("(no inventory items yet — run `nutrime inventory add`)")
        return 0
    for location, group in sorted(by_location(items).items()):
        print(f"— {location} —")
        for item in group:
            if item.quantity is not None:
                qty = f"{item.quantity:g} {item.unit}"
            else:
                qty = "on hand"
            best_by = f", best by {item.best_by_date}" if item.best_by_date else ""
            notes = f" ({item.notes})" if item.notes else ""
            print(f"  {item.name}: {qty}{best_by}{notes}")
    return 0


def _cmd_knowledge_sync(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    outcome = sync_from_intake(app.substrate, app.tenant_id)
    if outcome.total_atoms_added == 0 and outcome.constraints_added == 0:
        print("(nothing to derive — knowledge model already in sync with intake)")
        return 0
    if outcome.total_atoms_added:
        print(f"Added {outcome.total_atoms_added} atom(s):")
        for atom_type, count in sorted(outcome.atoms_added.items()):
            print(f"  {atom_type}: {count}")
    if outcome.constraints_added:
        print(f"Emitted {outcome.constraints_added} abstracted constraint(s).")
    return 0


def _cmd_knowledge_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    atoms = list_atoms(app.substrate, app.tenant_id)
    constraints = list_synthesized_entries(
        app.substrate, app.tenant_id, entry_type="abstracted_constraint"
    )
    if not atoms and not constraints:
        print("(no atoms yet — run `nutrime intake` then `nutrime knowledge sync`)")
        return 0
    by_type: dict[str, list] = {}
    for atom in atoms:
        by_type.setdefault(atom.type, []).append(atom)
    for atom_type, group in sorted(by_type.items()):
        print(f"— {atom_type} ({len(group)}) —")
        for atom in group:
            summary = _atom_summary(atom.type, atom.payload)
            print(f"  {summary}")
    if constraints:
        print(f"— abstracted_constraint ({len(constraints)}) —")
        for entry in constraints:
            print(f"  {entry.payload.get('abstracted_text', '(no text)')}")
    return 0


def _cmd_recipes_fetch(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)
    pacer = Pacer(delay_s=args.delay)
    if args.source == "themealdb":
        client = TheMealDBClient()
        letters = tuple(args.letters)
        outcome = seed_recipes(
            client, vault, letters=letters, limit=args.limit
        )
    elif args.source == "nhlbi":
        outcome = nhlbi_seed_recipes(vault, pacer=pacer, limit=args.limit)
    elif args.source == "myplate_wayback":
        outcome = myplate_seed_recipes(vault, pacer=pacer, limit=args.limit)
    elif args.source == "gutenberg":
        books = (
            tuple(b.strip() for b in args.books.split(",") if b.strip())
            if args.books
            else None
        )
        outcome = gutenberg_seed_recipes(
            vault, pacer=pacer, books=books, limit=args.limit
        )
    elif args.source == "pinterest":
        from nutrime.recipes.pinterest import (
            MissingTokenError,
            PinterestAuthError,
            PinterestClient,
            resolve_token,
            sync_pins,
        )

        try:
            token = resolve_token()
        except MissingTokenError as err:
            print(str(err))
            return 2
        client = PinterestClient(token=token, pacer=pacer)
        try:
            sync = sync_pins(
                client,
                vault,
                board_name=args.board,
                limit=args.limit,
                pacer=pacer,
            )
        except (PinterestAuthError, ValueError) as err:
            print(str(err))
            return 2
        print(
            f"Pinterest: {sync.pins_seen} pin(s) seen,"
            f" {sync.pins_with_links} with recipe links,"
            f" {sync.pins_without_links} without usable links"
            " (image-only pins stay on the #24 follow-up)."
        )
        outcome = sync.ingest
    elif args.source == "urls":
        if not args.urls_file:
            print("--source urls requires --urls-file <path> (one URL per line)")
            return 2
        urls = read_urls_file(Path(args.urls_file).expanduser())
        outcome = jsonld_seed_recipes(
            vault, urls, pacer=pacer, limit=args.limit
        )
    else:
        print(
            f"unknown --source {args.source!r}; wired sources:"
            " themealdb, nhlbi, myplate_wayback, gutenberg, urls, pinterest"
        )
        return 2
    print(
        f"Fetched {outcome.fetched} recipe(s); wrote {outcome.written} new"
        f" recipe file(s) to {vault.root}."
    )
    if outcome.skipped_upstream_ids:
        print(
            f"Skipped {len(outcome.skipped_upstream_ids)} already-ingested"
            " upstream id(s)."
        )
    for url, reason in getattr(outcome, "failures", ()):
        print(f"  ! {url} — {reason}")
    return 0


def _cmd_recipes_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)
    records = vault.list_recipes()
    if not records:
        print(
            "(no recipes yet — run `nutrime recipes fetch` to seed the vault)"
        )
        return 0
    shown = records if args.limit is None else records[: args.limit]
    print(f"— {len(shown)} of {len(records)} recipe(s) —")
    for record in shown:
        fm = record.frontmatter
        title = fm.get("title", "(untitled)")
        cuisine = ", ".join(fm.get("cuisine_tradition_tags", ())) or "-"
        categories = ", ".join(fm.get("meal_categories", ())) or "-"
        allergens = ", ".join(fm.get("top_allergens_present", ())) or "none"
        print(f"  {record.recipe_id}")
        print(f"    title:     {title}")
        print(f"    cuisine:   {cuisine}")
        print(f"    category:  {categories}")
        print(f"    allergens: {allergens}")
        print(f"    {attribution_line(fm)}")
    return 0


def _cmd_recipes_search(args: argparse.Namespace) -> int:
    from nutrime.knowledge.store import list_synthesized_entries
    from nutrime.recipes.search import (
        SearchFilters,
        filters_from_constraints,
        search,
    )

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)

    def _split(raw: str | None) -> frozenset[str]:
        if not raw:
            return frozenset()
        return frozenset(t.strip() for t in raw.split(",") if t.strip())

    filters = SearchFilters(
        query=args.query,
        exclude_allergens=_split(args.exclude_allergen),
        exclude_ingredients=_split(args.exclude_ingredient),
        max_total_time_min=args.max_time,
        meal_category=args.category,
        cuisine=args.cuisine,
    )
    applied: list[str] = []
    if args.apply_constraints:
        entries = list_synthesized_entries(
            app.substrate, app.tenant_id, entry_type="abstracted_constraint"
        )
        filters = filters_from_constraints(entries, base=filters)
        applied.append(f"{len(entries)} abstracted constraint(s)")
    if args.use_inventory:
        items = list_items(app.substrate, app.tenant_id)
        from dataclasses import replace as _replace

        filters = _replace(
            filters,
            on_hand=frozenset(item.name for item in items),
        )
        applied.append(f"{len(items)} inventory item(s)")
    if applied:
        print(f"(applying {', '.join(applied)})")

    results = search(vault, filters, limit=args.limit)
    if not results:
        print("(no recipes matched — relax a filter or fetch more sources)")
        return 0
    print(f"— {len(results)} result(s) —")
    for rank, result in enumerate(results, start=1):
        time_str = (
            f"{result.total_time_min} min"
            if result.total_time_min is not None
            else "time unknown"
        )
        allergens = ", ".join(result.allergens) or "none detected"
        print(f"{rank:>2}. {result.title}  [{result.recipe_id}]")
        print(f"    {time_str} · allergens: {allergens} · score {result.score:g}")
        if result.on_hand_matches:
            print(f"    uses on-hand: {', '.join(result.on_hand_matches)}")
        if result.prefer_matches:
            print(f"    matches preference: {', '.join(result.prefer_matches)}")
        print(f"    {result.attribution}")
    return 0


def _cmd_llm_ping(args: argparse.Namespace) -> int:
    from nutrime.llm.anthropic import AnthropicProvider
    from nutrime.llm.base import ChatMessage, LlmRequest, MissingApiKeyError, ProviderError
    from nutrime.llm.client import LlmClient
    from nutrime.llm.phi import LLM_PING

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    provider = AnthropicProvider(model=args.model)
    client = LlmClient((provider,), app.rule_engine, app.audit)
    request = LlmRequest(
        query_type=LLM_PING,
        messages=(
            ChatMessage(role="user", content="Reply with the single word: pong"),
        ),
        max_tokens=16,
    )
    try:
        response = client.complete(request)
    except MissingApiKeyError as exc:
        print(f"config error: {exc}")
        return 2
    except ProviderError as exc:
        print(f"provider error ({exc.outcome}): {exc.detail}")
        print("(the failed call was audit-logged — see `nutrime audit list`)")
        return 1
    print(f"provider:   {response.provider} ({response.model})")
    print(f"response:   {response.text.strip()}")
    print(
        f"tokens:     {response.prompt_tokens} in / {response.completion_tokens} out"
    )
    print(f"latency:    {response.latency_ms} ms")
    print(f"audit row:  {response.llm_request_log_id} (request {response.request_id})")
    return 0


def _cmd_audit_list(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    events = app.audit.events(event_kind=args.kind, limit=args.limit)
    if not events:
        print("(no audit events yet)")
        return 0
    print(f"— {len(events)} most recent event(s), newest first —")
    for event in events:
        subkind = f"/{event.event_subkind}" if event.event_subkind else ""
        request = f"  request={event.request_id}" if event.request_id else ""
        print(f"  {event.recorded_at}  {event.event_kind}{subkind}"
              f"  actor={event.actor}{request}")
        summary = ", ".join(
            f"{key}={value}" for key, value in sorted(event.payload.items())
        )
        if len(summary) > 120:
            summary = summary[:117] + "..."
        print(f"    {summary}")
    return 0


def _atom_summary(atom_type: str, payload: dict) -> str:
    if atom_type == "clinical_disclosure":
        return (
            f"{payload.get('disclosure_type', '?')}: "
            f"{payload.get('disclosure_text', '?')}"
        )
    if atom_type == "preference_statement":
        return (
            f"{payload.get('preference_type', '?')}: "
            f"{payload.get('subject_text', '?')}"
        )
    if atom_type == "screener_result":
        interp = payload.get("score_interpretation", "?")
        score = payload.get("score", "?")
        instrument = payload.get("instrument_id", "?")
        return f"{instrument}: score {score} → {interp}"
    return f"{atom_type}"


def _plan_base_filters(app, args) -> tuple[object, list[str]]:
    """Build the shared search filters for every slot + a note of what applied."""
    from dataclasses import replace as _replace

    from nutrime.knowledge.store import list_synthesized_entries
    from nutrime.recipes.search import SearchFilters, filters_from_constraints

    filters = SearchFilters(max_total_time_min=args.max_time)
    applied: list[str] = []
    if args.apply_constraints:
        entries = list_synthesized_entries(
            app.substrate, app.tenant_id, entry_type="abstracted_constraint"
        )
        filters = filters_from_constraints(entries, base=filters)
        applied.append(f"{len(entries)} abstracted constraint(s)")
    if args.use_inventory:
        items = list_items(app.substrate, app.tenant_id)
        filters = _replace(
            filters, on_hand=frozenset(item.name for item in items)
        )
        applied.append(f"{len(items)} inventory item(s)")
    return filters, applied


def _cmd_plans_generate(args: argparse.Namespace) -> int:
    from nutrime.audit import _now_iso
    from nutrime.llm.anthropic import AnthropicProvider
    from nutrime.llm.base import MissingApiKeyError
    from nutrime.llm.client import LlmClient
    from nutrime.plans.assemble import (
        MEAL_SLOTS,
        PlanSpec,
        assemble_plan,
        candidates_for_slot,
    )
    from nutrime.plans.store import PlanVault, new_plan_id, render_plan_body

    slots = tuple(s.strip().lower() for s in args.meals.split(",") if s.strip())
    unknown = [s for s in slots if s not in MEAL_SLOTS]
    if unknown:
        print(f"unknown meal slot(s): {', '.join(unknown)}")
        print(f"known slots: {', '.join(MEAL_SLOTS)}")
        return 2

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    vault = RecipeVault(app.corpus_dir)

    try:
        spec = PlanSpec(
            days=args.days,
            slots=slots,
            servings=args.servings,
            household_note=args.household or "",
            candidates_per_slot=args.candidates,
        )
    except ValueError as exc:
        print(f"invalid plan spec: {exc}")
        return 2

    filters, applied = _plan_base_filters(app, args)
    if applied:
        print(f"(applying {', '.join(applied)})")

    print(
        f"plan: {spec.days} day(s) x {len(spec.slots)} slot(s)"
        f" = {spec.crossings} LLM crossing(s)"
    )

    if args.dry_run:
        print("(dry run — nothing crosses)")
        for slot in spec.slots:
            pool = candidates_for_slot(
                vault, filters, slot, limit=spec.candidates_per_slot
            )
            preview = ", ".join(c.title for c in pool[:5]) or "(none)"
            print(f"  {slot}: {len(pool)} candidate(s) — {preview}")
        return 0

    provider = AnthropicProvider(model=args.model)
    client = LlmClient((provider,), app.rule_engine, app.audit)

    def _progress(outcome) -> None:
        label = f"  day {outcome.day} {outcome.slot}"
        if outcome.error:
            print(f"{label}: unfilled — {outcome.error}")
        else:
            print(f"{label}: {outcome.entry.title}  [{outcome.entry.recipe_id}]")

    try:
        plan = assemble_plan(
            vault, client, spec, filters, on_progress=_progress
        )
    except MissingApiKeyError as exc:
        print(f"config error: {exc}")
        return 2

    plan_id = new_plan_id()
    frontmatter = {
        "plan_id": plan_id,
        "content_type": "meal_plan",
        "created_at": _now_iso(),
        "tenant_id": app.tenant_id,
        "days": spec.days,
        "meal_slots": list(spec.slots),
        "meals_planned": plan.filled,
        "model": plan.model or args.model,
        "llm_request_ids": list(plan.request_ids),
        "llm_request_log_ids": list(plan.llm_request_log_ids),
        "constraints_applied": applied,
        "candidate_count": plan.candidate_count,
    }
    plan_vault = PlanVault(app.corpus_dir)
    path = plan_vault.write(
        plan_id, frontmatter, render_plan_body(plan.entries)
    )

    print(f"— plan {plan_id} written to {path} —")
    print(f"{plan.filled} of {spec.crossings} slot(s) filled")
    if plan.failures:
        print(
            f"({len(plan.failures)} slot(s) unfilled — every failed crossing is"
            " audit-logged; see `nutrime audit list`)"
        )
    return 0


def _cmd_plans_list(args: argparse.Namespace) -> int:
    from nutrime.plans.store import PlanVault

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    records = PlanVault(app.corpus_dir).list_plans()[: args.limit]
    if not records:
        print("(no plans yet — run `nutrime plans generate`)")
        return 0
    print(f"— {len(records)} plan(s), newest first —")
    for record in records:
        fm = record.frontmatter
        slots = ", ".join(str(s) for s in fm.get("meal_slots", ()) or ())
        print(f"{record.plan_id}")
        print(
            f"    {fm.get('created_at', '?')} · {fm.get('days', '?')} day(s)"
            f" · {slots or 'no slots'} · {fm.get('meals_planned', 0)} meal(s)"
            f" · {fm.get('model', 'unknown model')}"
        )
    return 0


def _cmd_plans_show(args: argparse.Namespace) -> int:
    from nutrime.plans.store import PlanVault

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    plan_vault = PlanVault(app.corpus_dir)
    if not plan_vault.exists(args.plan_id):
        print(f"no such plan: {args.plan_id}")
        return 1
    record = plan_vault.read(args.plan_id)
    vault = RecipeVault(app.corpus_dir)
    fm = record.frontmatter

    print(f"plan {record.plan_id}")
    print(
        f"  {fm.get('created_at', '?')} · {fm.get('days', '?')} day(s)"
        f" · {fm.get('model', 'unknown model')}"
    )
    constraints = fm.get("constraints_applied", ()) or ()
    if constraints:
        print(f"  applied: {', '.join(str(c) for c in constraints)}")
    log_ids = fm.get("llm_request_log_ids", ()) or ()
    print(f"  audit rows: {len(log_ids)} crossing(s) — see `nutrime audit list`")
    print()

    for entry in record.entries():
        header = f"Day {entry.day} · {entry.slot}"
        if not entry.filled:
            print(f"{header}: (unfilled) {entry.note}".rstrip())
            print()
            continue
        print(f"{header}: {entry.title}  [{entry.recipe_id}]")
        if entry.note:
            print(f"    {entry.note}")
        # Attribution renders adjacent to recipe content on every display
        # surface (issue #23) — this is the plan-side surface.
        try:
            recipe = vault.read(entry.recipe_id)
        except OSError:
            print("    Source: (recipe no longer in vault)")
        else:
            print(f"    {attribution_line(recipe.frontmatter)}")
        print()
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    from nutrime.webui import serve

    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    server = serve(data_dir=data_dir, host=args.host, port=args.port)
    print(f"NutriMe web UI: http://{args.host}:{args.port}/")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nutrime")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser(
        "init",
        help="Open DBs, apply migrations, and ensure the tenant row.",
    )
    init.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    init.set_defaults(func=_cmd_init)

    intake = subparsers.add_parser(
        "intake",
        help="Run first-run baseline intake (screener trio + demographics).",
    )
    intake.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    intake.set_defaults(func=_cmd_intake)

    inventory = subparsers.add_parser(
        "inventory",
        help="Manage pantry/fridge/freezer inventory (add-many + list).",
    )
    inventory_sub = inventory.add_subparsers(dest="inventory_command", required=True)

    inv_add = inventory_sub.add_parser("add", help="Add items to the inventory.")
    inv_add.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    inv_add.set_defaults(func=_cmd_inventory_add)

    inv_list = inventory_sub.add_parser(
        "list", help="Show current inventory grouped by location."
    )
    inv_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    inv_list.set_defaults(func=_cmd_inventory_list)

    knowledge = subparsers.add_parser(
        "knowledge",
        help="Derive + inspect the knowledge model (atoms + constraint stub).",
    )
    knowledge_sub = knowledge.add_subparsers(
        dest="knowledge_command", required=True
    )

    kn_sync = knowledge_sub.add_parser(
        "sync",
        help="Derive atoms + abstracted constraints from intake data (idempotent).",
    )
    kn_sync.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    kn_sync.set_defaults(func=_cmd_knowledge_sync)

    kn_list = knowledge_sub.add_parser(
        "list",
        help="Show currently-valid atoms + abstracted constraints.",
    )
    kn_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    kn_list.set_defaults(func=_cmd_knowledge_list)

    recipes = subparsers.add_parser(
        "recipes",
        help="Seed + inspect the recipe corpus vault (step 4).",
    )
    recipes_sub = recipes.add_subparsers(dest="recipes_command", required=True)

    rec_fetch = recipes_sub.add_parser(
        "fetch",
        help="Fetch recipes from a seed source and write them to the vault.",
    )
    rec_fetch.add_argument(
        "--source",
        default="themealdb",
        help=(
            "Seed source: themealdb (4.1), nhlbi or myplate_wayback (4.2),"
            " gutenberg (4.3), urls (4.4 schema.org JSON-LD scrape),"
            " pinterest (board sync via API, #24)."
        ),
    )
    rec_fetch.add_argument(
        "--board",
        default=None,
        help=(
            "For --source pinterest: sync only the named board"
            " (default: all pins on the account)."
        ),
    )
    rec_fetch.add_argument(
        "--urls-file",
        default=None,
        help=(
            "For --source urls: file with one recipe-page URL per line"
            " (# comments allowed) — e.g. links from a Pinterest export."
        ),
    )
    rec_fetch.add_argument(
        "--books",
        default=None,
        help=(
            "Comma-separated Gutenberg book keys"
            " (beeton,farmer,forme_of_cury,golden_age; default: all)."
        ),
    )
    rec_fetch.add_argument(
        "--letters",
        default="a",
        help="Letters to iterate for TheMealDB search.php?f=<letter> (default: a).",
    )
    rec_fetch.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Cap the number of writes (default: no cap).",
    )
    rec_fetch.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Politeness delay in seconds between HTTP requests (default: 1.0).",
    )
    rec_fetch.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_fetch.set_defaults(func=_cmd_recipes_fetch)

    rec_list = recipes_sub.add_parser(
        "list",
        help="Show recipes in the vault with their headline frontmatter fields.",
    )
    rec_list.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Show at most N recipes (default: show all).",
    )
    rec_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_list.set_defaults(func=_cmd_recipes_list)

    rec_search = recipes_sub.add_parser(
        "search",
        help="Query the vault: filters + on-hand/preference ranking (5.3).",
    )
    rec_search.add_argument(
        "--query", default=None, help="Substring match on recipe title."
    )
    rec_search.add_argument(
        "--exclude-allergen",
        default=None,
        help="Comma-separated top-9 allergens to hard-block.",
    )
    rec_search.add_argument(
        "--exclude-ingredient",
        default=None,
        help="Comma-separated ingredient terms to exclude.",
    )
    rec_search.add_argument(
        "--max-time",
        type=int,
        default=None,
        help=(
            "Max estimated total minutes (recipes without a time estimate are"
            " excluded when set)."
        ),
    )
    rec_search.add_argument(
        "--category", default=None, help="Meal category filter (exact tag)."
    )
    rec_search.add_argument(
        "--cuisine", default=None, help="Cuisine tag filter (exact tag)."
    )
    rec_search.add_argument(
        "--use-inventory",
        action="store_true",
        help="Rank recipes that use what's on hand higher.",
    )
    rec_search.add_argument(
        "--apply-constraints",
        action="store_true",
        help=(
            "Apply the knowledge model's abstracted constraints"
            " (avoids -> hard-block, prefers -> boost)."
        ),
    )
    rec_search.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Show at most N results (default: 10).",
    )
    rec_search.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    rec_search.set_defaults(func=_cmd_recipes_search)

    audit = subparsers.add_parser(
        "audit",
        help="Inspect the operational audit trail (op_event_log).",
    )
    audit_sub = audit.add_subparsers(dest="audit_command", required=True)

    aud_list = audit_sub.add_parser(
        "list",
        help="Show recent audit events, newest first.",
    )
    aud_list.add_argument(
        "--kind",
        choices=("audit", "epistemic_trail", "system"),
        default=None,
        help="Filter by event kind (default: all kinds).",
    )
    aud_list.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Show at most N events (default: 20).",
    )
    aud_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    aud_list.set_defaults(func=_cmd_audit_list)

    llm = subparsers.add_parser(
        "llm",
        help="LLM provider layer (step 5 s.c. 5.2).",
    )
    llm_sub = llm.add_subparsers(dest="llm_command", required=True)

    llm_ping = llm_sub.add_parser(
        "ping",
        help=(
            "Send a tiny PHI-free request through the full pipeline"
            " (envelope -> rules -> provider -> audit log)."
        ),
    )
    llm_ping.add_argument(
        "--model",
        default="claude-opus-4-8",
        help="Anthropic model id (default: claude-opus-4-8).",
    )
    llm_ping.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    llm_ping.set_defaults(func=_cmd_llm_ping)

    plans = subparsers.add_parser(
        "plans",
        help="Meal-plan assembly (step 5 s.c. 5.4).",
    )
    plans_sub = plans.add_subparsers(dest="plans_command", required=True)

    pl_gen = plans_sub.add_parser(
        "generate",
        help=(
            "Assemble a plan of X meals across Y days — one audited LLM"
            " crossing per meal, selecting only from the licensed corpus."
        ),
    )
    pl_gen.add_argument(
        "--days", type=int, default=7, help="Number of days to plan (default: 7)."
    )
    pl_gen.add_argument(
        "--meals",
        default="dinner",
        help=(
            "Comma-separated meal slots per day"
            " (default: dinner; e.g. breakfast,lunch,dinner)."
        ),
    )
    pl_gen.add_argument(
        "--servings", type=int, default=2, help="Servings per meal (default: 2)."
    )
    pl_gen.add_argument(
        "--household",
        default=None,
        help="Free-text household context in place of a plain servings count.",
    )
    pl_gen.add_argument(
        "--candidates",
        type=int,
        default=12,
        help="Candidate recipes offered per slot (default: 12).",
    )
    pl_gen.add_argument(
        "--max-time",
        type=int,
        default=None,
        help=(
            "Max estimated total minutes per meal (recipes without a time"
            " estimate are excluded when set)."
        ),
    )
    pl_gen.add_argument(
        "--use-inventory",
        action="store_true",
        help="Rank recipes that use what's on hand higher.",
    )
    pl_gen.add_argument(
        "--apply-constraints",
        action="store_true",
        help=(
            "Apply the knowledge model's abstracted constraints"
            " (avoids -> hard-block, prefers -> boost)."
        ),
    )
    pl_gen.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the candidate pools and crossing count without calling out.",
    )
    pl_gen.add_argument(
        "--model",
        default="claude-opus-4-8",
        help="Anthropic model id (default: claude-opus-4-8).",
    )
    pl_gen.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    pl_gen.set_defaults(func=_cmd_plans_generate)

    pl_list = plans_sub.add_parser(
        "list", help="Show plans in the vault, newest first."
    )
    pl_list.add_argument(
        "--limit", type=int, default=20, help="Show at most N plans (default: 20)."
    )
    pl_list.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    pl_list.set_defaults(func=_cmd_plans_list)

    pl_show = plans_sub.add_parser(
        "show",
        help="Render one plan's schedule with per-recipe attribution.",
    )
    pl_show.add_argument("plan_id", help="Plan id (pln-...).")
    pl_show.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    pl_show.set_defaults(func=_cmd_plans_show)

    serve = subparsers.add_parser(
        "serve",
        help="Run the localhost web UI prototype (fridge search + phase"
        " boosts + URL import).",
    )
    serve.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind address (default: 127.0.0.1 — localhost only).",
    )
    serve.add_argument(
        "--port", type=int, default=8765, help="Port (default: 8765)."
    )
    serve.add_argument(
        "--data-dir",
        help="Override data directory (default: $NUTRIME_DATA_DIR or ~/.nutrime).",
    )
    serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
