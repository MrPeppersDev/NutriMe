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


class TestSourceFacetAndOrdering:
    def _write(self, vault, title, method, ingredients):
        from nutrime.recipes.frontmatter import (
            Attribution,
            Yields,
            build_recipe_frontmatter,
        )
        from nutrime.recipes.ids import new_recipe_id

        rid = new_recipe_id()
        fm = build_recipe_frontmatter(
            recipe_id=rid,
            title=title,
            attribution=Attribution(
                source_name="x",
                source_url="https://example.com/r",
                source_license="test",
                ingested_at="2026-10-04T00:00:00Z",
                ingestion_method=method,
            ),
            source_status="live",
            last_source_check_at="2026-10-04T00:00:00Z",
            yields=Yields(count=2),
            top_allergens_present=[],
        )
        body = "\n".join(f"@{name}{{1}}" for name in ingredients)
        vault.write(rid, fm, body)
        return rid

    def test_source_filter(self, tmp_path):
        from nutrime.recipes.search import SearchFilters, search
        from nutrime.recipes.store import RecipeVault

        vault = RecipeVault(tmp_path)
        vault.ensure()
        self._write(vault, "Pinned", "schema_org_jsonld_v1", ["beef"])
        self._write(vault, "Mealdb", "themealdb_api_v1", ["beef"])
        results = search(vault, SearchFilters(sources=frozenset({"pins"})))
        assert [r.title for r in results] == ["Pinned"]
        assert results[0].source == "pins"

    def test_on_hand_count_dominates_boost_score(self, tmp_path):
        from nutrime.recipes.search import SearchFilters, search
        from nutrime.recipes.store import RecipeVault

        vault = RecipeVault(tmp_path)
        vault.ensure()
        # 1 on-hand match but 3 preference boosts (score 2.0 + 4.5 = 6.5)
        self._write(
            vault, "Boosted One-Match", "themealdb_api_v1",
            ["chicken", "salmon", "kale", "berry mix"],
        )
        # 3 on-hand matches, no boosts (score 6.0 — lower than 6.5)
        self._write(
            vault, "Three Match", "themealdb_api_v1",
            ["chicken", "onion", "carrot"],
        )
        filters = SearchFilters(
            on_hand=frozenset({"chicken", "onion", "carrot"}),
            prefer_terms=frozenset({"salmon", "kale", "berry"}),
        )
        results = search(vault, filters)
        assert results[0].title == "Three Match"
        assert len(results[0].on_hand_matches) == 3


class TestOptInSourcesAndPagination:
    def test_historical_excluded_by_default(self, tmp_path):
        from nutrime.recipes.search import SearchFilters, search
        from nutrime.recipes.store import RecipeVault

        t = TestSourceFacetAndOrdering()
        vault = RecipeVault(tmp_path)
        vault.ensure()
        t._write(vault, "Beeton Pudding", "gutenberg_text_v1", ["suet"])
        t._write(vault, "Modern Stew", "themealdb_api_v1", ["beef"])
        results = search(vault, SearchFilters())
        assert [r.title for r in results] == ["Modern Stew"]

    def test_historical_included_when_selected(self, tmp_path):
        from nutrime.recipes.search import SearchFilters, search
        from nutrime.recipes.store import RecipeVault

        t = TestSourceFacetAndOrdering()
        vault = RecipeVault(tmp_path)
        vault.ensure()
        t._write(vault, "Beeton Pudding", "gutenberg_text_v1", ["suet"])
        results = search(
            vault, SearchFilters(sources=frozenset({"historical"}))
        )
        assert [r.title for r in results] == ["Beeton Pudding"]

    def test_search_page_windows_and_totals(self, tmp_path):
        from nutrime.recipes.search import SearchFilters, search_page
        from nutrime.recipes.store import RecipeVault

        t = TestSourceFacetAndOrdering()
        vault = RecipeVault(tmp_path)
        vault.ensure()
        for i in range(30):
            t._write(vault, f"Recipe {i:02d}", "themealdb_api_v1", ["beef"])
        first = search_page(vault, SearchFilters(), limit=24, offset=0)
        assert first.total == 30
        assert len(first.results) == 24
        second = search_page(vault, SearchFilters(), limit=24, offset=24)
        assert len(second.results) == 6
        # no overlap between pages
        ids1 = {r.recipe_id for r in first.results}
        ids2 = {r.recipe_id for r in second.results}
        assert not ids1 & ids2


