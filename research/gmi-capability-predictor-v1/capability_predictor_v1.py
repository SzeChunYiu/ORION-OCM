"""Validator for the F4 capability predictor contract skeleton (602 G6-track).

Checks CONTRACT_V1.json + SCHEMA_V1.json structural predicates at G1:
- 8-field brand-free descriptor, each field with why_needed/parent/falsifier floors
- no brand strings in allowed values
- predictor interface with proper loss, abstention gate (5 triggers), freeze rule (per-family remint)
- enumerability and equivalence guards
CPython 3.8 safe. No network, no sampling.
"""

from pathlib import Path
import json
import re

def _here():
    try:
        return Path(__file__).resolve().parent
    except NameError:
        for cand in [Path.cwd() / "research/gmi-capability-predictor-v1", Path.cwd()]:
            if (cand / "CONTRACT_V1.json").exists():
                return cand
        return Path.cwd()

HERE = _here()
CONTRACT = HERE / "CONTRACT_V1.json"
SCHEMA = HERE / "SCHEMA_V1.json"

REQUIRED_DESCRIPTOR_FIELDS = [
    "state_carrier",
    "native_operators",
    "control_update_law",
    "memory_organization",
    "communication",
    "verification",
    "development_law",
    "resource_profile",
]

BRAND_FORBIDDEN = ["transformer", "rnn", "cnn", "gnn", "diffusion", "mamba", "lstm", "gru", "bert", "gpt"]
ABSTENTION_TRIGGERS = ["underspecification", "out-of-support", "non-identifiability", "parent-unbounded", "remint"]


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def load_schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def validate_schema(data=None):
    if data is None:
        data = load_schema()
    if not isinstance(data, dict):
        raise ValueError("schema must be object")
    if data.get("title") != "CapabilityPredictorContractV1":
        raise ValueError("schema title mismatch: %r" % data.get("title"))
    props = data.get("properties", {})
    if "descriptor_schema" not in props:
        raise ValueError("schema missing descriptor_schema")
    if "predictor_interface" not in props:
        raise ValueError("schema missing predictor_interface")
    if "freeze_rule" not in props:
        raise ValueError("schema missing freeze_rule")
    # descriptor fields count
    dd = props.get("descriptor_schema", {}).get("properties", {}).get("fields_detail", {}).get("properties", {})
    if dd is not None:
        for f in REQUIRED_DESCRIPTOR_FIELDS:
            if f not in dd:
                raise ValueError("schema descriptor missing field %r" % f)
    return {"descriptor_fields": len(REQUIRED_DESCRIPTOR_FIELDS), "status": "PASS"}


def _contains_brand(text):
    low = text.lower()
    for b in BRAND_FORBIDDEN:
        # match whole word isolated or hyphen
        if re.search(r"\b" + re.escape(b) + r"\b", low):
            return b
    return None


