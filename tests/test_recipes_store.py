"""Filesystem vault reader/writer for the recipe corpus."""

from pathlib import Path

import pytest

from nutrime.recipes.frontmatter import Attribution, Yields, build_recipe_frontmatter
from nutrime.recipes.ids import new_recipe_id
from nutrime.recipes.store import RecipeVault


def _sample_frontmatter(recipe_id: str) -> dict:
    return build_recipe_frontmatter(
        recipe_id=recipe_id,
        title="Sample",
        attribution=Attribution(
            source_name="Test",
            source_url="https://example.com",
            source_license="MIT",
            ingested_at="2026-07-02T12:00:00Z",
            ingestion_method="unit_test",
        ),
        source_status="live",
        last_source_check_at="2026-07-02T12:00:00Z",
        yields=Yields(count=4),
        top_allergens_present=[],
    )


@pytest.fixture
def vault(tmp_path: Path) -> RecipeVault:
    return RecipeVault(tmp_path / "corpus")


class TestRecipeVault:
    def test_write_creates_file_at_expected_path(self, vault: RecipeVault) -> None:
        recipe_id = new_recipe_id()
        fm = _sample_frontmatter(recipe_id)
        path = vault.write(recipe_id, fm, "-- body\n")
        assert path == vault.root / f"{recipe_id}.md"
        assert path.exists()

    def test_read_round_trips(self, vault: RecipeVault) -> None:
        recipe_id = new_recipe_id()
        fm = _sample_frontmatter(recipe_id)
        vault.write(recipe_id, fm, "-- Ingredients\n\n@salt\n")
        record = vault.read(recipe_id)
        assert record.recipe_id == recipe_id
        assert record.frontmatter == fm
        assert "@salt" in record.body

    def test_list_recipes_returns_all_written(self, vault: RecipeVault) -> None:
        ids = [new_recipe_id() for _ in range(3)]
        for rid in ids:
            vault.write(rid, _sample_frontmatter(rid), "body\n")
        records = vault.list_recipes()
        assert {r.recipe_id for r in records} == set(ids)

    def test_list_empty_vault_returns_empty(self, vault: RecipeVault) -> None:
        assert vault.list_recipes() == []

    def test_exists(self, vault: RecipeVault) -> None:
        recipe_id = new_recipe_id()
        assert not vault.exists(recipe_id)
        vault.write(recipe_id, _sample_frontmatter(recipe_id), "body\n")
        assert vault.exists(recipe_id)

    def test_count(self, vault: RecipeVault) -> None:
        assert vault.count() == 0
        for _ in range(4):
            rid = new_recipe_id()
            vault.write(rid, _sample_frontmatter(rid), "body\n")
        assert vault.count() == 4

    def test_ensure_creates_directory(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path / "corpus-not-yet")
        assert not vault.root.exists()
        vault.ensure()
        assert vault.root.is_dir()

    def test_write_validates_frontmatter(self, vault: RecipeVault) -> None:
        recipe_id = new_recipe_id()
        fm = _sample_frontmatter(recipe_id)
        del fm["yields"]
        with pytest.raises(ValueError):
            vault.write(recipe_id, fm, "body\n")
