"""Mandatory measured functor, restriction, resource, malformed and custody checks."""
REQUIRED = {'test_controls_v26': {'admission_named_controls': 6,
                       'indiscrete_failed_join_controls': 342,
                       'indiscrete_tree_controls': 474,
                       'nonfaithful_named_controls': 1,
                       'optional_parent_controls': 10,
                       'semantic_mutation_rejections': 7,
                       'valid_fixed_map_certificates': 1},
 'test_coverage_v26': {'coverage_guard_rejections': 279},
 'test_custody_v26': {'inherited_custody_rejections': 18,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_functors_v26': {'accepted_functors': 59,
                       'candidate_maps': 153,
                       'composition_rejected': 8,
                       'endpoint_rejected': 38,
                       'identity_rejected': 48,
                       'nonfaithful_injective_functors': 28,
                       'noninjective_witnesses': 7,
                       'object_injective_functors': 52,
                       'successful_tree_queries': 2926,
                       'tree_queries': 3862},
 'test_hostiles_v26': {'malformed_constructor_rejections': 91,
                       'malformed_path_rejections': 41,
                       'malformed_response_rejections': 12,
                       'malformed_tree_rejections': 108,
                       'valid_constructor_controls': 3,
                       'valid_failure_controls': 4},
 'test_kernel_guard_v26': {'kernel_registration_rejections': 4},
 'test_optional_ledger_v26': {'optional_ledger_mutation_rejections': 657, 'valid_optional_ledger_controls': 1},
 'test_resources_v26': {'empty_word_lifts': 9,
                        'failed_pair_revivals': 41,
                        'ill_typed_paths': 2229,
                        'path_attempts': 2331,
                        'resource_pairs': 196,
                        'successful_lifts': 70,
                        'successful_pair_projections': 20,
                        'typed_base_paths': 102,
                        'unaffordable_paths': 32},
 'test_restrictions_v26': {'admission_cases': 439,
                           'ambient_categories': 59,
                           'missing_composite_witnesses': 65,
                           'missing_identity_witnesses': 259,
                           'pattern_00': 47,
                           'pattern_01': 212,
                           'pattern_10': 18,
                           'pattern_11': 162,
                           'proper_wide_subcategories': 103,
                           'restricted_identity_checks': 200,
                           'restricted_pair_checks': 790,
                           'restricted_trees': 17478}}

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
