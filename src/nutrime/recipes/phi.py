"""PHI envelope declarations for the recipes package.

Registered at :func:`nutrime.app.initialize` so the ``recipe_search`` query
type is known to the fail-closed PhiEnvelopeRule from the moment the app
boots. Recipe corpus lookups carry no health PHI — the envelope is empty.
If a future call path tries to attach any :class:`PhiCategory` to a
``recipe_search`` request, the rule rejects it per S4-Q2 typed-PHI-boundary
discipline.
"""

from __future__ import annotations

from nutrime.phi import PhiEnvelopeRegistry

RECIPE_SEARCH_QUERY_TYPE = "recipe_search"


def register_recipe_envelopes(registry: PhiEnvelopeRegistry) -> None:
    """Register the ``recipe_search`` envelope with an empty PHI category set."""
    registry.register(RECIPE_SEARCH_QUERY_TYPE, ())
