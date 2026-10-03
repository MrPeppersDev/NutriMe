"""Public-board backfill — dump parsing, link/image triage, vision queue."""

import json
from pathlib import Path

import pytest

from nutrime.recipes.pinboard import (
    QUEUE_FILENAME,
    backfill_board,
    load_queued_pin_ids,
    parse_board_dump,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer


def _dump_entry(pin_id: str, link: str | None, image: str = "", desc: str = "") -> list:
    md = {
        "id": pin_id,
        "link": link,
        "description": desc,
        "title": "",
        "images": {"orig": {"url": image}} if image else {},
    }
    return [3, f"https://i.pinimg.com/x/{pin_id}.jpg", md]


def _recipe_page(name: str) -> str:
    node = {
        "@type": "Recipe",
        "name": name,
        "recipeIngredient": ["1 lb thing"],
        "recipeInstructions": "Cook.",
        "recipeYield": "2",
    }
    return (
        '<script type="application/ld+json">' + json.dumps(node) + "</script>"
    )


class TestParseBoardDump:
    def test_dedups_repeated_pin_entries(self) -> None:
        raw = json.dumps(
            [
                _dump_entry("1", "https://a.example.com/r"),
                _dump_entry("1", "https://a.example.com/r"),
                _dump_entry("2", None, image="https://i.pinimg.com/o/2.png"),
            ]
        )
        pins = parse_board_dump(raw)
        assert [p.pin_id for p in pins] == ["1", "2"]
        assert pins[1].image_url == "https://i.pinimg.com/o/2.png"

    def test_tolerates_metadata_only_entries(self) -> None:
        raw = json.dumps([{"id": "9", "link": "https://b.example.com/r"}])
        pins = parse_board_dump(raw)
        assert pins[0].pin_id == "9"


class TestBackfill:
    def _vault(self, tmp_path: Path) -> RecipeVault:
        vault = RecipeVault(tmp_path / "corpus")
        vault.ensure()
        return vault

    def _pacer(self) -> Pacer:
        return Pacer(delay_s=0, sleep=lambda _: None)

    def test_links_ingested_images_queued(self, tmp_path: Path) -> None:
        dump = json.dumps(
            [
                _dump_entry("1", "https://a.example.com/r1"),
                _dump_entry("2", None, image="https://i.pinimg.com/o/2.png",
                            desc="Maple pecans recipe"),
                _dump_entry("3", "https://www.amazon.com/shop/x"),  # junk link, no image
                _dump_entry("4", "https://b.example.com/r2"),
            ]
        )
        pages = {
            "https://a.example.com/r1": _recipe_page("Stew"),
            "https://b.example.com/r2": _recipe_page("Salad"),
            "https://www.amazon.com/shop/x": "<html>not a recipe</html>",
        }
        outcome = backfill_board(
            "https://www.pinterest.com/u/b/",
            self._vault(tmp_path),
            tmp_path,
            dumper=lambda url: dump,
            page_fetcher=lambda url: pages[url],
            pacer=self._pacer(),
        )
        assert outcome.pins_seen == 4
        # amazon link is still an external link — it goes to ingest and
        # fails honestly (no JSON-LD), reported in failures
        assert outcome.pins_with_links == 3
        assert outcome.written == 2
        assert len(outcome.ingest.failures) == 1
        assert outcome.image_only_queued == 1

        queue = tmp_path / QUEUE_FILENAME
        rows = [json.loads(l) for l in queue.read_text().splitlines()]
        assert rows[0]["pin_id"] == "2"
        assert rows[0]["status"] == "pending_vision_extraction"
        assert rows[0]["description"] == "Maple pecans recipe"

    def test_rerun_queues_nothing_new(self, tmp_path: Path) -> None:
        dump = json.dumps(
            [_dump_entry("2", None, image="https://i.pinimg.com/o/2.png")]
        )
        vault = self._vault(tmp_path)
        for _ in range(2):
            outcome = backfill_board(
                "https://www.pinterest.com/u/b/",
                vault,
                tmp_path,
                dumper=lambda url: dump,
                page_fetcher=lambda url: "",
                pacer=self._pacer(),
            )
        assert outcome.image_only_queued == 0
        assert load_queued_pin_ids(tmp_path / QUEUE_FILENAME) == {"2"}

    def test_limit_caps_candidate_links(self, tmp_path: Path) -> None:
        dump = json.dumps(
            [
                _dump_entry(str(i), f"https://a.example.com/r{i}")
                for i in range(5)
            ]
        )
        outcome = backfill_board(
            "https://www.pinterest.com/u/b/",
            self._vault(tmp_path),
            tmp_path,
            dumper=lambda url: dump,
            page_fetcher=lambda url: _recipe_page(url.rsplit("/", 1)[-1]),
            pacer=self._pacer(),
            limit=2,
        )
        assert outcome.pins_with_links == 2
        assert outcome.written == 2
