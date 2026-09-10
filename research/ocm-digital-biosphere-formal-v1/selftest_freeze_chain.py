#!/usr/bin/env python3
"""Self-test the biosphere freeze verifier BEFORE trusting its verdicts.

Mirrors the HSG lane's "self-test the checker before trusting it" CI step. A
checker that has only ever been seen returning VERIFIED has not been validated,
and one that cries wolf on its first real run gets switched off. Both
directions are asserted here on synthetic trees, so this never touches the real
freeze.

Exit 0 on success; any assertion failure is a hard CI failure.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

DIR = os.path.dirname(os.path.abspath(__file__))
VERIFIER = os.path.join(DIR, "verify_freeze_chain.py")


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _run(tmp):
    """Run a copy of the verifier rooted at tmp; return its exit code."""
    shutil.copy(VERIFIER, os.path.join(tmp, "verify_freeze_chain.py"))
    p = subprocess.run([sys.executable, os.path.join(tmp, "verify_freeze_chain.py")],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def _tree(tmpdir, files, freeze):
    for name, content in files.items():
        with open(os.path.join(tmpdir, name), "wb") as fh:
            fh.write(content)
    with open(os.path.join(tmpdir, "FREEZE_V1.json"), "w") as fh:
        json.dump(freeze, fh, indent=1)


def main():
    results = {}

    # 1. no-alarm: manifest matches the tree -> VERIFIED (0)
    with tempfile.TemporaryDirectory() as t:
        a = b"alpha\n"
        _tree(t, {"A.md": a}, {"manifest_sha256": {"A.md": _sha(a)}, "amendments": []})
        code, out = _run(t)
        assert code == 0, "no-alarm case did not verify: %s %s" % (code, out)
        results["no_alarm_matching"] = code

    # 2. alarm: a file changed with no amendment recording it -> DRIFT (2)
    with tempfile.TemporaryDirectory() as t:
        a = b"alpha\n"
        _tree(t, {"A.md": b"TAMPERED\n"}, {"manifest_sha256": {"A.md": _sha(a)}, "amendments": []})
        code, out = _run(t)
        assert code == 2, "unrecorded drift did not fire: %s %s" % (code, out)
        results["alarm_unrecorded_drift"] = code

    # 3. no-alarm DISCRIMINATOR: the same changed file, but a NUMBERED amendment
    #    records its CURRENT hash -> VERIFIED (0). Without this, case 2 could
    #    just mean the checker flags every change, amendment discipline or not.
    with tempfile.TemporaryDirectory() as t:
        new = b"TAMPERED\n"
        _tree(t, {"A.md": new}, {
            "manifest_sha256": {"A.md": _sha(b"alpha\n")},
            "amendments": [{"id": 1, "manifest_sha256": {"A.md": _sha(new)}}],
        })
        code, out = _run(t)
        assert code == 0, "recorded amendment reported as drift: %s %s" % (code, out)
        results["no_alarm_recorded_amendment"] = code

    # 4. alarm: a recorded file is missing entirely -> DRIFT (2)
    with tempfile.TemporaryDirectory() as t:
        _tree(t, {}, {"manifest_sha256": {"GONE.md": _sha(b"x")}, "amendments": []})
        code, out = _run(t)
        assert code == 2, "missing file did not fire: %s %s" % (code, out)
        results["alarm_missing_file"] = code

    # 5. cannot-check: no freeze file at all -> CANNOT_CHECK (3), never VERIFIED
    with tempfile.TemporaryDirectory() as t:
        code, out = _run(t)
        assert code == 3, "absent freeze reported as %s, not CANNOT_CHECK: %s" % (code, out)
        results["cannot_check_no_freeze"] = code

    # 6. cannot-check: unparseable freeze -> CANNOT_CHECK (3)
    with tempfile.TemporaryDirectory() as t:
        with open(os.path.join(t, "FREEZE_V1.json"), "w") as fh:
            fh.write("{not json")
        code, out = _run(t)
        assert code == 3, "unparseable freeze reported as %s: %s" % (code, out)
        results["cannot_check_unparseable"] = code

    # 7. no-alarm: prior_manifest_sha256_observed must NOT be double-counted as
    #    an authoritative manifest of this freeze's own files. It names another
    #    lane's paths, resolved against the repo root, so treating it as local
    #    would report FALSE drift.
    with tempfile.TemporaryDirectory() as t:
        a = b"alpha\n"
        _tree(t, {"A.md": a}, {
            "manifest_sha256": {"A.md": _sha(a)},
            "prior_manifest_sha256_observed": {},
            "amendments": [],
        })
        code, out = _run(t)
        assert code == 0, "empty prior_manifest caused a false alarm: %s %s" % (code, out)
        results["no_alarm_prior_manifest_not_double_counted"] = code

    print(json.dumps({"FREEZE_CHAIN_SELFTEST": "OK", "cases": results}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
