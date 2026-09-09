"""Array worker: evaluate ONE wave candidate on the generation's frozen dev
suite through the frozen meter.  Writes exactly one eval JSON + one candidate
ledger row.  Never touches lineage state, archive, or search history.

Usage: worker_evaluate.py --run-root R --generation G --wave W --index I
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
import pdev_search  # noqa: E402

SCHEMA = "pdev217.eval_row.v1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--generation", type=int, required=True)
    ap.add_argument("--wave", type=int, required=True)
    ap.add_argument("--index", type=int, required=True)
    args = ap.parse_args()

    wdir = IO.wave_dir(args.run_root, args.generation, args.wave)
    batch = IO.read_json(wdir / "batch.json")
    suites = IO.load_suites(args.run_root, args.generation)
    if not 0 <= args.index < len(batch["candidates"]):
        raise SystemExit("array index outside frozen batch denominator")
    cand = batch["candidates"][args.index]
    dev_tasks = suites["dev"]
    envelope = IO.execution_envelope("evaluate", args.index)

    started = time.time()
    status = "MEASURED"
    error = ""
    try:
        result = R.runner(cand["config"], dev_tasks)
        detail = R.aggregate_details(result["details"])
    except Exception:
        status = "CRASHED"
        error = traceback.format_exc(limit=6)
        result = {"n": 0, "success": 0, "preservation_violations": -1,
                  "resources": {"work": -1, "persistent_bytes": -1}, "details": []}
        detail = {}

    row = {
        "schema": SCHEMA,
        "candidate_id": cand["candidate_id"],
        "digest": cand["digest"],
        "config": cand["config"],
        "arm": cand["arm"],
        "origin": cand["origin"],
        "change_class": cand["change_class"],
        "size": cand["size"],
        "generation": args.generation,
        "wave": args.wave,
        "status": status,
        "error": error,
        "n": result["n"],
        "success": result["success"],
        "preservation_violations": result["preservation_violations"],
        "work": result["resources"]["work"],
        "persistent_bytes": result["resources"]["persistent_bytes"],
        "detail": detail,
        "envelope": envelope,
        "elapsed_s": round(time.time() - started, 3),
    }
    IO.write_json(wdir / "eval" / (cand["candidate_id"] + ".json"), row)
    # Full per-task details (incl. per-record rows) stay in the per-candidate
    # file for the verify stage and audits; the ledger row stays aggregate.
    if status == "MEASURED":
        row_full = dict(row)
        row_full["result"] = result
        IO.write_json(wdir / "eval" / (cand["candidate_id"] + ".full.json"),
                      row_full)
        IO.append_jsonl(IO.run_paths(args.run_root)["candidate_ledger"], row)
    print("%s %s status=%s work=%s" % (cand["candidate_id"], cand["arm"],
                                       status, row["work"]))
    return 0 if status == "MEASURED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
