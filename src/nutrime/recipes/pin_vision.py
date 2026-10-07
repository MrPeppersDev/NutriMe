"""Vision extraction for image-only pins — the #24 queue consumer.

``pinboard.backfill_board`` queues pins whose recipe is baked into the
picture (no usable outbound link) to ``pinterest_image_pins.jsonl``.
This module drains that queue: each pending image goes to a local
vision model (Ollama, ``qwen2.5vl:7b`` by default) which reads the
picture and returns the recipe as structured JSON; valid answers are
written to the vault as normal recipes, same shapes as every other
ingest.

Postures, consistent with the rest of the LLM tier:

- Local only. The pin photos are the household's own board content and
  the tier's "never cloud" stance holds (llm_classify precedent) —
  the request is built with CAP_LOCAL_PRIVATE + CAP_VISION required,
  so a missing local vision model fails with setup guidance, never a
  cloud fallback.
- Validate hard. A reply must parse as JSON with a plausible title,
  ≥2 ingredients and ≥1 step, else the pin is marked
  ``vision_extraction_failed`` (kept in the queue for re-runs with a
  better model, never retried in the same run, never half-written to
  the vault).
- Idempotent. Only ``pending_vision_extraction`` entries run; done
  entries carry ``extracted`` + the recipe id. Re-running after an
  interrupt resumes where it stopped — the queue file is rewritten
  after every pin so a crash loses at most the in-flight one.
- Low trust in extracted text. The model transcribes a photo the
  household pinned: ingredient lines go through the same
  ``split_ingredient_line`` + ``detect_allergens`` as scraped recipes,
  the vault gets ``ingestion_method='pin_vision_extraction'`` and the
  recipe body carries the pin URL so the picture remains the source of
  truth a human can check.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from nutrime.llm.base import (
    CAP_LOCAL_PRIVATE,
    CAP_VISION,
    ChatMessage,
    LlmRequest,
)
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
from nutrime.recipes.web import now_iso

PIN_VISION_EXTRACTION = "pin_vision_extraction"
VISION_MODEL_DEFAULT = "qwen2.5vl:7b"

STATUS_PENDING = "pending_vision_extraction"
STATUS_DONE = "extracted"
STATUS_FAILED = "vision_extraction_failed"

SOURCE_LICENSE = (
    "Personal-use capture of the household's own pinned image"
    " — recipe transcribed by a local vision model; verify against"
    " the picture before sharing."
)

_SYSTEM = (
    "You read recipe photos. The image is a recipe card or infographic;"
    " transcribe exactly what it shows — do not invent quantities, steps"
    " or a title that are not in the picture. Reply with JSON only:"
    ' {"is_recipe": true|false, "title": <string>,'
    ' "ingredients": [<one string per ingredient line, quantities kept>],'
    ' "steps": [<one string per instruction step>],'
    ' "servings": <int or null>, "total_minutes": <int or null>}.'
    " If the image is not a readable recipe (a food photo with no text,"
    " a cover image, an ad), reply {\"is_recipe\": false}."
    " No prose, no markdown fences."
)

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)

# Transcriptions are model output over a photo: bound every field so a
# hallucinating run can't write junk shaped like a recipe.
_MAX_TITLE_CHARS = 120
_MAX_LINES = 60
_MAX_LINE_CHARS = 300


def register_envelope(registry) -> None:
    registry.register(PIN_VISION_EXTRACTION, ())  # recipe photos, no PHI


class ImageFetchError(Exception):
    """The pin's image URL could not be fetched."""


def _fetch_image(url: str, timeout_s: float = 30.0) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "NutriMe/pin-vision (+household ingest)"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            return response.read()
    except Exception as exc:  # noqa: BLE001 — caller marks + moves on
        raise ImageFetchError(f"image fetch failed: {exc}") from exc


@dataclass(frozen=True)
class Extracted:
    title: str
    ingredient_lines: tuple[str, ...]
    steps: tuple[str, ...]
    servings: int | None
    total_minutes: int | None


def parse_vision_reply(text: str) -> Extracted | None:
    """Parse + validate a model reply; None means 'not a usable recipe'.

    A None is a *verdict* (not-a-recipe, or unusable transcription) —
    JSON that doesn't parse at all raises, so the caller can tell model
    noise from an honest negative.
    """
    match = _JSON_OBJECT.search(text or "")
    if match is None:
        raise ValueError(f"no JSON object in model reply: {text!r:.200}")
    payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise ValueError("model reply is not an object")
    if not payload.get("is_recipe"):
        return None

    title = str(payload.get("title") or "").strip()
    if not title or len(title) > _MAX_TITLE_CHARS:
        return None

    def _lines(key: str) -> tuple[str, ...]:
        raw = payload.get(key)
        if not isinstance(raw, list):
            return ()
        out = []
        for entry in raw[:_MAX_LINES]:
            line = str(entry).strip()
            if line and len(line) <= _MAX_LINE_CHARS:
                out.append(line)
        return tuple(out)

    ingredients = _lines("ingredients")
    steps = _lines("steps")
    if len(ingredients) < 2 or not steps:
        return None

    def _int_or_none(key: str, lo: int, hi: int) -> int | None:
        value = payload.get(key)
        try:
            value = int(value)
        except (TypeError, ValueError):
            return None
        return value if lo <= value <= hi else None

    return Extracted(
        title=title,
        ingredient_lines=ingredients,
        steps=steps,
        servings=_int_or_none("servings", 1, 64),
        total_minutes=_int_or_none("total_minutes", 1, 2880),
    )


