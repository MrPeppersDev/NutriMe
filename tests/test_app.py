import uuid
from pathlib import Path

import pytest

from nutrime.app import initialize

SUBSTRATE_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "substrate"
OPERATIONAL_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "operational"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    return tmp_path / "nutrime-data"


def test_initialize_creates_data_dir_and_dbs(data_dir: Path) -> None:
    app = initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )

    assert data_dir.is_dir()
    assert (data_dir / "substrate.db").is_file()
    assert (data_dir / "operational.db").is_file()
    assert app.data_dir == data_dir


def test_initialize_returns_real_uuid_tenant_id(data_dir: Path) -> None:
    app = initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )

    uuid.UUID(app.tenant_id)


def test_initialize_applies_substrate_migrations(data_dir: Path) -> None:
    app = initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )

    applied = app.substrate.execute(
        "SELECT number FROM schema_migrations"
    ).fetchall()
    assert (1,) in applied


def test_initialize_tracks_operational_migrations_independently(
    data_dir: Path,
) -> None:
    """S12: each DB owns its own schema_migrations table."""
    app = initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )

    op_table = app.operational.execute(
        "SELECT name FROM sqlite_master"
        " WHERE type = 'table' AND name = 'schema_migrations'"
    ).fetchone()
    assert op_table is not None


def test_initialize_is_idempotent(data_dir: Path) -> None:
    first = initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )
    first.substrate.close()
    first.operational.close()

    second = initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )

    assert second.tenant_id == first.tenant_id
    tenant_count = second.substrate.execute(
        "SELECT COUNT(*) FROM tenant"
    ).fetchone()[0]
    assert tenant_count == 1
