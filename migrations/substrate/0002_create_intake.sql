-- Sub-commit 2.1: first-run baseline intake.
-- Per stage3-plan.md § "Component verification log" (verified 2026-06-30) the
-- MVP screener trio (PHQ-2 + GAD-2 + Hunger Vital Sign) ships with substrate
-- values unchanged. Raw item responses land here, scoring is computed in
-- Python; storing normalized keeps future v0.2 additions (PSQI, AUDIT-C)
-- schema-neutral.

CREATE TABLE intake_profile (
    tenant_id             TEXT PRIMARY KEY
                            REFERENCES tenant(id) ON DELETE CASCADE,
    year_of_birth         INTEGER NOT NULL
                            CHECK (year_of_birth BETWEEN 1900 AND 2100),
    sex_assigned_at_birth TEXT NOT NULL
                            CHECK (sex_assigned_at_birth IN
                                   ('female', 'male', 'intersex',
                                    'prefer_not_to_say')),
    height_cm             INTEGER
                            CHECK (height_cm IS NULL
                                   OR height_cm BETWEEN 30 AND 275),
    weight_kg             REAL
                            CHECK (weight_kg IS NULL
                                   OR weight_kg BETWEEN 1 AND 500),
    life_stage            TEXT NOT NULL
                            CHECK (life_stage IN
                                   ('infant', 'child', 'adolescent',
                                    'adult', 'pregnant', 'lactating',
                                    'older_adult')),
    dietary_preferences   TEXT NOT NULL DEFAULT '[]'
                            CHECK (json_valid(dietary_preferences)),
    allergens             TEXT NOT NULL DEFAULT '[]'
                            CHECK (json_valid(allergens)),
    created_at            TEXT NOT NULL,
    updated_at            TEXT NOT NULL
);

CREATE TABLE intake_screener_response (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id             TEXT NOT NULL
                            REFERENCES tenant(id) ON DELETE CASCADE,
    instrument_id         TEXT NOT NULL,
    instrument_version    TEXT NOT NULL,
    item_id               TEXT NOT NULL,
    response_value        INTEGER NOT NULL,
    administered_at       TEXT NOT NULL,
    UNIQUE (tenant_id, instrument_id, instrument_version,
            item_id, administered_at)
);

CREATE INDEX idx_intake_screener_response_tenant_instrument
    ON intake_screener_response (tenant_id, instrument_id, administered_at);
