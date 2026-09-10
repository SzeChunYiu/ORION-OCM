#!/usr/bin/env python3
"""EB-0 reuse audit. Do not reimplement a parent that is actually installed."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402


PARENTS = (
    ("Avida", ("avida", "avida-core")),
    ("MABE2", ("mabe", "MABE2", "mabe2")),
    ("Empirical", ("empirical",)),
    ("DISHTINY", ("dishtiny", "dish-tiny")),
)


def _which_any(names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def _zoo_contract():
    # Cite #221 CognitiveUnitContractV1 from the sibling zoo package in this repo.
    repo = os.path.abspath(os.path.join(HERE, "..", ".."))
    path = os.path.join(
        repo, "research", "ocm-morphology-zoo-v1", "COGNITIVE_UNIT_CONTRACT_V1.json",
    )
    if os.path.exists(path):
        return {
            "status": "REUSED_AS_FOUNDER_LABELS_ONLY",
            "path": path,
            "sha256": lib.sha256_file(path),
            "note": "Founder palettes map onto contract types. Approximate units never mint C.",
        }
    return {
        "status": "CANNOT_CHECK_CONTRACT_ABSENT",
        "path": path,
        "sha256": None,
    }


def audit():
    rows = []
    for name, bins in PARENTS:
        found = _which_any(bins)
        rows.append({
            "parent": name,
            "status": "INSTALLED" if found else "CANNOT_CHECK_PARENT_NOT_INSTALLED",
            "binary": found,
            "residual": None if found else "OCM_CELL_VM_AND_ECOLOGY",
        })
    installed = [r["parent"] for r in rows if r["status"] == "INSTALLED"]
    return {
        "schema": "EB0_REUSE_AUDIT_V1",
        "ts": lib.now(),
        "host": os.uname().nodename,
        "parents": rows,
        "zoo_cognitive_unit_contract": _zoo_contract(),
        "decision": (
            "REUSE_PARENTS_FOR_GENERIC_ALIFE" if installed
            else "IMPLEMENT_OCM_RESIDUAL_ONLY"
        ),
        "installed_parents": installed,
        "rule": "Do not reimplement generic ALife machinery if a parent is present. "
                "LUNARC audit at submit time must agree with this decision.",
    }


def main() -> int:
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
    obj = audit()
    path = os.path.join(root, "results", "EB0_REUSE_AUDIT.json")
    sha = lib.write_json(path, obj)
    lib.event("eb0_audit", path=path, sha256=sha, decision=obj["decision"])
    print("EB0", obj["decision"], sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
