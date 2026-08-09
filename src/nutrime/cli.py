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
from nutrime.recipes.myplate_wayback import seed_recipes as myplate_seed_recipes
from nutrime.recipes.nhlbi import seed_recipes as nhlbi_seed_recipes
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
    else:
        print(
            f"unknown --source {args.source!r}; wired sources:"
            " themealdb, nhlbi, myplate_wayback, gutenberg"
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
            " gutenberg (4.3)."
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
