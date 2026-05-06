# NutriMe — Schema Design (Stage 3.5)

> Living document capturing Stage 3.5 schema-design decisions. Sister doc to [architecture.md](architecture.md) (Stage 3 architecture decisions) and [synthesis.md](synthesis.md) (Stage 2 cross-cutting design tensions). Each sub-block captures: what was decided, why, and which docs were updated.

## How this doc works

Stage 3.5 is the schema-design phase that resolves the deferred refinements collected throughout Stage 3 (B4 F1–F8 + C4 + C5 + D4 + E1 + E4 refinements) plus the standard schema-design work (table layouts + indexes + FK + migrations + verification rule-set + embedding-table layout).

12 sub-blocks (S1–S12) ordered so each unblocks the next. Same Stage 3 dialogue cadence — proposals with sub-questions, decisions, captured here as resolved.

---

## S1 — Base-table architecture

> Resolved 2026-05-03 across five sub-decisions Q1.1–Q1.5.

### Decision

**Single-table-per-layer + JSON payload** (three tables: `atom`, `molecule`, `synthesized_entry`); **15 shared base columns at S1, expanded to 24 after S7** spanning provenance, evidence, confidence, bitemporal lifecycle, retraction, versioning, consent, PHI, authority resolution, and verification status (S7 adds `verification_status` + `last_verified_at` + `verification_summary`); **typed prefix + UUIDv7** for IDs (`atm-...`, `mol-...`, `syn-...`); **UTC always** for all timestamps; **dual JSON schema validation** (application code primary + SQLite CHECK constraints as safety net).

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

### S2 — Atom payload schemas (Batch 1: 18 atom types)

> Resolved 2026-05-03.

Per-type payload schemas for atoms. Each lives in the `payload` JSON column of the `atom` table, alongside the 15 base columns from S1. Snake_case throughout, units in field names, required vs. optional explicit, plain-text vs. markdown declared per field per S2 principles.

