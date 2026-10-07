-- 0012: canonical matching name for inventory items.
--
-- The household names items how they think of them ("chives with chive
-- flowers", "EVOO", "kewpie mayo"); recipes ask for the generic food.
-- match_name stores the generic recipe-facing name, written ONCE at
-- intake time (the bulk-paste local-model tier proposes it, the user
-- reviews it) — matching stays deterministic at search/grocery time.
-- NULL = the item name already is the generic name (the common case).

ALTER TABLE inventory_item ADD COLUMN match_name TEXT;
