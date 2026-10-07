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

# #56 guard: raw animal protein must never leave this tier with no date
# — "thawed chicken" answered shelf_days=null would mean no use-soon
# nudge ever fires on raw meat. Names matching this get a hard ceiling
# (FDA raw-protein fridge range tops out at 5 days for red-meat cuts)
# and null is replaced by the lexicon's answer or the ceiling.
_RAW_PROTEIN = re.compile(
    r"\b(chicken|turkey|duck|beef|steak|pork|lamb|veal|mince|sausage|"
    r"fish|salmon|cod|tilapia|halibut|trout|tuna|shrimp|prawn|crab|"
    r"scallop|mussel|clam|oyster|lobster|squid|calamari|octopus|"
    r"meat|fillet|filet|cutlet|chop|breast|thigh|drumstick|loin|"
    r"brisket|liver)\b",
    re.I,
)
_RAW_PROTEIN_MAX_DAYS = 5
_CURED = re.compile(
    r"\b(cured|smoked|dried|jerky|canned|tinned|salted|fermented)\b", re.I
)

_SYSTEM = (
    "You are a food-storage expert. For each food item, decide where a home"
    " cook should store it and how many days it keeps from today, reasoning"
    " about preservation state: opened/cut items spoil like fresh ones even"
    " if the base food is shelf-stable; cured, canned-unopened, dried, UHT,"
    " and frozen items keep far longer than their fresh forms. Assume items"
    " are in the state the name describes, otherwise as typically purchased."
    " Also give the item's plain generic food name — the word a recipe's"
    " ingredient list would use (\"chives with chive flowers\" -> \"chives\","
    " \"EVOO\" -> \"olive oil\", \"grandma's strawberry jam\" -> \"strawberry"
    " jam\") — or null when the given name already is the generic name."
    " Never generalize to a broader food: a substitution that changes the"
    " dish is wrong (\"seedy bread\" -> null, NOT \"bread\")."
    " Reply with JSON only: a list of objects"
    ' {"name": "<name copied exactly>", "location":'
    ' "fridge"|"pantry"|"freezer"|"countertop", "shelf_days": <int days it'
    ' keeps, or null if it keeps a year or more>, "generic": <plain food'
    " name, or null>}."
    " No prose, no markdown fences."
)

# A proposed generic name is advisory UI-reviewed data, but still gets
# hard validation: a short food-name shape (≤4 words, ≤40 chars, letters
# only), no sentences, no JSON noise. Reject → None (the display name
# matches on its own or not; never worse than before the tier ran).
_GENERIC_OK = re.compile(r"^[a-z][a-z'-]*( [a-z'-]+){0,3}$")

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
        max_tokens=120 + 80 * len(targets),  # +generic field per item
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
        # #56: raw animal protein (not cured/dried/canned) never leaves
        # here undated or beyond the FDA raw-protein ceiling, whatever
        # the model said. Frozen is the one state that legitimately
        # clears the date.
        item_name = out[idx].name
        if (
            location != "freezer"
            and _RAW_PROTEIN.search(item_name)
            and not _CURED.search(item_name)
        ):
            if shelf is None:
                shelf = (
                    out[idx].shelf_days
                    if out[idx].shelf_days is not None
                    else _RAW_PROTEIN_MAX_DAYS
                )
            shelf = min(shelf, _RAW_PROTEIN_MAX_DAYS)
            location = "fridge"
        generic = answer.get("generic")
        match_name: str | None = None
        if isinstance(generic, str):
            cleaned = generic.strip().lower()
            if (
                len(cleaned) <= 40
                and _GENERIC_OK.match(cleaned)
                and cleaned != item_name.strip().lower()
            ):
                match_name = cleaned
        out[idx] = replace(
            out[idx],
            location=location,
            shelf_days=shelf,
            perishable=(shelf is not None and shelf <= _PERISHABLE_ASK_DAYS),
            recognized=True,
            match_name=match_name,
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
