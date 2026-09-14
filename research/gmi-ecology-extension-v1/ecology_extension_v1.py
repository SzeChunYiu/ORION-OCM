"""Validator for the ecology extension contract (592 item 2 / 602 A2).

Loads ECOLOGY_EXTENSION_CONTRACT_V1.json + SCHEMA_V1.json, checks schema
shape, coordinate counts, field floors, other_agents values,
equivalence/remint booleans, and a 3-world toy remint model.
CPython 3.8 safe. No network, no sampling.
"""

from pathlib import Path
import json
import re

def _here():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        for cand in [Path.cwd() / "research/gmi-ecology-extension-v1", Path.cwd()]:
            if (cand / "ECOLOGY_EXTENSION_CONTRACT_V1.json").exists():
                return cand
        return Path.cwd()

HERE = _here()
CONTRACT = HERE / "ECOLOGY_EXTENSION_CONTRACT_V1.json"
SCHEMA = HERE / "SCHEMA_V1.json"

REQUIRED_COORDS = [
    "other_agents",
    "observation_structure",
    "action_intervention_structure",
    "feedback_verifier_structure",
    "task_distribution_horizon",
    "drift_regime_change",
    "recurrence_reuse_structure",
    "noise_partial_observability",
    "compositionality_symmetry_relational",
    "social_topology",
    "embodiment_sensor_actuator",
    "resource_prices_budgets",
    "verification_latency_cost",
    "information_acquisition_cost",
    "protected_splits",
]


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def load_schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def validate_schema(data=None):
    if data is None:
        data = load_schema()
    if not isinstance(data, dict):
        raise ValueError("schema must be object")
    if data.get("title") != "EcologyExtensionContractV1":
        raise ValueError("schema title mismatch")
    props = data.get("properties", {}).get("coordinates", {}).get("properties", {})
    for coord in REQUIRED_COORDS:
        if coord not in props:
            raise ValueError("schema missing coordinate %r" % coord)
    return {"schema_coords": len(props), "status": "PASS"}


def is_bijection(mapping, n):
    """True iff mapping is a bijection on 0..n-1 (permutation)."""
    if not isinstance(mapping, dict) or len(mapping) != n:
        return False
    if set(mapping.keys()) != set(range(n)):
        return False
    if set(mapping.values()) != set(range(n)):
        return False
    return True


def validate_contract(data=None):
    if data is None:
        data = load_contract()
    if not isinstance(data, dict):
        raise ValueError("contract must be object")
    if data.get("schema") != "EcologyExtensionContractV1":
        raise ValueError("wrong schema tag: %r" % data.get("schema"))
    if not isinstance(data.get("scope"), str) or len(data["scope"]) < 20:
        raise ValueError("scope too short")
    ext = data.get("extends")
    if not isinstance(ext, list) or len(ext) < 2:
        raise ValueError("extends must be list with >=2 entries")
    coords = data.get("coordinates")
    if not isinstance(coords, dict):
        raise ValueError("coordinates must be object")
    if set(coords.keys()) != set(REQUIRED_COORDS):
        missing = set(REQUIRED_COORDS) - set(coords.keys())
        extra = set(coords.keys()) - set(REQUIRED_COORDS)
        raise ValueError("coordinate set mismatch missing=%r extra=%r" % (missing, extra))
    for name in REQUIRED_COORDS:
        entry = coords[name]
        if not isinstance(entry, dict):
            raise ValueError("coord %r must be object" % name)
        for field in ("definition", "parent", "falsifier"):
            if field not in entry:
                raise ValueError("coord %r missing field %r" % (name, field))
            val = entry[field]
            if not isinstance(val, str) or not val.strip():
                raise ValueError("coord %r field %r must be non-empty string" % (name, field))
        if len(entry["definition"]) < 20:
            raise ValueError("coord %r definition too short" % name)
        if len(entry["parent"]) < 10:
            raise ValueError("coord %r parent too short" % name)
        if len(entry["falsifier"]) < 20:
            raise ValueError("coord %r falsifier too short" % name)
    # other_agents specific: values must include NONE and ADAPTIVE_OPPONENTS
    oa = coords["other_agents"]
    vals = oa.get("values")
    if not isinstance(vals, list) or len(vals) < 2:
        raise ValueError("other_agents values must be list with >=2")
    if "NONE" not in vals or "ADAPTIVE_OPPONENTS" not in vals:
        raise ValueError("other_agents values must include NONE and ADAPTIVE_OPPONENTS")
    # equivalence / remint top-level
    eq = data.get("equivalence_remint_rules")
    if not isinstance(eq, dict):
        raise ValueError("equivalence_remint_rules must be object")
    for field in ("definition", "parent", "falsifier"):
        if field not in eq or not isinstance(eq[field], str) or not eq[field].strip():
            raise ValueError("equivalence_remint_rules missing field %r" % field)
    if len(eq["definition"]) < 20:
        raise ValueError("equivalence definition too short")
    if len(eq["parent"]) < 10:
        raise ValueError("equivalence parent too short")
    if len(eq["falsifier"]) < 20:
        raise ValueError("equivalence falsifier too short")
    if eq.get("remint_is_bijection") is not True:
        raise ValueError("remint_is_bijection must be true")
    if eq.get("label_leakage_forbidden") is not True:
        raise ValueError("label_leakage_forbidden must be true")
    return {"coords": len(coords), "other_agents_values": len(vals), "status": "PASS"}


def check_toy_remints():
    """3-world toy: identity and disjoint relabel accepted, collapsing and leaking rejected."""
    n = 3
    identity = {0: 0, 1: 1, 2: 2}
    relabel = {0: 2, 1: 0, 2: 1}
    collapsing = {0: 0, 1: 0, 2: 2}
    leaking = {0: 0, 1: 0, 2: 1}
    if not is_bijection(identity, n):
        raise ValueError("identity should be valid remint")
    if not is_bijection(relabel, n):
        raise ValueError("relabel should be valid remint")
    if is_bijection(collapsing, n):
        raise ValueError("collapsing map should be rejected as non-bijective remint")
    if is_bijection(leaking, n):
        raise ValueError("leaking map should be rejected (non-bijective, encodes answer)")
    return {"toy_checks": 4, "status": "PASS"}


def run():
    c = load_contract()
    s = load_schema()
    r1 = validate_schema(s)
    r2 = validate_contract(c)
    r3 = check_toy_remints()
    return {"schema": r1, "contract": r2, "remint_toy": r3, "status": "PASS"}


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(run(), indent=2))
