"""Conservative additive successor integrity, independent of scientific truth."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / "research/gmi-1068-recursive-audit-v3"
V4_SHA = "67424e8b749442d8ba30736eab5488dc8e28e1677082e2e72cbaf13c17e67f3d"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def evaluate():
    spec = importlib.util.spec_from_file_location("gate", OLD / "gate.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    before_path = OLD / "SCOPE_SNAPSHOT_V4.json"
    need(hashlib.sha256(before_path.read_bytes()).hexdigest() == V4_SHA, "V4 drift")
    before = json.loads(before_path.read_text())
    current = json.loads((HERE / "SCOPE_SNAPSHOT_V5.json").read_text())
    gate.validate(before, ROOT)
    result = gate.validate(current, ROOT)
    allowed_status = {"R1": "OPEN", "R2": "OPEN", "R3": "STALE", "R4": "STALE"}
    additions = set()
    for name in gate.NODES:
        old, new = before["rounds"][name], current["rounds"][name]
        need(new["status"] == allowed_status.get(name, old["status"]), "status drift")
        for key in ("obligations", "historical_reconciliation_status", "scope"):
            need(old[key] == new[key], "history or atom drift:" + name)
        old_artifacts = {a["path"]: a for a in old["artifacts"]}
        new_artifacts = {a["path"]: a for a in new["artifacts"]}
        need(all(new_artifacts.get(p) == a for p, a in old_artifacts.items()),
             "historical binding changed")
        added = set(new_artifacts) - set(old_artifacts)
        if name in ("R1", "R2"):
            need(bool(added), "missing foundation repair")
            need(new["local_repairs"][:-1] == old["local_repairs"], "repair history")
            repair = new["local_repairs"][-1]
            need(repair["id"] == name + "-foundation-repair-v5", "wrong repair")
            need(all(w["path"] in added for w in repair["evidence"]), "unrelated evidence")
        else:
            need(not added and new["local_repairs"] == old["local_repairs"], "unregistered repair")
        additions.update(added)
    need(result["registered_atoms"] == result["unresolved_atoms"] == 222, "coverage drift")
    need(not result["earned_rounds"], "round promotion")
    gate.validate_baseline(current, before, sorted(additions))
    # A stale descendant cannot be silently restored by changing only its status.
    mutant = json.loads(json.dumps(current))
    mutant["rounds"]["R7"]["status"] = "EARNED"
    try:
        gate.validate(mutant, ROOT)
    except ValueError:
        pass
    else:
        raise ValueError("stale promotion survived")
    return {"status": "PASS", "registered_atoms": 222, "overall_closure": "OPEN",
            "affected_cone": sorted(gate.descendants("R1"), key=lambda n: int(n[1:])),
            "scientific_truth_certified": False}


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True))
