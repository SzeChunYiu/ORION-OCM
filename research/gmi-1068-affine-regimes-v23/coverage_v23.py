"""Exact measured affine-diagram and actual-codec calibration."""
REQUIRED = {'test_contexts_v23': {'actual_contexts': 16064,
                       'boundaries': 12031,
                       'boundary_memberships': 23720,
                       'cells': 4033,
                       'decoded_observations': 31672,
                       'decoder_order_pairs': 62912,
                       'empty_active_cases': 4542,
                       'families': 1333,
                       'interval_cases': 7998,
                       'pair_cell_checks': 277,
                       'whole_cell_memberships': 7952,
                       'winner_ids': 7236},
 'test_controls_v23': {'changed_family_controls': 2,
                       'fractional_named_diagrams': 5,
                       'integer_field_boundaries': 1,
                       'invariance_comparisons': 10,
                       'nonlinear_controls': 1,
                       'old_empty_exceptions': 4,
                       'original_scalar_fixture_parameters': 3,
                       'original_tied_history_ids': 3,
                       'parameter_decoders': 2},
 'test_coverage_v23': {'coverage_guard_rejections': 225},
 'test_custody_v23': {'inherited_custody_rejections': 13,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_diagrams_v23': {'boundaries': 8194,
                       'boundary_memberships': 23630,
                       'cells': 3274,
                       'empty_cases': 6,
                       'interval_cases': 4920,
                       'legacy_function_calls': 50174,
                       'legacy_interval_cases': 4914,
                       'pair_cell_checks': 9178,
                       'rosters': 820,
                       'whole_cell_memberships': 9482},
 'test_hostiles_v23': {'codec_mutation_rejections': 13,
                       'diagram_mutation_rejections': 23,
                       'malformed_input_rejections': 154,
                       'valid_codec_certificates': 1,
                       'valid_diagram_certificates': 1},
 'test_kernel_guard_v23': {'kernel_registration_rejections': 4}}

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
