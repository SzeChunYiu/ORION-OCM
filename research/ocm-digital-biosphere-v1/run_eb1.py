#!/usr/bin/env python3
"""Run EB-1 microscopies + throughput. Not scored Earths."""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exploits  # noqa: E402
import lib  # noqa: E402
import throughput  # noqa: E402


def main() -> int:
    root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else HERE
    micros = exploits.run_all()
    open_ex = [m for m in micros if m.get("status") == "EXPLOIT_OPEN"]
    micro_path = os.path.join(root, "results", "EB1_MICROSCOPY.json")
    micro_obj = {
        "schema": "EB1_MICROSCOPY_V1",
        "ts": lib.now(),
        "n": len(micros),
        "open_exploits": [m["name"] for m in open_ex],
        "results": micros,
        "gate": "FAIL_OPEN_EXPLOIT" if open_ex else "PHYSICS_HOLDS",
    }
    sha_m = lib.write_json(micro_path, micro_obj)
    probe = throughput.probe(ticks=120, grid=12)
    rec = throughput.recommend_ensemble(probe["ticks_per_s"])
    tp_path = os.path.join(root, "results", "THROUGHPUT_PROBE.json")
    tp_obj = {
        "schema": "THROUGHPUT_PROBE_V1",
        "ts": lib.now(),
        "probe": probe,
        "recommend": rec,
    }
    sha_t = lib.write_json(tp_path, tp_obj)
    lib.event("eb1_microscopy", sha256=sha_m, gate=micro_obj["gate"])
    lib.event("eb1_throughput", sha256=sha_t, ticks_per_s=probe["ticks_per_s"])
    print("EB1", micro_obj["gate"], "ticks/s", probe["ticks_per_s"])
    if open_ex:
        print("OPEN", [m["name"] for m in open_ex])
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
