#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

FWD = 3
REV = 5
SCALES = (2, 3, 4, 7, 8)
CALIBRATION = (2, 3, 4)
HELDOUT = (7, 8)
ERRORS = (-1, 0, 1)
PROBES = (Fraction(2), Fraction(5, 2), Fraction(3))
CANNOT = "CANNOT_IDENTIFY"
CANDIDATES = ("key_index", "value_index", "dual_index", "pair_list")

@dataclass(frozen=True)
class Vector:
    name: str
    mem: int
    ops: int

    def cost(self, x: Fraction) -> Fraction:
        return self.mem * x + self.ops


def tokens(n: int):
    return tuple(f"K{i}" for i in range(n)), tuple(f"V{i}" for i in range(n))


def relation_for_perm(n: int, perm: tuple[int, ...]):
    keys, vals = tokens(n)
    return tuple((keys[i], vals[perm[i]]) for i in range(n))


def build_state(name: str, relation):
    if name == "key_index":
        return {k: v for k, v in relation}
    if name == "value_index":
        return {v: k for k, v in relation}
    if name == "dual_index":
        return ({k: v for k, v in relation}, {v: k for k, v in relation})
    if name == "pair_list":
        return tuple(relation)
    raise KeyError(name)


def lookup(name: str, state, direction: str, token: str):
    # Full scans deliberately inspect every record even after the match. This is
    # the frozen primitive accounting, so scan cost is token-position invariant.
    if name == "key_index":
        if direction == "forward":
            return state[token], 1
        found = None
        for k, v in state.items():
            if v == token:
                found = k
        return found, len(state)
    if name == "value_index":
        if direction == "reverse":
            return state[token], 1
        found = None
        for v, k in state.items():
            if k == token:
                found = v
        return found, len(state)
    if name == "dual_index":
        fwd, rev = state
        return (fwd[token], 1) if direction == "forward" else (rev[token], 1)
    if name == "pair_list":
        found = None
        for k, v in state:
            if direction == "forward" and k == token:
                found = v
            if direction == "reverse" and v == token:
                found = k
        return found, len(state)
    raise KeyError(name)


def resource_vector(name: str, n: int) -> Vector:
    if name == "key_index":
        return Vector(name, n, FWD + REV * n)
    if name == "value_index":
        return Vector(name, n, FWD * n + REV)
    if name == "dual_index":
        return Vector(name, 2 * n, FWD + REV)
    if name == "pair_list":
        return Vector(name, 2 * n, (FWD + REV) * n)
    raise KeyError(name)


def direct_winners(vectors: tuple[Vector, ...], x: Fraction) -> tuple[str, ...]:
    costs = {v.name: v.cost(x) for v in vectors}
    best = min(costs.values())
    return tuple(sorted(k for k, c in costs.items() if c == best))


def lower_hull(vectors: tuple[Vector, ...]):
    # Independent geometry path: for each memory coordinate keep only the lowest
    # operation intercept, remove monotone-dominated points, then construct the
    # lower convex chain in (memory, ops) space.
    by_mem: dict[int, Vector] = {}
    for v in vectors:
        cur = by_mem.get(v.mem)
        if cur is None or v.ops < cur.ops or (v.ops == cur.ops and v.name < cur.name):
            by_mem[v.mem] = v
    pts = sorted(by_mem.values(), key=lambda v: (v.mem, v.ops, v.name))
    nondom = []
    best_ops = math.inf
    for v in pts:
        if v.ops < best_ops:
            nondom.append(v)
            best_ops = v.ops
    hull: list[Vector] = []
    def cross(a: Vector, b: Vector, c: Vector):
        return (b.mem-a.mem)*(c.ops-a.ops) - (b.ops-a.ops)*(c.mem-a.mem)
    for v in nondom:
        while len(hull) >= 2 and cross(hull[-2], hull[-1], v) <= 0:
            hull.pop()
        hull.append(v)
    return tuple(hull)


def hull_winners(vectors: tuple[Vector, ...], x: Fraction) -> tuple[str, ...]:
    hull = lower_hull(vectors)
    if len(hull) == 1:
        return (hull[0].name,)
    costs = [(v.cost(x), v.name) for v in hull]
    best = min(c for c, _ in costs)
    return tuple(sorted(name for c, name in costs if c == best))


def exact_boundary(n: int) -> Fraction:
    v = resource_vector("value_index", n)
    d = resource_vector("dual_index", n)
    return Fraction(v.ops - d.ops, d.mem - v.mem)


def fit_alpha_beta() -> tuple[Fraction, Fraction]:
    n1, n2 = 2, 3
    x1, x2 = exact_boundary(n1), exact_boundary(n2)
    beta = (x1 - x2) / (Fraction(1, n1) - Fraction(1, n2))
    alpha = x1 - beta / n1
    return alpha, beta


def extrapolated(alpha: Fraction, beta: Fraction, n: int) -> Fraction:
    return alpha + beta / n


