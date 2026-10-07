"""Pre-surface constitutional rules (issue #30) — L1 harness, surface side.

Same discipline as tests/test_rules_adversarial.py: a corpus the layer
MUST block, a corpus it MUST annotate, and a benign corpus it MUST pass
untouched. New bypass → add it here first (red), then harden (green).

Families:
  R3  calorie / macro / food logging prompts
  R4  LLM-written recipes
  H   harmful: cure claims, ED content, purging, restriction, fasting
  R7  health claims without a Tier 1-3 basis
  R1  clinical-adjacent text needing an adjacent consult-professional line
  O   obfuscated variants of the above
"""

from pathlib import Path

import pytest

from nutrime.surface_rules import (
    CONSULT_LINE,
    SurfaceContent,
    SurfaceGuard,
    default_surface_guard,
    household_sensitivities,
)

GUARD = default_surface_guard()


def _check(text: str, **kw):
    return GUARD.check(SurfaceContent(surface="plan_reason", text=text, **kw))


BLOCKED = [
    # R3
    "Log what you ate today so we can fine-tune tomorrow.",
    "Remember to track your calories after dinner.",
    "Counting macros? This fits your plan.",
    "You have 600 calories remaining for today.",
    "Add it to your food diary.",
    # R4
    "Here's a recipe: brown the beef, add stock, simmer.",
    "Ingredients: 2 cups rice, 1 onion. Instructions: fry the onion, add rice.",
    "2 cups flour\n1 tsp salt\n3 tbsp butter\n1. Mix everything\n2. Bake 20 minutes",
    # H
    "Turmeric cures cancer, so this curry is perfect.",
    "This diet reverses diabetes in weeks.",
    "Great thinspo dinner!",
    "If you overeat, purging afterwards resets things.",
    "Skip meals to lose weight faster this week.",
    "Aim for 800 calories a day this week.",
    "Try to eat less than 900 calories while on this plan.",
    "A water fast for 5 days resets your gut.",
    # R7 (no evidence attached)
    "Salmon lowers your blood pressure.",
    "Garlic helps you fight inflammation naturally.",
    "This anti-inflammatory bowl is ideal.",
    "A detox soup to flush out toxins.",
    "Ginger boosts your immune system.",
    "Green tea speeds up your metabolism.",
    "Oats reduce the risk of heart disease.",
    "Spinach helps you lose weight.",
    # O
    "Ｌｏｇ ｗｈａｔ ｙｏｕ ａｔｅ today.",
    "Salmon low​ers your blood pressure.",
    "Turmeric   CURES   cancer.",
]

ANNOTATED = [
    "A gentle, low-sodium option given the kidney disease on file.",
    "Folate-rich greens are a common pick during pregnancy.",
    "Easy on the stomach if you're managing IBS.",
    "Grapefruit can interact with some medications.",
    "Lighter dinner for weight loss goals.",
    "Low in added sugar, which matters with diabetes.",
]

BENIGN = [
    "Quick weeknight chicken that uses up the spinach you have.",
    "Light, bright and on the table in 30 minutes.",
    "A hearty stew for a cold evening; leftovers freeze well.",
    "Kid-friendly and mild, with an optional chili oil on the side.",
    "Uses the kidney beans in the pantry.",
    "Steak and kidney pie — a slow Sunday project.",
    "Lemon cuts through the richness of the pork.",
    "Only 450 calories per serving and big on flavour.",
    "Reduce the heat and let the sauce thicken.",
    "Pick something new: you haven't cooked Ethiopian food yet.",
    "1. Fast 2. Uses leftovers 3. Mild enough for everyone",
    "A heart-healthy pick from the NHLBI collection.",
    "High in protein and fibre, low effort.",
    "",
]


@pytest.mark.parametrize("text", BLOCKED)
def test_blocked(text: str) -> None:
    verdict = _check(text)
    assert verdict.blocked, verdict
    assert verdict.text == ""


@pytest.mark.parametrize("text", ANNOTATED)
def test_annotated_adjacent(text: str) -> None:
    verdict = _check(text)
    assert verdict.action == "annotate", verdict
    assert verdict.text.startswith(text.rstrip())
    assert verdict.text.endswith(CONSULT_LINE)


@pytest.mark.parametrize("text", BENIGN)
def test_benign_untouched(text: str) -> None:
    verdict = _check(text)
    assert verdict.action == "pass", verdict
    assert verdict.text == text


