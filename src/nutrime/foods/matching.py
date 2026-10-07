"""Pantry↔ingredient matching — the ONE matcher every surface shares.

Grew out of search.py's match-quality pass (2026-10-06); hoisted here
(2026-10-08) because grocery netting had quietly kept its own exact-key
equality and diverged: search said "milk" covers "whole milk" while the
grocery list told the household to buy milk they had. One module, three
exported predicates, each tuned for its direction of error:

- :func:`terms_match` — precision-biased symmetric match for "do we have
  this?" (on-hand ranking, grocery have/to-buy netting). Token-boundary,
  head-noun compound guard, distinct-food guard, synonyms, and a curated
  food-family fallback (seedy bread IS bread; cheddar IS cheese).
- :func:`exclusion_match` — recall-biased match for avoid-lists (the
  safety direction): compound-head guard off, families consulted both
  ways ("avoids bread" must catch "sourdough loaf").
- :func:`normalize_term` — the shared normalizer (punctuation → space,
  lowercase, per-word light singularization).

The family table is deliberately curated, not learned: matching is a
trust surface (a wrong "you have this" hides a needed purchase; a wrong
exclusion hides a safe recipe), so new families land by edit, not by
model output at match time. The LLM tier belongs at *write* time
(inventory intake canonicalization), where a human reviews the result.
"""

from __future__ import annotations

import re

# -- normalization -------------------------------------------------------------


def normalize_term(term: str) -> str:
    """Punctuation→space, lowercase, strip a plural trailing 's' per word.

    Punctuation folding matters for token matching: "cilantro, minced"
    must yield the token "cilantro", not "cilantro," — exclusion safety
    depends on it.
    """
    text = re.sub(r"[^\w\s]", " ", term.lower())

    def singular(w: str) -> str:
        if len(w) <= 3 or w.endswith("ss"):
            return w
        # tomatoes→tomato, potatoes→potato; berries handled as -ies→y
        if w.endswith("oes"):
            return w[:-2]
        if w.endswith("ies"):
            return w[:-3] + "y"
        if w.endswith("s"):
            return w[:-1]
        return w

    return " ".join(singular(w) for w in text.strip().split())


# -- vocabulary ----------------------------------------------------------------

# Compound heads where the modifier is NOT the food: having the modifier
# in the pantry must not satisfy the compound. "chicken stock" is stock,
# not chicken; "onion powder" is a spice, not an onion.
_COMPOUND_HEADS = frozenset({
    "vinegar", "oil", "powder", "paste", "sauce", "flour", "syrup",
    "extract", "stock", "broth", "butter", "milk", "cream", "wine",
    "juice", "zest", "seasoning", "starch", "breadcrumb", "crumb",
    "snap", "chip", "seed",
})

# Compounds that are a DIFFERENT food from both their words: neither
# "milk" nor "coconut" should match "coconut milk"; "cream" is not
# "cream of tartar". Only the exact phrase (or a longer phrase
# containing it) matches these.
_DISTINCT_FOODS = frozenset({
    "coconut milk", "almond milk", "oat milk", "soy milk", "rice milk",
    "coconut cream", "cream of tartar", "peanut butter", "almond butter",
    "cashew butter", "apple butter", "cocoa butter",
    "buttermilk", "sweetened condensed milk", "evaporated milk",
    "egg noodle", "egg roll wrapper",
})

# Aliases → canonical (applied word-wise and phrase-wise after
# normalize_term). Deliberately conservative: only true same-food names.
_SYNONYMS = {
    "scallion": "green onion",
    "spring onion": "green onion",
    "coriander leaf": "cilantro",
    "coriander leave": "cilantro",  # post-normalize_term shape of "leaves"
    "fresh coriander": "cilantro",
    "garbanzo": "chickpea",
    "garbanzo bean": "chickpea",
    "courgette": "zucchini",
    "aubergine": "eggplant",
    "capsicum": "bell pepper",
    "rocket": "arugula",
    "beetroot": "beet",
    "prawn": "shrimp",
    "mange tout": "snow pea",
    "caster sugar": "sugar",
    "confectioner sugar": "powdered sugar",
    "icing sugar": "powdered sugar",
    "corn starch": "cornstarch",
    "cornflour": "cornstarch",
    "bicarbonate of soda": "baking soda",
    "porridge oat": "oat",
    "rolled oat": "oat",
    "mince": "ground beef",
    "minced beef": "ground beef",
    "ground mince": "ground beef",
    "evoo": "olive oil",
    "mayo": "mayonnaise",
    "bullion": "bouillon",  # household misspelling, one food
}

