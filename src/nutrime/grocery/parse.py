"""Ingredient-line parsing for grocery aggregation (6.1; rebuilt 2026-10-06).

Pattern per sweep #16 §1 (Mealie's brute parser, reimplemented from the
mechanism description in stdlib): one output shape behind a swappable
backend, dictionary-assisted tokenizing, parentheticals deferred, prep
words split from the food. A smarter (LLM) backend can slot in later
without touching callers — the aggregator only sees :class:`ParsedLine`.

Input is a Cooklang ``@name{qty%unit}`` line from the vault. The
structure is only a first guess — sources stuff quantities into names
("& 1/2 tbsp olive oil" with qty 2), units into quantities ("¼ teaspoon"),
foods into parentheses, and prep words around commas ("boneless, skinless
chicken breasts"). :func:`parse_ingredient` repairs those in stages:

1. structure — read name / qty / unit; braces inside names tolerated
2. quantity repair — "& 1/2" continuations, units hiding in the qty
   field, leading quantities in the name ("800g / 28oz tomatoes")
3. asides — balanced (nested) parentheticals and "Optional:" prefixes
   move to the note; an empty food falls back to the parenthetical
4. commas — leading descriptor-only segments rejoin the food
   ("boneless, skinless chicken"); the rest is the prep note
5. trailing phrases — "to taste", "for serving", "divided" → note
6. units at the head of the name ("can black beans", "pinch of salt")
7. alternatives — "X or Y" keeps X (sharing Y's head noun when X is only
   an adjective: "sea or kosher salt" → "sea salt"); "or Y" → note
8. compounds — unquantified "salt and pepper" → two lines
9. prep words — "finely chopped", "large", "softened" → note; identity
   words ("ground", "fresh", "unsalted", "crushed") stay in the food

The corpus-wide invariants in tests/test_grocery_corpus.py (no empty
foods, no digits, no descriptor-only foods across every recipe line) are
the regression gate for changes here.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from fractions import Fraction

from nutrime.grocery.units import find_unit

_FOOTNOTE = re.compile(r"\s*\*+\s*$")


@dataclass(frozen=True)
class ParsedLine:
    """One ingredient need, normalized for aggregation.

    ``quantity`` is None for unquantified lines ("salt to taste").
    ``unit`` is the canonical unit key ("" when unitless/count).
    ``food`` is the cleaned food name; ``note`` carries prep/asides.
    Per-field confidence in Mealie's shape (binary at this backend).
    """

    food: str
    quantity: float | None = None
    unit: str = ""
    note: str = ""
    confidence: float = 1.0


# -- vocabulary ---------------------------------------------------------------

# Preparation / size words: how to treat the food, not what to buy.
_PREP_WORDS = frozenset("""
    chopped diced minced sliced peeled halved quartered cubed julienned
    grated shredded beaten whisked softened melted sifted packed divided
    rinsed drained trimmed pitted seeded deseeded deveined cored stemmed
    torn cut crumbled mashed zested juiced toasted warmed chilled cooled
    large small medium jumbo extra-large heaping level scant generous
    optional thawed defrosted squeezed separated room temperature square
    strained sieved sized medium-sized bite-size bite-sized
""".split())
# Adverbs that only modify prep ("finely", "roughly"); "-ly" words that are
# foods or identity are excluded.
_NOT_ADVERBS = frozenset({"jelly", "belly", "chili", "lily", "curly", "family", "only"})
# Words that, alone, are never a food (a descriptor-only food is a bug).
_DESCRIPTORS = _PREP_WORDS | frozenset("""
    fresh freshly whole boneless skinless ripe raw cooked dried frozen canned
    ground extra virgin unsalted salted plain light dark low reduced fat free
    sodium organic cold warm hot boiling lean thick thin fine coarse
    a an the of and or to for with about plus more as needed taste
""".split())
# Adjectives that borrow the head noun of an alternative: "sea or kosher
# salt" → "sea salt"; "white or brown rice" → "white rice".
_SHARES_HEAD = frozenset("""
    sea kosher table coarse fine flaky white black brown red green yellow
    orange purple golden dark light whole low-fat nonfat skim reduced-fat
    regular dried fresh frozen canned smoked sweet hot mild sharp