class TestPantryFirstRanking:
    """User direction 2026-10-06: cookable-without-shopping ranks first,
    then most-on-hand, then fewest-missing; staples never count missing."""

    def _vault(self, tmp_path):
        vault = RecipeVault(tmp_path / "pantry-corpus")
        vault.ensure()
        vault.write(
            "rcp-complete",
            _frontmatter("rcp-complete", "Chicken and Rice"),
            _body("@chicken{1%lb}", "@rice{1%cup}", "@salt{}", "@olive oil{}"),
        )
        vault.write(
            "rcp-one-short",
            _frontmatter("rcp-one-short", "Chicken Rice Almondine"),
            _body("@chicken{1%lb}", "@rice{1%cup}", "@almonds{1%cup}"),
        )
        vault.write(
            "rcp-big-shop",
            _frontmatter("rcp-big-shop", "Chicken Rice Feast"),
            _body(
                "@chicken{1%lb}", "@rice{1%cup}", "@saffron{1%pinch}",
                "@lobster{1}", "@creme fraiche{1%cup}",
            ),
        )
        vault.write(
            "rcp-unrelated",
            _frontmatter("rcp-unrelated", "Aardvark Toast"),
            _body("@bread{2%slices}", "@aardvark{1}"),
        )
        return vault

    def test_cookable_now_beats_higher_match_count(self, tmp_path):
        vault = self._vault(tmp_path)
        results = search(
            vault, SearchFilters(on_hand=frozenset({"chicken", "rice"}))
        )
        titles = [r.title for r in results]
        # complete (2 matches, 0 missing) first; one-short (2 matches,
        # 1 missing) second; big-shop (2 matches, 3 missing) third.
        assert titles[:3] == [
            "Chicken and Rice", "Chicken Rice Almondine", "Chicken Rice Feast"
        ]

    def test_staples_do_not_count_as_missing(self, tmp_path):
        vault = self._vault(tmp_path)
        results = search(
            vault, SearchFilters(on_hand=frozenset({"chicken", "rice"}))
        )
        complete = next(r for r in results if r.recipe_id == "rcp-complete")
        assert complete.missing_ingredients == ()

    def test_missing_lists_what_to_buy(self, tmp_path):
        vault = self._vault(tmp_path)
        results = search(
            vault, SearchFilters(on_hand=frozenset({"chicken", "rice"}))
        )
        short = next(r for r in results if r.recipe_id == "rcp-one-short")
        assert short.missing_ingredients == ("almonds",)

    def test_fewest_missing_breaks_match_ties(self, tmp_path):
        vault = self._vault(tmp_path)
        results = search(
            vault, SearchFilters(on_hand=frozenset({"chicken", "rice"}))
        )
        ids = [r.recipe_id for r in results]
        assert ids.index("rcp-one-short") < ids.index("rcp-big-shop")

    def test_no_inventory_means_no_missing_tracking(self, tmp_path):
        vault = self._vault(tmp_path)
        results = search(vault, SearchFilters())
        assert all(r.missing_ingredients == () for r in results)


class TestStaplesOutOfStock:
    """Staples are assumed on hand — unless the household says otherwise."""

    def _vault(self, tmp_path):
        vault = RecipeVault(tmp_path / "staple-corpus")
        vault.ensure()
        vault.write(
            "rcp-oily",
            _frontmatter("rcp-oily", "Pan-Fried Chicken"),
            _body("@chicken{1%lb}", "@olive oil{2%tbsp}", "@salt{}"),
        )
        return vault

    def test_out_staple_counts_missing(self, tmp_path):
        vault = self._vault(tmp_path)
        base = SearchFilters(on_hand=frozenset({"chicken"}))
        (hit,) = search(vault, base)
        assert hit.missing_ingredients == ()  # oil + salt assumed
        from dataclasses import replace

        (hit,) = search(
            vault, replace(base, out_of_staples=frozenset({"olive oil"}))
        )
        assert hit.missing_ingredients == ("olive oil",)

    def test_other_staples_stay_assumed(self, tmp_path):
        vault = self._vault(tmp_path)
        from dataclasses import replace

        base = SearchFilters(on_hand=frozenset({"chicken"}))
        (hit,) = search(
            vault, replace(base, out_of_staples=frozenset({"olive oil"}))
        )
        assert "salt" not in hit.missing_ingredients

    def test_out_staple_demotes_from_cook_tonight(self, tmp_path):
        from dataclasses import replace

        vault = self._vault(tmp_path)
        vault.write(
            "rcp-no-oil",
            _frontmatter("rcp-no-oil", "Zesty Boiled Chicken"),
            _body("@chicken{1%lb}", "@salt{}"),
        )
        filters = replace(
            SearchFilters(on_hand=frozenset({"chicken"})),
            out_of_staples=frozenset({"olive oil"}),
        )
        results = search(vault, filters)
        # the oil-free recipe is now the only cookable-tonight one
        assert results[0].recipe_id == "rcp-no-oil"
        assert results[0].missing_ingredients == ()


