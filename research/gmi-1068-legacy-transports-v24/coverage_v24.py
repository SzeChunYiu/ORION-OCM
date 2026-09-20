"""Mandatory measured legacy transport checks, including every field and module."""
REQUIRED = {'test_controls_v24': {'plan_boundary_controls': 12,
                       'preference_boundary_controls': 5,
                       'profile_boundary_controls': 6},
 'test_coverage_v24': {'coverage_guard_rejections': 212},
 'test_custody_v24': {'inherited_custody_rejections': 14,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_hostiles_v24': {'malformed_input_rejections': 99,
                       'semantic_mutation_rejections': 28,
                       'valid_certificate_controls': 5},
 'test_kernel_guard_v24': {'kernel_registration_rejections': 4},
 'test_plans_v24': {'partial_decoded_observations': 33296,
                    'partial_feasible_contexts': 16790,
                    'partial_feasible_ids': 6243,
                    'partial_subfamily_cases': 33586,
                    'partial_tables': 4237,
                    'partial_threshold_cases': 8474,
                    'relation_decoded_observations': 5506,
                    'relation_feasible_contexts': 1940,
                    'relation_relations': 689,
                    'relation_subfamily_cases': 5054},
 'test_preferences_v24': {'context_instances': 43690,
                          'context_observations': 128160,
                          'parent_function_calls': 87380,
                          'pareto_ids': 29836,
                          'rosters': 4369,
                          'scalar_ids': 29018,
                          'selection_calls': 34952},
 'test_profiles_v24': {'a_case_tuples': 1296,
                       'a_context_observations': 11952,
                       'a_full_histories': 9936,
                       'a_selected_histories': 2016,
                       'a_tables': 81,
                       'b_case_tuples': 20000,
                       'b_context_observations': 112448,
                       'b_full_histories': 74688,
                       'b_selected_histories': 37760,
                       'b_tables': 625}}

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
