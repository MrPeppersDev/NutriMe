"""LlmClient — the one gate every LLM call goes through.

Pipeline per S4-Q2 + issue #22 (both landed before this module by design):

    LlmRequest
      -> S4-Q2 single-slice guard (multi-PHI-slice queries must be decomposed
         by the caller into single-slice calls + local aggregation)
      -> capability-vector provider selection (provider-abstraction.md)
      -> EgressRequest through the constitutional RuleEngine (PHI envelope +
         prompt-injection guard; every verdict audited by the 5.1 observer)
      -> provider adapter call (adapter owns retry policy)
      -> op_llm_request_log row via AuditLog (success AND failure — the row
         is written before the caller sees the result)
      -> LlmResponse

A blocked crossing writes only the pre_egress_blocked audit event — no
op_llm_request_log row, because nothing crossed.
"""

from __future__ import annotations

import time
from typing import Iterable

from nutrime.audit import AuditLog, _now_iso
from nutrime.knowledge.ids import uuid7
from nutrime.llm.base import (
    CAP_LOCAL_PRIVATE,
    LlmProvider,
    LlmRequest,
    LlmResponse,
    ProviderError,
)
from nutrime.llm.ollama import DEFAULT_MODEL, INSTALL_COMMAND
from nutrime.rules import EgressRequest, RuleEngine

# Local-mandatory (product-direction reset 2026-10-06): NO PHI category
# may cross to cloud, ever — the switch the 5.2 envelope design
# anticipated is flipped. Any PHI-tagged request requires a
# local-private provider, fail-closed. Cloud providers remain usable
# only for fully PHI-free work, and only when explicitly registered.
CLOUD_TOLERATED_PHI: frozenset[str] = frozenset()


class LlmUnavailableError(RuntimeError):
    """No registered provider satisfies the request's capability vector."""


class LlmDecompositionError(ValueError):
    """Request carries more than one PHI category in a single crossing.

    Per S4-Q2: cloud-bound queries are decomposed so no single query carries
    a combined health profile. The envelope declares the union a query type
    may touch; each crossing carries at most one slice.
    """


def new_request_id() -> str:
    return f"req-{uuid7()}"


class LlmClient:
    def __init__(
        self,
        providers: Iterable[LlmProvider],
        rule_engine: RuleEngine,
        audit: AuditLog,
    ) -> None:
        self._providers: tuple[LlmProvider, ...] = tuple(providers)
        self._rule_engine = rule_engine
        self._audit = audit

    def select_provider(
        self, required_capabilities: frozenset[str]
    ) -> LlmProvider:
        for provider in self._providers:
            if required_capabilities <= provider.capabilities:
                return provider
        raise LlmUnavailableError(
            "no provider satisfies capabilities"
            f" {sorted(required_capabilities)!r}; registered:"
            f" {[p.name for p in self._providers]!r}"
        )

    def complete(self, request: LlmRequest) -> LlmResponse:
        if len(request.phi_categories) > 1:
            raise LlmDecompositionError(
                f"query type {request.query_type!r} attempted a single crossing"
                f" with {len(request.phi_categories)} PHI categories"
                f" ({sorted(request.phi_categories)}); decompose into"
                " single-slice calls + local aggregation per S4-Q2"
            )
        # A3/A1-v2 two-tier routing. Policy:
        # - any PHI-tagged request PREFERS a local-private provider when
        #   one is registered (all PHI stays home once the local tier is
        #   installed);
        # - categories outside CLOUD_TOLERATED_PHI hard-REQUIRE local —
        #   no local provider means fail-closed with setup guidance,
        #   never a cloud fallback;
        # - demographics is the one category the 5.4 S4-Q2 decomposition
        #   explicitly legalized for a cloud crossing (single-slice,
        #   envelope-declared), so it alone may still cross to cloud on
        #   hosts without the local tier. PHI-free requests keep the
        #   existing cloud-primary selection untouched.
        required = request.required_capabilities
        if request.phi_categories:
            sensitive = {
                str(c) for c in request.phi_categories
            } - CLOUD_TOLERATED_PHI
            try:
                provider = self.select_provider(
                    required | {CAP_LOCAL_PRIVATE}
                )
            except LlmUnavailableError:
                if sensitive:
                    # The envelope verdict outranks routing: an illegal
                    # category must surface as PreEgressViolation (the
                    # 5.1/5.2 contract), not as a missing-provider error.
                    self._rule_engine.evaluate_pre_egress(
                        EgressRequest(
                            destination="local:unavailable",
                            query_type=request.query_type,
                            payload="\n".join(
                                part
                                for part in [request.system or ""]
                                + [m.content for m in request.messages]
                                if part
                            ),
                            phi_categories=request.phi_categories,
                        )
                    )
                    raise LlmUnavailableError(
                        f"query type {request.query_type!r} carries"
                        f" sensitive PHI ({sorted(sensitive)}) which"
                        " requires a local-private model, and none is"
                        " registered. Install the local tier"
                        f" ({INSTALL_COMMAND}; ollama pull {DEFAULT_MODEL};"
                        " ollama serve) — this data never falls back to cloud."
                    ) from None
                provider = self.select_provider(required)
        else:
            provider = self.select_provider(required)
        request_id = new_request_id()

        # The egress payload the rule engine scans is the user-influenced
        # content (system + messages), not the full wire body — that's what
        # prompt-injection patterns need to see.
        egress_payload_parts = [request.system or ""] + [
            m.content for m in request.messages
        ]
        self._rule_engine.evaluate_pre_egress(
            EgressRequest(
                destination=(
                    f"local:{provider.name}"
                    if CAP_LOCAL_PRIVATE in provider.capabilities
                    else f"cloud:{provider.name}"
                ),
                query_type=request.query_type,
                payload="\n".join(part for part in egress_payload_parts if part),
                phi_categories=request.phi_categories,
                request_id=request_id,
            )
        )

        caller_context = request.caller_context or request.query_type
        started_at = _now_iso()
        t0 = time.perf_counter()
        try:
            result = provider.complete(request)
        except ProviderError as exc:
            self._audit.record_llm_request(
                request_id=request_id,
                llm_provider=provider.name,
                llm_model=provider.model,
                request_payload=exc.request_payload,
                outcome=exc.outcome,
                error_detail=exc.detail,
                retry_attempts=exc.retry_attempts,
                caller_context=caller_context,
                started_at=started_at,
                completed_at=_now_iso(),
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )
            raise

        latency_ms = int((time.perf_counter() - t0) * 1000)
        log_id = self._audit.record_llm_request(
            request_id=request_id,
            llm_provider=provider.name,
            llm_model=result.model,
            request_payload=result.request_payload,
            response_payload=result.response_payload,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            latency_ms=latency_ms,
            retry_attempts=result.retry_attempts,
            outcome="success",
            caller_context=caller_context,
            started_at=started_at,
            completed_at=_now_iso(),
        )
        return LlmResponse(
            request_id=request_id,
            provider=provider.name,
            model=result.model,
            text=result.text,
            stop_reason=result.stop_reason,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            latency_ms=latency_ms,
            llm_request_log_id=log_id,
        )
