"""V1-V4 vision-gap features — learning loop, use-it-up, novelty, equipment."""

from pathlib import Path

import pytest

from nutrime.recipes.frontmatter import Attribution, Yields, build_recipe_frontmatter
from nutrime.recipes.ids import new_recipe_id
from nutrime.recipes.search import SearchFilters, search
from nutrime.recipes.store import RecipeVault


def _write(vault, title, *, ingredients=("beef",), cuisine=(), time_min=None):
    rid = new_recipe_id()
    fm = build_recipe_frontmatter(
        recipe_id=rid,
        title=title,
        attribution=Attribution(
            source_name="t", source_url="https://e.com/r", source_license="t",
            ingested_at="2026-10-04T00:00:00Z", ingestion_method="test_v1",
        ),
        source_status="live",
        last_source_check_at="2026-10-04T00:00:00Z",
        yields=Yields(count=2),
        top_allergens_present=[],
        cuisine_tradition_tags=list(cuisine),
        estimated_total_time_min=time_min,
    )
    body = "\n".join(f"@{n}{{1}}" for n in ingredients)
    vault.write(rid, fm, body)
    return rid


@pytest.fixture
def vault(tmp_path: Path) -> RecipeVault:
    v = RecipeVault(tmp_path)
    v.ensure()
    return v


class TestV1ExperienceBoosts:
    def test_loved_beats_equal_unloved(self, vault) -> None:
        loved = _write(vault, "Loved Stew")
        _write(vault, "Plain Stew")
        experience = {loved: {"times_cooked": 3, "avg_enjoyment": 5.0,
                              "avg_ease": 4.0, "avg_time_delta_min": None}}
        results = search(vault, SearchFilters(experience=experience))
        assert results[0].recipe_id == loved
        assert results[0].times_cooked == 3
        assert results[0].avg_enjoyment == 5.0

    def test_disliked_sinks_but_never_excluded(self, vault) -> None:
        disliked = _write(vault, "Awful Casserole")
        _write(vault, "Neutral Soup")
        experience = {disliked: {"times_cooked": 1, "avg_enjoyment": 1.0,
                                 "avg_ease": 2.0, "avg_time_delta_min": None}}
        results = search(vault, SearchFilters(experience=experience))
        assert results[-1].recipe_id == disliked
        assert len(results) == 2  # still present

    def test_history_never_outweighs_fridge(self, vault) -> None:
        # 5-star history (+2.0) vs one extra on-hand match (+2.0) → match
        # count sorts first regardless of score.
        loved_one_match = _write(vault, "Loved One-Match", ingredients=("beef",))
        plain_two_match = _write(
            vault, "Plain Two-Match", ingredients=("beef", "onion")
        )
        experience = {loved_one_match: {"times_cooked": 5, "avg_enjoyment": 5.0,
                                        "avg_ease": 5.0, "avg_time_delta_min": None}}
        results = search(
            vault,
            SearchFilters(
                on_hand=frozenset({"beef", "onion"}), experience=experience
            ),
        )
        assert results[0].recipe_id == plain_two_match

    def test_personal_time_corrects_budget_filter(self, vault) -> None:
        rid = _write(vault, "Optimistic Bake", time_min=30)
        experience = {rid: {"times_cooked": 2, "avg_enjoyment": 4.0,
                            "avg_ease": 3.0, "avg_time_delta_min": 25}}
        # Stated 30 min fits a 45-min budget; her real ~55 does not.
        results = search(
            vault,
            SearchFilters(max_total_time_min=45, experience=experience),
        )
        assert results == []
        # Without history it would pass (the blog's claim).
        assert len(search(vault, SearchFilters(max_total_time_min=45))) == 1

    def test_personal_time_surfaces(self, vault) -> None:
        rid = _write(vault, "Slow Roast", time_min=60)
        experience = {rid: {"times_cooked": 1, "avg_enjoyment": 4.0,
                            "avg_ease": 3.0, "avg_time_delta_min": 15}}
        (result,) = search(vault, SearchFilters(experience=experience))
        assert result.total_time_min == 60  # source claim intact
        assert result.personal_time_min == 75


