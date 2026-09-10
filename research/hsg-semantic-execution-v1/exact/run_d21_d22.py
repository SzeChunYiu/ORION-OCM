"""D21+D22 entry point.

Emits results/D21_RESULTS.json, results/D22_RESULTS.json and receipts/*.jsonl,
mirroring run_all.py's format. Deterministic: frozen seeds, sorted iteration,
stable JSON dumps. Protocol: D21_D22_PROTOCOL_V1.md (frozen before this ran).

Run: python3 -m exact.run_d21_d22 [d21|d22]
"""
from __future__ import annotations
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")

def _dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")

def _receipt(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

def main() -> int:
    which = sys.argv[1].lower() if len(sys.argv) > 1 else "both"
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    rc = 0

    if which in ("d21", "both"):
        from .d21_reduction_equality import run_d21
        t0 = time.time()
        d21, rec = run_d21()
        _dump(os.path.join(RESULTS, "D21_RESULTS.json"), d21)
        _receipt(rec, os.path.join(RECEIPTS, "D21_receipts.jsonl"))
        s = d21["summary"]
        print("D21 wall_s:", round(time.time() - t0, 2))
        for k in sorted(s):
            print(f"  {k}: {s[k]}")
        if not s["conformance_control_passed"] or not s["unsound_witness_found"]:
            print("D21 LANE INVALID: control failed")
            rc = 2
        if s["E1_hostile_detection_rate"] != 1.0:
            print("D21 E1 FAILED: hostile not detected everywhere")
            rc = 2
        if s["E2_clean_false_alarms"] != 0:
            print("D21 E2 FAILED: false alarm on a clean arm")
            rc = 2
        if s["E2b_alarms_on_not_contaminable_hostile_worlds"]:
            print("D21 E2b FAILED: alarm where contamination is impossible")
            rc = 2
        if s["E1_undecided_worlds_eclass_capped"]:
            print("D21 E1 UNDECIDED: e-class walk capped on",
                  s["E1_undecided_worlds_eclass_capped"])
            rc = 2
        if not s["E6_egglog_decided_every_pair"] or s["E6_cross_check_agreement"] != 1.0:
            print("D21 E6 FAILED: egglog did not decide every pair, or disagreed")
            rc = 2

    if which in ("d22", "both"):
        from .d22_logic_transport import run_d22
        t0 = time.time()
        d22, rec = run_d22()
        _dump(os.path.join(RESULTS, "D22_RESULTS.json"), d22)
        _receipt(rec, os.path.join(RECEIPTS, "D22_receipts.jsonl"))
        s = d22["summary"]
        print("D22 wall_s:", round(time.time() - t0, 2))
        for k in sorted(s):
            print(f"  {k}: {s[k]}")
        if s["F5_clean_alarms"] != 0:
            print("D22 F5 FAILED: alarm on the CLEAN arm")
            rc = 2
        if not s["F4_both_hostiles_fired"]:
            print("D22 F4 FAILED: a hostile did not fire")
            rc = 2
    return rc

if __name__ == "__main__":
    sys.exit(main())
