"""Interactive add-many inventory capture — I/O-parameterized for testability.

Ergonomic default per intake-pattern.md § "Quantity precision: loose by
default": name + location are required, quantity + unit + best-by + notes are
skippable. Session runs add-then-continue until the user opts out.
"""

from __future__ import annotations

import sqlite3
from typing import Callable

from nutrime.inventory.store import (
    InventoryItem,
    Location,
    Unit,
    add_item,
)

Prompter = Callable[[str], str]
Emitter = Callable[[str], None]


def _ask_choice(
    prompter: Prompter, emitter: Emitter, prompt: str, choices: tuple[str, ...]
) -> str:
    while True:
        emitter(prompt)
        for i, choice in enumerate(choices, start=1):
            emitter(f"  {i}) {choice}")
        raw = prompter("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        if raw in choices:
            return raw
        emitter(f"Please pick a number 1–{len(choices)} or one of the labels.")


def _ask_yes_no(prompter: Prompter, emitter: Emitter, prompt: str) -> bool:
    while True:
        emitter(prompt + " [y/n]")
        raw = prompter("> ").strip().lower()
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no", ""}:
            return False
        emitter("Please answer y or n.")


def _ask_optional_str(
    prompter: Prompter, emitter: Emitter, prompt: str
) -> str | None:
    emitter(prompt + " (leave blank to skip)")
    raw = prompter("> ").strip()
    return raw or None


def _ask_optional_float(
    prompter: Prompter,
    emitter: Emitter,
    prompt: str,
    *,
    minimum: float,
) -> float | None:
    while True:
        emitter(prompt + " (leave blank for loose — 'I just have some')")
        raw = prompter("> ").strip()
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError:
            emitter(f"Please enter a number ≥ {minimum} or leave blank.")
            continue
        if value < minimum:
            emitter(f"Value must be ≥ {minimum}.")
            continue
        return value


def _ask_date(
    prompter: Prompter, emitter: Emitter, prompt: str
) -> str | None:
    while True:
        emitter(prompt + " (YYYY-MM-DD; leave blank to skip)")
        raw = prompter("> ").strip()
        if not raw:
            return None
        if (
            len(raw) == 10
            and raw[4] == "-"
            and raw[7] == "-"
            and raw[:4].isdigit()
            and raw[5:7].isdigit()
            and raw[8:].isdigit()
        ):
            return raw
        emitter("Please enter a date as YYYY-MM-DD or leave blank.")


_LOCATIONS = tuple(loc.value for loc in Location)
_UNITS = tuple(unit.value for unit in Unit)


def _capture_one(prompter: Prompter, emitter: Emitter) -> InventoryItem:
    while True:
        emitter("Item name:")
        name = prompter("> ").strip()
        if name:
            break
        emitter("Name cannot be blank.")

    location = _ask_choice(prompter, emitter, "Where is it stored?", _LOCATIONS)

    quantity = _ask_optional_float(
        prompter, emitter, f"How much {name} do you have?", minimum=0
    )
    unit: str | None = None
    if quantity is not None:
        unit = _ask_choice(prompter, emitter, "Unit:", _UNITS)

    best_by = _ask_date(prompter, emitter, "Best-by date?")
    notes = _ask_optional_str(prompter, emitter, "Notes?")

    return InventoryItem(
        name=name,
        location=location,
        quantity=quantity,
        unit=unit,
        best_by_date=best_by,
        notes=notes,
    )


def capture_items(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    prompter: Prompter,
    emitter: Emitter = print,
) -> list[InventoryItem]:
    """Add-many session; returns items added (with populated ids)."""
    emitter(
        "Inventory capture — pantry / fridge / freezer. Add items one at a"
        " time; you can leave quantity blank if you just want to note that"
        " you have it."
    )
    added: list[InventoryItem] = []
    while True:
        item = _capture_one(prompter, emitter)
        item_id = add_item(conn, tenant_id, item)
        added.append(
            InventoryItem(
                id=item_id,
                name=item.name,
                location=item.location,
                quantity=item.quantity,
                unit=item.unit,
                best_by_date=item.best_by_date,
                notes=item.notes,
            )
        )
        emitter(f"Added {item.name!r} to {item.location}.")
        if not _ask_yes_no(prompter, emitter, "Add another item?"):
            break
    emitter(f"Saved {len(added)} item(s).")
    return added
