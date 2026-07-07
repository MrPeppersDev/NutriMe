"""Shared web-source plumbing for bulk-HTML recipe adapters.

Sub-commit 4.2 cross-cutting politeness requirements: every HTTP request
carries a descriptive User-Agent identifying the project, and multi-page
crawls pace themselves via :class:`Pacer` (injectable sleep so tests run
instantly).

Also carries the minimal HTML text extraction used by the NHLBI and
MyPlate-via-Wayback adapters: both sites ship stable server-rendered
markup, so bounded-window regex + tag stripping is sufficient at MVP —
no HTML-parser dependency.
"""

from __future__ import annotations

import html as html_lib
import re
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

USER_AGENT = (
    "NutriMe/0.0.1 (personal nutrition research;"
    " +https://github.com/MrPeppersDev/NutriMe)"
)

TextFetcher = Callable[[str], str]


def _urllib_fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read()
    return raw.decode(charset, errors="replace")


@dataclass
class Pacer:
    """Fixed inter-request delay; ``sleep`` is injectable for tests."""

    delay_s: float = 1.0
    sleep: Callable[[float], None] = time.sleep

    def wait(self) -> None:
        if self.delay_s > 0:
            self.sleep(self.delay_s)


def now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def strip_tags(fragment: str) -> str:
    """Flatten an HTML fragment to normalized plain text."""
    no_tags = re.sub(r"<[^>]+>", " ", fragment)
    text = html_lib.unescape(no_tags)
    return re.sub(r"\s+", " ", text).strip()


def extract_list_items(fragment: str) -> list[str]:
    """Return the flattened text of each ``<li>`` in ``fragment``."""
    items = re.findall(r"<li[^>]*>(.*?)</li>", fragment, re.S)
    out = [strip_tags(item) for item in items]
    return [item for item in out if item]


def parse_duration_minutes(text: str) -> int | None:
    """Parse "10 minutes" / "1 hour 15 minutes" / "2 hrs" → total minutes."""
    total = 0
    found = False
    for amount, unit in re.findall(
        r"(\d+)\s*(hours?|hrs?|minutes?|mins?)", text, flags=re.IGNORECASE
    ):
        found = True
        value = int(amount)
        if unit.lower().startswith(("hour", "hr")):
            total += value * 60
        else:
            total += value
    return total if found else None
