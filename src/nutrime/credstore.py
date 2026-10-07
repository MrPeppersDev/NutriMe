"""OS credential store — the no-plaintext-on-disk path for API secrets.

One seam for every stored secret (Anthropic key, Pinterest tokens + app
credentials), keyed by a *service* name with one ``(account, secret)`` entry
per service:

- **macOS** — login Keychain via ``security(1)``, unchanged from the 5.2 /
  #24 adapters, so entries stored before this module existed still resolve.
- **Windows** — Credential Manager generic credentials (``TargetName`` =
  service) via ``advapi32`` through ctypes. Stdlib only, per the
  no-SDK-dependency convention. Inspect with ``cmdkey /list:nutrime-*``.

Elsewhere reads return None and writes raise ``OSError`` — env vars remain
the fallback on every platform.
"""

from __future__ import annotations

import subprocess
import sys

_BACKEND_NAMES = {"darwin": "macOS Keychain", "win32": "Windows Credential Manager"}


def backend_name() -> str:
    """Human label for messages ("stored in the …")."""
    return _BACKEND_NAMES.get(sys.platform, "OS credential store")


def store_hint(service: str) -> str:
    """Platform-appropriate one-liner for storing a secret by hand."""
    if sys.platform == "win32":
        return (
            f"cmdkey /generic:{service} /user:%USERNAME% /pass"
            " (prompts for the secret)"
        )
    return f'security add-generic-password -U -s {service} -a "$USER" -w'


def read(service: str) -> tuple[str, str] | None:
    """Return ``(account, secret)`` for a service, or None. Never raises."""
    if sys.platform == "darwin":
        return _mac_read(service)
    if sys.platform == "win32":
        try:
            return _win_read(service)
        except OSError:
            return None
    return None


def read_secret(service: str) -> str | None:
    entry = read(service)
    if entry is None:
        return None
    return entry[1] or None


def write(service: str, account: str, secret: str) -> None:
    """Create or replace the service's entry. Raises OSError on failure."""
    if sys.platform == "darwin":
        _mac_write(service, account, secret)
    elif sys.platform == "win32":
        _win_write(service, account, secret)
    else:
        raise OSError(f"no OS credential store on {sys.platform}")


# -- macOS: security(1) --------------------------------------------------------


def _mac_read(service: str) -> tuple[str, str] | None:
    try:
        shown = subprocess.run(
            ["security", "find-generic-password", "-s", service],
            capture_output=True,
            text=True,
            timeout=5,
        )
        secret = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if shown.returncode != 0 or secret.returncode != 0:
        return None
    account = ""
    for line in shown.stdout.splitlines():
        line = line.strip()
        if line.startswith('"acct"'):
            account = line.split("=", 1)[1].strip().strip('"')
            # security(1) prints acct as <blob>="value"
            if account.startswith("<blob>="):
                account = account[len("<blob>=") :].strip('"')
    return (account, secret.stdout.strip())


def _mac_write(service: str, account: str, secret: str) -> None:
    # The secret goes through security(1)'s stdin command mode (-i), never
    # argv — argv is world-readable via `ps` (2026-10-07 audit).
    command = "add-generic-password -U -s {} -a {} -w {}\n".format(
        _sec_quote(service), _sec_quote(account), _sec_quote(secret)
    )
    result = subprocess.run(
        ["security", "-i"],
        input=command,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise OSError(f"Keychain write failed: {result.stderr.strip()}")


def _sec_quote(value: str) -> str:
    """Quote one argument for security(1)'s interactive command parser."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


# -- Windows: Credential Manager ----------------------------------------------

_CRED_TYPE_GENERIC = 1
_CRED_PERSIST_LOCAL_MACHINE = 2
_ERROR_NOT_FOUND = 1168


def _win_api():
    import ctypes
    from ctypes import wintypes

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]

    class CREDENTIALW(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    advapi32.CredReadW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.POINTER(ctypes.POINTER(CREDENTIALW)),
    ]
    advapi32.CredReadW.restype = wintypes.BOOL
    advapi32.CredWriteW.argtypes = [ctypes.POINTER(CREDENTIALW), wintypes.DWORD]
    advapi32.CredWriteW.restype = wintypes.BOOL
    advapi32.CredFree.argtypes = [ctypes.c_void_p]
    advapi32.CredFree.restype = None
    return ctypes, CREDENTIALW, advapi32


def _win_read(service: str) -> tuple[str, str] | None:
    ctypes, CREDENTIALW, advapi32 = _win_api()
    pcred = ctypes.POINTER(CREDENTIALW)()
    if not advapi32.CredReadW(service, _CRED_TYPE_GENERIC, 0, ctypes.byref(pcred)):
        if ctypes.get_last_error() == _ERROR_NOT_FOUND:
            return None
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        cred = pcred.contents
        blob = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize)
        return (cred.UserName or "", _decode_blob(blob))
    finally:
        advapi32.CredFree(pcred)


def _decode_blob(blob: bytes) -> str:
    # We write UTF-8; `cmdkey /pass` writes UTF-16-LE. Tell them apart by the
    # NUL high bytes UTF-16 leaves on ASCII secrets (tokens are ASCII).
    if len(blob) >= 2 and len(blob) % 2 == 0 and blob[1::2].count(0) == len(blob) // 2:
        return blob.decode("utf-16-le")
    return blob.decode("utf-8")


def _win_write(service: str, account: str, secret: str) -> None:
    ctypes, CREDENTIALW, advapi32 = _win_api()
    data = secret.encode("utf-8")
    buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    cred = CREDENTIALW()
    cred.Type = _CRED_TYPE_GENERIC
    cred.TargetName = service
    cred.CredentialBlobSize = len(data)
    cred.CredentialBlob = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
    cred.Persist = _CRED_PERSIST_LOCAL_MACHINE
    cred.UserName = account
    if not advapi32.CredWriteW(ctypes.byref(cred), 0):
        raise OSError(
            f"Credential Manager write failed: {ctypes.WinError(ctypes.get_last_error())}"
        )
