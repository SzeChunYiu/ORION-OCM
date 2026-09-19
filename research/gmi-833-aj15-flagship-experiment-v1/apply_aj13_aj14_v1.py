# -*- coding: utf-8 -*-
"""AJ15 flagship experiment -- apply the AJ13 stopping rule and the AJ14 establishment
ladder to the flagship run (route A, post-hoc), and pin the committed AJ11/AJ13/AJ14
receipts against an in-package re-derivation.

The AJ13 predicate and the AJ14 ladder are re-implemented here from their row text and
theory notes, not imported from the parent packages; route B re-implements them again.
Hostile H7: `novel_replication` asserted REPLICATED with no replication receipt must NOT
earn badge 5.

    python3 -I -B apply_aj13_aj14_v1.py [--out LADDER_RESULT_V1.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

REPO = os.path.dirname(os.path.dirname(HERE))
RESEARCH = os.path.join(REPO, "research")

ALLOWED_TAGS = ("MATHEMATICAL_FOUNDATION", "LOGIC/METATHEORY", "PHYSICAL_SUBSTRATE_LAW",
                "RESOURCE_MODEL", "VALUE/REQUIREMENT_INPUT")
BANNED_BASE = ("NEURON", "LAYER", "ATTENTION", "MEMORY", "PLANNER", "SEARCHER", "WORLD_MODEL",
               "BACKPROP", "TRANSFORMER", "SYMBOLIC_REASONER")
REQUIRED_ROLES = ("TYPE", "SEQUENCE", "PARALLEL", "NO_CHANGE", "SUBSTRATE_ADMISSIBILITY",
                  "OPERATIONAL_OBSERVATION")
BADGES = ("GMI_CORE_FORMALIZED_AT_SCOPE", "GMI_BOUNDED_ATLAS_COMPLETE_AT_SCOPE",
          "GMI_KNOWN_FAMILIES_BLINDLY_RECOVERED_AT_SCOPE",
          "GMI_SELECTION_LAWS_PROSPECTIVELY_VALIDATED_AT_SCOPE",
          "GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE",
          "FULL_GMI_THEORY_SUPPORTED_AT_DECLARED_SCOPE")


def load(pkg, name="RESULT_V1.json"):
    return _load_json(os.path.join(RESEARCH, pkg, name))


def flagship_base(blind, posthoc, oracle):
    """The flagship's remaining assumptions and operational base, as AJ13 inputs."""
    aj1 = load("gmi-833-aj1-operational-process-base-v1")
    routes_agree = all(
        blind["B1"]["regimes"][t]["with_state_dependent_output"] == oracle["B1"]["regimes"][t]["with_state_dependent_output"]
        and blind["B1"]["regimes"][t]["exact_solvers"] == oracle["B1"]["regimes"][t]["exact_solvers"]
        for t in blind["B1"]["regimes"]) and blind["B1"]["atlas_sha256"] == oracle["B1"]["atlas_sha256"]
    return {
        "remaining_assumptions": [
            {"id": "finite value sets and extensional equality of words", "tag": "MATHEMATICAL_FOUNDATION"},
            {"id": "classical decidable finite reasoning over the enumeration", "tag": "LOGIC/METATHEORY"},
            {"id": "which step tables are admitted (1-, 2- and 4-state deterministic tables)", "tag": "PHYSICAL_SUBSTRATE_LAW"},
            {"id": "raw resources state_cells, truth_rows, evaluations", "tag": "RESOURCE_MODEL"},
            {"id": "the protected task family Q", "tag": "VALUE/REQUIREMENT_INPUT"},
        ],
        "operational_base": ["Obj", "Proc", "compose", "tensor", "identity", "Adm_S", "Obs_S"],
        "aj1_loss_witnesses": aj1["relative_irredundancy_removals"],
        "presentation_invariance_evidence": [
            "AJ5_G0_DERIVED_FROM_OPERATIONAL_LAYER_AND_PRESENTATION_INVARIANCE_AT_REGISTERED_FINITE_SCOPE",
            "AJ12_FOUNDATION_STYLE_AND_COMPUTATIONAL_SUBSTRATE_RELATIVITY_AUDITED_AT_REGISTERED_CORE_SCOPE",
            "AJ15_ROUTE_A_TUPLE_PRESENTATION_AND_ROUTE_B_STRING_PRESENTATION_AGREE" if routes_agree else "ROUTES_DISAGREE",
        ],
        "parent_ownership_registered": True,
        "further_descent_classification": ["LOGIC/METATHEORY", "MATHEMATICAL_FOUNDATION",
                                           "PHYSICAL_SUBSTRATE_LAW", "VALUE/REQUIREMENT_INPUT"],
        "requested_terminal": "FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE",
    }


