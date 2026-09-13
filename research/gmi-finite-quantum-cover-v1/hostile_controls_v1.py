"""Registered hostile controls; each defect changes exactly one premise or witness."""
from fractions import Fraction as F
from quantum_witness_v1 import verify, verify_mixed, task_fingerprint, verify_registered
from rational_matrix_v1 import identity, ray_state, require

NAMES = ("zero_state", "float_state", "missing_sender", "missing_context",
         "missing_effect", "all_zero_effects", "swapped_effects", "tiny_leakage",
         "dropped_promised_pair", "expanded_acceptable_set", "empty_acceptable_set",
         "outside_mixed_support", "negative_mixture", "unnormalized_mixture",
         "approximate_success_misread_as_exact")


def example():
    task = {"actions": 2, "allowed": [[frozenset((0,))], [frozenset((1,))]]}
    return task, [list(v) for v in identity(2)], [
        [[list(row) for row in ray_state(v)] for v in identity(2)]]


def exercise(name):
    task, rays, factors = example()
    expected = task_fingerprint(task)
    if name == "zero_state":
        rays[0] = [0, 0]
    elif name == "float_state":
        rays[0][0] = 1.0
    elif name == "missing_sender":
        rays.pop()
    elif name == "missing_context":
        factors.pop()
    elif name == "missing_effect":
        factors[0].pop()
    elif name == "all_zero_effects":
        factors[0] = [[[0, 0], [0, 0]]] * 2
    elif name == "swapped_effects":
        factors[0].reverse()
    elif name == "tiny_leakage":
        rays[0] = [10**6, 1]  # forbidden probability exactly 1/(10^12+1), not zero
    elif name == "dropped_promised_pair":
        task["allowed"][1][0] = None
    elif name == "expanded_acceptable_set":
        task["allowed"][0][0] = frozenset((0, 1))
    elif name == "empty_acceptable_set":
        task["allowed"][0][0] = frozenset()
    elif name == "outside_mixed_support":
        task = {"actions": 3, "allowed": [[frozenset((0, 1))]]}
        basis = identity(3)
        return verify(task, (basis[2],), (tuple(ray_state(v) for v in basis),))
    elif name in ("negative_mixture", "unnormalized_mixture",
                  "approximate_success_misread_as_exact"):
        weights = {"negative_mixture": (F(-1), F(2)),
                   "unnormalized_mixture": (F(1), F(1)),
                   "approximate_success_misread_as_exact": (F(1, 2), F(1, 2))}[name]
        mixed = ((tuple(zip(weights, rays))), ((F(1), rays[1]),))
        return verify_mixed(task, mixed, factors)
    else:
        raise ValueError("unknown hostile control")
    return verify_registered(task, rays, factors, expected)


def run_hostile_controls():
    rejected = []
    for name in NAMES:
        try:
            exercise(name)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("hostile control escaped: " + name)
    require(len(rejected) == len(set(NAMES)) == 15, "hostile census incomplete")
    return rejected
