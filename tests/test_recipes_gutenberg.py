"""Gutenberg Bookshelf 419 adapter — boilerplate strip, segmentation, seed."""

from __future__ import annotations

import pytest

from nutrime.recipes.gutenberg import (
    BOOKS,
    SOURCE_NAME,
    convert_recipe,
    seed_recipes,
    strip_pg_boilerplate,
)
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.web import Pacer

_NOP_PACER = Pacer(delay_s=0.0)


def _wrap_pg(content: str, title: str = "A COOK BOOK") -> str:
    return (
        f"Front matter junk.\n"
        f"*** START OF THE PROJECT GUTENBERG EBOOK {title} ***\n"
        f"{content}\n"
        f"*** END OF THE PROJECT GUTENBERG EBOOK {title} ***\n"
        f"License boilerplate."
    )


_BEETON_SAMPLE = """
SOUPS.

RICH STRONG STOCK.

104. INGREDIENTS.--4 lbs. of shin of beef, 3 small onions (omit
in summer, lest they ferment), 1-1/2 oz. of salt.

_Mode_.--Line a stewpan with the beef and simmer gently.

_Time_.--5 hours. _Average cost_, 1s. 3d. per quart.

_Sufficient_ for 8 persons.

PLAIN SOUP.

105. INGREDIENTS.--2 carrots, 1 turnip.

_Mode_.--Boil everything.

_Time_.--1 hour 30 minutes.

DOMESTIC SERVANTS.

FURNITURE GLOSS.

106. INGREDIENTS.--Beeswax, turpentine.

_Mode_.--Polish the table.
"""

_FARMER_SAMPLE = """
                        BREAD AND BREAD MAKING

                        Baking Powder Biscuit I

                  2 cups flour
                  4 teaspoons baking powder
                  ¾ cup milk

Mix dry ingredients, and sift twice. Toss on a floured board and bake
in hot oven twelve to fifteen minutes.

                        Iced Tea

                  2 teaspoons tea
                  1 cup boiling water

Steep the tea, then pour over ice and serve with sugar as desired.

                                 INDEX

                        Our guarantee, Serial No. 685

                  1 advertisement thing

Buy our products today because they are excellent and modern.
"""

_CURY_SAMPLE = """
THE PROLOGUE.

I. FOR TO MAKE FURMENTY [1].

Nym clene Wete and bray it in a morter wel that the holys gon al of
and seyt yt til it breste and nym yt up.

[1] See again, No. I. of the second part.

FOR TO BOILE FESAUNTES. PARTRUCHES. XXXV.

Take gode broth and do thereto the fesauntes and let them boile
til they be tendre and serve forth.

FOR LL. MS. ED. SÆPE. XL.

Editorial apparatus that should not become a recipe body here.
"""

_GOLDEN_SAMPLE = """
PREFACE.

This book is dedicated to the golden age of good eating and health.

BAKING-POWDER BISCUIT.

One quart of sifted flour, three-quarters of a cup of butter, enough
milk to make a soft dough. Roll thin and bake in a quick oven.

TOOTH POWDER.

One ounce of powdered orris root mixed with chalk, definitely not food.
"""


class TestStripBoilerplate:
    def test_strips_front_and_back(self):
        inner = strip_pg_boilerplate(_wrap_pg("THE CONTENT"))
        assert "THE CONTENT" in inner
        assert "Front matter junk" not in inner
        assert "License boilerplate" not in inner

    def test_no_markers_passthrough(self):
        assert strip_pg_boilerplate("just text") == "just text"


class TestSegmentBeeton:
    def _recipes(self):
        return BOOKS["beeton"].segment(_BEETON_SAMPLE)

    def test_two_food_recipes_found(self):
        recipes = self._recipes()
        assert [r.title for r in recipes] == ["Rich Strong Stock", "Plain Soup"]

    def test_household_section_cut(self):
        assert all("Gloss" not in r.title for r in self._recipes())

    def test_ingredients_split_paren_aware(self):
        stock = self._recipes()[0]
        assert "4 lbs. of shin of beef" in stock.ingredient_lines
        assert (
            "3 small onions (omit in summer, lest they ferment)"
            in stock.ingredient_lines
        )
        assert "1-1/2 oz. of salt" in stock.ingredient_lines

    def test_time_and_yields_extracted(self):
        stock, soup = self._recipes()
        assert stock.total_time_min == 300
        assert stock.yields_count == 8
        assert soup.total_time_min == 90
        assert soup.yields_count is None

    def test_upstream_ids_from_paragraph_numbers(self):
        assert [r.upstream_id for r in self._recipes()] == [
            "pg10136-p0104",
            "pg10136-p0105",
        ]


class TestSegmentFarmer:
    def _recipes(self):
        return BOOKS["farmer"].segment(_FARMER_SAMPLE)

    def test_titles_and_ingredients(self):
        recipes = self._recipes()
        assert [r.title for r in recipes] == [
            "Baking Powder Biscuit I",
            "Iced Tea",
        ]
        assert recipes[0].ingredient_lines == (
            "2 cups flour",
            "4 teaspoons baking powder",
            "¾ cup milk",
        )

    def test_index_and_ads_cut(self):
        titles = [r.title for r in self._recipes()]
        assert not any("guarantee" in t.lower() for t in titles)

    def test_steps_are_flush_left_paragraphs(self):
        biscuit = self._recipes()[0]
        assert biscuit.steps[0].startswith("Mix dry ingredients")


