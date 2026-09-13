"""Counterexamples and no-alarm controls for the stated terminal interface."""
from fractions import Fraction

from terminal_kernel_v1 import reconstruct, terminal_kernel, require
from syntax_parent_v1 import execute, frontier, profiles


def compare(n, rows, terminal, queries):
    full, counts = reconstruct(n, rows, terminal, queries, False)
    minimal, _ = reconstruct(n, rows, terminal, queries, True)
    independent, candidates, accepted = profiles(n, rows, terminal, queries)
    require(set(full) == independent, "all-profile syntax mismatch")
    require(set(minimal) == frontier(independent), "frontier syntax mismatch")
    for v, tree in minimal.items():
        actual = []
        for x in range(2**n):
            a, cost = execute(tree, x, terminal, queries)
            require(a in rows[x], "constructed output inadequate")
            actual.extend(cost)
        require(tuple(actual) == v, "constructed resource mismatch")
    return {"full": set(full), "frontier": set(minimal), "counts": counts,
            "candidate_trees": candidates, "adequate_trees": accepted}


def controls():
    cases = {}
    r, s = ((0, 1, 2), (0, 3)), ((0, 1, 2), (1, 3))
    terminal = (((0,), (3,), (0,), (0,)),) * 2
    kr, ks = [terminal_kernel(1, row, terminal, ((1,),)) for row in (r, s)]
    require({p: bool(v) for p, v in kr.items()} == {p: bool(v) for p, v in ks.items()},
            "Boolean counterexample not matched")
    require(kr[(-1,)] != ks[(-1,)], "terminal invariant misses changed root")
    cases["boolean_parent_r"] = compare(1, r, terminal, ((1,),))
    cases["boolean_parent_s"] = compare(1, s, terminal, ((1,),))
    require(cases["boolean_parent_r"]["frontier"] == {(0, 0)}, "R result")
    require(cases["boolean_parent_s"]["frontier"] == {(1, 1)}, "S result")
    require((3, 3) in cases["boolean_parent_s"]["full"], "feasible early stop lost")
    cases["joint_terminal_tradeoff"] = compare(0, ((0, 1),), (((0, 2), (2, 0)),), ())
    require(cases["joint_terminal_tradeoff"]["frontier"] == {(0, 2), (2, 0)}, "joint tradeoff")
    costs = (((0,), (2,)), ((2,), (0,)))
    cases["hidden_terminal_cost"] = compare(1, ((0, 1),) * 2, costs, ((1,),))
    require(cases["hidden_terminal_cost"]["frontier"] == {(0, 2), (2, 0), (1, 1)},
            "input-conditioned free-action oracle leaked")
    rows = ((0,), (1,))
    zero = (((0,), (0,)),) * 2
    cases["zero_mass_obligation"] = compare(1, rows, zero, ((1,),))
    require(cases["zero_mass_obligation"]["frontier"] == {(1, 1)}, "zero mass dropped obligation")
    cases["free_query"] = compare(1, rows, zero, ((0,),))
    require(cases["free_query"]["frontier"] == {(0, 0)}, "zero query cost excluded")
    cases["empty_row"] = compare(1, ((), (1,)), zero, ((0,),))
    require(not cases["empty_row"]["frontier"], "inadequate input admitted")
    cases["rational_costs"] = compare(1, rows, zero, ((Fraction(1, 3),),))
    require(cases["rational_costs"]["frontier"] == {(Fraction(1, 3),) * 2}, "fraction lost")
    dominated = (((0,), (1,)),) * 2
    cases["dominated_terminal"] = compare(1, ((0, 1),) * 2, dominated, ((2,),))
    require((1, 1) in cases["dominated_terminal"]["full"] and
            (1, 1) not in cases["dominated_terminal"]["frontier"], "full/frontier conflation")
    repeated = ("query", 0, ("query", 0, ("emit", 0), ("emit", 1)), ("emit", 1))
    ordinary = ("query", 0, ("emit", 0), ("emit", 1))
    old = [execute(repeated, x, zero, ((1,),)) for x in range(2)]
    new = [execute(ordinary, x, zero, ((1,),)) for x in range(2)]
    require(old == [(0, (2,)), (1, (1,))] and new == [(0, (1,)), (1, (1,))],
            "repeated-query deletion control")
    result = {name: {"profiles": len(c["full"]), "frontier":
                    [[str(v) for v in row] for row in sorted(c["frontier"])]}
              for name, c in cases.items()}
    result["repeat_deletion"] = {"adequacy_preserved": True, "cost_nonincreasing": True}
    return result
