"""Exhaustive target-class optimizer in the PINNED V4/V5 finite surrogate domain.

This repairs witness-versus-class comparison at that model's scope. It does not
turn capability scores and separately supplied resource laws into real machines.
No search/target freeze, old verdict, protected seed or execution script is edited.
"""
from __future__ import annotations
from dataclasses import replace
import hashlib
import importlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

SOURCE_BLOBS = {
    "gmi_k4_resource_native_v4.py": "2f425210d1686ba94b22c504e950efb256812acc",
    "gmi_k4_search_v4.py": "1ad45e6a4c180917307131a895b05266b6d05949",
    "gmi_k4_search_v5.py": "90cc1c64ccbe013ccb77ac33eaa358d21e73ea0b",
    "gmi_k4_search.py": "5fcaf3ee8bfef3d7947714b9e560ec7a1071139b",
    "gmi_k4_search_v2.py": "846bd61f736b400af91eba13c1e2287cee6800e4",
    "gmi_k4_null_frontier_v5.py": "32070011e1aa1ab23b3b09bbf941592ebca21021",
}
VECTOR_KEYS = frozenset(("state_scales_with", "serve_scales_with", "update_locality",
                        "routing", "sharing", "retrieval", "serve_iterations",
                        "stochastic_serve", "verifier_gated", "external_authority"))


