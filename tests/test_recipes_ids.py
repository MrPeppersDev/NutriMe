"""IDs for recipe canonical rows follow the S9 base contract."""

import uuid

from nutrime.recipes.ids import new_recipe_id


def test_new_recipe_id_has_typed_prefix() -> None:
    assert new_recipe_id().startswith("rcp-")


def test_new_recipe_id_body_is_uuid7() -> None:
    body = new_recipe_id().removeprefix("rcp-")
    parsed = uuid.UUID(body)
    assert parsed.version == 7
    assert (parsed.int >> 62) & 0x3 == 0x2  # RFC 9562 variant 10xx


def test_new_recipe_ids_are_unique() -> None:
    ids = {new_recipe_id() for _ in range(200)}
    assert len(ids) == 200
