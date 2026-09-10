"""D19 entry point. Emits results/D19_RESULTS.json + receipts/D19_receipts.jsonl.

Run from research/hsg-semantic-execution-v1/ : python3 -m exact.run_d19
Exit 0 = every hostile flipped AND every clean control stayed silent.
Exit 4 = a hostile failed to flip. Exit 5 = a clean control raised a false alarm.
"""
from __future__ import annotations

import json
import os
import sys

from exact.d19 import run_d19

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")


def main():
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    out, rec = run_d19()
    with open(os.path.join(RESULTS, "D19_RESULTS.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(os.path.join(RECEIPTS, "D19_receipts.jsonl"), "w",
              encoding="utf-8") as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

    pc = out["positive_control"]
    print("D19 verdict:", out["verdict"])
    print("  control OW4  accepted", pc["accepted_set_agreement"],
          "reopened", pc["reopened_set_agreement"],
          "| alt-support rescues", pc["alt_support_rescues"])
    print("  A2/A1 lifecycle op ratio:",
          pc["substitution_vs_recomputation_op_ratio"],
          "(A1 subst", pc["a1_lifecycle_ops"],
          "vs A2 recompute", pc["a2_lifecycle_ops"], ")")
    np_ = out["negation_population"]
    print("  OW4N accepted", np_["accepted_set_agreement"],
          "reopened", np_["reopened_set_agreement"], "->", np_["terminal"])
    for h in out["hostiles"]:
        print("  %-8s flipped=%s control_silent=%s" %
              (h["id"], h["flipped"], h["clean_control_silent"]))
    print("  wall_s", out["wall_s"], "cpu_s", out["cpu_s"])

    if not all(h["clean_control_silent"] for h in out["hostiles"]):
        return 5
    if not all(h["flipped"] for h in out["hostiles"]):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
