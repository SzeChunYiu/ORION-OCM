"""Adjudicate only original R0 governance; preserve all scientific requirements."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "research/gmi-1068-recursive-audit-v8/SCOPE_SNAPSHOT_V8.json"

BASE_SHA = "3ca6f044247aecf24b712e6b071b371a9454b193b81c63f09389f44825ae5b93"

def need(ok, message):
    if not ok:
        raise ValueError(message)


def evaluate():
    spec = importlib.util.spec_from_file_location(
        "gate", ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    need(hashlib.sha256(BASE.read_bytes()).hexdigest() == BASE_SHA, "V8 baseline drift")
    before = json.loads(BASE.read_text())
    current = json.loads((HERE / "SCOPE_SNAPSHOT_V9.json").read_text())
    gate.validate(before, ROOT)
    result = gate.validate(current, ROOT)
    additions = set()
    for name in gate.NODES:
        old, new = before["rounds"][name], current["rounds"][name]
        for field in ("scope", "historical_reconciliation_status"):
            need(new[field] == old[field], "historical scope drift:" + name)
        old_artifacts = {a["path"]: a for a in old["artifacts"]}
        new_artifacts = {a["path"]: a for a in new["artifacts"]}
        need(all(new_artifacts.get(p) == a for p, a in old_artifacts.items()),
             "historical artifact drift:" + name)
        added = set(new_artifacts) - set(old_artifacts)
        if name in ("R0", "R1", "R2", "R14"):
            need(bool(added), "missing new evidence:" + name)
            need(new["local_repairs"][:-1] == old["local_repairs"], "repair history drift")
            repair = new["local_repairs"][-1]
            need(repair["id"] == name + "-foundation-v9", "wrong repair")
            need(all(w["path"] in added for w in repair["evidence"]), "unrelated witness")
        else:
            need(not added and new["local_repairs"] == old["local_repairs"],
                 "unregistered repair:" + name)
        if name == "R0":
            need(new["status"] == "EARNED", "governance round not earned")
            for a, b in zip(old["obligations"], new["obligations"]):
                for field in ("id", "title", "historical_status"):
                    need(a[field] == b[field], "original atom identity changed")
                need(b["status"] == "CLOSED" and bool(b["evidence"]), "missing R0 evidence")
                need("governance" in b["disposition"].lower(), "missing authority boundary")
        else:
            need(new["status"] == old["status"], "scientific round promotion:" + name)
            need(new["obligations"] == old["obligations"], "scientific atom promotion:" + name)
        additions.update(added)
    need(result["registered_atoms"] == 222 and result["unresolved_atoms"] == 214,
         "original coverage mismatch")
    need(result["earned_rounds"] == ["R0"], "unsupported round closure")
    gate.validate_baseline(current, before, sorted(additions))
    return {"status": "PASS", "registered_atoms": 222, "governance_atoms_closed": 8,
            "remaining_atoms": 214, "earned_rounds": ["R0"],
            "overall_closure": "OPEN", "scientific_truth_certified": False}


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True))
