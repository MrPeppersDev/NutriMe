# Sweep #12 — Skills-by-Cuisine Mapping

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Build a research-grounded matrix mapping cooking skills to cuisine traditions worldwide. This sweep is the **engine that bridges cooking-confidence assessment ↔ recipe selection ↔ horizon-broadening**: it lets the system match recipes to user capability, identify "stretch" recipes that grow specific skills, and pace the iterative culinary expansion the product is designed around.

## Deliverable

An annotated reference map containing:

- **Skill taxonomy** built from a hybrid base (professional culinary curriculum spine + academic culinary research + bottom-up extraction from major dishes per cuisine)
- **Skill ↔ cuisine matrix** at medium granularity by default, with fine-granularity available where user competence grows
- **Skill progression paths** — A enables B+C, B+C enable D — needed for iterative horizon-broadening
- **Equipment ↔ skill bindings** — what hardware enables what skills
- **Cultural / regional / generational variation** in skills within a cuisine
- **Skill ↔ recipe linkage schema** — this sweep owns it; [sweep #11](../11-recipe-sourcing/scope.md) consumes it
- **"Where to learn" reference map** — map educational sources for skill acquisition at reference level (we map what's available, we don't deliver lessons per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not))

This is a **reference map**, not corpus build.

## In scope

### Skill taxonomy basis (hybrid)

- **Professional culinary curriculum spine** — extract the core skill enumeration from CIA, Le Cordon Bleu, Tsuji, Ferrandi, ALMA, Hattori, IHM, China Culinary Academy curricula. Use as the structural backbone (acknowledging pro-kitchen bias).
- **Academic culinary research** — adapt for home-cooking-relevance using academic culinary studies, food science home-cooking research, behavioral cooking literature.
- **Bottom-up extraction** — iterate over major dishes per cuisine and extract required skills; aggregate to validate / extend the taxonomy.

### Granularity strategy

**Medium granularity by default.** Each major skill domain broken into 3–5 sub-skills:

- *Knife skills:* dicing, julienne, chiffonade, brunoise, supreming, deboning
- *Sauces:* pan sauces, mother sauces, emulsions, reductions, vinaigrettes
- *Dough:* mixing methods, kneading, lamination, proofing, shaping
- *Fermentation:* lactic-acid (kraut, kimchi), yeast (bread, beer), mold-driven (cheese, koji-adjacent), salt-cure
- *Heat-application:* sauté, braise, roast, sear, poach, blanch, steam, grill, smoke
- *Pressure / steam:* stovetop pressure, electric pressure, traditional steam (bamboo, dim sum)
- *Wok / high-heat stir-fry:* wok hei, parboil-stir-fry, dry-frying
- *Grilling / smoking:* direct, indirect, low-and-slow, charcoal-vs-gas-vs-wood
- *Doughs and batters by tradition:* European pastry, Asian dumpling skins, Indian flatbreads, Latin American masa
- *(further enumeration during research)*

**Fine granularity available** as user competence grows — system measures + recommends at finer resolution as it learns the user (parallel to iterative-intake horizon-broadening). E.g., a user proficient with sauces gets pressed on which mother sauces specifically, which emulsions, etc.

### Skill ↔ cuisine matrix

For each cuisine in [primary research scope](../00-meta/geographic-scope.md):
- Required entry-level skills (skills you must have to attempt entry-level dishes)
- Skills enabling intermediate-level dishes
- Skills enabling advanced / specialty dishes
- **Cultural / regional / generational variation** within the cuisine — Northern vs. Southern Italian, regional Indian (Punjabi vs. South Indian vs. Bengali), Chinese regional (Sichuan vs. Cantonese vs. Hunan), Korean (royal court vs. home banchan vs. street food), Japanese (kaiseki vs. izakaya vs. home washoku)
- Cross-cuisine skill transfer — French sauce skills transfer to Spanish, Italian; Japanese dashi skills transfer to Korean, Chinese; etc.

Methodology is **hybrid top-down + bottom-up**: top-down ("what does the literature say Cuisine X requires") + bottom-up ("iterate over major Cuisine X dishes, extract required skills, validate against top-down").

### Skill progression paths

Build dependency graph:
- Skill A enables skills B and C
- Skills B + C combined enable skill D
- D opens cuisine domain X

Example: Knife dicing + basic sauté + stock-making → braising → enables much of French peasant cuisine, Italian rustic, Chinese red-cooking. Add fermentation → opens Korean banchan, much of Eastern European preserved cuisine.

Used for:
- Iterative horizon-broadening pacing (system identifies the next skill to introduce based on current user competence + cuisine they want to explore)
- "Stretch recipe" identification (recipes that introduce one new skill within a base of mastered skills, vs. recipes that require multiple new skills at once)
- Cooking confidence growth tracking over time

### Equipment ↔ skill bindings

