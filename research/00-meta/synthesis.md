# NutriMe — Stage 2 Synthesis

> Living document capturing Stage 2 synthesis decisions. As tensions surfaced during research are resolved through dialogue, the resolutions are recorded here with pointers to which docs were updated. The full per-sweep findings remain in each sweep's `## Findings` section; this doc captures the cross-cutting decisions.

## How this doc works

Each resolved tension gets a section with: what surfaced during research, what we resolved it to, why (user direction), and which docs were updated. Roadmap tracks open tensions; this doc tracks resolved ones.

---

## Tension 1 — Mental-load framing supersedes raw-time, plus inventory tracking distinction

### What surfaced

- **Sweep #7** (cooking time + barriers): Bowen et al., reinforced by Wolfson 2016 + Lavelle 2016 — *cognitive overhead* of cooking, not time itself, is the primary barrier for busy adults. The constant deciding (what to make, what to buy, what's in the fridge, what fits, what the household will eat, how long it takes) is what exhausts people.
- **Sweep #13** (grocery infrastructure): "Pantry observed not asked" pattern proposed as a workaround to keep pantry awareness without violating the no-logging rule.

The two surfaced separately but resolve together because they share an underlying insight: removing the deciding/remembering/worrying is more important than removing minutes.

### Resolution

**1. Mental-load framing is co-equal with time-saving in product-framing.md**, not a replacement. Convenience messaging continues to lead with time ("boom, shows up at my door"); mental-load framing makes the deeper value prop explicit underneath.

**2. Convenience driver list expanded** to surface what mental-load research found:
- Removing planning effort
- Removing shopping effort
- Removing **deciding** (formerly "decision fatigue") — sharpened
- Removing **remembering** (what's in the fridge, what's been tried, what household members liked) — new
- Removing **monitoring / worrying** (am I covering nutrition, varying enough, within budget) — new
- Removing skill-acquisition burden

**3. Time stays central as a surface frame.** Recipe time estimates and per-meal time-accuracy feedback are kept — accurate time *reduces* mental load (one less thing to compute). The mental-load framing reinforces, not replaces, the time-accuracy work.

**4. Horizon-broadening pacing is NOT affected by mental-load research.** Per user direction: introduce variety at the iterative pace already established.

**5. Inventory tracking is a distinct data layer, in scope, and explicitly distinguished from food/macro/calorie logging.**

- *Logging (out per Rule 3)*: tracking what you ate; computing calories/macros consumed
- *Inventory (in)*: knowing what's on hand in pantry/fridge/freezer so the system uses what you have, avoids reordering, and minimizes waste

**Inventory mechanics:**
- Initial intake at onboarding (general inventory, loose — what staples + perishables you keep)
- Ongoing maintenance via orders + cook confirmations (passive observation)
- Just-in-time clarification when building a specific recipe / shopping list ("how much rice do you have?")
- Loose quantities by default — exact amounts only asked when they matter for a specific output

**Use-existing-ingredients priority:** meal planning prefers recipes that consume what's on hand; shopping list aware of what's there; waste-reduction is an implicit goal.

This **resolves Tension #3 (pantry "observed not asked") preemptively.** Sweep #13's "observed only" pattern was a workaround to avoid violating Rule 3; with the inventory/logging distinction now clear, *both observed and asked* are fine, with quantities loose unless precision is needed.

### Why (user direction)

User direction (2026-04-29, Stage 2 dialogue):
> "I don't think, though, that it has anything to do with the introduction of new things to avoid overwhelming. What I do want to put an emphasis on, though, is making sure we are using what exists and we have some intake process for what exists in a person's pantry, fridge, freezer, etc. The place I do think this doubles with possibly other apps is in necessarily tracking macros, but it is inventory tracking. Like, what do we have on hand to use in these things? We don't necessarily always need to know how much of something we have on hand. That's something we can always reach out and ask the user for clarification when building a recipe list and a shopping list. We should prioritize using existing ingredients and using those up as well."

### Updates applied

- **product-framing.md** — convenience driver list expanded (deciding/remembering/monitoring); mental-load co-equal frame added; inventory tracking added as a value prop with explicit "uses what you have" framing
- **intake-pattern.md** — new "Inventory awareness — a parallel data layer" section
- **constitutional-rules.md** — Rule 3 (no logging) clarified to specify inventory tracking is *not* food/macro/calorie logging and IS in scope
- **sweep #11 (recipe sourcing)** — recipe selection priority list now includes "uses-existing-ingredients" factor
- **sweep #13 (grocery infrastructure)** — pantry section updated: explicit inventory intake + just-in-time clarification supplement the observed-from-orders pattern
- **roadmap.md** — Tension #1 and Tension #3 both marked resolved in synthesis-phase tensions section

---

## Tension 2 — "Common base + per-plate deltas" evidence basis honesty

### What surfaced

**Sweep #9** (multi-user household): the household conflict-resolution pattern we already chose (one shared meal plan satisfies multiple household members via base + per-plate variations) has **thin** family-meal-intervention research support but **strong** professional-kitchen operational tradition behind it (Escoffier mother sauces, CIA mise en place, institutional foodservice production cooking). Under [Rule 7 (peer-reviewed evidence floor)](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), we need to be honest about what the basis actually is when surfacing this pattern to users.

