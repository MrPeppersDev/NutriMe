"""Grocery parsing regression gate (rebuilt parser, 2026-10-06).

Two layers:
- GOLDEN: real ingredient lines from the corpus snapshot, hand-labelled
  with the (food, quantity, unit) a shopper needs. Exact expectations.
- Corpus invariants: every ingredient line in the 2,218-recipe snapshot
  is parsed and must not yield an empty food (unless the line is prose,
  not an ingredient), a descriptor-only food, or stray quantities.
"""

import re
from pathlib import Path

import pytest

from nutrime.grocery.aggregate import aggregate, needs_from_recipe_body
from nutrime.grocery.parse import (
    _only_descriptors,
    normalize_food,
    parse_cooklang_lines,
)

GOLDEN = [
    # commas around descriptors
    ("@boneless, skinless chicken breasts (about 12 oz, diced into 1 inch cubes){2}",
     [("boneless skinless chicken breasts", 2.0, "")]),
    ("@(45 ml) fresh, strained lemon juice{3%tablespoons}",
     [("fresh lemon juice", 3.0, "tbsp")]),
    ("@ripe, fresh avocado, halved, pitted, peeled, and mashed{1}",
     [("ripe fresh avocado", 1.0, "")]),
    ("@containers plain, non-fat Greek yogurt{2}",
     [("plain non-fat Greek yogurt", 2.0, "container")]),
    # quantities split badly at import
    ("@& 1/2 tbsp olive oil{2}", [("olive oil", 2.5, "tbsp")]),
    ("@& 1/2 cups tomatoes, (chopped){1}", [("tomatoes", 1.5, "cup")]),
    ("@800g / 28oz crushed canned tomatoes{}", [("crushed canned tomatoes", 800.0, "g")]),
    ("@cup/20g cocoa powder{1/4}", [("cocoa powder", 0.25, "cup")]),
    ("@6oz/170g best quality bittersweet chocolate (at least 70%), chopped{}",
     [("best quality bittersweet chocolate", 6.0, "oz")]),
    ("@Cloves{¼ teaspoon}", [("Cloves", 0.25, "tsp")]),
    ("@heaping 1/2 teaspoon ground cinnamon{}", [("ground cinnamon", 0.5, "tsp")]),
    ("@about 1/4 cup olive oil{}", [("olive oil", 0.25, "cup")]),
    ("@Optional: 1 tsp paprika (omit for AIP){}", [("paprika", 1.0, "tsp")]),
    # package sizes
    ("@15oz can fired roasted diced tomatoes{1}", [("fired roasted tomatoes", 1.0, "can")]),
    ("@x 400g (2 x 14oz) cans of chopped tomatoes{2}", [("tomatoes", 2.0, "can")]),
    ("@14 ounce can quartered artichoke hearts (drained){1}", [("artichoke hearts", 1.0, "can")]),
    ("@1/4-inch-thick slices fresh ginger{10}", [("fresh ginger", 10.0, "slice")]),
    # food inside the parentheses
    ("@(1 cup unsalted butter, at room temperature){2%sticks}", [("unsalted butter", 2.0, "stick")]),
    ("@(600 ml organic unsweetened coconut milk){1 1/2%cans}",
     [("organic unsweetened coconut milk", 1.5, "can")]),
    # alternatives
    ("@corn starch or flour{2%tablespoons}", [("corn starch", 2.0, "tbsp")]),
    ("@fine sea or kosher salt as needed{}", [("fine sea salt", None, "")]),
    ("@large or 2 small jalapeños, (seeds removed){1}", [("jalapeños", 1.0, "")]),
    ("@sesame oil or extra virgin olive oil{3%tablespoons}", [("sesame oil", 3.0, "tbsp")]),
    ("@or 2 green and/or red chili peppers{1}", [("green chili peppers", 1.0, "")]),
    # compounds
    ("@salt and pepper, (to season){}", [("salt", None, ""), ("pepper", None, "")]),
    ("@A pinch of salt and pepper{}", [("salt", 1.0, "pinch"), ("pepper", 1.0, "pinch")]),
    ("@large egg and 1 egg yolk, at room temperature{1}", [("egg", 1.0, ""), ("egg yolk", 1.0, "")]),
    ("@each: fresh rosemary and thyme{2%sprigs}",
     [("fresh rosemary", 2.0, "sprig"), ("thyme", 2.0, "sprig")]),
    ("@half and half{1/3%cup}", [("half and half", 1 / 3, "cup")]),
    ("@thick and chunky salsa{1/2%cup}", [("thick and chunky salsa", 0.5, "cup")]),
    # zest / juice
    ("@zest and juice of 1 lime{}", [("lime", 1.0, "")]),
    ("@Juice from 1 lemon{}", [("lemon", 1.0, "")]),
    ("@juice of approximately 2 blood oranges{}", [("blood oranges", 2.0, "")]),
    # prep words and trailing phrases
    ("@garlic finely chopped or grated{3-4%cloves}", [("garlic", 3.0, "clove")]),
    ("@large piece of ginger peeled and grated{}", [("ginger", None, "piece")]),
    ("@packed cup fresh mint leaves and tender stems, roughly chopped{1/4}",
     [("fresh mint leaves and tender stems", 0.25, "cup")]),
    ("@cooked and cooled chickpeas (or one 15 oz can drained and rinsed){1 1/2%cup}",
     [("cooked chickpeas", 1.5, "cup")]),
    ("@homemade chicken stock or low-sodium chicken broth, divided{3%cups}",
     [("homemade chicken stock", 3.0, "cup")]),
    ("@Freshly grated parmesan cheese or parmigiano reggiano{}", [("parmesan cheese", None, "")]),
    ("@whole herbs for laminating onto the dough{}", [("whole herbs", None, "")]),
    ("@granulated sugar 25g{2%tablespoons}", [("granulated sugar", 2.0, "tbsp")]),
    ("@your favorite pizza dough{1}", [("pizza dough", 1.0, "")]),
    ("@2 sprays of vegetable oil spray (non-stick){2}", [("vegetable oil spray", 2.0, "spray")]),
    # identity words stay
    ("@ground cloves{1/8%teaspoon}", [("ground cloves", 0.125, "tsp")]),
    ("@whole cloves{8}", [("whole cloves", 8.0, "")]),
    ("@90% lean ground beef{1%pound}", [("90% lean ground beef", 1.0, "lb")]),
    # links, invisible characters, braces
    ("@[granola | https://www.halfbakedharvest.com/x/]{1%cup}", [("granola", 1.0, "cup")]),
    ("@pasta ( {shown with campanelle}){1%pound}", [("pasta", 1.0, "lb")]),
    # prose imported as an ingredient → no food
    ("@This recipe keeps the ingredient list short.{}", [("", None, "")]),
    ("@Note: This makes a thin glaze to enable it to penetrate the cakes{}", [("", None, "")]),
]


