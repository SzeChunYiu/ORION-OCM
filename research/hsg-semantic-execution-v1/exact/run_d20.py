"""D20 entry point. Emits results/D20_RESULTS.json + receipts/D20_receipts.jsonl.

Run from research/hsg-semantic-execution-v1/ : python3 -m exact.run_d20
Exit 0 ceiling held, every hostile flipped, every clean control silent.
Exit 4 a hostile failed to flip.
Exit 5 a clean control raised a false alarm.
Exit 6 the n-k ceiling was violated or a conclusive arm disagreed with the
       exhaustive concrete ground truth.
"""
from __future__ import annotations

import json
import os
import sys

from exact.d20 import run_d20

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    out, rec = run_d20()
    with open(os.path.join(RESULTS, "D20_RESULTS.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(os.path.join(RECEIPTS, "D20_receipts.jsonl"), "w",
              encoding="utf-8") as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

    pe, se = out["primary_endpoint"], out["secondary_endpoints"]
    print("D20 verdict:", out["verdict"])
    print("  PRIMARY  ceiling held on %d/%d worlds; violations=%s"
          % (pe["worlds"] - len(pe["ceiling_violations"]), pe["worlds"],
             pe["ceiling_violations"] or "none"))
    print("           conclusive-arm mismatches vs direct:",
          pe["conclusive_verdict_mismatches_vs_direct"] or "none")
    print("  SECONDARY cegar/direct ops = %s  fixed/direct = %s"
          % (se["cegar_ops_over_direct"], se["fixed_ops_over_direct"]))
    for n in sorted(se["per_n"], key=int):
        d = se["per_n"][n]
        print("    n=%-3s ceiling=%-2d max_rounds=%-2d headroom=%-2d "
              "spurious_worlds=%d cegar/direct=%s"
              % (n, d["ceiling"], d["rounds_max"], d["ceiling_headroom"],
                 d["spurious_worlds"], d["cegar_ops_over_direct"]))
    for h in out["hostiles"]:
        print("  %-8s flipped=%-5s control_silent=%s"
              % (h["id"], h["flipped"], h["clean_control_silent"]))
    if out["negative_finding"]:
        print("  NEGATIVE:", out["negative_finding"]["verdict"], "--",
              out["negative_finding"]["statement"])
    print("  wall_s", out["wall_s"], "cpu_s", out["cpu_s"])

    if not all(h["clean_control_silent"] for h in out["hostiles"]):
        return 5
    if pe["ceiling_violations"] or pe["conclusive_verdict_mismatches_vs_direct"]:
        return 6
    if not all(h["flipped"] for h in out["hostiles"]):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
