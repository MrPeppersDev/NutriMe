"""Corpus hygiene (V0) — title normalization + vet/quarantine pass."""

from pathlib import Path

from nutrime.recipes.frontmatter import Attribution, Yields, build_recipe_frontmatter
from nutrime.recipes.ids import new_recipe_id
from nutrime.recipes.search import SearchFilters, search
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.vetting import normalize_title, vet_vault


class TestNormalizeTitle:
    def test_shouting_caps_title_cased(self) -> None:
        assert (
            normalize_title("SESAME-GINGER CUCUMBER SOBA NOODLE SALAD")
            == "Sesame-Ginger Cucumber Soba Noodle Salad"
        )

    def test_small_words_stay_lower(self) -> None:
        assert (
            normalize_title("CHICKEN AND RICE WITH A TWIST")
            == "Chicken and Rice with a Twist"
        )

    def test_trailing_recipe_noise_stripped(self) -> None:
        assert normalize_title("Baked Salmon Recipe") == "Baked Salmon"
        assert normalize_title("Adana Kebab — Recipe Card") == "Adana Kebab"

    def test_entities_and_whitespace(self) -> None:
        assert normalize_title("Mac &amp; Cheese   Bake") == "Mac & Cheese Bake"

    def test_normal_title_untouched(self) -> None:
        assert (
            normalize_title("Chicken Souvlaki Bowls with Garlic Fries.")
            == "Chicken Souvlaki Bowls with Garlic Fries."
        )

    def test_forced_case_tokens(self) -> None:
        assert normalize_title("TEXAS BBQ BRISKET") == "Texas BBQ Brisket"


def _write(vault, title, body="@beef{500%g}\nSimmer."):
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
    )
    vault.write(rid, fm, body)
    return rid


class TestVetVault:
    def test_normalizes_and_keeps_original(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path)
        vault.ensure()
        rid = _write(vault, "GRILLED CHICKEN KEBAB BOWLS")
        outcome = vet_vault(vault)
        assert outcome.titles_normalized == 1
        record = vault.read(rid)
        assert record.frontmatter["title"] == "Grilled Chicken Kebab Bowls"
        assert record.frontmatter["title_original"] == "GRILLED CHICKEN KEBAB BOWLS"
        assert record.frontmatter["vetting_status"] == "vetted"

    def test_quarantines_segmentation_artifacts(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path)
        vault.ensure()
        _write(vault, "Ii", body="")
        _write(vault, "XIV", body="")
        rid_junk = _write(vault, "Salt", body="")  # no ingredients, no prose
        rid_good = _write(vault, "Beef Stew")
        outcome = vet_vault(vault)
        assert outcome.quarantined == 3
        assert vault.read(rid_junk).frontmatter["vetting_status"] == "quarantined"
        assert vault.read(rid_good).frontmatter["vetting_status"] == "vetted"

    def test_narrative_historical_recipe_passes(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path)
        vault.ensure()
        prose = (
            "Take fat capons and boil them in good broth with whole peppers"
            " and saffron, then grind almonds and temper with the broth."
        )
        rid = _write(vault, "Cormarye", body=prose)
        vet_vault(vault)
        assert vault.read(rid).frontmatter["vetting_status"] == "vetted"

    def test_idempotent_second_pass(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path)
        vault.ensure()
        _write(vault, "GRILLED THING")
        vet_vault(vault)
        second = vet_vault(vault)
        assert second.titles_normalized == 0
        assert second.already_vetted == 1

    def test_quarantined_excluded_from_search(self, tmp_path: Path) -> None:
        vault = RecipeVault(tmp_path)
        vault.ensure()
        _write(vault, "III", body="")
        rid_good = _write(vault, "Beef Stew")
        vet_vault(vault)
        results = search(vault, SearchFilters())
        assert [r.recipe_id for r in results] == [rid_good]


# -- V2 (issue #31) -------------------------------------------------------------


def _body(ingredients: list[str], steps: list[str]) -> str:
    return (
        "-- Ingredients\n\n" + "\n".join(ingredients)
        + "\n\n-- Instructions\n\n" + "\n".join(steps) + "\n"
    )


GOOD_STEPS = [
    "Brown the beef in batches over high heat.",
    "Add the carrots and stock, then simmer for two hours until tender.",
]


