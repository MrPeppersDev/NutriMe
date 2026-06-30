import pytest

from nutrime.phi import (
    PhiCategory,
    PhiEnvelope,
    PhiEnvelopeRegistry,
    PhiEnvelopeRule,
    default_phi_envelope_registry,
)
from nutrime.rules import EgressRequest, PreEgressViolation, default_rule_engine


def _req(
    *,
    query_type: str = "recipe.filter_by_allergens",
    phi_categories: frozenset[PhiCategory] = frozenset(),
) -> EgressRequest:
    return EgressRequest(
        destination="cloud-llm:anthropic",
        query_type=query_type,
        payload="payload",
        phi_categories=frozenset(c.value for c in phi_categories),
    )


def test_registry_register_returns_envelope() -> None:
    registry = PhiEnvelopeRegistry()
    envelope = registry.register(
        "recipe.filter_by_allergens", [PhiCategory.ALLERGENS]
    )
    assert isinstance(envelope, PhiEnvelope)
    assert envelope.allowed_categories == frozenset({PhiCategory.ALLERGENS})
    assert "recipe.filter_by_allergens" in registry


def test_registry_register_overwrites_prior_envelope() -> None:
    registry = PhiEnvelopeRegistry()
    registry.register("recipe.suggest", [PhiCategory.ALLERGENS])
    registry.register(
        "recipe.suggest", [PhiCategory.ALLERGENS, PhiCategory.CONDITIONS]
    )
    envelope = registry.get("recipe.suggest")
    assert envelope is not None
    assert envelope.allowed_categories == frozenset(
        {PhiCategory.ALLERGENS, PhiCategory.CONDITIONS}
    )


def test_envelope_rule_allows_request_within_envelope() -> None:
    registry = PhiEnvelopeRegistry()
    registry.register(
        "recipe.filter_by_allergens",
        [PhiCategory.ALLERGENS, PhiCategory.DEMOGRAPHICS],
    )
    rule = PhiEnvelopeRule(registry)

    result = rule.evaluate(
        _req(phi_categories=frozenset({PhiCategory.ALLERGENS}))
    )
    assert result.allowed


def test_envelope_rule_blocks_request_with_excess_categories() -> None:
    registry = PhiEnvelopeRegistry()
    registry.register("recipe.filter_by_allergens", [PhiCategory.ALLERGENS])
    rule = PhiEnvelopeRule(registry)

    result = rule.evaluate(
        _req(
            phi_categories=frozenset(
                {PhiCategory.ALLERGENS, PhiCategory.CONDITIONS}
            )
        )
    )
    assert not result.allowed
    assert "conditions" in result.reason


def test_envelope_rule_fail_closed_on_unregistered_query_type() -> None:
    """stage3-plan Q2 + phi-handling.md: undeclared egress fails closed."""
    rule = PhiEnvelopeRule(PhiEnvelopeRegistry())
    result = rule.evaluate(_req(query_type="not.registered"))
    assert not result.allowed
    assert "no registered PHI envelope" in result.reason


def test_envelope_rule_rejects_unknown_category_string() -> None:
    registry = PhiEnvelopeRegistry()
    registry.register("recipe.suggest", [PhiCategory.ALLERGENS])
    rule = PhiEnvelopeRule(registry)

    request = EgressRequest(
        destination="cloud-llm:anthropic",
        query_type="recipe.suggest",
        payload="payload",
        phi_categories=frozenset({"bogus-category"}),
    )
    result = rule.evaluate(request)
    assert not result.allowed
    assert "unknown PHI category" in result.reason


def test_default_rule_engine_carries_envelope_rule() -> None:
    registry = default_phi_envelope_registry()
    registry.register("recipe.suggest", [PhiCategory.ALLERGENS])
    engine = default_rule_engine(registry)

    names = {r.name for r in engine.rules}
    assert "phi-envelope" in names

    engine.evaluate_pre_egress(
        _req(
            query_type="recipe.suggest",
            phi_categories=frozenset({PhiCategory.ALLERGENS}),
        )
    )

    with pytest.raises(PreEgressViolation) as excinfo:
        engine.evaluate_pre_egress(
            _req(
                query_type="recipe.suggest",
                phi_categories=frozenset(
                    {PhiCategory.ALLERGENS, PhiCategory.LABS}
                ),
            )
        )
    assert excinfo.value.result.rule_name == "phi-envelope"
