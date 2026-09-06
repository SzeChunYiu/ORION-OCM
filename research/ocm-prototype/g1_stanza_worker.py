"""Same G1 chunk protocol with a fixed Stanza donor; native never imports OCM."""
from pathlib import Path
from importlib.metadata import version
import json
import os
import resource
import sys
import time
from matched_g1_worker import source_files as original_source_files
from syntax_contract import validate_tokens
from clia_tasks import validate_task
import clia_solver
import clia_checker
import g1_stanza_donor as D
import g1_stanza_profile as P


def source_files():
    files = original_source_files()
    here = Path(__file__).resolve().parent
    files["research/ocm-prototype/stanza_donor.py"] = P.digest_bytes((here/"stanza_donor.py").read_bytes())
    return files


def native(request, bundle, profile):
    if request["kind"] == "syntax":
        output = D.predict(request["tokens"], bundle, profile)
        checked = D.check(profile, request, output)
        claim = "MODEL_SUPPORTED_SYNTAX_OBSERVATION"
    else:
        output = clia_solver.propose(request["task"])
        checked = clia_checker.check(request["task"], output)
        claim = "SPECIFICATION_VERIFIED_PROGRAM"
    accepted = checked["status"] == "PASS"
    return {"status": "ACCEPTED_PARENT" if accepted else "NOT_ACCEPTED", "accepted": accepted,
        "answer": output if accepted else None, "proposal_diagnostic": None if accepted else output,
        "claim": claim if accepted else None, "host_check": checked}


def execute(config):
    start = time.perf_counter()
    if config["arm"] not in ("native", "ocm"):
        raise ValueError("unknown fixed arm")
    profile = P.validate(config["donor_profile"])
    requirements = {p["name"]: p["version"] for p in profile["packages"]} | profile["clia_additions"]
    observed = {name: version(name) for name in requirements}
    if observed != requirements:
        raise ValueError("combined runtime differs from pinned Stanza plus CLIA additions")
    state = Path(config["state"]); rows_path = Path(config["rows"])
    if rows_path.exists():
        raise ValueError("refuse to overwrite selected predictions")
    if config["model_sha256"] != profile["model_sha256"]:
        raise ValueError("configuration model identity")
    runtime = None
    if config["arm"] == "ocm":
        import g1_stanza_vessel as G
        runtime = G.G.OCMRuntime(state, config=G.G.CONFIG)
        if config["chunk"] == 0:
            G.setup(runtime, Path(config["model"]), profile)
        from g1_field import MODEL, payload
        if payload(runtime.state.ks, MODEL).get("stanza_profile") != profile:
            raise ValueError("persisted OCM profile changed")
    elif config["chunk"] == 0:
        P.prepare(state, Path(config["model"]), profile)
    bundle = P.verify_archive(P.archive_path(state, profile), profile)
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    with rows_path.open("x") as stream:
        for item in config["items"]:
            request = item["request"]
            if request["kind"] == "syntax" and set(request) == {"kind", "tokens"}:
                validate_tokens(request["tokens"])
            elif request["kind"] == "clia" and set(request) == {"kind", "task"}:
                validate_task(request["task"])
            else:
                raise ValueError("public supplied-word/task contract")
            result = G.query(runtime, request) if runtime is not None else native(request, bundle, profile)
            row = {"id": item["id"], "arm": config["arm"], "result": result}
            if runtime is None:
                with (state/"memory.jsonl").open("a") as memory:
                    memory.write(json.dumps(row, sort_keys=True)+"\n")
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True)+"\n")
            stream.flush()
    P.verify_archive(bundle, profile)
    own = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    state_files = {str(p.relative_to(state)): p.stat().st_size for p in state.rglob("*") if p.is_file()}
    return {"pid": os.getpid(), "arm": config["arm"], "chunk": config["chunk"], "rows": len(config["items"]),
        "worker_body_wall_s": time.perf_counter()-start, "process_cpu_s": own.ru_utime+own.ru_stime,
        "waited_direct_children_cpu_s": children.ru_utime+children.ru_stime,
        "total_process_tree_cpu_s": None, "complete_cpu_custody": False,
        "cpu_scope": "Worker self and waited children reported separately; whole tree completeness UNKNOWN.",
        "process_peak_rss_kib": own.ru_maxrss, "children_peak_rss_kib": children.ru_maxrss,
        "durable_state_bytes": sum(state_files.values()), "durable_state_file_bytes": state_files,
        "compiled_state": profile["compiled_state"], "profile_id": profile["id"],
        "runtime_versions": observed, "rows_sha256": P.digest_bytes(rows_path.read_bytes()),
        "source_files": source_files(), "ocm_runtime_imported": "ocm.runtime.ocm_runtime" in sys.modules}


if __name__ == "__main__":
    print(json.dumps(execute(json.loads(Path(sys.argv[1]).read_text())), sort_keys=True))
