"""Self-host maintenance (#34): backup, restore, doctor, live upgrades."""

import shutil
import sqlite3
import zipfile
from pathlib import Path

import pytest

from nutrime.app import initialize
from nutrime.db import apply_migrations, connect, discover_migrations
from nutrime.intake.store import IntakeProfile, load_member_profile, save_member_profile
from nutrime.maintenance import (
    RestoreError,
    create_backup,
    read_manifest,
    restore_backup,
    run_doctor,
)
from nutrime.members import add_member, list_members
from nutrime.paths import default_substrate_migrations_dir
from nutrime.recipes.store import RecipeVault
from nutrime.recipes.themealdb import convert_meal
from nutrime.tenancy import bootstrap_tenant


def _seed(data_dir: Path) -> str:
    app = initialize(data_dir=data_dir)
    sam = add_member(app.substrate, app.tenant_id, "Sam")
    save_member_profile(
        app.substrate, app.tenant_id, sam.id,
        IntakeProfile(year_of_birth=2015, sex_assigned_at_birth="female",
                      life_stage="child", allergens=("peanuts",)),
    )
    meal = {"idMeal": "1", "strMeal": "Stew", "strCategory": "Beef", "strArea": "",
            "strTags": "", "strInstructions": "Cook.", "strSource": ""}
    for i in range(1, 21):
        meal[f"strIngredient{i}"] = "beef" if i == 1 else ""
        meal[f"strMeasure{i}"] = "1" if i == 1 else ""
    c = convert_meal(meal, ingested_at="2026-10-06T00:00:00Z")
    RecipeVault(app.corpus_dir).write(c.recipe_id, c.frontmatter, c.cooklang_body)
    (data_dir / "crawl_sources.toml").write_text("# none\n")
    app.substrate.close()
    app.operational.close()
    return sam.id


