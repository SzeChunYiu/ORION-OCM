"""Exact mandatory measured checks; missing or unregistered evidence is invalid."""
REQUIRED = {
    "test_scalarization_v12": {
        "dimensions": 5, "vectors": 121, "ordered_pairs": 7381,
        "independent_dot_checks": 14762, "permutation_dot_checks": 14762,
        "positive_weights": 121, "nonnegative_weights": 121,
        "positive_pair_weight_checks": 551881, "nonnegative_pair_weight_checks": 551881,
        "dominated_weight_checks": 222302, "strict_improvement_checks": 192300,
        "separating_coordinates": 9534, "incomparable_pairs": 4392,
        "normalized_separator_checks": 8784, "feasible_sets": 512,
        "positive_minimizer_searches": 4599, "efficient_minimizer_checks": 4989,
        "rational_dot_checks": 32,
    },
    "test_hostiles_v12": {
        "malformed_input_rejections": 63, "scalar_reflection_failure_cases": 3,
        "separator_mutation_rejections": 16, "unsupported_frontier_certificates": 1,
        "unsupported_weight_checks": 49,
    },
    "test_kernel_guard_v12": {"kernel_registration_rejections": 3},
    "test_coverage_v12": {"coverage_guard_rejections": 134},
}


def validate_coverage(coverage):
    if type(coverage) is not dict or set(coverage) != set(REQUIRED):
        raise ValueError("missing or unexpected mandatory experiment")
    for module, required in REQUIRED.items():
        actual = coverage[module]
        if type(actual) is not dict or set(actual) != set(required):
            raise ValueError("missing or unexpected coverage field: " + module)
        for key, expected in required.items():
            if type(actual[key]) is not int or actual[key] != expected:
                raise ValueError("required check not executed: " + module + "/" + key)
    return True
