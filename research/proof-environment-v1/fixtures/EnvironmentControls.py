"""Exposed development controls, not a source-frozen commissioning claim."""
import copy
import json
import subprocess
import sys
from pathlib import Path
from ControlPackets import declaration, family, file_record, names, packet, raw, root_const, save, save_packet

BASE = Path("/home/billy/orion-director-work/20260907/proof-environment-development")
REPO = Path(__file__).resolve().parents[1]
SCHEMA = "ocm.proof-environment.request.v1"


def expected(terminal, stage, reason=""):
    return {"terminal": terminal, "stage": stage, "reason_contains": reason}


PASS = expected("KERNEL_PASS", "kernel_and_axioms")
PREPARED = expected("PREPARED", "replay_and_independent_target")


def run(output, label, argv):
    process = subprocess.run([sys.executable, str(BASE / "run.py"), output.name + "-" + label] + argv,
                             capture_output=True)
    (output / (label + "-launch.log")).write_bytes(process.stdout + process.stderr)
    receipt = BASE / (output.name + "-" + label) / "process.json"
    record = json.loads(receipt.read_text())
    return record, file_record(receipt)


def execute(output, case):
    directory = output / case["id"]
    directory.mkdir()
    source = packet(BASE / "fixture-export-1/stdout.txt")
    primitive = packet(BASE / "primitive-export-2/stdout.txt")
    target = case.get("target", "composition")
    data = directory / "reference"
    process, _ = run(output, case["id"] + "-extract", [".lake/build/bin/fixture_builder",
        str(BASE / "fixture-export-1/stdout.txt"), "Fixture." + target, str(data)])
    assert process["returncode"] == 0
    goal = json.loads((data / "goal.json").read_text())
    candidate_name = "stress" if case.get("stress") else "candidate"
    candidate = packet(data / (candidate_name + ".ndjson"))
    candidate_root = json.loads((data / (candidate_name + ".json")).read_text())["target_root"]
    policy = {"schema": "ocm.proof-environment.policy.v1", "target": "Fixture." + target,
              "target_root": goal["target_root"], "target_level_params": goal["target_level_params"],
              "roots": case.get("roots", [] if target == "composition" else ["rfl"]),
              "excluded": ["Fixture." + target], "axioms": case.get("axioms", []),
              "max_heartbeats": 100000000, "max_rec_depth": 100000}
    if "mutate" in case:
        case["mutate"](source, primitive, policy)
    save_packet(directory / "source.ndjson", source)
    save_packet(directory / "primitive.ndjson", primitive)
    save(directory / "policy.json", policy)
    roles = {"source_packet": directory / "source.ndjson", "primitive_packet": directory / "primitive.ndjson",
             "policy": directory / "policy.json", "registered_target_packet": data / "goal.ndjson"}
    save(directory / "prepare-request.json", {"schema": SCHEMA, "operation": "prepare", **{k: str(v) for k, v in roles.items()}})
    process, process_file = run(output, case["id"] + "-prepare", [".lake/build/bin/ocm_environment",
        str(directory / "prepare-request.json"), str(directory / "prepared")])
    actual = json.loads((directory / "prepared/result.json").read_text())
    intended = case.get("prepare", PREPARED)
    row = {"id": case["id"], "purpose": case["purpose"], "prepare_roles": {k: file_record(v) for k, v in roles.items()},
           "prepare_expected": intended, "prepare_actual": actual, "prepare_process": process_file, "checks": []}
    row["passed"] = matches(actual, intended) and process["returncode"] == 0
    if actual["terminal"] == "PREPARED":
        for filename in ("permitted.ndjson", "target.ndjson"):
            text = (directory / "prepared" / filename).read_text()
            assert "WITHHELD_PRIVATE_TABLE_CANARY_20260907" not in text and '"str":"forbiddenCanary"' not in text
        for idx, check in enumerate(case.get("checks", [{"expected": PASS}])):
            rows, root = copy.deepcopy(candidate), candidate_root
            if check.get("target_constant"):
                rows, root = root_const(rows, "Fixture." + target)
            if check.get("invalid_type"):
                root = next(row["ie"] for row in rows if row.get("sort") == 0)
            if check.get("declarations"):
                rows = source
            cpath = directory / f"candidate-{idx}.ndjson"
            save_packet(cpath, rows)
            prepared = directory / "prepared"
            request = {"schema": SCHEMA, "operation": "check", "permitted_packet": str(prepared / "permitted.ndjson"),
                       "target_packet": str(prepared / "target.ndjson"), "registration": str(prepared / "registration.json"),
                       "primitive_packet": str(roles["primitive_packet"]), "candidate_packet": str(cpath), "candidate_root": root}
            if check.get("normalization"):
                registration = json.loads((prepared / "registration.json").read_text())
                registration["normalization"] = check["normalization"]
                save(directory / f"registration-{idx}.json", registration)
                request["registration"] = str(directory / f"registration-{idx}.json")
            q = directory / f"check-{idx}-request.json"
            save(q, request)
            cp, receipt = run(output, case["id"] + f"-check-{idx}", [".lake/build/bin/ocm_environment", str(q), str(directory / f"checked-{idx}")])
            result = json.loads((directory / f"checked-{idx}/result.json").read_text())
            good = matches(result, check["expected"]) and cp["returncode"] == 0
            row["checks"].append({"candidate_packet": file_record(cpath), "candidate_root": root,
                "expected": check["expected"], "actual": result, "process": receipt, "passed": good})
            row["passed"] &= good
    elif case.get("checks", []) and intended["terminal"] == "PREPARED":
        row["passed"] = False
    return row


def matches(actual, intended):
    return all(actual[key] == intended[key] for key in ("terminal", "stage")) and intended["reason_contains"] in actual["reason"]


def main():
    from EnvironmentCases import cases
    output = BASE / sys.argv[1]
    output.mkdir()
    rows = []
    for case in cases():
        try:
            row = execute(output, case)
        except Exception as exc:
            row = {"id": case["id"], "passed": False, "prepare_actual": {"reason": repr(exc)}, "checks": [], "driver_error": repr(exc)}
            save(output / (case["id"] + "-driver-error.json"), row)
        rows.append(row)
        print(raw({"id": row["id"], "passed": row["passed"], "prepare": row["prepare_actual"]["reason"],
                   "checks": [(x["actual"]["terminal"], x["actual"]["reason"]) for x in row["checks"]]}), flush=True)
    save(output / "DEVELOPMENT_CASES.json", {"scope": "AUTHORED_DEVELOPMENT_ONLY", "cases": rows})
    return 0 if all(row["passed"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
