"""Installed bounded-world assets and their immutable source identity."""
from __future__ import annotations

import hashlib
from importlib.resources import files
from pathlib import Path


MANIFEST_NAME = "KNOWLEDGE_MANIFEST_V1.json"
MANIFEST_SHA256 = "dea32b88defcd56ef659e27c67ef359dbe5043cdb0dd6bb68a962788b80f85c6"


def default_manifest_path() -> Path:
    """Return the byte-verified installed manifest; missing/tampered data is an error.

    Standard wheel installations extract package data to disk. Zip import of the
    wheel itself is not supported by the path-based knowledge loader.
    """
    resource = files(__package__).joinpath(MANIFEST_NAME)
    raw = resource.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA256:
        raise ValueError("CANNOT_CHECK_PACKAGED_RESOURCE_CUSTODY: manifest hash mismatch")
    return Path(str(resource))
