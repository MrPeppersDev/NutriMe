"""Image-pin vision extraction (#24 queue consumer): parsing, validation,
queue lifecycle, vault writes, fail-safe."""

import json
from pathlib import Path

import pytest

from nutrime.recipes.pin_vision import (
    STATUS_DONE,
    STATUS_FAILED,
    STATUS_PENDING,
    Extracted,
    convert_extracted,
    extract_queued_pins,
    parse_vision_reply,
)
from nutrime.recipes.store import RecipeVault


def _reply(**overrides) -> str:
    payload = {
        "is_recipe": True,
        "title": "Maple Vanilla Candied Pecans",
        "ingredients": ["2 cups pecans", "1/3 cup maple syrup", "1 tsp vanilla"],
        "steps": ["Toss pecans with syrup.", "Bake 20 minutes at 350F."],
        "servings": 8,
        "total_minutes": 25,
    }
    payload.update(overrides)
    return json.dumps(payload)


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []

    def complete(self, request):
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply

        class R:
            text = reply

        return R()


def _queue(tmp_path: Path, entries) -> Path:
    path = tmp_path / "pinterest_image_pins.jsonl"
    path.write_text(
        "".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8"
    )
    return path


def _entry(pin_id: str, status: str = STATUS_PENDING) -> dict:
    return {
        "pin_id": pin_id,
        "pin_url": f"https://www.pinterest.com/pin/{pin_id}/",
        "image_url": f"https://i.pinimg.com/originals/{pin_id}.png",
        "description": "",
        "title": "Candied pecans",
        "queued_at": "2026-10-03T14:54:46Z",
        "status": status,
    }


def _fake_image(url: str) -> bytes:
    return b"\x89PNG fake bytes"


class TestParseVisionReply:
    def test_valid_reply_round_trips(self) -> None:
        extracted = parse_vision_reply(_reply())
        assert extracted.title == "Maple Vanilla Candied Pecans"
        assert len(extracted.ingredient_lines) == 3
        assert extracted.servings == 8
        assert extracted.total_minutes == 25

    def test_not_a_recipe_is_a_verdict_not_an_error(self) -> None:
        assert parse_vision_reply(json.dumps({"is_recipe": False})) is None

    def test_json_noise_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_vision_reply("I think this shows a pecan recipe!")

    def test_markdown_fenced_json_still_parses(self) -> None:
        assert parse_vision_reply("```json\n" + _reply() + "\n```") is not None

    def test_too_few_ingredients_rejected(self) -> None:
        assert parse_vision_reply(_reply(ingredients=["pecans"])) is None

    def test_no_steps_rejected(self) -> None:
        assert parse_vision_reply(_reply(steps=[])) is None

    def test_missing_title_rejected(self) -> None:
        assert parse_vision_reply(_reply(title="")) is None

    def test_absurd_numbers_dropped_not_fatal(self) -> None:
        extracted = parse_vision_reply(
            _reply(servings=5000, total_minutes=-3)
        )
        assert extracted.servings is None
        assert extracted.total_minutes is None


class TestConvertExtracted:
    def test_vault_shapes(self) -> None:
        extracted = Extracted(
            title="Candied Pecans",
            ingredient_lines=("2 cups pecans", "1/3 cup maple syrup"),
            steps=("Toss.", "Bake."),
            servings=None,
            total_minutes=None,
        )
        recipe_id, fm, body = convert_extracted(
            extracted,
            pin_url="https://www.pinterest.com/pin/1/",
            image_url="https://i.pinimg.com/originals/1.png",
        )
        assert fm["attribution"]["ingestion_method"] == "pin_vision_extraction"
        assert fm["attribution"]["source_url"] == "https://www.pinterest.com/pin/1/"
        assert "image" in fm["modality_availability"]
        assert fm["yields"]["count"] == 4  # default when the card shows none
        assert "tree_nuts" in fm["top_allergens_present"]  # pecans
        assert "pecans" in body


