# NutriMe — Research Index

This directory holds all research for the NutriMe project. Research is organized into numbered **sweeps** (research branches), each in its own folder. Cross-cutting principles, frames, and conventions live in `00-meta/`.

We are currently in **Stage 1: scoping and parallel research**. No code, no architecture decisions. Research outputs become the substrate for later library / corpus / system design work.

## Read these first

- [Product framing](00-meta/product-framing.md) — what NutriMe is and explicitly is not, including distribution intent
- [Constitutional rules](00-meta/constitutional-rules.md) — 10 non-negotiable safety + disclosure rules
- [Evidence tiers](00-meta/evidence-tiers.md) — how nutrition evidence is graded and surfaced
- [Intake pattern](00-meta/intake-pattern.md) — iterative onboarding + passive confirmation + semantic feedback model
- [Epistemic trail](00-meta/epistemic-trail.md) — how the system shows its work for AI-correlated inferences
- [Dynamic research expansion](00-meta/dynamic-research-expansion.md) — system capability for fetching + verifying public information when corpus has gaps
- [Knowledge model](00-meta/knowledge-model.md) — first-class system data layer (per-user + per-household) holding what's been delivered, experienced, preferred
- [User decision framework](00-meta/user-decision-framework.md) — how the system handles conflicts between user requests and its knowledge (surface + let user decide)
- [Geographic scope](00-meta/geographic-scope.md) — primary audience vs. broader research scope, with geographic-neutrality principle
- [Synthesis](00-meta/synthesis.md) — Stage 2 cross-cutting decisions resolving research-surfaced tensions
- [Publication ambitions](00-meta/publication-ambitions.md) — active tracker of publication-grade contributions NutriMe is designed to make to the field
- [Stage 3+ comprehensive plan](00-meta/stage3-plan.md) — full path from current state through architecture, MVP, build, iteration, and parallel tracks; downstream-impact callouts
- [Architecture decisions](00-meta/architecture.md) — Stage 3 architecture decisions as they resolve (sister doc to synthesis.md)
- [Schema design](00-meta/schema.md) — Stage 3.5 schema-design decisions (sister doc to architecture.md)
- [Provider abstraction](00-meta/provider-abstraction.md) — LLM provider agnosticism principle; capability-vector routing
- [PHI handling](00-meta/phi-handling.md) — operational doc for cloud LLM use under HIPAA-discipline posture; query-level decomposition principle
- [Preservation layer](00-meta/preservation-layer.md) — NutriMe as archival preservation when sources disappear (per Stage 3 E4 refinement)
- [Roadmap](00-meta/roadmap.md) — living tracker of open tensions, stretch goals, deferred items, and broader-scope futures
- [Citation style](00-meta/citation-style.md) — citation format and cross-reference conventions
- [Sources index](00-meta/sources.md) — navigational index of source coverage across sweeps

## Research sweeps

| # | Sweep | Status | Folder |
|---|-------|--------|--------|
| 1 | International nutrition reference standards | Scoped | [01-international-nutrition-standards/](01-international-nutrition-standards/) |
| 2 | Food composition databases — multi-source landscape | Scoped | [02-food-composition-databases/](02-food-composition-databases/) |
| 3 | Clinical nutrition assessment methodology | Scoped (final screener set TBD) | [03-clinical-nutrition-assessment/](03-clinical-nutrition-assessment/) |
| 4 | Adaptive intake agent design — clinical decision support | Scoped | [04-adaptive-intake-agent/](04-adaptive-intake-agent/) |
| 5 | Personalized nutrition — evidence audit | Scoped | [05-personalized-nutrition-evidence/](05-personalized-nutrition-evidence/) |
| 6 | Wearable & biometric data — availability, access, signal quality | Scoped | [06-wearable-data-availability/](06-wearable-data-availability/) |
| 7 | Cooking time, food skills, behavioral barriers | Scoped | [07-cooking-behavioral-barriers/](07-cooking-behavioral-barriers/) |
| 8 | Nutrition education and "why" delivery | Scoped | [08-nutrition-education-delivery/](08-nutrition-education-delivery/) |
| 9 | Multi-user / household nutrition planning | Scoped | [09-multi-user-household/](09-multi-user-household/) |
| 10 | Clinical condition gating + safety surface | Scoped | [10-clinical-condition-gating/](10-clinical-condition-gating/) |
| 11 | Recipe sourcing, licensing, attribution, distribution | Scoped | [11-recipe-sourcing/](11-recipe-sourcing/) |
| 12 | Skills-by-cuisine mapping | Scoped | [12-skills-by-cuisine/](12-skills-by-cuisine/) |
| 13 | Grocery sourcing, ordering, and delivery infrastructure | Scoped | [13-grocery-infrastructure/](13-grocery-infrastructure/) |
| 14 | Ingredient interactions, flavor science, and pairing knowledge | Researched + integration pass applied (2026-05-01) | [14-ingredient-interactions/](14-ingredient-interactions/) |

## Cross-reference map

Sweeps don't sit in isolation. Notable known overlaps:

- **#1 ↔ #2** — DRI standards and food composition databases share geographic scope (top 150 countries) and frequently share publishing bodies
- **#3 ↔ #4** — Clinical assessment methodology informs what an adaptive intake agent must be able to elicit
- **#3 ↔ #7** — Cooking confidence + equipment screeners in #3 are informed by #7's literature
- **#3 ↔ #10** — Safety screeners in #3 feed condition-gating logic in #10
- **#5 ↔ #6** — Wearable data availability (#6) is the substrate; whether we should act on a given signal is the evidence question (#5)
- **#7 ↔ #8** — Cooking-time barriers and behavior-change literature overlap heavily
- **#7 ↔ #11** — Cooking confidence + time perception drives recipe complexity tiering and presentation modality
- **#7 ↔ #12** — Equipment + skills + cuisine bindings sit between #7 (general barriers) and #12 (cuisine-specific mapping)
- **#11 ↔ #12** — Recipe selection depends on user skill ↔ cuisine matrix
- **#11 ↔ all** — Recipe sourcing is downstream of every nutrition-substrate decision
- **#14 ↔ #2** — Pairing-corpus ingredient identity resolves via composition-database authority table
- **#14 ↔ #11** — Pairing knowledge informs recipe ranking + substitution logic
- **#14 ↔ #12** — Technique-pairing-cuisine bindings (tadka enables Indian pairings, sofrito enables Latin pairings)
- **#14 ↔ #13** — Substitution logic informed by pairing science

Cross-references inside docs use relative markdown links and should be added in both directions when a connection is identified.

## How to add a new sweep

1. Copy [00-meta/SWEEP-TEMPLATE.md](00-meta/SWEEP-TEMPLATE.md) into a new numbered folder
2. Fill in scope.md following the template
3. Add the sweep to the table above with status
4. Add cross-references to / from related sweeps
5. Add any sources to [00-meta/sources.md](00-meta/sources.md) so we don't duplicate URL tracking
