#!/usr/bin/env python3
"""Build (`--write`) or verify RESULT_V1.json against a live two-route run.

Every input of this package is a frozen, blob-pinned artifact, so the receipt
is pinned by EQUALITY: any drift between the stored receipt and a live run is
a failure, never a "scope changed" note.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import registration_pass_v1 as A                 # noqa: E402
import independent_registration_oracle_v1 as B   # noqa: E402

RECEIPT = HERE / "RESULT_V1.json"
ORACLE_RECEIPT = HERE / "ORACLE_RESULT_V1.json"


def build():
    inp = A.Inputs()
    out = A.build(inp, write=False)
    b = B.derive()
    a = out["result"]
    a_bound = dict((rid, k) for rid, (_, k) in out["bound"].items())
    a_levels = dict((k, [r["maturity_level"], r["evidence_level"]]) for k, r in out["records"].items() if r["provenance"].get("maturity_level"))
    agreement = {
        "compared_by": "set / dict equality on bound rows, rules, levels, ledger keys, dependency edges, by-name edges, "
                       "strongest-parent edges, refused edges, descendants (direct and closed), per-gap grades, populated record count",
        "bound_rows_identical": a_bound == b["bound"],
        "binding_rules_identical": dict((rid, r) for rid, (r, _) in out["bound"].items()) == b["rules"],
        "levels_identical": a_levels == b["levels"],
        "ledger_keys_identical": all(sorted(k for k, r in out["records"].items() if r[f] != A.UNREGISTERED and r["binding"].get("registration")) == b["ledger_keys"][f] for f in A.LIST_FIELDS),
        "dependency_edges_identical": sorted(out["dep_edges"]) == [tuple(x) for x in b["dep_edges"]],
        "refused_edges_identical": sorted((r["layer"], r["index"], r["reason"]) for r in out["refusals"] if r["kind"] == "DEPENDENCY_EDGE") == [tuple(x) for x in b["refused_edges"]],
        "descendants_identical": dict((g["id"], g["descendants"]) for g in out["gaps"]) == b["descendants"],
        "grades_identical": dict((g["id"], g["materiality"]) for g in out["gaps"]) == b["grade_of"],
        "populated_records_identical": len(out["records"]) == b["populated_records"],
        "route_b_mechanics": "linear (package,id) tables; '_'-split id forms; regex citations; fixed-point descendants; 256-entry grade lookup",
    }
    receipt = dict(a)
    receipt["route_b"] = B.summary(b)
    receipt["route_agreement"] = agreement
    receipt["named_results"] = {
        "CRP-1": "173 of 197 scored rows bind to exactly one census object by exact identity (145 B1 + 28 B2); the 24 arrivals and the v3 arrival are package-level and bind nothing; a loose prefix variant adds 0",
        "CRP-2": "the four ledgers of 173 registrations and 113 object-to-id dependency edges are propagated with one pointer per entry; 12 edges refused by reason; 22380 objects are explicitly UNREGISTERED",
        "CRP-3": "materiality re-graded by AAG-3's threshold reproduces 847/293 and makes the field two-valued; descendants populate 50 of 1140 gaps, 1090 stay isolated",
        "CRP-4": "5 of the 19 fallacy rows left undecidable gain a registered discriminator, all bound by the assumptions ledger at 173/22553; 13 have no register field to read",
        "CRP-5": "the pointer verifier raises 0 findings on the real register and detects planted wrong pointers; every hostile H1-H8 is detected and the null is beaten 173 > 69",
    }
    return receipt, b


def main(argv):
    live, b = build()
    if "--write" in argv:
        RECEIPT.write_text(json.dumps(live, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        ORACLE_RECEIPT.write_text(json.dumps(B.summary(b), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("wrote %s and %s" % (RECEIPT.name, ORACLE_RECEIPT.name))
        return 0
    if not RECEIPT.exists() or not ORACLE_RECEIPT.exists():
        print("MISSING RECEIPT")
        return 1
    stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
    stored_b = json.loads(ORACLE_RECEIPT.read_text(encoding="utf-8"))
    diffs = [k for k in sorted(set(stored) | set(live)) if stored.get(k) != live.get(k)]
    if stored_b != B.summary(b):
        diffs.append("ORACLE_RESULT_V1.json")
    if not all(v for k, v in live["route_agreement"].items() if k.endswith("identical")):
        diffs.append("route_agreement")
    if diffs:
        for d in diffs:
            print("RECEIPT DRIFT: %s" % d)
        return 1
    print("receipt matches: %d objects, %d bound rows, %d populated records, grades %s, %d gaps with descendants, %d rows gained a discriminator"
          % (live["population"]["objects"], live["binding"]["bound_rows"], live["population"]["populated_records"],
             live["gap_graph"]["grade_counts"], live["gap_graph"]["gaps_with_nonempty_descendants"],
             live["decidability_summary"]["gained_registered_discriminator"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
