"""Life-stage food-avoidance rails (#46 / sweep #10 §3)."""

from pathlib import Path

from nutrime.life_stages import life_stage_rails
from nutrime.recipes.frontmatter import Attribution, Yields, build_recipe_frontmatter
from nutrime.recipes.ids import new_recipe_id
from nutrime.recipes.search import SearchFilters, search
from nutrime.recipes.store import RecipeVault


class TestRails:
    def test_no_sensitive_stage_no_rails(self) -> None:
        rails = life_stage_rails({"adult", "older_adult"})
        assert rails.avoid_terms == frozenset()
        assert rails.plan_notes == ()

    def test_pregnancy_rails(self) -> None:
        rails = life_stage_rails({"pregnant", "adult"})
        assert "swordfish" in rails.avoid_terms
        assert "unpasteurized milk" in rails.avoid_terms
        assert "deli meat" in rails.avoid_terms
        assert "alcohol" in rails.avoid_terms
        assert rails.stages == ("pregnant",)
        assert any("pregnant" in n for n in rails.plan_notes)

    def test_lactation_fish_only(self) -> None:
        # Hg list applies; the Listeria list does not (risk is fetal).
        rails = life_stage_rails({"lactating"})
        assert "swordfish" in rails.avoid_terms
        assert "deli meat" not in rails.avoid_terms
        assert "sushi" not in rails.avoid_terms

    def test_both_stages_union(self) -> None:
        rails = life_stage_rails({"pregnant", "lactating"})
        assert set(rails.stages) == {"pregnant", "lactating"}
        assert len(rails.plan_notes) == 2


def _write(vault, title, ingredients):
    rid = new_recipe_id()
    fm = build_recipe_frontmatter(
        recipe_id=rid, title=title,
        attribution=Attribution(
            source_name="t", source_url="https://e.com/r", source_license="t",
            ingested_at="2026-10-08T00:00:00Z", ingestion_method="test_v1",
        ),
        source_status="live", last_source_check_at="2026-10-08T00:00:00Z",
        yields=Yields(count=2), top_allergens_present=[],
    )
    body = "-- Ingredients\n\n" + "\n".join(f"@{i}{{}}" for i in ingredients) + \
        "\n\n-- Instructions\n\nCook it well.\n"
    vault.write(rid, fm, body)
    return rid


class TestSearchIntegration:
    def test_pregnancy_rails_exclude_recipes(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path)
        vault.ensure()
        sword = _write(vault, "Grilled Swordfish", ["swordfish steak", "lemon"])
        bagel = _write(vault, "Lox Bagel", ["smoked salmon", "bagel", "cream cheese"])
        safe = _write(vault, "Chicken Stew", ["chicken", "carrot", "stock"])
        rails = life_stage_rails({"pregnant"})
        results = search(
            vault, SearchFilters(exclude_ingredients=rails.avoid_terms)
        )
        ids = [r.recipe_id for r in results]
        assert safe in ids
        assert sword not in ids
        assert bagel not in ids