def convert_extracted(
    extracted: Extracted,
    *,
    pin_url: str,
    image_url: str,
    ingested_at: str | None = None,
):
    """Extracted → ConvertedRecipe-shaped triple for the vault."""
    when = ingested_at or now_iso()
    recipe_id = new_recipe_id()

    ingredients: list[Ingredient] = []
    for line in extracted.ingredient_lines:
        qty, unit, name = split_ingredient_line(line)
        if name:
            ingredients.append(Ingredient(name=name, quantity=qty, unit=unit))

    attribution = Attribution(
        source_name="Pinterest pin (image transcription)",
        source_url=pin_url,
        source_license=SOURCE_LICENSE,
        ingested_at=when,
        ingestion_method=PIN_VISION_EXTRACTION,
        upstream_id=pin_url,
    )
    frontmatter = build_recipe_frontmatter(
        recipe_id=recipe_id,
        title=extracted.title,
        attribution=attribution,
        source_status="live",
        last_source_check_at=when,
        yields=Yields(count=extracted.servings or 4, unit="servings"),
        top_allergens_present=detect_allergens(
            [ing.name for ing in ingredients]
        ),
        modality_availability=["text", "image"],
        modality_resources={"text": f"{recipe_id}.md", "image": image_url},
        estimated_total_time_min=extracted.total_minutes,
        ingredient_resolution_summary={
            "fully_resolved": 0,
            "partial": 0,
            "unresolved": len(ingredients),
        },
        ingredient_resolution_status="unresolved_pending_review",
    )
    recipe = Recipe(
        title=extracted.title,
        ingredients=tuple(ingredients),
        steps=tuple(extracted.steps),
        servings=extracted.servings,
        source_url=pin_url,
        attribution="Pinterest pin (image transcription)",
    )
    return recipe_id, frontmatter, emit_cooklang(recipe)


# -- queue driver -------------------------------------------------------------


@dataclass(frozen=True)
class ExtractOutcome:
    pending: int
    written: int
    not_recipes: int
    failures: tuple[tuple[str, str], ...]  # (pin_id, reason)


def _load_queue(queue_path: Path) -> list[dict]:
    entries: list[dict] = []
    if not queue_path.exists():
        return entries
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def _save_queue(queue_path: Path, entries: list[dict]) -> None:
    tmp = queue_path.with_suffix(".tmp")
    tmp.write_text(
        "".join(json.dumps(entry) + "\n" for entry in entries),
        encoding="utf-8",
    )
    tmp.replace(queue_path)


def extract_queued_pins(
    queue_path: Path,
    vault,  # RecipeVault
    client,  # LlmClient
    *,
    limit: int | None = None,
    image_fetcher=None,
    max_tokens: int = 2048,
) -> ExtractOutcome:
    """Drain pending image pins through the local vision model."""
    entries = _load_queue(queue_path)
    fetch = image_fetcher or _fetch_image

    pending = [
        e for e in entries if e.get("status") == STATUS_PENDING
    ]
    written = 0
    not_recipes = 0
    failures: list[tuple[str, str]] = []

    ran = 0
    for entry in entries:
        if entry.get("status") != STATUS_PENDING:
            continue
        if limit is not None and ran >= limit:
            break
        ran += 1
        pin_id = str(entry.get("pin_id") or "")
        try:
            image = fetch(str(entry.get("image_url") or ""))
            context = str(entry.get("title") or "").strip()
            prompt = (
                "Transcribe the recipe in this image."
                + (f' The pin was titled: "{context}".' if context else "")
            )
            response = client.complete(
                LlmRequest(
                    query_type=PIN_VISION_EXTRACTION,
                    system=_SYSTEM,
                    messages=(
                        ChatMessage(
                            role="user", content=prompt, images=(image,)
                        ),
                    ),
                    max_tokens=max_tokens,
                    required_capabilities=frozenset(
                        {CAP_LOCAL_PRIVATE, CAP_VISION}
                    ),
                    caller_context="recipes/pin_vision",
                )
            )
            extracted = parse_vision_reply(response.text)
        except Exception as exc:  # noqa: BLE001 — mark + continue the queue
            entry["status"] = STATUS_FAILED
            entry["failed_reason"] = str(exc)[:300]
            failures.append((pin_id, str(exc)[:300]))
            _save_queue(queue_path, entries)
            continue

        if extracted is None:
            entry["status"] = STATUS_FAILED
            entry["failed_reason"] = "not a readable recipe image"
            not_recipes += 1
            _save_queue(queue_path, entries)
            continue

        recipe_id, frontmatter, body = convert_extracted(
            extracted,
            pin_url=str(entry.get("pin_url") or ""),
            image_url=str(entry.get("image_url") or ""),
        )
        vault.write(recipe_id, frontmatter, body)
        entry["status"] = STATUS_DONE
        entry["recipe_id"] = recipe_id
        written += 1
        _save_queue(queue_path, entries)

    return ExtractOutcome(
        pending=len(pending),
        written=written,
        not_recipes=not_recipes,
        failures=tuple(failures),
    )
