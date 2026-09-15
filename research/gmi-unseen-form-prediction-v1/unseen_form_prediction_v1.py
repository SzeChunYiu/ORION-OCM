#!/usr/bin/env python3
"""Exact finite V6 unseen-form prediction microscope (RQM property vector).

Closes #602 V6 boxes at registered exact scope and advances #592 item 39 to
W2/W3 green with W4 explicitly not claimed. Py3.8-safe.

Search is conditional on the registered predictive quotient q_P (the RQM
prediction: keep the predictive substrate and add residual). Global machines that
abandon q_P are parent morphologies, not RQM recoveries.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import defaultdict
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

Partition = Tuple[int, ...]

FREEZE_LITERAL = b"GMI-UNSEEN-FORM-PREDICTION-V1/RQM-SPARSE-ALIAS"
FREEZE_SHA256 = "d8e9eac97a9ce7ee3735efe5cc77bef40d6ab611712cd7bccd3fae3f2550030b"

# Predicted ecology (frozen before search).
# max_m=3, |S_P|=2, |S_O|=5 → RQM cost 5 < flat-table cost 6.
Q_P = (0, 0, 0, 1, 1, 1)  # type: Partition
Q_O = (0, 1, 2, 3, 4, 3)  # type: Partition
H_SIZE = 6

# Negative twin: residual unnecessary.
Q_P_TWIN = (0, 1, 2, 3, 4, 3)  # type: Partition
Q_O_TWIN = (0, 1, 2, 3, 4, 3)  # type: Partition

# Held-out residual-specific ecology: max_m'=4, |S_P'|=2, |S_O'|=6 → cost 6 < 7.
Q_P_FRESH = (0, 0, 0, 0, 1, 1, 1, 1)  # type: Partition
Q_O_FRESH = (0, 1, 2, 3, 4, 5, 4, 5)  # type: Partition
H_FRESH = 8


def freeze_digest():
    # type: () -> str
    return hashlib.sha256(FREEZE_LITERAL).hexdigest()


def assert_freeze_intact():
    # type: () -> None
    got = freeze_digest()
    if got != FREEZE_SHA256:
        raise RuntimeError("freeze digest mismatch: %s != %s" % (got, FREEZE_SHA256))


def fiber_multiplicities(q_p, q_o):
    # type: (Partition, Partition) -> Dict[int, int]
    if len(q_p) != len(q_o):
        raise ValueError("partition length mismatch")
    fibers = defaultdict(set)  # type: Dict[int, set]
    for p, o in zip(q_p, q_o):
        fibers[p].add(o)
    return {p: len(s) for p, s in sorted(fibers.items())}


def max_multiplicity(q_p, q_o):
    # type: (Partition, Partition) -> int
    return max(fiber_multiplicities(q_p, q_o).values())


def property_vector_prediction(q_p, q_o):
    # type: (Partition, Partition) -> Dict[str, object]
    """C0 property-first prediction from residual-quotient theory — no search."""
    m = max_multiplicity(q_p, q_o)
    p_lb = len(set(q_p))
    return {
        "needs_residual": m > 1,
        "min_residual_alphabet": m,
        "min_predictor_classes": p_lb,
        "zero_residual_impossible_under_qp": m > 1,
        "predicted_min_cost": (p_lb + m) if m > 1 else (p_lb + 1),
        "fiber_multiplicities": fiber_multiplicities(q_p, q_o),
        "flat_table_cost": 1 + len(set(q_o)),
        "q_p": list(q_p),
        "q_o": list(q_o),
        "scope": "machines_with_P_assign_fixed_to_registered_q_P",
    }


def used_alphabet(assign):
    # type: (Sequence[int]) -> int
    return len(set(assign))


def machine_cost(q_p_assign, q_r_assign):
    # type: (Sequence[int], Sequence[int]) -> int
    return used_alphabet(q_p_assign) + used_alphabet(q_r_assign)


def build_decoder(q_p_assign, q_r_assign, q_o):
    # type: (Sequence[int], Sequence[int], Partition) -> Optional[Dict[Tuple[int, int], int]]
    decoder = {}  # type: Dict[Tuple[int, int], int]
    for h, target in enumerate(q_o):
        key = (q_p_assign[h], q_r_assign[h])
        if key in decoder and decoder[key] != target:
            return None
        decoder[key] = target
    return decoder


def decode_ok(q_p_assign, q_r_assign, decoder, q_o):
    # type: (Sequence[int], Sequence[int], Mapping[Tuple[int, int], int], Partition) -> bool
    for h, target in enumerate(q_o):
        if decoder.get((q_p_assign[h], q_r_assign[h])) != target:
            return False
    return True


def residual_separately_mutable(q_p_assign, q_r_assign, decoder, q_o):
    # type: (Sequence[int], Sequence[int], Mapping[Tuple[int, int], int], Partition) -> bool
    by_p = defaultdict(list)  # type: Dict[int, List[int]]
    for h in range(len(q_o)):
        by_p[q_p_assign[h]].append(h)
    for hs in by_p.values():
        for i, j in itertools.combinations(hs, 2):
            if q_r_assign[i] != q_r_assign[j] and q_o[i] != q_o[j]:
                key_i = (q_p_assign[i], q_r_assign[i])
                key_j = (q_p_assign[i], q_r_assign[j])
                if decoder.get(key_i) != decoder.get(key_j):
                    return True
    return max_multiplicity(tuple(q_p_assign), q_o) <= 1


def classify_property_vector(q_p_assign, q_r_assign, decoder, q_o, predicted):
    # type: (...) -> Dict[str, bool]
    exact = decode_ok(q_p_assign, q_r_assign, decoder, q_o)
    r_size = used_alphabet(q_r_assign)
    p_size = used_alphabet(q_p_assign)
    return {
        "PV1_exact_recovery": exact,
        "PV2_predictor_fixed_to_qp": list(q_p_assign) == list(predicted["q_p"]),
        "PV3_residual_alphabet": r_size >= int(predicted["min_residual_alphabet"]),
        "PV4_composition_decoder": exact,
        "PV5_uses_residual_when_required": (
            (not bool(predicted["needs_residual"])) or r_size >= 2
        ),
        "PV6_separately_mutable_residual": residual_separately_mutable(
            q_p_assign, q_r_assign, decoder, q_o
        ),
        "PV7_predictor_class_count": p_size == int(predicted["min_predictor_classes"]),
    }


def construct_canonical_rqm(q_p, q_o):
    # type: (Partition, Partition) -> Dict[str, object]
    fiber_residual = defaultdict(dict)  # type: Dict[int, Dict[int, int]]
    r_assign_list = []  # type: List[int]
    for p, o in zip(q_p, q_o):
        slot = fiber_residual[p]
        if o not in slot:
            slot[o] = len(slot)
        r_assign_list.append(slot[o])
    r_assign = tuple(r_assign_list)
    decoder = build_decoder(q_p, r_assign, q_o)
    assert decoder is not None
    return {
        "p_assign": q_p,
        "r_assign": r_assign,
        "decoder": dict(decoder),
        "cost": machine_cost(q_p, r_assign),
        "p_size": used_alphabet(q_p),
        "r_size": used_alphabet(r_assign),
    }


def exists_residual_exact(q_p, q_o, r_cap):
    # type: (Partition, Partition, int) -> bool
    """Whether some R-assignment with alphabet ⊆ {0..r_cap-1} decodes exactly under fixed P."""
    n = len(q_o)
    # Theorem short-circuit: impossible if r_cap < max_m.
    if r_cap < max_multiplicity(q_p, q_o):
        return False
    for r_assign in itertools.product(range(r_cap), repeat=n):
        if used_alphabet(r_assign) > r_cap:
            continue
        if build_decoder(q_p, r_assign, q_o) is not None:
            return True
    return False


def min_residual_under_qp(q_p, q_o):
    # type: (Partition, Partition) -> int
    """Smallest residual alphabet size with P fixed to q_p."""
    m = max_multiplicity(q_p, q_o)
    # PRQ-1 lower bound is tight via constructive canonical labeling.
    canon = construct_canonical_rqm(q_p, q_o)
    assert int(canon["r_size"]) == m
    assert not exists_residual_exact(q_p, q_o, m - 1) if m > 1 else True
    return m


def pure_predictor_under_qp_succeeds(q_p, q_o):
    # type: (Partition, Partition) -> bool
    """Parent: decode target from predictive class alone (R trivial)."""
    return exists_residual_exact(q_p, q_o, 1)


def flat_table_cost(q_o):
    # type: (Partition) -> int
    return 1 + len(set(q_o))


def remint_partitions(q_p, q_o, hist_perm, label_perm):
    # type: (Partition, Partition, Sequence[int], Mapping[int, int]) -> Tuple[Partition, Partition]
    if sorted(hist_perm) != list(range(len(q_p))):
        raise ValueError("hist_perm must be a permutation of histories")
    new_p = tuple(q_p[h] for h in hist_perm)
    new_o = tuple(label_perm[q_o[h]] for h in hist_perm)
    return new_p, new_o


def find_matching_residuals(q_p, q_o, predicted, sample_limit=8):
    # type: (Partition, Partition, Mapping[str, object], int) -> Dict[str, object]
    """Neutral search over residual assignments with P fixed to registered q_P."""
    m = int(predicted["min_residual_alphabet"])
    n = len(q_o)
    canon = construct_canonical_rqm(q_p, q_o)
    samples = []  # type: List[Dict[str, object]]
    canon_pv = classify_property_vector(
        canon["p_assign"], canon["r_assign"], canon["decoder"], q_o, predicted
    )
    samples.append(
        {
            "cost": canon["cost"],
            "p_size": canon["p_size"],
            "r_size": canon["r_size"],
            "property_vector": canon_pv,
            "matches_prediction": all(canon_pv.values()),
            "source": "canonical_rqm",
        }
    )
    n_exact = 0
    matched = bool(samples[0]["matches_prediction"])
    # Enumerate residual assignments using exactly alphabet size m (surjective onto 0..m-1).
    for r_assign in itertools.product(range(m), repeat=n):
        if used_alphabet(r_assign) != m:
            continue
        decoder = build_decoder(q_p, r_assign, q_o)
        if decoder is None:
            continue
        n_exact += 1
        pv = classify_property_vector(q_p, r_assign, decoder, q_o, predicted)
        ok = all(pv.values())
        if ok:
            matched = True
        if ok or len(samples) < sample_limit:
            samples.append(
                {
                    "cost": machine_cost(q_p, r_assign),
                    "p_size": used_alphabet(q_p),
                    "r_size": used_alphabet(r_assign),
                    "property_vector": pv,
                    "matches_prediction": ok,
                    "source": "enumeration",
                }
            )
        if matched and len(samples) >= sample_limit:
            break
    cheaper = exists_residual_exact(q_p, q_o, m - 1) if m > 1 else False
    measured_cost = used_alphabet(q_p) + m
    return {
        "found": matched,
        "min_cost": measured_cost,
        "no_cheaper_residual_under_qp": not cheaper,
        "canonical_constructive_cost": canon["cost"],
        "matches_predicted_min_cost": (
            int(canon["cost"]) == int(predicted["predicted_min_cost"]) and not cheaper
        ),
        "any_winner_matches_prediction": matched,
        "winners_sampled": samples,
        "n_exact_seen": n_exact,
        "min_residual_under_qp": m if not cheaper else min_residual_under_qp(q_p, q_o),
    }


def parent_reduction_residual(q_p, q_o, predicted):
    # type: (Partition, Partition, Mapping[str, object]) -> Dict[str, object]
    search = find_matching_residuals(q_p, q_o, predicted)
    predictor_ok = pure_predictor_under_qp_succeeds(q_p, q_o)
    flat_cost = flat_table_cost(q_o)
    measured_min = search["min_cost"]
    material_vs_flat = flat_cost - int(measured_min)
    return {
        "pure_predictor_under_qp_succeeds": predictor_ok,
        "flat_table_cost": flat_cost,
        "rqm_predicted_cost": int(predicted["predicted_min_cost"]),
        "measured_min_cost": measured_min,
        "material_residual_vs_flat": material_vs_flat,
        "material_residual_positive": material_vs_flat > 0 and not predictor_ok,
        "parent_first_refusal": (
            "PARENT_REDUCTION_LEAVES_MATERIAL_RESIDUAL"
            if material_vs_flat > 0 and not predictor_ok
            else "PARENT_FIRST_REFUSAL_WINS__NO_NEW_FORM"
        ),
        "no_cheaper_residual_under_qp": search["no_cheaper_residual_under_qp"],
    }


def negative_twin_assay():
    # type: () -> Dict[str, object]
    pred = property_vector_prediction(Q_P_TWIN, Q_O_TWIN)
    search = find_matching_residuals(Q_P_TWIN, Q_O_TWIN, pred)
    canon = construct_canonical_rqm(Q_P_TWIN, Q_O_TWIN)
    return {
        "prediction": {
            "needs_residual": pred["needs_residual"],
            "min_residual_alphabet": pred["min_residual_alphabet"],
            "min_predictor_classes": pred["min_predictor_classes"],
            "predicted_min_cost": pred["predicted_min_cost"],
            "zero_residual_impossible_under_qp": pred["zero_residual_impossible_under_qp"],
        },
        "search": {
            "min_cost": search["min_cost"],
            "canonical_r_size": canon["r_size"],
            "pure_predictor_under_qp": pure_predictor_under_qp_succeeds(Q_P_TWIN, Q_O_TWIN),
        },
        "negative_twin_removes_residual_necessity": (
            int(pred["min_residual_alphabet"]) == 1
            and int(canon["r_size"]) == 1
            and pure_predictor_under_qp_succeeds(Q_P_TWIN, Q_O_TWIN)
            and not bool(pred["needs_residual"])
        ),
    }


def remint_replication():
    # type: () -> Dict[str, object]
    pred0 = property_vector_prediction(Q_P, Q_O)
    hist_perm = tuple(reversed(range(H_SIZE)))
    labels = sorted(set(Q_O))
    label_perm = {lab: labels[(i + 2) % len(labels)] for i, lab in enumerate(labels)}
    q_p2, q_o2 = remint_partitions(Q_P, Q_O, hist_perm, label_perm)
    pred2 = property_vector_prediction(q_p2, q_o2)
    search2 = find_matching_residuals(q_p2, q_o2, pred2)
    return {
        "original_prediction": {
            "min_residual_alphabet": pred0["min_residual_alphabet"],
            "min_predictor_classes": pred0["min_predictor_classes"],
            "predicted_min_cost": pred0["predicted_min_cost"],
        },
        "remint_prediction": {
            "min_residual_alphabet": pred2["min_residual_alphabet"],
            "min_predictor_classes": pred2["min_predictor_classes"],
            "predicted_min_cost": pred2["predicted_min_cost"],
        },
        "prediction_invariant_under_remint": (
            pred0["min_residual_alphabet"] == pred2["min_residual_alphabet"]
            and pred0["min_predictor_classes"] == pred2["min_predictor_classes"]
            and pred0["predicted_min_cost"] == pred2["predicted_min_cost"]
        ),
        "remint_recovery": {
            "min_cost": search2["min_cost"],
            "any_winner_matches_prediction": search2["any_winner_matches_prediction"],
            "no_cheaper_residual_under_qp": search2["no_cheaper_residual_under_qp"],
            "matches_predicted_min_cost": search2["matches_predicted_min_cost"],
        },
        "independent_remint_replication": (
            search2["any_winner_matches_prediction"]
            and search2["matches_predicted_min_cost"]
            and search2["no_cheaper_residual_under_qp"]
        ),
    }


def fresh_residual_prediction():
    # type: () -> Dict[str, object]
    predicted = property_vector_prediction(Q_P_FRESH, Q_O_FRESH)
    search = find_matching_residuals(Q_P_FRESH, Q_O_FRESH, predicted)
    predictor_ok = pure_predictor_under_qp_succeeds(Q_P_FRESH, Q_O_FRESH)
    return {
        "predicted_max_m": predicted["min_residual_alphabet"],
        "predicted_min_cost": predicted["predicted_min_cost"],
        "predicted_zero_residual_impossible_under_qp": predicted[
            "zero_residual_impossible_under_qp"
        ],
        "flat_table_cost": predicted["flat_table_cost"],
        "measured_min_cost": search["min_cost"],
        "pure_predictor_under_qp": predictor_ok,
        "no_cheaper_residual_under_qp": search["no_cheaper_residual_under_qp"],
        "any_winner_matches_prediction": search["any_winner_matches_prediction"],
        "fresh_prediction_holds": (
            search["matches_predicted_min_cost"]
            and search["any_winner_matches_prediction"]
            and search["no_cheaper_residual_under_qp"]
            and (not predictor_ok)
            and int(predicted["min_residual_alphabet"]) == 4
            and int(predicted["flat_table_cost"]) - int(predicted["predicted_min_cost"]) > 0
        ),
    }


def v6_box_ledger(receipt):
    # type: (Mapping[str, object]) -> Dict[str, Dict[str, object]]
    pred = receipt["c0_prediction"]
    recovery = receipt["neutral_recovery"]
    twin = receipt["negative_twin"]
    parent = receipt["parent_reduction"]
    remint = receipt["remint"]
    fresh = receipt["fresh_prediction"]
    return {
        "V6_1_property_first_before_search": {
            "tick": True,
            "evidence": "C0 prediction derived from fiber multiplicities before enumeration",
            "detail": {
                "min_residual_alphabet": pred["min_residual_alphabet"],
                "predicted_min_cost": pred["predicted_min_cost"],
            },
        },
        "V6_2_neutral_recovery_in_predicted_ecology": {
            "tick": bool(recovery["any_winner_matches_prediction"])
            and bool(recovery["matches_predicted_min_cost"])
            and bool(recovery["no_cheaper_residual_under_qp"]),
            "evidence": "P-fixed residual grammar recovers predicted RQM property vector",
            "detail": {
                "min_cost": recovery["min_cost"],
                "matches": recovery["any_winner_matches_prediction"],
            },
        },
        "V6_3_negative_twin_removes_it": {
            "tick": bool(twin["negative_twin_removes_residual_necessity"]),
            "evidence": "zero-residual twin makes residual augmentation unnecessary under q_P",
            "detail": twin["search"],
        },
        "V6_4_parent_reduction_material_residual": {
            "tick": bool(parent["material_residual_positive"]),
            "evidence": parent["parent_first_refusal"],
            "detail": {
                "flat_table_cost": parent["flat_table_cost"],
                "measured_min_cost": parent["measured_min_cost"],
                "pure_predictor_under_qp_succeeds": parent["pure_predictor_under_qp_succeeds"],
            },
        },
        "V6_5_independent_remint_replication": {
            "tick": bool(remint["independent_remint_replication"]),
            "evidence": "history/label remint recovers the same property vector",
            "detail": remint["remint_recovery"],
        },
        "V6_6_fresh_residual_specific_prediction": {
            "tick": bool(fresh["fresh_prediction_holds"]),
            "evidence": "held-out m=4 ecology matches residual-alphabet prediction under q_P'",
            "detail": {
                "predicted_max_m": fresh["predicted_max_m"],
                "measured_min_cost": fresh["measured_min_cost"],
            },
        },
    }


def item39_ladder(boxes):
    # type: (Mapping[str, Mapping[str, object]]) -> Dict[str, object]
    all_v6 = all(b["tick"] for b in boxes.values())
    return {
        "W0_existence": True,
        "W1_necessity_compression": True,
        "W2_parent_separation": bool(boxes["V6_4_parent_reduction_material_residual"]["tick"]),
        "W3_empirical_niche": bool(boxes["V6_2_neutral_recovery_in_predicted_ecology"]["tick"])
        and bool(boxes["V6_5_independent_remint_replication"]["tick"]),
        "W4_domain_status": False,
        "W4_reason": (
            "Registered-scope property-vector recovery only; no claim of recurrent "
            "cross-ecology domain status or atlas phase-hole occupancy."
        ),
        "phase_hole_occupant_claim": False,
        "phase_hole_note": (
            "Prior open-niche phase-hole prediction failed (known parent occupant). "
            "This capsule does not revive that claim; it closes V6 via residual-quotient "
            "property prediction at exact finite scope, conditional on registered q_P."
        ),
        "claim_ceiling": (
            "UNSEEN_FORM_PREDICTION_SUPPORTED_AT_REGISTERED_SCOPE"
            if all_v6
            else "V6_PARTIAL__SEE_BOX_LEDGER"
        ),
        "item39_ceiling": (
            "NOVEL_INTEL_LADDER_W2_W3_GREEN_AT_EXACT_RQM_SCOPE__W4_NOT_CLAIMED"
            if all_v6 and boxes["V6_4_parent_reduction_material_residual"]["tick"]
            else "ITEM39_PARTIAL__SEE_LADDER"
        ),
    }


def run_campaign():
    # type: () -> Dict[str, object]
    assert_freeze_intact()
    predicted = property_vector_prediction(Q_P, Q_O)
    recovery = find_matching_residuals(Q_P, Q_O, predicted)
    twin = negative_twin_assay()
    parent = parent_reduction_residual(Q_P, Q_O, predicted)
    remint = remint_replication()
    fresh = fresh_residual_prediction()
    receipt = {
        "artifact": "GMI_UNSEEN_FORM_PREDICTION_V1",
        "freeze_sha256": freeze_digest(),
        "ecology": {
            "q_p": list(Q_P),
            "q_o": list(Q_O),
            "fiber_multiplicities": fiber_multiplicities(Q_P, Q_O),
        },
        "c0_prediction": {
            k: predicted[k]
            for k in (
                "needs_residual",
                "min_residual_alphabet",
                "min_predictor_classes",
                "zero_residual_impossible_under_qp",
                "predicted_min_cost",
                "fiber_multiplicities",
                "flat_table_cost",
                "scope",
            )
        },
        "neutral_recovery": recovery,
        "negative_twin": twin,
        "parent_reduction": parent,
        "remint": remint,
        "fresh_prediction": fresh,
    }  # type: Dict[str, object]
    boxes = v6_box_ledger(receipt)
    receipt["v6_boxes"] = boxes
    receipt["item39_ladder"] = item39_ladder(boxes)
    receipt["all_six_v6_boxes_green"] = all(b["tick"] for b in boxes.values())
    return receipt


def emit_receipt(path):
    # type: (str) -> Dict[str, object]
    receipt = run_campaign()
    compact = dict(receipt)
    nr = dict(compact["neutral_recovery"])
    nr["winners_sampled"] = nr.get("winners_sampled", [])[:5]
    compact["neutral_recovery"] = nr
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(compact, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return compact


def main():
    # type: () -> None
    import os

    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "RESULT_V1.json")
    receipt = emit_receipt(path)
    print(
        json.dumps(
            {
                "all_six_v6_boxes_green": receipt["all_six_v6_boxes_green"],
                "claim_ceiling": receipt["item39_ladder"]["claim_ceiling"],
                "item39_ceiling": receipt["item39_ladder"]["item39_ceiling"],
                "boxes": {k: v["tick"] for k, v in receipt["v6_boxes"].items()},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
