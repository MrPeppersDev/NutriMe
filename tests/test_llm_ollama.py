"""Ollama local-tier adapter + PHI routing (A3/A1-v2 two-tier bridge)."""

import json

import pytest

from nutrime.audit import AuditLog
from nutrime.llm import ollama as ollama_mod
from nutrime.llm.base import (
    CAP_CLOUD_PERMITTED,
    CAP_LOCAL_PRIVATE,
    ChatMessage,
    LlmRequest,
    ProviderError,
    ProviderResult,
)
from nutrime.llm.client import LlmClient, LlmUnavailableError
from nutrime.llm.ollama import OllamaProvider, is_available
from nutrime.phi import PhiCategory, PhiEnvelopeRegistry
from nutrime.rules import default_rule_engine


def _ok_response(text="hello", model="qwen3:8b"):
    return (
        200,
        json.dumps(
            {
                "model": model,
                "message": {"role": "assistant", "content": text},
                "done_reason": "stop",
                "prompt_eval_count": 12,
                "eval_count": 5,
            }
        ),
    )


def _request(**kwargs):
    defaults = dict(
        query_type="test_q",
        messages=(ChatMessage(role="user", content="hi"),),
        system="be brief",
    )
    defaults.update(kwargs)
    return LlmRequest(**defaults)


class TestOllamaProvider:
    def test_request_mapping_and_response_parse(self, monkeypatch) -> None:
        captured = {}

        def fake_post(url, body, timeout):
            captured["url"] = url
            captured["body"] = json.loads(body)
            return _ok_response()

        monkeypatch.setattr(ollama_mod, "_post", fake_post)
        provider = OllamaProvider()
        result = provider.complete(_request())
        assert captured["url"].endswith("/api/chat")
        assert captured["body"]["stream"] is False
        # Thinking off by default — qwen3 otherwise exhausts num_predict in
        # the `thinking` field and returns empty content.
        assert captured["body"]["think"] is False
        assert captured["body"]["messages"][0] == {
            "role": "system", "content": "be brief",
        }
        assert captured["body"]["messages"][1]["content"] == "hi"
        assert isinstance(result, ProviderResult)
        assert result.text == "hello"
        assert result.prompt_tokens == 12

    def test_connection_refused_fails_fast_with_hint(self, monkeypatch) -> None:
        def fake_post(url, body, timeout):
            raise OSError("Connection refused")

        monkeypatch.setattr(ollama_mod, "_post", fake_post)
        with pytest.raises(ProviderError) as err:
            OllamaProvider().complete(_request())
        assert err.value.outcome == "error_timeout"
        assert ollama_mod.INSTALL_COMMAND in err.value.detail
        assert err.value.retry_attempts == 0

    @pytest.mark.parametrize(
        "exc",
        [
            TimeoutError("timed out"),
            ollama_mod.urllib.error.URLError(TimeoutError("timed out")),
        ],
    )
    def test_slow_model_timeout_is_not_reported_as_daemon_down(
        self, monkeypatch, exc
    ) -> None:
        # Seen live: qwen3:30b-a3b spilling past 16 GB VRAM hit the read
        # timeout and was misreported as "daemon isn't running".
        def fake_post(url, body, timeout):
            raise exc

        monkeypatch.setattr(ollama_mod, "_post", fake_post)
        with pytest.raises(ProviderError) as err:
            OllamaProvider().complete(_request())
        assert err.value.outcome == "error_timeout"
        assert "isn't running" not in err.value.detail
        assert "did not" in err.value.detail

    def test_http_error_classified_provider(self, monkeypatch) -> None:
        monkeypatch.setattr(
            ollama_mod, "_post", lambda u, b, t: (500, "boom")
        )
        with pytest.raises(ProviderError) as err:
            OllamaProvider().complete(_request())
        assert err.value.outcome == "error_provider"

    def test_malformed_json_classified_validation(self, monkeypatch) -> None:
        monkeypatch.setattr(
            ollama_mod, "_post", lambda u, b, t: (200, "not json")
        )
        with pytest.raises(ProviderError) as err:
            OllamaProvider().complete(_request())
        assert err.value.outcome == "error_validation"

    def test_model_env_override(self, monkeypatch) -> None:
        captured = {}

        def fake_post(url, body, timeout):
            captured["body"] = json.loads(body)
            return _ok_response(model="llama3:8b")

        monkeypatch.setattr(ollama_mod, "_post", fake_post)
        monkeypatch.setenv(ollama_mod.MODEL_ENV, "llama3:8b")
        OllamaProvider().complete(_request())
        assert captured["body"]["model"] == "llama3:8b"

    def test_is_available_never_raises(self) -> None:
        # Nothing listens on this port — must return False, not raise.
        assert is_available("http://127.0.0.1:1") is False

    def test_capabilities_local_not_cloud(self) -> None:
        provider = OllamaProvider()
        assert CAP_LOCAL_PRIVATE in provider.capabilities
        assert CAP_CLOUD_PERMITTED not in provider.capabilities


