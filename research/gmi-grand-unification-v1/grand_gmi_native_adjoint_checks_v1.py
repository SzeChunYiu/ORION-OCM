#!/usr/bin/env python3
"""Complete frozen native-adjoint payload plus exported-runtime byte identity."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
UNIT = "research/gmi-native-adjoint-repair-v1"
DELTA = "research/gmi-pr551-delta-08821a0a-v1"
PREFIX = "research/machine-intelligence-morphogenesis-v1/"
TERMINAL = "GRAND_GMI_NATIVE_ADJOINT_BOUND_REPLAY_GREEN"


def live_bindings(root, gate, inventory):
    repository = root.parent.parent
    unit = repository / UNIT
    mapping = gate["strict_json"](
        (unit / "ACTIVE_RUNTIME_BINDING_V1.json").read_text(), "active binding")["files"]
    expected = set(gate["EXTERNAL_CONTROL_DEPENDENCIES"][Path(__file__).name])
    gate["require"](set(mapping) == expected, "active mapping coverage differs")
    for name, record in mapping.items():
        gate["require"](name.startswith(PREFIX), "unknown active mapping prefix")
        live = gate["bind_file"](repository, name, inventory["external_controls"][name])
        frozen = unit / "corrected_source" / name.removeprefix(PREFIX)
        gate["require"](len(live.read_bytes()) == record["bytes"] and
                        gate["sha256"](live) == record["sha256"] and
                        live.read_bytes() == frozen.read_bytes(),
                        "live runtime differs from frozen corrected source: " + name)
    return mapping


def run(root=HERE):
    root = Path(root).resolve()
    gate = runpy.run_path(str(root / "replay_theorem_capsule_v1.py"))
    inventory = gate["load_inventory"](root)
    mapping = live_bindings(root, gate, inventory)
    unit = root.parent.parent / UNIT
    expected = gate["strict_json"]((unit / "RECEIPT_V1.json").read_text(), "NAR receipt")
    with tempfile.TemporaryDirectory(prefix="gmi-nar-source-cache-") as cache:
        result = subprocess.run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={cache}",
             str(unit / "check_v1.py")],
            cwd=unit, capture_output=True, text=True, timeout=60)
    gate["require"](result.returncode == 0 and result.stderr == "",
                    "original native adjoint checker failed: " + result.stderr[-1000:])
    actual = gate["strict_json"](result.stdout, "original NAR stdout")
    gate["require"](gate["canonical"](actual) == gate["canonical"](expected),
                    "complete original native adjoint receipt differs")
    current = gate["load_inventory"](root)
    gate["require"](gate["canonical"](current) == gate["canonical"](inventory),
                    "inventory changed during native adjoint replay")
    gate["require"](live_bindings(root, gate, current) == mapping,
                    "active mapping changed during replay")
    return {"terminal": TERMINAL,
            "claim_ceiling": "source-scoped ordered clamped pullback repair; no campaign or family capability recovery",
            "external_units": {name: inventory["external_units"][name] for name in (UNIT, DELTA)},
            "active_runtime": mapping, "original_payload": actual}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
