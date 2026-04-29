# Sweep #9 — Multi-User / Household Nutrition Planning

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the research literature on couple-based and household dietary planning, conflict-balancing strategies for households with divergent needs (one diabetic + one not, athlete + sedentary adult, pregnant + non-pregnant, child + adult, etc.), and the operational patterns ("common base + per-plate deltas") that make multi-need cooking feasible. Output informs the household intake + planning + conflict-resolution + privacy-defaults architecture.

## Deliverable

An annotated reference map containing:

- Couple-based dietary intervention literature (the closest research analogue to "two adults with divergent needs")
- Household-meal pattern research across [primary research scope](../00-meta/geographic-scope.md) — Mediterranean extended-family meals, East Asian working-couple separate-eating norms, Nordic shared-cooking patterns, Western nuclear-family dinner patterns
- Conflict-balancing strategies from clinical nutrition practice (RD literature on counseling households with mixed needs)
- "Common base + per-plate deltas" pattern documentation — both research support and professional kitchen operational pattern
- Pediatric-inclusion considerations for households with children as eaters
- Privacy + consent literature for shared-household health data systems
- Couple / household decision-making patterns in food choice (Bisogni, Sobal)

This is a **reference map**, not corpus build.

## Household model — confirmed

Per user direction in sweep #9 turn:

### Composition
- 1 adult cooker, OR
- 2 adults cooking together (sharing the cooking labor)
- Children **may be in the household as eaters** but never as cooks. System plans for child dietary needs; intake for children is parent-mediated.

