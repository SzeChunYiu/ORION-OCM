"""Source-only worker; executes fixed Git plumbing, never materialized repository code."""
from pathlib import Path
import json
import os
import sys
import time


def run(request_path, expected_sha, output):
    import acquisition_contract as c
    import materialize_boot as boot
    import materialize_phase as phase
    import materialize_git as git
    import materialize_custody as custody
    began = time.monotonic()
    request, input_binding = phase.read(request_path, expected_sha)
    out = c.new_output(output, [request_path, *[r["bare_path"] for r in request["materials"]]])
    value = dict(schema="ocm.f1.materialization-worker.v1", terminal="MATERIALIZE_REFUSED",
                 output=str(out), pid=os.getpid(), materials=[], reference=request["reference"],
                 semantic_checks_reached=0, request=input_binding)
    try:
        if c.canonical(boot.recheck()) != c.canonical(request["sources"]):
            raise ValueError("WORKER_SOURCE_BINDING")
        if c.record(Path(sys.executable).resolve())["sha256"] != c.PYTHON:
            raise ValueError("WORKER_PYTHON")
        if c.record("/usr/bin/git")["sha256"] != phase.GIT:
            raise ValueError("WORKER_GIT")
        phase.recheck(request["inputs"]); phase.clock(request["start"])
        if len(request["materials"]) != 10 or len({r["name"] for r in request["materials"]}) != 10:
            raise ValueError("MATERIAL_DENOMINATOR")
        for row in request["materials"]:
            phase.clock(request["start"])
            result = git.materialize(row["bare_path"], row["commit"], row["tree"], row["files"],
                      out / row["name"], deadline_monotonic=request["start"]["whole_deadline_monotonic"],
                      acquisition_reference=request["reference"])
            value["materials"].append(dict(name=row["name"], result=result,
                                           receipt=c.record(out / row["name"] / "RESULT.json")))
            if result["terminal"] != "MATERIALIZED": raise ValueError("MATERIALIZE_FAILED: " + row["name"])
        phase.recheck(request["inputs"]); phase.recheck([input_binding]); boot.recheck()
        phase.clock(request["start"])
        value["terminal"] = "ALL_MATERIALIZED"
        custody.verify(value, request, out)
        phase.clock(request["start"])
    except BaseException as error:
        value["terminal"] = "MATERIALIZE_REFUSED"
        value["error"] = dict(kind=type(error).__name__, message=str(error))
    value["wall_before_result_s"] = time.monotonic() - began
    c.write(out / "RESULT.json", value)
    return value


def main():
    if len(sys.argv) != 4 or not sys.flags.isolated or not sys.flags.no_site:
        raise SystemExit("use pinned Python -I -S materialize_worker.py REQUEST SHA NEW_OUTPUT")
    import types
    path = Path(__file__).resolve().with_name("materialize_boot.py")
    module = types.ModuleType("materialize_boot"); module.__file__ = str(path)
    sys.modules["materialize_boot"] = module
    raw = path.read_bytes()
    from hashlib import sha256
    module.__source_record__ = dict(path=str(path), sha256=sha256(raw).hexdigest(), bytes=len(raw))
    exec(compile(raw, str(path), "exec"), module.__dict__)
    loaded = module.load()
    result = loaded["materialize_worker"].run(*sys.argv[1:])
    return 0 if result["terminal"] == "ALL_MATERIALIZED" else 2


if __name__ == "__main__": raise SystemExit(main())
