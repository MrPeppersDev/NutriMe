import sqlite3
import uuid
from pathlib import Path

import pytest

from nutrime.db import apply_migrations, connect
from nutrime.tenancy import bootstrap_tenant, tenant_where

SUBSTRATE_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "substrate"


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    c = connect(tmp_path / "test.db")
    apply_migrations(c, SUBSTRATE_MIGRATIONS)
    return c


def test_tenant_where_per_tenant() -> None:
    clause, params = tenant_where("t-123")
    assert clause == "tenant_id = ?"
    assert params == ("t-123",)


def test_tenant_where_include_global() -> None:
    clause, params = tenant_where("t-123", include_global=True)
    assert clause == "(tenant_id = ? OR is_global = TRUE)"
    assert params == ("t-123",)


def test_bootstrap_tenant_creates_row_on_first_call(
    conn: sqlite3.Connection,
) -> None:
    tenant_id = bootstrap_tenant(conn, name="Smith Household")

    row = conn.execute(
        "SELECT id, name, status FROM tenant WHERE id = ?", (tenant_id,)
    ).fetchone()
    assert row == (tenant_id, "Smith Household", "active")


def test_bootstrap_tenant_is_idempotent(conn: sqlite3.Connection) -> None:
    first = bootstrap_tenant(conn, name="Default Household")
    second = bootstrap_tenant(conn, name="Different Name")
    assert first == second

    count = conn.execute("SELECT COUNT(*) FROM tenant").fetchone()[0]
    assert count == 1


def test_bootstrap_tenant_uses_real_uuid_not_literal(
    conn: sqlite3.Connection,
) -> None:
    """Per F9 Q2 — no hardcoded 'default' literal that would collide on syndication."""
    tenant_id = bootstrap_tenant(conn)
    assert tenant_id != "default"
    uuid.UUID(tenant_id)


def test_bootstrap_tenant_raises_on_multi_tenant_state(
    conn: sqlite3.Connection,
) -> None:
    conn.execute(
        "INSERT INTO tenant (id, name, created_at, status)"
        " VALUES ('t-a', 'A', '2026-01-01T00:00:00.000Z', 'active')"
    )
    conn.execute(
        "INSERT INTO tenant (id, name, created_at, status)"
        " VALUES ('t-b', 'B', '2026-01-01T00:00:00.000Z', 'active')"
    )
    conn.commit()

    with pytest.raises(RuntimeError, match="multi-tenant install"):
        bootstrap_tenant(conn)


def test_tenant_status_check_constraint_rejects_unknown_status(
    conn: sqlite3.Connection,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO tenant (id, name, created_at, status)"
            " VALUES ('t-x', 'X', '2026-01-01T00:00:00.000Z', 'bogus')"
        )
