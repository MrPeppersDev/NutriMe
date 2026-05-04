# NutriMe — Schema Design (Stage 3.5)

> Living document capturing Stage 3.5 schema-design decisions. Sister doc to [architecture.md](architecture.md) (Stage 3 architecture decisions) and [synthesis.md](synthesis.md) (Stage 2 cross-cutting design tensions). Each sub-block captures: what was decided, why, and which docs were updated.

## How this doc works

Stage 3.5 is the schema-design phase that resolves the deferred refinements collected throughout Stage 3 (B4 F1–F8 + C4 + C5 + D4 + E1 + E4 refinements) plus the standard schema-design work (table layouts + indexes + FK + migrations + verification rule-set + embedding-table layout).

12 sub-blocks (S1–S12) ordered so each unblocks the next. Same Stage 3 dialogue cadence — proposals with sub-questions, decisions, captured here as resolved.

---

## S1 — Base-table architecture

> Resolved 2026-05-03 across five sub-decisions Q1.1–Q1.5.

### Decision

**Single-table-per-layer + JSON payload** (three tables: `atom`, `molecule`, `synthesized_entry`); **15 shared base columns** spanning provenance, evidence, confidence, bitemporal lifecycle, retraction, versioning, consent, PHI, authority resolution; **typed prefix + UUIDv7** for IDs (`atm-...`, `mol-...`, `syn-...`); **UTC always** for all timestamps; **dual JSON schema validation** (application code primary + SQLite CHECK constraints as safety net).

### Q1.1 — Single-table-per-layer + JSON payload

Three tables, one per atom/molecule/synthesized layer. Within each layer, type-specific fields live as JSON in a `payload` column with a `type` discriminator field.

