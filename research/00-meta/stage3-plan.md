# NutriMe — Stage 3+ Comprehensive Plan

> Living plan covering everything from current state (Stage 1 + 2 complete) through architecture, MVP, build, iteration, and parallel publication / corpus-build tracks. Updates as decisions land and scope changes.

## Where we are (2026-04-29)

- **Stage 1 (research)** — complete. 13 sweeps populated; sources.md consolidated; 16 commits on `origin/main`.
- **Stage 2 (synthesis)** — complete. All 13 cross-cutting tensions resolved in `synthesis.md` (one positively reversed mid-stream).
- **Architecture / build** — not started. Active publication ambition confirmed (`publication-ambitions.md`).

## Stage sequence

| Stage | What | Cadence | Depends on |
|---|---|---|---|
| **3** | Architecture / system design dialogue | Topic-by-topic with clarifying questions, captured in `architecture.md`. **Block A revised 2026-06-29** (A1-v2/A2-v2/A3-v2 + MVP-host refinement) — see [architecture.md Block A revision](architecture.md#block-a-revision--2026-06-29). | Stage 2 |
| **3.5** | Schema-design phase | All S1–S12 sub-blocks resolved 2026-05-03 → 2026-05-06, captured in `schema.md`. **F9 (tenant_id axis) reopened by A1-v2** — awaits an S13 follow-up sweep before Stage 4 build can begin. | Stage 3 |
| **4** | MVP scoping | Single dialogue once Stage 3 + 3.5 settle, captured in `mvp.md`. **Blocked on F9/S13 resolution.** | Stage 3 Blocks A + B + C; Stage 3.5 (including S13 F9 resolution) |
| **5** | Pre-corpus-build verification pass | Re-run wave-1/2/3 sweeps with live web tools to refresh time-sensitive details (per roadmap) | Web-tool availability |
| **6** | Build phase 1 — MVP implementation | Iterative build; commits per merged feature | Stages 3 + 4 + 5 |
| **7** | Use + iterate | Real use surfaces real findings; roadmap stays alive | Stage 6 |

**Parallel tracks** that can run alongside:
- **Publication target development** — first target (probably consumer-facing GLIM screener — narrowest standalone) can begin as soon as Stage 3 Block C decisions land
- **Corpus build phases** — can begin as soon as Stage 3 Block B (knowledge + retrieval) decisions land

---

## Stage 3 — Architecture / system design dialogue

Mirrors the Stage 2 cadence: topic-by-topic, my proposals with tradeoffs, your decisions, captured in a new `00-meta/architecture.md`. Five blocks below, ordered so each block's decisions are unblocked by the previous block's resolutions.

### Block A — Foundation (constrains everything)

Most cross-cutting decisions. Must be first. **Block A revised 2026-06-29** — A1/A2/A3 superseded by A1-v2/A2-v2/A3-v2 + two-tier hardware refinement; originals preserved in [architecture.md](architecture.md) as historical record; A4 unchanged. See [architecture.md Block A revision](architecture.md#block-a-revision--2026-06-29).

| # | Decision | Notes | Downstream impact | Status |
|---|---|---|---|---|
| A1 | **Deployment model** — *originally* pure local-first single-device; **revised to multi-tenant home server (A1-v2)** | A1 resolved 2026-04-29 as single-device. **A1-v2 (2026-06-29)** lands multi-tenant local home server for family-of-4 baseline + eventual syndication; PHI never leaves household network in steady state. **Two-tier refinement:** ≥64 GB Mac-class is the production target; MVP runs on the user's existing MBP M4 Pro 24 GB (also their primary work machine). Opens F9 schema axis (`tenant_id`). | Cascades to A2, A3, A4, all of Block D, the entire data-flow design | ✅ Resolved → revised A1-v2 |
| A2 | **Application shell** — *originally* native macOS app primary; **revised to iPhone-first client + Mac home server (A2-v2)** | A2 resolved 2026-04-29 as native macOS primary. **A2-v2 (2026-06-29)** demotes native macOS to optional admin/dev surface; iPhone app becomes the primary client; Mac server hosts substrate + corpus + LLM daemon + orchestration. HealthKit-on-iOS is structural fit for D1. | Affects intake UX, recipe presentation rendering (C4), HealthKit integration path (D1), now adds client/server transport surface | ✅ Resolved → revised A2-v2 |
| A3 | **LLM provider + privacy posture** — *originally* Anthropic + Google primary; **revised to OSS local primary + narrow cloud fallback (A3-v2)** | A3 resolved 2026-04-29 as Anthropic Claude + Google Gemini cloud-primary with query-level PHI decomposition. **A3-v2 (2026-06-29)** lands OSS local primary (Qwen3-32B Apache-2.0 via Ollama 0.19+ MLX) + narrow Claude Sonnet 4.x fallback for three dimensions only (adversarial robustness / >64K context / low-resource cuisine languages); DeepSeek V3.x do-not-use for constitutional enforcement; hardcoded constitutional rule layer outside any LLM; FoodyLLM-style domain fine-tunes. **MVP refinement:** cloud-primary at the 24 GB MVP host tier (Qwen3-32B Q4_K_M doesn't fit); OSS-local-primary kicks in at production target. PHI-decomposition discipline preserved across both tiers. | Constrains C1, C2, Block B retrieval orchestration, all educational content surfaces | ✅ Resolved → revised A3-v2 |
| A4 | **Data persistence + knowledge model storage** — hybrid: SQLite for substrate + operational, markdown vault for corpus | Resolved 2026-04-30 across Q4.1–Q4.4. Three-layer architecture (substrate / operational / corpus); LC + CKV patterns adopted (12 patterns total); atoms-with-molecules-refinement organizing principle for substrate. Full decision in [architecture.md A4](architecture.md#a4--data-persistence--knowledge-model-storage). **Unaffected by Block A revision.** | Constrains B1 (RAG architecture), B2 (provenance), B4 (schema), every data-write code path | ✅ Resolved |

### Schema design — Stage 3.5 deliverable between Blocks B and C

Per the [A4 schema-design overhead risk](architecture.md#a4--data-persistence--knowledge-model-storage) + [B4 architecture-level decision with explicit flags](architecture.md#b4--knowledge-model-schema-architecture-level), the schema-design phase has these explicit deliverables:

1. **Resolve the 8 B4 lower-confidence flags (F1–F8)** — asynchrony / temporal state model; household-vs-user subject boundary; corpus-vs-substrate boundary for system-generated shareable content; user-correction handling; generic `inference` catch-all; possible type merges (`dietary_pattern_assessment` ↔ `screener_result` and `audit_as_education_content` ↔ `educational_recommendation`); `provenance_chain` as relationship vs. computed view; possibly-overengineered atoms reconsideration
2. Define detailed table layouts (column definitions, types, constraints, defaults)
3. Define indexes (especially the `(source_id, type, target_id)` + `(target_id, type, source_id)` relationship indexes for graph traversal)
4. Define foreign key + referential integrity rules
5. Define migration strategy preserving bitemporal-immutability discipline
6. Define `KnowledgeEntry` base table vs. type-specific table normalization approach
7. Define the verification rule-set (per [B2](architecture.md#b2--rule-8-epistemic-trail-implementation))
8. Define the embedding-table layout (`embeddings_voyage_*` + `embeddings_local_*` per [B1 Q1.3](architecture.md#b1--semantic-rag-vs-structured-query-strategy))

Captured in a future `schema.md` once Block C dialogue surfaces additional schema requirements (intake agent + recipe presentation + daily-cadence model all touch the schema).

### Block B — Knowledge + retrieval (data flow)

Depends on Block A. Defines how the system actually thinks.

| # | Decision | Notes | Downstream impact |
|---|---|---|---|
| B1 | **Semantic RAG vs. structured query strategy** — three-mode retrieval (vector + FTS5 + structured-relational); filter-then-rank default; embed-for-retrieval-deliver-source principle; Voyage primary embedding + local model for PHI only | Resolved 2026-05-01 across Q1.1–Q1.4. Full decision in [architecture.md B1](architecture.md#b1--semantic-rag-vs-structured-query-strategy). | Affects retrieval quality + cost; constrains education delivery (Block C) and dynamic-research-expansion (B3) |
| B2 | **Rule 8 epistemic trail implementation** — substrate derivation graph + operational event log; structured + narrative reasoning capture; hybrid rule-based + LLM-causal-explanation verification; layered-disclosure rendering; stored at inference time with on-demand reconstruction fallback | Resolved 2026-05-01 across Q2.1–Q2.5. Full decision in [architecture.md B2](architecture.md#b2--rule-8-epistemic-trail-implementation). | Constrains every user-facing inference surface; affects publication-target #4 reproducibility |
| B3 | **Dynamic research expansion infrastructure** — hybrid reactive + proactive gap detection; hybrid explicit + LLM-extraction source adapters; both source-specific + centralized verification; per-content-type TTLs + change-triggered re-fetch; cascade failure with partial-success rebuild; fixed-N exponential backoff retries | Resolved 2026-05-01 across Q3.1–Q3.5c. Full decision in [architecture.md B3](architecture.md#b3--dynamic-research-expansion-infrastructure). | **Likely impacts downstream understanding most of any architecture decision** — dictates what gaps get filled how, when. Touches every domain (drugs, conditions, cuisines, ingredients, regulatory). |
| B4 | **Knowledge model schema (architecture-level)** — three confidence concepts (system / evidence-tier / user-facing-certainty) with deterministic mapping; 17 atom + 8 molecule + 16 synthesized types + 7 typed relationships + bitemporal lifecycle. **Architecture-level decision; ~70% confidence; 8 flags (F1–F8) explicitly deferred to schema-design phase for deeper review.** | Resolved 2026-05-01 across Q4.1–Q4.4. Full decision in [architecture.md B4](architecture.md#b4--knowledge-model-schema-architecture-level). | Constrains C1 (intake agent), C3 (hybrid administration), C5 (daily cadence interaction), all Block D integrations writing to it |

### Block C — Intake + interaction (user-facing)

Depends on A + B. Defines the user experience.

| # | Decision | Notes | Downstream impact |
|---|---|---|---|
| C1 | **Conversational intake agent architecture** — hybrid orchestrator + bounded sub-agents; structured tool call default; hybrid operational+substrate state; double-layer PHI enforcement; **LLM provider agnosticism** via capability-vector routing | Resolved 2026-05-01 across Q1.1–Q1.5. Full decision in [architecture.md C1](architecture.md#c1--conversational-intake-agent-architecture). New foundational meta doc: [provider-abstraction.md](provider-abstraction.md). | Affects every dialog surface, agent-to-agent handoff complexity, latency, cost |
| C2 | **CAT / IRT integration** — existing CAT engine (engine choice deferred to build); PROMIS banks downloaded locally for A1-compliant CAT execution; two parallel delivery paths (PROMIS adaptive + classical sum-score) both producing screener_result atoms; bitemporal + item-bank version stamping; invisible adaptive nature + explicit early-stopping notification with user agency | Resolved 2026-05-01 across Q2.1–Q2.5. Full decision in [architecture.md C2](architecture.md#c2--cat--irt-integration). | Affects intake quality + measurement validity; feeds B4 knowledge model with `validated-instrument` provenance |
| C3 | **Hybrid administration UX** — items rendered by application (LLM never produces item text); curated clarification corpus per validated instrument; pause-anywhere with core-service access during incomplete intake + caveat surfacing; templated framing with variable slots; double validation (pre-render + post-hoc) on LLM-generated framing | Resolved 2026-05-01 across Q3.1–Q3.5. Full decision in [architecture.md C3](architecture.md#c3--hybrid-administration-ux). | Affects intake completion rates, validity preservation, user friction |
| C4 | **Multi-modal recipe presentation rendering** — hybrid modality availability with fallback chain + user filter; embed video inline by default + deep-link option; inline tooltip for terminology lookup with text + linked demo video (cross-domain pattern); render-time at MVP; full-range presentation with context-conditional selection tracking, NOT pre-filtered by perceived skill | Resolved 2026-05-01 across Q4.1–Q4.5. Full decision in [architecture.md C4](architecture.md#c4--multi-modal-recipe-presentation-rendering). | Affects sweep #11 implementation, glossary infrastructure, cooking-confidence personalization fidelity |
| C5 | **Daily-cadence interaction model** — adaptive primary home-screen (time-of-day + recent activity); user-configurable per-category notifications default material-only; two-stage feedback (immediate cooking-experience + later body-response); dual-mode epistemic trail; quick-actions including new "reorient tonight's meal" life-happens affordance | Resolved 2026-05-01 across Q5.1–Q5.5. Full decision in [architecture.md C5](architecture.md#c5--daily-cadence-interaction-model). | Affects user retention, education delivery cadence, knowledge model update timing |

### Block D — External integrations

Largely parallel-doable within itself once Block A lands. Each constrains specific features.

| # | Decision | Notes | Downstream impact |
|---|---|---|---|
| D1 | **Wearable + biometric aggregation** — HealthKit primary + direct vendor APIs as second-pass; MVP-priority data type set; HealthKit background delivery + polling backup; hybrid pre-computed common constraints + on-demand uncommon; validation metadata + runtime confidence weighting | Resolved 2026-05-01 across Q1.1–Q1.5. Full decision in [architecture.md D1](architecture.md#d1--wearable--biometric-aggregation). | Constrains personalization sophistication; constrains Tension #5 abstracted-constraint-layer inputs |
| D2 | **Doctor-portal patient API integration** — three-path data flow (Apple Health Records primary + direct EHR adapters second-pass + manual upload always available); US-API-first MVP scope; substrate-extracted + corpus-preserved-source-documents with **per-document encryption for clinical source documents specifically** (Keychain-stored key, Secure Enclave-backed); **NutriMe doesn't diagnose — surfaces trends, defers to clinician** | Resolved 2026-05-01 across Q2.1–Q2.5. Full decision in [architecture.md D2](architecture.md#d2--doctor-portal-patient-api-integration). | **Likely impacts downstream understanding** — clinical-grade data unlocks meaningful condition gating + lab-driven personalization |
| D3 | **Grocery cart-aggregation integration** — three-layered cart-construction flow; combined-gate substitution authorization (pre-approved rules + system-mediated constraints + real-time approval for judgment calls only); cart hand-off only at MVP (Instacart IDP recipe-link); both periodic polling + user-initiated refresh; mechanical inheritance of sweep #13 six-tier graceful-degradation. Hong Kong / Chinese market deferred to broader-scope-future. | Resolved 2026-05-02 across Q3.1–Q3.5. Full decision in [architecture.md D3](architecture.md#d3--grocery-cart-aggregation-integration). | Constrains the "boom shows up at my door" promise; affects user satisfaction with the convenience layer |
| D4 | **Recipe source integration** — open-source-only MVP (TheMealDB + Project Gutenberg PD historical + open datasets; paid sources deferred); canonical Cooklang on ingest; best-effort ingredient identity resolution with user-review flag (operational nuance to schema-design phase); source-coherent multi-modality only (no cross-source compositing); mechanical inheritance with quiet-update + surface-on-next-view refinement | Resolved 2026-05-02 across Q4.1–Q4.5. Full decision in [architecture.md D4](architecture.md#d4--recipe-source-integration). | Constrains recipe corpus breadth + multi-modal availability; affects horizon-broadening fidelity |

### Block E — Reproducibility + publication infrastructure

Largely parallel after Block A. Informs design choices throughout.

| # | Decision | Notes | Downstream impact |
|---|---|---|---|
| E1 | **Data collection schema for reproducibility** — hybrid reproducibility scope (universal minimum + expanded for publication-eligible); dual versioning (coarse system + fine component); dual drift detection (schema versioning + diff capture); anonymization-ready schema + publication-prep logic; dual data lineage (epistemic-trail-inherited + dedicated analysis metadata) | Resolved 2026-05-03 across Q1.1–Q1.5 (all five resolved to "both"). Full decision in [architecture.md E1](architecture.md#e1--data-collection-schema-for-reproducibility). | Constrains B4 schema + every data-capture surface; foundational for publication targets #4 (recipe time-feedback) + #5 (cooking-state changes pairings) |
| E2 | **Anonymization + consent infrastructure** — tiered standing-consent + per-publication-confirmation; dual granularity (per-data-category + per-publication-target); three-layer anonymization (direct identifier removal + k-anonymity k=5 + inference-resistance review); just-in-time pre-publication review + full audit trail; right to withdraw via re-publication exclusion + future-publication blocking | Resolved 2026-05-03 across Q2.1–Q2.5. Full decision in [architecture.md E2](architecture.md#e2--anonymization--consent-infrastructure). | Affects every publication-eligible data path; enables vs. blocks open-science contributions |
| E3 | **License decisions per publication target** — Apache 2.0 for publishable architectural / methodological code (MIT for small utilities; AGPL not adopted); CC-BY 4.0 for documentation; CC-BY 4.0 for aggregate data publications; license recorded at consent time bound to consent record per E2; standard license requirements + recommended citation format | Resolved 2026-05-03 across Q3.1–Q3.5. Full decision in [architecture.md E3](architecture.md#e3--license-decisions-per-publication-target). | Affects open-source distribution clarity; constrains future commercial paths if user ever broadens distribution intent |
| E4 | **Update cadence + corpus refresh design** — hybrid trickle + scheduled batch refresh; automatic with user-controllable overrides; partial-success cycles per B3 cascade-failure; staleness indicator + material-implication callout PLUS **NutriMe-as-preservation-layer principle** when sources disappear (own meta doc); both Stage 5 one-time + ongoing **quarterly (3-month) re-verification cycles** | Resolved 2026-05-03 across Q4.1–Q4.5. Full decision in [architecture.md E4](architecture.md#e4--update-cadence--corpus-refresh-design). | **Likely impacts downstream research understanding** — defines how the corpus stays current vs. drifts; affects Stage 5 verification pass cadence going forward |

---

## Stage 4 — MVP scoping (in progress, opened 2026-06-29)

Single focused dialogue to pick the smallest useful end-to-end slice. **Opened 2026-06-29** once F9 (tenant_id axis) resolved via the S13 mini-sweep — see [schema.md F9](schema.md) for the locked-in tenant-axis decisions that constrain MVP shape.

The MVP must reflect the **two-tier hardware posture** from the A1-v2 refinement: scoped against the 24 GB MBP M4 Pro MVP host (cloud-primary reasoning per A3-v2 refinement), not the ≥64 GB production target. F9 closure means MVP code is multi-tenant-aware from day one (single tenant row at MVP; family-of-4 rows post-migration) — no tenant-unaware MVP technical debt.

### MVP shape (Q1 resolved 2026-06-29; remaining sub-questions still in flight)

**MVP includes:**
- Intake (validated-screener hybrid administration for the **MVP trio** — PHQ-2 + GAD-2 + Hunger Vital Sign — plus demographics + life-stage + dietary preferences + allergens) *(Q1)*
- Inventory awareness (initial intake + ongoing observation)
- Meal-plan generation (Tier 1/2 nutrition guidance + **open-source-only recipe sourcing** per D4: TheMealDB free-tier + Project Gutenberg PD historical + open datasets; paid sources deferred) *(Q1)*
- Grocery list (Instacart cart-aggregation when US-located, list-export fallback otherwise)
- Per-meal feedback (semantic + time-accuracy)
- Honest disclosure surfaces (consult-professional, evidence-tier, audit-as-education)

**MVP defers:**
- **Additional intake instruments — PSQI short, AUDIT-C, CCSS — defer to v0.2** *(Q1)*. PSQI short is the first to re-add if the MVP trio under-captures nutrition-actionable signal (sleep affects appetite regulation).
- **Commercial recipe APIs (paid sources)** *(Q1, per D4)*. MVP stays open-source-only; commercial API integration is post-MVP.
- Full knowledge model evolution (start with simple per-user + household; iterate)
- Multi-modal recipe presentation infrastructure (text + linked YouTube video; defer in-app video rendering, illustrated rendering, real-time terminology lookup glossary)
- Audit-as-education depth (start with consult-professional + evidence-tier surfacing; defer comprehensive educational corpus)
- All four publication targets — design-aware but no active push *(Q6 will lock this; placeholder here for the MVP-defers picture)*
- **Multi-user household UI** (tenant switcher, household-name labels, "switch tenant" affordance) defers to v0.2+ *(Q3)*. Schema + queries + `tenant` lifecycle table ARE multi-tenant from day one per Q3 resolution; only the UI surface stays single-context at MVP.
- Wearable signal interpretation (start with intake-only; add wearable in v0.2)

**Why this MVP:** ships a thing you'd actually use, validates the core meal-planning loop + inventory awareness + grocery integration, captures real data for the publication-#4 target without committing to the full-publication apparatus yet. The Q1 trim — MVP trio of screeners + open-source-only recipes — keeps the intake surface short enough that real onboarding completes, and removes the licensing/cost surface that paid recipe APIs introduce. PSQI short is the named re-add candidate so MVP→v0.2 expansion has a clear first move if signal-capture turns out thin.

### Six sub-questions to resolve

Each sub-question gets its own focused dialogue + per-resolution commit (per working-style: don't batch decisions). Confidence ratings are honest first-pass calibrations; "land but revisit during build" applies to any judgment-call answer (the F9/S13 mini-sweep pattern).

**S4-Q1: Is the starting-proposal MVP scope correct?** *(resolved 2026-06-29 — confidence was ~75%)*
- **Tensions:** (1) starting proposal said "1–2 commercial APIs" for recipe sourcing, but D4 already settled **open-source-only MVP** for recipe sources (TheMealDB + Project Gutenberg PD + open datasets) — the proposal text was stale; (2) 5–10 screeners is too much intake friction for MVP onboarding completion — needed the smallest screener set that's actionable in the MVP meal-plan loop.
- **Resolution:** **(a)** drop "1–2 commercial APIs" — MVP recipe sources = open-source-only per D4 (high confidence: alignment fix, not a new decision); **(b)** narrow intake instruments to the **MVP trio (PHQ-2 + GAD-2 + Hunger Vital Sign)** plus demographics/life-stage/dietary preferences/allergens; defer **PSQI short / AUDIT-C / CCSS** to v0.2. The trio is the smallest set actionable in the meal-plan loop: PHQ-2 (depression suppresses appetite + comfort-eating), GAD-2 (anxiety affects food choice + meal timing), Hunger Vital Sign (food insecurity directly gates recipe cost tier + grocery list). PSQI short is indirect (sleep → appetite), AUDIT-C doesn't drive MVP meal-plan logic, CCSS is too broad.
- **Land-but-revisit-during-build trigger:** the trio-trim is the judgment call. If MVP-trio screeners under-capture nutrition-actionable signal during real use, **add back PSQI short first** (sleep affects appetite regulation, and C5 already has sleep-conditional meal-plan logic). AUDIT-C and CCSS stay v0.2-deferred unless specific surfaces require them.

**S4-Q2: What does the cloud-primary MVP-host posture imply for MVP shape?** *(confidence ~80%)*
- **Tension:** A3-v2 MVP-host refinement is cloud-primary reasoning (24 GB can't fit Qwen3-32B Q4_K_M). Every cloud-bound query that touches user data needs PHI decomposition per query crossing. Is that MVP-essential or v0.2?
- **Proposed answer:** **MVP-essential.** PHI decomposition + typed PHI boundary enforcement (constitutional rule layer) ships in MVP, not v0.2. The constitutional rule layer is the spine of A3-v2 (hardcoded rules outside any LLM); shipping cloud-primary reasoning without it would be a compliance regression. A4 (production-target transport/auth shape) stays post-MVP.
- **Revisit-during-build trigger:** if PHI decomposition adds untenable latency to single-request meal-plan generation, narrow the decomposition surface to specific high-risk query types only.

**S4-Q3: How much multi-tenant scaffolding ships in MVP?** *(resolved 2026-06-29 — confidence was ~90%)*
- **Tension:** F9 closure (`a848293`) gave us `tenant_id` + `is_global` columns, the typed query helper, the `tenant` lifecycle table, and the PHI-on-global CHECK. MVP runs one household = one tenant row. Scaffold from day one or build single-tenant-aware and refactor later?
- **Resolution: scaffold from day one across three layers.**
  1. **Query layer — route through the typed helper.** Every MVP query goes through the F9-built tenant-aware helper; nothing bypasses it for the "single tenant" case. Cost is near-zero at write time and avoids a forced refactor before family-of-4 migration.
  2. **Data layer — populate the `tenant` lifecycle table from day one.** One row on first install with a generated UUID per F9-Q2 (uniform NOT NULL + UUID seed; no `'default'` literal — collides on syndication). Same write code that will produce family-of-4 rows later.
  3. **UI layer — hide tenant context at MVP.** No tenant switcher, no household-name labels, no "switch tenant" affordance. The schema + helper + `tenant` row exist; the interface stays single-context. UI surfaces multi-tenancy at v0.2+ when the family-of-4 migration happens; data layer doesn't change at that point.
- **Land-but-revisit-during-build trigger:** none expected. F9 closure already documented all three judgment-call alternatives (Q3 event-sourcing for tenant lifecycle, Q4 NULL-semantics for `is_global`, Q6 per-tenant `vec0` at ~10+ tenants) inline in [schema.md F9](schema.md). If any specific MVP-build pattern surfaces a real problem, the alternative is already pre-researched — no fresh sweep needed.

**S4-Q4: How does Stage 5 (pre-build verification) sequence against Stage 6 (build)?** *(confidence ~70%)*
- **Tension:** Stage 5 is the wave-1/2/3 verification pass. Run all of it before any Stage 6 code (clean cut), or just-in-time per component (less wasted verification on components we don't end up building)?
- **Proposed answer:** **per-component verification just-in-time.** Each Stage 6 step starts with its slice of Stage 5 verification (e.g., "before recipe sourcing step starts, re-verify recipe IP law + TheMealDB API state"). Universal pre-flight wastes time on components MVP may scope down. The wave-structure in roadmap.md becomes a checklist applied at each component-entry point, not a sequenced phase.
- **Revisit-during-build trigger:** if just-in-time verification surfaces a foundational fact change (e.g., DRI publication revision) that retroactively invalidates earlier-built components, swap to upfront pre-flight for the remaining steps.

**S4-Q5: How does Stage 6 (build) sequence internally?** *(confidence ~60% — most uncertain)*
- **Tension:** Current Stage 6 sequencing (in this doc, below) has eight steps. Two issues:
  1. Step 5 (recipe sourcing) must precede step 4 (meal-plan generation) — meal plans need a recipe source.
  2. Step 8 (honest-disclosure surfaces) is too late — constitutional rules make disclosure cross-cutting (every output needs disclosure logic from step 1, not bolted on at the end).
- **Proposed answer:** **promote honest-disclosure to cross-cutting** (woven through every step from step 1, since the constitutional rule layer is the spine of A3-v2); **swap step 4 + step 5** so recipe sourcing precedes meal-plan generation; **defer the full Stage 6 sequencing lock to Stage 6 entry** where MVP build clarity will make ordering decisions cheaper and more correct.
- **Revisit-during-build trigger:** this is the lowest-confidence answer. The entire Stage 6 sequencing will get re-examined when Stage 6 actually opens, with all Stage 4 + Stage 5 context in hand. Treat the current Stage 6 sequencing in this doc as a sketch, not a contract.

**S4-Q6: How actively do we pursue publication tracks during MVP?** *(confidence ~80%)*
- **Tension:** E1–E4 commit to publication-aware data collection from day one. Does MVP also include active publication push, or just keep the door open?
- **Proposed answer:** **no active publication push during MVP.** Keep data collection consent-clean (E2 standing consent + per-publication-confirmation), license-clean (E3: Apache 2.0 code / CC-BY 4.0 docs+data), reproducibility-aware (E1: dual versioning + drift detection + anonymization-ready schema), publication-deferred-active-push. Three publication targets the MVP naturally enables data capture for — recipe time-feedback (#4), cooking-state changes pairings (#5), architectural/methodological code (Apache 2.0 by default) — and we capture for them, but the actual publication apparatus (writeups, peer review submission, dataset releases) waits for post-MVP.
- **Revisit-during-build trigger:** if a publication opportunity surfaces unexpectedly mid-MVP (e.g., conference deadline matches captured-data state), revisit. Default stance is "data ready, push deferred."

### Suggested attack order

Resolve in the order **Q1 → Q3 → Q2 → Q6 → Q4 → Q5**:
1. **Q1** first — MVP scope drives every downstream decision (instrument count, recipe source, what we're actually building)
2. **Q3** next — small + schema-aligned + locks in the multi-tenant-from-day-one stance (already 90% confident)
3. **Q2** third — with MVP scope known, confirm whether PHI boundary work + constitutional rule layer is MVP-essential
4. **Q6** fourth — publication tracks decision is downstream of MVP scope clarity
5. **Q4** fifth — Stage 5 sequencing depends on what we're building (Q1 + Q2 outputs feed this)
6. **Q5** last — Stage 6 sequencing is the most uncertain answer and benefits from every prior answer landing first

Per working-style memory: each sub-question gets its own commit (`stage4(S4-Q1): ...`), confident answers lock in, judgment-call answers land but revisit during build with the trigger documented inline.

---

## Stage 5 — Pre-corpus-build verification pass

Run the wave-1/2/3 verification work tracked in roadmap.md once live web tools are available. Re-fetches:

- Wave 1: DRI publication versions, food composition database current state, vendor APIs current state, recipe IP law currency
- Wave 2: validated-instrument sensitivity/specificity figures, OSS repo states, post-2024 AI-credibility literature, latest Cochrane PLS templates
- Wave 3: NIH NPH program updates, meal-kit behavior-shift literature, regulatory guidance updates, Instacart IDP indie-tier status, all `VERIFY-AT-ADOPTION` items

**Not a re-do of the sweeps** — the framework, source identification, and analytical structure stand. Just a freshness check on time-sensitive details before corpus build kicks off.

---

## Stage 6 — Build phase 1 (MVP implementation)

Iterative build following Stage 3 architecture decisions + Stage 4 MVP scope. Per `publication-ambitions.md`: documentation-grade discipline, reproducibility-aware data collection, license-clear from the start. Test coverage at publication standard for components flagged for publication.

**Sequencing within Stage 6** (proposed; revisit during Stage 4):

1. Foundation — repo scaffolding, deployment shell, persistence layer
2. Intake (initial) — hybrid administration of MVP screener set; basic inventory intake
3. Knowledge model (initial) — per-user state with provenance tags; abstracted-constraint-layer stub
4. Meal-plan generation (initial) — single recipe → single plan, then weekly aggregation
5. Recipe sourcing — initial source integration (1–2 commercial APIs + 1 open dataset)
6. Grocery list — Instacart IDP integration + list-export fallback
7. Per-meal feedback — Mode 3 semantic feedback loop wired to knowledge model
8. Honest-disclosure surfaces — consult-professional callouts, 3-level certainty display, evidence-tier surfacing
9. Daily-cadence interaction model — home screen, meal-on-tonight surface
10. v0.1 ship to user (you) — iterate based on real use

---

## Stage 7 — Use + iterate

Real use surfaces real findings. Roadmap stays alive. Synthesis-phase tensions section grows again as new tensions emerge from real-world use. Publication targets advance as data accumulates.

---

## Parallel tracks

### Publication target development

- **First target: consumer-facing GLIM screener** (sweep #3 design opportunity, narrowest standalone). Can begin as soon as Block C decisions on hybrid administration UX (C3) land — doesn't need full MVP shipped.
- **Second target: hybrid LLM + CAT + structured-instrument open agent** (sweep #4, strongest "novel" claim). Starts after Block C decisions on intake agent architecture (C1, C2) land — and matures with the MVP intake implementation.
- **Third target: open-source nutrition-specific intake chatbot** (sweep #4). Subset of the second target's deliverable; ships as part of the open-source release strategy.
- **Fourth target: recipe time-feedback aggregate data** (sweep #7). Depends on user base size for statistical meaningfulness — long-horizon, accumulates during Stage 7.

### Corpus build phases

- Begins after Block B (knowledge + retrieval) decisions land
- Phased per domain: nutrition standards → food composition → recipes → conditions → drug-nutrient interactions → cuisines/skills
- Includes the verification pass from Stage 5 as a prerequisite step for each domain
- Dynamic-research-expansion (B3) supplements the base corpus at runtime per `dynamic-research-expansion.md`

---

## Decisions most impactful downstream

Per the user's specific ask. These deserve extra deliberation:

- **A1 (deployment model)** — cascades to every other architecture decision
- **A3 (LLM provider + multi-agent orchestration)** — cost, latency, capability all flow from this; constrains agent design
- **A4 (data persistence)** — wrong choice here is expensive to undo; affects every data path
- **B3 (dynamic research expansion infrastructure)** — defines how the system closes its own gaps; touches every domain over time
- **B4 (knowledge model schema)** — most complex schema in the system; the central data structure
- **C1 (conversational intake agent architecture)** — single vs. multi-agent shapes every dialog surface
- **D2 (doctor-portal patient API integration)** — clinical-grade data unlocks meaningful personalization; could surface new research-relevant possibilities
- **E1 (data collection schema for reproducibility)** — getting this wrong forecloses publication target #4
- **E4 (update cadence + corpus refresh design)** — defines whether the system stays current or drifts

## Suggested cadence

- **Stage 3 architecture dialogue:** topic-by-topic per Stage 2 cadence. Aim for 1–2 blocks per session if pace allows; deeper deliberation on the high-impact decisions above
- **Stage 4 MVP scoping:** one focused dialogue once Block C lands
- **Stage 5 verification pass:** opportunistic — run when live web tools are available
- **Stage 6 build:** iterative; commit-per-feature; pause at v0.1 for real-use evaluation
- **Stage 7+:** living roadmap

## Where to start

When ready: Block A, decision A1 (deployment model). It cascades furthest, and the original user direction ("locally hosted app on a MacBook with a web interface") gives us a strong starting point — Stage 3 dialogue can confirm or refine that direction with full Stage 1 + 2 context now in hand.
