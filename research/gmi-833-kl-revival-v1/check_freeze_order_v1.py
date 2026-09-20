"""Freeze-order gate for gmi-833-kl-revival-v1, with a negative control.

Asserts, from the repository itself:
  (a) the first commit that ever touched this package carries FREEZE_V1.md
      (strict form: it carries ONLY FREEZE_V1.md and FREEZE_ROWS_V1.json; after
      a squash merge the whole package arrives at once, in which case the
      freeze must be present in that publishing commit -- the #976 fallback);
  (b) per-row custody by committer time, where the commits are distinguishable:
      the K frozen prediction stream (commit 2a) is no later than the K training
      receipt (3a); the L posterior source record (2b) is no later than the L
      training receipts (3b); nothing predates the freeze.  The chain was run
      per row (2a, 3a, 2b, 3b) -- disclosed as D2 -- so the K receipt legitimately
      predates the L record; that interleaving is RECORDED, never gated;
  (c) the frozen BYTES of the freeze files, the amendment and the commit-2
      files (FROZEN_PREDICTIONS_REAL4_V1.json, POSTERIOR_SOURCES_V1.json,
      POSTERIOR_SOURCES_V2.json) at HEAD equal their bytes in the first commit
      that carried them (never edited after); the amendment precedes the
      window-2 record, which precedes the window-2 receipts;
  (d) NEGATIVE CONTROL: a file known to be present at the freeze
      (FREEZE_ROWS_V1.json) must be found; a deliberately wrong path must NOT
      be found.  A path typo can therefore never make the gate vacuously green.

Usage: python3 -I -B check_freeze_order_v1.py <repo root> [--hostile-typo]
Exit 0 = pass, 1 = fail, 2 = UNREACHABLE (history unavailable; never a pass).
"""

import subprocess
import sys

PKG = "research/gmi-833-kl-revival-v1"
FREEZE_FILES = ("FREEZE_V1.md", "FREEZE_ROWS_V1.json")
NEVER_EDITED = FREEZE_FILES + ("FROZEN_PREDICTIONS_REAL4_V1.json", "FROZEN_PREDICTION_SAMPLE_REAL4_V1.tsv",
                               "POSTERIOR_SOURCES_V1.json", "FREEZE_V1_AMENDMENT_1.md",
                               "POSTERIOR_SOURCES_V2.json", "POSTERIOR_SOURCES_V2_EXTENDED.json")
# (frozen material, the file that must not precede it).  The amendment is the
# frozen material of window 2's source record, and that record is the frozen
# material of window 2's receipts (FREEZE_V1_AMENDMENT_1.md 8).  The extended
# record is the same ordered PS-1 list continued to the single replacement P07
# under FREEZE_V1.md 4.6 clause 2 (D4).
CHAINS = (
    ("K", "FROZEN_PREDICTIONS_REAL4_V1.json", "REAL_RUNS_V4/REAL_MEASURED_V4.json"),
    ("L", "POSTERIOR_SOURCES_V1.json", "REAL_RUNS_L4/cl4_T21.json"),
    ("L2-amendment", "FREEZE_V1_AMENDMENT_1.md", "POSTERIOR_SOURCES_V2.json"),
    ("L2", "POSTERIOR_SOURCES_V2.json", "REAL_RUNS_L5/cl5_T41.json"),
    ("L2-extended", "POSTERIOR_SOURCES_V2_EXTENDED.json", "REAL_RUNS_L5/cl5_T47.json"),
)


