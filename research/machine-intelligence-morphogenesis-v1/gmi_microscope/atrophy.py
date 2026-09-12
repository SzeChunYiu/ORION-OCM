"""RV-377-071 — morphogenetic atrophy: does the recovered machine CONTAIN a known form, or only a large amount of bulk?

RV-377-057 crossed the admissibility gate (0.8809 and 0.8796 against theta = 0.85) but every one of its 24 winners is
133-209 nodes, against the planted coefficient learner's 47 and the minimal admissible program's 37, and every winner is
classified LOCAL_MEMORY or STORE_PLUS_NUMERIC rather than a coefficient machine. That is the new negative: ADMISSIBILITY
RECOVERY IS NOT FORM RECOVERY.

The diagnosis is that the compact solution is unreachable FROM BELOW (calibration (ii) of RV-377-057: the size-12 plateau
elite is in a closed basin, 0 of 400 single mutations reach 0.85) but may be reachable FROM ABOVE, by deletion. Deletion
is not a post-hoc device: pruning / atrophy is in the biosphere R5 morphogenesis primitive list, alongside the
clone-and-specialize operator the same record used.

Three instruments, all exact and all charged in evaluations:

  A. ATROPHY        greedy subtree deletion under the constraint score >= theta, to a fixed point. Each candidate deletion
                    replaces a subtree by each of the grammar's leaves and by each of its own children, and is accepted
                    only if the exact replayed score stays at or above theta. Deterministic given an ordering.
  B. STORE ABLATION delete every INSERT rule (the store writes) and re-score. If the score stays above theta the store was
                    vestigial and the machine is a coefficient machine that was MISCLASSIFIED by the descriptor, not a
                    hybrid.
  C. RULE ABLATION  delete each update rule in turn and re-score, giving the per-rule contribution, so that 'this machine
                    has three delta rules' is a measurement rather than a reading of the source text.

The comparand is the planted learner (0.9196, 47 nodes) and the greedily simplified minimal admissible program of
RV-377-057 calibration (iii) (0.8547, 37 nodes). Receipt: STAGE_F_ATROPHY_V1.json.
"""
from __future__ import annotations

import json
import os
import sys
import time

from . import blind, qd
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = blind.THETA_SMOOTH
LEAVES = ("x1", "x2", "x3", "c0", "c1", "c2", "c3", "k0", "k1", "kh", "e", "y", "out")


def _score(cand, eco):
    return qd.score_and_desc(cand, eco)[0]


def _subtrees(t, path=()):
    """every (path, subtree) of an expression tree, deepest last."""
    yield path, t
    if isinstance(t, list):
        for i, c in enumerate(t[1:], start=1):
            yield from _subtrees(c, path + (i,))


def _get(t, path):
    for i in path: t = t[i]
    return t


def _set(t, path, new):
    if not path: return new
    t = json.loads(json.dumps(t)); cur = t
    for i in path[:-1]: cur = cur[i]
    cur[path[-1]] = new
    return t


def _size(cand):
    return qd.cand_size(cand)


def atrophy(cand, eco, theta=THETA, max_rounds=8):
    """greedy deletion to a fixed point under score >= theta; returns (machine, trace)."""
    cur = json.loads(json.dumps(cand)); best = _score(cur, eco); evals = 1; trace = []
    for rnd in range(max_rounds):
        improved = False
        # 1. drop whole update rules whose removal does not break admissibility
        for gi in range(len(cur["g"]) - 1, -1, -1):
            trial = json.loads(json.dumps(cur)); del trial["g"][gi]
            s = _score(trial, eco); evals += 1
            if s >= theta:
                trace.append({"round": rnd, "op": "drop_rule", "index": gi, "size_before": _size(cur), "size_after": _size(trial), "score": s})
                cur, best, improved = trial, s, True
        # 2. replace subtrees of f and of every rule body by a smaller term, to a fixed point per target
        for key in ("f", "g"):
            roots = [()] if key == "f" else [(gi, 1) for gi in range(len(cur["g"]))]
            for root in roots:
                while True:
                    tree = _get_root(cur, root)
                    paths = sorted((p for p, t in _subtrees(tree) if isinstance(t, list)), key=len, reverse=True)
                    hit = False
                    for p in paths:
                        sub = _get(tree, p)
                        if not isinstance(sub, list): continue
                        for repl in [c for c in sub[1:] if isinstance(c, (list, str))] + list(LEAVES):
                            trial = _with_root(cur, root, _set(tree, p, repl))
                            if _size(trial) >= _size(cur): continue
                            s = _score(trial, eco); evals += 1
                            if s >= theta:
                                trace.append({"round": rnd, "op": "replace_subtree", "where": key, "score": s,
                                              "size_before": _size(cur), "size_after": _size(trial)})
                                cur, best, improved, hit = trial, s, True, True
                                break
                        if hit: break
                    if not hit: break
        if not improved: break
    return cur, {"final_score": best, "final_size": _size(cur), "evaluations_charged": evals, "rounds": rnd + 1, "n_ops": len(trace)}


