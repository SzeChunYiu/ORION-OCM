def _no_floats(obj: object) -> bool:
    if isinstance(obj, float):
        return False
    if isinstance(obj, dict):
        return all(_no_floats(k) and _no_floats(v) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return all(_no_floats(x) for x in obj)
    return True


def build_receipt() -> Dict[str, object]:
    census = registered_census()
    remint = remint_exhaustive_certificate()
    ga, gb = nonisometric_hostile_pair()
    pair = {
        "semantic_images_equal": set(ga.semantic.values()) == set(gb.semantic.values()),
        "selection_GA": selection(ga, ("A", "B")),
        "selection_GB": selection(gb, ("A", "B")),
        "GA_bias": grammar_bias_rows(ga),
        "GB_bias": grammar_bias_rows(gb),
        "isometric_certification": certify_isometric_remint(ga, gb, {"root": "root2", "a": "a2", "b": "b2"})[1],
    }
    hostile = hostile_remint_results()
    all_green = (
        census["presentation_count"] == 126
        and census["semantic_class_count"] == 18
        and census["undirected_edge_count"] == 1275
        and census["bfs_wave_mismatches"] == 0
        and census["all_presentations_reachable"]
        and remint["certified"] == 24
        and remint["invariant_failures"] == 0
        and pair["selection_GA"] == "A"
        and pair["selection_GB"] == "B"
        and pair["isometric_certification"] == "DESCRIPTION_LENGTH_CORRUPTION"
        and set(hostile.values()) == {
            "NON_BIJECTIVE_NODE_MAP",
            "SEMANTIC_MAP_CORRUPTION",
            "DESCRIPTION_LENGTH_CORRUPTION",
            "EDGE_CORRUPTION",
            "START_SET_CORRUPTION",
        }
    )
    receipt = {
        "schema": "GMI833G0GrammarBiasReceiptV1",
        "parent_issue": 833,
        "issue": 875,
        "source_main": SOURCE_MAIN,
        "freeze_commit": FREEZE_COMMIT,
        "parent_authority": {
            "issue": 868,
            "manifest_blob": PARENT_MANIFEST_BLOB,
            "receipt_blob": PARENT_RECEIPT_BLOB,
        },
        "registered_slice": {k:v for k,v in census.items() if k != "class_rows"},
        "isometric_remint_certificate": remint,
        "nonisometric_same_semantics_hostile": pair,
        "remint_hostiles": hostile,
        "kolmogorov_boundary": "ADDITIVE_CONSTANT_INVARIANCE_DOES_NOT_IMPLY_FINITE_LENGTH_MASS_OR_REACHABILITY_EQUALITY",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "terminal": "GMI_833_G0_GRAMMAR_BIAS_V1_ALL_GREEN" if all_green else "RED",
    }
    if not _no_floats(receipt):
        raise RuntimeError("floating-point evidence forbidden")
    return receipt
