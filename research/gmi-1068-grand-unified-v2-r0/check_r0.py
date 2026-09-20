#!/usr/bin/env python3
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent

ALLOWED_STATUS = {
    "PROVED","PARENT_OWNED","FINITE_CALIBRATION","CONJECTURE",
    "EMPIRICAL","CANNOT_CHECK","NOT_STARTED"
}
EXPECTED_ROUNDS = [f"R{i}" for i in range(17)]

class GateError(Exception):
    pass

def load(name):
    return json.loads((ROOT / name).read_text())

def validate(checklist, dag, parents, theorems, gate):
    ids = [row["id"] for row in checklist["rows"]]
    if len(ids) != len(set(ids)):
        raise GateError("DUPLICATE_ATOMIC_ID")
    rounds = {row["round"] for row in checklist["rows"]}
    if set(EXPECTED_ROUNDS) - rounds:
        raise GateError("MISSING_ATOMIC_ROUND")
    if set(dag["nodes"]) != set(EXPECTED_ROUNDS):
        raise GateError("DAG_ROUND_SET_MISMATCH")

    deps = dag["dependencies"]
    state = {}
    def visit(node):
        mark = state.get(node, 0)
        if mark == 1:
            raise GateError("DAG_CYCLE")
        if mark == 2:
            return
        state[node] = 1
        for parent in deps.get(node, []):
            if parent not in deps:
                raise GateError("DAG_UNKNOWN_DEPENDENCY")
            visit(parent)
        state[node] = 2
    for node in EXPECTED_ROUNDS:
        visit(node)

    for entry in theorems["entries"]:
        if entry["status"] not in ALLOWED_STATUS:
            raise GateError("INVALID_THEOREM_STATUS")

    for entry in parents["entries"]:
        if not str(entry.get("source_id", "")).strip():
            raise GateError("PARENT_WITHOUT_SOURCE")

    r16 = set(deps["R16"])
    if not {"R13","R14","R15"}.issubset(r16):
        raise GateError("FINAL_ROUND_MISSING_REQUIRED_DEPENDENCY")

    required_gate = {
        "freeze_precedes_outcome_implementation",
        "universal_claims_have_proof_or_parent_authority",
        "finite_claims_have_exact_or_source_separated_checks_where_feasible",
        "empirical_claims_are_preregistered_at_claimed_level",
        "hostiles_and_negative_controls_pass",
        "no_forbidden_promotion",
        "ci_green",
        "reconciliation_only_earned_rows",
    }
    if set(gate["requirements"]) != required_gate:
        raise GateError("MERGE_GATE_DRIFT")
    return True

def expect_hostile(label, mutator, base):
    data = copy.deepcopy(base)
    mutator(data)
    try:
        validate(**data)
    except GateError:
        return True
    raise GateError("HOSTILE_NOT_CAUGHT:" + label)

def main():
    base = dict(
        checklist=load("ATOMIC_CHECKLIST_V1.json"),
        dag=load("THEORY_DAG_V1.json"),
        parents=load("PARENT_REGISTRY_V1.json"),
        theorems=load("THEOREM_STATUS_V1.json"),
        gate=load("MERGE_GATE_V1.json"),
    )
    validate(**base)

    hostiles = []
    hostiles.append(expect_hostile("duplicate_id",
        lambda d: d["checklist"]["rows"].__setitem__(1, {**d["checklist"]["rows"][1], "id": d["checklist"]["rows"][0]["id"]}), base))
    hostiles.append(expect_hostile("missing_round",
        lambda d: d["checklist"].__setitem__("rows", [r for r in d["checklist"]["rows"] if r["round"] != "R8"]), base))
    hostiles.append(expect_hostile("cycle",
        lambda d: d["dag"]["dependencies"]["R0"].append("R16"), base))
    hostiles.append(expect_hostile("bad_status",
        lambda d: d["theorems"]["entries"][0].__setitem__("status", "ABSOLUTE_TRUTH"), base))
    hostiles.append(expect_hostile("missing_parent_source",
        lambda d: d["parents"]["entries"][0].__setitem__("source_id", ""), base))
    hostiles.append(expect_hostile("weak_final_dependencies",
        lambda d: d["dag"]["dependencies"].__setitem__("R16", ["R13"]), base))

    result = load("RESULT_V1.json")
    computed = {
        "atomic_rows": len(base["checklist"]["rows"]),
        "rounds": len(base["dag"]["nodes"]),
        "parent_entries": len(base["parents"]["entries"]),
        "theorem_entries": len(base["theorems"]["entries"]),
        "dag_nodes": len(base["dag"]["nodes"]),
        "expected_hostiles": len(hostiles),
    }
    for key, value in computed.items():
        if result.get(key) != value:
            raise GateError(f"RESULT_DRIFT:{key}:{result.get(key)}!={value}")
    if result.get("status") != "GREEN_REGISTRY_CONSTITUTION_ONLY":
        raise GateError("WRONG_R0_STATUS")
    if result.get("claim_ceiling") != "GRAND_GMI_V2_R0_PROGRAMME_REGISTRY_AND_EXECUTION_CONSTITUTION_ONLY":
        raise GateError("WRONG_CLAIM_CEILING")

    print(json.dumps({
        "status":"GREEN_REGISTRY_CONSTITUTION_ONLY",
        **computed,
        "hostiles_caught":sum(hostiles),
    }, sort_keys=True))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GateError as exc:
        print("R0_GATE_RED:" + str(exc), file=sys.stderr)
        raise SystemExit(1)
