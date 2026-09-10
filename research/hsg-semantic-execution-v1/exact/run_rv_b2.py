"""RV-B2 entry point. Emits results/RV_B2_RESULTS.json + receipts/RV_B2_receipts.jsonl.

Run from research/hsg-semantic-execution-v1/ : python3 -m exact.run_rv_b2
Exit 0 = targeting comparison complete and the repaired T72 oracle still passes.
Exit 8 = the oracle repair REGRESSED the D17 tranche (fix is wrong, revert it).
"""
from __future__ import annotations

import json
import os
import sys

from exact.rv_b2 import run_rv_b2

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "receipts"), exist_ok=True)
    out, rec = run_rv_b2()
    with open(os.path.join(HERE, "results", "RV_B2_RESULTS.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(os.path.join(HERE, "receipts", "RV_B2_receipts.jsonl"), "w",
              encoding="utf-8") as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

    e = out["endpoints_under_both_targetings"]
    mq = out["margin_question"]
    print("RV-B2 verdict:", out["verdict"])
    print("  PREMISE  D19 already revoked over true sources; the defect was in the T72 oracle.")
    for name in ("control_true_sources", "control_legacy_leaves",
                 "ow4n_true_sources", "ow4n_legacy_leaves"):
        d = e[name]
        print("  %-22s subsets=%-4d accepted=%-8s reopened=%-8s ratio=%-7s rescues=%d"
              % (name, d["revocation_subsets_exhausted"],
                 d["accepted_set_agreement"], d["reopened_set_agreement"],
                 d["lifecycle_ratio_a2_over_a1"], d["alt_support_rescues"]))
    print("  MARGIN   saving true_sources=%s legacy_leaves=%s | band %s | sensitive=%s"
          % (mq["saving_true_sources"], mq["saving_legacy_leaves"],
             out["decision_rule_frozen_before_the_number_was_seen"]["band"],
             mq["targeting_sensitive"]))
    print("           ", mq["conclusion"])
    o = out["oracle_fix"]
    print("  ORACLE   before: %s targets=%d verdict=%s"
          % (o["before_fix"]["detail"], o["before_fix"]["revocation_target_count"],
             o["before_fix"]["verdict"]))
    print("           after : %s targets=%d verdict=%s"
          % (o["after_fix"]["detail"], o["after_fix"]["revocation_target_count"],
             o["after_fix"]["verdict"]))
    print("           pass unchanged=%s | hostile flips unchanged=%s"
          % (o["pass_unchanged"], o["hostile_flips_unchanged"]))
    print("  wall_s", out["wall_s"], "cpu_s", out["cpu_s"])

    if not out["oracle_fix"]["after_fix"]["pass"]:
        return 8
    return 0


if __name__ == "__main__":
    sys.exit(main())
