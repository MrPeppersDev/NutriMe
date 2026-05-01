# NutriMe — Architecture Decisions

> Living document capturing Stage 3 architecture decisions. Sister doc to [synthesis.md](synthesis.md) (Stage 2 cross-cutting design tensions). Each decision section captures: what was decided, why, alternatives considered, and which docs were updated.

## How this doc works

Each Stage 3 decision (A1–A4, B1–B4, C1–C5, D1–D4, E1–E4 per [stage3-plan.md](stage3-plan.md)) gets a section as it's resolved. Cross-cutting principles that emerge during architecture dialogue may also be captured here.

---

## A1 — Deployment model

> Resolved 2026-04-29.

### Decision

**Pure local-first, single-device, no LAN exposure, no cloud sync.** All data on a single MacBook. No inbound network surface for the application itself.

### Rationale

User direction (2026-04-29):
> "This is purely local. Also, because we're dealing with HIPAA, we do not want to make anything web-based for any time in the near future."

HIPAA discipline at the data-handling level rules out the LAN-multi-device and web-exposed paths originally proposed. Single-device pure-local is the cleanest fit.

### Updates applied

- [product-framing.md](product-framing.md) — distribution-intent section expanded with architectural posture
- [constitutional-rules.md](constitutional-rules.md) Rule 6 strengthened to "data stays local by default; cloud crossings are decomposed and minimal"

---

## A2 — Application shell

> Resolved 2026-04-29.

### Decision

**Native macOS app as primary shell.** Localhost-served web acceptable as a build-speed-friendly alternative since it's never network-exposed.

### Rationale

Native gives access to macOS security primitives (Keychain, App Sandbox, Hardened Runtime, codesigning, native HealthKit access for D1). Localhost web is acceptable for build velocity since it's never exposed to a network.

User direction (2026-04-29):
> "Yeah, native only, native Mac OS app as the shell would be great, so we can lean on some of their security features, maybe, but a local host would also be fine just for the sake of speed."

---

## A3 — LLM provider + privacy posture

> Resolved 2026-04-29 (provider choice + privacy posture). Multi-agent orchestration specifics deferred to C1.

### Decision

**Anthropic Claude + Google Gemini as primary cloud LLM substrate**, NOT local-LLM-only. The privacy boundary lives **at the query level** — queries are decomposed so no single crossing carries a full health profile (per [phi-handling.md](phi-handling.md)).

HIPAA discipline applied at **data-handling level** (audit logs, careful-by-default culture, query-decomposition enforcement), NOT at formal compliance level.

### Open thread

**Why both Anthropic AND Google?** Provider diversity / capability differentiation / cost optimization — to be resolved during C1 (intake agent architecture) since orchestration shape depends on it.

### Rationale

User direction (2026-04-29):
> "A local LLM is not the primary path. We are going to be leaning on Anthropic and Google. We're just going to be very carefully deciding when, what, and why we send any sort of health data."

### Updates applied

- [phi-handling.md](phi-handling.md) — new operational meta doc capturing PHI posture, query-decomposition, audit logs, boundary enforcement
- [constitutional-rules.md](constitutional-rules.md) Rule 6 — strengthened with PHI posture + pointer to phi-handling.md
- [product-framing.md](product-framing.md) — distribution-intent section expanded with architectural posture
- [epistemic-trail.md](epistemic-trail.md) — new section 3a making PHI crossings part of the user-facing trail

---

## A4 — Data persistence + knowledge model storage

> Resolved 2026-04-30 across four sub-decisions Q4.1–Q4.4.

### Decision

