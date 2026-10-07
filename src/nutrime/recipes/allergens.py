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

# Compound foods whose dairy-looking word is NOT dairy: "almond milk" is
# almonds, not milk; "peanut butter" is peanuts, not butter. Rewriting to
# the base food (instead of stripping the whole phrase like _EXCLUSIONS)
# keeps the REAL allergen: almond milk must still flag tree_nuts.
# Longest-phrase-first, same discipline as _EXCLUSIONS.
_REWRITES: tuple[tuple[str, str], ...] = (
    ("sweetened condensed coconut milk", "coconut"),
    ("almond milk", "almond"), ("oat milk", "oat"),
    ("soy milk", "soy"), ("soya milk", "soy"),
    ("rice milk", "rice"), ("cashew milk", "cashew"),
    ("hemp milk", "hemp"), ("pea milk", "pea"), ("macadamia milk", "macadamia"),
    ("cashew cream", "cashew"), ("almond cream", "almond"),
    ("oat cream", "oat"), ("soy cream", "soy"),
    ("cashew yogurt", "cashew"), ("almond yogurt", "almond"),
    ("oat yogurt", "oat"), ("soy yogurt", "soy"),
    ("peanut butter", "peanut"), ("almond butter", "almond"),
    ("cashew butter", "cashew"), ("sunflower seed butter", "sunflower"),
    ("sunflower butter", "sunflower"), ("seed butter", "seed"),
    ("nut butter", "nut"), ("cocoa butter", "cocoa"), ("shea butter", "shea"),
    ("apple butter", "apple"), ("pumpkin butter", "pumpkin"),
    ("cream of tartar", "tartar"),
)

# "<word>-free" label → the allergen that label negates. A "-free" claim
# on the NAME is explicit enough to honor even under the over-flagging
# bias: "gluten-free bread" contains no gluten by definition. Lactose is
# deliberately ABSENT — lactose-free milk still carries milk protein
# (casein), which is what a dairy ALLERGY reacts to.
_FREE_NEGATES: dict[str, frozenset[str]] = {
    "gluten": frozenset({"gluten"}),
    "wheat": frozenset({"gluten"}),
    "dairy": frozenset({"dairy"}),
    "milk": frozenset({"dairy"}),
    "casein": frozenset({"dairy"}),
    "egg": frozenset({"eggs"}),
    "nut": frozenset({"tree_nuts", "peanuts"}),
    "peanut": frozenset({"peanuts"}),
    "soy": frozenset({"soy"}),
    "fish": frozenset({"fish"}),
    "shellfish": frozenset({"shellfish"}),
    "sesame": frozenset({"sesame"}),
}

_FREE_CLAIM = re.compile(r"\b([a-z]+?)s?[-\s]free\b", re.IGNORECASE)

# "vegan X" / "plant-based X" negates the ANIMAL-derived allergens only:
# vegan cheese has no dairy, but vegan pesto still has pine nuts.
_VEGAN_CLAIM = re.compile(r"\b(vegan|plant[-\s]based|non[-\s]dairy)\b", re.IGNORECASE)
_ANIMAL_ALLERGENS = frozenset({"dairy", "eggs", "fish", "shellfish"})

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
    for compound, base in _REWRITES:
        lower = lower.replace(compound, base)
    return lower


def _negated(name: str) -> frozenset[str]:
    """Allergens this name explicitly claims absent ("gluten-free",
    "vegan"). Scoped per ingredient line, never whole-recipe."""
    out: set[str] = set()
    for match in _FREE_CLAIM.finditer(name):
        out |= _FREE_NEGATES.get(match.group(1).lower(), frozenset())
    if _VEGAN_CLAIM.search(name):
        out |= _ANIMAL_ALLERGENS
    return frozenset(out)


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


def household_watchlist(conn, tenant_id: str) -> list[str]:
    """Canonical allergens anyone in the household actually avoids.

    The union of every active member's declared allergens (profile),
    allergen-shaped avoid_foods entries ("no shellfish" typed as an
    avoid food still reddens shellfish), and condition-implied
    avoidances (celiac → gluten). Drives DISPLAY emphasis only — a
    "contains X" chip turns red when X is on this list; hard exclusion
    stays with search filters, which have their own path.
    """
    from nutrime.conditions import classify
    from nutrime.foods.matching import normalize_term
    from nutrime.intake.store import household_profiles

    watched: set[str] = set()

    def _canonical_allergen(term: str) -> str | None:
        norm = normalize_term(term)
        if norm in _KEYWORDS:
            return norm
        return ALLERGEN_SYNONYMS.get(norm)

    for profile in household_profiles(conn, tenant_id).values():
        for raw in profile.allergens:
            hit = _canonical_allergen(raw)
            if hit:
                watched.add(hit)
        for raw in profile.avoid_foods:
            hit = _canonical_allergen(raw)
            if hit:
                watched.add(hit)
        for raw in profile.conditions:
            if classify(raw).canonical == "celiac disease":
                watched.add("gluten")
    return sorted(watched)


def detect_allergens(ingredient_names: list[str]) -> list[str]:
    """Return the sorted subset of the canonical 9 allergens present.

    The list is stable for downstream diff-friendly frontmatter output.
    """
    present: set[str] = set()
    for raw in ingredient_names:
        sanitized = _sanitize(raw)
        negated = _negated(raw)
        for allergen, patterns in _COMPILED.items():
            if allergen in present or allergen in negated:
                continue
            if any(p.search(sanitized) for p in patterns):
                present.add(allergen)
    return sorted(present)
