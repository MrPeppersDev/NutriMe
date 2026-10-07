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


def test_multi_statement_migration_is_all_or_nothing(tmp_path: Path) -> None:
    """2026-10-06 audit: executescript auto-committed as it went, so a
    failing later statement left earlier ones applied — and an ADD COLUMN
    migration then failed forever on retry ("duplicate column")."""
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "0001_base.sql").write_text(
        "CREATE TABLE t (id INTEGER PRIMARY KEY);"
    )
    # Second statement fails; the ADD COLUMN before it must roll back.
    (migrations_dir / "0002_crashy.sql").write_text(
        "ALTER TABLE t ADD COLUMN extra TEXT;\n"
        "INSERT INTO nope VALUES (1);\n"
    )

    conn = connect(tmp_path / "test.db")
    with pytest.raises(Exception):
        apply_migrations(conn, migrations_dir)
    assert applied_migrations(conn) == {1}
    columns = [r[1] for r in conn.execute("PRAGMA table_info(t)")]
    assert "extra" not in columns  # rolled back with its migration

    # The retry after "the crash is fixed" applies cleanly — this is the
    # exact path that used to brick with "duplicate column: extra".
    (migrations_dir / "0002_crashy.sql").write_text(
        "ALTER TABLE t ADD COLUMN extra TEXT;"
    )
    applied = apply_migrations(conn, migrations_dir)
    assert [m.number for m in applied] == [2]
    columns = [r[1] for r in conn.execute("PRAGMA table_info(t)")]
    assert "extra" in columns


def test_transaction_scope_commits_and_rolls_back(tmp_path: Path) -> None:
    from nutrime.db import transaction

    conn = connect(tmp_path / "test.db")
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
    conn.commit()

    with transaction(conn):
        conn.execute("INSERT INTO t VALUES (1)")
    assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1

    with pytest.raises(RuntimeError):
        with transaction(conn):
            conn.execute("INSERT INTO t VALUES (2)")
            raise RuntimeError("crash mid-write")
    assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1


def test_transaction_nesting_outer_owns_commit(tmp_path: Path) -> None:
    from nutrime.db import maybe_commit, transaction

    conn = connect(tmp_path / "test.db")
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
    conn.commit()

    with pytest.raises(RuntimeError):
        with transaction(conn):
            conn.execute("INSERT INTO t VALUES (1)")
            with transaction(conn):  # inner scope joins, doesn't commit
                conn.execute("INSERT INTO t VALUES (2)")
            maybe_commit(conn)  # store-helper style: no-op inside scope
            raise RuntimeError("crash after inner scope closed")
    # Nothing committed: the outer scope owned the whole write.
    assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0


def test_concurrent_bootstrap_tenant_single_row(tmp_path: Path) -> None:
    """2026-10-06 audit (reproduced): two processes initializing together
    each saw zero tenants and both inserted — after which every startup
    failed forever. BEGIN IMMEDIATE serializes the check-then-insert."""
    import subprocess
    import sys

    script = f"""
import sys
sys.path.insert(0, {str(Path(__file__).resolve().parent.parent / "src")!r})
from nutrime.app import initialize
from pathlib import Path
app = initialize(data_dir=Path({str(tmp_path / "data")!r}))
print(app.tenant_id)
app.substrate.close()
app.operational.close()
"""
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", script],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        for _ in range(4)
    ]
    outs = [p.communicate(timeout=120) for p in procs]
    for p, (out, err) in zip(procs, outs):
        assert p.returncode == 0, err
    tenant_ids = {out.strip() for out, _ in outs}
    assert len(tenant_ids) == 1  # every process agreed on one tenant

    conn = connect(tmp_path / "data" / "substrate.db")
    assert conn.execute("SELECT COUNT(*) FROM tenant").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM member").fetchone()[0] == 1


def test_atomic_write_no_partial_file(tmp_path: Path) -> None:
    """One truncated .md used to take down every corpus iteration."""
    from unittest import mock

    from nutrime.fsio import atomic_write_text

    target = tmp_path / "doc.md"
    atomic_write_text(target, "complete document\n")
    assert target.read_text() == "complete document\n"

    # Crash mid-write: the original must survive untouched, no temp left.
    with mock.patch("os.replace", side_effect=OSError("crash")):
        with pytest.raises(OSError):
            atomic_write_text(target, "half-written")
    assert target.read_text() == "complete document\n"
    assert list(tmp_path.glob("*.tmp")) == []
