# NutriMe — Stage 3+ Comprehensive Plan

> Living plan covering everything from current state (Stage 1 + 2 complete) through architecture, MVP, build, iteration, and parallel publication / corpus-build tracks. Updates as decisions land and scope changes.

## Where we are (2026-04-29)

- **Stage 1 (research)** — complete. 13 sweeps populated; sources.md consolidated; 16 commits on `origin/main`.
- **Stage 2 (synthesis)** — complete. All 13 cross-cutting tensions resolved in `synthesis.md` (one positively reversed mid-stream).
- **Architecture / build** — not started. Active publication ambition confirmed (`publication-ambitions.md`).

## Stage sequence

| Stage | What | Cadence | Depends on |
|---|---|---|---|
| **3** | Architecture / system design dialogue | Topic-by-topic with clarifying questions, captured in `architecture.md` | Stage 2 |
| **4** | MVP scoping | Single dialogue once Stage 3 settles, captured in `mvp.md` | Stage 3 Blocks A + B + C |
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

Most cross-cutting decisions. Must be first.

| # | Decision | Notes | Downstream impact | Status |
|---|---|---|---|---|
| A1 | **Deployment model** — pure local-first, single-device | Resolved 2026-04-29: pure local-first, single MacBook, no LAN exposure, no cloud sync. HIPAA discipline rules out the LAN-multi-device or web-exposed paths originally proposed. | Cascades to A2, A3, A4, all of Block D, the entire data-flow design | ✅ Resolved |
| A2 | **Application shell** — native macOS app primary; localhost web acceptable for build speed | Resolved 2026-04-29: native macOS app as primary shell to leverage Apple security primitives (Keychain, App Sandbox, Hardened Runtime, codesigning, native HealthKit access for D1). Localhost-served web acceptable as a build-speed-friendly alternative since it's never network-exposed. | Affects intake UX, recipe presentation rendering (C4), HealthKit integration path (D1) | ✅ Resolved |
| A3 | **LLM provider + multi-agent orchestration** — Anthropic Claude + Google Gemini with query-level PHI decomposition | Resolved 2026-04-29 (provider choice + privacy posture). Cloud LLMs as primary inference substrate; query decomposition keeps full health profiles from crossing in a single call (per [phi-handling.md](phi-handling.md)). Why-both-providers open thread flagged for Block C. Multi-agent orchestration specifics deferred to C1. | Constrains C1, C2, Block B retrieval orchestration, all educational content surfaces | ✅ Resolved (provider + PHI posture); orchestration specifics deferred to C1 |
| A4 | **Data persistence + knowledge model storage** — hybrid: SQLite for substrate + operational, markdown vault for corpus | Resolved 2026-04-30 across Q4.1–Q4.4. Three-layer architecture (substrate / operational / corpus); LC + CKV patterns adopted (12 patterns total); atoms-with-molecules-refinement organizing principle for substrate. Full decision in [architecture.md A4](architecture.md#a4--data-persistence--knowledge-model-storage). | Constrains B1 (RAG architecture), B2 (provenance), B4 (schema), every data-write code path | ✅ Resolved |

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
| C5 | **Daily-cadence interaction model** — what the user sees on app open, how meal planning + cook confirmations + semantic feedback + education ride on the natural daily interaction per synthesis Tension #3 | The home screen of the product. Meal-planning surface as the carrier for everything else. | Affects user retention, education delivery cadence, knowledge model update timing |

### Block D — External integrations

Largely parallel-doable within itself once Block A lands. Each constrains specific features.

| # | Decision | Notes | Downstream impact |
|---|---|---|---|
| D1 | **Wearable + biometric aggregation** — HealthKit primary + Health Auto Export bridge + direct integrations (Whoop, Oura, Garmin) for non-HealthKit-mirroring sources | Per sweep #6. Apple-centric assumption simplifies; broader hardware support adds work. | Constrains personalization sophistication; constrains Tension #5 abstracted-constraint-layer inputs |
| D2 | **Doctor-portal patient API integration** — Apple Health Records (FHIR US Core) + Epic MyChart / Oracle Health / Athena patient APIs where available | Per sweep #6. Most patient-friendly FHIR access in US per ONC Cures Act. | **Likely impacts downstream understanding** — clinical-grade data unlocks meaningful condition gating + lab-driven personalization. Could surface new clinical-data possibilities not yet in research. |
| D3 | **Grocery cart-aggregation integration** — Instacart IDP primary + Kroger Cart API backup + six-tier graceful-degradation fallback (per sweep #13) | Personal-use distribution + Instacart's indie-friendly tier make this tractable. Outside US/CA: list-export fallback. | Constrains the "boom shows up at my door" promise; affects user satisfaction with the convenience layer |
| D4 | **Recipe source integration** — paid commercial APIs (Spoonacular, Edamam) + curated publishers via legitimate paid access + open datasets + public-domain historical + institutional video | Per sweep #11 expanded scope. Source-qualification framework gates additions. | Constrains recipe corpus breadth + multi-modal availability; affects horizon-broadening fidelity |

### Block E — Reproducibility + publication infrastructure

Largely parallel after Block A. Informs design choices throughout.

| # | Decision | Notes | Downstream impact |
|---|---|---|---|
| E1 | **Data collection schema for reproducibility** — versioning of instruments, drift detection, provenance tagging, optional anonymization-ready fields | Per `publication-ambitions.md` methodology principles. Designed-from-start cheaper than retrofitted. | Constrains B4 schema + every data-capture surface; foundational for publication target #4 (recipe time-feedback) |
| E2 | **Anonymization + consent infrastructure** — IRB-equivalent consent design + anonymization protocol for any aggregate data publishing | Required before publication target #4 ships any data. | Affects every publication-eligible data path; enables vs. blocks open-science contributions |
| E3 | **License decisions per publication target** — code license (likely MIT or Apache 2.0), documentation license (likely CC-BY), data license (case-by-case), AGPL consideration for derivative-protection | Per `publication-ambitions.md`. Decide early so attribution + repo structure are clean. | Affects open-source distribution clarity; constrains future commercial paths if user ever broadens distribution intent |
| E4 | **Update cadence + corpus refresh design** — DRIs revise every 5–10 years; food composition periodically; recipes constantly; regulatory ad-hoc | Per roadmap deferred-to-architecture item. Touches B3 (dynamic-expansion) closely. | **Likely impacts downstream research understanding** — defines how the corpus stays current vs. drifts; affects Stage 5 verification pass cadence going forward |

---

## Stage 4 — MVP scoping

Single dialogue once Block C decisions are settled. Picks the smallest useful end-to-end slice. My current proposed MVP (subject to revision after Stage 3):

**MVP includes:**
- Intake (validated-screener hybrid administration for 5–10 highest-leverage instruments: PHQ-2, GAD-2, PSQI short, AUDIT-C, Hunger Vital Sign, CCSS, plus demographics + life-stage + dietary preferences + allergens)
- Inventory awareness (initial intake + ongoing observation)
- Meal-plan generation (Tier 1/2 nutrition guidance + recipe sourcing from open datasets + 1–2 commercial APIs)
- Grocery list (Instacart cart-aggregation when US-located, list-export fallback otherwise)
- Per-meal feedback (semantic + time-accuracy)
- Honest disclosure surfaces (consult-professional, evidence-tier, audit-as-education)

**MVP defers:**
- Full knowledge model evolution (start with simple per-user + household; iterate)
- Multi-modal recipe presentation infrastructure (text + linked YouTube video; defer in-app video rendering, illustrated rendering, real-time terminology lookup glossary)
- Audit-as-education depth (start with consult-professional + evidence-tier surfacing; defer comprehensive educational corpus)
- All four publication targets (start designing for them; defer active publication push)
- Multi-user household with full conflict-resolution UX (start single-user with stub for household)
- Wearable signal interpretation (start with intake-only; add wearable in v0.2)

**Why this MVP:** ships a thing you'd actually use, validates the core meal-planning loop + inventory awareness + grocery integration, captures real data for the publication-#4 target without committing to the full-publication apparatus yet.

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
