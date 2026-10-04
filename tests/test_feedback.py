"""Step 7 — meal events, two-stage feedback, consent gating, summaries."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.consent import ConsentError, record_decision
from nutrime.feedback import (
    meal_history,
    recipe_experience_summary,
    record_body_response,
    record_cooking_experience,
    record_meal_event,
    record_time_feedback,
)


@pytest.fixture
def app(tmp_path: Path):
    application = initialize(data_dir=tmp_path)
    yield application
    application.substrate.close()
    application.operational.close()


def _cook(app, recipe_id="rcp-x", title="Test Stew"):
    return record_meal_event(
        app.substrate, app.tenant_id, recipe_id=recipe_id, recipe_title=title
    )


class TestMealEvent:
    def test_cook_recorded_with_consent_id(self, app) -> None:
        meal_event_id = _cook(app)
        assert meal_event_id.startswith("mev-")
        row = app.substrate.execute(
            "SELECT consent_record_id FROM atom WHERE type = 'meal_event'"
        ).fetchone()
        assert row[0] and row[0].startswith("cns-")


class TestTwoStageFeedback:
    def test_cooking_experience(self, app) -> None:
        mev = _cook(app)
        atom_id = record_cooking_experience(
            app.substrate, app.tenant_id,
            meal_event_id=mev, ease_rating=4, enjoyment_rating=5,
            freetext_notes="fun but lots of dishes",
        )
        assert atom_id.startswith("atm-")

    def test_rating_bounds(self, app) -> None:
        mev = _cook(app)
        with pytest.raises(ValueError):
            record_cooking_experience(
                app.substrate, app.tenant_id,
                meal_event_id=mev, ease_rating=0, enjoyment_rating=3,
            )

    def test_body_response_requires_text(self, app) -> None:
        mev = _cook(app)
        with pytest.raises(ValueError, match="feeling is the data"):
            record_body_response(
                app.substrate, app.tenant_id,
                meal_event_id=mev, freetext_response="   ",
            )

    def test_time_delta_computed(self, app) -> None:
        mev = _cook(app)
        record_time_feedback(
            app.substrate, app.tenant_id,
            meal_event_id=mev, estimated_time_min=30, actual_time_min=50,
        )
        entry = meal_history(app.substrate, app.tenant_id)[0]
        assert entry.actual_time_min == 50
        assert entry.time_delta_min == 20


class TestConsentGate:
    def test_declined_semantic_blocks_body_response_only(self, app) -> None:
        record_decision(
            app.substrate, app.tenant_id,
            data_category="meal_feedback_semantic", purpose="local_operation",
            granted=False,
        )
        mev = _cook(app)  # time category still granted
        record_cooking_experience(
            app.substrate, app.tenant_id,
            meal_event_id=mev, ease_rating=3, enjoyment_rating=3,
        )
        with pytest.raises(ConsentError):
            record_body_response(
                app.substrate, app.tenant_id,
                meal_event_id=mev, freetext_response="sluggish by 8pm",
            )

    def test_declined_time_blocks_cook_capture(self, app) -> None:
        record_decision(
            app.substrate, app.tenant_id,
            data_category="meal_feedback_time", purpose="local_operation",
            granted=False,
        )
        with pytest.raises(ConsentError):
            _cook(app)


class TestHistoryAndSummary:
    def test_history_joins_all_stages(self, app) -> None:
        mev = _cook(app, recipe_id="rcp-a", title="Curry")
        record_cooking_experience(
            app.substrate, app.tenant_id,
            meal_event_id=mev, ease_rating=4, enjoyment_rating=5,
        )
        record_body_response(
            app.substrate, app.tenant_id,
            meal_event_id=mev, freetext_response="great energy all evening",
            energy_rating=5,
        )
        record_time_feedback(
            app.substrate, app.tenant_id,
            meal_event_id=mev, estimated_time_min=40, actual_time_min=45,
        )
        (entry,) = meal_history(app.substrate, app.tenant_id)
        assert entry.recipe_title == "Curry"
        assert entry.ease_rating == 4
        assert entry.body_response == "great energy all evening"
        assert entry.time_delta_min == 5

    def test_recipe_summary_aggregates(self, app) -> None:
        for ease in (3, 5):
            mev = _cook(app, recipe_id="rcp-b", title="Soup")
            record_cooking_experience(
                app.substrate, app.tenant_id,
                meal_event_id=mev, ease_rating=ease, enjoyment_rating=4,
            )
        summary = recipe_experience_summary(
            app.substrate, app.tenant_id, "rcp-b"
        )
        assert summary["times_cooked"] == 2
        assert summary["avg_ease"] == 4.0

    def test_never_cooked_is_none(self, app) -> None:
        assert (
            recipe_experience_summary(app.substrate, app.tenant_id, "rcp-z")
            is None
        )
