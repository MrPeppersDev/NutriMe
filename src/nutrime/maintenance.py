"""Self-host maintenance (issue #34): backup, restore, doctor.

Everyone self-hosts, so the person running NutriMe is usually not an
operator. These three commands are the "no reading logs" story:

- :func:`create_backup` — one zip with consistent copies of both SQLite
  databases (SQLite's online backup API, safe while the server runs),
  the recipe/plan vault and the crawl config + state, plus a manifest.
  Credentials are not included; they live in the OS credential store.
- :func:`restore_backup` — validates the archive (manifest, no path
  escapes), refuses to overwrite live data unless forced, takes a safety
  backup of what it replaces, then runs the normal startup so any newer
  migrations apply to the restored data.
- :func:`run_doctor` — plain-language checks, each with the fix.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

BACKUP_FORMAT = 1
DB_FILES = ("substrate.db", "operational.db")
EXTRA_FILES = ("crawl_sources.toml", "crawl_state.json")
BACKUP_DIR = "backups"


class RestoreError(Exception):
    """The archive can't be restored as asked; the message says why."""


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _migration_numbers(db: Path) -> list[int]:
    if not db.exists():
        return []
    conn = sqlite3.connect(db)
    try:
        return sorted(r[0] for r in conn.execute("SELECT number FROM schema_migrations"))
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def _sqlite_copy(src: Path, dest: Path) -> None:
    source = sqlite3.connect(src)
    target = sqlite3.connect(dest)
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def create_backup(data_dir: Path, out_dir: Path | None = None) -> Path:
    """Write ``nutrime-backup-<UTC stamp>.zip`` and return its path."""
    data_dir = Path(data_dir)
    if not (data_dir / "substrate.db").exists():
        raise FileNotFoundError(
            f"no NutriMe data in {data_dir} — nothing to back up"
        )
    out_dir = Path(out_dir) if out_dir else data_dir / BACKUP_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"nutrime-backup-{_stamp()}.zip"
    n = 1
    while archive.exists():  # two backups in the same second
        archive = out_dir / f"nutrime-backup-{_stamp()}-{n}.zip"
        n += 1

    corpus = data_dir / "corpus"
    counts = {
        "recipes": len(list((corpus / "recipes").glob("*.md"))) if corpus.exists() else 0,
        "plans": len(list((corpus / "plans").glob("*.md"))) if corpus.exists() else 0,
    }
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for name in DB_FILES:
            if (data_dir / name).exists():
                _sqlite_copy(data_dir / name, tmp_path / name)
        manifest = {
            "format": BACKUP_FORMAT,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "migrations": {
                name: _migration_numbers(tmp_path / name) for name in DB_FILES
            },
            "counts": counts,
            "note": "Credentials are not included (OS credential store).",
        }
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, indent=1))
            for name in DB_FILES:
                if (tmp_path / name).exists():
                    zf.write(tmp_path / name, name)
            for name in EXTRA_FILES:
                if (data_dir / name).exists():
                    zf.write(data_dir / name, name)
            if corpus.exists():
                for path in sorted(corpus.rglob("*")):
                    if path.is_file() and BACKUP_DIR not in path.parts:
                        zf.write(path, path.relative_to(data_dir).as_posix())
    return archive


def read_manifest(archive: Path) -> dict:
    try:
        with zipfile.ZipFile(archive) as zf:
            return json.loads(zf.read("manifest.json"))
    except (zipfile.BadZipFile, KeyError, json.JSONDecodeError) as exc:
        raise RestoreError(f"{archive} is not a NutriMe backup ({exc})") from exc


