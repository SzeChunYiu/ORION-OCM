"""Custody gate: assert the freeze commits precede every implementation.

A freeze that postdates its result is what #976 filed as POST_HOC_SUSPECT. This
runs in CI and fails the build if the order is not provable from git.

Checks, for each of the three freezes:
  1. the freeze commit exists and is an ancestor of HEAD;
  2. the freeze commit's tree contains that freeze file;
  3. the freeze commit's tree contains NONE of the implementation, test,
     receipt or REAL_RUNS paths it is supposed to precede.

Usage: python3 -I -B check_freeze_order_v1.py [<repo root>]
"""
import os
import subprocess
import sys

PKG = "research/gmi-833-real-developmental-validation-v1"
GIT = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"

# freeze sha -> (file that must be present, paths that must be ABSENT)
IMPL = [
    PKG + "/real_dev_validation_v1.py",
    PKG + "/oracle_real_dev_validation_v1.py",
    PKG + "/train_real_systems_v1.py",
    PKG + "/train_continual_v1.py",
    PKG + "/train_continual_v2.py",
    PKG + "/train_continual_v3.py",
    PKG + "/test_real_dev_validation_v1.py",
    PKG + "/derivation_v1.py",
    PKG + "/oracle_derivation_v1.py",
    PKG + "/test_derivation_v1.py",
    PKG + "/RESULT_V1.json",
    PKG + "/DERIVATION_RESULT_V1.json",
    PKG + "/ORACLE_DERIVATION_RESULT_V1.json",
]
FREEZES = [
    ("808054d94dcdc188b7ef3e72cd55c18265ef22af", PKG + "/FREEZE_V1.md", IMPL, "REAL_RUNS/"),
    ("bdf2cdab719396f67b8feef9834a25d45ef40103", PKG + "/FREEZE_V2_REVIVAL.md",
     [PKG + "/train_continual_v2.py"], "REAL_RUNS/cl2_"),
    ("8ada2a533e24d96f569ee2d0ea64406c496ae464", PKG + "/FREEZE_V3_REVIVAL.md",
     [PKG + "/train_continual_v3.py"], "REAL_RUNS/cl3_"),
]


def run(args, root):
    p = subprocess.Popen([GIT, "-C", root] + args, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    failures = []
    for sha, freeze_file, forbidden, forbidden_prefix in FREEZES:
        rc, _out, err = run(["cat-file", "-e", sha + "^{commit}"], root)
        if rc != 0:
            failures.append("FREEZE_COMMIT_MISSING:%s (%s)" % (sha, err.strip()))
            continue
        rc, _o, _e = run(["merge-base", "--is-ancestor", sha, "HEAD"], root)
        if rc != 0:
            failures.append("FREEZE_NOT_ANCESTOR_OF_HEAD:%s" % sha)
        rc, out, _e = run(["ls-tree", "-r", "--name-only", sha, "--", PKG], root)
        if rc != 0:
            failures.append("CANNOT_LIST_FREEZE_TREE:%s" % sha)
            continue
        names = [l.strip() for l in out.splitlines() if l.strip()]
        if freeze_file not in names:
            failures.append("FREEZE_FILE_ABSENT_AT_FREEZE:%s:%s" % (sha, freeze_file))
        for bad in forbidden:
            if bad in names:
                failures.append("IMPLEMENTATION_REACHABLE_FROM_FREEZE:%s:%s" % (sha, bad))
        for n in names:
            if forbidden_prefix and (PKG + "/" + forbidden_prefix) in n:
                failures.append("OUTCOME_REACHABLE_FROM_FREEZE:%s:%s" % (sha, n))
    if failures:
        sys.stderr.write("FREEZE ORDER VIOLATIONS:\n")
        for f in failures:
            sys.stderr.write("  " + f + "\n")
        sys.exit(1)
    print("freeze order OK: %d freezes, each an ancestor of HEAD with no "
          "implementation or outcome artifact reachable" % len(FREEZES))


if __name__ == "__main__":
    main()
