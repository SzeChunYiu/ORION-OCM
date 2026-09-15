from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha1
from itertools import product
import json
from pathlib import Path

AXIOMS = ("AX-1", "AX-2", "AX-3", "AX-4", "AX-5", "AX-6")
CLAIM_CEILING = "GMI_REGISTERED_FINITE_AXIOM_CORE_SATISFIABLE_AND_COMPACT_AT_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "GMI_ABSOLUTELY_CONSISTENT",
    "ZFC_CONSISTENCY_PROVED",
    "ALL_FUTURE_GMI_EXTENSIONS_CONSISTENT",
    "ONTOLOGICAL_COMPLETENESS",
    "ALL_GMI_DERIVED_FROM_SIX_AXIOMS_UNIVERSALLY",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    ("research/gmi-833-foundation-v1/RESULT_V1.json", "c0c574c4ec6e237d5fdafa694eac131399625a70", "GMI_833_FOUNDATION_V1_FORMALIZED_AT_DECLARED_SCOPE"),
    ("research/gmi-833-parent-equivalence-v1/RESULT_V1.json", "7f6ee1c2d6e3e1bc24e66b192abffcc2d0a23ed3", "GMI_PARENT_EQUIVALENCE_BOUNDARIES_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-morphcap-v1/RESULT_V1.json", "bdc5c3cd42e312d8c7af52f7ba84220631a25f8a", "GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE"),
    ("research/gmi-833-global-uncertainty-v1/RESULT_V1.json", "9ab16cf59087214e093ace3b18c6d08fc79ab871", "GMI_GLOBAL_UNCERTAINTY_AND_ABSTENTION_CONTRACT_AT_REGISTERED_FINITE_SCOPE"),
)


def F(x):
    return x if isinstance(x, Fraction) else Fraction(str(x))


def repo_root(start: Path | None = None):
    p = (start or Path(__file__).resolve()).parent
    while p.parent != p:
        if (p / ".git").exists() or (p / "research").is_dir():
            return p
        p = p.parent
    return Path(__file__).resolve().parents[2]


def git_blob_sha(data: bytes):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None):
    root = root or repo_root()
    rows = []
    for path, expected_blob, expected_ceiling in PARENT_PINS:
        p = root / path
        if not p.is_file():
            rows.append({"path": path, "blob_ok": False, "claim_ceiling_ok": False, "actual_blob": None})
            continue
        data = p.read_bytes()
        blob = git_blob_sha(data)
        try:
            parsed = json.loads(data)
            claim = parsed.get("claim_ceiling")
            if path.endswith("gmi-833-foundation-v1/RESULT_V1.json"):
                claim = parsed.get("terminal")
        except Exception:
            claim = None
        rows.append({
            "path": path,
            "actual_blob": blob,
            "blob_ok": blob == expected_blob,
            "claim_ceiling_ok": claim == expected_ceiling,
        })
    return {"rows": rows, "all_ok": all(r["blob_ok"] and r["claim_ceiling_ok"] for r in rows)}


