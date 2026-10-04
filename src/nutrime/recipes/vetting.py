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
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from nutrime.recipes.store import RecipeRecord, RecipeVault

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


@dataclass(frozen=True)
class VetOutcome:
    examined: int
    titles_normalized: int
    quarantined: int
    already_vetted: int


def vet_vault(vault: RecipeVault, *, revet: bool = False) -> VetOutcome:
    """One pass over the vault: normalize titles, stamp vetting_status.

    Idempotent: rows already stamped are skipped unless ``revet``.
    """
    examined = 0
    normalized = 0
    quarantined = 0
    skipped = 0
    for record in vault.iter_recipes():
        examined += 1
        fm = dict(record.frontmatter)
        if not revet and fm.get("vetting_status") in ("vetted", "quarantined"):
            skipped += 1
            continue

        title = str(fm.get("title", ""))
        cleaned = normalize_title(title)
        if cleaned != title:
            if "title_original" not in fm:
                fm["title_original"] = title
            fm["title"] = cleaned
            normalized += 1

        verdict = vet_record(
            RecipeRecord(
                recipe_id=record.recipe_id, frontmatter=fm, body=record.body,
                path=record.path,
            )
        )
        if verdict.ok:
            fm["vetting_status"] = "vetted"
            fm.pop("vetting_reason", None)
        else:
            fm["vetting_status"] = "quarantined"
            fm["vetting_reason"] = verdict.reason
            quarantined += 1
        vault.write(record.recipe_id, fm, record.body)
    return VetOutcome(
        examined=examined,
        titles_normalized=normalized,
        quarantined=quarantined,
        already_vetted=skipped,
    )
