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

*S5 (embedding tables — embeddings_voyage_* + embeddings_local_* layout per B1 Q1.3) is next.*