""".split())
_TRAILING_NOTE = re.compile(
    r"\s*(?:,\s*)?\b("
    r"to taste|as needed|if needed|or as needed|for serving|for garnish(?:ing)?"
    r"|to serve|to garnish|for drizzling|for topping|for dusting|for frying"
    r"|for the [a-z ]+|plus (?:more|extra)\b.*|or more\b.*|divided|optional"
    r"|at room temperature|room temperature|about [\d/.\s]+[a-z]*"
    r")\s*$",
    re.I,
)
_PREFIX_NOTE = re.compile(r"^\s*([a-z][a-z ]{2,30}):\s+(?=\S)", re.I)
# Longest forms first so "1/2" is never read as "1" + "/2".
_QTY_TOKEN = r"(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?|[½¼¾⅓⅔⅛⅜⅝⅞])"
_LEADING_QTY = re.compile(
    rf"^\s*(?P<qty>{_QTY_TOKEN}(?:\s*[-–]\s*{_QTY_TOKEN})?)\s*-?\s*"
    rf"(?P<unit>[a-zA-Z.]+|\"|”|'')?(?=[\s,)/]|$)\s*"
)
_ALT_QTY = re.compile(rf"^\s*/\s*{_QTY_TOKEN}\s*-?\s*[a-zA-Z.]*\s*")
_QTY_RANGE = rf"{_QTY_TOKEN}(?:\s*[-–]\s*{_QTY_TOKEN})?"
_HEDGE = re.compile(
    r"^\s*(?:~|about|approx\.?|approximately|roughly|around|heaping|heaped|scant|"
    r"generous|level|additional|extra|up to|a good|x)\s*(?=[\d½¼¾])", re.I
)
_SIZE_PREFIX = re.compile(
    rf"^\s*{_QTY_TOKEN}\s*-?\s*(?:inch(?:es)?|in\.?|cm|mm|\"|''|”)"
    r"(?:[-\s]*(?:thick|long|wide|diameter|pieces?|cubes?|chunks?|square))*[\s,]+",
    re.I,
)
_CONTAINERS = frozenset({"can", "jar", "bag", "box", "bottle", "container", "carton", "pack", "envelope"})
_NON_INGREDIENT_PREFIXES = frozenset({"note", "notes", "tip", "tips", "optional notes"})
_SENTENCE_START = re.compile(
    r"^\s*\**\s*(?:this|these|you|i|i'm|if|we|it|it's|however|my|our|"
    r"make sure|depending|feel free|recipe makes)\b", re.I,
)
_LINK_MARKUP = re.compile(r"\[\s*([^|\]]+?)\s*\|\s*https?://[^\]]*\]")


def parse_quantity(raw: str) -> float | None:
    """"1 1/2" / "1.5" / "½" / "3-4" (take low end) → float."""
    text = raw.strip()
    if not text:
        return None
    # Unicode vulgar fractions → "n/d" via decomposition ("½" → "1/2";
    # 2044 is the fraction slash). All vulgar fractions are single-digit.
    out: list[str] = []
    for ch in text:
        decomp = unicodedata.decomposition(ch)
        if decomp.startswith("<fraction>"):
            digits = [chr(int(p, 16)) for p in decomp.split()[1:] if p != "2044"]
            if len(digits) == 2:
                out.append(f" {digits[0]}/{digits[1]}")
                continue
        out.append(ch)
    text = "".join(out).strip()
    # Range: take the low end ("3-4 cups" → 3)
    range_match = re.match(r"^(\d+(?:[./]\d+)?)\s*[-–]\s*\d", text)
    if range_match:
        text = range_match.group(1)
    total = 0.0
    found = False
    for token in text.split():
        try:
            if "/" in token:
                total += float(Fraction(token))
            else:
                total += float(token)
            found = True
        except (ValueError, ZeroDivisionError):
            break
    return total if found else None


# -- stages ---------------------------------------------------------------------


def _extract_parentheticals(text: str) -> tuple[str, list[str]]:
    """Remove balanced (nested) parenthetical groups; return (rest, groups).
    Stray unmatched parens are dropped."""
    out: list[str] = []
    groups: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in text:
        if ch == "(":
            if depth > 0:
                current.append(" ")
            depth += 1
        elif ch == ")":
            if depth == 0:
                continue  # stray close
            depth -= 1
            if depth == 0:
                group = re.sub(r"\s+", " ", "".join(current)).strip(" ,;")
                if group:
                    groups.append(group)
                current = []
                out.append(" ")
            else:
                current.append(" ")
        elif depth > 0:
            current.append(ch)
        else:
            out.append(ch)
    if depth > 0 and current:  # unclosed group
        group = re.sub(r"\s+", " ", "".join(current)).strip(" ,;")
        if group:
            groups.append(group)
    return re.sub(r"\s+", " ", "".join(out)).strip(), groups


def _is_descriptor(word: str) -> bool:
    w = word.lower().strip(".,;:-")
    if not w:
        return True
    if w in _DESCRIPTORS:
        return True
    return w.endswith("ly") and len(w) > 4 and w not in _NOT_ADVERBS


def _only_descriptors(text: str) -> bool:
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    return bool(words) and all(_is_descriptor(w) for w in words)


def _take_leading_quantity(text: str) -> tuple[float | None, str, str]:
    """("800g / 28oz crushed tomatoes") → (800, "g", "crushed tomatoes").
    A non-unit word after the number stays in the text."""
    m = _LEADING_QTY.match(text)
    if not m:
        return None, "", text
    qty = parse_quantity(m.group("qty"))
    unit_word = m.group("unit") or ""
    if unit_word in ('"', "”", "''"):
        unit_word = "inch"
    rest = text[m.end():]
    unit = find_unit(unit_word) if unit_word else None
    if unit_word and unit is None:
        # "2 large eggs": the word is part of the food, not a unit
        rest = text[m.end("qty"):].lstrip()
    rest = _ALT_QTY.sub("", rest)  # drop "/ 28oz" metric-imperial echoes
    return qty, unit or "", rest.strip()


def _strip_prep_words(text: str, notes: list[str]) -> str:
    """Move prep/size words (and "and" joining them) to the note, wherever
    they sit, as long as a real food word remains."""
    words = text.split()

    def is_prep(word: str) -> bool:
        bare = word.lower().strip(".,;:")
        return bare in _PREP_WORDS or (
            bare.endswith("ly") and len(bare) > 4 and bare not in _NOT_ADVERBS
        )

    flags = [is_prep(w) for w in words]
    for i, w in enumerate(words):  # connectors between/after prep words
        if w.lower() in ("and", "&", "then") and 0 < i and (
            flags[i - 1] or _is_descriptor(words[i - 1])
        ) and (i + 1 == len(words) or flags[i + 1]):
            flags[i] = True
    kept = [w for w, f in zip(words, flags) if not f]
    moved = [w.lower().strip(".,;:") for w, f in zip(words, flags) if f]
    while moved and moved[0] in ("and", "&", "then"):
        moved.pop(0)
    while kept and kept[0].lower() in ("and", "or", "&", "then", "of"):
        kept.pop(0)
    if moved and kept and not _only_descriptors(" ".join(kept)):
        notes.insert(0, " ".join(moved))
        return " ".join(kept)
    return text


def _clean_food(text: str) -> str:
    text = re.sub(r"^[\s&+\-–,;:/]+|[\s,;:/\-–]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_alternatives(text: str, notes: list[str]) -> str:
    """"X or Y" → X (+ "or Y" note); adjective-only X borrows Y's head."""
    m = re.search(r"\s+or\s+", text, re.I)
    if not m:
        return text
    left, right = text[: m.start()].strip(), text[m.end():].strip()
    if not right:
        return left
    _, _, right_wo_qty = _take_leading_quantity(right)
    right_words = right_wo_qty.split()
    left_words = left.split()
    if not left_words:
        notes.append(f"or {right}")
        return right_wo_qty
    if _only_descriptors(left):
        # "large or 2 small jalapeños" → jalapeños
        head = [w for w in right_words if not _is_descriptor(w)]
        notes.append(f"{left} or {right}")
        return " ".join(head) or right_wo_qty
    if (
        len(right_words) >= 2
        and left_words[-1].lower() in _SHARES_HEAD
        and len(left_words) <= 2
    ):
        # "fine sea or kosher salt" → "fine sea salt"
        notes.append(f"or {right}")
        return f"{left} {' '.join(right_words[1:])}"
    notes.append(f"or {right}")
    return left


