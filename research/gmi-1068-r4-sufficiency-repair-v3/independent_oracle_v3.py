"""Independent conditional-independence oracle, without normalizing conditionals."""
from fractions import Fraction
from itertools import product


def rank_one(atoms, first, second, given):
    # Enumerate weighted atoms; empty conditioning events satisfy 0=0.
    witnesses = []
    for group, a, b in product((0, 1), repeat=3):
        total = Fraction()
        row = Fraction()
        col = Fraction()
        cell = Fraction()
        for theta, x, y, s, weight in atoms:
            values = (theta, x, y, s)
            if values[given] != group:
                continue
            total += weight
            if values[first] == a:
                row += weight
            if values[second] == b:
                col += weight
            if values[first] == a and values[second] == b:
                cell += weight
        if cell * total != row * col:
            witnesses.append([group, a, b, cell * total, row * col])
    return not witnesses, witnesses


def evaluate(joint, statistic):
    atoms = [(theta, x, y, statistic[x], Fraction(weight))
             for (theta, x, y), weight in joint.items()]
    parameter = rank_one(atoms, 0, 1, 3)
    predictive = rank_one(atoms, 2, 1, 3)
    return {"parameter_sufficient": parameter[0], "predictive_sufficient": predictive[0],
            "parameter_crossproduct_discrepancies": parameter[1],
            "predictive_crossproduct_discrepancies": predictive[1]}
