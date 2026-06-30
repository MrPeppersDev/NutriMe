from pathlib import Path

import pytest

from nutrime.db import (
    apply_migrations,
    applied_migrations,
    connect,
    discover_migrations,
)


def test_connect_loads_sqlite_vec(tmp_path: Path) -> None:
    conn = connect(tmp_path / "test.db")
    version = conn.execute("SELECT vec_version()").fetchone()[0]
    assert isinstance(version, str) and version


def test_connect_enables_foreign_keys(tmp_path: Path) -> None:
    conn = connect(tmp_path / "test.db")
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_apply_migrations_on_empty_dir_bootstraps_tracking_table(
    tmp_path: Path,
) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    conn = connect(tmp_path / "test.db")

    applied = apply_migrations(conn, migrations_dir)
    assert applied == []
    assert applied_migrations(conn) == set()

    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
    ).fetchone()
    assert row is not None


def test_apply_migrations_applies_in_order_and_is_idempotent(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "0001_create_thing.sql").write_text(
        "CREATE TABLE thing (id INTEGER PRIMARY KEY);"
    )
    (migrations_dir / "0002_add_value.sql").write_text(
        "ALTER TABLE thing ADD COLUMN value TEXT;"
    )

    conn = connect(tmp_path / "test.db")
    first = apply_migrations(conn, migrations_dir)
    assert [m.number for m in first] == [1, 2]
    assert applied_migrations(conn) == {1, 2}

    second = apply_migrations(conn, migrations_dir)
    assert second == []
    assert applied_migrations(conn) == {1, 2}


def test_discover_migrations_skips_non_matching_files(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "0001_first.sql").write_text("CREATE TABLE a (id INTEGER);")
    (migrations_dir / "README.md").write_text("not a migration")
    (migrations_dir / ".gitkeep").touch()
    (migrations_dir / "noprefix.sql").write_text("-- ignored")

    discovered = discover_migrations(migrations_dir)
    assert [m.number for m in discovered] == [1]


def test_discover_migrations_rejects_duplicate_numbers(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "0001_a.sql").write_text("CREATE TABLE a (id INTEGER);")
    (migrations_dir / "0001_b.sql").write_text("CREATE TABLE b (id INTEGER);")

    with pytest.raises(ValueError, match="Duplicate migration number 1"):
        discover_migrations(migrations_dir)


def test_failed_migration_rolls_back_and_is_not_recorded(tmp_path: Path) -> None:
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "0001_good.sql").write_text(
        "CREATE TABLE good (id INTEGER PRIMARY KEY);"
    )
    (migrations_dir / "0002_bad.sql").write_text("THIS IS NOT VALID SQL;")

    conn = connect(tmp_path / "test.db")
    with pytest.raises(Exception):
        apply_migrations(conn, migrations_dir)

    # 0001 stuck, 0002 didn't
    assert applied_migrations(conn) == {1}
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='good'"
    ).fetchone()
    assert row is not None
