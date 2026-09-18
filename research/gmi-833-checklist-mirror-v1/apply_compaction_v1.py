"""Apply the compaction to the live #833 body, under refuse-on-drift checks.

The ledger is generated from ISSUE_833_BODY_MIRROR.md. If the live body has
moved since that mirror was taken, the ledger would not cover the new rows'
evidence, so this tool REFUSES rather than compacting against a stale ledger.

    python3 -I -B apply_compaction_v1.py            # dry run
    python3 -I -B apply_compaction_v1.py --apply
"""

import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import checklist_core_v1 as core
import compact_body_v1 as comp
import issue_body_safe_write_v1 as safe


def main(argv):
    apply_it = "--apply" in argv
    mirror = core.read_text(os.path.join(HERE, "ISSUE_833_BODY_MIRROR.md"))
    live = safe.fetch_body(833)

    if live != mirror:
        raise safe.RefusedWrite(
            "live body has drifted from the mirror (live %d chars sha %s, mirror %d chars "
            "sha %s); refresh the mirror and regenerate the ledger before compacting"
            % (len(live), core.body_sha256(live)[:16], len(mirror), core.body_sha256(mirror)[:16]))

    new, ledger = comp.compact(live)

    committed = json.load(io.open(os.path.join(HERE, "EVIDENCE_LEDGER_V1.json"), encoding="utf-8"))
    if committed["entries"] != ledger["entries"]:
        raise safe.RefusedWrite("committed ledger does not reproduce from the live body")
    if committed["source_body_sha256"] != core.body_sha256(live):
        raise safe.RefusedWrite("committed ledger was built from a different body")

    rows_a, _ = core.parse(live)
    rows_b, _ = core.parse(new)
    if core.signature(rows_a) != core.signature(rows_b):
        raise safe.RefusedWrite("row signature changed")
    if [r["text"] for r in rows_a] != [r["text"] for r in rows_b]:
        raise safe.RefusedWrite("row text changed")
    if len(new) > core.BODY_LIMIT:
        raise safe.RefusedWrite("compacted body still over limit")

    print("live      : %d chars, sha %s" % (len(live), core.body_sha256(live)[:16]))
    print("compacted : %d chars, sha %s" % (len(new), core.body_sha256(new)[:16]))
    print("rows      : %d (%d checked / %d unchecked) - unchanged"
          % (len(rows_a), sum(1 for r in rows_a if r["checked"]),
             sum(1 for r in rows_a if not r["checked"])))
    print("headroom  : %d -> %d" % (core.BODY_LIMIT - len(live), core.BODY_LIMIT - len(new)))
    print("evidence recoverable byte-exact for all %d closed rows" % committed["checked"])
    if not apply_it:
        print("DRY RUN - pass --apply to write")
        return 0

    fd, tmp = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    core.write_text(tmp, new)
    subprocess.check_call(
        ["gh", "issue", "edit", "833", "--repo", safe.REPO, "--body-file", tmp])
    os.unlink(tmp)

    back = safe.fetch_body(833)
    if back != new:
        raise safe.RefusedWrite(
            "POST-WRITE MISMATCH: read back %d chars sha %s, intended %d sha %s"
            % (len(back), core.body_sha256(back)[:16], len(new), core.body_sha256(new)[:16]))
    rb, _ = core.parse(back)
    print("WRITE VERIFIED: %d chars, %d rows, %d checked, sha %s"
          % (len(back), len(rb), sum(1 for r in rb if r["checked"]),
             core.body_sha256(back)[:16]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except safe.RefusedWrite as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.exit(1)
