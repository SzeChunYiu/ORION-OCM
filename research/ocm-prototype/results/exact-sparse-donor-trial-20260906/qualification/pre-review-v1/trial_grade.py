"""External exact semantics and registered paired wall-time rule; no actor imports."""
from pathlib import Path
import argparse
import copy
from fractions import Fraction
from statistics import median
from trial_common import canonical, digest, read, sha, write

def need(condition, reason):
    if not condition: raise ValueError(reason)

def positive(value):
    return type(value) is int and value > 0

def semantic_call(payload, expected, arm):
    need(payload["state_before"] == payload["state_after"] == expected["state"], "STATE_OR_AUTHORITY_DRIFT")
    result = payload["result"]; answer = result["consumer"].get("answer")
    need(result["arm"] == arm and result["consumer"]["status"] == "COMPLETED", "INCOMPLETE_CONSUMER")
    need(result["consumer"]["decision"] == "ANSWER" and result["consumer"]["committed"] is True, "ORIGINAL_ANSWER_NOT_COMMITTED")
    need(type(answer) is dict and type(answer.get("value")) is int and all(type(v) is int for v in answer.get("arguments",[])), "NO_EXACT_VALUE")
    request = expected["request"]
    need(answer["program_id"] == request["program_id"] and answer["arguments"] == request["arguments"], "APPLICATION_IDENTITY")
    need(answer["status"] == "APPLIED" and answer["program_sha256"] == expected["program_sha256"], "PROGRAM_AUTHORITY")
    need(answer["value"] == max(request["arguments"]), "WRONG_PUBLIC_MAX_VALUE")
    need(type(answer.get("application_wall_s")) in (int,float) and answer["application_wall_s"] >= 0, "MISSING_RAW_APPLICATION_DURATION")
    vectors = result["vectors"]; n = expected["state"]["N"]
    need(len(vectors) == result["logical_fixed_point_calls"] == 4, "FOUR_VECTORS_REQUIRED")
    modes = ["WARRANTED","EXPLORATORY","WARRANTED","EXPLORATORY"]
    for i,v in enumerate(vectors):
        need(v["mode"] == modes[i] and v["alpha"] == expected["alpha"] and v["revoked"] == expected["state"]["revoked"], "KERNEL_INPUT_DRIFT")
        need(v["seed"] == (expected["query_seed"] if i < 2 else expected["uniform_seed"]), "SEED_DRIFT")
        need(set(v["values"]) == set(expected["ids"]) and len(v["values"]) == n, "TRUNCATED_FINE_OUTPUT")
        for value in v["values"].values():
            need(type(value) is str and "/" in value, "NONRATIONAL_FINE_OUTPUT")
            f = Fraction(value); need(value == str(f.numerator)+"/"+str(f.denominator), "NONCANONICAL_RATIONAL")
    checks = result["checks"]; need(len(checks) == 4, "FOUR_NAVIGATION_RECEIPTS_REQUIRED")
    for check in checks:
        if arm == "sympy":
            need(check.get("route") == "SYMPY_QQ_RREF" and check.get("donor_solve_calls") == 1, "DONOR_SOLVE_NOT_OBSERVED")
            need(check.get("independent_residual") == "EXACT_ZERO" and check.get("checker_dense_cells") == n*n and check.get("full_output_entries") == n, "RESIDUAL_NOT_CHECKED")
            need(check.get("candidate_assembly") == "DIRECT_SPARSE" and check.get("donor_method") == "DomainMatrix.solve_den(method='rref')", "WRONG_DONOR")
        else:
            need(check == {"route":"CURRENT_FRACTION_REFERENCE","donor_solve_calls":0,"independent_residual":"ORIGINAL_BEHAVIOR_NO_ADDED_CHECK"}, "HANDICAPPED_REFERENCE")
    counts = payload["counter_delta"]
    need(counts == {"catalogue_visits":expected["catalogue"],"application_calls":1,"pointwise_checks":1,"synthesis_dispatches":0}, "ACTUAL_CALL_COUNTS")
    application = copy.deepcopy(payload["application_checks"])
    need(len(application) == 4 and [c["operator"] for c in application] == expected["catalogue"], "CHECK_CATALOGUE")
    for c in application:
        need(c["phase"] == "solve", "WRONG_CHECK_PHASE")
        if c["operator"] == "apply:"+request["program_id"]:
            need(c["status"] == "PASS" and c["reason"] == "POINTWISE_VALUE_MATCH" and c["value"] == answer["value"] and c["arguments"] == request["arguments"], "POINTWISE_AUTHORITY")
            need(type(c.get("check_wall_s")) in (int,float) and c["check_wall_s"] >= 0, "MISSING_RAW_CHECK_DURATION")
            del c["check_wall_s"]
        else: need(c["status"] == "FAIL" and c["reason"] == "NOT_APPLICABLE", "UNRELATED_TOOL_RESULT")
    events = payload["invocations"]
    need(len(events) == 1 and events[0]["action"] == "application", "NATIVE_EVENT_COUNTS")
    need(set(events[0]) == {"index","action","payload_sha256","result","started_monotonic","finished_monotonic"}, "NATIVE_EVENT_SCHEMA")
    need(events[0]["index"] == payload["index"], "EVENT_SLICE_IDENTITY")
    need(events[0]["payload_sha256"] == digest(request) and events[0].get("result") == answer and "error" not in events[0], "NATIVE_EVENT_BINDING")
    need(events[0]["finished_monotonic"] >= events[0]["started_monotonic"], "INCOMPLETE_NATIVE_EVENT")
    semantic = copy.deepcopy(result)
    del semantic["arm"]; del semantic["checks"]
    del semantic["consumer"]["answer"]["application_wall_s"]
    return {"result":semantic, "application_checks":application, "counter_delta":counts,
            "state":payload["state_after"], "invocation": {"action":events[0]["action"], "payload_sha256":events[0]["payload_sha256"], "result":semantic["consumer"]["answer"]}}