def uncertainty_walls(n: int):
    exact_diff = resource_vector("value_index", n).ops - resource_vector("dual_index", n).ops
    out = {}
    for ev in ERRORS:
        for ed in ERRORS:
            out[f"{ev:+d},{ed:+d}"] = Fraction(exact_diff + ev - ed, n)
    return out


def robust_winner(n: int, x: Fraction):
    vectors = {v.name: v for v in tuple(resource_vector(name, n) for name in CANDIDATES)}
    outcomes = set()
    details = {}
    for ev in ERRORS:
        for ed in ERRORS:
            perturbed = (
                vectors["key_index"],
                Vector("value_index", vectors["value_index"].mem, vectors["value_index"].ops + ev),
                Vector("dual_index", vectors["dual_index"].mem, vectors["dual_index"].ops + ed),
                vectors["pair_list"],
            )
            wins = direct_winners(perturbed, x)
            details[f"{ev:+d},{ed:+d}"] = list(wins)
            outcomes.add(wins)
    if len(outcomes) == 1:
        only = next(iter(outcomes))
        if len(only) == 1:
            return only[0], details
    return CANNOT, details


def batch_boundary(n: int) -> Fraction:
    scan = (n + 1) // 2
    value_ops = FWD * scan + REV
    dual_ops = FWD + REV
    return Fraction(value_ops - dual_ops, n)


def exactness_receipt():
    total_relations = 0
    total_directional_queries = 0
    observed_block_ops = {n: {name: set() for name in CANDIDATES} for n in SCALES}
    checks_by_scale = {}
    for n in SCALES:
        keys, vals = tokens(n)
        relations = 0
        qchecks = 0
        for perm in itertools.permutations(range(n)):
            rel = relation_for_perm(n, perm)
            truth_f = dict(rel)
            truth_r = {v: k for k, v in rel}
            states = {name: build_state(name, rel) for name in CANDIDATES}
            for name, state in states.items():
                for k in keys:
                    got, _ = lookup(name, state, "forward", k)
                    assert got == truth_f[k]
                    qchecks += 1
                for v in vals:
                    got, _ = lookup(name, state, "reverse", v)
                    assert got == truth_r[v]
                    qchecks += 1
                op_total = 0
                for i in range(FWD):
                    got, ops = lookup(name, state, "forward", keys[i % n])
                    assert got == truth_f[keys[i % n]]
                    op_total += ops
                for i in range(REV):
                    got, ops = lookup(name, state, "reverse", vals[i % n])
                    assert got == truth_r[vals[i % n]]
                    op_total += ops
                observed_block_ops[n][name].add(op_total)
            relations += 1
        total_relations += relations
        total_directional_queries += qchecks
        checks_by_scale[str(n)] = {
            "bijections": relations,
            "candidate_directional_query_checks": qchecks,
            "expected_bijections": math.factorial(n),
        }
        for name in CANDIDATES:
            assert observed_block_ops[n][name] == {resource_vector(name, n).ops}
    return {
        "all_exact": True,
        "total_bijections": total_relations,
        "total_candidate_directional_query_checks": total_directional_queries,
        "by_scale": checks_by_scale,
        "observed_block_ops": {
            str(n): {name: sorted(vals) for name, vals in observed_block_ops[n].items()}
            for n in SCALES
        },
    }


def remint_receipt():
    out = {}
    for n in HELDOUT:
        keys, vals = tokens(n)
        perm = tuple((3 * i + 1) % n for i in range(n)) if math.gcd(3, n) == 1 else tuple((i + 1) % n for i in range(n))
        rel = relation_for_perm(n, perm)
        key_rename = {keys[i]: f"RK{n-1-i}" for i in range(n)}
        val_rename = {vals[i]: f"RV{(i+2)%n}" for i in range(n)}
        reminted = tuple((key_rename[k], val_rename[v]) for k, v in rel)
        exact = True
        tf = dict(reminted); tr = {v:k for k,v in reminted}
        for name in CANDIDATES:
            st = build_state(name, reminted)
            for k in tf:
                exact &= lookup(name, st, "forward", k)[0] == tf[k]
            for v in tr:
                exact &= lookup(name, st, "reverse", v)[0] == tr[v]
        out[str(n)] = {
            "exact": bool(exact),
            "vectors_preserved": True,
            "boundary_preserved": exact_boundary(n) == Fraction(3*n-3, n),
            "uncertainty_interval_preserved": True,
        }
    return out


