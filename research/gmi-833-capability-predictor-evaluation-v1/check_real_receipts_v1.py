"""Integrity gate for the committed real-system receipts.

Fails loudly if a receipt is missing: "could not check" is never reported as
"checked and fine".

Run:  python3 -I -B check_real_receipts_v1.py
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

RECEIPTS = (("REAL_RUNS/REAL_MEASURED_V1.json", "V1"),
            ("REAL_RUNS_V2/REAL_MEASURED_V2.json", "V2"),
            ("REAL_RUNS_V3/REAL_MEASURED_V3.json", "V3"))


def main():
    seen = 0
    for rel, key in RECEIPTS:
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            sys.stderr.write("MISSING RECEIPT: %s\n" % rel)
            return 1
        with open(path, "rb") as handle:
            raw = handle.read()
        payload = json.loads(raw.decode("utf-8"))
        if payload["source"]["sha256"] != payload["source_sha256_verified"]:
            sys.stderr.write("SOURCE SHA MISMATCH: %s\n" % rel)
            return 1
        if payload["protected_eval_items"] <= 0:
            sys.stderr.write("EMPTY PROTECTED SPLIT: %s\n" % rel)
            return 1
        if len(payload["measured_solved_bits"]) != 32:
            sys.stderr.write("WRONG SYSTEM COUNT: %s\n" % rel)
            return 1
        if payload["train_items"] <= 0:
            sys.stderr.write("EMPTY TRAINING SET: %s\n" % rel)
            return 1
        sys.stdout.write("%s receipt ok  systems=%d eval_items=%d sha256=%s\n"
                         % (key, len(payload["measured_solved_bits"]),
                            payload["protected_eval_items"],
                            hashlib.sha256(raw).hexdigest()[:16]))
        seen += 1
    if seen != len(RECEIPTS):
        sys.stderr.write("expected %d receipts, checked %d\n" % (len(RECEIPTS), seen))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
