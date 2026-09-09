"""Array worker: run the full hostile battery + shadow suites for ONE
surviving candidate.  Writes exactly one verify JSON.  Never touches lineage
state, archive, or search history.

The dev measurement is REUSED from the eval stage (same frozen measurement);
the shadow suites (target/preservation/harmful/fresh/relabel) are executed
fresh here, and the audit hostiles re-run the meter on the frozen audit suite
(independent re-measurement, charged).

Usage: worker_verify.py --run-root R --generation G --wave W --index I
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
for entry in (HERE, HERE.parent):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import pdev_io as IO  # noqa: E402
import pdev_grammar as G  # noqa: E402
import pdev_runner as R  # noqa: E402
import pdev_hostiles as H  # noqa: E402

SCHEMA = "pdev217.verify_row.v1"
MEMORIZATION_DROP_BOUND = 1  # frozen: at most one task's success may drop
QUALITY_MARGIN = 0.0         # frozen: strict noninferiority on preservation


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--generation", type=int, required=True)
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--index", type=int, required=True)
    args = ap.parse_args()

    wdir = IO.wave_dir(args.run_root, args.generation, args.wave)
    batch = IO.read_json(wdir / "verify_batch.json")
    suites = IO.load_suites(args.run_root, args.generation)
    incumbent = IO.read_json(IO.gen_dir(args.run_root, args.generation)
                             / "incumbent.json")
    if not 0 <= args.index < len(batch["candidates"]):
        raise SystemExit("array index outside frozen verify denominator")
    cand = batch["candidates"][args.index]
    envelope = IO.execution_envelope("verify", args.index)

    eval_full = IO.read_json(wdir / "eval" / (cand["candidate_id"] + ".full.json"))
    dev_result = eval_full["result"]

    started = time.time()
    status = "VERIFIED"
    error = ""
    try:
        suite_results = {}
        for name in ("target", "preservation", "harmful", "fresh", "relabel"):
            suite_results[name] = R.runner(cand["config"], suites[name])
        ctx = {
            "audit_tasks": suites["audit"],
            "memorization_drop_bound": MEMORIZATION_DROP_BOUND,
            "quality_margin": QUALITY_MARGIN,
            "incumbent_config": incumbent["config"],
            "archive_digests": batch.get("archive_digests", []),
        }
        receipts = H.run_hostiles(cand["config"], dev_result, suite_results,
                                  incumbent["suites"], ctx)
    except Exception:
        status = "CRASHED"
        error = traceback.format_exc(limit=6)
        suite_results, receipts = {}, []

    failing = [r["hostile_id"] for r in receipts
               if r["status"] == "FAIL"]
    integrity_fail = [r["hostile_id"] for r in receipts
                      if r["hostile_id"] in H.INTEGRITY_HOSTILES
                      and r["status"] != "PASS"]
    row = {
        "schema": SCHEMA,
        "candidate_id": cand["candidate_id"],
        "digest": cand["digest"],
        "config": cand["config"],
        "arm": cand["arm"],
        "origin": cand["origin"],
        "change_class": cand["change_class"],
        "generation": args.generation,
        "wave": args.wave,
        "status": status,
        "error": error,
        "hostiles": receipts,
        "failing_hostiles": failing,
        "integrity_failures": integrity_fail,
        "shadow": {name: {"n": res["n"], "success": res["success"],
                          "violations": res["preservation_violations"],
                          "work": res["resources"]["work"],
                          "persistent_bytes": res["resources"]["persistent_bytes"]}
                   for name, res in suite_results.items()},
        "envelope": envelope,
        "elapsed_s": round(time.time() - started, 3),
    }
    IO.write_json(wdir / "verify" / (cand["candidate_id"] + ".json"), row)
    print("%s hostiles_fail=%d integrity_fail=%d"
          % (cand["candidate_id"], len(failing), len(integrity_fail)))
    return 0 if status == "VERIFIED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
