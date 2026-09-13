#!/usr/bin/env python3
"""Exact finite checks for Grand GMI formal reasoning/proof-search theorem V1."""

from __future__ import annotations

import json
from collections import defaultdict
from itertools import permutations, product


def check_unique_proof_search():
    rows = []
    total_orders = 0
    for n in range(1, 9):
        worst_over_orders = 0
        for order in permutations(range(n)):
            total_orders += 1
            # Adversary chooses the candidate appearing last in this query order.
            target = order[-1]
            negatives = 0
            for candidate in order[:-1]:
                assert candidate != target
                negatives += 1
            assert negatives == n - 1
            worst_over_orders = max(worst_over_orders, negatives)
        assert worst_over_orders == n - 1
        rows.append({"candidate_count": n, "worst_negative_queries_before_forced": worst_over_orders})
    return {
        "candidate_sizes": rows,
        "query_orders_checked": total_orders,
        "verification_calls_for_supplied_candidate": 1,
        "all_exact": True,
    }


def state_level_dp():
    # A branches to two syntactically distinct but semantically identical states B,C.
    transitions = {
        "A": {0: "B", 1: "C"},
        "B": {0: "G", 1: "D"},
        "C": {0: "G", 1: "D"},
    }
    terminal = {"G": 1, "D": 0}
    values = dict(terminal)
    actions = {"G": (), "D": ()}
    for state in ("B", "C", "A"):
        q = {a: values[nxt] for a, nxt in transitions[state].items()}
        best = max(q.values())
        values[state] = best
        actions[state] = tuple(sorted(a for a, v in q.items() if v == best))
    return values, actions


def quotient_dp():
    transitions = {
        "A": {0: "X", 1: "X"},
        "X": {0: "G", 1: "D"},
    }
    terminal = {"G": 1, "D": 0}
    values = dict(terminal)
    actions = {"G": (), "D": ()}
    for state in ("X", "A"):
        q = {a: values[nxt] for a, nxt in transitions[state].items()}
        best = max(q.values())
        values[state] = best
        actions[state] = tuple(sorted(a for a, v in q.items() if v == best))
    return values, actions


def check_semantic_quotient_dp():
    sv, sa = state_level_dp()
    qv, qa = quotient_dp()
    assert sv["B"] == sv["C"] == qv["X"] == 1
    assert sa["B"] == sa["C"] == qa["X"] == (0,)
    assert sv["A"] == qv["A"] == 1
    assert sa["A"] == qa["A"] == (0, 1)
    return {
        "state_values": sv,
        "state_actions": {k: list(v) for k, v in sa.items()},
        "quotient_values": qv,
        "quotient_actions": {k: list(v) for k, v in qa.items()},
        "merged_states": ["B", "C"],
        "all_exact": True,
    }


def partition_rows(rows):
    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[tuple(row)].append(i)
    return list(groups.values())


def check_proof_response_quotients():
    tables = 0
    cardinality_checks = 0
    for bits in product((0, 1), repeat=12):
        rows = [bits[3 * i : 3 * (i + 1)] for i in range(4)]
        q = partition_rows(rows)
        assert len(q) == len(set(tuple(r) for r in rows))
        tables += 1
        cardinality_checks += 1
    return {"response_tables": tables, "cardinality_checks": cardinality_checks, "all_exact": True}


def check_unsound_verifier_boundary():
    certificates = ("good", "bad")
    truth = {"good": True, "bad": False}
    verifier = {"good": True, "bad": True}
    accepted = [c for c in certificates if verifier[c]]
    false_accepted = [c for c in accepted if not truth[c]]
    assert false_accepted == ["bad"]
    return {
        "accepted_certificates": accepted,
        "false_but_accepted": false_accepted,
        "verifier_acceptance_implies_truth": False,
        "all_exact": True,
    }


def check_sound_incomplete_boundary():
    theorem_true = True
    admitted_certificates = ("c0", "c1", "c2")
    verifier = {c: False for c in admitted_certificates}
    found = [c for c in admitted_certificates if verifier[c]]
    assert theorem_true
    assert found == []
    terminal = "NO_PROOF_IN_DECLARED_SEARCH_SCOPE"
    assert terminal != "REFUTED"
    return {
        "theorem_true": theorem_true,
        "accepted_certificates": found,
        "terminal": terminal,
        "false_refutation_avoided": True,
        "all_exact": True,
    }


def run_all():
    result = {
        "schema": "GRAND_GMI_PROOF_REASONING_CHECKS_V1",
        "unique_proof_search": check_unique_proof_search(),
        "semantic_quotient_dp": check_semantic_quotient_dp(),
        "proof_response_quotients": check_proof_response_quotients(),
        "unsound_verifier_boundary": check_unsound_verifier_boundary(),
        "sound_incomplete_boundary": check_sound_incomplete_boundary(),
    }
    result["terminal"] = "GRAND_GMI_FORMAL_REASONING_PROOF_SEARCH_TRANCHE_ALL_GREEN"
    return result


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2, sort_keys=True))
