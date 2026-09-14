"""Architecture-name-free morphology descriptor for issue #602 F4."""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent
REGISTRY = json.loads((ROOT / "MORPHOLOGY_DESCRIPTOR_V1.json").read_text())


def coordinate_contract() -> dict[str, tuple[str, ...]]:
    return {
        row["id"]: tuple(row["required_fields"])
        for row in REGISTRY["coordinates"]
    }


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _strings(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _strings(child)


def _assert_no_family_tokens(features: dict[str, Any]) -> None:
    forbidden = tuple(token.casefold() for token in REGISTRY["forbidden_feature_tokens"])
    for text in _strings(features):
        folded = text.casefold()
        for token in forbidden:
            if token in folded:
                raise ValueError(f"predictor-visible family token forbidden: {token}")


def validate_descriptor(descriptor: dict[str, Any]) -> None:
    if set(descriptor) != {"specimen_id", "source_ref", "features"}:
        raise ValueError("descriptor must contain exactly specimen_id, source_ref, features")
    if not isinstance(descriptor["specimen_id"], str) or not descriptor["specimen_id"]:
        raise ValueError("specimen_id must be a nonempty opaque string")
    if not isinstance(descriptor["source_ref"], str):
        raise ValueError("source_ref must be a string")
    features = descriptor["features"]
    if not isinstance(features, dict):
        raise ValueError("features must be an object")

    contract = coordinate_contract()
    if set(features) != set(contract):
        missing = sorted(set(contract) - set(features))
        extra = sorted(set(features) - set(contract))
        raise ValueError(f"feature coordinate mismatch; missing={missing}, extra={extra}")

    for coordinate, required in contract.items():
        payload = features[coordinate]
        if not isinstance(payload, dict):
            raise ValueError(f"{coordinate} must be an object")
        if set(payload) != set(required):
            raise ValueError(f"{coordinate} fields must equal {sorted(required)}")
        for field, value in payload.items():
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                if value < 0:
                    raise ValueError(f"{coordinate}.{field} must be nonnegative")
                continue
            if isinstance(value, str):
                if not value:
                    raise ValueError(f"{coordinate}.{field} string must be nonempty")
                continue
            raise ValueError(f"unsupported feature value at {coordinate}.{field}")

    _assert_no_family_tokens(features)


def predictor_projection(descriptor: dict[str, Any]) -> dict[str, Any]:
    """Return the only object a capability predictor may consume."""
    validate_descriptor(descriptor)
    return json.loads(json.dumps(descriptor["features"], sort_keys=True))


def morphology_fingerprint(descriptor: dict[str, Any]) -> str:
    projection = predictor_projection(descriptor)
    canonical = json.dumps(projection, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
