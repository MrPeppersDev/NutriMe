"""Consent records (#21) — baseline bootstrap, decisions, fail-closed gate."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.consent import (
    ConsentError,
    DATA_CATEGORIES,
    bootstrap_baseline,
    current_decision,
    list_current,
    record_decision,
    require_consent,
)


@pytest.fixture
def app(tmp_path: Path):
    application = initialize(data_dir=tmp_path)
    yield application
    application.substrate.close()
    application.operational.close()


class TestBaseline:
    def test_bootstrap_runs_at_initialize(self, app) -> None:
        rows = list_current(app.substrate, app.tenant_id)
        # every category x both purposes
        assert len(rows) == len(DATA_CATEGORIES) * 2

    def test_local_operation_granted_retroactive(self, app) -> None:
        record = current_decision(
            app.substrate, app.tenant_id, "intake_screener", "local_operation"
        )
        assert record.granted is True
        assert record.retroactive is True

    def test_publication_defaults_declined(self, app) -> None:
        record = current_decision(
            app.substrate, app.tenant_id, "meal_feedback_time",
            "publication_aggregate",
        )
        assert record.granted is False

    def test_rerun_is_idempotent(self, app) -> None:
        assert bootstrap_baseline(app.substrate, app.tenant_id) == 0


class TestDecisions:
    def test_supersede_chain(self, app) -> None:
        first = current_decision(
            app.substrate, app.tenant_id, "inventory", "publication_aggregate"
        )
        new_id = record_decision(
            app.substrate, app.tenant_id,
            data_category="inventory", purpose="publication_aggregate",
            granted=True, note="opting in",
        )
        now = current_decision(
            app.substrate, app.tenant_id, "inventory", "publication_aggregate"
        )
        assert now.id == new_id and now.granted is True
        # old row closed and linked forward
        row = app.substrate.execute(
            "SELECT valid_until, superseded_by FROM consent_record WHERE id = ?",
            (first.id,),
        ).fetchone()
        assert row[0] is not None and row[1] == new_id

    def test_unknown_category_rejected(self, app) -> None:
        with pytest.raises(ValueError):
            record_decision(
                app.substrate, app.tenant_id,
                data_category="telepathy", purpose="local_operation",
                granted=True,
            )


class TestGate:
    def test_granted_returns_record_id(self, app) -> None:
        consent_id = require_consent(
            app.substrate, app.tenant_id, "meal_feedback_time"
        )
        assert consent_id.startswith("cns-")

    def test_declined_blocks(self, app) -> None:
        record_decision(
            app.substrate, app.tenant_id,
            data_category="meal_feedback_semantic", purpose="local_operation",
            granted=False, note="user said no",
        )
        with pytest.raises(ConsentError):
            require_consent(
                app.substrate, app.tenant_id, "meal_feedback_semantic"
            )
