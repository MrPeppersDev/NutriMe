"""TheMealDB (themealdb.com) free-tier API adapter.

Per the step 4 entry decision, TheMealDB free tier is one of four sub-commit
4.1 seed sources. Free tier uses developer key ``1``; attribution ("Recipe
via TheMealDB") is surfaced at recipe render per the free-tier terms. See
themealdb.com/api.php for endpoint documentation.

Endpoint chosen for seed ingest: ``search.php?f=<letter>`` returns full meal
records (not just ids), so N recipes come out of a small number of calls.

The HTTP fetcher is dependency-injected: production uses ``urllib`` from
stdlib (no new runtime deps); tests inject a canned-response callable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from nutrime.recipes.allergens import detect_allergens
from nutrime.recipes.cooklang import Ingredient, Recipe, emit_cooklang, split_measure
from nutrime.recipes.frontmatter import (
    Attribution,
    Yields,
    build_recipe_frontmatter,
)
from nutrime.recipes.ids import new_recipe_id
from nutrime.recipes.store import collect_upstream_ids
from nutrime.recipes.web import now_iso, safe_urlopen

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
SOURCE_NAME = "TheMealDB"
SOURCE_LICENSE = "TheMealDB free-tier — attribution required"
INGESTION_METHOD = "themealdb_api_v1"

HttpFetcher = Callable[[str], dict[str, Any]]


def _urllib_fetch(url: str) -> dict[str, Any]:
    with safe_urlopen(url, timeout=30) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


@dataclass(frozen=True)
class TheMealDBClient:
    """Thin wrapper over the JSON API.

    The API returns ``{"meals": null}`` or ``{"meals": [...]}``; each meal
    is a flat dict with ``strIngredient1..20`` + ``strMeasure1..20`` slots.

    ``fetcher`` defaults to ``None`` and is resolved at call time to the
    module-level :func:`_urllib_fetch` so tests can monkey-patch the module
    binding without constructing a new client.
    """

    base_url: str = BASE_URL
    fetcher: HttpFetcher | None = None

    def _get(self, path: str) -> list[dict[str, Any]]:
        url = f"{self.base_url}/{path}"
        fetch = self.fetcher if self.fetcher is not None else _urllib_fetch
        payload = fetch(url)
        meals = payload.get("meals")
        return list(meals) if meals else []

    def search_by_letter(self, letter: str) -> list[dict[str, Any]]:
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError(f"letter must be a single a-z character: {letter!r}")
        return self._get(f"search.php?f={letter.lower()}")

    def lookup_by_id(self, meal_id: str) -> dict[str, Any] | None:
        meals = self._get(f"lookup.php?i={meal_id}")
        return meals[0] if meals else None

    def random(self) -> dict[str, Any] | None:
        meals = self._get("random.php")
        return meals[0] if meals else None


# -- meal payload → domain conversion --------------------------------------


def _extract_ingredients(meal: dict[str, Any]) -> list[Ingredient]:
    ingredients: list[Ingredient] = []
    for i in range(1, 21):
        raw_name = (meal.get(f"strIngredient{i}") or "").strip()
        raw_measure = (meal.get(f"strMeasure{i}") or "").strip()
        if not raw_name:
            continue
        qty, unit = split_measure(raw_measure)
        ingredients.append(Ingredient(name=raw_name, quantity=qty, unit=unit))
    return ingredients


def _extract_steps(meal: dict[str, Any]) -> list[str]:
    instructions = (meal.get("strInstructions") or "").strip()
    if not instructions:
        return []
    # TheMealDB blocks instructions as a single field; split on blank lines
    # so the emitted Cooklang has one paragraph per step.
    normalized = instructions.replace("\r\n", "\n").replace("\r", "\n")
    raw = [chunk.strip() for chunk in normalized.split("\n\n")]
    steps = [s for s in raw if s]
    if not steps:
        # Fallback: line-per-step
        steps = [
            line.strip() for line in normalized.splitlines() if line.strip()
        ]
    return steps


def _cuisine_tags(meal: dict[str, Any]) -> list[str]:
    area = (meal.get("strArea") or "").strip()
    return [area.lower()] if area else []


def _meal_categories(meal: dict[str, Any]) -> list[str]:
    category = (meal.get("strCategory") or "").strip()
    tags = (meal.get("strTags") or "").strip()
    out: list[str] = []
    if category:
        out.append(category.lower())
    if tags:
        for tag in tags.split(","):
            t = tag.strip().lower()
            if t and t not in out:
                out.append(t)
    return out


@dataclass(frozen=True)
class ConvertedRecipe:
    """Result of converting one TheMealDB meal payload."""

    recipe_id: str
    frontmatter: dict[str, Any]
    cooklang_body: str
    upstream_meal_id: str


def convert_meal(meal: dict[str, Any], *, ingested_at: str | None = None) -> ConvertedRecipe:
    """Map one TheMealDB meal payload → (frontmatter, Cooklang body)."""
    when = ingested_at or now_iso()
    recipe_id = new_recipe_id()
    upstream_id = (meal.get("idMeal") or "").strip()
    title = (meal.get("strMeal") or "Untitled Recipe").strip()
    source_url = (meal.get("strSource") or "").strip()
    if not source_url and upstream_id:
        source_url = f"https://www.themealdb.com/meal/{upstream_id}"

    ingredients = _extract_ingredients(meal)
    steps = _extract_steps(meal)
    allergens = detect_allergens([ing.name for ing in ingredients])

    attribution = Attribution(
        source_name=SOURCE_NAME,
        source_url=source_url,
        source_license=SOURCE_LICENSE,
        ingested_at=when,
        ingestion_method=INGESTION_METHOD,
        upstream_id=upstream_id,
    )
    yields = Yields(count=4)

    frontmatter = build_recipe_frontmatter(
        recipe_id=recipe_id,
        title=title,
        attribution=attribution,
        source_status="live",
        last_source_check_at=when,
        yields=yields,
        top_allergens_present=allergens,
        cuisine_tradition_tags=_cuisine_tags(meal),
        meal_categories=_meal_categories(meal),
        modality_availability=["text"],
        modality_resources={"text": f"{recipe_id}.md"},
        ingredient_resolution_summary={
            "fully_resolved": 0,
            "partial": 0,
            "unresolved": len(ingredients),
        },
        ingredient_resolution_status="unresolved_pending_review",
    )
    recipe = Recipe(
        title=title,
        ingredients=tuple(ingredients),
        steps=tuple(steps),
        servings=yields.count,
        source_url=source_url,
        attribution=SOURCE_NAME,
    )
    body = emit_cooklang(recipe)
    return ConvertedRecipe(
        recipe_id=recipe_id,
        frontmatter=frontmatter,
        cooklang_body=body,
        upstream_meal_id=upstream_id,
    )


# -- driver ----------------------------------------------------------------


@dataclass(frozen=True)
class SeedOutcome:
    fetched: int
    written: int
    skipped_upstream_ids: tuple[str, ...]


def seed_recipes(
    client: TheMealDBClient,
    vault,  # RecipeVault (avoids circular import at module load)
    *,
    letters: Iterable[str] = ("a", "b", "c"),
    limit: int | None = None,
    ingested_at: str | None = None,
) -> SeedOutcome:
    """Walk ``letters`` calling ``search.php?f=<letter>``; write each new meal.

    ``limit`` caps the total number of writes; ``None`` writes everything
    the API returns for the requested letters. Duplicates (by upstream meal
    id already ingested) are skipped.
    """
    written = 0
    fetched = 0
    skipped: list[str] = []

    def _legacy_url_id(attribution: dict[str, Any]) -> str:
        # Fallback for older writes that predate upstream_id in attribution
        url = attribution.get("source_url") or ""
        marker = "themealdb.com/meal/"
        return url.rsplit("/", 1)[-1] if marker in url else ""

    seen_upstream = collect_upstream_ids(
        vault, SOURCE_NAME, fallback=_legacy_url_id
    )

    for letter in letters:
        meals = client.search_by_letter(letter)
        for meal in meals:
            fetched += 1
            upstream_id = (meal.get("idMeal") or "").strip()
            if upstream_id and upstream_id in seen_upstream:
                skipped.append(upstream_id)
                continue
            converted = convert_meal(meal, ingested_at=ingested_at)
            vault.write(
                converted.recipe_id,
                converted.frontmatter,
                converted.cooklang_body,
            )
            written += 1
            if upstream_id:
                seen_upstream.add(upstream_id)
            if limit is not None and written >= limit:
                return SeedOutcome(
                    fetched=fetched,
                    written=written,
                    skipped_upstream_ids=tuple(skipped),
                )
    return SeedOutcome(
        fetched=fetched,
        written=written,
        skipped_upstream_ids=tuple(skipped),
    )