def base_model():
    return {
        "instances": ("i0", "i1"),
        "legal_traces": {"i0": ("t0", "t1"), "i1": ("t0", "t1")},
        "accepted": {"i0": ("t0",), "i1": ("t1",)},
        "states": ("s0", "s1", "s2"),
        "actions": ("stay", "flip"),
        "outputs": (0, 1),
        "initial_state": "s0",
        "transition": {
            ("s0", "stay"): "s0", ("s0", "flip"): "s1",
            ("s1", "stay"): "s1", ("s1", "flip"): "s0",
            ("s2", "stay"): "s2", ("s2", "flip"): "s2",
        },
        "emit": {
            ("s0", "stay"): 0, ("s0", "flip"): 1,
            ("s1", "stay"): 0, ("s1", "flip"): 1,
            ("s2", "stay"): 1, ("s2", "flip"): 1,
        },
        "resource_coordinates": ("compute", "memory"),
        "event_resources": {
            "execute_stay": {"compute": Fraction(1), "memory": Fraction(0)},
            "execute_flip": {"compute": Fraction(2), "memory": Fraction(0)},
            "store": {"compute": Fraction(0), "memory": Fraction(1)},
        },
        "versions": ("v0", "v1", "v2"),
        "development_initial": "v0",
        "development_edges": (("v0", "v1"), ("v1", "v2")),
        "development_resources": {
            ("v0", "v1"): {"compute": Fraction(1), "memory": Fraction(0)},
            ("v1", "v2"): {"compute": Fraction(1), "memory": Fraction(1)},
        },
        "development_budget": {"compute": Fraction(1), "memory": Fraction(1)},
        "capabilities": (
            {"id": "identity", "score_min": Fraction(0), "score_max": Fraction(1), "achieved": Fraction(3, 4), "ceiling": Fraction(1), "threshold": Fraction(2, 3), "depends_on": ("protected_trace", "resource_vector")},
            {"id": "hidden_world", "score_min": Fraction(0), "score_max": Fraction(1), "achieved": Fraction(1, 2), "ceiling": Fraction(1, 2), "threshold": Fraction(3, 4), "depends_on": ("protected_trace", "resource_vector")},
        ),
        "uncertainty": {
            "feasible": {"domain": (0, 1), "candidates": (0, 1)},
            "confidence": {"domain": (0, 1), "candidates": (0,), "alpha": Fraction(1, 10)},
            "predictive": {"outcomes": (0, 1), "probabilities": (Fraction(1, 4), Fraction(3, 4))},
        },
        "scope_records": (
            {"claim": "M_CORE_SATISFIES_AX1_AX6", "source_tag": "forall_fin", "target_tag": "forall_fin", "domain": "M_core"},
        ),
        "claim_record": {"claim": CLAIM_CEILING, "evidence_level": "EV2", "forbidden": FORBIDDEN_PROMOTIONS},
    }


def check_ax1(m):
    errors = []
    instances = tuple(m.get("instances", ()))
    if not instances:
        errors.append("EMPTY_INSTANCE_SET")
    for i in instances:
        legal = set(m.get("legal_traces", {}).get(i, ()))
        accepted = set(m.get("accepted", {}).get(i, ()))
        if not legal:
            errors.append(f"EMPTY_LEGAL_TRACE_SET:{i}")
        if not accepted:
            errors.append(f"EMPTY_ACCEPTED_SET:{i}")
        if not accepted.issubset(legal):
            errors.append(f"ACCEPTED_OUTSIDE_LEGAL:{i}")
    return tuple(errors)


def check_ax2(m):
    errors = []
    states = tuple(m.get("states", ()))
    actions = tuple(m.get("actions", ()))
    outputs = set(m.get("outputs", ()))
    state_set = set(states)
    if not states:
        errors.append("EMPTY_STATE_CARRIER")
    if not actions:
        errors.append("EMPTY_ACTION_CARRIER")
    if not outputs:
        errors.append("EMPTY_OUTPUT_CARRIER")
    if m.get("initial_state") not in state_set:
        errors.append("INITIAL_OUTSIDE_STATE")
    transition = m.get("transition", {})
    emit = m.get("emit", {})
    for s in states:
        for a in actions:
            key = (s, a)
            if key not in transition:
                errors.append(f"TRANSITION_NOT_TOTAL:{s}:{a}")
            elif transition[key] not in state_set:
                errors.append(f"TRANSITION_OUTSIDE_STATE:{s}:{a}")
            if key not in emit:
                errors.append(f"EMIT_NOT_TOTAL:{s}:{a}")
            elif emit[key] not in outputs:
                errors.append(f"EMIT_OUTSIDE_OUTPUT:{s}:{a}")
    return tuple(errors)


def _resource_errors(coords, vector, prefix):
    errors = []
    if set(vector) != set(coords):
        return (f"{prefix}:RESOURCE_COORDINATES_MISMATCH",)
    for c in coords:
        try:
            value = F(vector[c])
        except Exception:
            errors.append(f"{prefix}:NONRATIONAL:{c}")
            continue
        if value < 0:
            errors.append(f"{prefix}:NEGATIVE:{c}")
    return tuple(errors)


