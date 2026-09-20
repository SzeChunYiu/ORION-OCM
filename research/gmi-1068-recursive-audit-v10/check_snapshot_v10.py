"""Preserve V9 statuses while adding explicitly scoped resource proofs."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research/gmi-1068-recursive-audit-v9/SCOPE_SNAPSHOT_V9.json"
BASE_SHA = "c4b31baaf1ac0b3a07679be8fd3a76e007fcaedf60d9caa5c848ef8b6715f661"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def evaluate():
    spec = importlib.util.spec_from_file_location(
        "gate", ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    need(hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, "V9 baseline drift")
    before = json.loads(BASE.read_text())
    current = json.loads((HERE / "SCOPE_SNAPSHOT_V10.json").read_text())
    gate.validate(before, ROOT)
    result = gate.validate(current, ROOT)
    additions = set()
    for name in gate.NODES:
        old, new = before["rounds"][name], current["rounds"][name]
        for field in ("scope", "historical_reconciliation_status", "status", "obligations"):
            need(new[field] == old[field], "original status/scope drift:" + name)
        old_artifacts = {a["path"]: a for a in old["artifacts"]}
        new_artifacts = {a["path"]: a for a in new["artifacts"]}
        need(all(new_artifacts.get(p) == a for p, a in old_artifacts.items()),
             "historical artifact drift:" + name)
        added = set(new_artifacts) - set(old_artifacts)
        if name in ("R4", "R5", "R12", "R14", "R15"):
            need(bool(added), "missing new evidence:" + name)
            need(new["local_repairs"][:-1] == old["local_repairs"], "repair history drift")
            repair = new["local_repairs"][-1]
            need(repair["id"] == name + "-resource-v10", "wrong repair")
            need(all(w["path"] in added for w in repair["evidence"]), "unrelated witness")
        else:
            need(not added and new["local_repairs"] == old["local_repairs"],
                 "unregistered repair:" + name)
        additions.update(added)
    need(result["registered_atoms"] == 222 and result["unresolved_atoms"] == 214,
         "original coverage mismatch")
    need(result["earned_rounds"] == ["R0"], "unsupported round closure")
    gate.validate_baseline(current, before, sorted(additions))
    return {"status": "PASS", "registered_atoms": 222, "governance_atoms_closed": 8,
            "remaining_atoms": 214, "earned_rounds": ["R0"],
            "overall_closure": "OPEN", "scientific_truth_certified": False}


if __name__ == "__main__":
    try:
        print(json.dumps(evaluate(), sort_keys=True))
    except OSError as exc:
        print("CANNOT_CHECK:" + str(exc), file=sys.stderr)
        sys.exit(2)
    except (ValueError, KeyError, TypeError) as exc:
        print("CHECKED_INVALID:" + str(exc), file=sys.stderr)
        sys.exit(1)
