"""YAML frontmatter builder + minimal emitter for recipe corpus markdown.

Implements the S9 Q9.2 recipe frontmatter contract (23 required + 8 optional
fields) split into the S9 Q9.3 common base + ``recipe:`` extension block.

For MVP the emitter is hand-rolled (avoids a PyYAML runtime dep) and covers
the type shapes we produce: strings, ints, floats, booleans, None, flat
dicts, and lists of primitives. A matching :func:`parse_frontmatter` reads
what we emit — full YAML parsing is out of scope until the corpus author
tooling lands in a later sub-commit.

Frontmatter validation itself (per S9 Q9.4.b — synchronous at write time)
lives in :func:`validate_frontmatter`; the built-in checker asserts that
the 23 S9-required base+recipe fields are all present.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# -- required field lists per S9 Q9.2 + Q9.3 -------------------------------

_BASE_REQUIRED = (
    "canonical_id",
    "content_type",
    "version",
    "title",
    "attribution",
    "source_status",
    "last_source_check_at",
    "source_removed_at",
    "material_implication_note",
)

_RECIPE_REQUIRED = (
    "cuisine_tradition_tags",
    "meal_categories",
    "dietary_compatibility",
    "modality_availability",
    "modality_resources",
    "estimated_active_time_min",
    "estimated_total_time_min",
    "failure_cost_tags",
    "yields",
    "top_allergens_present",
    "ingredient_resolution_summary",
    "ingredient_resolution_status",
)

REQUIRED_FIELDS = _BASE_REQUIRED + _RECIPE_REQUIRED

# S9 Q9.2 optional field set — surfaced here so downstream tooling can
# reason about the full schema without recomputing it.
OPTIONAL_FIELDS = (
    "cooking_technique_tags",
    "pairing_role_summary",
    "equipment_required",
    "seasonality_tags",
    "regional_origin",
    "historical_context_note",
    "editor_notes",
    "image_references",
)

_SOURCE_STATUS_VALUES = frozenset(
    {"live", "archived_nutrime_preserved", "live_with_caveats", "unknown"}
)
_INGREDIENT_RESOLUTION_STATUS_VALUES = frozenset(
    {"fully_resolved", "partial", "unresolved_pending_review"}
)


# -- data shapes -----------------------------------------------------------


@dataclass(frozen=True)
class Attribution:
    source_name: str
    source_url: str
    source_license: str
    ingested_at: str
    ingestion_method: str
    upstream_id: str = ""
    # For content ingested from an archive after the source went dark
    # (preservation-layer principle): the snapshot actually fetched, while
    # source_url keeps the original canonical URL.
    archived_snapshot_url: str = ""

    def as_dict(self) -> dict[str, str]:
        out = {
            "source_name": self.source_name,
            "source_url": self.source_url,
            "source_license": self.source_license,
            "ingested_at": self.ingested_at,
            "ingestion_method": self.ingestion_method,
        }
        if self.upstream_id:
            out["upstream_id"] = self.upstream_id
        if self.archived_snapshot_url:
            out["archived_snapshot_url"] = self.archived_snapshot_url
        return out


@dataclass(frozen=True)
class Yields:
    count: int
    unit: str = "servings"
    yield_note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"count": self.count, "unit": self.unit}
        if self.yield_note is not None:
            out["yield_note"] = self.yield_note
        return out


# -- builder ---------------------------------------------------------------


def build_recipe_frontmatter(
    *,
    recipe_id: str,
    title: str,
    attribution: Attribution,
    source_status: str,
    last_source_check_at: str,
    yields: Yields,
    top_allergens_present: list[str],
    cuisine_tradition_tags: list[str] | None = None,
    meal_categories: list[str] | None = None,
    dietary_compatibility: dict[str, bool] | None = None,
    modality_availability: list[str] | None = None,
    modality_resources: dict[str, str] | None = None,
    estimated_active_time_min: int | None = None,
    estimated_total_time_min: int | None = None,
    failure_cost_tags: list[str] | None = None,
    ingredient_resolution_summary: dict[str, int] | None = None,
    ingredient_resolution_status: str = "unresolved_pending_review",
    source_removed_at: str | None = None,
    material_implication_note: str | None = None,
    version: str = "1.0.0",
) -> dict[str, Any]:
    """Assemble a frontmatter dict populating all 23 required S9 fields.

    Defaults are conservative for the sub-commit 4.1 seed corpus where the
    upstream source (TheMealDB) doesn't ship structured yields/times/etc.
    """
    if source_status not in _SOURCE_STATUS_VALUES:
        raise ValueError(
            f"source_status {source_status!r} not in {sorted(_SOURCE_STATUS_VALUES)}"
        )
    if ingredient_resolution_status not in _INGREDIENT_RESOLUTION_STATUS_VALUES:
        raise ValueError(
            f"ingredient_resolution_status {ingredient_resolution_status!r}"
            f" not in {sorted(_INGREDIENT_RESOLUTION_STATUS_VALUES)}"
        )

    fm: dict[str, Any] = {
        # Base contract per S9 Q9.3
        "canonical_id": recipe_id,
        "content_type": "recipe",
        "version": version,
        "title": title,
        "attribution": attribution.as_dict(),
        "source_status": source_status,
        "last_source_check_at": last_source_check_at,
        "source_removed_at": source_removed_at,
        "material_implication_note": material_implication_note,
        # Recipe extension per S9 Q9.2
        "cuisine_tradition_tags": list(cuisine_tradition_tags or ()),
        "meal_categories": list(meal_categories or ()),
        "dietary_compatibility": dict(dietary_compatibility or {}),
        "modality_availability": list(modality_availability or ["text"]),
        "modality_resources": dict(modality_resources or {}),
        "estimated_active_time_min": estimated_active_time_min,
        "estimated_total_time_min": estimated_total_time_min,
        "failure_cost_tags": list(failure_cost_tags or ()),
        "yields": yields.as_dict(),
        "top_allergens_present": list(top_allergens_present),
        "ingredient_resolution_summary": dict(
            ingredient_resolution_summary
            or {"fully_resolved": 0, "partial": 0, "unresolved": 0}
        ),
        "ingredient_resolution_status": ingredient_resolution_status,
    }
    return fm


def validate_frontmatter(fm: dict[str, Any]) -> None:
    """Raise ``ValueError`` if any required field is missing.

    Called at write time per S9 Q9.4.b (synchronous validation).
    """
    missing = [f for f in REQUIRED_FIELDS if f not in fm]
    if missing:
        raise ValueError(f"frontmatter missing required fields: {missing}")
    if fm.get("content_type") != "recipe":
        raise ValueError(
            f"content_type must be 'recipe' (got {fm.get('content_type')!r})"
        )
    if fm.get("source_status") not in _SOURCE_STATUS_VALUES:
        raise ValueError(
            f"invalid source_status: {fm.get('source_status')!r}"
        )
    if fm.get("ingredient_resolution_status") not in _INGREDIENT_RESOLUTION_STATUS_VALUES:
        raise ValueError(
            f"invalid ingredient_resolution_status:"
            f" {fm.get('ingredient_resolution_status')!r}"
        )


# -- YAML emit + parse (minimal, hand-rolled) ------------------------------


def _emit_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return _emit_string(value)
    raise TypeError(f"unsupported scalar type: {type(value).__name__}")


def _emit_string(value: str) -> str:
    # Always single-quote; escape embedded single quotes by doubling.
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _emit_list(value: list, indent: int) -> str:
    if not value:
        return "[]"
    pad = " " * indent
    lines: list[str] = []
    for item in value:
        if isinstance(item, dict):
            raise TypeError("nested list-of-dict emission not supported at MVP")
        lines.append(f"{pad}- {_emit_scalar(item)}")
    return "\n" + "\n".join(lines)


def _emit_dict(value: dict, indent: int) -> str:
    if not value:
        return "{}"
    pad = " " * indent
    lines: list[str] = []
    for k, v in value.items():
        lines.append(f"{pad}{k}: {_emit_value(v, indent + 2)}")
    return "\n" + "\n".join(lines)


def _emit_value(value: Any, indent: int) -> str:
    if isinstance(value, list):
        return _emit_list(value, indent)
    if isinstance(value, dict):
        return _emit_dict(value, indent)
    return _emit_scalar(value)


def emit_yaml(frontmatter: dict[str, Any]) -> str:
    """Emit a dict as human-readable YAML.

    Supports the shapes used by :func:`build_recipe_frontmatter`: scalars,
    lists of scalars, and one-level nested dicts of scalars.
    """
    lines: list[str] = []
    for k, v in frontmatter.items():
        lines.append(f"{k}: {_emit_value(v, 2)}")
    return "\n".join(lines) + "\n"


# -- Minimal parser (only handles what emit_yaml writes) -------------------


def _parse_scalar(token: str) -> Any:
    token = token.strip()
    if token == "null" or token == "~" or token == "":
        return None
    if token == "true":
        return True
    if token == "false":
        return False
    if token == "[]":
        return []
    if token == "{}":
        return {}
    if len(token) >= 2 and token[0] == "'" and token[-1] == "'":
        return token[1:-1].replace("''", "'")
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1]
    # Try numeric
    try:
        if "." in token or "e" in token or "E" in token:
            return float(token)
        return int(token)
    except ValueError:
        return token


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse the YAML shape produced by :func:`emit_yaml`.

    This is deliberately narrow: it understands scalars, block lists of
    scalars, and one level of nested dicts (indent 2). Anything else raises
    ``ValueError``.
    """
    lines = text.splitlines()
    result: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line[0] == " ":
            raise ValueError(
                f"top-level line unexpectedly indented at line {i + 1}: {line!r}"
            )
        if ":" not in line:
            raise ValueError(f"expected key: value at line {i + 1}: {line!r}")
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "":
            # Block child follows — could be dict or list
            children, consumed = _collect_block(lines, i + 1, base_indent=2)
            result[key] = children
            i += 1 + consumed
        else:
            result[key] = _parse_scalar(rest)
            i += 1
    return result


