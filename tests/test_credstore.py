"""OS credential store seam — macOS Keychain / Windows Credential Manager.

Platform dispatch and blob decoding are tested everywhere; the live
Credential Manager round-trip runs only on Windows (a uniquely named
throwaway entry, deleted afterwards).
"""

from __future__ import annotations

import subprocess
import sys
import uuid

import pytest

from nutrime import credstore


class TestDispatch:
    def test_unsupported_platform_reads_none(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        assert credstore.read("nutrime-anything") is None
        assert credstore.read_secret("nutrime-anything") is None

    def test_unsupported_platform_write_raises(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "linux")
        with pytest.raises(OSError):
            credstore.write("nutrime-anything", "me", "secret")

    def test_windows_read_error_is_swallowed(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "win32")

        def boom(service):
            raise OSError("advapi32 unavailable")

        monkeypatch.setattr(credstore, "_win_read", boom)
        assert credstore.read("nutrime-anything") is None

    def test_mac_dispatch(self, monkeypatch):
        monkeypatch.setattr(sys, "platform", "darwin")
        monkeypatch.setattr(credstore, "_mac_read", lambda s: ("me", "tok"))
        assert credstore.read_secret("nutrime-x") == "tok"

    def test_empty_secret_reads_as_none(self, monkeypatch):
        monkeypatch.setattr(credstore, "read", lambda s: ("me", ""))
        assert credstore.read_secret("nutrime-x") is None

    @pytest.mark.parametrize(
        ("platform", "label", "hint"),
        [
            ("darwin", "macOS Keychain", "security add-generic-password"),
            ("win32", "Windows Credential Manager", "cmdkey /generic:svc"),
        ],
    )
    def test_messages(self, monkeypatch, platform, label, hint):
        monkeypatch.setattr(sys, "platform", platform)
        assert credstore.backend_name() == label
        assert hint in credstore.store_hint("svc")


class TestDecodeBlob:
    def test_utf8(self):
        assert credstore._decode_blob("pina_abc123".encode("utf-8")) == "pina_abc123"

    def test_utf16_from_cmdkey(self):
        assert credstore._decode_blob("sk-ant-xyz".encode("utf-16-le")) == "sk-ant-xyz"


@pytest.mark.skipif(sys.platform != "win32", reason="Windows Credential Manager only")
class TestWindowsRoundTrip:
    def test_write_then_read_and_replace(self):
        service = f"nutrime-test-{uuid.uuid4().hex[:12]}"
        try:
            assert credstore.read(service) is None
            credstore.write(service, "tester", "first-secret")
            assert credstore.read(service) == ("tester", "first-secret")
            credstore.write(service, "tester", "second-secret")
            assert credstore.read_secret(service) == "second-secret"
        finally:
            subprocess.run(
                ["cmdkey", f"/delete:{service}"], capture_output=True, check=False
            )
