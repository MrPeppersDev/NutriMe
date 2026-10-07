"""Tests for shared web-source plumbing (recipes/web.py)."""

from __future__ import annotations

from nutrime.recipes.web import (
    USER_AGENT,
    Pacer,
    extract_list_items,
    now_iso,
    parse_duration_minutes,
    strip_tags,
)


class TestStripTags:
    def test_flattens_nested_markup(self):
        fragment = "<div><span>1</span> <em>cup</em> <b>flour</b></div>"
        assert strip_tags(fragment) == "1 cup flour"

    def test_unescapes_entities_and_collapses_whitespace(self):
        fragment = "salt&nbsp;&amp;   pepper\n\n  to taste"
        assert strip_tags(fragment) == "salt & pepper to taste"

    def test_empty_fragment(self):
        assert strip_tags("  <p> </p> ") == ""


class TestExtractListItems:
    def test_extracts_each_li(self):
        fragment = "<li>1 C sour cream</li><li>2 tsp dill</li>"
        assert extract_list_items(fragment) == [
            "1 C sour cream",
            "2 tsp dill",
        ]

    def test_skips_empty_items_and_strips_inner_tags(self):
        fragment = "<li class='x'>  <span>a</span>  </li><li></li>"
        assert extract_list_items(fragment) == ["a"]


class TestParseDurationMinutes:
    def test_minutes_only(self):
        assert parse_duration_minutes("10 minutes") == 10

    def test_hours_and_minutes(self):
        assert parse_duration_minutes("1 hour 15 minutes") == 75

    def test_hr_abbreviation(self):
        assert parse_duration_minutes("2 hrs") == 120

    def test_unparseable_returns_none(self):
        assert parse_duration_minutes("overnight") is None
        assert parse_duration_minutes("") is None


class TestPacer:
    def test_waits_with_injected_sleep(self):
        calls: list[float] = []
        pacer = Pacer(delay_s=0.5, sleep=calls.append)
        pacer.wait()
        pacer.wait()
        assert calls == [0.5, 0.5]

    def test_zero_delay_never_sleeps(self):
        calls: list[float] = []
        pacer = Pacer(delay_s=0.0, sleep=calls.append)
        pacer.wait()
        assert calls == []


class TestConstants:
    def test_user_agent_is_descriptive(self):
        assert "NutriMe" in USER_AGENT
        assert "github.com/MrPeppersDev/NutriMe" in USER_AGENT

    def test_now_iso_shape(self):
        stamp = now_iso()
        assert stamp.endswith("Z")
        assert "T" in stamp


class TestSsrfGuard:
    def test_localhost_refused(self) -> None:
        from nutrime.recipes.web import UnsafeUrlError, check_url_safety

        import pytest

        for url in (
            "http://127.0.0.1/admin",
            "http://localhost:8765/api/inventory",
            "http://169.254.169.254/latest/meta-data/",
            "file:///etc/passwd",
        ):
            with pytest.raises(UnsafeUrlError):
                check_url_safety(url)

    def test_private_ranges_refused(self) -> None:
        from nutrime.recipes.web import UnsafeUrlError, check_url_safety

        import pytest

        for url in ("http://10.0.0.5/x", "http://192.168.1.1/x"):
            with pytest.raises(UnsafeUrlError):
                check_url_safety(url)

    def test_public_host_passes(self) -> None:
        from nutrime.recipes.web import check_url_safety

        # Resolves live; example.com is stable public infrastructure.
        check_url_safety("https://example.com/recipe")


class TestRedirectGuards:
    """The SSRF check must hold on every hop, not just the first URL."""

    def _redirect_args(self, newurl: str):
        import io
        import urllib.request
        from email.message import Message

        req = urllib.request.Request("https://example.com/start")
        return (req, io.BytesIO(b""), 302, "Found", Message(), newurl)

    def test_redirect_to_internal_refused(self) -> None:
        import pytest

        from nutrime.recipes.web import UnsafeUrlError, _SafeRedirectHandler

        handler = _SafeRedirectHandler()
        for newurl in (
            "http://127.0.0.1:8765/api/profile",
            "http://169.254.169.254/latest/meta-data/",
        ):
            with pytest.raises(UnsafeUrlError):
                handler.redirect_request(*self._redirect_args(newurl))

    def test_redirect_to_public_allowed(self) -> None:
        from nutrime.recipes.web import _SafeRedirectHandler

        handler = _SafeRedirectHandler()
        result = handler.redirect_request(
            *self._redirect_args("https://example.com/moved")
        )
        assert result is not None
        assert result.full_url == "https://example.com/moved"

    def test_authenticated_requests_never_follow_redirects(self) -> None:
        import pytest

        from nutrime.recipes.web import UnsafeUrlError, _NoRedirectHandler

        handler = _NoRedirectHandler()
        # Even a safe public target is refused: urllib would re-send the
        # Authorization header to it.
        with pytest.raises(UnsafeUrlError):
            handler.redirect_request(
                *self._redirect_args("https://example.com/moved")
            )

    def test_safe_urlopen_rejects_unsafe_initial_url(self) -> None:
        import pytest

        from nutrime.recipes.web import UnsafeUrlError, safe_urlopen

        with pytest.raises(UnsafeUrlError):
            safe_urlopen("http://127.0.0.1:8765/api/profile")
