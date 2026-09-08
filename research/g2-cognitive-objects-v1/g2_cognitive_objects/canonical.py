"""Canonical JSON: sorted keys, no NaN, duplicate keys refused."""
from __future__ import annotations

import json
import math
from typing import Any

MAX_BYTES = 1 << 20
MAX_NODES = 100_000
MAX_DEPTH = 40


class SchemaError(ValueError):
    """Refused G2.1 object or JSON."""


def _walk(value: Any, *, nodes: list[int], depth: int) -> None:
    nodes[0] += 1
    if nodes[0] > MAX_NODES or depth > MAX_DEPTH:
        raise SchemaError("G2_DATA_BOUND")
    if isinstance(value, dict):
        if any(type(k) is not str for k in value):
            raise SchemaError("G2_DATA_KEY")
        for item in value.values():
            _walk(item, nodes=nodes, depth=depth + 1)
    elif isinstance(value, list):
        for item in value:
            _walk(item, nodes=nodes, depth=depth + 1)
    elif type(value) is float:
        if not math.isfinite(value):
            raise SchemaError("G2_DATA_FLOAT")
    elif type(value) not in (str, int, bool, type(None)):
        raise SchemaError("G2_NOT_DATA")


def dumps(value: Any) -> bytes:
    _walk(value, nodes=[0], depth=0)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    if len(raw) > MAX_BYTES:
        raise SchemaError("G2_DATA_BOUND")
    return raw


def loads(data: bytes) -> Any:
    if type(data) is not bytes or len(data) > MAX_BYTES:
        raise SchemaError("G2_DATA_BYTES")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SchemaError("G2_DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(data, object_pairs_hook=pairs)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise SchemaError("G2_JSON") from exc
    if dumps(value) != data:
        raise SchemaError("G2_NONCANONICAL")
    return value
