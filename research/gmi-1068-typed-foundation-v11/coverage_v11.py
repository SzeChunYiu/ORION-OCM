"""Mandatory measured corpus and hostile controls for original-atom closure."""
REQUIRED = {
 "test_paths_v11": {
  "dag_graphs":729, "complete_paths":10935, "unit_equations":21870,
  "legal_compositions":23328, "legal_triples":40824, "incompatible_compositions":172179,
  "concrete_interpretations":10935, "extensional_quotients":729, "renamed_graphs":729,
  "admission_subsets":117649, "path_admission_checks":2782416,
  "admitted_composition_checks":2370816, "admitted_identity_checks":470596,
  "binary_operation_tables":16, "associative_tables":8, "lawful_monoids":4,
  "monoid_word_interpretations":508,
 },
 "test_path_hostiles_v11": {
  "long_cyclic_paths":3, "structural_path_mutations":5, "cyclic_enumeration_rejections":4,
  "admission_cutoff_and_lift":1, "interpretation_boundary_cases":18,
  "quotient_rejections":10, "malformed_input_rejections":45,
 },
 "test_context_v11": {
  "typed_histories":182, "evaluator_disagreements":156, "identity_only_histories":26,
  "padded_ranking_reversals":36, "full_process_comparisons":1,
  "path_admission_comparisons":182, "v9_evaluation_comparisons":364,
  "composition_cells":16, "context_semantic_rejections":20, "context_custody_controls":2,
 },
 "test_kernel_guard_v11": {"kernel_registration_rejections":3},
 "test_coverage_v11": {"coverage_guard_rejections":150},
}


def validate_coverage(coverage):
    if not isinstance(coverage, dict) or set(coverage) != set(REQUIRED):
        raise ValueError("missing or unexpected mandatory experiment")
    for module, required in REQUIRED.items():
        if not isinstance(coverage[module], dict):
            raise ValueError("missing coverage mapping")
        for key, value in required.items():
            actual = coverage[module].get(key)
            if type(actual) is not int or actual != value:
                raise ValueError("required check not executed: " + module + "/" + key)
    return True
