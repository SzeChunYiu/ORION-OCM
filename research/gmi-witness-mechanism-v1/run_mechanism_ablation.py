"""Run exactly the registered three graphs; no search, pruning, or result-driven retries."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mechanism_support import digest, load_source, observe, write_json


def validate(unit, witness_unit, source):
    registration = json.loads((unit / "REGISTRATION_V1.json").read_text())
    for name, value in registration["unit_bindings"].items():
        if digest(unit / name) != value:
            raise ValueError("registered unit changed: " + name)
    for name, value in registration["witness_bindings"].items():
        if digest(witness_unit / name) != value:
            raise ValueError("witness input changed: " + name)
    dev, binding = load_source(witness_unit, source)
    candidates = json.loads((unit / "CANDIDATES_V1.json").read_text())["arms"]
    prior = json.loads((witness_unit / "evidence/s1-recovery-20260913/INDEPENDENT_VERIFICATION_V1.json").read_text())
    witness = json.loads((witness_unit / "evidence/s1-recovery-20260913/WITNESS.json").read_text())
    if candidates["original"]["genotype"] != witness["verifier"]["atrophied_genotype"]:
        raise ValueError("exact original genotype bytes changed")
    graphs = {name: dev.morph.from_json(row["genotype"]) for name, row in candidates.items()}
    for graph in graphs.values():
        dev.morph.typecheck(graph)
    if dev.morph.fingerprint(graphs["original"]) != prior["versions"]["atrophied"]["fingerprint"]:
        raise ValueError("original graph identity failed")
    if list(dev.PROBES) != registration["probes"] or dev.B0.name != registration["basis"]:
        raise ValueError("registered probe or basis changed")
    return dev, binding, graphs, prior["versions"]["atrophied"]


def run(unit, witness_unit, output, preflight=False):
    started, cpu = time.perf_counter(), time.process_time()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="gmi-mechanism-source-") as temporary:
        dev, binding, graphs, prior = validate(unit, witness_unit, Path(temporary))
        metadata = {name: {"fingerprint": dev.morph.fingerprint(g), "carrier": dev.b1.carrier_of(g),
                           "nodes": len(g["nodes"])} for name, g in graphs.items()}
        if preflight:
            result = {"validated": True, "ecology_calls": 0, "graphs": metadata}
            write_json(output / "PREFLIGHT.json", result)
            return result
        contexts = [("control:" + name, dev.spec_of("E_smooth3"), name)
                    for name in binding["registered_interventions"]]
        contexts += [("probe:" + name, dev.spec_of(name), "standard") for name in dev.PROBES]
        outcomes, calls = {}, 0
        evaluation_started, evaluation_cpu = time.perf_counter(), time.process_time()
        for arm in ("original", "zero_vector", "variable_key"):
            outcomes[arm] = {}
            for label, spec, intervention in contexts:
                calls += 1
                phase, phase_cpu = time.perf_counter(), time.process_time()
                try:
                    row = observe(dev.ecology, spec, graphs[arm], dev.B0, intervention)
                    row["error"] = None
                except Exception:
                    row = {"error": traceback.format_exc()}
                row["seconds"] = time.perf_counter() - phase
                row["cpu_seconds"] = time.process_time() - phase_cpu
                outcomes[arm][label] = row
                write_json(output / "PARTIAL.json", {"calls": calls, "outcomes": outcomes})
        comparisons, checks = {}, {}
        for arm, rows in outcomes.items():
            errors = {label: row["error"] for label, row in rows.items() if row["error"]}
            if errors:
                checks[arm] = {"passes": False, "errors": errors}
                continue
            controls = {label[8:]: row["native_response"] for label, row in rows.items() if label.startswith("control:")}
            probes = {label[6:]: row["native_response"] for label, row in rows.items() if label.startswith("probe:")}
            minimum = min(row["capability"] for row in controls.values())
            distinct = len({tuple(row["trace"][-1]) for row in probes.values()})
            margin = (minimum - 0.8125) / dev.FX_UNIT
            checks[arm] = {"caps": {k: r["capability"] for k, r in controls.items()},
                           "minimum": minimum, "margin": margin, "distinct_probe_answers": distinct,
                           "passes": minimum >= dev.THETA and margin >= 1 and distinct >= dev.LEARNS_MIN_DISTINCT}
            comparisons[arm] = {}
            for label, row in rows.items():
                reference = prior["controls" if label.startswith("control:") else "probes"][label.split(":", 1)[1]]
                native = row["native_response"]
                baseline = outcomes["original"][label]
                comparisons[arm][label] = {"native_equals_prior": native == reference,
                    "trace_equals_original": not baseline["error"] and native["trace"] == baseline["native_response"]["trace"],
                    "final_stores_equal_original": not baseline["error"] and
                    row["passive_capture"]["final_stores"] == baseline["passive_capture"]["final_stores"]}
        receipt = {"schema": "B6FixedMechanismAblationV1", "calls": calls, "graphs": metadata,
                   "source_commit": binding["source_commit"], "checks": checks, "comparisons": comparisons,
                   "outcomes": outcomes, "interpreter": sys.version, "executable": sys.executable,
                   "executable_sha256": digest(sys.executable),
                   "registration_sha256": digest(unit / "REGISTRATION_V1.json"),
                   "evaluation_and_partial_serialization_seconds": time.perf_counter() - evaluation_started,
                   "evaluation_and_partial_serialization_cpu_seconds": time.process_time() - evaluation_cpu,
                   "total_seconds_through_receipt": time.perf_counter() - started,
                   "total_cpu_seconds_through_receipt": time.process_time() - cpu}
        write_json(output / "RECEIPT_V1.json", receipt)
        return {k: v for k, v in receipt.items() if k not in ("outcomes", "comparisons")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness-unit", type=Path, default=Path(__file__).resolve().parent.parent / "gmi-witness-recovery-v1")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parent, args.witness_unit.resolve(),
                         args.output.resolve(), args.preflight), sort_keys=True, indent=2))
