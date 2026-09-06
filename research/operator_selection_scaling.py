"""Matched exact operator selection study; run outside service, on one host.

This measures catalogue compilation/selection/rebuild, not whole OCM cognition.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import math
from pathlib import Path
import platform
import resource
import statistics
import time

from ocm.runtime.operator_index import SolveOperatorIndex
from ocm.runtime.solve import OperatorSpec


def backend(*args):
    return {"value": 1}


def timed(fn):
    start_cpu = time.process_time()
    start = time.perf_counter()
    value = fn()
    return value, {"wall_seconds": time.perf_counter() - start,
                   "cpu_seconds": time.process_time() - start_cpu}


def summary(values):
    ordered = sorted(values)
    return {"median": statistics.median(values),
            "p95": ordered[max(0, math.ceil(len(values) * .95) - 1)],
            "samples": len(values)}


def scan(operators, active):
    return tuple(op for op in operators if set(op.input_atoms) <= active)


def study(size, repeats):
    operators, catalogue_cost = timed(lambda: tuple(
        OperatorSpec(f"op:{i}", "1", backend, ("common", f"input:{i}"))
        for i in range(size)))
    index, compile_cost = timed(lambda: SolveOperatorIndex(operators))
    active = frozenset(("common", f"input:{size // 2}"))
    expected = scan(operators, active)
    assert len(expected) == 1
    scan_times, indexed_times = [], []
    scan_cpu, indexed_cpu = [], []
    for iteration in range(repeats):
        # Alternate order to avoid always giving one arm the warmed CPU.
        arms = (("scan", lambda: scan(operators, active)),
                ("index", lambda: index.select(active)))
        if iteration % 2:
            arms = arms[::-1]
        for name, fn in arms:
            result, cost = timed(fn)
            selected = result if name == "scan" else result.operators
            assert selected == expected, "EXACT_ORDER_OR_CANDIDATE_DRIFT"
            (scan_times if name == "scan" else indexed_times).append(cost["wall_seconds"])
            (scan_cpu if name == "scan" else indexed_cpu).append(cost["cpu_seconds"])
    extra = OperatorSpec("new", "1", backend, ("common", "new:input"))
    rebuilt, rebuild_cost = timed(lambda: SolveOperatorIndex((*operators, extra)))
    assert rebuilt.select(("common", "new:input")).operators == (extra,)
    assert not index.select(("common", "new:input")).operators
    delta = statistics.median(scan_times) - statistics.median(indexed_times)
    return {
        "operators": size, "relevant_operators": 1, "parity": "EXACT_CANDIDATES_AND_ORDER",
        "catalogue_acquisition_shared": catalogue_cost, "cold_index_compile": compile_cost,
        "cold_work": index.build_work, "warm_work": dict(index.select(active).work),
        "full_scan_warm_wall_seconds": summary(scan_times),
        "indexed_warm_wall_seconds": summary(indexed_times),
        "full_scan_warm_cpu_seconds": summary(scan_cpu),
        "indexed_warm_cpu_seconds": summary(indexed_cpu),
        "catalogue_change_full_rebuild": rebuild_cost,
        "compile_amortization_queries_estimate": math.ceil(compile_cost["wall_seconds"] / delta) if delta > 0 else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 10000, 100000, 1000000])
    parser.add_argument("--repeats", type=int, default=11)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 2 or any(n < 1 for n in args.sizes):
        parser.error("positive catalogue sizes and at least two repeats required")
    rows = [study(n, args.repeats) for n in args.sizes]
    global_ops = tuple(OperatorSpec(f"global:{i}", "1", backend, ()) for i in range(1000))
    global_result = SolveOperatorIndex(global_ops).select(())
    assert global_result.operators == global_ops
    report = {
        "schema": "ocm.operator-selection-study.v1",
        "terminal": "EXACT_OPERATOR_SELECTION_SCALING_SUPPORTED",
        "whole_machine_terminal": "NOT_MEASURED",
        "parent": "same immutable ordered catalogue; exact subset scan; identical backend/warrant objects",
        "python": platform.python_version(), "platform": platform.platform(),
        "source_sha256": {str(p.relative_to(Path(__file__).resolve().parents[1])): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (Path(__file__).resolve(),
                                    Path(__file__).resolve().parents[1] / "src/ocm/runtime/operator_index.py",
                                    Path(__file__).resolve().parents[1] / "src/ocm/runtime/solve.py")},
        "measurement_conditions": "Paired alternating single-process development run; host exclusivity not established; timing descriptive.",
        "measurements": rows,
        "global_hostile": {"operators": len(global_ops), "work": dict(global_result.work),
                           "terminal": "GLOBAL_WORK_REQUIRED_ALL_OPERATORS_APPLICABLE"},
        "process_peak_rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_units": "KiB on Linux; bytes on macOS",
        "limitations": ["No claim about whole runtime latency, navigation, extraction or persistence.",
                        "Selection counters are exact logical cardinalities, not CPU instructions.",
                        "Amortization estimate includes index compile only; storage and lifetime maintenance remain separate.",
                        "Changed catalogues rebuild; liveness is checked downstream on every execution."],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "rows": len(rows), "terminal": report["terminal"]}))


if __name__ == "__main__":
    main()