class TestBackupRestore:
    def test_roundtrip_into_empty_folder(self, tmp_path: Path) -> None:
        src = tmp_path / "src"
        sam = _seed(src)
        archive = create_backup(src)
        assert archive.parent == src / "backups"
        manifest = read_manifest(archive)
        assert manifest["counts"]["recipes"] == 1
        assert 6 in manifest["migrations"]["substrate.db"]

        dest = tmp_path / "dest"
        outcome = restore_backup(archive, dest)
        assert outcome.safety_backup is None
        app = initialize(data_dir=dest)
        try:
            names = [m.display_name for m in list_members(app.substrate, app.tenant_id)]
            assert names == ["Me", "Sam"]
            assert load_member_profile(app.substrate, app.tenant_id, sam).allergens == ("peanuts",)
            assert RecipeVault(app.corpus_dir).count() == 1
            assert (dest / "crawl_sources.toml").exists()
        finally:
            app.substrate.close()
            app.operational.close()

    def test_backup_while_connection_open(self, tmp_path: Path) -> None:
        _seed(tmp_path)
        live = initialize(data_dir=tmp_path)  # server-style open handle
        try:
            archive = create_backup(tmp_path)
        finally:
            live.substrate.close()
            live.operational.close()
        with zipfile.ZipFile(archive) as zf:
            assert {"substrate.db", "operational.db", "manifest.json"} <= set(zf.namelist())

    def test_refuses_to_overwrite_without_force(self, tmp_path: Path) -> None:
        _seed(tmp_path / "a")
        archive = create_backup(tmp_path / "a")
        initialize(data_dir=tmp_path / "b").substrate.close()
        with pytest.raises(RestoreError, match="--force"):
            restore_backup(archive, tmp_path / "b")

    def test_force_takes_safety_backup_first(self, tmp_path: Path) -> None:
        _seed(tmp_path / "a")
        archive = create_backup(tmp_path / "a")
        b = tmp_path / "b"
        app = initialize(data_dir=b)
        add_member(app.substrate, app.tenant_id, "Only In B")
        app.substrate.close(); app.operational.close()
        outcome = restore_backup(archive, b, force=True)
        assert outcome.safety_backup and outcome.safety_backup.exists()
        # the replaced data is recoverable from the safety backup
        restore_backup(outcome.safety_backup, tmp_path / "c")
        app = initialize(data_dir=tmp_path / "c")
        try:
            assert "Only In B" in [m.display_name for m in list_members(app.substrate, app.tenant_id)]
        finally:
            app.substrate.close(); app.operational.close()

    def test_rejects_path_escape(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.zip"
        with zipfile.ZipFile(bad, "w") as zf:
            zf.writestr("manifest.json", '{"format": 1}')
            zf.writestr("substrate.db", "x")
            zf.writestr("../evil.txt", "x")
        with pytest.raises(RestoreError, match="unsafe path"):
            restore_backup(bad, tmp_path / "dest")
        assert not (tmp_path / "evil.txt").exists()

    def test_rejects_non_backup(self, tmp_path: Path) -> None:
        junk = tmp_path / "junk.zip"
        with zipfile.ZipFile(junk, "w") as zf:
            zf.writestr("hello.txt", "x")
        with pytest.raises(RestoreError, match="not a NutriMe backup"):
            restore_backup(junk, tmp_path / "dest")

    def test_nothing_to_back_up(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            create_backup(tmp_path / "empty")


@pytest.mark.parametrize(
    "level",
    [m.number for m in discover_migrations(default_substrate_migrations_dir())][:-1],
)
def test_live_upgrade_from_every_schema_level(tmp_path: Path, level: int) -> None:
    """A database left at any earlier migration level upgrades cleanly on
    the next start, keeping its tenant."""
    partial = tmp_path / "migrations"
    partial.mkdir()
    for sql in default_substrate_migrations_dir().glob("*.sql"):
        if int(sql.name.split("_")[0]) <= level:
            shutil.copy(sql, partial / sql.name)
    data = tmp_path / "data"
    data.mkdir()
    conn = connect(data / "substrate.db")
    apply_migrations(conn, partial)
    tenant = bootstrap_tenant(conn)
    conn.close()

    app = initialize(data_dir=data)
    try:
        assert app.tenant_id == tenant
        applied = {r[0] for r in app.substrate.execute("SELECT number FROM schema_migrations")}
        expected = {m.number for m in discover_migrations(default_substrate_migrations_dir())}
        assert applied == expected
        assert list_members(app.substrate, app.tenant_id)
    finally:
        app.substrate.close()
        app.operational.close()


class TestDoctor:
    def _by_name(self, checks):
        return {c.name: c for c in checks}

    def test_fresh_install(self, tmp_path: Path) -> None:
        initialize(data_dir=tmp_path).substrate.close()
        checks = self._by_name(run_doctor(tmp_path, check_model=False))
        assert checks["Database substrate.db"].status == "ok"
        assert checks["Recipes"].status == "warn"
        assert "corpus/README.md" in checks["Recipes"].fix
        assert checks["Household"].status == "warn"
        assert checks["Backups"].status == "warn"
        assert "Local model" not in checks

    def test_healthy_after_setup(self, tmp_path: Path) -> None:
        from nutrime.recipes.vetting import vet_vault

        _seed(tmp_path)
        app = initialize(data_dir=tmp_path)
        save_member_profile(
            app.substrate, app.tenant_id, None,
            IntakeProfile(year_of_birth=1990, sex_assigned_at_birth="male", life_stage="adult"),
        )
        app.substrate.close(); app.operational.close()
        vet_vault(RecipeVault(tmp_path / "corpus"))
        create_backup(tmp_path)
        checks = run_doctor(tmp_path, check_model=False)
        assert [c.name for c in checks if c.status != "ok"] == []

    def test_missing_database_is_a_failure_with_fix(self, tmp_path: Path) -> None:
        checks = self._by_name(run_doctor(tmp_path, check_model=False))
        assert checks["Database substrate.db"].status == "fail"
        assert "nutrime init" in checks["Database substrate.db"].fix

    def test_pending_migration_warns(self, tmp_path: Path) -> None:
        initialize(data_dir=tmp_path).substrate.close()
        conn = sqlite3.connect(tmp_path / "substrate.db")
        conn.execute("DELETE FROM schema_migrations WHERE number = 6")
        conn.commit(); conn.close()
        checks = self._by_name(run_doctor(tmp_path, check_model=False))
        assert checks["Database substrate.db"].status == "warn"


def test_cli_backup_restore_doctor(tmp_path: Path, capsys) -> None:
    from nutrime.cli import main

    _seed(tmp_path / "a")
    assert main(["backup", "--data-dir", str(tmp_path / "a")]) == 0
    out = capsys.readouterr().out
    archive = out.split("backup written: ")[1].split(" (")[0]
    assert main(["restore", archive, "--data-dir", str(tmp_path / "b")]) == 0
    assert "restored" in capsys.readouterr().out
    rc = main(["doctor", "--skip-model", "--data-dir", str(tmp_path / "b")])
    out = capsys.readouterr().out
    assert rc == 0 and "Database substrate.db: Up to date" in out
