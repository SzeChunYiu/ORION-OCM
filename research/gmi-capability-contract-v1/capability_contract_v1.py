"""Validator for the 27-row capability contract (592 item 4 / 602 A4).

Loads CONTRACT_V1.json and SCHEMA_V1.json, checks schema shape, row
counts, field lengths, id uniqueness and twin/parent/falsifier presence.
CPython 3.8 safe. No network, no sampling.
"""

from pathlib import Path
import json
import re

def _here():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        for cand in [Path.cwd() / "research/gmi-capability-contract-v1", Path.cwd()]:
            if (cand / "CONTRACT_V1.json").exists():
                return cand
        return Path.cwd()

HERE = _here()
CONTRACT = HERE / "CONTRACT_V1.json"
SCHEMA = HERE / "SCHEMA_V1.json"

REQUIRED_FIELDS = [
    "id", "capability", "inputs", "allowed_info", "required_behaviour",
    "success_metric", "resource_metric", "negative_twin",
    "strongest_parent", "atlas_reduction", "falsifier",
]

EXPECTED_IDS = [
    "cap-perception", "cap-selective-attention", "cap-working-memory",
    "cap-episodic-memory", "cap-semantic-memory", "cap-procedural-memory",
    "cap-retrieval", "cap-consolidation", "cap-forgetting",
    "cap-prediction", "cap-abstraction-concept", "cap-compositional-reasoning",
    "cap-hierarchical-skill", "cap-planning", "cap-exploration",
    "cap-causal-inference", "cap-counterfactual-reasoning", "cap-metacognition",
    "cap-social-cognition", "cap-communication", "cap-imitation",
    "cap-teaching", "cap-cultural-accumulation", "cap-self-modeling",
    "cap-self-improvement", "cap-tool-use", "cap-coordination",
]


def load_contract():
    text = CONTRACT.read_text(encoding="utf-8")
    data = json.loads(text)
    return data


def load_schema():
    text = SCHEMA.read_text(encoding="utf-8")
    data = json.loads(text)
    return data


def validate_contract(data=None):
    if data is None:
        data = load_contract()
    if not isinstance(data, dict):
        raise ValueError("contract must be an object")
    if data.get("schema") != "CapabilityContractV1":
        raise ValueError("wrong schema tag: %r" % data.get("schema"))
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise ValueError("rows must be a list")
    if len(rows) != 27:
        raise ValueError("expected 27 rows, got %d" % len(rows))
    ids = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError("row %d must be object" % i)
        for field in REQUIRED_FIELDS:
            if field not in row:
                raise ValueError("row %d missing field %r" % (i, field))
            val = row[field]
            if not isinstance(val, str) or not val.strip():
                raise ValueError("row %d field %r must be non-empty string" % (i, field))
        # length floors (catch thin columns)
        if len(row["inputs"]) < 20:
            raise ValueError("row %d inputs too short" % i)
        if len(row["allowed_info"]) < 20:
            raise ValueError("row %d allowed_info too short" % i)
        if len(row["required_behaviour"]) < 20:
            raise ValueError("row %d required_behaviour too short" % i)
        if len(row["success_metric"]) < 20:
            raise ValueError("row %d success_metric too short" % i)
        if len(row["resource_metric"]) < 15:
            raise ValueError("row %d resource_metric too short" % i)
        if len(row["negative_twin"]) < 20:
            raise ValueError("row %d negative_twin too short" % i)
        if len(row["falsifier"]) < 20:
            raise ValueError("row %d falsifier too short" % i)
        if not re.match(r"^cap-[a-z0-9-]+$", row["id"]):
            raise ValueError("row %d bad id %r" % (i, row["id"]))
        ids.append(row["id"])
    if len(set(ids)) != 27:
        raise ValueError("duplicate ids: %r" % ids)
    if set(ids) != set(EXPECTED_IDS):
        missing = set(EXPECTED_IDS) - set(ids)
        extra = set(ids) - set(EXPECTED_IDS)
        raise ValueError("id set mismatch missing=%r extra=%r" % (missing, extra))
    # scope present
    if not isinstance(data.get("scope"), str) or len(data["scope"]) < 20:
        raise ValueError("scope too short or missing")
    return {"rows": len(rows), "ids": sorted(ids), "status": "PASS"}


def validate_schema(data=None):
    if data is None:
        data = load_schema()
    if not isinstance(data, dict):
        raise ValueError("schema must be object")
    if data.get("title") != "CapabilityContractV1":
        raise ValueError("schema title mismatch")
    props = data.get("properties", {}).get("rows", {}).get("items", {}).get("properties", {})
    for field in REQUIRED_FIELDS:
        if field not in props:
            raise ValueError("schema missing property %r" % field)
    return {"schema_fields": len(props), "status": "PASS"}


def check_twin_parent_falsifier_present(data=None):
    if data is None:
        data = load_contract()
    rows = data["rows"]
    thin = []
    for row in rows:
        for col in ("negative_twin", "strongest_parent", "falsifier", "atlas_reduction"):
            if len(row[col].strip()) < 10:
                thin.append((row["id"], col))
    if thin:
        raise ValueError("thin twin/parent/falsifier/atlas: %r" % thin)
    return {"checked": len(rows), "status": "PASS"}


def run():
    c = load_contract()
    s = load_schema()
    r1 = validate_schema(s)
    r2 = validate_contract(c)
    r3 = check_twin_parent_falsifier_present(c)
    return {"contract": r2, "schema": r1, "twin_parent": r3, "status": "PASS"}


if __name__ == "__main__":
    import json as _json
    print(_json.dumps(run(), indent=2))
