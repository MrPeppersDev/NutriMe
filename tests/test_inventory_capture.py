from pathlib import Path
from typing import Callable

import pytest

from nutrime.app import initialize
from nutrime.inventory.capture import capture_items
from nutrime.inventory.store import list_items

SUBSTRATE_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "substrate"
OPERATIONAL_MIGRATIONS = Path(__file__).parent.parent / "migrations" / "operational"


@pytest.fixture
def initialized_app(tmp_path: Path):
    data_dir = tmp_path / "nutrime-data"
    return initialize(
        data_dir=data_dir,
        substrate_migrations=SUBSTRATE_MIGRATIONS,
        operational_migrations=OPERATIONAL_MIGRATIONS,
    )


def make_prompter(script: list[str]) -> Callable[[str], str]:
    it = iter(script)

    def prompter(_prompt: str) -> str:
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(
                "prompter script exhausted — capture flow asked for more input"
            )

    return prompter


def test_capture_single_loose_item(initialized_app) -> None:
    script = [
        "rice",     # name
        "pantry",   # location
        "",         # quantity (loose)
        "",         # best-by (skip)
        "",         # notes (skip)
        "n",        # add another? no
    ]
    emitted: list[str] = []
    added = capture_items(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=emitted.append,
    )
    assert len(added) == 1
    assert added[0].name == "rice"
    assert added[0].quantity is None
    assert added[0].id is not None

    items = list_items(
        initialized_app.substrate, initialized_app.tenant_id
    )
    assert len(items) == 1
    assert items[0].name == "rice"


def test_capture_full_item_with_quantity(initialized_app) -> None:
    script = [
        "milk",
        "fridge",
        "946",         # quantity
        "ml",          # unit
        "2026-07-15",  # best-by
        "skim",        # notes
        "n",
    ]
    added = capture_items(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=lambda _: None,
    )
    assert added[0].quantity == 946.0
    assert added[0].unit == "ml"
    assert added[0].best_by_date == "2026-07-15"
    assert added[0].notes == "skim"


def test_capture_add_many(initialized_app) -> None:
    script = [
        "rice", "pantry", "", "", "",
        "y",
        "milk", "fridge", "946", "ml", "", "",
        "y",
        "peas", "freezer", "", "", "",
        "n",
    ]
    added = capture_items(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=lambda _: None,
    )
    assert len(added) == 3
    items = list_items(
        initialized_app.substrate, initialized_app.tenant_id
    )
    assert {i.name for i in items} == {"rice", "milk", "peas"}


def test_capture_reprompts_on_blank_name(initialized_app) -> None:
    script = [
        "",         # blank name → reprompt
        "rice",
        "pantry",
        "", "", "",
        "n",
    ]
    emitted: list[str] = []
    capture_items(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=emitted.append,
    )
    assert any("cannot be blank" in line for line in emitted)


def test_capture_reprompts_on_invalid_date(initialized_app) -> None:
    script = [
        "milk",
        "fridge",
        "946",
        "ml",
        "tomorrow",     # invalid → reprompt
        "2026-07-15",
        "",
        "n",
    ]
    emitted: list[str] = []
    added = capture_items(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=emitted.append,
    )
    assert added[0].best_by_date == "2026-07-15"
    assert any("YYYY-MM-DD" in line for line in emitted)


def test_capture_numeric_choice_for_location(initialized_app) -> None:
    script = [
        "rice",
        "1",     # pantry (choice 1)
        "", "", "",
        "n",
    ]
    added = capture_items(
        initialized_app.substrate,
        initialized_app.tenant_id,
        prompter=make_prompter(script),
        emitter=lambda _: None,
    )
    assert added[0].location == "pantry"
