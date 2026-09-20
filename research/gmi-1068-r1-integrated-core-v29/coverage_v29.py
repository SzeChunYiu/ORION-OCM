"""Exact registered V29 module and measured calibration inventory."""
REQUIRED = {'test_controls_v29': {'named_structural_controls': 12},
 'test_coverage_v29': {'coverage_guard_rejections': 199},
 'test_custody_v29': {'inherited_custody_rejections': 17,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 9,
                      'valid_inherited_custody_controls': 1},
 'test_hostiles_v29': {'foreign_nested_certificate_rejections': 8,
                       'malformed_input_rejections': 121,
                       'semantic_certificate_rejections': 53,
                       'valid_certificate_baselines': 3},
 'test_information_v29': {'constructed_families': 90,
                          'full_target_decisions': 180,
                          'information_boundary_controls': 10,
                          'recoverable_full_reports': 102,
                          'recoverable_restricted_reports': 102,
                          'recoverable_source_reports': 102,
                          'source_and_restricted_decisions': 360,
                          'transport_reports': 180},
 'test_kernel_guard_v29': {'kernel_registration_rejections': 4},
 'test_named_v29': {'absent_guard_cases': 56,
                    'availability_controls': 4,
                    'failed_named_queries': 105,
                    'inclusion_comparisons': 40,
                    'named_parent_evaluations': 328,
                    'named_queries': 164,
                    'successful_named_queries': 59,
                    'typed_parent_evaluations': 216,
                    'typed_queries': 108},
 'test_presentation_v29': {'inverse_arrow_equations': 12,
                           'path_evaluations': 7,
                           'path_pairs': 49,
                           'quotient_products': 36,
                           'valid_presentation_certificates': 1},
 'test_rollup_ledger_v29': {'crosswalk_mutation_rejections': 791,
                            'inherited_ledger_mutation_rejections': 259,
                            'valid_rollup_ledgers': 4}}

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