def _safe_members(zf: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    allowed_roots = {*DB_FILES, *EXTRA_FILES, "manifest.json", "corpus"}
    members = []
    for info in zf.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
            raise RestoreError(f"refusing unsafe path in archive: {info.filename!r}")
        if path.parts and path.parts[0] not in allowed_roots:
            raise RestoreError(f"unexpected file in archive: {info.filename!r}")
        members.append(info)
    return members


@dataclass(frozen=True)
class RestoreOutcome:
    restored_from: Path
    safety_backup: Path | None
    counts: dict


def restore_backup(
    archive: Path, data_dir: Path, *, force: bool = False
) -> RestoreOutcome:
    """Replace ``data_dir``'s NutriMe data with the archive's contents."""
    archive = Path(archive)
    data_dir = Path(data_dir)
    manifest = read_manifest(archive)
    if manifest.get("format") != BACKUP_FORMAT:
        raise RestoreError(
            f"backup format {manifest.get('format')!r} is not supported by this version"
        )
    has_live = (data_dir / "substrate.db").exists()
    if has_live and not force:
        raise RestoreError(
            f"{data_dir} already holds NutriMe data. Restoring replaces it;"
            " run again with --force (a safety backup is taken first)."
        )
    with zipfile.ZipFile(archive) as zf:
        members = _safe_members(zf)
        if "substrate.db" not in {m.filename for m in members}:
            raise RestoreError("archive has no substrate.db — not a usable backup")
        safety = create_backup(data_dir) if has_live else None
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "restore"
            for info in members:
                zf.extract(info, staging)
            data_dir.mkdir(parents=True, exist_ok=True)
            for name in (*DB_FILES, *EXTRA_FILES):
                target = data_dir / name
                if target.exists():
                    target.unlink()
                for suffix in ("-wal", "-shm", "-journal"):
                    side = data_dir / f"{name}{suffix}"
                    if side.exists():
                        side.unlink()
                if (staging / name).exists():
                    shutil.move(str(staging / name), target)
            if (data_dir / "corpus").exists():
                shutil.rmtree(data_dir / "corpus")
            if (staging / "corpus").exists():
                shutil.move(str(staging / "corpus"), data_dir / "corpus")

    # Normal startup: applies any migrations newer than the backup.
    from nutrime.app import initialize

    app = initialize(data_dir=data_dir)
    app.substrate.close()
    app.operational.close()
    return RestoreOutcome(archive, safety, manifest.get("counts", {}))


# -- doctor ---------------------------------------------------------------------


@dataclass(frozen=True)
class Check:
    name: str
    status: str  # "ok" | "warn" | "fail"
    detail: str
    fix: str = ""


def _check_local_model() -> Check:
    import os
    import urllib.request

    from nutrime.llm.ollama import DEFAULT_MODEL, DEFAULT_URL, MODEL_ENV, URL_ENV

    url = (os.environ.get(URL_ENV) or DEFAULT_URL).rstrip("/")
    model = os.environ.get(MODEL_ENV) or DEFAULT_MODEL
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=2) as resp:
            tags = json.loads(resp.read())
    except Exception:  # noqa: BLE001
        return Check(
            "Local model", "warn",
            "Ollama isn't answering, so plan-making is off. Search, Tonight and"
            " grocery still work.",
            "Install Ollama from https://ollama.com, then run"
            f" `ollama pull {model}`.",
        )
    names = {m.get("name", "") for m in tags.get("models", [])}
    if model not in names and f"{model}:latest" not in names:
        return Check(
            "Local model", "warn",
            f"Ollama is running but the model {model} isn't downloaded.",
            f"Run `ollama pull {model}`.",
        )
    return Check("Local model", "ok", f"Ollama is running with {model}.")


