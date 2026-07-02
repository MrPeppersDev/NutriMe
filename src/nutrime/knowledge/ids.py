"""Typed-prefix IDs per schema.md S1 Q1.3.

RFC 9562 UUIDv7 chosen for time-orderability against ``valid_from`` bitemporal
queries. Python 3.13's stdlib ``uuid`` module doesn't ship v7 yet, so a small
generator lives here. Typed 4-char prefix (``atm-`` / ``syn-`` / ``mol-``)
gives human-visible discrimination at debugging time.
"""

from __future__ import annotations

import os
import time
import uuid


def uuid7() -> str:
    """Return an RFC 9562 UUIDv7 as a canonical string.

    Layout: 48 bits unix-ms | 4 bits version=7 | 12 bits rand_a
          | 2 bits variant=10 | 62 bits rand_b.
    """
    ms = int(time.time() * 1000) & 0xFFFFFFFFFFFF
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF
    value = (
        (ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0x2 << 62)
        | rand_b
    )
    return str(uuid.UUID(int=value))


def new_atom_id() -> str:
    return f"atm-{uuid7()}"


def new_synthesized_entry_id() -> str:
    return f"syn-{uuid7()}"
