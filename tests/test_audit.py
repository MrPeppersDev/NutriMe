"""Sub-commit 5.1 — operational audit persistence (issue #22).

Covers the event-log family migration, the AuditLog writers/readers, the
Q8.2.e PHI defense-in-depth CHECK, the pre-egress observer wiring (allowed and
blocked crossings both audited; audit failure blocks egress), the F9 Q3
tenant_created lifecycle event, and the app/CLI surfaces.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from nutrime.audit import (
    PAYLOAD_STORE_THRESHOLD,
    AuditLog,
    attach_pre_egress_audit,
    new_event_id,
    new_llm_request_id,
    sha256_hex,
)
from nutrime.db import apply_migrations, connect
from nutrime.paths import default_operational_migrations_dir
from nutrime.phi import PhiCategory, PhiEnvelopeRegistry, PhiEnvelopeRule
from nutrime.rules import EgressRequest, PreEgressViolation, RuleEngine


@pytest.fixture()
def op_conn(tmp_path):
    conn = connect(tmp_path / "operational.db")
    apply_migrations(conn, default_operational_migrations_dir())
    yield conn
    conn.close()


@pytest.fixture()
def audit(op_conn):
    return AuditLog(op_conn)


def _tables(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    return {row[0] for row in rows}


class TestMigration:
    def test_event_log_family_tables_created(self, op_conn):
        tables = _tables(op_conn)
        assert "op_event_log" in tables
        assert "op_llm_request_log" in tables

    def test_reapply_is_noop(self, op_conn):
        applied = apply_migrations(op_conn, default_operational_migrations_dir())
        assert applied == []


class TestIds:
    def test_prefixes(self):
        assert new_event_id().startswith("evt-")
        assert new_llm_request_id().startswith("llr-")


class TestRecordEvent:
    def test_round_trip(self, audit):
        event_id = audit.record_event(
            event_kind="audit",
            event_subkind="data_write",
            actor="user",
            request_id="req-1",
            subject_id="atm-x",
            subject_type="atom",
            payload={"field": "value"},
            phi_categories=["allergens"],
        )
        assert event_id.startswith("evt-")
        [event] = audit.events(request_id="req-1")
        assert event.id == event_id
        assert event.event_kind == "audit"
        assert event.event_subkind == "data_write"
        assert event.subject_type == "atom"
        assert event.payload == {"field": "value"}
        assert event.phi_categories == ("allergens",)

    def test_rejects_unknown_event_kind(self, audit):
        with pytest.raises(ValueError, match="event_kind"):
            audit.record_event(
                event_kind="telemetry", actor="system", payload={}
            )

    def test_rejects_unknown_subject_type(self, audit):
        with pytest.raises(ValueError, match="subject_type"):
            audit.record_event(
                event_kind="system",
                actor="system",
                payload={},
                subject_type="tenant",
            )

    def test_filter_by_kind_and_limit(self, audit):
        for n in range(3):
            audit.record_event(
                event_kind="system", actor="system", payload={"n": n}
            )
        audit.record_event(event_kind="audit", actor="system", payload={})
        assert len(audit.events(event_kind="system")) == 3
        assert len(audit.events(event_kind="system", limit=2)) == 2
        assert len(audit.events()) == 4


class TestRecordLlmRequest:
    def _record(self, audit, **overrides):
        kwargs = dict(
            request_id="req-llm-1",
            llm_provider="anthropic",
            llm_model="claude-x",
            request_payload='{"messages": []}',
            response_payload='{"content": "ok"}',
            outcome="success",
            caller_context="meal_plan_generation",
            started_at="2026-08-08T00:00:00.000Z",
        )
        kwargs.update(overrides)
        return audit.record_llm_request(**kwargs)

    def test_round_trip_with_hashes(self, audit):
        record_id = self._record(audit)
        assert record_id.startswith("llr-")
        [record] = audit.llm_requests()
        assert record.request_payload == '{"messages": []}'
        assert record.request_payload_hash == sha256_hex('{"messages": []}')
        assert record.response_payload_hash == sha256_hex('{"content": "ok"}')
        assert record.outcome == "success"

    def test_oversize_payload_stored_hash_only(self, audit):
        big = "x" * (PAYLOAD_STORE_THRESHOLD + 1)
        self._record(audit, request_payload=big)
        [record] = audit.llm_requests()
        assert record.request_payload is None
        assert record.request_payload_hash == sha256_hex(big)

    def test_rejects_unknown_outcome(self, audit):
        with pytest.raises(ValueError, match="outcome"):
            self._record(audit, outcome="partial")

    def test_phi_check_constraint_fail_closed(self, op_conn):
        # Q8.2.e defense-in-depth: the schema itself rejects any non-empty
        # phi_categories on an LLM request row, bypassing the Python layer.
        with pytest.raises(sqlite3.IntegrityError):
            op_conn.execute(
                """
                INSERT INTO op_llm_request_log (
                    id, request_id, llm_provider, llm_model,
                    request_payload_hash, response_payload_hash,
                    outcome, phi_categories, caller_context,
                    started_at, recorded_at, system_version, component_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "llr-test", "req", "anthropic", "claude-x",
                    "h", "h",
                    "success", json.dumps(["allergens"]), "test",
                    "t", "t", "0.0.1", "0.0.1",
                ),
            )


