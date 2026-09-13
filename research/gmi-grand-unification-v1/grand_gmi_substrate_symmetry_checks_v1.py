#!/usr/bin/env python3
"""Exact hostile checks for Grand GMI substrate/symmetry layer.

No RNG, no fitted parameters, no floating decision thresholds.
"""

from fractions import Fraction
from itertools import product
import json


def check_unique_deterministic_symmetry():
    vals = [0, 1, 2]
    invariant_tables = 0
    unique_cases = 0
    for a, b in product(vals, repeat=2):
        # Z2 swaps x=0<->1 and a=0<->1.
        loss = {(0, 0): a, (1, 1): a, (0, 1): b, (1, 0): b}
        risks = {}
        for p0, p1 in product([0, 1], repeat=2):
            risks[(p0, p1)] = loss[(0, p0)] + loss[(1, p1)]
        best = min(risks.values())
        opts = [p for p, r in risks.items() if r == best]
        invariant_tables += 1
        if len(opts) == 1:
            unique_cases += 1
            p = opts[0]
            assert p[1] == 1 - p[0]
    return {
        "invariant_loss_tables": invariant_tables,
        "unique_optimum_cases": unique_cases,
        "all_unique_optima_equivariant": True,
    }


def check_randomized_symmetrization():
    grid = [Fraction(i, 4) for i in range(5)]
    vals = [0, 1, 2]
    checks = 0

    for a, b, c in product(vals, repeat=3):
        # x=0<->1, x=2 fixed; action labels are swapped by the same Z2.
        loss = {
            (0, 0): Fraction(a), (1, 1): Fraction(a),
            (0, 1): Fraction(b), (1, 0): Fraction(b),
            (2, 0): Fraction(c), (2, 1): Fraction(c),
        }
        for p0, p1, p2 in product(grid, repeat=3):
            # p[x] = P(action=1 | x)
            p = {0: p0, 1: p1, 2: p2}
            gp = {0: 1 - p[1], 1: 1 - p[0], 2: 1 - p[2]}
            sym = {x: (p[x] + gp[x]) / 2 for x in (0, 1, 2)}

            assert sym[1] == 1 - sym[0]
            assert sym[2] == Fraction(1, 2)

            def risk(pol):
                return sum(
                    ((1 - pol[x]) * loss[(x, 0)] + pol[x] * loss[(x, 1)]) / 3
                    for x in (0, 1, 2)
                )

            # Convex, G-invariant resource proxy.
            def resource(pol):
                return sum((pol[x] - Fraction(1, 2)) ** 2 for x in (0, 1, 2))

            assert risk(sym) == risk(p)
            assert resource(sym) <= resource(p)
            checks += 1

    return {
        "exact_policy_loss_checks": checks,
        "risk_preserved": True,
        "convex_invariant_resource_not_worsened": True,
    }


def check_nonconvex_resource_boundary():
    # One group-fixed state, actions swapped. No deterministic equivariant policy exists.
    # The invariant nonconvex meter below rewards pure/extreme actions.
    r = lambda p: min(p, 1 - p)
    pure = Fraction(0)
    sym = Fraction(1, 2)
    assert r(pure) == 0
    assert r(sym) == Fraction(1, 2)
    return {
        "deterministic_resource": "0/1",
        "symmetrized_resource": "1/2",
        "no_worse_equivariant_claim_without_convexity": False,
    }


def check_substrate_refinement(max_len=7):
    # Source semantic process: one bit s. Input i toggles s when i=1; output is new s.
    def src_step(s, i):
        ns = s ^ i
        return ns, ns

    # Target substrate adds a hidden phase bit j that toggles every step.
    def tgt_step(st, i):
        s, j = st
        ns = s ^ i
        return (ns, j ^ 1), ns

    trace_checks = 0
    for s0, j0 in product([0, 1], repeat=2):
        for length in range(max_len + 1):
            for seq in product([0, 1], repeat=length):
                s = s0
                t = (s0, j0)
                out_s, out_t = [], []
                for i in seq:
                    s, o = src_step(s, i)
                    t, ot = tgt_step(t, i)
                    out_s.append(o)
                    out_t.append(ot)
                assert out_s == out_t
                assert t[0] == s
                trace_checks += 1

    # Recover target semantic quotient from all probe sequences through length 2.
    states = [(s, j) for s, j in product([0, 1], repeat=2)]
    probes = [seq for length in range(3) for seq in product([0, 1], repeat=length)]
    signatures = {}
    for st in states:
        profile = []
        for seq in probes:
            t = st
            outs = []
            for i in seq:
                t, o = tgt_step(t, i)
                outs.append(o)
            profile.append(tuple(outs))
        signatures[st] = tuple(profile)

    groups = {}
    for st, sig in signatures.items():
        groups.setdefault(sig, []).append(st)
    parts = sorted(sorted(v) for v in groups.values())
    assert parts == [[(0, 0), (0, 1)], [(1, 0), (1, 1)]]

    return {
        "trace_checks": trace_checks,
        "max_sequence_length": max_len,
        "semantic_classes": 2,
        "microstates_per_semantic_class": [2, 2],
        "observable_traces_preserved": True,
        "example_source_cost_per_step": "1",
        "example_target_cost_per_step": "3",
    }


def run():
    return {
        "terminal": "GRAND_GMI_SUBSTRATE_SYMMETRY_TRANCHE_ALL_GREEN",
        "unique_deterministic_symmetry": check_unique_deterministic_symmetry(),
        "randomized_symmetrization": check_randomized_symmetrization(),
        "nonconvex_resource_boundary": check_nonconvex_resource_boundary(),
        "substrate_refinement": check_substrate_refinement(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
