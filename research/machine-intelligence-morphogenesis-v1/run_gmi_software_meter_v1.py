#!/usr/bin/env python3
import json
import platform
import random
import statistics
import time
import tracemalloc
from pathlib import Path

SEED = 20260912
N = 5000
Q = 10000
U = 100
REPEATS = 7


def base(k):
    return 3 * k + 7


def main():
    rng = random.Random(SEED)
    keys = list(range(N))
    updated_keys = rng.sample(keys, U)
    updates = {k: base(k) + 1000003 for k in updated_keys}
    queries = updated_keys + [rng.randrange(N) for _ in range(Q - U)]

    def build_table(): return {k: base(k) for k in keys}
    def build_formula(): return None
    def build_hybrid(): return {}
    def build_scan(): return [[k, base(k)] for k in keys]

    builders = {
        "explicit_table": build_table,
        "shared_formula": build_formula,
        "shared_formula_plus_residual": build_hybrid,
        "linear_scan_records": build_scan,
    }

    def peak_build(builder):
        tracemalloc.start()
        state = builder()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return state, peak

    def update_state(name, state):
        if name == "explicit_table":
            for k, v in updates.items(): state[k] = v
        elif name == "shared_formula":
            pass
        elif name == "shared_formula_plus_residual":
            for k, v in updates.items(): state[k] = v
        elif name == "linear_scan_records":
            for k, v in updates.items():
                for rec in state:
                    if rec[0] == k:
                        rec[1] = v
                        break
        return state

    def query_state(name, state):
        checksum = 0
        mismatches = 0
        for k in queries:
            if name == "explicit_table":
                value = state[k]
            elif name == "shared_formula":
                value = base(k)
            elif name == "shared_formula_plus_residual":
                value = state.get(k, base(k))
            else:
                value = None
                for kk, vv in state:
                    if kk == k:
                        value = vv
                        break
            checksum = (checksum + value) & ((1 << 63) - 1)
            mismatches += value != updates.get(k, base(k))
        return checksum, mismatches

    peak = {}
    for name, builder in builders.items():
        _, peak[name] = peak_build(builder)

    results = {}
    for name, builder in builders.items():
        bt, ut, qt = [], [], []
        checksum = mismatch = None
        for _ in range(REPEATS):
            t0 = time.perf_counter_ns()
            state = builder()
            t1 = time.perf_counter_ns()
            update_state(name, state)
            t2 = time.perf_counter_ns()
            cs, mm = query_state(name, state)
            t3 = time.perf_counter_ns()
            bt.append(t1 - t0); ut.append(t2 - t1); qt.append(t3 - t2)
            if checksum is None:
                checksum, mismatch = cs, mm
            else:
                assert (checksum, mismatch) == (cs, mm)
        results[name] = {
            "median_build_time_ns": int(statistics.median(bt)),
            "median_update_time_ns": int(statistics.median(ut)),
            "median_query_time_ns": int(statistics.median(qt)),
            "peak_tracemalloc_bytes_for_built_state": int(peak[name]),
            "semantic_checksum": int(checksum),
            "semantic_mismatches": int(mismatch),
            "raw_build_times_ns": bt,
            "raw_update_times_ns": ut,
            "raw_query_times_ns": qt,
        }

    receipt = {
        "artifact": "GMI_SOFTWARE_METER_RECEIPT_V1",
        "status": "ENVIRONMENT_SPECIFIC_SOFTWARE_COUNTER_CALIBRATION",
        "freeze": "GMI_SOFTWARE_METER_FREEZE_V1.json",
        "runner": "run_gmi_software_meter_v1.py",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "results": results,
        "semantic_contract_pass": {
            "explicit_table": results["explicit_table"]["semantic_mismatches"] == 0,
            "shared_formula_plus_residual": results["shared_formula_plus_residual"]["semantic_mismatches"] == 0,
            "linear_scan_records": results["linear_scan_records"]["semantic_mismatches"] == 0,
            "shared_formula_negative_control_mismatches": results["shared_formula"]["semantic_mismatches"],
        },
        "measurement_caveat": "The preregistered tracemalloc field measures build-state peak only; for the hybrid this excludes residual entries inserted during updates and must not be interpreted as total post-update memory.",
        "claim_ceiling": "One Python runtime; no independent audit, energy counter, compiler equivalence or hardware-independent frontier claim.",
        "terminal": "SOFTWARE_METER_FROZEN_RUN_COMPLETE"
    }
    out = Path(__file__).with_name("GMI_SOFTWARE_METER_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