def origin_check(record, manifest, arm, final):
    for name, item in record["modules"].items():
        need(item == manifest["expected_module_origins"].get(name), "MODULE_ORIGIN_BINDING")
    required = {"ocm.runtime.solve", "ocm.kso.navigation", "g1_vessel", "clia_reuse_vessel", "clia_reuse_apply"}
    if final: required.add("exact_sparse_donor_consumer")
    if final and arm == "sympy": required |= {"exact_sparse_donor", "exact_sparse_donor_check"}
    need(required <= set(record["modules"]), "MISSING_MODULE_ORIGINS")
    for name, item in record["external"].items():
        need(item == manifest["runtime_modules"].get(name), "RUNTIME_ORIGIN_BINDING")
    need("z3" in record["external"], "MISSING_REAL_Z3")
    need(("sympy" in record["external"]) == (final and arm == "sympy"), "SYMPY_IMPORT_BINDING")

def check_process(process, preparation, payloads, manifest, assignment):
    need(process["exit_code"] == 0 and not process["timed_out"] and process["supervisor_error"] is None, "PROCESS_ERROR_OR_TIMEOUT")
    need(process["pid_absent"] and process["private_state_removed"] and not process["post_reap_group_required_kill"], "PROCESS_NOT_CLOSED")
    need(positive(process["total_two_call_process_ns"]), "MISSING_COLD_TIME")
    need(process["wait4_raw"] is not None, "MISSING_WAIT4")
    worker=process["worker"]; arm=assignment["arm"]
    need(worker["status"] == "COMPLETED" and worker["assignment"] == assignment and worker["pid"] == process["pid"], "WORKER_BINDING")
    need(worker["assigned_calls"] == len(worker["calls"]) == len(payloads) == 2, "INCOMPLETE_CALL_DENOMINATOR")
    need(worker["consumer_scope"] == manifest["consumer_scope"], "OVERSTATED_CONSUMER_SCOPE")
    origin_check(worker["origins"], manifest, arm, True)
    origin_check(preparation["origins"], manifest, arm, False)
    need(worker["origins"]["sympy_imported"] == (arm == "sympy") and not preparation["origins"]["sympy_imported"], "UNFAITHFUL_IMPORT_COST")
    need(preparation["state"] == worker["final_state"] == manifest["expected"]["state"], "PREPARATION_AUTHORITY")
    need(preparation["catalogue"] == manifest["expected"]["catalogue"] and not preparation["events"], "PREPARATION_TOOL_CALL")
    need(preparation["task"] == manifest["expected"]["task"] and preparation["config"] == manifest["expected"]["config"] and preparation["request"] == manifest["expected"]["request"], "PREPARATION_INPUT_DRIFT")
    need(len(preparation["binding_receipts"]) == 2, "MISSING_REAL_HOST_BINDINGS")
    bound=copy.deepcopy(preparation["binding_receipts"])
    for b in bound:
        need(type(b.get("bind_wall_s")) in (int,float) and b["bind_wall_s"] >= 0, "MISSING_BIND_DURATION")
        del b["bind_wall_s"]
    need(bound == manifest["expected"]["binding_receipts"], "WRONG_HOST_PROGRAMS")
    semantics=[]
    for i,payload in enumerate(payloads):
        need(worker["calls"][i]["index"] == payload["index"] == i and payload["assignment"] == assignment, "CALL_ASSIGNMENT")
        need(positive(worker["calls"][i]["wall_ns"]), "MISSING_CALL_TIME")
        semantics.append(semantic_call(payload,manifest["expected"],arm))
    need(semantics[0] == semantics[1], "REPEAT_SEMANTIC_DRIFT")
    need(process["total_two_call_process_ns"] >= sum(c["wall_ns"] for c in worker["calls"]), "IMPOSSIBLE_TOTAL_TIME")
    return {"semantic":semantics[0],"bindings":bound,"warm_ns":worker["calls"][1]["wall_ns"],
            "cold_ns":process["total_two_call_process_ns"],"pid":process["pid"]}

