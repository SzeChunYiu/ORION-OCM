"""Array worker (PDEV-2 / PDEV-11): evaluate ONE serial-control or parent-arm
entry on the generation's frozen dev suite through the SAME frozen meter.

Entries in the parent batch (written by the centre before submission):

* ``PARENT``     the #149 g2 morphology, fixed forever -- the matched
                 never-adopting parent arm, re-measured on every generation's
                 suite (matched parent arm jobs).
* ``CONTINUED``  the serial self-change control continuing from g2.
* ``RESET``      the serial self-change control reset to the donor's initial
                 morphology (discovering/learned), same procedure.

Each serial arm's incumbent + its frozen single-dimension neighbourhood are
evaluated; the centre (never a worker) advances each serial state by at most
ONE adoption per generation under the pre-frozen scalar rule.

Usage: worker_parent.py --run-root R --generation G --index I
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
import pdev_machine as M  # noqa: E402

SCHEMA = "pdev217.parent_row.v1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--generation", type=int, required=True)
    ap.add_argument("--index", type=int, required=True)
    args = ap.parse_args()

    gdir = IO.gen_dir(args.run_root, args.generation)
    batch = IO.read_json(gdir / ("parent_batch_g%d.json" % args.generation))
    suites = IO.load_suites(args.run_root, args.generation)
    if not 0 <= args.index < len(batch["entries"]):
        raise SystemExit("array index outside frozen parent denominator")
    entry = batch["entries"][args.index]
    envelope = IO.execution_envelope("parent", args.index)

    started = time.time()
    status = "MEASURED"
    error = ""
    try:
        result = R.runner(entry["config"], suites["dev"])
    except Exception:
        status = "CRASHED"
        error = traceback.format_exc(limit=6)
        result = {"n": 0, "success": 0, "preservation_violations": -1,
                  "resources": {"work": -1, "persistent_bytes": -1}}

    row = {
        "schema": SCHEMA,
        "entry_id": entry["entry_id"],
        "kind": entry["kind"],
        "arm": entry["arm"],
        "config": entry["config"],
        "digest": G.digest(entry["config"]),
        "generation": args.generation,
        "status": status,
        "error": error,
        "n": result["n"],
        "success": result["success"],
        "preservation_violations": result["preservation_violations"],
        "work": result["resources"]["work"],
        "persistent_bytes": result["resources"]["persistent_bytes"],
        "envelope": envelope,
        "elapsed_s": round(time.time() - started, 3),
    }
    out = gdir / "parents"
    IO.write_json(out / (entry["entry_id"] + ".json"), row)
    print("%s status=%s work=%s" % (entry["entry_id"], status, row["work"]))
    return 0 if status == "MEASURED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
