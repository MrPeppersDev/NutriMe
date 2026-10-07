"""Anthropic Messages API adapter — first concrete provider (5.2).

Stdlib-urllib per project convention (no SDK dependency; the ``_post`` seam is
monkeypatchable in tests, same pattern as ``recipes.themealdb._urllib_fetch``).
Provider quirks kept in here per provider-abstraction.md: endpoint, headers,
wire shapes, retry classification.

Retry policy: 429 (rate limit) and >=500 (provider/overloaded) are retryable
with exponential backoff; other 4xx are validation errors and fail
immediately; timeouts/connection errors are retryable. The final outcome maps
onto the ``op_llm_request_log.outcome`` enum.

Model default is ``claude-opus-4-8`` (current Opus tier as of 2026-08). Note
for the eventual capability-vector expansion: 4.6+ models drop sampling
parameters (``temperature`` etc.) — the adapter deliberately never sends them.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from nutrime import credstore
from nutrime.recipes.web import safe_urlopen
from nutrime.llm.base import (
    CAP_CLOUD_PERMITTED,
    CAP_LONG_CONTEXT,
    CAP_REASONING,
    CAP_STRUCTURED_OUTPUT,
    LlmRequest,
    MissingApiKeyError,
    ProviderError,
    ProviderResult,
)

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-opus-4-8"
API_KEY_ENV = "ANTHROPIC_API_KEY"
KEYCHAIN_SERVICE = "nutrime-anthropic"


def keychain_api_key(service: str = KEYCHAIN_SERVICE) -> str | None:
    """OS credential-store lookup — the no-plaintext-on-disk storage path.

    Store once with (macOS):
        security add-generic-password -U -s nutrime-anthropic -a "$USER" -w
    or (Windows):
        cmdkey /generic:nutrime-anthropic /user:%USERNAME% /pass
    Returns None when unsupported or no entry exists.
    """
    return credstore.read_secret(service)

_RETRYABLE_OUTCOMES = frozenset({"error_rate_limit", "error_provider", "error_timeout"})


def _classify_status(status: int) -> str:
    if status == 429:
        return "error_rate_limit"
    if status >= 500:  # includes 529 overloaded
        return "error_provider"
    return "error_validation"


class AnthropicProvider:
    name = "anthropic"
    capabilities = frozenset(
        {CAP_REASONING, CAP_STRUCTURED_OUTPUT, CAP_LONG_CONTEXT, CAP_CLOUD_PERMITTED}
    )

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        api_key: str | None = None,
        timeout_s: float = 120.0,
        max_retries: int = 2,
        backoff_base_s: float = 1.0,
        sleeper=time.sleep,
    ) -> None:
        self.model = model
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        self._backoff_base_s = backoff_base_s
        self._sleeper = sleeper

    def _resolve_api_key(self) -> str:
        key = (
            self._api_key
            or os.environ.get(API_KEY_ENV)
            or keychain_api_key()
        )
        if not key:
            raise MissingApiKeyError(
                f"no Anthropic API key: pass api_key=, set ${API_KEY_ENV},"
                f" or store one in the {credstore.backend_name()} (service"
                f" {KEYCHAIN_SERVICE!r}: {credstore.store_hint(KEYCHAIN_SERVICE)})"
            )
        return key

    def _post(self, payload: str) -> tuple[int, str]:
        """POST the serialized body; returns (status, response body).

        HTTP-level errors are returned as (status, body) rather than raised so
        the retry loop sees one shape. Network/timeout errors raise OSError.
        """
        request = urllib.request.Request(
            API_URL,
            data=payload.encode("utf-8"),
            headers={
                "x-api-key": self._resolve_api_key(),
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
                "user-agent": "NutriMe/0.0.1 (personal nutrition system)",
            },
            method="POST",
        )
        try:
            # redirects=False: the API never redirects, and urllib would
            # re-send x-api-key to any host a redirect named.
            with safe_urlopen(
                request, timeout=self._timeout_s, redirects=False
            ) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")

    def _build_payload(self, request: LlmRequest) -> str:
        body: dict = {
            "model": self.model,
            "max_tokens": request.max_tokens,
            "messages": [
                {"role": m.role, "content": m.content} for m in request.messages
            ],
        }
        if request.system is not None:
            body["system"] = request.system
        return json.dumps(body, ensure_ascii=False, sort_keys=True)

    def complete(self, request: LlmRequest) -> ProviderResult:
        payload = self._build_payload(request)
        retries = 0
        while True:
            outcome: str
            detail: str
            try:
                status, body = self._post(payload)
            except (TimeoutError, urllib.error.URLError, OSError) as exc:
                outcome = "error_timeout"
                detail = f"network error: {exc}"
            else:
                if status == 200:
                    return self._parse_success(body, payload, retries)
                outcome = _classify_status(status)
                detail = f"HTTP {status}: {body[:500]}"

            if outcome not in _RETRYABLE_OUTCOMES or retries >= self._max_retries:
                raise ProviderError(
                    outcome,
                    detail,
                    request_payload=payload,
                    retry_attempts=retries,
                )
            self._sleeper(self._backoff_base_s * (2**retries))
            retries += 1

    def _parse_success(
        self, body: str, payload: str, retries: int
    ) -> ProviderResult:
        try:
            parsed = json.loads(body)
            text = "".join(
                block.get("text", "")
                for block in parsed.get("content", [])
                if block.get("type") == "text"
            )
            usage = parsed.get("usage", {})
            return ProviderResult(
                text=text,
                model=parsed.get("model", self.model),
                stop_reason=parsed.get("stop_reason"),
                prompt_tokens=usage.get("input_tokens"),
                completion_tokens=usage.get("output_tokens"),
                request_payload=payload,
                response_payload=body,
                retry_attempts=retries,
            )
        except (ValueError, AttributeError, TypeError) as exc:
            raise ProviderError(
                "error_provider",
                f"unparseable success response: {exc}",
                request_payload=payload,
                retry_attempts=retries,
            ) from exc
