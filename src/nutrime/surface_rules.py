"""Constitutional rules at the pre-surface boundary (issue #30).

The pre-egress engine in :mod:`nutrime.rules` guards what *leaves* the
household. This module guards what the system *shows* — any text an LLM
(or another inference step) wrote that is about to reach a person. Same
discipline: deterministic, hardcoded, outside any LLM (constitutional
Rules 1 + 7 enforcement notes; A3-v2).

Three rules, three outcomes:

- :class:`BannedContentRule` — **block**. Rule 3 (no calorie/macro
  logging prompts), Rule 4 (no generated recipes), cure/reversal claims,
  and eating-disorder-adjacent advice. Nothing here is "surface with
  context"; it never reaches the user.
- :class:`EvidenceFloorRule` — **block** unless the content carries a
  Tier 1-3 evidence reference. Rule 7: a health claim cannot rest on
  nothing (or on Tier 4 alone). The caller drops or replaces the text.
- :class:`ConsultProfessionalRule` — **annotate**. Rule 1: clinical-
  adjacent content, a Tier 3 basis, or an eater with a disclosed
  condition / sensitive life stage gets the consult-a-professional line
  *adjacent* to the text — appended to it, not in a footer. Never
  withholds (Rule 1 is transparency plus redirection, not gatekeeping).

Any block wins; otherwise annotations are appended once each. The L1
harness (tests/test_surface_rules.py) is the test bed: a new bypass goes
into the corpus first, then the patterns harden — and every benign
sample must keep passing, because a rule layer that blocks real meal
notes is a rule layer that gets turned off.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from typing import Iterable, Literal, Protocol

from nutrime.rules import normalize_for_scan

Action = Literal["pass", "annotate", "block"]

CONSULT_LINE = (
    "This touches on health. Check with a doctor or registered dietitian"
    " before relying on it."
)

# Life stages whose nutrition needs differ enough that anything health-
# adjacent shown about the eater warrants the Rule 1 line.
SENSITIVE_LIFE_STAGES = frozenset(
    {"infant", "child", "adolescent", "pregnant", "lactating", "older_adult"}
)


@dataclass(frozen=True)
class SurfaceContent:
    """Text about to be shown, plus what the rules need to judge it.

    ``generated``: written by an LLM / inference step (corpus text the
    system merely displays is not checked for Rule 4).
    ``evidence_tier``: strongest tier (1 best … 4) backing any claim in the
    text, or None when the text cites nothing.
    ``eater_sensitivities``: disclosed conditions + sensitive life stages
    of whoever will eat this (Rule 10: gating applies to the eater).
    """

    surface: str
    text: str
    generated: bool = True
    evidence_tier: int | None = None
    eater_sensitivities: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class SurfaceFinding:
    rule_name: str
    action: Action
    reason: str
    annotation: str = ""


@dataclass(frozen=True)
class SurfaceVerdict:
    action: Action
    text: str  # what to display: original, annotated, or "" when blocked
    findings: tuple[SurfaceFinding, ...] = ()

    @property
    def blocked(self) -> bool:
        return self.action == "block"


class SurfaceRule(Protocol):
    name: str

    def evaluate(self, content: SurfaceContent) -> SurfaceFinding | None: ...


def _scan_text(text: str) -> str:
    return " ".join(normalize_for_scan(text).split())


def _first_match(
    patterns: Iterable[tuple[re.Pattern[str], str]], text: str
) -> str | None:
    for pattern, label in patterns:
        if pattern.search(text):
            return label
    return None


# -- Rule 3 / Rule 4 / harmful content ------------------------------------------

_LOGGING_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(log|record|enter|write\s+down)\s+(what|everything)\s+you\s+(ate|eat|had)\b", re.I),
     "food-logging prompt (Rule 3)"),
    (re.compile(r"\b(log|track|count|record)(ing)?\s+(your\s+|daily\s+|every\s+)*(calories|macros|kcal|carbs|food\s+intake|meals?\s+eaten)\b", re.I),
     "calorie/macro tracking prompt (Rule 3)"),
    (re.compile(r"\b(calories|kcal|macros)\s+(left|remaining|budget)\b", re.I),
     "calorie budget (Rule 3)"),
    (re.compile(r"\bfood\s+(diary|journal|log)\b", re.I),
     "food diary (Rule 3)"),
)

_HARM_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(cures?|reverses?|eliminates?)\s+(your\s+)?(cancer|diabetes|heart\s+disease|hypertension|arthritis|autism|adhd|depression|anxiety|alzheimer'?s|dementia|kidney\s+disease|ibs|crohn'?s)\b", re.I),
     "cure/reversal claim"),
    (re.compile(r"\b(thinspo|pro[\s-]?ana|pro[\s-]?mia|meanspo)\b", re.I),
     "eating-disorder content"),
    (re.compile(r"\b(purg(e|ing)|make\s+yourself\s+(sick|throw\s+up)|self[\s-]?induced\s+vomit)", re.I),
     "purging"),
    (re.compile(r"\b(starve\s+yourself|starvation\s+diet|skip(ping)?\s+(meals|eating)\s+to\s+(lose|drop|burn))\b", re.I),
     "restriction advice"),
    # A daily target under 1,200 kcal (the common adult floor), not a
    # per-serving fact ("only 450 calories per serving" is a recipe property).
    (re.compile(r"\b(1,?[01]\d\d|[1-9]\d\d|[1-9]\d)\s*(k?cal|calories)\s*(a|per|each)\s+day\b"
                r"|\b(eat|consume|stay|keep)\s+(less\s+than|under|below|fewer\s+than)\s*"
                r"(1,?[01]\d\d|[1-9]\d\d|[1-9]\d)\s*(k?cal|calories)\b", re.I),
     "very-low-calorie target"),
    (re.compile(r"\b(water|juice|dry)\s+fast(ing)?\s+for\s+(\d{2,}|[3-9])\s+days\b", re.I),
     "extended fasting"),
)

# Rule 4: an LLM-written recipe looks like quantities + method.
_QUANTITY_LINE = re.compile(
    r"^\s*(?:[-*•]\s*)?(?:\d+(?:[./]\d+)?|½|¼|¾|⅓|⅔)\s*"
    r"(?:g|kg|ml|l|oz|lb|lbs|cups?|tbsp|tsp|tablespoons?|teaspoons?|cloves?|"
    r"pinch|cans?|grams?|pounds?|ounces?)\b",
    re.I | re.M,
)
_STEP_LINE = re.compile(
    r"^\s*(?:step\s*\d+|\d+[.)])\s+\w", re.I | re.M,
)
_RECIPE_OFFER = re.compile(
    r"\b(here'?s|here\s+is)\s+(a|my|an?\s+easy|a\s+simple|the)?\s*recipe\b"
    r"|\bingredients\s*:.*\b(instructions|method|directions|steps)\s*:",
    re.I | re.S,
)


class BannedContentRule:
    name = "banned-content"

    def evaluate(self, content: SurfaceContent) -> SurfaceFinding | None:
        text = _scan_text(content.text)
        label = _first_match(_LOGGING_PATTERNS, text) or _first_match(
            _HARM_PATTERNS, text
        )
        if label is None and content.generated:
            raw = normalize_for_scan(content.text)
            quantities = len(_QUANTITY_LINE.findall(raw))
            steps = len(_STEP_LINE.findall(raw))
            if _RECIPE_OFFER.search(raw) or (quantities >= 3 and steps >= 2):
                label = "generated recipe (Rule 4)"
        if label is None:
            return None
        return SurfaceFinding(self.name, "block", label)


# -- Rule 7: evidence floor ---------------------------------------------------------

_CLAIM_VERB = (
    r"(lowers?|lowering|reduces?|reducing|cuts?|improves?|improving|boosts?|"
    r"boosting|prevents?|preventing|fights?|fighting|protects?\s+against|"
    r"heals?|treats?|treating|regulates?|balances?|strengthens?|supports?|"
    r"speeds?\s+up|burns?|melts?|flushes?|detoxif(?:y|ies)|cleanses?|"
    r"is\s+(?:good|great|proven)\s+for|helps?(?:\s+(?:to|you))?\s+(?:lower|reduce|"
    r"prevent|fight|boost|improve|heal|burn|lose|control|manage))"
)
_CLAIM_OBJECT = (
    r"(blood\s+pressure|cholesterol|inflammation|immun\w*|blood\s+sugar|glucose|"
    r"insulin|metabolism|hormones?|gut\s+health|heart\s+(?:health|disease)|"
    r"(?:cancer|disease|stroke|diabetes)(?:\s+risk)?|risk\s+of\s+(?:heart\s+\w+|"
    r"cancer|stroke|diabetes|disease|dementia|death|osteoporosis)|weight|"
    r"(?:belly|body|visceral)\s+fat|toxins?|liver|brain\s+health|anxiety|"
    r"depression|bone\s+density|arthritis|longevity)"
)
_HEALTH_CLAIM = re.compile(
    rf"\b{_CLAIM_VERB}\b(?:\s+\w+){{0,4}}?\s+{_CLAIM_OBJECT}\b"
    rf"|\b(anti[\s-]?inflammatory|detox(?:ifying)?|fat[\s-]?burning|"
    rf"immune[\s-]?boosting|superfood|metabolism[\s-]?boosting)\b",
    re.I,
)


class EvidenceFloorRule:
    name = "evidence-floor"

    def evaluate(self, content: SurfaceContent) -> SurfaceFinding | None:
        text = _scan_text(content.text)
        match = _HEALTH_CLAIM.search(text)
        if match is None:
            return None
        tier = content.evidence_tier
        if tier is not None and 1 <= tier <= 3:
            return None
        why = (
            "Tier 4 alone cannot support a health claim (Rule 7)"
            if tier == 4
            else "health claim with no peer-reviewed evidence attached (Rule 7)"
        )
        return SurfaceFinding(
            self.name, "block", f"{why}: {match.group(0)!r}"
        )


# -- Rule 1: consult a professional ---------------------------------------------

_CLINICAL_TOPIC = re.compile(
    r"\b(diabet\w*|insulin|kidney\s+(?:disease|function|stones?|failure|health|problems?)|ckd|renal|dialysis|"
    r"liver\s+disease|pregnan\w*|"
    r"breastfeed\w*|lactat\w*|eating\s+disorder|anorexi\w*|bulimi\w*|binge|"
    r"(?<!food\s)supplements?|vitamin\s+[a-k]\d*\s+(?:dose|pill|tablet)|medications?|"
    r"prescriptions?|drug\s+interactions?|warfarin|blood\s+thinners?|statins?|"
    r"maoi|metformin|ozempic|semaglutide|glp-1|celiac|coeliac|crohn'?s|"
    r"colitis|ibs|gerd|hypertension|high\s+blood\s+pressure|cholesterol|"
    r"heart\s+(?:disease|condition)|cancer|chemo\w*|gout|pku|"
    r"food\s+intolerance|fodmap|weight\s+loss|lose\s+weight)\b",
    re.I,
)
_ALREADY_REFERRED = re.compile(
    r"\b(doctor|physician|gp|dietitian|dietician|nutritionist|clinician|"
    r"health\s*care\s+(?:provider|professional|team)|pharmacist|midwife|"
    r"pediatrician|paediatrician)\b",
    re.I,
)


class ConsultProfessionalRule:
    name = "consult-professional"

    def evaluate(self, content: SurfaceContent) -> SurfaceFinding | None:
        text = _scan_text(content.text)
        if not text:
            return None
        reasons: list[str] = []
        topic = _CLINICAL_TOPIC.search(text)
        if topic:
            reasons.append(f"clinical-adjacent topic {topic.group(0)!r}")
        if content.evidence_tier is not None and content.evidence_tier >= 3:
            reasons.append(f"Tier {content.evidence_tier} evidence")
        if content.eater_sensitivities and _HEALTH_CLAIM.search(text):
            reasons.append("health content for an eater with a disclosed sensitivity")
        if not reasons:
            return None
        if _ALREADY_REFERRED.search(text):
            return None  # the text already points to a professional, adjacent
        return SurfaceFinding(
            self.name, "annotate", "; ".join(reasons), annotation=CONSULT_LINE
        )


# -- engine ---------------------------------------------------------------------


class SurfaceGuard:
    """Fail-closed pre-surface engine. A rule that raises blocks the text."""

    def __init__(self, rules: Iterable[SurfaceRule] | None = None) -> None:
        self._rules: list[SurfaceRule] = list(rules or [])

    def register(self, rule: SurfaceRule) -> None:
        self._rules.append(rule)

    @property
    def rules(self) -> tuple[SurfaceRule, ...]:
        return tuple(self._rules)

    def check(self, content: SurfaceContent) -> SurfaceVerdict:
        findings: list[SurfaceFinding] = []
        for rule in self._rules:
            try:
                finding = rule.evaluate(content)
            except Exception as exc:  # noqa: BLE001 — fail closed
                finding = SurfaceFinding(
                    getattr(rule, "name", type(rule).__name__),
                    "block",
                    f"rule raised {type(exc).__name__}: {exc}",
                )
            if finding is not None:
                findings.append(finding)
        if any(f.action == "block" for f in findings):
            return SurfaceVerdict("block", "", tuple(findings))
        annotations: list[str] = []
        for f in findings:
            if f.annotation and f.annotation not in annotations:
                annotations.append(f.annotation)
        if not annotations:
            return SurfaceVerdict("pass", content.text, tuple(findings))
        text = content.text.rstrip()
        joined = " ".join(annotations)
        return SurfaceVerdict(
            "annotate", f"{text} — {joined}" if text else joined, tuple(findings)
        )


def default_surface_guard() -> SurfaceGuard:
    return SurfaceGuard(
        [BannedContentRule(), EvidenceFloorRule(), ConsultProfessionalRule()]
    )


def household_sensitivities(
    conn: sqlite3.Connection, tenant_id: str
) -> frozenset[str]:
    """Disclosed non-allergy conditions + sensitive life stages across the
    household's active members — the eater context for household-wide
    surfaces such as a meal plan. Allergies are excluded: they are
    hard-filtered at candidate generation, not a Rule 1 trigger."""
    from nutrime.intake.store import household_profiles
    from nutrime.knowledge.store import list_atoms
    from nutrime.members import list_members, subject_ids_for

    out: set[str] = set()
    for profile in household_profiles(conn, tenant_id).values():
        if profile.life_stage in SENSITIVE_LIFE_STAGES:
            out.add(f"life_stage:{profile.life_stage}")
    subjects: set[str] = set()
    for member in list_members(conn, tenant_id):
        subjects.update(subject_ids_for(conn, tenant_id, member.id))
    for atom in list_atoms(conn, tenant_id, atom_type="clinical_disclosure"):
        if atom.subject_id not in subjects:
            continue
        if atom.payload.get("disclosure_type") == "allergy":
            continue
        text = str(atom.payload.get("disclosure_text") or "").strip().lower()
        if text:
            out.add(f"condition:{text}")
    return frozenset(out)
