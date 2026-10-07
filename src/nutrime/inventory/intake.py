"""Bulk pantry intake — paste a list, get a stocked inventory.

Direct user request (2026-10-06): "copy and paste in a full list comma or
space or other delineated and have the system automatically process the
input into a full inventory, intelligently storing the items where they
need to be" — plus perishability awareness: the system roughly identifies
what is perishable and asks how fresh it is, so use-it-up ranking
(``expiring_names``) has real dates to work with.

Deterministic and local — splitting, parsing, and classification are all
rule-based (the grocery parser handles quantity/unit/food extraction).
Two-step flow: :func:`preview` proposes items (location + perishability +
suggested shelf life); the UI lets the user adjust and answer freshness
for perishables; the commit endpoint stores what they confirmed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import date, timedelta

from nutrime.grocery.parse import parse_ingredient
from nutrime.inventory.store import Location

_QTY_PREFIX = r"\d+(?:\.\d+)?(?:\s*(?:lb|lbs|oz|g|kg|x))?\s+"

# -- classification lexicon ---------------------------------------------------
# keyword (matched against normalized food words/bigrams; longest match
# wins) → (default location, shelf-life days or None).
# shelf_days is the "fresh today" horizon used when the user doesn't give
# a date; None = shelf-stable, no freshness question asked.

_FRIDGE_SHORT = 4      # raw meat/fish, fresh herbs, berries
_FRIDGE_MEDIUM = 7     # milk, most vegetables, deli, leftovers
_FRIDGE_LONG = 21      # eggs, hard cheese, condiment-adjacent fresh
_COUNTER_FRUIT = 5

_LEXICON: dict[str, tuple[Location, int | None]] = {
    # -- raw proteins (fridge, short) --
    "chicken": (Location.FRIDGE, 2), "turkey": (Location.FRIDGE, 2),
    "beef": (Location.FRIDGE, 3), "steak": (Location.FRIDGE, 3),
    "pork": (Location.FRIDGE, 3), "lamb": (Location.FRIDGE, 3),
    "ground beef": (Location.FRIDGE, 2), "ground turkey": (Location.FRIDGE, 2),
    "sausage": (Location.FRIDGE, 5), "bacon": (Location.FRIDGE, 7),
    "fish": (Location.FRIDGE, 2), "salmon": (Location.FRIDGE, 2),
    "shrimp": (Location.FRIDGE, 2), "tuna steak": (Location.FRIDGE, 2),
    "crab": (Location.FRIDGE, 2), "tofu": (Location.FRIDGE, 7),
    "deli": (Location.FRIDGE, 5), "ham": (Location.FRIDGE, 5),
    # -- dairy + eggs --
    "milk": (Location.FRIDGE, _FRIDGE_MEDIUM), "cream": (Location.FRIDGE, _FRIDGE_MEDIUM),
    "half and half": (Location.FRIDGE, _FRIDGE_MEDIUM),
    "yogurt": (Location.FRIDGE, 14), "kefir": (Location.FRIDGE, 14),
    "butter": (Location.FRIDGE, 60), "cheese": (Location.FRIDGE, _FRIDGE_LONG),
    "cream cheese": (Location.FRIDGE, 14), "cottage cheese": (Location.FRIDGE, 7),
    "sour cream": (Location.FRIDGE, 14), "egg": (Location.FRIDGE, 28),
    # -- produce: fridge --
    "lettuce": (Location.FRIDGE, 5), "spinach": (Location.FRIDGE, 5),
    "kale": (Location.FRIDGE, 5), "arugula": (Location.FRIDGE, 4),
    "salad": (Location.FRIDGE, 4), "greens": (Location.FRIDGE, 5),
    "broccoli": (Location.FRIDGE, 7), "cauliflower": (Location.FRIDGE, 7),
    "carrot": (Location.FRIDGE, 21), "celery": (Location.FRIDGE, 14),
    "cucumber": (Location.FRIDGE, 7), "zucchini": (Location.FRIDGE, 5),
    "pepper": (Location.FRIDGE, 7), "bell pepper": (Location.FRIDGE, 7),
    "mushroom": (Location.FRIDGE, 5), "green bean": (Location.FRIDGE, 5),
    "asparagus": (Location.FRIDGE, 4), "cabbage": (Location.FRIDGE, 21),
    "brussels sprout": (Location.FRIDGE, 7), "leek": (Location.FRIDGE, 10),
    "scallion": (Location.FRIDGE, 7), "green onion": (Location.FRIDGE, 7),
    "herb": (Location.FRIDGE, 4), "cilantro": (Location.FRIDGE, 4),
    "parsley": (Location.FRIDGE, 5), "basil": (Location.COUNTERTOP, 4),
    "dill": (Location.FRIDGE, 4), "mint": (Location.FRIDGE, 5),
    "ginger": (Location.FRIDGE, 21),
    "berry": (Location.FRIDGE, 3), "strawberry": (Location.FRIDGE, 3),
    "blueberry": (Location.FRIDGE, 5), "raspberry": (Location.FRIDGE, 2),
    "grape": (Location.FRIDGE, 7), "cherry": (Location.FRIDGE, 4),
    # -- produce: countertop --
    "banana": (Location.COUNTERTOP, _COUNTER_FRUIT),
    "apple": (Location.COUNTERTOP, 14), "orange": (Location.COUNTERTOP, 10),
    "lemon": (Location.COUNTERTOP, 14), "lime": (Location.COUNTERTOP, 14),
    "avocado": (Location.COUNTERTOP, 3), "tomato": (Location.COUNTERTOP, 5),
    "peach": (Location.COUNTERTOP, 4), "pear": (Location.COUNTERTOP, 5),
    "mango": (Location.COUNTERTOP, 4), "melon": (Location.COUNTERTOP, 7),
    "pineapple": (Location.COUNTERTOP, 4), "plum": (Location.COUNTERTOP, 4),
    "kiwi": (Location.COUNTERTOP, 7),
    "onion": (Location.PANTRY, 30), "garlic": (Location.PANTRY, 60),
    "potato": (Location.PANTRY, 30), "sweet potato": (Location.PANTRY, 21),
    "shallot": (Location.PANTRY, 30), "winter squash": (Location.PANTRY, 30),
    "butternut squash": (Location.PANTRY, 30),
    # -- bakery --
    "bread": (Location.COUNTERTOP, 5), "bagel": (Location.COUNTERTOP, 5),
    "tortilla": (Location.FRIDGE, 14), "bun": (Location.COUNTERTOP, 5),
    "baguette": (Location.COUNTERTOP, 2), "pita": (Location.COUNTERTOP, 5),
    # -- leftovers / prepared --
    "leftover": (Location.FRIDGE, 3), "cooked": (Location.FRIDGE, 3),
    "soup": (Location.FRIDGE, 4), "hummus": (Location.FRIDGE, 7),
    "salsa": (Location.FRIDGE, 10), "pesto": (Location.FRIDGE, 7),
    # -- shelf-stable (no freshness question) --
    "rice": (Location.PANTRY, None), "pasta": (Location.PANTRY, None),
    "noodle": (Location.PANTRY, None), "flour": (Location.PANTRY, None),
    "sugar": (Location.PANTRY, None), "salt": (Location.PANTRY, None),
    "oil": (Location.PANTRY, None), "olive oil": (Location.PANTRY, None),
    "vinegar": (Location.PANTRY, None), "soy sauce": (Location.PANTRY, None),
    "bean": (Location.PANTRY, None), "lentil": (Location.PANTRY, None),
    "chickpea": (Location.PANTRY, None), "quinoa": (Location.PANTRY, None),
    "oat": (Location.PANTRY, None), "cereal": (Location.PANTRY, None),
    "cracker": (Location.PANTRY, None), "chip": (Location.PANTRY, None),
    "nut": (Location.PANTRY, None), "almond": (Location.PANTRY, None),
    "peanut": (Location.PANTRY, None), "walnut": (Location.PANTRY, None),
    "peanut butter": (Location.PANTRY, None), "jam": (Location.PANTRY, None),
    "honey": (Location.PANTRY, None), "maple syrup": (Location.PANTRY, None),
    "stock": (Location.PANTRY, None), "broth": (Location.PANTRY, None),
    "tomato paste": (Location.PANTRY, None), "coconut milk": (Location.PANTRY, None),
    "spice": (Location.PANTRY, None), "cumin": (Location.PANTRY, None),
    "paprika": (Location.PANTRY, None), "oregano": (Location.PANTRY, None),
    "cinnamon": (Location.PANTRY, None), "chocolate": (Location.PANTRY, None),
    "coffee": (Location.PANTRY, None), "tea": (Location.PANTRY, None),
    "raisin": (Location.PANTRY, None), "dried": (Location.PANTRY, None),
    "canned": (Location.PANTRY, None), "can": (Location.PANTRY, None),
    "jarred": (Location.PANTRY, None), "ketchup": (Location.PANTRY, None),
    "mustard": (Location.FRIDGE, None), "mayo": (Location.FRIDGE, 60),
    "mayonnaise": (Location.FRIDGE, 60), "hot sauce": (Location.PANTRY, None),
    "salad dressing": (Location.FRIDGE, 30),
}

# Modifiers that override the base keyword's location.
_FROZEN = re.compile(r"\bfrozen\b", re.I)
_CANNED = re.compile(r"\b(canned|tinned|jarred|can of|jar of|dried)\b", re.I)

# Preservation-state words that change how a food keeps. The grocery
# parser strips some of these as prep words ("cut melon" → "melon"), so
# preview() keeps the raw phrasing when one is present — the state IS
# the signal for the LLM tier (llm_classify.needs_llm).
STATE_WORDS = re.compile(
    r"\b(opened?|cut|sliced|halved|leftover|cooked|cured|smoked|fermented|"
    r"uht|shelf.?stable|unopened|ripe|overripe|thawed|defrosted|homemade|"
    r"fresh)\b",
    re.I,
)

_PERISHABLE_ASK_DAYS = 45  # shelf life at/below this → worth asking freshness


@dataclass(frozen=True)
class ProposedItem:
    """One parsed entry, ready for user review before committing."""

    name: str
    location: str
    quantity: float | None = None
    unit: str | None = None
    perishable: bool = False       # ask the freshness question
    shelf_days: int | None = None  # default horizon if they don't answer
    recognized: bool = True        # False → lexicon miss, defaults applied


def _normalize_words(name: str) -> list[str]:
    text = re.sub(r"[^\w\s]", " ", name.lower())
    words = text.split()
    # light singularization, matching normalize_food's conservatism
    out = []
    for w in words:
        if len(w) > 3 and w.endswith("ies"):
            out.append(w[:-3] + "y")
        elif len(w) > 3 and w.endswith("es") and not w.endswith("ss"):
            out.append(w[:-2] if w.endswith(("oes", "shes", "ches")) else w[:-1])
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            out.append(w[:-1])
        else:
            out.append(w)
    return out


def classify(name: str) -> tuple[Location, int | None, bool]:
    """(location, shelf_days, recognized) for one food name.

    Longest lexicon match wins (bigrams before single words) so
    "sweet potato" beats "potato" and "peanut butter" beats "peanut".
    Frozen/canned modifiers override location.
    """
    if _FROZEN.search(name):
        return Location.FREEZER, None, True
    if _CANNED.search(name):
        return Location.PANTRY, None, True
    words = _normalize_words(name)
    bigrams = [f"{a} {b}" for a, b in zip(words, words[1:])]
    for candidate in bigrams + words:
        hit = _LEXICON.get(candidate)
        if hit is not None:
            return hit[0], hit[1], True
    # Unknown food: pantry, no freshness question — the review step is
    # where the user corrects us, and pantry is the no-pressure default.
    return Location.PANTRY, None, False


_SPLIT_STRONG = re.compile(r"[\n;,\t]")
_LEADING_BULLET = re.compile(r"^[-•*·]+\s*")


def split_list(text: str) -> list[str]:
    """Split pasted text into item strings.

    Strong delimiters (newlines, commas, semicolons, tabs) win; leading
    bullets are stripped per line. A single run of space-separated words
    with no quantities falls back to greedy longest-match against the
    lexicon so "olive oil peanut butter rice" comes out as three items,
    not six words — but "2 lb ground beef" stays one item.
    """
    parts = [
        _LEADING_BULLET.sub("", p.strip())
        for p in _SPLIT_STRONG.split(text)
        if p and p.strip()
    ]
    parts = [p for p in parts if p]
    if len(parts) != 1:
        return parts
    words = parts[0].split()
    if len(words) <= 2 or any(ch.isdigit() for ch in parts[0]):
        return parts
    # Space-delimited fallback: greedy longest lexicon phrase, max 3 words.
    items: list[str] = []
    i = 0
    norm = _normalize_words(parts[0])
    while i < len(words):
        matched = 0
        for span in (3, 2):
            phrase = " ".join(norm[i:i + span])
            if i + span <= len(words) and phrase in _LEXICON:
                items.append(" ".join(words[i:i + span]))
                matched = span
                break
        if not matched:
            items.append(words[i])
            matched = 1
        i += matched
    return items


def preview(text: str) -> list[ProposedItem]:
    """Parse pasted text into proposed inventory items."""
    out: list[ProposedItem] = []
    seen: set[str] = set()
    for raw in split_list(text):
        for parsed in parse_ingredient(raw):
            if not parsed.food:
                continue
            # The parser strips prep words, which can erase preservation
            # state ("cut melon" → "melon"). State changes how a food
            # keeps, so when the raw line carried a state word that the
            # cleaned food lost, keep the raw phrasing as the name.
            if STATE_WORDS.search(raw) and not STATE_WORDS.search(parsed.food):
                raw_name = re.sub(r"\s+", " ", raw).strip(" -•*·\t")
                stripped = re.sub(
                    rf"^{_QTY_PREFIX}", "", raw_name
                ).strip() or raw_name
                parsed = replace(parsed, food=stripped)
            key = parsed.food.lower()
            if key in seen:
                continue
            seen.add(key)
            location, shelf_days, recognized = classify(parsed.food)
            out.append(
                ProposedItem(
                    name=parsed.food,
                    location=str(location),
                    quantity=parsed.quantity,
                    unit=parsed.unit or None,
                    perishable=(
                        shelf_days is not None
                        and shelf_days <= _PERISHABLE_ASK_DAYS
                    ),
                    shelf_days=shelf_days,
                    recognized=recognized,
                )
            )
    return out


def best_by_from_freshness(
    shelf_days: int | None, age_days: int | None, *, today: date | None = None
) -> str | None:
    """Turn the freshness answer into a best-by date.

    ``age_days`` is how long ago the item was bought/made (the UI's
    "fresh today / a few days / about a week" chips). None with a known
    shelf life assumes bought today; both None → no date (shelf-stable).

    The date may land in the past: an item already older than its shelf
    life is EXPIRED, and clamping it to today would present it as "use
    today" — which promoted week-old raw chicken into meal plans (#55).
    """
    if shelf_days is None:
        return None
    base = today or date.today()
    remaining = shelf_days - (age_days or 0)
    return (base + timedelta(days=remaining)).isoformat()
