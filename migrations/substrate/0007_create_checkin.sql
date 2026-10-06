-- 0007: periodic check-ins (intake-pattern.md Mode 2; genesis: "periodic
-- check-ins that are 5 to 15 minutes that revise the initial clinical
-- data"). Per member.
--
-- checkin: one row per completed (or skipped) check-in, with a JSON
-- summary of what changed — the household can see how their baseline
-- moved over time.
-- checkin_schedule: per-member cadence + snooze. Absent row = defaults
-- (28 days; 14 during pregnancy / breastfeeding).
-- intake_profile_history: every profile revision's PREVIOUS state, so a
-- revision never silently overwrites the record (append-only).

CREATE TABLE IF NOT EXISTS checkin (
    id             TEXT PRIMARY KEY,                -- chk-<uuid7>
    tenant_id      TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    member_id      TEXT NOT NULL REFERENCES member(id),
    completed_at   TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('completed', 'skipped')),
    summary        TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(summary))
);

CREATE INDEX IF NOT EXISTS idx_checkin_member
    ON checkin (tenant_id, member_id, completed_at);

CREATE TABLE IF NOT EXISTS checkin_schedule (
    tenant_id      TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    member_id      TEXT NOT NULL REFERENCES member(id),
    interval_days  INTEGER CHECK (interval_days IS NULL OR interval_days BETWEEN 7 AND 180),
    snoozed_until  TEXT,
    PRIMARY KEY (tenant_id, member_id)
);

CREATE TABLE IF NOT EXISTS intake_profile_history (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id             TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    member_id             TEXT NOT NULL REFERENCES member(id),
    replaced_at           TEXT NOT NULL,
    profile               TEXT NOT NULL CHECK (json_valid(profile))
);
