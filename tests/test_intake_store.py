import json
import sqlite3
from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.intake.instruments import GAD2, HUNGER_VITAL_SIGN, PHQ2
from nutrime.intake.store import (
    IntakeProfile,
    save_profile,
    save_screener_responses,
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


def test_profile_dataclass_rejects_invalid_year() -> None:
    with pytest.raises(ValueError, match="year_of_birth"):
        IntakeProfile(
            year_of_birth=1800,
            sex_assigned_at_birth="female",
            life_stage="adult",
        )


def test_profile_dataclass_rejects_invalid_life_stage() -> None:
    with pytest.raises(ValueError, match="life_stage"):
        IntakeProfile(
            year_of_birth=1990,
            sex_assigned_at_birth="female",
            life_stage="bogus",
        )


def test_profile_dataclass_rejects_invalid_sex() -> None:
    with pytest.raises(ValueError, match="sex_assigned_at_birth"):
        IntakeProfile(
            year_of_birth=1990,
            sex_assigned_at_birth="bogus",
            life_stage="adult",
        )


def test_save_profile_writes_row(initialized_app) -> None:
    profile = IntakeProfile(
        year_of_birth=1985,
        sex_assigned_at_birth="female",
        life_stage="adult",
        height_cm=170,
        weight_kg=68.5,
        dietary_preferences=("vegetarian",),
        allergens=("peanut", "shellfish"),
    )
    save_profile(initialized_app.substrate, initialized_app.tenant_id, profile)

    row = initialized_app.substrate.execute(
        "SELECT year_of_birth, life_stage, height_cm, weight_kg,"
        " dietary_preferences, allergens FROM intake_profile_v2"
        " WHERE tenant_id = ?",
        (initialized_app.tenant_id,),
    ).fetchone()
    assert row is not None
    assert row[0] == 1985
    assert row[1] == "adult"
    assert row[2] == 170
    assert row[3] == pytest.approx(68.5)
    assert json.loads(row[4]) == ["vegetarian"]
    assert json.loads(row[5]) == ["peanut", "shellfish"]


def test_save_profile_upserts(initialized_app) -> None:
    """Re-running baseline intake overwrites the tenant's existing profile."""
    first = IntakeProfile(
        year_of_birth=1985,
        sex_assigned_at_birth="female",
        life_stage="adult",
    )
    save_profile(initialized_app.substrate, initialized_app.tenant_id, first)

    second = IntakeProfile(
        year_of_birth=1985,
        sex_assigned_at_birth="female",
        life_stage="pregnant",
        allergens=("egg",),
    )
    save_profile(initialized_app.substrate, initialized_app.tenant_id, second)

    (count,) = initialized_app.substrate.execute(
        "SELECT COUNT(*) FROM intake_profile_v2"
    ).fetchone()
    assert count == 1

    row = initialized_app.substrate.execute(
        "SELECT life_stage, allergens FROM intake_profile_v2"
    ).fetchone()
    assert row[0] == "pregnant"
    assert json.loads(row[1]) == ["egg"]


def test_save_screener_responses_writes_one_row_per_item(initialized_app) -> None:
    save_screener_responses(
        initialized_app.substrate,
        initialized_app.tenant_id,
        PHQ2,
        {"anhedonia": 2, "depressed_mood": 1},
    )
    rows = initialized_app.substrate.execute(
        "SELECT item_id, response_value FROM intake_screener_response"
        " WHERE instrument_id = 'phq2'"
        " ORDER BY item_id"
    ).fetchall()
    assert rows == [("anhedonia", 2), ("depressed_mood", 1)]


def test_save_screener_missing_item_raises(initialized_app) -> None:
    with pytest.raises(ValueError, match="missing response"):
        save_screener_responses(
            initialized_app.substrate,
            initialized_app.tenant_id,
            PHQ2,
            {"anhedonia": 2},
        )


def test_all_three_instruments_persist(initialized_app) -> None:
    for instrument, responses in [
        (PHQ2, {"anhedonia": 0, "depressed_mood": 0}),
        (GAD2, {"nervousness": 0, "uncontrollable_worry": 0}),
        (
            HUNGER_VITAL_SIGN,
            {"worry_food_would_run_out": 0, "food_did_not_last": 0},
        ),
    ]:
        save_screener_responses(
            initialized_app.substrate,
            initialized_app.tenant_id,
            instrument,
            responses,
        )
    (count,) = initialized_app.substrate.execute(
        "SELECT COUNT(*) FROM intake_screener_response"
    ).fetchone()
    assert count == 6


def test_migration_enforces_life_stage_check(initialized_app) -> None:
    """Direct SQL bypassing the dataclass still gets caught by the schema check."""
    with pytest.raises(sqlite3.IntegrityError):
        initialized_app.substrate.execute(
            "INSERT INTO intake_profile ("
            " tenant_id, year_of_birth, sex_assigned_at_birth, life_stage,"
            " created_at, updated_at) VALUES (?, 1990, 'female', 'bogus',"
            " '2026-06-30T00:00:00Z', '2026-06-30T00:00:00Z')",
            (initialized_app.tenant_id,),
        )


def test_foreign_key_prevents_orphan_response(initialized_app) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        initialized_app.substrate.execute(
            "INSERT INTO intake_screener_response ("
            " tenant_id, instrument_id, instrument_version, item_id,"
            " response_value, administered_at)"
            " VALUES ('not-a-tenant', 'phq2', 'kroenke_2003',"
            " 'anhedonia', 0, '2026-06-30T00:00:00Z')"
        )