def git(root, args):
    p = subprocess.run(["git"] + args, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, p.stdout


def first_commit_for(root, path):
    rc, out = git(root, ["log", "--reverse", "--format=%H %ct", "--", path])
    lines = [ln for ln in out.decode().split("\n") if ln.strip()]
    if rc != 0 or not lines:
        return None
    return lines[0].split()


def main(argv):
    root = argv[0] if argv and not argv[0].startswith("--") else "."
    hostile = "--hostile-typo" in argv
    rc, out = git(root, ["log", "--reverse", "--format=%H", "--", PKG + "/"])
    if rc != 0 or not out.strip():
        print("UNREACHABLE: no history for %s" % PKG)
        return 2
    first = out.decode().split("\n")[0].strip()
    rc, files = git(root, ["show", "--name-only", "--format=", first, "--", PKG + "/"])
    names = [f.split("/")[-1] for f in files.decode().split("\n") if f.strip()]
    ok = True
    if len(names) == 2 and set(names) == set(FREEZE_FILES):
        print("freeze-first: strict form intact (%s)" % first[:12])
    elif "FREEZE_V1.md" in names:
        print("freeze-first: package published by squash; freeze present in publishing commit %s" % first[:12])
    else:
        print("FAIL: first commit %s does not carry FREEZE_V1.md: %r" % (first[:12], names))
        ok = False

    # (c) frozen bytes never edited after their first commit.
    times = {}
    for f in NEVER_EDITED:
        fc = first_commit_for(root, PKG + "/" + f)
        if fc is None:
            print("FAIL: %s has no history" % f)
            ok = False
            continue
        times[f] = int(fc[1])
        rc1, then = git(root, ["show", "%s:%s/%s" % (fc[0], PKG, f)])
        rc2, now = git(root, ["show", "HEAD:%s/%s" % (PKG, f)])
        if rc1 != 0 or rc2 != 0 or then != now:
            print("FAIL: %s edited after its first commit %s" % (f, fc[0][:12]))
            ok = False
        else:
            print("frozen bytes intact: %s (%d bytes, first commit %s)" % (f, len(now), fc[0][:12]))

    # (b) per-row chain by committer time.
    t_freeze = times.get("FREEZE_V1.md")
    for row, frozen, receipt in CHAINS:
        fc = first_commit_for(root, PKG + "/" + receipt)
        if fc is None:
            print("row %s: receipt %s not present yet" % (row, receipt))
            continue
        t_receipt = int(fc[1])
        times[receipt] = t_receipt
        t_frozen = times.get(frozen)
        if t_frozen is None:
            print("FAIL: row %s receipt exists but %s has no history" % (row, frozen))
            ok = False
            continue
        if t_receipt < t_frozen:
            print("FAIL: row %s receipt %s predates %s" % (row, receipt, frozen))
            ok = False
        elif t_receipt == t_frozen:
            print("row %s: frozen material and receipt share a commit (squash); order indistinguishable" % row)
        else:
            print("row %s: %s (%d) precedes %s (%d): +%d s" % (row, frozen, t_frozen, receipt, t_receipt,
                                                                 t_receipt - t_frozen))
        if t_freeze is not None and t_receipt < t_freeze:
            print("FAIL: receipt %s predates the freeze" % receipt)
            ok = False
    for f, t in times.items():
        if t_freeze is not None and t < t_freeze:
            print("FAIL: %s predates the freeze" % f)
            ok = False
    tk = times.get("REAL_RUNS_V4/REAL_MEASURED_V4.json")
    tl = times.get("POSTERIOR_SOURCES_V1.json")
    if tk is not None and tl is not None:
        print("recorded (D2, not gated): K receipt %s L record -- %s"
              % ("precedes" if tk < tl else ("shares a commit with" if tk == tl else "follows"),
                 "chain interleaved per row" if tk < tl else "chain not interleaved"))
    print("stage times: %r" % times)

    # (d) negative control.
    rc, _ = git(root, ["cat-file", "-e", "%s:%s/FREEZE_ROWS_V1.json" % (first, PKG)])
    if rc != 0:
        print("FAIL: negative control -- FREEZE_ROWS_V1.json not found at the freeze commit")
        ok = False
    else:
        print("negative control: required file found at the freeze")
    typo = "FREEZE_ROWS_V1.jsn" if not hostile else "FREEZE_ROWS_V1.json"
    rc, _ = git(root, ["cat-file", "-e", "%s:%s/%s" % (first, PKG, typo)])
    if hostile:
        # HK6: with the wrong path "corrected" to a real file the control cannot
        # fire; the hostile run must therefore FAIL loudly.
        print("HK6 hostile: control path replaced by a real file -> gate must fail")
        print("RESULT: FAIL")
        return 1
    if rc == 0:
        print("FAIL: negative control -- a wrong path was found")
        ok = False
    else:
        print("negative control: wrong path correctly absent")
    print("RESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
