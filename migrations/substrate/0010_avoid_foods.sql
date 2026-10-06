-- 0010: foods-to-avoid as its own profile field, distinct from
-- preferences (user direction 2026-10-06: "the preferences and
-- allergies/foods to avoid sections need to be distinctly separate
-- otherwise we breed confusion").
--
-- Previously one free-text list fed dietary_preferences, so "no
-- cilantro" became a "prefers no cilantro" ranking BOOST — the
-- opposite of intent. avoid_foods derives "avoids X" (hard exclusion,
-- like allergens); dietary_preferences keeps "prefers X" (soft boost).

ALTER TABLE intake_profile_v2
    ADD COLUMN avoid_foods TEXT NOT NULL DEFAULT '[]'
        CHECK (json_valid(avoid_foods));
