"""Bind every EB-F0-X result to the frozen EB-F0 contract.

A machine-check receipt that does not name the contract sha it was checked
against is not evidence. This module recomputes the frozen digests from the
files on disk and refuses to proceed on drift.
"""
from __future__ import annotations

import hashlib
import json
import os

# Frozen EB-F0 formal contract (issue #296 sec.15), landed on branch
# biosphere/eb-f0-formal.
CONTRACT_DIR_NAME = "ocm-digital-biosphere-formal-v1"
CONTRACT_COMMIT = "af4fa91e8f1dc74366857b25eb693809d1faf0eb"
CONTRACT_FREEZE_FILE = "FREEZE_V1.json"

DRIFT = "CANNOT_CHECK_CONTRACT_DRIFT"
ABSENT = "CANNOT_CHECK_CONTRACT_ABSENT"


def contract_dir(here: str | None = None) -> str:
    here = here or os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, os.pardir, CONTRACT_DIR_NAME))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_freeze(cdir: str | None = None) -> dict:
    cdir = cdir or contract_dir()
    path = os.path.join(cdir, CONTRACT_FREEZE_FILE)
    if not os.path.exists(path):
        return {"status": ABSENT, "path": path}
    with open(path, "r", encoding="utf-8") as fh:
        return {"status": "OK", "path": path, "freeze": json.load(fh)}


def verify_contract(cdir: str | None = None) -> dict:
    """Recompute every frozen file digest. Distinct exit status on drift.

    Returns status OK / CANNOT_CHECK_CONTRACT_ABSENT / CANNOT_CHECK_CONTRACT_DRIFT.
    "Could not check" is never reported as "checked and fine".
    """
    cdir = cdir or contract_dir()
    got = load_freeze(cdir)
    if got["status"] != "OK":
        return {"status": ABSENT, "detail": got}
    freeze = got["freeze"]
    declared = freeze.get("code_files_sha256") or {}
    if not declared:
        return {"status": DRIFT, "reason": "freeze declares no code_files_sha256"}
    mismatch, missing = [], []
    for name, want in sorted(declared.items()):
        p = os.path.join(cdir, name)
        if not os.path.exists(p):
            missing.append(name)
            continue
        have = sha256_file(p)
        if have != want:
            mismatch.append({"file": name, "declared": want, "recomputed": have})
    status = "OK" if not (mismatch or missing) else DRIFT
    return {
        "status": status,
        "contract_commit": CONTRACT_COMMIT,
        "code_digest": freeze.get("code_digest"),
        "frozen_utc": freeze.get("frozen_utc"),
        "n_files_verified": len(declared) - len(missing),
        "mismatch": mismatch,
        "missing": missing,
    }


def protocol_sha(here: str | None = None) -> str:
    here = here or os.path.dirname(os.path.abspath(__file__))
    return sha256_file(os.path.join(here, "PROTOCOL_V1.json"))


def code_digest(here: str | None = None) -> str:
    """sha256 over every .py in this lane, sorted -- binds results to code."""
    here = here or os.path.dirname(os.path.abspath(__file__))
    names = []
    for root, _dirs, files in os.walk(here):
        if "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                names.append(os.path.join(root, f))
    h = hashlib.sha256()
    for p in sorted(names):
        h.update(os.path.relpath(p, here).encode())
        h.update(b"\0")
        h.update(sha256_file(p).encode())
        h.update(b"\n")
    return h.hexdigest()