def _get_root(cand, root):
    return cand["f"] if root == () else cand["g"][root[0]][1]


def _with_root(cand, root, newroot):
    c = json.loads(json.dumps(cand))
    if root == (): c["f"] = newroot
    else: c["g"][root[0]][1] = newroot
    return c


def store_ablation(cand, eco):
    """delete every INSERT rule; the store becomes unwritten."""
    trial = json.loads(json.dumps(cand))
    n = len(trial["g"])
    trial["g"] = [r for r in trial["g"] if r[0] != "INSERT"]
    return {"n_insert_rules_removed": n - len(trial["g"]), "score_without_store": _score(trial, eco),
            "size_without_store": _size(trial)}


def rule_ablation(cand, eco):
    base = _score(cand, eco); out = []
    for gi in range(len(cand["g"])):
        trial = json.loads(json.dumps(cand)); tc = trial["g"][gi][0]; del trial["g"][gi]
        out.append({"index": gi, "target": tc, "score_without": _score(trial, eco), "delta": round(base - _score(trial, eco), 4)})
    return {"base": base, "per_rule": out}


def main(tag="V1"):
    eco = blind.ecology_div(); t0 = time.time()
    planted = blind.PLANTED_LEARNER_SMOOTH8_LR4
    rows = {}
    for seed in (5, 6):
        f = os.path.join(RES, f"STAGE_F_BLIND_RECOVERY_RUN10_QD_MAPELITES_S{seed}.json")
        if not os.path.exists(f): continue
        r = json.load(open(f))
        for i, e in enumerate(r["top_elites"]):
            if e["score"] < THETA: continue
            cand = {"f": json.loads(e["f"]), "g": json.loads(e["g"])}
            assert abs(_score(cand, eco) - e["score"]) < 1e-9, (seed, i)
            small, info = atrophy(cand, eco)
            rows[f"S{seed}_E{i}"] = {"seed": seed, "elite_index": i, "descriptor": e["descriptor"], "class_before": e["class"],
                                     "size_before": e["size"], "score_before": e["score"], **info,
                                     "store_ablation": store_ablation(small, eco), "rule_ablation": rule_ablation(small, eco),
                                     "atrophied_f": json.dumps(small["f"]), "atrophied_g": json.dumps(small["g"])}
            print(json.dumps({k: v for k, v in rows[f"S{seed}_E{i}"].items() if k not in ("atrophied_f", "atrophied_g", "rule_ablation")}), flush=True)
    sizes = [v["final_size"] for v in rows.values()]
    receipt = {"schema": "StageFMorphogeneticAtrophyV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-071", "run_tag": tag, "theta": THETA,
               "instrument": "greedy subtree deletion to a fixed point under score >= theta (biosphere R5 primitive 'prune / atrophy'), plus store ablation and per-rule ablation; every candidate deletion charged as one exact replay",
               "comparands": {"planted_learner_score": _score(planted, eco), "planted_learner_size": _size(planted),
                              "minimal_admissible_program_size_from_RV057_calibration": 37, "minimal_admissible_program_score_from_RV057_calibration": 0.8547},
               "rows": rows, "n_rows": len(rows),
               "summary": {"min_atrophied_size": min(sizes) if sizes else None, "max_atrophied_size": max(sizes) if sizes else None,
                           "median_atrophied_size": sorted(sizes)[len(sizes) // 2] if sizes else None,
                           "n_at_or_below_60_nodes": sum(1 for s in sizes if s <= 60),
                           "n_store_vestigial": sum(1 for v in rows.values() if v["store_ablation"]["score_without_store"] >= THETA),
                           "n_with_insert_rules": sum(1 for v in rows.values() if v["store_ablation"]["n_insert_rules_removed"] > 0)},
               "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "exact charged replay on one ecology (four sign-flipped smooth targets); atrophy is greedy and deterministic given the stated ordering, so the reported size is an UPPER bound on the smallest admissible machine contained in each elite, not the minimum"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_F_ATROPHY_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("summary:", json.dumps(receipt["summary"]))
    return receipt


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1")
