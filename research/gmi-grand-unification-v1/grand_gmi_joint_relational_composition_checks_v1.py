#!/usr/bin/env python3
"""Replay the complete frozen JRC payload without changing its internal bindings."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
UNIT = "research/gmi-joint-relational-composition-v1"
ORIGINAL_RECEIPT = "JOINT_RELATIONAL_COMPOSITION_RECEIPT_V1.json"
TERMINAL = "GRAND_GMI_JOINT_RELATIONAL_COMPOSITION_BOUND_REPLAY_GREEN"


def run(root=HERE):
    root = Path(root).resolve()
    gate = runpy.run_path(str(root / "replay_theorem_capsule_v1.py"))
    inventory = gate["load_inventory"](root)
    record = inventory["external_units"][UNIT]
    unit = root.parent.parent / UNIT
    expected = gate["strict_json"]((unit / ORIGINAL_RECEIPT).read_text(), ORIGINAL_RECEIPT)
    with tempfile.TemporaryDirectory(prefix="gmi-jrc-source-cache-") as cache:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}",
             "-c", "import runpy, sys; from pathlib import Path; "
             "unit=Path(sys.argv[1]); sys.path.insert(0, str(unit)); "
             "runpy.run_path(str(unit / 'joint_relation_checks_v1.py'), run_name='__main__')",
             str(unit)],
            cwd=unit, capture_output=True, text=True, timeout=60)
    gate["require"](result.returncode == 0 and result.stderr == "",
                    "original joint relational checker failed: " + result.stderr[-1000:])
    actual = gate["strict_json"](result.stdout, "original JRC stdout")
    gate["require"](gate["canonical"](actual) == gate["canonical"](expected),
                    "complete original joint relational receipt differs")
    gate["require"](gate["canonical"](gate["load_inventory"](root)) ==
                    gate["canonical"](inventory), "inventory changed during JRC replay")
    return {"terminal": TERMINAL,
            "claim_ceiling": "exact finite message-alphabet composition only; no physical or lifetime claim",
            "external_unit": UNIT, "manifest": record,
            "original_payload": actual}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