def _write_v2(
    vault, title, body, *, method="test_v1", allergens=(), yields=2,
    ingested_at="2026-10-04T00:00:00Z", **extra,
):
    rid = new_recipe_id()
    fm = build_recipe_frontmatter(
        recipe_id=rid,
        title=title,
        attribution=Attribution(
            source_name="t", source_url="https://e.com/r", source_license="t",
            ingested_at=ingested_at, ingestion_method=method,
        ),
        source_status="live",
        last_source_check_at="2026-10-04T00:00:00Z",
        yields=Yields(count=yields),
        top_allergens_present=list(allergens),
    )
    fm.update(extra)
    vault.write(rid, fm, body)
    return rid


def _vault(tmp_path: Path) -> RecipeVault:
    vault = RecipeVault(tmp_path)
    vault.ensure()
    return vault


class TestQualityFindings:
    def test_clean_recipe_has_no_flags(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(vault, "Beef Stew", _body(["@beef{500%g}", "@carrot{3}"], GOOD_STEPS))
        vet_vault(vault)
        fm = vault.read(rid).frontmatter
        assert fm["vetting_status"] == "vetted"
        assert "vetting_flags" not in fm
        from nutrime.recipes.vetting import VETTING_VERSION

        assert fm["vetting_version"] == VETTING_VERSION

    def test_pointer_only_method_quarantined(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Mystery Cake",
            _body(["@flour{2%cups}", "@sugar{1%cup}"], ["Watch the video for the full method."]),
        )
        vet_vault(vault)
        fm = vault.read(rid).frontmatter
        assert fm["vetting_status"] == "quarantined"
        assert fm["vetting_reason"].startswith("instructions_elsewhere")

    def test_page_chrome_ingredient_quarantined(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Soup",
            _body(["@onion{1}", "@Subscribe to our newsletter{}"], GOOD_STEPS),
        )
        vet_vault(vault)
        assert vault.read(rid).frontmatter["vetting_status"] == "quarantined"

    def test_linked_ingredient_only_flagged(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Bowl",
            _body(["@[granola | https://example.com/granola]{1%cup}", "@yogurt{1%cup}"], GOOD_STEPS),
        )
        vet_vault(vault)
        fm = vault.read(rid).frontmatter
        assert fm["vetting_status"] == "vetted"
        assert fm["vetting_flags"] == ["ingredient_has_link"]

    def test_roundup_page_quarantined(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "40 Spooky Halloween Cocktail Recipes", _body(["@vodka{2%oz}"], []),
        )
        vet_vault(vault)
        assert vault.read(rid).frontmatter["vetting_reason"].startswith("roundup_page")

    def test_review_flags(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        no_method = _write_v2(vault, "Lime Chicken", _body(["@chicken{1}", "@lime{2}"], []))
        thin = _write_v2(vault, "Omelette", _body(["@egg{2}"], ["Cook."]))
        huge_qty = _write_v2(
            vault, "Brine", _body(["@salt{200%tbsp}", "@water{4%l}"], GOOD_STEPS)
        )
        odd_yield = _write_v2(vault, "Dressing Mix", _body(["@oregano{1%tbsp}"], GOOD_STEPS), yields=300)
        odd_time = _write_v2(
            vault, "Spinach", _body(["@spinach{1}"], GOOD_STEPS),
            estimated_active_time_min=30, estimated_total_time_min=10,
        )
        vet_vault(vault)
        flags = {rid: vault.read(rid).frontmatter.get("vetting_flags") for rid in
                 (no_method, thin, huge_qty, odd_yield, odd_time)}
        assert flags[no_method] == ["no_instructions"]
        assert flags[thin] == ["thin_instructions"]
        assert flags[huge_qty] == ["implausible_quantity"]
        assert flags[odd_yield] == ["implausible_yield"]
        assert flags[odd_time] == ["active_exceeds_total"]
        # flagged rows stay searchable
        assert vault.read(no_method).frontmatter["vetting_status"] == "vetted"

    def test_multi_component_repeats_are_fine(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Pie",
            _body(["@butter{100%g}", "@flour{200%g}", "@butter{20%g}", "@apple{4}"], GOOD_STEPS),
        )
        vet_vault(vault)
        assert "vetting_flags" not in vault.read(rid).frontmatter


class TestAllergenReconcile:
    def test_undeclared_allergen_added_original_kept(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Peanut Noodles",
            _body(["@noodles{200%g}", "@peanut butter{2%tbsp}"], GOOD_STEPS),
            allergens=["wheat"],
        )
        outcome = vet_vault(vault)
        fm = vault.read(rid).frontmatter
        assert "peanuts" in fm["top_allergens_present"]
        assert fm["allergens_original"] == ["wheat"]
        assert outcome.allergens_reconciled == 1

    def test_reconciled_allergen_filters_search(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        _write_v2(
            vault, "Peanut Noodles",
            _body(["@noodles{200%g}", "@peanut butter{2%tbsp}"], GOOD_STEPS),
        )
        vet_vault(vault)
        assert search(vault, SearchFilters(exclude_allergens=frozenset({"peanuts"}))) == []

    def test_stale_false_positive_retired(self, tmp_path: Path) -> None:
        # V4: a recipe stamped "dairy" by the pre-negation detector
        # (almond milk) gets the tag removed on recompute, so dairy
        # avoiders see it again. tree_nuts (the real allergen) stays.
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Overnight Oats",
            _body(["@rolled oats{1%cup}", "@almond milk{1%cup}"], GOOD_STEPS),
            allergens=["dairy", "tree_nuts"],
        )
        outcome = vet_vault(vault)
        fm = vault.read(rid).frontmatter
        assert fm["top_allergens_present"] == ["tree_nuts"]
        assert fm["allergens_original"] == ["dairy", "tree_nuts"]
        assert outcome.allergens_reconciled == 1
        # Visible to dairy avoiders again; still hidden from nut avoiders.
        assert [r.recipe_id for r in search(
            vault, SearchFilters(exclude_allergens=frozenset({"dairy"}))
        )] == [rid]
        assert search(
            vault, SearchFilters(exclude_allergens=frozenset({"tree_nuts"}))
        ) == []

    def test_allergens_original_first_write_wins(self, tmp_path: Path) -> None:
        # #57's pass already stamped allergens_original on 342 live
        # files; a V4 recompute must not overwrite that ingest-time
        # snapshot with #57's intermediate state.
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Smoothie",
            _body(["@almond milk{1%cup}", "@banana{1}"], GOOD_STEPS),
            allergens=["dairy", "tree_nuts"],
        )
        record = vault.read(rid)
        fm = dict(record.frontmatter)
        fm["allergens_original"] = ["tree_nuts"]  # pre-#57 ingest list
        vault.write(rid, fm, record.body)
        vet_vault(vault, revet=True)
        fm = vault.read(rid).frontmatter
        assert fm["allergens_original"] == ["tree_nuts"]
        assert fm["top_allergens_present"] == ["tree_nuts"]

    def test_consistent_tags_untouched(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Peanut Satay",
            _body(["@peanut butter{2%tbsp}", "@rice{1%cup}"], GOOD_STEPS),
            allergens=["peanuts"],
        )
        outcome = vet_vault(vault)
        fm = vault.read(rid).frontmatter
        assert fm["top_allergens_present"] == ["peanuts"]
        assert "allergens_original" not in fm
        assert outcome.allergens_reconciled == 0


class TestDuplicates:
    def test_same_recipe_two_sources_one_hidden_pin_wins(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        ings = ["@chicken{1}", "@rice{2%cups}", "@peas{1%cup}", "@soy sauce{2%tbsp}"]
        api = _write_v2(vault, "Easy Chicken Fried Rice", _body(ings, GOOD_STEPS),
                        method="themealdb_api_v1")
        pin = _write_v2(vault, "Chicken Fried Rice", _body(ings[:3], GOOD_STEPS),
                        method="schema_org_jsonld_v1")
        outcome = vet_vault(vault)
        assert outcome.duplicates == 1
        hidden = vault.read(api).frontmatter
        assert hidden["vetting_status"] == "duplicate"
        assert hidden["duplicate_of"] == pin
        assert [r.recipe_id for r in search(vault, SearchFilters())] == [pin]

    def test_same_title_different_dish_both_kept(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        a = _write_v2(vault, "Summer Salad", _body(["@tomato{3}", "@basil{1}", "@mozzarella{1}"], GOOD_STEPS))
        b = _write_v2(vault, "Summer Salad", _body(["@watermelon{1}", "@feta{100%g}", "@mint{1}"], GOOD_STEPS))
        vet_vault(vault)
        assert {vault.read(r).frontmatter["vetting_status"] for r in (a, b)} == {"vetted"}

    def test_duplicate_released_when_twin_quarantined(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        ings = ["@beef{500%g}", "@carrot{3}", "@onion{1}"]
        first = _write_v2(vault, "Beef Stew", _body(ings, GOOD_STEPS), ingested_at="2026-01-01T00:00:00Z")
        second = _write_v2(vault, "Beef Stew", _body(ings, GOOD_STEPS), ingested_at="2026-02-01T00:00:00Z")
        vet_vault(vault)
        assert vault.read(second).frontmatter["duplicate_of"] == first
        # the canonical copy goes away (quarantined by hand) → its twin returns
        fm = dict(vault.read(first).frontmatter)
        fm["vetting_status"] = "quarantined"
        fm["vetting_reason"] = "de-scope: test"
        vault.write(first, fm, vault.read(first).body)
        vet_vault(vault, revet=True)
        released = vault.read(second).frontmatter
        assert released["vetting_status"] == "vetted"
        assert "duplicate_of" not in released

    def test_v1_rows_reexamined_and_manual_quarantine_kept(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(
            vault, "Old Book Recipe", _body(["@flour{1}"], GOOD_STEPS),
            vetting_status="quarantined", vetting_reason="de-scope: historical corpus",
        )
        v1 = _write_v2(vault, "Stew", _body(["@beef{1}"], GOOD_STEPS), vetting_status="vetted")
        outcome = vet_vault(vault)
        assert outcome.already_vetted == 0  # no version stamp → re-examined
        assert vault.read(rid).frontmatter["vetting_status"] == "quarantined"
        assert vault.read(rid).frontmatter["vetting_reason"].startswith("de-scope")
        from nutrime.recipes.vetting import VETTING_VERSION

        assert vault.read(v1).frontmatter["vetting_version"] == VETTING_VERSION

    def test_second_pass_writes_nothing(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        rid = _write_v2(vault, "Stew", _body(["@beef{1}"], GOOD_STEPS))
        vet_vault(vault)
        before = vault.path_for(rid).stat().st_mtime_ns
        outcome = vet_vault(vault)
        assert outcome.already_vetted == 1
        assert vault.path_for(rid).stat().st_mtime_ns == before


class TestInferMealCategories:
    """V3 (P2 #14): untagged recipes get conservative title-inferred
    categories so desserts can't reach dinner pools by exclusion."""

    def _infer(self, title):
        from nutrime.recipes.store import RecipeRecord
        from nutrime.recipes.vetting import infer_meal_categories

        return infer_meal_categories(
            RecipeRecord(recipe_id="rcp-x", frontmatter={"title": title},
                         body="", path=None)
        )

    def test_desserts_caught(self) -> None:
        for title in ("Ambrosia", "Apple Crisp", "Banana Bread Muffins",
                      "Chocolate Chip Cookies", "Pumpkin Pie",
                      "Rice Pudding", "Strawberry Shortcake"):
            assert "dessert" in self._infer(title), title

    def test_breakfast_and_drinks(self) -> None:
        assert "breakfast" in self._infer("Blueberry Pancakes")
        assert "breakfast" in self._infer("Overnight Oats with Apples")
        assert "drinks" in self._infer("Mango Lassi")
        assert "drinks" in self._infer("Berry Banana Smoothie")

    def test_sides_dips_dressings(self) -> None:
        assert "side" in self._infer("Black Bean Dip")
        assert "side" in self._infer("Honey Mustard Dressing")
        assert "side" in self._infer("Fresh Tomato Salsa")
        assert "side" in self._infer("Creamy Coleslaw")

    def test_mains_stay_untagged(self) -> None:
        # The ambiguous middle keeps main-course-by-exclusion.
        for title in ("2-Step Chicken", "Beef and Broccoli Stir-Fry",
                      "Baked Salmon with Lemon", "Lentil Chili"):
            assert self._infer(title) == [], title

    def test_salad_dressing_is_side_not_salad(self) -> None:
        got = self._infer("Garden Salad Dressing")
        assert "side" in got and "salad" not in got

    def test_vet_vault_fills_only_empty(self, tmp_path: Path) -> None:
        vault = _vault(tmp_path)
        untagged = _write(vault, "Apple Crisp")
        tagged_rid = _write(vault, "Weird Dessert Casserole")
        fm = dict(vault.read(tagged_rid).frontmatter)
        fm["meal_categories"] = ["main course"]  # source said main; trust it
        vault.write(tagged_rid, fm, vault.read(tagged_rid).body)
        outcome = vet_vault(vault, revet=True)
        assert outcome.categorized == 1
        got = vault.read(untagged).frontmatter
        assert got["meal_categories"] == ["dessert"]
        assert got["meal_categories_inferred"] is True
        assert vault.read(tagged_rid).frontmatter["meal_categories"] == ["main course"]

    def test_inferred_dessert_leaves_dinner_pool(self, tmp_path: Path) -> None:
        from nutrime.plans.assemble import candidates_for_slot

        vault = _vault(tmp_path)
        _write(vault, "Peach Cobbler")
        main = _write(vault, "Chicken Stew")
        vet_vault(vault)
        pool = candidates_for_slot(vault, SearchFilters(), "dinner")
        assert [r.recipe_id for r in pool] == [main]