class _StubCloud:
    name = "anthropic"
    model = "claude-x"
    capabilities = frozenset({CAP_CLOUD_PERMITTED})

    def complete(self, request):
        return ProviderResult(
            text="cloud says hi", model=self.model, stop_reason="end",
            prompt_tokens=1, completion_tokens=1,
            request_payload="{}", response_payload="{}",
        )


class _StubLocal:
    name = "ollama"
    model = "qwen3:8b"
    capabilities = frozenset({CAP_LOCAL_PRIVATE})

    def complete(self, request):
        return ProviderResult(
            text="local says hi", model=self.model, stop_reason="stop",
            prompt_tokens=1, completion_tokens=1,
            request_payload="{}", response_payload="{}",
        )


@pytest.fixture
def client_parts(tmp_path):
    from nutrime.app import initialize

    from nutrime.audit import attach_pre_egress_audit

    app = initialize(data_dir=tmp_path)
    registry = PhiEnvelopeRegistry()
    registry.register("phi_free_q", ())
    registry.register("phi_q", (PhiCategory.DEMOGRAPHICS,))
    registry.register("clinical_q", (PhiCategory.LABS,))
    engine = default_rule_engine(registry)
    audit = AuditLog(app.operational)
    attach_pre_egress_audit(engine, audit)
    yield engine, audit
    app.substrate.close()
    app.operational.close()


class TestTwoTierRouting:
    def test_phi_routes_to_local(self, client_parts) -> None:
        engine, audit = client_parts
        client = LlmClient([_StubCloud(), _StubLocal()], engine, audit)
        response = client.complete(
            _request(
                query_type="phi_q",
                phi_categories=frozenset({"demographics"}),
            )
        )
        assert response.provider == "ollama"
        assert response.text == "local says hi"

    def test_clinical_phi_without_local_fails_closed(self, client_parts) -> None:
        engine, audit = client_parts
        client = LlmClient([_StubCloud()], engine, audit)
        with pytest.raises(
            LlmUnavailableError, match="never falls back to cloud"
        ):
            client.complete(
                _request(
                    query_type="clinical_q",
                    phi_categories=frozenset({"labs"}),
                )
            )

    def test_all_phi_refuses_cloud_local_mandatory(self, client_parts) -> None:
        # Direction reset 2026-10-06: CLOUD_TOLERATED_PHI is empty —
        # even demographics never crosses to a cloud-only stack.
        engine, audit = client_parts
        client = LlmClient([_StubCloud()], engine, audit)
        with pytest.raises(LlmUnavailableError, match="never falls back"):
            client.complete(
                _request(
                    query_type="phi_q",
                    phi_categories=frozenset({"demographics"}),
                )
            )

    def test_phi_free_still_prefers_cloud(self, client_parts) -> None:
        engine, audit = client_parts
        client = LlmClient([_StubCloud(), _StubLocal()], engine, audit)
        response = client.complete(_request(query_type="phi_free_q"))
        assert response.provider == "anthropic"

    def test_single_slice_guard_still_enforced(self, client_parts) -> None:
        from nutrime.llm.client import LlmDecompositionError

        engine, audit = client_parts
        client = LlmClient([_StubLocal()], engine, audit)
        with pytest.raises(LlmDecompositionError):
            client.complete(
                _request(
                    query_type="phi_q",
                    phi_categories=frozenset({"demographics", "labs"}),
                )
            )

    def test_local_crossing_audited_with_local_destination(
        self, client_parts
    ) -> None:
        engine, audit = client_parts
        client = LlmClient([_StubLocal()], engine, audit)
        client.complete(
            _request(
                query_type="phi_q",
                phi_categories=frozenset({"demographics"}),
            )
        )
        events = audit.events(event_kind="audit")
        assert any(
            "local:ollama" in str(e.payload.get("destination", ""))
            for e in events
        )
