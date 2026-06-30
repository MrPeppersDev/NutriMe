# NutriMe — Knowledge Model

> First-class system data layer that holds **per-user** and **per-household** state of *what's been delivered, what's been experienced, and what's been preferred* over time. Distinct from food/macro/calorie logging (out per [Rule 3](constitutional-rules.md#rule-3--no-food--macro--calorie-logging)) — the knowledge model tracks *system delivery state* and *household experience memory*, not user food intake.

The knowledge model is what makes [spaced education](synthesis.md#tension-3--spaced-repetition-cadence-vs-no-daily-check-in-rule), [topic-relevance triggers](#topic-relevance-triggers), and [iterative horizon-broadening pacing](intake-pattern.md) actually work. Without it, the system would re-explain the same concepts to a user who's already learned them, push the same cuisines a household has rejected, and miss obvious cross-meal correlations.

## Tenant scoping (per A1-v2 / A2-v2 — 2026-06-29)

The knowledge model lives in a **multi-tenant home server** (per [architecture.md A1-v2](architecture.md#a1-v2--deployment-model-multi-tenant-home-server)). Every per-user and per-household row carries a `tenant_id` (the F9 schema axis open in [schema.md](schema.md)). Tenant boundary semantics:

- **Per-user knowledge model rows are tenant-scoped.** A tenant cannot read or write another tenant's per-user state without explicit cross-tenant consent. Default visibility is strict-per-user.
- **Per-household knowledge model rows live inside a household tenant scope.** Members of a household share the household-level rows; cross-household sharing is opt-in only.
- **Abstracted constraints surface across tenants only when their source data is constraint-only-shared or mutual-consent-shared** (per the Tension #5 three-level model below). The constraint travels; the source PHI does not.
- **Migration-runner implications** for the existing un-tenanted schema design are part of the F9 / S13 follow-up sweep before Stage 4 build.

Cross-tenant access is treated as a boundary crossing on par with cloud-LLM crossing per [Rule 6](constitutional-rules.md#rule-6--health-data-stays-inside-the-household-network-by-default-cross-tenant-and-cloud-crossings-are-decomposed-minimal-and-consent-gated) and [phi-handling.md](phi-handling.md). The iPhone↔Mac-server transport (per A2-v2) is another boundary surface; the knowledge model itself is not transport-aware but the persistence layer is.

## Two layers

### Per-user knowledge model

Tracks each user's individual state:

- **Concepts delivered + when** — every educational chunk surfaced to this user, with timestamp
- **Observed engagement** — whether the user opened, read past the first sentence, dwelt on, asked a follow-up question, dismissed quickly
- **Comprehension signals** — when the user later applies a concept correctly (e.g., asks for a recipe that fits a recently-explained dietary pattern), positive signal; when they ask the same question already answered, gap signal
- **Curiosity preferences** — topics the user actively explores via the opt-in pull surface
- **Stretch readiness** — current cooking confidence + skill state per [sweep #12](../12-skills-by-cuisine/scope.md), and per-cuisine progression position
- **Personal context** — health screeners, dietary preferences, allergies, life-stage state — pulled from the [intake pattern](intake-pattern.md)

Every signal in the per-user model is tagged with **provenance** (per [synthesis.md Tension #4](synthesis.md#tension-4--consumer-friendly-clinical-instrument-vs-validity-preservation)):

- `validated-instrument` — signal originated from a validated psychometric instrument (PHQ-9, GAD-7, SCOFF, PSQI, CCSS, etc.). Carries sensitivity/specificity profile + confidence intervals from the instrument's validation literature.
- `conversational-elicitation` — signal elicited via the methodology-borrowed conversational pattern in domains without validated instruments. Carries an honest "this is elicited, not measured" framing.
- `passive-observation` — signal inferred from order data, cook confirmations, app interactions. Carries inference-quality framing.

Downstream inferences (via [Rule 8 epistemic trail](epistemic-trail.md)) weight differently by provenance — the trail surfaces source so the user can understand what kind of evidence drove a recommendation.

### Per-household knowledge model

Tracks the household's collective state:

- **Shared experience memory** — meals the household has cooked together, who liked what, household-level repeat-success vs. rejection
- **Household-level interests** — cuisines the household actively explores, dietary patterns the household has moved toward
- **Collective decisions + their rationale** — "we agreed to lean Mediterranean for January," "we're avoiding nut-heavy recipes because of allergy in the household"
- **Negotiation history** — when household members had conflicting preferences, how it was resolved, whether the resolution stuck
- **Privacy boundaries** — which fields are shared across members, which are private (per [sweep #9 privacy defaults](../09-multi-user-household/scope.md))
- **Abstracted constraints sourced from each member** — see below

The household model is **not reducible to the union of per-user models.** A household has collective memory that no single member fully holds. *"We tried Korean last month and Sarah didn't love it"* is a household-level fact even though only Sarah's individual experience produced it.

### Abstracted constraint layer *(per [synthesis.md Tension #5](synthesis.md#tension-5--cross-sweep-wearable-data-household-sharing-gap))*

When wearable / biometric / clinical data exists at the per-user level (CGM streams, lab results, condition disclosures, life-stage state), the per-household model holds **abstracted constraints** computed from that data — not the data itself.

- *Per-user model* holds raw data + derived constraints + back-reference to the source data
- *Per-household model* holds the **constraints expressed in cooking terms** (`prefers lower-glycemic dinners`, `avoids X allergen`, `prefers cooked fish`, `priority on folate-rich foods`, `mercury weekly cap`)
- Other household members see the **constraint**, not the source data or the reason
- Back-references to source visible only to the source user (and explicit-consent recipients)

**Three-level sharing model** (per Tension #5 resolution):

- *Strict-per-user* — raw data ownership default
- *Constraint-only* — automatic for meal-planning utility (constraint surfaces to household planner; raw data stays per-user)
- *Mutual-consent* — opt-in for richer visibility between specific members (couple sharing pregnancy data; co-parents sharing kid's allergy panel)

**Reasonable opacity, not information-theoretic.** At the personal-use scale (user + family + friends), the constraint-only abstraction provides reasonable opacity within a household that has high mutual trust. The system does not engineer against careful-observer inference of underlying data from constraint patterns.

## How the model is built

Inputs:

1. **Intake at onboarding** — initial knowledge state (what the user already knows / has tried / cares about)
2. **Periodic check-ins** — revisions to baseline (concepts the user has clearly internalized; preferences that have shifted)
3. **Passive confirmation + semantic feedback** (per [intake-pattern.md Mode 3](intake-pattern.md#mode-3--passive-confirmation--semantic-feedback)) — every cooked-meal feedback loop adds to the household experience memory
4. **Educational delivery events** — when the system surfaces a concept, that's logged in the per-user knowledge model
5. **User-initiated pulls** — when the user actively asks "tell me more about X," strong signal of curiosity; updates curiosity preferences
6. **Inventory state changes** (per [intake-pattern.md inventory awareness layer](intake-pattern.md#inventory-awareness--a-parallel-data-layer)) — what got bought, what got cooked, what's running out

## How the model is used

### Spaced education scheduling

When delivering a concept (via per-meal microlearning, in-context tooltip, or opt-in pull), check the per-user model: when was this concept last delivered? Was engagement high or low? Has the user demonstrated comprehension since? Schedule re-surface at expanding intervals if comprehension is low; let the concept rest if comprehension is high.

### Topic-relevance triggers

When the user picks a recipe with a novel ingredient, the system checks: has this user been exposed to this ingredient before? If no, surface a brief in-context tooltip. When the user reports a feeling after a meal that correlates with a known nutritional mechanism, the system checks: have we explained this mechanism to this user? If no, surface a "here's why that might happen" microlearning chunk on next interaction.

### Horizon-broadening pacing

The system uses the per-user knowledge model to identify which next cuisine / dietary pattern / technique would be a *stretch within reach* (one new skill or one new cuisine, against a base of mastered ones). Per [sweep #12 stretch-recipe ≤1-new-skill rule](../12-skills-by-cuisine/scope.md). The household model informs whether the household has historically said yes or no to similar stretches.

### Conflict resolution context

When household members have conflicting preferences (per [sweep #9](../09-multi-user-household/scope.md) conflict prioritization order), the household knowledge model surfaces precedent — "this household typically resolves preference conflicts by [pattern X]" — to inform without overriding the current decision.

## Stretch-readiness as context-conditional pattern, not scalar

Per [architecture.md C4 Q4.5](architecture.md#c4--multi-modal-recipe-presentation-rendering), the `stretch_readiness_signal` synthesized type tracks **context-conditional selection patterns**, not a single "user is X-confident" scalar score. Dimensions include:

- Skill-level actually-demonstrated through completed recipes
- Skill-level the user *picks* in different contexts (time of day, day of week, life-stage signals like high-stress periods)
- Divergence between picked vs. demonstrated (picks high-skill but doesn't complete vs. picks easier but completes well)

The system **never pre-filters recipe surfaces by perceived skill** — full range always presented; suggestions become context-appropriate based on tracked patterns; user agency preserved per Rule 10.

Schema details for the context-conditional structure deferred to schema-design phase per B4 flag F8 (and now an additional refinement flagged here).

## Partial intake is the default state, not the exception

Per [architecture.md C3 Q3.3](architecture.md#c3--hybrid-administration-ux), the user can pause intake / screener administration at any time and continue using the core app (meal planning, recipes, grocery features) while intake remains incomplete. This means **the system reasons over partial knowledge as the default state, not the exception.**

Implications for the knowledge model:

- Synthesized entries computed from partial atom sets are normal, not edge cases
- Confidence framing per [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) reflects partial knowledge honestly — *"we're working with limited information; here's what we'd refine if we had X"*
- The 3-level user-facing certainty display per [Tension #8](synthesis.md#tension-8--grade-4-level-certainty-vs-consumer-comprehension) skews toward Suggestive until intake matures; this is correct + honest
- Caveat surfacing per C3 Q3.3 happens at the application layer when features would benefit from missing data; the knowledge model itself doesn't gate access — it surfaces what it can and what it can't

## Daily-interaction cadence — clarification

The knowledge model is updated on the natural daily-ish cadence of the user opening the app to plan / cook / shop. **This is NOT the same as a "daily check-in" product** (which is out per [Rule 3](constitutional-rules.md#rule-3--no-food--macro--calorie-logging) and the [product-framing](product-framing.md)). The user is not prompted to log; they are interacting with the meal-planning surface that they would interact with anyway. Knowledge model updates ride on that interaction.

See [synthesis.md Tension #3](synthesis.md#tension-3--spaced-repetition-cadence-vs-no-daily-check-in-rule) for the full distinction.

## What the knowledge model is NOT

- **NOT food-eaten tracking** — that's logging, out per Rule 3
- **NOT macro / calorie computation** — out per Rule 3
- **NOT health surveillance** — wearable signals, lab data, etc. live elsewhere with stricter privacy boundaries (per [Rule 6](constitutional-rules.md#rule-6--health-data-stays-local-where-possible))
- **NOT a behavior-modification engine** — the model informs delivery; it doesn't push the user to engage more or hit metrics
- **NOT shared across households** — strictly per-household; the system does not aggregate household models for "users like you" recommendations without explicit consent

## Bounds + privacy

- Rule 3 (no logging) still applies — the knowledge model tracks system delivery state and household experience memory, not user food intake
- Rule 6 (health data stays local) still applies — health-derived signals in the knowledge model (e.g., condition flags from intake) are processed locally; computed targets only cross to cloud per [epistemic-trail](epistemic-trail.md)
- Rule 8 (epistemic trail) applies — when the model contributes to a user-facing inference, the trail surfaces *what the model knew* and *how it shaped the recommendation*
- Privacy defaults from [sweep #9](../09-multi-user-household/scope.md) govern household-vs-per-user visibility

## Source

User direction (2026-04-29, Stage 2 Tension #3 dialogue):
> "Option D. Blended, please. I think the daily cadence is checking in to make recipes. I think the recipes have to flow in through the application surface. Yeah, the system absolutely maintains a knowledge model of the user and of the household."

## Related

- [synthesis.md Tension #3](synthesis.md#tension-3--spaced-repetition-cadence-vs-no-daily-check-in-rule) — full Stage 2 resolution
- [intake-pattern.md](intake-pattern.md) — three intake modes feed the knowledge model
- [sweep #4 (adaptive intake agent)](../04-adaptive-intake-agent/scope.md) — agent reads + writes knowledge model state
- [sweep #8 (nutrition education delivery)](../08-nutrition-education-delivery/scope.md) — Option D blended delivery uses knowledge model for scheduling
- [sweep #9 (multi-user household)](../09-multi-user-household/scope.md) — household-level model + privacy defaults
- [sweep #12 (skills-by-cuisine)](../12-skills-by-cuisine/scope.md) — stretch-readiness state in the knowledge model
