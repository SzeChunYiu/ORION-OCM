#!/usr/bin/env python3
"""Record supersession S1 against the EB-F0 freeze.

The freeze binds results to a code_digest and run_ebf0.py hard-refuses on drift.
That guard fired correctly when parents.py changed, so the change is recorded as
a numbered, append-only amendment rather than bypassed. The original manifest is
preserved verbatim beside it.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402

CAUSE = (
    "BIO-T9 requires an EXACT finite Price identity. multilevel_price() computed it in "
    "floats and checked it with a 1e-12 tolerance, which is not an exact identity. The "
    "float version was also host-dependent: a re-run on a disjoint host reproduced every "
    "theorem row and the gate byte-identically but emitted between=-0.4000000000000002 "
    "against the frozen -0.4, changing the certificate sha256 while the values were equal "
    "to within epsilon. A certificate whose hash depends on the host cannot anchor "
    "replication, which is what B1-IND-REPLAY in the TTAC blocker DAG needs. "
    "parents.py now computes the decomposition in exact rational arithmetic and checks "
    "the identity with exact equality."
)


def main() -> int:
    fp = os.path.join(HERE, lib.FREEZE_NAME)
    fz = lib.load_json(fp)
    if any(a.get("id") == "S1" for a in fz.get("amendments", [])):
        raise SystemExit("REFUSED: S1 already recorded")

    old_digest = fz["code_digest"]
    old_files = dict(fz.get("code_files_sha256", {}))
    new_files = lib.code_files_sha256(HERE)
    new_digest = lib.code_digest(HERE)
    changed = sorted(k for k, v in new_files.items() if old_files.get(k) != v)

    if changed != ["parents.py"]:
        raise SystemExit("REFUSED: S1 authorises only parents.py; changed=%s" % changed)
    if old_digest == new_digest:
        raise SystemExit("REFUSED: no drift to record")

    fz.setdefault("amendments", []).append({
        "id": "S1",
        "utc": lib.now(),
        "cause": CAUSE,
        "authorised_files": changed,
        "prior_code_digest": old_digest,
        "new_code_digest": new_digest,
        "prior_parents_py_sha256": old_files.get("parents.py"),
        "new_parents_py_sha256": new_files.get("parents.py"),
        "original_manifest_preserved": "code_files_sha256_v1 below",
        "worlds_contracts_endpoints_hostiles_touched": False,
        "theorem_rows_touched": False,
        "results_must_be_regenerated": True,
        "note": (
            "Arithmetic exactness only. No world, contract, endpoint, hostile, theorem row, "
            "seed or claim ceiling is altered. Every prior certificate section except the "
            "P-ML-PRICE parent row was already byte-identical across hosts."
        ),
    })
    fz.setdefault("code_files_sha256_v1", old_files)
    fz["code_digest"] = new_digest
    fz["code_files_sha256"] = new_files
    sha = lib.write_json(fp, fz)
    lib.event(kind="ebf0_freeze_amendment", amendment="S1",
              prior_code_digest=old_digest, new_code_digest=new_digest, sha256=sha)
    print("S1 recorded: %s -> %s" % (old_digest[:16], new_digest[:16]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
