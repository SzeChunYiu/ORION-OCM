"""Exact mandatory context-specialization calibration counts."""
REQUIRED = {
    'test_maps_v17': {
        'ambient_transport_controls': 1,
        'dual_comparison_equations': 1496,
        'dual_contexts': 802,
        'empty_active_nonmonotone_rejections': 1,
        'injective_maps': 5905,
        'map_candidates': 24907,
        'map_composition_equations': 880,
        'map_malformed_rejections': 12,
        'missing_reflection_controls': 2,
        'monotone_maps': 11345,
        'reflecting_maps': 3275,
        'transport_comparisons': 521184,
        'transport_contexts': 274658,
        'transport_observations': 549316,
        'unrestricted_map_reversal_controls': 1,
    },
    'test_products_v17': {
        'empty_independent_family_controls': 8,
        'empty_shared_family_controls': 64,
        'independent_product_cases': 5832,
        'joint_comparisons': 5616,
        'joint_observations': 17496,
        'product_malformed_rejections': 15,
        'projection_equations': 7776,
        'shared_domain_products': 1000,
        'unequal_shared_domain_rejections': 4832,
    },
    'test_specializations_v17': {
        'acceptance_contexts': 64,
        'acceptance_embedding_comparisons': 192,
        'ambient_specialization_controls': 4,
        'confidence_contexts': 81,
        'cost_contexts': 121,
        'cost_orientation_controls': 1,
        'incomparability_controls': 2,
        'semantic_comparisons': 1631,
        'specialization_contexts': 512,
        'specialization_malformed_rejections': 28,
        'specialization_observations': 1213,
        'utility_contexts': 125,
        'vector_contexts': 121,
        'zero_vector_domain_controls': 1,
    },
    'test_viability_v17': {
        'actual_viability_contexts': 4165,
        'deadend_controls': 1,
        'existential_adversarial_controls': 1,
        'safe_subset_candidates': 13975,
        'state_memberships': 12420,
        'strict_deletion_steps': 1887,
        'unsafe_path_controls': 1,
        'viability_cases': 4165,
        'viability_malformed_rejections': 15,
        'viability_observation_controls': 1,
    },
    'test_custody_v17': {
        'inherited_custody_rejections': 7,
        'source_path_escape_rejections': 5,
        'unavailable_inherited_controls': 4,
        'valid_inherited_custody_controls': 1,
    },
    'test_kernel_guard_v17': {
        'kernel_registration_rejections': 3,
    },
    'test_coverage_v17': {
        'coverage_guard_rejections': 285,
    },
}


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
