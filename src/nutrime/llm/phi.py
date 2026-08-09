"""PHI envelope declarations for LLM query types (5.2).

Per S4-Q2 typed-PHI-boundary discipline, every query type declares the PHI
categories it may carry before any crossing exists. Two registrations land
with the adapter layer:

- ``llm_ping`` — connectivity smoke test; carries nothing (empty, fail-closed
  on any accidental inclusion, same pattern as ``recipe_search``).
- ``meal_plan_generation`` — the 5.4 planner's query type, declared here so
  the envelope exists before the first planner call is ever written. The
  envelope is the **union across decomposed slices**: abstracted constraints
  derived from allergens ("avoids shellfish") and life-stage/demographic
  context ("household of 2 adults"). Raw screener results and clinical
  disclosures never cross — the planner reads abstracted constraints only
  (two-track seam). Per-crossing, the S4-Q2 single-slice rule is enforced by
  :class:`~nutrime.llm.client.LlmClient` — a single call carries at most one
  of these categories; multi-slice needs decompose into single-slice calls +
  local aggregation.
"""

from __future__ import annotations

from nutrime.phi import PhiCategory, PhiEnvelopeRegistry

LLM_PING = "llm_ping"
MEAL_PLAN_GENERATION = "meal_plan_generation"


def register_llm_envelopes(registry: PhiEnvelopeRegistry) -> None:
    registry.register(LLM_PING, ())
    registry.register(
        MEAL_PLAN_GENERATION,
        (PhiCategory.ALLERGENS, PhiCategory.DEMOGRAPHICS),
    )
