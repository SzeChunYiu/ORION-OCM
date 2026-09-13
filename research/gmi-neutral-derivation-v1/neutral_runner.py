"""Replay the separately frozen predictions against complete executable synthesis."""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import resource
from time import perf_counter

from neutral_machine import (encode, execute, inputs, observable_property,
                             verify_signature, verify_trace, weights)
from neutral_search import enumerate_space, minimize, verify_optimum

REGISTRATION_SHA256 = "3f9690238b81bf06b70e09763396e245a4ebcc942af7ab45df2af25da0fba1a3"


def check_prediction(case, cost, properties):
    if cost != Fraction(case["minimum"]) or sorted(properties) != sorted(case["properties"]):
        raise ValueError("Registered cost/property prediction is false")


def run_case(case, registration, levels):
    base = registration["prices"]
    prices = (base["read"], base["binary"], case["branch"], base["description_bit"])
    probabilities = weights(case["arity"], case["p"])
    cost, winners = minimize(levels, case["truth"], probabilities, prices)
    verify_optimum(levels, case["truth"], probabilities, prices, cost, winners)
    properties = sorted({observable_property(sig) for _, sig, _ in winners})
    status = "CHECKED"
    try:
        check_prediction(case, cost, properties)
    except ValueError:
        status = "PREDICTION_RED"
    certificates = []
    for size, sig, fiber in winners:
        verify_signature(fiber.program, case["arity"], sig)
        trace_records = []
        for bits in inputs(case["arity"]):
            output, events = execute(fiber.program, bits)
            verify_trace(fiber.program, bits, output, events)
            trace_records.append({"input": bits, "output": output, "events": events})
        certificates.append({"nodes": size, "encoding": encode(fiber.program),
                             "program": fiber.program, "trace_signature": sig,
                             "raw_program_multiplicity": fiber.multiplicity,
                             "property": observable_property(sig), "traces": trace_records})
    return {"id": case["id"], "split": case["split"], "status": status,
            "minimum": str(cost), "properties": properties,
            "optimal_trace_fibers": len(winners),
            "optimal_raw_programs": sum(f.multiplicity for _, _, f in winners),
            "all_optimal_fiber_certificates": certificates}


def run_registered(registration, spaces):
    return [run_case(c, registration, spaces[c["arity"], c["nodes"]])
            for c in registration["cases"]]


def deterministic_receipt(receipt):
    """Strip only the three named instrumentation fields; retain all science."""
    result = deepcopy(receipt)
    result.pop("ranking_and_certificate_seconds", None)
    for search in result.get("searches", []):
        search.pop("enumeration_seconds", None)
        search.pop("process_peak_resident_kib_linux", None)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--development-only", action="store_true")
    parser.add_argument("--receipt")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    raw = (root / "neutral_registration.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != REGISTRATION_SHA256:
        raise ValueError("Registration changed after its pre-execution freeze")
    registration = json.loads(raw)
    cases = [c for c in registration["cases"]
             if not args.development_only or c["split"] == "development"]
    spaces = {}
    searches = []
    for arity, bound in sorted({(c["arity"], c["nodes"]) for c in cases}):
        started = perf_counter()
        levels, counters = enumerate_space(arity, bound)
        spaces[arity, bound] = levels
        searches.append({"arity": arity, "node_bound": bound,
                         "description_bit_bound": 7 * bound,
                         "enumeration_seconds": perf_counter() - started,
                         "process_peak_resident_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         **counters})
    started = perf_counter()
    rows = [run_case(c, registration, spaces[c["arity"], c["nodes"]]) for c in cases]
    sources = list(root.glob("neutral_*.py")) + list(root.glob("test_neutral_*.py"))
    receipt = {"schema": "GMI_NEUTRAL_SYNTHESIS_RECEIPT_V1",
               "status": "CHECKED" if all(r["status"] == "CHECKED" for r in rows) else "PREDICTION_RED",
               "registration_sha256": digest, "cases": rows, "searches": searches,
               "ranking_and_certificate_seconds": perf_counter() - started,
               "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(sources)},
               "scope": "Exact finite grammar; parameter/function holdouts; no unseen-family or neural claim."}
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        with Path(args.receipt).open("x") as handle:
            handle.write(text)
    print(text)
    if receipt["status"] != "CHECKED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
