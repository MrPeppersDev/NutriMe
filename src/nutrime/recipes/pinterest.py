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
pattern: explicit param → ``$PINTEREST_ACCESS_TOKEN`` → OS credential store
(:mod:`nutrime.credstore` — macOS Keychain / Windows Credential Manager)
service ``nutrime-pinterest``. Getting a token requires a (free) Pinterest
developer app with ``pins:read`` + ``boards:read`` scopes; ``nutrime
pinterest connect`` stores it, or by hand on macOS:

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
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Iterator

from nutrime import credstore
from nutrime.recipes.jsonld import SeedOutcome as JsonLdOutcome
from nutrime.recipes.jsonld import seed_recipes as jsonld_seed_recipes
from nutrime.recipes.web import Pacer, TextFetcher

API_BASE = "https://api.pinterest.com/v5"
OAUTH_AUTHORIZE_URL = "https://www.pinterest.com/oauth/"
TOKEN_URL = f"{API_BASE}/oauth/token"
OAUTH_SCOPES = "boards:read,pins:read"
TOKEN_ENV = "PINTEREST_ACCESS_TOKEN"
KEYCHAIN_SERVICE = "nutrime-pinterest"
KEYCHAIN_REFRESH_SERVICE = "nutrime-pinterest-refresh"
KEYCHAIN_APP_SERVICE = "nutrime-pinterest-app"
_PAGE_SIZE = 100

# JSON API fetcher: (url, bearer_token) -> parsed payload
ApiFetcher = Callable[[str, str], dict[str, Any]]


class MissingTokenError(Exception):
    """No Pinterest access token available on any resolution path."""


class PinterestAuthError(Exception):
    """Token rejected (expired or revoked) — needs a fresh token."""


def keychain_token(service: str = KEYCHAIN_SERVICE) -> str | None:
    """OS credential-store lookup; None when unsupported or no entry exists."""
    return credstore.read_secret(service)


def resolve_token(explicit: str | None = None) -> str:
    token = explicit or os.environ.get(TOKEN_ENV) or keychain_token()
    if not token:
        raise MissingTokenError(
            f"no Pinterest access token: run `nutrime pinterest connect`,"
            f" set ${TOKEN_ENV}, or store one in the {credstore.backend_name()}"
            f" (service {KEYCHAIN_SERVICE!r}: {credstore.store_hint(KEYCHAIN_SERVICE)})."
            " Tokens come from a free Pinterest developer app with"
            " pins:read + boards:read scopes (developers.pinterest.com)."
        )
    return token


def has_token() -> bool:
    """Connection check for UI surfaces — never raises."""
    try:
        resolve_token()
    except MissingTokenError:
        return False
    return True


# -- OAuth connect flow -------------------------------------------------------
#
# `nutrime pinterest connect` runs the full authorization-code dance locally:
# spin up a one-shot localhost HTTP listener as the redirect_uri, open the
# Pinterest consent page in the default browser, catch the ?code= redirect,
# exchange it at /v5/oauth/token, and store both tokens in the OS credential
# store (Keychain on macOS, Credential Manager on Windows).
# The app's client id/secret are stored too (service nutrime-pinterest-app,
# account = client id) so `pinterest refresh` can renew the 30-day access
# token from the continuous refresh token without re-consent.


def _keychain_store(service: str, account: str, secret: str) -> None:
    credstore.write(service, account, secret)


def _keychain_read(service: str) -> tuple[str, str] | None:
    """Return (account, secret) for a service, or None."""
    return credstore.read(service)


def _os_user() -> str:
    return os.environ.get("USER") or os.environ.get("USERNAME") or "nutrime"


