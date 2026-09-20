"""Exact measured permission-gating and intervention calibration."""
REQUIRED = {'test_contexts_v22': {'context_instances': 1463,
                       'enabled_images': 22892,
                       'nested_images': 51507,
                       'observation_checks': 45280,
                       'relative_analyses': 146776,
                       'selectors': 5723,
                       'target_incidence': 73388,
                       'witness_ids': 9040},
 'test_controls_v22': {'branch_trace_checks': 124,
                       'family_boundary_replays': 1,
                       'history_roster_entries': 3,
                       'nonmonotone_context_models': 8,
                       'original_fixture_replays': 1,
                       'original_history_witnesses': 3},
 'test_coverage_v22': {'coverage_guard_rejections': 192},
 'test_custody_v22': {'inherited_custody_rejections': 11,
                      'source_path_escape_rejections': 5,
                      'unavailable_inherited_controls': 5,
                      'valid_inherited_custody_controls': 1},
 'test_execution_v22': {'executions': 3240,
                        'failed_traces': 1482,
                        'successful_traces': 1758,
                        'tables': 81,
                        'word_cuts': 9720},
 'test_families_v22': {'addition_candidates': 16658,
                       'deletion_candidates': 7070,
                       'enabled_cases': 2122,
                       'families': 278,
                       'minimal_addition_sets': 6645,
                       'minimal_blocker_sets': 1152,
                       'private_member_probes': 7012,
                       'relabel_cases': 2122},
 'test_hostiles_v22': {'corrupt_private_certificates': 5, 'malformed_rejections': 223},
 'test_kernel_guard_v22': {'kernel_registration_rejections': 4}}

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
