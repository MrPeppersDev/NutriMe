"""NHLBI "Delicious Heart Healthy Eating" bulk-HTML adapter.

Sub-commit 4.2 source (b) per the step 4 entry decision: ~54 recipes at
nhlbi.nih.gov, public domain per 17 USC §105 (US federal government work).
robots.txt verified 2026-07-07: recipe paths permitted, no crawl-delay.

Page shapes (verified live 2026-07-07):
- Listing paginated via ``?page=N`` with recipe links under
  ``/health/heart-healthy-living/healthy-foods/healthy-eating-recipes/<slug>``
- Recipe page: ``<h2>Ingredients</h2><ul><li>…`` + ``<h2>Directions</h2>
  <ol><li>…`` + a meta table with Prep Time / Cook Time / Yields /
  Serving Size rows in Drupal ``field__item`` cells.

Attribution + source URL are preserved per the S9 attribution block even
though public-domain status doesn't legally require it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from nutrime.recipes.allergens import detect_allergens
from nutrime.recipes.cooklang import (
    Ingredient,
    Recipe,
    emit_cooklang,
    split_ingredient_line,
)
from nutrime.recipes.frontmatter import (
    Attribution,
    Yields,
    build_recipe_frontmatter,
)
from nutrime.recipes.ids import new_recipe_id
from nutrime.recipes.store import collect_upstream_ids
from nutrime.recipes.themealdb import SeedOutcome
from nutrime.recipes.web import (
    Pacer,
    TextFetcher,
    _urllib_fetch_text,
    extract_list_items,
    now_iso,
    parse_duration_minutes,
    strip_tags,
)

BASE_URL = "https://www.nhlbi.nih.gov"
LISTING_PATH = (
    "/health/heart-healthy-living/healthy-foods/healthy-eating-recipes"
)
SOURCE_NAME = "NHLBI Delicious Heart Healthy Eating"
SOURCE_LICENSE = (
    "Public domain (17 USC §105) — US federal government work"
)
INGESTION_METHOD = "nhlbi_html_v1"

_RECIPE_HREF = re.compile(
    rf'href="({re.escape(LISTING_PATH)}/[a-z0-9\-]+)"'
)


def list_recipe_urls(
    fetcher: TextFetcher | None = None,
    *,
    pacer: Pacer | None = None,
    max_pages: int = 20,
) -> list[str]:
    """Walk ``?page=0..N`` collecting recipe URLs; stop on a page with no new."""
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    pace = pacer if pacer is not None else Pacer()
    seen: dict[str, None] = {}
    for page in range(max_pages):
        if page > 0:
            pace.wait()
        html = fetch(f"{BASE_URL}{LISTING_PATH}?page={page}")
        before = len(seen)
        for match in _RECIPE_HREF.finditer(html):
            seen.setdefault(f"{BASE_URL}{match.group(1)}", None)
        if len(seen) == before:
            break
    return list(seen)


# -- recipe page parsing ----------------------------------------------------


@dataclass(frozen=True)
class ParsedNhlbiRecipe:
    url: str
    slug: str
    title: str
    ingredients: tuple[str, ...]
    steps: tuple[str, ...]
    prep_min: int | None
    cook_min: int | None
    yields_count: int | None
    serving_size: str


def _meta_field(html: str, label: str) -> str:
    match = re.search(
        rf"<th>\s*{re.escape(label)}\s*</th>.{{0,400}}?field__item[^>]*>\s*([^<]+)",
        html,
        re.S,
    )
    return match.group(1).strip() if match else ""


def parse_recipe_page(html: str, url: str) -> ParsedNhlbiRecipe:
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    title_match = re.search(r"<title>([^<|]+)", html)
    title = (title_match.group(1).strip() if title_match else slug).strip()

    ing_match = re.search(r"<h2>Ingredients</h2>\s*<ul>(.*?)</ul>", html, re.S)
    ingredients = extract_list_items(ing_match.group(1)) if ing_match else []

    dir_match = re.search(r"<h2>Directions</h2>\s*<ol>(.*?)</ol>", html, re.S)
    steps = extract_list_items(dir_match.group(1)) if dir_match else []

    prep_min = parse_duration_minutes(_meta_field(html, "Prep Time"))
    cook_min = parse_duration_minutes(_meta_field(html, "Cook Time"))

    yields_text = _meta_field(html, "Yields")
    yields_match = re.search(r"(\d+)", yields_text)
    yields_count = int(yields_match.group(1)) if yields_match else None

    serving_size = strip_tags(_meta_field(html, "Serving Size"))
    return ParsedNhlbiRecipe(
        url=url,
        slug=slug,
        title=title,
        ingredients=tuple(ingredients),
        steps=tuple(steps),
        prep_min=prep_min,
        cook_min=cook_min,
        yields_count=yields_count,
        serving_size=serving_size,
    )


# -- conversion -------------------------------------------------------------


@dataclass(frozen=True)
class ConvertedNhlbiRecipe:
    recipe_id: str
    frontmatter: dict
    cooklang_body: str
    upstream_id: str


def convert_recipe(
    parsed: ParsedNhlbiRecipe, *, ingested_at: str | None = None
) -> ConvertedNhlbiRecipe:
    when = ingested_at or now_iso()
    recipe_id = new_recipe_id()

    ingredients: list[Ingredient] = []
    for raw in parsed.ingredients:
        qty, unit, name = split_ingredient_line(raw)
        ingredients.append(
            Ingredient(name=name or raw, quantity=qty, unit=unit)
        )

    allergens = detect_allergens([ing.name for ing in ingredients])
    total_min = None
    if parsed.prep_min is not None or parsed.cook_min is not None:
        total_min = (parsed.prep_min or 0) + (parsed.cook_min or 0)

    attribution = Attribution(
        source_name=SOURCE_NAME,
        source_url=parsed.url,
        source_license=SOURCE_LICENSE,
        ingested_at=when,
        ingestion_method=INGESTION_METHOD,
        upstream_id=parsed.slug,
    )
    yields = Yields(
        count=parsed.yields_count or 4,
        yield_note=parsed.serving_size or None,
    )
    frontmatter = build_recipe_frontmatter(
        recipe_id=recipe_id,
        title=parsed.title,
        attribution=attribution,
        source_status="live",
        last_source_check_at=when,
        yields=yields,
        top_allergens_present=allergens,
        meal_categories=["heart-healthy"],
        modality_availability=["text"],
        modality_resources={"text": f"{recipe_id}.md"},
        estimated_active_time_min=parsed.prep_min,
        estimated_total_time_min=total_min,
        ingredient_resolution_summary={
            "fully_resolved": 0,
            "partial": 0,
            "unresolved": len(ingredients),
        },
        ingredient_resolution_status="unresolved_pending_review",
    )
    recipe = Recipe(
        title=parsed.title,
        ingredients=tuple(ingredients),
        steps=parsed.steps,
        servings=yields.count,
        source_url=parsed.url,
        attribution=SOURCE_NAME,
    )
    return ConvertedNhlbiRecipe(
        recipe_id=recipe_id,
        frontmatter=frontmatter,
        cooklang_body=emit_cooklang(recipe),
        upstream_id=parsed.slug,
    )


# -- driver ------------------------------------------------------------------


def seed_recipes(
    vault,  # RecipeVault
    *,
    fetcher: TextFetcher | None = None,
    pacer: Pacer | None = None,
    limit: int | None = None,
    ingested_at: str | None = None,
) -> SeedOutcome:
    """Crawl the listing then each new recipe page; write to the vault."""
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    pace = pacer if pacer is not None else Pacer()
    seen_upstream = collect_upstream_ids(vault, SOURCE_NAME)

    fetched = 0
    written = 0
    skipped: list[str] = []
    for url in list_recipe_urls(fetch, pacer=pace):
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        if slug in seen_upstream:
            skipped.append(slug)
            continue
        if limit is not None and written >= limit:
            break
        pace.wait()
        html = fetch(url)
        fetched += 1
        converted = convert_recipe(
            parse_recipe_page(html, url), ingested_at=ingested_at
        )
        vault.write(
            converted.recipe_id,
            converted.frontmatter,
            converted.cooklang_body,
        )
        written += 1
        seen_upstream.add(slug)
    return SeedOutcome(
        fetched=fetched,
        written=written,
        skipped_upstream_ids=tuple(skipped),
    )
