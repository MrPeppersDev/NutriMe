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

## C4 — Multi-modal recipe presentation rendering

> Resolved 2026-05-01 across five sub-decisions Q4.1–Q4.5, with two architectural refinements that generalize beyond C4: the **"tap to understand more"** pattern (cross-domain) and the **anti-paternalism + context-conditional selection tracking** principle.

### Decision

**Hybrid modality availability** (fallback chain default, user-controlled filtering); **embed video inline by default with deep-link option** for fullscreen / cast-to-TV; **inline tooltip with text + linked demo video** for terminology lookup, **generalized to all domains including medical / clinical content**; **render-time presentation** at MVP (cache deferred); **hybrid system-suggestion + user-agency** for tier-shift over time, with **the system never pre-filtering options by perceived skill** — present the full range, track context-conditional selection patterns as signal not constraint.

### Q4.1 — Modality availability: hybrid fallback chain + user filter

Recipes won't all exist in all four modalities (video / structured text / cookbook prose / illustrated). System handles gaps via:

- **Default fallback chain** — preferred modality → next-best available → ultimately structured text (always available since corpus is markdown). User sees "video version not available; here's structured text instead."
- **User-controlled filtering** — user can request "show me only recipes with video for tonight" when modality matters

No recipe is hidden just because the user's preferred modality isn't available. Per Rule 10 user agency.

### Q4.2 — Video sourcing: embed inline by default + deep-link option

YouTube + subscription-platform videos are inline-embedded via WebKit / AVKit by default — keeps user in app's flow during cooking. Deep-link option for fullscreen / cast-to-TV / Picture-in-Picture cases (cooking with iPad propped + video playing on TV via cast).

A1 (pure local) compatible because video delivery is the only cloud touch and it's content delivery, not PHI. Per A1 boundaries: outbound network for non-PHI public content delivery is acceptable.

### Q4.3 — Real-time terminology lookup: inline tooltip with text + linked demo video

