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
        # #57 gaps (FDA guidance Ed. 5): wheat hiding under other names.
        "breadcrumb", "panko", "bulgur", "farro", "seitan",
        "soy sauce", "udon", "ramen", "orzo", "cracker", "crouton",
    ),
    "dairy": (
        "milk", "cheese", "butter", "cream", "yogurt", "yoghurt",
        "whey", "casein", "ghee",
        # #57 gaps: named cheeses and cultured/derived milk products.
        "buttermilk", "parmesan", "mozzarella", "ricotta", "cheddar",
        "paneer", "kefir", "caseinate", "custard", "feta", "mascarpone",
        "halloumi", "gouda", "brie", "provolone", "pecorino",
    ),
    "eggs": (
        "egg", "eggs", "yolk", "albumen", "meringue",
        # #57 gaps: albumin spelling + egg-based preparations.
        "albumin", "mayonnaise", "mayo", "aioli", "custard",
    ),
    "peanuts": ("peanut", "peanuts", "groundnut"),
    "tree_nuts": (
        "almond", "walnut", "pecan", "cashew", "hazelnut",
        "pistachio", "macadamia", "pine nut", "brazil nut",
        # #57: chestnut removed per FDA 2025 guidance (Edition 5).
        # Preparations and alternate names:
        "pesto", "marzipan", "praline", "filbert", "pignoli",
        "nutella", "nut", "nuts",
    ),
    "soy": ("soy", "tofu", "edamame", "tempeh", "miso", "soybean", "soya"),
    "fish": (
        "salmon", "tuna", "cod", "haddock", "trout",
        "anchovy", "sardine", "mackerel", "tilapia", "fish",
        # #57 gaps: more species + fish-derived preparations.
        "halibut", "pollock", "catfish", "surimi", "bonito", "dashi",
        "worcestershire", "caesar dressing", "bass", "snapper",
        "herring", "swordfish", "flounder", "sole fillet", "mahi",
        "fish sauce",
    ),
    "shellfish": (
        "shrimp", "prawn", "crab", "lobster", "oyster",
        "clam", "mussel", "scallop", "crayfish",
        # Molluscan + further crustacean shellfish (2026-10-07 audit: four
        # live squid recipes carried no shellfish tag — the tag is the only
        # allergen defense, so a gap here defeats the avoid-list outright).
        "squid", "calamari", "octopus", "cuttlefish",
        "cockle", "whelk", "periwinkle", "snail", "abalone",
        "crawfish", "langoustine", "krill",
    ),
    "sesame": (
        "sesame", "tahini",
        # #57 gaps: sesame-based preparations.
        "hummus", "za'atar", "zaatar", "halva", "halvah",
    ),
}

# Phrases stripped before matching — longest first, so "coconut milk"
# disappears as a WHOLE phrase (#57: replacing just "coconut" left
# " milk" behind, which false-flagged dairy).
_EXCLUSIONS: tuple[str, ...] = (
    "coconut milk", "coconut cream", "coconut butter", "coconut yogurt",
    "water chestnut", "eggplant", "coconut", "butternut",
)

# Canonical top-9 allergen names — the vocabulary used by
# ``top_allergens_present`` frontmatter and by search's constraint mapping
# ("avoids shellfish" -> allergen hard-block vs plain ingredient exclusion).
TOP_ALLERGENS: tuple[str, ...] = tuple(_KEYWORDS)


def _boundary_pattern(keyword: str) -> re.Pattern[str]:
    """Word-boundary match tolerating plurals: trailing ``s``/``es``,
    and ``y`` → ``ies`` (#57: "anchovies" missed the "+s"-only rule)."""
    if keyword.endswith("y"):
        escaped = re.escape(keyword[:-1])
        return re.compile(rf"\b{escaped}(y|ies)\b", flags=re.IGNORECASE)
    escaped = re.escape(keyword)
    return re.compile(rf"\b{escaped}(s|es)?\b", flags=re.IGNORECASE)


_COMPILED: dict[str, tuple[re.Pattern[str], ...]] = {
    allergen: tuple(_boundary_pattern(kw) for kw in kws)
    for allergen, kws in _KEYWORDS.items()
}


def _sanitize(name: str) -> str:
    # _EXCLUSIONS is ordered longest-phrase-first so "coconut milk" is
    # removed whole before "coconut" could strand a dairy-flagging "milk".
    lower = name.lower()
    for excl in _EXCLUSIONS:
        lower = lower.replace(excl, " ")
    return lower


# User-facing allergen names → canonical internal labels (#57): "milk",
# "wheat" and "tree nuts" are the FDA's OWN names for three of the nine
# major allergens — exactly what people type. Keys are normalize_term
# shapes (lowercase, singularized).
ALLERGEN_SYNONYMS: dict[str, str] = {
    "milk": "dairy",
    "lactose": "dairy",
    "wheat": "gluten",
    "tree nut": "tree_nuts",
    "nut": "tree_nuts",
    "egg": "eggs",
    "peanut": "peanuts",
    "shrimp": "shellfish",
    "prawn": "shellfish",
    "crustacean": "shellfish",
    "mollusc": "shellfish",
    "mollusk": "shellfish",
    "soya": "soy",
    "soybean": "soy",
}


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
