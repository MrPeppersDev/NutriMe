"""Heuristic top-9 allergen detection from raw ingredient names.

MVP-quality substring matcher against the canonical 9-allergen tracking set
per schema.md S9 ``top_allergens_present``. Replaced by ingredient resolution
(S6 two-threshold tier) once the resolver lands — until then, this errs on
the side of over-flagging (safer for Rule 1 clinical gating than under-flagging).

Match rules:
- Word-boundary matches only (``"egg"`` matches ``"egg yolk"`` but not
  ``"eggplant"`` because ``eggplant`` is on the exclusion list).
- Case-insensitive.
- Exclusions cover the two most common false positives (eggplant, coconut).
"""

from __future__ import annotations

import re

_KEYWORDS: dict[str, tuple[str, ...]] = {
    "gluten": (
        "wheat", "flour", "bread", "pasta", "noodle",
        "barley", "rye", "spelt", "semolina", "couscous",
    ),
    "dairy": (
        "milk", "cheese", "butter", "cream", "yogurt", "yoghurt",
        "whey", "casein", "ghee",
    ),
    "eggs": ("egg", "eggs", "yolk", "albumen", "meringue"),
    "peanuts": ("peanut", "peanuts", "groundnut"),
    "tree_nuts": (
        "almond", "walnut", "pecan", "cashew", "hazelnut",
        "pistachio", "macadamia", "chestnut", "pine nut", "brazil nut",
    ),
    "soy": ("soy", "tofu", "edamame", "tempeh", "miso", "soybean", "soya"),
    "fish": (
        "salmon", "tuna", "cod", "haddock", "trout",
        "anchovy", "sardine", "mackerel", "tilapia", "fish",
    ),
    "shellfish": (
        "shrimp", "prawn", "crab", "lobster", "oyster",
        "clam", "mussel", "scallop", "crayfish",
    ),
    "sesame": ("sesame", "tahini"),
}

_EXCLUSIONS: set[str] = {"eggplant", "coconut"}

# Canonical top-9 allergen names — the vocabulary used by
# ``top_allergens_present`` frontmatter and by search's constraint mapping
# ("avoids shellfish" -> allergen hard-block vs plain ingredient exclusion).
TOP_ALLERGENS: tuple[str, ...] = tuple(_KEYWORDS)


def _boundary_pattern(keyword: str) -> re.Pattern[str]:
    """Word-boundary match; accepts an optional trailing ``s`` for plurals."""
    escaped = re.escape(keyword)
    return re.compile(rf"\b{escaped}s?\b", flags=re.IGNORECASE)


_COMPILED: dict[str, tuple[re.Pattern[str], ...]] = {
    allergen: tuple(_boundary_pattern(kw) for kw in kws)
    for allergen, kws in _KEYWORDS.items()
}


def _sanitize(name: str) -> str:
    lower = name.lower()
    for excl in _EXCLUSIONS:
        lower = lower.replace(excl, " ")
    return lower


def detect_allergens(ingredient_names: list[str]) -> list[str]:
    """Return the sorted subset of the canonical 9 allergens present.

    The list is stable for downstream diff-friendly frontmatter output.
    """
    present: set[str] = set()
    for raw in ingredient_names:
        sanitized = _sanitize(raw)
        for allergen, patterns in _COMPILED.items():
            if allergen in present:
                continue
            if any(p.search(sanitized) for p in patterns):
                present.add(allergen)
    return sorted(present)
