# Sweep #1 — International Nutrition Reference Standards

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Build a comparative reference map of nutrition reference standards (DRIs / NRVs / RNIs / DRVs) across the top 150 countries' authoritative bodies, plus dietary pattern guidance and public-health additions. Characterize where bodies agree, where they diverge, why, and how the system should present those divergences to users.

## Deliverable

An annotated reference map containing:

- Per-body inventory: bodies covering ~150 countries' worth of standards (per FAO INFOODS membership), key publications, current versions, publication / next-revision dates
- Comparative table for major nutrients (energy, protein, fat distribution, carbohydrate, fiber, key vitamins, key minerals, water, sodium ceiling) showing where bodies agree and where they materially diverge
- Dietary pattern guidance per body — Mediterranean, Nordic NNR, Japanese spinning top, Brazilian dietary guidelines, EAT-Lancet planetary, US DGA, etc. — with links and current versions
- Public-health additions: added sugar, sodium, alcohol, ultra-processed foods, trans fat thresholds, where each body publishes them
- Methodology notes: how each body derives its numbers (basal needs, EAR/RDA model, AI/UL framing, age-sex stratification approach)

This is a **reference map**, not a corpus build. Actual data ingestion happens in a later phase.

## In scope

- **Geographic scope:** top 150 countries (effectively FAO INFOODS coverage)
- **Standards bodies (representative):**
  - US — NASEM/IOM DRIs, USDA Dietary Guidelines
  - EU — EFSA Dietary Reference Values
  - UK — SACN, Public Health England RNIs
  - Australia / New Zealand — NHMRC NRVs
  - Canada — Health Canada DRIs (uses US NASEM)
  - Nordic — NNR (Nordic Nutrition Recommendations)
  - WHO / FAO — global recommendations and EAR ranges
  - Japan — DRI-J (MHLW)
  - India — ICMR-NIN
  - China — Chinese Nutrition Society DRIs
  - Brazil — Ministry of Health Dietary Guidelines
  - Other countries surveyed at minimum at the dietary-guidelines level
- **Nutrient panel:** full DRI panel (energy, macros, micros, fatty acids, amino acids, fiber, water)
- **Population subgroups:** full matrix (age × sex × life stage including pregnancy / lactation)
- **Dietary patterns:** Mediterranean (multiple national variants), Nordic, Japanese spinning top, Brazilian, EAT-Lancet, DASH, MIND, Okinawan, traditional Andean, traditional Sub-Saharan, etc.
- **Public-health additions:** added-sugar limits, sodium ceilings, alcohol guidance, UPF warnings, trans fat thresholds
- **Recency tracking:** publication date, last revision, currently-under-revision status (e.g., US DGA 2025–2030 cycle)

## Out of scope (with reasons)

- Bulk ingestion of DRI tables — deferred to a later corpus-build phase (see Principle B in [README](../README.md))
- Food composition data — covered in [sweep #2](../02-food-composition-databases/scope.md)
- How recommendations should be communicated to users (the "why" delivery question) — covered in [sweep #8](../08-nutrition-education-delivery/scope.md)
- Cuisine-level eating patterns finer than national (regional / religious / diasporic) — partially covered in [sweep #3](../03-clinical-nutrition-assessment/scope.md), broad framework only

## Conflict resolution philosophy (for product surface)

When bodies disagree, the system uses **option C with geographic neutrality** (per [Constitutional Rule 9](../00-meta/constitutional-rules.md#rule-9--geographic-neutrality-in-evidence-surfacing)):

- Show the range of recommendations across bodies, **equal-weighted** regardless of country of origin
- Explain why bodies differ (methodology, population reference, evidence interpretation)
- **Do not default to or prioritize the user's home-country body.** Geographic location is a logistics data point, not a content filter.
- Always surface alternative dietary patterns and recommendations so the user understands their home country is one option among many — *"everybody's body is different, and they're going to handle these things differently, so we want to give them the options"*
- Apply [Constitutional Rule 1](../00-meta/constitutional-rules.md#rule-1--consult-a-professional): direct the user to a doctor or licensed nutritionist where authoritative bodies materially disagree

The presentation challenge — surfacing a multi-source global menu without overwhelming the user — is researched in [sweep #8](../08-nutrition-education-delivery/scope.md) (progressive disclosure, synthesis-with-expansion, comparative tables for depth-seeking users).

## Open questions for the research

- Which non-Western standards bodies have publicly accessible English-language documentation? Which require translation?
- Where do bodies materially disagree (>15–20% difference) on macronutrient or micronutrient targets, and what is the scientific basis for the disagreement?
- Which bodies have the most current evidence reviews vs. which are working off decades-old assumptions?
- Which bodies publish dietary pattern guidance vs. only nutrient-level DRIs?
- How do bodies handle sub-populations not well-represented in their underlying evidence base (e.g., older adults in DRI panels derived from younger-adult data)?

## Cross-references

- Bound by [Constitutional Rule 5 — international by default](../00-meta/constitutional-rules.md#rule-5--international-by-default-geographically-respectful)
- Bound by [Evidence Tiers](../00-meta/evidence-tiers.md) — DRIs from authoritative bodies are Tier 1
- Feeds [sweep #2 (food composition databases)](../02-food-composition-databases/scope.md) — geographic and body-publishing overlaps
- Feeds [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md) — DRIs are referenced in dietary assessment
- Feeds [sweep #8 (nutrition education / why delivery)](../08-nutrition-education-delivery/scope.md) — explanations rely on these standards
- Feeds [sweep #10 (clinical condition gating)](../10-clinical-condition-gating/scope.md) — condition-specific DRIs exist for many bodies

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
