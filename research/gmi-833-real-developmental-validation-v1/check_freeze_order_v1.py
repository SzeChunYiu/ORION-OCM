"""Custody gate: the freeze commits precede every implementation.

A freeze that postdates its result is what #976 filed as POST_HOC_SUSPECT. This
runs in CI and fails the build if the order is provably violated.

Since the package was squash-published (4ba7e89c, PR #1024) the three freeze
commits below no longer sit on main's history, so "freeze is an ancestor of
HEAD" cannot be re-derived there. The check therefore delegates to the shared
squash-safe checker (research/gmi-833-squash-safe-gates-v1, parent freeze PR
#1053), which keeps the strict ordering proof on a linear history and, on a
squash-published one, withholds ONLY that assertion while still checking
everything derivable from HEAD and from the pinned freeze commits:

  1. each freeze file is present at HEAD;
  2. the pinned freeze commit, when reachable, contains that freeze file and
     NONE of the implementation, test, receipt or REAL_RUNS paths it precedes,
     and its freeze bytes are the bytes at HEAD;
  3. the squash commit that introduced the freeze is a single-parent "(#N)"
     publishing commit whose parent holds nothing of the package.

One state line per freeze. Exit 0 = OK or NOT_REDERIVABLE (with the checks
listed), 1 = violation, 2 = could not check.

Usage: python3 -I -B check_freeze_order_v1.py [<repo root>]
"""
import os
import subprocess
import sys

PKG = "research/gmi-833-real-developmental-validation-v1"
CHECKER = "research/gmi-833-squash-safe-gates-v1/squash_safe_freeze_check_v1.py"

IMPL = [
    "real_dev_validation_v1.py",
    "oracle_real_dev_validation_v1.py",
    "train_real_systems_v1.py",
    "train_continual_v1.py",
    "train_continual_v2.py",
    "train_continual_v3.py",
    "test_real_dev_validation_v1.py",
    "derivation_v1.py",
    "oracle_derivation_v1.py",
    "test_derivation_v1.py",
    "RESULT_V1.json",
    "DERIVATION_RESULT_V1.json",
    "ORACLE_DERIVATION_RESULT_V1.json",
]
# freeze sha -> (freeze file, implementation/outcome patterns that must postdate it)
FREEZES = [
    ("808054d94dcdc188b7ef3e72cd55c18265ef22af", "FREEZE_V1.md", IMPL + ["REAL_RUNS/*"]),
    ("bdf2cdab719396f67b8feef9834a25d45ef40103", "FREEZE_V2_REVIVAL.md",
     ["train_continual_v2.py", "REAL_RUNS/cl2_*"]),
    ("8ada2a533e24d96f569ee2d0ea64406c496ae464", "FREEZE_V3_REVIVAL.md",
     ["train_continual_v3.py", "REAL_RUNS/cl3_*"]),
]


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    checker = os.path.join(root, CHECKER)
    if not os.path.exists(checker):
        sys.stderr.write("FREEZE_ORDER_COULD_NOT_CHECK:SHARED_CHECKER_MISSING:%s\n" % checker)
        sys.exit(2)
    worst = 0
    for sha, freeze_file, impl in FREEZES:
        cmd = [sys.executable, "-I", "-B", checker, "--repo", root, "--pkg", PKG,
               "--freeze", freeze_file, "--freeze-commit", sha]
        for pat in impl:
            cmd += ["--impl", pat]
        rc = subprocess.call(cmd)
        worst = max(worst, rc)
    if worst == 0:
        print("freeze order: %d freezes checked, no violation (see the state lines above)"
              % len(FREEZES))
    sys.exit(worst)


if __name__ == "__main__":
    main()
