#!/usr/bin/env python3
"""Check additive repair reconciliation; git custody remains an external CI gate."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
V3_SHA256 = "05081b8b8b063f783be06a9286e6383e3cff441c7d7982af6311bab26a276284"
SCOPE_CORRECTIONS = {
    "R14": (
        "Irreducibility/prior audit of surviving assumptions at declared scope.",
        "Proof-assistant formalization and kernel verification of the flagship theory bundle.",
    ),
}
EXPECTED_REPAIRS = {
    "R4": "R4-sufficiency-repair-v3",
    "R6": "R6-genesis-repair-v2",
    "R11": "R11-control-repair-v2",
    "R12": "R12-findings-scope-audit-v2",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_gate():
    spec = importlib.util.spec_from_file_location("gmi_scope_gate", ROOT / "gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    gate = load_gate()
    baseline_path = ROOT / "SCOPE_SNAPSHOT_V3.json"
    need(hashlib.sha256(baseline_path.read_bytes()).hexdigest() == V3_SHA256, "HISTORICAL_V3_CHANGED")
    baseline = json.loads(baseline_path.read_text())
    current = json.loads((ROOT / "SCOPE_SNAPSHOT_V4.json").read_text())
    # Both still describe actual bytes. None of the new repairs mutates V3 inputs.
    gate.validate(baseline, REPO)
    result = gate.validate(current, REPO)
    need({k: v for k, v in current.items() if k != "rounds"} ==
         {k: v for k, v in baseline.items() if k != "rounds"}, "TOP_LEVEL_SCOPE_CHANGED")
    changed_paths = set()
    for name in gate.NODES:
        old, new = baseline["rounds"][name], current["rounds"][name]
        for key in ("status", "historical_reconciliation_status", "obligations"):
            need(old[key] == new[key], "UNAUTHORIZED_REEARNING_OR_HISTORY_CHANGE:" + name + ":" + key)
        if name in SCOPE_CORRECTIONS:
            need((old["scope"], new["scope"]) == SCOPE_CORRECTIONS[name], "WRONG_SCOPE_CORRECTION:" + name)
        else:
            need(old["scope"] == new["scope"], "UNREGISTERED_SCOPE_CHANGE:" + name)
        old_artifacts = {a["path"]: a for a in old["artifacts"]}
        new_artifacts = {a["path"]: a for a in new["artifacts"]}
        need(all(new_artifacts.get(path) == artifact for path, artifact in old_artifacts.items()),
             "HISTORICAL_ARTIFACT_RECORD_CHANGED:" + name)
        additions = set(new_artifacts) - set(old_artifacts)
        if name in EXPECTED_REPAIRS:
            need(bool(additions), "MISSING_REPAIR_ARTIFACTS:" + name)
            need(new["local_repairs"][:-1] == old["local_repairs"], "PRIOR_REPAIR_RECORD_CHANGED:" + name)
            repair = new["local_repairs"][-1]
            need(repair["id"] == EXPECTED_REPAIRS[name] and repair["status"] == "LOCAL_VERIFIED",
                 "WRONG_LOCAL_REPAIR:" + name)
            need(all(w["path"] in additions for w in repair["evidence"]), "NEW_REPAIR_USES_UNRELATED_WITNESS:" + name)
        else:
            need(not additions and new["local_repairs"] == old["local_repairs"], "UNREGISTERED_REPAIR:" + name)
        changed_paths.update(additions)
    touched = gate.validate_baseline(current, baseline, sorted(changed_paths))
    need(touched == ["R4", "R6", "R11"], "PHYSICAL_MODULE_PATH_COVERAGE")
    need(result["registered_atoms"] == result["unresolved_atoms"] == 222, "ATOMIC_REQUIREMENT_COUNT")
    need(result["earned_rounds"] == [], "WHOLE_ROUND_PROMOTION")
    print(json.dumps({
        "status": "PASS_ADDITIVE_REPAIR_RECONCILIATION",
        "baseline_sha256": V3_SHA256,
        "snapshot_sha256": hashlib.sha256((ROOT / "SCOPE_SNAPSHOT_V4.json").read_bytes()).hexdigest(),
        "registered_atoms": 222,
        "unresolved_atoms": 222,
        "new_local_repairs": EXPECTED_REPAIRS,
        "scope_label_corrections": sorted(SCOPE_CORRECTIONS),
        "physical_changed_rounds": touched,
        "overall_closure": result["overall_closure"],
        "scientific_truth_certified": False,
        "review_level": "INTERNAL_AGENT_CROSS_REVIEW_NOT_EXTERNAL_REPLICATION",
        "git_custody": "EXTERNAL_CI_MUST_BIND_BASELINE_AND_CHANGED_PATHS_TO_GIT",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
