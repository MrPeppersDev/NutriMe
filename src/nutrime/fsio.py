"""Atomic file writes for the markdown vaults.

A plain ``write_text`` truncates in place, so a crash mid-write leaves a
half-file — and one truncated ``.md`` made every corpus iteration raise
(search, planner, doctor all down; 2026-10-06 audit, reproduced). Write
to a temp file in the same directory, then ``os.replace`` — atomic on
POSIX and Windows.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def atomic_write_text(path: Path, text: str, *, encoding: str = "utf-8") -> None:
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
