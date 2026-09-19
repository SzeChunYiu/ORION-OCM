# -*- coding: utf-8 -*-
"""Custody gate: the freeze must precede every implementation and every receipt.

From git alone: (1) the freeze commit exists and is an ancestor of HEAD; (2) its tree
holds FREEZE_V1.md and FREEZE_ROWS_V1.json; (3) it holds NONE of the implementation or
receipt paths; (4) NEGATIVE CONTROL -- a file known to be at the freeze is found, so a
path typo cannot make (2)/(3) vacuously green; (5) squash-safe -- the first commit
touching the package must CARRY the freeze.  If the freeze commit is unreachable the
verdict is the distinct state UNREACHABLE (exit 2), never a pass.

    python3 -I -B check_freeze_order_v1.py [<repo root>]
"""
import os
import subprocess
import sys

PKG = "research/gmi-833-aj15-flagship-experiment-v1"
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"
FREEZE_COMMIT = "793e3548db7b06ee998b374ace49043c14070f67"
FREEZE_FILES = [PKG + "/FREEZE_V1.md", PKG + "/FREEZE_ROWS_V1.json"]
MUST_BE_ABSENT = [PKG + "/" + f for f in (
    "SEARCH_CONFIG_V1.json", "aj15_flagship_v1.py", "independent_oracle_v1.py",
    "posthoc_adjudicate_v1.py", "apply_aj13_aj14_v1.py", "independent_ladder_oracle_v1.py",
    "BLIND_OUTCOME_V1.json", "ORACLE_RESULT_V1.json", "POSTHOC_RESULT_V1.json",
    "LADDER_RESULT_V1.json", "LADDER_ORACLE_RESULT_V1.json", "RESULT_V1.json",
    "MANIFEST_V1.json", "CORE.md", "AJ15_THEOREMS_V1.md", "PARENT_OWNERSHIP_V1.md",
    "check_freeze_order_v1.py", "check_receipt_v1.py", "build_result_v1.py",
    "build_manifest_v1.py", "build_reconciliation_v1.py", "ra1_citation_audit_v1.py",
    "test_aj15_flagship_v1.py", "ISSUE_833_COMMENT_RECONCILIATION_V1.json",
    "RA1_AUDIT_RESULT_V1.json", "CITATION_TABLE_V1.json")]
NEGATIVE_CONTROL = PKG + "/FREEZE_V1.md"


def run(root, args):
    p = subprocess.Popen([GIT, "-C", root] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, e = p.communicate()
    return p.returncode, o.decode("utf-8", "replace"), e.decode("utf-8", "replace")


def check(root):
    rc, _o, err = run(root, ["cat-file", "-e", FREEZE_COMMIT + "^{commit}"])
    if rc != 0:
        return "UNREACHABLE", ["FREEZE_COMMIT_UNREACHABLE:%s (%s)" % (FREEZE_COMMIT, err.strip())]
    failures = []
    rc, _o, _e = run(root, ["merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD"])
    if rc != 0:
        failures.append("FREEZE_NOT_ANCESTOR_OF_HEAD")
    rc, out, _e = run(root, ["ls-tree", "-r", "--name-only", FREEZE_COMMIT, "--", PKG])
    if rc != 0:
        return "UNREACHABLE", failures + ["CANNOT_LIST_FREEZE_TREE"]
    names = set(l.strip() for l in out.splitlines() if l.strip())
    if NEGATIVE_CONTROL not in names:
        failures.append("NEGATIVE_CONTROL_NOT_FOUND:%s" % NEGATIVE_CONTROL)
    for want in FREEZE_FILES:
        if want not in names:
            failures.append("FREEZE_FILE_ABSENT_AT_FREEZE:%s" % want)
    for bad in MUST_BE_ABSENT:
        if bad in names:
            failures.append("IMPLEMENTATION_REACHABLE_FROM_FREEZE:%s" % bad)
    rc, out, _e = run(root, ["log", "--reverse", "--format=%H", "--", PKG + "/"])
    first = out.split()[0] if rc == 0 and out.split() else None
    if not first:
        failures.append("NO_COMMIT_TOUCHES_PACKAGE")
    else:
        rc, out, _e = run(root, ["show", "--name-only", "--format=", first, "--", PKG])
        carried = set(l.strip() for l in out.splitlines() if l.strip())
        if PKG + "/FREEZE_V1.md" not in carried:
            failures.append("FIRST_PACKAGE_COMMIT_DOES_NOT_CARRY_THE_FREEZE:%s" % first)
        elif len(carried) > len(FREEZE_FILES):
            print("package published by squash; freeze present in publishing commit %s (%d files)" % (first[:8], len(carried)))
    return ("FAIL" if failures else "OK"), failures


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    state, failures = check(root)
    if state == "UNREACHABLE":
        sys.stderr.write("FREEZE ORDER: UNREACHABLE -- %s\n" % failures)
        return 2
    if failures:
        sys.stderr.write("FREEZE ORDER VIOLATIONS:\n" + "".join("  %s\n" % f for f in failures))
        return 1
    print("freeze order OK: %s precedes every implementation and receipt; negative control found" % FREEZE_COMMIT[:8])
    return 0


if __name__ == "__main__":
    sys.exit(main())
