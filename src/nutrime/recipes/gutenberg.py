"""Project Gutenberg Bookshelf 419 (Cookery) text-ingest adapter.

Sub-commit 4.3 per the step 4 entry decision: PD historical anchor from
four cookbooks — Beeton's Book of Household Management (1861, #10136),
Farmer's Boston Cooking-School Cook Book (1918, #65061), The Forme of
Cury (~1390, #8102), The Golden Age Cook Book (1898, #26209). Text is
public domain; the "Project Gutenberg" trademark is restricted for
commercial use, so PG boilerplate is stripped on ingest per the entry
decision. gutenberg.org robots.txt (checked 2026-07-15) disallows only
``/ebooks/search`` — direct file fetches are permitted; one paced fetch
per book.

The novel work versus 4.1/4.2 is **segmentation**: carving recipe units
out of book-length plain text. Each book gets a profile with its own
anchor heuristic (verified against the live texts 2026-07-15):

- **Beeton** — ``NNN. INGREDIENTS.--`` numbered paragraphs with a CAPS
  title line above; ``_Mode_.--`` narrative; ``_Time_`` / ``_Sufficient_``
  fields feed estimated time + yields.
- **Farmer** — centered mixed-case title, centered indented ingredient
  lines, flush-left instruction paragraphs.
- **Forme of Cury** — roman-numeral title lines, narrative Middle-English
  body; editorial ``[n]`` footnote markers stripped.
- **Golden Age** — ALL-CAPS short title ending with a period, narrative
  body with spelled-out quantities.

Narrative-only books (Forme of Cury, Golden Age) yield no structured
ingredient list; allergen detection then runs over title + body text —
over-flagging is the safe direction per Rule 1 clinical gating.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

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
    now_iso,
    parse_duration_minutes,
)

SOURCE_NAME = "Project Gutenberg Bookshelf 419 (Cookery)"
SOURCE_LICENSE = (
    "Public domain (text); 'Project Gutenberg' trademark restricted for"
    " commercial use — PG boilerplate stripped on ingest"
)
INGESTION_METHOD = "gutenberg_text_v1"

_MIN_BODY_CHARS = 40
_MAX_TITLE_CHARS = 60

_NON_RECIPE_HEADINGS = frozenset({
    "preface", "contents", "table of contents", "index", "introduction",
    "illustrations", "dedication", "appendix", "glossary", "bibliography",
    "footnotes", "transcriber's note", "facing page", "errata",
})


def strip_pg_boilerplate(text: str) -> str:
    """Return only the content between the ``*** START/END ...`` markers."""
    start = re.search(r"\*\*\* START OF [^\n]*\*\*\*", text)
    end = re.search(r"\*\*\* END OF [^\n]*\*\*\*", text)
    lo = start.end() if start else 0
    hi = end.start() if end else len(text)
    return text[lo:hi]


@dataclass(frozen=True)
class RawRecipe:
    """One segmented recipe before conversion."""

    upstream_id: str
    title: str
    ingredient_lines: tuple[str, ...]
    steps: tuple[str, ...]
    total_time_min: int | None = None
    yields_count: int | None = None


@dataclass(frozen=True)
class BookProfile:
    key: str
    ebook_id: int
    book_title: str
    author: str
    published: str
    segment: Callable[[str], list["RawRecipe"]] = field(repr=False)

    @property
    def text_url(self) -> str:
        return (
            f"https://www.gutenberg.org/cache/epub/{self.ebook_id}"
            f"/pg{self.ebook_id}.txt"
        )

    @property
    def book_url(self) -> str:
        return f"https://www.gutenberg.org/ebooks/{self.ebook_id}"


# -- shared segmentation helpers --------------------------------------------


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60] or "untitled"


def _dedupe_slug(slug: str, used: set[str]) -> str:
    candidate = slug
    n = 2
    while candidate in used:
        candidate = f"{slug}-{n}"
        n += 1
    used.add(candidate)
    return candidate


def _paragraphs(lines: list[str]) -> list[str]:
    out: list[str] = []
    buf: list[str] = []
    for line in lines:
        if line.strip():
            buf.append(line.strip())
        elif buf:
            out.append(" ".join(buf))
            buf = []
    if buf:
        out.append(" ".join(buf))
    return out


def _split_narrative_measures(text: str) -> list[str]:
    """Split a Beeton-style ingredient narrative on , and ; (paren-aware)."""
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char in ",;" and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(char)
    parts.append("".join(buf).strip())
    return [p for p in parts if p]


# -- per-book segmenters -----------------------------------------------------


_BEETON_ANCHOR = re.compile(r"^(\d+)\. INGREDIENTS\.--(.*)$")
# Field separators vary in the source: "_Mode_.--", "_Average cost_,",
# "_Sufficient_ for 8 persons" — punctuation after the marker is optional.
_BEETON_FIELD = re.compile(
    r"_(Mode|Time|Average cost|Sufficient|Seasonable|Note)_[.,]?-{0,2}\s*"
)


def _cut_at(lines: list[str], marker: str) -> list[str]:
    """Truncate at the first line equal to ``marker`` (back-matter cutoff)."""
    for i, line in enumerate(lines):
        if line.strip() == marker:
            return lines[:i]
    return lines


def _segment_beeton(text: str) -> list[RawRecipe]:
    # Household Management's food recipes end where the domestic-service /
    # medical / legal chapters begin — furniture gloss is not dinner.
    lines = _cut_at(text.splitlines(), "DOMESTIC SERVANTS.")
    recipes: list[RawRecipe] = []
    used: set[str] = set()
    anchors = [
        (i, m) for i, line in enumerate(lines)
        if (m := _BEETON_ANCHOR.match(line))
    ]
    for pos, (i, match) in enumerate(anchors):
        number = match.group(1)
        # Title: nearest preceding non-empty line
        title = ""
        for j in range(i - 1, max(0, i - 6), -1):
            if lines[j].strip():
                title = lines[j].strip().rstrip(".").title()
                break
        end = anchors[pos + 1][0] if pos + 1 < len(anchors) else len(lines)
        block = "\n".join([match.group(2)] + lines[i + 1 : end])

        segments = _BEETON_FIELD.split(block)
        # segments: [ingredients_text, field1, body1, field2, body2, ...]
        ingredients_text = (
            segments[0].replace("\n", " ").strip().rstrip(".")
        )
        fields = {
            segments[k]: segments[k + 1].strip()
            for k in range(1, len(segments) - 1, 2)
        }
        mode = fields.get("Mode", "")
        steps = tuple(_paragraphs(mode.splitlines())) if mode else ()

        total_min = None
        if "Time" in fields:
            total_min = parse_duration_minutes(fields["Time"].split(".")[0])
        yields_count = None
        sufficient = fields.get("Sufficient", "")
        ymatch = re.search(r"for (\d+)", sufficient)
        if ymatch:
            yields_count = int(ymatch.group(1))

        if not title or len(title) > _MAX_TITLE_CHARS:
            continue
        recipes.append(
            RawRecipe(
                # The 1861 text reuses a paragraph number at least once
                # (e.g. #1536), so ids run through collision-suffixing.
                upstream_id=_dedupe_slug(
                    f"pg10136-p{int(number):04d}", used
                ),
                title=title,
                ingredient_lines=tuple(
                    _split_narrative_measures(ingredients_text)
                ),
                steps=steps,
                total_time_min=total_min,
                yields_count=yields_count,
            )
        )
    return recipes


_CENTERED = re.compile(r"^\s{8,}(\S.*\S|\S)\s*$")
_QTYISH = re.compile(r"^(\d|[¼½¾⅓⅔⅛]|Few|Speck)")


def _segment_farmer(text: str) -> list[RawRecipe]:
    # The 1918 edition closes with an index + advertisement pages.
    lines = _cut_at(text.splitlines(), "INDEX")
    recipes: list[RawRecipe] = []
    used: set[str] = set()
    i = 0
    while i < len(lines):
        m = _CENTERED.match(lines[i])
        candidate = m.group(1).strip() if m else ""
        is_title = (
            bool(candidate)
            and len(candidate) <= _MAX_TITLE_CHARS
            and any(c.islower() for c in candidate)
            and not _QTYISH.match(candidate)
            and not candidate.startswith(("[", "Page "))
            and "_" not in candidate
            and "=" not in candidate
            and candidate.strip(".").lower() not in _NON_RECIPE_HEADINGS
        )
        if not is_title:
            i += 1
            continue
        title = candidate
        j = i + 1
        ingredient_lines: list[str] = []
        body: list[str] = []
        while j < len(lines):
            nxt = _CENTERED.match(lines[j])
            if nxt:
                inner = nxt.group(1).strip()
                if _QTYISH.match(inner):
                    ingredient_lines.append(inner)
                    j += 1
                    continue
                if any(c.islower() for c in inner) and body:
                    break  # next recipe title
                j += 1
                continue
            if lines[j].strip() and not lines[j].startswith(" "):
                body.append(lines[j])
            elif not lines[j].strip():
                body.append("")
            j += 1
            # Stop scanning a runaway block
            if j - i > 400:
                break
        steps = tuple(
            p for p in _paragraphs(body) if not p.startswith("[Illustration")
        )
        if ingredient_lines and sum(len(s) for s in steps) >= _MIN_BODY_CHARS:
            recipes.append(
                RawRecipe(
                    upstream_id=(
                        f"pg65061-{_dedupe_slug(_slugify(title), used)}"
                    ),
                    title=title,
                    ingredient_lines=tuple(ingredient_lines),
                    steps=steps,
                )
            )
        i = j
    return recipes


_CURY_LEADING = re.compile(r"^([IVXLC]+)\. (.+?)\.?\s*$")
# Main-roll format: title first, numeral last — medieval score notation
# appears as dotted numeral clusters ("XX.IX. XIII."), kept as opaque ids.
_CURY_TRAILING = re.compile(
    r"^([A-Z][^a-z]*?)\.\s*([IVXLC]+(?:\.\s*[IVXLC]+)*)\.\s*$"
)
_FOOTNOTE_MARK = re.compile(r"\s*\[\d+\]")


def _plausible_cury_title(raw_title: str) -> bool:
    # Editorial notes / page references also end in roman numerals; real
    # roll titles are short, quote-free, digit-free caps lines (after
    # stripping [n] footnote marks, whose digits are not the title's).
    probe = _FOOTNOTE_MARK.sub("", raw_title)
    words = [w.strip(".,") for w in probe.split() if w.strip(".,")]
    # Editorial apparatus reads like "LL. MS. ED." — mostly abbreviations.
    mostly_abbreviations = words and (
        sum(1 for w in words if len(w) <= 2) >= (len(words) + 1) // 2
    )
    return (
        any(c.isalpha() for c in probe)
        and 0 < len(probe) <= _MAX_TITLE_CHARS
        and not any(ch in probe for ch in "_'\"=")
        and not any(c.isdigit() for c in probe)
        and not mostly_abbreviations
    )


def _cury_anchor(line: str) -> tuple[str, str] | None:
    """Return ``(id_token, raw_title)`` if the line opens a recipe."""
    trailing = _CURY_TRAILING.match(line)
    if trailing and _plausible_cury_title(trailing.group(1)):
        numeral = re.sub(
            r"[.\s]+", "-", trailing.group(2).lower()
        ).strip("-")
        return (f"r-{numeral}", trailing.group(1))
    leading = _CURY_LEADING.match(line)
    if leading and _plausible_cury_title(leading.group(2)):
        return (leading.group(1).lower(), leading.group(2))
    return None


def _segment_forme_of_cury(text: str) -> list[RawRecipe]:
    lines = text.splitlines()
    recipes: list[RawRecipe] = []
    used: set[str] = set()
    anchors = [
        (i, found) for i, line in enumerate(lines)
        if (found := _cury_anchor(line)) is not None
    ]
    for pos, (i, (id_token, raw_title)) in enumerate(anchors):
        numeral = id_token
        title = _FOOTNOTE_MARK.sub("", raw_title).strip().title()
        end = anchors[pos + 1][0] if pos + 1 < len(anchors) else len(lines)
        body_paras = [
            _FOOTNOTE_MARK.sub("", p)
            for p in _paragraphs(lines[i + 1 : end])
            # Editorial footnote paragraphs start with the [n] marker itself
            if not re.match(r"^\[\d+\]", p)
        ]
        steps = tuple(p for p in body_paras if p)
        if not steps or sum(len(s) for s in steps) < _MIN_BODY_CHARS:
            continue
        recipes.append(
            RawRecipe(
                upstream_id=(
                    f"pg8102-{_dedupe_slug(numeral, used)}"
                ),
                title=title,
                ingredient_lines=(),
                steps=steps,
            )
        )
    return recipes


_GOLDEN_ANCHOR = re.compile(r"^([A-Z][A-Z '.,\-]{2,58})\.\s*$")


def _segment_golden_age(text: str) -> list[RawRecipe]:
    # Food recipes end where the toiletry/household entries begin (frozen
    # PD text, so the first non-food title is a stable cutoff).
    lines = _cut_at(text.splitlines(), "TOOTH POWDER.")
    recipes: list[RawRecipe] = []
    used: set[str] = set()
    anchors = [
        (i, m) for i, line in enumerate(lines)
        if (m := _GOLDEN_ANCHOR.match(line.strip()))
        and not line.startswith(" ")
        and m.group(1).strip().lower() not in _NON_RECIPE_HEADINGS
    ]
    for pos, (i, match) in enumerate(anchors):
        title = match.group(1).strip().title()
        end = anchors[pos + 1][0] if pos + 1 < len(anchors) else len(lines)
        steps = tuple(_paragraphs(lines[i + 1 : end]))
        if not steps or sum(len(s) for s in steps) < _MIN_BODY_CHARS:
            continue
        recipes.append(
            RawRecipe(
                upstream_id=(
                    f"pg26209-{_dedupe_slug(_slugify(title), used)}"
                ),
                title=title,
                ingredient_lines=(),
                steps=steps,
            )
        )
    return recipes


BOOKS: dict[str, BookProfile] = {
    "beeton": BookProfile(
        key="beeton",
        ebook_id=10136,
        book_title="The Book of Household Management",
        author="Mrs. Isabella Beeton",
        published="1861",
        segment=_segment_beeton,
    ),
    "farmer": BookProfile(
        key="farmer",
        ebook_id=65061,
        book_title="The Boston Cooking-School Cook Book",
        author="Fannie Merritt Farmer",
        published="1918 edition",
        segment=_segment_farmer,
    ),
    "forme_of_cury": BookProfile(
        key="forme_of_cury",
        ebook_id=8102,
        book_title="The Forme of Cury",
        author="Samuel Pegge (ed.), compiled ~1390",
        published="~1390",
        segment=_segment_forme_of_cury,
    ),
    "golden_age": BookProfile(
        key="golden_age",
        ebook_id=26209,
        book_title="The Golden Age Cook Book",
        author="Henrietta Latham Dwight",
        published="1898",
        segment=_segment_golden_age,
    ),
}


# -- conversion --------------------------------------------------------------


@dataclass(frozen=True)
class ConvertedGutenbergRecipe:
    recipe_id: str
    frontmatter: dict
    cooklang_body: str
    upstream_id: str


def convert_recipe(
    raw: RawRecipe,
    profile: BookProfile,
    *,
    ingested_at: str | None = None,
) -> ConvertedGutenbergRecipe:
    when = ingested_at or now_iso()
    recipe_id = new_recipe_id()

    ingredients: list[Ingredient] = []
    for line in raw.ingredient_lines:
        qty, unit, name = split_ingredient_line(line)
        ingredients.append(Ingredient(name=name or line, quantity=qty, unit=unit))

    if ingredients:
        allergens = detect_allergens([ing.name for ing in ingredients])
    else:
        # Narrative-only books: over-flagging beats under-flagging (Rule 1)
        allergens = detect_allergens([raw.title, *raw.steps])

    historical_note = (
        f"Historical recipe from {profile.book_title}"
        f" ({profile.published}); predates modern food-safety and"
        " nutrition guidance — surfaced for cultural/technique context."
    )
    attribution = Attribution(
        source_name=SOURCE_NAME,
        source_url=profile.book_url,
        source_license=SOURCE_LICENSE,
        ingested_at=when,
        ingestion_method=INGESTION_METHOD,
        upstream_id=raw.upstream_id,
    )
    frontmatter = build_recipe_frontmatter(
        recipe_id=recipe_id,
        title=raw.title,
        attribution=attribution,
        source_status="live",
        last_source_check_at=when,
        yields=Yields(count=raw.yields_count or 4),
        top_allergens_present=allergens,
        meal_categories=["historical"],
        modality_availability=["text"],
        modality_resources={"text": f"{recipe_id}.md"},
        estimated_total_time_min=raw.total_time_min,
        ingredient_resolution_summary={
            "fully_resolved": 0,
            "partial": 0,
            "unresolved": len(ingredients),
        },
        ingredient_resolution_status="unresolved_pending_review",
    )
    # S9 optional field — historical context per honest-disclosure discipline
    frontmatter["historical_context_note"] = historical_note

    recipe = Recipe(
        title=raw.title,
        ingredients=tuple(ingredients),
        steps=raw.steps,
        servings=raw.yields_count or 4,
        source_url=profile.book_url,
        attribution=SOURCE_NAME,
        extra_metadata=(
            ("book", profile.book_title),
            ("author", profile.author),
            ("published", profile.published),
        ),
    )
    return ConvertedGutenbergRecipe(
        recipe_id=recipe_id,
        frontmatter=frontmatter,
        cooklang_body=emit_cooklang(recipe),
        upstream_id=raw.upstream_id,
    )


# -- driver -------------------------------------------------------------------


def seed_recipes(
    vault,  # RecipeVault
    *,
    fetcher: TextFetcher | None = None,
    pacer: Pacer | None = None,
    books: tuple[str, ...] | None = None,
    limit: int | None = None,
    ingested_at: str | None = None,
) -> SeedOutcome:
    """Fetch each requested book once, segment, convert, write new recipes."""
    fetch = fetcher if fetcher is not None else _urllib_fetch_text
    pace = pacer if pacer is not None else Pacer()
    seen_upstream = collect_upstream_ids(vault, SOURCE_NAME)

    selected = books or tuple(BOOKS)
    unknown = [key for key in selected if key not in BOOKS]
    if unknown:
        raise ValueError(f"unknown book key(s): {unknown}; know {sorted(BOOKS)}")

    fetched = 0
    written = 0
    skipped: list[str] = []
    for pos, key in enumerate(selected):
        profile = BOOKS[key]
        if pos > 0:
            pace.wait()
        text = strip_pg_boilerplate(fetch(profile.text_url))
        for raw in profile.segment(text):
            fetched += 1
            if raw.upstream_id in seen_upstream:
                skipped.append(raw.upstream_id)
                continue
            converted = convert_recipe(raw, profile, ingested_at=ingested_at)
            vault.write(
                converted.recipe_id,
                converted.frontmatter,
                converted.cooklang_body,
            )
            written += 1
            seen_upstream.add(raw.upstream_id)
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
