-- Per schema.md F9 Q3: minimal tenant lifecycle table.
-- FK target for tenant_id columns on substrate + operational tables (added in
-- subsequent migrations as those tables land per Stage 6 sub-commits).
-- Per S1 Q1.4 all timestamps are ISO 8601 UTC.

CREATE TABLE tenant (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'suspended', 'archived')),
    owner_user_id   TEXT
);
