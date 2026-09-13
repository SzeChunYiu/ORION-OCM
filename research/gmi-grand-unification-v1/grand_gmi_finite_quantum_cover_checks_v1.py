#!/usr/bin/env python3
"""Replay the complete frozen FQC payload without changing its internal bindings."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
UNIT = "research/gmi-finite-quantum-cover-v1"
ORIGINAL_RECEIPT = "FINITE_QUANTUM_COVER_RECEIPT_V1.json"
TERMINAL = "GRAND_GMI_FINITE_QUANTUM_COVER_BOUND_REPLAY_GREEN"


def run(root=HERE):
    root = Path(root).resolve()
    gate = runpy.run_path(str(root / "replay_theorem_capsule_v1.py"))
    inventory = gate["load_inventory"](root)
    record = inventory["external_units"][UNIT]
    unit = root.parent.parent / UNIT
    expected = gate["strict_json"]((unit / ORIGINAL_RECEIPT).read_text(), ORIGINAL_RECEIPT)
    with tempfile.TemporaryDirectory(prefix="gmi-fqc-source-cache-") as cache:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}",
             str(unit / "check_finite_quantum_v1.py")],
            cwd=unit, capture_output=True, text=True, timeout=60)
    gate["require"](result.returncode == 0 and result.stderr == "",
                    "original finite quantum checker failed: " + result.stderr[-1000:])
    actual = gate["strict_json"](result.stdout, "original FQC stdout")
    gate["require"](gate["canonical"](actual) == gate["canonical"](expected),
                    "complete original finite quantum receipt differs")
    gate["require"](gate["canonical"](gate["load_inventory"](root)) ==
                    gate["canonical"](inventory), "inventory changed during FQC replay")
    return {"terminal": TERMINAL,
            "claim_ceiling": "inherited finite quantum witnesses only; no general solver or hardware claim",
            "external_unit": UNIT, "manifest": record,
            "original_payload": actual}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
