"""Clinical condition gating (sweep #10): registry, derivation, enforcement."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.conditions import (
    DISCLAIMER,
    GATE,
    REFUSE,
    classify,
    household_gates,
)
from nutrime.intake.store import IntakeProfile, save_member_profile
from nutrime.knowledge.derivation import sync_from_intake
from nutrime.knowledge.store import list_atoms
from nutrime.members import add_member


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
    def test_refuse_conditions(self) -> None:
        for text in (
            "anorexia recovery",
            "type 1 diabetes",
            "T1D",
            "stage 4 CKD",
            "on dialysis",
            "currently undergoing chemotherapy",
            "recent bariatric surgery",
        ):
            assert classify(text).behavior == REFUSE, text

    def test_t1d_with_coordination_gates_instead(self) -> None:
        info = classify("type 1 diabetes, coordinated with my endocrinologist")
        assert info.behavior == GATE
        assert "carbohydrate" in info.plan_note

    def test_gate_conditions(self) -> None:
        for text in ("celiac disease", "gestational diabetes", "early kidney disease"):
            assert classify(text).behavior == GATE, text

    def test_disclaimer_conditions(self) -> None:
        for text in (
            "type 2 diabetes",
            "prediabetes",
            "high blood pressure",
            "GERD / reflux",
            "gout",
            "PCOS",
            "hypothyroidism",
        ):
            assert classify(text).behavior == DISCLAIMER, text

    def test_unrecognized_fails_closed_to_gate(self) -> None:
        # #58: a clinical layer must not hand unknown conditions the
        # least restrictive behavior. Unrecognized → gate (surfaced on
        # every plan + refer-out), not disclaimer.
        info = classify("Ehlers-Danlos syndrome")
        assert info.behavior == GATE
        assert info.canonical == "ehlers-danlos syndrome"
        assert info.specialties  # always a refer-out
        assert info.plan_note  # surfaced to the planner, not silent

    def test_sweep10_refuse_tier_table(self) -> None:
        # Table-driven from the #58 probe table + sweep 10 scope.md —
        # every row here was falling through to disclaimer.
        for text in (
            "diabulimia",
            "OSFED",
            "type 1 diabetes, no endocrinologist",
            "type 1 diabetes but I don't have an endocrinologist",
            "gastric bypass",
            "sleeve gastrectomy",
            "kidney disease stage IV",
            "CKD stage V",
            "decompensated cirrhosis",
            "PKU",
            "phenylketonuria",
            "cystic fibrosis",
            "acute kidney injury",
            "AKI",
            "short bowel syndrome",
            "ketogenic diet for epilepsy",
            "palliative care",
            "cancer cachexia",
            "hyperemesis gravidarum",
            "brittle diabetes",
            "failure to thrive",
        ):
            assert classify(text).behavior == REFUSE, text

    def test_sweep10_gate_tier_table(self) -> None:
        for text in (
            "kidney transplant",
            "renal transplant on tacrolimus",
            "gastric bypass, stable maintenance",
            "bariatric surgery years ago, stable",
        ):
            assert classify(text).behavior == GATE, text

    def test_transplant_gate_excludes_grapefruit(self) -> None:
        info = classify("kidney transplant")
        assert "grapefruit" in info.plan_note

    def test_coordination_still_gates_when_affirmative(self) -> None:
        # The negation fix must not break the affirmative path.
        for text in (
            "type 1 diabetes, coordinated with my endocrinologist",
            "T1D managed with my care team",
        ):
            assert classify(text).behavior == GATE, text

    def test_case_insensitive(self) -> None:
        assert classify("TYPE 2 DIABETES").behavior == DISCLAIMER
        assert classify("Celiac").behavior == GATE

    # -- pediatric enumeration (#46 / sweep #10 §2) -------------------------

    def test_pediatric_refuse_tier_table(self) -> None:
        for text in (
            "my son has leukemia",
            "childhood cancer, in treatment",
            "biliary atresia",
            "Alagille syndrome",
            "pediatric liver disease",
            "my daughter's Crohn's disease",
            "pediatric IBD",
            "nephrotic syndrome",
            "my child has kidney disease",
            "EoE",
            "eosinophilic esophagitis",
            # already-covered pediatric rows keep refusing via the
            # adult patterns:
            "my child has type 1 diabetes",
            "ARFID",
            "pediatric anorexia",
            "PKU",
            "MSUD",
            "pediatric cystic fibrosis",
            "short bowel syndrome",
            "ketogenic diet for my son's epilepsy",
        ):
            assert classify(text).behavior == REFUSE, text

    def test_pediatric_coordination_gates(self) -> None:
        # Refuse-without / gate-with rows flip on coordination wording,
        # same pattern as adult T1D.
        for text in (
            "my daughter's Crohn's, coordinated with her GI team",
            "pediatric IBD, managed with pediatric gastro",
            "my child's kidney disease, nephrologist coordinating",
            "eosinophilic esophagitis, on elimination diet with GI team",
            "failure to thrive, pediatric RDN coordinating",
            "pediatric T1D coordinated with endocrinologist",
        ):
            assert classify(text).behavior == GATE, text

    def test_pediatric_gate_tier_table(self) -> None:
        for text in (
            "my kid has type 2 diabetes",
            "cow's milk protein allergy",
            "CMPA",
            "FPIES",
            "FPIAP",
            "RED-S",
            "female athlete triad",
            "cleft palate feeding",
            "dysphagia, IDDSI level 5",
        ):
            assert classify(text).behavior == GATE, text

    def test_pediatric_t2d_gates_while_adult_disclaims(self) -> None:
        # The pediatric row must win over the general t2d pattern.
        assert classify("my kid has type 2 diabetes").behavior == GATE
        assert classify("type 2 diabetes").behavior == DISCLAIMER

    def test_pediatric_disclaimer_tier_table(self) -> None:
        # Resolved to disclaimer by synthesis.md Tension #9
        # (bounded-role principle).
        for text in (
            "childhood obesity",
            "my son is overweight",
            "autism food selectivity",
            "autistic, sensory issues with food",
            "picky eater",
            "lactose intolerance",
            "fructose malabsorption",
        ):
            assert classify(text).behavior == DISCLAIMER, text

    def test_pediatric_obesity_no_weight_framing(self) -> None:
        # AAP 2023 / Rule 3: family meals, never weight language
        # directed at the child.
        info = classify("childhood obesity")
        assert "NOT" in info.plan_note
        assert "weight" in info.plan_note

    def test_picky_eating_satter_framing(self) -> None:
        info = classify("picky eater")
        assert "family-style" in info.plan_note

    def test_fpies_enforces_trigger_exclusion(self) -> None:
        info = classify("FPIES")
        assert "exclude" in info.plan_note.lower()

    def test_adult_rows_unchanged_by_pediatric_entries(self) -> None:
        # Adult defaults must not be shadowed by the new rows.
        assert classify("Crohn's disease").behavior == DISCLAIMER
        assert classify("IBS").behavior == DISCLAIMER
        assert classify("early kidney disease").behavior == GATE
        assert classify("stage 4 CKD").behavior == REFUSE
        assert classify("kidney transplant").behavior == GATE

    def test_specialties_mapped_per_scope_doc(self) -> None:
        assert any("endocrinolog" in s for s in classify("type 2 diabetes").specialties)
        assert any("nephrolog" in s for s in classify("dialysis").specialties)
        assert any("gastroenterolog" in s for s in classify("celiac").specialties)


class TestHouseholdGates:
    def test_no_conditions_no_gates(self, app) -> None:
        save_member_profile(app.substrate, app.tenant_id, None, _profile())
        decision = household_gates(app.substrate, app.tenant_id)
        assert not decision.refused
        assert decision.plan_notes == ()

    def test_any_member_refusal_refuses_household(self, app) -> None:
        save_member_profile(app.substrate, app.tenant_id, None, _profile())
        other = add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(
            app.substrate, app.tenant_id, other.id,
            _profile(conditions=("type 1 diabetes",)),
        )
        decision = household_gates(app.substrate, app.tenant_id)
        assert decision.refused
        msg = decision.refusal_message()
        assert "endocrinolog" in msg
        assert "search" in msg.lower()  # the rest of the app still works

    def test_gate_and_disclaimer_notes_combine(self, app) -> None:
        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("celiac disease", "high blood pressure")),
        )
        decision = household_gates(app.substrate, app.tenant_id)
        assert not decision.refused
        joined = " ".join(decision.plan_notes)
        assert "gluten" in joined
        assert "sodium" in joined

    def test_duplicate_disclosures_counted_once(self, app) -> None:
        save_member_profile(
            app.substrate, app.tenant_id, None, _profile(conditions=("gout",))
        )
        other = add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(
            app.substrate, app.tenant_id, other.id, _profile(conditions=("gout",))
        )
        decision = household_gates(app.substrate, app.tenant_id)
        assert len(decision.conditions) == 1

    def test_archived_member_conditions_ignored(self, app) -> None:
        from nutrime.members import archive_member

        other = add_member(app.substrate, app.tenant_id, "Sam")
        save_member_profile(
            app.substrate, app.tenant_id, other.id,
            _profile(conditions=("on dialysis",)),
        )
        assert household_gates(app.substrate, app.tenant_id).refused
        archive_member(app.substrate, app.tenant_id, other.id)
        assert not household_gates(app.substrate, app.tenant_id).refused


class TestDerivation:
    def test_condition_atoms_emitted_and_rule1_sees_them(self, app) -> None:
        from nutrime.surface_rules import household_sensitivities

        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("type 2 diabetes",)),
        )
        sync_from_intake(app.substrate, app.tenant_id)
        atoms = [
            a for a in list_atoms(
                app.substrate, app.tenant_id, atom_type="clinical_disclosure"
            )
            if a.payload.get("disclosure_type") == "condition"
        ]
        assert len(atoms) == 1
        assert atoms[0].payload["disclosure_text"] == "type 2 diabetes"
        sens = household_sensitivities(app.substrate, app.tenant_id)
        assert "condition:type 2 diabetes" in sens

    def test_removed_condition_retracted(self, app) -> None:
        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("gout",)),
        )
        sync_from_intake(app.substrate, app.tenant_id)
        save_member_profile(app.substrate, app.tenant_id, None, _profile())
        sync_from_intake(app.substrate, app.tenant_id)
        live = [
            a for a in list_atoms(
                app.substrate, app.tenant_id, atom_type="clinical_disclosure"
            )
            if a.payload.get("disclosure_type") == "condition"
        ]
        assert live == []

    def test_idempotent(self, app) -> None:
        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("celiac disease",)),
        )
        sync_from_intake(app.substrate, app.tenant_id)
        sync_from_intake(app.substrate, app.tenant_id)
        atoms = [
            a for a in list_atoms(
                app.substrate, app.tenant_id, atom_type="clinical_disclosure"
            )
            if a.payload.get("disclosure_type") == "condition"
        ]
        assert len(atoms) == 1


class TestPlanEnforcement:
    def _spec_filters(self, app):
        from nutrime.plans.assemble import PlanSpec
        from nutrime.plans.service import plan_base_filters

        filters, applied = plan_base_filters(app)
        return PlanSpec(days=1, slots=("dinner",)), filters, applied

    def test_refusal_blocks_before_any_llm_call(self, app) -> None:
        from nutrime.plans.service import PlanRefusedError, generate_and_store

        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("type 1 diabetes",)),
        )

        class ExplodingClient:
            def complete(self, request):  # pragma: no cover
                raise AssertionError("LLM must not be reached on refusal")

        spec, filters, applied = self._spec_filters(app)
        with pytest.raises(PlanRefusedError) as err:
            generate_and_store(
                app, ExplodingClient(), spec, filters, applied
            )
        assert "endocrinolog" in str(err.value)

    def test_refusal_is_audited(self, app) -> None:
        from nutrime.plans.service import PlanRefusedError, generate_and_store

        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("on dialysis",)),
        )
        spec, filters, applied = self._spec_filters(app)
        with pytest.raises(PlanRefusedError):
            generate_and_store(app, object(), spec, filters, applied)
        row = app.operational.execute(
            "SELECT payload FROM op_event_log WHERE event_subkind = 'condition_gate'"
            " ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        assert row is not None
        assert "severe chronic kidney disease" in row[0]

    def test_gate_notes_reach_the_prompt(self, app) -> None:
        from nutrime.plans.assemble import build_prompt
        from nutrime.conditions import household_gates
        from dataclasses import replace as dc_replace
        from nutrime.plans.assemble import PlanSpec

        save_member_profile(
            app.substrate, app.tenant_id, None,
            _profile(conditions=("gestational diabetes",)),
        )
        gates = household_gates(app.substrate, app.tenant_id)
        spec = PlanSpec(days=1, slots=("dinner",))
        spec = dc_replace(
            spec, household_note="2 servings; " + "; ".join(gates.plan_notes)
        )
        prompt = build_prompt(1, "dinner", [], spec)
        assert "gestational diabetes" in prompt or "carbohydrate" in prompt
