"""External exact grading against recorded original SV calls; never import the router/checker."""
from dataclasses import asdict, is_dataclass
from enum import Enum
from fractions import Fraction
import hashlib
import json


def wire(value):
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return wire(asdict(value))
    if isinstance(value, dict):
        return {str(k): wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [wire(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return [wire(v) for v in sorted(value, key=repr)]
    if value is None or type(value) in (str, int, bool, float):
        return value
    raise TypeError(f"Unsupported explicit record type: {type(value).__name__}")


def digest(value):
    return hashlib.sha256(json.dumps(wire(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def compare(reference, candidate):
    differences = []
    for key in ("request", "vectors", "consumer", "surprise"):
        if reference[key] != candidate[key]:
            differences.append(key)
    return {"functional_parity": not differences, "differences": differences,
            "reference_digest": digest({k: reference[k] for k in ("request", "vectors", "consumer", "surprise")}),
            "candidate_digest": digest({k: candidate[k] for k in ("request", "vectors", "consumer", "surprise")}),
            "performance_authority": "NOT_TESTED"}
