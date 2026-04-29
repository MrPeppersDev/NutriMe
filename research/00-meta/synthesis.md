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

## Tension 4 — Consumer-friendly clinical instrument vs. validity preservation

(Originally queued as Tension #5 in Stage 2 dialogue; takes synthesis-doc slot #4 because the queued Tension #4 — pantry "observed not asked" — was preemptively resolved by Tension #1.)

### What surfaced

**Sweep #3** (clinical nutrition assessment) found that consumer-friendly translations of clinical instruments routinely lose psychometric validity. A 5-question consumer adaptation of PHQ-9 typically doesn't preserve the depression-screening sensitivity/specificity of the validated 9-item version; SCOFF reworded for plainer language often shifts the cut-points; CCSS recast as conversational prompts loses normed reference points.

The tension: NutriMe needs intake to be **clinical-grade in fidelity** (to inform personalization downstream) AND **consumer-friendly in delivery** (so busy working adults complete it without friction). The literature says simplification often pulls these apart.

### Resolution

**1. Hybrid administration (c) as primary path.** Validated instruments delivered through the conversational LLM intake **with items preserved verbatim**. The conversational layer provides:

- Plain-language framing prefaces (*"I'm going to ask you nine questions about your mood over the past couple weeks. These are the same questions a doctor would use..."*) — but the items themselves stay exact
- Transitions between instrument blocks
- Item-level clarification on request (*"What does 'little interest or pleasure' mean here?"* — clarification, not item rewording)
- Pacing and friction-reduction (allow breaks, save state, return)

This is the "consumer-friendly *experience* without changing the *measurement instrument*" pattern.

**2. Conversational elicitation for non-validated-instrument domains (b)** — for things validated instruments don't cover (food relationship beyond TFEQ/IES-2, cuisine preferences, want-to-try, household-level dynamics, cooking literacy beyond CCSS), the conversational elicitation IS the measurement.

**3. Methodology principle — "borrow methodology even when you can't borrow items."** Where validated instruments don't exist for a domain, design the conversational elicitation **by analogy to validated-instrument design principles**, not freestyled:

- Item anchoring (specific time-bounded questions, not abstract "how do you feel about X")
- Frequency vs. severity scales (consistent response option families)
- Behavioral indicators (ask about specific behaviors, not self-perception of trait)
- Response option design (Likert vs. frequency vs. behavioral examples — pick consistently)
- Framing techniques (specificity, time-bounding, context-setting)

The system gets *rigor in how it asks* even when it can't get *validated measurement*.

**4. Provenance tracking in the knowledge model.** Per Rule 8 (epistemic trail), signals are tagged with their source: `validated-instrument` vs. `conversational-elicitation`. Downstream inferences weight differently (validated signals carry sensitivity/specificity profile and confidence intervals; conversational signals carry an honest "this is elicited, not measured" framing). See [knowledge-model.md](knowledge-model.md).

### Why (user direction)

User direction (2026-04-29, Stage 2 Tension #5 in dialogue / synthesis #4):
> "Yeah, C plus B, and where there isn't a validated instrument, then we're leaning on the validated instruments for suggestions and guidance on how to build that workflow and questionnaire."

### Updates applied

- **synthesis.md** — this entry (Tension #4)
- **sweep #3 (clinical nutrition assessment)** — note hybrid administration approach for validated instruments + borrow-methodology principle for non-validated domains
- **sweep #4 (adaptive intake agent)** — adaptive intake architecture must support hybrid administration (verbatim items + conversational framing) AND methodology-borrowing design for non-validated elicitation
- **knowledge-model.md** — signals tagged with provenance (`validated-instrument` vs. `conversational-elicitation`) per Rule 8
- **roadmap.md** — Tension #5 (consumer-friendly clinical instrument) marked resolved

---

## Tension 5 — Cross-sweep wearable-data household sharing gap

(Originally queued as Tension #6 in Stage 2 dialogue.)

### What surfaced

Sweep #6 (wearable & biometric data) characterized data sources and access methods. Sweep #9 (multi-user household) characterized household privacy defaults for preferences, health context, semantic feedback, surface meal feedback. Neither sweep addressed the intersection: **what happens when wearable / biometric / clinical data exists at the household level rather than the per-user level?** Concrete cases: an adult member's CGM data must shape household meal planning without being exposed to other members; a pregnant member's lab work must drive pregnancy-safe planning without disclosing the pregnancy; a child eater's allergy panel must produce allergen-avoidance constraints without exposing the panel.

### Resolution

**1. Abstracted constraint layer.** The system computes user-level *constraints* (lower-glycemic dinners, lower-FODMAP options, allergen avoidance, mercury limits, folate priority, etc.) from each member's raw clinical/wearable/screener data. The household meal planner / shopping list / cook-tonight surfaces consume the **constraints**, not the underlying data. Other household members see the constraint expressed in cooking terms (*"prefers cooked fish"*), not the source data or the reason.

**2. Sharing model — (d) all three:**
- *Strict-per-user* as the data ownership default (each member sees their own raw data only)
- *Constraint-only sharing* automatic for meal-planning utility (the abstracted constraints are shared so the planner works)
- *Mutual-consent sharing* opt-in for richer visibility (couple sharing pregnancy data, parent sharing kid's allergy panel with co-parent, etc.)

This honors the per-user privacy default from sweep #9 while still letting the household meal planner function.

**3. Knowledge model split:**
- *Per-user model* holds raw data + derived constraints + back-reference to source data
- *Per-household model* holds **abstracted constraints sourced from each member** (no raw data; no source disclosure beyond constraint name)
- Back-references to source user visible only to that user (and explicit-consent recipients per #2)

**4. Pregnancy and other sensitive-disclosure edge cases:** the constraint-only abstraction is sufficient. We do NOT add information-theoretic guarantees against careful-observer inference — at the personal-use scale (user + family + friends) this is excessive engineering for a household with high mutual trust. Constraint-only abstraction provides reasonable opacity; that's the bar.

### Why (user direction)

User direction (2026-04-29, Stage 2 Tension #6 in dialogue / synthesis #5):
> "Yeah, agreed. It's 5.1. All three is what I would do. Don't be very careful about any of that. That's fine."

Confirming: abstracted constraint layer (Q5.1), all three sharing levels (Q5.2 (d)), knowledge model split (Q5.3), no over-engineering of pregnancy disclosure protection (Q5.4).

### Updates applied

- **synthesis.md** — this entry (Tension #5)
- **knowledge-model.md** — household-level model section adds the abstracted constraint layer concept; per-user model section adds back-reference visibility note
- **sweep #6 (wearable & biometric data)** — abstracted-constraint-layer pattern noted as the household sharing model for clinical/wearable data
- **sweep #9 (multi-user household)** — explicit answer to the cross-sweep wearable/clinical sharing question added
- **roadmap.md** — Tension #6 (wearable-data household sharing gap) marked resolved

---

## Tension 6 — Food-relationship instrument fragmentation validates iterative-dialog elicitation

(Originally queued as Tension #7 positive finding in Stage 2 dialogue.)

### What surfaced

**Sweep #3** (clinical nutrition assessment) found that the food-relationship measurement space is genuinely fragmented — TFEQ-R18, IES-2, DEBQ, YFAS, others — with no single dominant validated scale. The field itself hasn't converged.

### Resolution

This is a **positive finding** rather than a tension to resolve. The lack of a canonical instrument **validates** the iterative-dialog elicitation approach NutriMe already uses (per [Tension #4 (b) methodology-borrowed conversational elicitation](#tension-4--consumer-friendly-clinical-instrument-vs-validity-preservation)). We don't apologize for not picking one canonical instrument — the field hasn't picked one either, and the conversational elicitation designed by analogy to validated-instrument methodology is the appropriate response when no canonical instrument exists.

### Updates applied

- **synthesis.md** — this entry (Tension #6)
- **roadmap.md** — Tension marked resolved in synthesis-phase tensions section
- (No new doc updates needed — Tension #4's hybrid + methodology-borrowed framing already covers the design implication; this entry just makes it explicit that the design choice is validated by sweep #3's finding)

---

## Tension 7 — Stretch recipe ≤1-new-skill rule

(Originally queued as Tension #8 positive finding in Stage 2 dialogue.)

### What surfaced

**Sweep #12** (skills-by-cuisine) surfaced a concrete pacing constraint: recipes introducing multiple new skills at once risk failure; recipes introducing **exactly one new skill within a base of mastered skills** is the optimal horizon-broadening unit. Useful operational rule for the iterative-broadening pacing.

### Resolution

**1. Codify as a system default** in [intake-pattern.md](intake-pattern.md) alongside iterative horizon-broadening notes. The rule:

> **Stretch recipe ≤1-new-skill default.** When the system suggests a recipe intended to broaden the user's horizon (introducing a new cuisine, technique, or skill), the recipe should introduce **at most one new skill** within a base of skills the user has mastered. Recipes introducing multiple new skills at once are reserved for explicit user opt-in.

**2. System default, not hard constraint** — per [Rule 10 (user decides with full context)](constitutional-rules.md#rule-10--user-decides-with-full-context), the user can override. If the user explicitly wants a multi-new-skill stretch (*"I want to try making fresh pasta from scratch this weekend"*), the system surfaces what the multiple new skills are + the elevated failure risk + offers a less-stretch alternative, then proceeds as the user directs.

**3. Failure-cost dimension in stretch metadata.** Beyond skill-novelty count, recipe metadata also captures **failure cost** (deep-frying, fermentation that ruins if wrong, complex laminated doughs). High-failure-cost stretches get surfaced with explicit framing even when they're "≤1 new skill" by count. The "stretch" decision considers both *novelty count* and *failure cost*. Sweep #11's recipe metadata schema includes both.

### Why (user direction)

User direction (2026-04-29, Stage 2 Tensions #6 + #7 in dialogue):
> "Accepted."

Confirming: codify in intake-pattern.md (Q7.1 (a)), system-default-not-hard-constraint per Rule 10 (Q7.2 first point), failure-cost dimension in metadata alongside novelty count (Q7.2 second point).

### Updates applied

- **synthesis.md** — this entry (Tension #7)
- **intake-pattern.md** — new "Stretch recipe ≤1-new-skill default" section under iterative horizon-broadening
- **sweep #11 (recipe sourcing)** — recipe metadata adds failure-cost dimension alongside the existing stretch-skill marker
- **sweep #12 (skills-by-cuisine)** — note the rule as a system default with user-override + failure-cost framing
- **roadmap.md** — Tension marked resolved in synthesis-phase tensions section

---

## Tension 8 — GRADE 4-level certainty vs. consumer comprehension

(Originally queued as Tension #9 in Stage 2 dialogue.)

### What surfaced

**Sweep #8** (nutrition education delivery) found that consumer comprehension of full GRADE 4-level certainty (High / Moderate / Low / Very Low) is poor. The literature recommends simplifying to 2- or 3-level user-facing display while preserving full GRADE in the audit trail. Plus **van der Bles et al. 2020 (PNAS)** found that numerical uncertainty disclosure preserves trust better than verbal hedging alone.

The interaction with NutriMe's existing 4-tier source framework needed clarification: the source tiers classify *sources*; certainty levels classify *confidence in effect*. They're related but distinct. We need a user-facing simplification on top of the source-tier framework.

### Resolution

**1. Three user-facing certainty levels: Strong / Moderate / Suggestive.**

| Level | Mapping |
|-------|---------|
| Strong | Tier 1 + GRADE high/moderate |
| Moderate | Tier 2 + GRADE moderate, OR Tier 1 + GRADE low |
| Suggestive | Tier 3, OR Tier 2 + GRADE low/very low, OR Tier 4 used as cultural/historical content with audit-as-education framing |

**2. Three display layers used together:**
- Traffic-light icons (green / amber / yellow — NICE-style precedent)
- Hedged language matched to the level (*evidence shows / evidence suggests / early findings hint*)
- Numerical uncertainty disclosure where meaningful (*"8 of 10 systematic reviews agree," "studied in 4 RCTs, n = 2,400," "95% CI [X, Y]"*) — per van der Bles 2020, numerical disclosure preserves trust better than verbal hedging alone; the layers together are best

**3. Source tiers + GRADE preserved in the audit trail.** The user sees the 3-level certainty + hedged language + numerical disclosure on primary surfaces; the full Tier + GRADE breakdown is one click away on demand via the [Rule 8 epistemic trail](epistemic-trail.md). Surface clean, full transparency on demand.

**4. Source tiers and certainty levels are distinct concepts** — the source tiers (1–4) classify *what kind of source supports the claim*; certainty levels (Strong / Moderate / Suggestive) classify *confidence in the effect estimate* given source type plus GRADE-style modifiers (risk of bias, inconsistency, indirectness, imprecision, publication bias). Both feed the trail; both are preserved.

### Why (user direction)

User direction (2026-04-29, Stage 2 Tension #9 in dialogue / synthesis #8):
> "Yeah, this makes sense to me"

Confirming: 3-level certainty display, three-layer visual + textual + numerical pattern, source tiers + GRADE preserved in the audit trail, user-facing certainty display added as a section in evidence-tiers.md.

### Updates applied

- **evidence-tiers.md** — new "User-facing certainty display" section added with three-level table, three-layer display pattern, relation to 4-tier source framework, bounds by other rules
- **synthesis.md** — this entry (Tension #8)
- **roadmap.md** — Tension marked resolved in synthesis-phase tensions section

---

## Tension 9 — Pediatric obesity AAP 2023 + needs-second-pass conditions

(Originally queued as Tension #10 in Stage 2 dialogue.)

### What surfaced

**Sweep #10** (clinical condition gating) flagged eight conditions where refuse / gate / proceed-with-disclaimer assignment isn't obvious because the **literature itself is contested**:

1. Pediatric obesity (AAP 2023 guideline contested)
2. Depression / anxiety boundary (when does screener-positive become "system shouldn't plan")
3. SIBO (small intestinal bacterial overgrowth — diagnostic + treatment contested)
4. NCGS (non-celiac gluten sensitivity — contested entity)
5. Histamine intolerance (limited rigorous evidence)
6. Orthorexia (not in DSM-5; contested as distinct disorder)
7. Long COVID (evolving literature, no nutritional consensus)
8. ASD-without-ARFID (autism-related dietary patterns without ARFID overlap)

These aren't research gaps in NutriMe's work — they're contested in the *underlying clinical literature*. The system can't resolve clinical controversies; it has to decide how to handle them.

### Resolution

**The bounded-role principle applies** — NutriMe is a meal-planning + mental-load-reduction + health-and-wellness-information-surfacing product. **It does not practice medicine, does not commit to per-condition clinical-management positions, does not adjudicate contested clinical literature.** All contested conditions resolve to the same default precisely because the system operates at a level *above* the clinical contestations:

- **Default behavior: proceed-with-disclaimer**
- **Heavy consult-professional surfacing** per [Rule 1](constitutional-rules.md#rule-1--consult-a-professional)
- **Audit-as-education content** that honestly surfaces the contested nature (per [audit-as-education pattern](evidence-tiers.md#audit-as-education-pattern)) — *"the clinical literature on X is genuinely contested — here's why; please work with your care team"*
- **No per-condition special handling** for contested conditions; the meta-default is the resolution

**Specific note for pediatric obesity:** the AAP 2023 guideline involves meds + surgery recommendations for severe pediatric obesity. NutriMe doesn't comment on meds or surgery — it plans meals. For pediatric obesity, the default is: plan family-appropriate meals respecting the child's needs as eater, surface that pediatric obesity care is contested + complex + must involve pediatrician + RD, do not weight system recommendations toward weight outcomes (no calorie cuts, no portion shaming, no aesthetic framing — per [Rule 3](constitutional-rules.md#rule-3--no-food--macro--calorie-logging) and the no-aesthetic-product framing in [product-framing.md](product-framing.md)).

### Why (user direction)

User direction (2026-04-29, Stage 2 Tension #10 in dialogue / synthesis #9):
> "I think option A is the default way to solve these things holistically, as we're just meal planning and helping with mental load around food. We're not doctors. We're not really there to pass medical advice. We're just surfacing information related to health and wellness and food."

### Updates applied

- **synthesis.md** — this entry (Tension #9) capturing the bounded-role framing + the proceed-with-disclaimer + audit-as-education default for contested conditions
- **sweep #10 (clinical condition gating)** — "needs second pass" condition list updated: all eight resolved to the default per this resolution; per-condition special handling removed
- **roadmap.md** — Tension #9 marked resolved; "needs second pass" item under sweep #10 verification removed (resolved by meta-default, not by per-condition assignment)

---

## Tension 10 — Novel-synthesis publication ambition

(Originally queued as Tension #11 in Stage 2 dialogue.)

### What surfaced

**Sweep #4** (adaptive intake agent) identified three plausible novel-synthesis contributions where NutriMe could publish into existing field gaps. Plus **sweep #3** flagged that a consumer-facing GLIM screener doesn't appear to exist (design opportunity); **sweep #7** flagged that NutriMe's own aggregated time-feedback data could fill a recipe-stated-vs-actual gap in the literature.

The question: do we want to *publish into* these gaps as well, or just be aware they exist?

### Resolution

**Active publication ambition** — distribution intent expands from "personal use only" to "personal use primary + active open-source contribution to the field." The documentation discipline NutriMe is already operating at *is* publication-grade; deferring would waste that effort. Designing-for-publication from the start is cheaper than retrofitting a personal-use product later.

**Four current publication targets** — all in:

1. **Open-source nutrition-specific intake chatbot** (sweep #4 gap)
2. **Hybrid LLM + CAT + structured-instrument open agent** (sweep #4 gap — the strongest "novel" claim)
3. **Consumer-facing GLIM screener** (sweep #3 design opportunity — narrow, standalone shippable)
4. **Recipe time-feedback aggregate data** (sweep #7 gap — depends on user base size for statistical meaningfulness)

Plus capacity to add more as they organically emerge.

**What changes:**

- Documentation operates at publication standard from the start (discipline already established; just made explicit)
- Data collection is reproducibility-aware from the start (versioning, instrument tracking, drift detection)
- License + attribution clarity decisions surface earlier in architecture phase
- Code quality bar set with open-source contribution in mind
- New meta doc: [publication-ambitions.md](publication-ambitions.md) tracks targets, methodology principles, process for adding new ones

**What does NOT change:**

- **Bounded-role principle still applies** — we publish what we can defensibly publish; we don't overreach into clinical-claim territory beyond Rule 7
- **Personal-use is still primary** — publication is co-equal, not dominant; the system is useful first
- **Privacy + Rule 6 (health data local)** — published data is anonymized, aggregated, consented; we never publish personally-identifiable data
- **Audit-as-education + epistemic-trail discipline** — applies to publication targets too

### Why (user direction)

User direction (2026-04-29, Stage 2 Tension #11 in dialogue / synthesis #10):
> "Yeah, we're always designing with publication in mind, simply because we don't document to that degree. What's the point of doing it? We want to know; we want to have the data. I think they're all in. Frankly, I don't see why not. Might as well. I don't want to actively defer, though. I do want to have active publication ambitions, so we track and code to that degree."

### Updates applied

- **publication-ambitions.md** — new meta doc capturing the four current targets, methodology principles (reproducibility-aware, license clarity, publication-grade documentation, code quality bar), what publication doesn't change, process for adding new targets
- **product-framing.md** — distribution intent expanded from "personal use only" to "personal use primary + active open-source contribution to the field" with shaping implications listed
- **synthesis.md** — this entry (Tension #10)
- **roadmap.md** — Tension #10 marked resolved; publication targets moved from "Broader-scope future" defer-tracking to active reference under publication-ambitions.md

---

*Future tensions will be added as resolved.*