def adjudicate(observations, assignments, errors):
    complete=len(observations); pairs=[]; mismatches=[]
    for pair in range(7):
        group={a["arm"]:observations.get(a["index"]) for a in assignments if a["pair"] == pair}
        if None in group.values() or set(group) != {"reference","sympy"}: continue
        a,b=group["reference"],group["sympy"]
        if (a["semantic"],a["bindings"]) != (b["semantic"],b["bindings"]): mismatches.append(pair)
        wr,cr=Fraction(b["warm_ns"],a["warm_ns"]),Fraction(b["cold_ns"],a["cold_ns"])
        pairs.append({"pair":pair,"warm_ratio":float(wr),"total_two_call_ratio":float(cr),
                      "warm_exact":str(wr),"total_exact":str(cr)})
    function = "CANNOT_CHECK" if errors or complete != 14 or len(pairs) != 7 else "FUNCTIONAL_MISMATCH" if mismatches else "EXACT_FUNCTIONAL_PARITY"
    warm=median(Fraction(p["warm_exact"]) for p in pairs) if len(pairs)==7 else None
    total=median(Fraction(p["total_exact"]) for p in pairs) if len(pairs)==7 else None
    passed=function == "EXACT_FUNCTIONAL_PARITY" and warm <= Fraction(4,5) and total < 1
    return {"assigned_processes":14,"assigned_calls":28,"qualified_processes":complete,"qualified_calls":2*complete,
            "functional_terminal":function,"component_gate":"ADOPT_EXACT_DONOR" if passed else function if function in ("CANNOT_CHECK","FUNCTIONAL_MISMATCH") else "PARENT_SUFFICIENT_FOR_REGISTERED_GATE",
            "warm_median_ratio":None if warm is None else float(warm),"total_two_call_median_ratio":None if total is None else float(total),"pairs":pairs,"mismatch_pairs":mismatches,"errors":errors,
            "cost_scope":"registered paired wall-time gate only; complete process-tree CPU, lifetime/asymptotic efficiency not established"}