Inline tooltip surfaces the term definition immediately (lightweight, no leaving the recipe). One-tap-deeper opens the linked demo video if available. Definition source is the curated culinary glossary corpus (CIA professional glossary, Larousse Gastronomique, On Cooking, Joy of Cooking technique sections) per [sweep #11](../11-recipe-sourcing/scope.md).

### "Tap to understand more" — generalized cross-domain pattern *(architectural refinement from C4 Q4.3 dialogue)*

The inline-tooltip pattern is **not specific to culinary terminology**. Per user direction:

> "The same should be for medical information. We should be able to tap text and understand more of what's happening and what we're trying to understand."

The pattern generalizes: **any text the system displays can carry inline lookup.** Same UX surface, different content corpus per domain:

| Term type | Corpus source |
|---|---|
| Culinary terminology + technique | CIA professional glossary, Larousse, On Cooking, Joy of Cooking technique sections (per sweep #11) |
| Medical / clinical / nutritional terminology | MedlinePlus, NIH ODS, ADA Standards of Care patient pages, Cochrane Plain Language Summaries, NHS A–Z health topics, peer-reviewed sources via [B3 dynamic-research-expansion](#b3--dynamic-research-expansion-infrastructure) |
| Evidence-tier / certainty labels | In-system explanation of [audit-as-education pattern + 3-level certainty display per Tension #8](synthesis.md#tension-8--grade-4-level-certainty-vs-consumer-comprehension) |
| Screener / instrument names | Curated clarification corpus from [C3 Q3.2](#c3--hybrid-administration-ux) |
| Ingredient names | Authority table + [sweep #14 ingredient interaction corpus](../14-ingredient-interactions/scope.md) — pairing rationale + scientific basis on tap |
| Cuisine / cultural terminology | Cuisine + technique knowledge from [sweep #12](../12-skills-by-cuisine/scope.md) |

Design implications:

- **Text rendering throughout the app supports term annotation** — text can declare "this term is loadable" without knowing which corpus serves it
- **Centralized lookup service** routes terms to the right corpus by domain
- **Lookups are cached + persistent** — once the user has expanded a term, the system tracks the expansion for the [knowledge model](knowledge-model.md) so concepts-delivered state is updated (per [B2 epistemic trail](#b2--rule-8-epistemic-trail-implementation))

This is a real architectural pattern that affects every text-rendering surface. Worth being explicit about — captured here as a C4 deliverable but applies system-wide.

### Q4.4 — Render-time presentation at MVP

Recipes in corpus are markdown files (per A4). User-facing rendered version (embedded video, glossary tooltips, ingredient-identity authority-table links for inventory matching) is **rendered at view time at MVP**. Pre-rendered cache deferred unless rendering becomes a real latency problem.

Personal-use scale doesn't have the request volume that justifies pre-rendered caches. Render-time is simpler + always reflects current corpus state + always reflects current user preferences (modality, confidence tier). Cache complexity isn't load-bearing at our scale.

### Q4.5 — Anti-paternalism: present full range; track context-conditional selection as signal *(architectural refinement)*

Per user direction during this dialogue:

> "I don't want to be limiting users too much by our perceived skill of them. Present high-skill options, but track how often the user picks them versus the easier options. Ensure that we map that to time available and resources available, etc."

The system **does NOT pre-filter recipe surfaces by perceived skill.** Instead:

- **Full range of options including high-skill is always presented** to the user
- **Selection patterns are tracked** — how often the user picks higher-skill vs. easier options
- **Context-conditional pattern recognition** — selection mapped against time available, equipment available, current life context (busy week vs. quiet weekend, time of day, day of week, life-stage signals like high-stress periods)
- **Suggestions become context-appropriate** — if user consistently picks easier options on weekday evenings + harder options on weekend mornings, suggestions lead with appropriate options for the current context, but the **full menu stays accessible**

This sharpens [Tension #7's "honest disclosure, not default filter"](synthesis.md#tension-7--stretch-recipe-metadata-for-honest-disclosure-not-a-default-filter) principle and extends it from skill-novelty to **skill-tier selection broadly**.

**B4 schema implication flagged:** the `stretch_readiness_signal` synthesized type needs to track **context-conditional selection patterns**, not just a single "user is X-confident" scalar score. Possible dimensions:

- Skill-level actually-demonstrated through completed recipes
- Skill-level the user *picks* in different contexts (time of day, day of week, life-stage signals)
- Divergence between picked vs. demonstrated (picks high-skill but doesn't complete vs. picks easier but completes well)

Added to schema-design phase deliverables for refinement of `stretch_readiness_signal`.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — C4 marked resolved; C5 (daily-cadence interaction model) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; "tap to understand more" architectural pattern flagged as cross-cutting; `stretch_readiness_signal` schema refinement added to schema-design phase
- [B4 architecture.md entry](#b4--knowledge-model-schema-architecture-level) — `stretch_readiness_signal` description note extended with context-conditional refinement flag
- [knowledge-model.md](knowledge-model.md) — note that `stretch_readiness_signal` tracks context-conditional patterns, not a scalar score

### Sources

User direction throughout the Q4.1 → Q4.5 dialogue (2026-05-01); two user-introduced refinements during the dialogue: tap-to-understand-more pattern generalization beyond culinary terminology, and anti-paternalism + context-conditional selection tracking.

---

## C5 — Daily-cadence interaction model

> Resolved 2026-05-01 across five sub-decisions Q5.1–Q5.5, with two user-introduced refinements during dialogue: sharpened immediate-vs-later feedback content + new "reorient tonight's meal" quick-action capability.

### Decision

**Adaptive primary home-screen surface** (computed from time-of-day + recent activity); **user-configurable per-category notifications, defaults to material-only**; **two-stage feedback prompts** with cooking-experience questions immediate + body-response question later; **dual-mode epistemic trail surfacing** (inline drill-in everywhere + dedicated audit view); **quick-actions including "reorient tonight's meal"** for real-time constraint changes.

### Q5.1 — Adaptive primary home-screen surface

Home-screen primary content is computed from current time-of-day + most-recent activity. Examples:

- **Morning** — surfaces today + tomorrow's plan
- **Midday** — surfaces tonight's meal
- **Post-dinner** — surfaces feedback prompt for what was just cooked + tomorrow preview

Aligns with [Tension #1 mental-load reduction](synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction) — surfaces what's relevant *now* without the user navigating. Home-screen state is computed from current time + last meal completed + last cook confirmation + current intake / inventory / knowledge model state.

### Q5.2 — User-configurable per-category notifications, default material-only

Per [Tension #3](synthesis.md#tension-3--spaced-repetition-cadence-vs-no-daily-check-in-rule), no streak-driven daily prompts. But material updates (per [B3 Q3.5b late-arriving sub-fetch](#b3--dynamic-research-expansion-infrastructure)) and per-meal feedback timing windows are genuinely useful.

- **Per-category notification controls** — user picks what's worth interrupting them for
- **Default to material-only** — late-arriving refinements that materially change a recommendation; per-meal feedback timing within a window
- User can dial up or down per category

Respects user autonomy + [Rule 10](constitutional-rules.md#rule-10--user-decides-with-full-context).

### Q5.3 — Two-stage feedback prompts with refined content

Per user direction, two distinct prompts at different timepoints, with sharpened content:

- **Immediate (post-cook confirmation)** — about the cooking experience:
  - *"How easy was the meal to make for you?"*
  - *"How enjoyable was this to make for you?"*
- **Later (several hours)** — about the body's response:
  - *"How did this make your body feel?"*

The immediate prompt captures **cooking experience** (effort + enjoyment of the *making*) while it's fresh. The later prompt captures **body response** (energy / digestion / fullness / mood) when the data exists.

Each prompt is brief; total burden is low. User can dismiss either.

**B4 schema implication flagged:** B4 currently has `meal_feedback_liked` + `meal_feedback_time` as separate atoms but doesn't cleanly distinguish "cooking experience feedback" from "body response feedback." Schema-design phase refines this split — possibly two distinct atom types like `meal_feedback_cooking_experience` (immediate) + `meal_feedback_body_response` (later) — both still members of the `meal_event` molecule.

### Q5.4 — Dual-mode epistemic trail surfacing

- **Inline drill-in everywhere** — every recommendation, every evidence-tier label, every certainty indicator has a "show your work" affordance (per [B2 layered disclosure](#b2--rule-8-epistemic-trail-implementation))
- **Dedicated audit view** — separate surface for "show me everything the system did with my data this month" — periodic review aligned with [Rule 8 surface-the-trail commitment](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) + audit log requirements from [phi-handling.md](phi-handling.md)

Both serve different needs: inline for in-the-moment "why did you suggest this," dedicated audit for "I want to understand what the system has been up to."

### Q5.5 — Quick-actions at the home screen, including "reorient tonight's meal"

Quick-actions one-tap from the home screen:

- **"Plan this week"** — weekly plan view + suggestion flow
- **"Browse recipes"** — recipe corpus browse with filtering
- **"Continue intake"** — wherever intake left off (per [C3 Q3.3 pause-anywhere](#c3--hybrid-administration-ux))
- **"Show inventory"** — inventory state view + edit
- **"Show me what you know about me"** — knowledge model summary view (per epistemic trail surface-the-trail)
- **"What's coming up"** — grocery list + delivery / pickup status
- **"Reorient tonight's meal"** ← new per user direction

#### "Reorient tonight's meal" — life-happens affordance *(architectural refinement from C5 Q5.5 dialogue)*

Per user direction:

> "There also needs to be an option to reorient what's going on for that upcoming meal if you know time constraints have changed or something like that."

The user can change the upcoming-meal context on the fly:

- Time available shifts (got home late, need a 20-min meal not the 45-min one planned)
- Equipment changes (oven occupied, need stovetop-only)
- Ingredients shift (one of the planned ingredients went bad)
- Energy / mood shifts (don't have it in me to do something complex tonight)
- Household availability shifts (partner working late, just cooking for one)

This is the **"life happens" affordance** — the system handles real-time constraint changes gracefully without forcing the user back through full meal-planning. Not just a UI feature; it implies:

- **Meal-planning agent supports a "regenerate within updated constraints, preserving intake-level constraints" operation** that returns quickly
- **Updated constraints are session-scoped, not global** — tonight's reorient doesn't change the week's plan or intake-level constraints (allergens, conditions, life-stage, etc.)
- **Reorient flow is brief** — a few targeted questions, not a re-plan
- **Cascade-failure-aware** — if reorient triggers a fetch (e.g., new ingredient lookup), the cascade-failure model from B3 applies

Per [Rule 10 user agency](constitutional-rules.md#rule-10--user-decides-with-full-context) + [Tension #1 mental-load reduction](synthesis.md#tension-1--mental-load-framing-supersedes-raw-time-plus-inventory-tracking-distinction).

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — C5 marked resolved; Block C complete; Block D becomes available next
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; meal-feedback atom split refinement added to schema-design phase
- [B4 architecture.md entry](#b4--knowledge-model-schema-architecture-level) — meal-feedback atom split flagged for schema-design refinement

### Sources

User direction throughout the Q5.1 → Q5.5 dialogue (2026-05-01); two user-introduced refinements: immediate-vs-later feedback content sharpening + "reorient tonight's meal" quick-action.

---

*Block C complete. Block D (external integrations) is next.*

## D1 — Wearable + biometric aggregation

> Resolved 2026-05-01 across five sub-decisions Q1.1–Q1.5.

### Decision

**Hybrid HealthKit primary + direct vendor APIs as second-pass** when user requests; **MVP-priority data type set** with framework-over-source-list extensibility for additions; **HealthKit background delivery (push) primary + periodic polling backup**; **hybrid pre-computed common constraints + on-demand uncommon constraints**, all flowing through the [Tension #5 abstracted-constraint-layer](synthesis.md#tension-5--cross-sweep-wearable-data-household-sharing-gap); **validation metadata per device + signal type informs runtime confidence weighting** flowing into the knowledge model's `system_confidence` field per B4.

### Q1.1 — HealthKit primary + direct vendor APIs as second-pass

Per [A2](#a2--application-shell) (native macOS app) and [Rule 6 / phi-handling.md](#a3--llm-provider--privacy-posture), Apple HealthKit is the natural primary aggregator:

- HealthKit-primary path covers ~80% of cases automatically — Apple Watch, iPhone, plus dozens of third-party devices that mirror to HealthKit (Whoop, Oura, smart scales, BP monitors, Withings, etc.)
- Single integration with native macOS access via HealthKit framework
- Data stays local per A1 + Rule 6
- Direct vendor APIs (Whoop, Oura, Garmin, Eight Sleep, etc.) added as second-pass when the user has a specific gap (vendor doesn't mirror to HealthKit, or richer data is available via direct API than what HealthKit surfaces)

Implementation follows the [framework-over-source-list principle](dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle) — vendor adapters register their capability profiles; the framework determines what's available. Adding a vendor = drop in an adapter.

### Q1.2 — MVP-priority data type set

| Priority | Signals |
|---|---|
| **High** | Heart rate variability (HRV), resting heart rate, sleep stages + duration, weight, activity / workout summary, blood glucose (if CGM present for T1D / T2D users) |
| **Medium** | Body composition (smart scale BIA), VO2 max, training load, blood pressure |
| **Low** | Skin temperature, ECG, blood oxygen, menstrual cycle, mindfulness minutes |

These map to constraint generation per [Tension #5 abstracted-constraint-layer](synthesis.md#tension-5--cross-sweep-wearable-data-household-sharing-gap). High-priority signals produce constraints like "user is recovering — favor anti-inflammatory dinners" or "elevated post-meal glucose pattern — favor lower-glycemic options."

Adding signals later is a constraint-generator addition, not a schema change — per the framework-over-source-list principle.

### Q1.3 — Background delivery (push) primary + periodic polling backup

- **HealthKit background delivery** as the primary mechanism — efficient, immediate, native to the platform
- **Periodic polling** as backup — catches missed notifications; handles cases where push isn't available for a specific data type
- **Polling cadence respects data-type update frequency** — HRV updates several times daily, weight updates once a day at most, sleep updates once per morning, etc.

### Q1.4 — Hybrid constraint computation

- **Pre-compute common constraints continuously** — daily-recovery-status from HRV + sleep, glucose-pattern, sleep-debt, training-load. These are checked frequently enough that pre-computing wins on latency.
- **Compute uncommon constraints on-demand** — when meal planner queries for a specific constraint not in the pre-computed set
- **Pre-computed constraints live as `synthesized` entries per [B4](#b4--knowledge-model-schema-architecture-level)** with their own bitemporal lifecycle (per [A4](#a4--data-persistence--knowledge-model-storage)) — meal planner reads current state without re-computing
- All constraints flow through the [Tension #5 abstracted-constraint-layer](synthesis.md#tension-5--cross-sweep-wearable-data-household-sharing-gap) — raw data stays per-user; constraints surface to household level in cooking-terms only

### Q1.5 — Validation metadata + runtime confidence weighting

Per [Rule 7 (peer-reviewed floor)](constitutional-rules.md#rule-7--peer-reviewed-evidence-floor) + sweep #6 findings (skin-tone bias in PPG sensors, vendor-vs-independent-validation gaps):

- **Hard-coded validation metadata** per device + signal type — system knows "Apple Watch HR has X validation profile, Whoop sleep staging has Y validation profile" with sources to peer-reviewed validation literature
- **Confidence weighting per signal** — every wearable signal carries a confidence score derived from the validation profile
- **Validation metadata informs default confidence weighting** — confidence flows into the knowledge model's `system_confidence` field per [B4 Q4.1](#b4--knowledge-model-schema-architecture-level)

When the system surfaces "elevated post-meal glucose pattern detected" or "user is in low-recovery state," the user can drill in via the epistemic trail to see the device + signal + validation profile + resulting confidence — per [Rule 8 + B2 layered disclosure](#b2--rule-8-epistemic-trail-implementation).

**Skin-tone PPG bias** (per Bent et al. 2020 + Koerber et al. 2023, surfaced in sweep #6) is one specific case the validation metadata captures — signal confidence is not uniform across users; the system reflects this honestly in the epistemic trail rather than presenting a uniform confidence.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — D1 marked resolved; D2 (doctor-portal patient API integration) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated

### Sources

User direction throughout the Q1.1 → Q1.5 dialogue (2026-05-01).

---

## D2 — Doctor-portal patient API integration

> Resolved 2026-05-01 across five sub-decisions Q2.1–Q2.5, with one architectural refinement: per-document encryption for clinical source documents specifically.

### Decision

**Three-path clinical data flow** — Apple Health Records / FHIR US Core primary, direct EHR adapters second-pass, manual upload always available; **US-API-first with manual upload as the fallback for HIPAA-constrained content** even within US coverage; **substrate-extracted-data + corpus-preserved-source-documents with per-document encryption for clinical documents specifically**; **NutriMe doesn't diagnose — surfaces trends, defers to clinician**; **mechanical inheritance of B3 cache + B4 bitemporal patterns** for clinical refresh.

### Q2.1 — Three-path data flow (HealthKit primary + direct EHR + manual upload always)

Per user direction, manual upload is co-equal with API paths, not a fallback for international cases only:

> "There is a lot of documentation that we won't have API access to because of HIPAA constraints, but that the patient might be able to pull themselves as PDFs and then upload to our system."

Three paths, available in any combination:

1. **Apple Health Records (FHIR US Core) primary** — single integration covers most major US EHR vendors via Apple's patient-mediated FHIR aggregation; user authorizes once via iPhone; data flows to HealthKit and the macOS app reads it from there
2. **Direct EHR adapters** as second-pass for gaps in Apple's coverage (small regional EHRs not on Apple's list, vendors with richer direct-API data than what FHIR US Core surfaces)
3. **Manual upload** always available — patient pulls PDFs from any portal, uploads to NutriMe, system extracts structured data via LLM per [B3 dynamic-research-expansion fetch + verification pipeline](#b3--dynamic-research-expansion-infrastructure) applied to user-uploaded documents

ONC Cures Act §170.315(g)(10) compliance has driven most major US EHR vendors to support FHIR US Core; Apple Health Records aggregates this. Same framework-over-source-list discipline as D1.

### Q2.2 — US-API first; manual upload fallback for everything else

MVP: US-API via Apple Health Records (and direct EHR adapters as needed for US gaps) + manual upload fallback for all other cases.

Direct international EHR adapters (UK NHS App, Australian My Health Record, etc.) are roadmap items, not MVP. Manual upload + LLM extraction handles non-US users.

Per user direction:
> "Right now, we're only worried about US documentation."

### Q2.3 — Substrate + corpus + per-document encryption for clinical source documents

**Both extracted structured data + original source documents preserved:**

- **Extracted structured data lives in substrate** as atoms + compositions per [B4](#b4--knowledge-model-schema-architecture-level): `lab_analyte_value` atoms in `lab_panel` composition; `clinical_disclosure` atoms; `document_upload` composition with `corpus_extracted_claim` atoms
- **Original source documents preserved in corpus** with frontmatter provenance — when the system surfaces "your vitamin D is 28 ng/mL," the user can drill down via the [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) to the original lab PDF the value came from
- **Re-extraction is possible** if extraction logic improves over time

#### Per-document encryption for clinical source documents *(architectural refinement)*

Per user direction during dialogue, encryption needs surfaced honestly. Best-practice approach that fits our scope (HIPAA discipline at data-handling level, NOT formal compliance):

**Clinical source documents specifically get per-document encryption** beyond the FileVault baseline:

- **Per-document encryption with a locally-derived key** — only for clinical documents in the corpus subdirectory holding clinical source files (lab PDFs, doctor's notes, imaging reports, etc.); not all data
- **Key stored in macOS Keychain** — protected by the user's account password + macOS hardware-secured enclave (T2 / Secure Enclave on Apple Silicon)
- **Decrypt-on-read** via the application; file on disk is never plaintext
- **Per-document, not per-volume** — granular; if one document is corrupted or needs deletion, others remain intact

**Reasoning:** clinical documents are denser PHI per file than other data, often stored long-lived unmodified, and commonly caught up in document-exfiltration malware. Per-document encryption adds meaningful protection beyond FileVault with low engineering cost (encrypted-at-rest libraries mature; Keychain integration native), without crossing into compliance-grade infrastructure.

**What this is NOT:**
- Not full-database encryption (substrate + operational DBs continue as plain SQLite — fine under FileVault for our scope)
- Not formal key management infrastructure beyond Keychain
- Not breach-notification-ready (still out per [phi-handling.md](phi-handling.md))

The rest of the corpus (recipes, educational content, food composition, etc.) stays unencrypted under the FileVault baseline.

### Q2.4 — NutriMe doesn't diagnose

Sharpened from my original "capture explicit + flag patterns" framing per user direction:

> "NutriMe doesn't diagnose 2.4. We can show data, but we don't diagnose. We just say, 'Here is a trend. Consult your doctor.' Done."

**Capture explicit clinical disclosures only** (diagnosed conditions, prescribed medications, allergies as-stated in EHR data or user-provided). **Surface trends without classification** — when lab patterns suggest something not in the explicit problem list, surface the pattern data with consult-professional callout per [Rule 1](constitutional-rules.md#rule-1--consult-a-professional). The system never auto-classifies, never produces system-generated diagnoses, never surfaces inferences that could be read as diagnostic conclusions.

Sharpens the [bounded-role principle from Tension #9](synthesis.md#tension-9--pediatric-obesity-aap-2023--needs-second-pass-conditions) for clinical-pattern surfacing specifically: NutriMe shows data + defers to clinician; classification is the clinician's job, not the system's.

### Q2.5 — Mechanical inheritance of refresh + change-detection patterns

No new sub-decision. Inherits from existing decisions:

- **Annual TTL with change-triggered re-fetch** for patient-API connection per [B3 cache+freshness policy](#b3--dynamic-research-expansion-infrastructure)
- **New data triggers full re-verification + integration** via cascade-failure pattern from B3
- **Bitemporal lifecycle** per [A4](#a4--data-persistence--knowledge-model-storage) + [B4](#b4--knowledge-model-schema-architecture-level) captures historical state — superseded conditions retain their record (e.g., lactose intolerance flagged then resolved per B4 F4 example)
- **User-initiated "refresh from doctor portal" action** available for cases where the user knows new data has arrived (post-appointment, post-lab)

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — D2 marked resolved; D3 (grocery cart-aggregation integration) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated
- [phi-handling.md](phi-handling.md) — note the per-document encryption refinement for clinical source documents specifically; flag as scope-extension to the previous "filesystem encryption is sufficient" framing

### Sources

User direction throughout the Q2.1 → Q2.5 dialogue (2026-05-01); user-introduced refinement on Q2.1 (manual upload as co-equal third path) + sharpening on Q2.4 (NutriMe doesn't diagnose) + accepted encryption proposal on Q2.3.

---

## D3 — Grocery cart-aggregation integration

> Resolved 2026-05-02 across five sub-decisions Q3.1–Q3.5, with Hong Kong / Chinese market interest deferred to broader-scope-future per roadmap.

### Decision

**Three-layered cart-construction flow** (single-cart per scheduled trip + multi-cart split when retailer coverage requires + user-controlled cadence); **combined-gate substitution authorization** (pre-approved rules + system-mediated constraint checks at fulfillment time + real-time user approval only for genuine judgment calls); **cart hand-off only at MVP** (Instacart IDP recipe-link integration; user completes payment on Instacart); **both periodic polling for material state changes + user-initiated refresh**; **mechanical inheritance of sweep #13 six-tier graceful-degradation** for non-aggregator regions.

### Q3.1 — Three-layered cart-construction flow

All three patterns layered:

- **User-controlled cadence** (outermost) — user picks their grocery rhythm: weekly, twice-weekly, ad-hoc; system batches accordingly per [Rule 10 user agency](constitutional-rules.md#rule-10--user-decides-with-full-context)
- **Multi-cart split when retailer coverage requires** — when no single retailer carries everything within the user's cadence trip, system surfaces a 2-or-3-cart flow per [sweep #13 multi-store split pattern](../13-grocery-infrastructure/scope.md)
- **Single-cart-per-scheduled-trip** (innermost happy path) — system batches all needed ingredients into one cart for one delivery / pickup within each scheduled trip

User picks the rhythm; system handles the operational complexity.

### Q3.2 — Combined-gate substitution authorization

Three patterns layered into a single combined gate:

1. **Pre-approved substitution rules** as user-facing input — user sets preferences upfront for ingredient classes ("if X out of stock, accept Y; if Y also out, refund," "always accept organic substitution," "never substitute brand on dairy")
2. **System-mediated constraint check** at fulfillment time — substitution proposal goes through allergen / condition / pairing-role / dietary-pattern checks AND user's pre-approved rules in one combined gate
3. **Real-time user approval requests only when both gates can't decide** — falls through to user when novel ingredient or genuinely ambiguous case

User has direct control upfront via rules; system handles constraint-checking automatically; user only gets pinged for genuine judgment calls. This is exactly where the abstracted-constraint-layer + condition-gating + ingredient-interaction (sweep #14 pairing-role taxonomy) all converge.

### Q3.3 — Cart hand-off only at MVP

Per [sweep #13](../13-grocery-infrastructure/scope.md) findings, Instacart IDP indie-tier supports recipe-link integration (cart pre-populated, user finishes checkout on Instacart). Full programmatic order placement requires partner-tier agreement.

**MVP: cart hand-off only.** System builds cart, hands user to Instacart for checkout; user completes payment there. Works without any partnership; doesn't depend on Instacart approval timeline.

Partner-tier programmatic order placement remains a roadmap item if distribution scope ever broadens.

### Q3.4 — Both periodic polling + user-initiated refresh

- **Periodic polling** of Instacart's order status API for material state changes — specifically: delivery delays that would affect tonight's meal plan, in which case the system can proactively suggest reorienting tonight's meal per [C5 reorient affordance](#c5--daily-cadence-interaction-model)
- **User-initiated refresh** for casual checks
- **Polling cadence respectful** — once every 15-30 min during expected delivery window, not constant

### Q3.5 — Non-aggregator regions: mechanical inheritance

Mechanical inheritance from [sweep #13's six-tier graceful-degradation](../13-grocery-infrastructure/scope.md): list-export → native-grocery-app deep-link → printable list → email/SMS export → pure recipe-only display. The system gracefully degrades through the tiers; meal planning + recipes still work fully.

### Hong Kong / Chinese market interest — deferred

User flagged interest during D3 dialogue:

> "I also really want to look at what options are available to take this and translate this into something that'll work in the Chinese market, specifically in Hong Kong."

**Deferred per user direction** — *"Let's defer the Hong Kong interest until after we've built and proved the US interest. Then we can go back and see what we want to do."*

Documented in [roadmap.md](roadmap.md) under broader-scope-future. Notable HK-specific considerations to revisit when the time comes:
- Distinct grocery infrastructure: HKTVmall, Wellcome / 惠康, ParknShop / 百佳, City Super, FreshDirect HK, Foodpanda HK groceries, Amazon HK
- HKMA consumer-app framework + PDPO (Personal Data Privacy Ordinance) instead of HIPAA
- Trilingual content (Cantonese / Traditional Chinese / English) — meaningful localization work
- Cuisine assumption shifts: Cantonese / Hong Kong cha chaan teng tradition + mainland regional + global influences
- Distinct from mainland China (NMPA / cybersecurity-law frameworks) and from broader Western-audience expansion paths

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — D3 marked resolved; D4 (recipe source integration) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; Hong Kong / Chinese market expansion added to broader-scope-future tracking

### Sources

User direction throughout the Q3.1 → Q3.5 dialogue (2026-05-02); user-introduced refinement on Q3.2 (combined-gate substitution authorization with all three patterns layered) + Hong Kong market interest deferred to broader-scope-future.

---

## D4 — Recipe source integration

> Resolved 2026-05-02 across five sub-decisions Q4.1–Q4.5, with two architectural refinements: open-source-only MVP (no paid sources at start) + source-coherent multi-modality principle (no cross-source compositing).

### Decision

**Open-source / non-paid sources only at MVP** (TheMealDB + Project Gutenberg public-domain historical + open datasets per their own licenses; paid commercial APIs and subscription publishers deferred); **convert to canonical Cooklang format on ingest**, stored as markdown in corpus with provenance frontmatter, embeddings indexed into substrate per A4 + B1; **best-effort ingredient identity resolution with user-review flag**, operational nuance deferred to schema-design phase; **source-coherent multi-modality only — never cross-source composite**; **mechanical inheritance of B3 cache + B4 bitemporal patterns** with quiet-update + surface-on-next-view refinement.

### Q4.1 — Open-source-only MVP

Per user direction:

> "Whatever is minimally viable, and I think we start with no paid sources and lean on open source, non-paid to begin with."

**MVP recipe corpus baseline** (no paid sources at start):

- **TheMealDB** — free API, smaller corpus, no friction to integrate
- **Project Gutenberg public-domain historical cookbooks** — Mrs. Beeton, Fannie Farmer, multiple historical works; legally clean baseline
- **Open datasets** usable per their own licenses — RecipeNLG (academic, ~2.2M recipes), Recipe1M+ (MIT), Food.com Kaggle, OpenRecipes successors

**Deferred (not MVP):**
- Spoonacular, Edamam (paid commercial APIs) — added later if open sources prove insufficient
- NYT Cooking, ckbk, Eat Your Books (paid subscriptions) — added per gap-driven dynamic-research-expansion when user surfaces specific gaps

Source additions follow the [framework-over-source-list principle](dynamic-research-expansion.md#framework-over-source-list--the-corpus-design-principle) — new sources qualify through the [sweep #11 source qualification framework](../11-recipe-sourcing/scope.md), not added by enumeration.

### Q4.2 — Convert to canonical Cooklang on ingest

Per [sweep #11 finding](../11-recipe-sourcing/scope.md): Cooklang + schema.org/Recipe is the recommended interchange-format architecture.

- **Convert to canonical Cooklang format on ingest**
- **Store as markdown in corpus** with provenance frontmatter (source identity, content hash, ingestion timestamp, evidence tier, verification status)
- **Embeddings indexed into substrate** per [A4 + B1](#a4--data-persistence--knowledge-model-storage)
- Source-format isn't preserved long-term; provenance metadata captures the source identity
- Re-ingestion from source per B3 cache+freshness handles updates

Single canonical internal format simplifies everything downstream — ranking, presentation, modification, attribution.

### Q4.3 — Best-effort ingredient identity resolution; operational nuance deferred to schema-design phase

When a recipe arrives with "chicken thigh," it needs to resolve to the canonical authority record (per A4 authority table) so inventory matching, allergen detection, condition gating, and pairing-role substitution all work.

**Architectural-level decision: best-effort resolution with user-review flag.**

- Strict resolution is too brittle (every novel ingredient blocks ingestion)
- Lazy resolution defers the problem and means downstream queries can fail unpredictably
- Best-effort balances corpus growth with resolution quality
- Unresolved ingredients trigger the dynamic-research-expansion pipeline (per [B3](#b3--dynamic-research-expansion-infrastructure)) to fetch authority data + integrate

**Operational nuance flagged for schema-design phase per user direction:**

> "Let's actually flag this for further review because this can get pretty nuanced."

Schema-design phase resolves:
- How aggressive resolution attempts are (fuzzy match thresholds, fallback ranking)
- What counts as a confident match
- How user-review flags surface in the UX
- What fraction of corpus we're willing to ship with unresolved ingredients
- Test discipline for the resolution pipeline (heavily tested per user direction)

Added to schema-design phase deliverables.

### Q4.4 — Source-coherent multi-modality; no cross-source compositing *(architectural refinement)*

Per user direction, important sharpening of my original "auto-search for missing modalities at ingest" lean:

> "We don't want to serve something unrelated to the original recipe. If we have a text recipe from somebody's grandma that we throw in here to get surfaced, we don't want to then provide also some random YouTube video that goes with it."

**A single recipe view shows content from exactly one source, in whatever modalities that source provided.** No cross-source completion. The system never composites a recipe from multiple unrelated sources.

**Multi-modality serving is bounded by the source's own contents:**

- **Single-modality source** (text-only recipe from a cookbook) — user sees the text. No auto-search for matching video.
- **Multi-modality source** (YouTube cooking video that includes video + summary text + linked / description recipe text) — user can see all three modalities **because they all came from the same original source**

**This protects against:**

- **Attribution corruption** — grandma's recipe shouldn't appear linked to someone else's video as if they're related
- **Quality drift** — a video's interpretation of "the same dish" may differ meaningfully from the original recipe
- **Provenance confusion** — the epistemic trail should always say *one* source per recipe view, not "stitched together recipe text from X with video from Y"

**Glossary / terminology lookup is out of band** — when the user encounters an unfamiliar technique term in a recipe, they can click into a glossary lookup per the [C4 "tap to understand more" pattern](#c4--multi-modal-recipe-presentation-rendering). That's a separate corpus + separate provenance — not cross-source recipe completion. The user is not consuming the recipe in mixed-source form; they're separately learning about a technique.

### Q4.5 — Mechanical inheritance with quiet-update refinement

Mechanical inheritance from existing decisions:

- **Per-recipe re-check on cite** (not whole-corpus re-fetch) per [B3 cache+freshness](#b3--dynamic-research-expansion-infrastructure)
- **Bitemporal lifecycle preserves prior version** when source recipe changes (per [A4](#a4--data-persistence--knowledge-model-storage) + [B4](#b4--knowledge-model-schema-architecture-level))
- **Source change triggers full re-ingest + re-canonicalize**

**MVP refinement:** **don't surface every source-recipe change automatically; track in epistemic trail; surface prominently only when user accesses the recipe again.** Quiet-update + surface-on-next-view is less noisy than push-notify-on-every-change. Per Tension #1 mental-load reduction.

For recipes the user has cooked before, surfacing changes prominently when the user views again — especially if changes affect ingredients / time / technique meaningfully — per Rule 8 epistemic trail.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — D4 marked resolved; Block D complete; Block E (reproducibility + publication) becomes available next
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated; ingredient identity resolution operational nuance added to schema-design phase deliverables; paid commercial recipe sources added to broader-scope-future tracker
- [B4 architecture.md entry](#b4--knowledge-model-schema-architecture-level) — ingredient identity resolution operational nuance added as flagged schema-design phase deliverable

### Sources

User direction throughout the Q4.1 → Q4.5 dialogue (2026-05-02); two user-introduced refinements: open-source-only MVP (no paid sources at start) + source-coherent multi-modality principle (no cross-source compositing).

---

*Block D complete. Block E (reproducibility + publication) is next.*

## E1 — Data collection schema for reproducibility

> Resolved 2026-05-03 across five sub-decisions Q1.1–Q1.5; all five sub-decisions resolved to "both" — universal minimum + expanded for publication-eligible.

### Decision

**Hybrid reproducibility scope** (universal minimum metadata for all collected data; expanded metadata for publication-eligible only); **dual versioning of methodology** (coarse system version on everything + fine component version when components change); **dual drift detection** (schema versioning + diff capture in operational DB); **anonymization-ready schema** (separates identifying / analytic fields from the start) + **publication-prep logic** for edge cases; **dual data lineage** (derivation graph from epistemic trail captures data inputs + dedicated analysis metadata captures methodology that turned data into a result).

### Q1.1 — Hybrid reproducibility scope

- **Universal minimum metadata** for all collected data — provenance + timestamp + version stamp on every atom + composition + synthesized entry. Aligns with epistemic-trail discipline already settled in [B2](#b2--rule-8-epistemic-trail-implementation) + [B4](#b4--knowledge-model-schema-architecture-level).
- **Expanded metadata** only for publication-eligible data — sample design, anonymization-ready fields, IRB-equivalent context, methodology spec
- Marked as publication-eligible at write time (not retroactively) — eligibility is a flag the writing code declares per [publication-ambitions.md](publication-ambitions.md) target inventory

Universal minimum is cheap and aligns with existing discipline; expanded metadata is justified by the publication ambition; trying to apply full reproducibility metadata to every casual data write is overhead without payoff.

### Q1.2 — Dual versioning of methodology

Per [B4](#b4--knowledge-model-schema-architecture-level) + [C2](#c2--cat--irt-integration) + [B3](#b3--dynamic-research-expansion-infrastructure), versioning of *content sources* (item-bank version stamp, content-source TTLs) is already settled. E1 extends to versioning of **collection methodology itself**:

- **Coarse system version** on every atom — system version + relevant component version (intake-agent version, screener-administration version, semantic-feedback-prompt version)
- **Fine component version** stamped only when methodology actually changes — if v1.2 of system uses same methodology as v1.1 for screener X, no new component-version stamp on screener X data; if v1.3 changes the screener-administration logic, new component-version stamp goes on data collected from v1.3 forward

Both feed reproducer-side analysis: *"all data collected under intake-agent v2.x"* vs. *"all data collected under system v1.5 to v1.7 regardless of which intake-agent version."*

### Q1.3 — Dual drift detection

Methodology drift (changes in how the system collects data) and content-source drift (changes in upstream sources) both affect reproducibility:

- **Schema versioning** — every methodology + content-source change bumps a version; reproducer sees the version chain. Automatic, queryable substrate.
- **Diff capture** — when methodology or content source changes, the system records *what* changed (not just "version bumped" but *"this question now asks X instead of Y,"* *"this content source dropped field Z"*). Recorded in operational DB.

Version chain is automatic + queryable; diff capture is one-time cost at change time + reproducer-actionable detail. Both needed for honest reproducibility.

### Q1.4 — Anonymization-ready schema + publication-prep logic

Per [publication-ambitions.md](publication-ambitions.md) data collection design must support reproducibility-aware anonymization from the start.

- **Anonymization-ready schema** — schema separates identifying fields from analytic fields from the start; publication-prep logic just selects analytic fields, no transformation needed at publication time. Prevents accidental identifier leakage by construction.
- **Publication-prep logic** for edge cases — low-cardinality fields that are technically non-identifying but might re-identify in combination; rare-condition disclosures that uniquely identify even when isolated; small-sample concerns where individual users could be identified by clustering. Logic handles edge cases the schema separation doesn't.

Schema separation is the foundation; publication-prep logic is the safety net. Per [E2 anonymization + consent infrastructure](#e2--anonymization--consent-infrastructure) (next decision).

### Q1.5 — Dual data lineage

When a publishable analysis is performed (e.g., aggregate recipe time-feedback analysis per publication target #4), the analysis must be reproducible from underlying data. Per [Rule 8 epistemic trail](constitutional-rules.md#rule-8--epistemic-trail-of-honesty) + [B2](#b2--rule-8-epistemic-trail-implementation), the derivation graph from atoms → synthesized entries is already partially settled.

- **Reproducibility inherits from epistemic trail** — the same derivation graph that supports the trail also supports reproducibility queries. The data inputs to any analysis are queryable via DerivedFrom traversal.
- **Dedicated analysis metadata** — analyses get their own metadata: analysis version, timestamp, parameters used, code git SHA, embedding model used (per [B1 Q1.3](#b1--semantic-rag-vs-structured-query-strategy) Voyage vs. local), inference results

Derivation graph reproduces the **data side** (what data fed into this analysis); analysis metadata reproduces the **methodology side** (what code, what parameters, what models turned data into result). Both needed for true reproducibility.

Becomes important the moment publication target #4 (recipe time-feedback aggregate data) actually starts shipping data, and target #5 (cooking-state changes pairings) similarly.

### Updates to apply

- [stage3-plan.md](stage3-plan.md) — E1 marked resolved; E2 (anonymization + consent infrastructure) becomes the next decision
- [roadmap.md](roadmap.md) — Stage 3 architecture decisions table updated
- [publication-ambitions.md](publication-ambitions.md) — methodology principles section refined with dual-versioning + dual drift detection + anonymization-ready schema + dual data lineage details
- [B4 architecture.md entry](#b4--knowledge-model-schema-architecture-level) — universal-minimum-metadata + expanded-for-publication-eligible distinction added as schema-design phase deliverable

### Sources

User direction throughout the Q1.1 → Q1.5 dialogue (2026-05-03); all five sub-decisions resolved to "both" — both universal + expanded, both coarse + fine versioning, both schema + diff drift detection, both anonymization-ready schema + publication-prep logic, both inherited derivation + dedicated analysis metadata.

---

*Future architecture decisions will be added as resolved.*
