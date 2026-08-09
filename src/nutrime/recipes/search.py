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


@dataclass(frozen=True)
class SearchFilters:
    query: str | None = None
    exclude_allergens: frozenset[str] = field(default_factory=frozenset)
    exclude_ingredients: frozenset[str] = field(default_factory=frozenset)
    prefer_terms: frozenset[str] = field(default_factory=frozenset)
    max_total_time_min: int | None = None
    meal_category: str | None = None
    cuisine: str | None = None
    on_hand: frozenset[str] = field(default_factory=frozenset)


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
        # Unknown time cannot be verified to fit an explicit time budget —
        # excluded rather than optimistically included (safe direction).
        if total is None or int(total) > filters.max_total_time_min:
            return False
    if filters.meal_category is not None:
        categories = [str(c).lower() for c in fm.get("meal_categories", ()) or ()]
        if filters.meal_category.lower() not in categories:
            return False
    if filters.cuisine is not None:
        cuisines = [
            str(c).lower() for c in fm.get("cuisine_tradition_tags", ()) or ()
        ]
        if filters.cuisine.lower() not in cuisines:
            return False
    return True


def _score(
    record: RecipeRecord, filters: SearchFilters
) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    names = ingredient_names(record.body)
    title = str(record.frontmatter.get("title", ""))
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
    score = (
        _ON_HAND_POINTS * len(on_hand_matches)
        + _PREFER_POINTS * len(prefer_matches)
    )
    return score, on_hand_matches, prefer_matches


def search(
    vault: RecipeVault,
    filters: SearchFilters,
    *,
    limit: int = 10,
) -> list[SearchResult]:
    """Scan the vault, hard-filter, then rank by on-hand + preference score."""
    results: list[SearchResult] = []
    for record in vault.iter_recipes():
        if not _passes(record, filters):
            continue
        score, on_hand_matches, prefer_matches = _score(record, filters)
        fm = record.frontmatter
        total = fm.get("estimated_total_time_min")
        results.append(
            SearchResult(
                recipe_id=record.recipe_id,
                title=str(fm.get("title", "(untitled)")),
                score=score,
                total_time_min=int(total) if total is not None else None,
                allergens=tuple(
                    str(a) for a in fm.get("top_allergens_present", ()) or ()
                ),
                on_hand_matches=on_hand_matches,
                prefer_matches=prefer_matches,
                attribution=attribution_line(fm),
            )
        )
    results.sort(key=lambda r: (-r.score, r.title.lower(), r.recipe_id))
    return results[:limit]
