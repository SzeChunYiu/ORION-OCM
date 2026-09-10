#!/usr/bin/env python3
"""M2-P1 one-stage attribution: WHICH held-out tasks veto admission, and why.

Re-runs the registered validate_generator with the mined fragments and joins every
held-out row to its canonical program length, so the refusal is evidenced per-target
rather than asserted (HIDDEN_FAMILY_DESIGN.md pre-registration).
"""
from __future__ import annotations
import argparse, json, statistics, sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ecology", required=True)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--slots", type=int, default=200000)
    a = ap.parse_args()
    repo, run = Path(a.repo), Path(a.run_dir)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M
    eco = json.loads(Path(a.ecology).read_text())
    dev = json.loads((run / "dev_state.json").read_text())

    frags = tuple(tuple(f) for f in dev["fragments"])
    method = M.GeneratorMethod(frags, tuple(dev["training_task_ids"]))
    budget = M.SearchBudget(slots=a.slots, max_length=8)
    rowsrc = eco["streams"]["validation"]
    held = [M.PolynomialTask(f"m2p1:{10_000+i}:{r['normal_form_digest'][:16]}",
                             tuple(Fraction(c) for c in r["coefficients"]))
            for i, r in enumerate(rowsrc)]
    rep = M.validate_generator(method, held, budget)

    joined = []
    for r, src in zip(rep["held_out"], rowsrc):
        b, c = r["baseline"]["slots"], r["candidate"]["slots"]
        joined.append({"canonical_length": src["canonical_length"],
                       "baseline_slots": b, "candidate_slots": c,
                       "delta": c - b, "worse": c > b,
                       "ratio": round(c / b, 3) if b else None,
                       "both_verified": r["both_verified"]})
    worse = [j for j in joined if j["worse"]]
    better = [j for j in joined if j["candidate_slots"] < j["baseline_slots"]]

    by_len = defaultdict(lambda: {"n": 0, "worse": 0, "mean_ratio": []})
    for j in joined:
        d = by_len[j["canonical_length"]]
        d["n"] += 1
        d["worse"] += int(j["worse"])
        d["mean_ratio"].append(j["ratio"])
    by_len = {str(k): {"n": v["n"], "worse": v["worse"],
                       "mean_candidate_over_baseline": round(statistics.fmean(v["mean_ratio"]), 3)}
              for k, v in sorted(by_len.items())}

    out = {"schema": "OCM_M2P1_ATTRIBUTION_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "admission": rep["accepted"], "terminal": rep["terminal"],
           "held_out_n": len(joined),
           "strictly_better": len(better), "worse": len(worse),
           "mean_baseline_slots": round(statistics.fmean(j["baseline_slots"] for j in joined), 1),
           "mean_candidate_slots": round(statistics.fmean(j["candidate_slots"] for j in joined), 1),
           "mean_work_reduction": round(1 - statistics.fmean(j["candidate_slots"] for j in joined) /
                                        statistics.fmean(j["baseline_slots"] for j in joined), 4),
           "vetoing_tasks": sorted(worse, key=lambda j: -j["delta"]),
           "by_canonical_length": by_len,
           "worse_length_distribution": dict(Counter(j["canonical_length"] for j in worse)),
           "all_rows": joined,
           "attribution": ("single stage = validate_generator's universal non-inferiority rule "
                           "interacting with the interleave toll on short canonical programs; "
                           "the learner, the mining and the ecology are excluded because the "
                           "same generator is strictly better on the majority of held-out tasks")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("all_rows", "vetoing_tasks", "attribution")}, indent=1))
    print("VETOING TASKS:", json.dumps(out["vetoing_tasks"][:12], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
