"""Explicit opt-in search prefix; use only after preparation and scheduling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_instrument import TraceCapture, VerifierCapture, write_json
from prepare_recovery import validate_prepared


def run(prepared, output, evaluations, execute=False):
    if not execute:
        return {"search_launched": False, "reason": "explicit --run-search required"}
    if type(evaluations) is not int or not 1 <= evaluations <= 20000:
        raise ValueError("registered search prefix must be in 1..20000")
    run_started, run_cpu = time.perf_counter(), time.process_time()
    prepared, output = Path(prepared).resolve(), Path(output).resolve()
    binding = validate_prepared(prepared)
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(prepared/"source"))
    from gmi_microscope import b6_development as dev
    if list(dev.ecology.INTERVENTIONS) != binding["registered_interventions"]:
        raise ValueError("six-intervention historical bar changed")
    if Path(dev.__file__).resolve() != prepared/"source/gmi_microscope/b6_development.py":
        raise ValueError("source import came from an unintended module cache")
    seeds = json.loads((prepared/"seed_population.json").read_text())
    population = [dev.morph.from_json(row["genotype"]) for row in seeds]
    if [dev.morph.fingerprint(g) for g in population] != [row["fingerprint"] for row in seeds]:
        raise ValueError("seed genotype fingerprint mismatch")
    arm = json.loads((prepared/"historical_arm.json").read_text())
    spec = dev.spec_of("E_smooth3")
    if dev.ecology.spec_id(spec) != arm["target_spec_id"]:
        raise ValueError("target specification changed")
    started = time.perf_counter()
    extractor = dev.validate_extractor()
    if not extractor["valid"]:
        raise ValueError("historical rule-42 extractor failed")
    calibration_seconds = time.perf_counter()-started
    bc, _ = dev.eco_axis.best_constant(dev.ecology.target_of(spec), dev.smooth.UNSEEN)
    trace = TraceCapture(output/"raw_theta_trace.jsonl")
    started, cpu = time.perf_counter(), time.process_time()
    try:
        archive, n, failed, tries, history = dev.b1.search(
            dev.ecology.target_of(spec), 1, evaluations, seed_population=population, trace=trace)
    finally:
        trace.close()
    search_seconds, search_cpu = time.perf_counter()-started, time.process_time()-cpu
    compact = [{k: r[k] for k in ("n_eval", "capability", "desc", "n_nodes", "origin")} |
               {"fingerprint": dev.morph.fingerprint(dev.morph.from_json(r["genotype"]))} for r in trace]
    expected = [r for r in arm["trace_compact"] if r["n_eval"] <= n]
    prefix_matches = compact == expected
    write_json(output/"trace_identity.json", {"prefix_matches": prefix_matches,
               "new_count": len(compact), "historical_count": len(expected),
               "full_historical_execution_identity_proven": False})
    # Mismatch is retained; a new witness is still a valid retrospective target.
    started, cpu = time.perf_counter(), time.process_time()
    with VerifierCapture(dev, output) as capture:
        found = dev.first_of_class(trace, spec, bc, ("DENSE",))
    verification_seconds, verification_cpu = time.perf_counter()-started, time.process_time()-cpu
    result = {"schema": "B6RetrospectiveWitnessRecoveryRunV1", "search_launched": True,
              "purpose": "retrospective witness recovery, not prospective prediction",
              "source_commit": binding["source_commit"], "search_evaluations": n,
              "failed_phenotypes": failed, "proposal_tries_charged": tries,
              "source_acquisition_excluded": [20000, 20000], "prefix_matches": prefix_matches,
              "first_historical_instrument_dense": found,
              "verifier_reported_evaluations": capture.charged, "verifier_actual_ecology_calls": capture.actual_calls,
              "extractor_validation_replays": 2*len(dev.PROBES),
              "search_seconds": search_seconds, "search_cpu_seconds": search_cpu,
              "verification_seconds": verification_seconds, "verification_cpu_seconds": verification_cpu,
              "trace_io_seconds_included_in_search": trace.io_seconds, "calibration_seconds": calibration_seconds,
              "history": history, "interpreter": sys.version, "executable": sys.executable,
              "executable_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
              "platform": platform.platform(), "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
              "total_seconds_through_receipt": time.perf_counter()-run_started,
              "total_cpu_seconds_through_receipt": time.process_time()-run_cpu,
              "capture_code_sha256": {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                  for name in ("recover_witness.py", "capture_instrument.py", "prepare_recovery.py")},
              "independent_verification_pending": found["found"]}
    write_json(output/"RECOVERY_RUN.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--evaluations", type=int, default=128)
    parser.add_argument("--run-search", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.prepared, args.output, args.evaluations, args.run_search), indent=2, sort_keys=True))
