#!/usr/bin/env python3
"""Replay the complete frozen formal-derivation payload without changing its internal bindings."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
UNIT = "research/gmi-formal-derivation-v1"
AUDIT = "research/gmi-main566567-audit-v1"
LIVE_THEOREM = "research/gmi-recursive-theory-closure-v1/GLOBAL_ADAPTIVE_COMPOSITION_THEOREM_V1.md"
ORIGINAL_RECEIPT = "RECEIPT_V1.json"
TERMINAL = "GRAND_GMI_FORMAL_DERIVATION_BOUND_REPLAY_GREEN"


def run(root=HERE):
    root = Path(root).resolve()
    gate = runpy.run_path(str(root / "replay_theorem_capsule_v1.py"))
    inventory = gate["load_inventory"](root)
    records = {name: inventory["external_units"][name] for name in (UNIT, AUDIT)}
    unit = root.parent.parent / UNIT
    expected = gate["strict_json"]((unit / ORIGINAL_RECEIPT).read_text(), ORIGINAL_RECEIPT)
    with tempfile.TemporaryDirectory(prefix="gmi-formal-source-cache-") as cache:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}",
             str(unit / "verify_unit.py")],
            cwd=unit, capture_output=True, text=True, timeout=60)
    gate["require"](result.returncode == 0 and result.stderr == "",
                    "original formal derivation verifier failed: " + result.stderr[-1000:])
    actual = gate["strict_json"](result.stdout, "original formal stdout")
    gate["require"](gate["canonical"](actual) == gate["canonical"](expected),
                    "complete original formal derivation receipt differs")
    gate["require"](gate["canonical"](gate["load_inventory"](root)) ==
                    gate["canonical"](inventory), "inventory changed during formal replay")
    return {"terminal": TERMINAL,
            "claim_ceiling": "finite witnesses for conditional discrete-time derivations; no proof-assistant validation, universal closure or empirical superiority",
            "external_units": records,
            "corrected_live_theorem": {LIVE_THEOREM: inventory["external_documents"][LIVE_THEOREM]},
            "original_payload": actual}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
