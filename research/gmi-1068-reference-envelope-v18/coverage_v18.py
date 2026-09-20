"""Exact mandatory reference-envelope calibration coverage."""
REQUIRED = {'test_boundaries_v18': {'actual_policy_reversals': 9,
                         'common_bound_controls': 4,
                         'conditional_probability_checks': 12,
                         'environment_history_checks': 254,
                         'nonrectangular_reversal_controls': 1,
                         'rectangular_repair_controls': 1},
 'test_coverage_v18': {'coverage_guard_rejections': 272},
 'test_custody_v18': {'inherited_custody_rejections': 10,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_hostiles_v18': {'empty_history_measure_controls': 2,
                       'empty_output_alphabet_controls': 1,
                       'empty_resource_controls': 1,
                       'measure_malformed_rejections': 47,
                       'prefix_malformed_rejections': 46,
                       'resource_interaction_malformed_rejections': 33},
 'test_kernel_guard_v18': {'kernel_registration_rejections': 4},
 'test_measures_v18': {'actual_measure_contexts': 52,
                       'constant_expectations': 63,
                       'constant_lower_values': 93,
                       'context_observations': 260,
                       'nonlinear_lower_controls': 1,
                       'omitted_coordinate_controls': 1,
                       'pair_family_checks': 2511,
                       'pair_weight_checks': 11349,
                       'prior_families': 31,
                       'probability_vectors': 21,
                       'profile_family_values': 279,
                       'profile_pairs': 820,
                       'profiles': 40},
 'test_prefix_v18': {'alias_output_controls': 1,
                     'empty_interpreter_controls': 1,
                     'epsilon_interpreter_controls': 1,
                     'finite_books': 15131,
                     'kraft_checks': 105917,
                     'padding_margin_controls': 3,
                     'prefix_domains': 677,
                     'shortest_output_equations': 181572,
                     'tiny_weight_controls': 1,
                     'wrapper_cases': 90786,
                     'wrapper_decode_queries': 1906506,
                     'wrapper_profile_bounds': 817074},
 'test_resources_v18': {'actual_target_contexts': 96,
                        'equivalent_resource_controls': 1,
                        'pair_target_checks': 816,
                        'partial_resource_controls': 1,
                        'resource_orientation_controls': 1,
                        'resource_pairs': 278,
                        'resource_preorders': 35,
                        'target_context_values': 278}}

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