**Atom count:** 18 = B4's original 17 + C5's net addition of 1 (meal-feedback split into `meal_feedback_cooking_experience` + `meal_feedback_body_response` + `meal_feedback_time` = three distinct types instead of B4's original `meal_feedback_liked` + `meal_feedback_time` two-type split).

#### Atom 1 — `intake_response`

```
required:
  question_id           TEXT
  question_text         TEXT      -- verbatim text shown to user (preserved per Tension #4)
  response_value        TEXT      -- raw response (string for free-text, JSON-stringified for structured)
  response_type         TEXT      -- 'free_text_plain' | 'single_choice' | 'multi_choice' | 'numeric' | 'scale' | 'date'
  intake_session_id     TEXT      -- FK to intake_session molecule
optional:
  response_options      JSON_ARRAY  -- if response_type involved choice; null otherwise
  freetext_format       TEXT        -- 'plain' | 'markdown'; null for non-freetext
  user_clarification_requested  BOOLEAN  -- true if user asked for item-level clarification per C3 Q3.2
```

#### Atom 2 — `screener_result`

```
required:
  instrument_name       TEXT      -- 'PHQ-9' | 'GAD-7' | 'SCOFF' | etc.
  instrument_version    TEXT      -- per C2 Q2.4 item-bank version stamp
  score                 REAL
  score_interpretation  TEXT      -- 'none' | 'mild' | 'moderate' | 'severe' | etc. per instrument
  scoring_method        TEXT      -- 'CAT' | 'sum_score' | 'weighted_sum' per C2 Q2.3
optional:
  per_item_responses    JSON_ARRAY  -- nested for sub-score reconstruction; null if not required
  early_stopped         BOOLEAN     -- per C2 Q2.5; null for non-CAT instruments
  precision_metric      REAL        -- standard error or similar; CAT only
```

#### Atom 3 — `literacy_response`

```
required:
  literacy_type         TEXT      -- 'highest_education' | 'health_literacy' | 'cooking_literacy'
  instrument_name       TEXT      -- 'NVS' | 'REALM-SF' | 'TOFHLA' | 'eHEALS' | 'self_reported_education' | 'cooking_literacy_inventory'
  instrument_version    TEXT
  score                 REAL
  score_interpretation  TEXT
optional:
  per_item_responses    JSON_ARRAY
```

#### Atom 4 — `pediatric_observation`

```
required:
  observation_type      TEXT      -- 'growth_metric' | 'allergen_history' | 'developmental_eating' | 'screener_result' | etc.
  child_member_id       TEXT      -- FK to household member; child specifically
  parent_recorder_id    TEXT      -- FK to household member; parent who recorded
  observation_value     JSON      -- structured per observation_type
optional:
  age_at_observation_months  INTEGER  -- computed from child DOB + observation date
  growth_chart_percentile    REAL     -- if observation_type is growth_metric
```

#### Atom 5 — `cook_confirmation`

```
required:
  recipe_id             TEXT      -- FK to recipe in corpus
  recipe_version        TEXT      -- per E4 + B3 cache+freshness; recipe version at time of cook
  meal_event_id         TEXT      -- FK to meal_event molecule
  cooked_at             TEXT      -- ISO 8601 UTC
optional:
  modifications         TEXT      -- markdown free-text; user's own modifications/substitutions noted
  modifications_format  TEXT      -- always 'markdown' if modifications present
```

#### Atom 6 — `meal_feedback_cooking_experience` *(per C5 split refinement)*

```
required:
  meal_event_id         TEXT
  ease_rating           INTEGER   -- 1-5 scale; "How easy was the meal to make for you?"
  enjoyment_rating      INTEGER   -- 1-5 scale; "How enjoyable was this to make for you?"
  prompt_responded_at   TEXT      -- ISO 8601 UTC
optional:
  freetext_notes        TEXT      -- plain-text user notes
  freetext_format       TEXT      -- always 'plain' if freetext_notes present
```

#### Atom 7 — `meal_feedback_body_response` *(per C5 split refinement)*

```
required:
  meal_event_id         TEXT
  freetext_response     TEXT      -- "How did this make your body feel?" (plain-text; the feeling itself is the data)
  freetext_format       TEXT      -- always 'plain'
  prompt_responded_at   TEXT      -- ISO 8601 UTC
optional:
  energy_rating         INTEGER   -- 1-5 scale; null if user didn't volunteer
  digestion_rating      INTEGER   -- 1-5 scale
  fullness_rating       INTEGER   -- 1-5 scale
  mood_rating           INTEGER   -- 1-5 scale
```

#### Atom 8 — `meal_feedback_time`

```
required:
  meal_event_id         TEXT
  estimated_time_min    INTEGER   -- recipe's stated time
  actual_time_min       INTEGER   -- user's reported actual time
  time_delta_min        INTEGER   -- generated column or computed
  prompt_responded_at   TEXT      -- ISO 8601 UTC
```

#### Atom 9 — `wearable_signal_aggregate`

```
required:
  signal_type           TEXT      -- 'hrv_ms' | 'resting_hr_bpm' | 'sleep_duration_min' | 'sleep_stage_distribution' | 'weight_kg' | 'glucose_mg_dl' | 'activity_minutes' | etc.
  source_device         TEXT      -- 'apple_watch_s9' | 'whoop_4' | 'oura_gen3' | 'apple_health_kit_aggregate' | etc.
  validation_profile_id TEXT      -- FK to validation metadata table per D1 Q1.5
  aggregate_value       REAL
  aggregate_method      TEXT      -- 'daily_avg' | 'weekly_avg' | 'nightly_total' | 'instantaneous' | etc.
  measurement_period_start TEXT   -- ISO 8601 UTC
  measurement_period_end   TEXT   -- ISO 8601 UTC
optional:
  raw_value_count       INTEGER   -- how many raw measurements went into aggregate
  confidence_modifier   REAL      -- 0.0-1.0; per validation profile (e.g., skin-tone PPG bias adjustment per Bent 2020)
```

#### Atom 10 — `lab_analyte_value`

```
required:
  lab_panel_id          TEXT      -- FK to lab_panel molecule
  analyte_name          TEXT      -- 'vitamin_d' | 'b12' | 'a1c' | 'ferritin' | etc.
  analyte_canonical_id  TEXT      -- FK to authority record (S6); resolves nutrient identity across labs
  value                 REAL
  unit                  TEXT      -- 'ng_ml' | 'pg_ml' | 'percent' | 'ng_dl' | etc.
  reference_range_low   REAL      -- lab's stated low end of normal
  reference_range_high  REAL      -- lab's stated high end of normal
  measurement_date      TEXT      -- ISO 8601; date of blood draw
optional:
  lab_provider          TEXT      -- 'labcorp' | 'quest' | etc.
  collection_method     TEXT      -- 'venous_blood' | 'capillary_blood' | 'urine' | etc.
  abnormal_flag         TEXT      -- 'low' | 'high' | 'normal' per lab's interpretation; null if not provided
```

#### Atom 11 — `inventory_observation`

```
required:
  ingredient_canonical_id TEXT    -- FK to authority record
  ingredient_text       TEXT      -- as user/source described it
  observation_type      TEXT      -- 'have' | 'don't_have' | 'running_low' | 'expired' | 'used_up'
  observed_at           TEXT      -- ISO 8601 UTC
  observation_source    TEXT      -- 'initial_intake' | 'order_inferred' | 'cook_confirmation_decrement' | 'just_in_time_clarification' | 'manual_user_update'
optional:
  approximate_quantity  TEXT      -- "about 2 lbs" | "almost done" | etc.; loose per Tension #1
  precise_quantity      REAL      -- only when just-in-time clarification asked for precision
  precise_unit          TEXT      -- only when precise_quantity present
  storage_location      TEXT      -- 'pantry' | 'fridge' | 'freezer' | etc.
```

#### Atom 12 — `grocery_order_record`

```
required:
  grocery_order_id      TEXT      -- FK to grocery_order molecule
  ingredient_canonical_id TEXT
  ingredient_text       TEXT      -- as ordered
  quantity              REAL
  unit                  TEXT
  retailer              TEXT      -- 'instacart_safeway' | 'kroger' | 'amazon_fresh' | etc.
optional:
  brand                 TEXT
  was_substitution      BOOLEAN   -- true if Instacart shopper substituted per D3 Q3.2
  original_requested    TEXT      -- if substitution, what was originally requested
```

#### Atom 13 — `clinical_disclosure`

```
required:
  disclosure_type       TEXT      -- 'condition' | 'medication' | 'allergy' | 'intolerance' | 'past_event'
  disclosure_text       TEXT      -- as disclosed; verbatim if user-typed; standardized if from EHR
  disclosure_text_format TEXT     -- 'plain' | 'markdown'
  disclosure_source     TEXT      -- 'self_reported_intake' | 'ehr_extracted' | 'manual_upload_extracted'
optional:
  canonical_code        TEXT      -- ICD-10/SNOMED/RxNorm code if available
  canonical_code_system TEXT      -- 'icd10' | 'snomed' | 'rxnorm' | etc.
  disclosure_date       TEXT      -- when condition was diagnosed/medication started/etc.
  active                BOOLEAN   -- still relevant; null = unknown/not stated
```

#### Atom 14 — `preference_statement`

```
required:
  preference_type       TEXT      -- 'cuisine_like' | 'cuisine_dislike' | 'ingredient_dislike' | 'ingredient_want_to_try' | 'cooking_method_preference' | 'dietary_pattern_preference' | etc.
  subject_text          TEXT      -- "Italian" | "cilantro" | "fermented foods" | etc.
  subject_canonical_id  TEXT      -- FK to authority record if resolved; null if unresolved
  strength              TEXT      -- 'mild' | 'moderate' | 'strong' | 'absolute'
  preference_format     TEXT      -- 'plain' (preferences are simple strings)
optional:
  reason                TEXT      -- plain-text user explanation if volunteered
```

#### Atom 15 — `document_upload_event`

```
required:
  document_upload_id    TEXT      -- FK to document_upload molecule
  filename              TEXT
  file_hash             TEXT      -- SHA-256 of original file
  file_type             TEXT      -- 'pdf' | 'jpeg' | 'png' | 'docx' | etc.
  file_size_bytes       INTEGER
  uploaded_at           TEXT      -- ISO 8601 UTC
  encryption_status     TEXT      -- 'encrypted_at_rest' for clinical docs per D2 Q2.3 refinement; 'unencrypted' for non-clinical
optional:
  user_provided_label   TEXT      -- "Lab results from Dr. Smith" etc.
  source_context        TEXT      -- 'clinical' | 'recipe' | 'nutrition_reference' | etc.
```

#### Atom 16 — `corpus_extracted_claim`

```
required:
  document_upload_id    TEXT      -- FK to document_upload molecule (or to corpus markdown source for system-fetched)
  claim_text            TEXT      -- markdown; preserves source structure
  claim_text_format     TEXT      -- always 'markdown'
  claim_type            TEXT      -- 'fact' | 'measurement' | 'recommendation' | 'caveat' | 'definition' | etc.
  extraction_method     TEXT      -- 'llm_structured_extraction' | 'rule_based_parser' | 'manual'
  extraction_confidence REAL      -- 0.0-1.0
optional:
  source_page_or_section TEXT     -- where in source document the claim appears
  source_quote          TEXT      -- verbatim quote from source supporting the claim
```

#### Atom 17 — `recipe_attribution_record`

```
required:
  recipe_id             TEXT      -- FK to recipe in corpus
  source_name           TEXT      -- 'NYT Cooking' | 'TheMealDB' | 'Mrs. Beeton 1861' | etc.
  source_url            TEXT      -- where applicable
  source_license        TEXT      -- 'CC-BY-4.0' | 'public_domain' | 'TheMealDB_terms' | 'subscription_NYTCooking' | etc.
  ingested_at           TEXT      -- ISO 8601 UTC
  ingestion_method      TEXT      -- 'api_fetch' | 'rss' | 'manual_upload' | 'mirror_tool' per dynamic-research-expansion
optional:
  source_attribution_text  TEXT   -- preferred attribution string per source's own request (Cochrane-style citation template)
  source_first_published   TEXT   -- ISO 8601 date if known
```

#### Atom 18 — `phi_crossing_event`

```
required:
  operation_type        TEXT      -- 'recipe_filter' | 'nutrient_compute' | 'condition_substitution' | 'cuisine_query' | etc.
  llm_provider          TEXT      -- 'anthropic_claude' | 'google_gemini' | 'local_ollama' | etc.
  llm_model             TEXT      -- specific model identifier
  phi_categories_sent   TEXT      -- JSON array of PHI categories included
  phi_categories_returned TEXT    -- JSON array of PHI categories in result
  request_id            TEXT      -- correlation ID for joining to operational event log
  crossed_at            TEXT      -- ISO 8601 UTC
optional:
  decomposed_from_request TEXT    -- correlation ID of higher-level user request that decomposed into this crossing
```

### Sources

User direction (2026-05-03) on Atom payload schemas batch 1.

---

### S2 — Molecule payload schemas (Batch 2: 8 molecule types)

> Resolved 2026-05-03 with explicit lower-confidence flags on 4 items. Overall confidence ~70%; same hybrid-A-and-C pattern from B4: land at schema-design level with confidence flags + revisit during S3 F1 (asynchrony / temporal state model) + after synthesized batch lands.

Per A4 + B4: molecules are compositions of co-belonging atoms. They aggregate atoms via membership (atom's `composition_id` FK) but also carry composition-level metadata (when the composition started, when it closed, who/what created it, composition-level summaries).

#### Molecule 1 — `intake_session` *(~85% confident)*

```
required:
  session_started_at    TEXT      -- ISO 8601 UTC
  session_closed_at     TEXT      -- ISO 8601 UTC; null if still in progress
  session_purpose       TEXT      -- 'initial_intake' | 'periodic_check_in' | 'condition_disclosure_followup' | 'custom'
  total_questions_asked INTEGER   -- count for completion tracking
  total_questions_answered INTEGER
optional:
  pause_resume_count    INTEGER   -- per C3 Q3.3 pause-anywhere; 0 if completed in one sitting
  user_initiated_resume_at JSON_ARRAY  -- timestamps of resume events
  intake_agent_version  TEXT      -- per E1 component_version; specific agent used
```

#### Molecule 2 — `lab_panel` *(~85% confident)*

```
required:
  lab_provider          TEXT      -- 'labcorp' | 'quest' | etc.
  collection_date       TEXT      -- ISO 8601; date of blood draw
  panel_name            TEXT      -- 'CBC + CMP + Lipid' | 'thyroid_panel' | 'micronutrient_panel' | etc.
  ingestion_path        TEXT      -- 'apple_health_records' | 'epic_mychart_api' | 'manual_pdf_upload' per D2 Q2.1
optional:
  ordering_provider     TEXT      -- doctor/clinic that ordered the panel
  panel_id_at_provider  TEXT      -- the lab's own panel ID for reference
  panel_status          TEXT      -- 'final' | 'preliminary' | 'amended'
  retraction_propagated BOOLEAN   -- per F4 retraction-propagation; true if retraction triggered downstream re-derivation
```

#### Molecule 3 — `wearable_daily_aggregate` *(⚠ ~55% confident — flagged for revisit)*

```
required:
  observation_date      TEXT      -- ISO 8601 date (no time); the day this aggregate represents
  source_devices        JSON_ARRAY -- list of devices contributing aggregates this day
  signal_type_count     INTEGER   -- how many distinct signal types this day's aggregate covers
optional:
  data_completeness     TEXT      -- 'full' | 'partial' | 'sparse' based on expected vs. actual signals
```

**⚠ Confidence flag M3:** Is this meaningfully a molecule, or is it a query view? Same-day wearable atoms don't have the substantive co-belonging that lab_panel atoms do (same blood draw). Argument for keeping: stable join target + day-level metadata like `data_completeness`. Argument against: reducible to a query over wearable_signal_aggregate atoms by date. Revisit during S3 F1.

#### Molecule 4 — `meal_event` *(⚠ ~60% confident — flagged for field-set revisit)*

```
required:
  meal_recommendation_id TEXT     -- FK to the synthesized meal_recommendation that suggested this; null if user-initiated cooking
  recipe_id             TEXT      -- FK to recipe in corpus
  recipe_version        TEXT
  meal_slot             TEXT      -- 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'special_occasion'
  planned_for_date      TEXT      -- ISO 8601 date
  household_eaters      JSON_ARRAY -- member IDs of who ate this; per Tension #5 abstracted-constraint-layer
  cooked                BOOLEAN   -- true if cook_confirmation atom present
optional:
  reorient_event        BOOLEAN   -- per C5 Q5.5; true if user invoked "reorient tonight's meal"
  reorient_reason       TEXT      -- 'time_constraint' | 'equipment' | 'ingredient_unavailable' | 'energy' | 'household_change' | 'other'
  skipped               BOOLEAN   -- true if explicitly skipped (vs. just not yet cooked)
  skip_reason           TEXT      -- if skipped
```

**⚠ Confidence flag M4:**
- `meal_recommendation_id` is FK to a synthesized type that gets defined in the synthesized batch — circular dependency-ish; needs resolution
- `household_eaters` only captures household members; doesn't accommodate guests / non-household eaters per [user-decision-framework.md "recipes may target household members or guests"](user-decision-framework.md). Schema may need a richer eater representation.
- `cooked` + `skipped` as separate booleans might be better as a state-machine field per F1 (asynchrony / temporal state model: scheduled → cooking → cooked → skipped lifecycle)
- Reorient_event is captured but **what changed** isn't — no field for the new constraint set the reorient applied. May need reorient_constraint_snapshot field.

Revisit during S3 F1 + after synthesized batch lands.

#### Molecule 5 — `document_upload` *(~85% confident)*

```
required:
  primary_document_event_id TEXT  -- FK to document_upload_event atom (the upload event itself)
  upload_purpose        TEXT      -- 'clinical_lab_results' | 'doctor_note' | 'recipe_to_ingest' | 'nutrition_reference' | 'other'
  extraction_status     TEXT      -- 'pending' | 'in_progress' | 'completed' | 'failed' | 'partial'
optional:
  total_claims_extracted INTEGER  -- count of corpus_extracted_claim atoms produced
  extraction_completed_at TEXT    -- ISO 8601 UTC
  user_review_required  BOOLEAN   -- true if extraction surfaced low-confidence claims needing user review
```

#### Molecule 6 — `grocery_order` *(~85% confident)*

```
required:
  retailer              TEXT      -- 'instacart_safeway' | 'kroger' | 'amazon_fresh' | 'manual_list_export' | etc.
  ordered_at            TEXT      -- ISO 8601 UTC
  delivery_window_start TEXT      -- ISO 8601 UTC
  delivery_window_end   TEXT      -- ISO 8601 UTC
  fulfillment_status    TEXT      -- 'placed' | 'shopping' | 'in_transit' | 'delivered' | 'cancelled' | 'failed'
  cart_construction_method TEXT   -- 'recipe_link_handoff' | 'list_export_only' | 'manual' per D3 Q3.3
optional:
  retailer_order_id     TEXT      -- the retailer's own order ID for reference
  scheduled_trip_id     TEXT      -- per D3 Q3.1 user-controlled cadence; null for ad-hoc orders
  trip_part_of_split    INTEGER   -- 1 of N for multi-cart split per D3 Q3.1; null if single-cart
  total_items_ordered   INTEGER
  delivery_confirmed_at TEXT      -- ISO 8601 UTC
```

#### Molecule 7 — `recipe_document` *(⚠ ~65% confident — flagged for field-set revisit)*

```
required:
  recipe_id             TEXT      -- canonical recipe ID; matches corpus markdown filename
  attribution_record_id TEXT      -- FK to recipe_attribution_record atom
  canonical_format      TEXT      -- 'cooklang' per D4 Q4.2
  cuisine_tradition_tags JSON_ARRAY -- per D4 sweep #14 integration: ['western_shared_compound'] | ['japanese_umami_synergy'] | ['indian_masala_with_tadka'] | etc.
  modality_availability JSON_ARRAY -- ['video' | 'structured_text' | 'cookbook_prose' | 'illustrated']; per C4 Q4.1
optional:
  ingredient_resolution_summary JSON  -- per D4 Q4.3: {fully_resolved: N, partial: N, unresolved: N}
  novelty_skill_count   INTEGER   -- per Tension #7 honest disclosure metadata
  failure_cost_tags     JSON_ARRAY -- ['deep_frying' | 'lamination' | 'fermentation' | etc.]
  estimated_active_time_min INTEGER
  estimated_total_time_min  INTEGER
```

**⚠ Confidence flag M7:**
- `cuisine_tradition_tags` and `modality_availability` are duplicated between substrate molecule and corpus markdown frontmatter (S9). Need to decide which is source-of-truth.
- `novelty_skill_count` and `failure_cost_tags` are user-context-conditional per Tension #7 honest disclosure — they only have meaning relative to a user's mastered-skills set. Storing them on the recipe molecule means precomputing for some default user profile; they likely belong in per-user `stretch_recipe_disclosure` synthesized entries (not on the recipe molecule itself).
- The boundary between `recipe_document` molecule (substrate side) and corpus markdown file (corpus side) needs clearer delineation — both represent the same recipe.

Revisit after S9 (corpus markdown frontmatter contract) lands + after synthesized batch lands.

#### Molecule 8 — `week_of_meal_events` *(⚠ ~60% confident — flagged for revisit)*

```
required:
  week_starting_date    TEXT      -- ISO 8601 date; Monday of the week
  meal_event_count      INTEGER   -- total meal events in this week
  cooked_count          INTEGER   -- meal events with cook_confirmation present
optional:
  weekly_pattern_summary JSON     -- aggregate signals: avg cooking_experience ratings, common feel-responses, etc.
  household_meal_count  INTEGER   -- meal events shared by 2+ household eaters
  individual_meal_count INTEGER   -- meal events for single household member
```

**⚠ Confidence flag M8:** Same fundamental question as M3 — is this a stored composition or a query view? Argument for storing: weekly-pattern-summary is meaningful aggregate metadata + horizon-broadening pacing might query frequently. Argument against: reducible to a query over meal_event molecules grouped by week. F1 (asynchrony / temporal state model) covers adjacent territory.

### Lower-confidence flag summary

Four molecules flagged for explicit revisit:
- **M3** `wearable_daily_aggregate` — molecule vs. query view
- **M4** `meal_event` — meal_recommendation_id circular dep, household_eaters guest gap, cooked/skipped vs. state machine, reorient_constraint_snapshot missing
- **M7** `recipe_document` — substrate-vs-corpus duplication, user-context-conditional fields wrong layer, substrate/corpus boundary
- **M8** `week_of_meal_events` — molecule vs. query view

Schema-design phase tracks all four for revisit during S3 F1 (asynchrony / temporal state model) + after S9 (corpus markdown frontmatter contract) + after synthesized batch.

### Sources

User direction (2026-05-03) on molecule payload schemas batch with hybrid-A-and-C pattern: land all 8 with confidence flags rather than defer.

---

### S2 — Synthesized payload schemas (Batch 3: 16 synthesized types)

> Resolved 2026-05-03 with per-type confidence breakdown + F-flag reminders. Closes S2.

Per-type payload schemas for all 16 synthesized types from B4 + the C4 refinement (`stretch_readiness_signal` as context-conditional, not scalar) + the C5 refinement (meal-feedback split surfaced through `meal_recommendation` state machine). These are mutable, LLM-managed entries carrying derived inferences.

#### Synthesized 1 — `nutrient_intake_estimate`

```
required:
  estimate_period_start TEXT      -- ISO 8601 UTC
  estimate_period_end   TEXT      -- ISO 8601 UTC
  nutrient_canonical_id TEXT      -- FK to authority record
  estimated_value       REAL
  unit                  TEXT      -- 'g' | 'mg' | 'mcg' | 'kcal' | etc.
  source_atom_count     INTEGER
  estimate_method       TEXT      -- 'meal_event_aggregation' | 'sparse_recall' | 'wearable_proxy' | etc.
optional:
  uncertainty_range_low  REAL
  uncertainty_range_high REAL
  data_completeness_note TEXT     -- per C3 Q3.3 partial-intake-as-default; honest framing of gaps
```

#### Synthesized 2 — `dietary_constraint`

```
required:
  constraint_type       TEXT      -- 'allergen' | 'intolerance' | 'medical_condition_required' | 'religious_observance' | 'preference' | 'life_stage_requirement' | etc.
  constraint_priority   INTEGER   -- 1-6 per Tension #5 conflict prioritization order
  constraint_text       TEXT      -- "no peanuts" | "lower-glycemic dinners" | "halal" | etc.
  derived_from_disclosures JSON_ARRAY  -- atom IDs of clinical_disclosure / preference_statement that grounded this
optional:
  constraint_strength   TEXT      -- 'absolute' | 'strong' | 'moderate' | 'mild'
  active_from_date      TEXT      -- ISO 8601 date; when constraint became active (e.g., pregnancy onset)
  active_until_date     TEXT      -- ISO 8601 date; when constraint expires (e.g., lactation end)
```

#### Synthesized 3 — `abstracted_constraint`

```
required:
  household_id          TEXT      -- per Tension #5 abstracted-constraint-layer at household level
  source_member_id      TEXT      -- which household member the constraint originates from (back-reference)
  abstracted_text       TEXT      -- cooking-terms expression: "prefers lower-glycemic dinners" | "avoids peanuts" | etc.
  sharing_level         TEXT      -- 'strict_per_user' | 'constraint_only_automatic' | 'mutual_consent_explicit' per Tension #5
optional:
  back_reference_visible_to JSON_ARRAY  -- member IDs allowed to see the back-reference; per mutual-consent sharing
```

#### Synthesized 4 — `meal_plan`

```
required:
  plan_period_start     TEXT      -- ISO 8601 date
  plan_period_end       TEXT      -- ISO 8601 date
  plan_subject_id       TEXT      -- subject_id for whom (user / household)
  meal_recommendation_ids JSON_ARRAY  -- ordered list of synthesized meal_recommendation IDs
  plan_status           TEXT      -- 'draft' | 'active' | 'archived' | 'superseded'
optional:
  generation_method     TEXT      -- 'weekly_batch_initial' | 'reorient_regeneration' per C5 Q5.5 | 'horizon_broadening_pass' per intake-pattern.md
  cadence_choice        TEXT      -- 'weekly' | 'twice_weekly' | 'ad_hoc' per D3 Q3.1 user-controlled cadence
```

#### Synthesized 5 — `meal_recommendation`

```
required:
  recipe_id             TEXT      -- FK to recipe in corpus
  recipe_version        TEXT
  meal_slot             TEXT      -- 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'special_occasion'
  planned_for_date      TEXT      -- ISO 8601 date
  recommendation_state  TEXT      -- 'proposed' | 'accepted' | 'scheduled' | 'cooking' | 'cooked' | 'skipped' (per F1 state machine; replaces meal_event boolean cooked + skipped fields per M4 flag)
  household_eater_targets JSON   -- structured per Rule 10 user-decision-framework; supports household members AND guests AND for-whom-other-than-requester (addresses M4 flag household_eaters gap)
  recommendation_rationale TEXT   -- markdown; the "why this recipe" explanation per Rule 8
  rationale_format      TEXT      -- always 'markdown'
optional:
  reorient_constraint_snapshot JSON  -- if recommendation came from a reorient event per C5 Q5.5; captures the constraint set the reorient applied (addresses M4 flag)
  novelty_skill_count   INTEGER   -- per-user-context value of novelty per Tension #7 (NOT on recipe molecule per M7 flag)
  failure_cost_tags     JSON_ARRAY  -- per-user-context failure cost surfacing per Tension #7
```

#### Synthesized 6 — `recipe_match`

```
required:
  recipe_id             TEXT      -- FK to recipe in corpus
  match_query_context   TEXT      -- what query produced this match (filter-then-rank per B1 Q1.2)
  match_score           REAL      -- 0.0-1.0
  ranking_position      INTEGER   -- where this recipe ranked among candidates
  filtered_constraints  JSON      -- which constraints this recipe satisfied (allergens, conditions, equipment, time-budget)
optional:
  ranked_against_count  INTEGER   -- candidate set size that this recipe was ranked within
  semantic_similarity_score REAL  -- vector-search component of the score
  fts_relevance_score   REAL      -- full-text component of the score
```

#### Synthesized 7 — `educational_recommendation`

```
required:
  concept_id            TEXT      -- canonical concept identifier from educational corpus
  delivery_surface      TEXT      -- 'per_meal_microlearning' | 'opt_in_pull' | 'in_context_tooltip' per Tension #3 Option D
  trigger_context       TEXT      -- what prompted this recommendation (recipe choice, semantic feedback pattern, time-since-last-delivery, etc.)
  delivery_state        TEXT      -- 'queued' | 'delivered' | 'engaged' | 'dismissed' | 'comprehended_signal_observed'
optional:
  spaced_repetition_position INTEGER  -- which re-surface cycle this is (1st, 2nd, 3rd) per knowledge-model.md
  prior_engagement_signals JSON   -- engagement history with this concept; informs scheduling
```

#### Synthesized 8 — `inference` *(generic catch-all per F5)*

```
required:
  inference_subject     TEXT      -- what the inference is about
  inference_text        TEXT      -- markdown; the inference itself with reasoning chain
  inference_text_format TEXT      -- always 'markdown'
  reasoning_chain       JSON      -- structured fields per B2 Q2.2: inputs, inference_type, assumptions, excluded, confidence_factors, causal_explanation
  verification_status   TEXT      -- 'verified' | 'verification_failed_rule' | 'verification_failed_coherence' | 'verification_pending'
optional:
  user_facing_phrasing  TEXT      -- markdown; user-friendly version of inference_text if it differs
```

⚠ **F5 reminder:** generic catch-all exists per the explicit B4 F5 flag — load-bearing for cases not yet enumerated as specific synthesized types, with a smell flag to monitor + remove once enumeration matures.

#### Synthesized 9 — `inferred_pattern`

```
required:
  pattern_type          TEXT      -- 'food_response_correlation' | 'cooking_frequency_trend' | 'cuisine_preference_drift' | 'wearable_signal_pattern' | etc.
  pattern_text          TEXT      -- markdown; the pattern description + evidence
  pattern_text_format   TEXT      -- always 'markdown'
  observation_period_start TEXT   -- ISO 8601 UTC
  observation_period_end   TEXT   -- ISO 8601 UTC
  supporting_atom_count INTEGER   -- how many atoms support the pattern
optional:
  statistical_strength  TEXT      -- 'preliminary_observation' | 'consistent_pattern' | 'strong_correlation' (honest framing; not statistical-significance overclaim)
  consult_professional_recommended BOOLEAN  -- true if pattern warrants Rule 1 callout
```

#### Synthesized 10 — `pairing_rationale` *(per sweep #14 integration)*

```
required:
  pairing_subject       TEXT      -- "garlic + thyme + roasted chicken" | "umami synergy: kombu + bonito" | etc.
  pairing_tradition     TEXT      -- 'western_shared_compound' | 'japanese_umami_synergy' | etc.
  rationale_text        TEXT      -- markdown; why these go together
  rationale_text_format TEXT      -- always 'markdown'
  scientific_basis_present BOOLEAN -- true if backed by peer-reviewed mechanistic literature
optional:
  scientific_citations  JSON_ARRAY  -- references to peer-reviewed sources where available
  evidence_note         TEXT      -- 'tier_1_2_mechanistic' | 'practitioner_tradition_only' | 'contested_per_audit_as_education' per Q14 + audit-as-education
```

#### Synthesized 11 — `substitution_proposal`

```
required:
  original_ingredient_id TEXT     -- FK to authority record
  proposed_alternatives JSON_ARRAY -- ordered list of {ingredient_id, role_satisfied, rationale, constraint_compliant_against: []}
  pairing_role_being_filled TEXT  -- per sweep #14 pairing-role taxonomy: 'acid' | 'umami' | 'aromatic' | 'pungent' | 'textural' | 'fat_vehicle' | etc.
  combined_gate_status  TEXT      -- per D3 Q3.2: 'all_alternatives_pre_approved' | 'pre_approved_subset_pending_real_time' | 'no_pre_approved_real_time_required'
optional:
  user_pre_approved_rules_applied JSON  -- which user rules from D3 Q3.2 informed the proposal
  active_constraints_checked JSON_ARRAY  -- which constraints (allergens, conditions) the proposal cleared
```

#### Synthesized 12 — `stretch_recipe_disclosure` *(per Tension #7)*

```
required:
  recipe_id             TEXT      -- FK to recipe being disclosed
  user_subject_id       TEXT      -- per-user context (per Tension #7 honest disclosure is per-user)
  novelty_skill_count   INTEGER   -- new-skill count relative to THIS user's mastered set
  novelty_skill_names   JSON_ARRAY  -- specific new skills the recipe introduces for this user
  failure_cost_tags     JSON_ARRAY  -- high-failure-cost techniques in this recipe
  disclosure_text       TEXT      -- markdown; the actual disclosure shown to user
  disclosure_text_format TEXT     -- always 'markdown'
optional:
  alternative_lower_stretch_options JSON_ARRAY  -- recipe IDs of less-stretch alternatives offered alongside
```

#### Synthesized 13 — `audit_as_education_content` *(per evidence-tiers.md)*

```
required:
  topic_subject         TEXT      -- "microbiome-targeted personalization" | "aroma-compound-overlap pairing hypothesis" | etc.
  evidence_tier_assessment INTEGER -- 1-4
  audit_summary_text    TEXT      -- markdown; what's claimed + what evidence shows + why system does/doesn't drive behavior
  audit_summary_text_format TEXT  -- always 'markdown'
  contested_status      TEXT      -- 'consensus' | 'mainstream_with_dissent' | 'contested' | 'fringe' per audit-as-education pattern
optional:
  citations             JSON_ARRAY  -- supporting + opposing references
  consult_professional_recommended BOOLEAN  -- true per Rule 1 if the topic is clinical-adjacent
```

#### Synthesized 14 — `dietary_pattern_assessment`

```
required:
  pattern_instrument    TEXT      -- 'MEDAS' | 'HEI' | 'AHEI' | 'DASH' | etc.
  pattern_version       TEXT      -- per E1 + B3 versioning
  adherence_score       REAL
  adherence_interpretation TEXT   -- per-instrument tiers
  observation_period_start TEXT   -- ISO 8601 UTC
  observation_period_end   TEXT   -- ISO 8601 UTC
  source_atom_count     INTEGER   -- atoms feeding the assessment
optional:
  per_component_scores  JSON      -- sub-scores within the instrument (e.g., per-food-group HEI components)
  data_completeness_note TEXT     -- partial-intake honesty per C3 Q3.3
```

⚠ **F6 reminder:** B4 F6 flagged whether `dietary_pattern_assessment` should merge with `screener_result`. Currently separate; F6 still open for schema-design final pass.

#### Synthesized 15 — `stretch_readiness_signal` *(per C4 refinement)*

```
required:
  user_subject_id       TEXT
  context_dimensions    JSON      -- per C4 refinement: NOT a scalar score; multi-dimensional context-conditional
                                  -- structure: {
                                  --   demonstrated_skill_level: { skill_name: confidence_score, ... },
                                  --   picked_in_context: { context_key: { skill_name: pick_frequency, ... } },
                                  --     -- context_key examples: 'weekday_evening' | 'weekend_morning' | 'high_stress_period' | 'normal'
                                  --   demonstrated_vs_picked_divergence: { skill_name: divergence_score, ... }
                                  -- }
  observation_period_start TEXT   -- ISO 8601 UTC
  observation_period_end   TEXT   -- ISO 8601 UTC
optional:
  prior_signal_id       TEXT      -- FK to prior stretch_readiness_signal that this supersedes
  pattern_recognition_method TEXT -- 'rule_based_aggregation' | 'llm_pattern_inference' | 'hybrid'
```

#### Synthesized 16 — `audit_log_entry`

```
required:
  operation_type        TEXT      -- 'phi_crossing' | 'data_write' | 'data_read' | 'consent_change' | 'license_change' | 'publication_event' | 'inference_computed' | etc.
  actor                 TEXT      -- 'user' | 'system' | 'agent_id' | etc.
  operation_result      TEXT      -- 'success' | 'failure' | 'partial' | 'declined'
  log_subject_summary   TEXT      -- short summary; full detail in payload
optional:
  request_id            TEXT      -- correlation to other audit entries from the same operation
  declined_reason       TEXT      -- if declined, why
  user_visible_in_audit_view BOOLEAN -- true for entries surfaced in C5 Q5.4 dedicated audit view
```

⚠ **F6 reminder:** B4 F6 also flagged `audit_as_education_content` ↔ `educational_recommendation` merge. Currently separate; F6 still open.

### Per-type confidence breakdown

**Higher confidence (~80-85%):**
- `dietary_constraint`, `abstracted_constraint`, `nutrient_intake_estimate` — clear referents, clean field sets
- `pairing_rationale`, `substitution_proposal`, `stretch_recipe_disclosure` — directly map to sweep #14 / Tension #7 + D3 design choices
- `audit_log_entry` — operationally-driven, well-bounded

**Moderate confidence (~65-75%):**
- `meal_recommendation` — addresses M4 flags (state machine for cooked/skipped, household_eater_targets handles guests, reorient_constraint_snapshot captures what changed); but introduces new design surface that's untested
- `meal_plan` — depends on `meal_recommendation` shape stabilizing
- `recipe_match` — clear shape but actual scoring fields will refine in implementation
- `educational_recommendation` — depends on educational corpus structure (S9-related)
- `stretch_readiness_signal` — context_dimensions JSON shape captures C4 refinement intent but is a meaningful design choice

**Lower confidence (~50-65%):**
- `inference` — F5 reminder; generic catch-all is intentionally smelly
- `inferred_pattern` — distinction from `inference` is subtle; might collapse
- `audit_as_education_content` vs. `educational_recommendation` — F6 reminder; might merge
- `dietary_pattern_assessment` vs. `screener_result` — F6 reminder; might merge

### S2 closure summary

S2 complete: 18 atom + 8 molecule + 16 synthesized = **42 type schemas** specified.

Active flags at S2 close, all tracked for S3 + later resolution:

- **Atom batch:** none open (closed at high confidence)
- **Molecule batch:** M3, M4, M7, M8 (4 confidence flags)
- **Synthesized batch:** F5, F6 reminders (carried forward from B4); 4 lower-confidence types flagged for S3 + downstream refinement

### Sources

User direction (2026-05-03) on synthesized payload schemas batch closing S2.

---

## S3 — B4 lower-confidence flags F1–F8 resolution

> Resolved 2026-05-04 — all 8 flags closed with concrete schema impacts.

Per B4 architecture-level decision, eight flags were explicitly deferred to schema-design phase. With S1 + S2 schemas now concrete, these resolve.

### F1 — Asynchrony / temporal state model

**Resolved partly by S2 already** (`meal_recommendation.recommendation_state` state machine replaced M4 separate `cooked` + `skipped` booleans). Remaining items closed:

- **F1.a state set for `meal_recommendation.recommendation_state`:** add `'reorient_pending'` between `'proposed'` and `'scheduled'` for the C5 Q5.5 reorient affordance flow. Final set: `'proposed' | 'accepted' | 'scheduled' | 'reorient_pending' | 'cooking' | 'cooked' | 'skipped'`.
- **F1.b state machines on other types:** add `'declined_for_now'` to `educational_recommendation.delivery_state` (distinct from `'dismissed'` — declined-for-now means user might engage later; dismissed means hard-no). All other existing state-machine fields (`meal_plan.plan_status`, `grocery_order.fulfillment_status`, `intake_session.session_closed_at` as nullable timestamp) stand as proposed.
- **F1.c M3 + M8 resolution:** **`wearable_daily_aggregate` and `week_of_meal_events` are demoted from molecules to query views**. Same-day wearable atoms and same-week meal_event molecules don't have substantive co-belonging like `lab_panel` atoms do (one blood draw); metadata they would carry (`data_completeness`, `weekly_pattern_summary`) is computable at query time; storing them creates state-sync issues if backing atoms change. **Molecule count drops from 8 to 6.**

### F2 — Household vs. user-level subject boundary

**`member_subset` represented as inline JSON array of user IDs** when `subject_type = 'member_subset'`. No separate subset entity table — at household scale (2–4 members), separate table is overhead without payoff. Inline JSON keeps subject reference co-located with the data.

Final base column semantics:
- `subject_type = 'user'` → `subject_id` is a user ID
- `subject_type = 'household'` → `subject_id` is a household ID
- `subject_type = 'member_subset'` → `subject_id` is JSON array of user IDs (e.g., `'["usr-...", "usr-..."]'`)

### F3 — Corpus vs. substrate boundary for shareable content

**No 4th storage layer.** `pairing_rationale` (and similar cross-user-applicable synthesized content) **stays in substrate as a synthesized type with `subject_id NULL`** when the rationale is genuinely cross-user-applicable. Per-user variants populate `subject_id`.

This generalizes: any synthesized type can have `subject_id NULL` to indicate "applicable to any user." The existing schema accommodates this without new layers.

### F4 — User-correction handling

**Resolved by S1's `retraction_reason` field.** When a user corrects a prior inference ("no, that wasn't lactose intolerance — it was a one-off"):

1. New `clinical_disclosure` atom written that supersedes the prior
2. Prior atom's `valid_until` populated + `retraction_reason = 'retracted_user_correction'`
3. `Supersedes` relationship links new atom to prior

No new atom type needed. Confidence ~80%.

### F5 — Generic `inference` catch-all type

**Keep as catch-all with the smell flag — ongoing-monitoring item, not a one-time resolution.** If during build half of all inferences cluster as `nutrient_inference` or `behavioral_inference` or `cuisine_inference`, promote those to specific types and shrink the catch-all. F5 stays open as a build-phase monitoring concern.

### F6 — Possible type merges

- **MERGE: `dietary_pattern_assessment` into `screener_result`** with `instrument_category ∈ {'dietary_pattern', 'clinical_screener'}` discriminator. Both have instrument/version/score/interpretation/per_item_responses; the differences (subject + scoring methodology) are slight and discriminator-friendly. **Synthesized count drops from 16 to 15.**
- **DON'T MERGE: `audit_as_education_content` and `educational_recommendation` stay separate.** They serve different roles — `educational_recommendation` is delivery-targeted (this concept should be delivered to this user, in this surface, at this time); `audit_as_education_content` is the actual content body with evidence-tier framing. An `educational_recommendation` can point to an `audit_as_education_content` via DerivedFrom or relationship.

### F7 — `provenance_chain` as relationship vs. computed view

**Computed view via recursive `DerivedFrom` traversal.** No new stored relationship type. Substrate already stores immediate-parent `DerivedFrom` per the LC pattern adopted in A4; recursive traversal yields the full chain. Confidence ~85%.

### F8 — Possibly-overengineered atoms reconsideration

Atoms stay folded:

- **`emotional_state_atom`** — folded into `meal_feedback_body_response` (mood_rating + freetext_response). ~80% confident.
- **`goal_atom`** — **add `'goal'` to `preference_statement.preference_type` enum** rather than splitting into a new atom type. ~75% confident.
- **`schedule_atom`** — folded into `meal_recommendation.planned_for_date` + `meal_slot`. Calendar concerns out of MVP scope. ~85% confident.

### Schema impact summary

After F1–F8 resolution:

- **Molecule count: 8 → 6** (M3 wearable_daily_aggregate + M8 week_of_meal_events demoted to query views)
- **Synthesized count: 16 → 15** (dietary_pattern_assessment merged into screener_result)
- **State machine additions:** `'reorient_pending'` (meal_recommendation), `'declined_for_now'` (educational_recommendation)
- **Enum additions:** `'goal'` (preference_statement.preference_type), `instrument_category ∈ {'dietary_pattern', 'clinical_screener'}` (screener_result)
- **Subject-id semantics:** `NULL` indicates cross-user-applicable synthesized content
- **Member-subset semantics:** inline JSON array of user IDs

### Active flags after S3

- **F5** stays open as build-phase monitoring item (catch-all-smell ongoing concern)
- **M4 + M7** still flagged for revisit during S9 (corpus markdown frontmatter contract)

S3 closed; M3, M8, F1, F2, F3, F4, F6, F7, F8 resolved.

### Sources

User direction (2026-05-04) on F1–F8 resolution batch.

---

## S4 — Typed relationships table + indexes

> Resolved 2026-05-04 across five sub-decisions Q4.1–Q4.5.

### Decision

**Single `relationships` table** with a `relationship_type` discriminator covering the 7 typed relationship types (DerivedFrom, Contradicts, Supersedes, Tension, EnrichedBy, MemberOf, RetractedBy); **bitemporal + provenance-bearing schema** that inherits the relevant subset of S1 base columns so the epistemic trail can answer "when was this relationship asserted, by whom, with what confidence, and was it ever retracted"; **MemberOf retained alongside atom's `composition_id` FK** (both representations: FK for O(1) parent lookup + relationship for uniform graph traversal); **per-type metadata schemas** declared in the canonical schema-of-schemas (per S2 Q2.5); **trust SQLite recursive CTE** for provenance-chain traversal at personal-use scale.

### Q4.1 — Single relationships table

One `relationships` table with `relationship_type` discriminator (vs. one table per type or hybrid).

- Uniform queries for "all relationships touching atom X"
- Single index strategy covers all 7 types
- Adding new relationship types = new discriminator value, not new table + migration
- Per-type validation handled at the schema-of-schemas layer (per S2 Q2.5)

### Q4.2 — Schema

```sql
CREATE TABLE relationships (
  id                      TEXT PRIMARY KEY,            -- rel-{uuidv7}
  source_id               TEXT NOT NULL,
  source_type             TEXT NOT NULL,               -- 'atom' | 'molecule' | 'synthesized'
  target_id               TEXT NOT NULL,
  target_type             TEXT NOT NULL,
  relationship_type       TEXT NOT NULL,
  provenance              TEXT NOT NULL,               -- JSON: how this relationship was established (LLM extraction, rule, user assertion)
  evidence_tier           INTEGER,                     -- relevant when LLM-detected (e.g., Tier 4 contradiction)
  system_confidence       REAL,                        -- 0.0-1.0
  valid_from              TEXT NOT NULL,               -- ISO 8601 UTC
  valid_until             TEXT,                        -- ISO 8601 UTC; NULL = currently valid
  recorded_at             TEXT NOT NULL,               -- ISO 8601 UTC
  retraction_reason       TEXT,                        -- NULL | 'superseded' | 'retracted_user_correction' | 'retracted_source_revision' | 'retracted_validation_failure' | 'retracted_consent_withdrawn'
  system_version          TEXT NOT NULL,
  component_version       TEXT NOT NULL,
  payload_schema_version  TEXT NOT NULL,
  publication_eligible    INTEGER NOT NULL DEFAULT 1,
  metadata                TEXT,                        -- JSON; per-type schema declared in schema-of-schemas
  CHECK (source_type IN ('atom','molecule','synthesized')),
  CHECK (target_type IN ('atom','molecule','synthesized')),
  CHECK (relationship_type IN ('DerivedFrom','Contradicts','Supersedes','Tension','EnrichedBy','MemberOf','RetractedBy')),
  CHECK (source_id != target_id)
);

CREATE UNIQUE INDEX idx_rel_unique  ON relationships(source_id, relationship_type, target_id, valid_from);
CREATE INDEX idx_rel_forward        ON relationships(source_id, relationship_type, target_id) WHERE valid_until IS NULL;
CREATE INDEX idx_rel_reverse        ON relationships(target_id, relationship_type, source_id) WHERE valid_until IS NULL;
CREATE INDEX idx_rel_typed          ON relationships(relationship_type, source_type) WHERE valid_until IS NULL;
```

Subset of S1 base columns inherited (intentional choices):
- **Inherited:** `provenance`, `evidence_tier`, `system_confidence`, `valid_from`, `valid_until`, `recorded_at`, `retraction_reason`, `system_version`, `component_version`, `payload_schema_version`, `publication_eligible`, `metadata` (analog of `payload`)
- **Skipped:** `user_facing_certainty` (relationships are infrastructure, not user-facing facts), `consent_record_id` + `phi_categories` (components carry PHI markers; relationships are structural), `source_identity` + `authority_resolution_status` (N/A — those describe atom-level subject identity)
- **Replaced:** `subject_id` / `subject_type` → `source_id`/`source_type` + `target_id`/`target_type` (relationships have two endpoints, not one subject)

Index strategy:
- **Forward + reverse partial indexes** with `WHERE valid_until IS NULL` keep the common "current relationships" query lean
- **Typed partial index** for type-filtered queries (e.g., "all current Contradicts relationships originating from atoms")
- **Unique index on `(source_id, relationship_type, target_id, valid_from)`** prevents duplicate active assertions while permitting historical re-assertions across bitemporal windows
- **`CHECK (source_id != target_id)`** sanity guard — none of the 7 relationship types has a meaningful self-referential case

### Q4.3 — `MemberOf` AND atom's `composition_id` FK both retained

Atoms in a molecule are referenced two ways:

- **Atom's `composition_id` FK** to its parent molecule — O(1) lookup of "what molecule does this atom belong to" without joining the relationships table
- **`MemberOf` row in `relationships` table** — uniform graph traversal (all relationships are queryable the same way) + supports the case of an atom being referenced by multiple molecules over time

Slight denormalization cost; consistent with the LC pattern adopted in A4.

### Q4.4 — Per-type metadata schemas

Declared in the canonical schema-of-schemas (per S2 Q2.5 hybrid). Per-relationship-type metadata:

- **DerivedFrom** — `derivation_depth` (int), `derivation_method` (enum: `extraction` | `inference` | `aggregation` | `LLM_synthesis`)
- **Contradicts** — `contradiction_dimension` (enum: `factual` | `methodological` | `scope` | `tier`), `severity` (enum: `minor` | `moderate` | `major`)
- **Supersedes** — `supersession_reason` (enum: `newer_evidence` | `retraction` | `scope_correction` | `source_update`)
- **Tension** — `tension_dimension` (enum: `evidence_conflict` | `guideline_conflict` | `source_disagreement`), `resolution_strategy` (enum: `surface_to_user` | `weighted_blend` | `tier_priority` | `unresolved`)
- **EnrichedBy** — `enrichment_type` (enum: `causal_explanation` | `mechanism` | `example` | `contraindication`)
- **MemberOf** — typically empty `{}`; reserved for future use (e.g., `member_role` if ordered membership becomes relevant)
- **RetractedBy** — typically empty `{}`; reason carried on the target's `retraction_reason` column instead

The "who/what extracted this relationship" concern is handled by the first-class `provenance` column, not metadata.

### Q4.5 — Recursive provenance-chain traversal

**SQLite recursive CTE.** At personal-use scale (chain depth ≤10), recursive CTEs are well-optimized; query latency stays below perception threshold. Materialized views and cached `provenance_chain` columns introduce invalidation complexity that doesn't pay off until orders of magnitude more relationships.

Per F7 (already resolved in S3): `provenance_chain` is computed-on-demand via recursive `DerivedFrom` traversal, not a stored relationship type.

### Out of scope at S4

- Embedding tables — S5
- Authority table — S6
- Verification rule-set (referenced via `provenance` JSON shape) — S7
- Operational DB tables (audit log + epistemic-trail event log) — S8
- Foreign keys + referential integrity — S11

### Sources

User direction throughout the Q4.1 → Q4.5 dialogue (2026-05-04); user prompted Q4.2 rethink which surfaced 9 additions (bitemporal columns, first-class provenance, evidence_tier + system_confidence, retraction_reason, version columns, publication_eligible flag, sanity CHECK, partial-index optimization, bitemporal-aware unique index).

---

## S5 — Embedding tables

> Resolved 2026-05-04 across five sub-decisions Q5.1–Q5.5 plus Q5.2.1 (PHI defense-in-depth).

### Decision

**Single embeddings table per provider** (`embeddings_voyage` + `embeddings_local`) with `content_role` discriminator covering all embeddable content types; **defense-in-depth PHI marker** at the schema layer (`source_phi_categories` column + CHECK constraint on `embeddings_voyage` rejecting any non-empty PHI categories); **status-column staleness representation** (not bitemporal) with partial unique index per current-row + `state_changed_at` for cleanup; **loose polymorphic reference** (subject_id + subject_type, application-layer resolver) consistent with S4; **`vec0` virtual table per (provider, dimension) combination** holding vectors with sqlite-vec ANN index, joined to main metadata table via `id`.

### Q5.1 — Single embeddings table per provider

One `embeddings_voyage` + one `embeddings_local` table, each carrying a `content_role` discriminator (`'recipe_description' | 'recipe_ingredient_list' | 'corpus_chunk' | 'screener_item' | 'authority_canonical_name' | 'atom_payload' | ...`).

- Mirrors S1 single-table-per-layer + JSON payload pattern + S4 single-relationships-table pattern
- Adding new content-types = new discriminator value, not new table + migration
- sqlite-vec's index efficiency is per-column not per-table at our scale; partitioning into many small tables doesn't pay off until orders of magnitude more vectors
- Single `vec0` virtual table per (provider, dimension) for ANN search; partitioning by content-type would force per-content-type ANN indexes that complicate cross-content retrieval
- Per-content-role partial indexes addable later as optimization without schema churn

### Q5.2 — Embeddings table schema

```sql
CREATE TABLE embeddings_voyage (
  id                       TEXT PRIMARY KEY,            -- emb-{uuidv7}
  subject_id               TEXT NOT NULL,               -- ID of source entity (loose polymorphic ref per Q5.5)
  subject_type             TEXT NOT NULL,               -- 'atom' | 'molecule' | 'synthesized' | 'recipe' | 'corpus_chunk' | 'authority_record'
  content_role             TEXT NOT NULL,               -- discriminator; validated via schema-of-schemas (per S2 Q2.5), not CHECK
  source_text_hash         TEXT NOT NULL,               -- SHA-256 of input text; enables stale detection per Q5.4
  source_phi_categories    TEXT NOT NULL,               -- JSON array; defense-in-depth per Q5.2.1
  embedding_model          TEXT NOT NULL,               -- 'voyage-3-large' | 'voyage-2' | etc.
  embedding_dimension      INTEGER NOT NULL,            -- 1024 / 1536 / etc.; selects the vec0 table to join
  status                   TEXT NOT NULL DEFAULT 'current',  -- per Q5.4 staleness lifecycle
  state_changed_at         TEXT NOT NULL,               -- ISO 8601 UTC; when status last transitioned
  recorded_at              TEXT NOT NULL,               -- ISO 8601 UTC
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,               -- embedding pipeline version (chunking, normalization)
  publication_eligible     INTEGER NOT NULL DEFAULT 1,
  CHECK (subject_type IN ('atom','molecule','synthesized','recipe','corpus_chunk','authority_record')),
  CHECK (status IN ('current','stale_pending_reembed','retired')),
  CHECK (source_phi_categories = '[]')                  -- defense-in-depth: voyage table accepts NO PHI content
);

-- Partial unique index per Q5.4: exactly one current embedding per subject+role+model
CREATE UNIQUE INDEX idx_emb_voy_subject_current
  ON embeddings_voyage(subject_id, content_role, embedding_model)
  WHERE status = 'current';

CREATE INDEX idx_emb_voy_role           ON embeddings_voyage(content_role, subject_type);
CREATE INDEX idx_emb_voy_hash           ON embeddings_voyage(source_text_hash);
CREATE INDEX idx_emb_voy_status         ON embeddings_voyage(status, state_changed_at);

-- vec0 virtual table per (provider, dimension); main table joins via id
CREATE VIRTUAL TABLE vec_voyage_1024 USING vec0(
  embedding_id TEXT PRIMARY KEY,
  embedding FLOAT[1024]
);
```

`embeddings_local` table = identical structure **except** the PHI CHECK constraint is removed (local embedder accepts both PHI and non-PHI content):

```sql
-- embeddings_local schema differs only in:
-- 1. No CHECK on source_phi_categories (local accepts any PHI category set)
-- 2. Separate vec_local_<dim> virtual tables per local model dimension
```

Schema rationale (the *why* per non-obvious column):

- **`source_text_hash`** — stale-detection trigger per Q5.4(i); also fast "is this text already embedded somewhere?" lookup via `idx_emb_voy_hash`
- **`source_phi_categories`** — defense-in-depth per Q5.2.1; copied from source atom at embedding time; CHECK constraint on `embeddings_voyage` is the schema-level fail-closed guard against PHI leak through a routing bug
- **`embedding_model` + `embedding_dimension`** — supports model upgrades; old model rows stay queryable until re-embedded; dimension selects the right `vec0` table to join
- **`status` + `state_changed_at`** — Q5.4 staleness lifecycle; status column over bitemporal because we don't need point-in-time historical embedding queries
- **`recorded_at` + version columns** — reproducibility for publication targets (per E1)
- **`publication_eligible`** — embeddings publication-relevance is non-trivial: Voyage embeddings aren't reproducible without API access; local model embeddings are. Publication-prep queries this directly.
- **No `payload_schema_version`** — embedding shape fully determined by `embedding_model` + `embedding_dimension`; the model identifier *is* the schema version
- **No `payload`** — embeddings table is pure retrieval infrastructure; actual content lives in source tables (per B1 "embed-as-index, deliver source")
- **No `provenance` / `evidence_tier` / `system_confidence` / `user_facing_certainty`** — embeddings are derived index, not facts; provenance lives on source content
- **Vectors only in `vec0`, not duplicated in main table** — saves ~50% on embedding storage; the join is cheap; main table stays a pure metadata index
- **`vec0` per (provider, dimension)** — Voyage has voyage-3-large (1024) + voyage-3-lite (512); local candidates have varying dims (mxbai 1024 / BGE-M3 1024 / nomic 768). One `vec0` per dimension within each provider

### Q5.2.1 — PHI defense-in-depth (schema-level enforcement)

Per [phi-handling.md](phi-handling.md) double-layer enforcement: schema rejects PHI content from being written to `embeddings_voyage` (not just trust application-layer routing).

Implementation: `source_phi_categories TEXT NOT NULL` column on both tables (copied from source atom at embedding time) + `CHECK (source_phi_categories = '[]')` on `embeddings_voyage` only. `embeddings_local` has no constraint (accepts both PHI and non-PHI).

Per the C1 double-layer-enforcement pattern + phi-handling.md "fails closed" principle. Cost: one extra column + one CHECK; benefit: hard schema-level guard against PHI leak through a routing bug.

### Q5.3 — Local embedding model: single table with discriminator

**Single `embeddings_local` table** with `embedding_model` discriminator (vs. one table per local model). Same reasoning as Q5.1 — discriminator pattern beats per-model tables for our scale.

During a model migration (e.g., mxbai → BGE-M3), both old and new model rows coexist in the same table; partial unique index per Q5.4 (`WHERE status = 'current'`) prevents duplicates while permitting transition. If old + new model share dimension, they share one `vec_local_<dim>` virtual table; if dimensions differ, separate `vec_local_768` + `vec_local_1024` tables already accommodated by per-(provider,dimension) `vec0` pattern.

**Build-time validation flag (ζ):** sqlite-vec's auxiliary metadata column support potentially enables collapsing main table + `vec0` into a single virtual table holding both metadata + vectors. Build-time validation needed: confirm CHECK constraints + partial indexes + S11 FK semantics work on virtual tables. If yes, application surface unaffected by physical-layout swap (resolver per Q5.5 doesn't care). Tracked in roadmap.

### Q5.4 — Re-embedding triggers + status-column staleness

Three triggers for re-embedding:

- (i) **Source-text change** — `source_text_hash` mismatch
- (ii) **Model upgrade** — `embedding_model` version change (Voyage v2 → v3, or local model swap)
- (iii) **Component-version change** — pre-embedding text-prep pipeline change (chunking, normalization), detected via `component_version` mismatch

Staleness representation: **status column** (not bitemporal). Status values: `'current' | 'stale_pending_reembed' | 'retired'`. Operational semantics:

- Re-embed pipeline polls `WHERE status = 'stale_pending_reembed'`
- Retrieval queries filter `WHERE status IN ('current','stale_pending_reembed')` — stale rows stay serveable until new ones land
- Cleanup job archives `WHERE status = 'retired' AND state_changed_at < threshold`
- Atomic swap: write new row with `status='current'`; in same transaction, update old row from `'current'` to `'retired'`

Bitemporal pattern rejected because we don't need point-in-time historical embedding queries ("what did this text embed to in March?"); we need "current embedding for this subject."

**Partial unique index** (replaces Q5.2's full unique index):

```sql
CREATE UNIQUE INDEX idx_emb_voy_subject_current
  ON embeddings_voyage(subject_id, content_role, embedding_model)
  WHERE status = 'current';
```

The invariant is "exactly one current embedding per subject+role+model" — partial index expresses it precisely without constraining retired rows.

### Q5.5 — Loose polymorphic reference + application-layer resolver

`subject_id` + `subject_type` is a loose polymorphic reference (no SQL FK). Application-layer resolver maps `subject_type` → source table and queries.

- Mirrors S4 relationships table pattern — consistent across substrate
- SQLite native polymorphic FK gymnastics (separate nullable FK columns per subject_type, conditional CHECKs) cost more in schema noise than they buy in safety
- Application-layer resolver is the natural place to enforce "deliver source" rule (per B1) — it's where retrieval orchestration lives
- S11 (foreign keys + referential integrity) will revisit; if S11 lands a polymorphic-FK pattern (subject_registry lookup table), embeddings adopt without schema break

**Orphan-prevention (operational, S8 territory):**

- (1) **Application-layer cascade-on-retire** — when source atom/molecule/synthesized retires, application layer marks corresponding embedding rows `status='retired'` via Q5.4 lifecycle
- (2) **Periodic orphan-sweep job** — background job finds embedding rows where `subject_id` no longer resolves and retires them; catches race conditions + crashed mid-delete operations

Both: defense-in-depth. Tracked for S8.

### Schema impact summary

After S5:

- **2 main tables** (`embeddings_voyage` + `embeddings_local`) — identical schema except `source_phi_categories` CHECK constraint
- **Variable `vec0` virtual tables per (provider, dimension)** — currently `vec_voyage_1024` + `vec_local_<dim>` based on candidate model selection
- **Status-column lifecycle** with partial unique index keying off `status='current'`
- **Defense-in-depth PHI marker** at schema layer
- **Application-layer resolver** for polymorphic reference (consistent with S4)

### Out of scope at S5 (deferred)

- Local model final choice (`mxbai-embed-large` / `BGE-M3` / `nomic-embed-text`) — build-time decision per roadmap
- Voyage model selection (`voyage-3-large` vs. `voyage-3-lite`) — build-time decision; depends on dimension/quality/cost tradeoff at adoption
- Orphan-prevention operational mechanics (cascade + sweep job) — S8
- FK + referential-integrity revisit — S11
- Voyage-vs-open-source publication-reproducibility re-embedding pipeline — tracked in roadmap; lands when publication target #4 ships data
- (ζ) build-time validation: collapse main table + `vec0` into single virtual table with auxiliary metadata columns — roadmap

### Sources

User direction throughout the Q5.1 → Q5.5 + Q5.2.1 dialogue (2026-05-04); user prompted Q5.2 critical re-look (surfaced silent adjustments + the genuine PHI defense-in-depth question Q5.2.1) + Q5.3 cleaner-way challenge (surfaced and rejected (γ)/(δ)/(ε)/(ζ) alternatives, with (ζ) flagged for build-time validation only).

---

## S6 — Authority table + ingredient identity resolution

> Resolved 2026-05-04 across five sub-decisions Q6.1–Q6.5 (with sub-questions Q6.2.1, Q6.3.a/b/c, Q6.5.a/b.i/b.ii).

### Decision

**Single `authority_records` table** with `authority_namespace` discriminator + JSON payload for namespace-specific fields (consistent with S1/S4/S5 single-table-plus-discriminator pattern); **separate `authority_resolution_review_queue` table** for failed/ambiguous resolution attempts (per Q6.3.c) with PHI defense-in-depth marker; **hybrid trigram + embedding rerank** fuzzy match algorithm leveraging S5 embeddings layer; **two-threshold tier** confidence semantics mapping directly to S1 `authority_resolution_status` enum (`'fully_resolved' | 'partial' | 'unresolved_pending_review'`); **eager seed for small/internal namespaces** (cuisine, cooking_technique, pairing_role, nutrient) + **lazy seed on demand for vast vocabularies** (ingredient subset, clinical_code) with **selective DRE auto-trigger** per namespace; **DRE-created records stay at `'auto_resolved_high_confidence'`** tier until human review.

### Q6.1 — Single authority_records table

One `authority_records` table with `authority_namespace` discriminator (`'ingredient' | 'nutrient' | 'clinical_code' | 'cuisine' | 'cooking_technique' | 'pairing_role'`).

- Mirrors the consistent pattern across S1/S4/S5 — single table + discriminator + JSON payload
- `authority_resolution_status` from S1 references "an authority record" generically; type-uniform table simplifies FK semantics (atom rows reference authority via single table regardless of namespace)
- Hybrid (c) was the genuine alternative (separate `authority_ingredients` table for the dominant-volume namespace) — rejected for consistency-first; per-namespace partial indexes addable later as optimization without schema churn

### Q6.2 — Authority records schema

```sql
CREATE TABLE authority_records (
  id                        TEXT PRIMARY KEY,            -- aut-{uuidv7}
  authority_namespace       TEXT NOT NULL,               -- 'ingredient' | 'nutrient' | 'clinical_code' | 'cuisine' | 'cooking_technique' | 'pairing_role'
  canonical_name            TEXT NOT NULL,               -- canonical English name
  canonical_name_normalized TEXT NOT NULL,               -- lowercased + diacritic-stripped + whitespace-normalized for fuzzy match (computed at write time)
  external_identifiers      TEXT NOT NULL,               -- JSON object: {"usda_fdc_id": "11215", "icd10": "I10", "snomed": "59621000", ...}
  parent_authority_id       TEXT,                        -- FK to authority_records.id; NULL for root entries; supports hierarchies
  aliases                   TEXT NOT NULL,               -- JSON array of alternate names + transliterations
  display_metadata          TEXT,                        -- JSON; namespace-specific display hints (preferred unit for nutrients, common-pairing tags for ingredients)
  payload                   TEXT NOT NULL,               -- JSON; namespace-specific authoritative fields per schema-of-schemas (per S2 Q2.5)
  resolution_status         TEXT NOT NULL DEFAULT 'verified',  -- 'verified' | 'auto_resolved_high_confidence' | 'pending_review' | 'deprecated'
  state_changed_at          TEXT NOT NULL,               -- ISO 8601 UTC
  source_origin             TEXT NOT NULL,               -- JSON: which authoritative source(s) seeded this record (for publication-reproducibility + epistemic trail)
  recorded_at               TEXT NOT NULL,               -- ISO 8601 UTC
  valid_from                TEXT NOT NULL,               -- ISO 8601 UTC; bitemporal — authority records change over time
  valid_until               TEXT,                        -- ISO 8601 UTC; NULL = currently valid
  retraction_reason         TEXT,                        -- NULL | 'superseded' | 'merged_into_other' | 'deprecated_by_source'
  superseded_by_id          TEXT,                        -- FK to authority_records.id; populated when this record was merged or superseded
  system_version            TEXT NOT NULL,
  component_version         TEXT NOT NULL,
  payload_schema_version    TEXT NOT NULL,
  publication_eligible      INTEGER NOT NULL DEFAULT 1,
  CHECK (authority_namespace IN ('ingredient','nutrient','clinical_code','cuisine','cooking_technique','pairing_role')),
  CHECK (resolution_status IN ('verified','auto_resolved_high_confidence','pending_review','deprecated'))
);

CREATE INDEX idx_aut_namespace_normname ON authority_records(authority_namespace, canonical_name_normalized) WHERE valid_until IS NULL;
CREATE INDEX idx_aut_canonical_name      ON authority_records(canonical_name) WHERE valid_until IS NULL;
CREATE INDEX idx_aut_parent              ON authority_records(parent_authority_id) WHERE valid_until IS NULL;
```

Schema rationale (the *why* per non-obvious column):

- **`canonical_name_normalized`** — separate from `canonical_name` so the hot-path fuzzy-match index doesn't pay normalization cost per query
- **`external_identifiers`** as JSON object — open-ended cross-DB mapping; avoids N×M join tables; queryable via `json_extract`
- **`parent_authority_id`** — supports hierarchies (cantonese → chinese; gala_apple → apple; tadka → tempering); recursive CTE for traversal consistent with S4 Q4.5 + F7
- **`aliases`** as JSON array — alternate names + spellings + transliterations; informs fuzzy-match candidate generation; internationalization-aware
- **`display_metadata`** vs. **`payload`** — display-side hints separate from canonical authoritative data; display side may evolve faster
- **`resolution_status`** 4-state lifecycle — `'verified'` (human-curated or seeded from authoritative source) / `'auto_resolved_high_confidence'` (DRE or LLM-resolved with confidence above threshold per D4) / `'pending_review'` / `'deprecated'`
- **Bitemporal** (`valid_from`, `valid_until`) + **`superseded_by_id`** — authority records change over time (ICD-10 codes deprecated, ingredient definitions revised, cuisines re-categorized); bitemporal pattern lets old references stay resolvable; `superseded_by_id` redirects cleanly
- **`source_origin`** — which authoritative source(s) seeded this record; critical for publication-reproducibility + epistemic trail (per E1)
- **No `subject_id` / `subject_type`** — authority records aren't *about* a subject; they *are* the subject for other records to reference

### Q6.2.1 — JSON-path index on external_identifiers (deferred to S11/S12)

Hot-path lookup "find authority record by USDA FDC ID 11215" requires JSON-path index (via generated column) or full table scan. **Deferred to S11/S12** — generate columns added when actual query patterns prove out. We don't yet know the query mix (ingredient resolution dominant; clinical-code lookup may be cold path; pairing-role lookups tiny). Premature optimization at S6.

### Q6.3 — Fuzzy match resolution algorithm + confidence semantics

Operational pipeline: incoming text → resolver → authority record. Three stages:
1. **Exact match on `canonical_name_normalized`** — instant; binds with confidence 1.0
2. **Alias match** — query `aliases` JSON array; binds with confidence 0.95
3. **Fuzzy match** — algorithm per Q6.3.a; binds at threshold per Q6.3.b; queues below threshold per Q6.3.c

#### Q6.3.a — Hybrid trigram + embedding rerank (chosen)

- **Trigram first-pass** via SQLite FTS5 trigram tokenizer (built-in; essentially free at our scale); eliminates obvious matches fast
- **Embedding rerank** for ambiguous cases (3+ candidates within trigram-score band) — uses S5 embeddings layer; bounded cost
- Authority records embedded under `subject_type='authority_record'` per S5 — operational dependency: every new authority record must be embedded (one-time + ongoing cost; meaningful for ingredient namespace at 100k+ records)
- Rejected: pure trigram (weaker on semantic synonyms), pure Levenshtein (weaker on word-order), pure embedding (pays embedding-lookup cost per resolution; trigram first-pass keeps common case fast)

#### Q6.3.b — Two-threshold tier (chosen)

Maps directly to S1 `authority_resolution_status` enum:

- **Above 0.90** → `'fully_resolved'` (auto-resolve)
- **Between 0.75 and 0.90** → `'partial'` (resolved-but-flagged for opportunistic review)
- **Below 0.75** → `'unresolved_pending_review'` (queue entry per Q6.3.c)

Aggressive enough to keep user-review queue manageable + conservative enough to surface true ambiguity.

#### Q6.3.c — Failed + ambiguous resolution attempts only (chosen)

Successful auto-resolutions don't get audit-trail records (mostly noise; trillions of typical "garlic" → "garlic" cases). Failed/ambiguous attempts get recorded in `authority_resolution_review_queue` table per Q6.4 — feeds user-review UX, lets us improve the resolver over time, gives publication-reproducibility data on resolution accuracy.

### Q6.4 — Authority resolution review queue

```sql
CREATE TABLE authority_resolution_review_queue (
  id                          TEXT PRIMARY KEY,            -- arq-{uuidv7}
  input_text                  TEXT NOT NULL,               -- as-received text that needed resolution
  input_text_normalized       TEXT NOT NULL,               -- normalized form used in fuzzy match
  authority_namespace         TEXT NOT NULL,
  source_atom_id              TEXT NOT NULL,               -- loose polymorphic ref consistent with S4/S5
  source_atom_type            TEXT NOT NULL,               -- 'atom' | 'molecule' | 'synthesized'
  source_field_path           TEXT NOT NULL,               -- which field on the source held the unresolved text
  phi_categories              TEXT NOT NULL,               -- JSON array; defense-in-depth per S5 Q5.2.1 pattern (queue entries can carry PHI)
  candidate_authority_ids     TEXT NOT NULL,               -- JSON array of {authority_id, confidence_score, match_method}; AUDIT SNAPSHOT at attempt time; user-review UI re-runs resolution for fresh candidates
  resolution_method_attempted TEXT NOT NULL,               -- 'trigram' | 'embedding_rerank' | 'hybrid'
  triggered_by                TEXT NOT NULL,               -- 'recipe_ingest' | 'grocery_order' | 'intake_response' | 'corpus_extraction' | 'dynamic_research_expansion' | etc.
  status                      TEXT NOT NULL DEFAULT 'pending',
  state_changed_at            TEXT NOT NULL,
  resolved_authority_id       TEXT,                        -- FK to authority_records.id when resolved
  resolution_metadata         TEXT,                        -- JSON; flexible audit trail
  recorded_at                 TEXT NOT NULL,
  system_version              TEXT NOT NULL,
  component_version           TEXT NOT NULL,               -- resolver pipeline version
  CHECK (source_atom_type IN ('atom','molecule','synthesized')),
  CHECK (status IN ('pending','resolved_by_user','resolved_by_system_update','created_new_authority','declined_unresolvable')),
  CHECK (resolution_method_attempted IN ('trigram','embedding_rerank','hybrid'))
);

CREATE INDEX idx_arq_status_changed   ON authority_resolution_review_queue(status, state_changed_at) WHERE status = 'pending';
CREATE INDEX idx_arq_source_atom      ON authority_resolution_review_queue(source_atom_id, source_atom_type);
CREATE INDEX idx_arq_namespace        ON authority_resolution_review_queue(authority_namespace, status);
```

Status state machine (5 states):
- `'pending'` — awaiting user action
- `'resolved_by_user'` — user picked one of the candidates or created new
- `'resolved_by_system_update'` — authority record was updated/added since queue entry; resolver re-attempted and now binds with high confidence (S8 operational dependency: replay job)
- `'created_new_authority'` — user signaled "this is a new thing"; new authority record created and bound
- `'declined_unresolvable'` — user signaled "this can't be resolved"; leave unresolved on source atom

PHI defense-in-depth: `phi_categories` column carries the PHI marker copied from source atom at queue-entry write time. Unlike S5 there's no CHECK constraint (queue accepts any PHI category set; PHI-aware not PHI-restricted), but the column documents the routing concern + lets queue retention + cleanup + future cloud-bound resolution-improvement pipeline filter PHI entries deterministically.

### Q6.5 — Seeding strategy + dynamic-research-expansion integration

#### Q6.5.a — Eager seed for small/internal + lazy seed for vast vocabularies

**Eager-seeded namespaces** (shipped with MVP DB; static-ish; fully populated):
- **`nutrient`** — IOM/NAM DRI tables + WHO/FAO + INFOODS tagnames (~50-150 records)
- **`cuisine`** — internal taxonomy from sweep #12 (~50-100 records)
- **`cooking_technique`** — internal taxonomy from sweep #12 + sweep #14 (~100-200 records)
- **`pairing_role`** — internal taxonomy from sweep #14 (~20-30 records)

**Lazy-seeded namespaces** (seed minimally + expand on demand):
- **`ingredient`** — seed "common pantry" subset (~5-10k records covering top ingredients in seeded recipes per sweep #11) at MVP; expand via DRE when resolution falls below threshold
- **`clinical_code`** — seed nothing at MVP; populate on demand when `clinical_disclosure` references one and resolution succeeds against external source

#### Q6.5.b.i — Selective DRE auto-trigger per namespace

Per-namespace policy in resolver config:
- **Auto-trigger DRE** for namespaces with well-documented authoritative APIs + high resolution success rates (`ingredient`, `clinical_code`)
- **User-trigger DRE only** for namespaces without canonical external APIs (`cuisine`, `cooking_technique`, `pairing_role`) — auto-triggering would mostly fail

#### Q6.5.b.ii — DRE-created records stay at 'auto_resolved_high_confidence'

When DRE creates a new authority record from external API:
- `resolution_status` defaults to `'auto_resolved_high_confidence'` (NOT `'verified'`)
- Promotion to `'verified'` requires human review
- Keeps the verification tier honest — `'verified'` is reserved for human-curated or seeded-from-authoritative-source records

`source_origin` JSON records the DRE fetch + API source + epistemic-trail verification chain.

### Out of scope at S6 (deferred)

- **Authority-record dedup-suggestion job** — periodic scan for fuzzy-similar authority records within same namespace; surfaces merge candidates for human review (S8). Schema accommodates merges via `superseded_by_id` + `valid_until` columns.
- **Queue replay-on-update job** — when authority records change, replay pending queue entries to see if any now resolve at high confidence; supports `'resolved_by_system_update'` status (S8)
- **JSON-path index on `external_identifiers`** — generate columns + indexes per common identifier system; deferred to S11/S12 once query patterns prove out
- **Authority-record embedding pipeline cost** — embedding ~10k+ ingredients at MVP + ongoing per DRE expansion; operational planning lands in S8

### Schema impact summary

After S6:

- **2 new tables** — `authority_records` + `authority_resolution_review_queue`
- **6 authority namespaces** — ingredient, nutrient, clinical_code, cuisine, cooking_technique, pairing_role
- **Hot-path index** — `(authority_namespace, canonical_name_normalized)` partial on `valid_until IS NULL`
- **Two-threshold tier** mapping resolver confidence → S1 `authority_resolution_status` enum
- **Hybrid trigram + embedding rerank** algorithm leveraging S5 embeddings layer
- **PHI defense-in-depth** on review queue (column carrying marker, no CHECK)
- **Eager + lazy seeding** with selective DRE auto-trigger per namespace
- **Three S8 operational dependencies flagged:** dedup-suggestion job, queue replay-on-update job, authority-record embedding pipeline cost

### Sources

User direction throughout the Q6.1 → Q6.5 dialogue (2026-05-04); user prompted Q6.4 critical re-look (surfaced PHI marker omission as significant adjustment + slimmed `resolution_method_attempted` enum + clarified `candidate_authority_ids` audit-snapshot semantics).

---

## S7 — Verification rule-set per B2 epistemic trail verification

> Resolved 2026-05-05 across five sub-decisions Q7.1–Q7.5 (with sub-questions Q7.3.a/b, Q7.4.a/b, Q7.5.a/b).

### Decision

**Hybrid code-plus-data verification rules** (code defines rule kinds + execution machinery; data defines rule instances + parameters); **two new tables** — `verification_rules` (rule definitions) + `verification_results` (per-(record, rule, run) audit trail) — plus **inline summary columns added to S1 base column set** (verification_status + last_verified_at + verification_summary growing the base set from 21 to 24 columns); **hybrid write-time-for-critical-rules + async-default execution** with `runs_at_write_time` column flagging which rules block writes; **hybrid targeted reverse-index + low-frequency full-sweep re-verification triggers**; **fails + warnings surface by default** in epistemic trail UX; **conditional manual re-verify with soft rate-limit + transparent messaging** per anti-paternalism + epistemic-honesty pattern.

### Q7.1 — Hybrid code-plus-data rules

Pure code makes rule additions/changes require code releases; pure data forces complex execution machinery into the substrate (interpreters, DSL evaluators) and can't fully accommodate LLM-causal-explanation rules. Hybrid maps naturally onto rule categories — range/reference/cross-field checks are highly parameterizable + data-friendly; LLM-causal-explanation is inherently code-driven.

Likely rule kinds at MVP: `'range_check'` | `'reference_resolves'` | `'unit_valid'` | `'cross_field_consistency'` | `'derivation_math_check'` | `'authority_namespace_match'` | `'llm_causal_explanation'`. Adding a new kind requires both code (executor) + data (rule instances) work — manageable but means rule-kind set evolves slowly.

Maps onto S2 schema-of-schemas pattern (Q2.5) — canonical declarative file + per-type modules.

### Q7.2 — verification_rules table schema

```sql
CREATE TABLE verification_rules (
  id                       TEXT PRIMARY KEY,            -- vrl-{uuidv7}
  rule_kind                TEXT NOT NULL,
  applies_to_type          TEXT NOT NULL,               -- target type discriminator (e.g., 'lab_analyte_value', 'inference', '*' for type-agnostic)
  applies_to_layer         TEXT NOT NULL,               -- 'atom' | 'molecule' | 'synthesized' | 'relationship' | '*'
  applies_to_field_path    TEXT,                        -- JSON path within payload the rule targets; NULL for whole-record rules
  rule_payload             TEXT NOT NULL,               -- JSON; rule-kind-specific parameters
  rule_severity            TEXT NOT NULL DEFAULT 'blocking',  -- 'blocking' | 'warning' | 'advisory'
  runs_at_write_time       INTEGER NOT NULL DEFAULT 0,  -- per Q7.4.a: 1 = write-time blocking; 0 = async post-write
  rule_description         TEXT NOT NULL,               -- markdown; user-facing in epistemic trail drill-in
  rule_description_format  TEXT NOT NULL DEFAULT 'markdown',
  source_origin            TEXT NOT NULL,               -- JSON: where rule came from (manual_seed, sweep_<n>, dre_authority_update, regulatory_source, etc.)
  evidence_tier            INTEGER,                     -- when rule grounded in literature (e.g., biological-plausibility ranges from clinical guidelines)
  active                   INTEGER NOT NULL DEFAULT 1,
  recorded_at              TEXT NOT NULL,
  valid_from               TEXT NOT NULL,
  valid_until              TEXT,                        -- bitemporal — rules deprecate as authority sources update
  retraction_reason        TEXT,
  superseded_by_id         TEXT,                        -- FK to verification_rules.id when rule was revised
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,               -- rule executor version (rule_kind machinery changes)
  payload_schema_version   TEXT NOT NULL,               -- rule_payload schema version
  publication_eligible     INTEGER NOT NULL DEFAULT 1,
  CHECK (rule_kind IN ('range_check','reference_resolves','unit_valid','cross_field_consistency','derivation_math_check','authority_namespace_match','llm_causal_explanation')),
  CHECK (applies_to_layer IN ('atom','molecule','synthesized','relationship','*')),
  CHECK (rule_severity IN ('blocking','warning','advisory')),
  CHECK (runs_at_write_time IN (0,1))
);

CREATE INDEX idx_vrl_target          ON verification_rules(applies_to_layer, applies_to_type, active) WHERE valid_until IS NULL;
CREATE INDEX idx_vrl_kind            ON verification_rules(rule_kind, active) WHERE valid_until IS NULL;
CREATE INDEX idx_vrl_writetime       ON verification_rules(runs_at_write_time, active) WHERE valid_until IS NULL;
```

Schema rationale per non-obvious column:

- **`applies_to_type` + `applies_to_layer` + `applies_to_field_path`** — three-part target spec; wildcards (`'*'`) for type-agnostic rules
- **`rule_payload`** examples by kind:
  - `range_check`: `{"min": 0, "max": 200, "unit": "ng_mL", "applies_when": {"$.analyte_canonical_id": "aut-vitamin-d"}}`
  - `reference_resolves`: `{"reference_path": "$.analyte_canonical_id", "must_exist_in": "authority_records", "namespace": "nutrient"}`
  - `cross_field_consistency`: `{"fields": ["$.measurement_period_start", "$.measurement_period_end"], "constraint": "start_before_end"}`
  - `llm_causal_explanation`: `{"prompt_template_id": "...", "expected_inference_pattern": "..."}`
- **`rule_severity`** three tiers — `'blocking'` prevents the record from being written/marked-verified; `'warning'` flags but doesn't block; `'advisory'` logs but doesn't surface to user
- **`runs_at_write_time`** flag (per Q7.4.a) — write-time-blocking rules typically: all `reference_resolves` (otherwise we write atoms with broken FKs), all `unit_valid` (cheap; structural), all blocking-severity `range_check` (cheap; user-protection). Async-only: `cross_field_consistency` (some non-trivial), `derivation_math_check` (some need DB context), all `llm_causal_explanation` (cost-prohibitive at write time)
- **Bitemporal columns** — rules deprecate; bitemporal lets old verification results stay interpretable against the rule version that ran them
- **`component_version`** distinct from `payload_schema_version` — executor machinery may change independently of rule payload schema; both matter for reproducibility

**Rule-count expectation at MVP:** with 18 atom + 6 molecule + 15 synthesized = 39 type schemas, and likely 3-10 rules per type, rule count lands ~150-400 records. Manageable; seeding strategy needs care (deliberately authored, not boilerplate auto-generated).

### Q7.3 — Verification results storage (hybrid summary + detail)

#### Q7.3.a — Hybrid: inline summary + separate detail table

Inline summary on the verified record (status access is hot path — every UX surface that drills into epistemic trail asks "is this verified?" first); full detail in separate `verification_results` table for audit-grade queries.

Pure inline-only forces every record's payload to carry result history (bloats records that get re-verified frequently); pure separate-only loses fast status access (forces a join + aggregation for every status check).

#### Q7.3.b — verification_results table schema

```sql
CREATE TABLE verification_results (
  id                            TEXT PRIMARY KEY,            -- vrs-{uuidv7}
  rule_id                       TEXT NOT NULL,               -- FK to verification_rules.id
  rule_version_at_run           TEXT NOT NULL,               -- snapshot of verification_rules.component_version at run time
  subject_id                    TEXT NOT NULL,               -- record being verified (loose polymorphic per S4/S5/S6)
  subject_type                  TEXT NOT NULL,               -- 'atom' | 'molecule' | 'synthesized' | 'relationship'
  subject_layer_record_version  TEXT,                        -- snapshot of subject's component_version + payload_schema_version at run time
  outcome                       TEXT NOT NULL,               -- 'pass' | 'warning' | 'fail' | 'error_executor' | 'skipped_inapplicable'
  outcome_detail                TEXT,                        -- markdown; for warnings/fails, what specifically went wrong + which field path
  outcome_detail_format         TEXT NOT NULL DEFAULT 'markdown',
  rule_kind_at_run              TEXT NOT NULL,               -- snapshot of rule_kind at run time
  evidence_observed             TEXT,                        -- JSON; for cross-field/range/causal-explanation rules, actual values observed
  llm_provider                  TEXT,                        -- for rule_kind = 'llm_causal_explanation' only
  llm_model                     TEXT,                        -- for rule_kind = 'llm_causal_explanation' only
  llm_request_id                TEXT,                        -- correlation to operational event log (S8) for LLM-based verifications
  ran_at                        TEXT NOT NULL,
  ran_by                        TEXT NOT NULL,               -- 'system_pipeline' | 'manual_user_trigger' | 'dre_post_authority_update' | etc.
  recorded_at                   TEXT NOT NULL,
  system_version                TEXT NOT NULL,
  component_version             TEXT NOT NULL,               -- verification executor pipeline version
  CHECK (subject_type IN ('atom','molecule','synthesized','relationship')),
  CHECK (outcome IN ('pass','warning','fail','error_executor','skipped_inapplicable'))
);

CREATE INDEX idx_vrs_subject       ON verification_results(subject_id, subject_type, ran_at DESC);
CREATE INDEX idx_vrs_outcome       ON verification_results(outcome, ran_at) WHERE outcome IN ('warning','fail','error_executor');
CREATE INDEX idx_vrs_rule          ON verification_results(rule_id, ran_at);
```

Schema rationale per non-obvious column:

- **`rule_version_at_run` + `subject_layer_record_version`** — both snapshots needed because rules and records both evolve; results must remain interpretable against the versions that produced them. Without these, re-verification triggers (rule updated → re-verify; subject mutated → re-verify) can't tell whether a stored result is stale
- **`outcome` 5-state enum** distinguishes:
  - `'pass'` — rule passed
  - `'warning'` — rule failed at warning severity
  - `'fail'` — rule failed at blocking severity
  - `'error_executor'` — rule didn't execute properly (LLM call failed, malformed rule_payload, etc.); distinct from rule semantics
  - `'skipped_inapplicable'` — rule's `applies_when` clause didn't match this record; recorded for completeness
- **`outcome_detail`** as markdown — user-facing surface in epistemic trail audit view (per B2 + C5)
- **`evidence_observed`** as JSON — for range/cross-field/causal-explanation rules, the actual values; lets audit reconstruct *why* the rule failed without re-fetching the record at result-display time
- **`llm_*` columns** populated only for `llm_causal_explanation` kind — lets audit reproduce + trace LLM-based verification calls; `llm_request_id` correlates to operational event log (S8)
- **`ran_by`** — provenance: who triggered the verification run (pipeline scheduled, user manual trigger, DRE post-authority-update job)

#### S1 base column expansion (21 → 24 columns)

Three new columns added to the canonical S1 base column set across all atom/molecule/synthesized/relationship layers:

```sql
verification_status      TEXT,                          -- NULL | 'verified' | 'verified_with_warnings' | 'verification_failed' | 'verification_pending' | 'verification_inapplicable'
last_verified_at         TEXT,                          -- ISO 8601 UTC; latest verification run
verification_summary     TEXT                           -- JSON: {pass: N, warning: N, fail: N, error: N, skipped: N}
```

Reason for inline-summary cost (3 columns × every record on every layer): status access is hot path for every UX surface that drills into epistemic trail. Without inline summary, every status check forces a join to `verification_results` + aggregation. Per Q7.3.a hybrid pattern.

### Q7.4 — Verification triggers + cadence

#### Q7.4.a — Hybrid write-time-for-critical + async-default

`verification_rules.runs_at_write_time` column (added to Q7.2 schema) flags which rules block writes:

- **Write-time blocking** (default for): all `reference_resolves` rules (otherwise atoms with broken FKs land in substrate), all `unit_valid` rules (cheap; structural), all blocking-severity `range_check` rules (cheap; user-protection)
- **Async post-write** (default for): `cross_field_consistency` rules (some non-trivial), `derivation_math_check` rules (some need DB context), all `llm_causal_explanation` rules (cost-prohibitive at write time — adding 2-5 seconds per inference write breaks C5 daily-cadence interaction model)

Pure write-time would protect correctness but break interaction model under LLM-causal-explanation overhead; pure async would write objectively-broken records (broken FKs, invalid units). Hybrid keeps writes fast for the common case while preserving structural integrity.

#### Q7.4.b — Hybrid targeted reverse-index + low-frequency full sweep

- **Targeted reverse-index** at change time — when authority records or rules change, query substrate for records that referenced the changed authority/rule; enqueue them. Reverse-lookup indexes already exist for the reference relationships (per S4 + S6 patterns)
- **Low-frequency full sweep** (weekly/monthly) — background job runs all rules against all records; catches drift cases (results stored against old rule versions, LLM-causal-explanation drift, edge-case re-verification missed by targeted invalidation)

S8 territory for the operational details of both pipelines.

### Q7.5 — Verification surface in epistemic trail UX

#### Q7.5.a — Fails + warnings surface by default

`outcome IN ('fail', 'error_executor', 'warning')` surfaces by default in inline drill-in; advisory hidden until user opts to see them. Aligns with `rule_severity` enum where `'advisory'` was defined as "log but don't surface" (Q7.2). Honest about meaningful issues without noise from advisory-tier checks.

#### Q7.5.b — Conditional manual re-verify with soft rate-limit

Per [C5 Q5.4 dedicated audit view](architecture.md#c5--daily-cadence-interaction-model): "re-verify now" button surfaces conditionally — only when `last_verified_at` is older than threshold OR when current `verification_status = 'verification_pending'`. Anti-noise (don't show button when verification just ran); user-empowering (surface when staleness is plausible). Per [user-decision-framework.md](user-decision-framework.md) "surface + let user decide" pattern.

**Soft rate-limit on manual re-verification:** if user re-verifies a record N times in a window (e.g., 3 in an hour), surface transparent message: *"You've re-verified this 3 times in the last hour; verification re-runs the same logic and the result is unlikely to change unless source data changed."* Friction, not block — per anti-paternalism (sweep #14/Tension #7) + cost transparency (LLM-causal-explanation re-verifications hit cloud LLM with real cost).

### Out of scope at S7 (deferred)

- **Targeted re-verification queue mechanics + low-frequency full-sweep job** — operational pipeline lands in S8
- **Per-rule seeding from sweep findings** — the actual rule instances at MVP (vitamin D plausibility ranges from sweep #1 DRI tables, ingredient-resolution rules from sweep #11 corpus, etc.) are content-not-schema; tracked for build phase
- **Soft rate-limit window + thresholds** — UX details (3 per hour? 10 per session?); build-phase decision
- **`evidence_observed` JSON shape per rule kind** — declared in canonical schema-of-schemas (per S2 Q2.5); concrete shapes land alongside per-rule-kind executors at build time

### Schema impact summary

After S7:

- **2 new tables** — `verification_rules` + `verification_results`
- **S1 base column set grows from 21 to 24 columns** — `verification_status` + `last_verified_at` + `verification_summary` added across all atom/molecule/synthesized/relationship layers
- **7 verification rule kinds** — range_check, reference_resolves, unit_valid, cross_field_consistency, derivation_math_check, authority_namespace_match, llm_causal_explanation
- **3 rule severities** — blocking, warning, advisory
- **5 verification outcomes** — pass, warning, fail, error_executor, skipped_inapplicable
- **6 verification-status states on records** — verified, verified_with_warnings, verification_failed, verification_pending, verification_inapplicable, NULL
- **`runs_at_write_time` flag on rules** — separates synchronous (block-on-write) from asynchronous (post-write) verification per Q7.4.a
- **Two S8 operational dependencies flagged from S7:** targeted re-verification queue mechanics, low-frequency full-sweep job

### Sources

User direction throughout the Q7.1 → Q7.5 dialogue (2026-05-04 → 2026-05-05); user prompted explicit confirmation on the S1 base column expansion since adding 3 columns to the canonical base set across all layers is non-trivial.

---

## S8 — Operational DB tables

> Resolved 2026-05-05 across three sub-decisions Q8.1–Q8.3 (with sub-questions Q8.2.a-e).

### Decision

**Knowledge/infrastructure boundary** as load-bearing criterion separating substrate (what the system knows) from operational (how the system worked); **two-layer pattern** of substrate-atom + heavy operational-counterpart correlated via `request_id` (e.g., S2 Atom 18 `phi_crossing_event` substrate ↔ `op_llm_request_log` operational); **8 operational tables at MVP** spanning event log + session/state + cycle-state + job queue families; **`op_event_log` collapses audit + epistemic-trail + system events** into single table with `event_kind` discriminator (consistent with S4-S6 single-table-plus-discriminator pattern); **single `op_job_queue`** with `job_kind` discriminator covering the 5 S6+S7 operational dependencies; **generic-payload pattern** for build-time-heavy tables (`op_agent_orchestration_state`, `op_dre_cycle_state`, `op_corpus_refresh_cycle_state`) — schema stable, payload shape build-time-determined; **PHI defense-in-depth on `op_llm_request_log`** (`phi_categories TEXT NOT NULL` + `CHECK (phi_categories = '[]')` — same pattern as S5 Q5.2.1 / S6 Q6.4); `op_user_session` dropped as speculative (UI session state is client-side concern at A1+A2 deployment model).

### Q8.1 — Knowledge/infrastructure boundary + two-layer pattern

The substrate-vs-operational decision rule: ask "does this represent something the system *knows*, or how the system *worked*?"

- **Substrate**: atoms, molecules, synthesized, relationships, authority records, verification rules + results (verification *outcomes* are knowledge about a record's trustworthiness)
- **Operational**: HTTP/LLM call logs, session state, intake-session in-progress state, job queue entries

**Two-layer pattern:** operational tables are the heavy/transient counterpart to lighter substrate atoms that reference them. Substrate `audit_log_entry` (S2 Synthesized 16) is a knowledge-record about the operation; operational `op_event_log` is the heavy detail. Substrate `phi_crossing_event` (S2 Atom 18) carries *what crossed*; operational `op_llm_request_log` carries the full request/response payload + timing + retry state. Correlation via shared `request_id`.

Three framings hold in alignment but knowledge/infrastructure (b) is the load-bearing one:
- (a) mutable/immutable is mostly a consequence of (b) — knowledge gets supersession discipline because facts evolve via new evidence; infrastructure mutates because work-in-flight changes constantly
- (c) reproducibility is also a consequence — you reproduce knowledge, not the operational pipeline

### Q8.2 — Operational table set enumeration (8 tables)

#### Q8.2.a — Table set after collapse

**Event log family:**
1. `op_llm_request_log` — every LLM API call: provider + model + payloads (or hashes) + tokens + latency + retry state. Correlates to substrate `phi_crossing_event` + `verification_results.llm_request_id`
2. `op_event_log` — collapsed audit + epistemic-trail + system events (single table, `event_kind` discriminator)

**Session + state family:**
3. `op_intake_session_state` — per C3 pause-anywhere intake; resumable in-progress state
4. `op_agent_orchestration_state` — per C1 hybrid orchestrator + bounded sub-agents; in-flight orchestration state (generic-payload per Q8.2.d)

**Cycle-state family** (per Q8.2.d generic-payload pattern):
5. `op_dre_cycle_state` — per B3 cascade-failure with partial-success rebuild
6. `op_corpus_refresh_cycle_state` — per E4 hybrid trickle + scheduled batch

**Job queue family:**
7. `op_job_queue` — single table covering 5 S6+S7 operational dependencies (per Q8.2.b)
8. `op_job_execution_log` — audit trail for the queue

#### Q8.2.b — Single `op_job_queue` table with `job_kind` discriminator

Same single-table-plus-discriminator pattern as S4-S7. Covers the 5 operational dependencies flagged from S6+S7: authority dedup-suggestion, queue replay-on-update, authority-record embedding, targeted re-verification, low-frequency full-sweep verification. Adding new job kinds = new discriminator value, not new table.

#### Q8.2.c — Dropped `op_user_session`

UI session state is client-side concern at A1+A2 deployment model (native macOS app + localhost web). Speculative table; can add later if a real persistence need surfaces.

#### Q8.2.d — Generic-payload pattern for build-time-heavy tables

`op_agent_orchestration_state`, `op_dre_cycle_state`, `op_corpus_refresh_cycle_state` get spec'd at minimal-shape level only at S8: `(id, kind, status, correlation_id, payload JSON, created_at, updated_at, completed_at)` + relevant per-table fields. Payload shape flagged for build-time refinement when underlying machinery (orchestration framework, DRE pipeline, refresh pipeline) is concrete.

Same pattern S5 used for local-model-choice deferral. Keeps tables present in schema (so application code can write to them from day 1) without committing to payload shapes that will likely be wrong without the framework choice.

#### Q8.2.e — PHI defense-in-depth on `op_llm_request_log`

`phi_categories TEXT NOT NULL` column + `CHECK (phi_categories = '[]')` constraint — same pattern as S5 Q5.2.1 / S6 Q6.4. Per phi-handling.md cloud LLM calls go through PHI decomposition; request payloads sent to cloud providers should never contain PHI by routing rule. CHECK constraint is the schema-level fail-closed guard.

### Q8.3 — Operational table schemas

#### Event log family

```sql
-- 1. LLM request log
CREATE TABLE op_llm_request_log (
  id                       TEXT PRIMARY KEY,            -- llr-{uuidv7}
  request_id               TEXT NOT NULL,               -- correlates to substrate phi_crossing_event.request_id + verification_results.llm_request_id
  llm_provider             TEXT NOT NULL,
  llm_model                TEXT NOT NULL,
  request_payload_hash     TEXT NOT NULL,               -- SHA-256 of full request payload
  request_payload          TEXT,                        -- full payload if under size threshold; NULL if hash-only (build-time threshold)
  response_payload         TEXT,
  response_payload_hash    TEXT NOT NULL,
  prompt_tokens            INTEGER,
  completion_tokens        INTEGER,
  total_cost_usd           REAL,                        -- approximate; informs cost transparency per Q7.5.b
  latency_ms               INTEGER,
  retry_attempts           INTEGER NOT NULL DEFAULT 0,
  outcome                  TEXT NOT NULL,
  error_detail             TEXT,
  phi_categories           TEXT NOT NULL,               -- per Q8.2.e defense-in-depth
  caller_context           TEXT NOT NULL,               -- 'intake_agent' | 'verification' | 'inference_synthesis' | 'dre_extraction' | etc.
  started_at               TEXT NOT NULL,
  completed_at             TEXT,
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (outcome IN ('success','error_provider','error_timeout','error_rate_limit','error_validation')),
  CHECK (phi_categories = '[]')                          -- defense-in-depth: cloud LLM calls never carry PHI
);

CREATE INDEX idx_llr_request_id    ON op_llm_request_log(request_id);
CREATE INDEX idx_llr_caller_time   ON op_llm_request_log(caller_context, started_at DESC);
CREATE INDEX idx_llr_outcome       ON op_llm_request_log(outcome, started_at) WHERE outcome != 'success';
CREATE INDEX idx_llr_provider_time ON op_llm_request_log(llm_provider, started_at DESC);

-- 2. Collapsed event log (audit + epistemic-trail + system events)
CREATE TABLE op_event_log (
  id                       TEXT PRIMARY KEY,            -- evt-{uuidv7}
  event_kind               TEXT NOT NULL,               -- 'audit' | 'epistemic_trail' | 'system'
  event_subkind            TEXT,                        -- per-kind discriminator (e.g., 'data_write', 'consent_change', 'reasoning_step', 'orchestration_handoff')
  request_id               TEXT,                        -- correlation to op_llm_request_log + substrate audit_log_entry
  parent_event_id          TEXT,                        -- FK to op_event_log.id; lets epistemic-trail chains form trees
  subject_id               TEXT,                        -- substrate record this event is about (loose polymorphic per S4/S5/S6)
  subject_type             TEXT,                        -- 'atom' | 'molecule' | 'synthesized' | 'relationship' | NULL for non-record events
  actor                    TEXT NOT NULL,               -- 'user' | 'system' | 'agent_id' | 'job_id' | etc.
  payload                  TEXT NOT NULL,               -- JSON; event-kind/subkind-specific shape per schema-of-schemas
  phi_categories           TEXT NOT NULL,               -- documents routing concern; no CHECK (events legitimately carry PHI when about PHI-bearing records)
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (event_kind IN ('audit','epistemic_trail','system')),
  CHECK (subject_type IN ('atom','molecule','synthesized','relationship') OR subject_type IS NULL)
);

CREATE INDEX idx_evt_request_id    ON op_event_log(request_id);
CREATE INDEX idx_evt_subject       ON op_event_log(subject_id, subject_type, recorded_at DESC);
CREATE INDEX idx_evt_kind_time     ON op_event_log(event_kind, recorded_at DESC);
CREATE INDEX idx_evt_parent        ON op_event_log(parent_event_id) WHERE parent_event_id IS NOT NULL;
```

#### Session + state family

```sql
-- 3. Intake session resumable state (per C3 pause-anywhere)
CREATE TABLE op_intake_session_state (
  id                       TEXT PRIMARY KEY,            -- iss-{uuidv7}
  intake_session_id        TEXT NOT NULL,               -- correlates to substrate intake_session molecule
  current_question_position TEXT,                       -- JSON: {item_bank_id, position_index, last_administered_item_id, ...}
  partial_responses        TEXT NOT NULL,               -- JSON: response staging; flushed to substrate atoms on commit checkpoint or session close (build-time semantics)
  last_paused_at           TEXT,
  resume_count             INTEGER NOT NULL DEFAULT 0,
  agent_state_snapshot     TEXT,                        -- JSON; resume context for agent that was running
  status                   TEXT NOT NULL DEFAULT 'active',
  state_changed_at         TEXT NOT NULL,
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (status IN ('active','paused','committed','abandoned'))
);

CREATE INDEX idx_iss_session_id    ON op_intake_session_state(intake_session_id);
CREATE INDEX idx_iss_status        ON op_intake_session_state(status, state_changed_at) WHERE status IN ('active','paused');

-- 4. Agent orchestration state (generic-payload per Q8.2.d)
CREATE TABLE op_agent_orchestration_state (
  id                       TEXT PRIMARY KEY,            -- aos-{uuidv7}
  orchestration_kind       TEXT NOT NULL,               -- 'intake' | 'recipe_match' | 'inference_synthesis' | 'dre_expansion' | etc.
  status                   TEXT NOT NULL,
  correlation_id           TEXT NOT NULL,               -- group related orchestrations (session_id, request_id)
  payload                  TEXT NOT NULL,               -- JSON; orchestration-kind-specific shape (build-time-determined)
  payload_schema_version   TEXT NOT NULL,
  created_at               TEXT NOT NULL,
  updated_at               TEXT NOT NULL,
  completed_at             TEXT,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (status IN ('in_progress','completed','failed','cancelled'))
);

CREATE INDEX idx_aos_status        ON op_agent_orchestration_state(status, updated_at) WHERE status = 'in_progress';
CREATE INDEX idx_aos_correlation   ON op_agent_orchestration_state(correlation_id);
```

#### Cycle-state family (generic-payload per Q8.2.d)

```sql
-- 5. DRE cycle state (per B3 cascade-failure with partial-success rebuild)
CREATE TABLE op_dre_cycle_state (
  id                       TEXT PRIMARY KEY,            -- drc-{uuidv7}
  cycle_kind               TEXT NOT NULL,               -- 'gap_detection_reactive' | 'proactive_refresh' | 'authority_expansion' | etc.
  trigger_context          TEXT NOT NULL,
  status                   TEXT NOT NULL,
  payload                  TEXT NOT NULL,               -- JSON; per Q8.2.d generic-payload (atom-level success/fail tracking, retry state)
  payload_schema_version   TEXT NOT NULL,
  cycle_started_at         TEXT NOT NULL,
  cycle_ended_at           TEXT,
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (status IN ('in_progress','partial_success','completed','failed','cancelled'))
);

CREATE INDEX idx_drc_status        ON op_dre_cycle_state(status, cycle_started_at) WHERE status IN ('in_progress','partial_success');

-- 6. Corpus refresh cycle state (per E4 hybrid trickle + scheduled batch)
CREATE TABLE op_corpus_refresh_cycle_state (
  id                       TEXT PRIMARY KEY,            -- crc-{uuidv7}
  source_identifier        TEXT NOT NULL,               -- 'usda_fdc' | 'icd10_cms' | 'themealdb' | etc.
  refresh_mode             TEXT NOT NULL,               -- 'trickle' | 'scheduled_batch' | 'manual'
  status                   TEXT NOT NULL,
  last_successful_check_at TEXT,
  last_successful_fetch_at TEXT,
  content_hash_at_check    TEXT,
  payload                  TEXT NOT NULL,               -- JSON; per-source state (per Q8.2.d generic-payload)
  payload_schema_version   TEXT NOT NULL,
  cycle_started_at         TEXT NOT NULL,
  cycle_ended_at           TEXT,
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (refresh_mode IN ('trickle','scheduled_batch','manual')),
  CHECK (status IN ('in_progress','partial_success','completed','failed','no_changes'))
);

CREATE INDEX idx_crc_source_status ON op_corpus_refresh_cycle_state(source_identifier, status, cycle_started_at DESC);
CREATE INDEX idx_crc_status        ON op_corpus_refresh_cycle_state(status, cycle_started_at) WHERE status IN ('in_progress','partial_success');
```

#### Job queue family

```sql
-- 7. Job queue (single table per Q8.2.b)
CREATE TABLE op_job_queue (
  id                       TEXT PRIMARY KEY,            -- job-{uuidv7}
  job_kind                 TEXT NOT NULL,               -- 'authority_dedup_suggest' | 'authority_queue_replay_on_update' | 'authority_record_embed' | 'reverify_targeted' | 'reverify_full_sweep' | etc.
  priority                 INTEGER NOT NULL DEFAULT 5,  -- 1 (highest) to 10 (lowest)
  status                   TEXT NOT NULL DEFAULT 'pending',
  payload                  TEXT NOT NULL,               -- JSON; job-kind-specific input
  payload_schema_version   TEXT NOT NULL,
  scheduled_for            TEXT NOT NULL,               -- ISO 8601 UTC; when job is eligible to run
  attempts                 INTEGER NOT NULL DEFAULT 0,
  max_attempts             INTEGER NOT NULL DEFAULT 3,
  last_attempted_at        TEXT,
  last_error               TEXT,                        -- markdown
  triggered_by             TEXT NOT NULL,
  recorded_at              TEXT NOT NULL,
  state_changed_at         TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (status IN ('pending','in_progress','completed','failed','cancelled','deferred'))
);

CREATE INDEX idx_job_pending_priority ON op_job_queue(priority, scheduled_for) WHERE status = 'pending' AND scheduled_for <= datetime('now');
CREATE INDEX idx_job_status_changed   ON op_job_queue(status, state_changed_at);
CREATE INDEX idx_job_kind_status      ON op_job_queue(job_kind, status);

-- 8. Job execution log
CREATE TABLE op_job_execution_log (
  id                       TEXT PRIMARY KEY,            -- jex-{uuidv7}
  job_id                   TEXT NOT NULL,
  job_kind                 TEXT NOT NULL,               -- denormalized for fast filter without join
  attempt_number           INTEGER NOT NULL,
  outcome                  TEXT NOT NULL,
  outputs_summary          TEXT,                        -- markdown; what the job produced
  outputs_summary_format   TEXT NOT NULL DEFAULT 'markdown',
  side_effects_summary     TEXT,                        -- JSON: structured side-effect tracking (atom IDs created, jobs enqueued, authority records updated)
  error_detail             TEXT,
  duration_ms              INTEGER NOT NULL,
  started_at               TEXT NOT NULL,
  completed_at             TEXT NOT NULL,
  recorded_at              TEXT NOT NULL,
  system_version           TEXT NOT NULL,
  component_version        TEXT NOT NULL,
  CHECK (outcome IN ('success','failure','timeout','cancelled'))
);

CREATE INDEX idx_jex_job_id      ON op_job_execution_log(job_id, attempt_number);
CREATE INDEX idx_jex_kind_time   ON op_job_execution_log(job_kind, started_at DESC);
CREATE INDEX idx_jex_outcome     ON op_job_execution_log(outcome, started_at) WHERE outcome != 'success';
```

### Out of scope at S8 (deferred)

- **Operational DB retention policy** — event logs grow huge fast; retention is operationally critical but not a schema concern. Build/post-MVP.
- **`op_event_log.payload` shape per (event_kind, event_subkind)** — canonical schema-of-schemas territory; concrete shapes land alongside B2 + C5 implementations
- **`op_llm_request_log.request_payload` size threshold for hash-only-vs-full-storage** — depends on cost/storage tradeoffs at build time
- **`op_intake_session_state.partial_responses` flush-to-substrate semantics** — when in-progress responses migrate from operational to substrate (commit checkpoint? session close? per response?). Build-time decision.
- **`op_agent_orchestration_state` / `op_dre_cycle_state` / `op_corpus_refresh_cycle_state` payload shapes** — per Q8.2.d generic-payload pattern; refinement at build time when framework/pipeline machinery is concrete
- **Performance + diagnostic tables** (`op_query_performance_log` etc.) — defer to post-MVP unless build phase surfaces query bottlenecks
- **`op_user_session`** — dropped at Q8.2.c; UI session state client-side at A1+A2

### Schema impact summary

After S8:

- **8 new operational tables** across 4 families (event log, session/state, cycle-state, job queue)
- **Two-layer pattern** formalized: substrate-atom + heavy operational-counterpart correlated via `request_id`
- **Single `op_event_log`** collapses audit + epistemic-trail + system events
- **Single `op_job_queue`** covers 5 S6+S7 operational dependencies
- **PHI defense-in-depth** on `op_llm_request_log` (CHECK constraint at schema layer)
- **Generic-payload pattern** adopted for 3 build-time-heavy tables; payload shape flagged for build-time refinement
- **`op_user_session` dropped** as speculative

### Sources

User direction throughout the Q8.1 → Q8.3 dialogue (2026-05-05); user prompted Q8.2 critical re-look (surfaced 4 adjustments: collapse audit + epistemic-trail event logs, drop `op_user_session`, generic-payload pattern for build-time-heavy tables, PHI defense-in-depth on LLM request log).

---

*S9 (corpus markdown frontmatter contract — revisits M4, M7 flags + E4 source_status fields per preservation-layer.md) is next.*
