"""Grocery-list aggregation (6.1 core) — merge gate + provenance ledger.

Sweep #16 §2 patterns, reimplemented:

- **Merge gate, not conversion engine.** Lines merge only when the
  normalized food matches AND units are identical, or both convertible
  within one dimension via the curated table. Incompatible quantified
  lines for the same food stay separate ("2 cans" + "400 g" = 2 lines).
- **oz/fl-oz disambiguation** before the gate.
- **Provenance ledger**: every aggregated line records which (recipe,
  slot) contributed what, so a plan edit can re-derive the list and the
  user can see why an item is there.
- **Presence-based inventory netting** (the 6.1 scope): an inventory
  item naming the same food marks the line "have", it never deletes it
  — the user decides at the store. Mealie's boolean on-hand suppression
  drops lines silently; surfacing beats suppressing for honesty.
"""

from __future__ import annotations

import re

from dataclasses import dataclass, field
from typing import Iterable

from nutrime.grocery.parse import ParsedLine, normalize_food, parse_cooklang_lines
from nutrime.grocery.units import (
    best_display,
    dimension,
    resolve_oz_ambiguity,
    to_base,
)


@dataclass(frozen=True)
class Contribution:
    """Provenance: one recipe's share of a grocery line."""

    recipe_id: str
    recipe_title: str
    quantity: float | None
    unit: str


@dataclass
class GroceryLine:
    food: str  # display name (first-seen spelling)
    food_key: str  # normalized aggregation key
    quantity: float | None = None  # None = unquantified ("to taste")
    unit: str = ""  # canonical unit key, "" = count/unitless
    base_amount: float | None = None  # running total in base unit
    base_dim: str | None = None  # "volume"/"mass" when converting
    units_seen: tuple[str, ...] = ()
    notes: list[str] = field(default_factory=list)
    contributions: list[Contribution] = field(default_factory=list)
    on_hand: bool = False  # presence-based netting flag


def _merge_into(line: GroceryLine, parsed: ParsedLine, contrib: Contribution) -> bool:
    """Try to merge; False means the caller must open a new line."""
    # Unquantified joins anything for the same food (salt is salt).
    if parsed.quantity is None:
        line.contributions.append(contrib)
        if parsed.note and parsed.note not in line.notes:
            line.notes.append(parsed.note)
        return True
    if line.quantity is None and line.base_amount is None:
        # Line was unquantified so far; adopt this quantity.
        line.quantity, line.unit = parsed.quantity, parsed.unit
        line.units_seen = tuple({*line.units_seen, parsed.unit} - {""}) or line.units_seen
        line.contributions.append(contrib)
        if parsed.note and parsed.note not in line.notes:
            line.notes.append(parsed.note)
        return True

    unit_a, unit_b = resolve_oz_ambiguity(line.unit, parsed.unit)

    # Identical units: plain addition (covers count-ish units too).
    if unit_a == unit_b and line.base_amount is None:
        line.quantity = (line.quantity or 0.0) + parsed.quantity
        line.unit = unit_a
        line.contributions.append(contrib)
        if parsed.note and parsed.note not in line.notes:
            line.notes.append(parsed.note)
        return True

    # Same dimension via the curated table: accumulate in base units.
    incoming = to_base(parsed.quantity, unit_b)
    if incoming is None:
        return False
    if line.base_amount is None:
        existing = to_base(line.quantity or 0.0, unit_a)
        if existing is None or existing[1] != incoming[1]:
            return False
        line.base_amount, line.base_dim = existing
        line.units_seen = tuple({*line.units_seen, unit_a} - {""})
        line.quantity, line.unit = None, ""
    elif line.base_dim != incoming[1]:
        return False
    line.base_amount += incoming[0]
    line.units_seen = tuple({*line.units_seen, unit_b} - {""})
    line.contributions.append(contrib)
    if parsed.note and parsed.note not in line.notes:
        line.notes.append(parsed.note)
    return True


@dataclass(frozen=True)
class RecipeNeed:
    """One recipe's parsed ingredient list, ready for aggregation."""

    recipe_id: str
    title: str
    lines: tuple[ParsedLine, ...]


