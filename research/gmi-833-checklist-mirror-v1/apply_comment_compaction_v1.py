"""Compact a live #833 comment to pointer form, under refuse-on-drift checks.

    python3 -I -B apply_comment_compaction_v1.py <comment_id>            # dry run
    python3 -I -B apply_comment_compaction_v1.py <comment_id> --apply

Before any write: snapshot the pre-compaction body byte-exact into comments/,
so the change is reversible. After: read back and require byte equality, then
union the per-comment ledger into COMMENT_EVIDENCE_LEDGER_V1.json without ever
letting a pointer overwrite real evidence.
"""
import io, json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import checklist_core_v1 as core
import compact_comment_v1 as cc
from issue_body_safe_write_v1 import RefusedWrite, REPO
from comment_safe_write_v1 import fetch_comment

def main(argv):
    cid = int(argv[0]); apply_it = "--apply" in argv
    live = fetch_comment(cid)
    new, ledger = cc.compact(live, cid)
    c = ledger["compaction"]
    print("comment %d: %d rows -> pointer form; %d -> %d chars; headroom %d -> %d"
          % (cid, c["rows_compacted"], c["chars_before"], c["chars_after"],
             cc.LIMIT - c["chars_before"], c["headroom_after"]))
    if cc.signature(cc.parse(new)) != cc.signature(cc.parse(live)):
        raise RefusedWrite("row signature changed")
    if not apply_it:
        print("DRY RUN - pass --apply to write"); return 0
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    snap = os.path.join(HERE, "comments", "comment_%d.pre_compaction_%s.md" % (cid, stamp))
    core.write_text(snap, live)
    fd, tmp = tempfile.mkstemp(suffix=".md"); os.close(fd); core.write_text(tmp, new)
    subprocess.check_call(["gh", "api", "-X", "PATCH", "repos/%s/issues/comments/%d" % (REPO, cid), "-F", "body=@%s" % tmp])
    os.unlink(tmp)
    back = fetch_comment(cid)
    if back != new:
        raise RefusedWrite("POST-WRITE MISMATCH on comment %d (read back %d chars, intended %d)" % (cid, len(back), len(new)))
    cc.merge_ledger(cc.LEDGER_PATH_LOCAL, ledger)
    core.write_text(os.path.join(HERE, "comments", "comment_%d.md" % cid), back)
    print("WRITE VERIFIED: %d chars sha %s; snapshot %s; ledger merged" % (len(back), core.body_sha256(back)[:12], os.path.basename(snap)))
    return 0

if __name__ == "__main__":
    try: sys.exit(main(sys.argv[1:]))
    except RefusedWrite as e: sys.stderr.write("REFUSED: %s\n" % e); sys.exit(1)
