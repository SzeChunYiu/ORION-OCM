"""One measured chunk of the frozen G1 stream, native parent or OCM."""
from pathlib import Path
import json
import os
import resource
import shutil
import sys
import time
from udpipe_donor import predict, sha256
from syntax_contract import validate, validate_tokens
from clia_solver import propose
from clia_checker import check
from clia_tasks import validate_task


def source_files():
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    files = sorted({*here.glob("g1_*.py"), *here.glob("clia_*.py"),
                    here / "syntax_contract.py", here / "udpipe_donor.py",
                    here / "vendor/conll18_ud_eval.py", *repo.glob("src/ocm/**/*.py")})
    return {str(p.relative_to(repo)): sha256(p) for p in files}


def native(request, model, digest):
    if request["kind"] == "syntax":
        output = predict(request["tokens"], model, digest)
        reason = validate(output.get("words"), request["tokens"]) if output["status"] == "PREDICTED" else output.get("reason")
        accepted = output["status"] == "PREDICTED" and reason is None
        checked = {"status": "PASS" if accepted else ("CANNOT_CHECK" if output["status"] == "CANNOT_CHECK" else "FAIL"), "reason": reason,
                   "scope": "STRUCTURE_ONLY_NO_GOLD_CORRECTNESS"}
        claim = "MODEL_SUPPORTED_SYNTAX_OBSERVATION"
    else:
        output = propose(request["task"])
        checked = check(request["task"], output)
        accepted = checked["status"] == "PASS"
        claim = "SPECIFICATION_VERIFIED_PROGRAM"
    return {"status": "ACCEPTED_PARENT" if accepted else "NOT_ACCEPTED", "accepted": accepted,
            "answer": output if accepted else None, "proposal_diagnostic": None if accepted else output,
            "claim": claim if accepted else None, "host_check": checked}


def execute(config):
    start = time.perf_counter()
    state = Path(config["state"])
    rows_path = Path(config["rows"])
    if rows_path.exists():
        raise ValueError("refuse to overwrite predictions")
    runtime = None
    if config["arm"] == "ocm":
        import g1_vessel as G
        from g1_field import archive_path, setup
        runtime = G.OCMRuntime(state, config=G.CONFIG)
        if config["chunk"] == 0:
            fixture = setup(runtime, Path(config["model"]), config["training_manifest"])
            assert fixture["model_sha256"] == config["model_sha256"]
        model = archive_path(runtime, config["model_sha256"])
    else:
        model = state / "archive" / (config["model_sha256"] + ".udpipe")
        if config["chunk"] == 0:
            model.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(config["model"], model)
            (state / "training.json").write_text(json.dumps(config["training_manifest"], sort_keys=True) + "\n")
    if sha256(model) != config["model_sha256"]:
        raise ValueError("model archive mismatch")
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    with rows_path.open("x") as stream:
        for item in config["items"]:
            request = item["request"]
            if request["kind"] == "syntax":
                assert set(request) == {"kind", "tokens"}; validate_tokens(request["tokens"])
            else:
                assert request["kind"] == "clia" and set(request) == {"kind", "task"}; validate_task(request["task"])
            result = G.query(runtime, item["request"]) if runtime is not None else native(item["request"], model, config["model_sha256"])
            row = {"id": item["id"], "arm": config["arm"], "result": result}
            if runtime is None:
                # Ordinary append-only memory is a native reference, not an OCM field.
                with (state / "memory.jsonl").open("a") as memory:
                    memory.write(json.dumps(row, sort_keys=True) + "\n")
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"pid": os.getpid(), "arm": config["arm"], "chunk": config["chunk"],
            "rows": len(config["items"]), "worker_body_wall_s": time.perf_counter() - start,
            "process_cpu_s": own.ru_utime + own.ru_stime,
            "terminated_child_cpu_s": children.ru_utime + children.ru_stime,
            "process_peak_rss_kib": own.ru_maxrss, "children_peak_rss_kib": children.ru_maxrss,
            "durable_state_bytes": sum(p.stat().st_size for p in state.rglob("*") if p.is_file()),
            "rows_sha256": sha256(rows_path), "source_files": source_files(),
            "ocm_runtime_imported": "ocm.runtime.ocm_runtime" in sys.modules}


if __name__ == "__main__":
    print(json.dumps(execute(json.loads(Path(sys.argv[1]).read_text())), sort_keys=True))
