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
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

USER_AGENT = (
    "NutriMe/0.0.1 (personal nutrition research;"
    " +https://github.com/MrPeppersDev/NutriMe)"
)

TextFetcher = Callable[[str], str]


class UnsafeUrlError(Exception):
    """URL resolves to a private/internal address — refused (SSRF guard)."""


def check_url_safety(url: str) -> None:
    """Reject URLs whose host resolves to non-public address space.

    Sweep #16 security pattern (stdlib cut): the web UI accepts arbitrary
    user-pasted URLs, so a crafted link must not be able to make the
    server fetch localhost/LAN/cloud-metadata addresses. Every resolved
    address must be globally routable. (Connection pinning to the
    validated IP is deferred — single-household localhost server; DNS
    rebinding within the fetch window is out of threat model at MVP.)
    """
    import ipaddress
    import socket

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeUrlError(f"unsupported scheme: {parsed.scheme!r}")
    host = parsed.hostname or ""
    if not host:
        raise UnsafeUrlError("URL has no host")
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as exc:
        raise UnsafeUrlError(f"cannot resolve host {host!r}: {exc}") from exc
    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
            address = address.ipv4_mapped
        if not address.is_global:
            raise UnsafeUrlError(
                f"host {host!r} resolves to non-public address {address}"
            )


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-run the SSRF check on EVERY redirect hop.

    2026-10-07 audit (verified by execution): the guard checked only
    the initial URL, so a public URL 302-ing to 127.0.0.1 had its
    internal response fetched. urllib follows redirects by default;
    this handler closes that hole for every caller of the opener.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url_safety(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse redirects outright — for requests carrying credentials.

    urllib re-sends the original Request's headers (Authorization
    included) to the redirect target, so an authenticated call that
    gets redirected hands the bearer token to whatever host answers
    (2026-10-07 audit). The APIs we authenticate to never legitimately
    redirect; failing loudly is strictly safer than following.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise UnsafeUrlError(
            f"refusing redirect of authenticated request to {newurl!r}"
        )


_SAFE_OPENER = urllib.request.build_opener(_SafeRedirectHandler())
_NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirectHandler())


def safe_urlopen(url_or_request, *, timeout: float = 30, redirects: bool = True):
    """urlopen with the SSRF guard applied to the initial URL and every
    redirect hop. All outbound web fetches must come through here.

    Pass ``redirects=False`` for requests that carry credentials — any
    redirect then raises instead of forwarding the auth header.
    """
    url = (
        url_or_request
        if isinstance(url_or_request, str)
        else url_or_request.full_url
    )
    check_url_safety(url)
    opener = _SAFE_OPENER if redirects else _NO_REDIRECT_OPENER
    return opener.open(url_or_request, timeout=timeout)


def _urllib_fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with safe_urlopen(request, timeout=30) as response:
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
