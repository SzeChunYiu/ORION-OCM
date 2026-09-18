#!/usr/bin/env python3
"""Verify the Section-AE lane reconciliation against the snapshotted comment.

Runs with stdlib only, under `python3 -I -B` and `python3 -I -O -B`.  Every
assertion is a real comparison, never an `assert` that `-O` would strip.
"""

from __future__ import annotations

from hashlib import md5
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

SPEC = HERE / "ISSUE_833_COMMENT_RECONCILIATION_V1.json"
SNAPSHOT = HERE / "COMMENT_5692689542_AT_EXTRACTION.md"
PACKAGE_SPECS = (
    "research/gmi-833-ae-morphology-sweep-v1/"
    "ISSUE_833_RECONCILIATION_AE_MORPHOLOGY_SWEEP_V1.json",
    "research/gmi-833-ae-ae3-compression-learning-v1/"
    "ISSUE_833_RECONCILIATION_AE3_COMPRESSION_LEARNING_V1.json",
    "research/gmi-833-ae-ae5-causal-state-audit-v1/"
    "ISSUE_833_RECONCILIATION_AE5_CAUSAL_STATE_AUDIT_V1.json",
)


def fail(msg):
    sys.stderr.write("FAIL: " + msg + "\n")
    raise SystemExit(1)


def main():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    body = SNAPSHOT.read_text(encoding="utf-8")

    digest = md5(SNAPSHOT.read_bytes()).hexdigest()
    if digest != spec["comment_body_md5_at_extraction"]:
        fail("snapshot md5 " + digest + " != declared "
             + spec["comment_body_md5_at_extraction"])

    if spec["schema"] != "GMI_ISSUE_COMMENT_RECONCILIATION_V1":
        fail("wrong schema")
    if spec["issue"] != 833 or spec["comment_id"] != 5692689542:
        fail("wrong issue or comment id")

    anchors = set()
    unchecked = []
    cur = None
    for line in body.split("\n"):
        if line.startswith("### "):
            cur = line
            anchors.add(line)
        elif cur is not None and line.startswith("- [ ] "):
            unchecked.append((cur, line))

    if len(unchecked) != spec["rows_unchecked_before"]:
        fail("unchecked count " + str(len(unchecked)) + " != declared "
             + str(spec["rows_unchecked_before"]))

    reps = spec["replacements"]
    ncs = spec["not_closed"]
    if len(reps) != spec["rows_closed_here"]:
        fail("replacement count mismatch")
    if len(ncs) != spec["rows_left_open"]:
        fail("not_closed count mismatch")
    if len(reps) + len(ncs) != len(unchecked):
        fail("replacements + not_closed must cover every unchecked row")

    live = dict((row, anchor) for anchor, row in unchecked)
    seen = set()
    for entry in reps + ncs:
        if entry.get("comment_id") != 5692689542:
            fail("every entry must carry comment_id 5692689542")
        old = entry["old"]
        if old in seen:
            fail("duplicate old: " + old[:60])
        seen.add(old)
        if body.count(old) != 1:
            fail("old does not occur exactly once: " + old[:60])
        if old not in live:
            fail("old is not a live unchecked row: " + old[:60])
        if live[old] != entry["anchor"]:
            fail("anchor mismatch for: " + old[:60])
        if entry["anchor"] not in anchors:
            fail("unknown anchor: " + entry["anchor"])

    for rep in reps:
        if not rep["old"].startswith("- [ ] "):
            fail("old is not an unchecked row")
        if not rep["new"].startswith("- [x] "):
            fail("new is not a checked row")
        if not rep["new"][6:].startswith(rep["old"][6:]):
            fail("new must extend old verbatim: " + rep["old"][:60])
        if " — ✅ " not in rep["new"]:
            fail("new must carry the evidence marker")

    # every closed row is backed by exactly one committed package receipt
    pkg_rows = {}
    for rel in PACKAGE_SPECS:
        d = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        if d["schema"] != "GMI_ISSUE_RECONCILIATION_V2":
            fail("package spec has the wrong schema: " + rel)
        for r in d["replacements"]:
            if r["old"] in pkg_rows:
                fail("two packages claim the same row: " + r["old"][:60])
            pkg_rows[r["old"]] = (d["package"], r["new"])
    if set(pkg_rows) != set(r["old"] for r in reps):
        fail("section replacements and package receipts disagree")
    for rep in reps:
        pkg, new = pkg_rows[rep["old"]]
        if rep["package"] != pkg:
            fail("package attribution mismatch: " + rep["old"][:60])
        if rep["new"] != new:
            fail("section new line differs from the package receipt")

    tiers = {}
    for nc in ncs:
        tiers[nc["tier"]] = tiers.get(nc["tier"], 0) + 1
        if not nc["reason"]:
            fail("every not_closed entry needs a reason")
        if nc["tier"] == 3 and not nc["reason"].startswith("INSTRUMENT_REQUIRED"):
            fail("tier-3 rows must state their instrument requirement")
        if nc["tier"] == 4 and not nc["reason"].startswith(
            "LEDGER_SWEEP_PENDING"
        ):
            fail("tier-4 rows must say what they are waiting on")
        if nc["tier"] in (1, 2) and not nc["reason"].startswith(
            "NOT_ATTEMPTED_IN_THIS_LANE"
        ):
            fail("untouched tier-1 rows must be recorded as not attempted, "
                 "never as blocked")
    if tiers.get(3) != 16:
        fail("the 16 instrument-blocked rows must all stay open, found "
             + str(tiers.get(3)))
    if tiers.get(4) != 7:
        fail("the 7 AE17 ledger rows must all stay open")

    if spec["section_checked_after_apply"] != 21 + len(reps):
        fail("section total mismatch")
    if spec["section_checked_after_apply"] > spec["honest_ceiling"]:
        fail("claimed more than the honest ceiling")

    print("section reconciliation OK: "
          + str(len(reps)) + " closed, "
          + str(len(ncs)) + " open ("
          + str(tiers.get(3)) + " instrument-blocked, "
          + str(tiers.get(4)) + " ledger, "
          + str(tiers.get(1, 0) + tiers.get(2, 0)) + " not attempted)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
