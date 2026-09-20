"""Exact required governance controls, measured on real frozen evidence."""
REQUIRED = {'test_custody_v16': {'publication_positive_controls': 3,
                      'published_rewrite_rejections': 2,
                      'repository_custody_rejections': 6,
                      'unavailable_custody_controls': 3,
                      'unavailable_publication_base_controls': 1,
                      'valid_repository_custody_controls': 1},
 'test_evidence_v16': {'attestation_mutation_rejections': 14,
                       'coupled_evidence_rejections': 2,
                       'dependency_authority_controls': 3,
                       'successor_authority_controls': 5,
                       'valid_evidence_controls': 4},
 'test_guard_v16': {'coverage_guard_rejections': 84},
 'test_structure_v16': {'revision_graph_rejections': 5,
                        'structure_mutation_rejections': 44,
                        'valid_structure_controls': 5}}

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
