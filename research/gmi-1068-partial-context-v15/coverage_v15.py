"""Exact mandatory partial-context evidence counts."""
REQUIRED = {
    'test_context_v15': {
        'comparisons': 14355,
        'contexts': 3625,
        'empty_domains': 232,
        'equivalence_equations': 14355,
        'equivalence_reflexivity': 6525,
        'equivalence_symmetry': 14355,
        'equivalence_transitivity': 34713,
        'full_process_collisions': 1,
        'full_process_law_equations': 42,
        'observations': 10875,
        'opposite_evaluator_pairs': 12960,
        'opposite_formula_equations': 25920,
        'preorders': 29,
        'quotient_antisymmetry': 8517,
        'quotient_comparison_equations': 14355,
        'quotient_reflexivity': 5025,
        'quotient_transitivity': 16185,
        'reflexivity': 6525,
        'representative_equations': 42291,
        'transitivity': 34713,
    },
    'test_hostiles_v15': {
        'ambient_restriction_controls': 2,
        'empty_carrier_controls': 2,
        'equivalent_value_controls': 1,
        'failed_reversal_premises': 16,
        'registered_indicator_class_controls': 1,
        'nonmatching_indicator_class_controls': 1,
        'malformed_input_rejections': 81,
        'outside_domain_comparison_rejections': 3,
        'quotient_corruption_rejections': 4,
        'swap_closure_alternative_controls': 1,
        'undefined_label_controls': 1,
        'weakened_diagnostic_rejections': 1,
    },
    'test_kernel_guard_v15': {
        'kernel_registration_rejections': 3,
    },
    'test_coverage_v15': {
        'coverage_guard_rejections': 179,
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