**Hybrid storage: SQLite for transactional layers (substrate + operational), markdown vault for the corpus.** Patterns drawn from Library Consortium ([library-consortium-project-docs](https://github.com/MrPeppersDev/library-consortium-project-docs)) and consortium-knowledge-vault ([Kirsendarken/consortium-knowledge-vault](https://github.com/Kirsendarken/consortium-knowledge-vault)) — adopting the data-shape patterns, not the governance machinery.

### Three-layer architecture

| Layer | Storage | Contents | Write semantics |
|---|---|---|---|
| **Substrate** | `nutrime-substrate.db` (SQLite + sqlite-vec) | Per-user + per-household knowledge model, typed entries, typed relationships, provenance tags, bitemporal lifecycle, derivation graph, embeddings | Transactional; high-frequency writes |
| **Operational** | `nutrime-operational.db` (SQLite) | Session state, audit log, PHI crossing records | Transactional; append-only patterns |
| **Corpus** | `nutrime-corpus/` (markdown files) | Recipes, educational content, food composition references, cuisine + technique knowledge, regulatory references | Read-mostly bulk-import; mirror-tool fetches; git as audit trail |

Corpus embeddings live in `nutrime-substrate.db` for unified vector-search query path; **source-of-truth for corpus content is the markdown files**. A corpus indexer reads markdown → writes embeddings into the substrate DB. If embeddings drift or sqlite-vec needs rebuilding, the corpus is reconstructable from markdown files.

### Q4.1 — Hybrid storage shape

Adopted from the start (not deferred until publication ramp). Reasons: publication ambition is first-class per [Tension #10](synthesis.md#tension-10--novel-synthesis-publication-ambition) — designing-for-publication from the start is cheaper than retrofitting; corpus content is the most likely thing to publish; the corpus indexer is bounded, well-understood work; git-as-audit-trail benefit is meaningful for corpus content specifically.

### Q4.2 — Mirror-tool pattern for dynamic-research-expansion

Adopted CKV's mirror-tool design *pattern* (not the LC-specific code) as the architectural shape for [dynamic-research-expansion](dynamic-research-expansion.md)'s fetch-and-integrate pipeline. NutriMe-specific adaptations:

- **Heterogeneous source adapters** — USDA FDC API, Open Food Facts, NIH ODS, EMA SmPCs, recipe APIs, regulatory PDFs each need a fetcher adapter
- **Verification-before-write** — fetched content goes through verification (provenance check, peer-reviewed-floor check, sanity-check, causal-explanation generation per Rule 8) BEFORE landing in corpus
- **Gap-detection-driven fetches** primary; static-refresh sources also exist (USDA FDC scheduled refresh per E4 cadence)
- **Richer provenance frontmatter** — source URL + accessed-at + content hash + evidence tier + verification status + which gap triggered the fetch
- **Triggered re-verification** on source changes (CKV silently overwrites; we re-verify because peer-reviewed evidence quality might have changed — retractions, revisions)

Two specific CKV elements adopted directly:

- **Frontmatter-with-provenance contract** — every fetched markdown file carries YAML frontmatter declaring source identity, content hash, fetch timestamp, tool version, evidence tier tag, verification status
- **`mode:` ownership zone concept** — `mode: read-only` for mirror-managed content (silently overwritten on next mirror run if locally edited); `mode: ai-owned` for system-generated synthesis in the corpus

### Q4.3 — Production retrieval = sqlite-vec; Obsidian + Smart Connections = optional dev convenience

System retrieval depends on sqlite-vec inside the substrate DB (deterministic, versioned, ours). Obsidian + Smart Connections is an optional browse interface — when the user wants to explore the corpus directly (recipes, educational content, evidence audit notes), Obsidian gives graph view + backlinks + semantic chat for free. Not required for the system; available because the corpus is plain markdown.

**Implication flagged for B1:** embedding model choice has publication-reproducibility implications. Voyage / Gemini Embedding are proprietary; open-source models (`mxbai-embed-large`, `BGE-M3`, `nomic-embed-text` via Ollama) sidestep this. Decision deferred to B1.

### Q4.4 — Atoms-vs-synthesis split, with molecules

Adopted the atomic-evidence-vs-synthesized-presentation split as the organizing principle for the substrate, sharpening LC's typed-knowledge-categories pattern. **Refined from CKV's "one atom per file":** in our SQLite-substrate context, atoms are *rows*, not files; molecules (compositions) aggregate co-belonging atoms naturally as a row-and-relation pattern.

| Layer | Type of entry | Mutability | Examples |
|---|---|---|---|
| **Atomic** (immutable) | Raw observations, discrete events | Append-only; never edited | Intake response: "user reports tree nut allergy" (timestamped, source: intake session); per-meal feedback: "user cooked recipe X, reported feeling sluggish 2hr after"; wearable signal aggregate: "Apple Watch HRV 42ms avg week of YYYY-MM-DD"; lab result analyte value |
| **Molecule / composition** | Aggregation of co-belonging atoms | Composition-level append-only (atoms inside cannot be retroactively edited; new atoms can join a *new* composition, not retroactively join a closed one) | Intake session, lab panel, wearable daily aggregate, meal event (cook + liked + time + feel atoms together), document upload |
| **Synthesized** (mutable, LLM-managed) | Current understanding, derived inferences, recommendations, plans | Re-writeable; reflects current knowledge state; carries `derived_from` chain pointing to source atoms or compositions | "User's typical iron intake estimate"; "household member A's current dietary constraints"; "this week's meal plan"; "user's mastered cooking skills" |

**Cross-references between layers:**

- Synthesized entries carry `derived_from: [list of atom or composition IDs]` (per the LC-derived `DerivedFrom` graph pattern)
- When an atom is superseded (new intake reveals tree-nut tolerance after retesting), a new atom is written with `parents: [old-atom-id]` + `relation: supersedes`. Old atom stays. Synthesized "user's allergens" page gets re-derived.
- Compositions can be retracted (lab panel was misread, contaminated sample); retraction propagates to constituent atoms; downstream synthesis re-derives from the `derived_from` graph.
- Cross-composition typed relationships (atom in panel X `Contradicts` atom in intake session Y) work without going through the composition; composition is one organizing dimension among others.

### LC + CKV patterns adopted

The 6 patterns from LC + 5 patterns from CKV that NutriMe explicitly takes:

**From LC (Library Consortium):**

1. **Typed knowledge categories** — observation / synthesized understanding / actionable direction / system knowledge with different write + retrieval semantics per category
2. **Typed relationships as first-class data** — `DerivedFrom`, `Contradicts`, `Supersedes`, `Tension`, `EnrichedBy` stored in the same persistence layer; the epistemic trail becomes a graph, not a log
3. **Provenance tags participate in conflict resolution** — `validated-instrument` / `conversational-elicitation` / `passive-observation` tags drive write-time conflict logic, not just display
4. **DerivedFrom graph for confidence + retraction** — when a source turns out to be wrong, traverse the graph to find downstream inferences that absorbed the error
5. **Three-layer corpus separation** — raw / governed / substrate physically separate; resolves "relational AND vector search" tension by routing per query type
6. **Bitemporal entry lifecycle** — `active_from` / `active_until` + `Supersedes` rather than deletion; preserves history for E1 publication reproducibility
7. **Authority control for canonical concept naming** — "folate" / "folic acid" / "B9" resolve to one canonical record

**From CKV (consortium-knowledge-vault):**

8. **Atoms-vs-synthesis split** — sharpened with the molecules refinement above
9. **Frontmatter-with-provenance contract** for corpus markdown files
10. **`mode:` ownership zones** in corpus frontmatter
11. **Mirror-tool pattern** (pattern, not code) for fetch-and-integrate pipeline
12. **Append-only atom rule with `parents` + `relation` references** when contradicting/superseding

### What we explicitly NOT taking from LC + CKV

LC: Governor quality-gate pipeline, cross-family LLM validation at write time, P11 retrospective audit, Consolidator pipeline, delegation contracts, Bulletin Board, specialist-spawning, mitosis/merge protocols. NutriMe has one user, one device, "user is the authority" trust model.

CKV: Obsidian dependency for the user-facing product; Smart Connections as the production retrieval layer; Slice 3 bidirectional gateway (multi-project shared-vault pattern); multi-dev coordination patterns (pull-only mode, manual commit discipline).

### Risks flagged

1. **Schema design overhead before code.** ~1 week of careful upfront work to define NutriMe's knowledge categories + atom types + composition types + relationship types + provenance discipline. Painful to retrofit. **To be done inline with Stage 3 between Block B and Block C** (architecture deliverable, not build deliverable).
2. **DerivedFrom + atom-write discipline** must be baked into the write API, not bolted on. Every code path that records an observation writes an atom; every code path that produces an inference records `derived_from`. Typed write APIs enforce this.
3. **Over-indexing on LC's complexity is the real risk.** LC has ~340 architecture-conformance decisions; we're using 12. Discipline: every adopted pattern needs a concrete NutriMe query / feature within MVP scope. New patterns surfaced during build don't get adopted just because LC has them.
4. **Three concepts of "confidence" must be distinguished** during schema design: *system confidence* (write-time conflict resolution), *evidence tier* (source classification), *user-facing certainty* (display layer). Related but distinct. Flagged for schema-design phase.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — A4 marked resolved; B1 (semantic RAG vs. structured query strategy) becomes the next decision; embedding-model-choice flagged within B1
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; schema-design overhead added as a Stage 3 deliverable between Blocks B and C
- [README.md](../README.md) — architecture.md added to read-first index; corpus storage approach noted

### Sources

- LC research synthesis (2026-04-30, sub-agent report) at `library-consortium-project-docs` and `library-consortium`
- CKV research (2026-04-30, README.md + WIKI.md direct read) at `consortium-knowledge-vault`
- User direction throughout the Q4.1 → Q4.4 dialogue

---

## B1 — Semantic RAG vs. structured query strategy

> Resolved 2026-05-01 across four sub-decisions Q1.1–Q1.4.

### Decision

Three retrieval modes used together — **vector search + full-text search + structured-relational query** — composed via filter-then-rank. Embeddings are an index over content, not a substitute for it: deliver from source, retrieve via embeddings. Embedding provider chosen per information type — Voyage as primary for non-PHI content, local model for PHI-touching content.

### Q1.1 — Embed-vs-structured-query line + the "embed for retrieval, deliver source" principle

**The line per content type:**

| Content type | Retrieval mode |
|---|---|
| Recipe text descriptions, technique glossary, educational content prose, cuisine context | Semantic — meaning-based search |
| Recipe metadata (ingredients normalized, time, equipment, complexity tier, dietary tags) | Structured — filter-driven |
| Food composition data (USDA FDC nutrient values per ingredient) | Structured — exact lookups |
| Nutrition standards (DRI tables, dietary patterns) | Structured — by population/nutrient |
| Per-user knowledge model state | Structured — relational queries |
| Per-household abstracted constraints | Structured — relational |
| Audit logs + epistemic trail | Structured — temporal + categorical filters |
| Educational content chunks | Both — topic tags for navigability + filtering, embeddings for "what content does this user need next" |
| Validated screener items | Structured — exact items, never embedded (we deliver verbatim per Tension #4) |
| Clinical condition gating logic | Structured — exact rules, never embedded |
| Recipe similarity ("recipes like this one") | Hybrid — embed for similarity + structured filter for constraints |
| User want-to-try preferences elicited conversationally | Semantic — meaning-based matching against recipe corpus |

**Edge case settled — recipe ingredients:** structured (`ingredient_id` references composition data + canonical authority record). Identity matters for inventory matching, allergen detection, condition gating, substitution logic. Authority table resolves variants ("chicken breast" / "boneless skinless chicken breast") to canonical records, not vector similarity.

**Embeddings as index, not substitute (the principle):**

> Embeddings are used **for retrieval matching only**. The artifact delivered to the user is **always the ground-truth source content**, never an LLM-regenerated version. Semantic embedding finds the right recipe / educational chunk / glossary entry; the system then retrieves and renders the source markdown file itself.

This eliminates a class of regeneration mistakes (LLM accidentally changes a temperature, drops an ingredient, mis-paraphrases a step) and preserves attribution + provenance per Rule 8 + Constitutional Rule 4 (no recipe generation).

### Q1.2 — Filter-then-rank as default hybrid orchestration

Constraints (allergens, conditions, equipment, time-budget, life-stage requirements) are non-negotiable per the [conflict prioritization order](../09-multi-user-household/scope.md). Filter first against structured constraints; then semantic-rank within the safe set. Cheaper, more deterministic, easier to debug, and respects safety priorities mechanically.

Deviates only with explicit reason (e.g., evidence-weak [audit-as-education](evidence-tiers.md#audit-as-education-pattern) content discovery doesn't have hard constraints — semantic-first is fine there).

### Q1.3 — Embedding provider routing per information type

**Voyage as primary** for non-PHI content (recipes, educational content, food composition descriptions, cuisine knowledge, glossary, regulatory content). Best quality; the bulk of corpus retrieval is here.

**Local embedding model** (best-fit for our hardware constraints — likely `mxbai-embed-large`, `BGE-M3`, `nomic-embed-text` via Ollama or `sentence-transformers` direct; final choice in schema-design phase) **only for PHI-touching content** — per-user atoms, semantic feedback prose, household abstracted constraints, user-specific embeddings.

This makes Voyage the primary in most cases. PHI is the only domain where local embedding is required (per [phi-handling.md](phi-handling.md)).

**Architectural implications:**

- **Two index spaces in the substrate DB** — `embeddings_voyage_*` and `embeddings_local_*` — schema needs a `provider` field per embedding row
- **Cross-space queries** (rare but real — "find recipes similar to what made the user feel sluggish" needs PHI-side feedback embeddings + non-PHI-side recipe embeddings): pattern is re-embed query string into both spaces, search separately, combine results in application layer with provenance preserved
- **Local model choice is narrower** than originally scoped — MVP-relevant local content is per-user feedback + per-user atoms; manageable on M-series hardware
- **Publication-reproducibility flag** — Voyage embeddings are proprietary; corpus content embedded via Voyage isn't reproducible by anyone without API access. For publication target #4 (recipe time-feedback aggregate data), reproducibility considerations may favor optional re-embedding pipeline using open-source model. Tracked in [roadmap.md](roadmap.md).

### Q1.4 — FTS5 alongside sqlite-vec from the start

SQLite's FTS5 is built-in, mature, fast, runs alongside sqlite-vec in the same DB. Adopted as the third retrieval mode for keyword-exact queries ("find recipes with 'butternut squash'") where semantic search is too fuzzy. Trivial to add at MVP since FTS5 is built into SQLite.

Three-mode retrieval (vector + FTS + structured-relational) covers the full query space.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — B1 marked resolved; B2 (epistemic trail implementation) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; embedding model choice for PHI deferred to schema-design phase; Voyage-vs-open-source-embedding publication-reproducibility tradeoff flagged
- [phi-handling.md](phi-handling.md) — note that embedding-layer PHI boundary is enforced via local-only embeddings for PHI content
- [dynamic-research-expansion.md](dynamic-research-expansion.md) — embedding pipeline decision flagged for the verification-and-integrate step

### Sources

User direction throughout the Q1.1 → Q1.4 dialogue (2026-05-01).

---

## B2 — Rule 8 epistemic trail implementation

> Resolved 2026-05-01 across five sub-decisions Q2.1–Q2.5.

### Decision

The epistemic trail is implemented as **a structural derivation graph in the substrate DB plus an event-log in the operational DB**, with reasoning-chain capture in both structured and narrative form, hybrid rule-based + LLM-causal-explanation verification, layered-disclosure user-facing rendering, and stored-at-inference-time-with-on-demand-reconstruction-fallback durability.

### Q2.1 — Trail storage location

**Both substrate primary + operational supplementary.**

- **Substrate** — every inference is a synthesized entry per [A4 atoms-with-molecules schema](#a4--data-persistence--knowledge-model-storage); the trail is the entry's `derived_from` graph + reasoning chain + verification metadata. The substrate's typed-relationship graph IS the canonical structural backbone of the epistemic trail.
- **Operational** — chronological event log of inference computation events (LLM calls made, intermediate verification step results, latencies, failures). Useful for debugging + AI-confidence calibration over time. Supplementary, not the canonical trail.

### Q2.2 — Reasoning-chain capture format

**Both structured + narrative.** Structured fields on synthesized entries are the queryable derivation substrate (find all inferences depending on atom X, all inferences with low confidence, etc.). LLM-generated narrative is the user-facing "show me the reasoning" surface.

**Narrative generation IS the verification step** per [Tension #8](synthesis.md#tension-8--grade-4-level-certainty-vs-consumer-comprehension) + [epistemic-trail.md section 3](epistemic-trail.md#3-verification-before-presenting). Generating the causal-explanation catches yes/no flips and off-by-one errors before the inference reaches the user. Verification + user-facing trail are produced by the same artifact, preventing drift between what the system did internally and what it tells the user externally.

### Q2.3 — Verification step implementation

**Hybrid: deterministic rule-based checks + LLM-generated causal-explanation.**

Rule-based checks (deterministic, fast, reliable) handle:
- Input-existence (do all referenced atoms / compositions exist?)
- Peer-reviewed-floor confirmation (per [Rule 7](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor))
- Sanity-range checks (numbers in plausible ranges)
- Contradiction detection against existing knowledge model entries

LLM-generated causal-explanation handles soft-coherence verification — does the reasoning hold together? — which isn't easily ruled.

Failed rule-based checks fail closed (inference rejected or downgraded). Failed coherence checks surface low-confidence framing per Tension #8 + Rule 1.

### Q2.4 — User-facing trail rendering

**Layered disclosure** — three depths:

- **Default:** 1-2 sentence summary of what drove the recommendation
- **Show more:** linear chain — inputs → reasoning → output
- **Show full trail:** graph view + reasoning narrative + verification status + PHI crossings (per [phi-handling.md](phi-handling.md))

Most queries surface the default; the deeper layers are available on demand without overwhelming the primary surface.

### Q2.5 — Real-time vs. stored trail

**Stored at inference time as primary; reconstruction-on-demand also supported as a fallback when errors are encountered.**

Stored at inference time because: (i) the verification step IS the trail generation — they can't be skipped; (ii) reconstruction relies on inputs being available, but atoms get superseded over time per the bitemporal lifecycle from A4; (iii) AI-confidence-calibration over time requires stored historical data; (iv) at our scale, trail storage cost is trivial.

Reconstruction-on-demand also supported because: when errors are encountered, walking back through the entire derivation chain reconstructively is genuinely useful for debugging. Both modes available; stored is the default; reconstruction is a debugging fallback.

### Updates applied

- Three concepts of "confidence" remain to be distinguished in schema design: *system confidence* (write-time conflict resolution), *evidence tier* (source classification per Tier 1–4 framework), *user-facing certainty* (Strong / Moderate / Suggestive display per Tension #8). Already flagged in roadmap.
- Verification rule-set design is its own substantial spec — flagged for schema-design phase between Block B and Block C.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — B2 marked resolved; B3 (dynamic research expansion infrastructure) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; verification rule-set design added to schema-design phase scope

### Sources

User direction throughout the Q2.1 → Q2.5 dialogue (2026-05-01); Stage 3 architecture context.

---

## Sweep #14 integration pass — applied 2026-05-01

Sweep #14 (ingredient interactions, flavor science, pairing knowledge) returned with findings during Stage 3 Block B dialogue. Per the sweep's design, a structured integration pass surfaces what existing docs need updates from its findings.

### Updates applied

- **[Sweep #2 (food composition)](../02-food-composition-databases/scope.md)** — authority table requirement extended to accept FlavorDB ingredient IDs alongside USDA FDC IDs; food-composition lookups and ingredient-interaction lookups resolve to the same canonical record
- **[Sweep #11 (recipe sourcing)](../11-recipe-sourcing/scope.md)** — recipe metadata adds pairing-tradition tags (Western shared-compound, Japanese umami-synergy, Chinese five-flavor balance, Indian masala-with-tadka, Latin sofrito-base, Korean gochugaru-base, etc.) for audit-as-education explanations + horizon-broadening recommendations
- **[Sweep #12 (skills-by-cuisine)](../12-skills-by-cuisine/scope.md)** — institutional culinary academy list cross-referenced with sweep #14; same academies serve both technique-pedagogy (#12) and pairing-pedagogy (#14)
- **[Sweep #13 (grocery infrastructure)](../13-grocery-infrastructure/scope.md)** — substitution logic uses pairing-role taxonomy (acid / umami / aromatic / pungent / textural / fat-vehicle) from sweep #14, not just nominal-similarity
- **[evidence-tiers.md](evidence-tiers.md)** — audit-as-education pattern gets new illustrative-examples section, with the flavor-pairing controversy added alongside microbiome / nutrigenomics
- **[publication-ambitions.md](publication-ambitions.md)** — new publication target #5 added: cooking-state changes pairings flavor-science aggregate data (depends on sweep #14 metadata + same anonymization infra as target #4 + sufficient user base)
- **[B1 corpus organization](#b1--semantic-rag-vs-structured-query-strategy)** — both ingredient-as-node and pairing-as-document views fit naturally into the markdown corpus + authority-table model from A4; no architectural changes needed, just documented as a fit
- **No changes** to constitutional rules, intake-pattern, knowledge-model, phi-handling, dynamic-research-expansion, or other meta docs

### Notable findings worth surfacing

- **Umami synergy** (glutamate + 5'-nucleotides) and **capsaicin + TRPV1 cooling-pairings** are the strongest peer-reviewed mechanistic pairing science — both Tier 1 / 2 grounded in primary taste-receptor pharmacology
- The **Ahn et al. 2011 aroma-compound-overlap hypothesis is NOT universal** — Western cuisines lean shared-compound, East Asian cuisines lean contrasting-compound; the system covers both equal-weighted per Rule 9, names the controversy honestly per audit-as-education
- **Cooking-state changes pairings** (raw vs. cooked tomato + basil) is a publishable research gap — added as publication target #5

---

## B3 — Dynamic research expansion infrastructure

> Resolved 2026-05-01 across eight sub-decisions Q3.1–Q3.5c.

### Decision

Operationalizes [dynamic-research-expansion.md](dynamic-research-expansion.md) into a concrete pipeline: **hybrid reactive + proactive gap detection; hybrid explicit + LLM-extraction source adapters; both source-specific + centralized verification; both per-source TTLs + change-triggered re-fetch; cascade failure with partial-success rebuild and per-sub-fetch retry budgets**.

### Q3.1 — Gap-detection mechanism — hybrid reactive + proactive

**Proactive** for predictable gaps (intake reveals new medication → background fetch for related drug-nutrient interactions; new condition disclosed → background fetch for condition-specific guidance + composition data for relevant nutrients).

**Reactive** for unpredictable gaps (user asks about an obscure cuisine, a niche regional dish, a drug we haven't seen before — fetch is triggered by the actual query).

### Q3.2 — Source adapter architecture — hybrid explicit + LLM-extraction

**Explicit per-source code adapters** for high-volume / high-trust / structured-API sources where extraction errors would be high-cost:
- USDA FoodData Central
- OpenFDA / DailyMed (drug labels)
- EMA SmPC (EU drug labels)
- NIH ODS (Office of Dietary Supplements)
- PubMed (peer-reviewed nutrition literature)
- FlavorDB
- Cochrane (systematic reviews)
- Authoritative DRI publications (NASEM, EFSA, SACN, etc.)
- Major recipe APIs (Spoonacular, Edamam)

**Generic web-fetch + LLM-extraction adapter** for one-off / unstructured / low-volume sources where fetch-and-parse via LLM is acceptable. Used for novel queries against sources that don't justify dedicated adapter work.

Boundary moves over time — if a generic-extraction source proves valuable + high-volume, it gets promoted to an explicit adapter.

### Q3.3 — Verification harness — both source-specific + centralized

**Source-specific verification (in adapter)** handles "is this content well-formed for its type":
- USDA FDC adapter verifies record has required fields, units are recognized, source citation present
- Drug-label adapter verifies the SmPC structure, active-ingredient identification, indication present
- Recipe adapter verifies markdown frontmatter is valid, ingredient identity resolves to authority table

**Centralized verification pipeline** handles cross-source concerns:
- Peer-reviewed-floor confirmation (per [Rule 7](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor))
- Sanity-range checks (numbers in plausible ranges)
- Contradiction detection against existing knowledge model entries
- Causal-explanation generation (per [B2 epistemic trail verification](#b2--rule-8-epistemic-trail-implementation))

Both run before integration; failures are categorized so the failure-handling cascade (Q3.5) knows what failed and how.

### Q3.4 — Cache + freshness policy — both per-source TTLs + change-triggered re-fetch

**Per-content-type TTL defaults:**

| Content type | TTL | Notes |
|---|---|---|
| Drug labels | Monthly | Drug labels update with safety reports; monthly cap on staleness |
| Nutrition standards (DRIs) | Annual | Revisions are rare; annual touchstone |
| Food composition (USDA FDC, etc.) | Quarterly | Update cadence varies per source |
| Recipe APIs | Per-recipe re-check on cite | Whole-corpus re-fetch is expensive; per-recipe lazy refresh |
| Regulatory guidance | Annual touchstone + on-demand re-check | When regulatory landscape is queried, re-check freshness |
| Peer-reviewed literature | Indefinite TTL | Papers don't change after publication; use citation-tracking for retractions / corrections |
| Cuisine + technique knowledge | Annual | Slow-changing |
| Ingredient interaction / pairing knowledge | Annual | Slow-changing per [sweep #14 findings](../14-ingredient-interactions/scope.md) |

**Change-triggered re-fetch** complements TTLs: when TTL fires, fetch the source's current hash; if hash differs from last-fetched, full re-fetch + re-verify; if hash matches, just update accessed-at timestamp.

### Q3.5 — Failure handling — cascade failure with partial-success rebuild

The pipeline isn't atomic; it's compositional. A query like "drug-nutrient interactions for warfarin + foods rich in vitamin K" decomposes into multiple parallel sub-fetches:

- Drug label fetch (DailyMed)
- Drug-nutrient interaction database fetch (Lexicomp / NHS DFI)
- Vitamin K composition data (USDA FDC)
- Peer-reviewed literature on warfarin/vitamin K interaction (PubMed)

**If one sub-fetch fails (e.g., PubMed times out), the others still succeeded. Don't throw away the partial corpus.** Pattern:

1. Each sub-fetch fails or succeeds independently — failures are isolated, not cascading
2. Partial success is captured — system records what got fetched + verified successfully, what didn't
3. Rebuild from successes — system continues with the inference using the partial corpus + explicit acknowledgment of gaps in the [epistemic trail](epistemic-trail.md)
4. Retry only the failures — bounded retries with exponential backoff on just the failed sub-fetches
5. Surface the cascade state to the user — "we got drug label + interaction database + composition data; we're still trying for the peer-reviewed literature; here's what we have so far + what's still loading"
6. Per-failure-type error surfacing — different failure modes (timeout / verification-failed / source-down / rate-limited) get different surfacing

**Inference confidence is downgraded when sources are missing.** Per [B2 epistemic trail](#b2--rule-8-epistemic-trail-implementation), confidence isn't generic "low" — it's "moderate confidence; missing peer-reviewed literature; retrying" with specific gap acknowledgment.

**[Rule 1 (consult-professional)](constitutional-rules.md#rule-1--consult-a-professional) callout fires automatically when a clinical-adjacent inference ships with missing critical sources.**

### Q3.5a — Cascade composition rules — both system-defined templates + LLM-decomposed

**System-defined templates** for common query types (drug-nutrient query → these N standard sub-fetches; recipe query → these M standard sub-fetches; condition-gating query → these K standard sub-fetches). Cheaper, deterministic, debuggable.

**LLM-decomposed** at query time for novel queries that don't match a template. Flexible; falls back to LLM-driven decomposition with the same per-sub-fetch failure handling.

### Q3.5b — Late-arriving sub-fetch surfacing — two distinct notifications

When a previously-failed sub-fetch eventually succeeds after the initial inference shipped, **two distinct kinds of surfacing happen depending on what changed**:

- **Trail update — always notify** — any time a previously-failed sub-fetch succeeds and updates the trail, the user sees a low-key notification that the system's underlying state changed. Knowledge model updates, audit trail records updated, evidence-tier or confidence may shift.
- **Material refinement — prominent surfacing** — if the new data materially changes the answer (contradicts the prior inference, shifts confidence meaningfully, adds a new safety consideration), the user gets prominent "this changes things — your prior recommendation should be revisited" framing.

Both surface honestly per [Rule 8](constitutional-rules.md#rule-8--epistemic-trail-of-honesty); the difference is *prominence* in the user-facing surface, not whether-or-not the user is told. The user always knows when underlying state changed; they're prompted to revisit only when the answer materially changed.

### Q3.5c — Per-sub-fetch retry caps — fixed N with exponential backoff

**Default: 3 retries with exponential backoff (e.g., 30s / 2m / 10m).** Per-source-type override available later if specific sources prove flaky and need different parameters.

Caps are at the **sub-fetch level**, not the whole-query level — partial success can ship while individual failed sub-fetches retry within their own budgets.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — B3 marked resolved; B4 (knowledge model schema) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated
- [dynamic-research-expansion.md](dynamic-research-expansion.md) — operational pipeline architecture detail added (gap-detection modes, source adapters, verification harness, cache/freshness, cascade failure)

### Sources

User direction throughout the Q3.1 → Q3.5c dialogue (2026-05-01).

---

## B4 — Knowledge model schema (architecture-level)

> Resolved 2026-05-01 across four sub-decisions Q4.1–Q4.4. **This decision lands the architecture-level schema choices; a deeper-pass schema design phase between Block B and Block C will resolve the lower-confidence flags noted below.**

### ⚠ Confidence + scope of this decision

This B4 entry is the **architecture-level** schema decision — it commits NutriMe to a specific organizing taxonomy + relationship-type set + bitemporal lifecycle + confidence-concept reconciliation. It is **NOT a finalized implementation schema**. Detailed work (table definitions, indexes, foreign keys, constraints, migrations, type-merge decisions on the lower-confidence flags) lands in the **schema-design phase** between Block B and Block C, per the [A4 schema-design risk callout](#a4--data-persistence--knowledge-model-storage).

**Overall architecture-level confidence: ~70%.**

The lower-confidence flags below are explicitly recorded as **schema-design phase deliverables** rather than buried; they need a more in-depth pass before any implementation work lands. Per the [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty), this surfacing of confidence is the design itself.

### Q4.1 — Three confidence concepts, naming + reconciliation

The system has three distinct concepts that must NOT collapse into one column:

- **`system_confidence`** (numeric 0.0–1.0) — internal numeric confidence for write-time conflict resolution + DerivedFrom propagation
- **`evidence_tier`** (enum: 1 / 2 / 3 / 4 / N/A) — source classification per the [4-tier framework](evidence-tiers.md)
- **`user_facing_certainty`** (enum: strong / moderate / suggestive / not-applicable) — display layer per [Tension #8](synthesis.md#tension-8--grade-4-level-certainty-vs-consumer-comprehension)

**Mapping rules between them** (deterministic; final numeric values tunable in schema-design phase):

| Source mix | evidence_tier | system_confidence default | user_facing_certainty |
|---|---|---|---|
| All inputs Tier 1 + GRADE high/moderate | Tier 1 | 0.95 | Strong |
| Tier 2 + GRADE moderate | Tier 2 | 0.80 | Moderate |
| Mixed Tier 1 + Tier 2 + low GRADE | Tier 1/2 mix | 0.70 | Moderate |
| Tier 3 only | Tier 3 | 0.50 | Suggestive |
| Tier 2 + GRADE low/very low | Tier 2 | 0.40 | Suggestive |
| Tier 4 audit-as-education context | Tier 4 | 0.20 | Suggestive (with "evidence weak" framing) |

### Q4.2 — Knowledge type taxonomy

#### Atom types (immutable, append-only — 17)

`intake_response`, `screener_result`, `literacy_response`, `pediatric_observation`, `cook_confirmation`, `meal_feedback_liked`, `meal_feedback_time`, `wearable_signal_aggregate`, `lab_analyte_value`, `inventory_observation`, `grocery_order_record`, `clinical_disclosure`, `preference_statement`, `document_upload_event`, `corpus_extracted_claim`, `recipe_attribution_record`, `phi_crossing_event`

#### Molecule (composition) types (8)

`intake_session`, `lab_panel`, `wearable_daily_aggregate`, `meal_event`, `document_upload`, `grocery_order`, `recipe_document`, `week_of_meal_events`

#### Synthesized entry types (mutable, LLM-managed — 16)

`nutrient_intake_estimate`, `dietary_constraint`, `abstracted_constraint`, `meal_plan`, `meal_recommendation`, `recipe_match`, `educational_recommendation`, `inference`, `inferred_pattern`, `pairing_rationale`, `substitution_proposal`, `stretch_recipe_disclosure`, `audit_as_education_content`, `dietary_pattern_assessment`, `stretch_readiness_signal`, `audit_log_entry`

### ⚠ Lower-confidence flags — schema-design phase resolves

The following architecture-level decisions are landed but warrant explicit deeper review before implementation. **Schema-design phase has these as deliverables.**

| # | Flag | Open question | Architecture-level lean (~confidence) |
|---|---|---|---|
| F1 | **Asynchrony / temporal state model** | The taxonomy doesn't yet capture meal lifecycle (proposed → accepted → scheduled → cooking → cooked → skipped). Probably belongs as `state` fields on existing types like `meal_recommendation`, not new types. | Add state machines to existing types, not new types (~50% confident) |
| F2 | **Household vs. user-level subject boundary** | Most synthesized types need a `subject_id` + `subject_type ∈ {user, household, member_subset}` field. Pattern repeats across `meal_plan`, `meal_recommendation`, `dietary_constraint`, `abstracted_constraint`. | Add `subject_id` + `subject_type` to all synthesized types (~70% confident); could be more granular if needed |
| F3 | **Corpus vs. substrate boundary for system-generated shareable content** | `pairing_rationale` is generated from corpus + user-knowledge-model state, but is the same across users for the same recipe. Should there be a 4th storage layer for `corpus_synthesized_content`? | Keep in substrate for now (~55% confident); flag for re-evaluation if cache patterns emerge |
| F4 | **User-correction handling** | When a user corrects a prior inference ("no, that wasn't lactose intolerance — it was a one-off"), do we use a generic `clinical_disclosure` atom + Supersedes relationship, or introduce a `user_correction` atom type? | Use existing types + Supersedes (~50% confident); could shift to `user_correction` atom type after observation |
| F5 | **Generic `inference` catch-all type** | Generic catch-all types are usually a smell. Should we force every inference into a specific synthesized type, or keep `inference` as a load-bearing catch-all? | Keep as load-bearing catch-all (~65% confident); flag as smell to monitor; remove once enumeration matures |
| F6 | **Possible type merges** | `dietary_pattern_assessment` ↔ `screener_result` (both might be the same shape with different `instrument_type` enum values). `audit_as_education_content` ↔ `educational_recommendation` (might be the same shape with different `evidence_tier_framing` enum). | Currently separate (~40% confident on each merge being right vs. wrong); resolve in schema-design phase |
| F7 | **`provenance_chain` as relationship vs. computed view** | The full lineage atom → molecule → synthesis → user-facing-surface needed for layered-disclosure rendering. Lean on it being a computed view over recursive `DerivedFrom` traversal rather than a stored relationship. | Computed view (~tentative); decide in schema-design phase |
| F8 | **Possibly-overengineered atoms reconsidered** | I considered + rejected: `emotional_state_atom` (folded into meal feedback), `goal_atom` (folded into preference_statement), `schedule_atom` (folded into meal_event time). Reconsider during schema-design phase if real use cases surface. | Folded into existing types currently; flag for revisit |

### Q4.3 — Typed relationship enumeration (7)

`DerivedFrom`, `Contradicts`, `Supersedes`, `Tension`, `EnrichedBy`, `MemberOf`, `RetractedBy`

Per LC pattern adopted in [A4](#a4--data-persistence--knowledge-model-storage). Forward + reverse indexes on `(source_id, type, target_id)` / `(target_id, type, source_id)` so derivation traversal is a graph operation, not a log scan.

### Q4.4 — Bitemporal lifecycle field naming

- **`valid_from`** (timestamp) — when this entry became authoritative
- **`valid_until`** (timestamp, nullable) — when this entry was superseded; null means currently valid
- **`recorded_at`** (timestamp) — when the entry was written to the DB (different from `valid_from` for backdated entries)

Most queries default to `valid_until IS NULL` (current state); historical queries use the full bitemporal pair. Per LC pattern adopted in A4.

### Schema-design phase deliverables (between Block B and Block C)

The schema-design phase is now scoped with these explicit deliverables:

1. Resolve the 8 lower-confidence flags above (F1–F8)
2. Define detailed table layouts (column definitions, types, constraints, defaults)
3. Define indexes (especially the `(source_id, type, target_id)` + `(target_id, type, source_id)` relationship indexes)
4. Define foreign key + referential integrity rules
5. Define migration strategy (how the schema evolves over time without losing the bitemporal-immutability discipline)
6. Define the `KnowledgeEntry` base table vs. type-specific table normalization approach
7. Define the verification rule-set (per [B2](#b2--rule-8-epistemic-trail-implementation))
8. Define the embedding-table layout (`embeddings_voyage_*` + `embeddings_local_*` per [B1 Q1.3](#b1--semantic-rag-vs-structured-query-strategy))

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — B4 marked resolved (architecture-level); schema-design phase deliverables expanded
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; schema-design phase scope expanded with the 8 flag deliverables

### Sources

User direction throughout the Q4.1 → Q4.4 dialogue (2026-05-01); explicit hybrid-A-and-C resolution on flag-handling.

---

*Block B complete. Block C (intake + interaction) is next; Block D (external integrations) and Block E (reproducibility + publication) can run in parallel after Block A but were deferred per the topic-by-topic cadence.*

---

## C1 — Conversational intake agent architecture

> Resolved 2026-05-01 across five sub-decisions Q1.1–Q1.5, with a new architectural commitment to **LLM provider agnosticism** that cascades across the system.

### Decision

**Hybrid orchestrator + bounded specialized sub-agents** topology, with **structured tool call** as the default agent communication protocol, **hybrid short-term-operational + long-term-substrate state management**, and **double-layered (per-agent + per-tool) PHI enforcement** that fails closed. All of this routed through a **provider-agnostic adapter layer** keyed on capability vector, not provider name (per the new [provider-abstraction.md](provider-abstraction.md)).

### Provider agnosticism — new architectural commitment

User direction during C1 dialogue elevated provider choice into a foundational principle: **the system addresses LLM capabilities, not LLM providers.** Capability vectors are the addressable unit; providers register their capability vectors at the adapter layer; the routing layer matches request capability requirements against registered providers.

Adding a new provider = dropping in an adapter, not refactoring the system. Today's Anthropic Claude + Google Gemini choice is a current default, not a baked-in dependency. Local LLMs become first-class adapters for PHI-lane reasoning when capability matches.

Captured as a foundational meta doc: [provider-abstraction.md](provider-abstraction.md). Cascades across A3, B1, C1, and forward.

### Q1.1 — Topology: hybrid orchestrator + bounded specialized sub-agents

A single primary agent handles user-facing dialog + meal planning + education delivery + general retrieval. Specialized sub-agents are invoked only for bounded tasks where specialization clearly wins:

- Validated-screener administration (per [Tension #4 hybrid administration](synthesis.md#tension-4--consumer-friendly-clinical-instrument-vs-validity-preservation))
- Complex multi-source verification cascades (per [B3 dynamic research expansion](#b3--dynamic-research-expansion-infrastructure))
- Possibly recipe-to-cart translation (per [sweep #13](../13-grocery-infrastructure/scope.md))

Most concerns stay in the primary agent's context. Simpler than full multi-agent; less brittle than single-agent-with-everything.

### Q1.2 — Why both Anthropic + Google: combination (capability differentiation + failover + cost optimization)

Resolves the open thread from A3. Three layers, each serving a distinct purpose:

- **Capability differentiation** — load-bearing reason. Claude's structured-output reliability + reasoning quality on substrate writes; Gemini's native search grounding for [B3 dynamic-research-expansion](#b3--dynamic-research-expansion-infrastructure) fetches + multimodal capability.
- **Failover** — provider-agnostic adapter layer means if primary provider is down / rate-limited / quality-degraded, secondary takes over without application change.
- **Cost optimization** — per-query tier choice within each provider's lineup (Sonnet vs. Haiku, Pro vs. Flash) keyed on capability requirements.

Now operationalized through capability-vector routing per [provider-abstraction.md](provider-abstraction.md), not hardcoded provider-name routing.

### Q1.3 — State management: hybrid short-term-operational + long-term-substrate

- **Short-term conversation state** (last N turns of current session) lives in `nutrime-operational.db` so any agent picking up the session has recent context without re-fetching
- **Long-term knowledge state** (per-user history, preferences, semantic feedback patterns, knowledge model entries) is queried from `nutrime-substrate.db` per-call so it's always fresh + reflects updates from concurrent activity

Avoids the "agent has stale knowledge of the user" problem while keeping per-call latency reasonable.

### Q1.4 — Communication protocol: structured tool call (with conversation-handoff escape hatch flagged)

**Structured tool call as default** — sub-agents are exposed as tool calls; primary agent invokes them with structured inputs, gets structured outputs.

**Wins:**
- Auditability (B2 epistemic trail captures inputs + outputs cleanly)
- PHI-decomposition enforcement (structured calls make it easy to declare + enforce which PHI categories are allowed)
- Testability (sub-agents become unit-testable: known inputs → expected outputs)
- Provider-agnosticism friendly (maps cleanly to capability-vector routing)
- Failure handling integrates cleanly with B3 cascade-failure model

**Drawbacks acknowledged (deferred to specific-use-case escape hatch):**
- Structured tool call discards conversational nuance (rapport, hesitations, qualifying language); recreation via structured fields isn't perfect
- Multi-turn within a sub-agent is awkward (e.g., 9-turn PHQ-9 administration via repeated tool calls)
- User notices the seams — stitch-together responses vs. seamless conversation
- Sub-agent specialization can't accumulate cross-session expertise the same way

**Escape hatch:** if a specific use case during build hits drawbacks 1 or 2 hard enough that structured tool call is genuinely the wrong tool, we add a conversation-handoff sub-pattern **for that specific case** — not as a general capability. Per the discipline of "every adopted pattern needs a concrete use within MVP scope" from the LC research.

### Q1.5 — PHI enforcement: both per-agent + per-tool (double layer, fails closed)

- **Per-agent PHI policy** — outer envelope: each agent (primary, sub-agent) declares the PHI categories it's allowed to handle; calls that would exceed are rejected at the agent boundary
- **Per-tool PHI policy** — inner enforcement: each tool call declares the PHI categories it's allowed to carry; agents may be flexible but tool calls are the actual enforcement point at the LLM-call site

Both layers fail closed. Per [phi-handling.md](phi-handling.md) "typed, tested, fails closed" commitment. Belt-and-suspenders on PHI to catch leaks even if one layer is bypassed.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — C1 marked resolved; C2 (CAT/IRT integration) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; provider-agnosticism added as a foundational principle alongside the existing meta docs
- [README.md](../README.md) — provider-abstraction.md added to read-first index
- [phi-handling.md](phi-handling.md) — note the per-agent + per-tool double-layer enforcement now explicit in C1

### Sources

User direction throughout the Q1.1 → Q1.5 dialogue (2026-05-01); explicit elevation of provider-agnosticism principle to foundational status.

---

## C2 — CAT / IRT integration

> Resolved 2026-05-01 across five sub-decisions Q2.1–Q2.5.

### Decision

**Use an existing CAT engine** (avoid NIH syndrome until operational difficulties surface), **download PROMIS calibrated item banks for local CAT execution** (no PHI crosses, A1-compliant), **two parallel delivery paths** (PROMIS adaptive via CAT engine + classical instruments via deterministic sum-score) both producing `screener_result` atoms per [B4 taxonomy](#b4--knowledge-model-schema-architecture-level), **bitemporal lifecycle with item-bank version stamping**, and **invisible adaptive nature with explicit early-stopping notification** giving the user agency to continue if desired.

### Q2.1 — Existing engine, not roll-your-own

**Use an existing CAT engine.** Don't reinvent the wheel until operational difficulties during build justify it.

Open sub-question deferred to build phase: **which existing engine?**

- **R-based mature options:** mirtCAT (integrates with `mirt` Multidimensional IRT, strong psychometric grounding), Concerto (used in academic CAT-MH research, MIT-licensed), catR (lighter, focused on CAT simulation + administration)
- **Python re-implementation:** less mature than R-based options; no R interop overhead

Lean: mirtCAT in R with thin Python wrapper if stack ends up Python-primary; evaluate R-interop overhead vs. porting validated logic ourselves once stack is pinned. Decision lands during build.

### Q2.2 — PROMIS banks: local download + local CAT execution

**Download PROMIS calibrated item banks; run CAT locally** with the chosen engine. Pure-local execution per [A1](#a1--deployment-model); no PHI crossing per [phi-handling.md](phi-handling.md). PROMIS Assessment Center API (web service) is incompatible with A1 + violates phi-handling boundaries — out.

Item-bank download is a one-time setup; periodic re-fetch per B3 cache+freshness policy (annual TTL on PROMIS banks since calibrations are updated periodically).

Open sub-question deferred to build phase: **PROMIS bank scope at MVP.** Per [stage3-plan.md MVP](stage3-plan.md), MVP includes 5–10 highest-leverage instruments. Lean: **start with MVP set** (depression, anxiety, sleep, fatigue, perceived stress); **add others as user disclosure surfaces need** per [B3 dynamic-research-expansion gap-detection](#b3--dynamic-research-expansion-infrastructure).

### Q2.3 — Classical instruments: deterministic sum-score, same hybrid administration UX

PROMIS covers depression / anxiety / sleep / fatigue / perceived stress. Classical instruments (PHQ-9, GAD-7, SCOFF, EAT-26, PSQI, CCSS, AUDIT-C, Hunger Vital Sign) are scored differently — sum-score with documented cutoffs, not IRT-based ability estimates. Sweep #4 found no PROMIS bank exists for diet quality / eating behavior / cooking confidence; classical instruments fill those gaps per [sweep #3](../03-clinical-nutrition-assessment/scope.md).

**Two parallel delivery paths:**

- **PROMIS instruments** — adaptive item selection via local CAT engine
- **Classical instruments** — verbatim items in fixed order (per Tension #4); deterministic sum-score with documented cutoffs (PHQ-9 ≥10 = moderate depression, etc.)

**Both produce `screener_result` atoms** per [B4 taxonomy](#b4--knowledge-model-schema-architecture-level) with:
- The score
- The interpretation tier (none / mild / moderate / severe / etc.)
- The item-bank version (per Q2.4 below)
- Provenance: `validated-instrument` per [knowledge-model.md](knowledge-model.md)

**Hybrid administration UX (per [Tension #4](synthesis.md#tension-4--consumer-friendly-clinical-instrument-vs-validity-preservation)) is the same for both paths** — verbatim items + conversational framing prefaces. Only the under-the-hood scoring engine differs. The user experience is uniform.

### Q2.4 — Bitemporal lifecycle + item-bank version stamping

Adopts the standard B4 bitemporal pattern (`valid_from` / `valid_until`) plus an additional **item-bank version stamp** on every `screener_result` atom.

- A 2026 PHQ-9 administration is distinguishable from a 2030 PHQ-9 administration if cutoffs change in the interim
- Item-bank revisions tracked per B3 cache+freshness policy (annual TTL with change-triggered re-fetch)
- Migration handling for users with stored results from an older bank version when the bank updates: existing results retain their original version stamp; new administrations use the current version; longitudinal-comparison queries surface version differences honestly per [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty)

### Q2.5 — UX during CAT administration

**Adaptive nature is invisible.** The user shouldn't have to understand IRT to take a screener. Items appear one at a time; the fact that the next item is selected by max-information is implementation detail, not user-facing.

**Early-stopping notification with user agency.** When CAT measurement reaches sufficient precision, the user is shown: *"We have a confident measurement now; you can stop here or continue if you want."* Per [Rule 10 (user decides with full context)](constitutional-rules.md#rule-10--user-decides-with-full-context). Some users will want to complete the full instrument anyway (psychological closure, comparing against prior administrations, etc.); the system honors that without forcing it.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — C2 marked resolved; C3 (hybrid administration UX) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; engine choice + MVP PROMIS scope flagged as build-phase decisions
- [phi-handling.md](phi-handling.md) — note that PROMIS item-bank download is a one-time non-PHI fetch; CAT administration runs locally with no PHI crossing

### Sources

User direction throughout the Q2.1 → Q2.5 dialogue (2026-05-01); explicit early-stopping reversal mid-dialogue.

---

## C3 — Hybrid administration UX

> Resolved 2026-05-01 across five sub-decisions Q3.1–Q3.5.

### Decision

**Items rendered by application (LLM never has the chance to modify item text)**, **curated clarification corpus per validated instrument**, **pause-anywhere with core-service access during incomplete intake + caveat surfacing**, **templated framing with variable slots**, and **double validation (pre-render + post-hoc review) on LLM-generated framing**.

### Q3.1 — Item-text-as-data: items rendered by application; LLM produces only framing

**Items are application data; the LLM never produces item text.** The application layer renders verbatim item text directly in the UI; the LLM produces only the surrounding conversational framing (preface, transitions, item-level clarification on request, pacing).

- Eliminates LLM-text-drift risk entirely — items can't be paraphrased / "simplified" / elaborated
- Validity preservation is mechanical, not conventional
- Framing references items abstractly (*"I'm going to ask you 9 questions about how you've been feeling lately"*) since LLM doesn't see/render the items
- **Surfacing ground truth**: per user direction, items are surfaced verbatim so any accidental LLM blips or mistakes the user notices can be caught + corrected during comprehensive review

Tradeoff: slightly more application code (item-rendering layer) + framing is decoupled from item rendering. Worth it for the safety + simplicity.

### Q3.2 — Item-level clarification: curated corpus per instrument

When users request item-level clarification (*"What does 'little interest or pleasure' mean here?"*), the application looks up + delivers from a **curated clarification corpus per validated instrument**.

- PROMIS + classical instruments have published "user guides" + "administration manuals" with clarification language for common items
- Curate these into a corpus per instrument
- Higher quality + consistency than LLM general knowledge
- Respects the validated-instrument provenance discipline (clarifications come from the instrument's own publishers, not from the LLM)
- Falls back to LLM-generated clarification only if curated corpus has no entry; flagged for curation review

### Q3.3 — Pause anywhere; core service stays accessible; caveat-surface honestly

**The user can pause intake / screener administration at any time AND continue using the core app while incomplete.** Intake completion is NOT a gate on accessing meal planning + recipes + grocery features. The convenience starts immediately, not after clinical-grade intake completes.

- **Pause is a first-class action at every step** — not a special "save and resume later" flow; just stopping is fine
- **Core service usable with partial intake** — meal planning, recipes, grocery list all work
- **Caveat surfacing** — when the user accesses features that *would* benefit from missing data, the system surfaces honestly: *"You haven't finished the [sleep questionnaire / cooking confidence assessment / clinical history]. We're working with what we have. If you completed [X], we'd be able to [pinpoint Y / refine Z / personalize W]."*
- **Caveat is informational, not pushy** — tells the user what they'd gain from completing, doesn't badger
- **Per-item save points** — anything answered is preserved + used (per `intake_response` atoms in B4 taxonomy being independently meaningful)

**Downstream implication:** the system gracefully handles partial intake as the **default state, not the exception**. Inferences computed with partial data carry honest "we're working with limited information" framing per Rule 8 epistemic trail. The 3-level user-facing certainty display (per [Tension #8](synthesis.md#tension-8--grade-4-level-certainty-vs-consumer-comprehension)) skews toward Suggestive until intake matures — that's fine; it's honest.

Aligns with:
- [Convenience-driven framing](product-framing.md) — convenience starts immediately, not after intake completes
- [Rule 10 user agency](constitutional-rules.md#rule-10--user-decides-with-full-context) — user decides when to deepen system's understanding
- [Tension #1 mental-load reduction](synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction) — intake friction is itself mental load; deferring it preserves the convenience win
- [knowledge-model.md](knowledge-model.md) — system reasons over partial knowledge with appropriate confidence framing

### Q3.4 — Conversational framing: templated with variable slots

Framing is **templated with variable slots** — fixed structural skeleton (curated, application-owned) + LLM-generated context-aware fills.

- Predictable structure for testing + auditing + validity discipline
- LLM responsiveness for context-aware adaptation (e.g., preface knows it's user's third intake session, adjusts tone)
- Templates are part of application's curated content
- Variable slots are LLM-generated and pass through Q3.5 validation

Best of both deterministic + variable patterns.

### Q3.5 — Validation: both pre-render + post-hoc

**Pre-render validation** — LLM-generated framing is checked against rules (no item-content reference, no leading language, no answer-priming) before rendering to user. Strict gate; failures fall back to deterministic template-only framing.

**Post-hoc review** — framing is logged + audited periodically; problem cases surface even if they slipped past pre-render rules. Pattern-detection layer.

Both per [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) — every LLM-generated framing is captured + auditable. Pre-render prevents worst cases reaching users; post-hoc catches subtle patterns the rules don't anticipate.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — C3 marked resolved; C4 (multi-modal recipe presentation rendering) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; partial-intake-as-default-state flagged as a downstream implication for Block C4 + C5 design
- [knowledge-model.md](knowledge-model.md) — note that partial intake state is the default, not exception; system reasons over partial knowledge with appropriate confidence framing per Rule 8

### Sources

User direction throughout the Q3.1 → Q3.5 dialogue (2026-05-01); user-introduced refinement on Q3.3 expanding pause-and-resume into full pause-anywhere-with-core-service-access pattern.

---

*Future architecture decisions will be added as resolved.*
