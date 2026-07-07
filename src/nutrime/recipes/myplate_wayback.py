"""USDA MyPlate Kitchen adapter — ingested from Internet Archive snapshots.

MyPlate.gov was retired 2026-01-07 (replaced by RealFood.gov alongside the
2025–2030 Dietary Guidelines); the ~1,072-recipe MyPlate Kitchen library was
removed from the live site. The content is public domain per 17 USC §105,
and the Wayback Machine holds full pre-retirement coverage — so this adapter
exercises the preservation-layer principle: frontmatter carries
``source_status='archived_nutrime_preserved'``, ``source_removed_at`` set to
the retirement date, the original myplate.gov URL as ``source_url``, and the
snapshot actually fetched as ``attribution.archived_snapshot_url``.

Mechanics (verified against live Wayback 2026-07-07):
- Recipe URLs enumerate via the CDX API (``collapse=urlkey``), filtered to
  clean ``myplate.gov/recipes/<slug>`` originals (query-string variants and
  hub pages dropped).
- Each snapshot fetches via the ``id_`` URL form, which serves the original
  bytes without the Wayback toolbar injection.
- Recipe pages are Drupal 10: schema.org Recipe JSON-LD carries
  name/description/yield/nutrition; ingredients + instructions + notes +
  contributor live in ``field--name-field-*`` markup.
"""

from __future__ import annotations

import json
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
    strip_tags,
)

SOURCE_NAME = "USDA MyPlate Kitchen"
SOURCE_LICENSE = (
    "Public domain (17 USC §105) — US federal government work"
)
INGESTION_METHOD = "myplate_wayback_html_v1"
SOURCE_REMOVED_AT = "2026-01-07T00:00:00Z"
MATERIAL_IMPLICATION_NOTE = (
    "MyPlate.gov retired 2026-01-07 (replaced by RealFood.gov); content"
    " preserved from Internet Archive snapshot per preservation-layer"
    " principle. Public-domain status (17 USC §105) unaffected."
)

CDX_URL = (
    "https://web.archive.org/cdx/search/cdx"
    "?url=myplate.gov/recipes/*&output=json"
    "&filter=statuscode:200&filter=mimetype:text/html"
    "&collapse=urlkey&from=2024&to=20260107"
)

