import sqlite3
from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.inventory.store import (
    InventoryItem,
    add_item,
    by_location,
    list_items,
    remove_item,
    update_item,
)

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


class TestInventoryItemValidation:
    def test_rejects_blank_name(self) -> None:
        with pytest.raises(ValueError, match="name"):
            InventoryItem(name="   ", location="pantry")

    def test_rejects_unknown_location(self) -> None:
        with pytest.raises(ValueError, match="location"):
            InventoryItem(name="rice", location="garage")

    def test_rejects_unpaired_quantity(self) -> None:
        with pytest.raises(ValueError, match="quantity and unit"):
            InventoryItem(name="rice", location="pantry", quantity=1.0)

    def test_rejects_unpaired_unit(self) -> None:
        with pytest.raises(ValueError, match="quantity and unit"):
            InventoryItem(name="rice", location="pantry", unit="g")

    def test_rejects_negative_quantity(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            InventoryItem(
                name="rice", location="pantry", quantity=-1.0, unit="g"
            )

    def test_rejects_unknown_unit(self) -> None:
        with pytest.raises(ValueError, match="unit"):
            InventoryItem(
                name="rice", location="pantry", quantity=1.0, unit="stone"
            )

    def test_rejects_malformed_date(self) -> None:
        with pytest.raises(ValueError, match="best_by_date"):
            InventoryItem(
                name="milk", location="fridge", best_by_date="tomorrow"
            )

    def test_accepts_loose_item(self) -> None:
        item = InventoryItem(name="rice", location="pantry")
        assert item.quantity is None
        assert item.unit is None

    def test_accepts_full_item(self) -> None:
        item = InventoryItem(
            name="milk",
            location="fridge",
            quantity=946.0,
            unit="ml",
            best_by_date="2026-07-15",
            notes="skim",
        )
        assert item.quantity == 946.0
        assert item.best_by_date == "2026-07-15"


class TestPersistence:
    def test_add_and_list(self, initialized_app) -> None:
        add_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            InventoryItem(name="rice", location="pantry"),
        )
        add_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            InventoryItem(
                name="milk",
                location="fridge",
                quantity=946.0,
                unit="ml",
                best_by_date="2026-07-15",
            ),
        )
        items = list_items(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert [i.name for i in items] == ["milk", "rice"]  # ordered by location, name

    def test_list_filter_by_location(self, initialized_app) -> None:
        for item in [
            InventoryItem(name="rice", location="pantry"),
            InventoryItem(name="lentils", location="pantry"),
            InventoryItem(name="milk", location="fridge"),
        ]:
            add_item(
                initialized_app.substrate, initialized_app.tenant_id, item
            )
        pantry = list_items(
            initialized_app.substrate,
            initialized_app.tenant_id,
            location="pantry",
        )
        assert {i.name for i in pantry} == {"rice", "lentils"}

    def test_by_location_groups(self, initialized_app) -> None:
        for item in [
            InventoryItem(name="rice", location="pantry"),
            InventoryItem(name="milk", location="fridge"),
            InventoryItem(name="peas", location="freezer"),
        ]:
            add_item(
                initialized_app.substrate, initialized_app.tenant_id, item
            )
        items = list_items(
            initialized_app.substrate, initialized_app.tenant_id
        )
        grouped = by_location(items)
        assert set(grouped.keys()) == {"pantry", "fridge", "freezer"}

    def test_remove_item(self, initialized_app) -> None:
        item_id = add_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            InventoryItem(name="rice", location="pantry"),
        )
        assert remove_item(
            initialized_app.substrate, initialized_app.tenant_id, item_id
        )
        assert list_items(
            initialized_app.substrate, initialized_app.tenant_id
        ) == []

    def test_remove_missing_returns_false(self, initialized_app) -> None:
        assert not remove_item(
            initialized_app.substrate, initialized_app.tenant_id, 999
        )

    def test_update_item(self, initialized_app) -> None:
        item_id = add_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            InventoryItem(
                name="rice", location="pantry", quantity=500.0, unit="g"
            ),
        )
        assert update_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            item_id,
            quantity=250.0,
            notes="opened, half used",
        )
        (item,) = list_items(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert item.quantity == 250.0
        assert item.notes == "opened, half used"

    def test_schema_check_rejects_bad_location(self, initialized_app) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            initialized_app.substrate.execute(
                "INSERT INTO inventory_item ("
                "  tenant_id, name, location, added_at, updated_at)"
                " VALUES (?, 'rice', 'garage', ?, ?)",
                (
                    initialized_app.tenant_id,
                    "2026-06-30T00:00:00Z",
                    "2026-06-30T00:00:00Z",
                ),
            )

    def test_schema_check_pairs_quantity_and_unit(self, initialized_app) -> None:
        with pytest.raises(sqlite3.IntegrityError):
            initialized_app.substrate.execute(
                "INSERT INTO inventory_item ("
                "  tenant_id, name, location, quantity, unit,"
                "  added_at, updated_at)"
                " VALUES (?, 'rice', 'pantry', 100, NULL, ?, ?)",
                (
                    initialized_app.tenant_id,
                    "2026-06-30T00:00:00Z",
                    "2026-06-30T00:00:00Z",
                ),
            )

    def test_unknown_tenant_cannot_add(self, initialized_app) -> None:
        # The consent gate fails closed before the FK constraint can:
        # an unknown tenant has no consent rows at all.
        from nutrime.consent import ConsentError

        with pytest.raises(ConsentError):
            add_item(
                initialized_app.substrate,
                "not-a-tenant",
                InventoryItem(name="rice", location="pantry"),
            )

    def test_foreign_key_prevents_orphan(self, initialized_app) -> None:
        # The FK constraint itself, probed below the consent seam.
        with pytest.raises(sqlite3.IntegrityError):
            initialized_app.substrate.execute(
                "INSERT INTO inventory_item"
                " (tenant_id, name, location, added_at, updated_at)"
                " VALUES ('not-a-tenant', 'rice', 'pantry', '', '')"
            )


class TestMatchName:
    def test_round_trip(self, initialized_app) -> None:
        add_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            InventoryItem(
                name="chives with chive flowers",
                location="fridge",
                match_name="chives",
            ),
        )
        (item,) = list_items(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert item.match_name == "chives"
        assert item.matching_name == "chives"

    def test_matching_name_defaults_to_name(self, initialized_app) -> None:
        add_item(
            initialized_app.substrate,
            initialized_app.tenant_id,
            InventoryItem(name="milk", location="fridge"),
        )
        (item,) = list_items(
            initialized_app.substrate, initialized_app.tenant_id
        )
        assert item.match_name is None
        assert item.matching_name == "milk"
