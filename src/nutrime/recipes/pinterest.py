"""Pinterest board sync — pins → recipe corpus, hands-free (issue #24 rung 2).

The product requirement (2026-10-03 follow-up): the user should never have
to know what they pinned or what's in the corpus — connect once, then pins
simply become searchable. This adapter makes the corpus a *consequence* of
pinning rather than a thing to manage.

Mechanism: Pinterest API v5 ``GET /v5/pins`` (bookmark-paginated) yields the
account's pins; each food pin carries an outbound ``link`` to the recipe
page. Those links feed straight into the 4.4 schema.org JSON-LD adapter
(:mod:`nutrime.recipes.jsonld`), which already handles fetch politeness,
extraction, URL-normalized de-dup and skip-with-report. Re-running sync is
therefore cheap and idempotent — already-ingested pins are skipped at the
URL level, so "sync" means "catch up on whatever was pinned since".

Token resolution mirrors the Anthropic adapter's no-plaintext-on-disk
pattern: explicit param → ``$PINTEREST_ACCESS_TOKEN`` → macOS Keychain
service ``nutrime-pinterest``. Getting a token requires a (free) Pinterest
developer app with ``pins:read`` + ``boards:read`` scopes; store it once:

    security add-generic-password -U -s nutrime-pinterest -a "$USER" -w

Watch items recorded on #24: access tokens expire after 30 days; the
continuous-refresh-token flow (60-day, refreshable indefinitely — requires
storing the app's client id/secret) is the follow-up that removes even the
monthly re-paste. Image-only pins (no outbound link) are counted and
reported but not extracted — the vision-extraction follow-up stays open.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from nutrime.recipes.jsonld import SeedOutcome as JsonLdOutcome
from nutrime.recipes.jsonld import seed_recipes as jsonld_seed_recipes
from nutrime.recipes.web import Pacer, TextFetcher

API_BASE = "https://api.pinterest.com/v5"
TOKEN_ENV = "PINTEREST_ACCESS_TOKEN"
KEYCHAIN_SERVICE = "nutrime-pinterest"
_PAGE_SIZE = 100

# JSON API fetcher: (url, bearer_token) -> parsed payload
ApiFetcher = Callable[[str, str], dict[str, Any]]


class MissingTokenError(Exception):
    """No Pinterest access token available on any resolution path."""


class PinterestAuthError(Exception):
    """Token rejected (expired or revoked) — needs a fresh token."""


def keychain_token(service: str = KEYCHAIN_SERVICE) -> str | None:
    """macOS Keychain lookup; None off-macOS or when no entry exists."""
    if sys.platform != "darwin":
        return None
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    token = result.stdout.strip()
    return token or None


def resolve_token(explicit: str | None = None) -> str:
    token = explicit or os.environ.get(TOKEN_ENV) or keychain_token()
    if not token:
        raise MissingTokenError(
            f"no Pinterest access token: set ${TOKEN_ENV} or store one in"
            f" the macOS Keychain (service {KEYCHAIN_SERVICE!r}:"
            f' security add-generic-password -U -s {KEYCHAIN_SERVICE}'
            f' -a "$USER" -w). Tokens come from a free Pinterest developer'
            " app with pins:read + boards:read scopes"
            " (developers.pinterest.com)."
        )
    return token


def has_token() -> bool:
    """Connection check for UI surfaces — never raises."""
    try:
        resolve_token()
    except MissingTokenError:
        return False
    return True


def _urllib_api_fetch(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        if err.code in (401, 403):
            raise PinterestAuthError(
                f"Pinterest rejected the access token (HTTP {err.code})"
                " — it has likely expired (30-day lifetime); generate a"
                " fresh one and re-store it."
            ) from err
        raise


@dataclass(frozen=True)
class Pin:
    pin_id: str
    link: str
    title: str
    board_id: str


@dataclass(frozen=True)
class PinterestClient:
    """Bookmark-paginated reads against the v5 API.

    ``fetcher`` is resolved at call time to the module-level
    :func:`_urllib_api_fetch` so tests can monkey-patch the module binding.
    """

    token: str
    base_url: str = API_BASE
    fetcher: ApiFetcher | None = None
    pacer: Pacer | None = None

    def _get_pages(
        self, path: str, params: dict[str, str]
    ) -> Iterator[list[dict[str, Any]]]:
        fetch = self.fetcher if self.fetcher is not None else _urllib_api_fetch
        bookmark: str | None = None
        first = True
        while True:
            query = dict(params)
            if bookmark:
                query["bookmark"] = bookmark
            url = f"{self.base_url}/{path}?{urllib.parse.urlencode(query)}"
            if not first and self.pacer is not None:
                self.pacer.wait()
            first = False
            payload = fetch(url, self.token)
            yield list(payload.get("items") or [])
            bookmark = payload.get("bookmark") or None
            if not bookmark:
                return

    def list_boards(self) -> list[dict[str, Any]]:
        boards: list[dict[str, Any]] = []
        for page in self._get_pages("boards", {"page_size": str(_PAGE_SIZE)}):
            boards.extend(page)
        return boards

    def iter_pins(self, *, board_id: str | None = None) -> Iterator[Pin]:
        path = f"boards/{board_id}/pins" if board_id else "pins"
        for page in self._get_pages(path, {"page_size": str(_PAGE_SIZE)}):
            for item in page:
                yield Pin(
                    pin_id=str(item.get("id") or ""),
                    link=str(item.get("link") or "").strip(),
                    title=str(item.get("title") or "").strip(),
                    board_id=str(item.get("board_id") or ""),
                )

    def board_id_by_name(self, name: str) -> str | None:
        wanted = name.strip().lower()
        for board in self.list_boards():
            if str(board.get("name") or "").strip().lower() == wanted:
                return str(board.get("id") or "") or None
        return None


def _is_ingestible_link(link: str) -> bool:
    """A pin link we can try: external http(s), not a pinterest-internal URL."""
    if not link.startswith(("http://", "https://")):
        return False
    host = urllib.parse.urlparse(link).netloc.lower()
    return not (host == "pinterest.com" or host.endswith(".pinterest.com"))


@dataclass(frozen=True)
class SyncOutcome:
    pins_seen: int
    pins_with_links: int
    pins_without_links: int
    ingest: JsonLdOutcome

    @property
    def written(self) -> int:
        return self.ingest.written


def sync_pins(
    client: PinterestClient,
    vault,  # RecipeVault
    *,
    board_name: str | None = None,
    limit: int | None = None,
    page_fetcher: TextFetcher | None = None,
    pacer: Pacer | None = None,
) -> SyncOutcome:
    """Enumerate pins, then ingest their recipe pages via the 4.4 adapter.

    ``limit`` caps the number of *candidate links* passed to ingest (not
    writes) so a first sync over a large account can be chunked; because
    de-dup is URL-level in the jsonld adapter, re-running sync continues
    where the previous run left off.
    """
    board_id: str | None = None
    if board_name:
        board_id = client.board_id_by_name(board_name)
        if board_id is None:
            raise ValueError(f"no Pinterest board named {board_name!r}")

    pins_seen = 0
    without_links = 0
    links: list[str] = []
    seen_links: set[str] = set()
    for pin in client.iter_pins(board_id=board_id):
        pins_seen += 1
        if not _is_ingestible_link(pin.link):
            without_links += 1
            continue
        if pin.link in seen_links:
            continue
        seen_links.add(pin.link)
        links.append(pin.link)
        if limit is not None and len(links) >= limit:
            break

    ingest = jsonld_seed_recipes(
        vault,
        links,
        fetcher=page_fetcher,
        pacer=pacer or Pacer(delay_s=1.0),
    )
    return SyncOutcome(
        pins_seen=pins_seen,
        pins_with_links=len(links),
        pins_without_links=without_links,
        ingest=ingest,
    )
