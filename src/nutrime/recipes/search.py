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
}

SOURCE_LABELS: dict[str, str] = {
    "pins": "My saved pins",
    "themealdb": "TheMealDB",
    "myplate": "USDA MyPlate",
    "nhlbi": "NHLBI heart-healthy",
    "historical": "Historical cookbooks",
    "web": "Public web (crawled)",
    "other": "Other",
}

# User direction 2026-10-04: the historical corpus (1861 measurements,
# pre-food-safety guidance) isn't applicable to everyday cooking — it is
# opt-in only. With no explicit source selection, these collections are
# excluded from search and planner pools alike; selecting the pill
# includes them.
OPT_IN_SOURCES = frozenset({"historical"})


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


def normalize_term(term: str) -> str:
    """Lowercase + trim + strip a plural trailing 's' from each word."""
    words = term.lower().strip().split()
    return " ".join(
        w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w
        for w in words
    )


def _terms_match(a: str, b: str) -> bool:
    na, nb = normalize_term(a), normalize_term(b)
    if not na or not nb:
        return False
    return na in nb or nb in na


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
        for name in ingredient_names(record.body):
            for excluded in filters.exclude_ingredients:
                if _terms_match(excluded, name):
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


def _score(record: RecipeRecord, filters: SearchFilters) -> _ScoreDetail:
    names = ingredient_names(record.body)
    fm = record.frontmatter
    title = str(fm.get("title", ""))
    on_hand_matches = tuple(
        sorted(
            item
            for item in filters.on_hand
            if any(_terms_match(item, name) for name in names)
        )
    )
    prefer_matches = tuple(
        sorted(
            term
            for term in filters.prefer_terms
            if _terms_match(term, title)
            or any(_terms_match(term, name) for name in names)
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
            )
        )
    # On-hand match COUNT dominates the ordering: when the user says what
    # they have, "uses most of my ingredients" beats any boost arithmetic —
    # a 3-match recipe always outranks a 1-match recipe regardless of
    # preference boosts. Score (which folds in boosts) breaks ties.
    results.sort(
        key=lambda r: (
            -len(r.on_hand_matches),
            -r.score,
            r.title.lower(),
            r.recipe_id,
        )
    )
    return results if limit is None else results[:limit]