class TestExtractQueuedPins:
    def test_happy_path_writes_and_marks(self, tmp_path: Path) -> None:
        queue = _queue(tmp_path, [_entry("1")])
        vault = RecipeVault(tmp_path / "corpus")
        client = FakeClient([_reply()])
        outcome = extract_queued_pins(
            queue, vault, client, image_fetcher=_fake_image
        )
        assert (outcome.pending, outcome.written) == (1, 1)
        entries = [
            json.loads(line) for line in queue.read_text().splitlines()
        ]
        assert entries[0]["status"] == STATUS_DONE
        assert entries[0]["recipe_id"].startswith("rcp-")
        records = list(vault.iter_recipes())
        assert len(records) == 1
        assert records[0].frontmatter["title"] == "Maple Vanilla Candied Pecans"

    def test_request_is_local_vision_and_carries_the_image(
        self, tmp_path: Path
    ) -> None:
        queue = _queue(tmp_path, [_entry("1")])
        client = FakeClient([_reply()])
        extract_queued_pins(
            queue,
            RecipeVault(tmp_path / "corpus"),
            client,
            image_fetcher=_fake_image,
        )
        request = client.requests[0]
        assert "local-private" in request.required_capabilities
        assert "vision" in request.required_capabilities
        assert request.messages[0].images == (_fake_image(""),)

    def test_not_a_recipe_marks_failed_and_continues(
        self, tmp_path: Path
    ) -> None:
        queue = _queue(tmp_path, [_entry("1"), _entry("2")])
        client = FakeClient(
            [json.dumps({"is_recipe": False}), _reply()]
        )
        outcome = extract_queued_pins(
            queue,
            RecipeVault(tmp_path / "corpus"),
            client,
            image_fetcher=_fake_image,
        )
        assert (outcome.written, outcome.not_recipes) == (1, 1)
        entries = [
            json.loads(line) for line in queue.read_text().splitlines()
        ]
        assert entries[0]["status"] == STATUS_FAILED
        assert entries[1]["status"] == STATUS_DONE

    def test_model_noise_marks_failed_never_writes(
        self, tmp_path: Path
    ) -> None:
        queue = _queue(tmp_path, [_entry("1")])
        client = FakeClient(["total nonsense, no JSON"])
        vault = RecipeVault(tmp_path / "corpus")
        outcome = extract_queued_pins(
            queue, vault, client, image_fetcher=_fake_image
        )
        assert outcome.written == 0
        assert len(outcome.failures) == 1
        assert list(vault.iter_recipes()) == []

    def test_done_and_failed_entries_never_rerun(self, tmp_path: Path) -> None:
        queue = _queue(
            tmp_path,
            [
                _entry("1", status=STATUS_DONE),
                _entry("2", status=STATUS_FAILED),
                _entry("3"),
            ],
        )
        client = FakeClient([_reply()])
        outcome = extract_queued_pins(
            queue,
            RecipeVault(tmp_path / "corpus"),
            client,
            image_fetcher=_fake_image,
        )
        assert outcome.pending == 1
        assert len(client.requests) == 1

    def test_limit_caps_the_run(self, tmp_path: Path) -> None:
        queue = _queue(tmp_path, [_entry("1"), _entry("2"), _entry("3")])
        client = FakeClient([_reply(), _reply(), _reply()])
        outcome = extract_queued_pins(
            queue,
            RecipeVault(tmp_path / "corpus"),
            client,
            limit=2,
            image_fetcher=_fake_image,
        )
        assert outcome.written == 2
        entries = [
            json.loads(line) for line in queue.read_text().splitlines()
        ]
        assert entries[2]["status"] == STATUS_PENDING

    def test_image_fetch_failure_marks_failed(self, tmp_path: Path) -> None:
        def _no_image(url: str) -> bytes:
            raise RuntimeError("404")

        queue = _queue(tmp_path, [_entry("1")])
        client = FakeClient([])
        outcome = extract_queued_pins(
            queue,
            RecipeVault(tmp_path / "corpus"),
            client,
            image_fetcher=_no_image,
        )
        assert outcome.written == 0
        assert len(outcome.failures) == 1
        assert client.requests == []
