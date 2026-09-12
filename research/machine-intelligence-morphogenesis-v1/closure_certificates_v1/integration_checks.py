"""Additional actual-repository assertions, separate from local standalone tests."""
from dataclasses import replace
import json

from legacy_class_bound import load_pinned_model, target_class_bound, compare_rival
from claim_audit import run_development_cell


def main():
    rn, engine, phase = load_pinned_model()
    import gmi_k4_null_frontier_v5 as nulls
    grammar = "G1_TENSOR_GRAPH"
    inert = nulls.null_candidates(grammar)["NULL_FIXED_NUMERIC"]
    target = inert.vector()
    bound = target_class_bound(target, grammar=grammar, task="linear", scale=8, seed=17)
    profile = phase.world_profile(17, "linear", 8)
    inert_cost = sum(float(v) for v in nulls.null_cost(inert, 8, profile).values())
    assert bound["matching_nulls_admissible"] >= 1
    assert bound["target_minimum"] <= inert_cost
    # A registered null is also a potential target-class member, not just a rival.
    comparison = compare_rival(inert, target, task="linear", scale=8, seed=17,
                               registered_null_id="NULL_FIXED_NUMERIC")
    assert comparison["verdict"] == "RIVAL_IS_TARGET_CLASS_MEMBER"
    forged = replace(inert, cap_atoms=("affine", "low_rank_revision"))
    try:
        compare_rival(forged, target, task="linear", scale=8, seed=17,
                      registered_null_id="NULL_FIXED_NUMERIC")
    except ValueError:
        pass
    else:
        raise AssertionError("forged null discount accepted")
    # Exercise the public wrapper from this subdirectory, without PYTHONPATH setup.
    empty = run_development_cell("missing", grammar, "w1", freeze={}, seed=17, budget=0)
    assert empty["legacy_verdict"] == "INCONCLUSIVE_GRAMMAR"
    assert empty["full_GMI_closure"] is False
    print(json.dumps({"null_membership_bound": bound,
                      "forged_null_discount_rejected": True,
                      "development_wrapper_executed": True,
                      "protected_evidence": False}, indent=2))


if __name__ == "__main__":
    main()
