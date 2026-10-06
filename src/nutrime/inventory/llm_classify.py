"""Local-LLM tier for pantry classification — the "why" the lexicon lacks.

The lexicon in ``inventory.intake`` is the fast path and the safety
floor: deterministic, instant, offline. This module is the smart tier
layered on top, for the cases a lookup table structurally can't get
right:

- unknown foods ("xylotholo root", regional staples, brand names)
- preservation state the name carries ("opened salsa", "UHT milk",
  "cured chorizo", "cut melon", "fresh pasta") — where opened/cut
  flips shelf-stable to perishable and cured/UHT flips the other way

One batched request to the local Ollama model per paste (never per
item, never cloud — food names are PHI-free but the local-only mandate
holds). Every model answer is validated hard: locations must be one of
the four real locations, shelf days clamp to [0, 730], and any parse or
validation failure falls back to the lexicon's answer for that item —
the model can only ever *refine* a default, never break the flow. The
model being down means the lexicon answer stands, silently.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace

from nutrime.inventory.intake import (
    STATE_WORDS,
    ProposedItem,
    _PERISHABLE_ASK_DAYS,
)
from nutrime.llm.base import ChatMessage, LlmRequest

FOOD_CLASSIFICATION = "food_storage_classification"

_VALID_LOCATIONS = frozenset({"fridge", "pantry", "freezer", "countertop"})
_MAX_SHELF_DAYS = 730

_SYSTEM = (
    "You are a food-storage expert. For each food item, decide where a home"
    " cook should store it and how many days it keeps from today, reasoning"
    " about preservation state: opened/cut items spoil like fresh ones even"
    " if the base food is shelf-stable; cured, canned-unopened, dried, UHT,"
    " and frozen items keep far longer than their fresh forms. Assume items"
    " are in the state the name describes, otherwise as typically purchased."
    " Reply with JSON only: a list of objects"
    ' {"name": "<name copied exactly>", "location":'
    ' "fridge"|"pantry"|"freezer"|"countertop", "shelf_days": <int days it'
    " keeps, or null if it keeps a year or more>}."
    " No prose, no markdown fences."
)

_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


def needs_llm(item: ProposedItem) -> bool:
    """Items the lexicon couldn't settle: unknowns, or names carrying a
    preservation-state word whose meaning a lookup can't invert."""
    return (not item.recognized) or bool(STATE_WORDS.search(item.name))


def register_envelope(registry) -> None:
    registry.register(FOOD_CLASSIFICATION, ())  # food names, no PHI


def refine(items: list[ProposedItem], client) -> list[ProposedItem]:
    """Run the LLM tier over the items that need it; lexicon answers
    survive untouched for everything else and on any failure."""
    targets = [(i, item) for i, item in enumerate(items) if needs_llm(item)]
    if not targets or client is None:
        return items

    listing = "\n".join(f"- {item.name}" for _, item in targets)
    request = LlmRequest(
        query_type=FOOD_CLASSIFICATION,
        system=_SYSTEM,
        messages=(ChatMessage(role="user", content=listing),),
        max_tokens=120 + 60 * len(targets),
        caller_context="inventory/bulk_classify",
    )
    try:
        response = client.complete(request)
        answers = _parse(response.text)
    except Exception:  # noqa: BLE001 — model trouble never breaks a paste
        return items

    out = list(items)
    by_name = {item.name.strip().lower(): i for i, item in targets}
    for answer in answers:
        idx = by_name.get(str(answer.get("name", "")).strip().lower())
        if idx is None:
            continue
        location = str(answer.get("location", "")).strip().lower()
        if location not in _VALID_LOCATIONS:
            continue
        shelf = answer.get("shelf_days")
        if shelf is not None:
            try:
                shelf = max(0, min(int(shelf), _MAX_SHELF_DAYS))
            except (TypeError, ValueError):
                continue
        out[idx] = replace(
            out[idx],
            location=location,
            shelf_days=shelf,
            perishable=(shelf is not None and shelf <= _PERISHABLE_ASK_DAYS),
            recognized=True,
        )
    return out


def _parse(text: str) -> list[dict]:
    match = _JSON_ARRAY.search(text or "")
    if match is None:
        raise ValueError(f"no JSON array in model reply: {text!r:.200}")
    payload = json.loads(match.group(0))
    if not isinstance(payload, list):
        raise ValueError("model reply is not a list")
    return [entry for entry in payload if isinstance(entry, dict)]
