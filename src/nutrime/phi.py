"""Typed per-query-type PHI envelope.

Per ``research/00-meta/stage3-plan.md`` Q2 resolution + ``phi-handling.md``
"Boundary enforcement (architectural)":

> Typed PHI boundary enforcement. The Q3 tenant-aware query helper extends to a
> typed PHI envelope per request. Every cloud-bound payload is constructed via
> the helper; helper enforces "this query type may carry these PHI categories,
> no others." Bypass requires a code-review-flagged exception.

The envelope is the inner enforcement of the double-layered scheme (per-agent
outer + per-tool inner). Each query type declares the PHI categories it is
allowed to carry; the :class:`PhiEnvelopeRule` plugs into the constitutional
:class:`~nutrime.rules.RuleEngine` and rejects any egress request whose
:attr:`EgressRequest.phi_categories` set exceeds the declared envelope.

This module ships the scaffolding (categories enum, registry, the rule). Real
query-type envelope declarations land alongside the components that introduce
those query types in later Stage 6 sub-commits. The registry is empty by
default; an unregistered query type **fails closed** at egress time so a missed
declaration cannot accidentally bypass the boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from nutrime.rules import EgressRequest, RuleResult


class PhiCategory(StrEnum):
    """Categories per ``phi-handling.md`` audit-log requirements.

    These are categories, not values — audit logs and the envelope record
    "allergens crossed" rather than the allergen list itself.
    """

    DEMOGRAPHICS = "demographics"
    ALLERGENS = "allergens"
    CONDITIONS = "conditions"
    MEDICATIONS = "medications"
    LABS = "labs"
    WEARABLES = "wearables"
    INTAKE_SCREENER = "intake_screener"


@dataclass(frozen=True)
class PhiEnvelope:
    query_type: str
    allowed_categories: frozenset[PhiCategory]


class PhiEnvelopeRegistry:
    def __init__(self, envelopes: Iterable[PhiEnvelope] = ()) -> None:
        self._envelopes: dict[str, PhiEnvelope] = {e.query_type: e for e in envelopes}

    def register(
        self, query_type: str, allowed_categories: Iterable[PhiCategory]
    ) -> PhiEnvelope:
        envelope = PhiEnvelope(
            query_type=query_type, allowed_categories=frozenset(allowed_categories)
        )
        self._envelopes[query_type] = envelope
        return envelope

    def get(self, query_type: str) -> PhiEnvelope | None:
        return self._envelopes.get(query_type)

    def __contains__(self, query_type: object) -> bool:
        return query_type in self._envelopes


class PhiEnvelopeRule:
    name = "phi-envelope"

    def __init__(self, registry: PhiEnvelopeRegistry) -> None:
        self._registry = registry

    def evaluate(self, request: EgressRequest) -> RuleResult:
        envelope = self._registry.get(request.query_type)
        if envelope is None:
            return RuleResult(
                allowed=False,
                rule_name=self.name,
                reason=(
                    f"query type {request.query_type!r} has no registered PHI"
                    " envelope; egress declared via the envelope helper is"
                    " required (fail-closed)"
                ),
            )
        # Coerce request categories to PhiCategory so callers that pass raw
        # strings (e.g., from JSON) still match envelope membership.
        try:
            request_categories = frozenset(
                PhiCategory(c) for c in request.phi_categories
            )
        except ValueError as exc:
            return RuleResult(
                allowed=False,
                rule_name=self.name,
                reason=f"unknown PHI category in request: {exc}",
            )
        exceeded = request_categories - envelope.allowed_categories
        if exceeded:
            categories = ", ".join(sorted(c.value for c in exceeded))
            return RuleResult(
                allowed=False,
                rule_name=self.name,
                reason=(
                    f"query type {request.query_type!r} attempted to carry"
                    f" PHI categories outside its envelope: {categories}"
                ),
            )
        return RuleResult(allowed=True, rule_name=self.name)


def default_phi_envelope_registry() -> PhiEnvelopeRegistry:
    """Empty registry — concrete query types register as their components land."""
    return PhiEnvelopeRegistry()