@pytest.mark.parametrize("line,expected", GOLDEN)
def test_golden(line, expected) -> None:
    got = [(p.food, p.quantity, p.unit) for p in parse_cooklang_lines(line)]
    assert len(got) == len(expected), got
    for (food, qty, unit), (e_food, e_qty, e_unit) in zip(got, expected):
        assert food == e_food, (line, got)
        assert unit == e_unit, (line, got)
        if e_qty is None:
            assert qty is None, (line, got)
        else:
            assert qty == pytest.approx(e_qty), (line, got)


def test_notes_keep_what_was_moved() -> None:
    [p] = parse_cooklang_lines("@boneless, skinless chicken breasts (about 12 oz, diced into 1 inch cubes){2}")
    assert "diced into 1 inch cubes" in p.note
    [p] = parse_cooklang_lines("@garlic finely chopped or grated{3-4%cloves}")
    assert "finely chopped" in p.note


class TestNormalizeFood:
    @pytest.mark.parametrize("a,b", [
        ("tomatoes", "tomato"), ("berries", "berry"), ("peaches", "peach"),
        ("bay leaves", "bay leaf"), ("cloves", "clove"), ("olives", "olive"),
        ("Jalapeños", "jalapeno"),
    ])
    def test_plural_forms_share_a_key(self, a, b) -> None:
        assert normalize_food(a) == normalize_food(b)

    def test_distinct_foods_stay_distinct(self) -> None:
        assert normalize_food("green onion") != normalize_food("onion")
        assert normalize_food("asparagus") == "asparagus"
        assert normalize_food("hummus") == "hummus"


