-- 0009: disclosed health conditions on the member profile (sweep #10,
-- clinical condition gating — planned in research, unbuilt until now).
--
-- Free-text disclosures, JSON list like dietary_preferences. The gating
-- behavior (refuse / gate / proceed-with-disclaimer) is NOT stored: it is
-- computed by the deterministic registry in nutrime/conditions.py at every
-- use, so a registry fix applies to already-disclosed conditions.

ALTER TABLE intake_profile_v2
    ADD COLUMN conditions TEXT NOT NULL DEFAULT '[]'
        CHECK (json_valid(conditions));
