-- 0005: consent record family (S8 deliverable, issue #21, E2 model).
--
-- E2: tiered standing-consent (per data category) + per-publication
-- confirmation. This migration lands the standing-consent layer that the
-- live capture surfaces (intake 2.1, inventory 2.2, knowledge 3.1, and
-- step-7 per-meal feedback) must be able to reference; per-publication
-- confirmation rows join later with the publication track.
--
-- consent_record is append-only: a change of mind writes a new row and
-- closes the old one (valid_until), preserving the honest historical
-- record per E2 Q2.5. The 24-column shared base's consent_record_id FK
-- targets consent_record.id.

CREATE TABLE IF NOT EXISTS consent_record (
    id              TEXT PRIMARY KEY,           -- cns-<uuid7>
    tenant_id       TEXT NOT NULL
                        REFERENCES tenant(id) ON DELETE CASCADE,
    subject_user    TEXT NOT NULL DEFAULT 'primary',
    data_category   TEXT NOT NULL,              -- 'intake_screener' | 'intake_profile' | 'inventory' | 'knowledge_derived' | 'meal_feedback_time' | 'meal_feedback_semantic'
    purpose         TEXT NOT NULL,              -- 'local_operation' | 'publication_aggregate'
    granted         INTEGER NOT NULL,           -- 1 grant / 0 explicit decline
    granted_at      TEXT NOT NULL,              -- UTC ISO-8601
    valid_until     TEXT,                       -- NULL = current
    superseded_by   TEXT REFERENCES consent_record(id),
    note            TEXT,
    retroactive     INTEGER NOT NULL DEFAULT 0  -- 1 = covers rows captured before grant (E2 single-user-local allowance)
);

CREATE INDEX IF NOT EXISTS idx_consent_tenant_cat
    ON consent_record(tenant_id, data_category, purpose)
    WHERE valid_until IS NULL;