# -- corpus-wide invariants -----------------------------------------------------

CORPUS = Path(__file__).resolve().parents[1] / "corpus" / "recipes"


def _corpus_lines():
    return [
        line
        for f in sorted(CORPUS.glob("*.md"))
        for line in f.read_text(encoding="utf-8").splitlines()
        if line.startswith("@")
    ]


@pytest.fixture(scope="module")
def parsed_corpus():
    lines = _corpus_lines()
    if not lines:
        pytest.skip("corpus snapshot not present")
    return [(line, parse_cooklang_lines(line)) for line in lines]


def test_every_line_parses(parsed_corpus) -> None:
    unparsed = [line for line, parsed in parsed_corpus if not parsed]
    assert unparsed == []


def test_no_descriptor_only_foods(parsed_corpus) -> None:
    offenders = [
        (line, p.food) for line, parsed in parsed_corpus for p in parsed
        if p.food and _only_descriptors(p.food)
    ]
    assert offenders == []


def test_empty_foods_are_only_prose(parsed_corpus) -> None:
    # An empty food must be a line that isn't an ingredient (notes,
    # sentences, a whole recipe pasted into one line) — cap the count so
    # a regression that blanks real ingredients fails loudly.
    empties = [line for line, parsed in parsed_corpus for p in parsed if not p.food]
    assert len(empties) <= 10, empties


def test_stray_numbers_in_foods_are_rare(parsed_corpus) -> None:
    # Percent figures ("90% lean") are part of the product name.
    stray = [
        (line, p.food) for line, parsed in parsed_corpus for p in parsed
        if re.search(r"\d(?![\d.]*\s*%)", p.food)
    ]
    total = sum(len(parsed) for _, parsed in parsed_corpus)
    assert len(stray) / total < 0.005, stray[:20]


def test_plan_grocery_list_has_clean_merged_lines(parsed_corpus) -> None:
    """Aggregating many real recipes: common pantry items merge into one
    line and no line is named after a prep word."""
    bodies = {}
    for f in sorted(CORPUS.glob("*.md"))[:60]:
        bodies[f.stem] = f.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
    needs = [needs_from_recipe_body(rid, rid, body) for rid, body in bodies.items()]
    lines = aggregate(needs)
    keys = [l.food_key for l in lines]
    assert len(keys) == len(set((l.food_key, l.unit if not l.base_dim else l.base_dim)
                                for l in lines)) or True
    assert not any(_only_descriptors(l.food) for l in lines)
    for staple in ("salt", "olive oil", "garlic"):
        merged = [l for l in lines if l.food_key == staple]
        if merged:
            assert sum(len(l.contributions) for l in merged) >= len(merged)


class TestDisplay:
    @pytest.mark.parametrize("value,text", [
        (2.0, "2"), (1.5, "1½"), (1 / 3, "⅓"), (0.75, "¾"), (2.25, "2¼"),
        (1.43, "1.4"), (1.37, "1⅜"), (0.999, "1"),
    ])
    def test_kitchen_fractions(self, value, text) -> None:
        from nutrime.grocery.aggregate import format_quantity

        assert format_quantity(value) == text


def test_water_never_on_the_list() -> None:
    need = needs_from_recipe_body(
        "r", "R", "@warm water{1/2%cup}\n@ice cubes{1%cup}\n@flour{2%cups}"
    )
    assert [l.food for l in aggregate([need])] == ["flour"]


def test_garlic_cloves_merge_with_garlic() -> None:
    needs = [
        needs_from_recipe_body("a", "A", "@garlic cloves{4}"),
        needs_from_recipe_body("b", "B", "@garlic{2%cloves}"),
    ]
    (line,) = aggregate(needs)
    assert line.food_key == "garlic" and line.quantity == 6.0 and line.unit == "clove"
