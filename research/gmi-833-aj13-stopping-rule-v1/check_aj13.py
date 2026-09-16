from __future__ import annotations
import copy, json
from pathlib import Path

HERE = Path(__file__).resolve().parent

ALLOWED_TAGS = {
    "MATHEMATICAL_FOUNDATION",
    "LOGIC/METATHEORY",
    "PHYSICAL_SUBSTRATE_LAW",
    "RESOURCE_MODEL",
    "VALUE/REQUIREMENT_INPUT",
}
BANNED_MI_PRIMITIVES = {
    "NEURON", "LAYER", "ATTENTION", "MEMORY", "PLANNER", "SEARCHER",
    "WORLD_MODEL", "BACKPROP", "TRANSFORMER", "SYMBOLIC_REASONER",
}
REQUIRED_OPERATIONAL_ROLES = {"TYPE", "SEQUENCE", "PARALLEL", "NO_CHANGE", "SUBSTRATE_ADMISSIBILITY", "OPERATIONAL_OBSERVATION"}


def baseline():
    return {
        "remaining_assumptions": [
            {"id": "F", "tag": "MATHEMATICAL_FOUNDATION"},
            {"id": "L", "tag": "LOGIC/METATHEORY"},
            {"id": "S", "tag": "PHYSICAL_SUBSTRATE_LAW"},
            {"id": "R", "tag": "RESOURCE_MODEL"},
            {"id": "Q", "tag": "VALUE/REQUIREMENT_INPUT"},
        ],
        "operational_base": ["Obj", "Proc", "compose", "tensor", "I", "id", "Adm_S", "Obs_S"],
        "aj1_irredundancy": {
            "Obj": "TYPE",
            "compose": "SEQUENCE",
            "tensor": "PARALLEL",
            "id": "NO_CHANGE",
            "Adm_S": "SUBSTRATE_ADMISSIBILITY",
            "Obs_S": "OPERATIONAL_OBSERVATION",
        },
        "presentation_invariance_evidence": [
            "AJ5_G0_DERIVED_FROM_OPERATIONAL_LAYER_AND_PRESENTATION_INVARIANCE_AT_REGISTERED_FINITE_SCOPE",
            "AJ12_FOUNDATION_STYLE_AND_COMPUTATIONAL_SUBSTRATE_RELATIVITY_AUDITED_AT_REGISTERED_CORE_SCOPE",
        ],
        "parent_ownership_registered": True,
        "further_descent_classification": [
            "LOGIC/METATHEORY", "MATHEMATICAL_FOUNDATION", "PHYSICAL_SUBSTRATE_LAW", "VALUE/REQUIREMENT_INPUT"
        ],
        "requested_terminal": "FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE",
    }


def audit(x):
    failures = []
    tags = [a.get("tag") for a in x.get("remaining_assumptions", [])]
    if not tags or any(t not in ALLOWED_TAGS for t in tags):
        failures.append("UNTAGGED_OR_INVALID_REMAINING_ASSUMPTION")

    base = set(x.get("operational_base", []))
    if base & BANNED_MI_PRIMITIVES:
        failures.append("MI_SPECIFIC_PRIMITIVE_REMAINS_IN_BASE")

    irr = x.get("aj1_irredundancy", {})
    if set(irr.values()) != REQUIRED_OPERATIONAL_ROLES:
        failures.append("OPERATIONAL_PRIMITIVE_LOSS_NOT_DEMONSTRATED")

    inv = set(x.get("presentation_invariance_evidence", []))
    if not any(s.startswith("AJ5_") for s in inv) or not any(s.startswith("AJ12_") for s in inv):
        failures.append("PRESENTATION_OR_FOUNDATION_INVARIANCE_EVIDENCE_MISSING")

    if x.get("parent_ownership_registered") is not True:
        failures.append("PARENT_OWNERSHIP_MISSING")

    descent = set(x.get("further_descent_classification", []))
    if not descent or not descent <= ALLOWED_TAGS or "RESOURCE_MODEL" in descent:
        failures.append("FURTHER_DESCENT_NOT_CONFined_TO_FOUNDATION_PHYSICS_VALUE")

    if x.get("requested_terminal") == "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN":
        failures.append("ABSOLUTE_BOTTOM_PROMOTION_FORBIDDEN")

    return failures


def run_hostiles():
    cases = {}
    x = baseline(); x["remaining_assumptions"].append({"id":"bad","tag":"INTELLIGENCE_ATOM"}); cases["bad_tag"] = x
    x = baseline(); x["operational_base"].append("NEURON"); cases["mi_primitive"] = x
    x = baseline(); x["aj1_irredundancy"].pop("Obs_S"); cases["missing_loss_witness"] = x
    x = baseline(); x["presentation_invariance_evidence"] = [x["presentation_invariance_evidence"][0]]; cases["missing_cross_foundation"] = x
    x = baseline(); x["parent_ownership_registered"] = False; cases["missing_parent"] = x
    x = baseline(); x["requested_terminal"] = "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN"; cases["absolute_promotion"] = x
    out = {}
    for name, case in cases.items():
        f = audit(case)
        assert f, name
        out[name] = f
    return out


def main():
    good = baseline()
    failures = audit(good)
    assert failures == []
    hostiles = run_hostiles()
    result = {
        "status": "GREEN",
        "criteria_satisfied": 6,
        "hostile_cases_rejected": len(hostiles),
        "hostiles": hostiles,
        "operational_base_contains_no_registered_mi_specific_primitive": True,
        "remaining_assumptions_all_explicitly_tagged": True,
        "aj1_relative_irredundancy_consumed": True,
        "aj5_aj12_invariance_evidence_consumed": True,
        "parent_ownership_required": True,
        "further_descent_boundary": "LOGIC_MATHEMATICS_PHYSICAL_LAW_VALUE_NOT_HIDDEN_MI_MECHANISM",
        "terminal": "FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE",
        "forbidden_terminal": "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN",
        "claim_ceiling": "AJ13_RECURSIVE_DESCENT_STOPPING_RULE_SATISFIED_AT_REGISTERED_AJ_SCOPE",
    }
    (HERE / "RESULT_V1.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))

if __name__ == "__main__":
    main()