def check_ax3(m):
    errors = []
    coords = tuple(m.get("resource_coordinates", ()))
    if not coords or len(set(coords)) != len(coords):
        errors.append("BAD_RESOURCE_COORDINATES")
    for event, vector in m.get("event_resources", {}).items():
        errors.extend(_resource_errors(coords, vector, f"EVENT:{event}"))
    for edge, vector in m.get("development_resources", {}).items():
        errors.extend(_resource_errors(coords, vector, f"DEVELOPMENT:{edge}"))
    try:
        errors.extend(_resource_errors(coords, m["development_budget"], "BUDGET"))
    except KeyError:
        errors.append("MISSING_DEVELOPMENT_BUDGET")
    return tuple(errors)


def check_ax4(m):
    errors = []
    versions = set(m.get("versions", ()))
    if not versions:
        errors.append("EMPTY_VERSION_CARRIER")
    if m.get("development_initial") not in versions:
        errors.append("DEVELOPMENT_INITIAL_OUTSIDE_CARRIER")
    edges = tuple(m.get("development_edges", ()))
    if not edges:
        errors.append("EMPTY_DEVELOPMENT_RELATION")
    resources = m.get("development_resources", {})
    for u, v in edges:
        if u not in versions or v not in versions:
            errors.append(f"DEVELOPMENT_EDGE_OUTSIDE_CARRIER:{u}:{v}")
        if (u, v) not in resources:
            errors.append(f"DEVELOPMENT_EDGE_RESOURCE_MISSING:{u}:{v}")
    return tuple(errors)


def check_ax5(m):
    errors = []
    capabilities = tuple(m.get("capabilities", ()))
    if not capabilities:
        errors.append("NO_CAPABILITY_CONTRACT")
    allowed_dependencies = {"protected_trace", "resource_vector", "verifier_outcome", "task_instance"}
    for cap in capabilities:
        cid = cap.get("id", "<missing>")
        lo, hi = F(cap["score_min"]), F(cap["score_max"])
        achieved, ceiling = F(cap["achieved"]), F(cap["ceiling"])
        if lo > hi:
            errors.append(f"BAD_SCORE_DOMAIN:{cid}")
        if not lo <= achieved <= hi:
            errors.append(f"ACHIEVED_OUTSIDE_SCORE_DOMAIN:{cid}")
        if not lo <= ceiling <= hi:
            errors.append(f"CEILING_OUTSIDE_SCORE_DOMAIN:{cid}")
        if achieved > ceiling:
            errors.append(f"ACHIEVED_ABOVE_CEILING:{cid}")
        if set(cap.get("depends_on", ())) - allowed_dependencies:
            errors.append(f"NONEXTERNAL_CAPABILITY_DEPENDENCY:{cid}")
    return tuple(errors)


def check_ax6(m):
    errors = []
    uncertainty = m.get("uncertainty", {})
    feasible = uncertainty.get("feasible")
    if feasible is None:
        errors.append("FEASIBLE_MISSING")
    elif not set(feasible["candidates"]).issubset(set(feasible["domain"])):
        errors.append("FEASIBLE_OUTSIDE_DOMAIN")
    confidence = uncertainty.get("confidence")
    if confidence is None:
        errors.append("CONFIDENCE_MISSING")
    else:
        domain = set(confidence["domain"])
        candidates = set(confidence["candidates"])
        alpha = F(confidence["alpha"])
        if not candidates.issubset(domain):
            errors.append("CONFIDENCE_OUTSIDE_DOMAIN")
        if not 0 <= alpha <= 1:
            errors.append("CONFIDENCE_ALPHA_OUT_OF_RANGE")
        if not candidates and alpha < 1:
            errors.append("EMPTY_POSITIVE_COVERAGE_CONFIDENCE")
    predictive = uncertainty.get("predictive")
    if predictive is None:
        errors.append("PREDICTIVE_MISSING")
    else:
        outcomes = tuple(predictive["outcomes"])
        probabilities = tuple(F(x) for x in predictive["probabilities"])
        if len(outcomes) != len(probabilities) or len(set(outcomes)) != len(outcomes):
            errors.append("PREDICTIVE_SHAPE")
        if any(x < 0 for x in probabilities) or sum(probabilities, Fraction(0)) != 1:
            errors.append("PREDICTIVE_NOT_NORMALIZED")
    return tuple(errors)


