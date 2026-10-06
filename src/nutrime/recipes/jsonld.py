"""schema.org/Recipe JSON-LD URL-scrape adapter (sub-commit 4.4, unparked).

Per the step 4 entry decision, schema.org/Recipe JSON-LD is the canonical
interchange format for structured ingest from arbitrary web sources
(Mealie / Tandoor as prior art, reference only). Unparked 2026-10-03 by the
household-user Pinterest product pull (issue #24): a Pinterest pin is a
link to an external recipe page, so "ingest my pinned recipes" reduces to
"ingest this list of URLs".

MVP front door is a local file of URLs (one per line, ``#`` comments
allowed) — sourced from a Pinterest account data export or links copied
out of the app. No Pinterest API / OAuth at this cut; that is the
"keep it synced" follow-up on #24.

License posture: pages ingested this way are personal-use web captures.
Attribution records the page's host + URL and an honest
"all rights reserved by source" license line — this content is for the
household's private corpus, never redistribution.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

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
from nutrime.recipes.web import (
    Pacer,
    TextFetcher,
    _urllib_fetch_text,
    now_iso,
    strip_tags,
)

SOURCE_LICENSE = (
    "Personal-use web capture — all rights reserved by source"
)
INGESTION_METHOD = "schema_org_jsonld_v1"

_LD_SCRIPT = re.compile(
    r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.S | re.I,
)
_ISO_DURATION = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+)S)?)?$"
)


def parse_iso_duration_minutes(value: Any) -> int | None:
    """``"PT1H30M"`` → 90. Returns None for anything unparseable."""
    if not isinstance(value, str):
        return None
    match = _ISO_DURATION.match(value.strip())
    if not match or not any(match.groupdict().values()):
        return None
    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    total = days * 24 * 60 + hours * 60 + minutes + (1 if seconds >= 30 else 0)
    return total if total > 0 else None


def _is_recipe_node(node: Any) -> bool:
    if not isinstance(node, dict):
        return False
    node_type = node.get("@type")
    if isinstance(node_type, str):
        return node_type.lower() == "recipe"
    if isinstance(node_type, list):
        return any(
            isinstance(t, str) and t.lower() == "recipe" for t in node_type
        )
    return False


def _walk_for_recipe(payload: Any) -> dict[str, Any] | None:
    """Find the first Recipe node in a JSON-LD payload (@graph-tolerant)."""
    if _is_recipe_node(payload):
        return payload
    if isinstance(payload, dict):
        graph = payload.get("@graph")
        if isinstance(graph, list):
            for node in graph:
                found = _walk_for_recipe(node)
                if found is not None:
                    return found
    if isinstance(payload, list):
        for node in payload:
            found = _walk_for_recipe(node)
            if found is not None:
                return found
    return None


def extract_recipe_jsonld(html_text: str) -> dict[str, Any] | None:
    """Return the first schema.org Recipe node in the page, or None.

    Scans every ``application/ld+json`` script block; malformed JSON in one
    block never aborts the scan of the rest (real-world pages ship broken
    sibling blocks routinely).
    """
    for raw in _LD_SCRIPT.findall(html_text):
        try:
            payload = json.loads(raw.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        node = _walk_for_recipe(payload)
        if node is not None:
            return node
    return None


# -- Recipe node → domain conversion ----------------------------------------


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item)
        return out
    return []


def _extract_steps(value: Any) -> list[str]:
    """Flatten recipeInstructions: string | [string] | HowToStep | HowToSection."""
    if isinstance(value, str):
        text = strip_tags(value)
        return [text] if text else []
    steps: list[str] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                text = strip_tags(item)
                if text:
                    steps.append(text)
            elif isinstance(item, dict):
                item_type = str(item.get("@type") or "").lower()
                if item_type == "howtosection":
                    steps.extend(_extract_steps(item.get("itemListElement")))
                else:  # HowToStep or untyped dict with text/name
                    text = strip_tags(
                        str(item.get("text") or item.get("name") or "")
                    )
                    if text:
                        steps.append(text)
    return steps


def _extract_equipment(node: dict[str, Any]) -> list[str]:
    """schema.org ``tool`` → equipment names (V4, populate-where-stated).

    Shapes in the wild: string, list of strings, HowToTool dicts (name
    key). No inference from instruction text — stated-only per the
    honesty discipline.
    """
    value = node.get("tool")
    items = value if isinstance(value, list) else [value] if value else []
    out: list[str] = []
    for item in items:
        name = ""
        if isinstance(item, str):
            name = strip_tags(item)
        elif isinstance(item, dict):
            name = strip_tags(str(item.get("name") or ""))
        name = name.strip()
        if name and name.lower() not in {n.lower() for n in out}:
            out.append(name)
    return out


def _extract_yield(value: Any) -> Yields:
    candidates = value if isinstance(value, list) else [value]
    for candidate in candidates:
        if isinstance(candidate, (int, float)) and int(candidate) > 0:
            return Yields(count=int(candidate))
        if isinstance(candidate, str):
            match = re.search(r"\d+", candidate)
            if match:
                return Yields(count=int(match.group()), yield_note=candidate)
    return Yields(count=4)


def _host(url: str) -> str:
    netloc = urlparse(url).netloc
    return netloc.removeprefix("www.") or "unknown host"


def normalize_url(url: str) -> str:
    """De-dup key: scheme/host lowercased, fragment + trailing slash dropped."""
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}{query}"


@dataclass(frozen=True)
class ConvertedRecipe:
    recipe_id: str
    frontmatter: dict[str, Any]
    cooklang_body: str
    source_url: str


def convert_recipe_node(
    node: dict[str, Any],
    *,
    source_url: str,
    ingested_at: str | None = None,
    ingestion_method: str = INGESTION_METHOD,
    source_license: str = SOURCE_LICENSE,
    source_name: str | None = None,
) -> ConvertedRecipe:
    """Map one schema.org Recipe node → (frontmatter, Cooklang body).

    The crawler (#32) reuses this with its own ingestion method, licence
    note and site name so crawled pages stay a distinct collection.
    """
    when = ingested_at or now_iso()
    recipe_id = new_recipe_id()
    title = strip_tags(str(node.get("name") or "")) or "Untitled Recipe"

    ingredients: list[Ingredient] = []
    for line in _as_text_list(node.get("recipeIngredient")):
        qty, unit, name = split_ingredient_line(strip_tags(line))
        if name:
            ingredients.append(Ingredient(name=name, quantity=qty, unit=unit))

    steps = _extract_steps(node.get("recipeInstructions"))
    allergens = detect_allergens([ing.name for ing in ingredients])
    yields = _extract_yield(node.get("recipeYield"))

    total_min = parse_iso_duration_minutes(node.get("totalTime"))
    if total_min is None:
        prep = parse_iso_duration_minutes(node.get("prepTime"))
        cook = parse_iso_duration_minutes(node.get("cookTime"))
        if prep is not None or cook is not None:
            total_min = (prep or 0) + (cook or 0)
    active_min = parse_iso_duration_minutes(node.get("prepTime"))

    cuisines = [
        c.strip().lower()
        for c in _as_text_list(node.get("recipeCuisine"))
        if c.strip()
    ]
    categories = [
        c.strip().lower()
        for c in _as_text_list(node.get("recipeCategory"))
        if c.strip()
    ]

    attribution = Attribution(
        source_name=source_name or _host(source_url),
        source_url=source_url,
        source_license=source_license,
        ingested_at=when,
        ingestion_method=ingestion_method,
        upstream_id=normalize_url(source_url),
    )
    frontmatter = build_recipe_frontmatter(
        recipe_id=recipe_id,
        title=title,
        attribution=attribution,
        source_status="live",
        last_source_check_at=when,
        yields=yields,
        top_allergens_present=allergens,
        cuisine_tradition_tags=cuisines,
        meal_categories=categories,
        modality_availability=["text"],
        modality_resources={"text": f"{recipe_id}.md"},
        estimated_active_time_min=active_min,
        estimated_total_time_min=total_min,
        ingredient_resolution_summary={
            "fully_resolved": 0,
            "partial": 0,
            "unresolved": len(ingredients),
        },
        ingredient_resolution_status="unresolved_pending_review",
    )
    equipment = _extract_equipment(node)
    if equipment:
        frontmatter["equipment_required"] = equipment
    recipe = Recipe(
        title=title,
        ingredients=tuple(ingredients),
        steps=tuple(steps),
        servings=yields.count,
        source_url=source_url,
        attribution=source_name or _host(source_url),
    )
    return ConvertedRecipe(
        recipe_id=recipe_id,
        frontmatter=frontmatter,
        cooklang_body=emit_cooklang(recipe),
        source_url=source_url,
    )


# -- driver ------------------------------------------------------------------


def read_urls_file(path: Path) -> list[str]:
    """One URL per line; blank lines and ``#`` comments skipped."""
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.append(stripped)
    return urls


@dataclass(frozen=True)
class SeedOutcome:
    fetched: int
    written: int
    skipped_upstream_ids: tuple[str, ...]
    # URL → reason, for pages that fetched but yielded no usable recipe
    # (no JSON-LD Recipe node, fetch error). First cut: skip + report,
    # per #24 — no microdata fallback yet.
    failures: tuple[tuple[str, str], ...] = ()


def seed_recipes(
    vault,  # RecipeVault (avoids circular import at module load)
    urls: Iterable[str],
    *,
    fetcher: TextFetcher | None = None,
    pacer: Pacer | None = None,
    limit: int | None = None,
    ingested_at: str | None = None,
) -> SeedOutcome:
    """Fetch each URL, extract its Recipe node, write new recipes to the vault.

    De-dup is per normalized URL across *all* JSON-LD-ingested recipes:
    source_name varies by host, so upstream ids are collected by
    INGESTION_METHOD rather than via ``collect_upstream_ids`` (which keys
    on a single source_name).
    """
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    pacer = pacer or Pacer(delay_s=1.0)

    seen: set[str] = set()
    for record in vault.iter_recipes():
        attribution = record.frontmatter.get("attribution", {}) or {}
        if attribution.get("ingestion_method") == INGESTION_METHOD:
            upstream = attribution.get("upstream_id") or ""
            if upstream:
                seen.add(upstream)

    fetched = 0
    written = 0
    skipped: list[str] = []
    failures: list[tuple[str, str]] = []

    first = True
    for url in urls:
        key = normalize_url(url)
        if key in seen:
            skipped.append(key)
            continue
        if not first:
            pacer.wait()
        first = False
        try:
            html_text = fetch(url)
        except Exception as exc:  # noqa: BLE001 — report, don't abort the run
            failures.append((url, f"fetch failed: {exc}"))
            continue
        fetched += 1
        node = extract_recipe_jsonld(html_text)
        if node is None:
            failures.append((url, "no schema.org/Recipe JSON-LD found"))
            continue
        converted = convert_recipe_node(
            node, source_url=url, ingested_at=ingested_at
        )
        vault.write(
            converted.recipe_id,
            converted.frontmatter,
            converted.cooklang_body,
        )
        seen.add(key)
        written += 1
        if limit is not None and written >= limit:
            break
    return SeedOutcome(
        fetched=fetched,
        written=written,
        skipped_upstream_ids=tuple(skipped),
        failures=tuple(failures),
    )
