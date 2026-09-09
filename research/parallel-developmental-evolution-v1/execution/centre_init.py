"""Centre: bootstrap a run root.  Idempotent; refuses to reset a live run.

Usage: centre_init.py --run-root R [--protocol P]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for entry in (HERE, HERE.parent):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import pdev_io as IO  # noqa: E402
import pdev_grammar as G  # noqa: E402
import pdev_machine as M  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-root", required=True)
    args = ap.parse_args()
    paths = IO.run_paths(args.run_root)
    if paths["state"].exists():
        raise SystemExit("run root already initialized")
    state = {
        "schema": "pdev217.run_state.v1",
        # The canonical lineage CONTINUES from the parent's g2: our first
        # adoption would be g3, earned only through a full M11 cycle.
        "generation": 2,
        "incumbent": {"config": dict(M.G2_MORPHOLOGY),
                      "digest": G.digest(M.G2_MORPHOLOGY)},
        "parent_ceiling": "g2 (AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION)",
        "adoptions": 0,
        "attempted_cycles": 0,
        "waves_run": 0,
    }
    IO.write_json(paths["state"], state)
    IO.write_json(paths["manifests"] / "BATCH.json",
                  {"schema": "pdev217.batch_manifest.v1", "waves": []})
    print("initialized run root at %s (generation=2, incumbent=%s)"
          % (args.run_root, state["incumbent"]["digest"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
