"""Minimal Cooklang emitter — canonical body format per D4 Q4.2.

The spec (github.com/cooklang/spec) defines a plain-text recipe format with
structured markers: ``@ingredient{qty%unit}``, ``#cookware{}``,
``~timer{n%unit}``, ``>> key: value`` metadata, ``-- comment``. This module
emits a small subset sufficient for the sub-commit 4.1 seed corpus (title +
servings + source metadata, ingredient list, narrated instructions). More
sophisticated emission (step-ingredient linking, timers, cookware tags) can
land alongside adapters that expose that structure.

The emitter is deliberately lossless-adjacent for the fields we have and
lossy for the fields we don't: TheMealDB (and PG Bookshelf 419) do not
expose per-step ingredient linkage, so ingredients are declared once at the
top and instructions are emitted as narrative paragraphs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Ingredient:
    """One row from the source recipe's ingredient list.

    ``quantity`` and ``unit`` are strings so that fractional / textual
    measures like ``"3/4"`` or ``"to taste"`` survive round-trip without
    forcing premature numeric parsing.
    """

    name: str
    quantity: str = ""
    unit: str = ""


@dataclass(frozen=True)
class Recipe:
    """The minimal structured shape we emit as Cooklang."""

    title: str
    ingredients: tuple[Ingredient, ...]
    steps: tuple[str, ...]
    servings: int | None = None
    source_url: str = ""
    attribution: str = ""
    extra_metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


_MEASURE_SPLIT = re.compile(r"^([\d./\-\s]+?)\s+(.+)$")


def split_measure(measure: str) -> tuple[str, str]:
    """Return ``(quantity, unit)`` parsed from a source measure string.

    Handles the common TheMealDB shapes: ``"3/4 cup"`` → ``("3/4", "cup")``;
    ``"2"`` → ``("2", "")``; ``"to taste"`` → ``("to taste", "")``;
    ``""`` → ``("", "")``.
    """
    m = measure.strip()
    if not m:
        return ("", "")
    match = _MEASURE_SPLIT.match(m)
    if match:
        return (match.group(1).strip(), match.group(2).strip())
    return (m, "")


# -- combined ingredient-line parsing (bulk-HTML sources) --------------------

_VULGAR_FRACTIONS = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4",
    "⅕": "1/5", "⅖": "2/5", "⅗": "3/5", "⅘": "4/5",
    "⅙": "1/6", "⅚": "5/6", "⅛": "1/8", "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}

_UNIT_WORDS = frozenset({
    "c", "cup", "cups", "tsp", "tsps", "teaspoon", "teaspoons",
    "tbsp", "tbsps", "tablespoon", "tablespoons",
    "lb", "lbs", "pound", "pounds", "oz", "ounce", "ounces",
    "g", "gram", "grams", "kg", "mg", "ml", "l", "liter", "liters",
    "litre", "litres", "qt", "quart", "quarts", "pt", "pint", "pints",
    "gal", "gallon", "gallons", "can", "cans", "package", "packages",
    "pkg", "jar", "jars", "bag", "bags", "box", "boxes", "container",
    "slice", "slices", "clove", "cloves", "pinch", "dash",
    "stalk", "stalks", "sprig", "sprigs", "head", "heads",
    "bunch", "bunches", "piece", "pieces", "stick", "sticks",
})

_QTY_LEAD = re.compile(
    r"^((?:\d+\s+\d+/\d+)|(?:\d+/\d+)|(?:\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?))\s+(.+)$"
)


def normalize_fractions(text: str) -> str:
    """Expand unicode vulgar fractions: ``"1½ lb"`` → ``"1 1/2 lb"``."""
    out = text
    for char, ascii_frac in _VULGAR_FRACTIONS.items():
        out = out.replace(char, f" {ascii_frac}")
    return re.sub(r"\s+", " ", out).strip()


def split_ingredient_line(line: str) -> tuple[str, str, str]:
    """Parse a combined line → ``(quantity, unit, name)``.

    Bulk-HTML sources (NHLBI, MyPlate) ship one flattened string per
    ingredient — ``"1½ lb salmon fillet"`` → ``("1 1/2", "lb",
    "salmon fillet")``; lines with no leading quantity (``"Cooking
    spray"``) come back as name-only.
    """
    text = normalize_fractions(line)
    if not text:
        return ("", "", "")
    match = _QTY_LEAD.match(text)
    if not match:
        return ("", "", text)
    qty, rest = match.group(1), match.group(2).strip()
    first, _, remainder = rest.partition(" ")
    if first.strip(".,()").lower() in _UNIT_WORDS and remainder.strip():
        return (qty, first.strip(".,"), remainder.strip())
    return (qty, "", rest)


def _emit_ingredient(ingredient: Ingredient) -> str:
    name = ingredient.name.strip()
    qty = ingredient.quantity.strip()
    unit = ingredient.unit.strip()
    if not qty and not unit:
        # Single-word ingredients don't need braces per Cooklang spec;
        # multi-word ingredients need them to delimit the name.
        if " " in name:
            return f"@{name}{{}}"
        return f"@{name}"
    if qty and unit:
        return f"@{name}{{{qty}%{unit}}}"
    if qty:
        return f"@{name}{{{qty}}}"
    return f"@{name}{{%{unit}}}"


def emit_cooklang(recipe: Recipe) -> str:
    """Serialize a :class:`Recipe` to canonical Cooklang text."""
    lines: list[str] = []
    lines.append(f">> title: {recipe.title}")
    if recipe.servings is not None:
        lines.append(f">> servings: {recipe.servings}")
    if recipe.source_url:
        lines.append(f">> source: {recipe.source_url}")
    if recipe.attribution:
        lines.append(f">> attribution: {recipe.attribution}")
    for key, value in recipe.extra_metadata:
        lines.append(f">> {key}: {value}")

    lines.append("")
    lines.append("-- Ingredients")
    lines.append("")
    if recipe.ingredients:
        for ingredient in recipe.ingredients:
            lines.append(_emit_ingredient(ingredient))
    else:
        lines.append("-- (no ingredients recorded at ingest)")

    lines.append("")
    lines.append("-- Instructions")
    lines.append("")
    if recipe.steps:
        for step in recipe.steps:
            text = step.strip()
            if not text:
                continue
            lines.append(text)
            lines.append("")
    else:
        lines.append("-- (no instructions recorded at ingest)")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
