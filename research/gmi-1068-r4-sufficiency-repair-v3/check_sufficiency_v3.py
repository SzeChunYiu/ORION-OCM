#!/usr/bin/env python3
"""Exact finite re-evaluation of two independent notions of sufficiency."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_sibling(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate = load_sibling("sufficiency_v3")
oracle = load_sibling("independent_oracle_v3")


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def clean(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def verdict(result):
    return result["parameter_sufficient"], result["predictive_sufficient"]


def compare(joint, statistic):
    first, second = candidate.analyze(joint, statistic), oracle.evaluate(joint, statistic)
    require(verdict(first) == verdict(second), "conditional/cross-product disagreement")
    return first, second


def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def evaluate():
    rules = {
        "A": ("independent", "copy"),
        "B": ("theta", "constant"),
        "A_future_made_constant": ("independent", "constant"),
        "A_observation_made_parameter_dependent": ("theta", "copy"),
        "B_observation_made_independent": ("independent", "constant"),
        "B_future_made_observation_dependent": ("theta", "copy"),
    }
    expected = {"A": (True, False), "B": (False, True),
                "A_future_made_constant": (True, True),
                "A_observation_made_parameter_dependent": (False, False),
                "B_observation_made_independent": (True, True),
                "B_future_made_observation_dependent": (False, False)}
    records, mechanism_checks = {}, 0
    for name, (x_rule, y_rule) in rules.items():
        for prior in (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)):
            joint = candidate.model(x_rule, y_rule, prior)
            actual, independent = compare(joint, (0, 0))
            require(verdict(actual) == expected[name], "mechanism intervention: " + name)
            require(verdict(compare(joint, (0, 1))[0]) == (True, True), "identity statistic")
            mechanism_checks += 1
            if prior == Fraction(1, 2):
                records[name] = {"joint_theta_X_Y": [[*atom, p] for atom, p in sorted(joint.items())],
                                 "statistic": [0, 0], "conditional_analysis": actual,
                                 "independent_analysis": independent}
    # The actual joint laws must change under the registered interventions.
    require(candidate.model(*rules["A"]) != candidate.model(*rules["A_future_made_constant"]), "fake intervention A")
    require(candidate.model(*rules["B"]) != candidate.model(*rules["B_future_made_observation_dependent"]), "fake intervention B")

    relabel_checks = 0
    for name, mechanisms in rules.items():
        joint = candidate.model(*mechanisms)
        for ft, fx, fy, fs in itertools.product((0, 1), repeat=4):
            transported = {(t ^ ft, x ^ fx, y ^ fy): p for (t, x, y), p in joint.items()}
            statistic = (fs, fs)  # transported constant statistic, including S relabel
            require(verdict(compare(transported, statistic)[0]) == expected[name], "label dependence")
            relabel_checks += 1

    table_counts, verdict_counts, evidence_hash = {}, {}, hashlib.sha256()
    statistics = tuple(itertools.product((0, 1), repeat=2))
    for denominator in (4, 6):
        supported = 0
        for counts in compositions(denominator, 8):
            if sum(counts[:4]) == 0 or sum(counts[4:]) == 0:
                continue
            joint = {atom: Fraction(n, denominator) for atom, n in zip(candidate.CELLS, counts)}
            supported += 1
            for statistic in statistics:
                actual, _ = compare(joint, statistic)
                label = ",".join(str(int(v)) for v in verdict(actual))
                verdict_counts[label] = verdict_counts.get(label, 0) + 1
                evidence_hash.update(json.dumps([denominator, counts, statistic, verdict(actual)]).encode())
        combinatorial = math.comb(denominator + 7, 7) - 2 * math.comb(denominator + 3, 3)
        require(supported == combinatorial, "joint-table enumeration count")
        table_counts[str(denominator)] = supported
    require(sum(table_counts.values()) == 1808 and sum(verdict_counts.values()) == 7232, "frozen enumeration count")

    # Both theta values remain supported, but X=1 and S=1 never occur.
    zero_x = {(t, x, y): Fraction(1, 2) if x == 0 and y == 0 else Fraction()
              for t, x, y in candidate.CELLS}
    zero_actual, _ = compare(zero_x, (0, 1))
    require(verdict(zero_actual) == (True, True), "unsupported-X event is not evidence of failure")
    require(zero_actual["zero_predictive_conditioning_events"] == [1], "zero event not exposed")

    rejected = []
    reference_laws = [candidate.model(*rules[key]) for key in ("A", "B")]
    fixed_mutants = {"hardcoded_A_verdict": (True, False), "hardcoded_B_verdict": (False, True),
                     "always_sufficient": (True, True), "never_sufficient": (False, False)}
    for name, fixed in fixed_mutants.items():
        require(any(fixed != verdict(oracle.evaluate(law, (0, 0))) for law in reference_laws), name + " escaped")
        rejected.append(name)
    require(any((verdict(oracle.evaluate(law, (0, 0)))[0],) * 2 != verdict(oracle.evaluate(law, (0, 0)))
                for law in reference_laws), "parameter/predictive conflation escaped")
    rejected.append("copy_parameter_verdict_to_predictive")
    invalid = {}
    invalid["theta_zero_prior"] = candidate.model("independent", "copy", Fraction(0))
    invalid["unnormalized_joint"] = {atom: 2 * p for atom, p in reference_laws[0].items()}
    negative = reference_laws[0].copy()
    negative[(0, 0, 0)] -= Fraction(1, 2)
    negative[(0, 1, 0)] += Fraction(1, 2)
    invalid["negative_probability"] = negative
    floating = reference_laws[0].copy()
    floating[(0, 0, 0)] = float(floating[(0, 0, 0)])
    invalid["inexact_probability"] = floating
    for name, bad in invalid.items():
        try:
            candidate.analyze(bad, (0, 0))
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError(name + " escaped")

    parents = json.loads((ROOT / "PARENT_SCOPE_V3.json").read_text())
    require(parents["round_status"] == "OPEN_SEMANTIC_INTEGRATION", "round closure overclaim")
    for relative, expected_hash in parents["historical_input_sha256"].items():
        require(hashlib.sha256((ROOT.parent / relative).read_bytes()).hexdigest() == expected_hash,
                "historical file changed: " + relative)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.iterdir())
              if p.is_file() and p.name != "RESULT_V3.json"}
    return clean({"schema": "GMI_R4_EXACT_SUFFICIENCY_REPAIR_V3",
        "check_status": "PASS_EXACT_REGISTERED_CONDITIONAL_LAW_CHECKS",
        "round_status": "OPEN_SEMANTIC_INTEGRATION", "formal_status": "PAPER_PROOF_NOT_LEAN_VERIFIED",
        "countermodels_and_interventions": records,
        "mechanism_checks_with_nonuniform_priors": mechanism_checks,
        "relabel_checks": relabel_checks, "joint_table_occurrences_by_denominator": table_counts,
        "binary_statistic_comparisons": sum(verdict_counts.values()), "verdict_counts": verdict_counts,
        "exhaustive_evidence_sha256": evidence_hash.hexdigest(), "zero_X_support_case": zero_actual,
        "negative_controls_rejected": rejected, "input_sha256": hashes,
        "historical_input_sha256": parents["historical_input_sha256"],
        "forbidden_promotions": ["R4_COMPLETE", "R0_R17_COMPLETE", "ALL_TESTS_COMPLETE",
            "PARAMETER_SUFFICIENCY_EQUALS_PREDICTIVE_SUFFICIENCY", "UNIVERSAL_PREDICTIVE_MINIMALITY",
            "FINITE_STATISTICAL_TEST_PROVES_ALL_MODEL_DISTRIBUTIONS"]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = evaluate()
    output = ROOT / "RESULT_V3.json"
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(output.read_text()) == result, "stale or altered receipt")
    print(json.dumps({key: result[key] for key in ("check_status", "round_status", "binary_statistic_comparisons",
          "mechanism_checks_with_nonuniform_priors", "relabel_checks", "negative_controls_rejected")}, sort_keys=True))


if __name__ == "__main__":
    main()