# -- food families ---------------------------------------------------------------
#
# family name → member terms (normalize_term shapes). A family answers
# "is X a kind of Y?" where phrase matching can't: "sourdough" contains
# no token "bread", yet a recipe wanting bread is satisfied by it.
#
# Curation rules (precision is the point — err toward leaving a term out):
# - members must SATISFY a generic ask for the family name in a recipe.
#   Cream cheese does not satisfy "cheese" in a quesadilla → not a member.
# - the family name must be how recipes actually ask ("bread", "cheese",
#   "milk"); niche group names (cruciferous, alliums) don't earn a row.
# - one-way is fine: every member is the family, the family is not every
#   member. Directionality is handled in the matcher, not the table.
FOOD_FAMILIES: dict[str, frozenset[str]] = {
    "bread": frozenset({
        "sourdough", "baguette", "ciabatta", "focaccia", "brioche", "rye bread",
        "seedy bread", "seeded loaf", "multigrain loaf", "whole wheat loaf",
        "sandwich loaf", "boule", "batard", "loaf",
    }),
    "cheese": frozenset({
        "cheddar", "mozzarella", "parmesan", "parmigiano reggiano", "gouda",
        "gruyere", "swiss cheese", "provolone", "monterey jack", "colby",
        "pecorino", "manchego", "asiago", "fontina", "havarti", "emmental",
        "comte", "edam", "jarlsberg",
    }),
    "milk": frozenset({
        "whole milk", "skim milk", "2 milk", "1 milk",  # "2% milk" post-normalize
        "low fat milk", "nonfat milk", "semi skimmed milk", "raw milk",
    }),
    "yogurt": frozenset({
        "greek yogurt", "plain yogurt", "natural yogurt", "skyr",
    }),
    "lettuce": frozenset({
        "romaine", "iceberg", "butter lettuce", "little gem", "frisee",
    }),
    "onion": frozenset({
        "yellow onion", "white onion", "red onion", "sweet onion", "vidalia",
    }),
    "potato": frozenset({
        "russet", "yukon gold", "red potato", "fingerling", "new potato",
    }),
    "apple": frozenset({
        "granny smith", "honeycrisp", "gala apple", "fuji apple",
        "pink lady", "braeburn",
    }),
    "rice": frozenset({
        "jasmine rice", "basmati", "arborio", "long grain rice",
        "short grain rice", "brown rice", "white rice", "sushi rice",
    }),
    "pasta": frozenset({
        "spaghetti", "penne", "rigatoni", "fusilli", "linguine", "fettuccine",
        "macaroni", "farfalle", "tagliatelle", "bucatini", "rotini", "ziti",
    }),
    "sugar": frozenset({
        "white sugar", "granulated sugar", "cane sugar",
    }),
    "vinegar": frozenset({
        "white vinegar", "apple cider vinegar", "red wine vinegar",
        "white wine vinegar", "rice vinegar", "balsamic", "sherry vinegar",
    }),
    "mayonnaise": frozenset({
        "kewpie mayonnaise",  # post-synonym shape of "kewpie mayo"
    }),
    "bouillon": frozenset({
        "chicken bouillon", "beef bouillon", "vegetable bouillon",
        "bouillon cube",
    }),
    "breadcrumb": frozenset({
        "panko",
    }),
}

# term → family names it belongs to, normalized once at import. A term
# can sit in several families (none do today; the shape allows it).
_FAMILY_OF: dict[str, frozenset[str]] = {}
for _family, _members in FOOD_FAMILIES.items():
    for _member in _members:
        _key = normalize_term(_member)
        _FAMILY_OF[_key] = _FAMILY_OF.get(_key, frozenset()) | {_family}


# Word-level synonym pass: only synonyms mapping one word to one word
# are safe mid-phrase ("kewpie mayo" → "kewpie mayonnaise"); multi-word
# values would reshape token counts unpredictably.
_WORD_SYNONYMS = {
    k: v for k, v in _SYNONYMS.items()
    if " " not in k and " " not in v
}

# Spelling folds applied mid-phrase (post-normalize): spaced compounds
# whose joined form is the canonical food word. Token-boundary safe.
_PHRASE_FOLDS = (
    (re.compile(r"\bbread crumb\b"), "breadcrumb"),
)


