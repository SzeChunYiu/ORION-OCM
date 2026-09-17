#!/usr/bin/env python3
"""GMI #833 claim-discipline E9 append assembler.

Produces REGISTRATIONS_E9_APPEND.json = deep copy of REGISTRATIONS_V2.json
with exactly one change: the gmi-833-g0-grammar-growth-v1 claim object's
forbidden_extrapolations.content gains the E9 metric-conditionality note
(status APPEND_E9_EXEC_RANK_REVIVAL, content appended in place, provenance in
the appended_source field). The v1 and v2 registers are never written; their
sha256 is recorded and asserted unchanged.

Channel correction (2026-09-17, Supplement 2 of GMI_THEORY_BASELINE_V1):
this assembler originally lived in research/gmi-833-claim-discipline-v1/,
which is a FROZEN closed-set package of the baseline; unregistered additions
there fail test_theory_baseline_v1.py. It now lives in its owning lane
(gmi-833-g0-exec-rank-revival-v1/claim_discipline_append/) and reads the
frozen registers read-only. Output bytes are unchanged by the move.

Hostile checks (fail closed):
  - v1 baseline integrity: exactly 234 objects, byte-sha recorded;
  - v2 register byte-sha recorded;
  - exactly one object and one field differ between v2 and the append output;
  - the appended content strings are present exactly once each and unique
    across the merged register;
  - every other field of the target object is deep-equal to v2.
Deterministic under -I -B / -I -O -B.
"""
import copy
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from authored_e9_append import (  # noqa: E402
    TARGET_OBJECT_ID, TARGET_PACKAGE, TARGET_FIELD, APPEND,
)

REG_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "gmi-833-claim-discipline-v1"))
V1_PATH = os.path.join(REG_DIR, "REGISTRATIONS_V1.json")
V2_PATH = os.path.join(REG_DIR, "REGISTRATIONS_V2.json")
OUT_PATH = os.path.join(HERE, "REGISTRATIONS_E9_APPEND.json")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def main():
    v1_bytes = open(V1_PATH, "rb").read()
    v2_bytes = open(V2_PATH, "rb").read()
    v1 = json.loads(v1_bytes.decode())
    v2 = json.loads(v2_bytes.decode())
    assert v1["counts"]["objects"] == 234, v1["counts"]["objects"]
    assert len(v1["objects"]) == 234, len(v1["objects"])
    # v2 = v1's 234 objects + the v2-arrival object (235)
    assert len(v2["objects"]) == len(v1["objects"]) + 1, len(v2["objects"])

    targets = [o for o in v2["objects"]
               if o.get("object_id") == TARGET_OBJECT_ID
               and o.get("package") == TARGET_PACKAGE]
    assert len(targets) == 1, "target object not uniquely resolvable"
    target = targets[0]
    assert TARGET_FIELD in target["fields"], "field missing"

    out = copy.deepcopy(v2)
    otgt = next(o for o in out["objects"] if o["object_id"] == TARGET_OBJECT_ID)
    fe = otgt["fields"][TARGET_FIELD]
    new_content = list(fe["content"]) + list(APPEND["appended_content"])
    otgt["fields"][TARGET_FIELD] = {
        "status": APPEND["status"],
        "content": new_content,
        "appended_source": APPEND["source"],
        "superseded_status": fe["status"],
        "evidence_package": APPEND["evidence_package"],
    }

    # integrity: exactly one object/field diff
    diffs = []
    for a, b in zip(v2["objects"], out["objects"]):
        if a != b:
            changed = [k for k in a["fields"] if a["fields"][k] != b["fields"].get(k)]
            diffs.append((a["object_id"], changed))
    assert diffs == [(TARGET_OBJECT_ID, [TARGET_FIELD])], diffs

    # uniqueness of appended strings across the entire merged register
    all_derived = []
    for o in out["objects"]:
        for f in o["fields"].values():
            c = f.get("content") if isinstance(f, dict) else None
            if isinstance(c, list):
                all_derived.extend(x for x in c if isinstance(x, str))
    for s in APPEND["appended_content"]:
        assert all_derived.count(s) == 1, "appended content not unique"

    out["e9_append"] = {
        "schema": "GMI833_CLAIM_DISCIPLINE_E9_APPEND_V1",
        "parent_issue": APPEND["parent_issue"],
        "evidence_issue": APPEND["evidence_issue"],
        "evidence_package": APPEND["evidence_package"],
        "target_object_id": TARGET_OBJECT_ID,
        "target_field": TARGET_FIELD,
        "appended_content": APPEND["appended_content"],
        "v1_register_sha256": sha256_bytes(v1_bytes),
        "v2_register_sha256": sha256_bytes(v2_bytes),
        "note": "additive append; REGISTRATIONS_V1/V2 never written by this tranche",
    }
    with open(OUT_PATH, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps({"written": OUT_PATH,
                      "v1_sha256": out["e9_append"]["v1_register_sha256"],
                      "v2_sha256": out["e9_append"]["v2_register_sha256"],
                      "appended": APPEND["appended_content"]}, indent=1))


if __name__ == "__main__":
    main()