def grade(root, expected_manifest_sha256):
    root=Path(root); inventory=read(root/"SEAL.json")
    def get(rel):
        need(rel in inventory and sha(root/rel)==inventory[rel],"CAPTURE_CUSTODY:"+rel)
        return read(root/rel)
    for rel in inventory: need(sha(root/rel)==inventory[rel],"CAPTURE_CUSTODY:"+rel)
    m=get("manifest.json"); need(sha(root/"manifest.json")==expected_manifest_sha256,"UNREGISTERED_MANIFEST")
    receipt=get("receipt.json"); launch=get("launch.json")
    need(receipt["status"]=="SEALED" and receipt["assigned_processes"]==14 and receipt["assigned_calls"]==28,"INCOMPLETE_RECEIPT")
    need(receipt["manifest_sha256"]==launch["manifest_sha256"]==expected_manifest_sha256,"MANIFEST_CUSTODY")
    need(len(receipt["reports"])==len(m["assignments"])==14,"MISSING_ARM")
    observations={}; errors=[]; pids=[]
    for a,report in zip(m["assignments"],receipt["reports"],strict=True):
        try:
            need(report["assignment"]==a,"ASSIGNMENT_ORDER")
            prefix=f"case-{a['index']:02d}"; process=get(prefix+"/process.json"); case=get(prefix+"/input.json")
            worker=get(prefix+"/captured-worker.json")
            need(case["assignment"]==a and case["manifest_sha256"]==expected_manifest_sha256,"CASE_BINDING")
            need(case["output"]==str(Path(launch["root"])/prefix) and case["manifest"]==launch["manifest_source"],"CASE_PATH_CUSTODY")
            need(sha(root/(prefix+"/stderr"))==process["stderr_sha256"],"STDERR_CUSTODY")
            need(worker==process["worker"] and sha(root/(prefix+"/stdout"))==process["stdout_sha256"],"WORKER_CUSTODY")
            need(read(root/(prefix+"/stdout"))==worker,"RAW_WORKER_DISAGREEMENT")
            need(worker["case_sha256"]==sha(root/(prefix+"/input.json")) and worker["manifest_sha256"]==expected_manifest_sha256,"WORKER_INPUT")
            prep=get(prefix+"/preparation.json"); need(worker["preparation_sha256"]==sha(root/(prefix+"/preparation.json")),"PREP_CUSTODY")
            payloads=[]
            for i,c in enumerate(worker["calls"]):
                need(c["path"]==f"call-{i}.json" and c["sha256"]==sha(root/(prefix+"/"+c["path"])),"CALL_CUSTODY")
                payloads.append(get(prefix+"/"+c["path"]))
            observations[a["index"]]=check_process(process,prep,payloads,m,a); pids.append(process["pid"])
        except (KeyError,TypeError,ValueError,OSError) as exc: errors.append({"case":a["index"],"reason":str(exc)})
    if len(set(pids))!=len(pids): errors.append({"reason":"PID_REUSE_NOT_INDEPENDENTLY_RESOLVED"})
    return adjudicate(observations,m["assignments"],errors)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--capture",type=Path,required=True)
    p.add_argument("--manifest-sha256",required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    try: result=grade(a.capture,a.manifest_sha256)
    except (ValueError,KeyError,TypeError,OSError) as exc: result={"functional_terminal":"CANNOT_CHECK","error":str(exc)}
    write(a.output,result)
    return 2 if result["functional_terminal"]=="CANNOT_CHECK" else 1 if result["functional_terminal"]=="FUNCTIONAL_MISMATCH" else 0
if __name__ == "__main__": raise SystemExit(main())
