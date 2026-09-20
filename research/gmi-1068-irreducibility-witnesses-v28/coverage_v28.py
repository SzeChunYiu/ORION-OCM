"""Strict mandatory coverage of the frozen finite witness calibration."""
REQUIRED = {'test_coverage_v28': {'coverage_guard_rejections': 232},
 'test_custody_v28': {'inherited_custody_rejections': 14,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 6,
                      'valid_inherited_custody_controls': 1},
 'test_forward_v28': {'allowed_positive_revivals': 1,
                      'collapsed_history_controls': 1,
                      'context_decoder_decisions': 81,
                      'context_recoverable_pairs': 9,
                      'designated_reversal_controls': 1,
                      'forward_contexts': 9,
                      'forward_long_or_empty_queries': 5,
                      'forward_premise_rejections': 5,
                      'order_decoder_decisions': 81,
                      'order_recoverable_pairs': 27,
                      'original_checker_replays': 1,
                      'singleton_tags': 18,
                      'unchanged_process_pairs': 81},
 'test_hostiles_v28': {'empty_or_type_separation_controls': 5,
                       'malformed_input_rejections': 122,
                       'semantic_certificate_baselines': 4,
                       'semantic_mutation_rejections': 20},
 'test_kernel_guard_v28': {'kernel_registration_rejections': 4},
 'test_reverse_v28': {'active_domain_decoder_decisions': 256,
                      'active_domain_recoverable_pairs': 192,
                      'domain_signature_decoder_decisions': 256,
                      'domain_signature_recoverable_pairs': 256,
                      'primitive_roundtrips': 4,
                      'raw_admission_checks': 120,
                      'reverse_contexts': 64,
                      'reverse_model_pairs': 256,
                      'reverse_named_boundary_controls': 10,
                      'reverse_tag_observations': 1920,
                      'same_admission_composition_controls': 1,
                      'tagged_decoder_decisions': 256,
                      'tagged_recoverable_pairs': 256,
                      'weak_state_decoder_decisions': 256,
                      'weak_state_recoverable_pairs': 64},
 'test_scalar_v28': {'scalar_named_premise_controls': 4,
                     'scalar_profile_pairs': 16,
                     'scalar_weight_comparisons': 32},
 'test_witness_ledger_v28': {'valid_witness_ledger_controls': 1,
                             'witness_ledger_mutation_rejections': 603}}

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
