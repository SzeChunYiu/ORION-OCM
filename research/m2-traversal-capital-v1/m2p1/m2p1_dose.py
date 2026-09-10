#!/usr/bin/env python3
"""M2-P1 development-depth dose-response (#323 section 8).

"A single capability jump is insufficient... test whether future-search burden
improves monotonically or predictably with verified developmental history."

For each frozen depth t, the registered learner is given the FIRST t solved
developmental tasks, mines a generator, and is scored by the registered
validate_generator on the SAME held-out set at every depth.  Held-out tasks never
participate in mining (the learner enforces this itself).

Reports, per depth: fragments mined, strictly-better count, mean baseline vs
candidate slots, and the work reduction -- plus a SHUFFLED control at full depth.
"""
from __future__ import annotations
import argparse, json, random, statistics, sys, time
from fractions import Fraction
from itertools import product
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--depths", default="8,16,32,64,128")
    ap.add_argument("--slots", type=int, default=200000)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M
    eco = json.loads(Path(a.ecology).read_text())
    depths = [int(x) for x in a.depths.split(",")]
    budget = M.SearchBudget(slots=a.slots, max_length=8)

    def task(row, i):
        return M.PolynomialTask(f"m2p1:{i}:{row['normal_form_digest'][:16]}",
                                tuple(Fraction(c) for c in row["coefficients"]))

    train_rows = eco["streams"]["train"]
    held = [task(r, 10_000 + i) for i, r in enumerate(eco["streams"]["validation"])]

    # solve developmental tasks once, reuse the prefix at every depth
    solved = []
    for i, row in enumerate(train_rows):
        t = task(row, i)
        res = M.solve(t, budget)
        if M.verify_solution(t, res):
            solved.append((t, res))

    def score(method):
        rep = M.validate_generator(method, held, budget)
        rows = rep["held_out"]
        mb = statistics.fmean(r["baseline"]["slots"] for r in rows)
        mc = statistics.fmean(r["candidate"]["slots"] for r in rows)
        return {"fragments": len(method.fragments), "admitted": rep["accepted"],
                "terminal": rep["terminal"],
                "strictly_better": sum(1 for r in rows if r["candidate"]["slots"] < r["baseline"]["slots"]),
                "worse": sum(1 for r in rows if r["candidate"]["slots"] > r["baseline"]["slots"]),
                "held_out_n": len(rows),
                "mean_baseline_slots": round(mb, 1), "mean_candidate_slots": round(mc, 1),
                "work_reduction": round(1 - mc / mb, 4)}

    curve = {}
    for t in depths:
        if t > len(solved):
            curve[str(t)] = {"skipped": f"only {len(solved)} solved"}
            continue
        curve[str(t)] = score(M.learn_generator(solved[:t]))
        print(f"depth {t}: {json.dumps(curve[str(t)])}", flush=True)

    # SHUFFLED control at full depth: same fragment count and length profile, random content
    full = M.learn_generator(solved[:depths[-1]])
    rng = random.Random(int(eco["frozen_seed"]) + 99)
    pool = [p for L in (2, 3, 4) for p in product(M.PRIMITIVES, repeat=L)]
    pick, seen = [], set()
    for f in full.fragments:
        c = [p for p in pool if len(p) == len(f) and p not in seen]
        if c:
            x = rng.choice(c)
            seen.add(x)
            pick.append(x)
    shuffled = score(M.GeneratorMethod(tuple(pick), full.training_tasks))
    print("shuffled:", json.dumps(shuffled), flush=True)

    # ORACLE calibration: the true hidden motifs
    oracle = score(M.GeneratorMethod(tuple(tuple(m) for m in eco["hidden_motifs"]), ()))
    print("oracle:", json.dumps(oracle), flush=True)

    red = [curve[str(t)]["work_reduction"] for t in depths if "work_reduction" in curve.get(str(t), {})]
    out = {"schema": "OCM_M2P1_DOSE_RESPONSE_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "owner_issue": 165, "hardening_parent": 323,
           "ecology_variant": eco.get("ecology_variant"), "frozen_seed": eco["frozen_seed"],
           "developmental_tasks_solved": len(solved), "depths": depths,
           "curve": curve, "shuffled_control_full_depth": shuffled,
           "oracle_calibration_true_motifs": oracle,
           "monotone_nondecreasing": all(x <= y + 1e-9 for x, y in zip(red, red[1:])),
           "work_reduction_by_depth": red,
           "timing_seconds": round(time.perf_counter() - t0, 2)}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"monotone": out["monotone_nondecreasing"],
                      "curve": red, "shuffled": shuffled["work_reduction"],
                      "oracle": oracle["work_reduction"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
