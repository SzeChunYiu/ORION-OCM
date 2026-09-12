#!/usr/bin/env python3
"""Architecture-blind finite formula synthesis and scoped closure checks.

Standard-library only. Trees/formulas, NOT general shared-subexpression DAGs.
Run --freeze first; commit source and freeze before --run. Never overwrite receipts.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import heapq
import itertools
import json
from pathlib import Path
import platform
import time

BASE = "f211f99a9aaefcfcca05850e1930885701358bcc"
OPS = {"not", "and", "or", "xor", "nand", "nor"}
ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "GMI_PRIMITIVE_CLOSURE_FREEZE_V1.json"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def put(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n")


def terminals(n: int) -> dict[int, tuple]:
    mask = (1 << (1 << n)) - 1
    result = {0: ("c", 0), mask: ("c", 1)}
    for i in range(n):
        result[sum(((x >> i) & 1) << x for x in range(1 << n))] = ("v", i)
    return result


def apply(op: str, a: int, b: int, mask: int) -> int:
    if op == "not":
        return mask ^ a
    if op == "and":
        return a & b
    if op == "or":
        return a | b
    if op == "xor":
        return a ^ b
    if op == "nand":
        return mask ^ (a & b)
    if op == "nor":
        return mask ^ (a | b)
    raise ValueError("Unknown primitive")


def validate_prices(prices: dict[str, int]) -> None:
    if not prices or set(prices) - OPS or any(type(c) is not int or c <= 0 for c in prices.values()):
        raise ValueError("Only registered primitives and positive integer prices are legal")


def synthesize(n: int, prices: dict[str, int]) -> dict:
    """Positive-cost grammar shortest derivations over semantic truth tables."""
    validate_prices(prices)
    size = 1 << (1 << n)
    mask = size - 1
    distances, expressions = [10**9] * size, [None] * size
    queue, settled, done, attempts = [], [], set(), 0
    for state, expression in terminals(n).items():
        distances[state], expressions[state] = 0, expression
        heapq.heappush(queue, (0, state))

    def offer(state: int, cost: int, expression: tuple) -> None:
        if cost < distances[state]:
            distances[state], expressions[state] = cost, expression
            heapq.heappush(queue, (cost, state))

    while queue:
        cost, a = heapq.heappop(queue)
        if a in done or cost != distances[a]:
            continue
        done.add(a)
        settled.append(a)
        for op in sorted(prices):
            if op == "not":
                attempts += 1
                offer(apply(op, a, 0, mask), cost + prices[op], (op, expressions[a]))
            else:
                for b in settled:
                    attempts += 1
                    offer(apply(op, a, b, mask), cost + distances[b] + prices[op], (op, expressions[a], expressions[b]))
    if len(done) != size:
        raise ValueError("Grammar not complete at the registered finite scope")
    return {"n": n, "prices": prices, "costs": distances, "expressions": expressions, "relaxations": attempts}


def scalar(expression: tuple, row: int, prices: dict[str, int], n: int) -> tuple[int, int]:
    op = expression[0]
    if op == "c":
        if len(expression) != 2 or expression[1] not in (0, 1):
            raise ValueError("Bad constant")
        return expression[1], 0
    if op == "v":
        if len(expression) != 2 or not 0 <= expression[1] < n:
            raise ValueError("Bad variable")
        return (row >> expression[1]) & 1, 0
    if op not in prices or len(expression) != (2 if op == "not" else 3):
        raise ValueError("Illegal syntax")
    a, ca = scalar(expression[1], row, prices, n)
    if op == "not":
        return int(not a), ca + prices[op]
    b, cb = scalar(expression[2], row, prices, n)
    values = {"and": bool(a) and bool(b), "or": bool(a) or bool(b), "xor": a != b,
              "nand": not (bool(a) and bool(b)), "nor": not (bool(a) or bool(b))}
    return int(values[op]), ca + cb + prices[op]


def certify(certificate: dict) -> dict:
    """Achievable witnesses plus all Bellman inequalities certify exact optima."""
    n, prices = certificate["n"], certificate["prices"]
    validate_prices(prices)
    size, inequalities, scalar_rows = 1 << (1 << n), 0, 0
    d, expressions = certificate["costs"], certificate["expressions"]
    if len(d) != size or len(expressions) != size:
        raise ValueError("Missing certificate state")
    for state in range(size):
        if type(d[state]) is not int or d[state] < 0:
            raise ValueError("Invalid distance")
        for row in range(1 << n):
            value, cost = scalar(expressions[state], row, prices, n)
            scalar_rows += 1
            if value != ((state >> row) & 1) or cost != d[state]:
                raise ValueError("Witness mismatch")
    for state in terminals(n):
        if d[state] != 0:
            raise ValueError("Terminal price mismatch")
    for op, price in prices.items():
        for a in range(size):
            for b in (range(size) if op != "not" else (0,)):
                inequalities += 1
                if d[apply(op, a, b, size - 1)] > d[a] + (d[b] if op != "not" else 0) + price:
                    raise ValueError("Bellman lower-bound certificate fails")
    return {"witness_rows": scalar_rows, "bellman_inequalities": inequalities}


def bounded(n: int, cap: int) -> dict:
    """All behaviors realizable by unit-cost formulas of at most cap operators."""
    mask, levels, attempts = (1 << (1 << n)) - 1, [], 0
    best = {f: (0, e) for f, e in terminals(n).items()}
    levels.append(sorted(best))
    for k in range(1, cap + 1):
        new = {}
        for a in levels[k - 1]:
            attempts += 1
            f = mask ^ a
            if f not in best:
                new.setdefault(f, ("not", best[a][1]))
        for i in range(k):
            j = k - 1 - i
            if i > j:
                continue
            for a in levels[i]:
                for b in levels[j]:
                    if i == j and a > b:
                        continue
                    for op in ("and", "or", "xor"):
                        attempts += 1
                        f = apply(op, a, b, mask)
                        if f not in best:
                            new.setdefault(f, (op, best[a][1], best[b][1]))
        levels.append(sorted(new))
        best.update({f: (k, e) for f, e in new.items()})
    return {"best": best, "layer_counts": list(map(len, levels)), "relaxations": attempts}


def descriptor(f: int, n: int) -> tuple:
    # Specification measurements only: output balance and each coordinate influence.
    changes = tuple(sum(((f >> x) ^ (f >> (x | (1 << i)))) & 1
                        for x in range(1 << n) if not (x & (1 << i))) for i in range(n))
    return (f.bit_count(),) + changes


def descriptor_audit(n: int, labels: list[int]) -> dict:
    groups = defaultdict(list)
    for f, label in enumerate(labels):
        groups[descriptor(f, n)].append((f, label))
    errors, ambiguous, witness = 0, 0, None
    max_labels = 1
    for z, rows in sorted(groups.items()):
        counts = Counter(label for _, label in rows)
        max_labels = max(max_labels, len(counts))
        errors += len(rows) - max(counts.values())
        if len(counts) > 1:
            ambiguous += 1
            if witness is None:
                a = rows[0]
                b = next(row for row in rows if row[1] != a[1])
                witness = {"descriptor": z, "function_a": a[0], "label_a": a[1], "function_b": b[0], "label_b": b[1]}
    return {"functions": len(labels), "descriptor_cells": len(groups), "ambiguous_cells": ambiguous,
            "unavoidable_point_prediction_errors_under_uniform_functions": errors,
            "minimum_additional_worst_case_label_bits": (max_labels - 1).bit_length(), "witness": witness,
            "scope": "Only this measured descriptor, not all GMI descriptors; labels are synthesis outcomes."}


def corrected_bounds() -> dict:
    lower_checks = upper_checks = failures = 0
    for a, b, threshold in itertools.product(range(7), range(7), range(13)):
        if a + b > threshold:
            for actual_a, actual_b in itertools.product(range(a, 7), range(b, 7)):
                lower_checks += 1
                failures += actual_a + actual_b <= threshold
        if a + b <= threshold:
            for actual_a, actual_b in itertools.product(range(a + 1), range(b + 1)):
                upper_checks += 1
                failures += actual_a + actual_b > threshold
    joint_cases = strict = joint_failures = 0
    for matrix_bits in range(1 << 9):
        rows = [[(matrix_bits >> (3 * i + j)) & 1 for j in range(3)] for i in range(3)]
        for budget in range(4):
            reachable = [[0, 0, 0]] + rows[:budget]
            pointwise = sum(max(row[j] for row in reachable) for j in range(3))
            joint = max(map(sum, reachable))
            joint_cases += 1
            strict += pointwise > joint
            joint_failures += joint > pointwise
    return {"loss_grid_denominator": 7, "uniform_lower_bound_checks": lower_checks,
            "constructive_upper_bound_checks": upper_checks, "bound_failures": failures,
            "new_success_matrices": 512, "budget_matrix_cases": joint_cases,
            "strict_pointwise_overstatements": strict, "joint_envelope_failures": joint_failures}


def cut_and_retention() -> dict:
    minimum_errors, exact_encoders, outcomes = 8, 0, 0
    for encoder in itertools.product((0, 1), repeat=4):
        for decoder in itertools.product((0, 1), repeat=4):
            errors = 0
            for record in range(4):
                for query in range(2):
                    errors += decoder[2 * encoder[record] + query] != ((record >> query) & 1)
                    outcomes += 1
            minimum_errors = min(minimum_errors, errors)
            exact_encoders += errors == 0
    histories, failures = 0, 0
    for length in range(6):
        for initial in (0, 1):
            for sequence in itertools.product(range(4), repeat=length):
                reference = state = initial
                for pair in sequence:
                    keep, new = pair & 1, pair >> 1
                    reference = reference if keep else new
                    state = new ^ (keep & (state ^ new))
                histories += 1
                failures += reference != state
    target = sum((((x >> 1) & 1) if x & 1 else ((x >> 2) & 1)) << x for x in range(8))
    affine_matches = 0
    for coeff in range(16):
        truth = sum((((coeff & 1) ^ (((coeff >> 1) & x).bit_count() & 1))) << x for x in range(8))
        affine_matches += truth == target
    return {"one_bit_record_encoders_times_decoders": 256, "scored_cut_outcomes": outcomes,
            "one_bit_exact_solutions": exact_encoders, "minimum_uniform_errors_out_of_8": minimum_errors,
            "query_before_cut_one_bit_construction": "send (record >> query) & 1",
            "two_bit_after_cut_construction": "retain record; read queried bit",
            "retention_histories": histories, "retention_failures": failures,
            "unconditional_affine_transition_candidates": 16, "affine_exact_matches": affine_matches}


def lifecycle() -> dict:
    checks = failures = 0
    for build_a, build_b, serve_a, serve_b, reuse in itertools.product(range(9), range(9), range(7), range(7), range(17)):
        actual = build_b + reuse * serve_b < build_a + reuse * serve_a
        delta = serve_a - serve_b
        if delta > 0:
            predicted = Fraction(reuse) > Fraction(build_b - build_a, delta)
        elif delta < 0:
            predicted = Fraction(reuse) < Fraction(build_b - build_a, delta)
        else:
            predicted = build_b < build_a
        checks += 1
        failures += actual != predicted
    return {"priced_build_serve_reuse_cases": checks, "failures": failures,
            "assumption": "Known complete build and serving costs; not a hardware or learned-cost estimator."}


def hostile_checks(certificate: dict) -> dict:
    mutations = []
    for label in ("low_cost", "high_cost", "wrong_semantics", "missing_state", "macro", "zero_price", "negative_price", "noninteger_price"):
        c = json.loads(json.dumps(certificate))
        if label in ("low_cost", "high_cost"):
            c["costs"][202] += -1 if label == "low_cost" else 1
        elif label == "wrong_semantics":
            c["expressions"][202] = ["c", 0]
        elif label == "missing_state":
            c["costs"].pop()
        elif label == "macro":
            c["prices"]["attention"] = 1
        else:
            c["prices"]["and"] = {"zero_price": 0, "negative_price": -1, "noninteger_price": 0.5}[label]
        try:
            certify(c)
            mutations.append({"mutation": label, "rejected": False})
        except (ValueError, TypeError, IndexError):
            mutations.append({"mutation": label, "rejected": True})
    return {"controls": mutations, "all_rejected": all(x["rejected"] for x in mutations)}


def specification() -> dict:
    return {
        "base_head": BASE, "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "status": "FROZEN_BEFORE_SUCCESSOR_AND_SYNTHESIS_RUN",
        "neutral_input": "Truth-table semantics, arity, and primitive prices only. No architecture names or templates.",
        "formula_scope": "Finite Boolean expression trees; free preloaded input wires/constants. All reads, persistent storage and output transfers are outside this isolated operator meter and must be priced for lifecycle claims.",
        "primary_prediction": "For select(s,a,b)=b XOR (s AND (a XOR b)), min formula cost is min(2+2*k,8), when NOT=AND=OR=2 and XOR=k, k=1..8. Conjectural lower bound before certification; preserve any miss.",
        "negative_twins": "Always keep/always overwrite need zero internal operators; no claim of zero full lifecycle cost.",
        "descriptor_hypothesis": "Output balance plus coordinate influence counts might determine min cost (arity 3) or cost<=4 (arity 4). Attack; a collision falsifies ONLY this candidate descriptor sufficiency claim.",
        "successor_bounds": "Replace upper_A in pure-A no-go premise with a uniform lower_A. Use a single reachable developed state for simultaneous breadth; pointwise envelopes remain outer bounds.",
        "enumerations": {"arity3_price_cells": 8, "additional_bases": ["nand", "nor"], "arity4_operator_cap": 4, "successor_loss_denominator": 7, "joint_success_matrices": [3, 3], "retention_max_horizon": 5},
        "parents": "Ordinary minimum-cost Boolean formula synthesis, lookup tables, nonlinear recurrence, indexed selection. No distinct GMI performance advantage predicted over an identical cost-complete parent.",
        "kill_conditions": ["any incorrect witness", "any Bellman violation", "any frozen crossover miss", "any accepted hostile control", "any uncharged architecture macro", "any joint-bound violation"],
        "protected_status": "Exact exhaustive microscopes. Public remote hash freeze, but no independent blind author/evaluator and no real-workload or held-family validation.",
        "scope_terminals": {"NO_KNOWN_UNTYPED_OR_UNTESTED_BLOCKING_GAP_AT_REGISTERED_SCOPE": False, "KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE": False},
    }


def run() -> None:
    frozen = json.loads(FREEZE.read_text())
    if frozen != specification():
        raise ValueError("Freeze/source mismatch: create a new version; do not overwrite")
    start = time.perf_counter()
    certificates, summaries, predictions = [], [], []
    target = sum((((x >> 1) & 1) if x & 1 else ((x >> 2) & 1)) << x for x in range(8))
    for k in range(1, 9):
        c = synthesize(3, {"not": 2, "and": 2, "or": 2, "xor": k})
        checks = certify(c)
        certificates.append(c)
        summaries.append({"basis": c["prices"], "functions": 256, "relaxations": c["relaxations"], **checks})
        predictions.append({"xor_price": k, "predicted": min(2 + 2 * k, 8), "observed": c["costs"][target], "expression": c["expressions"][target]})
    for op in ("nand", "nor"):
        c = synthesize(3, {op: 1})
        checks = certify(c)
        certificates.append(c)
        summaries.append({"basis": c["prices"], "functions": 256, "relaxations": c["relaxations"], "selector_cost": c["costs"][target], **checks})
    bounded4 = bounded(4, 4)
    bounded_rows = 0
    for f, (cost, expr) in bounded4["best"].items():
        for row in range(16):
            value, witness_cost = scalar(expr, row, {"not": 1, "and": 1, "or": 1, "xor": 1}, 4)
            if value != ((f >> row) & 1) or witness_cost != cost:
                raise ValueError("Arity-four bounded witness mismatch")
            bounded_rows += 1
    labels4 = [int(f in bounded4["best"]) for f in range(1 << 16)]
    base = certificates[1]
    audits = {"arity3_exact_cost": descriptor_audit(3, base["costs"]), "arity4_cost_at_most_four": descriptor_audit(4, labels4)}
    for audit in audits.values():
        witness = audit["witness"]
        if witness and audit["functions"] == 65536:
            for key in ("a", "b"):
                f = witness["function_" + key]
                witness["formula_" + key] = bounded4["best"].get(f)
    report = {
        "base_head": BASE, "freeze_sha256": hashlib.sha256(FREEZE.read_bytes()).hexdigest(),
        "source_sha256": frozen["source_sha256"], "receipt_type": "EXACT_FINITE_NOT_GLOBAL_OR_EMPIRICAL_CLOSURE",
        "corrected_developmental_bounds": corrected_bounds(), "causal_cut_and_retention": cut_and_retention(),
        "neutral_synthesis": summaries, "frozen_selector_predictions": predictions,
        "selector_prediction_misses": sum(x["predicted"] != x["observed"] for x in predictions),
        "negative_twins_internal_operator_costs": {"always_keep": base["costs"][204], "always_overwrite": base["costs"][240]},
        "descriptor_tests": audits, "arity4_bounded_search": {"layer_counts": bounded4["layer_counts"], "relaxations": bounded4["relaxations"], "independent_witness_rows": bounded_rows},
        "lifecycle": lifecycle(), "hostile_checker_controls": hostile_checks(base),
        "certificate_digest": digest(certificates), "domain_status": "REDUCED_TO_ORDINARY_BOOLEAN_PROGRAMS_AT_H4; no new domain",
        "held_family_prediction": "NOT_EXECUTED", "real_regime_transfer": "NOT_EXECUTED", "GMI_specific_excess_over_identical_parent": 0,
        "scope_terminals": frozen["scope_terminals"],
    }
    report["corrected_finite_checks_green"] = (
        report["corrected_developmental_bounds"]["bound_failures"] == 0
        and report["corrected_developmental_bounds"]["joint_envelope_failures"] == 0
        and report["causal_cut_and_retention"]["retention_failures"] == 0
        and report["causal_cut_and_retention"]["one_bit_exact_solutions"] == 0
        and report["causal_cut_and_retention"]["minimum_uniform_errors_out_of_8"] == 2
        and report["causal_cut_and_retention"]["affine_exact_matches"] == 0
        and all(v == 0 for v in report["negative_twins_internal_operator_costs"].values())
        and report["selector_prediction_misses"] == 0 and report["lifecycle"]["failures"] == 0
        and report["hostile_checker_controls"]["all_rejected"])
    report["descriptor_hypothesis_status"] = "FALSIFIED" if any(a["ambiguous_cells"] for a in audits.values()) else "NOT_FALSIFIED_AT_FINITE_SCOPE_ONLY"
    put(ROOT / "GMI_PRIMITIVE_CLOSURE_CERTIFICATES_V1.json", certificates)
    put(ROOT / "GMI_PRIMITIVE_CLOSURE_RECEIPT_V1.json", report)
    put(ROOT / "GMI_PRIMITIVE_CLOSURE_RUNTIME_V1.json", {"python": platform.python_version(), "platform": platform.platform(), "wall_seconds": time.perf_counter() - start, "scientific_receipt_digest": digest(report)})
    print(json.dumps(report, sort_keys=True, indent=2))
    if not report["corrected_finite_checks_green"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("--freeze", "--run"))
    # Positional action is read explicitly so invocation remains unambiguous.
    import sys
    if sys.argv[1:] == ["--freeze"]:
        put(FREEZE, specification())
        print(FREEZE.read_text())
    elif sys.argv[1:] == ["--run"]:
        run()
    else:
        parser.print_help()
        raise SystemExit(2)
