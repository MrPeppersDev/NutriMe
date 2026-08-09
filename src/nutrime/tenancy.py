"""F9 multi-tenant typed query helper and tenant bootstrap.

Per ``research/00-meta/schema.md`` F9 (multi-tenant ``tenant_id`` axis,
resolved 2026-06-29):

- :func:`tenant_where` returns a parameterized WHERE-clause fragment enforcing
  the F9 Q1 + Q4 isolation rule — ``tenant_id = ?`` for per-tenant rows, or
  ``tenant_id = ? OR is_global = TRUE`` when cross-tenant globals are
  surfaced. Callers compose this into a larger SELECT against any
  tenant-scoped table.
- :func:`bootstrap_tenant` writes a single tenant row on first install with a
  locally-generated UUID per F9 Q2 (no hardcoded ``'default'`` literal that
  would collide on syndication). Idempotent — checks for an existing row
  before inserting; raises on multi-tenant state because that path uses
  explicit tenant creation rather than bootstrap.

Lifecycle event integration with ``op_event_log`` (F9 Q3) landed with the
operational baseline (sub-commit 5.1): :meth:`nutrime.audit.AuditLog.\
ensure_tenant_created` records the ``tenant_created`` event idempotently from
``app.initialize()``, which also backfills any tenant row bootstrapped before
5.1.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone


def tenant_where(
    tenant_id: str, *, include_global: bool = False
) -> tuple[str, tuple[str, ...]]:
    if include_global:
        return "(tenant_id = ? OR is_global = TRUE)", (tenant_id,)
    return "tenant_id = ?", (tenant_id,)


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def bootstrap_tenant(
    conn: sqlite3.Connection,
    name: str = "Default Household",
    *,
    owner_user_id: str | None = None,
) -> str:
    rows = conn.execute("SELECT id FROM tenant").fetchall()
    if len(rows) == 1:
        return rows[0][0]
    if len(rows) > 1:
        raise RuntimeError(
            f"bootstrap_tenant called with {len(rows)} existing tenants; "
            "multi-tenant install uses explicit tenant creation, not bootstrap."
        )
    tenant_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO tenant (id, name, created_at, status, owner_user_id)"
        " VALUES (?, ?, ?, 'active', ?)",
        (tenant_id, name, _now_iso(), owner_user_id),
    )
    conn.commit()
    return tenant_id