CHECKS = {"AX-1": check_ax1, "AX-2": check_ax2, "AX-3": check_ax3, "AX-4": check_ax4, "AX-5": check_ax5, "AX-6": check_ax6}


def validate_model(model):
    details = {axiom: CHECKS[axiom](model) for axiom in AXIOMS}
    violated = tuple(axiom for axiom in AXIOMS if details[axiom])
    return {"satisfies": not violated, "violated_axioms": violated, "details": details}


def protected_response_profiles(model):
    return {s: tuple(model["emit"][(s, a)] for a in model["actions"]) for s in model["states"]}


def protected_response_quotient(model):
    groups = {}
    for state, profile in protected_response_profiles(model).items():
        groups.setdefault(profile, []).append(state)
    return tuple(sorted((tuple(sorted(group)) for group in groups.values()), key=repr))


def relation_is_equivalence(carrier, relation):
    carrier = set(carrier)
    rel = set(relation)
    reflexive = all((x, x) in rel for x in carrier)
    symmetric = all((b, a) in rel for a, b in rel)
    transitive = all((a, c) in rel for a, b in rel for b2, c in rel if b == b2)
    closed = all(a in carrier and b in carrier for a, b in rel)
    return reflexive and symmetric and transitive and closed


def quotient_relation(model):
    profiles = protected_response_profiles(model)
    return tuple(sorted((a, b) for a in model["states"] for b in model["states"] if profiles[a] == profiles[b]))


def reachable_versions(model):
    coords = tuple(model["resource_coordinates"])
    budget = {c: F(model["development_budget"][c]) for c in coords}
    initial = model["development_initial"]
    reached = {initial}
    frontier = [(initial, {c: Fraction(0) for c in coords})]
    seen = set()
    while frontier:
        current, cost = frontier.pop()
        key = (current, tuple(cost[c] for c in coords))
        if key in seen:
            continue
        seen.add(key)
        for u, v in model["development_edges"]:
            if u != current:
                continue
            edge = model["development_resources"][(u, v)]
            new = {c: cost[c] + F(edge[c]) for c in coords}
            if all(new[c] <= budget[c] for c in coords):
                reached.add(v)
                frontier.append((v, new))
    return tuple(sorted(reached))


def capability_impossibility_ids(model):
    return tuple(cap["id"] for cap in model["capabilities"] if F(cap["threshold"]) > F(cap["ceiling"]))


def query_disposition(set_object, query=None):
    if query is None:
        return {"terminal": "CANNOT_CHECK", "values": ()}
    candidates = tuple(set_object["candidates"])
    if not candidates:
        return {"terminal": "INCONSISTENT_REGISTERED_ASSUMPTIONS", "values": ()}
    values = tuple(sorted({query(x) for x in candidates}, key=repr))
    return {"terminal": "IDENTIFIED" if len(values) == 1 else "CANNOT_IDENTIFY", "values": values}


ALLOWED_SCOPE_TAGS = {"forall", "forall_fin", "heldout", "sample"}


def check_meta1(model):
    errors = []
    for record in model.get("scope_records", ()):
        source, target = record.get("source_tag"), record.get("target_tag")
        if source not in ALLOWED_SCOPE_TAGS or target not in ALLOWED_SCOPE_TAGS:
            errors.append("UNKNOWN_SCOPE_TAG")
        if source in {"forall_fin", "heldout", "sample"} and target == "forall":
            errors.append(f"ILLEGAL_SCOPE_PROMOTION:{source}->forall")
    return tuple(errors)


EVIDENCE_ORDER = {"EV0": 0, "EV1": 1, "EV2": 2, "EV3": 3, "EV4": 4, "EV5": 5}
CLAIM_MIN_EVIDENCE = {CLAIM_CEILING: "EV2", "COMPLETE_GMI": "EV5"}


