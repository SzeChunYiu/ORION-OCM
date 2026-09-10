#!/usr/bin/env python3
"""Self-test for verify_freeze_chain.py.

A checker that has never been shown to FIRE is not a checker. This asserts all
four directions on the REAL tree, including the no-alarm case, and fails if any
direction is wrong. Exit 0 = the checker behaves; exit 1 = the checker is broken.
"""
import json, os, shutil, subprocess, sys, tempfile

DIR = os.path.dirname(os.path.abspath(__file__))
CHECKER = "verify_freeze_chain.py"


def run(tree):
    return subprocess.run([sys.executable, os.path.join(tree, CHECKER)],
                          capture_output=True, text=True).returncode


def stage(root, name):
    """Stage the freeze directory AND any sibling directory its amendments
    name (AM-2-P1-PIPELINE binds ../independent-authorship-gate-v1/*, since
    verify_freeze_chain.py resolves manifest keys against this directory).
    Without the sibling, every staged case would false-alarm on FILE MISSING.
    """
    layout = os.path.join(root, name)
    os.makedirs(layout)
    dst = os.path.join(layout, os.path.basename(DIR))
    shutil.copytree(DIR, dst)
    for key in _cross_directory_targets():
        shutil.copytree(os.path.normpath(os.path.join(DIR, key)),
                        os.path.normpath(os.path.join(dst, key)))
    return dst


def _cross_directory_targets():
    """../<dir>/... manifest keys recorded by any amendment or freeze here."""
    targets = set()
    for fname in sorted(os.listdir(DIR)):
        if not (fname.startswith("FREEZE") and fname.endswith(".json")):
            continue
        try:
            doc = json.load(open(os.path.join(DIR, fname)))
        except ValueError:
            continue
        docs = [doc] + [a for a in doc.get("amendments", []) if isinstance(a, dict)]
        for d in docs:
            man = d.get("manifest_sha256")
            if not isinstance(man, dict):
                continue
            for key in man:
                if isinstance(key, str) and key.startswith("../"):
                    targets.add("/".join(key.split("/")[:2]))
    return sorted(targets)


def main():
    fails = []
    with tempfile.TemporaryDirectory() as root:
        # 1. clean tree must NOT alarm
        t = stage(root, "clean")
        rc = run(t)
        if rc != 0:
            fails.append(f"clean tree returned {rc}, expected 0 (FALSE ALARM)")

        # 2. tampering a file whose authority is an amendment must be caught
        t = stage(root, "amended")
        with open(os.path.join(t, "D19_D20_PROTOCOL_V1.json"), "a") as fh:
            fh.write("\n")
        rc = run(t)
        if rc != 2:
            fails.append(f"tampered amended file returned {rc}, expected 2 (MISS)")

        # 3. tampering a file asserted untouched must be caught
        t = stage(root, "unamended")
        with open(os.path.join(t, "THEOREM_REGISTRY_V1.json"), "a") as fh:
            fh.write("\n")
        rc = run(t)
        if rc != 2:
            fails.append(f"tampered unamended file returned {rc}, expected 2 (MISS)")

        # 4. cannot-check must be DISTINCT from both verified and drift
        t = stage(root, "unparseable")
        with open(os.path.join(t, "FREEZE_V1.json"), "w") as fh:
            fh.write("{ broken")
        rc = run(t)
        if rc != 3:
            fails.append(f"unparseable freeze returned {rc}, expected 3 "
                         f"('could not check' must never read as 'checked and fine')")

        t = stage(root, "absent")
        for n in os.listdir(t):
            if n.startswith("FREEZE") and n.endswith(".json"):
                os.remove(os.path.join(t, n))
        rc = run(t)
        if rc != 3:
            fails.append(f"absent freeze returned {rc}, expected 3")

    if fails:
        for f in fails:
            print("SELFTEST FAIL:", f)
        return 1
    print("SELFTEST OK: no-alarm holds, both tamper directions fire, "
          "cannot-check is distinct from both")
    return 0


if __name__ == "__main__":
    sys.exit(main())