# Kitchen basics nobody shops for ("warm water", "ice cubes").
_NOT_BOUGHT = re.compile(
    r"(?:(?:warm|cold|hot|boiling|ice|tap|lukewarm|room temperature|filtered)\s+)?"
    r"(?:water|ice|ice cube)"
)


def needs_from_recipe_body(recipe_id: str, title: str, body: str) -> RecipeNeed:
    lines = []
    for raw in body.splitlines():
        # One line can carry several needs ("salt and pepper").
        for parsed in parse_cooklang_lines(raw.strip()):
            if parsed.food:
                lines.append(parsed)
    return RecipeNeed(recipe_id=recipe_id, title=title, lines=tuple(lines))


def aggregate(
    needs: Iterable[RecipeNeed],
    *,
    inventory_names: Iterable[str] = (),
) -> list[GroceryLine]:
    """Fold recipe needs into grocery lines; mark on-hand foods.

    Lines are keyed by normalized food; a food can own several lines when
    quantified units are incompatible (the merge gate refusing to guess).
    """
    lines_by_food: dict[str, list[GroceryLine]] = {}

    for need in needs:
        for parsed in need.lines:
            key = normalize_food(parsed.food)
            if not key or _NOT_BOUGHT.fullmatch(key):
                continue
            contrib = Contribution(
                recipe_id=need.recipe_id,
                recipe_title=need.title,
                quantity=parsed.quantity,
                unit=parsed.unit,
            )
            bucket = lines_by_food.setdefault(key, [])
            for line in bucket:
                if _merge_into(line, parsed, contrib):
                    break
            else:
                new_line = GroceryLine(
                    food=parsed.food,
                    food_key=key,
                    quantity=parsed.quantity,
                    unit=parsed.unit,
                    units_seen=(parsed.unit,) if parsed.unit else (),
                    notes=[parsed.note] if parsed.note else [],
                    contributions=[contrib],
                )
                bucket.append(new_line)

    on_hand_keys = {normalize_food(name) for name in inventory_names}
    out: list[GroceryLine] = []
    for bucket in lines_by_food.values():
        for line in bucket:
            if line.food_key in on_hand_keys:
                line.on_hand = True
            out.append(line)
    out.sort(key=lambda l: (l.on_hand, l.food_key))
    return out


def display_amount(line: GroceryLine) -> str:
    """Human-readable quantity for a line."""
    if line.base_amount is not None and line.base_dim is not None:
        shown = best_display(line.base_amount, line.base_dim, line.units_seen)
        return f"{format_quantity(shown.quantity)} {_unit_label(shown.unit, shown.quantity)}"
    if line.quantity is None:
        return ""
    return f"{format_quantity(line.quantity)} {_unit_label(line.unit, line.quantity)}".strip()


_FRACTIONS = {1 / 8: "⅛", 1 / 4: "¼", 1 / 3: "⅓", 3 / 8: "⅜", 1 / 2: "½",
              5 / 8: "⅝", 2 / 3: "⅔", 3 / 4: "¾", 7 / 8: "⅞"}


def format_quantity(value: float) -> str:
    """Kitchen-readable: 1.5 → "1½", 0.333 → "⅓", 2.0 → "2", 1.37 → "1.4"."""
    whole = int(value)
    frac = value - whole
    if frac < 0.02:
        return str(whole)
    if frac > 0.98:
        return str(whole + 1)
    for amount, glyph in _FRACTIONS.items():
        if abs(frac - amount) < 0.02:
            return f"{whole}{glyph}" if whole else glyph
    return f"{value:.1f}".rstrip("0").rstrip(".")


_PLURAL_UNITS = {"cup": "cups", "clove": "cloves", "can": "cans", "slice": "slices",
                 "sprig": "sprigs", "stalk": "stalks", "head": "heads", "pinch": "pinches",
                 "bunch": "bunches", "stick": "sticks", "jar": "jars", "bag": "bags",
                 "box": "boxes", "bottle": "bottles", "pack": "packs", "piece": "pieces",
                 "handful": "handfuls", "container": "containers"}


def _unit_label(unit: str, quantity: float) -> str:
    label = unit.replace("fl_oz", "fl oz")
    if quantity > 1.02 and unit in _PLURAL_UNITS:
        return _PLURAL_UNITS[unit]
    return label