### Resolution

**1. User-facing transparency: describe the pattern operationally.** When the system surfaces the "common base + per-plate deltas" pattern to users, it names the operational basis honestly — e.g., *"we use the same approach professional kitchens use to serve diverse needs from a single base — mise en place, mother sauces, modular service."* Honest, brief, and frames the system positively (using known-good patterns, not inventing).

**2. Broader principle: operational tradition is a legitimate supplementary evidence basis when peer-reviewed evidence is thin — but must be flagged as such.** Codified as a new section in [evidence-tiers.md](evidence-tiers.md#operational-tradition-as-supplementary-basis), sister concept to audit-as-education. Both handle situations where the standard Tier 1–4 framework needs supplementary surfacing rules to stay honest.

**3. Where this principle applies beyond sweep #9:** sweep #12's professional culinary curricula (CIA, Le Cordon Bleu, Tsuji, etc.) sit in the same epistemic territory — institutional authority, not peer-reviewed nutrition research. The system treats them analogously when surfacing skill knowledge.

**4. Bounds on the principle:** operational tradition supports operational patterns and technique knowledge. **Health claims still require Tier 1/2/3 peer-reviewed support.** Operational tradition does not provide a back door for unsupported health claims.

### Why (user direction)

User direction (2026-04-29, Stage 2 dialogue Tension #2):
> "I think we go with B. I think we stay operationally transparent, so to speak. By cue 2.2, I agree."

Confirming both:
- (b) describe operationally — honest about the operational basis
- yes on adding the operational-tradition-as-legitimate-basis principle as a reusable cross-cutting concept

### Updates applied

- **evidence-tiers.md** — new section "Operational tradition as supplementary basis" added as sister concept to audit-as-education
- **roadmap.md** — Tension #2 marked resolved in synthesis-phase tensions section
- (sweep #9 and sweep #12 already reference operational tradition appropriately in their own findings; the new evidence-tiers.md section gives them a canonical anchor to point to in any future user-facing surface descriptions)

---

## Tension 3 — Spaced-repetition cadence vs. no-daily-check-in rule

### What surfaced

**Sweep #8** (nutrition education delivery) found that spaced repetition is one of the strongest evidence-based patterns for nutrition concept retention. Most spaced-repetition systems use **daily-engagement / streak design** (Duolingo, Anki, Quizlet). The intake-pattern.md "no daily check-in" rule plus broader product-framing rules against tracker-style behavior appeared to rule out streak-driven daily engagement — putting a strong evidence-based education pattern in tension with the product framing.

### Resolution

**1. Reframe: the "no daily check-in" rule was about prompted-tracker-data-entry, NOT about daily app use.** The user *does* open the app daily-ish — that's the natural cadence for meal planning, cook confirmations, semantic feedback, and inventory updates. What's banned is fitness-tracker-style "log what you ate today" prompts, streak punishments, daily badges. Daily app interaction is normal and expected. **This was a docs-precision issue, not an actual rule conflict.**

**2. Option D — blended education delivery.** Three surfaces, each serving a different purpose:
- **(a) Per-meal-attached microlearning** — chunks ride on cook confirmations / Mode 3 feedback events
- **(b) Opt-in "tell me more" pull surface** — depth-seekers can ask; no streaks, no badges, no punishment for not pulling
- **(c) Just-in-time in-context tooltips** — explain why this recipe was suggested, why a substitution was made, why a food made the user feel a certain way

**3. Cadence comes from the meal-planning interaction, not time-based prompts.** Recipes flow *into* the user through the application surface. Education, semantic feedback, inventory updates, knowledge model updates all ride on that natural interaction. The cadence is daily-ish because meal planning is daily-ish — but the system doesn't *prompt for* engagement.

**4. Knowledge model is a first-class system data layer.** Both per-user AND per-household. Tracks: concepts delivered + when, observed engagement, comprehension signals, curiosity preferences, household experience memory, collective decisions. Used for spaced education scheduling, topic-relevance triggers, horizon-broadening pacing, conflict resolution context. New meta doc: [knowledge-model.md](knowledge-model.md).

### Why (user direction)

User direction (2026-04-29, Stage 2 Tension #3 dialogue):
> "Option D. Blended, please. I think the daily cadence is checking in to make recipes. I think the recipes have to flow in through the application surface. Yeah, the system absolutely maintains a knowledge model of the user and of the household."

### Updates applied

- **knowledge-model.md** — new meta doc capturing per-user + per-household knowledge state, how it's built, how it's used, what it isn't, bounds + privacy
- **intake-pattern.md** — new "Daily interaction is the natural cadence — and that's NOT a 'check-in'" section clarifying the distinction
- **product-framing.md** — "It is NOT" line for daily check-in product sharpened (prompted-tracker, not daily app use)
- **sweep #4 (adaptive intake agent)** — note that the agent reads + writes knowledge model state; intake feeds it
- **sweep #8 (nutrition education delivery)** — Option D blended education delivery as the chosen architecture; knowledge model drives scheduling
- **sweep #9 (multi-user household)** — knowledge model is per-user AND per-household with collective experience memory
- **roadmap.md** — Tension #3 marked resolved in synthesis-phase tensions section

---

*Future tensions will be added as resolved.*
