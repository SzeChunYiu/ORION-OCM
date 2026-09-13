"""Fresh-process direct controls on captured raw and atrophied genotypes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_instrument import write_json
from prepare_recovery import validate_prepared


def verify(prepared, witness, output):
    complete_started, complete_cpu = time.perf_counter(), time.process_time()
    prepared, witness = Path(prepared).resolve(), Path(witness)
    binding = validate_prepared(prepared)
    sys.path.insert(0, str(prepared/"source"))
    from gmi_microscope import b6_development as dev
    if Path(dev.__file__).resolve() != prepared/"source/gmi_microscope/b6_development.py":
        raise ValueError("unintended source import")
    if list(dev.ecology.INTERVENTIONS) != binding["registered_interventions"]:
        raise ValueError("historical intervention bar changed")
    data = json.loads(witness.read_text())
    spec = dev.spec_of("E_smooth3")
    bc, _ = dev.eco_axis.best_constant(dev.ecology.target_of(spec), dev.smooth.UNSEEN)
    versions = {"raw": data["raw_genotype"], "atrophied": data["verifier"]["atrophied_genotype"]}
    result, calls = {}, 0
    started, cpu = time.perf_counter(), time.process_time()
    for name, encoded in versions.items():
        g = dev.morph.from_json(encoded)
        dev.morph.typecheck(g)
        controls, probes = {}, {}
        for intervention in binding["registered_interventions"]:
            calls += 1
            controls[intervention] = dev.ecology.run_genotype(spec, g, dev.B0, intervention)
        for probe in dev.PROBES:
            calls += 1
            probes[probe] = dev.ecology.run_genotype(dev.spec_of(probe), g, dev.B0, "standard")
        caps = {key: value["capability"] for key, value in controls.items()}
        distinct = len({tuple(value["trace"][-1]) for value in probes.values()})
        minimum = min(caps.values())
        result[name] = {"fingerprint": dev.morph.fingerprint(g), "carrier": dev.b1.carrier_of(g),
                        "controls": controls, "probes": probes, "caps": caps, "min_capability": minimum,
                        "margin_from_registered_caps": (minimum-bc)/dev.FX_UNIT, "distinct_probe_answers": distinct,
                        "passes": minimum >= dev.THETA and (minimum-bc)/dev.FX_UNIT >= 1
                                  and distinct >= dev.LEARNS_MIN_DISTINCT}
    comparisons = {"raw_fingerprint": result["raw"]["fingerprint"] == data["raw_fingerprint"],
                   "atrophied_fingerprint": result["atrophied"]["fingerprint"] == data["verifier"]["atrophied_fingerprint"],
                   "raw_caps": result["raw"]["caps"] == data["verifier"]["caps"],
                   "atrophied_minimum": result["atrophied"]["min_capability"] == data["verifier"]["atrophied_min_over_six"],
                   "atrophied_dense": result["atrophied"]["carrier"] == "DENSE"}
    passed = all(comparisons.values()) and all(row["passes"] for row in result.values())
    receipt = {"schema": "B6FreshProcessWitnessVerificationV1", "verified": passed,
               "terminal": "VERIFIED_FROZEN_SIX_WITH_ERROR_FREE_PROBES" if passed else "CORRECTED_WITNESS_VERIFICATION_FAILED",
               "source_commit": binding["source_commit"], "witness_sha256": hashlib.sha256(witness.read_bytes()).hexdigest(),
               "interventions": binding["registered_interventions"], "comparisons": comparisons, "versions": result,
               "additional_actual_ecology_calls": calls, "seconds": time.perf_counter()-started,
               "cpu_seconds": time.process_time()-cpu, "interpreter": sys.version, "executable": sys.executable,
               "total_seconds_through_receipt": time.perf_counter()-complete_started,
               "total_cpu_seconds_through_receipt": time.process_time()-complete_cpu,
               "verification_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "claim_scope": "same primitive evaluator, separately composed fresh-process checks; no independent VM implementation"}
    write_json(output, receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", required=True)
    parser.add_argument("--witness", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = verify(args.prepared, args.witness, args.output)
    print(json.dumps({k: v for k, v in result.items() if k != "versions"}, indent=2, sort_keys=True))
    raise SystemExit(0 if result["verified"] else 1)
