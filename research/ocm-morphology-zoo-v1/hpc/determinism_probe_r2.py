#!/usr/bin/env python3
"""GS-R2 cross-host determinism probe (JOB B smoke component).

Runs the REAL gs_run.py worker end-to-end TWICE in an isolated temp-root
copy of the capsule, on the GSA6_ALL lever package (novelty gate + dedup
+ cumulative surrogate), with the archive/surrogate impls switched to the
STDLIB builtin pair so the probe runs identically on any python >= 3.8
host (laptop py3.8, LUNARC py3.11) — the pinned ribs/sklearn impls stay
pinned for scored runs; the probe checks the R2 LEVER machinery and the
receipt path, not third-party versions.

Prints exactly one PROBE_DIGEST=<sha256> line: the digest of the run
output's deterministic content (counts, viable counts, distinct survivor
phenotype digests, receipt chain head).  The dispatcher compares this
digest across hosts; any mismatch = nondeterminism, campaign halts.

Usage: python3 hpc/determinism_probe_r2.py <CAPSULE_ROOT> [--pinned]
  default: builtin impls (cross-host, laptop py3.8 vs LUNARC py3.11)
  --pinned: keep the freeze-pinned impls (on-host ribs/sklearn check)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(sys.argv[1])
PINNED = "--pinned" in sys.argv[2:]
FREEZE_NAME = "GRAND_SEARCH_R2_FREEZE.json"
SPEC = {"task_id": "DET2probe", "base_arm": "GSA6_ALL", "seed": 7,
        "t0_budget": 162, "n0": 81}


def result_digest(path: str) -> str:
    d = json.load(open(path))
    det = {
        "run_id": d["run_id"], "arm": d["arm"], "seed": d["seed"],
        "algorithm": d["algorithm"], "rounds": d["rounds"],
        "counts": d["counts"], "viable_counts": d["viable_counts"],
        "distinct_t2_viable_phenotypes": d["distinct_t2_viable_phenotypes"],
        "revival_levers": d["revival_levers"],
        "survivor_digests": sorted(
            s["phenotype_digest"] for s in d["survivors"]),
        "receipt_records": [
            {"index": r["index"],
             "payload": {k: v for k, v in r["payload"].items()
                         if k != "cpu_hours"}}  # timing-free content only
            for r in d["receipt"]["chain"]],
    }
    return hashlib.sha256(
        json.dumps(det, sort_keys=True).encode()).hexdigest()


def one_run(tmp: str, tag: str) -> str:
    rdir = os.path.join(tmp, tag)
    shutil.copytree(ROOT, rdir, ignore=shutil.ignore_patterns(
        "results", "logs", "archives", "manifests", "__pycache__"))
    for d in ("results", "logs", "archives", "manifests/receipts"):
        os.makedirs(os.path.join(rdir, d), exist_ok=True)
    frz = json.load(open(os.path.join(rdir, FREEZE_NAME)))
    if not PINNED:
        # builtin impls for the probe ONLY (temp copy; scored runs keep
        # the freeze-pinned ribs/sklearn pair — never edits the root)
        frz["environment"]["novelty_archive_impl"] = "builtin"
        frz["environment"]["surrogate_impl"] = "builtin"
    with open(os.path.join(rdir, FREEZE_NAME), "w") as fh:
        json.dump(frz, fh, indent=2, sort_keys=True)
    spec_path = os.path.join(rdir, "det_spec.json")
    SPEC["freeze_sha256"] = hashlib.sha256(
        open(os.path.join(rdir, FREEZE_NAME), "rb").read()).hexdigest()
    with open(spec_path, "w") as fh:
        json.dump(SPEC, fh, sort_keys=True)
    env = dict(os.environ, GS_RUN_PREFIX="GS_R2_", GS_FREEZE_NAME=FREEZE_NAME)
    p = subprocess.run(
        [sys.executable, os.path.join(rdir, "hpc", "gs_run.py"),
         rdir, "GSA6_ALL", str(SPEC["seed"]), spec_path],
        capture_output=True, text=True, env=env, cwd=rdir)
    out = os.path.join(rdir, "results", "GS_R2_DET2probe.json")
    assert p.returncode == 0 and os.path.exists(out), (
        "probe run failed:\n%s\n%s" % (p.stdout[-500:], p.stderr[-800:]))
    return result_digest(out)


def main() -> None:
    assert os.path.exists(os.path.join(ROOT, FREEZE_NAME)), (
        "no %s in %s — probe requires a frozen R2 capsule" % (FREEZE_NAME,
                                                              ROOT))
    tmp = tempfile.mkdtemp(prefix="gs2det_")
    try:
        d1 = one_run(tmp, "a")
        d2 = one_run(tmp, "b")
        assert d1 == d2, "same-host nondeterminism: %s != %s" % (d1, d2)
        print("PROBE_HOST=%s PY=%s IMPLS=%s" % (
            os.uname().nodename, sys.version.split()[0],
            "pinned" if PINNED else "builtin"))
        print("%s=%s" % ("PROBE_PINNED_DIGEST" if PINNED
                         else "PROBE_DIGEST", d1))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
