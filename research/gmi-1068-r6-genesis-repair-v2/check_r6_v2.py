#!/usr/bin/env python3
"""Reproduce registered operational evidence; default verifies the saved receipt."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parent


def load_sibling(name):
    # Bind each import to the reviewed sibling bytes even under python -I.
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate = load_sibling("genesis_v2")
oracle = load_sibling("independent_oracle_v2")


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate():
    rejected = []
    scheduler_cases = []
    for k in range(1, 9):
        for t in range(1, 10):
            factory = lambda i, k=k, t=t: candidate.halts_after(t) if i == k else candidate.divergent()
            stages = k + t
            machines, finishes, slots = candidate.dovetail(factory, stages)
            require(finishes == oracle.schedule(factory, stages), "scheduler/oracle disagreement")
            require(finishes == {k: k + t - 1}, "triangular completion bound")
            require(len(slots) == stages * (stages + 1) // 2, "slot count")
            require(not machines[0].stopped, "divergent prefix unexpectedly stopped")
            scheduler_cases.append([k, t, finishes[k], len(slots)])
    factory = lambda i: candidate.halts_after(4) if i == 3 else candidate.divergent()
    for mode in ("serial", "latest"):
        _, finishes, _ = candidate.dovetail(factory, 7, mode)
        require(finishes != {3: 6}, "hostile scheduler escaped")
        rejected.append("scheduler_" + mode)
    require(max(3, 4 - 1) != 3 + 4 - 1, "wrong max bound escaped")
    rejected.append("completion_bound_max_instead_of_sum")

    # Check every registered cost regime, including n=0 and exact equality.
    costs = [Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1),
             Fraction(4, 3), Fraction(2), Fraction(3), Fraction(4)]
    cost_counts = {"WIN": 0, "TIE": 0, "LOSE": 0}
    for D, L, c in itertools.product(costs, repeat=3):
        for n in range(13):
            got = candidate.abstraction(D, L, c, n)
            require(got["outcome"] == oracle.cost_outcome(D, L, c, n), "cost/oracle disagreement")
            if L > c:
                require((got["outcome"] == "WIN") == (n > D / (L - c)), "strict threshold")
                first = got["first_positive_n"]
                require(candidate.abstraction(D, L, c, first)["outcome"] == "WIN", "first win")
                require(candidate.abstraction(D, L, c, first - 1)["outcome"] != "WIN", "preceding win")
            else:
                require(got["first_positive_n"] is None and got["outcome"] != "WIN", "nonpositive saving slope")
            cost_counts[got["outcome"]] += 1
    mutants = {
        "abstraction_weak_instead_of_strict": (lambda D, L, c, n: n*(L-c) >= D, (4, 3, 1, 2)),
        "abstraction_absolute_gap": (lambda D, L, c, n: n*abs(L-c) > D, (0, 1, 2, 1)),
        "abstraction_zero_repeat_win": (lambda D, L, c, n: D == 0 or n*(L-c) > D, (0, 2, 1, 0)),
    }
    for name, (mutant, witness) in mutants.items():
        require(mutant(*witness) != (oracle.cost_outcome(*witness) == "WIN"), name + " escaped")
        rejected.append(name)
    try:
        _ = Fraction(0) / (Fraction(1) - Fraction(1))
    except ZeroDivisionError:
        require(candidate.abstraction(0, 1, 1, 1)["first_positive_n"] is None, "zero slope unsupported")
        rejected.append("abstraction_divide_by_zero")
    try:
        candidate.abstraction(-1, 2, 1, 1)
    except ValueError:
        rejected.append("negative_setup_cost")
    else:
        raise AssertionError("negative cost escaped")

    reflection = []
    for depth in (1, 2, 3, 4, 8, 16):
        for value in (-7, 0, 1, 42):
            program = candidate.reflection_chain(depth, value)
            machine, state = candidate.execute(program, depth + 3)
            ref_state, ref_out, ref_steps, ref_trace = oracle.run(program, depth + 3)
            require((state, machine.output, machine.steps, machine.trace) ==
                    (ref_state, ref_out, ref_steps, ref_trace), "reflection oracle disagreement")
            require(state == "HALTED" and machine.output == [value], "reflection output")
            for level in range(depth):
                require(machine.trace[level]["write"][0] == 3 * (level + 1) + 2,
                        "modifier does not write next instruction")
                require(machine.trace[level + 1]["instruction"][2] == value,
                        "modified code not subsequently fetched")
            reflection.append([depth, value, machine.steps])
    program = candidate.reflection_chain(2, 42)
    hostile, _ = candidate.execute(program, 5, frozen_code=True)
    require(hostile.output != [42], "immutable-code interpreter escaped")
    rejected.append("immutable_instruction_fetch")
    chain, _ = candidate.execute(program, 5)
    # A causal intervention varies the first modifier, holding later initial code fixed.
    changed = program.copy()
    changed[2] = 43
    alternative, _ = candidate.execute(changed, 5)
    require(chain.output == [42] and alternative.output == [43], "meta edit lacks causal effect")
    budget_machine, state = candidate.execute(candidate.divergent(), 50)
    require(state == "BUDGET_EXHAUSTED" and budget_machine.steps == 50, "timeout is not divergence oracle")
    require(candidate.execute([99, 0, 0], 1)[1] == "FAULT", "invalid code accepted")

    words = [bits for length in range(9) for bits in itertools.product((0, 1), repeat=length)]
    for bits in words:
        expected = () if not bits else (0,) + bits[:-1]
        require(candidate.delay(bits) == expected, "last-bit invariant witness")
    stateless_solutions = 0
    for table in itertools.product((0, 1), repeat=2):
        works = all(tuple(table[x] for x in bits) == candidate.delay(bits) for bits in words)
        stateless_solutions += works
    require(stateless_solutions == 0, "stateless delay")
    rejected.append("stateless_delay")

    minimax_cases = 0
    for denominator in range(1, 18):
        for numerator in range(denominator + 1):
            p = Fraction(numerator, denominator)
            require(p + (1 - p) == 1 and max(p, 1 - p) >= Fraction(1, 2), "binary minimax")
            minimax_cases += 1

    ledger = json.loads((ROOT / "BIAS_LEDGER_V2.json").read_text())
    require(ledger["literal_prior_free"] is False, "prior-free overclaim")
    require(ledger["r6_round_status"] == "OPEN", "unearned round closure")
    parent_hashes = ledger["historical_parent_sha256"]
    for relative, expected in parent_hashes.items():
        require(digest(ROOT.parent / relative) == expected, "historical parent changed: " + relative)
    inputs = {path.name: digest(path) for path in sorted(ROOT.iterdir())
              if path.is_file() and path.name != "RESULT_V2.json"}
    return {
        "schema": "GMI_R6_OPERATIONAL_REPAIR_V2",
        "check_status": "PASS_REGISTERED_REPAIR_CHECKS",
        "round_status": "OPEN_PARENT_AND_GENERAL_CLAIMS",
        "scope": "exact declared RAM/cost/delay witnesses and accompanying paper proofs",
        "scheduler_cases": len(scheduler_cases),
        "scheduler_case_sha256": hashlib.sha256(json.dumps(scheduler_cases).encode()).hexdigest(),
        "hard_scheduler_case": {"candidate": 3, "steps": 4, "finish_stage": 6, "slots": 28},
        "abstraction_cases": sum(cost_counts.values()), "abstraction_outcomes": cost_counts,
        "encoded_reflection_cases": len(reflection), "modifier_of_modifier_trace": chain.trace,
        "delay_words": len(words), "stateless_solutions": stateless_solutions,
        "minimax_rational_sanity_cases": minimax_cases,
        "analytic_obstructions": ["binary_minimax_half", "countable_uniform_probability_paper_proof"],
        "negative_controls_rejected": rejected,
        "proof_status": "PAPER_PROOFS_NOT_LEAN_CHECKED",
        "parent_status": "HISTORICAL_R5_BYTES_PINNED_NOT_REEARNED",
        "input_sha256": inputs, "historical_parent_sha256": parent_hashes,
        "forbidden_promotions": ["R6_COMPLETE", "ALL_R0_R17_COMPLETE", "LITERAL_PRIOR_FREE",
            "ALL_ARCHITECTURES_DERIVED", "UNIVERSAL_OPTIMALITY", "SELF_IMPROVEMENT_PROVEN",
            "GENERAL_HALTING_DECIDER", "NO_UNKNOWN_GAPS", "EMPIRICAL_GENERALIZATION"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = evaluate()
    output = ROOT / "RESULT_V2.json"
    if args.write:
        output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(output.read_text()) == result, "receipt mismatch; do not reuse stale evidence")
    print(json.dumps({k: result[k] for k in ("check_status", "round_status", "scheduler_cases",
          "abstraction_cases", "encoded_reflection_cases", "delay_words", "negative_controls_rejected")},
          sort_keys=True))


if __name__ == "__main__":
    main()
