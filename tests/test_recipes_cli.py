"""CLI wiring for ``nutrime recipes fetch|list``."""

from pathlib import Path

import pytest

from nutrime.cli import main
from nutrime.recipes import themealdb as themealdb_mod


def _sample_meal(meal_id: str = "52772") -> dict:
    meal = {
        "idMeal": meal_id,
        "strMeal": "Sample",
        "strCategory": "Chicken",
        "strArea": "Japanese",
        "strTags": "",
        "strInstructions": "Cook it. Serve.",
        "strSource": "https://example.com/x",
    }
    for i in range(1, 21):
        meal[f"strIngredient{i}"] = "salt" if i == 1 else ""
        meal[f"strMeasure{i}"] = "1 tsp" if i == 1 else ""
    return meal


@pytest.fixture
def stubbed_fetcher(monkeypatch):
    def _fetcher(url: str) -> dict:
        return {"meals": [_sample_meal()]}

    monkeypatch.setattr(themealdb_mod, "_urllib_fetch", _fetcher)


class TestRecipesFetchCLI:
    def test_fetch_writes_to_vault(
        self, tmp_path: Path, capsys, stubbed_fetcher
    ) -> None:
        rc = main(
            [
                "recipes",
                "fetch",
                "--data-dir",
                str(tmp_path),
                "--letters",
                "a",
                "--limit",
                "1",
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "Fetched" in out and "wrote 1" in out

    def test_fetch_rejects_unknown_source(
        self, tmp_path: Path, capsys
    ) -> None:
        rc = main(
            [
                "recipes",
                "fetch",
                "--source",
                "unknown",
                "--data-dir",
                str(tmp_path),
            ]
        )
        assert rc == 2
        out = capsys.readouterr().out
        assert "unknown" in out


class TestRecipesFetchBulkSourcesCLI:
    def test_fetch_nhlbi_writes_to_vault(
        self, tmp_path: Path, capsys, monkeypatch
    ) -> None:
        from nutrime.recipes import nhlbi as nhlbi_mod

        listing = (
            f'<a href="{nhlbi_mod.LISTING_PATH}/test-dish">x</a>'
        )
        recipe = """<html><head><title>Test Dish | NHLBI, NIH</title></head>
<body><h2>Ingredients</h2><ul><li>1 cup rice</li></ul>
<h2>Directions</h2><ol><li>Cook rice.</li></ol></body></html>"""

        def _fetch(url: str) -> str:
            return recipe if url.endswith("/test-dish") else (
                listing if "page=0" in url else "<html></html>"
            )

        monkeypatch.setattr(nhlbi_mod, "_urllib_fetch_text", _fetch)
        rc = main(
            [
                "recipes", "fetch",
                "--source", "nhlbi",
                "--data-dir", str(tmp_path),
                "--delay", "0",
                "--limit", "1",
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "wrote 1" in out

    def test_fetch_myplate_wayback_writes_to_vault(
        self, tmp_path: Path, capsys, monkeypatch
    ) -> None:
        import json as json_mod

        from nutrime.recipes import myplate_wayback as myplate_mod

        cdx = json_mod.dumps([
            ["urlkey", "timestamp", "original", "mimetype",
             "statuscode", "digest", "length"],
            ["gov,myplate)/recipes/test-dish", "20241126000000",
             "https://www.myplate.gov/recipes/test-dish",
             "text/html", "200", "D", "1"],
        ])
        recipe = """<html><head><script type="application/ld+json">
{"@graph": [{"@type": "Recipe", "name": "Test Dish", "recipeYield": "2"}]}
</script></head><body>
<div class="field--name-field-ingredients"><ul><li>1 cup rice</li></ul></div>
<div class="field--name-field-instructions"><ol><li>Cook rice.</li></ol></div>
</body></html>"""

        def _fetch(url: str) -> str:
            return cdx if "cdx" in url else recipe

        monkeypatch.setattr(myplate_mod, "_urllib_fetch_text", _fetch)
        rc = main(
            [
                "recipes", "fetch",
                "--source", "myplate_wayback",
                "--data-dir", str(tmp_path),
                "--delay", "0",
                "--limit", "1",
            ]
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "wrote 1" in out


class TestRecipesListCLI:
    def test_list_empty_shows_placeholder(
        self, tmp_path: Path, capsys
    ) -> None:
        rc = main(["recipes", "list", "--data-dir", str(tmp_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "no recipes yet" in out

    def test_list_after_fetch_shows_titles(
        self, tmp_path: Path, capsys, stubbed_fetcher
    ) -> None:
        main(
            [
                "recipes",
                "fetch",
                "--data-dir",
                str(tmp_path),
                "--letters",
                "a",
                "--limit",
                "1",
            ]
        )
        capsys.readouterr()  # drain
        rc = main(["recipes", "list", "--data-dir", str(tmp_path)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Sample" in out
        assert "japanese" in out
