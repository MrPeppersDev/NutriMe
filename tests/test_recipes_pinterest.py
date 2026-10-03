"""Pinterest board sync — pagination, link triage, hand-off to jsonld ingest."""

import json
from pathlib import Path

import pytest

from nutrime.recipes.pinterest import (
    MissingTokenError,
    Pin,
    PinterestClient,
    _is_ingestible_link,
    resolve_token,
    sync_pins,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer


def _recipe_page(name: str) -> str:
    node = {
        "@type": "Recipe",
        "name": name,
        "recipeIngredient": ["1 lb thing"],
        "recipeInstructions": "Cook the thing.",
        "recipeYield": "2",
    }
    return (
        '<script type="application/ld+json">' + json.dumps(node) + "</script>"
    )


def _pin_item(pin_id: str, link: str, title: str = "") -> dict:
    return {"id": pin_id, "link": link, "title": title, "board_id": "b1"}


class _FakeApi:
    """Bookmark-paginated /pins + /boards fixture."""

    def __init__(self, pin_pages: list[list[dict]], boards: list[dict] | None = None):
        self.pin_pages = pin_pages
        self.boards = boards or []
        self.calls: list[str] = []

    def __call__(self, url: str, token: str) -> dict:
        self.calls.append(url)
        assert token == "tkn"
        if "/boards?" in url or url.endswith("/boards"):
            return {"items": self.boards, "bookmark": None}
        # pins (account-wide or per-board): serve pages in order
        page_index = sum("pins" in c for c in self.calls[:-1])
        items = self.pin_pages[page_index]
        more = page_index + 1 < len(self.pin_pages)
        return {"items": items, "bookmark": f"pg{page_index + 1}" if more else None}


class TestTokenResolution:
    def test_explicit_wins(self) -> None:
        assert resolve_token("abc") == "abc"

    def test_env_fallback(self, monkeypatch) -> None:
        monkeypatch.setenv("PINTEREST_ACCESS_TOKEN", "from-env")
        assert resolve_token() == "from-env"

    def test_missing_raises_with_guidance(self, monkeypatch) -> None:
        monkeypatch.delenv("PINTEREST_ACCESS_TOKEN", raising=False)
        monkeypatch.setattr(
            "nutrime.recipes.pinterest.keychain_token", lambda: None
        )
        with pytest.raises(MissingTokenError, match="nutrime-pinterest"):
            resolve_token()


class TestLinkTriage:
    def test_external_https_ok(self) -> None:
        assert _is_ingestible_link("https://blog.example.com/stew")

    def test_pinterest_internal_rejected(self) -> None:
        assert not _is_ingestible_link("https://www.pinterest.com/pin/123/")
        assert not _is_ingestible_link("https://pinterest.com/pin/123/")

    def test_empty_and_non_http_rejected(self) -> None:
        assert not _is_ingestible_link("")
        assert not _is_ingestible_link("ftp://x/y")


class TestClientPagination:
    def test_iter_pins_walks_bookmarks(self) -> None:
        api = _FakeApi(
            [
                [_pin_item("1", "https://a.example.com/r1")],
                [_pin_item("2", "https://b.example.com/r2")],
            ]
        )
        client = PinterestClient(token="tkn", fetcher=api)
        pins = list(client.iter_pins())
        assert [p.pin_id for p in pins] == ["1", "2"]
        assert sum("bookmark=pg1" in c for c in api.calls) == 1

    def test_board_id_by_name_case_insensitive(self) -> None:
        api = _FakeApi([[]], boards=[{"id": "b9", "name": "Dinner Ideas"}])
        client = PinterestClient(token="tkn", fetcher=api)
        assert client.board_id_by_name("dinner ideas") == "b9"
        assert client.board_id_by_name("nope") is None


class TestSyncPins:
    def _vault(self, tmp_path: Path) -> RecipeVault:
        vault = RecipeVault(tmp_path / "corpus")
        vault.ensure()
        return vault

    def _pacer(self) -> Pacer:
        return Pacer(delay_s=0, sleep=lambda _: None)

    def test_end_to_end_counts(self, tmp_path: Path) -> None:
        api = _FakeApi(
            [
                [
                    _pin_item("1", "https://a.example.com/r1"),
                    _pin_item("2", ""),  # image-only pin
                    _pin_item("3", "https://www.pinterest.com/pin/3/"),
                    _pin_item("4", "https://a.example.com/r1"),  # dup link
                    _pin_item("5", "https://b.example.com/r2"),
                ]
            ]
        )
        client = PinterestClient(token="tkn", fetcher=api, pacer=self._pacer())
        pages = {
            "https://a.example.com/r1": _recipe_page("Pin Stew"),
            "https://b.example.com/r2": _recipe_page("Pin Salad"),
        }
        outcome = sync_pins(
            client,
            self._vault(tmp_path),
            page_fetcher=lambda url: pages[url],
            pacer=self._pacer(),
        )
        assert outcome.pins_seen == 5
        assert outcome.pins_with_links == 2
        assert outcome.pins_without_links == 2  # empty link + pinterest-internal
        assert outcome.written == 2

    def test_resync_skips_already_ingested(self, tmp_path: Path) -> None:
        vault = self._vault(tmp_path)
        api_pages = [[_pin_item("1", "https://a.example.com/r1")]]
        pages = {"https://a.example.com/r1": _recipe_page("Pin Stew")}

        for _ in range(2):
            client = PinterestClient(
                token="tkn", fetcher=_FakeApi(list(api_pages)), pacer=self._pacer()
            )
            outcome = sync_pins(
                client,
                vault,
                page_fetcher=lambda url: pages[url],
                pacer=self._pacer(),
            )
        assert outcome.written == 0
        assert len(outcome.ingest.skipped_upstream_ids) == 1
        assert vault.count() == 1

    def test_unknown_board_raises(self, tmp_path: Path) -> None:
        api = _FakeApi([[]], boards=[])
        client = PinterestClient(token="tkn", fetcher=api)
        with pytest.raises(ValueError, match="no Pinterest board"):
            sync_pins(
                client,
                self._vault(tmp_path),
                board_name="Dinners",
                pacer=self._pacer(),
            )

    def test_board_scoped_sync_uses_board_path(self, tmp_path: Path) -> None:
        api = _FakeApi(
            [[_pin_item("1", "https://a.example.com/r1")]],
            boards=[{"id": "b7", "name": "Dinners"}],
        )
        client = PinterestClient(token="tkn", fetcher=api, pacer=self._pacer())
        sync_pins(
            client,
            self._vault(tmp_path),
            board_name="Dinners",
            page_fetcher=lambda url: _recipe_page("Pin Stew"),
            pacer=self._pacer(),
        )
        assert any("boards/b7/pins" in c for c in api.calls)
