"""SQLite + sqlite-vec connection helper and forward-only migration runner.

Per ``research/00-meta/schema.md`` S12 (Q12.2 — Custom Python migration runner +
forward-only): each DB (substrate + operational) tracks its own migrations
independently via a ``schema_migrations`` table. Migrations are numbered SQL
files (e.g. ``0001_substrate__initial.sql``); pure SQL when possible, per Q12.2
adjustment 2.

The runner does not yet author any baseline migration — the S1–S11 baselines
(``0001_substrate__initial.sql`` + ``0001_operational__initial.sql``) land with
the multi-tenant scaffolding sub-commit that follows, so the F9 typed query
helper + ``tenant`` lifecycle table land in the same migration that introduces
the rest of the baseline schema.
"""

from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import sqlite_vec

MIGRATION_FILENAME = re.compile(r"^(\d+)_.*\.sql$")

# Concurrent processes (app + doctor, app + CLI) wait this long for the
# other's write transaction instead of failing with "database is locked".
BUSY_TIMEOUT_MS = 10_000


class Connection(sqlite3.Connection):
    """sqlite3.Connection + a transaction-depth slot for :func:`transaction`.

    Plain sqlite3.Connection forbids new attributes; the subclass gives the
    nesting counter somewhere to live.
    """

    txn_depth: int = 0


def connect(db_path: Path | str) -> Connection:
    conn = sqlite3.connect(db_path, factory=Connection)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS};")
    # WAL: readers don't block the writer (or each other) across the
    # threaded server + CLI + doctor. Persistent per database file;
    # NORMAL sync is the standard WAL pairing (durable at checkpoint,
    # app-crash safe). Memory DBs don't support WAL — tests use them.
    if str(db_path) not in ("", ":memory:"):
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """All-or-nothing write scope (2026-10-06 audit: zero BEGINs anywhere).

    ``BEGIN IMMEDIATE`` takes the write lock up front, so check-then-insert
    sequences (tenant bootstrap, migration re-checks) are race-free across
    processes. Nests: inner scopes join the outer transaction; only the
    outermost commits or rolls back.
    """
    depth = getattr(conn, "txn_depth", 0)
    if depth == 0 and not conn.in_transaction:
        # If python's sqlite3 already auto-opened an implicit (DEFERRED)
        # transaction for earlier DML, an explicit BEGIN would raise;
        # that implicit transaction simply becomes this scope's.
        conn.execute("BEGIN IMMEDIATE")
    conn.txn_depth = depth + 1
    try:
        yield conn
    except BaseException:
        conn.txn_depth = depth
        if depth == 0:
            conn.rollback()
        raise
    else:
        conn.txn_depth = depth
        if depth == 0:
            conn.commit()


def maybe_commit(conn: sqlite3.Connection) -> None:
    """Commit unless a :func:`transaction` scope is open above us.

    Store helpers call this instead of ``conn.commit()`` so they stay
    standalone-safe AND composable into one atomic write when a caller
    wraps a multi-helper sequence in :func:`transaction`.
    """
    if getattr(conn, "txn_depth", 0) == 0:
        conn.commit()


@dataclass(frozen=True)
class Migration:
    number: int
    name: str
    path: Path

    @property
    def filename(self) -> str:
        return self.path.name


def discover_migrations(migrations_dir: Path) -> list[Migration]:
    """Return migrations in ``migrations_dir``, sorted by number; raises on duplicates."""
    found: list[Migration] = []
    for entry in sorted(migrations_dir.iterdir()):
        if not entry.is_file():
            continue
        match = MIGRATION_FILENAME.match(entry.name)
        if not match:
            continue
        found.append(
            Migration(number=int(match.group(1)), name=entry.stem, path=entry)
        )

    seen: set[int] = set()
    for migration in found:
        if migration.number in seen:
            raise ValueError(
                f"Duplicate migration number {migration.number} in {migrations_dir}"
            )
        seen.add(migration.number)

    return sorted(found, key=lambda m: m.number)


def _ensure_schema_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            number INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            applied_at TEXT NOT NULL
                DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    conn.commit()


def applied_migrations(conn: sqlite3.Connection) -> set[int]:
    _ensure_schema_migrations_table(conn)
    cursor = conn.execute("SELECT number FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}


def apply_migrations(
    conn: sqlite3.Connection, migrations_dir: Path
) -> list[Migration]:
    """Apply unapplied migrations in number order; each runs in its own transaction."""
    _ensure_schema_migrations_table(conn)
    already_applied = applied_migrations(conn)
    pending = [
        m for m in discover_migrations(migrations_dir) if m.number not in already_applied
    ]

    newly_applied: list[Migration] = []
    for migration in pending:
        sql = migration.path.read_text()
        # One real transaction per migration: statements + the
        # schema_migrations row commit together, so a crash mid-migration
        # leaves nothing behind and the retry is clean. (executescript
        # auto-commits as it goes — a crash left half a migration applied
        # and the ADD COLUMN ones then failed forever on retry; 2026-10-06
        # audit, reproduced.)
        with transaction(conn):
            # Re-check under the write lock: a concurrent process (app
            # launch + doctor) may have applied this number since the
            # pending list was computed.
            raced = conn.execute(
                "SELECT 1 FROM schema_migrations WHERE number = ?",
                (migration.number,),
            ).fetchone()
            if raced:
                continue
            for statement in _iter_statements(sql):
                conn.execute(statement)
            conn.execute(
                "INSERT INTO schema_migrations (number, name, filename)"
                " VALUES (?, ?, ?)",
                (migration.number, migration.name, migration.filename),
            )
        newly_applied.append(migration)

    return newly_applied


def _iter_statements(sql: str) -> Iterator[str]:
    """Split a migration file into executable statements.

    Uses sqlite3.complete_statement so semicolons inside literals or
    trigger bodies don't split; our migrations are plain SQL (no PRAGMA,
    no BEGIN/COMMIT — the runner owns the transaction).
    """
    buffer = ""
    for line in sql.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statement = buffer.strip()
            if statement and statement != ";":
                yield statement
            buffer = ""
    tail = buffer.strip()
    if tail and tail != ";":
        yield tail