def run_doctor(data_dir: Path, *, check_model: bool = True) -> list[Check]:
    import sys

    from nutrime.db import discover_migrations
    from nutrime.paths import (
        default_operational_migrations_dir,
        default_substrate_migrations_dir,
    )

    data_dir = Path(data_dir)
    checks: list[Check] = []

    if sys.version_info >= (3, 13):
        checks.append(Check("Python", "ok", f"Python {sys.version.split()[0]}."))
    else:
        checks.append(Check(
            "Python", "fail", f"Python {sys.version.split()[0]} is too old.",
            "Install Python 3.13 or newer (the installer does this via uv).",
        ))

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".doctor-probe"
        probe.write_text("ok")
        probe.unlink()
        checks.append(Check("Data folder", "ok", f"{data_dir} is writable."))
    except OSError as exc:
        checks.append(Check(
            "Data folder", "fail", f"Can't write to {data_dir}: {exc}",
            "Check the folder's permissions, or set NUTRIME_DATA_DIR to a"
            " folder you own.",
        ))
        return checks

    for name, mig_dir in (
        ("substrate.db", default_substrate_migrations_dir()),
        ("operational.db", default_operational_migrations_dir()),
    ):
        db = data_dir / name
        if not db.exists():
            checks.append(Check(
                f"Database {name}", "fail", "Not created yet.",
                "Run `nutrime init` (or just start NutriMe once).",
            ))
            continue
        try:
            applied = set(_migration_numbers(db))
            known = {m.number for m in discover_migrations(mig_dir)}
            conn = sqlite3.connect(db)
            (ok,) = conn.execute("PRAGMA quick_check").fetchone()
            conn.close()
        except sqlite3.Error as exc:
            checks.append(Check(
                f"Database {name}", "fail", f"Can't read it: {exc}",
                "Restore your latest backup with `nutrime restore <file> --force`.",
            ))
            continue
        if ok != "ok":
            checks.append(Check(
                f"Database {name}", "fail", f"Integrity check failed: {ok}",
                "Restore your latest backup with `nutrime restore <file> --force`.",
            ))
        elif known - applied:
            checks.append(Check(
                f"Database {name}", "warn",
                f"{len(known - applied)} update(s) not applied yet.",
                "Start NutriMe once (or run `nutrime init`); updates apply"
                " automatically.",
            ))
        else:
            checks.append(Check(f"Database {name}", "ok", "Up to date and healthy."))

    recipes_dir = data_dir / "corpus" / "recipes"
    recipe_files = list(recipes_dir.glob("*.md")) if recipes_dir.exists() else []
    if not recipe_files:
        checks.append(Check(
            "Recipes", "warn", "The recipe collection is empty.",
            "Copy the bundled collection: see corpus/README.md in the NutriMe"
            " folder (the installer does this).",
        ))
    else:
        from nutrime.recipes.store import RecipeVault
        from nutrime.recipes.vetting import VETTING_VERSION

        stale = sum(
            1 for r in RecipeVault(data_dir / "corpus").iter_recipes()
            if int(r.frontmatter.get("vetting_version") or 0) < VETTING_VERSION
        )
        if stale:
            checks.append(Check(
                "Recipes", "warn",
                f"{len(recipe_files)} recipes; {stale} not checked by the"
                " current vetting rules.",
                "Run `nutrime recipes vet`.",
            ))
        else:
            checks.append(Check("Recipes", "ok", f"{len(recipe_files)} recipes, all vetted."))

    if (data_dir / "substrate.db").exists():
        conn = sqlite3.connect(data_dir / "substrate.db")
        try:
            members = conn.execute(
                "SELECT COUNT(*) FROM member WHERE status = 'active'"
            ).fetchone()[0]
            profiles = conn.execute(
                "SELECT COUNT(*) FROM intake_profile_v2 p JOIN member m"
                " ON m.id = p.member_id WHERE m.status = 'active'"
            ).fetchone()[0]
        except sqlite3.Error:
            members = profiles = 0
        finally:
            conn.close()
        if members and profiles < members:
            checks.append(Check(
                "Household", "warn",
                f"{members - profiles} of {members} people have no profile yet,"
                " so their allergies aren't on the avoid-list.",
                "Open NutriMe, pick each person, and fill in their answers.",
            ))
        elif members:
            checks.append(Check("Household", "ok", f"{members} people, all with profiles."))

    backups = sorted((data_dir / BACKUP_DIR).glob("nutrime-backup-*.zip"))
    if not backups:
        checks.append(Check(
            "Backups", "warn", "No backup yet.", "Run `nutrime backup`.",
        ))
    else:
        age_days = (
            datetime.now().timestamp() - backups[-1].stat().st_mtime
        ) / 86400
        if age_days > 30:
            checks.append(Check(
                "Backups", "warn", f"Latest backup is {int(age_days)} days old.",
                "Run `nutrime backup`.",
            ))
        else:
            checks.append(Check("Backups", "ok", f"Latest: {backups[-1].name}."))

    if check_model:
        checks.append(_check_local_model())
    return checks
