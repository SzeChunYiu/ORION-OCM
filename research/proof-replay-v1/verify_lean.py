"""Execute the small Lean bridge and negative fixtures; unavailable tool exits 2."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

NAMES = ("interval_conjunction", "live_refinement", "separate_witnesses_not_joint",
         "agreement_sound", "agreement_refinement", "authority_nonamplification",
         "integer_work_bound", "risk_not_exact")
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def audit_output(text: str, expected: tuple[str, ...]) -> dict:
    reports = {}
    for line in text.splitlines():
        if "depends on axioms:" in line:
            name = line.split("'")[1]
            match = re.search(r"depends on axioms:\s*\[([^]]*)\]", line)
            if match is None:
                raise ValueError("unreadable axiom report")
            axes = {x.strip() for x in match[1].split(",") if x.strip()}
            if not axes <= ALLOWED:
                raise ValueError("undeclared axioms: " + repr(sorted(axes - ALLOWED)))
            reports[name] = sorted(axes)
        elif "does not depend on any axioms" in line:
            reports[line.split("'")[1]] = []
    if set(reports) != set(expected):
        raise ValueError("missing or extra theorem axiom report")
    return reports


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lean", default="lean")
    args = parser.parse_args()
    lean = shutil.which(args.lean)
    if lean is None:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": "Lean binary unavailable"}))
        return 2
    source = Path(__file__).with_name("Foundation.lean")
    if not source.is_file():
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": "proof source unavailable"}))
        return 2
    try:
        version = subprocess.run([lean, "--version"], capture_output=True, text=True, timeout=30)
        if version.returncode or "version 4.19.0" not in version.stdout:
            raise ValueError("unregistered Lean toolchain: " + version.stdout + version.stderr)
        text = source.read_text()
        if re.search(r"\b(sorry|admit|unsafe|native_decide)\b|^\s*(axiom|opaque)\s", text, re.M):
            raise ValueError("unregistered proof escape in source")
        positive = subprocess.run([lean, str(source)], capture_output=True, text=True, timeout=120)
        if positive.returncode:
            raise ValueError("Lean build failed:\n" + positive.stdout + positive.stderr)
        axioms = audit_output(positive.stdout, tuple("MEFoundation." + n for n in NAMES))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "Negative.lean"
            target.write_text("import Lean\ntheorem false_target : (0 : Nat) = 1 := by decide\n")
            wrong = subprocess.run([lean, str(target)], capture_output=True, text=True, timeout=30)
            if wrong.returncode == 0:
                raise ValueError("false theorem negative fixture was accepted")
            for name, code in {
                "injected_axiom": "axiom injected : False\ntheorem bad : False := injected\n#print axioms bad\n",
                "admitted_proof": "theorem bad : False := by sorry\n#print axioms bad\n",
            }.items():
                target.write_text("import Lean\n" + code)
                trial = subprocess.run([lean, str(target)], capture_output=True, text=True, timeout=30)
                if trial.returncode:
                    raise ValueError("negative axiom fixture did not elaborate: " + name)
                try:
                    audit_output(trial.stdout, ("bad",))
                except ValueError:
                    pass
                else:
                    raise ValueError("axiom audit missed " + name)
        print(json.dumps({"terminal": "LEAN_LOGICAL_BRIDGE_PASS", "toolchain": version.stdout.strip(),
                          "source_sha256": sha256(source.read_bytes()).hexdigest(),
                          "theorem_count": len(NAMES), "axioms": axioms,
                          "negative_fixtures": ["false_theorem", "injected_axiom", "admitted_proof"],
                          "scope": "logical bridge only; no probability or matrix formalization",
                          "independent_review": "NOT_OBTAINED"}, indent=2, sort_keys=True))
        return 0
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except (ValueError, IndexError) as exc:
        print(json.dumps({"terminal": "FAIL", "reason": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
