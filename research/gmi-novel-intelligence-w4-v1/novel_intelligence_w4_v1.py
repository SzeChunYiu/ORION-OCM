#!/usr/bin/env python3
"""W4 residual-quotient structural-domain capsule (composes after #796 V6).

Advances #592 item 39 beyond W2/W3 and #602 P4 residual novelty at a registered
exact finite *family* scope. Py3.8-safe.

Upstream (#796 `gmi-unseen-form-prediction-v1`) closed V6 with W4 NOT claimed
because recurrence across a parametric family was missing. This package does
not duplicate that capsule: it imports its witness, requires W2/W3 green and
W4 false upstream, then asks whether the residual-quotient *law* is recurrent
and parent-nonreducible on a registered family.

W4 here means novelty-ladder domain status at registered finite family scope:
recurrent residual-quotient structure with a material residual against pure
predictor, flat table, and fixed-budget residual parents. It does NOT mean
J4 NEW_DOMAIN, phase-hole occupancy, or NEW_FORM_OF_INTELLIGENCE_PROVEN.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from typing import Dict, List, Mapping, Sequence, Tuple

Partition = Tuple[int, ...]

FREEZE_LITERAL = b"GMI-NOVEL-INTELLIGENCE-W4-V1/RQM-FAMILY-RECURRENCE"
FREEZE_SHA256 = "57ddb8d1195e0eba61e0527828882bce1f9e0da24a4474ef3a69b7c6c71789c9"

# Registered parametric family F(k): |S_P|=2, max_m=k, |S_O|=k+2, C*=2+k < flat=k+3.
FAMILY_KS = (2, 3, 4)  # type: Tuple[int, ...]
# Held-out fresh residual-specific ecology outside the training family.
FRESH_K = 5
# Fixed-budget residual parent (RAG-without-residual-law caricature).
FIXED_BUDGET_B = 3

UPSTREAM_REL = "../gmi-unseen-form-prediction-v1/unseen_form_prediction_v1.py"
UPSTREAM_FREEZE = "d8e9eac97a9ce7ee3735efe5cc77bef40d6ab611712cd7bccd3fae3f2550030b"


def freeze_digest():
    # type: () -> str
    return hashlib.sha256(FREEZE_LITERAL).hexdigest()


def assert_freeze_intact():
    # type: () -> None
    got = freeze_digest()
    if got != FREEZE_SHA256:
        raise RuntimeError("freeze digest mismatch: %s != %s" % (got, FREEZE_SHA256))


def _load_upstream():
    # type: () -> object
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, UPSTREAM_REL))
    if not os.path.isfile(path):
        raise RuntimeError("upstream V6 package missing at %s" % path)
    spec = importlib.util.spec_from_file_location("unseen_form_prediction_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load upstream module")
    mod = importlib.util.module_from_spec(spec)
    # Ensure sibling imports resolve if any.
    sys.modules["unseen_form_prediction_v1"] = mod
    spec.loader.exec_module(mod)
    return mod


def ecology_for_k(k):
    # type: (int) -> Tuple[Partition, Partition]
    """Construct sparse-alias residual ecology with max_m=k and material flat gap."""
    if k < 2:
        raise ValueError("k must be >= 2")
    fiber0_p = (0,) * k
    fiber0_o = tuple(range(k))
    fiber1_p = (1,) * k
    # Two target classes in fiber 1, labels k and k+1, alternating → m(1)=2.
    fiber1_o = tuple(k + (i % 2) for i in range(k))
    q_p = fiber0_p + fiber1_p
    q_o = fiber0_o + fiber1_o
    return q_p, q_o


def family_prediction(v6, k):
    # type: (object, int) -> Dict[str, object]
    q_p, q_o = ecology_for_k(k)
    pred = v6.property_vector_prediction(q_p, q_o)
    return {
        "k": k,
        "q_p": list(q_p),
        "q_o": list(q_o),
        "max_m": int(pred["min_residual_alphabet"]),
        "predicted_min_cost": int(pred["predicted_min_cost"]),
        "flat_table_cost": int(pred["flat_table_cost"]),
        "needs_residual": bool(pred["needs_residual"]),
        "material_gap_vs_flat": int(pred["flat_table_cost"]) - int(pred["predicted_min_cost"]),
    }


def fixed_budget_parent_succeeds(v6, q_p, q_o, budget):
    # type: (object, Partition, Partition, int) -> bool
    """Parent: residual alphabet capped at fixed B, independent of measured max_m."""
    return bool(v6.exists_residual_exact(q_p, q_o, budget))


def family_member_assay(v6, k):
    # type: (object, int) -> Dict[str, object]
    q_p, q_o = ecology_for_k(k)
    pred = v6.property_vector_prediction(q_p, q_o)
    recovery = v6.find_matching_residuals(q_p, q_o, pred)
    parent = v6.parent_reduction_residual(q_p, q_o, pred)
    fixed_ok = fixed_budget_parent_succeeds(v6, q_p, q_o, FIXED_BUDGET_B)
    law_tracks = (
        int(pred["min_residual_alphabet"]) == k
        and int(recovery["min_cost"]) == 2 + k
        and bool(recovery["no_cheaper_residual_under_qp"])
        and bool(recovery["any_winner_matches_prediction"])
        and bool(parent["material_residual_positive"])
    )
    # Per-member discriminator vs fixed-budget caricature of RAG-without-law:
    # - k > B: cannot recover exactly
    # - k < B: recovers but tight min residual is k, not B (fails size-tracking)
    # - k == B: locally indistinguishable; family recurrence must kill it elsewhere
    if not fixed_ok:
        fixed_verdict = "FAILS_RECOVERY"
    elif k < FIXED_BUDGET_B:
        fixed_verdict = "OVERPROVISIONS__DOES_NOT_TRACK_MAX_M"
    elif k > FIXED_BUDGET_B:
        fixed_verdict = "FAILS_RECOVERY"
    else:
        fixed_verdict = "LOCALLY_MATCHES_AT_B_ONLY"
    return {
        "k": k,
        "prediction": {
            "max_m": int(pred["min_residual_alphabet"]),
            "predicted_min_cost": int(pred["predicted_min_cost"]),
            "flat_table_cost": int(pred["flat_table_cost"]),
            "needs_residual": bool(pred["needs_residual"]),
        },
        "recovery": {
            "min_cost": recovery["min_cost"],
            "any_winner_matches_prediction": recovery["any_winner_matches_prediction"],
            "no_cheaper_residual_under_qp": recovery["no_cheaper_residual_under_qp"],
            "matches_predicted_min_cost": recovery["matches_predicted_min_cost"],
        },
        "parent_reduction": {
            "material_residual_positive": parent["material_residual_positive"],
            "pure_predictor_under_qp_succeeds": parent["pure_predictor_under_qp_succeeds"],
            "flat_table_cost": parent["flat_table_cost"],
            "measured_min_cost": parent["measured_min_cost"],
            "parent_first_refusal": parent["parent_first_refusal"],
        },
        "fixed_budget_parent": {
            "budget": FIXED_BUDGET_B,
            "succeeds_exact_recovery": fixed_ok,
            "verdict": fixed_verdict,
            "tracks_max_m_locally": fixed_ok and k == FIXED_BUDGET_B,
        },
        "residual_law_holds": law_tracks,
    }


def remint_family_member(v6, k):
    # type: (object, int) -> Dict[str, object]
    q_p, q_o = ecology_for_k(k)
    n = len(q_p)
    hist_perm = tuple(reversed(range(n)))
    labels = sorted(set(q_o))
    label_perm = {lab: labels[(i + 1) % len(labels)] for i, lab in enumerate(labels)}
    q_p2, q_o2 = v6.remint_partitions(q_p, q_o, hist_perm, label_perm)
    pred2 = v6.property_vector_prediction(q_p2, q_o2)
    search2 = v6.find_matching_residuals(q_p2, q_o2, pred2)
    return {
        "k": k,
        "prediction_invariant": int(pred2["min_residual_alphabet"]) == k
        and int(pred2["predicted_min_cost"]) == 2 + k,
        "remint_recovery": bool(search2["any_winner_matches_prediction"])
        and bool(search2["matches_predicted_min_cost"])
        and bool(search2["no_cheaper_residual_under_qp"]),
    }


def fresh_outside_family(v6):
    # type: (object) -> Dict[str, object]
    q_p, q_o = ecology_for_k(FRESH_K)
    pred = v6.property_vector_prediction(q_p, q_o)
    # Freeze-style prediction stated from k alone (no search yet).
    predicted_before_search = {
        "max_m": FRESH_K,
        "predicted_min_cost": 2 + FRESH_K,
        "flat_table_cost": FRESH_K + 3,
        "zero_residual_impossible": True,
    }
    search = v6.find_matching_residuals(q_p, q_o, pred)
    predictor_ok = v6.pure_predictor_under_qp_succeeds(q_p, q_o)
    fixed_ok = fixed_budget_parent_succeeds(v6, q_p, q_o, FIXED_BUDGET_B)
    holds = (
        int(pred["min_residual_alphabet"]) == predicted_before_search["max_m"]
        and int(pred["predicted_min_cost"]) == predicted_before_search["predicted_min_cost"]
        and int(pred["flat_table_cost"]) == predicted_before_search["flat_table_cost"]
        and bool(search["matches_predicted_min_cost"])
        and bool(search["any_winner_matches_prediction"])
        and bool(search["no_cheaper_residual_under_qp"])
        and (not predictor_ok)
        and (not fixed_ok)  # FRESH_K=5 > FIXED_BUDGET_B=3
    )
    return {
        "k": FRESH_K,
        "outside_family": FRESH_K not in FAMILY_KS,
        "predicted_before_search": predicted_before_search,
        "measured": {
            "max_m": int(pred["min_residual_alphabet"]),
            "min_cost": search["min_cost"],
            "flat_table_cost": int(pred["flat_table_cost"]),
            "pure_predictor": predictor_ok,
            "fixed_budget_succeeds": fixed_ok,
        },
        "fresh_prediction_holds": holds,
    }


def upstream_gate(v6):
    # type: (object) -> Dict[str, object]
    if v6.freeze_digest() != UPSTREAM_FREEZE:
        raise RuntimeError("upstream freeze digest drift")
    receipt = v6.run_campaign()
    ladder = receipt["item39_ladder"]
    return {
        "upstream_artifact": receipt["artifact"],
        "all_six_v6_boxes_green": bool(receipt["all_six_v6_boxes_green"]),
        "W2_parent_separation": bool(ladder["W2_parent_separation"]),
        "W3_empirical_niche": bool(ladder["W3_empirical_niche"]),
        "W4_domain_status_upstream": bool(ladder["W4_domain_status"]),
        "item39_ceiling_upstream": ladder["item39_ceiling"],
        "phase_hole_occupant_claim_upstream": bool(ladder["phase_hole_occupant_claim"]),
        "compose_ok": (
            bool(receipt["all_six_v6_boxes_green"])
            and bool(ladder["W2_parent_separation"])
            and bool(ladder["W3_empirical_niche"])
            and (not bool(ladder["W4_domain_status"]))
            and (not bool(ladder["phase_hole_occupant_claim"]))
        ),
    }


def w4_box_ledger(family_assays, remints, fresh, upstream):
    # type: (...) -> Dict[str, Dict[str, object]]
    all_law = all(a["residual_law_holds"] for a in family_assays)
    all_parent = all(a["parent_reduction"]["material_residual_positive"] for a in family_assays)
    # Fixed budget B is a family law only if every member has max_m==B and recovers.
    # With distinct k in F this is impossible — that is the recurrence residual.
    distinct_max_m = sorted({int(a["prediction"]["max_m"]) for a in family_assays})
    fixed_budget_is_family_law = all(
        a["fixed_budget_parent"]["tracks_max_m_locally"] for a in family_assays
    )
    has_under_and_over = (
        any(a["k"] < FIXED_BUDGET_B for a in family_assays)
        and any(a["k"] > FIXED_BUDGET_B for a in family_assays)
    )
    fixed_budget_family_residual = (not fixed_budget_is_family_law) and has_under_and_over and (
        any(a["fixed_budget_parent"]["verdict"] == "FAILS_RECOVERY" for a in family_assays)
        and any(
            a["fixed_budget_parent"]["verdict"] == "OVERPROVISIONS__DOES_NOT_TRACK_MAX_M"
            for a in family_assays
        )
    )
    all_remint = all(r["prediction_invariant"] and r["remint_recovery"] for r in remints)
    ks_seen = sorted(a["k"] for a in family_assays)
    return {
        "W4_1_upstream_compose_gate": {
            "tick": bool(upstream["compose_ok"]),
            "evidence": "Upstream V6 W2/W3 green, W4 false, phase-hole refused",
            "detail": {
                "W2": upstream["W2_parent_separation"],
                "W3": upstream["W3_empirical_niche"],
                "W4_upstream": upstream["W4_domain_status_upstream"],
            },
        },
        "W4_2_parametric_family_registered": {
            "tick": ks_seen == list(FAMILY_KS) and len(set(ks_seen)) >= 3,
            "evidence": "Registered F(k) for k in {2,3,4} with distinct max_m",
            "detail": {"ks": ks_seen},
        },
        "W4_3_property_first_family_law": {
            "tick": all(
                a["prediction"]["max_m"] == a["k"]
                and a["prediction"]["predicted_min_cost"] == 2 + a["k"]
                for a in family_assays
            ),
            "evidence": "C0 law |R|>=max_m=k and C*=2+k predicted before search for every k",
            "detail": {
                a["k"]: {
                    "max_m": a["prediction"]["max_m"],
                    "C_star": a["prediction"]["predicted_min_cost"],
                }
                for a in family_assays
            },
        },
        "W4_4_neutral_recovery_on_all_members": {
            "tick": all_law,
            "evidence": "P-fixed residual grammar recovers law on every family member",
            "detail": {a["k"]: a["recovery"] for a in family_assays},
        },
        "W4_5_parent_reduction_family_residual": {
            "tick": all_parent and fixed_budget_family_residual and len(distinct_max_m) >= 3,
            "evidence": (
                "Material residual vs pure predictor + flat table on every member; "
                "fixed-budget parent is not the family residual law (overprovisions "
                "some k, fails recovery on others)"
            ),
            "detail": {
                "distinct_max_m": distinct_max_m,
                "fixed_budget_is_family_law": fixed_budget_is_family_law,
                "fixed_budget_family_residual": fixed_budget_family_residual,
                "per_k": {
                    a["k"]: {
                        "material": a["parent_reduction"]["material_residual_positive"],
                        "fixed_verdict": a["fixed_budget_parent"]["verdict"],
                    }
                    for a in family_assays
                },
            },
        },
        "W4_6_remint_replication": {
            "tick": all_remint,
            "evidence": "History/label remint preserves family law and recovery",
            "detail": {r["k"]: r for r in remints},
        },
        "W4_7_fresh_outside_family_prediction": {
            "tick": bool(fresh["fresh_prediction_holds"]) and bool(fresh["outside_family"]),
            "evidence": "Held-out k=5 ecology matches residual law; fixed-budget parent fails",
            "detail": fresh,
        },
        "W4_8_phase_hole_honesty": {
            "tick": (not bool(upstream["phase_hole_occupant_claim_upstream"])),
            "evidence": "Phase-hole occupant claim remains refused (known-parent negative stands)",
            "detail": {"phase_hole_occupant_claim": False},
        },
    }


def item39_ladder(boxes):
    # type: (Mapping[str, Mapping[str, object]]) -> Dict[str, object]
    all_w4 = all(b["tick"] for b in boxes.values())
    return {
        "W0_existence": True,
        "W1_necessity_compression": True,
        "W2_parent_separation": True,
        "W3_empirical_niche": True,
        "W4_domain_status": all_w4,
        "W4_scope": (
            "residual_quotient_structural_domain_at_registered_finite_family_F_k_in_2_3_4"
        ),
        "W4_reason": (
            "Recurrent residual-quotient law across registered parametric family with "
            "parent-nonreducible residual vs predictor/flat/fixed-budget; not J4 NEW_DOMAIN."
            if all_w4
            else "W4 boxes incomplete; see ledger."
        ),
        "phase_hole_occupant_claim": False,
        "phase_hole_note": (
            "Prior open-niche phase-hole prediction failed (known parent). This capsule "
            "does not revive that claim."
        ),
        "j4_new_domain_claimed": False,
        "p4_surviving_unseen_morphology": all_w4,
        "p4_surviving_unseen_domain": False,  # J4 gate not attempted
        "claim_ceiling": (
            "W4_RESIDUAL_QUOTIENT_STRUCTURAL_DOMAIN_AT_REGISTERED_FINITE_FAMILY_SCOPE"
            if all_w4
            else "W4_PARTIAL__SEE_BOX_LEDGER"
        ),
        "item39_ceiling": (
            "NOVEL_INTEL_LADDER_W2_W3_W4_GREEN_AT_EXACT_RQM_FAMILY_SCOPE"
            if all_w4
            else "ITEM39_PARTIAL__SEE_LADDER"
        ),
    }


def run_campaign():
    # type: () -> Dict[str, object]
    assert_freeze_intact()
    v6 = _load_upstream()
    upstream = upstream_gate(v6)
    # Property-first family predictions BEFORE member search assays.
    c0_family = [family_prediction(v6, k) for k in FAMILY_KS]
    family_assays = [family_member_assay(v6, k) for k in FAMILY_KS]
    remints = [remint_family_member(v6, k) for k in FAMILY_KS]
    fresh = fresh_outside_family(v6)
    boxes = w4_box_ledger(family_assays, remints, fresh, upstream)
    ladder = item39_ladder(boxes)
    return {
        "artifact": "GMI_NOVEL_INTELLIGENCE_W4_V1",
        "freeze_sha256": freeze_digest(),
        "upstream_compose": upstream,
        "c0_family_predictions": c0_family,
        "family_assays": family_assays,
        "remints": remints,
        "fresh_prediction": fresh,
        "w4_boxes": boxes,
        "item39_ladder": ladder,
        "all_w4_boxes_green": all(b["tick"] for b in boxes.values()),
        "fixed_budget_B": FIXED_BUDGET_B,
        "family_ks": list(FAMILY_KS),
        "fresh_k": FRESH_K,
    }


def emit_receipt(path):
    # type: (str) -> Dict[str, object]
    receipt = run_campaign()
    # Compact recovery samples if any leaked through (upstream samples not stored here).
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return receipt


def main():
    # type: () -> None
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "RESULT_V1.json")
    receipt = emit_receipt(path)
    print(
        json.dumps(
            {
                "all_w4_boxes_green": receipt["all_w4_boxes_green"],
                "claim_ceiling": receipt["item39_ladder"]["claim_ceiling"],
                "item39_ceiling": receipt["item39_ladder"]["item39_ceiling"],
                "W4_domain_status": receipt["item39_ladder"]["W4_domain_status"],
                "boxes": {k: v["tick"] for k, v in receipt["w4_boxes"].items()},
                "upstream_compose_ok": receipt["upstream_compose"]["compose_ok"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
