"""Recipe canonical IDs per S9 Q9.3 base contract.

Follows the same UUIDv7 + typed-prefix pattern as ``knowledge.ids`` so
``rcp-<uuid7>`` ids are time-ordered and visually distinguishable at
debugging time.
"""

from __future__ import annotations

from nutrime.knowledge.ids import uuid7


def new_recipe_id() -> str:
    return f"rcp-{uuid7()}"
