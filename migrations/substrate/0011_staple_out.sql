-- 0011: staples the household is OUT of (user direction 2026-10-06:
-- staples are assumed on hand, "but like anything else non-perishable
-- you should be able to select that you do not have something").
--
-- Pantry-first ranking assumes ~50 staples (salt, oil, flour...) are
-- always available so they never count as "missing". A row here breaks
-- that assumption for one staple: it counts missing again until the
-- household restocks (row deleted via toggle or by adding the item to
-- inventory). Household-level — one kitchen, one staple shelf.

CREATE TABLE IF NOT EXISTS staple_out (
    tenant_id  TEXT NOT NULL REFERENCES tenant(id) ON DELETE CASCADE,
    name       TEXT NOT NULL,                -- canonical staple name
    marked_at  TEXT NOT NULL,
    PRIMARY KEY (tenant_id, name)
);
