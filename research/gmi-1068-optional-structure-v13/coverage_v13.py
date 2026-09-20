"""Exact mandatory evidence counts for optional-structure adjudication."""
REQUIRED = {
    "test_optional_v13": {
        "actual_associativity_equations": 27, "actual_commutation_checks": 9,
        "actual_compositions": 9, "actual_failed_candidates": 81,
        "actual_inverse_pair_checks": 9, "actual_unit_equations": 6,
        "associative_operations": 113, "binary_operations": 19683,
        "common_unit_operations": 81, "complete_obstruction_certificates": 1,
        "composition_associativity_equations": 27, "empty_braiding_hom_sets": 2,
        "incompatible_composition_rejections": 30, "interchange_equations": 6561,
        "positive_c2_interchange_equations": 16, "relabeled_candidates": 486,
        "tensor_associativity_equations": 243, "tensor_identity_equations": 18,
        "typed_compositions": 15, "typed_hom_sets": 18,
        "typed_interchange_equations": 153, "typed_tensors": 45, "typed_unit_equations": 36,
    },
    "test_hostiles_v13": {
        "actual_naturality_failure_controls": 1, "actual_unitor_naturality_equations": 16,
        "malformed_input_rejections": 65, "obstruction_certificate_rejections": 12,
        "one_sided_inverse_controls": 1, "weak_unitor_necessity_checks": 734,
    },
    "test_kernel_guard_v13": {"kernel_registration_rejections": 3},
    "test_coverage_v13": {"coverage_guard_rejections": 164},
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
