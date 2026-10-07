"""Typed request/response schema + provider protocol for the LLM layer.

The internal schema discipline from provider-abstraction.md: application code
constructs :class:`LlmRequest` and receives :class:`LlmResponse`; it never sees
a provider wire format. Adapters map both directions and declare a capability
vector so the routing layer can match requests to providers.

Outcome strings on :class:`ProviderError` are exactly the
``op_llm_request_log.outcome`` enum values from schema.md Q8.3, so the client
can log a failed call without translation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

DEFAULT_MAX_TOKENS = 1024

# Capability tags per provider-abstraction.md "Capability vector" (illustrative
# dimensions; the set grows as routing needs discrimination).
CAP_REASONING = "reasoning"
CAP_STRUCTURED_OUTPUT = "structured-output"
CAP_LONG_CONTEXT = "long-context"
CAP_CLOUD_PERMITTED = "cloud-permitted"
# A3/A1-v2 two-tier posture: providers carrying this run on-device and
# never egress. The client REQUIRES it for any PHI-tagged request.
CAP_LOCAL_PRIVATE = "local-private"
# Provider accepts images on messages (pin-photo recipe extraction, #24).
CAP_VISION = "vision"


@dataclass(frozen=True)
class ChatMessage:
    role: str  # 'user' | 'assistant'
    content: str
    # Raw image bytes attached to this message, base64-encoded by the
    # adapter. Routing must include CAP_VISION in required_capabilities
    # when any message carries images; text-only providers ignore none —
    # the client never hands them an image-bearing request.
    images: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class LlmRequest:
    """A provider-agnostic completion request.

    ``phi_categories`` declares what the payload carries; the client checks it
    against the query type's registered envelope pre-egress and enforces the
    S4-Q2 single-slice rule (multi-slice queries must be decomposed by the
    caller into single-slice calls + local aggregation).
    """

    query_type: str
    messages: tuple[ChatMessage, ...]
    system: str | None = None
    max_tokens: int = DEFAULT_MAX_TOKENS
    phi_categories: frozenset[str] = field(default_factory=frozenset)
    required_capabilities: frozenset[str] = field(default_factory=frozenset)
    caller_context: str | None = None


@dataclass(frozen=True)
class LlmResponse:
    request_id: str
    provider: str
    model: str
    text: str
    stop_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    latency_ms: int
    llm_request_log_id: str


@dataclass(frozen=True)
class ProviderResult:
    """What an adapter returns to the client on success.

    Carries the exact serialized request/response payloads so the client can
    write the ``op_llm_request_log`` row (hashes + optional inline storage)
    without re-deriving provider wire formats.
    """

    text: str
    model: str
    stop_reason: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    request_payload: str
    response_payload: str
    retry_attempts: int = 0


class ProviderError(Exception):
    """A provider call failed after the adapter's own retry policy ran out.

    ``outcome`` is one of the ``op_llm_request_log`` enum values:
    'error_provider' | 'error_timeout' | 'error_rate_limit' |
    'error_validation'.
    """

    def __init__(
        self,
        outcome: str,
        detail: str,
        *,
        request_payload: str,
        retry_attempts: int = 0,
    ) -> None:
        self.outcome = outcome
        self.detail = detail
        self.request_payload = request_payload
        self.retry_attempts = retry_attempts
        super().__init__(f"{outcome}: {detail}")


class MissingApiKeyError(RuntimeError):
    """Configuration error raised before any network egress is attempted."""


class LlmProvider(Protocol):
    name: str
    model: str
    capabilities: frozenset[str]

    def complete(self, request: LlmRequest) -> ProviderResult: ...