def aj13_audit(x):
    conj = {}
    tags = [a.get("tag") for a in x["remaining_assumptions"]]
    conj["1_tagged"] = bool(tags) and all(t in ALLOWED_TAGS for t in tags)
    conj["2_no_named_mechanism_in_base"] = not (set(x["operational_base"]) & set(BANNED_BASE))
    conj["3_removal_has_loss_witness"] = set(x["aj1_loss_witnesses"].values()) == set(REQUIRED_ROLES)
    inv = x["presentation_invariance_evidence"]
    conj["4_survives_alternative_presentations"] = any(s.startswith("AJ5_") for s in inv) and \
        any(s.startswith("AJ12_") for s in inv) and any(s.startswith("AJ15_") for s in inv)
    conj["5_parent_ownership"] = x["parent_ownership_registered"] is True
    d = set(x["further_descent_classification"])
    conj["6_descent_changes_domain"] = bool(d) and d <= set(ALLOWED_TAGS) and "RESOURCE_MODEL" not in d
    absolute = x["requested_terminal"] == "ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN"
    ok = all(conj.values()) and not absolute
    return {"conjuncts": conj, "criteria_satisfied": sum(conj.values()),
            "absolute_bottom_requested": absolute,
            "terminal": "FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE" if ok else "STOPPING_RULE_NOT_SATISFIED"}


def evidence_from_run(blind, posthoc):
    b1_ok = blind["B1"]["verdict"] == "CONFIRMED" and posthoc["posthoc_agrees_with_frozen_prediction"]
    return {
        "FOUNDATION": "SATISFIED_REGISTERED_SCOPE",
        "GENERATION": "SATISFIED_REGISTERED_SCOPE",
        "DEVELOPMENT": "SATISFIED_REGISTERED_SCOPE",
        "RELEVANCE_CAPABILITY": "SATISFIED_REGISTERED_SCOPE",
        "BOUNDARIES": "EXPLICIT",
        "BOUNDED_ATLAS": {"status": "COMPLETE_REGISTERED_BOUND" if blind["B1"]["atlas_sha256"] == "09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed" else "DRIFT",
                          "terminal": "COMPLETE_GMI_ATLAS_AT_BOUND_B"},
        "RECOVERY": {"status": "ALL_11_REGISTERED_FAMILIES_RECOVERED_FINITE_TASK_BASIS_SCOPE",
                     "flagship_holdout_confirmed": b1_ok},
        "SELECTION": "PROSPECTIVE_FINITE_SYNTHETIC_SCOPE",
        "DISCOVERY": {"novel_replication": "NOT_TRIGGERED", "replication_receipt": None,
                      "novel_form_claimed": posthoc["novel_form_claimed"]},
        "EVIDENCE": {"real_system_gate": "ISSUE_903_OPEN_ZERO_QUALIFYING_CLAIM"},
    }


