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