class TestV2ExpiringBoost:
    def test_expiring_tilts_within_same_match_count(self, vault) -> None:
        uses_spinach = _write(vault, "Spinach Pie", ingredients=("spinach",))
        uses_beef = _write(vault, "Beef Pie", ingredients=("beef",))
        results = search(
            vault,
            SearchFilters(
                on_hand=frozenset({"spinach", "beef"}),
                expiring=frozenset({"spinach"}),
            ),
        )
        # Both 1-match; expiring spinach wins the tie through score.
        assert results[0].recipe_id == uses_spinach
        assert results[0].expiring_matches == ("spinach",)

    def test_expiring_never_reorders_match_counts(self, vault) -> None:
        one_expiring = _write(vault, "Spinach Only", ingredients=("spinach",))
        two_plain = _write(vault, "Beef Onion", ingredients=("beef", "onion"))
        results = search(
            vault,
            SearchFilters(
                on_hand=frozenset({"spinach", "beef", "onion"}),
                expiring=frozenset({"spinach"}),
            ),
        )
        assert results[0].recipe_id == two_plain


class TestV2InventoryHelpers:
    def test_expiring_window(self, tmp_path) -> None:
        from nutrime.app import initialize
        from nutrime.inventory.store import (
            InventoryItem,
            add_item,
            expiring_names,
        )

        app = initialize(data_dir=tmp_path)
        add_item(app.substrate, app.tenant_id,
                 InventoryItem(name="spinach", location="fridge",
                               best_by_date="2026-10-06"))
        add_item(app.substrate, app.tenant_id,
                 InventoryItem(name="rice", location="pantry",
                               best_by_date="2027-01-01"))
        add_item(app.substrate, app.tenant_id,
                 InventoryItem(name="old yogurt", location="fridge",
                               best_by_date="2026-09-30"))
        soon = expiring_names(app.substrate, app.tenant_id, today="2026-10-04")
        names = {i.name for i in soon}
        # #55: past-due is EXCLUDED from use-it-up (never a cooking
        # candidate); it surfaces via expired_names instead.
        assert names == {"spinach"}
        from nutrime.inventory.store import expired_names

        tossed = {i.name for i in expired_names(
            app.substrate, app.tenant_id, today="2026-10-04")}
        assert tossed == {"old yogurt"}
        app.substrate.close(); app.operational.close()

    def test_expired_perishable_never_a_planner_candidate(self, tmp_path) -> None:
        # #55 end-to-end: raw chicken (2-day shelf life) entered with the
        # "about a week" freshness chip is expired — the planner's
        # use-it-up pool (expiring_names) must not contain it.
        from datetime import date

        from nutrime.app import initialize
        from nutrime.inventory.intake import best_by_from_freshness
        from nutrime.inventory.store import (
            InventoryItem,
            add_item,
            expiring_names,
        )

        today = date(2026, 10, 6)
        best_by = best_by_from_freshness(2, 7, today=today)
        assert best_by < "2026-10-06"  # expired, not clamped to today

        app = initialize(data_dir=tmp_path)
        add_item(app.substrate, app.tenant_id,
                 InventoryItem(name="raw chicken", location="fridge",
                               best_by_date=best_by))
        pool = expiring_names(
            app.substrate, app.tenant_id, today=today.isoformat()
        )
        assert pool == []
        app.substrate.close(); app.operational.close()

    def test_remove_by_name_exact_case_insensitive(self, tmp_path) -> None:
        from nutrime.app import initialize
        from nutrime.inventory.store import (
            InventoryItem,
            add_item,
            list_items,
            remove_items_by_name,
        )

        app = initialize(data_dir=tmp_path)
        add_item(app.substrate, app.tenant_id,
                 InventoryItem(name="Spinach", location="fridge"))
        add_item(app.substrate, app.tenant_id,
                 InventoryItem(name="beef", location="freezer"))
        removed = remove_items_by_name(
            app.substrate, app.tenant_id, ["spinach"]
        )
        assert removed == ["Spinach"]
        assert [i.name for i in list_items(app.substrate, app.tenant_id)] == ["beef"]
        app.substrate.close(); app.operational.close()