def load_pinned_model():
    root = Path(__file__).resolve().parent.parent
    for name, expected in SOURCE_BLOBS.items():
        raw = (root / name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if actual != expected:
            raise ValueError(f"SOURCE_DRIFT: re-audit before using class certificate: {name}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return (importlib.import_module("gmi_k4_resource_native_v4"),
            importlib.import_module("gmi_k4_search_v4"),
            importlib.import_module("gmi_k4_search_v2"))


def _validate_target(target, rn):
    if type(target) is not dict or set(target) != VECTOR_KEYS:
        raise ValueError("exact ten-coordinate target required")
    domains = {"routing": rn.ROUTING, "sharing": rn.SHARING, "retrieval": rn.RETRIEVAL,
               "serve_iterations": rn.ITERATIONS, "update_locality": rn.LOCALITY}
    if any(type(target[k]) is not str or target[k] not in values for k, values in domains.items()):
        raise ValueError("target coordinate outside the pinned product domain")
    if any(type(target[k]) is not bool for k in ("stochastic_serve", "verifier_gated", "external_authority")):
        raise ValueError("target boolean coordinates must be actual booleans")
    if any(type(target[k]) is not str for k in ("state_scales_with", "serve_scales_with")):
        raise ValueError("resource labels must be strings")


def target_class_bound(target: dict, *, grammar: str, task: str, scale: int, seed: int) -> dict:
    rn, engine, phase = load_pinned_model()
    _validate_target(target, rn)
    if grammar not in rn.PREFIX or task not in rn.REQUIRED_CAPS:
        raise ValueError("unknown grammar or obligation")
    if type(scale) is not int or scale not in (1, 2, 4, 8) or type(seed) is not int:
        raise ValueError("registered scale and integer development seed required")
    states = tuple(e for e in rn.STATE_LAWS if rn.measure_state_law(e) == target["state_scales_with"])
    serves = tuple(e for e in rn.SERVE_LAWS if rn.measure_serve_law(e) == target["serve_scales_with"])
    profile = phase.world_profile(seed, task, scale)
    best = None
    enumerated = admissible = 0
    # Every sampled candidate has 1..3 distinct sorted CAP_ATOMS, width 1..2,
    # one STATE_LAW, one SERVE_LAW and the five categorical/three bool factors.
    # Target equality fixes the latter eight fields. No cap subset is pruned.
    for count in (1, 2, 3):
        for atoms, state, serve, width in product(combinations(rn.CAP_ATOMS, count), states, serves, (1, 2)):
            cand = rn.Candidate(grammar, state, serve, atoms, target["routing"], target["sharing"],
                                target["retrieval"], target["serve_iterations"], target["stochastic_serve"],
                                target["verifier_gated"], target["external_authority"], target["update_locality"], width)
            if cand.vector() != target:
                raise AssertionError("enumerator violated target membership")
            enumerated += 1
            score = engine._semantic(cand, task, scale, False, profile)
            if score >= engine.THRESHOLD:
                admissible += 1
                total = engine._scalar(rn.lifecycle(cand, scale, profile))
                row = (total, len(cand.tokens()), cand.cid)
                if best is None or row < best[0]:
                    best = (row, cand, score)
    # V5 adds six typed inert-null realizations with a distinct cost rule.
    # Include matching nulls in the TARGET class too; otherwise the lower bound
    # would silently omit potentially cheaper target members.
    nulls = importlib.import_module("gmi_k4_null_frontier_v5")
    null_enumerated = null_admissible = 0
    best_kind = "sampled_product" if best is not None else None
    for null_id, cand in nulls.null_candidates(grammar).items():
        if cand.vector() != target:
            continue
        null_enumerated += 1
        score = engine._semantic(cand, task, scale, False, profile)
        if score >= engine.THRESHOLD:
            null_admissible += 1
            total = sum(float(v) for v in nulls.null_cost(cand, scale, profile).values())
            row = (total, len(cand.tokens()), cand.cid)
            if best is None or row < best[0]:
                best = (row, cand, score)
                best_kind = "registered_null:" + null_id
    domain = {"source_blobs": SOURCE_BLOBS, "target": target, "grammar": grammar,
              "task": task, "scale": scale, "seed": seed, "world_profile": profile}
    return {"schema": "GMIK4FiniteSurrogateTargetClassBoundV1",
            "domain_sha256": hashlib.sha256(json.dumps(domain, sort_keys=True).encode()).hexdigest(),
            "source_blobs": dict(SOURCE_BLOBS), "target": dict(target), "grammar": grammar,
            "task": task, "scale": scale, "seed": seed, "world_profile": profile,
            "enumerated_candidates": enumerated, "admissible_candidates": admissible,
            "matching_nulls_enumerated": null_enumerated, "matching_nulls_admissible": null_admissible,
            "minimizer_kind": best_kind,
            "domain_kind": "V4_FACTOR_PRODUCT_UNION_V5_TYPED_NULL_REALIZATIONS",
            "target_minimum": None if best is None else best[0][0],
            "minimizer_id": None if best is None else best[1].cid,
            "minimizer_serial": None if best is None else best[1].serial(),
            "exhaustive_product_domain": True,
            "numeric_scope": "EXACT_MINIMUM_OF_PINNED_PYTHON_FLOAT_SCORER_NOT_REAL_COST_ARITHMETIC",
            "real_machine_realization_established": False,
            "protected_evidence": False}


def compare_rival(rival, target: dict, *, task: str, scale: int, seed: int,
                  registered_null_id: str | None = None) -> dict:
    rn, engine, phase = load_pinned_model()
    if type(rival) is not rn.Candidate:
        raise ValueError("rival must be a concrete candidate of the pinned module")
    _validate_target(rival.vector(), rn)
    nulls = importlib.import_module("gmi_k4_null_frontier_v5")
    if registered_null_id is not None:
        if (type(registered_null_id) is not str or rival.grammar not in rn.PREFIX
                or nulls.null_candidates(rival.grammar).get(registered_null_id) != rival):
            raise ValueError("null discount requires the exact registered null realization")
    elif (rival.grammar not in rn.PREFIX or rival.state_expr not in rn.STATE_LAWS
            or rival.serve_expr not in rn.SERVE_LAWS or type(rival.cap_atoms) is not tuple
            or any(type(a) is not str or a not in rn.CAP_ATOMS for a in rival.cap_atoms)
            or tuple(sorted(set(rival.cap_atoms))) != rival.cap_atoms
            or not 1 <= len(rival.cap_atoms) <= 3 or type(rival.width_knob) is not int
            or rival.width_knob not in (1, 2)):
        raise ValueError("rival is outside pinned sampler product domain")
    bound = target_class_bound(target, grammar=rival.grammar, task=task, scale=scale, seed=seed)
    score = engine._semantic(rival, task, scale, False, bound["world_profile"])
    cost = (engine._scalar(rn.lifecycle(rival, scale, bound["world_profile"]))
            if registered_null_id is None else
            sum(float(v) for v in nulls.null_cost(rival, scale, bound["world_profile"]).values()))
    minimum = bound["target_minimum"]
    verdict = ("RIVAL_INADMISSIBLE" if score < engine.THRESHOLD else
               "RIVAL_IS_TARGET_CLASS_MEMBER" if rival.vector() == target else
               "TARGET_CLASS_EMPTY" if minimum is None else
               "SURROGATE_TARGET_CLASS_STRICTLY_DOMINATED" if cost + 1e-12 < minimum else
               "NO_STRICT_SURROGATE_CLASS_DOMINANCE")
    return {"schema": "GMIK4SurrogateClassComparisonV1", "verdict": verdict,
            "class_bound": bound, "rival_id": rival.cid, "registered_null_id": registered_null_id,
            "rival_semantic_score": score,
            "rival_lifecycle_cost": cost, "real_machine_realization_established": False,
            "protected_evidence": False, "full_GMI_closure": False}


def regression_probe() -> dict:
    rn, engine, phase = load_pinned_model()
    target = {"state_scales_with": "n_features", "serve_scales_with": "n_features",
              "update_locality": "global", "routing": "none", "sharing": "shared",
              "retrieval": "none", "serve_iterations": "one", "stochastic_serve": False,
              "verifier_gated": False, "external_authority": False}
    w = rn.witness_from_target("G1_TENSOR_GRAPH", target, "linear")
    t = replace(w, cap_atoms=("affine", "low_rank_revision"))
    n = replace(t, verifier_gated=True)
    profile = phase.world_profile(17, "linear", 8)
    costs = [engine._scalar(rn.lifecycle(c, 8, profile)) for c in (w, t, n)]
    assert t.vector() == w.vector() and n.vector() != target
    assert all(engine._semantic(c, "linear", 8, False, profile) == 1.0 for c in (w, t, n))
    assert costs[1] < costs[2] < costs[0]
    comparison = compare_rival(n, target, task="linear", scale=8, seed=17)
    assert comparison["verdict"] == "NO_STRICT_SURROGATE_CLASS_DOMINANCE"
    assert comparison["class_bound"]["target_minimum"] <= costs[1]
    recall = replace(w, state_expr=rn.C(1), serve_expr=rn.C(1), cap_atoms=("volatile_records",),
                     retrieval="exact_key", sharing="unshared", update_locality="local")
    recall_rows = []
    for scale in (1, 2, 4, 8):
        score = engine._semantic(recall, "recall", scale, False, phase.world_profile(17, "recall", scale))
        counts = rn.resource_counts(recall, scale)
        assert score == 1.0 and counts == (1, 1)
        recall_rows.append({"scale": scale, "surrogate_score": score, "declared_counts": counts})
    return {"actual_legacy_modules_executed": True, "development_seed": 17,
            "witness_same_target_rival_costs": costs, "corrected_comparison": comparison,
            "capability_resource_gap_still_open": recall_rows, "protected_evidence": False}


if __name__ == "__main__":
    print(json.dumps(regression_probe(), indent=2))
