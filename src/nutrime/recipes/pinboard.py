"""Public-board backfill via gallery-dl (issue #24, no-API path).

The Pinterest developer-app registration is review-gated and the account
data export is all-or-nothing, so the backfill path for an existing board
is gallery-dl — an existing, widely-used extractor — driven as a
subprocess. We pipe its ``--dump-json`` metadata (never its image
downloads) into the same ingest plumbing the API adapter uses:

- pins with an outbound link → the 4.4 jsonld adapter (URL-level de-dup,
  skip-and-report), exactly like an API sync;
- image-only pins (recipe baked into the picture) → persisted to a queue
  file (``pinterest_image_pins.jsonl`` in the data dir) for the vision
  extraction stage planned on #24. Queueing is idempotent by pin id, so
  re-running a backfill never duplicates queue entries.

ToS posture, stated honestly: gallery-dl reads Pinterest's internal web
API, which their robots.txt disallows for generic crawlers. This is the
household pulling the household's own board; the ingested pages are
personal-use captures, same license line as every jsonld ingest. The
official API adapter (pinterest.py) remains the preferred path once app
review clears, and both feed identical corpus shapes.

gallery-dl is NOT a runtime dependency — it's invoked as an external
command (``gallery-dl`` on PATH, or ``uvx gallery-dl``), and this module
degrades with a clear message when neither is available.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from nutrime.recipes.jsonld import SeedOutcome as JsonLdOutcome
from nutrime.recipes.jsonld import seed_recipes as jsonld_seed_recipes
from nutrime.recipes.pinterest import _is_ingestible_link
from nutrime.recipes.web import Pacer, TextFetcher, now_iso

QUEUE_FILENAME = "pinterest_image_pins.jsonl"

# Runs gallery-dl and returns its stdout. Injectable for tests.
BoardDumper = Callable[[str], str]


class GalleryDlUnavailable(Exception):
    """Neither ``gallery-dl`` nor ``uvx`` is on PATH."""


def _default_dumper(board_url: str) -> str:
    if shutil.which("gallery-dl"):
        cmd = ["gallery-dl"]
    elif shutil.which("uvx"):
        cmd = ["uvx", "gallery-dl"]
    else:
        raise GalleryDlUnavailable(
            "gallery-dl not found — install it (pipx install gallery-dl)"
            " or make `uvx` available."
        )
    result = subprocess.run(
        cmd + ["--dump-json", board_url],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"gallery-dl failed (rc={result.returncode}):"
            f" {result.stderr.strip()[:500]}"
        )
    return result.stdout


@dataclass(frozen=True)
class BoardPin:
    pin_id: str
    link: str
    image_url: str
    description: str
    title: str

    @property
    def pin_url(self) -> str:
        return f"https://www.pinterest.com/pin/{self.pin_id}/"


def parse_board_dump(raw: str) -> list[BoardPin]:
    """Parse ``gallery-dl --dump-json`` output; de-dup by pin id.

    The dump is a JSON array whose entries repeat per file; the last
    element of each entry is the metadata dict when present.
    """
    data = json.loads(raw)
    seen: set[str] = set()
    pins: list[BoardPin] = []
    for entry in data:
        md: dict[str, Any] | None = None
        if isinstance(entry, list) and entry and isinstance(entry[-1], dict):
            md = entry[-1]
        elif isinstance(entry, dict):
            md = entry
        if not md:
            continue
        pin_id = str(md.get("id") or "").strip()
        if not pin_id or pin_id in seen:
            continue
        seen.add(pin_id)
        images = md.get("images") or {}
        orig = images.get("orig") if isinstance(images, dict) else None
        image_url = str((orig or {}).get("url") or "") if isinstance(orig, dict) else ""
        pins.append(
            BoardPin(
                pin_id=pin_id,
                link=str(md.get("link") or "").strip(),
                image_url=image_url,
                description=str(md.get("description") or "").strip(),
                title=str(md.get("title") or "").strip(),
            )
        )
    return pins


# -- image-only pin queue (vision stage feedstock, #24) ----------------------


def load_queued_pin_ids(queue_path: Path) -> set[str]:
    ids: set[str] = set()
    if not queue_path.exists():
        return ids
    for line in queue_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ids.add(str(json.loads(line).get("pin_id") or ""))
        except json.JSONDecodeError:
            continue
    return ids


def queue_image_pins(queue_path: Path, pins: list[BoardPin]) -> int:
    """Append image-only pins not already queued; returns count added."""
    existing = load_queued_pin_ids(queue_path)
    added = 0
    with queue_path.open("a", encoding="utf-8") as fh:
        for pin in pins:
            if pin.pin_id in existing or not pin.image_url:
                continue
            fh.write(
                json.dumps(
                    {
                        "pin_id": pin.pin_id,
                        "pin_url": pin.pin_url,
                        "image_url": pin.image_url,
                        "description": pin.description,
                        "title": pin.title,
                        "queued_at": now_iso(),
                        "status": "pending_vision_extraction",
                    }
                )
                + "\n"
            )
            existing.add(pin.pin_id)
            added += 1
    return added


# -- driver -------------------------------------------------------------------


@dataclass(frozen=True)
class BackfillOutcome:
    pins_seen: int
    pins_with_links: int
    image_only_queued: int
    image_only_total: int
    ingest: JsonLdOutcome

    @property
    def written(self) -> int:
        return self.ingest.written


def backfill_board(
    board_url: str,
    vault,  # RecipeVault
    data_dir: Path,
    *,
    dumper: BoardDumper | None = None,
    page_fetcher: TextFetcher | None = None,
    pacer: Pacer | None = None,
    limit: int | None = None,
) -> BackfillOutcome:
    """Enumerate a public board via gallery-dl; ingest links, queue images.

    ``limit`` caps candidate links passed to ingest (the jsonld adapter's
    URL de-dup makes re-runs resume where the last one stopped).
    """
    dump = (dumper or _default_dumper)(board_url)
    pins = parse_board_dump(dump)

    links: list[str] = []
    seen_links: set[str] = set()
    image_only: list[BoardPin] = []
    for pin in pins:
        if _is_ingestible_link(pin.link):
            if pin.link not in seen_links:
                seen_links.add(pin.link)
                if limit is None or len(links) < limit:
                    links.append(pin.link)
        elif pin.image_url:
            image_only.append(pin)

    queued = queue_image_pins(data_dir / QUEUE_FILENAME, image_only)
    ingest = jsonld_seed_recipes(
        vault,
        links,
        fetcher=page_fetcher,
        pacer=pacer or Pacer(delay_s=1.0),
    )
    return BackfillOutcome(
        pins_seen=len(pins),
        pins_with_links=len(links),
        image_only_queued=queued,
        image_only_total=len(image_only),
        ingest=ingest,
    )
