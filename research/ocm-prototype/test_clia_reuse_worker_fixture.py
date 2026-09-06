"""Fresh-worker controls use exposed unit programs/tuples only, never study acquisitions."""
import json
import os
from pathlib import Path
import sys

import pytest
from clia_reuse_study_common import HERE, REPO, digest, run_process, sha, source_files, write
from clia_reuse_study_state import Actor


def emit_unit_workers(tmp_path, arm):
    from test_clia_reuse_program import UNIT_PROGRAMS
    from clia_tasks import load_task
    import clia_reuse_descriptor as D
    root = tmp_path / "state"
    actor = Actor(root, arm)
    if arm == "ocm":
        from test_clia_reuse_vessel import fixture_state
        actor.runtime, records, _, shared = fixture_state(root)
    for alias, task_id in [("max3", "jmbl_fg_max3"), ("guard2", "jmbl_fg_mpg_guard2")]:
        task = load_task(task_id)
        history = actor.evidence({"UNIT_FIXTURE": "known program, no acquisition run", "task_id": task_id}, "history")
        if arm == "native":
            query = actor.evidence({"UNIT_FIXTURE": task_id}, "query-registration")["id"]
            profile = {"lower": [[query, "unit-shared"]], "upper": [[query, "unit-shared"]]}
            proposal = {"status": "SOLUTION", "candidate": UNIT_PROGRAMS[task_id],
                        "task_sha256": task["task_sha256"], "grammar_id": task["grammar"]["id"]}
            desc = D.create(task, proposal, profile, history=[history["id"]])
            actor.library.install(desc)
            proof = "acquisitions/" + alias + ".json"
            write(root / proof, {"UNIT_FIXTURE": proposal, "support": desc["support"]})
        else:
            proof, query, _ = records[task_id]
            desc = actor.V.adopt(actor.runtime, proof, history=[history["id"]])
        actor.bindings["programs"][alias] = {"descriptor_id": desc["id"], "program_sha256": desc["program_sha256"],
            "task_id": task_id, "task_sha256": task["task_sha256"], "checker_identity": digest(desc["checker_prior"]),
            "support": desc["support"], "registration": [query], "history_ids": [history["id"]],
            "history_records": [history], "proof_id": proof, "descriptor": desc}
    model = root / "UNIT_FIXTURE_NOT_A_MODEL"
    model.write_bytes(b"UNIT_FIXTURE: never syntax inference")
    actor.bindings.update(model_file=model.name, model_sha256=sha(model))
    actor.save_bindings()
    processes = []
    for phase in ("warm", "restart", "history", "withdraw", "restore"):
        prefix = tmp_path / phase
        items = [{"id": "UNIT_FIXTURE." + alias, "request": {"kind": "clia_apply",
                  "program_id": b["descriptor_id"], "arguments": [41, -7, 12]}}
                 for alias, b in actor.bindings["programs"].items()]
        config = {"phase": phase, "arm": arm, "state": str(root), "source_files": source_files(),
            "bindings_sha256": digest(actor.bindings), "f0_sha256": "UNIT_FIXTURE", "f1_sha256": "UNIT_FIXTURE",
            "rows": str(prefix.with_suffix(".rows.jsonl")), "events": str(prefix.with_suffix(".events.jsonl")), "items": items}
        input_path = prefix.with_suffix(".input.json"); write(input_path, config)
        process = run_process([sys.executable, str(HERE / "clia_reuse_study_worker.py"), str(input_path)],
            prefix, seconds=30, cwd=REPO, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        out = json.loads(prefix.with_suffix(".stdout").read_text())
        write(prefix.with_suffix(".receipt.json"), {"process": process, "worker": out})
        assert process["exit_code"] == 0, out
        assert out["status"] == "STAGE_COMPLETED"
        assert all(e["action"] != "synthesize" for e in out["invocations"])
        assert len(out["binds"]) == 2
        rows = [json.loads(line) for line in prefix.with_suffix(".rows.jsonl").read_text().splitlines()]
        from grade_clia_reuse import grade_math
        for row, alias in zip(rows, ("max3", "guard2")):
            authorized = phase != "withdraw" or alias != "max3"
            grade = grade_math(row, actor.bindings["programs"][alias], authorized=authorized)
            assert grade["status"] == ("CORRECT_VALUE" if authorized else "EXPECTED_POLICY_REFUSAL"), grade
        assert out["entry_audit"]["programs"][actor.bindings["programs"]["max3"]["descriptor_id"]]["host_bound"] is False
        processes.append(process["pid"])
    assert len(set(processes)) == 5
    return {"bindings": actor.bindings, "root": str(tmp_path), "pids": processes}


@pytest.mark.parametrize("arm", ["native", "ocm"])
def test_five_fresh_unit_workers_preserve_revision_authority_and_selected_values(tmp_path, arm):
    emit_unit_workers(tmp_path, arm)
