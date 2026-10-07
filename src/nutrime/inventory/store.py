"""Inventory item dataclass + CRUD helpers.

The schema check enforces that quantity + unit are set together or both NULL
(``CHECK ((quantity IS NULL) = (unit IS NULL))``); the dataclass mirrors that
invariant in Python so callers get a clean error before hitting the DB.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from nutrime.db import maybe_commit
from nutrime.tenancy import _now_iso


class Location(StrEnum):
    PANTRY = "pantry"
    FRIDGE = "fridge"
    FREEZER = "freezer"
    COUNTERTOP = "countertop"


class Unit(StrEnum):
    # Mass
    GRAM = "g"
    KILOGRAM = "kg"
    OUNCE = "oz"
    POUND = "lb"
    # Volume
    MILLILITER = "ml"
    LITER = "L"
    FLUID_OUNCE = "fl_oz"
    CUP = "cup"
    TABLESPOON = "tbsp"
    TEASPOON = "tsp"
    # Discrete
    COUNT = "count"


_LOCATIONS = frozenset(loc.value for loc in Location)
_UNITS = frozenset(unit.value for unit in Unit)
_DATE_LEN = len("YYYY-MM-DD")


@dataclass(frozen=True)
class InventoryItem:
    name: str
    location: str
    quantity: float | None = None
    unit: str | None = None
    best_by_date: str | None = None
    notes: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be blank")
        if self.location not in _LOCATIONS:
            raise ValueError(
                f"location {self.location!r} not in {sorted(_LOCATIONS)}"
            )
        if (self.quantity is None) != (self.unit is None):
            raise ValueError(
                "quantity and unit must be set together or both left blank"
            )
        if self.quantity is not None and self.quantity < 0:
            raise ValueError("quantity must be non-negative")
        if self.unit is not None and self.unit not in _UNITS:
            raise ValueError(f"unit {self.unit!r} not in {sorted(_UNITS)}")
        if self.best_by_date is not None:
            if (
                len(self.best_by_date) != _DATE_LEN
                or self.best_by_date[4] != "-"
                or self.best_by_date[7] != "-"
                or not (
                    self.best_by_date[:4].isdigit()
                    and self.best_by_date[5:7].isdigit()
                    and self.best_by_date[8:].isdigit()
                )
            ):
                raise ValueError(
                    f"best_by_date {self.best_by_date!r} not ISO 8601 YYYY-MM-DD"
                )


def add_item(
    conn: sqlite3.Connection, tenant_id: str, item: InventoryItem
) -> int:
    # Enforced at the store seam so every caller (web single add, bulk
    # paste, CLI capture) honors the Privacy toggle — declining "Kitchen
    # inventory" used to change nothing (2026-10-06 audit).
    from nutrime.consent import require_consent

    require_consent(conn, tenant_id, "inventory")
    now = _now_iso()
    cursor = conn.execute(
        """
        INSERT INTO inventory_item (
            tenant_id, name, location, quantity, unit,
            best_by_date, notes, added_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            tenant_id,
            item.name,
            item.location,
            item.quantity,
            item.unit,
            item.best_by_date,
            item.notes,
            now,
            now,
        ),
    )
    maybe_commit(conn)
    return int(cursor.lastrowid)


def list_items(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    location: str | None = None,
) -> list[InventoryItem]:
    query = (
        "SELECT id, name, location, quantity, unit, best_by_date, notes"
        " FROM inventory_item WHERE tenant_id = ?"
    )
    params: tuple = (tenant_id,)
    if location is not None:
        query += " AND location = ?"
        params = (tenant_id, location)
    query += " ORDER BY location, name"
    rows = conn.execute(query, params).fetchall()
    return [
        InventoryItem(
            id=row[0],
            name=row[1],
            location=row[2],
            quantity=row[3],
            unit=row[4],
            best_by_date=row[5],
            notes=row[6],
        )
        for row in rows
    ]


EXPIRING_WINDOW_DAYS = 4


