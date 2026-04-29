# NutriMe — Intake Pattern

> The iterative intake + passive confirmation + semantic feedback model. This is the substitute for daily user-initiated logging — and arguably a more powerful one.

## Three data-collection modes, no traditional logging

NutriMe gathers data about the user through three modes. None of them require the user to open a daily entry form.

### Daily interaction is the natural cadence — and that's NOT a "check-in"

A clarification per [synthesis.md Tension #3](synthesis.md#tension-3--spaced-repetition-cadence-vs-no-daily-check-in-rule):

The "no daily check-in" framing in this project means **no daily prompted tracker-style data entry** ("did you log today," streak punishments, daily badges, fitness-tracker engagement loops). It does NOT mean the user shouldn't open the app daily. **The user IS expected to interact with the app on a roughly-daily cadence** — that's the natural touchpoint for:

- Meal planning ("what am I cooking tonight," "here's tomorrow")
- Cook confirmations + per-meal semantic feedback ([Mode 3](#mode-3--passive-confirmation--semantic-feedback) below)
- Inventory state updates (per [inventory awareness layer](#inventory-awareness--a-parallel-data-layer))
- Education chunks delivered through Option D blended education (per [sweep #8](../08-nutrition-education-delivery/scope.md))
- Knowledge model updates (per [knowledge-model.md](knowledge-model.md))

Recipes *flow into* the user through the application surface; that daily interaction is the carrier for everything else. What's banned is the prompt-the-user-to-log-stuff pattern, not daily app use itself.

## Mode 1 — Initial intake (in-depth)

Comprehensive, clinical-assessment-grade intake at onboarding. Designed against [sweep #3 (clinical nutrition assessment methodology)](../03-clinical-nutrition-assessment/scope.md) standards but delivered consumer-friendly via the [adaptive intake agent](../04-adaptive-intake-agent/scope.md).

Captures:

- Demographics + life stage
- Cultural / religious / regional cuisine background
- Current eating patterns (pattern-based, not recall-based)
- Health history + clinical conditions (gates downstream — see [sweep #10](../10-clinical-condition-gating/scope.md))
- Safety screeners (ED, food security, mood, sleep, stress, substance use, cooking confidence — see [sweep #3 scope](../03-clinical-nutrition-assessment/scope.md))
- Goals + motivations + readiness for change
- Food preferences, dislikes, things-to-try, allergies, intolerances
- Time, budget, kitchen, equipment constraints

### Mode 2 — Periodic check-ins (5–15 minutes)

Light, scheduled re-assessment that revises the baseline. Detects drift, life-stage changes, condition progression, cooking-skill growth, evolving preferences. Frequency TBD (cadence informed by [sweep #4](../04-adaptive-intake-agent/scope.md)).

### Mode 3 — Passive confirmation + semantic feedback

When the system **suggests** a meal and the user confirms they cooked it and ate it, the system captures:

- Confirmation cooked / eaten
- Liked / disliked
- **How it made them feel** — energy, digestion, fullness, mood, sleep that night
- Whether substitutions or more-nutritious variants worked
- **Cooking time accuracy** — was the time estimate right? "this actually took me 45 minutes, not 25" — feeds back to recalibrate future time estimates for this user (and aggregates across users to update recipe metadata)
- Cooking experience — was the technique clear? was the recipe difficulty right? did any step take longer than expected?

This is "passive" because the user never opens a logging form. They confirm a meal that was suggested to them. The data captured is **semantic**, not numeric — feelings and experiences, not grams and calories.

## Inventory awareness — a parallel data layer

Distinct from the three intake modes above, NutriMe maintains a **parallel data layer** for kitchen inventory — what's on hand in the pantry, fridge, and freezer. This is **not** food / macro / calorie logging (which remains out per [Constitutional Rule 3](constitutional-rules.md#rule-3--no-food--macro--calorie-logging)). It's awareness of available ingredients so the system can use what you have, avoid reordering what's there, and minimize waste.

### How inventory data gets in

- **Initial intake at onboarding** — general inventory (loose): what staples you keep, what perishables are in your fridge/freezer right now, what categories you typically stock
- **Ongoing passive observation** — orders confirmed (system knows what you bought), per-meal cook confirmations (system infers what got used)
- **Just-in-time clarification** — when building a specific recipe or shopping list, the system can ask: *"How much rice do you have?"* — only when precision matters for the immediate output

### Quantity precision: loose by default

The system **does not require exact quantities by default.** "I have rice" is enough until a specific recipe or shopping list needs to know "do you have enough rice for this dish." Asking for precision is just-in-time, not at-intake.

### Use-existing-ingredients priority

Inventory awareness drives the meal planner to **prefer recipes that consume what's on hand**. The shopping list is **aware of what's already there** so it doesn't reorder. The implicit goal is **waste reduction** — using up perishables before they spoil, depleting pantry overflow, not buying what's already in the cupboard.

### Why this is not logging

- *Logging (out)*: tracking what you ate, computing calories or macros consumed
- *Inventory (in)*: knowing what's on hand to use in planning future meals

The user never opens a "what did I eat today" form. Inventory tracking is about *forward-looking utility* (what's available for tomorrow's meal), not *backward-looking accounting* (what did I consume yesterday). See [Constitutional Rule 3](constitutional-rules.md#rule-3--no-food--macro--calorie-logging) for the formal distinction.

### Mental-load reduction

This layer materially reduces mental load (per [product-framing.md](product-framing.md#convenience-driven-framing--and-mental-load-reduction)). The user no longer has to remember what's in the fridge before grocery shopping, no longer has to mentally cross-reference recipes against pantry contents, and no longer has to worry about food waste. The system holds that state.

## Why this is more powerful than tracking

- Nobody logs consistently long-term. Adherence to logging apps is famously low.
- Semantic feedback ("that meal made me feel sluggish, the next morning my run was bad") is more useful for personalization than macro counts.
- Passive confirmation removes the cognitive cost of remembering, weighing, and entering food.
- Semantic feedback respects the user's lived experience as evidence — which is appropriate where Tier 1 evidence is silent on the personal-response question.

## Stretch recipe ≤1-new-skill default *(per [synthesis.md Tension #7](synthesis.md#tension-7--stretch-recipe-1-new-skill-rule))*

When the system suggests a recipe intended to broaden the user's horizon (introducing a new cuisine, technique, or skill), the recipe should introduce **at most one new skill** within a base of skills the user has mastered. Recipes introducing multiple new skills at once are reserved for explicit user opt-in.

This is a **system default, not a hard constraint** — per [Rule 10 (user decides with full context)](constitutional-rules.md#rule-10--user-decides-with-full-context), the user can always override. When the user explicitly wants a multi-new-skill stretch (*"I want to try making fresh pasta from scratch this weekend"*), the system surfaces what the multiple new skills are + the elevated failure risk + offers a less-stretch alternative, then proceeds as the user directs.

The "stretch" determination considers both **novelty count** (how many new skills the recipe introduces) and **failure cost** (high-failure-cost techniques like deep-frying, fermentation, laminated doughs get surfaced with explicit framing even when they're "≤1 new skill" by count). Recipe metadata in [sweep #11](../11-recipe-sourcing/scope.md) captures both dimensions.

The user's [knowledge model](knowledge-model.md) tracks which skills are mastered so the system can identify what counts as a stretch for *this* user.

## Iterative horizon-broadening

The intake model is also a **discovery and growth** model. A user starting on chicken nuggets shouldn't be left there. The system progressively introduces:

- More nutritionally complete versions of foods the user already eats (e.g., breaded baked chicken with whole-grain coating + roasted vegetables)
- Adjacent cuisines and techniques, scaled to current cooking skill (see cooking-skills screener in [sweep #3](../03-clinical-nutrition-assessment/scope.md))
- Cultural and dietary patterns from beyond the user's home country (see [sweep #1](../01-international-nutrition-standards/scope.md))

The pace is informed by:

- Stated openness to trying new foods (initial intake)
- Behavioral signal (did the user cook it? did they like it? how did it make them feel?)
- Readiness for change (TTM stage from intake screeners)

## What this is NOT

- Not a calorie / macro / micronutrient tracker
- Not a food diary
- Not a weight tracker
- Not a daily check-in product
- Not a "did you hit your targets" surface

See [product-framing.md](product-framing.md) and [Rule 3 in constitutional-rules.md](constitutional-rules.md#rule-3--no-food--macro--calorie-logging).

## Source

- User reframe (2026-04-28) on iterative intake: "the user doesn't describe themselves just once. I think this is a back-and-forth process to discover continuously what the user likes, broaden their horizons, and incorporate more nutritious, holistic foods over time"
- User reframe (2026-04-28) on periodic check-ins: "I'd rather be more in-depth in the initial intakes on stuff, with periodic check-ins that are 5 to 15 minutes that revise the initial clinical data kind of gathered"
- User reframe (2026-04-28) on passive confirmation + semantic feedback: "It's no logging in terms of user tracking, these things. When we suggest it and the user confirms that they cooked the thing and used the ingredients, we should be logging that and getting feedback on not just how the user liked the food but also how it made them feel"
- User direction (2026-04-29, Stage 2 Tension #1) on inventory awareness layer: "What I do want to put an emphasis on... is making sure we are using what exists and we have some intake process for what exists in a person's pantry, fridge, freezer, etc... it is inventory tracking... We don't necessarily always need to know how much of something we have on hand. That's something we can always reach out and ask the user for clarification when building a recipe list and a shopping list. We should prioritize using existing ingredients and using those up as well."
