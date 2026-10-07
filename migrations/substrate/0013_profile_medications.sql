-- 0013: disclosed medications on the member profile (sweep #10 §6,
-- drug–nutrient interactions — issue #46 second half).
--
-- Free-text disclosures, JSON list like conditions. The interaction
-- rails (food exclusions / consistency notes / timing guidance) are NOT
-- stored: they are computed by the deterministic registry in
-- nutrime/medications.py at every use, so a registry correction applies
-- to already-disclosed medications. PhiCategory.MEDICATIONS exists for
-- this field; medication names never cross into LLM prompts — only the
-- mechanism-level food rails do.

ALTER TABLE intake_profile_v2
    ADD COLUMN medications TEXT NOT NULL DEFAULT '[]'
        CHECK (json_valid(medications));
