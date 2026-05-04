# NutriMe — Publication Ambitions

> Active tracker of publication-grade contributions NutriMe is designed to make to the field. Distribution is primary personal-use (you + family + friends) **with active open-source / publication contribution as a co-equal design goal**. Documentation rigor, code quality, data-collection reproducibility, and license discipline are operated at publication standard from the start.

## Why active ambition rather than defer

User direction (2026-04-29, Stage 2 Tension #10):
> "Yeah, we're always designing with publication in mind, simply because we don't document to that degree. What's the point of doing it? We want to know; we want to have the data... I don't want to actively defer, though. I do want to have active publication ambitions, so we track and code to that degree."

The reasoning: the documentation rigor we're already operating at *is* publication-grade; deferring would waste that effort. Designing-for-publication from the start is cheaper than retrofitting a personal-use product later.

## Current publication targets

### 1. Open-source nutrition-specific intake chatbot

**Gap surfaced by:** [sweep #4 (adaptive intake agent)](../04-adaptive-intake-agent/scope.md). No published open-source nutrition-specific intake chatbot exists. The mental-health chatbot space (Woebot, Wysa, Tess, Limbic Access) is mature; nutrition is empty.

**What NutriMe contributes:** A consumer-friendly, methodology-borrowed conversational intake architecture (per [Tension #4 hybrid administration](synthesis.md#tension-4--consumer-friendly-clinical-instrument-vs-validity-preservation)) integrating validated screeners + non-validated-domain conversational elicitation + the iterative back-and-forth that broadens horizons over time.

**Design implications:** open the conversational architecture, not the user data. License decision deferred to architecture phase.

### 2. Hybrid LLM + CAT + structured-instrument open agent

**Gap surfaced by:** [sweep #4](../04-adaptive-intake-agent/scope.md). No published hybrid LLM + CAT + structured-instrument open agent exists. Each component is published; the composite design isn't.

**What NutriMe contributes:** Architecture + protocol for routing intake items between conversational LLM, IRT-driven CAT (using PROMIS public banks where available), and structured smart-branching forms. Plus the methodology-borrowing pattern for non-validated-instrument domains. This is the **strongest "novel" claim** in our publication portfolio.

**Design implications:** must document the routing logic, item bank usage, signal provenance tracking (per [knowledge-model.md](knowledge-model.md)), and per-mode elicitation patterns at publication-paper standard.

### 3. Consumer-facing GLIM screener

**Gap surfaced by:** [sweep #3 (clinical nutrition assessment)](../03-clinical-nutrition-assessment/scope.md). GLIM (Global Leadership Initiative on Malnutrition) is the cleanest example of geographic-neutrality harmonization in adult malnutrition diagnosis — but a consumer-facing GLIM screener does not appear to exist.

**What NutriMe contributes:** A consumer-friendly GLIM screener following the [Tension #4 hybrid administration](synthesis.md#tension-4--consumer-friendly-clinical-instrument-vs-validity-preservation) pattern (items preserved verbatim with conversational framing) — design that preserves psychometric validity while reducing friction for non-clinical use.

**Design implications:** narrow scope, well-defined deliverable. Could ship as a standalone artifact even before the broader system is mature.

### 4. Recipe time-feedback aggregate data

**Gap surfaced by:** [sweep #7 (cooking time + barriers)](../07-cooking-behavioral-barriers/scope.md). Recipe-stated-time vs. actual-cooking-time underreporting is a real but under-quantified gap in peer-reviewed literature.

**What NutriMe contributes:** Through the per-meal time-accuracy feedback (per [intake-pattern.md Mode 3](intake-pattern.md#mode-3--passive-confirmation--semantic-feedback)), NutriMe organically generates a dataset on recipe-stated vs. actual cooking time. With appropriate consent + anonymization, this becomes publishable data.

**Design implications:** data collection design must support reproducibility from the start (recipe identifier, user-confidence stratification, time-accuracy delta capture, optional demographic aggregation). Anonymization protocol + IRB-equivalent consent design needed before any data is shared. Not an immediate publication target — depends on user base size for statistical meaningfulness.

### 5. Cooking-state changes pairings — flavor-science aggregate data

**Gap surfaced by:** [sweep #14 (ingredient interactions)](../14-ingredient-interactions/scope.md). Cooking-state changes ingredient pairings (e.g., raw vs. cooked tomato + basil) — currently under-quantified in peer-reviewed flavor-science literature.

**What NutriMe contributes:** With per-meal semantic feedback capturing how meals made the user feel + the recipe's cooking-state metadata + ingredient-interaction tagging from sweep #14, NutriMe could generate aggregate data on user-perceived pairing satisfaction across cooking states. With sufficient sample size + appropriate anonymization, this becomes publishable food-science data.

**Design implications:** depends on (a) the same anonymization + consent infrastructure as target #4, (b) pairing-tradition + cooking-state metadata being on every recipe served (per the sweep #14 integration pass updates to sweep #11 metadata), (c) sufficient user base for statistical meaningfulness. Long-horizon target. Not immediate.

## Methodology principles

For all publication targets:

### Reproducibility-aware data collection

Per [architecture.md E1](architecture.md#e1--data-collection-schema-for-reproducibility), the schema is designed for reproducibility from day one:

- Every data field has documented collection methodology (per [intake-pattern.md provenance tagging](knowledge-model.md))
- Sample design choices documented at the architecture phase
- **Hybrid metadata scope** — universal minimum metadata (provenance + timestamp + version stamp) on every atom + composition + synthesized entry; expanded metadata (sample design, anonymization-ready fields, IRB-equivalent context) only for publication-eligible data
- **Dual versioning** — coarse system version on everything + fine component version stamped only when methodology actually changes
- **Dual drift detection** — schema versioning (automatic, queryable) + diff capture (one-time at change, reproducer-actionable detail) so we can characterize whether data collected at time T1 is comparable to data collected at time T2
- **Anonymization-ready schema** — schema separates identifying fields from analytic fields from the start; publication-prep logic handles edge cases
- **Dual data lineage** — derivation graph from epistemic trail captures data inputs + dedicated analysis metadata captures methodology that turned data into a result

### Anonymization + consent infrastructure

Per [architecture.md E2](architecture.md#e2--anonymization--consent-infrastructure):

- **Tiered standing-consent + per-publication-confirmation** — standing consent at intake establishes eligibility; per-publication confirmation gates each specific data release
- **Dual consent granularity** — per-data-category (atom type) AND per-publication-target; both must be eligible for inclusion
- **Three-layer anonymization** — direct identifier removal + quasi-identifier handling via k-anonymity (k=5 minimum) + inference-resistance review per publication
- **Just-in-time pre-publication review** — user sees the exact data going out before any publication ships + can edit / exclude / cancel
- **Full audit trail** of all publications — historical record per Rule 8 epistemic trail
- **Right to withdraw** — future-publication blocking + re-publication exclusion in next revision; past publications stay as honest historical record (superseded with caveat, not recalled)

### License + attribution clarity from the start

Per [architecture.md E3](architecture.md#e3--license-decisions-per-publication-target), license decisions are settled:

- **Apache 2.0** for publishable architectural / methodological code (publication targets #1 + #2 + #3) — explicit patent grant matters in LLM-agent patent landscape; permissive; established for backend / library code
- **MIT** acceptable for small reusable utilities outside NutriMe-specific architecture
- **AGPL not adopted** — copyleft overkill for personal-use-primary distribution
- **CC-BY 4.0** for documentation — attribution required, otherwise free reuse
- **CC-BY 4.0** for aggregate data publications (#4 + #5) — consistent with documentation; attribution maintains citation-trail discipline; no share-alike copyleft to deter downstream use
- **License recorded at consent time** per E2 — license is part of the user's consent record; license change requires re-confirmation
- **Standard license requirements + recommended citation format** published alongside each artifact (Cochrane / GRADE / PROMIS pattern)
- Attribution pipelines preserved through transformations (per [sweep #11 attribution architecture](../11-recipe-sourcing/scope.md))

### Publication-grade documentation discipline

- Already operating at this level per [feedback_documentation_discipline](../../.claude/projects/-Users-b-sayer-src/memory/feedback_documentation_discipline.md) (sweep folders, citation style, sources index, bidirectional cross-refs)
- Methodology sections must be writeable — design choices justified with citations + rationale, not just code comments
- Limitations sections honest about evidence floors, sample sizes, generalizability

### Code quality bar

- Architecture-phase decisions consider open-source contribution from day 1
- Test coverage for published components beyond personal-use minimum
- Documentation of API surface for any published component

## What publication does NOT change

- **Bounded-role principle still applies** — we publish what we can defensibly publish. We do NOT overreach into clinical-claim territory beyond [Rule 7 peer-reviewed floor](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor).
- **Personal-use is still primary** — publication is co-equal but doesn't crowd out the actual use case. The system is built to be useful first; publication-readiness is a discipline, not a goal that distorts product decisions.
- **Privacy + Rule 6 (health data local)** — publishable data is anonymized, aggregated, and consented. We don't publish personally-identifiable clinical or wearable data ever, regardless of publication ambition.
- **Audit-as-education + epistemic-trail discipline** — apply to publication targets too. We publish what we can stand behind with the same rigor we surface to users.

## Process for adding new targets

When research, design, or build organically surfaces a publishable gap:

1. Document the gap (what's missing in the field, why)
2. Document NutriMe's contribution (what we have / will have that fills it)
3. Document design implications (data collection requirements, methodology choices needed)
4. Add to the "Current publication targets" section above
5. Note dependencies (some targets depend on user base size, system maturity, etc.)

## Related

- [synthesis.md Tension #10](synthesis.md#tension-10--novel-synthesis-publication-ambition) — full Stage 2 resolution
- [product-framing.md distribution intent](product-framing.md#target-user) — updated for active publication ambition
- [roadmap.md](roadmap.md) — broader-scope futures + verification pass + open tensions tracker
