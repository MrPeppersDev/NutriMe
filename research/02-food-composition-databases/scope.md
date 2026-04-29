# Sweep #2 — Food Composition Databases — Multi-Source Landscape

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Map the landscape of food composition databases worldwide, characterize coverage / quality / access / licensing, identify harmonization standards and known gaps, and surface the framework-level literature on cooking transformations (yield + retention factors).

## Deliverable

An annotated reference map containing:

- Per-database inventory (mirroring sweep #1's geographic scope of top 150 countries via FAO INFOODS):
  - Maintainer + license (public domain, ODbL, CC-BY, proprietary)
  - Access modality (free API, paid API, downloadable, PDF-only)
  - Coverage profile (whole foods, branded, prepared, restaurant)
  - Item count + nutrient panel breadth
  - Last update / version cadence
  - Known coverage gaps (e.g., USDA FDC weak on prepared international dishes)
- Branded / packaged product sub-section (Open Food Facts, USDA branded, GS1)
- Cooking transformation framework: yield factors and retention factors, citing the foundational literature (USDA Tables 12 & 13, EuroFIR factors, Bognar)
- Harmonization standards: INFOODS tagnames, LanguaL, FoodEx2

## In scope

- **Geographic scope:** top 150 countries (mirrors [sweep #1](../01-international-nutrition-standards/scope.md))
- **Major databases:** USDA FoodData Central (Foundation, SR Legacy, FNDDS, Branded), EuroFIR, McCance & Widdowson (UK CoFID), AUSNUT/NUTTAB, Canadian Nutrient File (CNF), INFOODS regional databases, Japan STFC, Indian Food Composition Tables, China FCT, Brazilian TBCA
- **Branded products:** Open Food Facts (3M+ items, ODbL), USDA FDC Branded, plus regional branded databases — handled as a *separate category* from whole/generic foods
- **Cooking transformations:** framework-level coverage of yield factors (mass change with cooking) and retention factors (nutrient survival through cooking) — references and literature pointers, not full tables
- **Access details:** API endpoints, rate limits, pricing, license terms, terms of use
- **Coverage gaps:** known weaknesses (international prepared dishes, regional/ethnic foods, traditional preparations)
- **Harmonization standards:** INFOODS tagnames, LanguaL food classification, FoodEx2

## Out of scope (with reasons)

- Restaurant / chain food databases (MenuStat, FastFoodNutrition) — deferred. Without a logging surface, the obvious use case disappears. Pending decision on whether traveler/eating-out *recommendations* justify keeping at reference level.
- Full ingestion of any database — deferred to later corpus-build phase
- Deep cooking transformation tables — deferred (frameworks cited here, full tables in a later corpus build)
- Micronutrient bioavailability literature — deferred (would warrant its own sweep if needed)
- Nutrient interaction modeling — deferred

## Branded vs. whole / generic foods

Per user direction: **whole, generic, from-scratch foods are the default surface**; branded packaged goods are in scope but treated as a separate category. Real cook-from-scratch users still buy branded staples (canned tomatoes, pasta, condiments). The data model should distinguish these but neither is excluded.

## Cooking transformations

Cooking changes nutrition substantially:

- Vitamin C losses in boiling
- B-vitamin losses across multiple methods
- Water and fat changes in roasting / frying
- Mineral leaching into discarded steaming water
- Fat absorption from frying oil

Framework-level coverage in this sweep means: cite the foundational literature and the standard tables (USDA Tables 12 & 13, EuroFIR factors, Bognar 2002), characterize what's available and how rigorous it is. Full table ingestion happens later.

## Open questions for the research

- Which databases have free, programmatic API access vs. download-only vs. paywalled?
- What are the licensing terms for downstream use (especially commercial, even though we're personal-first)?
- For the top 150 countries, how many have a maintained national food composition database, and how many rely on regional / WHO INFOODS aggregates?
- How do the major databases harmonize (or fail to harmonize) on units, nutrient definitions, and ingredient identifiers?
- What is the state of branded product coverage internationally — is Open Food Facts the global gold standard, or are there regional alternatives?
- How are cultural/religious-specific foods (halal, kosher, jain, ayurvedic, traditional preparations) covered?

## Cross-references

- Bound by [Evidence Tiers](../00-meta/evidence-tiers.md) — composition data quality varies; treat USDA Foundation Foods as authoritative, branded data as user-submitted (Open Food Facts) → Tier 4 unless verified
- Mirrors geographic scope of [sweep #1](../01-international-nutrition-standards/scope.md)
- Feeds [sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md) — recipes need composition data to compute nutrition
- Feeds [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — condition-relevant nutrient lookups (e.g., potassium for CKD)

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
