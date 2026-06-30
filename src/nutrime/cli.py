"""Minimal CLI for the deployment shell.

The MVP CLI exists to drive :func:`nutrime.app.initialize` from a terminal —
``nutrime init`` opens the DBs under the data directory (``$NUTRIME_DATA_DIR``
or ``~/.nutrime``), applies pending migrations, and ensures the single tenant
row exists. Subsequent subcommands (run, ingest, query) land as their
components arrive in later Stage 6 sub-commits; we deliberately ship only
``init`` here to keep this slice scoped to the deployment shell.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from nutrime import __version__
from nutrime.app import initialize


def _cmd_init(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else None
    app = initialize(data_dir=data_dir)
    print(f"data_dir:    {app.data_dir}")
    print(f"substrate:   {app.data_dir / 'substrate.db'}")
    print(f"operational: {app.data_dir / 'operational.db'}")
    print(f"tenant_id:   {app.tenant_id}")
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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
