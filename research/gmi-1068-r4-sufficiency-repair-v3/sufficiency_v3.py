"""Finite, exact conditional-law criteria; Θ has the declared two-point support."""
from fractions import Fraction
from itertools import product

CELLS = tuple(product((0, 1), repeat=3))


def validate(joint, statistic):
    if set(joint) != set(CELLS):
        raise ValueError("declare every theta/X/Y cell, including zero cells")
    if any(not isinstance(p, (int, Fraction)) or p < 0 for p in joint.values()):
        raise ValueError("exact nonnegative rational probabilities required")
    if sum(joint.values()) != 1:
        raise ValueError("joint probability must sum to one")
    if len(statistic) != 2 or any(s not in (0, 1) for s in statistic):
        raise ValueError("statistic must be a declared map from binary X to binary S")
    for theta in (0, 1):
        if sum(p for (t, x, y), p in joint.items() if t == theta) <= 0:
            raise ValueError("every declared theta requires positive prior mass")


def mass(joint, predicate):
    return sum((Fraction(p) for atom, p in joint.items() if predicate(*atom)), Fraction())


def conditional(joint, variable, condition):
    denominator = mass(joint, condition)
    if denominator == 0:
        return None
    return tuple(mass(joint, lambda t, x, y, v=v: condition(t, x, y) and variable(t, x, y) == v)
                 / denominator for v in (0, 1))


def analyze(joint, statistic):
    validate(joint, statistic)
    parameter_failures, predictive_failures = [], []
    parameter_tables, predictive_tables = [], []
    zero_parameter_events, zero_predictive_events = [], []
    for s in (0, 1):
        reference = conditional(joint, lambda t, x, y: x, lambda t, x, y: statistic[x] == s)
        for theta in (0, 1):
            actual = conditional(joint, lambda t, x, y: x,
                                 lambda t, x, y: statistic[x] == s and t == theta)
            if actual is None:
                zero_parameter_events.append([s, theta])
                continue
            row = {"S": s, "theta": theta, "X_given_S_theta": actual, "X_given_S": reference}
            parameter_tables.append(row)
            if actual != reference:
                parameter_failures.append(row)
    for observed in (0, 1):
        actual = conditional(joint, lambda t, x, y: y, lambda t, x, y: x == observed)
        if actual is None:
            zero_predictive_events.append(observed)
            continue
        reference = conditional(joint, lambda t, x, y: y,
                                lambda t, x, y: statistic[x] == statistic[observed])
        row = {"X": observed, "S": statistic[observed], "Y_given_X": actual, "Y_given_S": reference}
        predictive_tables.append(row)
        if actual != reference:
            predictive_failures.append(row)
    return {"parameter_sufficient": not parameter_failures,
            "predictive_sufficient": not predictive_failures,
            "parameter_tables": parameter_tables, "predictive_tables": predictive_tables,
            "parameter_discrepancies": parameter_failures, "predictive_discrepancies": predictive_failures,
            "zero_parameter_conditioning_events": zero_parameter_events,
            "zero_predictive_conditioning_events": zero_predictive_events}


def model(x_rule, y_rule, theta_one=Fraction(1, 2)):
    """Construct the joint law from independent theta and a fair auxiliary coin."""
    if x_rule not in ("independent", "theta") or y_rule not in ("copy", "constant"):
        raise ValueError("unknown mechanism")
    if not isinstance(theta_one, (int, Fraction)):
        raise ValueError("exact rational prior required")
    theta_one = Fraction(theta_one)
    joint = {cell: Fraction() for cell in CELLS}
    for theta, coin in product((0, 1), repeat=2):
        weight = (theta_one if theta else 1 - theta_one) / 2
        x = coin if x_rule == "independent" else theta
        y = x if y_rule == "copy" else 0
        joint[(theta, x, y)] += weight
    return joint