def check_meta2(model):
    record = model.get("claim_record", {})
    errors = []
    claim = record.get("claim")
    evidence = record.get("evidence_level")
    if claim in set(record.get("forbidden", ())):
        errors.append(f"FORBIDDEN_PROMOTION:{claim}")
    if evidence not in EVIDENCE_ORDER:
        errors.append("BAD_EVIDENCE_LEVEL")
    required = CLAIM_MIN_EVIDENCE.get(claim)
    if required and evidence in EVIDENCE_ORDER and EVIDENCE_ORDER[evidence] < EVIDENCE_ORDER[required]:
        errors.append(f"EVIDENCE_TOO_LOW:{evidence}<{required}")
    return tuple(errors)


def dependency_graph():
    return {
        "AX-1": (), "AX-2": (), "AX-3": (), "AX-4": (), "AX-5": (), "AX-6": (),
        "DEF-1": ("AX-1", "AX-2"),
        "DEF-2": ("AX-2", "AX-3", "AX-4"),
        "DEF-3": ("AX-3", "AX-4"),
        "DEF-4": ("AX-5",),
        "DEF-5": ("AX-6",),
        "META-1": (),
        "META-2": ("META-1",),
    }


def graph_is_acyclic(graph):
    state = {}
    def visit(node):
        if state.get(node) == 1:
            return False
        if state.get(node) == 2:
            return True
        state[node] = 1
        for dep in graph.get(node, ()):
            if dep not in graph or not visit(dep):
                return False
        state[node] = 2
        return True
    return all(visit(n) for n in graph)


def hostile_model(label):
    model = deepcopy(base_model())
    if label == "AX-1":
        model["accepted"]["i0"] = ()
    elif label == "AX-2":
        del model["transition"][("s0", "stay")]
    elif label == "AX-3":
        model["event_resources"]["execute_stay"]["compute"] = Fraction(-1)
    elif label == "AX-4":
        model["development_edges"] = (("v0", "v1"), ("v1", "outside"))
        model["development_resources"][("v1", "outside")] = {"compute": Fraction(0), "memory": Fraction(0)}
    elif label == "AX-5":
        caps = list(model["capabilities"])
        caps[0] = dict(caps[0], achieved=Fraction(5, 4), score_max=Fraction(2))
        model["capabilities"] = tuple(caps)
    elif label == "AX-6-outside":
        model["uncertainty"]["confidence"]["candidates"] = (2,)
    elif label == "AX-6-empty":
        model["uncertainty"]["confidence"]["candidates"] = ()
    elif label == "AX-6-predictive":
        model["uncertainty"]["predictive"]["probabilities"] = (Fraction(1, 4), Fraction(1, 2))
    elif label == "META-1":
        model["scope_records"] = ({"claim": "bad", "source_tag": "forall_fin", "target_tag": "forall", "domain": "M_core"},)
    elif label == "META-2":
        model["claim_record"]["claim"] = "COMPLETE_GMI"
    else:
        raise KeyError(label)
    return model


def hostile_hypercube():
    labels = ("AX-1", "AX-2", "AX-3", "AX-4", "AX-5", "AX-6-outside", "AX-6-predictive")
    failures = []
    violation_histogram = {}
    singleton = {}
    for bits in product((0, 1), repeat=len(labels)):
        model = base_model()
        for bit, label in zip(bits, labels):
            if not bit:
                continue
            patch = hostile_model(label)
            if label == "AX-1":
                model["accepted"] = patch["accepted"]
            elif label == "AX-2":
                model["transition"] = patch["transition"]
            elif label == "AX-3":
                model["event_resources"] = patch["event_resources"]
            elif label == "AX-4":
                model["development_edges"] = patch["development_edges"]
                model["development_resources"] = patch["development_resources"]
            elif label == "AX-5":
                model["capabilities"] = patch["capabilities"]
            elif label == "AX-6-outside":
                model["uncertainty"]["confidence"]["candidates"] = (2,)
            elif label == "AX-6-predictive":
                model["uncertainty"]["predictive"]["probabilities"] = (Fraction(1, 4), Fraction(1, 2))
        out = validate_model(model)
        expected = set()
        for bit, label in zip(bits, labels):
            if bit:
                expected.add("AX-6" if label.startswith("AX-6") else label)
        actual = set(out["violated_axioms"])
        key = ",".join(sorted(actual)) or "NONE"
        violation_histogram[key] = violation_histogram.get(key, 0) + 1
        if actual != expected:
            failures.append({"bits": bits, "expected": tuple(sorted(expected)), "actual": out["violated_axioms"]})
        if sum(bits) == 1:
            singleton[labels[bits.index(1)]] = out["violated_axioms"]
    return {"cases": 128, "failures": tuple(failures), "singleton_attribution": singleton, "satisfying_cases": violation_histogram.get("NONE", 0), "violation_histogram": violation_histogram}


