"""Exact required coverage for the frozen frontier and simulation study."""
REQUIRED = {'test_bridge_v20': {'budget_models': 9,
                     'budget_revival_controls': 1,
                     'budget_word_checks': 90,
                     'endpoint_context_rejections': 38,
                     'endpoint_contexts': 108,
                     'trace_scope_controls': 1},
 'test_controls_v20': {'guarded_composition_cases': 2336,
                       'revival_controls': 3,
                       'scope_controls': 40},
 'test_coverage_v20': {'coverage_guard_rejections': 229},
 'test_custody_v20': {'inherited_custody_rejections': 11,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_frontiers_v20': {'actual_contexts': 18101,
                        'ambient_observations': 51654,
                        'attained_subsets': 251,
                        'cofinal_subset_candidates': 823,
                        'context_selectors': 134911,
                        'enumeration_choices': 487,
                        'frontier_preorders': 35,
                        'minimum_cover_checks': 399},
 'test_hostiles_v20': {'malformed_api_rejections': 162,
                       'relation_scope_controls': 5},
 'test_kernel_guard_v20': {'kernel_registration_rejections': 4},
 'test_maps_v20': {'cofinal_image_equations': 752245,
                   'guarded_maps': 23539,
                   'map_subset_candidates': 1563467,
                   'partial_maps': 59403,
                   'postcomposition_contexts': 7409,
                   'postcomposition_observations': 13392,
                   'postcomposition_selectors': 26969},
 'test_simulation_v20': {'candidate_simulation_relations': 5193,
                         'greatest_pairs': 455404,
                         'maximum_distinguishing_word_length': 4,
                         'pair_bfs_checks': 1070356,
                         'pruned_endpoint_equations': 3331183,
                         'pruning_subsets': 951577,
                         'refinement_deleted_pairs': 196836,
                         'refinement_stability_checks': 235925,
                         'rejected_pair_witnesses': 614952,
                         'simulation_machines': 119113}}

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
