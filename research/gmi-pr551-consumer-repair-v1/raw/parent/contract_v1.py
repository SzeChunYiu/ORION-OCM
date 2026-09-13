"""Small strict contracts shared by the static census and its independent oracle."""
import hashlib
import json
import math


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def bad(value):
        raise AuditError("nonfinite JSON: " + value)
    result = json.loads(data, object_pairs_hook=pairs, parse_constant=bad)
    def finite(value):
        if isinstance(value, float):
            require(math.isfinite(value), "nonfinite JSON number")
        elif isinstance(value, dict):
            for child in value.values(): finite(child)
        elif isinstance(value, list):
            for child in value: finite(child)
    finite(result)
    return result


def same(a, b, message):
    require(json.dumps(a, sort_keys=True, allow_nan=False) ==
            json.dumps(b, sort_keys=True, allow_nan=False), message)


def receipt_self_hash(record):
    # Exact pinned core.sha256_of convention, including its default separators.
    value = {k: v for k, v in record.items() if k != "receipt_sha256"}
    return sha(json.dumps(value, sort_keys=True, default=str).encode())
