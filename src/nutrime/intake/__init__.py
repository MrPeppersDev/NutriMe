"""First-run baseline intake — MVP screener trio + demographics profile.

Sub-commit 2.1 (Stage 6 step 2, per S4-Q5 yellow-flag resolution 2026-06-30).
Ships the three validated instruments verified in ``stage3-plan.md`` §
"Component verification log" (PHQ-2 ≥3, GAD-2 ≥3, Hunger Vital Sign ≥1
affirmative on either item) plus the structured demographics + life-stage +
dietary preferences + allergens capture.

Inventory intake (pantry / fridge / freezer) lands in sub-commit 2.2 and is a
separate surface with zero PHI per Rule 3.
"""

from nutrime.intake.instruments import (
    PHQ2,
    GAD2,
    HUNGER_VITAL_SIGN,
    Instrument,
    InstrumentItem,
    ScreenerResult,
    ResponseScale,
)
from nutrime.intake.store import IntakeProfile, save_profile, save_screener_responses

__all__ = [
    "PHQ2",
    "GAD2",
    "HUNGER_VITAL_SIGN",
    "Instrument",
    "InstrumentItem",
    "ScreenerResult",
    "ResponseScale",
    "IntakeProfile",
    "save_profile",
    "save_screener_responses",
]