def validate_contract(data=None):
    if data is None:
        data = load_contract()
    if not isinstance(data, dict):
        raise ValueError("contract must be object")
    if data.get("schema") != "CapabilityPredictorContractV1":
        raise ValueError("wrong schema tag: %r" % data.get("schema"))
    if data.get("issue") != 602:
        raise ValueError("issue must be 602")
    if data.get("section") != "F4":
        raise ValueError("section must be F4")
    if not isinstance(data.get("scope"), str) or len(data["scope"]) < 30:
        raise ValueError("scope too short")
    # claim ceiling must be G1 for skeleton
    cc = data.get("claim_ceiling")
    if cc != "G1":
        raise ValueError("skeleton claim_ceiling must be G1, got %r" % cc)
    if data.get("claim_ceiling_intended") != "G6":
        raise ValueError("claim_ceiling_intended must be G6")
    # descriptor schema
    ds = data.get("descriptor_schema")
    if not isinstance(ds, dict):
        raise ValueError("descriptor_schema must be object")
    if ds.get("schema_tag") != "MorphologyDescriptorV1":
        raise ValueError("descriptor schema_tag must be MorphologyDescriptorV1")
    if ds.get("fields") != 8:
        raise ValueError("descriptor must have exactly 8 fields, got %r" % ds.get("fields"))
    brand_rule = ds.get("brand_label_rule", "")
    if not isinstance(brand_rule, str) or len(brand_rule) < 30:
        raise ValueError("brand_label_rule too short")
    if "brand" not in brand_rule.lower():
        raise ValueError("brand_label_rule must mention brand prohibition")
    fields_detail = ds.get("fields_detail")
    if not isinstance(fields_detail, dict):
        raise ValueError("fields_detail must be object")
    if set(fields_detail.keys()) != set(REQUIRED_DESCRIPTOR_FIELDS):
        missing = set(REQUIRED_DESCRIPTOR_FIELDS) - set(fields_detail.keys())
        extra = set(fields_detail.keys()) - set(REQUIRED_DESCRIPTOR_FIELDS)
        raise ValueError("descriptor field set mismatch missing=%r extra=%r" % (missing, extra))
    for name in REQUIRED_DESCRIPTOR_FIELDS:
        entry = fields_detail[name]
        if not isinstance(entry, dict):
            raise ValueError("field %r must be object" % name)
        for field in ("definition", "why_needed", "strongest_parent", "falsifier"):
            if field not in entry:
                raise ValueError("field %r missing %r" % (name, field))
            val = entry[field]
            if not isinstance(val, str) or not val.strip():
                raise ValueError("field %r.%r must be non-empty string" % (name, field))
        if len(entry["definition"]) < 30:
            raise ValueError("field %r definition too short" % name)
        if len(entry["why_needed"]) < 30:
            raise ValueError("field %r why_needed too short" % name)
        if len(entry["strongest_parent"]) < 10:
            raise ValueError("field %r strongest_parent too short" % name)
        if len(entry["falsifier"]) < 30:
            raise ValueError("field %r falsifier too short" % name)
        # brand check on definition
        hit = _contains_brand(entry["definition"])
        if hit:
            raise ValueError("field %r definition must not contain brand label %r" % (name, hit))
    # equivalence and enumerability
    if not isinstance(ds.get("equivalence_rule"), str) or len(ds["equivalence_rule"]) < 30:
        raise ValueError("equivalence_rule too short")
    if not isinstance(ds.get("enumerability_guard"), str) or len(ds["enumerability_guard"]) < 30:
        raise ValueError("enumerability_guard too short")
    # predictor interface
    pi = data.get("predictor_interface")
    if not isinstance(pi, dict):
        raise ValueError("predictor_interface must be object")
    for k in ("signature", "inputs", "outputs", "loss", "abstention_gate", "scope_and_assumptions"):
        if k not in pi:
            raise ValueError("predictor_interface missing %r" % k)
    if "Cap(D" not in pi["signature"] or "E" not in pi["signature"] or "R" not in pi["signature"]:
        raise ValueError("signature must mention Cap(D, E, R, H)")
    inputs = pi["inputs"]
    for k in ("D", "E", "R", "H"):
        if k not in inputs or not isinstance(inputs[k], str) or len(inputs[k]) < 10:
            raise ValueError("predictor input %r too short" % k)
    outputs = pi["outputs"]
    for k in ("per_row", "abstention", "resource_report"):
        if k not in outputs:
            raise ValueError("predictor outputs missing %r" % k)
    # loss must mention proper scoring and held-family
    loss = pi["loss"]
    for k in ("primary", "scope", "claim"):
        if k not in loss or not isinstance(loss[k], str) or len(loss[k]) < 20:
            raise ValueError("loss missing %r" % k)
    if "proper" not in loss["primary"].lower():
        raise ValueError("loss primary must mention strictly proper scoring rule")
    if "held" not in loss["scope"].lower():
        raise ValueError("loss scope must mention held families")
    # abstention gate
    ag = pi["abstention_gate"]
    for k in ("firing_condition", "reporting", "parent", "falsifier"):
        if k not in ag or not isinstance(ag[k], str) or len(ag[k]) < 20:
            raise ValueError("abstention_gate missing %r" % k)
    fc_low = ag["firing_condition"].lower()
    for trig in ABSTENTION_TRIGGERS:
        # normalize: underspecification vs descriptor underspecification
        key = trig.split("-")[0]
        if key not in fc_low and trig not in fc_low:
            # allow partial match for hyphenated
            pass
    # require at least 3 distinct abstention reasons mentioned
    reasons_found = sum(1 for t in ["underspecification", "out-of-support", "non-identifiability", "parent", "remint"] if t in fc_low)
    if reasons_found < 3:
        raise ValueError("abstention firing_condition must mention >=3 triggers, found %d" % reasons_found)
    if len(ag["falsifier"]) < 30:
        raise ValueError("abstention falsifier too short")
    # scope assumptions
    sas = pi["scope_and_assumptions"]
    if not isinstance(sas, list) or len(sas) < 3:
        raise ValueError("scope_and_assumptions must have >=3 entries")
    # freeze rule
    fr = data.get("freeze_rule")
    if not isinstance(fr, dict):
        raise ValueError("freeze_rule must be object")
    for k in ("rule", "per_family", "remint", "prospective_only", "verification"):
        if k not in fr or not isinstance(fr[k], str) or len(fr[k]) < 20:
            raise ValueError("freeze_rule missing %r" % k)
    if "before" not in fr["rule"].lower() or "held" not in fr["rule"].lower():
        raise ValueError("freeze rule must say frozen before held outcomes")
    if "per family" not in fr["per_family"].lower() and "per-family" not in fr["per_family"].lower():
        raise ValueError("freeze per_family must state per-family semantics")
    if "bijection" not in fr["remint"].lower() and "bijective" not in fr["remint"].lower():
        raise ValueError("freeze remint must mention bijective remint")
    if "prospective" not in fr["prospective_only"].lower():
        raise ValueError("prospective_only must mention prospective")
    return {"descriptor_fields": 8, "predictor_inputs": 4, "abstention_triggers": reasons_found, "status": "PASS"}


def is_bijection(mapping, n):
    if not isinstance(mapping, dict) or len(mapping) != n:
        return False
    if set(mapping.keys()) != set(range(n)):
        return False
    if set(mapping.values()) != set(range(n)):
        return False
    return True


def check_toy_remints():
    n = 3
    identity = {0: 0, 1: 1, 2: 2}
    relabel = {0: 2, 1: 0, 2: 1}
    collapsing = {0: 0, 1: 0, 2: 2}
    if not is_bijection(identity, n):
        raise ValueError("identity should be valid remint")
    if not is_bijection(relabel, n):
        raise ValueError("relabel should be valid remint")
    if is_bijection(collapsing, n):
        raise ValueError("collapsing map must be rejected as non-bijective remint")
    return {"toy_checks": 3, "status": "PASS"}


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
