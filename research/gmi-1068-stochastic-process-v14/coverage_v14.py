"""Exact mandatory stochastic-process evidence counts."""
REQUIRED = {
    'test_stochastic_v14': {
        'closed_witness_arrows': 7,
        'closed_witness_pairs': 49,
        'closed_witness_triples': 343,
        'deterministic_maps': 11,
        'embedding_composition_equations': 94,
        'embedding_faithfulness_equations': 50,
        'embedding_identity_equations': 6,
        'embedding_triple_equations': 422,
        'kernel_pairs': 827,
        'kernel_triples': 20779,
        'kernel_unit_equations': 70,
        'kernels': 35,
        'probability_loss_witnesses': 1,
        'products_outside_input_grid': 372,
        'relation_pairs': 145,
        'relation_triples': 1341,
        'relation_unit_equations': 34,
        'relations': 17,
        'support_composition_equations': 827,
        'uniform_support_equations': 17,
    },
    'test_hostiles_v14': {
        'accepted_container_cases': 3,
        'corrupt_semantics_controls': 2,
        'empty_source_cases': 3,
        'malformed_input_rejections': 83,
        'missing_assumption_counterexamples': 4,
        'reversed_order_counterexamples': 1,
        'tiny_positive_support_cases': 1,
        'uniformization_counterexamples': 1,
    },
    'test_kernel_guard_v14': {
        'kernel_registration_rejections': 3,
    },
    'test_coverage_v14': {
        'coverage_guard_rejections': 159,
    },
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
