"""Exact mandatory corrected-target calibration counts from independent runs."""
REQUIRED = {
    'test_history_v16': {
        'admitted_paths': 682,
        'empty_graph_controls': 1,
        'empty_path_units': 162,
        'graph_admission_cases': 81,
        'history_malformed_rejections': 37,
        'nongenerated_domain_controls': 1,
        'parallel_edge_controls': 1,
        'paths_length_0': 162,
        'paths_length_1': 216,
        'paths_length_2': 324,
        'paths_length_3': 516,
        'paths_length_4': 868,
        'singleton_decodings': 216,
        'source_definedness_controls': 1,
        'subtype_concatenation_equations': 2090,
        'subtype_correspondences': 682,
        'typed_paths': 2086,
    },
    'test_algebra_v16': {
        'algebra_malformed_rejections': 23,
        'constant_selector_rejections': 1,
        'different_quotient_kernel_controls': 1,
        'group_associativity': 128,
        'group_products': 32,
        'group_unit_equations': 16,
        'independent_folds': 10922,
        'nonconstant_context_controls': 1,
        'parity_homomorphisms': 32,
        'unmatched_label_controls': 1,
        'words': 5461,
        'words_length_0': 1,
        'words_length_1': 4,
        'words_length_2': 16,
        'words_length_3': 64,
        'words_length_4': 256,
        'words_length_5': 1024,
        'words_length_6': 4096,
        'wrong_fold_context_rejections': 1,
    },
    'test_linear_v16': {
        'additivity_probes': 22765,
        'callback_unavailability_controls': 2,
        'coefficient_dimension_0': 1,
        'coefficient_dimension_1': 7,
        'coefficient_dimension_2': 49,
        'coefficient_dimension_3': 343,
        'coefficient_vectors': 400,
        'empty_dimension_counterexamples': 1,
        'homogeneity_probes': 91060,
        'linear_malformed_rejections': 39,
        'minmax_constant_preservation': 8,
        'minmax_fixed_weight_exclusions': 2,
        'minmax_monotonicity': 200,
        'minmax_rank_reversals': 1,
        'minmax_symmetry': 32,
        'negative_coefficient_witnesses': 162,
        'nonlinear_impostor_rejections': 1,
        'normalized_vectors': 30,
        'ordered_profile_pairs': 347971,
        'profile_evaluations': 22765,
        'representation_equations': 22765,
        'weak_basis_diagnostic_controls': 1,
    },
    'test_kernel_guard_v16': {
        'kernel_registration_rejections': 3,
    },
    'test_coverage_v16': {
        'coverage_guard_rejections': 311,
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
