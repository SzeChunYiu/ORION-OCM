"""Fixture-only capture/grader controls; never execute the prospective request panel."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


def module(name):
    assert importlib.util.find_spec(name) is not None, name + " implementation is absent"
    return importlib.import_module(name)


def unit_binding():
    return {"descriptor_id": "1" * 64, "program_sha256": "2" * 64,
            "task_id": "jmbl_fg_max3", "task_sha256": "4" * 64, "registration": ["unit-query"],
            "support": {"lower": [["unit-query"]], "upper": [["unit-query"]]}}


def unit_row():
    q = {"kind": "clia_apply", "program_id": "1" * 64, "arguments": [41, -7, 12]}
    a = {"status": "APPLIED", "program_id": "1" * 64, "program_sha256": "2" * 64,
         "arguments": [41, -7, 12], "value": 41}
    return {"id": "UNIT_FIXTURE.max3", "arm": "native", "request": q, "result":
            {"status": "ACCEPTED_PARENT", "record_id": "unit-record", "answer": a,
             "check": {"status": "PASS"}}}


@pytest.mark.parametrize("value", [40, True, 41.0, "41"])
def test_external_grader_rejects_wrong_value_and_nonintegers(value):
    G = module("grade_clia_reuse")
    row = unit_row()
    assert G.grade_math(row, unit_binding(), authorized=True)["status"] == "CORRECT_VALUE"
    row["result"]["answer"]["value"] = value
    assert G.grade_math(row, unit_binding(), authorized=True)["status"] != "CORRECT_VALUE"


def test_guard_oracle_uses_z_and_exact_boundary():
    G = module("grade_clia_reuse")
    assert G.oracle("jmbl_fg_mpg_guard2", [17, -9, -7]) == 8
    assert G.oracle("jmbl_fg_mpg_guard2", [17, -9, -8]) == 26


def test_wrong_tuple_boolean_alias_and_diagnostic_not_selected():
    G = module("grade_clia_reuse")
    row = unit_row()
    row["result"]["answer"]["arguments"] = [41, -7, 11]
    assert G.grade_math(row, unit_binding(), authorized=True)["status"] == "WRONG_BINDING"
    row = unit_row(); row["request"]["arguments"] = [1, -7, 12]
    row["result"]["answer"]["arguments"] = [True, -7, 12]
    assert G.grade_math(row, unit_binding(), authorized=True)["status"] == "WRONG_BINDING"
    row = unit_row(); row["result"]["proposal_diagnostic"] = row["result"].pop("answer")
    assert G.grade_math(row, unit_binding(), authorized=True)["status"] == "NO_SELECTED_VALUE"


def test_policy_refusal_is_not_error_or_live_unbound():
    G = module("grade_clia_reuse")
    row = unit_row()
    row.update(authority={"liveness": "DEAD", "revoked": ["unit-query"]},
               invocation_delta={"synthesize": 0, "application": 0})
    row["result"] = {"status": "REFUSED_DEAD_SUPPORT", "answer": None}
    assert G.grade_math(row, unit_binding(), authorized=False)["status"] == "EXPECTED_POLICY_REFUSAL"
    row["result"]["status"] = "CANNOT_CHECK_APPLICATION"
    assert G.grade_math(row, unit_binding(), authorized=False)["status"] == "REFUSAL_NOT_ESTABLISHED"
    row["result"]["status"] = "REFUSED_DEAD_SUPPORT"; row["authority"]["liveness"] = "LIVE"
    assert G.grade_math(row, unit_binding(), authorized=False)["status"] == "REFUSAL_NOT_ESTABLISHED"


def test_actual_native_invocation_is_observed_without_changing_result():
    C = module("clia_reuse_study_common")
    import clia_process
    events = []
    spec = "(set-logic LIA)\n(synth-fun unit_const ((u Int)) Int)\n(declare-var u Int)\n(constraint (= (unit_const u) 7))\n(check-synth)"
    with C.InvocationMeter(events):
        result = clia_process.invoke("synthesize", {"sygus": spec})
    assert result["status"] == "SOLUTION" and result["native_invoked"]
    assert len(events) == 1 and events[0]["action"] == "synthesize"
    assert events[0]["result"] == result
    assert events[0]["result"]["metrics"]["worker_pid"] > 0
    assert events[0]["result"]["solver"] == "cvc5 1.3.4"


def test_wait4_records_actor_and_reaped_child_cpu_without_wrapper_omission(tmp_path):
    C = module("clia_reuse_study_common")
    script = tmp_path / "UNIT_FIXTURE_cpu.py"
    script.write_text("import json,resource,subprocess,sys,time\n"
        "t=time.process_time()\nwhile time.process_time()-t<0.04: pass\n"
        "subprocess.run([sys.executable,'-c','import time;t=time.process_time()\\nwhile time.process_time()-t<0.05: pass'],check=True)\n"
        "a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)\n"
        "print(json.dumps({'self':a.ru_utime+a.ru_stime,'children':b.ru_utime+b.ru_stime}))\n")
    receipt = C.run_process([sys.executable, str(script)], tmp_path / "cpu", seconds=5)
    raw = json.loads((tmp_path / "cpu.stdout").read_text())
    assert receipt["exit_code"] == 0
    assert raw["self"] >= .035 and raw["children"] >= .045
    assert receipt["wait4_cpu_s"] >= raw["self"] + raw["children"] - .005
    assert receipt["complete_tree_cpu_verified"] is False


def test_timeout_is_preserved_as_incomplete_cpu_scope(tmp_path):
    C = module("clia_reuse_study_common")
    receipt = C.run_process([sys.executable, "-c", "import time;time.sleep(2)"],
                            tmp_path / "timeout", seconds=.05)
    assert receipt["timed_out"] and receipt["exit_code"] != 0
    assert not receipt["complete_tree_cpu_verified"]


def test_f1_different_canonical_program_refused_and_aliases_do_not_change_tuples():
    C = module("capture_clia_reuse")
    bindings = {a: {"programs": {k: {**unit_binding(), "task_id": k,
        "checker_identity": "fixture", "registration": [a + k]}
        for k in ("max3", "guard2")}} for a in ("native", "ocm")}
    f1 = C.bind_f1(bindings)
    templates = [{"id": "UNIT_FIXTURE", "request":
                  {"kind": "clia_apply", "program_id": "@max3", "arguments": [41, -7, 12]}}]
    resolved = C.resolve_requests(templates, f1["arms"]["native"])
    assert resolved[0]["request"]["program_id"] == "1" * 64
    assert resolved[0]["request"]["arguments"] == [41, -7, 12]
    assert templates[0]["request"]["program_id"] == "@max3"
    bindings["ocm"]["programs"]["max3"]["program_sha256"] = "3" * 64
    with pytest.raises(ValueError, match="CANNOT_CHECK_IDENTICAL_DONOR_BINDING"):
        C.bind_f1(bindings)

def test_actual_native_and_ocm_unit_outputs_qualify_external_grader(tmp_path):
    G = module("grade_clia_reuse")
    from test_clia_reuse_program import descriptor
    from test_clia_reuse_vessel import fixture_state
    from clia_reuse_native import NativeLibrary
    import clia_reuse_vessel as V
    desc = descriptor()
    native = NativeLibrary(tmp_path / "native"); native.install(desc); native.bind(desc["id"])
    runtime, records, _, _ = fixture_state(tmp_path / "ocm")
    ocm_desc = V.adopt(runtime, records["jmbl_fg_max3"][0]); V.bind(runtime, ocm_desc["id"])
    evidence = []
    for arm, d in [("native", desc), ("ocm", ocm_desc)]:
        request = {"kind": "clia_apply", "program_id": d["id"], "arguments": [41, -7, 12]}
        result = native.apply(request) if arm == "native" else V.apply(runtime, request)
        row = {"id": "UNIT_FIXTURE.actual." + arm, "arm": arm, "request": request, "result": result}
        binding = {"descriptor_id": d["id"], "program_sha256": d["program_sha256"],
                   "task_id": d["task"]["task_id"], "registration": ["UNUSED_FOR_VALUE_GRADING"]}
        assert G.grade_math(row, binding, authorized=True)["status"] == "CORRECT_VALUE"
        changed = copy.deepcopy(row); changed["result"]["answer"]["value"] += 1
        assert G.grade_math(changed, binding, authorized=True)["status"] == "WRONG_VALUE"
        wrong_tuple = copy.deepcopy(row); wrong_tuple["result"]["answer"]["arguments"][2] += 1
        assert G.grade_math(wrong_tuple, binding, authorized=True)["status"] == "WRONG_BINDING"
        evidence.append({"arm": arm, "scope": "ACTUAL_ACCEPTED_UNIT_FIXTURE_NOT_PANEL",
                         "descriptor": d, "row": row, "wrong_value_record": changed,
                         "wrong_tuple_record": wrong_tuple})
    (tmp_path / "actual-unit-records.json").write_text(json.dumps(evidence, indent=2))

def test_end_revision_uses_exact_existing_support_without_query_reregistration(tmp_path):
    W = module("clia_reuse_study_worker")
    A = module("clia_reuse_study_state")
    from test_clia_reuse_program import descriptor
    from clia_reuse_study_common import write
    actor = A.Actor(tmp_path, "native")
    desc = descriptor()
    actor.library.install(desc)
    actor.bindings = {"programs": {"max3": {"descriptor_id": desc["id"],
        "registration": ["query-unit"], "history_ids": ["source-unit"]}}}
    actor.library.bind(desc["id"])
    q = {"kind": "clia_apply", "program_id": desc["id"], "arguments": [41, -7, 12]}
    answer = actor.library.apply(q)
    audit_record = actor.audit()["records"]["library/answer-" + answer["record_id"] + ".json"]
    assert audit_record.get("support") == desc["support"]
    for phase, dead in [("restart", False), ("history", True), ("withdraw", False)]:
        W.end_revision(actor, phase)
        fresh = A.Actor(tmp_path, "native"); fresh.bindings = actor.bindings
        assert ("query-unit" in fresh.library.revoked) is dead
        assert "source-unit" in fresh.library.revoked
        assert fresh.library.answer_liveness(answer["record_id"]) == ("DEAD" if dead else "LIVE")
        assert not fresh.library._bound
        actor = fresh

def test_serialized_acquisition_order_matches_protocol_actions(tmp_path):
    W = module("clia_reuse_study_worker")
    from clia_reuse_study_common import write
    path = tmp_path / "planned-config.json"
    write(path, {"tasks": {"max3": "jmbl_fg_max3", "guard2": "jmbl_fg_mpg_guard2"}})
    assert W.acquisition_tasks(json.loads(path.read_text())) == [
        ("max3", "jmbl_fg_max3"), ("guard2", "jmbl_fg_mpg_guard2")]
    with pytest.raises(ValueError):
        W.acquisition_tasks({"tasks": {"max3": "unknown", "guard2": "jmbl_fg_mpg_guard2"}})

def test_real_public_task_freeze_binding_and_changed_source_refusal():
    C = module("capture_clia_reuse")
    path = Path(C.HERE) / "results/clia-reuse-study-qualification-20260906/protocol/protocol.json"
    protocol = json.loads(path.read_text())
    tasks = C.bound_tasks(protocol)
    assert [t["task_id"] for t in tasks] == ["jmbl_fg_max3", "jmbl_fg_mpg_guard2"]
    changed = copy.deepcopy(protocol)
    changed["tasks"][0]["original_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="TASK_CHANGED"):
        C.bound_tasks(changed)

def test_six_published_protocol_files_are_exact_and_required(tmp_path):
    import shutil
    C = module("capture_clia_reuse")
    source = C.HERE / "results/clia-reuse-study-qualification-20260906/protocol"
    copied = tmp_path / "protocol"; shutil.copytree(source, copied)
    assert set(C.protocol_inventory(copied)) == {"CORE.md", "GRADING.md", "REVIEW.md",
        "protocol.json", "public-requests.jsonl", "SHA256SUMS"}
    (copied / "CORE.md").write_text("changed")
    with pytest.raises(ValueError, match="PUBLISHED_PROTOCOL_CHANGED"):
        C.protocol_inventory(copied)
