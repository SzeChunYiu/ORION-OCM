"""RV-B1 entry point. Emits results/RV_B1_RESULTS.json + receipts/RV_B1_receipts.jsonl.

Run from research/hsg-semantic-execution-v1/ : python3 -m exact.run_rv_b1
Exit 0 lever valid (equivalence guard silent, ceiling held, verdicts match).
Exit 7 equivalence guard FAILED -- the incremental abstraction diverged from a
       from-scratch rebuild. A defect in the lever, never a finding.
Exit 6 ceiling violated or a conclusive arm disagreed with ground truth.
"""
from __future__ import annotations

import json
import os
import sys

from exact.rv_b1 import run_rv_b1

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "receipts"), exist_ok=True)
    out, rec = run_rv_b1()
    with open(os.path.join(HERE, "results", "RV_B1_RESULTS.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(os.path.join(HERE, "receipts", "RV_B1_receipts.jsonl"), "w",
              encoding="utf-8") as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

    lv, pe, sq, lb = (out["lever"], out["preserved_endpoints"],
                      out["single_query"], out["lower_bound"])
    mq = out["multi_query_amortisation"]
    print("RV-B1 verdict:", out["verdict"])
    print("  LEVER   incremental/rebuild = %s  (construction overhead removed %s%%)"
          % (lv["incremental_over_rebuild"],
             lv["construction_overhead_removed_pct"]))
    print("          equivalence guard: %d checks, %d failures | rounds identical to rebuild: %s"
          % (lv["equivalence_guard_checks"], lv["equivalence_guard_failures"],
             lv["rounds_identical_to_rebuild_on_all_worlds"]))
    print("  PRESERVED ceiling violations %s | verdict mismatches %s"
          % (pe["ceiling_violations"] or "none",
             pe["conclusive_verdict_mismatches"] or "none"))
    print("  SINGLE  rebuild/direct = %s   incremental/direct = %s   worlds saved = %d"
          % (sq["rebuild_over_direct"], sq["incremental_over_direct"],
             sq["worlds_where_incremental_saved_search"]))
    ec = lb["empirical_companion"]
    print("  BOUND   build-alone/direct = %s ; build alone >= entire direct search on %d/%d worlds"
          % (ec["build_only_over_direct"],
             ec["worlds_where_build_alone_ge_entire_direct_search"],
             ec["worlds_total"]))
    cv = out["cost_ratio_curve_across_grid"]
    cs = cv["summary"]
    print("  CURVE   cost ratio across the frozen grid (RV-1 deliverable)")
    print("            n     rebuild/direct  incremental/direct  lever gain  validation share")
    for n in [str(x) for x in cs["n_grid"]]:
        c = cv["per_n"][n]
        print("            %-4s  %-14s  %-18s  %-10s  %s"
              % (n, c["rebuild_over_direct"], c["incremental_over_direct"],
                 c["lever_gain_vs_rebuild"], c["validation_share"]))
    print("            growth across grid: rebuild x%s -> incremental x%s | flattens=%s"
          % (cs["rebuild_growth_factor_across_grid"],
             cs["incremental_growth_factor_across_grid"],
             cs["lever_flattens_the_curve"]))
    print("            incremental plateaued=%s %s | rebuild still climbing=%s %s | crosses 1.0 anywhere=%s"
          % (cs["plateau"]["incremental_plateaued"], cs["plateau"]["last_two_incremental"],
             cs["plateau"]["rebuild_still_climbing"], cs["plateau"]["last_two_rebuild"],
             cs["crosses_one_anywhere"]))
    print("  AMORT   crossover Q =", mq["crossover_Q"])
    for q in mq["q_grid_preregistered"]:
        d = mq["per_q"][str(q)]
        print("            Q=%-3d direct=%-7d incremental=%-7d ratio=%-6s wins=%s"
              % (q, d["direct_ops"], d["incremental_ops"],
                 d["ratio_inc_over_direct"], d["incremental_wins"]))
    print("          ceiling held across queries on %d/%d worlds; verdicts match on %d/%d"
          % (mq["ceiling_held_across_queries_worlds"], len(out["per_world"]),
             mq["verdicts_match_direct_worlds"], len(out["per_world"])))
    t = out["terminal"]
    print("  TERMINAL", t["verdict"], "(%s)" % t["class"])
    print("            ", t["statement"])
    print("  wall_s", out["wall_s"], "cpu_s", out["cpu_s"])

    if lv["equivalence_guard_failures"]:
        return 7
    if pe["ceiling_violations"] or pe["conclusive_verdict_mismatches"]:
        return 6
    return 0


if __name__ == "__main__":
    sys.exit(main())
