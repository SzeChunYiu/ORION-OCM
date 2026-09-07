"""Registered, bounded JSON data snapshots for cold rollback.

This format contains no Python object tags, import names, pickle payloads or
executable loader. Unsupported host artifacts retain their in-process path.
The adoption event, not a caller-provided filename, binds the SHA-256 digest.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

SCHEMA = "ocm.rollback.data.v1"
MAX_BYTES = 8 * 1024 * 1024
MAX_NODES = 100_000
MAX_DEPTH = 64
FIELDS = {"schema", "proposal_fingerprint", "target", "incumbent",
          "previous_artifact", "previous_state_hash", "previous_components", "cache_snapshot"}


def plain_data(value: Any) -> bool:
    """Only exact built-in JSON tree types, with finite floats and bounded size."""
    remaining = MAX_NODES

    def visit(node: Any, depth: int) -> bool:
        nonlocal remaining
        remaining -= 1
        if remaining < 0 or depth > MAX_DEPTH:
            return False
        if node is None or type(node) in (str, bool, int):
            return True
        if type(node) is float:
            return math.isfinite(node)
        if type(node) is list:
            return all(visit(v, depth + 1) for v in node)
        if type(node) is dict:
            return all(type(k) is str and visit(v, depth + 1) for k, v in node.items())
        return False

    return visit(value, 0)


def encoded(value: Any) -> bytes:
    if not plain_data(value):
        raise ValueError("unsupported or over-budget rollback data")
    data = json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()
    if len(data) > MAX_BYTES:
        raise ValueError("rollback data exceeds byte budget")
    return data


def write(root: Path, payload: dict[str, Any]) -> dict[str, str]:
    """Persist before completed adoption; a crash can leave only an unused blob."""
    try:
        data = encoded(payload)
    except (ValueError, RecursionError):
        return {"status": "HOST_ARTIFACT_UNAVAILABLE", "schema": SCHEMA}
    digest = hashlib.sha256(data).hexdigest()
    directory = root / "rollback-data"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (digest + ".json")
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("rollback data digest collision or modified blob")
    else:
        fd, temporary = tempfile.mkstemp(dir=directory, prefix=".rollback-")
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return {"status": "DURABLE_DATA_ONLY", "schema": SCHEMA, "sha256": digest}


def read(root: Path, record: Mapping[str, Any]) -> dict[str, Any]:
    binding = record.get("rollback_data", {})
    if not isinstance(binding, Mapping):
        raise ValueError("invalid rollback binding")
    digest = binding.get("sha256", "")
    if (binding.get("status") != "DURABLE_DATA_ONLY" or binding.get("schema") != SCHEMA
            or type(digest) is not str or re.fullmatch("[0-9a-f]{64}", digest) is None):
        raise ValueError("no registered data-only rollback binding")
    with (root / "rollback-data" / (digest + ".json")).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("rollback snapshot digest mismatch or budget exceeded")
    payload = json.loads(data)
    if (type(payload) is not dict or set(payload) != FIELDS or not plain_data(payload)
            or payload["schema"] != SCHEMA or payload["proposal_fingerprint"] != record.get("adopted")
            or payload["target"] != record.get("target") or payload["incumbent"] != record.get("incumbent")
            or type(payload["target"]) is not str or type(payload["incumbent"]) is not str
            or type(payload["previous_state_hash"]) is not str
            or re.fullmatch("[0-9a-f]{64}", payload["previous_state_hash"]) is None
            or type(payload["previous_components"]) is not dict or type(payload["cache_snapshot"]) is not dict
            or type(payload["previous_components"].get(payload["target"])) is not dict
            or payload["previous_components"][payload["target"]].get("artifact") != payload["incumbent"]):
        raise ValueError("rollback snapshot schema or adoption binding mismatch")
    return payload