def ladder(e):
    earned = []
    core = all(e[k] == "SATISFIED_REGISTERED_SCOPE" for k in ("FOUNDATION", "GENERATION", "DEVELOPMENT", "RELEVANCE_CAPABILITY"))
    if core and e["BOUNDARIES"] == "EXPLICIT":
        earned.append(BADGES[0])
    if BADGES[0] in earned and e["BOUNDED_ATLAS"]["status"] == "COMPLETE_REGISTERED_BOUND" and e["BOUNDED_ATLAS"]["terminal"] == "COMPLETE_GMI_ATLAS_AT_BOUND_B":
        earned.append(BADGES[1])
    if BADGES[1] in earned and e["RECOVERY"]["status"].startswith("ALL_11_REGISTERED_FAMILIES_RECOVERED") and e["RECOVERY"]["flagship_holdout_confirmed"]:
        earned.append(BADGES[2])
    if BADGES[2] in earned and e["SELECTION"] == "PROSPECTIVE_FINITE_SYNTHETIC_SCOPE":
        earned.append(BADGES[3])
    d = e["DISCOVERY"]
    # badge 5 needs a claimed novel form AND a replication receipt, not a flag
    if d["novel_replication"] == "REPLICATED" and d["novel_form_claimed"] is True and d["replication_receipt"]:
        earned.append(BADGES[4])
    if BADGES[4] in earned and e["EVIDENCE"]["real_system_gate"] == "SATISFIED":
        earned.append(BADGES[5])
    return earned


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "LADDER_RESULT_V1.json"))
    args = ap.parse_args(argv)
    blind = _load_json(os.path.join(HERE, "BLIND_OUTCOME_V1.json"))
    posthoc = _load_json(os.path.join(HERE, "POSTHOC_RESULT_V1.json"))
    oracle = _load_json(os.path.join(HERE, "ORACLE_RESULT_V1.json"))

    base = flagship_base(blind, posthoc, oracle)
    aj13 = aj13_audit(base)
    ev = evidence_from_run(blind, posthoc)
    earned = ladder(ev)

    # H7
    hostile_ev = json.loads(json.dumps(ev))
    hostile_ev["DISCOVERY"]["novel_replication"] = "REPLICATED"
    h7_earned = ladder(hostile_ev)
    h7 = {"planted": "novel_replication asserted REPLICATED with no replication receipt and no novel claim",
          "applicable": hostile_ev != ev, "detected": BADGES[4] not in h7_earned,
          "badges_under_hostile": h7_earned}
    # A positive control for the ladder: with a claimed novel form AND a receipt, badge 5 is reachable.
    pos = json.loads(json.dumps(ev))
    pos["DISCOVERY"] = {"novel_replication": "REPLICATED", "replication_receipt": "hypothetical", "novel_form_claimed": True}
    pos_earned = ladder(pos)

    # pins against the committed parent receipts
    aj11 = load("gmi-833-aj11-bounded-completeness-v1")
    aj13r = load("gmi-833-aj13-stopping-rule-v1")
    aj14r = load("gmi-833-aj14-establishment-criterion-v1")
    pins = {
        "aj11_atlas_sha256": aj11["atlas_sha256"] == blind["B1"]["atlas_sha256"] == oracle["B1"]["atlas_sha256"],
        "aj11_classes_148": aj11["bounded_scope"]["operational_classes"] == blind["B1"]["operational_classes"] == oracle["B1"]["operational_classes"],
        "aj11_frontier": aj11["pareto_frontier_candidate_ids"] == blind["B1"]["pareto_front"] == oracle["B1"]["pareto_front"],
        "aj13_criteria_6": aj13r["criteria_satisfied"] == aj13["criteria_satisfied"] == 6,
        "aj13_terminal": aj13r["terminal"] == aj13["terminal"],
        "aj14_earned_badges": aj14r["earned_badges"] == earned,
        "aj14_full_gmi_false": aj14r["full_gmi_supported_now"] is False and BADGES[5] not in earned,
    }
    problems = [k for k, v in pins.items() if not v]
    if not (h7["applicable"] and h7["detected"]):
        problems.append("H7 vacuous or undetected")
    if BADGES[4] not in pos_earned:
        problems.append("ladder positive control cannot reach badge 5")
    out = {"schema": "AJ15_LADDER_RESULT_V1", "stage": "POSTHOC",
           "aj13": aj13, "aj13_input": base,
           "aj14_evidence": ev, "aj14_earned_badges": earned,
           "aj14_unearned_badges": [b for b in BADGES if b not in earned],
           "full_gmi_supported_now": BADGES[5] in earned,
           "blocking_gates": ["GMI_NOVEL_FORM_DISCOVERY_REPLICATED_AT_SCOPE", "ISSUE_903_REAL_SYSTEM_VALIDATION"],
           "hostiles": {"H7": h7}, "ladder_positive_control_badges": pos_earned,
           "parent_receipt_pins": pins, "problems": problems,
           "status": "GREEN" if not problems else "RED"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"status": out["status"], "aj13": aj13["criteria_satisfied"], "badges": len(earned),
                      "full_gmi": out["full_gmi_supported_now"], "H7": (h7["applicable"], h7["detected"]),
                      "problems": problems}, sort_keys=True))
    return 0 if out["status"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