class TestSegmentFormeOfCury:
    def _recipes(self):
        return BOOKS["forme_of_cury"].segment(_CURY_SAMPLE)

    def test_leading_and_trailing_numeral_formats(self):
        recipes = self._recipes()
        assert [r.upstream_id for r in recipes] == ["pg8102-i", "pg8102-r-xxxv"]

    def test_footnote_marks_stripped(self):
        furmenty = self._recipes()[0]
        assert furmenty.title == "For To Make Furmenty"
        assert all("[1]" not in step for step in furmenty.steps)

    def test_editorial_apparatus_rejected(self):
        titles = [r.title for r in self._recipes()]
        assert not any("Sæpe" in t for t in titles)

    def test_narrative_recipes_have_no_ingredient_lines(self):
        assert all(r.ingredient_lines == () for r in self._recipes())


class TestSegmentGoldenAge:
    def _recipes(self):
        return BOOKS["golden_age"].segment(_GOLDEN_SAMPLE)

    def test_recipe_found_preface_skipped(self):
        assert [r.title for r in self._recipes()] == ["Baking-Powder Biscuit"]

    def test_household_tail_cut(self):
        assert all("Tooth" not in r.title for r in self._recipes())


class TestConvertRecipe:
    def test_beeton_conversion_headline_fields(self):
        profile = BOOKS["beeton"]
        raw = profile.segment(_BEETON_SAMPLE)[0]
        converted = convert_recipe(raw, profile, ingested_at="2026-07-15T00:00:00Z")
        fm = converted.frontmatter
        assert fm["title"] == "Rich Strong Stock"
        assert fm["estimated_total_time_min"] == 300
        assert fm["yields"]["count"] == 8
        assert fm["meal_categories"] == ["historical"]
        assert fm["attribution"]["upstream_id"] == "pg10136-p0104"
        assert "Household Management" in fm["historical_context_note"]
        assert "@shin of beef{4%lbs}" in converted.cooklang_body

    def test_narrative_allergen_detection_over_body(self):
        profile = BOOKS["golden_age"]
        raw = profile.segment(_GOLDEN_SAMPLE)[0]
        converted = convert_recipe(raw, profile, ingested_at="2026-07-15T00:00:00Z")
        allergens = converted.frontmatter["top_allergens_present"]
        assert "dairy" in allergens  # butter + milk in the narrative
        assert "gluten" in allergens  # flour in the narrative

    def test_book_metadata_in_cooklang(self):
        profile = BOOKS["forme_of_cury"]
        raw = profile.segment(_CURY_SAMPLE)[0]
        converted = convert_recipe(raw, profile, ingested_at="2026-07-15T00:00:00Z")
        assert ">> book: The Forme of Cury" in converted.cooklang_body
        assert ">> published: ~1390" in converted.cooklang_body


class TestSeedRecipes:
    @pytest.fixture()
    def vault(self, tmp_path):
        return RecipeVault(tmp_path / "corpus")

    def _fetcher(self):
        mapping = {
            BOOKS["beeton"].text_url: _wrap_pg(_BEETON_SAMPLE),
            BOOKS["golden_age"].text_url: _wrap_pg(_GOLDEN_SAMPLE),
        }

        def fetch(url: str) -> str:
            return mapping[url]

        return fetch

    def test_writes_recipes_from_selected_books(self, vault):
        outcome = seed_recipes(
            vault,
            fetcher=self._fetcher(),
            pacer=_NOP_PACER,
            books=("beeton", "golden_age"),
        )
        assert outcome.written == 3  # 2 beeton + 1 golden_age
        assert vault.count() == 3

    def test_second_seed_skips_by_upstream_id(self, vault):
        fetcher = self._fetcher()
        seed_recipes(
            vault, fetcher=fetcher, pacer=_NOP_PACER, books=("beeton",)
        )
        outcome = seed_recipes(
            vault, fetcher=fetcher, pacer=_NOP_PACER, books=("beeton",)
        )
        assert outcome.written == 0
        assert set(outcome.skipped_upstream_ids) == {
            "pg10136-p0104",
            "pg10136-p0105",
        }

    def test_limit_caps_writes(self, vault):
        outcome = seed_recipes(
            vault,
            fetcher=self._fetcher(),
            pacer=_NOP_PACER,
            books=("beeton", "golden_age"),
            limit=1,
        )
        assert outcome.written == 1

    def test_unknown_book_key_raises(self, vault):
        with pytest.raises(ValueError, match="unknown book"):
            seed_recipes(
                vault,
                fetcher=self._fetcher(),
                pacer=_NOP_PACER,
                books=("narnia_cookbook",),
            )

    def test_source_name_attribution(self, vault):
        seed_recipes(
            vault, fetcher=self._fetcher(), pacer=_NOP_PACER,
            books=("golden_age",),
        )
        record = vault.list_recipes()[0]
        assert record.frontmatter["attribution"]["source_name"] == SOURCE_NAME