- Atomic / molecule / synthesized layer distinction is meaningful per [A4 + B4](architecture.md#a4--data-persistence--knowledge-model-storage) and warrants table-level separation (different write semantics, different mutability discipline)
- Within each layer, type-specific fields as JSON payload — adding new types is a new discriminator value + payload schema documented in code, not a new table + migration
- SQLite's JSON support (json_extract, json_set, generated columns from JSON paths) is mature enough to make this practical
- Indexes on commonly-queried JSON paths via generated columns when needed
- Per Stage 3 framework-over-source-list discipline + LC research's "extract selectively" warning — adding 17+ tables for 17+ atom types is overengineering

### Q1.2 — Shared base columns (15)

Per critical re-look against Stage 3 commitments, 6 columns added beyond the initial proposal:

```sql
id                          TEXT PRIMARY KEY        -- typed prefix + UUIDv7 (atm-018f3..., mol-018f3..., syn-018f3...)
type                        TEXT NOT NULL           -- discriminator (intake_response, lab_panel, meal_plan, etc.)
subject_id                  TEXT                    -- per F2: user_id / household_id / member_subset_id
subject_type                TEXT                    -- per F2: 'user' | 'household' | 'member_subset'
provenance                  TEXT NOT NULL           -- 'validated-instrument' | 'conversational-elicitation' | 'passive-observation'
source_identity             TEXT                    -- structured per type; references originating event/document/utterance
evidence_tier               INTEGER                 -- 1 | 2 | 3 | 4 | NULL (per evidence-tiers.md)
system_confidence           REAL                    -- 0.0–1.0 (per B4 Q4.1)
user_facing_certainty       TEXT                    -- 'strong' | 'moderate' | 'suggestive' | NULL (per Tension #8)
valid_from                  TEXT NOT NULL           -- ISO 8601 UTC
valid_until                 TEXT                    -- ISO 8601 UTC; NULL = currently valid
recorded_at                 TEXT NOT NULL           -- ISO 8601 UTC; when written to DB
retraction_reason           TEXT                    -- NULL | 'superseded' | 'retracted_user_correction' | 'retracted_source_revision' | 'retracted_validation_failure' | 'retracted_consent_withdrawn'
system_version              TEXT NOT NULL           -- coarse system version (per E1 Q1.2)
component_version           TEXT                    -- fine component version when methodology changed (per E1 Q1.2)
payload_schema_version      TEXT NOT NULL           -- payload schema version per type
publication_eligible        INTEGER                 -- 0 | 1; fast filter (per E1 Q1.1)
consent_record_id           TEXT                    -- FK to consent record (per E2 + E3 license-bound-to-consent)
phi_categories              TEXT NOT NULL           -- JSON array of PHI category names; '[]' for non-PHI (per C1 Q1.5)
authority_resolution_status TEXT                    -- NULL | 'fully_resolved' | 'partial' | 'unresolved_pending_review' | 'unresolved_dynamic_expansion_in_flight'
payload                     TEXT NOT NULL           -- JSON payload, type-specific schema
```

Six additions beyond the initial proposal, with confidence honestly recorded:

- **`source_identity`** (~85% confident) — load-bearing for B2 epistemic trail layered disclosure; carries the specific source identity that `provenance` (a category) doesn't
- **`retraction_reason`** (~80%) — captures F4 distinction between superseded vs. retracted (user-correction, source-revision, validation-failure, consent-withdrawn)
- **`payload_schema_version`** (~80%) — E1 reproducibility requires it; payload schema may evolve independently of system or component version
- **`consent_record_id`** (~70%) — FK to consent record table (S8 deliverable); shape may evolve when S8 lands
- **`phi_categories`** (~80%) — C1 Q1.5 double-layer PHI enforcement needs this for routing/filtering without payload parsing
- **`authority_resolution_status`** (~65%) — only relevant for entries referencing authority records; may shift to typed-relationship state in S4

Per-layer additions:
- **`atom` table** adds `composition_id TEXT` (FK to molecule, nullable per F1 — atom may exist without composition)
- **`molecule` table** adds nothing (composition_type folds into base `type`)
- **`synthesized_entry` table** adds nothing layer-specific; relationships are external in S4

### Q1.3 — Typed prefix + UUIDv7 IDs

`atm-018f3...`, `mol-018f3...`, `syn-018f3...`

- Helps debugging (you can see at a glance what kind of entry an ID refers to)
- UUIDv7 sorts well for time-ordered queries (per bitemporal queries on `valid_from`)
- Typed prefix is 4-char overhead per ID; cheap

### Q1.4 — UTC always for timestamps

Every timestamp stored as UTC ISO 8601. Single source of truth for time; conversion to local time is a presentation-layer concern. No timezone-comparison bugs. Per Apple platform conventions (NSDate is UTC under the hood).

### Q1.5 — Dual JSON schema validation

Both:

- **Application code as primary validation** — better error messages, richer schema language than SQLite CHECK constraints
- **SQLite CHECK constraints as safety net** — uses `json_valid()` + path-specific validations to catch any schema drift that escapes application validation

Per the publication-ambitions-from-day-one discipline + the "fails closed" PHI-handling pattern.

### Out of scope at S1 (deferred to later sub-blocks)

- Specific per-type payload schemas — S2 covers atom/molecule/synthesized type tables in detail
- F1 asynchrony / temporal state model details — S3 resolves the F-flag set
- F2 subject_type granularity (`member_subset` semantics) — S3 resolves
- Typed relationship table layout — S4
- Embedding tables — S5
- Authority table — S6
- Verification rule-set — S7
- Consent record table layout — S8
- Corpus markdown frontmatter contract — S9
- system_confidence numeric mapping detail — S10
- Foreign keys + referential integrity — S11
- Migration strategy — S12

### Sources

User direction throughout the Q1.1 → Q1.5 dialogue (2026-05-03); user pushed back on Q1.2 to think more critically, leading to 6 field additions surfaced from a re-check against Stage 3 commitments.

---

## S2 — Atom + molecule + synthesized type tables (payload-shape principles)

> Resolved 2026-05-03 across five sub-decisions Q2.1–Q2.5. Per-type payload schemas (17 atom + 8 molecule + 16 synthesized) follow in subsequent batches within this sub-block.

### Decision

**Flat unless nesting is genuinely useful** for payload structure; **explicit required vs. optional discipline with explicit-null for absent optionals**; **no reserved keys at payload root** (premature for MVP); **snake_case throughout**; **units always in field names** (e.g. `glucose_mg_dl`, `cooking_time_minutes`, `weight_kg`); **per-type judgment for plain-text vs. markdown free-text fields**; **hybrid schema-of-schemas** (canonical declarative file + per-type modules that import + extend with runtime-specific concerns).

### Q2.1 — Payload-shape principles

- **Flat unless nesting is genuinely useful.** Most atom payloads are simple single observations; some molecule + synthesized payloads need nesting for genuinely-structured content (sub-scores in screener_result, multi-part inferences in synthesized entries).
- **Required vs. optional explicit per type** with explicit-null discipline for optional fields (rather than absent fields).
- **No reserved keys at payload root** at MVP. Premature optimization. If a cross-type pattern emerges (free-text user notes attached to any entry, etc.), elevate to a base column or typed sub-table later.

### Q2.2 — snake_case throughout

Standard for SQLite + JSON-in-SQLite + Python. Matches base column naming. Per-publication reproducibility benefits from convention consistency.

### Q2.3 — Units always in field names

Examples: `glucose_mg_dl`, `cooking_time_minutes`, `weight_kg`, `hrv_ms`, `sleep_duration_min`.

- Eliminates ambiguity (kg vs. lb; mg/dL vs. mmol/L for glucose)
- Self-documenting at query time
- Aligns with publication-reproducibility discipline
- Per-publication-target consumers can convert if they want different units; source data has unambiguous units

### Q2.4 — Per-type judgment for plain-text vs. markdown free-text

Atom-types like `meal_feedback_body_response` (per [C5 split](architecture.md#c5--daily-cadence-interaction-model)) get plain-text fields — the user said *"I felt sluggish around 8pm"*; no markdown semantics needed.

Atom-types like `corpus_extracted_claim` get markdown fields — preserves source structure (lists, emphasis, etc. from the original document).

Per-type schema declares which fields are plain vs. markdown; the rendering layer handles accordingly.

### Q2.5 — Hybrid schema-of-schemas

**Canonical declarative schema file** at top level lists every type + its base schema. **Per-type modules** import from the canonical file and extend with runtime-specific concerns:

- **Canonical file** (`payload_schemas.json` or equivalent declarative format) — source-of-truth; every atom/molecule/synthesized type listed; schema declared in declarative format (field names, types, required/optional, units, validation rules)
- **Per-type modules** (`atoms/intake_response.py`, `atoms/lab_analyte_value.py`, etc.) — import their schema from canonical file, layer on type-specific business logic (write helpers, transformation, type-aware error messages)
- **CHECK-constraint generator** reads canonical file → emits SQL CHECK clauses for the substrate DB per [S1 Q1.5 dual validation](#s1--base-table-architecture)
- **Publication-target reproducers** can read the canonical file directly without parsing application code

Better than pure-canonical-only because per-type modules add type-aware error messages + transformation without the canonical file becoming a junk drawer. Better than pure-per-type-only because the audit + reproducibility surface stays single-file-readable.

### Out of scope at S2 principles (next batches within this sub-block)

- Per-atom-type payload schemas (17 types) — atoms batch
- Per-molecule-type payload schemas (8 types) — molecules batch
- Per-synthesized-type payload schemas (16 types + C5 meal-feedback split + C4 stretch_readiness_signal context-conditional refinement) — synthesized batch

### Sources

User direction throughout the Q2.1 → Q2.5 dialogue (2026-05-03); user picked hybrid on Q2.5 (sharper than my pure-canonical lean).

---

*Per-type payload schema batches follow within this sub-block.*
