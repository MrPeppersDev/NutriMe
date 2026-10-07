"""Life-stage food-avoidance rails — sweep #10 §3, built per issue #46.

Life-stage is the always-honored physiological tier (sweep #9): these
rails stack on top of whatever conditions a member disclosed. Like the
condition registry, this is **hardcoded and outside any LLM** — the
lists are computed from the profile at every use, never stored, so a
correction here applies to already-captured life stages.

Only the food-AVOIDANCE half of §3 lives here (the part expressible as
search/planner exclusions). Nutrient emphasis (folate, iron, choline…)
is prompt-rail territory and stays with the planner notes.

Sources (scope.md §3.1-§3.2): ACOG Nutrition During Pregnancy;
FDA/EPA Advice About Eating Fish (high-mercury list: shark, swordfish,
king mackerel, tilefish, marlin, orange roughy, bigeye tuna); FDA
food-safety-for-pregnancy guidance (Listeria: unpasteurized milk/soft
cheese, deli/luncheon meats unless steaming-hot, refrigerated pâté and
smoked seafood, raw sprouts); CDC alcohol-in-pregnancy guidance.
Lactation mirrors the fish list (same Hg concern) but NOT the Listeria
list — listeriosis risk is to the fetus, and current consensus does
not restrict the maternal diet while nursing beyond fish choices.
"""

from __future__ import annotations

from dataclasses import dataclass

# High-mercury fish — FDA/EPA "choices to avoid" list, shared by
# pregnancy and lactation.
_HIGH_MERCURY_FISH: tuple[str, ...] = (
    "shark", "swordfish", "king mackerel", "tilefish", "marlin",
    "orange roughy", "bigeye tuna",
)

# Listeria / Toxoplasma / raw-protein vectors — pregnancy only.
_PREGNANCY_FOOD_SAFETY: tuple[str, ...] = (
    "raw oyster", "raw clam", "raw fish", "sashimi", "sushi",
    "ceviche", "carpaccio", "steak tartare", "raw egg",
    "unpasteurized milk", "raw milk", "unpasteurized cheese",
    "raw sprouts", "bean sprouts",
    "deli meat", "luncheon meat", "cold cuts", "prosciutto",
    "smoked salmon", "lox", "pate", "pâté",
    "alcohol", "wine", "beer", "rum", "brandy", "bourbon", "vodka",
    "sake", "mirin",
)


@dataclass(frozen=True)
class LifeStageRails:
    """Avoidance terms + the planner note for one household."""

    avoid_terms: frozenset[str]
    plan_notes: tuple[str, ...]
    stages: tuple[str, ...]  # which life stages contributed


def life_stage_rails(active_life_stages: set[str]) -> LifeStageRails:
    """Rails for the given set of active members' life stages.

    Terms are recipe-ingredient exclusion terms (recall-biased matching
    downstream, same as the avoid-list). Empty set → empty rails.
    """
    avoid: set[str] = set()
    notes: list[str] = []
    stages: list[str] = []
    if "pregnant" in active_life_stages:
        stages.append("pregnant")
        avoid.update(_HIGH_MERCURY_FISH)
        avoid.update(_PREGNANCY_FOOD_SAFETY)
        notes.append(
            "an eater is pregnant — exclude high-mercury fish, raw or "
            "undercooked animal protein, unpasteurized dairy, deli meats, "
            "raw sprouts and alcohol entirely; favor folate- and "
            "iron-rich meals"
        )
    if "lactating" in active_life_stages:
        stages.append("lactating")
        avoid.update(_HIGH_MERCURY_FISH)
        notes.append(
            "an eater is breastfeeding — exclude high-mercury fish "
            "(shark, swordfish, king mackerel, tilefish, marlin, orange "
            "roughy, bigeye tuna); favor iodine- and choline-rich meals"
        )
    return LifeStageRails(
        avoid_terms=frozenset(avoid),
        plan_notes=tuple(notes),
        stages=tuple(stages),
    )


def household_life_stage_rails(conn, tenant_id: str) -> LifeStageRails:
    """Rails for every ACTIVE member's current life stage."""
    from nutrime.intake.store import household_profiles

    stages = {
        profile.life_stage
        for profile in household_profiles(conn, tenant_id).values()
    }
    return life_stage_rails(stages)
