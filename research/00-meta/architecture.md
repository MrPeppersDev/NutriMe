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

*Future architecture decisions will be added as resolved.*
