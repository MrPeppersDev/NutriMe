"""Unit vocabulary + the curated conversion table (6.1, sweep #16 §2).

Mealie's load-bearing insight, adopted wholesale as design (and
reimplemented from scratch): DON'T build a units engine. A small
hand-curated table of convertible units per dimension, everything else
deliberately non-convertible, and a merge gate that refuses rather than
guesses. "2 cans" + "400 g" is two honest lines, never one wrong one.

The standardization mapping is a pure function of normalized unit name
(their migration-replayable design), so it needs no storage.
"""

from __future__ import annotations

from dataclasses import dataclass

# -- vocabulary: canonical key → aliases -------------------------------------

_ALIASES: dict[str, tuple[str, ...]] = {
    "tsp": ("tsp", "teaspoon", "teaspoons", "t"),
    "tbsp": ("tbsp", "tablespoon", "tablespoons", "tbs", "tbl"),
    "cup": ("cup", "cups", "c"),
    "fl_oz": ("fl oz", "fluid ounce", "fluid ounces", "fl. oz."),
    "pint": ("pint", "pints", "pt"),
    "quart": ("quart", "quarts", "qt"),
    "gallon": ("gallon", "gallons", "gal"),
    "ml": ("ml", "milliliter", "milliliters", "millilitre", "millilitres"),
    "l": ("l", "liter", "liters", "litre", "litres"),
    "g": ("g", "gram", "grams", "gr"),
    "kg": ("kg", "kilogram", "kilograms", "kilo", "kilos"),
    "mg": ("mg", "milligram", "milligrams"),
    "oz": ("oz", "ounce", "ounces", "oz."),
    "lb": ("lb", "lbs", "pound", "pounds", "lb."),
    # Deliberately non-convertible (count-ish / vague):
    "can": ("can", "cans", "tin", "tins"),
    "bunch": ("bunch", "bunches"),
    "clove": ("clove", "cloves"),
    "head": ("head", "heads"),
    "pinch": ("pinch", "pinches"),
    "dash": ("dash", "dashes"),
    "splash": ("splash", "splashes"),
    "sprig": ("sprig", "sprigs"),
    "slice": ("slice", "slices"),
    "piece": ("piece", "pieces"),
    "pack": ("pack", "packs", "package", "packages", "packet", "packets"),
    "stick": ("stick", "sticks"),
    "serving": ("serving", "servings"),
}

_LOOKUP: dict[str, str] = {}
for key, aliases in _ALIASES.items():
    for alias in aliases:
        _LOOKUP[alias] = key


def normalize_token(token: str) -> str:
    return token.strip().strip(".,").lower()


def find_unit(token: str) -> str | None:
    """Canonical unit key for a token, or None (dictionary-first, no fuzz —
    per-field threshold discipline from sweep #16: units get alias lookup,
    foods get conservative normalization, nothing fuzzy at MVP)."""
    return _LOOKUP.get(normalize_token(token))


# -- the curated conversion table ---------------------------------------------
# (factor, base) per convertible unit; base per dimension: ml / g.

_VOLUME_ML: dict[str, float] = {
    "tsp": 4.92892,
    "tbsp": 14.7868,
    "fl_oz": 29.5735,
    "cup": 236.588,
    "pint": 473.176,
    "quart": 946.353,
    "gallon": 3785.41,
    "ml": 1.0,
    "l": 1000.0,
}

_MASS_G: dict[str, float] = {
    "mg": 0.001,
    "g": 1.0,
    "kg": 1000.0,
    "oz": 28.3495,
    "lb": 453.592,
}

# Display preference: larger units first per dimension (render "2.5 cups",
# never "591 ml of milk" when cups were the input family — sweep #16 §2).
_DISPLAY_ORDER_VOLUME = ("gallon", "quart", "pint", "cup", "fl_oz", "tbsp", "tsp", "l", "ml")
_DISPLAY_ORDER_MASS = ("lb", "kg", "oz", "g", "mg")


def dimension(unit_key: str) -> str | None:
    """"volume" / "mass" / None (non-convertible or unitless)."""
    if unit_key in _VOLUME_ML:
        return "volume"
    if unit_key in _MASS_G:
        return "mass"
    return None


def resolve_oz_ambiguity(unit_a: str, unit_b: str) -> tuple[str, str]:
    """Recipe authors write "oz" meaning fl oz for liquids: when a mass-oz
    meets a volume unit, reinterpret the oz as fl_oz (sweep #16 hardcoded
    rule — the one conversion guess that's right more often than wrong)."""
    if unit_a == "oz" and dimension(unit_b) == "volume":
        return ("fl_oz", unit_b)
    if unit_b == "oz" and dimension(unit_a) == "volume":
        return (unit_a, "fl_oz")
    return (unit_a, unit_b)


def to_base(quantity: float, unit_key: str) -> tuple[float, str] | None:
    """(amount in base unit, dimension) or None if non-convertible."""
    if unit_key in _VOLUME_ML:
        return (quantity * _VOLUME_ML[unit_key], "volume")
    if unit_key in _MASS_G:
        return (quantity * _MASS_G[unit_key], "mass")
    return None


@dataclass(frozen=True)
class DisplayQuantity:
    quantity: float
    unit: str


def best_display(base_amount: float, dim: str, prefer_units: tuple[str, ...]) -> DisplayQuantity:
    """Render a base amount in the most readable unit.

    Try the units the inputs used (largest first); pick the first giving a
    quantity >= 1. Falls back to the smallest input unit.
    """
    table = _VOLUME_ML if dim == "volume" else _MASS_G
    order = _DISPLAY_ORDER_VOLUME if dim == "volume" else _DISPLAY_ORDER_MASS
    candidates = [u for u in order if u in prefer_units] or [
        u for u in order if u in table
    ]
    for unit in candidates:
        value = base_amount / table[unit]
        if value >= 1:
            return DisplayQuantity(quantity=round(value, 2), unit=unit)
    unit = candidates[-1]
    return DisplayQuantity(
        quantity=round(base_amount / table[unit], 2), unit=unit
    )