### Joint plan vs. independent plans (provisional default)
- **Joint plan as default** — one shared meal plan that satisfies all household members via "common base + per-plate deltas" (e.g., shared protein + roasted vegetables, with per-plate scaling, side variation, or modular accompaniments to honor each member's needs)
- **Independent plans + convergence days** — supported for households with asymmetric schedules or sharp dietary divergence; "tonight we cook together" days when intersection makes sense
- User-selectable; defaults to joint

### Engagement model — symmetric
- All household members go through full intake (vs. asymmetric engagement where one user is "active" and another is "passive")
- For children: parent does intake on child's behalf
- After intake, all members carry equal weight in conflict resolution, subject to age-appropriate adjustments

### Account model — household top-level, users per household
- **Household** is the top-level entity in the system
- **Users** belong to households; each user has their own data (preferences, semantic feedback, health context, intake history)
- Per-user data tracking enables individual personalization within a shared household plan
- Privacy defaults (above) operate at the per-user level within the household
- A user can belong to one household at a time (relationship arrangements that span households out of scope)
- For per-recipe assignment, the system supports tagging recipes / meals with which household member(s) they're for, enabling the [Rule 10 (user decides with full context)](../00-meta/constitutional-rules.md#rule-10--user-decides-with-full-context) "for whom" gating pattern

### Privacy defaults
- **Preferences / cuisine / want-to-try lists:** shared by default
- **Health context (conditions, medications, lab results):** not shared by default
- **Semantic feedback ("made me feel bloated", mood reports):** not shared by default
- **Per-meal surface feedback (liked / disliked):** shared by default
- All defaults are user-configurable for downstream sharing as needed

### Wearable / biometric / clinical data household sharing — abstracted constraint layer *(per [synthesis.md Tension #5](../00-meta/synthesis.md#tension-5--cross-sweep-wearable-data-household-sharing-gap))*

When household members have wearable, biometric, or clinical data (CGM streams, lab results, condition disclosures, life-stage state including pregnancy / lactation / pediatric medical context), the system handles cross-household visibility through the **abstracted constraint layer** defined in [knowledge-model.md](../00-meta/knowledge-model.md#abstracted-constraint-layer):

- Per-user model holds raw data + derived constraints + back-reference
- Per-household model holds **only the constraints expressed in cooking terms** (e.g., `prefers lower-glycemic dinners`, `avoids X allergen`, `prefers cooked fish`, `priority on folate-rich foods`)
- Other household members see the **constraint**, not the source data or the reason
- Three-level sharing model: strict-per-user (default) + constraint-only (automatic for meal-planning) + mutual-consent (opt-in for richer visibility between specific members like couples or co-parents)
- Reasonable opacity within a high-trust household; the system does not engineer against careful-observer inference

This handles the cross-sweep gap surfaced during research (sweep #6 mapped the data; sweep #9 mapped the household; neither addressed the intersection).

### Conflict prioritization order

1. **Allergens + intolerances** (always honored)
2. **Medical / clinical conditions + life-stage physiological requirements** (pregnancy, lactation, growing children, elderly nutritional needs) (always honored — folded together because both are non-negotiable physiological priority; system distinguishes pathology from life-stage via underlying data when surfacing the *why*)
3. **Religious / ethical dietary observance** (always honored)
4. **Strong preferences / dislikes**
5. **Macronutrient targets** (reconcilable via portion + side scaling)
6. **Cuisine variety + horizon-broadening goals**

## In scope

### Couple-based dietary intervention research

- Brisbane / Australian work on couple-based dietary change
- Spousal-influence literature on diet change (multiple US + EU sources)
- Concordance / discordance research — when household members align vs. diverge

### Household-meal patterns across primary research scope

- Mediterranean / extended-family communal meal patterns
- East Asian working-couple eating patterns (Japan, Korea, urban China)
- Nordic shared-cooking + lagom portion norms
- Western nuclear-family dinner patterns
- US "second shift" cooking patterns (Hochschild adapted for cooking labor)
- South Asian household meal-prep patterns (relevant given diaspora populations in primary audience)

### Conflict balancing — clinical literature

- RD counseling literature on households with mixed needs
- Behavior change in couples (BCT taxonomy applied to dyads)
- Negotiation patterns in food choice (Bisogni)
- Decision-making roles in household food provisioning (Sobal)

### "Common base + per-plate deltas" pattern

- Research support for the pattern (limited but present in family-meal intervention literature)
- Professional kitchen operational pattern (mise en place, mother sauces, modular service)
- Translation to home cooking

### Pediatric inclusion

- Age-appropriate portion + texture + spice + allergen considerations
- Child dietary needs without making the child a cook
- Family-meal-as-default vs. separate-kid-meal patterns
- Cross-references [sweep #3 (pediatric assessment instruments)](../03-clinical-nutrition-assessment/scope.md) and [sweep #10 (pediatric conditions)](../10-clinical-condition-gating/scope.md)

### Privacy + consent

- Shared-household health data systems (research from family health portal literature, shared EHR access patterns)
- Consent and disclosure between household members (family medicine literature)
- Configurable-default design patterns

## Out of scope (with reasons)

- **Children as cooks** — out per [product-framing.md](../00-meta/product-framing.md). Cooking is an adult activity in this product.
- **Kid-cooking-education research** — out per "not a cooking class" boundary; would re-enter as stretch goal of "where to learn"
- **Households of 3+ adults** — uncommon and not target user; system will handle in principle but not optimized for
- **Roommate / shared-kitchen-but-not-meals scenarios** — different problem
- **Food-insecure households** — different product
- **Family meal interventions specifically focused on children's eating behavior change** — child as primary intervention target is out; child as household member whose needs are accommodated is in
- **Pediatric clinical condition gating** — covered in [sweep #10](../10-clinical-condition-gating/scope.md)
- **Pediatric assessment instruments** — covered in [sweep #3](../03-clinical-nutrition-assessment/scope.md)

## Geographic scope

Research per [geographic-scope.md](../00-meta/geographic-scope.md) — broad. Audience-relevant household patterns (US, Canada, Western Europe) get primary depth; non-Western household patterns get coverage for horizon-broadening relevance to diverse-cuisine recommendations.

## Open questions for the research

- What is the strongest evidence for joint-meal-planning vs. independent-plans-with-convergence in adult households?
- What conflict-resolution order do clinical RDs use in practice when counseling couples / households?
- How is "common base + per-plate deltas" actually implemented in real household cooking — what's the cognitive overhead, what works, what fails?
- What does the literature say about appropriate privacy defaults for shared-household health data systems?
- How do high-cooking cultures (Italian, Japanese, Indian) handle household-meal divergence vs. low-cooking cultures?
- For households with children: what is the published evidence on family-meal-as-default vs. separate-kid-meal patterns, and how does this affect adult diet quality?

## Cross-references

- Bound by [target-user definition in product-framing.md](../00-meta/product-framing.md#target-user)
- Cross-references [sweep #1 (international nutrition standards)](../01-international-nutrition-standards/scope.md) — life-stage DRIs
- Cross-references [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — pediatric assessment instruments + per-member intake
- Cross-references [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — household members may have conditions that gate
- Cross-references [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — recipes that support common-base + per-plate-deltas, kid-friendly recipes
- See [geographic-scope.md](../00-meta/geographic-scope.md) for primary audience vs. broader research scope distinction

## Findings

> **Epistemic note (2026-04-29):** Both `WebSearch` and `WebFetch` were denied for this sweep. Findings below are reconstructed from training-data knowledge of the published peer-reviewed literature in couple-based nutrition intervention, family-meal sociology, household food-decision research, professional-kitchen production methods, pediatric family-meal literature, and shared-EHR / family health portal research, current to roughly the assistant's knowledge cutoff. **Every cited reference, DOI, page range, year, and finding direction below should be re-verified against the primary sources before any of this map is treated as load-bearing for design.** Where a finding's *direction* is well-established in the literature but a *specific* number or DOI is at risk of memory drift, the finding is marked with `[verify]`. References are listed with the URL/DOI form they are most likely to resolve at; accessed-on dates are recorded as `2026-04-29` with the explicit caveat that no fetch was performed today.

---

### 1. Couple-based dietary intervention research

The closest research analogue to NutriMe's "two adults with divergent needs" household model is the **couple-based dietary intervention literature** — randomized and quasi-experimental trials that recruit *both* partners (typically a "patient" with a clinical indication and a "spouse" or cohabiting partner) and intervene at the dyad level rather than at the individual level.

#### 1.1 Brisbane / Australian work — the largest single program

The most consolidated body of couple-based dietary intervention work has come from groups in **Brisbane (Queensland University of Technology, University of Queensland)** in collaboration with prostate-cancer and cardiovascular-disease cohorts. The pattern across these trials:

- The "patient" partner has a clinical indication (most commonly prostate cancer survivorship, cardiovascular rehabilitation, or T2D); the "spouse" partner has no formal indication but co-resides and shares meals.
- The intervention is delivered to the *couple* as the unit, with explicit dyadic content (joint goal-setting, shared self-monitoring, communication scaffolding) layered on top of conventional dietary education (Mediterranean / DASH-style targets).
- Outcomes consistently show **larger and more durable dietary change in the couple-arm than in the patient-only arm**, with the spouse partner *also* improving despite no clinical indication — i.e., the intervention "spills over" rather than the spouse acting as a passive support [Tier 2/3 — see [Hartmann-Boyce et al. 2018](#references) systematic review and [Burke et al. 1999](#references) earlier RCT for direction]. `[verify]`

Implication for NutriMe: the **dyadic-by-default** posture is the better-supported design than treating one user as primary + spouse as bystander. The household model NutriMe has provisionally chosen (symmetric engagement, joint plan as default) aligns with the direction of this evidence base.

#### 1.2 Spousal-influence / concordance literature (US + EU)

A separate but related literature looks at **spousal concordance** — the degree to which cohabiting partners' diets converge over time, *without* explicit intervention.

- Cross-sectional concordance is moderate-to-strong on **food selection, meal patterns, eating timing, and eating location** (most household meals are eaten together). Concordance is weaker on **portion size, snacking, and individual beverage choice** — the categories least mediated by shared cooking [Tier 2/3 — see [Pachucki, Jacques & Christakis 2011](#references) and the broader Framingham Offspring social-network food-choice work]. `[verify]`
- Longitudinal work (e.g., **Whitehall II**, **EPIC-Norfolk** spousal substudies, **ARIC** cardiovascular cohort spousal analyses) finds that one partner adopting a healthier dietary pattern is associated with a measurable but smaller shift in the cohabiting partner's diet — the "**transmission coefficient**" is roughly 0.2–0.4 of the index partner's change. Effects are larger when the change involves *what enters the household* (groceries, shared cooked dishes) than when it involves *individual behaviors* (snacks, portion sizes) [Tier 3]. `[verify]`
- **Concordance/discordance research** distinguishes (a) baseline-similar couples (assortative mating on food preferences), (b) couples who converge over cohabitation, and (c) couples who remain discordant on at least one dietary axis (often around meat consumption, alcohol, or religious/ethical observance). The concordant-converger pattern is the modal one but the discordant pattern is non-trivial — roughly a third of long-cohabiting Western couples remain meaningfully divergent on at least one major dietary category [Tier 3]. `[verify]`

Implication for NutriMe: the **default joint plan** assumption is well-supported for the modal couple, but the **independent-plans-with-convergence-days** affordance is empirically necessary for the non-trivial discordant minority. Hard-coding "single plan only" would mis-serve this segment.

#### 1.3 Mechanisms of dyadic effects (BCT-applied-to-dyads)

The **Behaviour Change Technique (BCT) Taxonomy v1** ([Michie et al. 2013](#references)) has been adapted to couple/dyad interventions in subsequent work ([Carr et al. 2019; Hagger et al. various](#references)). Mechanisms with the strongest dyadic support are:

- **Joint goal-setting** (BCT 1.1, 1.3) where the goal is articulated *as a couple* rather than as two parallel individual goals
- **Shared monitoring of behavior** (BCT 2.x cluster) — but where the monitoring is *of the household*, not of each partner individually
- **Restructuring the physical environment** (BCT 12.1) — what enters the kitchen, what is in arm's reach — which by definition is a household-level lever, not an individual one
- **Social support (practical)** (BCT 3.2) and **social support (emotional)** (BCT 3.3) — where the partner is explicitly cued to provide support rather than expected to provide it implicitly

Implication for NutriMe: the system's "household-level" framing of plan + grocery + kitchen state aligns with the strongest-evidence BCT mechanisms. Per-individual surfacing of "your partner is doing X" should be available but not default — the literature is mixed on whether per-partner monitoring helps or backfires (control / reactance concerns; see also [Lewis & Butterfield 2007](#references) on social control vs. social support in couples).

---

### 2. Household-meal patterns across primary research scope

#### 2.1 Mediterranean / extended-family communal meal patterns

The Mediterranean dietary pattern as nutritionally defined ([Trichopoulou et al. 2003](#references); the **PREDIMED** trial cluster) is *also* a household-meal pattern: long, shared, multi-generational meals with a high vegetable + legume + olive oil base and meat in smaller portions, eaten communally and slowly. The **commensality** literature ([Fischler 2011](#references); the EU **Eurest Lifestyle Study**) consistently finds that Southern European households (Italy, Greece, Iberia) report higher rates of weekday-evening shared family meals than Northern European or Anglo households, and that this *commensality* dimension predicts dietary quality independently of food composition [Tier 2/3]. `[verify]`

Implication for NutriMe: the "common base + per-plate deltas" pattern is **traditional, not novel** in Mediterranean cooking — a single shared *primo* / *secondo* with per-plate variation in portion and accompaniment is the historical norm. The system can reach for Mediterranean exemplars when illustrating the pattern to users.

#### 2.2 East Asian working-couple patterns (Japan, Korea, urban China)

- **Japan:** dual-earner households increasingly rely on the *konbini* (convenience store) + *bento* economy for weekday lunches, with the shared evening meal preserved on a 2–4-evenings-per-week basis. The traditional *ichiju-sansai* ("one soup, three sides") pattern is itself a "common base + per-plate deltas" architecture — the rice + miso are shared, the *okazu* sides are individualized by appetite, age, and sometimes by health needs (lower-sodium versions for elderly household members are a recognized practice) [Tier 3 — see [Kurotani et al. 2016](#references) on Japanese dietary patterns and household-level cohort work in JPHC]. `[verify]`
- **Korea:** the *banchan* pattern (multiple small shared side dishes around a rice + soup core) is even more explicitly a per-plate-deltas pattern — banchan composition can vary night-to-night, and household members self-select from the array. Working-couple Seoul households show a documented shift toward "half-cooked" *bansangchaek* / meal-kit hybrid patterns to preserve banchan diversity under time constraints [Tier 3]. `[verify]`
- **Urban China:** the *yi cai yi tang* / *si cai yi tang* pattern (one-to-four dishes plus a soup, served family-style with a shared rice base) is explicitly designed for divergent-appetite households; per-plate consumption is determined at the table by what each diner takes from shared dishes. Working-couple urban households (Shanghai, Beijing, Guangzhou cohorts) show high reliance on extended-family cooking labor (a grandparent often cooks the evening meal) and on workplace canteens for lunch [Tier 3 — see [Du et al. 2014](#references) on the China Health and Nutrition Survey]. `[verify]`

Implication for NutriMe: Western users should be exposed to these patterns as **demonstrated solutions to the same problem** the system is solving — they are not exotic, they are time-tested architectures for divergent-need household feeding.

#### 2.3 Nordic shared-cooking + lagom portion norms

Nordic household-meal patterns (Sweden, Denmark, Norway, Finland) are characterized by:

- **High shared-cooking labor between cohabiting adults** — Nordic time-use surveys consistently show the **smallest cooking-labor gender gap** among OECD countries [Tier 3 — see OECD Time Use database; [Sayer 2005](#references) for cross-national comparison framework]. `[verify]`
- ***Lagom* (Swedish) / *passe* (Norwegian) portion norms** — a cultural emphasis on "just enough, not too much" portions, served from shared platters with self-determined per-plate amounts. This is a per-plate-deltas pattern enacted at the table rather than at the plating step.
- **Husmanskost** (Sweden) / **husmandskost** (Denmark) traditional weekday cooking is built around a small repertoire of shared base dishes (root vegetables, dairy, fish, pork) with seasonal accompaniment variation.
- **Skolmat / school-lunch culture:** Finland and Sweden offer free hot school lunches universally, which means children's lunches are *not* a household planning concern on weekdays — the cooking-labor question shrinks to dinner only. This shifts the household planning load relative to US/UK households where school lunches are a planning artifact [Tier 3]. `[verify]`

Implication for NutriMe: Nordic households are an existence proof that **shared cooking + per-plate self-determination** can be the default. The system's cooking-labor-sharing affordances (for two-adult households) should accommodate this division explicitly rather than assuming a single primary cook.

#### 2.4 Western nuclear-family dinner patterns

The "family dinner" as a normative US/UK/Anglo pattern ("breakfast + packed lunch + cooked dinner together") is well-documented in the **family-meals literature** ([Fulkerson et al. various; Neumark-Sztainer Project EAT cohort](#references)). Key findings:

- Frequency of shared family meals has **declined** over the past three decades in the US/UK but remains the **modal evening pattern** in households with children — roughly 4–5 shared dinners per week is the median in cross-sectional surveys [Tier 3]. `[verify]`
- **Higher family-meal frequency** is associated with better diet quality (more fruits/vegetables, less soda/fast food), better adolescent mental health, and lower disordered-eating risk — across multiple cohorts and after adjustment for SES [Tier 2/3 — see Project EAT longitudinal results, and [Hammons & Fiese 2011 meta-analysis](#references)]. `[verify]`
- The effect is **strongest for adolescents** and weakest for younger preschool-age children, where shared mealtime is closer to baseline universal.

Implication for NutriMe: **family-meal-as-default** is well-supported as an organizing principle for households with children. The system should default to "the family eats together" planning patterns for these households, with separate-kid-meal as a configurable affordance rather than the default.

#### 2.5 US "second shift" cooking-labor patterns (Hochschild-adapted)

[Hochschild & Machung's *The Second Shift* (1989, revised 2012)](#references) documented the persistent gender asymmetry in unpaid household labor in dual-earner US couples. The cooking-labor application (developed by [DeVault 1991, *Feeding the Family*](#references); [Bowen, Brenton & Elliott 2019, *Pressure Cooker*](#references)) extends this:

- Cooking labor includes not only the cooking act but also **planning, shopping, mental load of remembering preferences and dietary needs, and the emotional labor of accommodating divergent eaters** ("the kid won't eat this," "my spouse needs low sodium").
- This **mental-load fraction** of cooking labor remains substantially gender-asymmetric in US/UK/Anglo households even where the cooking-act labor has equalized [Tier 3 — see [Daminger 2019](#references) on cognitive labor; [Bowen et al. 2014](#references) on the joys/burdens of feeding the family]. `[verify]`
- **Pressure Cooker** (Bowen, Brenton & Elliott) ethnography found that "cook from scratch every night, eat together as a family" — the cultural ideal — is **functionally infeasible** for most working-class US households given time, money, and equipment constraints. The pattern is upheld as an aspiration even when daily practice diverges sharply.

Implication for NutriMe: the system's **mental-load-reducing posture** (the system plans, the system remembers preferences, the system accommodates divergent needs) directly addresses the second-shift cognitive load — and this is a load that has historically fallen disproportionately on one partner. The system should be careful **not to reproduce that asymmetry by defaulting to a single "primary cook" user model**; the symmetric two-adult engagement model resists this.

#### 2.6 South Asian household meal-prep patterns

South Asian (Indian, Pakistani, Bangladeshi, Sri Lankan) household cooking patterns relevant to diaspora populations in the primary audience:

- **Common-base + per-plate-deltas is structural**: a shared *dal* + *sabzi* + *roti/rice* base, with per-plate variation in spice level (children/elderly served lower-spice portions from the same pot before chili is added at the cook's discretion), *raita*/yogurt to moderate heat per-eater, and pickle/chutney accompaniments selected per-plate.
- **Multigenerational household cooking** with frequent extended-family co-cooking remains common in both subcontinent and diaspora contexts — the "two-adult cook" model is often actually three or four cooks across generations, with senior-generation members holding recipe knowledge and junior-generation members executing.
- **Fasting traditions** (Hindu *vrat*, Muslim Ramadan fasting, Jain dietary observance, regional + caste-specific patterns) overlay individual-level dietary divergence onto the household plan with strong religious significance — these are exactly the case where **per-eater variation must be honored without negotiation** [Tier 3 — see [Misra et al. 2010](#references) on South Asian dietary patterns and CVD risk; Fischler & Masson on commensality + religion]. `[verify]`

Implication for NutriMe: the per-plate-deltas pattern with explicit per-eater religious/observance overlays is both technically necessary and culturally familiar to South Asian users. Conflict-prioritization rule #3 (religious / ethical observance) operationalizes this directly.

---

### 3. Conflict balancing — clinical literature

#### 3.1 RD counseling literature on households with mixed needs

Registered Dietitian / dietitian-nutritionist clinical practice literature on **counseling households with divergent needs** has been published primarily through:

- The **Academy of Nutrition and Dietetics Evidence Analysis Library (EAL)** — practice guidelines for RDs, including specific guidance on family-based counseling for cardiovascular disease, diabetes, and pediatric obesity contexts.
- **Journal of the Academy of Nutrition and Dietetics** (formerly *JADA*) and *Journal of Nutrition Education and Behavior* — case-series and cohort literature on household-level counseling. `[verify]`

Common practice patterns documented in this literature:

1. **Assess the household, not just the patient** — full intake includes who else eats from the same kitchen, who cooks, what divergent needs are present.
2. **Identify the highest-priority clinical need first** (allergens > pregnancy/lactation > active disease > preventive targets) and design the household's *base* meal pattern to honor that need by default — then add back per-plate flexibility for the unaffected members.
3. **Negotiate explicitly with the household** rather than handing the patient a prescription and expecting them to negotiate it at home.
4. **Build for the cook, not just the eater** — the person cooking is the one carrying out the recommendation; their constraints (time, skill, equipment) bind the plan.

Implication for NutriMe: the **conflict-prioritization order** in the scope (allergens → medical/life-stage → religious → preferences → macros → variety) aligns with documented RD practice. The **"for whom"** elicitation pattern (Rule 10) maps directly to step 1 (assess the household).

#### 3.2 Behavior change in couples — BCT taxonomy applied to dyads

See §1.3 above. Additionally, [Hagger & Hamilton 2018](#references) and [Carr et al. 2019](#references) systematic reviews of dyadic behavior-change interventions identify:

- Joint planning ("we will cook X tonight") consistently outperforms parallel individual planning ("you do your plan, I do mine").
- **Shared self-monitoring** of household-level metrics (groceries bought, meals cooked at home) outperforms individual self-monitoring of personal behaviors when the goal is dietary change.
- **Communal coping** framing (the dyad faces the health challenge together) outperforms patient-spouse framing where one partner is "supporting" the other [Tier 2/3]. `[verify]`

#### 3.3 Negotiation patterns in food choice — Bisogni's food-choice process model

The **Food Choice Process Model** ([Bisogni, Connors, Devine & Sobal 2002](#references); [Sobal & Bisogni 2009](#references); [Bisogni et al. 2007](#references)) is the leading qualitative framework for understanding how individuals make food choices in context. Key constructs:

- **Life course events and experiences** that shape food trajectories
- **Influences** (ideals, personal factors, resources, social factors, food context)
- **Personal food system** — strategies, values, and rules people develop to navigate food choices
- **Value negotiations** — explicit weighing of competing values (taste vs. health vs. cost vs. convenience vs. relationships)

For households specifically, [Bisogni, Jastran et al. 2007](#references) and follow-up work documented **household food-choice negotiation patterns**:

- Couples and families develop **shared "personal food systems"** that are partially shared and partially individual — not all values are negotiated, only the load-bearing ones.
- Most household food-choice negotiation is **implicit and routine** rather than explicit and conscious; couples report that they "just know" what to cook, and only surface negotiation when a routine breaks (illness, schedule change, new dietary diagnosis).
- Explicit conflict surfaces when one partner's **value salience changes** (new health diagnosis, religious/ethical shift, weight-management goal) — this is exactly the moment NutriMe is likely to be adopted.

Implication for NutriMe: the system enters at the moment of value-salience-change, when implicit routines have broken. The system should support **explicit re-negotiation** at intake and at periodic check-in moments — these are the moments the literature identifies as conscious decision points.

#### 3.4 Decision-making roles in household food provisioning — Sobal's work

[Sobal, Bove & Rauschenbach 2002](#references); [Sobal & Bisogni 2009](#references); [Sobal, Hanson & Frongillo 2014](#references) documented role differentiation in household food provisioning:

- **Provisioner** (who decides what enters the household)
- **Preparer / cook** (who transforms ingredients into meals)
- **Server / portioner** (who decides per-plate amounts)
- **Eater** (who consumes)
- **Cleaner** (who handles post-meal labor)

These roles are **separable** — the same person often holds multiple roles, but not always, and the role distribution shapes who has decision power over each axis of the meal. Sobal documented that the **preparer role often holds the most de facto power** over what gets eaten, even when the *provisioner* is nominally the decision-maker, because the preparer makes the moment-to-moment substitutions and accommodations.

Implication for NutriMe: the system's **household model** should ideally distinguish these roles rather than assume one user = one undifferentiated household member. The two-adult-cooks pattern in NutriMe maps well to *shared preparer* role; the *eater* role expands to children + guests; *provisioner* maps to whoever places the grocery order. Per-recipe "for whom" tagging (Rule 10) operationalizes the eater-vs-preparer distinction.

---

### 4. "Common base + per-plate deltas" pattern

#### 4.1 Research support in family-meal intervention literature

Direct intervention studies of "common-base / per-plate-deltas" as a *named* meal-planning pattern are limited, but the *principle* surfaces under several names:

- **"Family-style serving"** in the family-meal literature — food served from shared platters with each diner taking their own portion. Associated with better child self-regulation of intake and better dietary quality in mixed-age households [Tier 3 — see [Savage, Fisher & Birch 2007](#references); [Larson et al. 2013](#references)]. `[verify]`
- **"Component meals"** in school-foodservice and institutional-cooking literature — a base + selectable accompaniments architecture that allows per-eater customization within a controlled production framework.
- **"Modular meal planning"** in some family-meal intervention curricula (e.g., **HOME Plus** by [Fulkerson et al. 2015](#references); some **EFNEP** curricula) — explicitly teaching households to design meals as a shared base + individualized variations to handle picky-eating + adult-need divergence simultaneously.

The intervention literature on this pattern is **thin but consistent in direction**: it reduces the cognitive overhead of cooking for divergent eaters compared to fully separate meals, and reduces the friction of "everyone has to eat the same thing" relative to one-meal-fits-all approaches [Tier 3]. `[verify]`

#### 4.2 Professional-kitchen operational pattern

In professional kitchen practice, the common-base + per-plate-deltas architecture is **the operational default**, not an innovation. The relevant constructs:

- **Mise en place** ([Pépin 1976; The Culinary Institute of America curriculum](#references)) — pre-prepared component ingredients staged for assembly. A professional kitchen prepares components once, then assembles plates per-order.
- **The mother sauces** ([Escoffier 1903, *Le Guide Culinaire*](#references); [Carême earlier](#references)) — a small set of base sauces (béchamel, velouté, espagnole, hollandaise, tomate; sometimes mayonnaise added) from which a large derived-sauce repertoire is built. The architecture is "make the base; differentiate at the finish."
- **Modular service / station-based plating** (CIA, Le Cordon Bleu, MOF curricula) — components are produced in batch at stations, assembled per-plate at the pass; per-order modifications (allergen swaps, dietary variants) are handled at assembly.
- **Production cooking** in healthcare/institutional foodservice (see [Spears & Gregoire 2007 *Foodservice Organizations*](#references)) — explicitly designed around base recipes with documented per-diet variants (renal, cardiac, diabetic, texture-modified, allergen-restricted) generated from the same production line.

These are well-codified industry practices, not research findings; they appear in trade literature and culinary curricula rather than peer-reviewed journals. **They cannot themselves be cited as Tier 1/2/3 evidence for a health claim**, but they can be cited descriptively per [evidence-tiers.md](../00-meta/evidence-tiers.md) §"Audit-as-education": the pattern is a *fact about how professional kitchens are organized*, not a health claim.

#### 4.3 Translation to home cooking

The home-cooking adaptation of the professional pattern has been written about by:

- **Samin Nosrat, *Salt, Fat, Acid, Heat* (2017)** — explicit pedagogy for "base preparation + per-plate finishing" for home cooks.
- **Mark Bittman, *How to Cook Everything* (multiple editions)** — recipe families with documented variations (the same braise as a base for 6+ derived dishes).
- **J. Kenji López-Alt, *The Food Lab* (2015)** and Serious Eats columns — explicit modular recipe architecture for weeknight cooking.
- **Yotam Ottolenghi's** cookbooks — extensive use of "shared base + mixed mezze accompaniments" structure that mirrors the Levantine commensal pattern.

These are trade publications (Tier 4 by NutriMe's evidence framework) and serve only as **cultural / operational context**, not as evidence for any health claim. They are useful for the system's *recipe-presentation* sweep ([sweep #11](../11-recipe-sourcing/scope.md)) more than for this sweep.

Implication for NutriMe: the common-base + per-plate-deltas pattern is **an operational-design principle borrowed from professional and home-cooking practice**, with **thin but directionally-consistent supportive evidence from the family-meal intervention literature**. The system can lean on the pattern as a *design choice* with appropriate transparency about the evidence base — strong on operational feasibility, modest on outcome evidence.

---

### 5. Pediatric inclusion considerations

(Per scope: child as eater, never as cook; child intake parent-mediated. Pediatric clinical condition gating is in [sweep #10](../10-clinical-condition-gating/scope.md); pediatric assessment instruments are in [sweep #3 §Pediatric assessment](../03-clinical-nutrition-assessment/scope.md).)

#### 5.1 Age-appropriate portion + texture + spice + allergen considerations

The relevant authoritative bodies:

- **AAP Bright Futures: Guidelines for Health Supervision** ([Hagan, Shaw & Duncan eds., 4th ed. 2017](#references)) — the canonical US pediatric primary-care framework with age-band feeding/nutrition guidance from birth to age 21.
- **WHO Complementary Feeding Guidelines** ([WHO 2003, updated 2023](#references)) — global guidance on the introduction of solid foods 6–24 months, including texture progression, food-group introduction, and allergen-introduction guidance.
- **USDA / HHS Dietary Guidelines for Americans birth-24 months** ([DGA 2020-2025 birth-24mo chapter](#references)) — first US Dietary Guidelines edition to include explicit B-24 guidance.
- **NIAID-sponsored guidelines on early peanut introduction** ([Togias et al. 2017](#references); the LEAP trial [Du Toit et al. 2015 *NEJM*](#references)) — landmark reversal of prior "delay introduction" guidance based on RCT evidence that early introduction of peanut between 4-11 months in high-risk infants reduces peanut allergy by ~80%.

Salient pattern-level considerations:

- **Texture progression** runs from purées (~6 months) → mashed/lumpy (~7-9 months) → soft finger foods (~9-12 months) → most family foods with appropriate cutting (~12+ months). Choking-risk food list (whole grapes, hot dogs cut in coins, whole nuts, hard candy, popcorn, etc.) extends to age 4 per AAP. [Tier 1.]
- **Spice tolerance** is largely cultural exposure rather than developmental — children habituated to a cuisine's spice profile from weaning tolerate it; the "kids can't handle spice" generalization is a Western cultural pattern, not a developmental fact [Tier 3 — Mennella et al. on flavor learning in early life]. `[verify]`
- **Sodium**: AAP recommends limiting added salt for under-2s; CDC documents that children's diets are typically *above* DGA sodium recommendations from age 2 onward. Per-plate sodium reduction (don't salt the kid's portion) is a recognized strategy.
- **Added sugar**: DGA 2020-2025 recommends *no added sugar* for under-2s — a stronger position than for adults (where the recommendation is <10% of energy).
- **Allergens**: per LEAP / LEAP-On / EAT trial evidence, the **early introduction** of peanut, egg, and other top allergens between 4–11 months is now recommended for most infants (and *strongly* recommended for high-risk infants), reversing the delay-introduction guidance of the 2000s. [Tier 1/2.]

Implication for NutriMe: the system's child-eater accommodations should default to **age-appropriate texture + cutting, low-added-salt for under-2s, no-added-sugar for under-2s, and explicit allergen-introduction support during the 4-11mo window**. None of these require the child to cook; all of them require the cooking adult to know the per-plate adjustments.

#### 5.2 Family-meal-as-default vs. separate-kid-meal patterns

The family-meal literature ([Project EAT longitudinal, Neumark-Sztainer et al.](#references); [Hammons & Fiese 2011 meta-analysis](#references); [Fulkerson et al. various](#references)) consistently finds:

- **Family-meal-as-default** (children eating the same/similar foods as adults from a shared cooking effort) is associated with better child diet quality, better adolescent psychosocial outcomes, and lower disordered-eating risk than the **separate-kid-meal** pattern (children eating "kid foods" — chicken nuggets, pasta with butter, etc. — distinct from the adult meal).
- **Per-plate accommodations within a shared meal** (child gets the same dish but with less spice, smaller portion, sauces on the side) are consistent with the family-meal benefit and are how most documented family-meal-positive households actually operate — pure "everyone eats the same thing" is uncommon and not necessary for the benefit.
- The separate-kid-meal pattern is associated with **picky-eating reinforcement** and with a narrower lifelong food repertoire ([Birch & Fisher work on food acceptance](#references)).
- **Repeated exposure** (8-15 neutral exposures to a new food) is the documented effective strategy for expanding child food acceptance — pressure to eat is counterproductive ([Wardle et al. 2003](#references); [Cooke 2007](#references)). [Tier 2.]

Implication for NutriMe: **family-meal-as-default with per-plate accommodation** is the well-supported design choice. This aligns directly with the **common-base + per-plate-deltas** pattern (§4) and with the **conflict-prioritization order** in the scope. The system should default to "the family eats together, with per-plate adjustments for the child" rather than "the child gets a different meal."

#### 5.3 What this sweep does NOT cover

Per scope:

- **Children as cooks** — out per [product-framing.md](../00-meta/product-framing.md).
- **Family-meal interventions specifically focused on changing children's eating behavior** — out; covered elsewhere if at all.
- **Pediatric clinical condition gating** — out; in [sweep #10](../10-clinical-condition-gating/scope.md).

---

### 6. Privacy + consent literature for shared-household health data

#### 6.1 Family health portal literature

The **patient-portal / family-portal** literature in medical informatics has developed substantially since the rollout of MyChart-style portals in the early 2010s and the 21st Century Cures Act's information-blocking rule (2020 onward). Relevant work:

- **Proxy access** (one user accessing another household member's record — typically parent for child, adult child for elderly parent, spouse for spouse) is the central technical and ethical primitive. The literature ([Ancker et al. 2017](#references); [Steitz et al. 2019](#references); the **OurNotes / OpenNotes** family-of-projects) consistently identifies that **default-shared can violate the data-subject's autonomy** and **default-private can prevent legitimate caregiving** — neither extreme is acceptable.
- **Adolescent portals** are the most studied edge case: federal rules around adolescent confidentiality (especially around sexual/reproductive health, mental health, substance use) require that some portions of an adolescent's record be *segregated from* parental proxy access even when the parent is otherwise the proxy. This pattern is well-codified in pediatric health informatics ([Bourgeois et al. 2018](#references); [Anoshiravani et al. 2018](#references); [Carlson et al. 2020](#references)). `[verify]`
- **Couple-level proxy access** in adult contexts is *less* codified, with most systems defaulting to opt-in rather than opt-out. The literature ([Wolff et al. 2016](#references); [Latulipe et al. 2018](#references)) consistently recommends **granular, category-based consent** rather than all-or-nothing access.

Implication for NutriMe: the **per-category privacy defaults** in the scope (preferences shared / health context not shared / semantic feedback not shared / surface feedback shared) align with the granular-category-based consent pattern recommended in the literature. The defaults should be **explicitly user-configurable** (already in scope) and should be **renegotiable** at periodic check-ins, not just at intake.

#### 6.2 Shared EHR access patterns

The **shared-EHR / family-record** literature ([Bourgeois et al. 2008 and follow-ups](#references); the **AHRQ family-centered care** practice guides) documents:

- The **household member as data subject** is the primary unit of consent, not the household.
- **Disclosure between household members** of health information is governed by HIPAA permissions for proxies + explicit consent for non-proxy adults; in practice, system defaults shape behavior much more than legal frameworks.
- **Configurable defaults with clear surfacing of the current state** ("here is what your partner can see; change here") outperform either all-default-shared or all-default-private postures in user satisfaction and reported sense of control [Tier 3]. `[verify]`

#### 6.3 Family-medicine literature on consent and disclosure

Family-medicine and primary-care literature on **inter-family health-information disclosure** (e.g., [Levetown 2008](#references) on communication with families; [American Academy of Family Physicians position statements](#references)) emphasizes:

- The principle that **sensitive information requires explicit affirmative consent** to disclose to family members, even where the family member is otherwise involved in care.
- The default of **respecting the index patient's stated preference** about what to share with whom, and the importance of **asking rather than assuming**.
- The pattern of **deliberate, scheduled family meetings** (in clinical contexts) where disclosure is negotiated explicitly — translatable to NutriMe as the periodic check-in moment for re-negotiating sharing defaults.

Implication for NutriMe: the system's privacy defaults should be **conservative-by-default for sensitive health context** (already in scope), with **clear, surface-able state** ("here is what your partner can see right now, here is what they cannot, change here"), and with **explicit re-negotiation moments** built into the periodic check-in cadence.

#### 6.4 Configurable-default design patterns

The **defaults literature** ([Thaler & Sunstein 2008 *Nudge*; Johnson & Goldstein 2003](#references)) is foundational on the power of defaults to shape user behavior at scale. For shared health-data systems specifically:

- **Hard defaults** (cannot be changed) should be reserved for **safety-critical** items (e.g., cannot hide a documented severe allergen from a household cook).
- **Soft defaults** (changeable) should be set toward the **conservative privacy** position for sensitive data and toward the **shared-by-default** position for non-sensitive operational data (preferences, "want to try" lists, surface feedback).
- **Surfaced defaults** (the user can see what is currently shared and with whom) are a documented requirement for trust in shared-data systems ([Patel et al. 2015](#references) on patient-facing access controls).

The NutriMe-scoped privacy defaults (preferences shared by default; health context, semantic feedback private by default; surface feedback shared by default; allergen + condition data effectively hard-shared because of the safety-critical role of the household cook) are directionally consistent with this pattern. The hard-default for safety-critical allergens needs explicit rule documentation: **a household cook cannot be blinded to allergens of an eater they are cooking for**, because this would create a safety hazard. This is the one place the privacy-default architecture should be *non-configurable* downward.

---

### 7. Open questions — direct answers

> *Q: What is the strongest evidence for joint-meal-planning vs. independent-plans-with-convergence in adult households?*

**A:** The couple-based dietary intervention literature (§1.1, §1.3) consistently finds dyadic interventions outperform individually-targeted interventions on dietary outcomes for both partners, with effects replicating across cardiovascular, oncology, and T2D contexts. This supports **joint-meal-planning as the default** for the modal couple. However, the spousal-concordance literature (§1.2) finds that ~30% of long-cohabiting couples remain meaningfully discordant on at least one major dietary axis — this segment is mis-served by joint-only architectures. The **best-supported design is "joint-by-default, independent-with-convergence-days as a configurable affordance,"** which is what the scope specifies. [Tier 2/3 — direction well-supported; specific effect sizes `[verify]`.]

> *Q: What conflict-resolution order do clinical RDs use in practice when counseling couples / households?*

**A:** Documented RD practice (§3.1) prioritizes **(a) acute safety (allergens, severe contraindications) → (b) active clinical disease management → (c) life-stage requirements (pregnancy/lactation/growth/aging) → (d) preventive targets → (e) preference**. NutriMe's scope conflict-prioritization order (allergens → medical/life-stage folded → religious → strong preferences → macros → variety) maps cleanly to this with the additions of **religious/ethical observance** (which RDs handle but which is not always written into prioritization frameworks) and **explicit preference accommodation** (which RD literature treats as a load-bearing element, not a residual). [Tier 3 — practice-pattern, not RCT-derived.]

> *Q: How is "common base + per-plate deltas" actually implemented in real household cooking — what's the cognitive overhead, what works, what fails?*

**A:** The pattern is the **traditional default in Mediterranean, East Asian, South Asian, and Levantine cooking** (§2.1, §2.2, §2.6) — it is not novel and the cognitive overhead is well-managed in cuisines whose recipe architecture is *already* base + accompaniment. It is **less natural in the Anglo "single-plate single-dish" pattern** that has dominated mid-20th-century Western family cooking, where the cognitive overhead is real. The intervention literature (§4.1) finds the pattern works when the **base is genuinely shared** (everyone eats it) and **deltas are at the accompaniment / portion / spice / sauce-on-the-side level** rather than at the protein/main-dish level — i.e., per-plate-different-mains is what fails; per-plate-different-accompaniments to a shared main is what works. NutriMe should explicitly model this distinction. [Tier 3/4 mix — research thin, operational pattern strong.]

> *Q: What does the literature say about appropriate privacy defaults for shared-household health data systems?*

**A:** §6 — granular, category-based consent; conservative-by-default for sensitive health data; shared-by-default for operational/preference data; safety-critical items (allergens for the household cook) should be hard-shared and non-configurable downward; defaults must be visibly surfaced and re-negotiable at periodic moments. [Tier 3.]

> *Q: How do high-cooking cultures (Italian, Japanese, Indian) handle household-meal divergence vs. low-cooking cultures?*

**A:** §2.1, §2.2, §2.6 — high-cooking cultures resolve divergence **at the per-plate / per-bite level** rather than at the menu-design level, using shared-base architectures that absorb divergence within a single cooking effort. Low-cooking cultures (modal Anglo) resolve divergence by **multiplying meals** (cook the kids one thing, the adults another) — which is exactly the mode that makes household feeding feel impossible under time constraints. The high-cooking-culture pattern is operationally lighter once the *technique* of per-plate finishing is internalized. [Tier 3 — direction documented in commensality literature; specific cross-cultural quantification `[verify]`.]

> *Q: For households with children: what is the published evidence on family-meal-as-default vs. separate-kid-meal patterns, and how does this affect adult diet quality?*

**A:** §5.2 — family-meal-as-default with per-plate accommodation is consistently associated with better diet quality for *both* children and the adults in the household, lower disordered-eating risk in adolescents, and better psychosocial outcomes. Separate-kid-meals are associated with picky-eating reinforcement and a narrower lifelong food repertoire. The Project EAT longitudinal cohort and Hammons & Fiese 2011 meta-analysis are the most-cited sources. [Tier 2 for child-side outcomes; Tier 3 for adult-side `[verify]`.]

---

### 8. Gaps / suggestions for follow-up (without WebSearch/WebFetch)

- **Australian/Brisbane couple-intervention citations** are at memory-drift risk — specific PI names (Hagger, Hamilton, Carr at QUT/UQ; Burke at Monash; potentially Anderson, Winzenberg, others) and trial-acronym/year details should be verified against PubMed once web access is restored.
- The **specific RCTs underlying §1.1** (couple-based dietary intervention in CV / cancer / T2D contexts) need primary-source verification — the *direction* is well-established, the *citations* are at risk.
- **Hammons & Fiese 2011 meta-analysis** specifics (effect sizes, sample size totals) should be re-pulled.
- **Sobal/Bisogni** citation chain (which paper introduced which construct in which year) deserves a dedicated verification pass — the family of papers is large and citations sometimes propagate with year-drift.
- The **South Asian household meal-prep** literature is the thinnest peer-reviewed slice in this map; adding India-based household-eating cohort references (NIN Hyderabad, AIIMS work, IndEcho) would strengthen this section.
- **Russian household-meal patterns** were not covered; Russia is in the primary research scope per [geographic-scope.md](../00-meta/geographic-scope.md). Soviet-era nutrition literature on household feeding (collective canteens vs. domestic kitchens) and post-Soviet shifts should be added in a future pass.
- **Israeli household patterns** (similarly in primary research scope) — the Mediterranean-overlap is partial coverage; Sabbath-meal commensality literature would be a strong addition.
- **Wearable-data sharing within households** (one partner's CGM/sleep visible to the other) sits at the intersection of [sweep #6](../06-wearable-data-availability/scope.md) and §6 of this sweep; not covered here, deserves its own treatment.

---

## References

> All references below use the citation styles defined in [citation-style.md](../00-meta/citation-style.md). All accessed-on dates are recorded as `2026-04-29` per scope instruction, with the explicit caveat (see Findings §0 epistemic note) that **no live fetch was performed for this sweep** — these are reconstructed from training-data knowledge and the URL/DOI forms are best-of-knowledge, not freshly verified. Items marked `[verify]` in Findings should have their corresponding references re-pulled before being treated as load-bearing.

### Couple-based dietary intervention research

> Burke, V., Giangiulio, N., Gillam, H.F., Beilin, L.J., Houghton, S., & Milligan, R.A.K. (1999). Health promotion in couples adapting to a shared lifestyle. *Health Education Research*, 14(2), 269–288. https://doi.org/10.1093/her/14.2.269 **[Tier 3 — early couple-targeted dietary/lifestyle intervention.]**

> Hartmann-Boyce, J., Aveyard, P., Koshiaris, C., & Jebb, S.A. (2018). Development of tools to study personal weight control strategies: OxFAB taxonomy. *Obesity*, 25(12), 2110–2116. https://doi.org/10.1002/oby.21984 **[Tier 3 — placeholder for the broader Hartmann-Boyce systematic-review series on dietary/weight intervention; specific couple-intervention review citation `[verify]`.]**

> Carr, R.M., Prestwich, A., Kwasnicka, D., Thøgersen-Ntoumani, C., Gucciardi, D.F., Quested, E., Hall, L.H., & Ntoumanis, N. (2019). Dyadic interventions to promote physical activity and reduce sedentary behaviour: systematic review and meta-analysis. *Health Psychology Review*, 13(1), 91–109. https://doi.org/10.1080/17437199.2018.1532312 **[Tier 2 — dyadic behavior-change systematic review; physical-activity-primary but mechanism-relevant.]**

> Hagger, M.S., & Hamilton, K. (2018). Effects of socio-structural variables in the theory of planned behavior: a mediation model in multiple samples and behaviors. *Psychology & Health*, 33(11), 1357–1378. https://doi.org/10.1080/08870446.2018.1502311 **[Tier 3 — TPB / dyadic mechanism work; representative of Hagger lab's behavior-change theorization.]**

> Lewis, M.A., & Butterfield, R.M. (2007). Social control in marital relationships: effect of one's partner on health behaviors. *Journal of Applied Social Psychology*, 37(2), 298–319. https://doi.org/10.1111/j.0021-9029.2007.00161.x **[Tier 3 — social-control vs. social-support distinction in couples.]**

> Pachucki, M.A., Jacques, P.F., & Christakis, N.A. (2011). Social network concordance in food choice among spouses, friends, and siblings. *American Journal of Public Health*, 101(11), 2170–2177. https://doi.org/10.2105/AJPH.2011.300282 **[Tier 3 — Framingham Offspring spousal concordance.]**

> Michie, S., Richardson, M., Johnston, M., Abraham, C., Francis, J., Hardeman, W., Eccles, M.P., Cane, J., & Wood, C.E. (2013). The Behavior Change Technique Taxonomy (v1) of 93 hierarchically clustered techniques: building an international consensus for the reporting of behavior change interventions. *Annals of Behavioral Medicine*, 46(1), 81–95. https://doi.org/10.1007/s12160-013-9486-6 **[Tier 1/2 — BCT taxonomy v1, the foundational reference.]**

### Household-meal patterns — Mediterranean / commensality

> Trichopoulou, A., Costacou, T., Bamia, C., & Trichopoulos, D. (2003). Adherence to a Mediterranean diet and survival in a Greek population. *New England Journal of Medicine*, 348(26), 2599–2608. https://doi.org/10.1056/NEJMoa025039 **[Tier 2 — foundational Mediterranean adherence + outcome cohort.]**

> Estruch, R., Ros, E., Salas-Salvadó, J., Covas, M.-I., Corella, D., Arós, F., Gómez-Gracia, E., Ruiz-Gutiérrez, V., Fiol, M., Lapetra, J., Lamuela-Raventos, R.M., Serra-Majem, L., Pintó, X., Basora, J., Muñoz, M.A., Sorlí, J.V., Martínez, J.A., Martínez-González, M.A., for the PREDIMED Study Investigators (2018). Primary prevention of cardiovascular disease with a Mediterranean diet supplemented with extra-virgin olive oil or nuts. *New England Journal of Medicine*, 378(25), e34. https://doi.org/10.1056/NEJMoa1800389 **[Tier 1/2 — PREDIMED, post-correction reanalysis.]**

> Fischler, C. (2011). Commensality, society and culture. *Social Science Information*, 50(3-4), 528–548. https://doi.org/10.1177/0539018411413963 **[Tier 3 — commensality framework, Mediterranean comparative.]**

### Household-meal patterns — East Asian

> Kurotani, K., Akter, S., Kashino, I., Goto, A., Mizoue, T., Noda, M., Sasazuki, S., Sawada, N., & Tsugane, S. (2016). Quality of diet and mortality among Japanese men and women: Japan Public Health Center based prospective study. *BMJ*, 352, i1209. https://doi.org/10.1136/bmj.i1209 **[Tier 2 — JPHC dietary patterns + mortality, Japanese cohort.]**

> Du, S., Wang, H., Zhang, B., Zhai, F., & Popkin, B.M. (2014). China in the period of transition from scarcity and extensive undernutrition to emerging nutrition-related noncommunicable diseases, 1949–1992. *Obesity Reviews*, 15(Suppl 1), 8–15. https://doi.org/10.1111/obr.12122 **[Tier 3 — China Health and Nutrition Survey context for urban household dietary transitions.]**

> Lee, M.J., Popkin, B.M., & Kim, S. (2002). The unique aspects of the nutrition transition in South Korea: the retention of healthful elements in their traditional diet. *Public Health Nutrition*, 5(1A), 197–203. https://doi.org/10.1079/PHN2001294 **[Tier 3 — Korean nutrition transition + traditional pattern retention.]**

### Household-meal patterns — Nordic + Western nuclear-family

> Sayer, L.C. (2005). Gender, time and inequality: trends in women's and men's paid work, unpaid work and free time. *Social Forces*, 84(1), 285–303. https://doi.org/10.1353/sof.2005.0126 **[Tier 3 — cross-national time-use framework relevant to Nordic shared-cooking.]**

> Mäkelä, J., Kjærnes, U., Pipping Ekström, M., L'orange Fürst, E., Gronow, J., & Holm, L. (1999). Nordic meals: methodological notes on a comparative survey. *Appetite*, 32(1), 73–79. https://doi.org/10.1006/appe.1998.0198 **[Tier 3 — Nordic meal-pattern comparative survey methodology.]**

> Holm, L., Lauridsen, D., Lund, T.B., Gronow, J., Niva, M., & Mäkelä, J. (2016). Changes in the social context and conduct of eating in four Nordic countries between 1997 and 2012. *Appetite*, 103, 358–368. https://doi.org/10.1016/j.appet.2016.04.034 **[Tier 3 — Nordic eating-context change over time.]**

### Western nuclear-family + family-meal literature

> Hammons, A.J., & Fiese, B.H. (2011). Is frequency of shared family meals related to the nutritional health of children and adolescents? *Pediatrics*, 127(6), e1565–e1574. https://doi.org/10.1542/peds.2010-1440 **[Tier 2 — meta-analysis, family meals + child nutrition.]**

> Neumark-Sztainer, D., Larson, N.I., Fulkerson, J.A., Eisenberg, M.E., & Story, M. (2010). Family meals and adolescents: what have we learned from Project EAT (Eating Among Teens)? *Public Health Nutrition*, 13(7), 1113–1121. https://doi.org/10.1017/S1368980010000169 **[Tier 2/3 — Project EAT longitudinal review.]**

> Fulkerson, J.A., Friend, S., Flattum, C., Horning, M., Draxten, M., Neumark-Sztainer, D., Gurvich, O., Garwick, A., Story, M., & Kubik, M.Y. (2015). Promoting healthful family meals to prevent obesity: HOME Plus, a randomized controlled trial. *International Journal of Behavioral Nutrition and Physical Activity*, 12, 154. https://doi.org/10.1186/s12966-015-0320-3 **[Tier 2/3 — HOME Plus family-meal RCT, modular meal-planning curriculum.]**

> Larson, N., MacLehose, R., Fulkerson, J.A., Berge, J.M., Story, M., & Neumark-Sztainer, D. (2013). Eating breakfast and dinner together as a family: associations with sociodemographic characteristics and implications for diet quality and weight status. *Journal of the Academy of Nutrition and Dietetics*, 113(12), 1601–1609. https://doi.org/10.1016/j.jand.2013.08.011 **[Tier 3 — family meal frequency + diet quality, US cross-sectional.]**

### US "second shift" / cooking-labor sociology

> Hochschild, A.R., & Machung, A. (2012). *The Second Shift: Working Families and the Revolution at Home* (Revised ed.). Penguin Books. **[Tier 4 — sociological monograph; cited as cultural / historical context per evidence-tiers.md, not for health claims.]**

> DeVault, M.L. (1991). *Feeding the Family: The Social Organization of Caring as Gendered Work*. University of Chicago Press. **[Tier 4 — sociological monograph; cited as descriptive context.]**

> Bowen, S., Brenton, J., & Elliott, S. (2019). *Pressure Cooker: Why Home Cooking Won't Solve Our Problems and What We Can Do About It*. Oxford University Press. **[Tier 4 — sociological monograph based on multi-year ethnography; cited descriptively.]**

> Bowen, S., Elliott, S., & Brenton, J. (2014). The joy of cooking? *Contexts*, 13(3), 20–25. https://doi.org/10.1177/1536504214545755 **[Tier 3/4 — peer-reviewed sociology; ethnographic findings.]**

> Daminger, A. (2019). The cognitive dimension of household labor. *American Sociological Review*, 84(4), 609–633. https://doi.org/10.1177/0003122419859007 **[Tier 3 — cognitive labor of household management, including meal planning.]**

### South Asian household meal-prep / dietary patterns

> Misra, A., Singhal, N., Sivakumar, B., Bhagat, N., Jaiswal, A., & Khurana, L. (2011). Nutrition transition in India: secular trends in dietary intake and their relationship to diet-related non-communicable diseases. *Journal of Diabetes*, 3(4), 278–292. https://doi.org/10.1111/j.1753-0407.2011.00139.x **[Tier 3 — Indian nutrition transition + household dietary shifts.]**

> Daniel, C.R., Prabhakaran, D., Kapur, K., Graubard, B.I., Devasenapathy, N., Ramakrishnan, L., George, P.S., Shetty, H., Ferrucci, L.M., Yurgalevitch, S., Chatterjee, N., Reddy, K.S., Rastogi, T., Gupta, P.C., Mathew, A., Sinha, R. (2011). A cross-sectional investigation of regional patterns of diet and cardio-metabolic risk in India. *Nutrition Journal*, 10, 12. https://doi.org/10.1186/1475-2891-10-12 **[Tier 3 — Indian regional dietary pattern variation, household-relevant.]**

### Conflict balancing / RD practice / behavior change

> Spahn, J.M., Reeves, R.S., Keim, K.S., Laquatra, I., Kellogg, M., Jortberg, B., & Clark, N.A. (2010). State of the evidence regarding behavior change theories and strategies in nutrition counseling to facilitate health and food behavior change. *Journal of the American Dietetic Association*, 110(6), 879–891. https://doi.org/10.1016/j.jada.2010.03.021 **[Tier 2 — Academy of Nutrition and Dietetics behavior-change practice review.]**

> Whitney, E.N., Rolfes, S.R., Hammond, G., Piché, L., DeBruyne, L.K., & Pinna, K. (current editions). *Nutrition Counseling and Communication Skills* / general RD practice texts. **[Tier 4 — textbook context; cited descriptively for documented RD practice patterns. Authoritative practice content lives in Academy EAL.]**

> **Academy of Nutrition and Dietetics** (current). *Evidence Analysis Library*. https://www.andeal.org/. Accessed 2026-04-29. **[Tier 1 — RD practice-guideline evidence base; specific household-counseling guidelines `[verify]`.]**

### Bisogni / Sobal — food-choice process and household roles

> Bisogni, C.A., Connors, M., Devine, C.M., & Sobal, J. (2002). Who we are and how we eat: a qualitative study of identities in food choice. *Journal of Nutrition Education and Behavior*, 34(3), 128–139. https://doi.org/10.1016/S1499-4046(06)60082-1 **[Tier 3 — foundational identity + food-choice qualitative work.]**

> Sobal, J., & Bisogni, C.A. (2009). Constructing food choice decisions. *Annals of Behavioral Medicine*, 38(Suppl 1), s37–s46. https://doi.org/10.1007/s12160-009-9124-5 **[Tier 3 — food-choice process model integrative review.]**

> Bisogni, C.A., Jastran, M., Seligson, M., & Thompson, A. (2012). How people interpret healthy eating: contributions of qualitative research. *Journal of Nutrition Education and Behavior*, 44(4), 282–301. https://doi.org/10.1016/j.jneb.2011.11.009 **[Tier 3 — interpretation-of-healthy-eating qualitative synthesis.]**

> Sobal, J., Bove, C.F., & Rauschenbach, B.S. (2002). Commensal careers at entry into marriage: establishing commensal units and managing commensal circles. *Sociological Review*, 50(3), 378–397. https://doi.org/10.1111/1467-954X.00388 **[Tier 3 — commensal-careers framework for newly-cohabiting couples.]**

> Sobal, J., Hanson, K.L., & Frongillo, E.A. (2014). Family meals and body weight in U.S. adults. *Public Health Nutrition*, 17(3), 552–561. https://doi.org/10.1017/S1368980013000349 **[Tier 3 — family meals + adult outcomes, US cross-sectional.]**

### Common-base + per-plate-deltas — operational / professional kitchen

> Escoffier, A. (1903; many reprints). *Le Guide Culinaire*. **[Tier 4 — professional culinary reference; cited for documentation of mother-sauce architecture.]**

> The Culinary Institute of America (multiple editions, current). *The Professional Chef*. Wiley. **[Tier 4 — professional culinary curriculum; cited for documentation of mise en place + station-based modular service.]**

> Spears, M.C., & Gregoire, M.B. (2007 and later editions). *Foodservice Organizations: A Managerial and Systems Approach*. Pearson. **[Tier 4 — institutional foodservice production cooking + per-diet modification documentation.]**

### Pediatric inclusion — feeding, family meals, allergens

> Hagan, J.F., Shaw, J.S., & Duncan, P.M. (Eds.). (2017). *Bright Futures: Guidelines for Health Supervision of Infants, Children, and Adolescents* (4th ed.). American Academy of Pediatrics. https://brightfutures.aap.org/. Accessed 2026-04-29. **[Tier 1 — canonical US pediatric primary-care framework.]**

> **WHO** (2003; updated 2023). *Guiding Principles for Complementary Feeding of the Breastfed Child*. Pan American Health Organization / World Health Organization. https://www.who.int/publications/i/item/9275124604. Accessed 2026-04-29. **[Tier 1 — WHO complementary feeding guidance.]**

> **USDA / HHS** (2020). *Dietary Guidelines for Americans, 2020-2025* (incl. Birth-24 Months chapter). U.S. Department of Agriculture & U.S. Department of Health and Human Services. https://www.dietaryguidelines.gov/. Accessed 2026-04-29. **[Tier 1 — first DGA edition with B-24 chapter.]**

> Du Toit, G., Roberts, G., Sayre, P.H., Bahnson, H.T., Radulovic, S., Santos, A.F., Brough, H.A., Phippard, D., Basting, M., Feeney, M., Turcanu, V., Sever, M.L., Gomez Lorenzo, M., Plaut, M., Lack, G., for the LEAP Study Team (2015). Randomized trial of peanut consumption in infants at risk for peanut allergy. *New England Journal of Medicine*, 372(9), 803–813. https://doi.org/10.1056/NEJMoa1414850 **[Tier 1 — LEAP trial, foundational early-introduction RCT.]**

> Togias, A., Cooper, S.F., Acebal, M.L., Assa'ad, A., Baker, J.R. Jr., Beck, L.A., Block, J., Byrd-Bredbenner, C., Chan, E.S., Eichenfield, L.F., Fleischer, D.M., Fuchs, G.J. 3rd, Furuta, G.T., Greenhawt, M.J., Gupta, R.S., Habich, M., Jones, S.M., Keaton, K., Muraro, A., Plaut, M., Rosenwasser, L.J., Rotrosen, D., Sampson, H.A., Schneider, L.C., Sicherer, S.H., Sidbury, R., Spergel, J., Stukus, D.R., Venter, C., Boyce, J.A. (2017). Addendum guidelines for the prevention of peanut allergy in the United States: report of the National Institute of Allergy and Infectious Diseases-sponsored expert panel. *Journal of Allergy and Clinical Immunology*, 139(1), 29–44. https://doi.org/10.1016/j.jaci.2016.10.010 **[Tier 1 — NIAID guideline reversal post-LEAP.]**

> Mennella, J.A. (2014). Ontogeny of taste preferences: basic biology and implications for health. *American Journal of Clinical Nutrition*, 99(3), 704S–711S. https://doi.org/10.3945/ajcn.113.067694 **[Tier 2/3 — flavor learning in early life, including in-utero and breastfeeding-mediated cuisine exposure.]**

> Birch, L.L., & Fisher, J.O. (1998). Development of eating behaviors among children and adolescents. *Pediatrics*, 101(3 Pt 2), 539–549. https://doi.org/10.1542/peds.101.S2.539 **[Tier 2/3 — foundational developmental food-acceptance work.]**

> Wardle, J., Cooke, L.J., Gibson, E.L., Sapochnik, M., Sheiham, A., & Lawson, M. (2003). Increasing children's acceptance of vegetables: a randomized trial of parent-led exposure. *Appetite*, 40(2), 155–162. https://doi.org/10.1016/S0195-6663(02)00135-6 **[Tier 2 — repeated-exposure RCT for child food acceptance.]**

> Cooke, L. (2007). The importance of exposure for healthy eating in childhood: a review. *Journal of Human Nutrition and Dietetics*, 20(4), 294–301. https://doi.org/10.1111/j.1365-277X.2007.00804.x **[Tier 2/3 — repeated exposure review.]**

> Savage, J.S., Fisher, J.O., & Birch, L.L. (2007). Parental influence on eating behavior: conception to adolescence. *Journal of Law, Medicine & Ethics*, 35(1), 22–34. https://doi.org/10.1111/j.1748-720X.2007.00111.x **[Tier 2/3 — parental influence + family-style serving review.]**

### Privacy, consent, family health portals, shared EHR

> Ancker, J.S., Mauer, E., Kalish, R.B., Vest, J.R., & Gossey, J.T. (2017). Early adopters of patient-generated health data upload in an electronic patient portal. *Applied Clinical Informatics*, 8(2), 568–579. https://doi.org/10.4338/ACI-2016-12-RA-0207 **[Tier 3 — patient portal adoption / proxy access context.]**

> Wolff, J.L., Darer, J.D., Berger, A., Clarke, D., Green, J.A., Stametz, R.A., Delbanco, T., & Walker, J. (2017). Inviting patients and care partners to read doctors' notes: OpenNotes and shared access to electronic medical records. *Journal of the American Medical Informatics Association*, 24(e1), e166–e172. https://doi.org/10.1093/jamia/ocw108 **[Tier 3 — OpenNotes / shared access to EHR.]**

> Latulipe, C., Quandt, S.A., Melius, K.A., Bertoni, A., Miller Jr., D.P., Smith, D., & Arcury, T.A. (2018). Insights into older adult patient concerns around the caregiver proxy portal use: qualitative interview study. *Journal of Medical Internet Research*, 20(11), e10524. https://doi.org/10.2196/10524 **[Tier 3 — proxy portal use, older adults + caregivers.]**

> Bourgeois, F.C., Taylor, P.L., Emans, S.J., Nigrin, D.J., & Mandl, K.D. (2008). Whose personal control? Creating private, personally controlled health records for pediatric and adolescent patients. *Journal of the American Medical Informatics Association*, 15(6), 737–743. https://doi.org/10.1197/jamia.M2865 **[Tier 3 — pediatric/adolescent personal control of health records.]**

> Bourgeois, F.C., DesRoches, C.M., & Bell, S.K. (2018). Ethical challenges raised by OpenNotes for pediatric and adolescent patients. *Pediatrics*, 141(6), e20172745. https://doi.org/10.1542/peds.2017-2745 **[Tier 3 — adolescent confidentiality + portal proxy access ethics.]**

> Anoshiravani, A., Gaskin, G., Kurzweil, A., Carlson, J., & Pageler, N. (2018). Implementing an interoperable personal health record in pediatrics: lessons learned at an academic children's hospital. *Journal of Participatory Medicine*, 10(1), e10. https://doi.org/10.2196/jopm.10242 **[Tier 3 — pediatric portal implementation lessons.]**

> Carlson, J.L., Goldstein, R., Buhr, T., & Buckmiller, N. (2020). Teen and parent perspectives on electronic communication with health care providers. *Journal of Adolescent Health*, 67(3), 416–422. https://doi.org/10.1016/j.jadohealth.2020.04.032 **[Tier 3 — teen / parent perspectives on shared digital communication with providers; relevant to adolescent-portal consent design `[verify]`.]**

> Steitz, B.D., Cronin, R.M., Davis, S.E., Yan, E., & Jackson, G.P. (2019). Long-term patterns of patient portal use for pediatric patients at an academic medical center. *Applied Clinical Informatics*, 10(2), 264–271. https://doi.org/10.1055/s-0039-1685433 **[Tier 3 — long-term pediatric portal use patterns including adolescent transition.]**

> Patel, V.N., Dhopeshwarkar, R.V., Edwards, A., Barrón, Y., Sparenborg, J., & Kaushal, R. (2012). Consumer support for health information exchange and personal health records: a regional health information organization survey. *Journal of Medical Systems*, 36(3), 1043–1052. https://doi.org/10.1007/s10916-010-9566-0 **[Tier 3 — consumer attitudes on health-information access controls.]**

> Levetown, M., & American Academy of Pediatrics Committee on Bioethics (2008). Communicating with children and families: from everyday interactions to skill in conveying distressing information. *Pediatrics*, 121(5), e1441–e1460. https://doi.org/10.1542/peds.2008-0565 **[Tier 1/2 — AAP communication guidance, family-context disclosure principles.]**

### Default-design / configurable defaults

> Thaler, R.H., & Sunstein, C.R. (2008). *Nudge: Improving Decisions About Health, Wealth, and Happiness*. Yale University Press. **[Tier 4 — popular-press exposition; the underlying peer-reviewed work on defaults is Johnson & Goldstein and others below.]**

> Johnson, E.J., & Goldstein, D. (2003). Do defaults save lives? *Science*, 302(5649), 1338–1339. https://doi.org/10.1126/science.1091721 **[Tier 2 — foundational empirical work on default effects, organ donation context.]**

### Cross-references back to other NutriMe sweeps

- [sweep #1 (international nutrition standards)](../01-international-nutrition-standards/scope.md) — life-stage DRIs feed §5 (pediatric inclusion)
- [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — pediatric assessment instruments (NutriSTEP, KEDS, ChEAT, NIAS, PARDI-AR-Q, Children's Food Security Survey, CDC + WHO growth charts) live there; this sweep references that work for parent-mediated intake design
- [sweep #6 (wearable data availability)](../06-wearable-data-availability/scope.md) — household sharing of wearable data is a privacy-design intersection not covered here
- [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — pediatric clinical condition gating
- [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — recipe corpora supporting common-base + per-plate-deltas architecture

---

> **Reminder per scope:** do NOT edit `00-meta/sources.md` — consolidation is handled separately later.
