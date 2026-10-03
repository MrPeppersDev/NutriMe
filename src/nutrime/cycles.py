"""Cycle-phase → food-preference boost terms (PROTOTYPE STUB, issue #25).

This is the prototype-grade cut explicitly allowed by issue #25: a
user-entered phase maps to canned "prefers"-style boost terms so the
household can exercise the query shape end-to-end. It is NOT Track G
constraint derivation — no knowledge-model atoms are written, no DRI
refresh fires, and nothing here claims clinical authority. When Track G
resumes, this module is replaced by real phase atoms + an
evidence-tier-graded phase→nutrient mapping emitting synthesized
"prefers X" constraints.

Privacy shape (the part that is NOT a stub): the selected phase is used
only to pick local search-ranking boosts. It never crosses the egress
boundary — recipe search is a local, PHI-free operation per the 4.1
``recipe_search`` envelope, and boosts are score nudges, never filters
(matching the seam rule: "prefers" may boost, only "avoids" may block).

Evidence honesty per constitutional Rules 8/9: each phase carries a
plain-language note stating how well-supported the association is.
Iron repletion around menstruation is the solid one; most broader
"cycle-syncing" food lore is weakly evidenced, and the notes say so.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseProfile:
    key: str
    label: str
    # Ingredient-shaped terms fed to SearchFilters.prefer_terms (boosts only)
    prefer_terms: tuple[str, ...]
    # What the boost is aiming at, in food-first language
    emphasis: str
    # Plain-language evidence honesty line, always shown beside results
    evidence_note: str


PHASES: tuple[PhaseProfile, ...] = (
    PhaseProfile(
        key="menstrual",
        label="Menstrual",
        prefer_terms=(
            "spinach", "lentil", "bean", "beef", "tofu",
            "citrus", "orange", "pepper",
        ),
        emphasis="iron-rich foods, paired with vitamin-C sources that aid"
        " iron absorption",
        evidence_note="Replacing iron lost during menstruation is"
        " well-supported nutrition guidance; pairing iron with vitamin C"
        " to improve absorption is also well-established.",
    ),
    PhaseProfile(
        key="follicular",
        label="Follicular",
        prefer_terms=(
            "egg", "chicken", "fish", "yogurt",
            "broccoli", "spinach", "berry", "oat",
        ),
        emphasis="protein and generally nutrient-dense whole foods",
        evidence_note="Specific follicular-phase food rules are weakly"
        " evidenced — most 'cycle-syncing' food advice for this phase is"
        " wellness lore, not clinical guidance. These boosts just favor"
        " broadly nutrient-dense recipes.",
    ),
    PhaseProfile(
        key="ovulatory",
        label="Ovulatory",
        prefer_terms=(
            "salmon", "fish", "quinoa", "tomato",
            "berry", "kale", "avocado",
        ),
        emphasis="fiber and antioxidant-rich produce",
        evidence_note="There is no solid evidence for ovulation-specific"
        " food needs; these boosts simply favor produce-forward recipes."
        " Treat phase-specific claims you see online with skepticism.",
    ),
    PhaseProfile(
        key="luteal",
        label="Luteal",
        prefer_terms=(
            "salmon", "chickpea", "banana", "potato",
            "whole grain", "oat", "pumpkin", "almond",
        ),
        emphasis="magnesium- and B6-containing foods plus steady complex"
        " carbohydrates",
        evidence_note="Magnesium/B6 for premenstrual symptoms has mixed,"
        " modest evidence (some supplement trials show small benefits);"
        " food-level effects are plausible but not firmly established.",
    ),
)

PHASES_BY_KEY = {phase.key: phase for phase in PHASES}

STUB_DISCLOSURE = (
    "Phase-based suggestions are a prototype: gentle ranking boosts toward"
    " foods associated with each phase, with the evidence honestly labeled."
    " They never exclude recipes, and your selection stays on this device."
)


def phase_prefer_terms(phase_key: str) -> frozenset[str]:
    """Boost terms for a phase key; unknown keys get no boosts (fail-open
    to zero effect, never to a filter)."""
    profile = PHASES_BY_KEY.get(phase_key)
    if profile is None:
        return frozenset()
    return frozenset(profile.prefer_terms)