What hardware enables what skills (cross-references [sweep #7](../07-cooking-behavioral-barriers/scope.md) equipment-surfacing UX):

- Wok ↔ high-heat stir-fry, wok hei
- Pressure cooker (stovetop or electric) ↔ pressure-based cuisines (much of Indian, some Latin American, some Eastern European)
- Bamboo / metal steamer ↔ dim sum, mantou, idli/dhokla, dumpling steaming
- Tandoor (or convection-based home substitute) ↔ tandoor-style breads + meats
- Cast iron ↔ certain American Southern, certain European peasant
- Outdoor grill / smoker ↔ BBQ traditions, certain Korean, Brazilian churrasco
- Sous vide ↔ modern precision cooking (technique, not cuisine-bound)
- KitchenAid / stand mixer ↔ certain bread + pastry workflows
- Mortar and pestle / molcajete / suribachi ↔ many traditional cuisines (Thai, Mexican, Japanese)

### Cultural / regional / generational variation

Skills within a cuisine vary by region, era, and generation:

- Northern Italian (butter, dairy-rich, broader pasta variety) vs. Southern (olive oil, tomato-forward, simpler pasta)
- Regional Indian — Punjabi (tandoor-heavy, dairy-rich), South Indian (rice + fermented batters, coconut), Bengali (mustard oil, freshwater fish), Gujarati (vegetarian, sweet-savory balance)
- Regional Chinese — Sichuan (málà, pickling, dry-frying), Cantonese (steaming, freshness, dim sum), Hunan (smoked + spicy), Shanghai (red-cooking, sweetness), Northern wheat-based vs. Southern rice-based
- Korean — royal court (jeongol, gujeolpan), home banchan, street food (tteokbokki, gimbap, hotteok)
- Japanese — kaiseki precision, izakaya rustic, home washoku, regional ramen
- Generational — traditional skills (fermentation from scratch, butchery, full pastry from raw flour) vs. modern home cooking (semi-prepared component assembly)

System should respect this nuance, not flatten cuisines into single profiles.

### Skill ↔ recipe linkage schema

This sweep produces the schema fields that recipes (in [sweep #11](../11-recipe-sourcing/scope.md)) will populate:

- Required skills (list, with granularity tags)
- Skill prerequisites (dependency on prior skills)
- Stretch-skill markers (skills this recipe introduces, if any)
- Equipment requirements (cross-references equipment ↔ skill bindings)
- Cultural / regional context (which variant of the cuisine this recipe represents)
- Confidence-tier mapping (which user confidence level this recipe is appropriate for)
- Progression-graph position (where this recipe sits in the skill-growth path)

### "Where to learn" reference map (stretch-goal scope at reference level)

Per [product-framing](../00-meta/product-framing.md#what-nutrime-is-explicitly-not): NutriMe maps where a user can learn a missing skill, but does not deliver lessons. Map educational sources for skill acquisition:

- YouTube channels by skill domain (cross-references institutional + credentialed sources from [sweep #11](../11-recipe-sourcing/scope.md))
- Cooking school programs (online + in-person, by region)
- MasterClass / educational subscription platforms
- Skill-focused books (Kenji's *The Food Lab*, *On Cooking*, *The Professional Chef*, region-specific equivalents)
- In-person community classes (community college culinary, recreational cooking schools, cultural-center classes)

Map only — do not deliver, do not curate, do not partner. The system surfaces these as "if you want to learn this skill, here are the kinds of resources that exist."

### Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md), with **explicit attention to non-Western cuisine skill mapping** paralleling [sweep #11](../11-recipe-sourcing/scope.md)'s non-Western emphasis. The system's horizon-broadening promise depends on having credible skill mapping for cuisines beyond US/Western European.

## Out of scope (with reasons)

- **Cooking instruction delivery** — out per [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not). Mapping where to learn ≠ teaching.
- **Building actual skill assessment instruments** — covered in [sweep #3 (cooking confidence + cooking literacy screeners)](../03-clinical-nutrition-assessment/scope.md)
- **Recipe selection algorithms** — that's downstream system design; this sweep produces the substrate
- **Equipment vendor recommendations** — out (we surface what equipment a recipe needs, not where to buy it)

## Open questions for the research

- For the hybrid skill taxonomy: where do professional culinary curricula converge vs. diverge across CIA, Le Cordon Bleu, Tsuji, IHM, China Culinary Academy?
- For skill progression: what's the published evidence on how home cooks actually grow skills over time (vs. what professional curricula assume)?
- For non-Western cuisine skill mapping: what English-language / translated sources adequately characterize regional skill variation?
- For equipment ↔ skill: which equipment substitutions actually work (e.g., dutch oven as tandoor substitute, sheet pan as broiler-charring substitute)?
- For "where to learn" mapping: what's the realistic universe of skill-acquisition resources, and how do they get ranked / filtered by quality?
- For cultural variation: how much variation does the system surface to the user vs. abstract away?

## Cross-references

- Sister to [sweep #7 (cooking behavioral barriers)](../07-cooking-behavioral-barriers/scope.md) — confidence + equipment + skills bindings
- Feeds [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — skill metadata schema, skill ↔ recipe linkage
- Bound by [product-framing "not a cooking class" boundary](../00-meta/product-framing.md#what-nutrime-is-explicitly-not) — we map skills, we don't teach them
- Cross-references [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — cooking confidence + cooking literacy intake screeners feed into the matrix
- Cross-references [intake-pattern.md](../00-meta/intake-pattern.md) — iterative horizon-broadening uses the skill progression graph
- Implements [framework-over-source-list principle](../00-meta/dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle)
- See [geographic-scope.md](../00-meta/geographic-scope.md) for primary research scope with non-Western emphasis

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
