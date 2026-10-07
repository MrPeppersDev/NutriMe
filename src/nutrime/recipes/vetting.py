"""Corpus hygiene — title normalization + vetting pass (V0, 2026-10-04).

User direction: recipes must not "appear in the app weirdly named or
skewed somehow". Two mechanisms, both preservation-friendly:

1. **Title normalization** (`normalize_title`) — display-grade cleanup
   applied in place at vet time: entity decode, whitespace collapse,
   SHOUTING-CAPS → title case (with cooking-aware small words), trailing
   "Recipe"/"Recipe Card" noise stripped. The original title is kept in
   frontmatter as ``title_original`` the first time it changes (honesty +
   reversibility; preservation-layer discipline — never destroy source
   data).

2. **Vetting** (`vet_record`) — quality flags that QUARANTINE, never
   delete: segmentation artifacts (roman-numeral / sub-3-char titles),
   entries with no ingredients AND no usable instruction text (junk
   fragments — distinct from legitimate narrative historical recipes,
   which have prose bodies). Quarantined rows get
   ``vetting_status: 'quarantined'`` + a reason; search skips them by
   default; ``nutrime recipes vet --list-quarantined`` reviews them and
   the file stays in the vault untouched otherwise.

Anything not flagged gets ``vetting_status: 'vetted'`` so the pass is
idempotent and new ingests are distinguishable (absent field = never
vetted).

V2 (issue #31, 2026-10-06) adds content checks, stamped as
``vetting_version: 2`` (rows below 2 are re-examined on the next pass):

3. **Quality flags** (`quality_findings`) — ingredient plausibility,
   instruction completeness, serving/time sanity. Most are *flags*
   (``vetting_flags`` — kept searchable, shown for review); only clear
   junk quarantines (instructions that are just a pointer elsewhere,
   non-food ingredient lines).
4. **Allergen consistency** — re-runs detection over the ingredient list;
   anything detected but not declared is ADDED to
   ``top_allergens_present`` (the safe direction: filtering only gets
   stricter), with the pre-vet list kept as ``allergens_original``.
5. **Cross-source duplicates** (`find_duplicates`) — same normalized
   title + overlapping ingredients. The non-canonical copy gets
   ``vetting_status: 'duplicate'`` + ``duplicate_of``; search hides it
   like quarantine, the file stays. Canonical preference: the
   household's own saved pins, then richer records, then earliest.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from nutrime.recipes.store import RecipeRecord, RecipeVault

# 3 (2026-10-08): meal-category inference for untagged recipes (P2 #14).
VETTING_VERSION = 3
HIDDEN_STATUSES = frozenset({"quarantined", "duplicate"})

# Words kept lowercase when title-casing (unless first/last)
_SMALL_WORDS = frozenset(
    "a an and as at but by for from in of on or the to with".split()
)
# Tokens whose casing is idiomatic — restored after title-casing
_FORCED_CASE = {
    "bbq": "BBQ", "blt": "BLT", "kfc": "KFC", "usa": "USA", "uk": "UK",
    "a1": "A1", "ipa": "IPA", "pb&j": "PB&J", "mac": "Mac",
}
_ROMAN = re.compile(r"^[ivxlcdm]+\.?$", re.I)
_TRAILING_NOISE = re.compile(
    r"[\s\-–—|:]*\b(recipe( card)?|video( recipe)?)\s*$", re.I
)


def _smart_title_case(text: str) -> str:
    words = text.lower().split()
    out = []
    for i, word in enumerate(words):
        forced = _FORCED_CASE.get(word.strip("().,"))
        if forced:
            out.append(forced)
        elif 0 < i < len(words) - 1 and word in _SMALL_WORDS:
            out.append(word)
        else:
            # capitalize() lowercases the rest — fine post-lower(); keep
            # hyphenated parts each capped ("sesame-ginger" → "Sesame-Ginger")
            out.append("-".join(p.capitalize() for p in word.split("-")))
    return " ".join(out)


def normalize_title(title: str) -> str:
    """Display-grade cleanup; conservative — only fixes clear weirdness."""
    text = html.unescape(title)
    text = re.sub(r"\s+", " ", text).strip()
    text = _TRAILING_NOISE.sub("", text).strip()
    # SHOUTING CAPS (allow short acronym-ish titles through)
    letters = [c for c in text if c.isalpha()]
    if len(letters) > 6 and all(c.isupper() for c in letters):
        text = _smart_title_case(text)
    return text or title.strip()


@dataclass(frozen=True)
class VetVerdict:
    ok: bool
    reason: str = ""


def vet_record(record: RecipeRecord) -> VetVerdict:
    """Quarantine checks. Conservative on purpose: only clear junk fails.

    Narrative historical recipes (zero @-ingredients but a real prose
    body) pass — Forme of Cury's shape is legitimate per 4.3.
    """
    title = str(record.frontmatter.get("title", "")).strip()
    bare = title.strip(" .")
    if len(bare) < 3:
        return VetVerdict(False, f"title too short: {title!r}")
    if _ROMAN.match(bare):
        return VetVerdict(False, f"roman-numeral segmentation artifact: {title!r}")

    has_ingredients = any(
        line.strip().startswith("@") for line in record.body.splitlines()
    )
    # Prose length excluding Cooklang metadata/comment lines
    prose = " ".join(
        line.strip()
        for line in record.body.splitlines()
        if line.strip() and not line.strip().startswith((">>", "--", "@"))
    )
    if not has_ingredients and len(prose) < 80:
        return VetVerdict(
            False, "no ingredients and no usable instruction text"
        )
    return VetVerdict(True)


# -- V2: content checks ----------------------------------------------------------

@dataclass(frozen=True)
class Finding:
    code: str
    severity: str  # "flag" (kept, shown for review) | "quarantine"
    detail: str = ""


_STEP_HEADER = "-- Instructions"
_POINTER_ONLY = re.compile(
    r"\b(see|watch|check\s+out)\s+(the\s+)?(video|link|website|blog|post|"
    r"full\s+recipe|original\s+recipe|recipe\s+card)\b"
    r"|\bclick\s+(here|the\s+link)\b|\blink\s+in\s+(bio|description)\b"
    r"|\b(continue|keep)\s+reading\b|\bfull\s+(recipe|instructions)\s+"
    r"(at|on|here)\b",
    re.I,
)
_NON_FOOD_INGREDIENT = re.compile(
    r"\badvertisement\b|\bsubscribe\b|\bclick\b|\bprint\s+recipe\b|"
    r"\bjump\s+to\b|\bpin\s+it\b|\bnewsletter\b",
    re.I,
)
# A real ingredient that carries a link ("[granola | https://…]") — the food
# is fine; the markup is worth a review flag, not a quarantine.
_LINKED_INGREDIENT = re.compile(r"https?://|www\.", re.I)
_ROUNDUP_TITLE = re.compile(
    r"^\s*\d{1,3}\s+.*\b(recipes|ideas|ways|snacks|cocktails|dinners|meals)\b",
    re.I,
)
_NUMBER = re.compile(r"(\d+(?:\.\d+)?)")
# Units where a quantity over the limit means a parse error, not a big batch.
_UNIT_LIMITS = {
    "tsp": 30, "teaspoon": 30, "teaspoons": 30,
    "tbsp": 30, "tablespoon": 30, "tablespoons": 30,
    "cup": 40, "cups": 40,
}
_INGREDIENT_QTY = re.compile(r"@[^{]*\{(?P<qty>[^}%]*)%?(?P<unit>[^}]*)\}")


def _sections(body: str) -> tuple[list[str], list[str]]:
    """(ingredient lines, instruction lines) from a canonical Cooklang body."""
    ingredients: list[str] = []
    steps: list[str] = []
    in_steps = False
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith(">>"):
            continue
        if line.startswith("--"):
            in_steps = line.lower().startswith(_STEP_HEADER.lower())
            continue
        if line.startswith("@"):
            ingredients.append(line)
        elif in_steps:
            steps.append(line)
    return ingredients, steps


def quality_findings(record: RecipeRecord) -> list[Finding]:
    """V2 content checks. Conservative: a flag is a note for review; only
    unambiguous junk quarantines."""
    fm = record.frontmatter
    ingredients, steps = _sections(record.body)
    out: list[Finding] = []

    # -- ingredient plausibility
    junk = [i for i in ingredients if _NON_FOOD_INGREDIENT.search(i)]
    if junk:
        out.append(Finding(
            "non_food_ingredient", "quarantine",
            f"{len(junk)} ingredient line(s) look like page chrome: {junk[0][:60]!r}",
        ))
    linked = [
        i for i in ingredients
        if _LINKED_INGREDIENT.search(i) and not _NON_FOOD_INGREDIENT.search(i)
    ]
    if linked:
        out.append(Finding(
            "ingredient_has_link", "flag", linked[0][:60]
        ))
    # Repeated names are NOT flagged: multi-component recipes legitimately
    # list salt/butter/water once per component (calibrated on the corpus).
    if len(ingredients) > 40:
        out.append(Finding(
            "too_many_ingredients", "flag", f"{len(ingredients)} ingredient lines"
        ))
    for line in ingredients:
        m = _INGREDIENT_QTY.search(line)
        if not m:
            continue
        unit = m.group("unit").strip().lower()
        num = _NUMBER.search(m.group("qty"))
        limit = _UNIT_LIMITS.get(unit)
        if limit and num and float(num.group(1)) > limit:
            out.append(Finding(
                "implausible_quantity", "flag", line[:80]
            ))
            break

    # -- instruction completeness
    step_text = " ".join(steps)
    if ingredients and not steps:
        if _ROUNDUP_TITLE.search(str(fm.get("title", ""))):
            out.append(Finding(
                "roundup_page", "quarantine",
                "a list-of-recipes page, not a recipe",
            ))
        else:
            out.append(Finding(
                "no_instructions", "flag", "ingredients but no method"
            ))
    elif steps and len(step_text) < 40:
        out.append(Finding(
            "thin_instructions", "flag", f"method is {len(step_text)} characters"
        ))
    if steps and _POINTER_ONLY.search(step_text) and len(step_text) < 200:
        out.append(Finding(
            "instructions_elsewhere", "quarantine",
            "the method only points to another page or video",
        ))

    # -- serving / time sanity
    yields = fm.get("yields") or {}
    count = yields.get("count") if isinstance(yields, dict) else None
    if isinstance(count, (int, float)) and not 1 <= count <= 60:
        out.append(Finding("implausible_yield", "flag", f"yields {count}"))
    for key in ("estimated_total_time_min", "estimated_active_time_min"):
        value = fm.get(key)
        if isinstance(value, (int, float)) and not 1 <= value <= 4320:
            out.append(Finding("implausible_time", "flag", f"{key} = {value}"))
    active = fm.get("estimated_active_time_min")
    total = fm.get("estimated_total_time_min")
    if (
        isinstance(active, (int, float))
        and isinstance(total, (int, float))
        and active > total
    ):
        out.append(Finding(
            "active_exceeds_total", "flag", f"active {active} > total {total}"
        ))
    return out


def reconcile_allergens(record: RecipeRecord) -> list[str] | None:
    """Detected-but-undeclared allergens, or None when consistent."""
    from nutrime.recipes.allergens import detect_allergens
    from nutrime.recipes.search import ingredient_names

    declared = set(record.frontmatter.get("top_allergens_present") or [])
    detected = set(detect_allergens(list(ingredient_names(record.body))))
    missing = sorted(detected - declared)
    return missing or None


# -- V3: meal-category inference (audit P2 #14) --------------------------------
# 782 recipes carried meal_categories: [] — and the dinner slot is defined
# by EXCLUSION (anything not tagged dessert/side/breakfast/... is a
# candidate main), so an untagged dessert lands in dinner pools. This
# infers the slot-relevant categories from the title, conservatively:
# only patterns that are unambiguous get a tag; anything else stays
# untagged and keeps its main-course-by-exclusion default. Title-only on
# purpose — ingredient lists share too much across courses (a cake and a
# quiche both have eggs/flour/butter).

_CATEGORY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("dessert", re.compile(
        r"\b(desserts?|cakes?|cupcakes?|cookies?|brownies?|blondies?|fudge|"
        r"cobblers?|crumbles?|crisps?|pudding|custard|flan|sorbet|gelato|"
        r"ice cream|cheesecake|tiramisu|baklava|macaroons?|meringues?|"
        r"truffles?|parfaits?|shortcake|gingerbread|biscotti|"
        r"caramel sauce|muffins?|doughnuts?|donuts?|ambrosia|rice krispie)\b"
        # Pie/tart default to dessert UNLESS a savory marker precedes
        # ("chicken pot pie", "shepherd's pie", "fish pie" stay mains).
        r"|(?<!pot )(?<!shepherd's )(?<!shepherds )(?<!cottage )(?<!tamale )"
        r"(?<!fish )(?<!meat )(?<!pizza )\b(pies?|tarts?)\b", re.I)),
    ("breakfast", re.compile(
        r"\b(pancakes?|waffles?|oatmeal|porridge|granola|muesli|"
        r"french toast|breakfast|omelett?es?|scrambled eggs?|"
        r"overnight oats?)\b", re.I)),
    ("drinks", re.compile(
        r"\b(smoothies?|lassi|milkshakes?|shakes?|punch|lemonade|"
        r"coolers?|spritzers?|hot (?:chocolate|cocoa)|iced tea|"
        r"aguas? frescas?|horchata|cider)\b", re.I)),
    ("side", re.compile(
        r"\b(coleslaw|slaw|dressings?|vinaigrettes?|salsas?|dips?|"
        r"spreads?|relish|chutney|pickles?|pickled|croutons?|"
        r"side(?:\s+dish)?)\b", re.I)),
    ("snack", re.compile(
        r"\b(snacks?|trail mix|energy (?:balls?|bites?)|popcorn|"
        r"roasted chickpeas?)\b", re.I)),
    # Informational tags — no slot effect, but searchable.
    ("soup", re.compile(r"\b(soups?|chowders?|bisques?|gazpacho)\b", re.I)),
    ("salad", re.compile(r"\bsalads?\b", re.I)),
)


def infer_meal_categories(record: RecipeRecord) -> list[str]:
    """Conservative title-based category inference for untagged recipes.

    Returns [] when nothing matches — the recipe keeps its implicit
    main-course-by-exclusion status, which is the right default for the
    ambiguous middle.
    """
    title = str(record.frontmatter.get("title", ""))
    out = [cat for cat, pattern in _CATEGORY_PATTERNS if pattern.search(title)]
    # A "salad dressing" is a side, not a salad; a "soup mix" title with
    # "dip" stays a side. Dessert wins over everything (apple pie salad
    # is unlikely; fruit-salad desserts tagging both is harmless).
    if "side" in out and "salad" in out:
        out.remove("salad")
    return out


# -- V2: duplicates ------------------------------------------------------------------

_TITLE_FILLER = frozenset(
    "the a an best easy easiest simple quick homemade perfect classic my our "
    "recipe healthy ultimate".split()
)
# Lower rank wins canonical: the household's own saves first, then curated
# public-health sources, then the general API.
_SOURCE_RANK = {"pins": 0, "nhlbi": 1, "myplate": 2, "themealdb": 3}


def duplicate_key(title: str) -> str:
    words = re.sub(r"[^a-z0-9 ]", " ", html.unescape(title).lower()).split()
    return " ".join(w for w in words if w not in _TITLE_FILLER)


def _ingredient_set(record: RecipeRecord) -> frozenset[str]:
    from nutrime.recipes.search import ingredient_names

    out = set()
    for name in ingredient_names(record.body):
        words = re.sub(r"[^a-z ]", " ", name.lower()).split()
        if words:
            out.add(words[-1].rstrip("s"))  # head noun, crude singular
    return frozenset(out)


def find_duplicates(
    records: list[RecipeRecord], *, min_overlap: float = 0.6
) -> dict[str, str]:
    """duplicate recipe_id → canonical recipe_id.

    Candidates share a normalized title; they are duplicates when their
    ingredient head-noun sets overlap (Jaccard) at least ``min_overlap``.
    Records already hidden for other reasons never take part.
    """
    from nutrime.recipes.search import source_collection

    groups: dict[str, list[RecipeRecord]] = {}
    for r in records:
        if r.frontmatter.get("vetting_status") == "quarantined":
            continue
        key = duplicate_key(str(r.frontmatter.get("title", "")))
        if key:
            groups.setdefault(key, []).append(r)

    def rank(r: RecipeRecord) -> tuple:
        ingredients, steps = _sections(r.body)
        return (
            _SOURCE_RANK.get(source_collection(r.frontmatter), 9),
            -(len(ingredients) + len(steps)),
            str((r.frontmatter.get("attribution") or {}).get("ingested_at", "")),
            r.recipe_id,
        )

    result: dict[str, str] = {}
    for group in groups.values():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=rank)
        sets = {r.recipe_id: _ingredient_set(r) for r in ordered}
        canon: list[RecipeRecord] = []
        for r in ordered:
            mine = sets[r.recipe_id]
            match = None
            for c in canon:
                theirs = sets[c.recipe_id]
                union = mine | theirs
                if union and len(mine & theirs) / len(union) >= min_overlap:
                    match = c
                    break
            if match is None:
                canon.append(r)
            else:
                result[r.recipe_id] = match.recipe_id
    return result


@dataclass(frozen=True)
class VetOutcome:
    examined: int
    titles_normalized: int
    quarantined: int
    already_vetted: int
    flagged: int = 0
    duplicates: int = 0
    allergens_added: int = 0
    categorized: int = 0


def vet_vault(vault: RecipeVault, *, revet: bool = False) -> VetOutcome:
    """One pass over the vault: normalize titles, run V0 + V2 checks,
    reconcile allergens, mark cross-source duplicates.

    Idempotent: rows already stamped at the current ``VETTING_VERSION``
    are skipped unless ``revet``. Duplicate detection always considers
    the whole vault, so a new ingest can be matched against old rows.
    """
    examined = normalized = quarantined = skipped = 0
    flagged = duplicates = allergens_added = categorized = 0

    records = list(vault.iter_recipes())
    staged: dict[str, dict] = {}
    for record in records:
        examined += 1
        fm = dict(record.frontmatter)
        current = (
            fm.get("vetting_status") in ("vetted", "quarantined", "duplicate")
            and int(fm.get("vetting_version") or 1) >= VETTING_VERSION
        )
        if current and not revet:
            skipped += 1
            continue
        # A row the de-scope pass quarantined by hand (historical corpus)
        # keeps its reason; V2 never un-quarantines it.
        manual_quarantine = (
            fm.get("vetting_status") == "quarantined"
            and "de-scope" in str(fm.get("vetting_reason") or "")
        )

        title = str(fm.get("title", ""))
        cleaned = normalize_title(title)
        if cleaned != title:
            if "title_original" not in fm:
                fm["title_original"] = title
            fm["title"] = cleaned
            normalized += 1

        candidate = RecipeRecord(
            recipe_id=record.recipe_id, frontmatter=fm, body=record.body,
            path=record.path,
        )
        missing = reconcile_allergens(candidate)
        if missing:
            if "allergens_original" not in fm:
                fm["allergens_original"] = list(
                    fm.get("top_allergens_present") or []
                )
            fm["top_allergens_present"] = sorted(
                set(fm.get("top_allergens_present") or []) | set(missing)
            )
            allergens_added += 1

        # V3 (P2 #14): untagged recipes get conservative title-inferred
        # categories so a dessert can't land in a dinner pool via the
        # main-course-by-exclusion default. Only ever fills EMPTY lists —
        # source-provided tags are never touched.
        if not fm.get("meal_categories"):
            inferred = infer_meal_categories(candidate)
            if inferred:
                fm["meal_categories"] = inferred
                fm["meal_categories_inferred"] = True
                categorized += 1

        verdict = vet_record(candidate)
        findings = quality_findings(candidate)
        flags = [f.code for f in findings if f.severity == "flag"]
        blocking = [f for f in findings if f.severity == "quarantine"]
        fm.pop("duplicate_of", None)
        if manual_quarantine:
            pass
        elif not verdict.ok:
            fm["vetting_status"] = "quarantined"
            fm["vetting_reason"] = verdict.reason
        elif blocking:
            fm["vetting_status"] = "quarantined"
            fm["vetting_reason"] = f"{blocking[0].code}: {blocking[0].detail}"
        else:
            fm["vetting_status"] = "vetted"
            fm.pop("vetting_reason", None)
        if flags:
            fm["vetting_flags"] = flags
            flagged += 1
        else:
            fm.pop("vetting_flags", None)
        fm["vetting_version"] = VETTING_VERSION
        staged[record.recipe_id] = fm

    # Duplicates across the whole vault (staged state wins over disk).
    view = [
        RecipeRecord(
            recipe_id=r.recipe_id,
            frontmatter=staged.get(r.recipe_id, r.frontmatter),
            body=r.body, path=r.path,
        )
        for r in records
    ]
    dupes = find_duplicates(view)
    for r in view:
        fm = r.frontmatter
        if r.recipe_id in dupes:
            if fm.get("vetting_status") != "duplicate" or fm.get(
                "duplicate_of"
            ) != dupes[r.recipe_id]:
                fm = dict(fm)
                fm["vetting_status"] = "duplicate"
                fm["duplicate_of"] = dupes[r.recipe_id]
                fm["vetting_version"] = VETTING_VERSION
                staged[r.recipe_id] = fm
            duplicates += 1
        elif fm.get("vetting_status") == "duplicate":
            # Its canonical twin changed or left: back to vetted.
            fm = dict(fm)
            fm["vetting_status"] = "vetted"
            fm.pop("duplicate_of", None)
            staged[r.recipe_id] = fm

    by_id = {r.recipe_id: r for r in records}
    for recipe_id, fm in staged.items():
        if fm.get("vetting_status") == "quarantined":
            quarantined += 1
        vault.write(recipe_id, fm, by_id[recipe_id].body)
    return VetOutcome(
        examined=examined,
        titles_normalized=normalized,
        quarantined=quarantined,
        already_vetted=skipped,
        flagged=flagged,
        duplicates=duplicates,
        allergens_added=allergens_added,
        categorized=categorized,
    )