# -- main entry -------------------------------------------------------------------


def parse_ingredient(name: str, qty: str = "", unit: str = "") -> list[ParsedLine]:
    """Clean one structured ingredient into one or more ParsedLines."""
    notes: list[str] = []
    # Invisible format characters (U+2063 etc.) and link markup from imports
    name = "".join(ch for ch in name if unicodedata.category(ch) != "Cf")
    name = _LINK_MARKUP.sub(lambda m: m.group(1), name)
    text = _FOOTNOTE.sub("", name.replace("{", " ").replace("}", " ").strip())
    qty = qty.strip()
    unit = unit.strip()

    # Stage 2a — unit hiding in the qty field ("¼ teaspoon", "2 cans")
    if qty and not unit:
        q_val, q_unit, q_rest = _take_leading_quantity(qty)
        if q_val is not None and q_unit:
            qty, unit = str(q_val), q_unit
            if q_rest:
                notes.append(q_rest)  # "30g roughly crumbled into pieces"
    quantity = parse_quantity(qty)
    # "cup/20g cocoa powder", "Tablespoon/15ml maple syrup" (qty in the field)
    unit_alt = re.match(rf"^\s*([a-zA-Z.]+)\s*/\s*{_QTY_TOKEN}\s*-?\s*[a-zA-Z.]*\s+", text)
    if unit_alt and find_unit(unit_alt.group(1)) and not unit:
        unit = unit_alt.group(1)
        text = text[unit_alt.end():]
    text = _HEDGE.sub("", text)

    # Stage 3a — parentheticals (done before quantity repair so
    # "(15 ml) champagne vinegar" exposes the food)
    text, groups = _extract_parentheticals(text)

    # Stage 2b — "& 1/2 tbsp olive oil" with qty 2 → 2.5 tbsp
    cont = re.match(rf"^\s*(?:&|and|\+)\s*({_QTY_TOKEN})\s*", text, re.I)
    if cont and quantity is not None:
        extra = parse_quantity(cont.group(1)) or 0.0
        quantity += extra
        text = text[cont.end():]
        lead_unit = re.match(r"([a-zA-Z.]+)\s+", text)
        if lead_unit and find_unit(lead_unit.group(1)) and not unit:
            unit = lead_unit.group(1)
            text = text[lead_unit.end():]
    # Range tails of the qty ("- 1/2 inch", "to 7 tomatoes", "- up to 1 Tbs") → note
    rng = re.match(rf"^\s*(?:[-–]\s*(?:up\s+to)?|to|up\s+to)\s*{_QTY_TOKEN}\s*", text, re.I)
    if rng and quantity is not None:
        notes.append(f"{qty} {text[: rng.end()].strip()}".strip())
        text = text[rng.end():]
    # "plus 2 Tbsp. olive oil" — an extra amount of the same food → note
    plus = re.match(rf"^\s*plus\s+{_QTY_TOKEN}\s*[a-zA-Z.]*\s+", text, re.I)
    if plus and quantity is not None:
        notes.append(text[: plus.end()].strip())
        text = text[plus.end():]
    text = _ALT_QTY.sub("", text)  # "/500g dried pappardelle"
    text = re.sub(r"^\s*each\s+of\s+", "", text, flags=re.I)

    # Package size in the name with a count in qty: "15oz can tomatoes" (qty 1)
    if quantity is not None:
        dup0 = re.match(rf"^\s*({_QTY_TOKEN})\s+(?=[a-zA-Z])", text)
        if dup0 and parse_quantity(dup0.group(1)) == quantity:
            text = text[dup0.end():]  # "2 sprays of oil spray" with qty 2
        s_qty, s_unit, s_rest = _take_leading_quantity(text)
        if s_qty is not None and s_unit and s_rest:
            size = f"{s_qty:g} {s_unit}"
            first, _, after = s_rest.partition(" ")
            container = find_unit(first)
            if container in _CONTAINERS and after.strip():
                if not unit:
                    unit = first
                text = after.strip()
            else:
                text = s_rest
            notes.append(f"{size} each")
        dup = re.match(rf"^\s*({_QTY_TOKEN})\s+(?=[a-zA-Z])", text)
        if dup and parse_quantity(dup.group(1)) == quantity:
            text = text[dup.end():]  # "2 sprays of oil spray" with qty 2
        size = _SIZE_PREFIX.match(text)
        if size:
            notes.append(size.group(0).strip(" ,"))
            text = text[size.end():]
        text = re.sub(r"^(?:us\s+)?fluid\s+ounces?\s+", "fl oz ", text, flags=re.I)
        if text.lower().startswith("fl oz ") and not unit:
            unit, text = "fl oz", text[6:]
        plus_more = re.match(rf"^\s*(?:\+|&|and)\s*{_QTY_TOKEN}\s*[a-zA-Z.]*\s+", text)
        if plus_more:
            notes.append(text[: plus_more.end()].strip())
            text = text[plus_more.end():]

    # Stage 2c — quantity written into the name ("800g / 28oz tomatoes")
    if quantity is None:
        l_qty, l_unit, l_rest = _take_leading_quantity(text)
        if l_qty is not None and l_rest:
            quantity, text = l_qty, l_rest
            if l_unit and not unit:
                unit = l_unit

    # Stage 3b — "Optional for serving: Ranch dressing"
    prefix = _PREFIX_NOTE.match(text)
    if prefix:
        if prefix.group(1).strip().lower() in _NON_INGREDIENT_PREFIXES:
            return [ParsedLine(food="", note=text, confidence=0.0)]
        notes.append(prefix.group(1).strip())
        text = text[prefix.end():]
        if quantity is None:  # "Optional: 1 tsp paprika"
            p_qty, p_unit, p_rest = _take_leading_quantity(_HEDGE.sub("", text))
            if p_qty is not None and p_rest:
                quantity, text = p_qty, p_rest
                if p_unit and not unit:
                    unit = p_unit
    # A sentence imported as an ingredient ("This recipe keeps…") is not one.
    if _SENTENCE_START.match(text):
        return [ParsedLine(food="", note=text.strip(), confidence=0.0)]
    text = re.sub(r"^\s*your\s+(?:favou?rite|preferred|choice of)\s+", "", text, flags=re.I)
    # "or more turmeric", "or so" — hedges, not alternatives
    text = re.sub(r"^\s*or\s+(?:more|so|less)\s+", "", text, flags=re.I)
    text = re.sub(r"\s+mixed with\b.*$", "", text, flags=re.I)
    # Hedges before an amount: "about 1/4 cup olive oil"
    text = re.sub(r"^\s*(?:about|approx\.?|approximately|roughly|around)\s+(?=[\d½¼¾])",
                  "", text, flags=re.I)
    # "or 2 Thai chilies" (qty 1): an alternative count → note
    alt = re.match(rf"^\s*or\s+{_QTY_TOKEN}\s+", text, re.I)
    if alt and quantity is not None:
        notes.append(text[: alt.end()].strip())
        text = text[alt.end():]
    # "8 count, refrigerated biscuits" → count is packaging
    cnt = re.match(rf"^\s*{_QTY_TOKEN}\s*count\b[,\s]*", text, re.I)
    if cnt:
        notes.append(text[: cnt.end()].strip(" ,"))
        text = text[cnt.end():]
    # Amount written after the food: "granulated sugar 25g", "water 5.3oz"
    tail = re.search(rf"\s+{_QTY_TOKEN}\s*(?:g|kg|ml|l|oz|lb|gr|gms?)\.?\s*$", text, re.I)
    if tail and tail.start() > 0:
        notes.append(text[tail.start():].strip())
        text = text[: tail.start()]
    # "thyme plus 3 tsp. fresh thyme leaves" → the extra amount is a note
    mid_plus = re.search(r"\s+plus\s+\S.*$", text, re.I)
    if mid_plus and mid_plus.start() > 0:
        notes.append(mid_plus.group(0).strip())
        text = text[: mid_plus.start()]
    # "for deglazing the pan", "for laminating onto the dough" → note
    use = re.search(r"\s+for\s+\w+ings?\b.*$", text, re.I)
    if use and use.start() > 0:
        notes.append(use.group(0).strip())
        text = text[: use.start()]
    # " - cooked per package instructions" tail → note
    dash = re.search(r"\s+[-–—]\s+", text)
    if dash:
        head_part, tail_part = text[: dash.start()], text[dash.end():].strip()
        head_words = [w for w in head_part.split() if not find_unit(w)]
        if head_words and not _only_descriptors(" ".join(head_words)):
            notes.append(tail_part)
            text = head_part
        else:
            # "gms – 5 oz. soft goat's cheese": the food is after the dash
            notes.append(head_part.strip())
            _, _, tail_rest = _take_leading_quantity(tail_part)
            text = tail_rest or tail_part
    choice = re.search(r"\s+of (?:your|choice)\b.*$", text, re.I)
    if choice:
        notes.append(choice.group(0).strip())
        text = text[: choice.start()]

    # Stage 6a — unit word at the head before comma handling
    # ("containers plain, non-fat Greek yogurt")
    if not unit:
        words = text.strip().split()
        lead_prep = []
        while len(words) > 2 and words[0].lower() in _PREP_WORDS and find_unit(words[1]) is None:
            break
        if len(words) > 2 and words[0].lower() in _PREP_WORDS and find_unit(words[1]):
            lead_prep.append(words.pop(0))  # "packed cup fresh mint"
        if len(words) > 1 and find_unit(words[0]):
            unit = words.pop(0)
            if lead_prep:
                notes.append(" ".join(lead_prep))
            text = " ".join(words)

    # Stage 4 — commas: descriptor-only heads rejoin the food
    segments = [s.strip() for s in text.split(",")]
    head = segments[0]
    i = 1
    while _only_descriptors(head) and i < len(segments) and segments[i]:
        head = f"{head} {segments[i]}"
        i += 1
    trailing = ", ".join(s for s in segments[i:] if s)
    if trailing:
        notes.append(trailing)
    text = head
    if len(text.split()) > 16:  # a paragraph, not an ingredient
        return [ParsedLine(food="", note=name.strip(), confidence=0.0)]

    # Stage 5 — trailing phrases
    while True:
        m = _TRAILING_NOTE.search(text)
        if not m or m.start() == 0:
            break
        notes.append(m.group(1).strip())
        text = text[: m.start()]

    # Stage 6 — unit at the head of the name ("can black beans", "a pinch of salt")
    text = re.sub(r"^(?:a|an)\s+", "", text.strip(), flags=re.I)
    unit_key = find_unit(unit) if unit else ""
    if unit and unit_key is None:
        notes.append(unit)  # unknown unit stays visible ("heaping scoop")
        unit_key = ""
    if not unit_key:
        first, _, rest = text.partition(" ")
        promoted = find_unit(first)
        if promoted and rest.strip() and promoted not in ("t", "c"):
            unit_key = promoted
            text = rest.strip()
            if quantity is None and promoted in ("pinch", "dash", "splash"):
                quantity = 1.0
    if text.lower().startswith("of "):
        text = text[3:]

    # Stage 3c — empty food: the food was inside the parentheses
    if not _clean_food(text) or _only_descriptors(text):
        for group in groups:
            g_qty, g_unit, g_rest = _take_leading_quantity(_HEDGE.sub("", group))
            candidate = g_rest.split(",")[0].strip()
            cw = candidate.split()
            while len(cw) > 1 and (find_unit(cw[0]) or cw[0].lower() in _PREP_WORDS):
                cw.pop(0)
            candidate = " ".join(cw)
            if candidate and not _only_descriptors(candidate):
                if g_qty is not None:
                    notes.append(f"{g_qty:g} {g_unit}".strip())
                text = f"{text} {candidate}".strip() if _clean_food(text) else candidate
                groups = [g for g in groups if g is not group]
                rest = g_rest.split(",", 1)[1].strip() if "," in g_rest else ""
                if rest:
                    notes.append(rest)
                break
    notes.extend(groups)

    text = re.sub(r"\s+and\s*/?\s*or\s+", " or ", text, flags=re.I)
    text = re.sub(r"^of\s+", "", text.strip(), flags=re.I)
    text = re.sub(r"^(\w+)\s+or\s+(?:two|three|so)\s+(?:of\s+)?", r"\1 ", text, flags=re.I)
    text = re.sub(r"^\s*or\s+(?:two|three|so)\s+(?:of\s+)?", "", text, flags=re.I)
    text = re.sub(r"^of\s+", "", text.strip(), flags=re.I)

    # Stage 8 — compounds before alternatives: "salt and pepper"
    foods = [text]
    quantities: list[float | None] = [quantity]
    each = any(n.strip().lower() == "each" for n in notes) or bool(
        re.match(r"^\s*each\b", name, re.I)
    )
    pair = re.match(rf"^(.+?)\s+(?:and|\+)\s+({_QTY_TOKEN})\s+(.+)$", text, re.I)
    if pair and quantity is not None and not _only_descriptors(pair.group(1)):
        # "large egg and 1 egg yolk" → egg ×qty, egg yolk ×1
        foods = [pair.group(1).strip(), pair.group(3).strip()]
        quantities = [quantity, parse_quantity(pair.group(2))]
    elif each and " and " in text.lower():
        a, _, b = re.split(r"\s+(and)\s+", text, maxsplit=1, flags=re.I)
        b_words = b.split()
        if len(a.split()) == 1 and len(b_words) >= 2:
            # "black and white sesame seeds" → shared head
            foods = [f"{a} {' '.join(b_words[1:])}", b]
        else:
            foods = [a, b]
        quantities = [quantity, quantity]
    loose_amount = quantity is None or unit_key in ("pinch", "dash", "splash") or bool(
        re.fullmatch(r"(?:\w+\s+)?salt\s+and\s+(?:\w+\s+)?pepper", text.strip(), re.I)
    )
    if (
        loose_amount and " and " in text.lower() and " or " not in text.lower()
        and not re.search(r"\b(?:of|from)\b", text, re.I)  # "zest and juice of 1 lime"
    ):
        parts = [p.strip() for p in re.split(r"\s+and\s+", text, flags=re.I)]
        if (
            len(parts) == 2
            and all(0 < len(p.split()) <= 4 for p in parts)
            and parts[0].lower() != parts[1].lower()     # "half and half"
            and not _only_descriptors(parts[0])          # "thick and chunky salsa"
            and not _only_descriptors(parts[1])          # "ginger peeled and grated"
        ):
            foods = parts
            quantities = [quantity, quantity]

    out: list[ParsedLine] = []
    for idx, food_text in enumerate(foods):
        line_notes = [n for n in notes if n.strip().lower() != "each"] if each else list(notes)
        # "zest and juice of 1 lime" → lime
        of_match = re.match(
            rf"^(.*?)\b(?:of|from)\s+(?:approximately\s+|about\s+|roughly\s+)?(?:{_QTY_RANGE})?\s*(.+)$",
            food_text, re.I,
        )
        if of_match:
            target = re.sub(r"^(?:a|an)\s+", "", of_match.group(2), flags=re.I)
            if _SIZE_PREFIX.match(target + " ") or re.match(r"^[\d½¼¾]", target):
                of_match = None  # "juice from a 2-inch piece" — not the food
        line_qty = quantities[idx] if idx < len(quantities) else quantity
        if of_match and _only_descriptors(of_match.group(1)) is False and re.search(
            r"\b(zest|juice|rind|peel|leaves|seeds)\b", of_match.group(1), re.I
        ):
            line_notes.insert(0, of_match.group(1).strip())
            n = re.search(_QTY_TOKEN, food_text[len(of_match.group(1)):of_match.start(2)])
            if line_qty is None and n:
                line_qty = parse_quantity(n.group(0))
            food_text = of_match.group(2)
            # "8 sprigs of fresh thyme" → thyme (count kept in the note)
            inner_unit, _, inner_rest = food_text.partition(" ")
            if find_unit(inner_unit) and inner_rest:
                line_notes.append(f"{n.group(0) if n else ''} {inner_unit}".strip())
                food_text = re.sub(r"^of\s+", "", inner_rest)
        food_text = _split_alternatives(food_text, line_notes)
        food_text = _strip_prep_words(food_text, line_notes)
        # "cooked pieces of chicken" → cooked chicken
        food_text = re.sub(r"\b(?:pieces?|chunks?|cubes?|strips?|bits?)\s+of\s+", "",
                           food_text, flags=re.I)
        # "4 garlic cloves" → garlic, counted in cloves
        line_unit = unit_key or ""
        tail_words = food_text.split()
        if not line_unit and len(tail_words) > 1:
            tail_unit = find_unit(tail_words[-1])
            if tail_unit in ("clove", "sprig", "stalk", "head", "bunch", "slice") and not (
                _only_descriptors(" ".join(tail_words[:-1]))  # "whole cloves" is a spice
            ):
                line_unit = tail_unit
                food_text = " ".join(tail_words[:-1])
        food = _clean_food(food_text)
        if re.fullmatch(r"[\d\s./-]*", food):
            food = ""
        note = "; ".join(n for n in (s.strip(" ,;") for s in line_notes) if n)
        out.append(ParsedLine(
            food=food,
            quantity=line_qty,
            unit=line_unit,
            note=note,
            confidence=1.0 if food else 0.0,
        ))
    return out


