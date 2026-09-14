#!/usr/bin/env python3
"""Replay the complete frozen threshold-task frontier payload, unchanged.

The unit answers the one question the parity-n registration left open: whether
the registered coordinate can ever return a verdict in favour of a structurally
neural realization. It cannot in the opcode-only coordinate, for any task at any
n; it can once a constant cell is charged at any positive rate.
"""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
UNIT = "research/gmi-threshold-task-frontier-v1"
INSTRUMENT_UNIT = "research/gmi-delegation-cost-repair-v1"
ORIGINAL_RECEIPT = "RECEIPT_V1.json"
ENTRY = "check_frontier_v1.py"
TERMINAL = "GRAND_GMI_THRESHOLD_TASK_FRONTIER_GREEN_AT_FINITE_SCOPE"


def run(root=HERE):
    root = Path(root).resolve()
    gate = runpy.run_path(str(root / "replay_theorem_capsule_v1.py"))
    inventory = gate["load_inventory"](root)
    record = inventory["external_units"][UNIT]
    instrument = inventory["external_units"][INSTRUMENT_UNIT]
    unit = root.parent.parent / UNIT
    expected = gate["strict_json"]((unit / ORIGINAL_RECEIPT).read_text(), ORIGINAL_RECEIPT)
    with tempfile.TemporaryDirectory(prefix="gmi-ttf-source-cache-") as cache:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}", str(unit / ENTRY)],
            cwd=unit, capture_output=True, text=True, timeout=60)
    gate["require"](result.returncode == 0 and result.stderr == "",
                    "threshold-task frontier checker failed: " + result.stderr[-1000:])
    actual = gate["strict_json"](result.stdout, "threshold-task frontier stdout")
    gate["require"](gate["canonical"](actual) == gate["canonical"](expected),
                    "complete threshold-task frontier receipt differs")
    gate["require"](actual["terminal"] == TERMINAL, "unit terminal changed")
    # The costs must come from the same instrument that produced the registered
    # parity-3 facts, and the unit must reproduce those facts in the same run.
    reproduced = actual["layout_contract"]["registered_parity3_facts_reproduced"]
    gate["require"](reproduced == {"DELEGATING_SUM_AND_MASK": [6, 1],
                                   "WRITTEN_SHARED_SUM_NET": [39, 4],
                                   "WRITTEN_XOR_CHAIN": [11, 0]},
                    "the registered parity-3 facts were not reproduced by the unit")
    gate["require"](gate["canonical"](gate["load_inventory"](root)) ==
                    gate["canonical"](inventory),
                    "inventory changed during threshold-task frontier replay")
    return {"terminal": TERMINAL,
            "claim_ceiling": "one task family, one code grammar, one validated opcode "
                             "layout and one declared constant-cell count; no timing, no "
                             "physical memory, no coverage of unwritten realizations",
            "external_unit": UNIT, "manifest": record,
            "instrument_unit": INSTRUMENT_UNIT, "instrument_manifest": instrument,
            "original_payload": actual}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
