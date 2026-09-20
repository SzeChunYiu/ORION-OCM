"""Measured finite coverage is mandatory, with strict module/key/count identities."""
REQUIRED = {'test_controls_v27': {'lawful_system_compositions': 2,
                       'probability_loss_controls': 1,
                       'resource_boundary_controls': 2,
                       'system_failure_revivals': 1,
                       'system_tagged_preservations': 1},
 'test_coverage_v27': {'coverage_guard_rejections': 246},
 'test_custody_v27': {'inherited_custody_rejections': 14,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 6,
                      'valid_inherited_custody_controls': 1},
 'test_events_v27': {'basis_extractions': 177,
                     'event_boundary_controls': 4,
                     'event_pairs': 2117,
                     'event_triples': 79401,
                     'events': 59,
                     'normalized_events': 17},
 'test_hostiles_v27': {'coherent_semantic_rejections': 15,
                       'malformed_input_rejections': 168,
                       'semantic_certificate_baselines': 5,
                       'valid_empty_and_typed_controls': 4},
 'test_kernel_guard_v27': {'kernel_registration_rejections': 4},
 'test_lts_v27': {'back_maps': 433,
                  'candidate_maps': 1143,
                  'forward_maps': 521,
                  'hom_maps': 159,
                  'lts_named_controls': 5,
                  'mapped_source_paths': 3876,
                  'path_composition_pairs': 10178,
                  'source_lifts': 1517,
                  'target_path_queries': 1031},
 'test_parent_ledger_v27': {'parent_ledger_mutation_rejections': 949, 'valid_parent_ledger_controls': 1},
 'test_tasks_v27': {'adjacent_regular_triples': 1672,
                    'admissible_possibility_subsets': 6,
                    'possibility_pair_checks': 256,
                    'regular_task_pairs': 169,
                    'task_named_controls': 3,
                    'task_pairs': 256,
                    'task_relations': 16,
                    'task_triples': 4096,
                    'typed_inclusion_bridges': 169},
 'test_tests_v27': {'labelled_test_controls': 5,
                    'labelled_tests': 125,
                    'paired_outcome_events': 49084,
                    'test_pairs': 12271}}

def validate_coverage(actual):
    if type(actual) is not dict or set(actual) != set(REQUIRED):
        raise ValueError("coverage module inventory differs")
    for module, expected in REQUIRED.items():
        values = actual[module]
        if type(values) is not dict or set(values) != set(expected):
            raise ValueError("coverage counter inventory differs: " + module)
        for key, count in expected.items():
            if type(values[key]) is not int or values[key] != count:
                raise ValueError("coverage count differs: " + module + ":" + key)
    return True
