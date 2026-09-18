#!/usr/bin/env python3
"""Separated post-hoc exact-reference mapper for issue #998."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
UNKNOWN = "UNKNOWN"


def observation_fingerprint(value: object) -> tuple[tuple[str, tuple[int, ...]], ...]:
    if type(value) not in (tuple, list) or len(value) != 3:
        raise ValueError("protected fingerprint must contain exactly three rows")
    rows: list[tuple[str, tuple[int, ...]]] = []
    for row in value:
        if type(row) not in (tuple, list) or len(row) != 2 or type(row[0]) is not str:
            raise ValueError("malformed protected fingerprint row")
        if type(row[1]) not in (tuple, list) or any(type(item) is not int or item < 0 for item in row[1]):
            raise ValueError("malformed protected output")
        rows.append((row[0], tuple(row[1])))
    return tuple(rows)


def load_registry(path: Path | None = None) -> tuple[dict[str, object], ...]:
    source = path or HERE / "PROTOCOL_V1.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    rows = payload.get("posthoc_registry")
    if type(rows) is not list or not rows:
        raise ValueError("post-hoc registry must be a nonempty list")
    result: list[dict[str, object]] = []
    for row in rows:
        if type(row) is not dict or set(row) != {"family", "observations"}:
            raise ValueError("malformed post-hoc registry row")
        if type(row["family"]) is not str or not row["family"] or row["family"] == UNKNOWN:
            raise ValueError("known reference label is invalid")
        result.append({"family": row["family"], "observations": observation_fingerprint(row["observations"])})
    return tuple(result)


def map_fingerprint(
    observations: object,
    registry: tuple[dict[str, object], ...] | None = None,
) -> str:
    fingerprint = observation_fingerprint(observations)
    references = load_registry() if registry is None else registry
    if type(references) is not tuple:
        raise ValueError("registry must be a tuple")
    matches = []
    for row in references:
        if type(row) is not dict or set(row) != {"family", "observations"}:
            raise ValueError("malformed runtime registry row")
        if observation_fingerprint(row["observations"]) == fingerprint:
            matches.append(row["family"])
    return matches[0] if len(matches) == 1 else UNKNOWN