def canonicalize(x):
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, tuple):
        return [canonicalize(v) for v in x]
    if isinstance(x, list):
        return [canonicalize(v) for v in x]
    if isinstance(x, dict):
        return {str(k): canonicalize(v) for k, v in sorted(x.items(), key=lambda kv: repr(kv[0]))}
    return x


def canonical_json(x):
    return json.dumps(canonicalize(x), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def build_receipt(parent_audit=None):
    model = base_model()
    valid = validate_model(model)
    quotient = protected_response_quotient(model)
    qrel = quotient_relation(model)
    hyper = hostile_hypercube()
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    independence = {}
    for label, expected in (
        ("AX-1", "AX-1"), ("AX-2", "AX-2"), ("AX-3", "AX-3"), ("AX-4", "AX-4"), ("AX-5", "AX-5"),
        ("AX-6-outside", "AX-6"), ("AX-6-empty", "AX-6"), ("AX-6-predictive", "AX-6"),
    ):
        independence[label] = validate_model(hostile_model(label))["violated_axioms"]
    meta1 = check_meta1(hostile_model("META-1"))
    meta2 = check_meta2(hostile_model("META-2"))
    checks = {
        "parents_exactly_pinned": parent_audit["all_ok"],
        "finite_model_satisfies_all_object_axioms": valid["satisfies"],
        "protected_response_quotient_nontrivial": 1 < len(quotient) < len(model["states"]),
        "protected_response_relation_is_equivalence": relation_is_equivalence(model["states"], qrel),
        "development_reachability_nontrivial": reachable_versions(model) == ("v0", "v1"),
        "impossibility_region_present": capability_impossibility_ids(model) == ("hidden_world",),
        "unknown_query_abstains": query_disposition(model["uncertainty"]["feasible"], lambda x: x)["terminal"] == "CANNOT_IDENTIFY",
        "constant_query_identified": query_disposition(model["uncertainty"]["feasible"], lambda x: 7)["terminal"] == "IDENTIFIED",
        "dependency_graph_acyclic": graph_is_acyclic(dependency_graph()),
        "bounded_independence_witnesses": all(set(v) == {("AX-6" if k.startswith("AX-6") else k)} for k, v in independence.items()),
        "hostile_hypercube_complete": hyper["cases"] == 128 and not hyper["failures"] and hyper["satisfying_cases"] == 1,
        "scope_promotion_blocked": bool(meta1),
        "claim_promotion_blocked": bool(meta2),
    }
    return {
        "schema": "GMI833FiniteAxiomCoreResultV1",
        "issue": 854,
        "parent_issue": 833,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "object_axioms": AXIOMS,
        "derived_definitions": ("DEF-1", "DEF-2", "DEF-3", "DEF-4", "DEF-5"),
        "metarules": ("META-1", "META-2"),
        "parent_audit": parent_audit,
        "finite_model": {
            "state_count": len(model["states"]),
            "action_count": len(model["actions"]),
            "version_count": len(model["versions"]),
            "resource_coordinates": model["resource_coordinates"],
            "protected_response_quotient": quotient,
            "reachable_versions": reachable_versions(model),
            "impossibility_ids": capability_impossibility_ids(model),
            "identity_query": query_disposition(model["uncertainty"]["feasible"], lambda x: x),
            "constant_query": query_disposition(model["uncertainty"]["feasible"], lambda x: 7),
        },
        "independence_witnesses": independence,
        "hostile_hypercube": hyper,
        "governance_hostiles": {"META-1": meta1, "META-2": meta2},
        "dependency_graph": dependency_graph(),
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


if __name__ == "__main__":
    print(canonical_json(build_receipt(audit_parents())), end="")
