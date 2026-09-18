"""Custody gate: the freeze must precede every implementation and every receipt.

A freeze that postdates its result is what #976 filed as POST_HOC_SUSPECT. This
checks, from git alone:

  1. the freeze commit exists and is an ancestor of HEAD;
  2. its tree contains FREEZE_V1.md and FREEZE_ROWS_V1.json;
  3. its tree contains NONE of the executor, oracle, test or receipt paths;
  4. NEGATIVE CONTROL: a file known to be present at the freeze is found, so a
     path typo cannot make clauses 2 and 3 vacuously green;
  5. squash-safe: after publication the whole package arrives in one commit, so
     the first commit touching the package is required to CARRY the freeze
     rather than to consist of it alone.

Usage: python3 -I -B check_freeze_order_v1.py [<repo root>]
"""
import os
import subprocess
import sys

PKG = "research/gmi-833-body-residual-akl-v1"
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"
FREEZE_COMMIT = "c9dec25dad00ddde53ddadd3852c1d5fef1a0e03"

FREEZE_FILES = [PKG + "/FREEZE_V1.md", PKG + "/FREEZE_ROWS_V1.json"]
MUST_BE_ABSENT = [
    PKG + "/body_residual_akl_v1.py",
    PKG + "/oracle_route_b_v1.py",
    PKG + "/test_body_residual_akl_v1.py",
    PKG + "/check_freeze_order_v1.py",
    PKG + "/RESULT_V1.json",
    PKG + "/ORACLE_RESULT_V1.json",
    PKG + "/MANIFEST_V1.json",
    PKG + "/BODY_RESIDUAL_AKL_THEOREMS_V1.md",
    PKG + "/ISSUE_833_RECONCILIATION_BODY_RESIDUAL_V1.json",
    PKG + "/build_manifest_v1.py",
    PKG + "/build_reconciliation_v1.py",
    PKG + "/check_receipt_v1.py",
    PKG + "/CORE.md",
    PKG + "/PARENT_OWNERSHIP_V1.md",
]
# Clause 4: this file was present at the freeze. If the lookup cannot find it,
# the tree listing is wrong and every other verdict here is worthless.
NEGATIVE_CONTROL = PKG + "/FREEZE_V1.md"


def run(root, args):
    proc = subprocess.Popen([GIT, "-C", root] + args, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return proc.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def check(root):
    failures = []
    rc, _o, err = run(root, ["cat-file", "-e", FREEZE_COMMIT + "^{commit}"])
    if rc != 0:
        return ["FREEZE_COMMIT_MISSING:%s (%s)" % (FREEZE_COMMIT, err.strip())]
    rc, _o, _e = run(root, ["merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD"])
    if rc != 0:
        failures.append("FREEZE_NOT_ANCESTOR_OF_HEAD:%s" % FREEZE_COMMIT)
    rc, out, _e = run(root, ["ls-tree", "-r", "--name-only", FREEZE_COMMIT, "--", PKG])
    if rc != 0:
        return failures + ["CANNOT_LIST_FREEZE_TREE"]
    names = set(l.strip() for l in out.splitlines() if l.strip())
    if NEGATIVE_CONTROL not in names:
        failures.append("NEGATIVE_CONTROL_NOT_FOUND:%s" % NEGATIVE_CONTROL)
    for want in FREEZE_FILES:
        if want not in names:
            failures.append("FREEZE_FILE_ABSENT_AT_FREEZE:%s" % want)
    for bad in MUST_BE_ABSENT:
        if bad in names:
            failures.append("IMPLEMENTATION_REACHABLE_FROM_FREEZE:%s" % bad)

    # Clause 5, squash-safe.
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
            print("package published by squash; freeze present in the publishing "
                  "commit %s (%d files)" % (first[:8], len(carried)))
    return failures


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    failures = check(os.path.abspath(root))
    if failures:
        sys.stderr.write("FREEZE ORDER VIOLATIONS:\n")
        for f in failures:
            sys.stderr.write("  " + f + "\n")
        return 1
    print("freeze order OK: %s precedes every implementation and receipt; "
          "negative control found" % FREEZE_COMMIT[:8])
    return 0


if __name__ == "__main__":
    sys.exit(main())
