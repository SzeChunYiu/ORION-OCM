"""Independent exact tiny-cube certificates for the analytic lower bounds."""
from itertools import combinations, product
from structural_threshold_costs_v1 import INPUTS, PARITY, require


def midpoint_certificates():
    result = []
    for parity in (0, 1):
        same = [x for x in INPUTS if sum(x) % 2 == parity]
        other = [x for x in INPUTS if sum(x) % 2 != parity]
        for x, y in combinations(same, 2):
            target = tuple(a + b for a, b in zip(x, y))
            witnesses = [(u, v) for u, v in combinations(other, 2)
                         if tuple(a + b for a, b in zip(u, v)) == target]
            require(witnesses, "opposite-parity midpoint missing")
            result.append({"parity": parity, "same": [x, y], "opposite": witnesses[0]})
    require(len(result) == 12, "incomplete same-parity pair coverage")
    return result


def two_input_threshold_certificate():
    square = tuple(product((0, 1), repeat=2)); realized = set()
    for weights in product((-1, 0, 1), repeat=2):
        for threshold in range(-2, 4):
            realized.add(tuple(int(sum(w * x for w, x in zip(weights, point)) >= threshold)
                               for point in square))
    all_functions = set(product((0, 1), repeat=4))
    forbidden = {(0, 1, 1, 0), (1, 0, 0, 1)}
    require(realized == all_functions - forbidden, "two-input output classification")
    categories = {"constant": 0, "literal": 0, "one_corner": 0, "three_corners": 0}
    for function in realized:
        count = sum(function)
        category = "constant" if count in (0, 4) else "one_corner" if count == 1 else (
            "three_corners" if count == 3 else "literal")
        if count == 2:
            chosen = [x for x, value in zip(square, function) if value]
            require(sum(a != b for a, b in zip(*chosen)) == 1, "opposite corners falsely admitted")
        categories[category] += 1
    return {"realized_output_functions": len(realized), "categories": categories,
            "two_opposite_corner_patterns_excluded_by_midpoint": True}


def nonunate_controls():
    directions = []
    for axis in range(3):
        differences = []
        for x in INPUTS:
            if x[axis] == 0:
                y = list(x); y[axis] = 1
                differences.append(sum(y) % 2 - sum(x) % 2)
        require(set(differences) == {-1, 1}, "parity became unate")
        directions.append(differences)
    # Dropping the hidden-only output premise permits one hidden gate.
    def skip_net(x):
        s = sum(x); h = int(s >= 2)
        return int(s - 2 * h >= 1)
    values = tuple(skip_net(x) for x in INPUTS)
    require(values == PARITY, "skip-connection boundary control failed")
    return {"parity_edge_differences_each_axis": directions,
            "one_hidden_gate_with_raw_input_skip_computes_parity": True,
            "skip_connections_inside_registered_class": False}