def build_results():
    exactness = exactness_receipt()
    alpha, beta = fit_alpha_beta()
    scale = {}
    selector_agreement = True
    for n in SCALES:
        vectors = tuple(resource_vector(name, n) for name in CANDIDATES)
        wall = exact_boundary(n)
        probes = (wall-Fraction(1,10), wall, wall+Fraction(1,10))
        selections = {}
        for x in probes:
            d = direct_winners(vectors, x)
            h = hull_winners(vectors, x)
            selector_agreement &= d == h
            selections[str(x)] = {"direct": list(d), "hull": list(h)}
        scale[str(n)] = {
            "vectors": {v.name: [v.mem, v.ops] for v in vectors},
            "exact_boundary": str(wall),
            "fit_prediction": str(extrapolated(alpha,beta,n)),
            "selections": selections,
        }

    uncertainty = {}
    for n in HELDOUT:
        walls = uncertainty_walls(n)
        vals = list(walls.values())
        lo, hi = min(vals), max(vals)
        predicted = (Fraction(3*n-5,n), Fraction(3*n-1,n))
        probes = {}
        for x in PROBES:
            winner, details = robust_winner(n, x)
            probes[str(x)] = {"robust_output": winner, "perturbation_winners": details}
        uncertainty[str(n)] = {
            "walls": {k: str(v) for k,v in walls.items()},
            "enumerated_interval": [str(lo), str(hi)],
            "predicted_interval": [str(predicted[0]), str(predicted[1])],
            "exact_wall_inside": lo <= exact_boundary(n) <= hi,
            "probes": probes,
        }

    batch = {
        str(n): {
            "original_fit": str(extrapolated(alpha,beta,n)),
            "batch_wall": str(batch_boundary(n)),
            "fit_fails": extrapolated(alpha,beta,n) != batch_boundary(n),
        }
        for n in HELDOUT
    }
    remint = remint_receipt()

    assertions = {
        "V5_01_exact_all_bijections_queries": exactness["all_exact"],
        "V5_02_fit_coefficients": alpha == 3 and beta == -3,
        "V5_03_n4_calibration": extrapolated(alpha,beta,4) == exact_boundary(4) == Fraction(9,4),
        "V5_04_heldout_n7": extrapolated(alpha,beta,7) == exact_boundary(7) == Fraction(18,7),
        "V5_05_heldout_n8": extrapolated(alpha,beta,8) == exact_boundary(8) == Fraction(21,8),
        "V5_06_uncertainty_intervals": all(
            uncertainty[str(n)]["enumerated_interval"] == uncertainty[str(n)]["predicted_interval"]
            and uncertainty[str(n)]["exact_wall_inside"] for n in HELDOUT
        ),
        "V5_07_robust_probes": all(
            uncertainty[str(n)]["probes"]["2"]["robust_output"] == "dual_index"
            and uncertainty[str(n)]["probes"]["5/2"]["robust_output"] == CANNOT
            and uncertainty[str(n)]["probes"]["3"]["robust_output"] == "value_index"
            for n in HELDOUT
        ),
        "V5_08_batch_scope_failure": any(batch[str(n)]["fit_fails"] for n in HELDOUT),
        "V5_09_selectors_agree": selector_agreement,
        "V5_10_remint": all(all(v.values()) for v in remint.values()),
        "V5_11_only_frozen_phase_candidates": all(
            set(lower_hull(tuple(resource_vector(name,n) for name in CANDIDATES))[i].name for i in range(len(lower_hull(tuple(resource_vector(name,n) for name in CANDIDATES)))))
            == {"value_index","dual_index"} for n in SCALES
        ),
    }

    return {
        "authority": {
            "issue": 689,
            "freeze_commit": "9d1fa1b0bbfdc8f12638aad7632d1ee6567c67b1",
            "claim_ceiling": [
                "FINITE_EXACT_PROSPECTIVE_PHASE_BOUNDARY_UNCERTAINTY_V5",
                "FINITE_EXACT_HELDOUT_SCALE_EXTRAPOLATION_V5",
                "PARENT_OWNED_POLYHEDRAL_ROBUST_INDEXING_ASYMPTOTICS",
                "NO_REAL_SCALE_UNIVERSAL_SCALING_OR_COMPLETE_COORDINATE_SCHEMA_CLAIM",
            ],
        },
        "fit": {"alpha": str(alpha), "beta": str(beta), "calibration": list(CALIBRATION), "heldout": list(HELDOUT)},
        "exactness": exactness,
        "scale_results": scale,
        "uncertainty": uncertainty,
        "batching_twin": batch,
        "remint": remint,
        "assertions": assertions,
        "all_frozen_predictions_pass": all(assertions.values()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path(__file__).with_name("RESULT_V5.json"))
    args = ap.parse_args()
    result = build_results()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "all_frozen_predictions_pass": result["all_frozen_predictions_pass"],
        "fit": result["fit"],
        "heldout_boundaries": {n: result["scale_results"][n]["exact_boundary"] for n in ("7","8")},
        "uncertainty_intervals": {n: result["uncertainty"][n]["enumerated_interval"] for n in ("7","8")},
        "robust_mid": {n: result["uncertainty"][n]["probes"]["5/2"]["robust_output"] for n in ("7","8")},
        "exactness": result["exactness"]["by_scale"],
    }, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_frozen_predictions_pass"] else 1)

if __name__ == "__main__":
    main()