class TestMatchPrecision:
    """Match-quality pass: token boundaries, compound heads, synonyms."""

    def test_no_inside_word_matches(self):
        from nutrime.recipes.search import _terms_match

        for a, b in (
            ("apple", "pineapple"), ("egg", "eggplant"), ("pea", "peanut"),
            ("corn", "cornstarch"), ("ginger", "gingersnaps"),
        ):
            assert not _terms_match(a, b), f"{a} wrongly matched {b}"
            assert not _terms_match(b, a), f"{b} wrongly matched {a}"

    def test_compound_heads_not_satisfied_by_modifier(self):
        from nutrime.recipes.search import _terms_match

        for a, b in (
            ("rice", "rice vinegar"), ("rice", "rice wine"),
            ("milk", "coconut milk"), ("butter", "peanut butter"),
            ("cream", "cream of tartar"), ("onion", "onion powder"),
            ("garlic", "garlic powder"), ("chicken", "chicken stock"),
        ):
            assert not _terms_match(a, b), f"{a} wrongly satisfied {b}"

    def test_head_itself_satisfies_compound(self):
        from nutrime.recipes.search import _terms_match

        assert _terms_match("vinegar", "rice vinegar")
        assert _terms_match("rice vinegar", "rice vinegar")
        assert _terms_match("stock", "chicken stock")

    def test_plain_modifiers_still_match(self):
        from nutrime.recipes.search import _terms_match

        # non-compound phrases keep the generous behavior
        assert _terms_match("chicken", "chicken thighs")
        assert _terms_match("chicken", "boneless chicken breasts")
        assert _terms_match("onion", "yellow onion")
        assert _terms_match("tomatoes", "canned tomatoes, diced")

    def test_synonyms(self):
        from nutrime.recipes.search import _terms_match

        assert _terms_match("green onions", "scallions")
        assert _terms_match("scallion", "green onion, sliced")
        assert _terms_match("chickpeas", "garbanzo beans")
        assert _terms_match("zucchini", "courgette")
        assert _terms_match("shrimp", "prawns")
        assert _terms_match("eggplant", "aubergine")

    def test_exclusion_matcher_keeps_recall(self):
        from nutrime.recipes.search import _exclusion_match

        # safety direction: base-food avoiders catch derived compounds
        assert _exclusion_match("peanut", "peanut butter")
        assert _exclusion_match("onion", "onion powder")
        assert _exclusion_match("milk", "coconut milk") is True  # conservative
        # but token boundaries still hold
        assert not _exclusion_match("egg", "eggplant")
        assert not _exclusion_match("apple", "pineapple")

    def test_junk_lines_do_not_count_missing(self, tmp_path):
        vault = RecipeVault(tmp_path / "junk-corpus")
        vault.ensure()
        vault.write(
            "rcp-prose",
            _frontmatter("rcp-prose", "Historical Duck"),
            _body(
                "@duck{1}",
                "@and truss them at the back of the bird. After the duck is stuffed{}",
                "@To every lb. of lump sugar allow 1 gill of spring water{}",
            ),
        )
        results = search(vault, SearchFilters(on_hand=frozenset({"duck"})))
        (hit,) = results
        assert hit.missing_ingredients == ()  # prose never counts

    def test_descriptor_lines_match_cleanly(self, tmp_path):
        vault = RecipeVault(tmp_path / "desc-corpus")
        vault.ensure()
        vault.write(
            "rcp-desc",
            _frontmatter("rcp-desc", "Herby Potatoes"),
            _body("@medium potatoes, sliced{3}", "@oregano, minced (or 1 tsp dried){}"),
        )
        results = search(vault, SearchFilters(on_hand=frozenset({"potatoes", "oregano"})))
        (hit,) = results
        assert len(hit.on_hand_matches) == 2
        assert hit.missing_ingredients == ()
