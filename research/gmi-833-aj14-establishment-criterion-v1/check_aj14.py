from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

BADGES = [
    "GMI_CORE_FORMALIZED_AT_SCOPE",
    "GMI_BOUNDED_ATLAS_COMPLETE_AT_SCOPE",
    "GMI_KNOWN_FAMILIES_BLINDLY_RECOVERED_AT_SCOPE",
    "GMI_SELECTION_LAWS_PROSPECTIVELY_VALIDATED_AT_SCOPE",
    "GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE",
    "FULL_GMI_THEORY_SUPPORTED_AT_DECLARED_SCOPE",
]

EVIDENCE = {
    "FOUNDATION": {"status":"SATISFIED_REGISTERED_SCOPE", "parents":["AJ1","AJ5","AJ12","AJ13"]},
    "GENERATION": {"status":"SATISFIED_REGISTERED_SCOPE", "parents":["AJ4","AJ5"]},
    "DEVELOPMENT": {"status":"SATISFIED_REGISTERED_SCOPE", "parents":["AJ6","HSG"]},
    "RELEVANCE_CAPABILITY": {"status":"SATISFIED_REGISTERED_SCOPE", "parents":["AJ3","AJ8","GMI_CAPABILITY_PARENT"]},
    "SELECTION": {"status":"PROSPECTIVE_FINITE_SYNTHETIC_SCOPE", "parents":["PR902"], "real_system_gate":"OPEN_ISSUE_903"},
    "RECOVERY": {"status":"ALL_11_REGISTERED_FAMILIES_RECOVERED_FINITE_TASK_BASIS_SCOPE", "parents":["PR951"], "historical_ignorance":"NOT_CLAIMED"},
    "DISCOVERY": {"status":"UNKNOWN_CHANNEL_EXERCISED_PARENT_REDUCED_NO_NOVEL_FORM", "parents":["AJ10"], "novel_replication":"NOT_TRIGGERED"},
    "BOUNDARIES": {"status":"EXPLICIT", "parents":["AJ11","AJ12","HSG"]},
    "EVIDENCE": {"status":"BOUNDED_HOSTILE_AND_SYNTHETIC_PROSPECTIVE_GREEN_REAL_SYSTEM_OPEN", "real_system_gate":"ISSUE_903_OPEN_ZERO_QUALIFYING_CLAIM"},
}

FORBIDDEN = [
    "ALL_PHYSICALLY_POSSIBLE_INTELLIGENCES_KNOWN",
    "UNIQUE_ABSOLUTE_MATHEMATICAL_FOUNDATION",
    "UNIVERSAL_BEST_INTELLIGENCE",
    "ALL_FUTURE_MI_FORMS_ENUMERATED",
    "ALL_SEMANTIC_PROPERTIES_DECIDABLE",
    "OBJECTIVES_DERIVED_FROM_PHYSICS_ALONE",
    "COMPLETE_GMI_IN_ALL_CONCEIVABLE_PHYSICS",
]

def earned_badges(e=EVIDENCE):
    earned=[]
    if all(e[k]["status"].startswith("SATISFIED") or k in {"BOUNDARIES"} for k in ["FOUNDATION","GENERATION","DEVELOPMENT","RELEVANCE_CAPABILITY","BOUNDARIES"]):
        earned.append(BADGES[0])
    if earned and e["BOUNDARIES"]["status"]=="EXPLICIT":
        earned.append(BADGES[1])
    if BADGES[1] in earned and e["RECOVERY"]["status"].startswith("ALL_11_REGISTERED_FAMILIES_RECOVERED"):
        earned.append(BADGES[2])
    if BADGES[2] in earned and e["SELECTION"]["status"]=="PROSPECTIVE_FINITE_SYNTHETIC_SCOPE":
        earned.append(BADGES[3])
    if e["DISCOVERY"].get("novel_replication")=="REPLICATED":
        earned.append(BADGES[4])
    if BADGES[4] in earned and e["EVIDENCE"].get("real_system_gate")=="SATISFIED":
        earned.append(BADGES[5])
    return earned

def audit_no_promotion(earned):
    assert BADGES[5] not in earned
    assert BADGES[4] not in earned
    assert EVIDENCE["EVIDENCE"]["real_system_gate"] != "SATISFIED"
    assert EVIDENCE["DISCOVERY"]["novel_replication"] != "REPLICATED"

def main():
    earned=earned_badges()
    audit_no_promotion(earned)
    assert earned==BADGES[:4]
    result={
        "status":"GREEN",
        "establishment_dimensions":EVIDENCE,
        "earned_badges":earned,
        "unearned_badges":[b for b in BADGES if b not in earned],
        "current_scientific_terminal":"GMI_CORE_PLUS_BOUNDED_ATLAS_PLUS_REGISTERED_BLIND_RECOVERY_PLUS_FINITE_PROSPECTIVE_SELECTION_SUPPORTED__NOVEL_REPLICATION_AND_REAL_SYSTEM_VALIDATION_OPEN",
        "full_gmi_supported_now":False,
        "blocking_gates":["GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE","ISSUE_903_REAL_SYSTEM_VALIDATION"],
        "forbidden_implications":FORBIDDEN,
        "claim_ceiling":"AJ14_SCOPED_FULL_GMI_ESTABLISHMENT_LADDER_MACHINE_CHECKED_CURRENTLY_PARTIAL",
    }
    (HERE/"RESULT_V1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