def refine(name: str, qty: str, unit: str) -> ParsedLine:
    """Single-line form of :func:`parse_ingredient` (first item)."""
    return parse_ingredient(name, qty, unit)[0]


_COOKLANG_LINE = re.compile(
    r"^@(?:(?P<braced>[^@{}]+)\{(?P<qty>[^%}]*)%?(?P<unit>[^}]*)\}|(?P<bare>\S+))$"
)
# Fallback for names that themselves contain braces: "@pasta ( {shown}){1%lb}"
_COOKLANG_LOOSE = re.compile(r"^@(?P<name>.+)\{(?P<qty>[^%{}]*)%?(?P<unit>[^{}]*)\}\s*$")


def parse_cooklang_lines(line: str) -> list[ParsedLine]:
    """All ingredient needs on one vault body line ([] if not an ingredient)."""
    stripped = line.strip()
    match = _COOKLANG_LINE.match(stripped)
    if match:
        if match.group("bare"):
            return parse_ingredient(match.group("bare"))
        return parse_ingredient(
            match.group("braced") or "",
            match.group("qty") or "",
            match.group("unit") or "",
        )
    loose = _COOKLANG_LOOSE.match(stripped)
    if loose:
        return parse_ingredient(loose.group("name"), loose.group("qty"), loose.group("unit"))
    return []


def parse_cooklang_line(line: str) -> ParsedLine | None:
    """First ingredient need on a vault body line; None when it isn't one."""
    lines = parse_cooklang_lines(line)
    return lines[0] if lines else None


def _singular(word: str) -> str:
    if len(word) <= 3 or word.endswith(("ss", "us", "is")):
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"           # berries → berry
    if word.endswith("oes"):
        return word[:-2]                 # tomatoes → tomato
    if word.endswith("ves") and word not in ("chives", "olives", "cloves"):
        return word[:-3] + "f"           # leaves → leaf, halves → half
    if word.endswith(("ches", "shes", "xes", "sses")):
        return word[:-2]                 # peaches → peach
    if word.endswith("s"):
        return word[:-1]
    return word


def normalize_food(food: str) -> str:
    """Aggregation key for a food name (sweep #16 normalize-once helper).

    Accent-strip → punctuation→space → lowercase → singularize last word.
    Deliberately conservative: "green onion" and "onion" stay distinct
    (merge-gate discipline — fuzzy merging of foods risks wrong lists).
    """
    text = unicodedata.normalize("NFKD", food).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s]", " ", text).lower()
    words = text.split()
    if words:
        words[-1] = _singular(words[-1])
    return " ".join(words)
