"""Validate additive V8 evidence while retaining unresolved scientific scope."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V7 = ROOT / "research/gmi-1068-recursive-audit-v7/SCOPE_SNAPSHOT_V7.json"
V7_SHA = "55390dfcacf65a76987bd8d8f8cffd17e2234dbddf751162a22b6e434c1799a5"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def evaluate():
    spec = importlib.util.spec_from_file_location(
        "gate", ROOT / "research/gmi-1068-recursive-audit-v3/gate.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    need(hashlib.sha256(V7.read_bytes()).hexdigest() == V7_SHA, "V7 drift")
    before = json.loads(V7.read_text())
    current = json.loads((HERE / "SCOPE_SNAPSHOT_V8.json").read_text())
    gate.validate(before, ROOT)
    result = gate.validate(current, ROOT)
    additions = set()
    for name in gate.NODES:
        old, new = before["rounds"][name], current["rounds"][name]
        for key in ("status", "obligations", "historical_reconciliation_status", "scope"):
            need(old[key] == new[key], "history or authority drift:" + name)
        old_artifacts = {a["path"]: a for a in old["artifacts"]}
        new_artifacts = {a["path"]: a for a in new["artifacts"]}
        need(all(new_artifacts.get(p) == a for p, a in old_artifacts.items()), "binding drift")
        added = set(new_artifacts) - set(old_artifacts)
        if name in ("R3", "R4", "R14"):
            need(bool(added), "missing constructive evidence")
            need(new["local_repairs"][:-1] == old["local_repairs"], "history changed")
            repair = new["local_repairs"][-1]
            need(repair["id"] == name + "-continuation-v8", "wrong repair")
            need(all(w["path"] in added for w in repair["evidence"]), "unrelated witness")
        else:
            need(not added and new["local_repairs"] == old["local_repairs"], "unregistered repair")
        additions.update(added)
    need(result["registered_atoms"] == result["unresolved_atoms"] == 222, "coverage drift")
    need(not result["earned_rounds"], "round promotion")
    gate.validate_baseline(current, before, sorted(additions))
    return {"status": "PASS", "registered_atoms": 222, "overall_closure": "OPEN",
            "local_repairs": ["R3", "R4", "R14"], "scientific_truth_certified": False}


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True))
