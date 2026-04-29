# NutriMe — Epistemic Trail of Honesty

> When NutriMe correlates data, combines sources, or infers conclusions, the system must show its work. The user sees the reasoning, the verification, and the limitations — not just the conclusion.

This is the operational definition of [Constitutional Rule 8](constitutional-rules.md#rule-8--epistemic-trail-of-honesty).

## The five operational requirements

### 1. Provenance tracking

Every input to a correlation / inference must retain a documented source.

Examples:

- A lab value: "Vitamin D 28 ng/mL — source: LabCorp report uploaded 2026-03-15, requested through doctor portal X, lab method Y"
- A wearable signal: "Average HRV 42ms — source: Apple Watch Series 9, daily aggregate from HealthKit 2026-04-01 to 2026-04-21"
- A user statement: "Reports bloating after wheat — source: semantic feedback, meal X, recorded 2026-04-12"
- An evidence claim: "Adults need 7+ hours sleep for metabolic health — source: NSF 2015 consensus statement, Tier 1, see [evidence-tiers.md](evidence-tiers.md)"

### 2. Cross-referencing logic documentation

When two or more inputs combine to produce an inference, the reasoning chain must be documented:

- Which inputs were used
- What the inference logic was (explicit rule, statistical correlation, LLM reasoning, etc.)
- What assumptions were made
- What was excluded or weighted down

Example documented chain:

> *Inference:* "Your iron intake may be borderline given your reported fatigue and sleep quality."
>
> *Inputs:*
> - Reported chronic mild fatigue (intake, 2026-04-01)
> - Sleep quality PSQI 9 (intake, 2026-04-01) — moderately poor
> - Estimated iron intake 9.5 mg/day (computed from semantic feedback over 14 days against USDA FDC)
> - Female, age 32, no pregnancy disclosed → US RDA 18 mg/day
>
> *Logic:* Estimated intake is approximately 53% of RDA. Fatigue and poor sleep are non-specific but consistent with iron insufficiency in pre-menopausal females. This is a hypothesis from low-certainty inference, not a diagnosis.
>
> *Assumptions:* Intake estimate from 14-day semantic-feedback sample; missing meals not estimated. Iron bioavailability not modeled (heme/non-heme split, vitamin C co-intake, polyphenol inhibition).

### 3. Verification before presenting

Inferences pass through verification before reaching the user:

- Sanity-check inputs against expected ranges
- Confirm provenance is complete (no anonymous inferences)
- Confirm peer-reviewed evidence supports the inference type (per [Rule 7](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor))
- Confirm consult-professional language is included where required (per [Rule 1](constitutional-rules.md#rule-1--consult-a-professional))
- Flag inferences where AI confidence is low or where multiple plausible explanations exist
- **Causal-explanation generation as verification.** Before delivering an inference, the system generates the full causal chain explaining *why* the conclusion follows from the inputs. The act of articulating "input X → mechanism Y → conclusion Z" surfaces inconsistencies and small numerical errors (yes/no flips, off-by-one quantities, contradictory premises) that pass through unverified opaque reasoning. Inferences whose causal explanation does not hold together are rejected or downgraded.

Failed verifications are either suppressed or surfaced with explicit "low-confidence inference" framing.

The causal-explanation step is itself a deliverable — the same explanation that verifies the inference becomes the user-facing "why" content (per [sweep #8](../08-nutrition-education-delivery/scope.md)). Verification and education are produced by the same artifact, which prevents drift between what the system *did* internally and what it *tells the user* externally.

### 4. Surface the trail to the user

Provenance + reasoning + verification status are first-class user-visible content, not hidden in logs. The user can always:

- See where any conclusion came from
- See the evidence base behind it (per [evidence-tiers.md](evidence-tiers.md))
- See the AI confidence level
- Drill into the supporting inputs

The user does NOT have to be a researcher to use the product, but the trail is *available* on demand and surfaced *prominently* when confidence is moderate or low.

### 5. Be explicit about AI limitations

The product never pretends AI inference is more reliable than it is:

- "AI correlation is not always perfect"
- "Combinations of data sources can produce errors that individual sources do not"
- "Bring uncertainties to your doctor or licensed nutritionist" (per Rule 1)
- "This inference is based on [N] inputs over [period]; longer / more data improves accuracy"

Confidence framing is honest:

- **High confidence:** multiple peer-reviewed sources, consistent inputs, narrow reasoning chain
- **Moderate confidence:** some peer-reviewed support, some inference required, some assumptions
- **Low confidence:** inference-heavy, sparse data, or multiple plausible explanations — explicit "this is suggestive, not conclusive" framing

Low-confidence outputs require the consult-professional callout.

## Why this exists

AI systems can produce conclusions that look authoritative but are stitched together from sources of varying quality with assumptions the user can't see. In a health-adjacent product this is dangerous — the user may act on a conclusion that, on inspection, doesn't hold up.

The epistemic trail makes the inference auditable. It prevents NutriMe from looking like an oracle and instead positions it as a research-and-recommendation collaborator whose work is visible to the user.

## Where this rule applies (selected examples)

- Lab result interpretation (correlating panel + dietary pattern + history)
- Wearable signal interpretation (HRV + sleep + dietary feedback)
- Food-symptom correlation (semantic feedback "made me feel bloated" against ingredient lists)
- Nutrient adequacy estimates from semantic feedback against composition databases
- Personalization adjustments based on multiple feedback channels
- Cross-cuisine recommendation generation
- Multi-user household conflict resolution

## Source

- User direction (2026-04-28, sweep #6 scoping): "we need to surface the fact that we are trying to correlate data as best as possible with an AI system, and that that's not always gonna be perfect. We really want to try to build an epistemic trail of honesty as to how the data was cross-referenced and in what way, and then run verification pipelines over that before we present it to the user with that trail of honesty."
- User direction (2026-04-28, sweep #8 scoping) on causal-explanation as verification: "we want to provide for the causal explanation depth pretty in-depth explanations here. This way we can have system checks preemptively to make sure that there were no bit changes in a yes versus a no or 25 versus 26, right, little number changes, before we deliver the answer to the user, as well as delivering the most comprehensive understanding of the answer possible based on our system knowledge."
