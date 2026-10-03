"""Ingredient-line parsing for grocery aggregation (6.1).

Pattern per sweep #16 §1 (Mealie's brute parser, reimplemented from the
mechanism description in stdlib): one output shape behind a swappable
backend, dictionary-assisted tokenizing, parentheticals deferred, comma
splits food from note. A smarter (LLM) backend can slot in later without
touching callers — the aggregator only sees :class:`ParsedLine`.

Input here is a Cooklang ``@name{qty%unit}`` line from the vault, which
is already structured — so unlike Mealie we parse *two* layers:
`parse_cooklang_line` reads the structure, then `refine` cleans the
name/qty/unit the structure carries (sources stuff "1 can chopped" into
qty or name fields routinely).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from fractions import Fraction

from nutrime.grocery.units import find_unit

_FOOTNOTE = re.compile(r"\s*\*+\s*$")
_PARENTHETICAL = re.compile(r"\s*\(([^()]*)\)")


@dataclass(frozen=True)
class ParsedLine:
    """One ingredient need, normalized for aggregation.

    ``quantity`` is None for unquantified lines ("salt to taste").
    ``unit`` is the canonical unit key ("" when unitless/count).
    ``food`` is the cleaned food name; ``note`` carries prep/asides.
    Per-field confidence in Mealie's shape (binary at this backend).
    """

    food: str
    quantity: float | None = None
    unit: str = ""
    note: str = ""
    confidence: float = 1.0


def parse_quantity(raw: str) -> float | None:
    """"1 1/2" / "1.5" / "½" / "3-4" (take low end) → float."""
    text = raw.strip()
    if not text:
        return None
    # Unicode vulgar fractions → "n/d" via decomposition ("½" → "1/2";
    # 2044 is the fraction slash). All vulgar fractions are single-digit.
    out: list[str] = []
    for ch in text:
        decomp = unicodedata.decomposition(ch)
        if decomp.startswith("<fraction>"):
            digits = [chr(int(p, 16)) for p in decomp.split()[1:] if p != "2044"]
            if len(digits) == 2:
                out.append(f" {digits[0]}/{digits[1]}")
                continue
        out.append(ch)
    text = "".join(out).strip()
    # Range: take the low end ("3-4 cups" → 3)
    range_match = re.match(r"^(\d+(?:[./]\d+)?)\s*[-–]\s*\d", text)
    if range_match:
        text = range_match.group(1)
    total = 0.0
    found = False
    for token in text.split():
        try:
            if "/" in token:
                total += float(Fraction(token))
            else:
                total += float(token)
            found = True
        except (ValueError, ZeroDivisionError):
            break
    return total if found else None


def refine(name: str, qty: str, unit: str) -> ParsedLine:
    """Clean one structured ingredient into a ParsedLine.

    Handles the dirt real sources leave in structured fields: units
    hiding in the name ("can chopped tomatoes"), notes after commas,
    parentheticals ("flour (sifted)"), footnote asterisks.
    """
    notes: list[str] = []

    text = _FOOTNOTE.sub("", name.strip())
    # Defer parentheticals to the note (sweep #16: move-parens-out trick)
    def _stash(match: re.Match) -> str:
        content = match.group(1).strip()
        if content:
            notes.append(content)
        return " "

    text = _PARENTHETICAL.sub(_stash, text).strip()

    # Comma splits food from prep note ("onion, finely diced")
    if "," in text:
        text, _, trailing = text.partition(",")
        trailing = trailing.strip()
        if trailing:
            notes.append(trailing)
        text = text.strip()

    quantity = parse_quantity(qty)

    unit_key = ""
    unit_match = find_unit(unit)
    if unit_match is not None:
        unit_key = unit_match
    elif unit.strip():
        # Unknown unit string — keep it visible in the note, honesty over
        # silent loss ("heaping scoop").
        notes.append(unit.strip())

    # Unit hiding at the head of the name ("can crushed tomatoes" with
    # qty=1 unit=""): promote it (dictionary-assisted boundary per #16).
    if not unit_key and quantity is not None:
        head, _, rest = text.partition(" ")
        promoted = find_unit(head)
        if promoted is not None and rest.strip():
            unit_key = promoted
            text = rest.strip()
            # "of" connective: "2 cups of flour"
            if text.lower().startswith("of "):
                text = text[3:].strip()

    food = re.sub(r"\s+", " ", text).strip()
    return ParsedLine(
        food=food,
        quantity=quantity,
        unit=unit_key,
        note="; ".join(notes),
        confidence=1.0 if food else 0.0,
    )


_COOKLANG_LINE = re.compile(
    r"^@(?:(?P<braced>[^@{}]+)\{(?P<qty>[^%}]*)%?(?P<unit>[^}]*)\}|(?P<bare>\S+))$"
)


def parse_cooklang_line(line: str) -> ParsedLine | None:
    """Parse one vault body line; None when it isn't an ingredient."""
    match = _COOKLANG_LINE.match(line.strip())
    if not match:
        return None
    if match.group("bare"):
        return refine(match.group("bare"), "", "")
    return refine(
        match.group("braced") or "",
        match.group("qty") or "",
        match.group("unit") or "",
    )


def normalize_food(food: str) -> str:
    """Aggregation key for a food name (sweep #16 normalize-once helper).

    Accent-strip → punctuation→space → lowercase → singularize last word.
    Deliberately conservative: "green onion" and "onion" stay distinct
    (merge-gate discipline — fuzzy merging of foods risks wrong lists).
    """
    text = unicodedata.normalize("NFKD", food).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s]", " ", text).lower()
    words = text.split()
    if words and len(words[-1]) > 3 and words[-1].endswith("s") and not words[-1].endswith("ss"):
        words[-1] = words[-1][:-1]
    return " ".join(words)