class TestV3Novelty:
    def test_never_cooked_cuisine_boosted(self, vault) -> None:
        novel = _write(vault, "Pho", cuisine=("vietnamese",))
        cooked = _write(vault, "Tacos", cuisine=("mexican",))
        results = search(
            vault,
            SearchFilters(cooked_cuisines=frozenset({"mexican"})),
        )
        assert results[0].recipe_id == novel
        assert results[0].novel_cuisine is True

    def test_stated_preference_beats_novelty(self, vault) -> None:
        novel = _write(vault, "Pho", cuisine=("vietnamese",))
        preferred = _write(
            vault, "Chicken Tacos", ingredients=("chicken",),
            cuisine=("mexican",),
        )
        results = search(
            vault,
            SearchFilters(
                cooked_cuisines=frozenset({"mexican"}),
                prefer_terms=frozenset({"chicken"}),
            ),
        )
        # preference 1.5 > novelty 0.5
        assert results[0].recipe_id == preferred

    def test_none_disables_novelty(self, vault) -> None:
        _write(vault, "Pho", cuisine=("vietnamese",))
        (result,) = search(vault, SearchFilters())
        assert result.novel_cuisine is False


class TestV4Equipment:
    def test_jsonld_tool_shapes(self) -> None:
        from nutrime.recipes.jsonld import convert_recipe_node

        node = {
            "@type": "Recipe",
            "name": "Mixer Bread",
            "recipeIngredient": ["1 cup flour"],
            "recipeInstructions": "Mix and bake.",
            "recipeYield": "1",
            "tool": [
                "stand mixer",
                {"@type": "HowToTool", "name": "9x13 pan"},
                "Stand Mixer",  # dupe, different case
            ],
        }
        converted = convert_recipe_node(
            node, source_url="https://e.com/r"
        )
        assert converted.frontmatter["equipment_required"] == [
            "stand mixer", "9x13 pan",
        ]

    def test_absent_tool_leaves_field_out(self) -> None:
        from nutrime.recipes.jsonld import convert_recipe_node

        node = {
            "@type": "Recipe",
            "name": "Plain Toast",
            "recipeIngredient": ["bread"],
            "recipeInstructions": "Toast it.",
            "recipeYield": "1",
        }
        converted = convert_recipe_node(node, source_url="https://e.com/r")
        assert "equipment_required" not in converted.frontmatter


class TestFeedbackBulkHelpers:
    def test_experience_summaries_matches_single(self, tmp_path) -> None:
        from nutrime.app import initialize
        from nutrime.feedback import (
            experience_summaries,
            record_cooking_experience,
            record_meal_event,
            recipe_experience_summary,
        )

        app = initialize(data_dir=tmp_path)
        mev = record_meal_event(
            app.substrate, app.tenant_id,
            recipe_id="rcp-q", recipe_title="Soup",
        )
        record_cooking_experience(
            app.substrate, app.tenant_id,
            meal_event_id=mev, ease_rating=4, enjoyment_rating=5,
        )
        bulk = experience_summaries(app.substrate, app.tenant_id)
        single = recipe_experience_summary(app.substrate, app.tenant_id, "rcp-q")
        assert bulk["rcp-q"] == single
        app.substrate.close(); app.operational.close()

    def test_cooked_cuisines(self, tmp_path) -> None:
        from nutrime.app import initialize
        from nutrime.feedback import cooked_cuisines, record_meal_event

        app = initialize(data_dir=tmp_path)
        vault = RecipeVault(app.corpus_dir)
        vault.ensure()
        rid = _write(vault, "Tacos", cuisine=("mexican",))
        record_meal_event(
            app.substrate, app.tenant_id, recipe_id=rid, recipe_title="Tacos"
        )
        assert cooked_cuisines(app.substrate, app.tenant_id, vault) == {"mexican"}
        app.substrate.close(); app.operational.close()
