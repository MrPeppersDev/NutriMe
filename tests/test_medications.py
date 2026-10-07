"""Drug–nutrient interaction rails (#46 / sweep #10 §6): registry + wiring."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.intake.store import IntakeProfile, save_member_profile
from nutrime.medications import (
    AWARENESS,
    CONSISTENCY,
    EXCLUSION,
    classify,
    household_medication_rails,
    medication_rails,
)


@pytest.fixture
def app(tmp_path: Path):
    application = initialize(data_dir=tmp_path)
    yield application
    application.substrate.close()
    application.operational.close()


def _profile(**kw) -> IntakeProfile:
    base = dict(year_of_birth=1988, sex_assigned_at_birth="female", life_stage="adult")
    base.update(kw)
    return IntakeProfile(**base)


class TestClassify:
    def test_statin_grapefruit_is_plain_avoidance(self) -> None:
        # #46 correction: no "dose-timing per prescriber" alternative —
        # grapefruit's effect outlasts any dosing interval (Bailey 2013).
        info = classify("simvastatin 20mg")
        assert info is not None
        assert info.kind == EXCLUSION
        assert "grapefruit" in info.avoid_terms
        assert "timing" not in info.plan_note.lower()

    def test_low_interaction_statins_not_excluded(self) -> None:
        # Pravastatin/rosuvastatin aren't CYP3A4-cleared.
        for text in ("pravastatin", "rosuvastatin 10mg", "Crestor"):
            info = classify(text)
            assert info is not None, text
            assert info.kind == AWARENESS, text
            assert info.avoid_terms == (), text

    def test_erythromycin_grapefruit_high_risk(self) -> None:
        # #46 correction: base table said "minimal"; Bailey 2013 rates it
        # high (torsade de pointes).
        for text in ("erythromycin", "clarithromycin"):
            info = classify(text)
            assert info is not None, text
            assert info.kind == EXCLUSION, text
            assert "grapefruit" in info.avoid_terms, text

    def test_maoi_hard_exclusion(self) -> None:
        info = classify("phenelzine")
        assert info is not None
        assert info.kind == EXCLUSION
        for term in ("aged cheese", "soy sauce", "sauerkraut", "fava bean"):
            assert term in info.avoid_terms

    def test_linezolid_is_awareness_not_exclusion(self) -> None:
        # #46 correction: label says avoid LARGE amounts — a hard gate
        # is too strict.
        info = classify("linezolid")
        assert info is not None
        assert info.kind == AWARENESS
        assert info.avoid_terms == ()

    def test_selegiline_patch_above_general_maoi(self) -> None:
        patch = classify("selegiline transdermal patch 6mg")
        oral = classify("selegiline")
        assert patch is not None and patch.kind == AWARENESS
        assert oral is not None and oral.kind == EXCLUSION

    def test_alcohol_hard_stops_added(self) -> None:
        # #46 missing-HIGH rows: metronidazole, tinidazole, disulfiram,
        # acitretin.
        for text in ("metronidazole", "tinidazole", "disulfiram", "acitretin"):
            info = classify(text)
            assert info is not None, text
            assert info.kind == EXCLUSION, text
            assert "alcohol" in info.avoid_terms, text
            assert "wine" in info.avoid_terms, text

    def test_disulfiram_reaches_hidden_alcohol(self) -> None:
        # Label: reactions from alcohol "in sauces, vinegars".
        info = classify("Antabuse")
        assert info is not None
        assert "vinegar" in info.avoid_terms
        assert "vanilla extract" in info.avoid_terms

    def test_metronidazole_does_not_exclude_vinegar(self) -> None:
        info = classify("metronidazole")
        assert info is not None
        assert "vinegar" not in info.avoid_terms

    def test_licorice_keyed_to_digoxin_and_k_losing_diuretics(self) -> None:
        # #46 correction: spironolactone COUNTERS licorice; the risk is
        # digoxin + potassium-losing diuretics.
        for text in ("digoxin", "furosemide", "hydrochlorothiazide"):
            info = classify(text)
            assert info is not None, text
            assert "licorice" in info.avoid_terms, text
        spiro = classify("spironolactone")
        assert spiro is not None
        assert "licorice" not in spiro.avoid_terms

    def test_potassium_rails_cover_salt_substitutes_and_supplements(self) -> None:
        # #46 missing-HIGH: supplement warning, not just salt substitutes.
        for text in ("lisinopril", "losartan", "spironolactone"):
            info = classify(text)
            assert info is not None, text
            assert "salt substitute" in info.avoid_terms, text
            assert "supplement" in info.note.lower(), text

    def test_warfarin_is_consistency_not_exclusion(self) -> None:
        info = classify("warfarin")
        assert info is not None
        assert info.kind == CONSISTENCY
        # Leafy greens are NOT excluded — consistency is the rail.
        assert "spinach" not in info.avoid_terms
        assert "kale" not in info.avoid_terms
        assert info.avoid_terms == ("natto",)
        assert "consistent" in info.plan_note.lower()

    def test_levothyroxine_ppi_is_monitoring_not_spacing(self) -> None:
        # #46 correction: "4 h from PPI" has no effect — label says
        # monitor TSH.
        info = classify("levothyroxine")
        assert info is not None
        assert info.kind == AWARENESS
        assert "monitor" in info.note.lower()

    def test_atelvia_exception_noted(self) -> None:
        # #46 correction: delayed-release risedronate is taken AFTER
        # breakfast.
        info = classify("alendronate")
        assert info is not None
        assert "after" in info.note.lower()

    def test_fluoroquinolone_window_is_per_drug(self) -> None:
        # #46 correction: one "2h/6h" rule doesn't fit moxifloxacin.
        info = classify("moxifloxacin")
        assert info is not None
        assert "4 h" in info.note or "4 h" in info.note.replace(" ", " ")

    def test_raltegravir_no_antacid_coadministration(self) -> None:
        # #46 correction: separating doses isn't enough.
        info = classify("raltegravir")
        assert info is not None
        assert "isn't enough" in info.note or "not enough" in info.note

    def test_methotrexate_split_by_indication(self) -> None:
        # #46 correction: folate guidance differs for RA vs oncology.
        info = classify("methotrexate")
        assert info is not None
        assert info.kind == AWARENESS
        assert "cancer" in info.note.lower()
        assert "rheumatoid" in info.note.lower()

    def test_oral_semaglutide_rule_present(self) -> None:
        # #46 correction: Rybelsus empty-stomach/30-min rule was missing.
        info = classify("Rybelsus")
        assert info is not None
        assert "30" in info.note

    def test_phenytoin_folate_warning(self) -> None:
        info = classify("phenytoin")
        assert info is not None
        assert "folic" in info.note.lower()

    def test_grapefruit_class_transplant_oncology(self) -> None:
        for text in ("tacrolimus", "cyclosporine", "nilotinib", "ibrutinib"):
            info = classify(text)
            assert info is not None, text
            assert info.kind == EXCLUSION, text
            assert "grapefruit" in info.avoid_terms, text

    def test_unknown_medication_returns_none(self) -> None:
        # Unlike conditions, unknown drugs don't gate: most medications
        # have no food interaction (alert-fatigue §6.4).
        assert classify("amoxicillin") is None
        assert classify("vitamin D") is None
        assert classify("") is None

    def test_no_aspirin_row(self) -> None:
        # #46: the aspirin + vitamin C/folate row was unsourceable — dropped.
        assert classify("aspirin") is None

    def test_brand_names_match(self) -> None:
        for brand, canonical_fragment in (
            ("Coumadin", "warfarin"),
            ("Lipitor", "statin"),
            ("Flagyl", "metronidazole"),
            ("Ozempic", "GLP-1"),
            ("Synthroid", "levothyroxine"),
        ):
            info = classify(brand)
            assert info is not None, brand
            assert canonical_fragment.lower() in info.canonical.lower(), brand

    def test_case_insensitive(self) -> None:
        assert classify("WARFARIN") is not None
        assert classify("Simvastatin") is not None


class TestRailsAggregation:
    def test_empty_disclosures_empty_rails(self) -> None:
        rails = medication_rails([])
        assert rails.avoid_terms == frozenset()
        assert rails.plan_notes == ()
        assert rails.medications == ()

    def test_union_and_dedup(self) -> None:
        rails = medication_rails(
            ["simvastatin", "atorvastatin", "warfarin", "ibuprofen"]
        )
        # Two statins collapse to one canonical entry.
        assert len(rails.medications) == 2
        assert "grapefruit" in rails.avoid_terms
        assert "natto" in rails.avoid_terms
        assert rails.unrecognized == ("ibuprofen",)

    def test_plan_notes_never_name_the_drug(self) -> None:
        # MEDICATIONS is not in the planner's PHI envelope: the note that
        # rides household_note must be mechanism-level only.
        from nutrime.medications import _REGISTRY

        for _, info in _REGISTRY:
            if not info.plan_note:
                continue
            # The canonical name's distinctive words must not appear in
            # the plan note (generic words like "inhibitor" aside, the
            # check is on the drug-ish tokens).
            for token in info.canonical.lower().split():
                if token in ("medication", "antibiotic", "inhibitor",
                             "receptor", "agonist", "diuretic", "oral",
                             "(minimal", "grapefruit", "interaction)",
                             "/", "patch", "(long-term)", "diuretic)"):
                    continue
                assert token.strip("()/") not in info.plan_note.lower(), (
                    info.canonical, info.plan_note
                )


class TestHouseholdRails:
    def test_household_aggregates_members(self, app) -> None:
        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(medications=("warfarin",)),
        )
        rails = household_medication_rails(app.substrate, app.tenant_id)
        assert "natto" in rails.avoid_terms
        assert any("vitamin K" in n for n in rails.plan_notes)

    def test_no_medications_no_rails(self, app) -> None:
        save_member_profile(
            app.substrate, app.tenant_id, None, _profile(),
        )
        rails = household_medication_rails(app.substrate, app.tenant_id)
        assert rails.avoid_terms == frozenset()


class TestPlanAndSearchWiring:
    def test_plan_base_filters_include_medication_exclusions(self, app) -> None:
        from nutrime.plans.service import plan_base_filters

        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(medications=("simvastatin", "phenelzine")),
        )
        filters, applied = plan_base_filters(app, use_inventory=False)
        assert "grapefruit" in filters.exclude_ingredients
        assert "aged cheese" in filters.exclude_ingredients
        assert any("medication rails" in a for a in applied)

    def test_awareness_only_meds_add_no_filter_line(self, app) -> None:
        from nutrime.plans.service import plan_base_filters

        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(medications=("levothyroxine",)),
        )
        filters, applied = plan_base_filters(app, use_inventory=False)
        assert not any("medication rails" in a for a in applied)


class TestSearchIntegration:
    def test_statin_excludes_grapefruit_recipes(self, tmp_path: Path) -> None:
        from nutrime.recipes.frontmatter import (
            Attribution,
            Yields,
            build_recipe_frontmatter,
        )
        from nutrime.recipes.ids import new_recipe_id
        from nutrime.recipes.search import SearchFilters, search
        from nutrime.recipes.store import RecipeVault

        vault = RecipeVault(tmp_path)
        vault.ensure()

        def _write(title, ingredients):
            rid = new_recipe_id()
            fm = build_recipe_frontmatter(
                recipe_id=rid, title=title,
                attribution=Attribution(
                    source_name="t", source_url="https://e.com/r",
                    source_license="t",
                    ingested_at="2026-10-08T00:00:00Z",
                    ingestion_method="test_v1",
                ),
                source_status="live",
                last_source_check_at="2026-10-08T00:00:00Z",
                yields=Yields(count=2), top_allergens_present=[],
            )
            body = (
                "-- Ingredients\n\n"
                + "\n".join(f"@{i}{{}}" for i in ingredients)
                + "\n\n-- Instructions\n\nCook it well.\n"
            )
            vault.write(rid, fm, body)
            return rid

        citrus = _write("Grapefruit Salad", ["grapefruit", "arugula"])
        safe = _write("Chicken Stew", ["chicken", "carrot", "stock"])
        rails = medication_rails(["atorvastatin"])
        results = search(
            vault, SearchFilters(exclude_ingredients=rails.avoid_terms)
        )
        ids = [r.recipe_id for r in results]
        assert safe in ids
        assert citrus not in ids
