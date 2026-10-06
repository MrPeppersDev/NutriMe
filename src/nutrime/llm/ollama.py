"""Ollama local-model adapter — the A3/A1-v2 two-tier bridge.

The architecture's local tier (PHI-adjacent inference runs at home) was
designed for the ≥64 GB production host; this is the pragmatic bridge on
the 24 GB MVP host: an 8B-class model via the Ollama daemon on
localhost. Default model ``qwen3:8b`` (overridable via
``$NUTRIME_OLLAMA_MODEL``); daemon URL ``http://127.0.0.1:11434``
(overridable via ``$NUTRIME_OLLAMA_URL``).

Capability posture: this provider carries ``CAP_LOCAL_PRIVATE`` and NOT
``CAP_CLOUD_PERMITTED`` — the routing layer (client.py) requires
``CAP_LOCAL_PRIVATE`` for any request carrying PHI categories, so PHI
never routes to a cloud adapter even by misconfiguration (fail-closed:
no local provider registered → the PHI request errors, it never falls
back to cloud).

Error discipline differs from the cloud adapter on one point: a
connection-refused is NOT retried — a local daemon either runs or it
doesn't, and the error message says exactly how to start it. No API
key, no keychain: localhost needs neither.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from nutrime.llm.base import (
    CAP_LOCAL_PRIVATE,
    CAP_REASONING,
    CAP_STRUCTURED_OUTPUT,
    LlmRequest,
    ProviderError,
    ProviderResult,
)

DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:8b"
URL_ENV = "NUTRIME_OLLAMA_URL"
MODEL_ENV = "NUTRIME_OLLAMA_MODEL"

INSTALL_COMMAND = (
    "winget install Ollama.Ollama"
    if sys.platform == "win32"
    else "brew install ollama"
)

INSTALL_HINT = (
    "Ollama isn't reachable — the local model daemon isn't running."
    f" One-time setup: `{INSTALL_COMMAND}` then `ollama pull {DEFAULT_MODEL}`,"
    " then `ollama serve` (or launch the Ollama app)."
)


def _post(url: str, body: str, timeout: float) -> tuple[int, str]:
    """POST JSON; returns (status, response body). Monkeypatchable seam."""
    request = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return (response.status, response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return (err.code, err.read().decode("utf-8", "replace"))


@dataclass(frozen=True)
class OllamaProvider:
    """LlmProvider over the Ollama /api/chat endpoint (non-streaming)."""

    name: str = "ollama"
    base_url: str = ""
    model: str = ""
    timeout_s: float = 120.0
    # Thinking-capable models (qwen3) reason in a separate `thinking` field
    # that still spends `num_predict`: at the planner's 256-token budget they
    # were cut off mid-thought with empty `content` on every crossing. Our
    # calls are bounded selection/extraction tasks, so thinking stays off
    # unless a caller constructs the provider with think=True.
    think: bool = False
    capabilities: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {CAP_LOCAL_PRIVATE, CAP_REASONING, CAP_STRUCTURED_OUTPUT}
        )
    )

    def _resolved_url(self) -> str:
        return (
            self.base_url or os.environ.get(URL_ENV) or DEFAULT_URL
        ).rstrip("/")

    def _resolved_model(self) -> str:
        return self.model or os.environ.get(MODEL_ENV) or DEFAULT_MODEL

    def complete(self, request: LlmRequest) -> ProviderResult:
        messages = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.extend(
            {"role": m.role, "content": m.content} for m in request.messages
        )
        model = self._resolved_model()
        body = json.dumps(
            {
                "model": model,
                "messages": messages,
                "stream": False,
                "think": self.think,
                "options": {"num_predict": request.max_tokens},
            }
        )
        url = f"{self._resolved_url()}/api/chat"
        try:
            status, raw = _post(url, body, self.timeout_s)
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            # Local daemon down — fail fast with the setup hint, no retry.
            raise ProviderError(
                "error_timeout",
                f"{INSTALL_HINT} ({exc})",
                request_payload=body,
            ) from exc
        if status != 200:
            raise ProviderError(
                "error_provider",
                f"Ollama returned HTTP {status}: {raw[:300]}",
                request_payload=body,
            )
        try:
            payload = json.loads(raw)
            text = payload["message"]["content"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ProviderError(
                "error_validation",
                f"malformed Ollama response: {exc}",
                request_payload=body,
            ) from exc
        return ProviderResult(
            text=text,
            model=str(payload.get("model") or model),
            stop_reason=str(payload.get("done_reason") or "") or None,
            prompt_tokens=payload.get("prompt_eval_count"),
            completion_tokens=payload.get("eval_count"),
            request_payload=body,
            response_payload=raw,
        )


def is_available(base_url: str | None = None, *, timeout_s: float = 2.0) -> bool:
    """True when the daemon answers /api/tags. Never raises (status surface)."""
    url = (base_url or os.environ.get(URL_ENV) or DEFAULT_URL).rstrip("/")
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=timeout_s) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001 — any failure means "not available"
        return False
