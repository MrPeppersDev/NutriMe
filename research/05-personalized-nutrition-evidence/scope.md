# Sweep #5 — Personalized Nutrition — Evidence Audit

> Status: Scoped
> Last updated: 2026-04-28

## Purpose

Honest tier-by-claim audit of personalized nutrition science across the major commercial and academic strands: PREDICT / ZOE, Food4Me, microbiome-based personalization, nutrigenomics, metabolomics, and CGM-for-non-diabetics. Establish what evidence supports each claim vs. what vendors market. Output serves dual purpose: (1) gates which personalization mechanisms can drive system behavior under the [peer-reviewed floor](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor), and (2) becomes "audit-as-education" content per [evidence-tiers.md](../00-meta/evidence-tiers.md#audit-as-education-pattern).

## Deliverable

A per-domain evidence audit table with:

- Domain (e.g., "CGM-driven meal personalization for non-diabetics")
- Best Tier 1 evidence (if any)
- Best Tier 2 evidence (systematic reviews, meta-analyses)
- Representative Tier 3 evidence (RCTs, cohort studies)
- Tier 4 marketing-vs-evidence gap (vendors, marketed claims)
- **Steel-man counter-evidence** — strongest published case that the personalization mechanism adds little over good population-level guidance
- Verdict against NutriMe's evidence floor: drives system behavior? Educational-content-only? Excluded?
- Notes on n-of-1 study designs relevant to NutriMe's [semantic feedback loop](../00-meta/intake-pattern.md#mode-3--passive-confirmation--semantic-feedback)

Format is flexible — research findings may justify expansion (additional domains, methodological subsections, international initiative summaries).

This is a **reference map**, not corpus build. Audit produces the evidence summaries; ingestion of underlying datasets/studies happens later.

## Domains in scope

- **PREDICT / ZOE** — large cohort with CGM, gut microbiome, postprandial response measurement
- **Food4Me** — EU-funded RCT of personalization based on questionnaires + biomarkers + genetics
- **Microbiome-based personalization** — Viome, ZOE microbiome component, DayTwo, academic literature
- **Nutrigenomics** — DNAFit, Nutrigenomix, 23andMe-derived diets, academic literature
- **Metabolomics-based personalization** — InsideTracker (blood biomarkers), commercial blood-test-driven diets
- **CGM-for-non-diabetics** — Levels, Nutrisense, Stelo (Dexcom OTC), academic literature on glucose response variability — **stretch goal at reference level**, not primary
- **N-of-1 study designs in nutrition** — small but growing literature; relevant to how the semantic feedback loop is designed
- **Steel-man literature** — strongest published evidence that personalization adds little over good population guidance (Beresford 2006, others)
- **International initiatives** — UK NHS personalized nutrition pilots, EU Horizon programs, Chinese precision-nutrition initiatives, Israeli Weizmann work (Segal lab — major center)

## Geographic scope

Per [geographic-scope.md](../00-meta/geographic-scope.md) — primary is US, EU, UK, AU, NZ, Canada, China, Japan, Korea, Israel, Russia. Opportunistic inclusion of Nordic countries, India, Brazil, Singapore, and others where notable work surfaces. Per user direction this list is not a hyperfocus — research follows the evidence wherever it's strong.

## Audit-as-education framing

Per user direction: even where personalization mechanisms fail the evidence floor and cannot drive system behavior, the audit itself becomes educational content presented to users. Topics that fall into this category (microbiome, nutrigenomics, metabolomics, fad-diet personalization) are covered honestly: what they claim, what the evidence actually shows, why NutriMe does or does not use them.

This dual purpose shapes how findings should be written — accessible enough to become user-facing educational copy, rigorous enough to back system-behavior decisions.

## Out of scope (with reasons)

- Implementation of personalization mechanisms — that's later phase
- Wearable / biometric *data availability* — covered in [sweep #6](../06-wearable-data-availability/scope.md). Sweep #6 = "what data exists and is reliable"; sweep #5 = "should we act on it"
- General population-level dietary guidance — covered in [sweep #1](../01-international-nutrition-standards/scope.md)
- Bulk ingestion of trial data — deferred

## Open questions for the research

- For each domain: what is the best Tier 2 evidence? Is there ANY Tier 1 evidence?
- What is the strongest published steel-man against personalization adding meaningful value over population guidance?
- For CGM-driven personalization, what does the evidence say about whether postprandial glucose variability translates to meaningful long-term outcomes?
- What does the n-of-1 design literature in nutrition look like, and how could it inform the semantic feedback loop?
- Where are international initiatives moving — is the EU's Horizon precision-nutrition work converging with US/UK approaches, or diverging?
- For microbiome / nutrigenomic / metabolomic testing, where exactly does the marketing diverge from the evidence?

## Cross-references

- Sister sweep to [sweep #6 (wearable data availability)](../06-wearable-data-availability/scope.md) — #6 = data substrate, #5 = should-we-act-on-it evidence
- Bound by [Constitutional Rule 7 (peer-reviewed floor)](../00-meta/constitutional-rules.md#rule-7--peer-reviewed-evidence-floor)
- Bound by [evidence-tiers.md](../00-meta/evidence-tiers.md), especially the [audit-as-education pattern](../00-meta/evidence-tiers.md#audit-as-education-pattern)
- N-of-1 findings cross-reference [intake-pattern.md](../00-meta/intake-pattern.md) — semantic feedback loop design
- Cross-references [sweep #1 (international nutrition standards)](../01-international-nutrition-standards/scope.md) — population-level baseline against which personalization is measured

## Findings

To be populated when research is run.

## References

To be populated. Add new sources to [sources.md](../00-meta/sources.md) when added.
