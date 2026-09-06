"""One fresh actor stage. Public requests only; external oracle is never imported."""
import json
import os
from pathlib import Path
import resource
import sys
import time

START = time.perf_counter()
from clia_reuse_study_common import InvocationMeter, digest, sha, source_files, tree_bytes, write
from clia_reuse_study_state import Actor


def end_revision(actor, phase):
    target = actor.bindings["programs"]["max3"]
    changes = {"restart": ("revoke", target["history_ids"]),
               "history": ("revoke", target["registration"]),
               "withdraw": ("reinstate", target["registration"])}
    before = actor.audit()
    if phase in changes:
        action, ids = changes[phase]; actor.revise(action, ids)
    else: action, ids = "none", []
    after = actor.audit(); actor.persist()
    return {"action": action, "ids": ids, "before": before, "after": after}


def acquisition_tasks(config):
    expected = {"max3": "jmbl_fg_max3", "guard2": "jmbl_fg_mpg_guard2"}
    if config["tasks"] != expected: raise ValueError("TASK_BINDING_CHANGED")
    return [(alias, expected[alias]) for alias in ("max3", "guard2")]


def event_delta(events):
    return {**{k: sum(e["action"] == k for e in events) for k in ("application", "syntax", "verify")},
            "synthesize": sum(e["action"] == "synthesize" and bool(e.get("result", {}).get("native_invoked")) for e in events),
            "synthesis_requests": sum(e["action"] == "synthesize" for e in events)}


def execute(config, input_path):
    if source_files() != config["source_files"]: raise ValueError("SOURCE_CHANGED_BEFORE_ACTOR")
    actor = Actor(config["state"], config["arm"])
    phase = config["phase"]; rows = Path(config["rows"])
    if rows.exists(): raise ValueError("refuse rows overwrite")
    receipt = {"schema": "ocm.reuse.stage.v1", "arm": config["arm"], "phase": phase, "pid": os.getpid(),
               "f0_sha256": config["f0_sha256"], "f1_sha256": config.get("f1_sha256"),
               "input_sha256": sha(input_path), "source_files_before": source_files(), "binds": [],
               "invocations": [], "row_count": 0, "status": "RUNNING"}
    if phase != "acquire":
        if digest(actor.bindings) != config["bindings_sha256"]: raise ValueError("F1_STATE_BINDING_CHANGED")
        actor.model_path()
        receipt["entry_audit"] = actor.audit()
    else:
        if any(Path(config["state"]).iterdir()):
            # Actor constructors may create only empty native library directories.
            if any(p.is_file() for p in Path(config["state"]).rglob("*")): raise ValueError("ACQUISITION_STATE_NOT_FRESH")
        actor.setup(config["model"], config["training_manifest"])
        receipt["entry_audit"] = actor.audit()
    event_path = Path(config["events"])
    with rows.open("x") as output, event_path.open("x") as event_file:
        def observe(kind, event):
            event_file.write(json.dumps({"event": kind, "record": event}, sort_keys=True) + "\n"); event_file.flush()
        try:
            with InvocationMeter(receipt["invocations"], observe):
                if phase == "acquire":
                    from clia_tasks import load_task
                    for alias, task_id in acquisition_tasks(config):
                        start = len(receipt["invocations"]); task = load_task(task_id)
                        result = actor.acquire(alias, task, receipt["invocations"])
                        row = {"id": "acquire." + alias, "arm": config["arm"], "phase": phase,
                               "request": {"kind": "clia", "task": task}, "result": result,
                               "event_range": [start, len(receipt["invocations"])]}
                        output.write(json.dumps(row, sort_keys=True) + "\n"); output.flush(); receipt["row_count"] += 1
                    actor.save_bindings()
                else:
                    for alias, binding in actor.bindings["programs"].items():
                        try: bound = actor.bind(binding["descriptor_id"])
                        except ValueError as exc:
                            bound = {"status": "BIND_REFUSED", "reason": str(exc)}
                        receipt["binds"].append({"alias": alias, **bound})
                    for item in config["items"]:
                        request = item["request"]; start = len(receipt["invocations"])
                        authority = actor.authority(request["program_id"]) if request["kind"] == "clia_apply" else None
                        result = actor.query(request)
                        events = receipt["invocations"][start:]
                        row = {**item, "arm": config["arm"], "phase": phase, "result": result,
                               "authority": authority, "event_range": [start, len(receipt["invocations"])],
                               "invocation_events": events, "invocation_delta": event_delta(events)}
                        output.write(json.dumps(row, sort_keys=True) + "\n"); output.flush(); receipt["row_count"] += 1
                    if event_delta(receipt["invocations"])["synthesis_requests"]:
                        raise ValueError("SYNTHESIS_STILL_EXECUTED")
            receipt["exit_query_audit"] = actor.audit()
            receipt["end_revision"] = end_revision(actor, phase)
            receipt["status"] = "STAGE_COMPLETED"
        except Exception as exc:
            receipt["status"] = "CANNOT_CHECK_STAGE"; receipt["error"] = type(exc).__name__ + ":" + str(exc)
        finally:
            actor.persist()
            receipt["bindings"] = actor.bindings
            receipt["final_audit"] = actor.audit()
    own = resource.getrusage(resource.RUSAGE_SELF); child = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt.update(source_files_after=source_files(), rows_sha256=sha(rows),
        events_sha256=sha(event_path), worker_wall_s=time.perf_counter() - START,
        cpu={"self_s": own.ru_utime + own.ru_stime, "reaped_children_s": child.ru_utime + child.ru_stime,
             "scope": "separate direct self and reaped-child rusage; no full-tree completeness claim"},
        self_peak_rss_kib=own.ru_maxrss, reaped_children_peak_rss_kib=child.ru_maxrss,
        state_bytes=tree_bytes(config["state"]), ocm_runtime_imported="ocm.runtime.ocm_runtime" in sys.modules)
    if receipt["source_files_after"] != receipt["source_files_before"]: receipt["status"] = "CANNOT_CHECK_SOURCE_CHANGED"
    return receipt


if __name__ == "__main__":
    path = Path(sys.argv[1]); result = execute(json.loads(path.read_text()), path)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["status"] == "STAGE_COMPLETED" else 2)