_CLEAN_RECIPE_URL = re.compile(
    r"^https?://(?:www\.)?myplate\.gov/recipes/([a-z0-9\-]+)/?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ArchivedRecipeRef:
    slug: str
    original_url: str
    timestamp: str

    @property
    def snapshot_url(self) -> str:
        return (
            f"https://web.archive.org/web/{self.timestamp}id_/"
            f"{self.original_url}"
        )


def list_archived_recipes(
    fetcher: TextFetcher | None = None,
) -> list[ArchivedRecipeRef]:
    """Enumerate archived recipe pages via one CDX API call."""
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    rows = json.loads(fetch(CDX_URL))
    refs: dict[str, ArchivedRecipeRef] = {}
    for row in rows[1:]:  # row 0 is the CDX header
        _, timestamp, original = row[0], row[1], row[2]
        match = _CLEAN_RECIPE_URL.match(original)
        if not match:
            continue
        slug = match.group(1).lower()
        if slug not in refs:
            refs[slug] = ArchivedRecipeRef(
                slug=slug, original_url=original, timestamp=timestamp
            )
    return sorted(refs.values(), key=lambda r: r.slug)


# -- recipe page parsing ----------------------------------------------------


@dataclass(frozen=True)
class ParsedMyPlateRecipe:
    slug: str
    original_url: str
    snapshot_url: str
    title: str
    description: str
    ingredients: tuple[str, ...]
    steps: tuple[str, ...]
    yields_count: int | None
    serving_size: str
    calories_per_serving: str
    contributor: str
    notes: str


def _recipe_jsonld(html: str) -> dict:
    for block in re.findall(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "Recipe":
                return node
    return {}


def _field_window(html: str, field: str, end: str) -> str:
    """Content of a Drupal field block: after its opening tag, up to ``end``."""
    match = re.search(
        rf"field--name-{re.escape(field)}[^>]*>(.*?){end}", html, re.S
    )
    return match.group(1) if match else ""


def parse_recipe_page(html: str, ref: ArchivedRecipeRef) -> ParsedMyPlateRecipe:
    node = _recipe_jsonld(html)
    title = (node.get("name") or ref.slug.replace("-", " ").title()).strip()
    description = (node.get("description") or "").strip()

    yields_count: int | None = None
    yield_match = re.search(r"\d+", str(node.get("recipeYield") or ""))
    if yield_match:
        yields_count = int(yield_match.group(0))

    nutrition = node.get("nutrition") or {}
    calories = str(nutrition.get("calories") or "").strip()

    ingredients = extract_list_items(
        _field_window(html, "field-ingredients", "</ul>")
    )
    steps = extract_list_items(
        _field_window(html, "field-instructions", "</ol>")
    )
    serving_size = strip_tags(
        _field_window(html, "field-recipe-serving-size", "</div>")
    ).removeprefix("Serving Size:").strip()
    contributor = strip_tags(
        _field_window(html, "field-source", "</div>")
    ).removeprefix("Source:").strip()
    notes = strip_tags(_field_window(html, "field-notes", "</div>"))
    if notes.lower().startswith("notes"):
        notes = notes[5:].strip(" :")

    return ParsedMyPlateRecipe(
        slug=ref.slug,
        original_url=ref.original_url,
        snapshot_url=ref.snapshot_url,
        title=title,
        description=description,
        ingredients=tuple(ingredients),
        steps=tuple(steps),
        yields_count=yields_count,
        serving_size=serving_size,
        calories_per_serving=calories,
        contributor=contributor,
        notes=notes,
    )


# -- conversion -------------------------------------------------------------


@dataclass(frozen=True)
class ConvertedMyPlateRecipe:
    recipe_id: str
    frontmatter: dict
    cooklang_body: str
    upstream_id: str


def convert_recipe(
    parsed: ParsedMyPlateRecipe, *, ingested_at: str | None = None
) -> ConvertedMyPlateRecipe:
    when = ingested_at or now_iso()
    recipe_id = new_recipe_id()

    ingredients: list[Ingredient] = []
    for raw in parsed.ingredients:
        qty, unit, name = split_ingredient_line(raw)
        ingredients.append(
            Ingredient(name=name or raw, quantity=qty, unit=unit)
        )
    allergens = detect_allergens([ing.name for ing in ingredients])

    attribution = Attribution(
        source_name=SOURCE_NAME,
        source_url=parsed.original_url,
        source_license=SOURCE_LICENSE,
        ingested_at=when,
        ingestion_method=INGESTION_METHOD,
        upstream_id=parsed.slug,
        archived_snapshot_url=parsed.snapshot_url,
    )
    yields = Yields(
        count=parsed.yields_count or 4,
        yield_note=parsed.serving_size or None,
    )
    frontmatter = build_recipe_frontmatter(
        recipe_id=recipe_id,
        title=parsed.title,
        attribution=attribution,
        source_status="archived_nutrime_preserved",
        last_source_check_at=when,
        source_removed_at=SOURCE_REMOVED_AT,
        material_implication_note=MATERIAL_IMPLICATION_NOTE,
        yields=yields,
        top_allergens_present=allergens,
        meal_categories=[],
        modality_availability=["text"],
        modality_resources={"text": f"{recipe_id}.md"},
        ingredient_resolution_summary={
            "fully_resolved": 0,
            "partial": 0,
            "unresolved": len(ingredients),
        },
        ingredient_resolution_status="unresolved_pending_review",
    )

    extra_metadata: list[tuple[str, str]] = []
    if parsed.description:
        extra_metadata.append(("description", parsed.description))
    if parsed.calories_per_serving:
        extra_metadata.append(
            ("calories_per_serving", parsed.calories_per_serving)
        )
    if parsed.contributor:
        extra_metadata.append(("original_contributor", parsed.contributor))
    if parsed.notes:
        extra_metadata.append(("notes", parsed.notes))

    recipe = Recipe(
        title=parsed.title,
        ingredients=tuple(ingredients),
        steps=parsed.steps,
        servings=yields.count,
        source_url=parsed.original_url,
        attribution=SOURCE_NAME,
        extra_metadata=tuple(extra_metadata),
    )
    return ConvertedMyPlateRecipe(
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
    """Enumerate via CDX, then fetch + convert + write each new recipe."""
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    pace = pacer if pacer is not None else Pacer()
    seen_upstream = collect_upstream_ids(vault, SOURCE_NAME)

    fetched = 0
    written = 0
    skipped: list[str] = []
    for ref in list_archived_recipes(fetch):
        if ref.slug in seen_upstream:
            skipped.append(ref.slug)
            continue
        if limit is not None and written >= limit:
            break
        pace.wait()
        html = fetch(ref.snapshot_url)
        fetched += 1
        converted = convert_recipe(
            parse_recipe_page(html, ref), ingested_at=ingested_at
        )
        vault.write(
            converted.recipe_id,
            converted.frontmatter,
            converted.cooklang_body,
        )
        written += 1
        seen_upstream.add(ref.slug)
    return SeedOutcome(
        fetched=fetched,
        written=written,
        skipped_upstream_ids=tuple(skipped),
    )
