-- 0006: household members (issue #29, direction reset 2026-10-06 item 3).
--
-- One tenant = one household; a member is a person in it. Members share
-- one device for now (picker, not auth). Personal state — intake profile,
-- screener responses, feedback atoms, consent decisions — is keyed per
-- member; corpus, inventory and plans stay household-shared.
--
-- Members are archived, never deleted, so atoms keep a resolvable
-- subject. The first member and the legacy single-profile migration are
-- written by nutrime.members.bootstrap_default_member (ids are uuid7,
-- generated in Python).

CREATE TABLE IF NOT EXISTS member (
    id            TEXT PRIMARY KEY,               -- mem-<uuid7>
    tenant_id     TEXT NOT NULL
                    REFERENCES tenant(id) ON DELETE CASCADE,
    display_name  TEXT NOT NULL
                    CHECK (length(trim(display_name)) BETWEEN 1 AND 60),
    status        TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'archived')),
    created_at    TEXT NOT NULL,
    archived_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_member_tenant ON member (tenant_id, status);

-- Per-member profile. Same columns and checks as intake_profile (0002),
-- re-keyed (tenant_id, member_id). The legacy table stays readable until
-- every caller is member-aware; nothing writes to it after this point.
CREATE TABLE IF NOT EXISTS intake_profile_v2 (
    tenant_id             TEXT NOT NULL
                            REFERENCES tenant(id) ON DELETE CASCADE,
    member_id             TEXT NOT NULL
                            REFERENCES member(id),
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
    updated_at            TEXT NOT NULL,
    PRIMARY KEY (tenant_id, member_id)
);

ALTER TABLE intake_screener_response ADD COLUMN member_id TEXT
    REFERENCES member(id);