class TestPreEgressObserver:
    def _engine_with_envelope(self):
        registry = PhiEnvelopeRegistry()
        registry.register("recipe_search", ())
        registry.register(
            "meal_plan_generation", (PhiCategory.ALLERGENS,)
        )
        engine = RuleEngine()
        engine.register(PhiEnvelopeRule(registry))
        return engine

    def test_allowed_crossing_audited(self, audit):
        engine = self._engine_with_envelope()
        attach_pre_egress_audit(engine, audit)
        engine.evaluate_pre_egress(
            EgressRequest(
                destination="cloud:anthropic",
                query_type="recipe_search",
                payload="chicken dinner ideas",
                request_id="req-ok",
            )
        )
        [event] = audit.events(request_id="req-ok")
        assert event.event_subkind == "pre_egress_allowed"
        assert event.payload["query_type"] == "recipe_search"
        assert event.payload["payload_sha256"] == sha256_hex(
            "chicken dinner ideas"
        )

    def test_blocked_crossing_audited_and_raises(self, audit):
        engine = self._engine_with_envelope()
        attach_pre_egress_audit(engine, audit)
        with pytest.raises(PreEgressViolation):
            engine.evaluate_pre_egress(
                EgressRequest(
                    destination="cloud:anthropic",
                    query_type="unregistered_type",
                    payload="anything",
                    request_id="req-blocked",
                )
            )
        [event] = audit.events(request_id="req-blocked")
        assert event.event_subkind == "pre_egress_blocked"
        assert event.payload["rule_name"] == "phi-envelope"

    def test_audit_write_failure_blocks_egress(self, op_conn, audit):
        # Fail-closed: if the audit row cannot be written, the crossing must
        # not proceed silently.
        engine = self._engine_with_envelope()
        attach_pre_egress_audit(engine, audit)
        op_conn.execute("DROP TABLE op_event_log")
        with pytest.raises(sqlite3.OperationalError):
            engine.evaluate_pre_egress(
                EgressRequest(
                    destination="cloud:anthropic",
                    query_type="recipe_search",
                    payload="x",
                )
            )


class TestTenantLifecycle:
    def test_ensure_tenant_created_idempotent(self, audit):
        first = audit.ensure_tenant_created("tenant-123")
        assert first is not None
        assert audit.ensure_tenant_created("tenant-123") is None
        events = audit.events(event_kind="system")
        assert len(events) == 1
        assert events[0].event_subkind == "tenant_created"
        assert events[0].subject_id == "tenant-123"


class TestAppWiring:
    def test_initialize_records_tenant_created_and_audits_egress(self, tmp_path):
        from nutrime.app import initialize

        app = initialize(data_dir=tmp_path / "data")
        events = app.audit.events(event_kind="system")
        assert any(
            e.event_subkind == "tenant_created" and e.subject_id == app.tenant_id
            for e in events
        )

        # A second initialize must not duplicate the lifecycle event.
        app2 = initialize(data_dir=tmp_path / "data")
        assert len(app2.audit.events(event_kind="system")) == 1

        # Egress through the app-carried engine writes an audit row
        # (blocked here: fail-closed on the unregistered query type).
        with pytest.raises(PreEgressViolation):
            app2.rule_engine.evaluate_pre_egress(
                EgressRequest(
                    destination="cloud:anthropic",
                    query_type="never_registered",
                    payload="x",
                    request_id="req-app",
                )
            )
        [event] = app2.audit.events(request_id="req-app")
        assert event.event_subkind == "pre_egress_blocked"


class TestCli:
    def test_audit_list_empty_then_populated(self, tmp_path, capsys):
        from nutrime.cli import main

        data_dir = str(tmp_path / "data")
        assert main(["audit", "list", "--data-dir", data_dir]) == 0
        out = capsys.readouterr().out
        # tenant_created lands during initialize, so the list is never
        # actually empty after first run.
        assert "system/tenant_created" in out

    def test_audit_list_kind_filter(self, tmp_path, capsys):
        from nutrime.app import initialize
        from nutrime.cli import main

        data_dir = tmp_path / "data"
        app = initialize(data_dir=data_dir)
        app.audit.record_event(
            event_kind="audit", actor="system", payload={"marker": "abc123"}
        )
        assert main(
            ["audit", "list", "--kind", "audit", "--data-dir", str(data_dir)]
        ) == 0
        out = capsys.readouterr().out
        assert "marker=abc123" in out
        assert "tenant_created" not in out
