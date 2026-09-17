#!/usr/bin/env python3
"""Complete the D5 determinism protocol across two hosts and emit
RECEIPT_MULTIHOST_V1.json (REV-L47-NOVEL-INTELLIGENCE-W4).

Inputs: the two hosts' RESULT_V1.json (each produced by the executor's
--protocol driver, so each already carries the same-host bit-identity half
of D5) and the two RUNTIME_V1.json charging records. Verifies:

  - both results parse and carry verdict
    PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED,
  - both runtimes record same_host_bit_identical = true,
  - the two result files are byte-identical (sha256) -- the cross-host half
    of D5,
  - exactly two distinct hosts are present,

then writes the multihost receipt. Distinct exit codes: 0 verified, 2
protocol violation, 3 cannot-check (missing/unparseable input).

Py3.8-safe, stdlib-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Dict, List, Tuple

CLEARED = "PROSPECTIVE_CONTENT_CONFIRMED__SUSPICION_CLEARED"


def sha256_file(path):
    # type: (str) -> str
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    # type: () -> int
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--primary-result", required=True)
    ap.add_argument("--primary-runtime", required=True)
    ap.add_argument("--secondary-result", required=True)
    ap.add_argument("--secondary-runtime", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    loaded = []  # type: List[Tuple[str, Dict[str, object], Dict[str, object], str]]
    for res, run in (
        (args.primary_result, args.primary_runtime),
        (args.secondary_result, args.secondary_runtime),
    ):
        try:
            with open(res, "r", encoding="utf-8") as fh:
                result = json.load(fh)
            with open(run, "r", encoding="utf-8") as fh:
                runtime = json.load(fh)
        except (OSError, ValueError) as exc:
            print("CANNOT_CHECK %s / %s: %s" % (res, run, exc))
            return 3
        loaded.append((res, result, runtime, sha256_file(res)))

    violations = []  # type: List[str]
    hosts = []  # type: List[str]
    for res, result, runtime, digest in loaded:
        if result.get("verdict") != CLEARED:
            violations.append("%s: verdict %r != %r" % (res, result.get("verdict"), CLEARED))
        flags = result.get("decision_flags") or {}
        if flags.get("D5_determinism_bit_identity") is not True:
            violations.append("%s: same-host D5 half not true" % res)
        if runtime.get("same_host_bit_identical") is not True:
            violations.append("%s: runtime same_host_bit_identical not true" % res)
        hosts.append(str(runtime.get("host")))
    if len(set(hosts)) != 2:
        violations.append("expected 2 distinct hosts, saw %r" % sorted(set(hosts)))
    if loaded[0][3] != loaded[1][3]:
        violations.append(
            "cross-host result sha256 differ: %s != %s" % (loaded[0][3], loaded[1][3])
        )
    if violations:
        for v in violations:
            print("PROTOCOL_VIOLATION", v)
        return 2

    host_records = []  # type: List[Dict[str, object]]
    for (_, result, runtime, digest) in loaded:
        host_records.append(
            {
                "host": runtime.get("host"),
                "platform": runtime.get("platform"),
                "python": runtime.get("python"),
                "elapsed": runtime.get("elapsed"),
                "result_sha256": digest,
                "same_host_bit_identical": runtime.get("same_host_bit_identical"),
            }
        )
    receipt = {
        "schema": "GMI_NOVEL_INTELLIGENCE_W4_PROSPECTIVE_MULTIHOST_V1",
        "ticket": "REV-L47-NOVEL-INTELLIGENCE-W4",
        "protocol": [
            "per host: executor --protocol runs the campaign twice in isolated "
            "subprocesses; receipts must be byte-identical (same-host half of D5)",
            "across hosts: the two RESULT_V1.json files must be byte-identical "
            "(cross-host half of D5), verified here by sha256",
        ],
        "hosts": host_records,
        "host_count": len(host_records),
        "cross_host_bit_identical": True,
        "D5_completed": True,
        "final_verdict": CLEARED,
        "result_sha256": loaded[0][3],
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(
        json.dumps(
            {
                "cross_host_bit_identical": True,
                "hosts": hosts,
                "host_count": receipt["host_count"],
                "result_sha256": loaded[0][3],
                "final_verdict": CLEARED,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
