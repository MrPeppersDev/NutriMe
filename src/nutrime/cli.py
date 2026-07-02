"""Minimal CLI for the deployment shell + first-run baseline intake + inventory.

Subcommands ship with the components that require them; each new sub-commit
adds only the subparser it needs. Current surface:

- ``nutrime init``               — open DBs, apply migrations, ensure tenant row
- ``nutrime intake``             — first-run baseline intake (step 2 s.c. 2.1)
- ``nutrime inventory add``      — add pantry/fridge/freezer items (2.2)
- ``nutrime inventory list``     — show current inventory grouped by location (2.2)
- ``nutrime knowledge sync``     — derive atoms + constraint stub from intake (step 3)
- ``nutrime knowledge list``     — show currently-valid atoms + constraints (step 3)
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
