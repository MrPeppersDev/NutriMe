"""LLM pantry-classification tier: routing, validation, fail-safe."""

import json

from nutrime.inventory.intake import preview
from nutrime.inventory.llm_classify import _parse, needs_llm, refine


class FakeClient:
    def __init__(self, reply: str):
        self.reply = reply
        self.requests = []

    def complete(self, request):
        self.requests.append(request)

        class R:
            text = self.reply

        return R()


class ExplodingClient:
    def complete(self, request):
        raise RuntimeError("model fell over")


def _answer(entries) -> str:
    return json.dumps(entries)


class TestRouting:
    def test_known_plain_foods_skip_the_model(self) -> None:
        items = preview("milk, rice, spinach")
        assert not any(needs_llm(p) for p in items)

    def test_unknowns_route_to_model(self) -> None:
        (item,) = preview("xylotholo root")
        assert needs_llm(item)

    def test_state_words_route_even_when_lexicon_matched(self) -> None:
        for text in ("opened salsa", "cut melon", "cured chorizo",
                     "UHT milk", "cooked rice", "fresh pasta"):
            (item,) = preview(text)
            assert needs_llm(item), text

    def test_no_targets_means_no_request(self) -> None:
        client = FakeClient("[]")
        items = preview("milk, rice")
        assert refine(items, client) is items
        assert client.requests == []

    def test_one_batched_request_for_many_items(self) -> None:
        client = FakeClient("[]")
        items = preview("opened salsa, xylotholo root, cut melon")
        refine(items, client)
        assert len(client.requests) == 1
        content = client.requests[0].messages[0].content
        assert "opened salsa" in content and "cut melon" in content


class TestRefinement:
    def test_model_answer_applied(self) -> None:
        items = preview("opened salsa")
        client = FakeClient(_answer([
            {"name": "opened salsa", "location": "fridge", "shelf_days": 10},
        ]))
        (got,) = refine(items, client)
        assert got.location == "fridge"
        assert got.shelf_days == 10
        assert got.perishable
        assert got.recognized

    def test_long_keeper_not_marked_perishable(self) -> None:
        items = preview("cured chorizo")
        client = FakeClient(_answer([
            {"name": "cured chorizo", "location": "pantry", "shelf_days": 180},
        ]))
        (got,) = refine(items, client)
        assert got.location == "pantry"
        assert not got.perishable  # 180d > ask threshold

    def test_null_shelf_days_means_shelf_stable(self) -> None:
        items = preview("UHT milk")
        client = FakeClient(_answer([
            {"name": "UHT milk", "location": "pantry", "shelf_days": None},
        ]))
        (got,) = refine(items, client)
        assert got.location == "pantry" and got.shelf_days is None

    def test_untargeted_items_untouched(self) -> None:
        items = preview("milk, xylotholo root")
        client = FakeClient(_answer([
            {"name": "xylotholo root", "location": "fridge", "shelf_days": 5},
        ]))
        got = refine(items, client)
        milk = next(p for p in got if p.name == "milk")
        assert milk.location == "fridge" and milk.shelf_days == 7  # lexicon


class TestFailSafe:
    def test_model_crash_returns_lexicon_answers(self) -> None:
        items = preview("opened salsa")
        got = refine(items, ExplodingClient())
        assert got == items

    def test_garbage_reply_returns_lexicon_answers(self) -> None:
        items = preview("opened salsa")
        got = refine(items, FakeClient("I think salsa goes in the fridge!"))
        assert got == items

    def test_invalid_location_rejected(self) -> None:
        items = preview("xylotholo root")
        client = FakeClient(_answer([
            {"name": "xylotholo root", "location": "basement", "shelf_days": 5},
        ]))
        (got,) = refine(items, client)
        assert got.location == "pantry"  # lexicon default stands
        assert not got.recognized

    def test_absurd_shelf_days_clamped(self) -> None:
        items = preview("xylotholo root")
        client = FakeClient(_answer([
            {"name": "xylotholo root", "location": "pantry", "shelf_days": 99999},
        ]))
        (got,) = refine(items, client)
        assert got.shelf_days == 730

    def test_negative_shelf_days_clamped_to_zero(self) -> None:
        items = preview("xylotholo root")
        client = FakeClient(_answer([
            {"name": "xylotholo root", "location": "fridge", "shelf_days": -3},
        ]))
        (got,) = refine(items, client)
        assert got.shelf_days == 0

    def test_hallucinated_item_names_ignored(self) -> None:
        items = preview("xylotholo root")
        client = FakeClient(_answer([
            {"name": "plutonium", "location": "freezer", "shelf_days": 1},
        ]))
        (got,) = refine(items, client)
        assert got.location == "pantry" and not got.recognized

    def test_no_client_is_a_noop(self) -> None:
        items = preview("opened salsa")
        assert refine(items, None) is items


class TestRawProteinGuard:
    """#56: raw animal protein never leaves the LLM tier undated or
    beyond the FDA raw-protein ceiling."""

    def test_null_shelf_days_on_thawed_chicken_rejected(self) -> None:
        items = preview("thawed chicken")
        client = FakeClient(_answer([
            {"name": "thawed chicken", "location": "fridge", "shelf_days": None},
        ]))
        (got,) = refine(items, client)
        # Falls back to the lexicon's chicken answer, never undated.
        assert got.shelf_days == 2
        assert got.perishable

    def test_long_shelf_days_on_raw_fish_clamped(self) -> None:
        items = preview("fresh salmon")
        client = FakeClient(_answer([
            {"name": "fresh salmon", "location": "fridge", "shelf_days": 30},
        ]))
        (got,) = refine(items, client)
        assert got.shelf_days == 5  # FDA raw-protein ceiling

    def test_pantry_answer_for_raw_meat_forced_to_fridge(self) -> None:
        items = preview("fresh turkey")
        client = FakeClient(_answer([
            {"name": "fresh turkey", "location": "pantry",
             "shelf_days": 60},
        ]))
        (got,) = refine(items, client)
        assert got.location == "fridge" and got.shelf_days == 5

    def test_cured_meat_exempt_from_guard(self) -> None:
        items = preview("smoked sausage")
        client = FakeClient(_answer([
            {"name": "smoked sausage", "location": "pantry",
             "shelf_days": 180},
        ]))
        (got,) = refine(items, client)
        assert got.location == "pantry" and got.shelf_days == 180

    def test_frozen_answer_exempt_from_guard(self) -> None:
        items = preview("thawed chicken")  # state word routes to LLM
        client = FakeClient(_answer([
            {"name": "thawed chicken", "location": "freezer",
             "shelf_days": None},
        ]))
        (got,) = refine(items, client)
        assert got.location == "freezer" and got.shelf_days is None


class TestParse:
    def test_json_extracted_from_prose_wrapper(self) -> None:
        got = _parse('Sure! [{"name": "a", "location": "fridge"}] hope that helps')
        assert got == [{"name": "a", "location": "fridge"}]

    def test_non_dict_entries_dropped(self) -> None:
        got = _parse('[{"name": "a"}, "junk", 3]')
        assert got == [{"name": "a"}]