def store_tokens(
    access_token: str,
    refresh_token: str | None,
    *,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> None:
    _keychain_store(KEYCHAIN_SERVICE, _os_user(), access_token)
    if refresh_token:
        _keychain_store(KEYCHAIN_REFRESH_SERVICE, _os_user(), refresh_token)
    if client_id and client_secret:
        _keychain_store(KEYCHAIN_APP_SERVICE, client_id, client_secret)


def _token_request(form: dict[str, str], client_id: str, client_secret: str) -> dict[str, Any]:
    import base64

    basic = base64.b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("ascii")
    request = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode(form).encode("utf-8"),
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def exchange_code(
    code: str, *, client_id: str, client_secret: str, redirect_uri: str
) -> dict[str, Any]:
    return _token_request(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        client_id,
        client_secret,
    )


def refresh_access_token() -> str:
    """Renew the access token from the stored continuous refresh token."""
    refresh = _keychain_read(KEYCHAIN_REFRESH_SERVICE)
    app = _keychain_read(KEYCHAIN_APP_SERVICE)
    if refresh is None or app is None:
        raise MissingTokenError(
            "no stored refresh token / app credentials — run"
            " `nutrime pinterest connect` first."
        )
    client_id, client_secret = app
    payload = _token_request(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh[1],
            "refresh_on": "true",
        },
        client_id,
        client_secret,
    )
    access = str(payload.get("access_token") or "")
    if not access:
        raise PinterestAuthError(f"token refresh returned no access_token: {payload}")
    store_tokens(
        access,
        str(payload.get("refresh_token") or "") or None,
    )
    return access


def connect_interactive(
    client_id: str,
    client_secret: str,
    *,
    port: int = 8766,
    open_browser: Callable[[str], Any] | None = None,
    emitter: Callable[[str], None] = print,
    timeout_s: float = 300.0,
) -> None:
    """Run the full OAuth dance; store tokens + app creds in the Keychain.

    The redirect_uri is ``http://localhost:<port>/`` — it must be listed
    exactly in the Pinterest app's Redirect URIs setting.
    """
    import http.server
    import secrets
    import socketserver
    import webbrowser

    redirect_uri = f"http://localhost:{port}/"
    state = secrets.token_urlsafe(16)
    auth_url = OAUTH_AUTHORIZE_URL + "?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": OAUTH_SCOPES,
            "state": state,
        }
    )

    captured: dict[str, str] = {}

    class _CallbackHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args) -> None:  # noqa: A002
            pass

        def do_GET(self) -> None:  # noqa: N802
            query = urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query
            )
            captured["code"] = (query.get("code") or [""])[0]
            captured["state"] = (query.get("state") or [""])[0]
            captured["error"] = (query.get("error") or [""])[0]
            body = (
                "<html><body style='font-family:sans-serif;padding:40px'>"
                "<h2>NutriMe is connected to Pinterest.</h2>"
                "<p>You can close this tab and go back to the recipe page.</p>"
                "</body></html>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    class _ReusableServer(socketserver.TCPServer):
        # The redirect port lingers in TIME_WAIT after a previous connect
        # attempt; without reuse a quick retry would fail to bind.
        allow_reuse_address = True

    with _ReusableServer(("127.0.0.1", port), _CallbackHandler) as httpd:
        httpd.timeout = timeout_s
        emitter("Opening Pinterest in your browser — log in as the account")
        emitter("whose pins you want, and click Allow.")
        emitter(f"(If nothing opens, visit:\n  {auth_url})")
        (open_browser or webbrowser.open)(auth_url)
        httpd.handle_request()  # one-shot: blocks until the redirect lands

    if captured.get("error"):
        raise PinterestAuthError(f"Pinterest denied access: {captured['error']}")
    if not captured.get("code"):
        raise PinterestAuthError(
            "no authorization code received (timed out or tab closed)"
        )
    if captured.get("state") != state:
        raise PinterestAuthError("OAuth state mismatch — aborting")

    payload = exchange_code(
        captured["code"],
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )
    access = str(payload.get("access_token") or "")
    if not access:
        raise PinterestAuthError(f"token exchange returned no access_token: {payload}")
    store_tokens(
        access,
        str(payload.get("refresh_token") or "") or None,
        client_id=client_id,
        client_secret=client_secret,
    )
    emitter("Connected. Tokens stored in the macOS Keychain.")
    emitter("Pins will sync from the recipe page's Sync button, or:")
    emitter("  nutrime recipes fetch --source pinterest")


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
