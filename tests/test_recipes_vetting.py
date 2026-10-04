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
