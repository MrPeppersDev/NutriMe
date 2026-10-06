-- 0008: per-member settings (C5 Q5.2 notification switches; key/value so
-- later per-member preferences need no new table).
CREATE TABLE IF NOT EXISTS member_setting (
    tenant_id  TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    member_id  TEXT NOT NULL REFERENCES member(id),
    key        TEXT NOT NULL,
    value      TEXT NOT NULL,
    PRIMARY KEY (tenant_id, member_id, key)
);
