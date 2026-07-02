"""recipe_search PHI envelope registration + fail-closed behaviour."""

from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.phi import PhiCategory, PhiEnvelopeRule
from nutrime.recipes.phi import RECIPE_SEARCH_QUERY_TYPE, register_recipe_envelopes
from nutrime.rules import EgressRequest

SUBSTRATE_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "substrate"
OPERATIONAL_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "operational"


@pytest.fixture
def initialized_app(tmp_path: Path):
    return initialize(
        data_dir=tmp_path / "nutrime-data",
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )


class TestRecipeSearchEnvelope:
    def test_registered_on_app_init(self, initialized_app) -> None:
        envelope = initialized_app.phi_envelope.get(RECIPE_SEARCH_QUERY_TYPE)
        assert envelope is not None
        assert envelope.allowed_categories == frozenset()

    def test_empty_categories_allowed(self, initialized_app) -> None:
        rule = PhiEnvelopeRule(initialized_app.phi_envelope)
        result = rule.evaluate(
            EgressRequest(
                destination="test",
                query_type=RECIPE_SEARCH_QUERY_TYPE,
                payload="",
                phi_categories=frozenset(),
            )
        )
        assert result.allowed is True

    def test_any_phi_category_rejected(self, initialized_app) -> None:
        rule = PhiEnvelopeRule(initialized_app.phi_envelope)
        result = rule.evaluate(
            EgressRequest(
                destination="test",
                query_type=RECIPE_SEARCH_QUERY_TYPE,
                payload="",
                phi_categories=frozenset({PhiCategory.ALLERGENS.value}),
            )
        )
        assert result.allowed is False
        assert "allergens" in (result.reason or "")

    def test_multiple_phi_categories_all_named_in_rejection(
        self, initialized_app
    ) -> None:
        rule = PhiEnvelopeRule(initialized_app.phi_envelope)
        result = rule.evaluate(
            EgressRequest(
                destination="test",
                query_type=RECIPE_SEARCH_QUERY_TYPE,
                payload="",
                phi_categories=frozenset(
                    {PhiCategory.CONDITIONS.value, PhiCategory.LABS.value}
                ),
            )
        )
        assert result.allowed is False
        reason = result.reason or ""
        assert "conditions" in reason
        assert "labs" in reason


class TestRegisterRecipeEnvelopes:
    def test_direct_registration(self) -> None:
        from nutrime.phi import default_phi_envelope_registry

        registry = default_phi_envelope_registry()
        assert RECIPE_SEARCH_QUERY_TYPE not in registry
        register_recipe_envelopes(registry)
        assert RECIPE_SEARCH_QUERY_TYPE in registry
        envelope = registry.get(RECIPE_SEARCH_QUERY_TYPE)
        assert envelope is not None
        assert envelope.allowed_categories == frozenset()

    def test_reregistration_is_idempotent(self) -> None:
        from nutrime.phi import default_phi_envelope_registry

        registry = default_phi_envelope_registry()
        register_recipe_envelopes(registry)
        register_recipe_envelopes(registry)
        envelope = registry.get(RECIPE_SEARCH_QUERY_TYPE)
        assert envelope is not None
        assert envelope.allowed_categories == frozenset()
