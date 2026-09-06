"""Instrument the unchanged CLIA synthesis command sequence; diagnostic only."""
import importlib.metadata as metadata
import json
import os
import resource
import sys
import time


def phase(name, index=None):
    row = {"schema": "ocm.clia.phase.v1", "phase": name, "command_index": index,
           "monotonic_ns": time.monotonic_ns(), "process_cpu_ns": time.process_time_ns(),
           "pid": os.getpid(), "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    print(json.dumps(row, sort_keys=True), file=sys.stderr, flush=True)


def synthesize(payload, timeout_ms):
    phase("import.before")
    import cvc5
    phase("import.after")
    phase("version.before")
    if metadata.version("cvc5") != "1.3.4":
        return {"status": "CANNOT_CHECK", "reason": "cvc5 version mismatch"}
    phase("version.after")
    phase("solver.before")
    solver = cvc5.Solver()
    phase("solver.after")
    phase("options.before")
    for key, value in [("sygus", "true"), ("incremental", "false"),
                       ("tlimit-per", str(timeout_ms)), ("check-synth-sol", "true")]:
        solver.setOption(key, value)
    phase("options.after")
    phase("parser.before")
    parser = cvc5.InputParser(solver)
    parser.setStringInput(cvc5.InputLanguage.SYGUS_2_1, payload["sygus"], "bound-public-clia")
    phase("parser.after")
    output, index = [], 0
    while True:
        phase("next_command.before", index)
        command = parser.nextCommand()
        phase("next_command.after", index)
        if command.isNull():
            break
        phase("invoke.before", index)
        text = command.invoke(solver, parser.getSymbolManager())
        phase("invoke.after", index)
        phase("collect.before", index)
        if text.strip():
            output.append(text)
        phase("collect.after", index)
        index += 1
    phase("candidate.before")
    candidate = "\n".join(output)
    phase("candidate.after")
    phase("statistics.before")
    counters = {str(k): v for k, v in solver.getStatistics() if str(k) in
                ("resource::resourceUnitsUsed", "global::totalTime")}
    phase("statistics.after")
    status = "SOLUTION" if candidate.lstrip().startswith("(") and "define-fun" in candidate else "CANNOT_CHECK"
    return {"status": status, "candidate": candidate if status == "SOLUTION" else "",
            "solver_result": "solution" if status == "SOLUTION" else candidate.strip(),
            "reason": "" if status == "SOLUTION" else "native solver returned no candidate; not a no-program proof",
            "solver": "cvc5 1.3.4", "logical_counters_not_physical_cost": counters}


def main():
    phase("main.entry")
    start, cpu = time.perf_counter(), time.process_time()
    try:
        phase("request.before")
        request = json.load(sys.stdin)
        phase("request.after")
        if request["action"] != "synthesize":
            raise ValueError("diagnostic accepts synthesis only")
        result = synthesize(request["payload"], request["timeout_ms"])
    except Exception as exc:
        result = {"status": "CANNOT_CHECK", "reason": f"{type(exc).__name__}: {exc}"}
        phase("exception")
    result["metrics"] = {"worker_wall_s": time.perf_counter() - start,
                         "worker_cpu_s": time.process_time() - cpu,
                         "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         "worker_pid": os.getpid()}
    phase("serialize.before")
    encoded = json.dumps(result)
    phase("serialize.after")
    print(encoded, flush=True)
    phase("main.exit")


if __name__ == "__main__":
    main()
