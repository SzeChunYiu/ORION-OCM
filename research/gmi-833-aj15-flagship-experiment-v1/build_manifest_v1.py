# -*- coding: utf-8 -*-
"""Build MANIFEST_V1.json: parent pins (path + git blob sha + claim ceiling), source_main,
freeze commit, claim ceiling, forbidden promotions, receipt digests.

    python3 -I -B build_manifest_v1.py            # write
    python3 -I -B build_manifest_v1.py --check    # require byte equality with the committed file
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

REPO = os.path.dirname(os.path.dirname(HERE))

PARENTS = [
    ("gmi-833-aj9a-known-family-benchmark-v1", "KNOWN_FAMILY_BENCHMARK_V1.json", None),
    ("gmi-833-aj9a-known-family-benchmark-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj9h-k07-k11-blind-recovery-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj9-holdout-source-audit-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj10-prospective-unknown-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj11-bounded-completeness-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj12-foundation-substrate-relativity-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj13-stopping-rule-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj14-establishment-criterion-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-aj1-operational-process-base-v1", "RESULT_V1.json", "claim_ceiling"),
    ("gmi-833-h-family-gate-soundness-v1", "SCIENTIFIC_LEDGER_V1.json", None),
]


def blob_sha(path):
    data = _read_bytes(path)
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()


def sha256(path):
    return hashlib.sha256(_read_bytes(path)).hexdigest()


def build():
    result = _load_json(os.path.join(HERE, "RESULT_V1.json"))
    pins = []
    for pkg, fn, key in PARENTS:
        p = os.path.join(REPO, "research", pkg, fn)
        doc = _load_json(p)
        pins.append({"package": pkg, "path": "research/%s/%s" % (pkg, fn), "blob_sha": blob_sha(p),
                     "claim_ceiling": doc.get(key) if key else None,
                     "status": doc.get("status")})
    return {
        "schema": "GMI_833_MANIFEST_V1",
        "package": "gmi-833-aj15-flagship-experiment-v1",
        "issue": 833,
        "authority_comment_id": 5693954852,
        "source_main": "f1e150ea89d1e3422d5ab18ec9a61d36ff17c3e5",
        "freeze_commit": "793e3548db7b06ee998b374ace49043c14070f67",
        "claim_ceiling": result["claim_ceiling"],
        "ceilings_not_exceeded": result["ceilings_not_exceeded"],
        "forbidden_promotions": result["forbidden_promotions"],
        "named_results": ["FX-1", "FX-2", "FX-3", "FX-4", "FX-5", "FX-6"],
        "parent_pins": pins,
        "receipts_sha256": {fn: sha256(os.path.join(HERE, fn)) for fn in (
            "BLIND_OUTCOME_V1.json", "ORACLE_RESULT_V1.json", "POSTHOC_RESULT_V1.json",
            "LADDER_RESULT_V1.json", "LADDER_ORACLE_RESULT_V1.json", "RESULT_V1.json")},
        "reconciliation_mode": "JSON_ONLY__ORCHESTRATOR_PERFORMS_EVERY_ISSUE_WRITE",
        "compute_host": "laptop-billy (python 3.8.10); CI ubuntu-latest (python 3.12)",
    }


def main(argv=None):
    doc = build()
    text = json.dumps(doc, indent=1, sort_keys=True) + "\n"
    path = os.path.join(HERE, "MANIFEST_V1.json")
    if "--check" in (argv or sys.argv[1:]):
        if _read_text(path) != text:
            sys.stderr.write("MANIFEST_V1.json differs from a live rebuild\n")
            return 1
        print("MANIFEST_V1.json matches a live rebuild (%d parent pins)" % len(doc["parent_pins"]))
        return 0
    _write_text(path, text)
    print("wrote MANIFEST_V1.json with %d parent pins" % len(doc["parent_pins"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
