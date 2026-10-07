"""Vault reader/writer for the recipe corpus.

Layout per S9 Q9.1 markdown-as-source-of-truth:
- ``<corpus_dir>/recipes/<recipe_id>.md`` — one file per canonical id
- Content: ``---\\n<yaml>\\n---\\n\\n<cooklang body>``

Substrate denormalization (``recipe_document`` molecule + async
``op_job_queue`` sync per S9 Q9.4.b) is deferred until a consumer of the
substrate index shows up. For sub-commit 4.1 the vault itself is enough:
list + read + write against the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

from nutrime.recipes.frontmatter import (
    render_markdown_document,
    split_markdown_document,
)


@dataclass(frozen=True)
class RecipeRecord:
    """One materialised markdown file in the vault."""

    recipe_id: str
    frontmatter: dict[str, Any]
    body: str
    path: Path


class RecipeVault:
    """Filesystem-backed vault at ``<corpus_dir>/recipes/``."""

    def __init__(self, corpus_dir: Path) -> None:
        self._root = corpus_dir / "recipes"

    @property
    def root(self) -> Path:
        return self._root

    def ensure(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    def path_for(self, recipe_id: str) -> Path:
        # Containment (2026-10-07 security audit): ids come from URLs; a
        # "../"-carrying or absolute id must never escape the vault root
        # (verified traversal read an .md outside the corpus pre-fix).
        path = (self._root / f"{recipe_id}.md").resolve()
        root = self._root.resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"recipe id escapes the vault: {recipe_id!r}")
        return path

    def exists(self, recipe_id: str) -> bool:
        return self.path_for(recipe_id).exists()

    def write(
        self, recipe_id: str, frontmatter: dict[str, Any], body: str
    ) -> Path:
        """Write ``<recipe_id>.md``; frontmatter is validated at render time."""
        self.ensure()
        document = render_markdown_document(frontmatter, body)
        path = self.path_for(recipe_id)
        path.write_text(document, encoding="utf-8")
        return path

    def read(self, recipe_id: str) -> RecipeRecord:
        path = self.path_for(recipe_id)
        text = path.read_text(encoding="utf-8")
        fm, body = split_markdown_document(text)
        return RecipeRecord(
            recipe_id=recipe_id, frontmatter=fm, body=body, path=path
        )

    def iter_recipes(self) -> Iterator[RecipeRecord]:
        if not self._root.exists():
            return iter(())
        return self._iter_sorted()

    def _iter_sorted(self) -> Iterator[RecipeRecord]:
        for path in sorted(self._root.glob("*.md")):
            recipe_id = path.stem
            text = path.read_text(encoding="utf-8")
            fm, body = split_markdown_document(text)
            yield RecipeRecord(
                recipe_id=recipe_id, frontmatter=fm, body=body, path=path
            )

    def list_recipes(self) -> list[RecipeRecord]:
        return list(self.iter_recipes())

    def count(self) -> int:
        if not self._root.exists():
            return 0
        return sum(1 for _ in self._root.glob("*.md"))


def collect_upstream_ids(
    vault: RecipeVault,
    source_name: str,
    *,
    fallback: Callable[[dict[str, Any]], str] | None = None,
) -> set[str]:
    """Upstream ids already ingested for ``source_name`` (seed de-dup).

    ``fallback`` lets an adapter derive an id from the attribution block for
    legacy writes that predate ``upstream_id`` (e.g. TheMealDB source-URL
    pattern).
    """
    seen: set[str] = set()
    for record in vault.iter_recipes():
        attribution = record.frontmatter.get("attribution", {}) or {}
        if attribution.get("source_name") != source_name:
            continue
        upstream = attribution.get("upstream_id") or ""
        if not upstream and fallback is not None:
            upstream = fallback(attribution) or ""
        if upstream:
            seen.add(upstream)
    return seen
