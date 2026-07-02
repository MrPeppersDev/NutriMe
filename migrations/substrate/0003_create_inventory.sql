-- Sub-commit 2.2: inventory intake (pantry / fridge / freezer / countertop).
--
-- Zero PHI per constitutional-rules.md Rule 3 inventory-is-not-logging
-- distinction:
--   Logging (out):    tracking what you ate; backward-looking accounting
--   Inventory (in):   knowing what's on hand to use; forward-looking utility
-- The user never opens a "what did I eat today" form. Inventory captures the
-- state of the kitchen shelves so downstream meal planning + shopping list
-- construction can prefer already-owned ingredients + reduce waste.
--
-- Per intake-pattern.md § "Quantity precision: loose by default", quantity +
-- unit are optional and paired — "I have rice" is enough until a specific
-- recipe or shopping list forces just-in-time precision.

CREATE TABLE inventory_item (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id       TEXT NOT NULL
                      REFERENCES tenant(id) ON DELETE CASCADE,
    name            TEXT NOT NULL
                      CHECK (length(trim(name)) > 0),
    location        TEXT NOT NULL
                      CHECK (location IN
                             ('pantry', 'fridge', 'freezer', 'countertop')),
    quantity        REAL
                      CHECK (quantity IS NULL OR quantity >= 0),
    unit            TEXT,
    best_by_date    TEXT
                      CHECK (best_by_date IS NULL
                             OR best_by_date GLOB
                                '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
    notes           TEXT,
    added_at        TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    CHECK ((quantity IS NULL) = (unit IS NULL))
);

CREATE INDEX idx_inventory_item_tenant_location
    ON inventory_item (tenant_id, location);
