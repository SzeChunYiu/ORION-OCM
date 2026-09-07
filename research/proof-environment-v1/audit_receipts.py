"""Independent fixed-matrix/issuer/receipt checks over retained bytes only."""
from audit_data import bound, canonical, inventory, load_json, record, require, same
from audit_process import check_processes


def subset(data, prefix, excluded=()):
    return {n[len(prefix):]: b for n, b in data.items() if n.startswith(prefix) and n[len(prefix):] not in excluded}


def json_at(data, name): return load_json(data[name])


def audit_rows(data, result, matrix, runtime, origin):
    require(result["schema"] == "ocm.proof-environment.commission.v1" and
            result["terminal"] == "PROVISIONAL_PASS_REQUIRES_COMPLETE_SEAL" and
            result["evidence_complete"] is True and result["failure"] is None, "incomplete result")
    require(matrix["schema"] == "ocm.proof-environment.controls.v1" and
            matrix["scope"] == result["scope"] == "AUTHORED_NATIVE_ENVIRONMENT_CONTROLS", "matrix scope differs")
    require(result["matrix_sha256"] == record(data["matrix.json"])["sha256"], "matrix binding differs")
    expected = [(c, phase, expected) for c in matrix["cases"] for phase, expected in
                [("prepare", c["prepare_expected"]), *[(f"check-{i}", x["expected"]) for i, x in enumerate(c["checks"])]]]
    require(len(expected) == 47 and type(result["denominator"]) is int and result["denominator"] == 47 and
            type(result["passed"]) is int and result["passed"] == 47, "control count differs")
    ids = [(c["id"], p) for c, p, _ in expected]
    require(len(set(ids)) == 47 and [(x["case"], x["phase"]) for x in result["controls"]] == ids, "row identities differ")
    pids = []; kernel_passes = 0
    for row, (case, phase, wanted) in zip(result["controls"], expected):
        require(row["passed"] is True and row["reason"] == "ASSESSED", "unassessed row")
        prefix = "cases/" + case["id"] + "/" + phase
        name = prefix + ("/receipt.json" if phase == "prepare" else "/check.json")
        require(row["receipt"]["path"] == origin + "/" + name, "row receipt path differs")
        receipt = load_json(bound(data[name], row["receipt"], "row receipt"))
        base = json_at(data, prefix + "/receipt.json")
        if phase != "prepare":
            require(same(base, {k: v for k, v in receipt.items() if k not in
                               {"prepared_receipt_sha256", "environment_id"}}), "check/base receipt differs")
        op = "prepare" if phase == "prepare" else "check"
        native = receipt["native"]
        require(receipt["schema"] == "ocm.proof-environment.receipt.v1" and
                native["schema"] == "ocm.proof-environment.result.v1", "receipt schema differs")
        require(receipt.get("evidence_complete", True) is True and "artifact_error" not in receipt, "incomplete receipt")
        require(receipt["operation"] == native["operation"] == op and
                receipt["terminal"] == native["terminal"] == wanted["terminal"] and
                receipt["stage"] == native["stage"] == wanted["stage"] and
                receipt["reason"] == native["reason"] and wanted["reason_contains"] in native["reason"], "control cause differs")
        require(same(receipt["files"], inventory(subset(data, prefix + "/", ("receipt.json", "check.json")))),
                "receipt inventory differs")
        require(same(receipt["driver_sources"], runtime["driver_sources"]), "receipt source binding differs")
        runtime_raw = data[prefix + "/runtime.json"]
        bound(runtime_raw, matrix["runtime"], "runtime copy")
        require(same(load_json(runtime_raw), runtime) and receipt["runtime_sha256"] == matrix["runtime"]["sha256"],
                "runtime identity differs")
        frozen_raw = data[prefix + "/freeze.json"]; freeze = load_json(frozen_raw)
        require(receipt["authorization_sha256"] == record(frozen_raw)["sha256"], "authorization differs")
        request = json_at(data, prefix + "/request.json")
        require(receipt["request_sha256"] == record(data[prefix + "/request.json"])["sha256"], "request differs")
        expected_request = {"schema": "ocm.proof-environment.request.v1", "operation": op}
        if op == "prepare":
            frozen_binding = case["prepare_freeze"]; bound(frozen_raw, frozen_binding, "prepare freeze")
            require(same(freeze["inputs"], receipt["inputs"]) and set(receipt["inputs"]) ==
                    {"policy", "primitive_packet", "registered_target_packet", "source_packet"}, "preparation inputs differ")
        else:
            index = int(phase.split("-")[1]); registered = case["checks"][index]
            issuer_name = "cases/" + case["id"] + "/prepare/receipt.json"
            issuer = json_at(data, issuer_name); issuer_binding = {"path": origin + "/" + issuer_name, **record(data[issuer_name])}
            require(same(freeze["prepared_receipt"], issuer_binding) and
                    receipt["prepared_receipt_sha256"] == issuer_binding["sha256"] and
                    receipt["environment_id"] == freeze["environment_id"] == issuer["environment_id"], "issuer differs")
            require(same(freeze["candidate_packet"], registered["candidate_packet"]) and
                    same(freeze["candidate_root"], registered["candidate_root"]), "candidate authorization differs")
            expected_inputs = {"candidate_packet": registered["candidate_packet"]}
            prepare_prefix = "cases/" + case["id"] + "/prepare/"
            for role, path in {"permitted_packet": "execution/native/permitted.ndjson", "target_packet": "execution/native/target.ndjson",
                               "registration": "execution/native/registration.json", "primitive_packet": "inputs/primitive_packet.ndjson"}.items():
                full_name = prepare_prefix + path
                expected_inputs[role] = {"path": origin + "/" + full_name, **record(data[full_name])}
            require(same(expected_inputs, receipt["inputs"]), "issued input identities differ")
            frozen_name = "cases/" + case["id"] + "/" + phase + "-freeze.json"
            require(data[frozen_name] == frozen_raw, "check freeze copy differs")
            frozen_binding = {"path": origin + "/" + frozen_name, **record(frozen_raw)}
            expected_request["candidate_root"] = registered["candidate_root"]
        require(freeze["schema"] == "ocm.proof-environment.freeze.v1" and freeze["operation"] == op, "freeze role differs")
        for role, binding in receipt["inputs"].items():
            suffix = ".json" if role in {"policy", "registration"} else ".ndjson"
            filename = role + suffix
            bound(data[prefix + "/inputs/" + filename], binding, "input snapshot")
            expected_request[role] = "/inputs/" + filename
        require(same(request, expected_request), "native request roles differ")
        outputs = subset(data, prefix + "/execution/native/")
        require(set(native["files"]) == set(outputs) and len(native["files"]) == len(outputs), "native output membership differs")
        if op == "prepare" and native["terminal"] == "PREPARED":
            identity = {"runtime": matrix["runtime"]["sha256"], "inputs": {k: v["sha256"] for k, v in receipt["inputs"].items()},
                        "outputs": inventory(outputs)}
            require(receipt["environment_id"] == record(canonical(identity))["sha256"], "environment identity differs")
        pids.extend(check_processes(data, prefix, receipt, matrix, runtime, origin, frozen_binding))
        kernel_passes += native["terminal"] == "KERNEL_PASS"
    require(len(set(pids)) == 94, "recorded process identities repeated")
    require(kernel_passes == 14, "kernel pass count differs")
    return {"controls": 47, "kernel_passes": kernel_passes, "native_processes": 47, "recorded_process_ids": len(pids)}
