"""Corrected finite-enumeration, rendering and delegation countercontrols."""
from functools import partial
from itertools import product
from structural_threshold_costs_v1 import INPUTS, PARITY, compiled, require


def bounded_output_counterexample():
    inputs = tuple(product((0, 1), repeat=4)); table = set()
    for weights in product(range(-2, 3), repeat=4):
        values = [sum(w * b for w, b in zip(weights, point)) for point in inputs]
        table.update(tuple(int(v >= t) for v in values) for t in range(-8, 10))
    weights, threshold = (3, 2, 2, 1), 4
    omitted = tuple(int(sum(w * b for w, b in zip(weights, point)) >= threshold)
                    for point in inputs)
    require(len(table) == 986 and omitted not in table, "old output-grid counterexample lost")
    return {"bounded_output_functions": len(table), "omitted_weights": weights,
            "omitted_threshold": threshold, "omitted_full_truth_table": omitted,
            "bounded_grid_covers_arbitrary_output_coefficients": False}


def rendering_counterexample():
    head = "def f(x):\n    a,b,c=x\n    s="
    first = head + "-a+b+c\n    return int(s>=1)\n"
    reordered = head + "b+c-a\n    return int(s>=1)\n"
    n, f, _ = compiled(first); m, g, _ = compiled(reordered)
    require(tuple(f(x) for x in INPUTS) == tuple(g(x) for x in INPUTS), "rendering changed function")
    require((n, m) == (18, 17), "UNVERIFIABLE: rendering countercontrol opcode layout")
    return {"fixed_order_opcodes": n, "reordered_opcodes": m, "all8_outputs_equal": True,
            "fixed_input_order_is_always_minimal": False}


def delegation_counterexample():
    def threshold_net(x):
        a, b, c = x; s = a + b + c
        h0, h1, h2 = int(s >= 1), int(s >= 2), int(s >= 3)
        return int(h0 - h1 + h2 >= 1)
    def xor_net(x):
        return x[0] ^ x[1] ^ x[2]
    # partial is a C-implemented outer callable; its Python descendant is explicit.
    neural, non_neural = partial(threshold_net), partial(xor_net)
    require(not hasattr(neural, "__code__") and hasattr(neural.func, "__code__"),
            "opaque-wrapper/visible-descendant control changed")
    source = "def f(x):\n    return delegate(x)\n"
    n, f, _ = compiled(source, {"delegate": neural})
    m, g, _ = compiled(source, {"delegate": non_neural})
    require(tuple(f(x) for x in INPUTS) == tuple(g(x) for x in INPUTS) == PARITY,
            "delegated exact task failed")
    require(n == m == 4, "UNVERIFIABLE: delegated wrapper opcode layout")
    return {"neural_wrapper_per_sweep": 8 * n, "non_neural_wrapper_per_sweep": 8 * m,
            "same_candidate_frame_overhead": True, "outer_callable_has_python_code": False,
            "python_descendant_is_explicitly_present": True,
            "candidate_frame_call_opcode_included": True, "callee_work_included": False,
            "universal_exclusion_of_delegating_class": False,
            "full_physical_cost_comparison_established": False}
