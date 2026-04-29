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

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
