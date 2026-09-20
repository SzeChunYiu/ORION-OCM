"""Mandatory frozen corpus and independent-control counters."""
REQUIRED = {
    "test_resource_v10": {
        "primary_machines": 114244, "primary_budget_products": 214116,
        "primary_ordered_pair_checks": 856464, "larger_machines": 40,
        "triangle_checks": 6200, "relabeled_pair_checks": 1080,
        "execution_relation_checks": 10800, "bound_attaining_chains": 14,
    },
    "test_resource_hostiles_v10": {
        "boundary_models": 11, "hidden_cost_budget_checks": 4,
        "rejected_certificate_mutations": 22, "malformed_input_rejections": 66,
    },
    "test_independent_review_v10": {
        "machines": 200, "residual_pair_comparisons": 6109,
        "distance_mutants": 6601, "coherent_infinity_mutants": 705,
        "malformed_models": 8, "malformed_certificates": 8,
        "zero_cycle_controls": 2, "delayed_nonminimal_witness_rejected": 1,
        "seed": 106810, "coverage_guard_rejections": 100,
    },
}


def validate_coverage(coverage):
    if not isinstance(coverage, dict) or set(coverage) != set(REQUIRED):
        raise ValueError("missing or unexpected mandatory test module")
    for module, required in REQUIRED.items():
        if not isinstance(coverage[module], dict):
            raise ValueError("missing coverage mapping")
        for key, value in required.items():
            actual = coverage[module].get(key)
            if type(actual) is not int or actual != value:
                raise ValueError("frozen corpus/control not executed: " + module + "/" + key)
    for key in ("primary_finite_witnesses", "larger_finite_witnesses", "larger_budget_products"):
        actual = coverage["test_resource_v10"].get(key)
        if type(actual) is not int or actual <= 0:
            raise ValueError("missing executed resource witnesses/products")
    return True