def _canonical(term: str) -> str:
    norm = normalize_term(term)
    for pattern, folded in _PHRASE_FOLDS:
        norm = pattern.sub(folded, norm)
    phrase = _SYNONYMS.get(norm)
    if phrase is not None:
        return phrase
    words = [_WORD_SYNONYMS.get(w, w) for w in norm.split()]
    rewritten = " ".join(words)
    return _SYNONYMS.get(rewritten, rewritten)


def _token_phrase_in(needle: str, hay: str) -> bool:
    """True when needle's full word sequence appears on word boundaries
    in hay — "apple" in "apple pie" but NOT in "pineapple"."""
    n_words = needle.split()
    h_words = hay.split()
    if not n_words or len(n_words) > len(h_words):
        return False
    for start in range(len(h_words) - len(n_words) + 1):
        if h_words[start : start + len(n_words)] == n_words:
            return True
    return False


def _head(term: str) -> str:
    words = term.split()
    return words[-1] if words else ""


def _families(canon: str) -> frozenset[str]:
    """Families the canonicalized term belongs to — by exact membership,
    or by any member phrase appearing inside it on token boundaries
    ("2 slice sourdough bread" carries "sourdough")."""
    direct = _FAMILY_OF.get(canon)
    if direct:
        return direct
    out: set[str] = set()
    for member, families in _FAMILY_OF.items():
        if _token_phrase_in(member, canon):
            out |= families
    return frozenset(out)


def _family_covers(a: str, b: str) -> bool:
    """Does ``a`` satisfy ``b`` through the family table, either way?

    Membership is directional (cheddar IS cheese) but coverage here is
    symmetric on purpose: a pantry "cheddar" satisfies a recipe's
    "cheese", AND a pantry "cheese" satisfies a recipe's "cheddar" —
    the household wrote the generic name for the thing they have.
    Same family on both sides is NOT a match: cheddar ≠ gouda. Only
    member↔family-name pairs match.
    """
    for member, other in ((a, b), (b, a)):
        for family in _families(member):
            if other == family:
                return True
            # A modified ask ("crusty bread", "shredded cheese") is
            # still generic — unless the modifier makes it a DIFFERENT
            # food ("coconut milk" is not a milk ask) or a compound
            # whose head isn't the family ("bread flour" is flour).
            if not _token_phrase_in(family, other):
                continue
            if any(_token_phrase_in(c, other) for c in _DISTINCT_FOODS):
                continue
            if _head(other) in _COMPOUND_HEADS and _head(other) != family:
                continue
            return True
    return False


def terms_match(a: str, b: str) -> bool:
    """Does pantry/filter term ``a`` match food name ``b`` (either way)?

    Token-boundary + head-noun aware; both sides canonicalized first;
    food-family fallback for member↔family-name pairs.
    """
    na, nb = _canonical(a), _canonical(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na.split()) <= len(nb.split()) else (nb, na)
    if not _token_phrase_in(shorter, longer):
        # No phrase overlap — the family table is the last resort
        # (sourdough vs bread share no token).
        return _family_covers(na, nb)
    # Distinct-food compounds: only the exact phrase satisfies them —
    # "milk" must not match "coconut milk", nor "cream" match "cream of
    # tartar", whatever the head-noun arithmetic says.
    for compound in _DISTINCT_FOODS:
        if _token_phrase_in(compound, longer) and not _token_phrase_in(
            compound, shorter
        ):
            return False
    # Word-boundary hit. Guard the compound-head trap: if the longer
    # term ends in a compound head that the shorter term doesn't cover,
    # the modifier alone must not match ("rice" vs "rice vinegar").
    # The head itself always satisfies it ("vinegar" vs "rice vinegar").
    long_head = _head(longer)
    if long_head in _COMPOUND_HEADS and _head(shorter) != long_head:
        # The family table can still vouch: "seedy bread" ends in a
        # compound head, but bread-the-family claims it whole.
        return _family_covers(na, nb)
    return True


def exclusion_match(avoided: str, name: str) -> bool:
    """Recall-biased matcher for avoid-lists — the safety direction.

    The compound-head guard is deliberately ABSENT: "peanut butter"
    contains peanut, "onion powder" contains onion — a recipe using
    them must be excluded for an avoider of the base food. Token
    boundaries still apply ("egg" does not exclude eggplant: different
    plant, no egg in it). Families consulted both directions: "avoids
    bread" excludes sourdough.
    """
    na, nb = _canonical(avoided), _canonical(name)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na.split()) <= len(nb.split()) else (nb, na)
    if _token_phrase_in(shorter, longer):
        return True
    return _family_covers(na, nb)
