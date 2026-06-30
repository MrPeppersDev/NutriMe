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
from dataclasses import dataclass
from pathlib import Path

import sqlite_vec

MIGRATION_FILENAME = re.compile(r"^(\d+)_.*\.sql$")


def connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


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
        try:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (number, name, filename)"
                " VALUES (?, ?, ?)",
                (migration.number, migration.name, migration.filename),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        newly_applied.append(migration)

    return newly_applied
