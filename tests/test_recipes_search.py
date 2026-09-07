"""Sub-commit 5.3 — recipe search over the corpus vault.

Covers ingredient extraction from Cooklang bodies, term normalization, every
hard filter (query/allergen/ingredient/time/category/cuisine), on-hand +
preference scoring, the constraint-mapping seam (avoids -> allergen block vs
ingredient exclusion, prefers -> boost), attribution rendering (#23 on this
surface), and the CLI.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from nutrime.recipes.frontmatter import Attribution, Yields, build_recipe_frontmatter
from nutrime.recipes.search import (
    SearchFilters,
    attribution_line,
    filters_from_constraints,
    ingredient_names,
    normalize_term,
    search,
)
from nutrime.recipes.store import RecipeVault


def _frontmatter(recipe_id: str, title: str, **overrides):
    kwargs = dict(
        recipe_id=recipe_id,
        title=title,
        attribution=Attribution(
            source_name=overrides.pop("source_name", "TheMealDB"),
            source_url="https://example.test/r",
            source_license=overrides.pop("source_license", "free-tier-attribution"),
            ingested_at="2026-08-09T00:00:00Z",
            ingestion_method="rest_api",
        ),
        source_status="live",
        last_source_check_at="2026-08-09T00:00:00Z",
        yields=Yields(count=4),
        top_allergens_present=overrides.pop("allergens", []),
        estimated_total_time_min=overrides.pop("total_time", None),
        meal_categories=overrides.pop("categories", ["dinner"]),
        cuisine_tradition_tags=overrides.pop("cuisines", ["american"]),
    )
    kwargs.update(overrides)
    return build_recipe_frontmatter(**kwargs)


def _body(*ingredients: str, steps: str = "Cook everything.") -> str:
    lines = [">> title: t", "", "-- Ingredients", ""]
    lines += list(ingredients)
    lines += ["", "-- Instructions", "", steps, ""]
    return "\n".join(lines)


@pytest.fixture()
def vault(tmp_path):
    vault = RecipeVault(tmp_path / "corpus")
    vault.write(
        "rcp-chicken",
        _frontmatter("rcp-chicken", "Quick Chicken Creole", total_time=25),
        _body("@chicken breasts{2}", "@celery{1%stalk}", "@rice{1%cup}"),
    )
    vault.write(
        "rcp-shrimp",
        _frontmatter(
            "rcp-shrimp",
            "Garlic Shrimp Pasta",
            allergens=["shellfish", "gluten"],
            total_time=30,
            cuisines=["italian"],
        ),
        _body("@shrimp{1%lb}", "@pasta{8%oz}", "@garlic{3%cloves}"),
    )
    vault.write(
        "rcp-stew",
        _frontmatter(
            "rcp-stew",
            "Beeton Beef Stew",
            source_name="Project Gutenberg",
            source_license="public-domain",
            total_time=None,
            categories=["dinner", "historical"],
        ),
        _body("@beef{2%lb}", "@carrots{3}", "@onion"),
    )
    return vault


class TestHelpers:
    def test_ingredient_names_braced_and_bare(self):
        body = _body("@chicken breasts{2}", "@salt", "@olive oil{}")
        assert ingredient_names(body) == ("chicken breasts", "salt", "olive oil")

    def test_normalize_strips_plurals(self):
        assert normalize_term("Chicken Breasts") == "chicken breast"
        assert normalize_term("swiss") == "swiss"  # no ss-strip

    def test_attribution_line(self):
        fm = _frontmatter("rcp-x", "X")
        assert (
            attribution_line(fm)
            == "Source: TheMealDB (free-tier-attribution) — https://example.test/r"
        )


class TestFilters:
    def test_no_filters_returns_all_ranked_by_title(self, vault):
        results = search(vault, SearchFilters())
        assert [r.recipe_id for r in results] == [
            "rcp-stew",
            "rcp-shrimp",
            "rcp-chicken",
        ]

    def test_query_on_title(self, vault):
        results = search(vault, SearchFilters(query="shrimp"))
        assert [r.recipe_id for r in results] == ["rcp-shrimp"]

    def test_allergen_hard_block(self, vault):
        results = search(
            vault, SearchFilters(exclude_allergens=frozenset({"shellfish"}))
        )
        assert "rcp-shrimp" not in [r.recipe_id for r in results]

    def test_ingredient_exclusion_matches_plural(self, vault):
        results = search(
            vault, SearchFilters(exclude_ingredients=frozenset({"carrot"}))
        )
        assert "rcp-stew" not in [r.recipe_id for r in results]

    def test_max_time_excludes_unknown(self, vault):
        results = search(vault, SearchFilters(max_total_time_min=28))
        # 25-min chicken passes; 30-min shrimp too slow; stew unknown -> out.
        assert [r.recipe_id for r in results] == ["rcp-chicken"]

    def test_category_and_cuisine(self, vault):
        assert [
            r.recipe_id
            for r in search(vault, SearchFilters(meal_category="historical"))
        ] == ["rcp-stew"]
        assert [
            r.recipe_id for r in search(vault, SearchFilters(cuisine="italian"))
        ] == ["rcp-shrimp"]

    def test_limit(self, vault):
        assert len(search(vault, SearchFilters(), limit=2)) == 2


class TestScoring:
    def test_on_hand_ranks_first(self, vault):
        results = search(
            vault,
            SearchFilters(on_hand=frozenset({"chicken breast", "rice"})),
        )
        top = results[0]
        assert top.recipe_id == "rcp-chicken"
        assert top.on_hand_matches == ("chicken breast", "rice")
        assert top.score == pytest.approx(4.0)

    def test_prefer_terms_boost(self, vault):
        results = search(
            vault, SearchFilters(prefer_terms=frozenset({"pasta"}))
        )
        assert results[0].recipe_id == "rcp-shrimp"
        assert results[0].prefer_matches == ("pasta",)


@dataclass(frozen=True)
class FakeEntry:
    payload: dict = field(default_factory=dict)


class TestConstraintSeam:
    def test_avoids_allergen_maps_to_hard_block(self):
        filters = filters_from_constraints(
            [FakeEntry({"abstracted_text": "avoids shellfish"})]
        )
        assert filters.exclude_allergens == frozenset({"shellfish"})
        assert filters.exclude_ingredients == frozenset()

    def test_avoids_non_allergen_maps_to_ingredient_exclusion(self):
        filters = filters_from_constraints(
            [FakeEntry({"abstracted_text": "avoids cilantro"})]
        )
        assert filters.exclude_ingredients == frozenset({"cilantro"})

    def test_prefers_maps_to_boost(self):
        filters = filters_from_constraints(
            [FakeEntry({"abstracted_text": "prefers italian"})]
        )
        assert filters.prefer_terms == frozenset({"italian"})

    def test_base_filters_preserved(self):
        base = SearchFilters(query="soup", max_total_time_min=30)
        filters = filters_from_constraints(
            [FakeEntry({"abstracted_text": "avoids eggs"})], base=base
        )
        assert filters.query == "soup"
        assert filters.max_total_time_min == 30
        assert filters.exclude_allergens == frozenset({"eggs"})

    def test_end_to_end_constraint_search(self, vault):
        filters = filters_from_constraints(
            [
                FakeEntry({"abstracted_text": "avoids shellfish"}),
                FakeEntry({"abstracted_text": "prefers chicken"}),
            ]
        )
        results = search(vault, filters)
        ids = [r.recipe_id for r in results]
        assert "rcp-shrimp" not in ids
        assert ids[0] == "rcp-chicken"


class TestCli:
    def _seed(self, data_dir):
        from nutrime.app import initialize

        app = initialize(data_dir=data_dir)
        vault = RecipeVault(app.corpus_dir)
        vault.write(
            "rcp-chicken",
            _frontmatter("rcp-chicken", "Quick Chicken Creole", total_time=25),
            _body("@chicken breasts{2}", "@rice{1%cup}"),
        )
        return app

    def test_search_output_carries_attribution(self, tmp_path, capsys):
        from nutrime.cli import main

        self._seed(tmp_path / "data")
        code = main(
            ["recipes", "search", "--query", "chicken", "--data-dir",
             str(tmp_path / "data")]
        )
        out = capsys.readouterr().out
        assert code == 0
        assert "Quick Chicken Creole" in out
        assert "Source: TheMealDB" in out

    def test_list_output_carries_attribution(self, tmp_path, capsys):
        from nutrime.cli import main

        self._seed(tmp_path / "data")
        assert main(["recipes", "list", "--data-dir", str(tmp_path / "data")]) == 0
        assert "Source: TheMealDB" in capsys.readouterr().out

    def test_search_no_results(self, tmp_path, capsys):
        from nutrime.cli import main

        self._seed(tmp_path / "data")
        code = main(
            ["recipes", "search", "--query", "octopus", "--data-dir",
             str(tmp_path / "data")]
        )
        assert code == 0
        assert "no recipes matched" in capsys.readouterr().out


class TestCategorySetFilters:
    """5.4 additions — corpus categories are not a clean slot vocabulary."""

    @pytest.fixture()
    def mixed(self, tmp_path):
        vault = RecipeVault(tmp_path / "mixed")
        vault.write(
            "rcp-beef",
            _frontmatter("rcp-beef", "Beef Main", categories=["beef"]),
            _body("@beef{1}"),
        )
        vault.write(
            "rcp-cake",
            _frontmatter("rcp-cake", "Cake", categories=["dessert"]),
            _body("@flour{1}"),
        )
        vault.write(
            "rcp-eggs",
            _frontmatter("rcp-eggs", "Eggs", categories=["breakfast"]),
            _body("@egg{2}"),
        )
        return vault

    def test_exclude_categories_rejects_matching(self, mixed):
        results = search(
            mixed,
            SearchFilters(exclude_categories=frozenset({"dessert", "breakfast"})),
        )
        assert [r.recipe_id for r in results] == ["rcp-beef"]

    def test_categories_any_matches_on_one(self, mixed):
        results = search(
            mixed,
            SearchFilters(meal_categories_any=frozenset({"dessert", "breakfast"})),
        )
        assert {r.recipe_id for r in results} == {"rcp-cake", "rcp-eggs"}

    def test_unset_category_filters_are_inert(self, mixed):
        assert len(search(mixed, SearchFilters())) == 3

    def test_exact_meal_category_still_works(self, mixed):
        results = search(mixed, SearchFilters(meal_category="beef"))
        assert [r.recipe_id for r in results] == ["rcp-beef"]
