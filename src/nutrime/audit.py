"""Operational audit persistence — writers + readers for the event-log family.

Closes issue #22 (Stage 6 sub-commit 5.1). Per ``schema.md`` S8 Q8.1–Q8.3 +
F9 Q3 (tenant lifecycle events) + constitutional Rule 8 (the system shows its
work):

- :class:`AuditLog` wraps the operational connection with typed writers for
  ``op_event_log`` (audit / epistemic-trail / system events) and
  ``op_llm_request_log`` (every LLM API call, with SHA-256 payload hashes and
  the Q8.2.e defense-in-depth ``CHECK (phi_categories = '[]')``).
- :func:`attach_pre_egress_audit` hooks the constitutional
  :class:`~nutrime.rules.RuleEngine` so **every** pre-egress crossing — allowed
  and blocked — records an audit event. The observer raises on write failure,
  which blocks the crossing: fail-closed, because an unaudited egress is the
  one history that cannot be backfilled.
- :meth:`AuditLog.ensure_tenant_created` is the F9 Q3 lifecycle wiring — a
  ``system/tenant_created`` event per tenant, idempotent so pre-5.1 installs
  are backfilled on the next ``initialize()``.

Payload storage follows the Q8.3 watch item: full request/response payloads are
stored inline only under :data:`PAYLOAD_STORE_THRESHOLD` characters; above it
only the hash is kept (threshold is a build-time judgment, revisit with cost
data).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterable, Mapping

from nutrime import __version__
from nutrime.db import maybe_commit
from nutrime.knowledge.ids import uuid7

if TYPE_CHECKING:
    from nutrime.rules import EgressRequest, RuleEngine, RuleResult

EVENT_KINDS = ("audit", "epistemic_trail", "system")
SUBJECT_TYPES = ("atom", "molecule", "synthesized", "relationship")
LLM_OUTCOMES = (
    "success",
    "error_provider",
    "error_timeout",
    "error_rate_limit",
    "error_validation",
)

# Q8.3 watch item: request/response payloads above this many characters are
# stored hash-only. Generous for MVP single-user volumes; revisit with cost
# data when op DB size becomes observable.
PAYLOAD_STORE_THRESHOLD = 65_536


def new_event_id() -> str:
    return f"evt-{uuid7()}"


def new_llm_request_id() -> str:
    return f"llr-{uuid7()}"


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


@dataclass(frozen=True)
class AuditEvent:
    id: str
    event_kind: str
    event_subkind: str | None
    request_id: str | None
    parent_event_id: str | None
    subject_id: str | None
    subject_type: str | None
    actor: str
    payload: dict
    phi_categories: tuple[str, ...]
    recorded_at: str


@dataclass(frozen=True)
class LlmRequestRecord:
    id: str
    request_id: str
    llm_provider: str
    llm_model: str
    request_payload_hash: str
    request_payload: str | None
    response_payload: str | None
    response_payload_hash: str
    prompt_tokens: int | None
    completion_tokens: int | None
    latency_ms: int | None
    retry_attempts: int
    outcome: str
    error_detail: str | None
    caller_context: str
    started_at: str
    completed_at: str | None
    recorded_at: str


class AuditLog:
    def __init__(
        self,
        conn: sqlite3.Connection,
        *,
        system_version: str = __version__,
        component_version: str = __version__,
    ) -> None:
        self._conn = conn
        self._system_version = system_version
        self._component_version = component_version

    def record_event(
        self,
        *,
        event_kind: str,
        actor: str,
        payload: Mapping[str, object],
        event_subkind: str | None = None,
        request_id: str | None = None,
        parent_event_id: str | None = None,
        subject_id: str | None = None,
        subject_type: str | None = None,
        phi_categories: Iterable[str] = (),
    ) -> str:
        if event_kind not in EVENT_KINDS:
            raise ValueError(
                f"event_kind {event_kind!r} not in {EVENT_KINDS}"
            )
        if subject_type is not None and subject_type not in SUBJECT_TYPES:
            raise ValueError(
                f"subject_type {subject_type!r} not in {SUBJECT_TYPES}"
            )
        event_id = new_event_id()
        self._conn.execute(
            """
            INSERT INTO op_event_log (
                id, event_kind, event_subkind, request_id, parent_event_id,
                subject_id, subject_type, actor, payload, phi_categories,
                recorded_at, system_version, component_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event_kind,
                event_subkind,
                request_id,
                parent_event_id,
                subject_id,
                subject_type,
                actor,
                json.dumps(dict(payload), ensure_ascii=False, sort_keys=True),
                json.dumps(sorted(set(phi_categories))),
                _now_iso(),
                self._system_version,
                self._component_version,
            ),
        )
        maybe_commit(self._conn)
        return event_id

    def record_llm_request(
        self,
        *,
        request_id: str,
        llm_provider: str,
        llm_model: str,
        request_payload: str,
        outcome: str,
        caller_context: str,
        started_at: str,
        response_payload: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_cost_usd: float | None = None,
        latency_ms: int | None = None,
        retry_attempts: int = 0,
        error_detail: str | None = None,
        completed_at: str | None = None,
        payload_store_threshold: int = PAYLOAD_STORE_THRESHOLD,
    ) -> str:
        """Write one row per LLM API call.

        There is deliberately no ``phi_categories`` parameter: cloud LLM calls
        never carry PHI by routing rule (phi-handling.md), the column is always
        ``'[]'``, and the schema CHECK enforces the same fail-closed.
        """
        if outcome not in LLM_OUTCOMES:
            raise ValueError(f"outcome {outcome!r} not in {LLM_OUTCOMES}")
        record_id = new_llm_request_id()
        stored_request = (
            request_payload
            if len(request_payload) <= payload_store_threshold
            else None
        )
        stored_response = (
            response_payload
            if response_payload is not None
            and len(response_payload) <= payload_store_threshold
            else None
        )
        self._conn.execute(
            """
            INSERT INTO op_llm_request_log (
                id, request_id, llm_provider, llm_model,
                request_payload_hash, request_payload,
                response_payload, response_payload_hash,
                prompt_tokens, completion_tokens, total_cost_usd, latency_ms,
                retry_attempts, outcome, error_detail, phi_categories,
                caller_context, started_at, completed_at, recorded_at,
                system_version, component_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                request_id,
                llm_provider,
                llm_model,
                sha256_hex(request_payload),
                stored_request,
                stored_response,
                sha256_hex(response_payload or ""),
                prompt_tokens,
                completion_tokens,
                total_cost_usd,
                latency_ms,
                retry_attempts,
                outcome,
                error_detail,
                "[]",
                caller_context,
                started_at,
                completed_at,
                _now_iso(),
                self._system_version,
                self._component_version,
            ),
        )
        maybe_commit(self._conn)
        return record_id

    def events(
        self,
        *,
        event_kind: str | None = None,
        request_id: str | None = None,
        limit: int = 50,
    ) -> list[AuditEvent]:
        clauses: list[str] = []
        params: list[object] = []
        if event_kind is not None:
            clauses.append("event_kind = ?")
            params.append(event_kind)
        if request_id is not None:
            clauses.append("request_id = ?")
            params.append(request_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        rows = self._conn.execute(
            f"""
            SELECT id, event_kind, event_subkind, request_id, parent_event_id,
                   subject_id, subject_type, actor, payload, phi_categories,
                   recorded_at
            FROM op_event_log {where}
            ORDER BY recorded_at DESC, id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [
            AuditEvent(
                id=row[0],
                event_kind=row[1],
                event_subkind=row[2],
                request_id=row[3],
                parent_event_id=row[4],
                subject_id=row[5],
                subject_type=row[6],
                actor=row[7],
                payload=json.loads(row[8]),
                phi_categories=tuple(json.loads(row[9])),
                recorded_at=row[10],
            )
            for row in rows
        ]

    def llm_requests(self, *, limit: int = 50) -> list[LlmRequestRecord]:
        rows = self._conn.execute(
            """
            SELECT id, request_id, llm_provider, llm_model,
                   request_payload_hash, request_payload,
                   response_payload, response_payload_hash,
                   prompt_tokens, completion_tokens, latency_ms,
                   retry_attempts, outcome, error_detail, caller_context,
                   started_at, completed_at, recorded_at
            FROM op_llm_request_log
            ORDER BY recorded_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [LlmRequestRecord(*row) for row in rows]

    def ensure_tenant_created(self, tenant_id: str) -> str | None:
        """F9 Q3 lifecycle wiring — idempotent ``system/tenant_created`` event.

        Returns the new event id, or ``None`` when the event already exists
        (covers both repeat ``initialize()`` calls and the backfill case for
        tenants bootstrapped before 5.1 landed).
        """
        existing = self._conn.execute(
            """
            SELECT id FROM op_event_log
            WHERE event_kind = 'system' AND event_subkind = 'tenant_created'
              AND subject_id = ?
            """,
            (tenant_id,),
        ).fetchone()
        if existing is not None:
            return None
        return self.record_event(
            event_kind="system",
            event_subkind="tenant_created",
            actor="system",
            subject_id=tenant_id,
            payload={"tenant_id": tenant_id},
        )


def attach_pre_egress_audit(engine: "RuleEngine", audit: AuditLog) -> None:
    """Register the #22 observer: one audit event per crossing, both verdicts.

    The observer lets write failures propagate — the rule engine treats an
    observer exception as a blocked crossing, so egress can never outrun its
    audit row.
    """

    def _observer(request: "EgressRequest", result: "RuleResult") -> None:
        audit.record_event(
            event_kind="audit",
            event_subkind=(
                "pre_egress_allowed" if result.allowed else "pre_egress_blocked"
            ),
            actor="system",
            request_id=request.request_id,
            payload={
                "destination": request.destination,
                "query_type": request.query_type,
                "rule_name": result.rule_name,
                "reason": result.reason,
                "payload_sha256": sha256_hex(request.payload),
                "payload_chars": len(request.payload),
            },
            phi_categories=request.phi_categories,
        )

    engine.add_observer(_observer)
