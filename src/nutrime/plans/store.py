"""Plan vault — markdown source-of-truth at ``<corpus_dir>/plans/``.

Entry decision (5.4, 2026-08-09): plans persist exactly like recipes — one
markdown file per plan, YAML frontmatter + human-readable body — reusing the
hand-rolled YAML emit/parse from ``recipes.frontmatter``. The recipe-specific
S9 field validation doesn't apply; plans validate their own small contract.

Frontmatter carries the epistemic trail (Rule 8): the ``llm_request_ids`` /
``llm_request_log_ids`` columns correlate every plan to its audited crossings
in ``op_llm_request_log``. They are *lists* because 5.4 issues one crossing
per meal, not one per plan — each meal is its own workload with its own audit
row and its own failure domain.

Why per-meal detail lives in the body rather than the frontmatter: the natural
shape would be a ``meals:`` list-of-dicts, but ``frontmatter._emit_list``
refuses nested dicts at MVP. Rather than widen the emitter under the recipe
write path, plans follow the same split recipes already use — frontmatter for
plan-level metadata, body for the structured content that downstream code
parses back (``search.ingredient_names`` reads Cooklang bodies the same way).
:func:`parse_plan_body` is the 6.1 grocery-aggregation hand-off point.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from nutrime.fsio import atomic_write_text
from nutrime.knowledge.ids import uuid7
from nutrime.recipes.frontmatter import emit_yaml, split_markdown_document

PLAN_REQUIRED_FIELDS = (
    "plan_id",
    "content_type",
    "created_at",
    "tenant_id",
    "days",
    "meal_slots",
    "meals_planned",
    "model",
    "llm_request_ids",
    "llm_request_log_ids",
    "constraints_applied",
    "candidate_count",
)

_TABLE_HEADER = "| Day | Slot | Recipe ID | Title | Note |"
_TABLE_RULE = "| --- | --- | --- | --- | --- |"
_UNFILLED = "(unfilled)"


def new_plan_id() -> str:
    return f"pln-{uuid7()}"


@dataclass(frozen=True)
class PlanEntry:
    """One meal slot in a plan. ``recipe_id`` is None when the slot failed."""

    day: int
    slot: str
    recipe_id: str | None = None
    title: str = ""
    note: str = ""

    @property
    def filled(self) -> bool:
        return self.recipe_id is not None


@dataclass(frozen=True)
class PlanRecord:
    plan_id: str
    frontmatter: dict[str, Any]
    body: str
    path: Path

    def entries(self) -> tuple[PlanEntry, ...]:
        return parse_plan_body(self.body)


def validate_plan_frontmatter(fm: dict[str, Any]) -> None:
    missing = [f for f in PLAN_REQUIRED_FIELDS if f not in fm]
    if missing:
        raise ValueError(f"plan frontmatter missing fields: {missing}")
    if fm.get("content_type") != "meal_plan":
        raise ValueError("plan content_type must be 'meal_plan'")


# -- body render + parse ---------------------------------------------------


def _escape_cell(text: str) -> str:
    return text.replace("\\", "\\\\").replace("|", "\\|").strip()


def _unescape_cell(text: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            out.append(text[i + 1])
            i += 2
        else:
            out.append(text[i])
            i += 1
    return "".join(out).strip()


def render_plan_body(entries: tuple[PlanEntry, ...] | list[PlanEntry]) -> str:
    """Render the schedule as a markdown table :func:`parse_plan_body` reads."""
    lines = [_TABLE_HEADER, _TABLE_RULE]
    for entry in entries:
        recipe = entry.recipe_id if entry.recipe_id is not None else _UNFILLED
        lines.append(
            f"| {entry.day} | {_escape_cell(entry.slot)} |"
            f" {_escape_cell(recipe)} | {_escape_cell(entry.title)} |"
            f" {_escape_cell(entry.note)} |"
        )
    return "\n".join(lines) + "\n"


def _split_row(line: str) -> list[str]:
    """Split a markdown table row on unescaped pipes."""
    cells: list[str] = []
    current: list[str] = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line):
            current.append(ch)
            current.append(line[i + 1])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(current))
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    cells.append("".join(current))
    # A leading and trailing pipe produce empty edge cells.
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return cells


def parse_plan_body(body: str) -> tuple[PlanEntry, ...]:
    """Read the schedule back out of a plan body.

    Non-table lines (headings, prose) are ignored, so the body stays free to
    carry human-facing context alongside the machine-readable table.
    """
    entries: list[PlanEntry] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [_unescape_cell(c) for c in _split_row(stripped)]
        if len(cells) < 4:
            continue
        if cells[0].lower() == "day" or set(cells[0]) <= {"-", " "}:
            continue
        try:
            day = int(cells[0])
        except ValueError:
            continue
        recipe_id: str | None = cells[2]
        if recipe_id in ("", _UNFILLED):
            recipe_id = None
        entries.append(
            PlanEntry(
                day=day,
                slot=cells[1],
                recipe_id=recipe_id,
                title=cells[3],
                note=cells[4] if len(cells) > 4 else "",
            )
        )
    return tuple(entries)


# -- vault -----------------------------------------------------------------


class PlanVault:
    def __init__(self, corpus_dir: Path) -> None:
        self._root = corpus_dir / "plans"

    @property
    def root(self) -> Path:
        return self._root

    def ensure(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    def path_for(self, plan_id: str) -> Path:
        # Same containment guard as RecipeVault (2026-10-07 audit).
        path = (self._root / f"{plan_id}.md").resolve()
        root = self._root.resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"plan id escapes the vault: {plan_id!r}")
        return path

    def exists(self, plan_id: str) -> bool:
        return self.path_for(plan_id).exists()

    def write(
        self, plan_id: str, frontmatter: dict[str, Any], body: str
    ) -> Path:
        validate_plan_frontmatter(frontmatter)
        self.ensure()
        yaml_text = emit_yaml(frontmatter)
        document = f"---\n{yaml_text}---\n\n{body.rstrip()}\n"
        path = self.path_for(plan_id)
        atomic_write_text(path, document)
        return path

    def read(self, plan_id: str) -> PlanRecord:
        path = self.path_for(plan_id)
        fm, body = split_markdown_document(path.read_text(encoding="utf-8"))
        return PlanRecord(plan_id=plan_id, frontmatter=fm, body=body, path=path)

    def iter_plans(self) -> Iterator[PlanRecord]:
        """Yield every plan, newest first.

        Ordering keys off ``created_at`` rather than the filename: ``uuid7()``
        has no intra-millisecond monotonic counter (``rand_a`` is pure random),
        so two ids minted in the same millisecond do not sort by creation
        order. The id is the tiebreaker for a genuine timestamp collision.
        """
        if not self._root.exists():
            return
        records: list[PlanRecord] = []
        for path in self._root.glob("*.md"):
            fm, body = split_markdown_document(path.read_text(encoding="utf-8"))
            records.append(
                PlanRecord(
                    plan_id=path.stem, frontmatter=fm, body=body, path=path
                )
            )
        records.sort(
            key=lambda r: (str(r.frontmatter.get("created_at", "")), r.plan_id),
            reverse=True,
        )
        yield from records

    def list_plans(self) -> list[PlanRecord]:
        return list(self.iter_plans())

    def count(self) -> int:
        if not self._root.exists():
            return 0
        return sum(1 for _ in self._root.glob("*.md"))
