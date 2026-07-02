"""Filesystem paths for the deployment shell.

Defaults assume source-tree execution (the MVP runtime — user runs nutrime
from the cloned repo). Packaging-time path resolution (importlib.resources
for migrations bundled in the wheel) is deferred until we actually ship a
distributable wheel.
"""

from __future__ import annotations

import os
from pathlib import Path

NUTRIME_DATA_DIR_ENV = "NUTRIME_DATA_DIR"


def default_data_dir() -> Path:
    env = os.environ.get(NUTRIME_DATA_DIR_ENV)
    if env:
        return Path(env).expanduser()
    return Path.home() / ".nutrime"


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def default_substrate_migrations_dir() -> Path:
    return _project_root() / "migrations" / "substrate"


def default_operational_migrations_dir() -> Path:
    return _project_root() / "migrations" / "operational"


def default_corpus_dir(data_dir: Path) -> Path:
    """Corpus vault root — markdown source-of-truth per S9 Q9.1."""
    return data_dir / "corpus"
