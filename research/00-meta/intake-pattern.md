# NutriMe — Intake Pattern

> The iterative intake + passive confirmation + semantic feedback model. This is the substitute for daily user-initiated logging — and arguably a more powerful one.

## Three data-collection modes, no traditional logging

NutriMe gathers data about the user through three modes. None of them require the user to open a daily entry form.

### Mode 1 — Initial intake (in-depth)

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

## Why this is more powerful than tracking

- Nobody logs consistently long-term. Adherence to logging apps is famously low.
- Semantic feedback ("that meal made me feel sluggish, the next morning my run was bad") is more useful for personalization than macro counts.
- Passive confirmation removes the cognitive cost of remembering, weighing, and entering food.
- Semantic feedback respects the user's lived experience as evidence — which is appropriate where Tier 1 evidence is silent on the personal-response question.

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
