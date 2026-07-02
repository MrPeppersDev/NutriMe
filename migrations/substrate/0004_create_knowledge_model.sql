-- Stage 6 step 3 (Knowledge model, initial) — Option B (lean middle).
-- Per stage3-plan.md § "Stage 6 numbered step 3 — entry decision resolved
-- 2026-06-30", land the atom + synthesized_entry tables with the 24-column
-- shared base per schema.md S1 Q1.2. The molecule table is deferred until it
-- has consumers (meal_event / lab_panel etc. land in later steps).
--
-- Column enumerations mirror schema.md S1 Q1.2; CHECK constraints act as the
-- SQLite safety net for the dual JSON-schema validation pattern (application
-- code primary + schema CHECK backstop) per S1 Q1.1.
--
-- The `composition_id` FK-to-molecule column from S1 Q1.2 is deliberately
-- omitted here — no molecule table exists yet, so a nullable orphan column
-- would only be noise. It lands with the molecule migration when the first
-- molecule type has a consumer.
--
-- Per F9 (schema.md S11): every substrate table carries a `tenant_id` FK with
-- cascade delete. `subject_id` + `subject_type` per F2 remain the per-row
-- semantic subject (user / household / member_subset) inside a tenant; the
-- two axes are orthogonal.

CREATE TABLE atom (
    id                              TEXT PRIMARY KEY,
    tenant_id                       TEXT NOT NULL
                                        REFERENCES tenant(id) ON DELETE CASCADE,
    type                            TEXT NOT NULL,
    subject_id                      TEXT,
    subject_type                    TEXT
                                        CHECK (subject_type IS NULL OR subject_type IN
                                               ('user', 'household', 'member_subset')),
    provenance                      TEXT NOT NULL
                                        CHECK (provenance IN
                                               ('validated-instrument',
                                                'conversational-elicitation',
                                                'passive-observation')),
    source_identity                 TEXT,
    evidence_tier                   INTEGER
                                        CHECK (evidence_tier IS NULL OR
                                               evidence_tier BETWEEN 1 AND 4),
    system_aggregate_quality_score  REAL
                                        CHECK (system_aggregate_quality_score IS NULL OR
                                               (system_aggregate_quality_score BETWEEN 0.0 AND 1.0)),
    user_facing_certainty           TEXT
                                        CHECK (user_facing_certainty IS NULL OR
                                               user_facing_certainty IN
                                               ('strong', 'moderate', 'suggestive')),
    valid_from                      TEXT NOT NULL,
    valid_until                     TEXT,
    recorded_at                     TEXT NOT NULL,
    retraction_reason               TEXT
                                        CHECK (retraction_reason IS NULL OR retraction_reason IN
                                               ('superseded',
                                                'retracted_user_correction',
                                                'retracted_source_revision',
                                                'retracted_validation_failure',
                                                'retracted_consent_withdrawn')),
    system_version                  TEXT NOT NULL,
    component_version               TEXT,
    payload_schema_version          TEXT NOT NULL,
    publication_eligible            INTEGER NOT NULL DEFAULT 0
                                        CHECK (publication_eligible IN (0, 1)),
    consent_record_id               TEXT,
    phi_categories                  TEXT NOT NULL DEFAULT '[]'
                                        CHECK (json_valid(phi_categories)),
    authority_resolution_status     TEXT
                                        CHECK (authority_resolution_status IS NULL OR
                                               authority_resolution_status IN
                                               ('fully_resolved', 'partial',
                                                'unresolved_pending_review',
                                                'unresolved_dynamic_expansion_in_flight')),
    payload                         TEXT NOT NULL
                                        CHECK (json_valid(payload))
);

CREATE INDEX idx_atom_tenant_type      ON atom (tenant_id, type);
CREATE INDEX idx_atom_tenant_valid     ON atom (tenant_id, valid_from);
CREATE INDEX idx_atom_currently_valid  ON atom (tenant_id, type) WHERE valid_until IS NULL;

CREATE TABLE synthesized_entry (
    id                              TEXT PRIMARY KEY,
    tenant_id                       TEXT NOT NULL
                                        REFERENCES tenant(id) ON DELETE CASCADE,
    type                            TEXT NOT NULL,
    subject_id                      TEXT,
    subject_type                    TEXT
                                        CHECK (subject_type IS NULL OR subject_type IN
                                               ('user', 'household', 'member_subset')),
    provenance                      TEXT NOT NULL
                                        CHECK (provenance IN
                                               ('validated-instrument',
                                                'conversational-elicitation',
                                                'passive-observation')),
    source_identity                 TEXT,
    evidence_tier                   INTEGER
                                        CHECK (evidence_tier IS NULL OR
                                               evidence_tier BETWEEN 1 AND 4),
    system_aggregate_quality_score  REAL
                                        CHECK (system_aggregate_quality_score IS NULL OR
                                               (system_aggregate_quality_score BETWEEN 0.0 AND 1.0)),
    user_facing_certainty           TEXT
                                        CHECK (user_facing_certainty IS NULL OR
                                               user_facing_certainty IN
                                               ('strong', 'moderate', 'suggestive')),
    valid_from                      TEXT NOT NULL,
    valid_until                     TEXT,
    recorded_at                     TEXT NOT NULL,
    retraction_reason               TEXT
                                        CHECK (retraction_reason IS NULL OR retraction_reason IN
                                               ('superseded',
                                                'retracted_user_correction',
                                                'retracted_source_revision',
                                                'retracted_validation_failure',
                                                'retracted_consent_withdrawn')),
    system_version                  TEXT NOT NULL,
    component_version               TEXT,
    payload_schema_version          TEXT NOT NULL,
    publication_eligible            INTEGER NOT NULL DEFAULT 0
                                        CHECK (publication_eligible IN (0, 1)),
    consent_record_id               TEXT,
    phi_categories                  TEXT NOT NULL DEFAULT '[]'
                                        CHECK (json_valid(phi_categories)),
    authority_resolution_status     TEXT
                                        CHECK (authority_resolution_status IS NULL OR
                                               authority_resolution_status IN
                                               ('fully_resolved', 'partial',
                                                'unresolved_pending_review',
                                                'unresolved_dynamic_expansion_in_flight')),
    payload                         TEXT NOT NULL
                                        CHECK (json_valid(payload))
);

CREATE INDEX idx_synth_tenant_type     ON synthesized_entry (tenant_id, type);
CREATE INDEX idx_synth_tenant_valid    ON synthesized_entry (tenant_id, valid_from);
CREATE INDEX idx_synth_currently_valid ON synthesized_entry (tenant_id, type) WHERE valid_until IS NULL;
