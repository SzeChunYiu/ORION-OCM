#!/usr/bin/env python3
"""Re-derive every headline number and compare it to the committed receipt."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ab_harness_v1 as A                # noqa: E402
import independent_ab_oracle_v1 as B     # noqa: E402
import terminology_ratchet_v1 as R       # noqa: E402


def main():
    receipt = json.load(open(os.path.join(HERE, "RESULT_V1.json")))
    a = A.run()
    b = B.run()
    base = json.load(open(R.BASELINE))
    bad = []
    for k in ("crosswalk_rows", "extension_rows", "banned_terms", "banned_with_replacement"):
        if not (receipt[k] == a[k] == b[k]):
            bad.append("%s: receipt=%r A=%r B=%r" % (k, receipt[k], a[k], b[k]))
    for k in ("rows_checked", "rows_earned", "rows_open", "required_terms_total",
              "parent_covered_total", "total_covered_total"):
        if receipt[k] != a[k]:
            bad.append("%s: receipt=%r A=%r" % (k, receipt[k], a[k]))
    # the shared (crosswalk-row) subset must agree exactly between routes
    am = dict((x["row_id"], x) for x in a["rows"])
    for x in b["rows"]:
        av = am[x["row_id"]]
        for k in ("parent_covered", "total_covered", "required",
                  "parent_rows_found", "extension_rows_found"):
            if av[k] != x[k]:
                bad.append("row %s %s: A=%r B=%r" % (x["row_id"], k, av[k], x[k]))
    cs = receipt["corpus_state"]
    if cs["baseline_total_hits"] != base["total_hits"]:
        bad.append("ratchet baseline drift: receipt=%r file=%r"
                   % (cs["baseline_total_hits"], base["total_hits"]))
    if cs["baseline_files_with_hits"] != base["files_with_hits"]:
        bad.append("ratchet files_with_hits drift")
    if bad:
        print("RECEIPT DRIFT:")
        for x in bad:
            print("  " + x)
        return 1
    print("receipt matches route A, route B and the ratchet baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
