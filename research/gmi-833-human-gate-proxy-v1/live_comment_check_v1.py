#!/usr/bin/env python3
"""Verify every reconciliation `old` line against a LIVE fetch of the three issue
comments, taken immediately before the reconciliation is finalised.

    python3 -I -B live_comment_check_v1.py <dir>

<dir> holds `body_<comment_id>.txt` (the comment body bytes, exactly as the API
returned them) and `fetched_at.txt` (UTC timestamp of the fetch).  For every row
in build_reconciliation_v1.ROWS the `old` line must occur exactly once in the
live body and exactly once under its `###` anchor, and the anchor itself must
occur exactly once.  Writes LIVE_COMMENT_CHECK_V1.json; exit 1 on any failure.
Nothing here writes to GitHub.  Stdlib only, python3.8.
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(src):
    spec = importlib.util.spec_from_file_location("br", os.path.join(HERE, "build_reconciliation_v1.py"))
    br = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(br)
    fetched_at = open(os.path.join(src, "fetched_at.txt"), encoding="utf-8").read().strip()
    bodies = {}
    for cid in br.SNAP:
        bodies[cid] = open(os.path.join(src, "body_%s.txt" % cid), "rb").read()
    per_comment = {}
    for cid, raw in bodies.items():
        snap = open(os.path.join(HERE, br.SNAP[cid]), "rb").read()
        per_comment[cid] = {"live_bytes": len(raw), "live_sha256": hashlib.sha256(raw).hexdigest(),
                            "snapshot_bytes": len(snap), "snapshot_sha256": hashlib.sha256(snap).hexdigest(),
                            "live_equals_snapshot": raw == snap,
                            "live_equals_snapshot_modulo_trailing_newline": raw.rstrip(b"\n") == snap.rstrip(b"\n")}
    rows = {}
    failures = []
    for row, (cid, anchor, old) in br.ROWS.items():
        text = bodies[cid].decode("utf-8")
        n_anchor = text.count("\n" + anchor + "\n") + int(text.startswith(anchor + "\n"))
        n_body = text.count(old + "\n") + int(text.endswith(old))
        if n_anchor == 1:
            section = text.split(anchor, 1)[1].split("\n### ", 1)[0]
            n_section = section.count(old + "\n") + int(section.endswith(old))
        else:
            n_section = 0
        rows[row] = {"comment_id": int(cid), "anchor_occurrences": n_anchor, "old_in_body": n_body, "old_under_anchor": n_section}
        if not (n_anchor == 1 and n_body == 1 and n_section == 1):
            failures.append(row)
    out = {"schema": "GMI_833_LIVE_COMMENT_CHECK_V1", "fetched_at_utc": fetched_at, "comments": per_comment,
           "rows_checked": len(rows), "rows_failing": failures, "rows": rows,
           "rule": "every `old` occurs exactly once in the live body and exactly once under its anchor; "
                   "a row failing here is not written by the orchestrator"}
    with open(os.path.join(HERE, "LIVE_COMMENT_CHECK_V1.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"rows_checked": len(rows), "rows_failing": failures, "fetched_at": fetched_at}))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main(sys.argv[1])
