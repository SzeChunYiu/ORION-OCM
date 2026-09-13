"""DU V2: static underdetermination, retained comparators and finite closure."""
from fractions import Fraction as F
from itertools import permutations
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def vertices(edges):
    return set(edges) | {target for targets in edges.values() for target in targets}


def reach(edges, start, budget):
    if type(budget) is not int or budget < 0 or start not in vertices(edges):
        raise ValueError("registered initial state and nonnegative integer steps required")
    seen = frontier = {start}
    for _ in range(budget):
        frontier = {v for u in frontier for v in edges.get(u, ())}-seen
        seen = seen | frontier
        if not frontier:
            break
    return seen


def best_by_family(profiles, families, retained):
    if not set(retained) <= profiles.keys() or not set(retained) <= families.keys():
        raise ValueError("retained realization lacks registered profile/family")
    best = {}
    for state in retained:
        value = profiles[state]
        if type(value) not in (int, F) or value < 0:
            raise ValueError("finite exact nonnegative scalar profiles required")
        family = families[state]
        best[family] = min(value, best.get(family, value))
    return best


def support(best):
    return tuple(sorted(f for f, value in best.items() if value == min(best.values()))) if best else ()


def exclusion(profiles, families, retained, target, lower, comparator):
    """Finite check of both the target bound and the retained competing witness."""
    best_by_family(profiles, families, retained)
    if type(lower) not in (int, F) or lower < 0:
        raise ValueError("finite exact target lower bound required")
    if any(profiles[s] < lower for s in retained if families[s] == target):
        raise ValueError("claimed lower bound is false on the retained set")
    return (comparator in retained and families[comparator] != target
            and profiles[comparator] < lower)


def closure_certificate(edges, start, paths):
    """Finite positive certificate: paths to every listed state + successor closure."""
    covered = set(paths)
    if start not in covered or not covered <= vertices(edges):
        return False
    for state, path in paths.items():
        if not path or path[0] != start or path[-1] != state:
            return False
        if any(v not in edges.get(u, ()) for u, v in zip(path, path[1:])):
            return False
        if not set(edges.get(state, ())) <= covered:
            return False
    return True


def check_static_underdetermination():
    profiles = {"s0": 10, "a": 5, "b": 3}
    families = {"s0": "A", "a": "A", "b": "B"}
    results = {}
    for name, edges in (("D1", {"s0": ("a",)}), ("D2", {"s0": ("b",)})):
        kept = reach(edges, "s0", 1)
        results[name] = {"reachable": sorted(kept), "support": list(support(best_by_family(profiles, families, kept)))}
    require(results["D1"]["support"] == ["A"] and results["D2"]["support"] == ["B"],
            "static-data counterexample lost")
    return {"laws": results, "scope": "static profiles/families alone; registered-D analysis stays open"}


def check_schedule_scope():
    updates = {"double": lambda x: 2*x, "add_three": lambda x: x+3}
    orders = {}
    for order in permutations(updates):
        value, accepted = 1, True
        for name in order:
            proposal = updates[name](value)
            if proposal > 6:
                accepted = False
                break
            value = proposal
        orders["->".join(order)] = {"last_admitted": value, "completed": accepted}
    edges = {i: tuple(v for op in updates.values() if (v := op(i)) <= 6) for i in range(1, 7)}
    attainable = reach(edges, 1, 2)
    require(orders["double->add_three"] == {"last_admitted": 5, "completed": True}, "order result wrong")
    require(orders["add_three->double"] == {"last_admitted": 4, "completed": False}, "rejected update committed")
    require(attainable == {1, 2, 4, 5}, "all-schedules reachability incorrect")
    return {"orders": orders, "all_admitted_schedules_at_most_two_steps": sorted(attainable)}


def check_retained_comparator():
    profiles = {"A2": 2, "A9": 9, "B5": 5}
    families = {"A2": "A", "A9": "A", "B5": "B"}
    whole, restricted = set(profiles), {"A9", "B5"}
    before, after = (best_by_family(profiles, families, s) for s in (whole, restricted))
    require(all(after[f] >= before[f] for f in before), "restriction lowered an infimum")
    require(support(before) == ("A",) and support(after) == ("B",), "selection inversion lost")
    decisions = [exclusion(profiles, families, s, "B", 5, "A2") for s in (whole, restricted, whole)]
    require(decisions == [True, False, True], "exclusion survived loss of its comparator")
    return {"global_bests": before, "restricted_bests": after,
            "B_excluded_before_removed_restored": decisions,
            "lower_bounds_monotone_but_exclusions_need_retained_comparator": True}


def check_prefix_and_closure():
    closed = {"s0": ("s1",), "s1": ("s2",), "s2": ()}
    extended = dict(closed, s2=("s3",), s3=())
    profiles = {"s0": 3, "s1": 2, "s2": 1, "s3": F(1, 2)}
    families = {"s0": "A", "s1": "A", "s2": "A", "s3": "B"}
    prefix = {f"s{i}": tuple(f"s{j}" for j in range(i+1)) for i in range(3)}
    require(reach(closed, "s0", 2) == reach(extended, "s0", 2), "prefix differs")
    require(closure_certificate(closed, "s0", prefix), "exhaustive finite certificate refused")
    require(not closure_certificate(extended, "s0", prefix), "hidden successor escaped closure check")
    require(closure_certificate(extended, "s0", dict(prefix, s3=("s0", "s1", "s2", "s3"))),
            "extended complete certificate refused")
    outcomes = [support(best_by_family(profiles, families, reach(g, "s0", 3))) for g in (closed, extended)]
    require(outcomes == [("A",), ("B",)], "adverse continuation fails to change verdict")
    branching = {"s0": ("b", "c"), "c": ("d",)}
    bp, bf = {"s0": 10, "b": 1, "c": 9, "d": 8}, {"s0": "A", "b": "B", "c": "B", "d": "A"}
    require(all(bp[v] < bp[u] and bf[v] != bf[u] for u, vs in branching.items() for v in vs), "branch premise fails")
    require(all(support(best_by_family(bp, bf, reach(branching, "s0", b))) == ("B",) for b in (1, 2)),
            "edgewise improvement was confused with alternating optimum")
    return {"same_prefix_budget": 2, "closed_limit_support": ["A"], "extended_limit_support": ["B"],
            "closed_certificate_accepted": True, "incomplete_certificate_rejected": True,
            "strict_improvement_and_family_change_do_not_force_branching_verdict_flip": True}


def run():
    return {"schema": "developmental-underdetermination-v2", "all_checks_green": True,
            "terminal": "GRAND_GMI_DEVELOPMENTAL_SCOPE_REPAIR_GREEN_AT_FINITE_SCOPE",
            "static_underdetermination": check_static_underdetermination(),
            "schedule_scope": check_schedule_scope(), "retained_comparator": check_retained_comparator(),
            "prefix_and_positive_closure": check_prefix_and_closure(),
            "historical_receipt_preserved": "GRAND_GMI_DEVELOPMENTAL_UNDERDETERMINATION_RECEIPT_V1.json",
            "claim_ceiling": "finite declared graphs; no learned dynamics or empirical training claim"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