def expiring_names(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    today: str,
    window_days: int = EXPIRING_WINDOW_DAYS,
) -> list[InventoryItem]:
    """Items whose best_by_date falls within the window (V2 use-it-up).

    ``today`` is ISO YYYY-MM-DD; string comparison is safe for ISO dates.
    Past-due items are EXCLUDED (#55): everything returned here is
    promoted toward meal plans, and an expired perishable must never be
    a use-it-up candidate. Expired items are ``expired_names`` —
    surfaced as "probably toss", never cooked.
    """
    from datetime import date, timedelta

    limit = (date.fromisoformat(today) + timedelta(days=window_days)).isoformat()
    return [
        item
        for item in list_items(conn, tenant_id)
        if item.best_by_date is not None and today <= item.best_by_date <= limit
    ]


def expired_names(
    conn: sqlite3.Connection, tenant_id: str, *, today: str
) -> list[InventoryItem]:
    """Items past their best-by date — "probably toss" (#55). These are
    kept out of every cooking surface; the UI offers discard instead."""
    return [
        item
        for item in list_items(conn, tenant_id)
        if item.best_by_date is not None and item.best_by_date < today
    ]


def staples_out(conn: sqlite3.Connection, tenant_id: str) -> frozenset[str]:
    """Staples the household marked as out of stock — search counts
    these as missing again (pantry-first ranking escape hatch)."""
    return frozenset(
        row[0]
        for row in conn.execute(
            "SELECT name FROM staple_out WHERE tenant_id = ?", (tenant_id,)
        ).fetchall()
    )


def set_staple_out(
    conn: sqlite3.Connection, tenant_id: str, name: str, out: bool
) -> None:
    name = name.strip().lower()
    if not name:
        raise ValueError("staple name must not be blank")
    if out:
        conn.execute(
            "INSERT OR IGNORE INTO staple_out (tenant_id, name, marked_at)"
            " VALUES (?, ?, ?)",
            (tenant_id, name, _now_iso()),
        )
    else:
        conn.execute(
            "DELETE FROM staple_out WHERE tenant_id = ? AND name = ?",
            (tenant_id, name),
        )
    maybe_commit(conn)


def remove_items_by_name(
    conn: sqlite3.Connection, tenant_id: str, names: list[str]
) -> list[str]:
    """Presence-level consumption: delete items matching the given names
    (case-insensitive exact). Returns the names actually removed (V2 cook
    decrement — caller confirms the list with the user first)."""
    removed: list[str] = []
    for item in list_items(conn, tenant_id):
        if any(item.name.lower() == n.strip().lower() for n in names):
            conn.execute(
                "DELETE FROM inventory_item WHERE tenant_id = ? AND id = ?",
                (tenant_id, item.id),
            )
            removed.append(item.name)
    maybe_commit(conn)
    return removed


def remove_item(
    conn: sqlite3.Connection, tenant_id: str, item_id: int
) -> bool:
    cursor = conn.execute(
        "DELETE FROM inventory_item WHERE tenant_id = ? AND id = ?",
        (tenant_id, item_id),
    )
    maybe_commit(conn)
    return cursor.rowcount > 0


def update_item(
    conn: sqlite3.Connection,
    tenant_id: str,
    item_id: int,
    *,
    quantity: float | None = None,
    unit: str | None = None,
    best_by_date: str | None = None,
    notes: str | None = None,
) -> bool:
    """Update mutable fields; unspecified fields left untouched.

    Passing an explicit ``None`` for ``quantity``/``unit`` is not supported
    here since the schema pairs them — use :func:`add_item` after
    :func:`remove_item` to fully re-shape an entry.
    """
    fields: list[str] = []
    values: list = []
    if quantity is not None:
        fields.append("quantity = ?")
        values.append(quantity)
    if unit is not None:
        fields.append("unit = ?")
        values.append(unit)
    if best_by_date is not None:
        fields.append("best_by_date = ?")
        values.append(best_by_date)
    if notes is not None:
        fields.append("notes = ?")
        values.append(notes)
    if not fields:
        return False
    fields.append("updated_at = ?")
    values.append(_now_iso())
    values.extend([tenant_id, item_id])
    cursor = conn.execute(
        f"UPDATE inventory_item SET {', '.join(fields)}"
        " WHERE tenant_id = ? AND id = ?",
        values,
    )
    maybe_commit(conn)
    return cursor.rowcount > 0


def by_location(
    items: Iterable[InventoryItem],
) -> dict[str, list[InventoryItem]]:
    grouped: dict[str, list[InventoryItem]] = {}
    for item in items:
        grouped.setdefault(item.location, []).append(item)
    return grouped
