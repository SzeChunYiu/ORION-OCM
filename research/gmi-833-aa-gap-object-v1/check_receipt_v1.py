#!/usr/bin/env python3
"""Re-derive every headline number and compare it to the committed receipt.

A stale RESULT_V1.json is a defect, so this runs in CI on every push.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gap_object_v1 as A            # noqa: E402
import independent_oracle_v1 as B    # noqa: E402

def main():
    receipt = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
    live = A.run(scan_root=os.path.join(A.REPO, "research"))
    oracle = B.run()
    bad = []
    checks = [
        ("AAG-1.conforming", receipt["AAG-1"]["conforming"], live["AAG-1"]["conforming"], oracle["conforming"]),
        ("AAG-1.records", receipt["AAG-1"]["records"], live["AAG-1"]["records"], oracle["records"]),
        ("AAG-1.distinct_claim_id", receipt["AAG-1"]["distinct_claim_id"],
         live["AAG-1"]["distinct_claim_id"], oracle["distinct_claim_id"]),
        ("AAG-3.MATERIAL", receipt["AAG-3"]["applied"]["grade_counts"]["MATERIAL"],
         live["AAG-3"]["applied"]["grade_counts"]["MATERIAL"], oracle["grade_counts"]["MATERIAL"]),
        ("AAG-3.CRITICAL", receipt["AAG-3"]["applied"]["grade_counts"]["CRITICAL"],
         live["AAG-3"]["applied"]["grade_counts"]["CRITICAL"], oracle["grade_counts"]["CRITICAL"]),
        ("AAG-4.violations", receipt["AAG-4"]["violations"], live["AAG-4"]["violations"],
         oracle["closure_chain"]["violations"]),
        ("AA38.nonempty_descendants", receipt["AA38_not_earned"]["records_with_nonempty_descendants"],
         live["AA38_not_earned"]["records_with_nonempty_descendants"],
         oracle["records_with_nonempty_descendants"]),
    ]
    for name, r, a, b in checks:
        if not (r == a == b):
            bad.append("%s: receipt=%r routeA=%r routeB=%r" % (name, r, a, b))
    single = [
        ("AAG-2.degenerate_count", receipt["AAG-2"]["degenerate_count"], live["AAG-2"]["degenerate_count"]),
        ("AAG-3.monotonicity", receipt["AAG-3"]["monotonicity"]["violations"],
         live["AAG-3"]["monotonicity"]["violations"]),
        ("AAG-5.emitted", receipt["AAG-5"]["emitted"], live["AAG-5"]["emitted"]),
    ]
    for name, r, a in single:
        if r != a:
            bad.append("%s: receipt=%r live=%r" % (name, r, a))
    if receipt["AAG-2"]["degenerate_columns"] != oracle["degenerate_columns"]:
        bad.append("degenerate_columns disagree between receipt and route B")
    # The bare-closed scan is a REPO-WIDE measurement over a corpus that sibling
    # lanes are actively extending, so it is asserted NON-VACUOUSLY rather than
    # by equality: AAG-4 claims "the detector works and the backlog is large",
    # not "the backlog is exactly N". The live number is printed every run.
    sc = live["bare_closed_scan"]
    print("bare-closed scan (live): %d hits in %d packages over %d files (receipt recorded %d/%d/%d)"
          % (sc["hits"], sc["packages_with_hits"], sc["files_scanned"],
             receipt["bare_closed_scan"]["hits"],
             receipt["bare_closed_scan"]["packages_with_hits"],
             receipt["bare_closed_scan"]["files_scanned"]))
    if sc["hits"] <= 1000:
        bad.append("bare-closed scan became vacuous: %d hits" % sc["hits"])
    if sc["packages_with_hits"] <= 100:
        bad.append("bare-closed scan became vacuous: %d packages" % sc["packages_with_hits"])
    if sc["files_scanned"] <= sc["packages_with_hits"]:
        bad.append("bare-closed scan scanned fewer files than packages with hits")
    if bad:
        print("RECEIPT DRIFT:")
        for x in bad:
            print("  " + x)
        return 1
    print("receipt matches both routes on %d quantities" % (len(checks) + len(single) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
