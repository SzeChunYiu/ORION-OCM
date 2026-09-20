"""Exact mandatory partial-operation reconstruction coverage."""
REQUIRED = {'test_coverage_v19': {'coverage_guard_rejections': 255},
 'test_custody_v19': {'inherited_custody_rejections': 10,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_hostiles_v19': {'empty_category_controls': 1,
                       'table_query_malformed_rejections': 64,
                       'tagged_failure_controls': 3,
                       'typed_category_malformed_rejections': 36},
 'test_kernel_guard_v19': {'kernel_registration_rejections': 4},
 'test_recovery_v19': {'binary_encoding_decoder_checks': 26264,
                       'model_pair_information_checks': 6566,
                       'raw_response_checks': 2602,
                       'recovery_models': 84},
 'test_tables_v19': {'accepted_tables': 59,
                     'arrow_permutations': 324,
                     'base_responses': 6561,
                     'bundled_pair_checks': 489,
                     'composable_pairs': 403,
                     'law_pattern_000': 218695,
                     'law_pattern_001': 42291,
                     'law_pattern_010': 540,
                     'law_pattern_011': 237,
                     'law_pattern_100': 119,
                     'law_pattern_101': 237,
                     'law_pattern_110': 50,
                     'law_pattern_111': 59,
                     'object_permutations': 83,
                     'object_roundtrip_responses': 9422,
                     'objects': 79,
                     'relabel_responses': 38701,
                     'tables_size_0': 1,
                     'tables_size_1': 2,
                     'tables_size_2': 81,
                     'tables_size_3': 262144,
                     'unit_instances': 79,
                     'weak_local_coherent_nonassociative_tables': 27,
                     'weak_nonassociative_tables': 31392},
 'test_witnesses_v19': {'associativity_isolation_controls': 1,
                        'coherence_isolation_controls': 1,
                        'composite_value_loss_controls': 1,
                        'filled_definedness_collision_controls': 1,
                        'fresh_bottom_retention_controls': 1,
                        'nonunital_multiplicative_map_controls': 1,
                        'one_sided_identity_controls': 2,
                        'small_total_magmas': 18,
                        'small_unital_associative_magmas': 5,
                        'weak_definedness_isolation_controls': 1}}

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