def _collect_block(
    lines: list[str], start: int, *, base_indent: int
) -> tuple[Any, int]:
    """Collect a block starting at ``start`` with items indented ``base_indent``.

    Returns ``(parsed_value, lines_consumed)``.
    """
    pad = " " * base_indent
    consumed = 0
    # Detect list vs dict from first non-blank child line
    first_idx: int | None = None
    for j in range(start, len(lines)):
        if lines[j].strip():
            first_idx = j
            break
    if first_idx is None:
        return ({}, 0)
    first = lines[first_idx]
    if not first.startswith(pad):
        # Empty block
        return ({}, 0)
    remainder = first[base_indent:]
    if remainder.startswith("- "):
        # List of scalars
        items: list[Any] = []
        j = start
        while j < len(lines):
            raw = lines[j]
            if not raw.strip():
                j += 1
                consumed += 1
                continue
            if not raw.startswith(pad):
                break
            body = raw[base_indent:]
            if not body.startswith("- "):
                break
            items.append(_parse_scalar(body[2:].strip()))
            j += 1
            consumed += 1
        return (items, consumed)
    # Dict block
    sub: dict[str, Any] = {}
    j = start
    while j < len(lines):
        raw = lines[j]
        if not raw.strip():
            j += 1
            consumed += 1
            continue
        if not raw.startswith(pad):
            break
        body = raw[base_indent:]
        if body.startswith(" "):
            raise ValueError(
                f"nested-dict-inside-dict deeper than one level unsupported"
                f" at line {j + 1}: {raw!r}"
            )
        if ":" not in body:
            raise ValueError(
                f"expected key: value at line {j + 1}: {raw!r}"
            )
        k, _, v = body.partition(":")
        sub[k.strip()] = _parse_scalar(v.strip())
        j += 1
        consumed += 1
    return (sub, consumed)


# -- combined write helper -------------------------------------------------


def render_markdown_document(frontmatter: dict[str, Any], body: str) -> str:
    """Combine YAML frontmatter + Cooklang body into a single markdown file."""
    validate_frontmatter(frontmatter)
    yaml_text = emit_yaml(frontmatter)
    return f"---\n{yaml_text}---\n\n{body.rstrip()}\n"


def split_markdown_document(text: str) -> tuple[dict[str, Any], str]:
    """Split a written document back into (frontmatter, body)."""
    if not text.startswith("---\n"):
        raise ValueError("document missing leading '---' fence")
    remainder = text[4:]
    end = remainder.find("\n---\n")
    if end < 0:
        raise ValueError("document missing closing '---' fence")
    yaml_text = remainder[:end]
    body = remainder[end + len("\n---\n") :].lstrip("\n")
    fm = parse_frontmatter(yaml_text)
    return (fm, body)