class TestEvidenceTiers:
    CLAIM = "Oats lower cholesterol."

    def test_tier_1_to_3_lifts_the_block(self) -> None:
        for tier in (1, 2):
            verdict = _check(self.CLAIM, evidence_tier=tier)
            assert not verdict.blocked
        # cholesterol is clinical-adjacent → still gets the Rule 1 line

    def test_tier_3_passes_floor_but_gets_consult_line(self) -> None:
        verdict = _check("Oats support heart health.", evidence_tier=3)
        assert verdict.action == "annotate"
        assert verdict.text.endswith(CONSULT_LINE)

    def test_tier_4_alone_blocks(self) -> None:
        verdict = _check(self.CLAIM, evidence_tier=4)
        assert verdict.blocked
        assert any("Tier 4" in f.reason for f in verdict.findings)


class TestEaterContext:
    def test_health_text_for_sensitive_eater_gets_line(self) -> None:
        verdict = _check(
            "Oats support heart health.",
            evidence_tier=1,
            eater_sensitivities=frozenset({"life_stage:pregnant"}),
        )
        assert verdict.action == "annotate"

    def test_plain_text_for_sensitive_eater_untouched(self) -> None:
        text = "Quick and mild."
        verdict = _check(text, eater_sensitivities=frozenset({"condition:ckd"}))
        assert verdict.action == "pass" and verdict.text == text

    def test_existing_referral_is_not_duplicated(self) -> None:
        text = "Grapefruit can interact with medications; ask your pharmacist."
        assert _check(text).action == "pass"


class TestRecipeGenerationScope:
    RECIPE = "Ingredients: 2 cups rice. Instructions: boil the rice."

    def test_generated_recipe_blocked(self) -> None:
        assert _check(self.RECIPE).blocked

    def test_displayed_corpus_text_not_rule_4(self) -> None:
        # Corpus recipes are displayed, not generated — Rule 4 is about
        # the model writing recipes.
        assert not _check(self.RECIPE, generated=False).blocked


class TestEngine:
    def test_raising_rule_fails_closed(self) -> None:
        class Broken:
            name = "broken"

            def evaluate(self, content):
                raise RuntimeError("boom")

        verdict = SurfaceGuard([Broken()]).check(
            SurfaceContent(surface="x", text="fine")
        )
        assert verdict.blocked
        assert "RuntimeError" in verdict.findings[0].reason

    def test_annotation_appended_once(self) -> None:
        text = "Low sodium for the kidney disease and the diabetes."
        verdict = _check(text)
        assert verdict.text.count(CONSULT_LINE) == 1


def test_corpus_has_no_banned_content_false_positives() -> None:
    """Every real recipe in the repo snapshot passes the banned-content
    rule — Rule 3/H patterns must not fire on ordinary recipe prose."""
    corpus = Path(__file__).resolve().parents[1] / "corpus" / "recipes"
    files = sorted(corpus.glob("*.md"))
    if not files:
        pytest.skip("corpus snapshot not present")
    offenders = []
    for f in files:
        verdict = GUARD.check(
            SurfaceContent(
                surface="corpus",
                text=f.read_text(encoding="utf-8"),
                generated=False,
            )
        )
        offenders += [
            (f.name, x.reason) for x in verdict.findings
            if x.rule_name == "banned-content"
        ]
    assert offenders == []


class TestHouseholdSensitivities:
    def test_collects_life_stage_and_conditions_not_allergies(self, tmp_path) -> None:
        from nutrime.app import initialize
        from nutrime.intake.store import IntakeProfile, save_member_profile
        from nutrime.knowledge.store import Provenance, insert_atom
        from nutrime.members import add_member

        app = initialize(data_dir=tmp_path)
        try:
            kid = add_member(app.substrate, app.tenant_id, "Kid")
            save_member_profile(
                app.substrate, app.tenant_id, kid.id,
                IntakeProfile(year_of_birth=2018, sex_assigned_at_birth="male",
                              life_stage="child", allergens=("peanut",)),
            )
            insert_atom(
                app.substrate, app.tenant_id,
                atom_type="clinical_disclosure",
                provenance=Provenance.CONVERSATIONAL_ELICITATION,
                payload={"disclosure_type": "condition",
                         "disclosure_text": "Celiac disease"},
                subject_id=app.default_member_id,
            )
            from nutrime.knowledge.derivation import sync_from_intake

            sync_from_intake(app.substrate, app.tenant_id)
            got = household_sensitivities(app.substrate, app.tenant_id)
            assert got == {"life_stage:child", "condition:celiac disease"}
        finally:
            app.substrate.close()
            app.operational.close()


def test_daily_floor_boundary() -> None:
    assert _check("Keep under 1,100 calories a day.").blocked
    assert not _check("About 1800 calories a day is typical for many adults.").blocked
