"""Recipe search — the query surface over the corpus vault (5.3).

Backs the ``recipe_search`` query type registered on the PHI envelope in 4.1
(empty category set — searching recipes is a local, PHI-free operation), and
doubles as the candidate-generation stage for the 5.4 planner: the LLM only
ever selects from what this module returns, it never free-generates recipes.

Two-track seam discipline: :func:`filters_from_constraints` is the ONLY
knowledge-model-facing entry point, and it reads abstracted-constraint
synthesized entries ("avoids X" / "prefers Y") — never raw atoms. "avoids"
terms that name a top-9 allergen become allergen hard-blocks (matching the
``top_allergens_present`` frontmatter vocabulary); anything else becomes an
ingredient-name exclusion. "prefers" terms become score boosts, never filters.

Implementation is a full vault scan per query (filesystem is source of truth
per S9 Q9.1). Substrate index denormalization stays deferred until scan cost
actually hurts; at ~4k recipes a scan is fine for a single-household CLI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, Iterable

from nutrime.recipes.allergens import TOP_ALLERGENS
from nutrime.recipes.store import RecipeRecord, RecipeVault

_INGREDIENT_LINE = re.compile(r"^@(?P<braced>[^@{}]+)\{|^@(?P<bare>\S+)$")

_ON_HAND_POINTS = 2.0
_PREFER_POINTS = 1.5
# V2 (#27): expiring-soon on-hand matches earn this ON TOP of on-hand
# points — tilts score, never reorders match counts (count sorts first).
_EXPIRING_POINTS = 2.0
# V1 (#26): experience boost capped at one on-hand ingredient's weight —
# history never outweighs what's in the fridge. Symmetric boost-down for
# disliked; never a filter.
_EXPERIENCE_POINTS_PER_STAR = 1.0
# V3 (#28): never-cooked cuisine nudge — deliberately below preference
# weight; broadening nudges, never overrides stated taste.
_NOVELTY_POINTS = 0.5

# Pantry-first ranking (user direction 2026-10-06): recipes you can cook
# WITHOUT buying anything rank first. Assumed-staple ingredients don't
# count as "missing" — nobody shops for salt to fulfill a recipe.
PANTRY_STAPLES = frozenset({
    "salt", "pepper", "black pepper", "salt and pepper", "water", "ice",
    "oil", "olive oil", "vegetable oil", "cooking oil", "canola oil",
    "sugar", "flour", "all purpose flour", "butter",
    "garlic powder", "onion powder", "paprika", "cumin", "oregano",
    "chili powder", "cinnamon", "bay leaf", "bay leaves", "thyme",
    "red pepper flakes", "cayenne pepper", "italian seasoning",
    "vanilla extract", "baking powder", "baking soda", "cornstarch",
    "soy sauce", "vinegar", "white vinegar", "ketchup", "mustard",
    "mayonnaise", "honey", "hot sauce", "worcestershire sauce",
    "cooking spray", "nonstick spray", "stock", "broth",
})


_STAPLE_KEYS: frozenset[str] | None = None  # built lazily (normalize_term below)


def _is_staple(name: str) -> bool:
    global _STAPLE_KEYS
    if _STAPLE_KEYS is None:
        _STAPLE_KEYS = frozenset(normalize_term(s) for s in PANTRY_STAPLES)
    return normalize_term(name) in _STAPLE_KEYS


@dataclass(frozen=True)
class SearchFilters:
    query: str | None = None
    exclude_allergens: frozenset[str] = field(default_factory=frozenset)
    exclude_ingredients: frozenset[str] = field(default_factory=frozenset)
    prefer_terms: frozenset[str] = field(default_factory=frozenset)
    max_total_time_min: int | None = None
    meal_category: str | None = None
    # Corpus ``meal_categories`` are not a clean meal-slot vocabulary — a
    # source may tag by course (dessert, side), protein (beef, chicken) or
    # diet (vegetarian) in the same field. ``meal_categories_any`` matches if
    # ANY listed tag is present; ``exclude_categories`` rejects if any listed
    # tag is present. Together they express "a main course" as "not a dessert,
    # side, or breakfast" without enumerating every protein.
    meal_categories_any: frozenset[str] = field(default_factory=frozenset)
    exclude_categories: frozenset[str] = field(default_factory=frozenset)
    cuisine: str | None = None
    on_hand: frozenset[str] = field(default_factory=frozenset)
    # Source-collection facet: keys from SOURCE_COLLECTIONS ("pins",
    # "themealdb", ...). Empty = all sources.
    sources: frozenset[str] = field(default_factory=frozenset)
    # V2: subset of on_hand names whose best_by_date is near — matches
    # earn _EXPIRING_POINTS on top of on-hand points.
    expiring: frozenset[str] = field(default_factory=frozenset)
    # Staples the household marked as out of stock: these count as
    # missing again despite PANTRY_STAPLES assuming them on hand.
    out_of_staples: frozenset[str] = field(default_factory=frozenset)
    # V1: recipe_id → experience summary (feedback.experience_summaries
    # shape). None = no history consulted.
    experience: Any = None
    # V3: cuisines already cooked; None disables novelty scoring. Only
    # the planner passes this by default ("what can I make right now" is
    # not the broadening moment) — search surfaces opt in.
    cooked_cuisines: frozenset[str] | None = None


# ingestion_method → user-facing collection key. Her pins are stored under
# each blog's own source_name (attribution honesty), so the facet groups by
# HOW a recipe arrived, which matches how the household thinks about it.
SOURCE_COLLECTIONS: dict[str, str] = {
    "schema_org_jsonld_v1": "pins",
    "themealdb_api_v1": "themealdb",
    "myplate_wayback_html_v1": "myplate",
    "nhlbi_html_v1": "nhlbi",
    "gutenberg_text_v1": "historical",
    "crawl_jsonld_v1": "web",
    "pinterest_top_jsonld_v1": "pinterest_top",
}

SOURCE_LABELS: dict[str, str] = {
    "pins": "My saved pins",
    "themealdb": "TheMealDB",
    "myplate": "USDA MyPlate",
    "nhlbi": "NHLBI heart-healthy",
    "historical": "Historical cookbooks",
    "web": "Public web (crawled)",
    "pinterest_top": "Pinterest top pins",
    "other": "Other",
}

# User direction 2026-10-04: the historical corpus (1861 measurements,
# pre-food-safety guidance) isn't applicable to everyday cooking — it is
# opt-in only. With no explicit source selection, these collections are
# excluded from search and planner pools alike; selecting the pill
# includes them.
OPT_IN_SOURCES = frozenset({"historical"})


# Sources tag cuisines by country or by adjective; one name per cuisine.
CUISINE_ALIASES = {
    "united states": "american", "usa": "american", "us": "american",
    "france": "french", "india": "indian", "norway": "norwegian",
    "netherlands": "dutch", "italy": "italian", "spain": "spanish",
    "china": "chinese", "japan": "japanese", "mexico": "mexican",
    "greece": "greek", "thailand": "thai", "vietnam": "vietnamese",
    "turkey": "turkish", "poland": "polish", "canada": "canadian",
    "australia": "australian", "jamaica": "jamaican", "algeria": "algerian",
    "united kingdom": "british", "uk": "british", "england": "british",
    "morocco": "moroccan", "korea": "korean", "ireland": "irish",
}


def canonical_cuisine(tag: str) -> str:
    tag = tag.strip().lower()
    return CUISINE_ALIASES.get(tag, tag)


def source_collection(frontmatter: dict[str, Any]) -> str:
    method = (frontmatter.get("attribution") or {}).get("ingestion_method", "")
    return SOURCE_COLLECTIONS.get(method, "other")


@dataclass(frozen=True)
class SearchResult:
    recipe_id: str
    title: str
    score: float
    total_time_min: int | None
    allergens: tuple[str, ...]
    on_hand_matches: tuple[str, ...]
    prefer_matches: tuple[str, ...]
    attribution: str
    source: str = "other"
    # V1: cook-history surface fields (None/0 when no history)
    times_cooked: int = 0
    avg_enjoyment: float | None = None
    # "usually takes ~N min for you" — stated + avg delta; never
    # overwrites total_time_min (the source's claim stays visible).
    personal_time_min: int | None = None
    # V2/V3 surface flags
    expiring_matches: tuple[str, ...] = ()
    novel_cuisine: bool = False
    # Pantry-first: non-staple ingredients the kitchen doesn't have.
    # Empty + inventory in play = cookable tonight with no shopping.
    missing_ingredients: tuple[str, ...] = ()


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


# -- pantry↔ingredient matching (match-quality pass, 2026-10-06) ---------------
#
# The old matcher was bidirectional substring containment over the whole
# normalized string. Recall was perfect; precision was not: "apple"
# matched pineAPPLE, "egg" matched EGGplant, "rice" matched rice VINEGAR,
# "milk" matched coconut milk. Three fixes, all deterministic:
#
# 1. token-boundary matching — terms match on whole normalized words,
#    never inside a word (kills pineapple/eggplant/cornstarch);
# 2. head-noun compounds — in food names like "rice vinegar" the LAST
#    noun is the food ("vinegar"); a pantry item only satisfies the
#    compound if it covers the head, so rice ≠ rice vinegar but
#    "rice vinegar" in the pantry matches "rice vinegar" (and plain
#    "vinegar" matches it too, deliberately — same food family);
# 3. synonyms — US/UK + common aliases normalize to one canonical form
#    before comparison (scallion=green onion, garbanzo=chickpea...).

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
}


def _canonical(term: str) -> str:
    norm = normalize_term(term)
    return _SYNONYMS.get(norm, norm)


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


def _terms_match(a: str, b: str) -> bool:
    """Does pantry/filter term ``a`` match food name ``b`` (either way)?

    Token-boundary + head-noun aware; both sides canonicalized first.
    """
    na, nb = _canonical(a), _canonical(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na.split()) <= len(nb.split()) else (nb, na)
    if not _token_phrase_in(shorter, longer):
        return False
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
        return False
    return True


def _exclusion_match(avoided: str, name: str) -> bool:
    """Recall-biased matcher for avoid-lists — the safety direction.

    The compound-head guard is deliberately ABSENT: "peanut butter"
    contains peanut, "onion powder" contains onion — a recipe using
    them must be excluded for an avoider of the base food. Token
    boundaries still apply ("egg" does not exclude eggplant: different
    plant, no egg in it).
    """
    na, nb = _canonical(avoided), _canonical(name)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na.split()) <= len(nb.split()) else (nb, na)
    return _token_phrase_in(shorter, longer)


def ingredient_names(body: str) -> tuple[str, ...]:
    """Extract ingredient names from a canonical Cooklang body."""
    names: list[str] = []
    for line in body.splitlines():
        match = _INGREDIENT_LINE.match(line.strip())
        if match:
            names.append((match.group("braced") or match.group("bare")).strip())
    return tuple(names)


def attribution_line(frontmatter: dict[str, Any]) -> str:
    """Render-side credit per issue #23, generalized to every source.

    Every recipe display surface shows its source adjacent to the content;
    attribution-required licenses (TheMealDB free tier) are thereby always
    satisfied, and PD sources get honest provenance for free.
    """
    attribution = frontmatter.get("attribution", {}) or {}
    source = attribution.get("source_name", "unknown source")
    license_ = attribution.get("source_license", "license unknown")
    url = attribution.get("source_url", "")
    line = f"Source: {source} ({license_})"
    if url:
        line += f" — {url}"
    return line


def filters_from_constraints(
    entries: Iterable[Any],
    base: SearchFilters | None = None,
) -> SearchFilters:
    """Fold abstracted-constraint entries into filters — the seam crossing.

    Accepts the ``KnowledgeRecord`` rows from
    ``list_synthesized_entries(entry_type="abstracted_constraint")``; only the
    ``payload["abstracted_text"]`` shape is read, never raw atom content.
    """
    filters = base or SearchFilters()
    exclude_allergens = set(filters.exclude_allergens)
    exclude_ingredients = set(filters.exclude_ingredients)
    prefer_terms = set(filters.prefer_terms)
    allergen_names = {normalize_term(a): a for a in TOP_ALLERGENS}
    for entry in entries:
        text = (entry.payload.get("abstracted_text") or "").strip().lower()
        if text.startswith("avoids "):
            term = text[len("avoids ") :].strip()
            canonical = allergen_names.get(normalize_term(term))
            if canonical is not None:
                exclude_allergens.add(canonical)
            else:
                exclude_ingredients.add(term)
        elif text.startswith("prefers "):
            prefer_terms.add(text[len("prefers ") :].strip())
    return replace(
        filters,
        exclude_allergens=frozenset(exclude_allergens),
        exclude_ingredients=frozenset(exclude_ingredients),
        prefer_terms=frozenset(prefer_terms),
    )


def _passes(record: RecipeRecord, filters: SearchFilters) -> bool:
    fm = record.frontmatter
    # Corpus hygiene (V0/V2): rows the vetting pass quarantined or marked
    # as a cross-source duplicate never rank. Un-vetted rows (no stamp
    # yet) pass — new ingests stay searchable.
    if fm.get("vetting_status") in ("quarantined", "duplicate"):
        return False
    collection = source_collection(fm)
    if filters.sources:
        if collection not in filters.sources:
            return False
    elif collection in OPT_IN_SOURCES:
        return False
    if filters.query:
        if filters.query.lower() not in str(fm.get("title", "")).lower():
            return False
    allergens = {
        normalize_term(str(a)) for a in fm.get("top_allergens_present", ()) or ()
    }
    for blocked in filters.exclude_allergens:
        if normalize_term(blocked) in allergens:
            return False
    if filters.exclude_ingredients:
        # Safety direction: exclusion uses the recall-biased matcher —
        # "avoids peanut" must catch peanut butter (compound guard off).
        for name in ingredient_names(record.body):
            for excluded in filters.exclude_ingredients:
                if _exclusion_match(excluded, name):
                    return False
    if filters.max_total_time_min is not None:
        total = fm.get("estimated_total_time_min")
        # V1: her real times beat the blog's optimism — when history has
        # an avg delta, the time budget filters on the corrected value.
        if total is not None and filters.experience is not None:
            summary = filters.experience.get(
                str(fm.get("canonical_id", ""))
            )
            if summary and summary.get("avg_time_delta_min") is not None:
                total = int(total) + int(summary["avg_time_delta_min"])
        # Unknown time cannot be verified to fit an explicit time budget —
        # excluded rather than optimistically included (safe direction).
        if total is None or int(total) > filters.max_total_time_min:
            return False
    if (
        filters.meal_category is not None
        or filters.meal_categories_any
        or filters.exclude_categories
    ):
        categories = {str(c).lower() for c in fm.get("meal_categories", ()) or ()}
        if (
            filters.meal_category is not None
            and filters.meal_category.lower() not in categories
        ):
            return False
        if filters.exclude_categories & {c.lower() for c in categories}:
            return False
        if filters.meal_categories_any and not (
            {c.lower() for c in filters.meal_categories_any} & categories
        ):
            return False
    if filters.cuisine is not None:
        cuisines = [
            str(c).lower() for c in fm.get("cuisine_tradition_tags", ()) or ()
        ]
        if filters.cuisine.lower() not in cuisines:
            return False
    return True


@dataclass(frozen=True)
class _ScoreDetail:
    score: float
    on_hand_matches: tuple[str, ...]
    prefer_matches: tuple[str, ...]
    expiring_matches: tuple[str, ...]
    novel_cuisine: bool
    missing_ingredients: tuple[str, ...] = ()


# Cleaned-ingredient cache: the grocery parser strips descriptors and
# prep ("oregano, minced (or 1 tsp dried)" → "oregano") so matching and
# missing-counts run on food names, not raw lines. Keyed by recipe id +
# body length (bodies are immutable in practice; vet rewrites change
# length). ~0.03 ms/parse, but search scans the whole vault per query —
# caching keeps repeat searches flat.
_CLEAN_CACHE: dict[tuple[str, int], tuple[tuple[str, ...], tuple[str, ...]]] = {}

_SENTENCE_JUNK = re.compile(
    r"^(and|to|the|a|for|if|when|after|before|then|this|these|it|add)\b", re.I
)


def cleaned_ingredients(record: RecipeRecord) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """(clean food names for matching, junk-free names for missing-counts).

    The first tuple parses every raw line into its food term. The second
    drops lines that are prose fragments, not foods — historical-corpus
    bodies carry lines like "and truss them at the back of the bird",
    which must not count as a missing ingredient (they made the
    "nothing to buy" tier unreachable for whole sources).
    """
    key = (record.recipe_id, len(record.body))
    hit = _CLEAN_CACHE.get(key)
    if hit is not None:
        return hit
    from nutrime.grocery.parse import parse_ingredient

    foods: list[str] = []
    countable: list[str] = []
    for raw in ingredient_names(record.body):
        parsed = parse_ingredient(raw)
        for line in parsed:
            food = line.food.strip()
            if not food:
                continue
            foods.append(food)
            # Junk heuristics: sentence-shaped, starts with a function
            # word, or runs past any plausible food-name length.
            if (
                len(food.split()) > 5
                or _SENTENCE_JUNK.match(food)
                or food.endswith(".")
            ):
                continue
            countable.append(food)
    result = (tuple(foods), tuple(countable))
    if len(_CLEAN_CACHE) > 8192:
        _CLEAN_CACHE.clear()
    _CLEAN_CACHE[key] = result
    return result


def _score(record: RecipeRecord, filters: SearchFilters) -> _ScoreDetail:
    names, countable_names = cleaned_ingredients(record)
    fm = record.frontmatter
    title = str(fm.get("title", ""))
    on_hand_matches = tuple(
        sorted(
            item
            for item in filters.on_hand
            if any(_terms_match(item, name) for name in names)
        )
    )
    # Pantry-first: which recipe ingredients does the kitchen NOT cover?
    # Staples never count — nobody shops for salt — UNLESS the household
    # marked that staple as out of stock. Only meaningful when inventory
    # is in play (empty on_hand would mark everything missing).
    missing: tuple[str, ...] = ()
    if filters.on_hand:
        def _assumed(name: str) -> bool:
            if not _is_staple(name):
                return False
            return not any(
                _terms_match(out, name) for out in filters.out_of_staples
            )

        missing = tuple(
            sorted(
                {
                    name.strip().lower()
                    for name in countable_names
                    if not _assumed(name)
                    and not any(
                        _terms_match(item, name) for item in filters.on_hand
                    )
                }
            )
        )
    prefer_matches = tuple(
        sorted(
            term
            for term in filters.prefer_terms
            if _terms_match(term, title)
            or any(_terms_match(term, name) for name in names)
            # cuisine interests from check-ins ("prefers thai")
            or any(
                _terms_match(term, canonical_cuisine(str(c)))
                for c in (fm.get("cuisine_tradition_tags") or [])
            )
        )
    )
    expiring_matches = tuple(
        item for item in on_hand_matches if item in filters.expiring
    )
    score = (
        _ON_HAND_POINTS * len(on_hand_matches)
        + _PREFER_POINTS * len(prefer_matches)
        + _EXPIRING_POINTS * len(expiring_matches)
    )
    # V1: experience boost/boost-down around the 3-star midpoint.
    if filters.experience is not None:
        summary = filters.experience.get(str(fm.get("canonical_id", "")))
        if summary and summary.get("avg_enjoyment") is not None:
            score += _EXPERIENCE_POINTS_PER_STAR * (
                summary["avg_enjoyment"] - 3.0
            )
    # V3: novelty nudge for never-cooked cuisines (planner opt-in).
    novel = False
    if filters.cooked_cuisines is not None:
        tags = {
            str(c).lower() for c in fm.get("cuisine_tradition_tags", ()) or ()
        }
        if tags and not (tags & filters.cooked_cuisines):
            novel = True
            score += _NOVELTY_POINTS
    return _ScoreDetail(
        score=score,
        on_hand_matches=on_hand_matches,
        prefer_matches=prefer_matches,
        expiring_matches=expiring_matches,
        novel_cuisine=novel,
        missing_ingredients=missing,
    )


@dataclass(frozen=True)
class SearchPage:
    """A page of results plus the total matched (for pagination UX)."""

    results: tuple[SearchResult, ...]
    total: int


def search_page(
    vault: RecipeVault,
    filters: SearchFilters,
    *,
    limit: int = 24,
    offset: int = 0,
) -> SearchPage:
    """Paginated variant of :func:`search` — same scan, windowed slice."""
    ranked = search(vault, filters, limit=None)
    return SearchPage(
        results=tuple(ranked[offset : offset + limit]),
        total=len(ranked),
    )


def search(
    vault: RecipeVault,
    filters: SearchFilters,
    *,
    limit: int | None = 10,
) -> list[SearchResult]:
    """Scan the vault, hard-filter, then rank by on-hand + preference score."""
    results: list[SearchResult] = []
    for record in vault.iter_recipes():
        if not _passes(record, filters):
            continue
        detail = _score(record, filters)
        fm = record.frontmatter
        total = fm.get("estimated_total_time_min")
        times_cooked = 0
        avg_enjoyment = None
        personal_time = None
        if filters.experience is not None:
            summary = filters.experience.get(record.recipe_id)
            if summary:
                times_cooked = summary.get("times_cooked", 0)
                avg_enjoyment = summary.get("avg_enjoyment")
                delta = summary.get("avg_time_delta_min")
                if total is not None and delta is not None:
                    personal_time = int(total) + int(delta)
        results.append(
            SearchResult(
                recipe_id=record.recipe_id,
                title=str(fm.get("title", "(untitled)")),
                score=detail.score,
                total_time_min=int(total) if total is not None else None,
                allergens=tuple(
                    str(a) for a in fm.get("top_allergens_present", ()) or ()
                ),
                on_hand_matches=detail.on_hand_matches,
                prefer_matches=detail.prefer_matches,
                attribution=attribution_line(fm),
                source=source_collection(fm),
                times_cooked=times_cooked,
                avg_enjoyment=avg_enjoyment,
                personal_time_min=personal_time,
                expiring_matches=detail.expiring_matches,
                novel_cuisine=detail.novel_cuisine,
                missing_ingredients=detail.missing_ingredients,
            )
        )
    # Pantry-first ordering (user direction 2026-10-06). When inventory
    # is in play, three tiers before boost arithmetic:
    #   1. cookable-now first — zero missing non-staple ingredients
    #      ("no new ingredients need to be bought to fulfill the meal");
    #   2. then most on-hand matches — uses up the most of what's here;
    #   3. then fewest missing — a 1-item shop beats a 6-item shop.
    # Score (preference/expiring/experience boosts) breaks ties; without
    # inventory the old count-then-score ordering is unchanged.
    results.sort(
        key=lambda r: (
            0 if r.on_hand_matches and not r.missing_ingredients else 1,
            -len(r.on_hand_matches),
            len(r.missing_ingredients),
            -r.score,
            r.title.lower(),
            r.recipe_id,
        )
    )
    return results if limit is None else results[:limit]
