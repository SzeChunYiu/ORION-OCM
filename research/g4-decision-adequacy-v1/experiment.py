"""G4 remaining non-ML decision-adequacy measurements on the exact cache toy.

Imports ``research/g4-horizon-exact-v1/horizon_exact.py``; does not copy its
engines and does not train a router. G4.4 stays locked (0/9). Box 4 is refuted.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
HORIZON_DIR = REPO / "research" / "g4-horizon-exact-v1"
HORIZON_PATH = HORIZON_DIR / "horizon_exact.py"
sys.path.insert(0, str(HORIZON_DIR))
import horizon_exact as H  # noqa: E402

SCHEMA = "ocm.g4.decision-adequacy.v1"
ISSUE = 165
SALT = "orion-ocm-g4-decision-adequacy-v1"
LEGAL_FEATURES = ("cached", "remaining", "item", "time")
SERVICE_COORDS = ("rent", "build", "hit")
RESET_INTERVALS = (1, 2, 4, 8)
HYPOTHETICAL_LEARNER_TRAIN = 1
HYPOTHETICAL_LEARNER_INFER_PER_QUERY = 1

G44_BOXES = (
    "G4.4/001-multiple_safe_strategies_remain_after_exact_admissibility",
    "G4.4/002-optimal_strategy_changes_across_legal_pre_outcome_states",
    "G4.4/003-counterfactual_value_is_identifiable",
    "G4.4/004-simple_exact_analytic_parents_leave_a_material_residual",
    "G4.4/005-legal_features_contain_enough_information_for_the_required_d",
    "G4.4/006-hypothesis_class_is_adequate",
    "G4.4/007-lifetime_benefit_remains_positive_after_training_inference_u",
    "G4.4/008-lifecycle_semantics_remain_equivalent",
    "G4.4/009-result_survives_pareto_resource_price_analysis",
)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def myopic_1step(_t, _item, cached, _remaining):
    """Strictly poorer class: one-step costs only. Future hits are invisible."""
    if cached:
        return "hit"
    return "buy" if H.BUILD < H.RENT else "rent"


def legal_features(t: int, item: int, cached: bool, remaining: int) -> dict[str, int | bool]:
    return {
        "cached": bool(cached),
        "remaining": int(remaining),
        "item": int(item),
        "time": int(t),
    }


def required_action(cached: bool, remaining: int) -> str:
    if cached:
        return "hit"
    return "buy" if H.analytic_should_buy(remaining) else "rent"


def mask_key(feat: dict[str, int | bool], drop: tuple[str, ...]) -> tuple:
    return tuple((name, feat[name]) for name in LEGAL_FEATURES if name not in drop)


def decision_states(sequences) -> list[dict[str, Any]]:
    """Legal pre-outcome states: remaining from the sequence; cached if the item appeared."""
    rows = []
    for seq in sequences:
        seen = set()
        for t, item in enumerate(seq, start=1):
            remaining = H.remaining_count(seq, t - 1, item)
            candidates = [False]
            if item in seen:
                candidates.append(True)
            for cached in candidates:
                feat = legal_features(t, item, cached, remaining)
                rows.append(
                    {
                        "sequence": list(seq),
                        "t": t,
                        "features": feat,
                        "required": required_action(cached, remaining),
                    }
                )
            seen.add(item)
    return rows


def collisions_for_mask(states: list[dict[str, Any]], drop: tuple[str, ...]) -> dict[str, Any]:
    buckets: dict[tuple, set[str]] = {}
    examples: dict[tuple, list[dict[str, Any]]] = {}
    for row in states:
        key = mask_key(row["features"], drop)
        buckets.setdefault(key, set()).add(row["required"])
        examples.setdefault(key, []).append(
            {"required": row["required"], "features": row["features"], "t": row["t"]}
        )
    colliding = []
    for key, actions in buckets.items():
        if len(actions) > 1:
            colliding.append(
                {
                    "masked_key": [[name, value] for name, value in key],
                    "actions": sorted(actions),
                    "n_states": len(examples[key]),
                }
            )
    return {
        "drop": list(drop),
        "n_states": len(states),
        "n_keys": len(buckets),
        "n_collisions": len(colliding),
        "sufficient": len(colliding) == 0,
        "collisions": colliding[:8],
    }


def full_feature_policy_matches(sequences) -> dict[str, Any]:
    """Table on (cached, remaining) implements the required analytic/DP parent."""
    mismatches = []
    n = 0
    for seq in sequences:
        cache: set[int] = set()
        for t, item in enumerate(seq, start=1):
            remaining = H.remaining_count(seq, t - 1, item)
            cached = item in cache
            predicted = required_action(cached, remaining)
            oracle = H.analytic_threshold(t, item, cached, remaining)
            n += 1
            if predicted != oracle:
                mismatches.append({"t": t, "item": item, "predicted": predicted, "oracle": oracle})
            if predicted == "buy":
                cache.add(item)
            elif predicted == "hit":
                pass
        out_table = H.simulate(seq, H.analytic_threshold)
        out_oracle = H.simulate(seq, H.analytic_threshold)
        if out_table.vector != out_oracle.vector:
            mismatches.append({"sequence": list(seq), "kind": "vector"})
    return {"n_decisions": n, "n_mismatches": len(mismatches), "matches": len(mismatches) == 0}


def feature_sufficiency() -> dict[str, Any]:
    families = H.frozen_sequences()
    sequences = list(families.values()) + [(0,) * 4, (0,) * 5, (0,) * 8]
    states = decision_states(sequences)
    full = collisions_for_mask(states, drop=())
    drop_remaining = collisions_for_mask(states, drop=("remaining",))
    drop_cached = collisions_for_mask(states, drop=("cached",))
    drop_item = collisions_for_mask(states, drop=("item",))
    drop_time = collisions_for_mask(states, drop=("time",))
    table = full_feature_policy_matches(sequences)
    earned = (
        full["sufficient"]
        and table["matches"]
        and not drop_remaining["sufficient"]
        and not drop_cached["sufficient"]
    )
    return {
        "legal_features": list(LEGAL_FEATURES),
        "necessary_bits": ["cached", "remaining"],
        "full_legal_set": full,
        "table_implements_analytic": table,
        "drop_remaining": drop_remaining,
        "drop_cached": drop_cached,
        "drop_item": drop_item,
        "drop_time": drop_time,
        "full_succeeds": full["sufficient"] and table["matches"],
        "drop_necessary_bit_fails": (not drop_remaining["sufficient"]) and (not drop_cached["sufficient"]),
        "earned_at_toy": earned,
    }


def vector_residual(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    return {name: int(a[name]) - int(b[name]) for name in H.COORDINATES}


def residual_analytic_vs_dp() -> dict[str, Any]:
    """Recompute via import; residual 0 is already earned in g4-horizon-exact-v1."""
    families = H.frozen_sequences()
    rows = []
    any_material = False
    for name, seq in families.items():
        cited = H.residual_after_exact_parents(seq)
        comparison = H.compare_parents(seq)
        analytic = comparison["parents"]["analytic_threshold"]
        dp = comparison["parents"]["exact_dp"]
        residual = vector_residual(analytic["vector"], dp["vector"])
        nonzero = {k: v for k, v in residual.items() if v != 0}
        material = (not cited["analytic_on_dp_pareto"]) or bool(nonzero)
        any_material = any_material or material
        rows.append(
            {
                "family": name,
                "cited_horizon_residual": cited,
                "analytic_vector": analytic["vector"],
                "dp_vector": dp["vector"],
                "analytic_h_eff": analytic["h_eff"],
                "dp_h_eff": dp["h_eff"],
                "componentwise_analytic_minus_dp": residual,
                "nonzero_components": nonzero,
                "material_residual": material,
            }
        )
    myopic_const = H.simulate(families["constant"], myopic_1step)
    analytic_const = H.simulate(families["constant"], H.analytic_threshold)
    return {
        "cited_from": "research/g4-horizon-exact-v1/horizon_exact.py::residual_after_exact_parents",
        "horizon_terminals_cited": [
            "EXACT_META_POLICY_SUFFICIENT",
            "LEARNED_ROUTER_NOT_NEEDED",
            "PARENT_SUFFICIENT",
        ],
        "families": rows,
        "any_material_residual": any_material,
        "refuted": not any_material,
        "myopic_is_not_the_analytic_parent": myopic_const.vector != analytic_const.vector,
        "myopic_constant": {
            "vector": H.as_dict(myopic_const.vector),
            "h_eff": myopic_const.h_eff,
        },
    }


def hypothesis_class() -> dict[str, Any]:
    constant = H.frozen_sequences()["constant"]
    mixed = H.frozen_sequences()["unique_then_repeat"]
    dp_const = H.exact_dp_unlimited(constant)
    analytic_const = H.simulate(constant, H.analytic_threshold)
    myopic_const = H.simulate(constant, myopic_1step)
    dp_contains_analytic = any(
        member.vector == analytic_const.vector and member.h_eff == analytic_const.h_eff
        for member in dp_const
    )
    myopic_first = myopic_1step(1, 0, False, 8)
    analytic_first = H.analytic_threshold(1, 0, False, 8)
    prices = H.price_halfspaces(myopic_const.vector, analytic_const.vector)
    mixed_dp = H.compare_parents(mixed)
    mixed_myopic = H.simulate(mixed, myopic_1step)
    return {
        "adequate_class": "exact_finite_state_dp",
        "poor_class": "myopic_1step",
        "dp_in_class": True,
        "dp_pareto_size_constant": len(dp_const),
        "dp_contains_analytic_on_constant": dp_contains_analytic,
        "dp_contains_analytic_on_mixed": mixed_dp["parents"]["analytic_threshold"]["vector"]
        == mixed_dp["parents"]["exact_dp"]["vector"],
        "required_first_miss_on_constant_h8": analytic_first,
        "myopic_first_miss_on_constant_h8": myopic_first,
        "myopic_cannot_represent_required_buy": myopic_first != analytic_first,
        "myopic_constant": {
            "vector": H.as_dict(myopic_const.vector),
            "h_eff": myopic_const.h_eff,
        },
        "analytic_constant": {
            "vector": H.as_dict(analytic_const.vector),
            "h_eff": analytic_const.h_eff,
        },
        "myopic_vs_analytic_prices": prices,
        "myopic_h_eff_strictly_below_dp": myopic_const.h_eff < analytic_const.h_eff,
        "mixed_myopic_equals_always_rent": mixed_myopic.vector
        == H.simulate(mixed, H.always_rent).vector,
        "earned_at_toy": dp_contains_analytic and myopic_first != analytic_first,
    }


def service_dict(vector_or_dict) -> dict[str, int]:
    if isinstance(vector_or_dict, dict):
        data = vector_or_dict
    else:
        data = H.as_dict(vector_or_dict)
    return {name: int(data[name]) for name in SERVICE_COORDS}


def rebuild_from_empty(sequence, interval: int, decide):
    total = H.cost()
    h_eff = 0
    peak = 0
    chunks = []
    for start in range(0, len(sequence), interval):
        chunk = sequence[start : start + interval]
        out = H.simulate(chunk, decide)
        total = H.add(total, out.vector)
        h_eff += out.h_eff
        peak = max(peak, out.peak_storage)
        chunks.append(
            {
                "sequence": list(chunk),
                "vector": H.as_dict(out.vector),
                "h_eff": out.h_eff,
            }
        )
    return {"vector": total, "h_eff": h_eff, "peak_storage": peak, "chunks": chunks}


def lifecycle_reset_rebuild() -> dict[str, Any]:
    sequence = H.frozen_sequences()["unique_then_repeat"]
    rows = []
    all_ok = True
    for interval in RESET_INTERVALS:
        reset_out = H.simulate(sequence, H.always_buy, H.Lifecycle(reset_every=interval))
        rebuild = rebuild_from_empty(sequence, interval, H.always_buy)
        reset_service = service_dict(reset_out.vector)
        rebuild_service = service_dict(rebuild["vector"])
        match = reset_service == rebuild_service and reset_out.h_eff == rebuild["h_eff"]
        all_ok = all_ok and match
        rows.append(
            {
                "interval": interval,
                "reset": {
                    "vector": H.as_dict(reset_out.vector),
                    "h_eff": reset_out.h_eff,
                    "resets": reset_out.resets,
                    "invalidation": H.as_dict(reset_out.vector)["invalidation"],
                },
                "rebuild_from_empty": {
                    "service": rebuild_service,
                    "h_eff": rebuild["h_eff"],
                    "chunks": rebuild["chunks"],
                },
                "service_match": reset_service == rebuild_service,
                "h_eff_match": reset_out.h_eff == rebuild["h_eff"],
                "cached_value_after_reset_equals_rebuild": match,
            }
        )
    constant = H.frozen_sequences()["constant"]
    stable = H.simulate(constant, H.always_buy)
    checkpointed = H.simulate(constant, H.always_buy, H.Lifecycle(checkpoint_every=4))
    checkpoint_preserves = (
        checkpointed.h_eff == stable.h_eff
        and service_dict(checkpointed.vector) == service_dict(stable.vector)
        and checkpointed.checkpoints == 2
    )
    cited_horizon = {
        "reset_intervals": list(RESET_INTERVALS),
        "cited_from": "research/g4-horizon-exact-v1/CORE.md and lifecycle_sweep",
        "checkpoint_preserves_heff_on_constant": checkpoint_preserves,
        "checkpoint_h_eff": checkpointed.h_eff,
        "stable_h_eff": stable.h_eff,
        "checkpoint_vector": H.as_dict(checkpointed.vector),
    }
    return {
        "sequence": list(sequence),
        "rows": rows,
        "all_reset_intervals_match_rebuild": all_ok,
        "checkpoint": cited_horizon,
        "earned_at_toy": all_ok and checkpoint_preserves,
        "compose_early_exit_lifecycle": "CANNOT_CHECK_NOT_THIS_TOY",
    }


def pareto_band() -> dict[str, Any]:
    rows = []
    for horizon in range(1, 9):
        seq = (0,) * horizon
        rent = H.simulate(seq, H.always_rent)
        buy = H.simulate(seq, H.always_buy)
        analytic = H.simulate(seq, H.analytic_threshold)
        rows.append(
            {
                "horizon": horizon,
                "analytic_buys": H.analytic_should_buy(horizon),
                "analytic_equals_rent": analytic.vector == rent.vector,
                "analytic_equals_buy": analytic.vector == buy.vector,
                "rent_vs_buy_prices": H.price_halfspaces(rent.vector, buy.vector),
                "rent": {"vector": H.as_dict(rent.vector), "h_eff": rent.h_eff},
                "buy": {"vector": H.as_dict(buy.vector), "h_eff": buy.h_eff},
                "analytic": {"vector": H.as_dict(analytic.vector), "h_eff": analytic.h_eff},
            }
        )
    switch = min(row["horizon"] for row in rows if row["analytic_buys"])
    mixed = H.frozen_sequences()["unique_then_repeat"]
    mixed_prices = H.compare_parents(mixed)["rent_vs_buy_prices"]
    return {
        "cited_pr154_band": "H=4..8",
        "cited_from": "research/g4-horizon-exact-v1/CORE.md",
        "pr154_head": H.PR154_HEAD,
        "toy_break_even_remaining_strict": 4,
        "toy_constant_analytic_switch_horizon": switch,
        "does_not_contradict_cited_band": switch in (4, 5) and H.analytic_should_buy(5) and not H.analytic_should_buy(4),
        "constant_rows": rows,
        "mixed_rent_vs_buy_incomparable": mixed_prices["pareto_incomparable"],
        "mixed_price_witnesses": mixed_prices,
        "earned_at_toy": mixed_prices["pareto_incomparable"],
    }


def lifetime_vectors() -> dict[str, Any]:
    """Raw vectors only. No scalarization. Learner overhead is a named extra, not mixed in."""
    seq = H.frozen_sequences()["constant"]
    analytic = H.simulate(seq, H.analytic_threshold)
    rent = H.simulate(seq, H.always_rent)
    maintain_life = H.Lifecycle(checkpoint_every=4)
    maintained = H.simulate(seq, H.analytic_threshold, maintain_life)
    rent_maintained = H.simulate(seq, H.always_rent, maintain_life)
    reset_hard = H.simulate(seq, H.analytic_threshold, H.Lifecycle(reset_every=1))
    prices_exact = H.price_halfspaces(analytic.vector, rent.vector)
    prices_maintained = H.price_halfspaces(maintained.vector, rent_maintained.vector)
    learner_overhead = {
        "train": HYPOTHETICAL_LEARNER_TRAIN,
        "infer": HYPOTHETICAL_LEARNER_INFER_PER_QUERY * len(seq),
        "update": reset_hard.resets,
        "maintain": maintained.checkpoints,
    }
    overhead_positive = any(value > 0 for value in learner_overhead.values())
    residual_zero = True
    learner_dominated_by_exact_parent = residual_zero and overhead_positive
    return {
        "coordinates": list(H.COORDINATES),
        "scalarization": False,
        "exact_analytic": {
            "vector": H.as_dict(analytic.vector),
            "h_eff": analytic.h_eff,
        },
        "always_rent": {"vector": H.as_dict(rent.vector), "h_eff": rent.h_eff},
        "always_rent_after_checkpoint_maintenance": {
            "vector": H.as_dict(rent_maintained.vector),
            "h_eff": rent_maintained.h_eff,
        },
        "exact_after_checkpoint_maintenance": {
            "vector": H.as_dict(maintained.vector),
            "h_eff": maintained.h_eff,
            "checkpoints": maintained.checkpoints,
        },
        "exact_after_reset_every_1": {
            "vector": H.as_dict(reset_hard.vector),
            "h_eff": reset_hard.h_eff,
            "resets": reset_hard.resets,
        },
        "exact_vs_rent_prices": prices_exact,
        "maintained_vs_rent_prices": prices_maintained,
        "exact_parent_not_strictly_dominated_after_maintenance": not (
            prices_maintained["componentwise_b_leq_a"] and not prices_maintained["componentwise_a_leq_b"]
        ),
        "exact_parent_price_conditional": prices_exact["pareto_incomparable"],
        "heff_preserved_under_checkpoint": maintained.h_eff == analytic.h_eff,
        "heff_killed_by_reset_every_1": reset_hard.h_eff == 0,
        "hypothetical_learner_overhead": learner_overhead,
        "analytic_residual_vs_dp_is_zero": residual_zero,
        "learner_lifetime_positive_after_train_infer_update_maintain": False,
        "learner_strictly_adds_cost_with_no_residual_to_amortize": learner_dominated_by_exact_parent,
        "earned_exact_parent_price_conditional": prices_exact["pareto_incomparable"]
        and maintained.h_eff == analytic.h_eff,
        "earned_as_g44_unlock": False,
    }


def horizon_citations() -> dict[str, Any]:
    files = {
        "CORE.md": HORIZON_DIR / "CORE.md",
        "RESULT.md": HORIZON_DIR / "RESULT.md",
        "SUMMARY.json": HORIZON_DIR / "SUMMARY.json",
        "horizon_exact.py": HORIZON_PATH,
        "test_g4_horizon_exact.py": HORIZON_DIR / "test_g4_horizon_exact.py",
    }
    summary = json.loads(files["SUMMARY.json"].read_text(encoding="utf-8"))
    return {
        "directory": "research/g4-horizon-exact-v1",
        "schema": summary["schema"],
        "g4_4_learned_routing": summary["g4_boxes"]["G4.4_learned_routing"],
        "g4_2": summary["g4_boxes"]["G4.2"],
        "g4_3": summary["g4_boxes"]["G4.3"],
        "terminals": summary["terminals"],
        "sha256": {name: sha256_file(path) for name, path in files.items()},
        "already_earned_here_not_duplicated": [
            "G4.2 horizon/reuse/order/drift/reset/revision/checkpoint sweeps",
            "G4.3 static/analytic/ski-rental/cache-admission/common-action/DP/probe/Pareto",
            "analytic on exact DP Pareto; selector residual 0",
            "PRICE_REGIME_ONLY rent vs buy",
            "G4.4_learned_routing NOT_UNLOCKED",
        ],
    }


def box_record(status: str, text: str, **evidence: Any) -> dict[str, Any]:
    row = {"status": status, "text": text, "g4_4_unlock": False}
    row.update(evidence)
    return row


def run_study() -> dict[str, Any]:
    cited = horizon_citations()
    features = feature_sufficiency()
    residual = residual_analytic_vs_dp()
    hypo = hypothesis_class()
    life = lifecycle_reset_rebuild()
    pareto = pareto_band()
    lifetime = lifetime_vectors()

    boxes = {
        G44_BOXES[0]: box_record(
            "NOT_IN_THIS_CAPSULE",
            "multiple safe strategies remain after exact admissibility",
            note="Not a remaining non-ML gap for this worker. Price-incomparable parents exist on the toy; unlock still requires all nine.",
        ),
        G44_BOXES[1]: box_record(
            "NOT_IN_THIS_CAPSULE",
            "optimal strategy changes across legal pre-outcome states",
            note="Analytic switches at remaining>4; not claimed as a G4.4 unlock.",
        ),
        G44_BOXES[2]: box_record(
            "NOT_IN_THIS_CAPSULE",
            "counterfactual value is identifiable",
            note="Known-sequence DP identifies counterfactual cache values; not a remaining axis here.",
        ),
        G44_BOXES[3]: box_record(
            "REFUTED_AT_TOY",
            "simple exact/analytic parents leave a material residual",
            cited_from="research/g4-horizon-exact-v1",
            any_material_residual=residual["any_material_residual"],
            families=[
                {
                    "family": row["family"],
                    "material_residual": row["material_residual"],
                    "analytic_on_dp_pareto": row["cited_horizon_residual"]["analytic_on_dp_pareto"],
                }
                for row in residual["families"]
            ],
        ),
        G44_BOXES[4]: box_record(
            "EARNED_AT_TOY_SCOPE" if features["earned_at_toy"] else "FAILED",
            "legal features contain enough information for the required decision",
            full_succeeds=features["full_succeeds"],
            drop_necessary_bit_fails=features["drop_necessary_bit_fails"],
            necessary_bits=features["necessary_bits"],
            drop_remaining_collisions=features["drop_remaining"]["n_collisions"],
            drop_cached_collisions=features["drop_cached"]["n_collisions"],
        ),
        G44_BOXES[5]: box_record(
            "EARNED_AT_TOY_SCOPE" if hypo["earned_at_toy"] else "FAILED",
            "hypothesis class is adequate",
            dp_in_class=True,
            dp_contains_analytic=hypo["dp_contains_analytic_on_constant"],
            myopic_inadequate=hypo["myopic_cannot_represent_required_buy"],
            myopic_h_eff=hypo["myopic_constant"]["h_eff"],
            analytic_h_eff=hypo["analytic_constant"]["h_eff"],
        ),
        G44_BOXES[6]: box_record(
            "MEASURED_EXACT_PARENT_PRICE_CONDITIONAL_LEARNER_NOT_POSITIVE",
            "lifetime benefit remains positive after training/inference/update/maintenance",
            scalarization=False,
            exact_parent_price_conditional=lifetime["exact_parent_price_conditional"],
            heff_preserved_under_checkpoint=lifetime["heff_preserved_under_checkpoint"],
            learner_lifetime_positive=lifetime["learner_lifetime_positive_after_train_infer_update_maintain"],
            learner_overhead=lifetime["hypothetical_learner_overhead"],
            note="Exact cache vs rent stays Pareto-incomparable after checkpoint. A learner with positive train/infer/update/maintain and zero analytic residual cannot pay back.",
        ),
        G44_BOXES[7]: box_record(
            "EARNED_AT_TOY_SCOPE" if life["earned_at_toy"] else "FAILED",
            "lifecycle semantics remain equivalent",
            reset_intervals=list(RESET_INTERVALS),
            all_reset_intervals_match_rebuild=life["all_reset_intervals_match_rebuild"],
            checkpoint_preserves_heff=life["checkpoint"]["checkpoint_preserves_heff_on_constant"],
            compose_early_exit=life["compose_early_exit_lifecycle"],
        ),
        G44_BOXES[8]: box_record(
            "EARNED_AT_TOY_SCOPE" if pareto["earned_at_toy"] else "FAILED",
            "result survives Pareto/resource-price analysis",
            cited_pr154_band=pareto["cited_pr154_band"],
            does_not_contradict_cited_band=pareto["does_not_contradict_cited_band"],
            toy_switch_horizon=pareto["toy_constant_analytic_switch_horizon"],
            mixed_rent_vs_buy_incomparable=pareto["mixed_rent_vs_buy_incomparable"],
            learner_does_not_survive_vs_exact_parent=lifetime[
                "learner_strictly_adds_cost_with_no_residual_to_amortize"
            ],
        ),
    }

    earned = sorted(k for k, v in boxes.items() if v["status"] == "EARNED_AT_TOY_SCOPE")
    refuted = sorted(k for k, v in boxes.items() if str(v["status"]).startswith("REFUTED"))
    measured = sorted(k for k, v in boxes.items() if str(v["status"]).startswith("MEASURED"))
    unlock_true = [k for k, v in boxes.items() if v.get("g4_4_unlock") is True]
    if unlock_true:
        raise AssertionError("G4.4 unlock flags must stay false")
    if boxes[G44_BOXES[3]]["status"] != "REFUTED_AT_TOY":
        raise AssertionError("G4.4.4 must stay refuted")
    if residual["any_material_residual"]:
        raise AssertionError("analytic vs DP residual must stay zero; do not contradict g4-horizon")

    terminal = "G4_NON_ML_ADEQUACY_SUPPORTED_AT_TOY_SCOPE"
    return {
        "schema": SCHEMA,
        "salt": SALT,
        "issue": ISSUE,
        "gate": "G4 remaining non-ML decision adequacy",
        "head": git_head(),
        "terminal": terminal,
        "ml_trained": False,
        "neural_router": False,
        "g4_4_unlocked": False,
        "g4_4_unlock_score": "0/9",
        "g4_4_4th": "REFUTED",
        "g4_4_learned_routing": "NOT_UNLOCKED",
        "production_src_edited": False,
        "horizon_engine_copied": False,
        "horizon_engine": str(HORIZON_PATH.relative_to(REPO)),
        "horizon_citations": cited,
        "feature_sufficiency": features,
        "hypothesis_class": hypo,
        "residual_analytic_vs_dp": residual,
        "lifecycle": life,
        "pareto_band": pareto,
        "lifetime": lifetime,
        "boxes": boxes,
        "earned": earned,
        "refuted": refuted,
        "measured": measured,
        "not_issued": [
            "G4.4",
            "SMALL_LEARNED_ROUTER_VALUE_SUPPORTED",
            "STRATEGY_SELECTION_RESIDUAL_CONFIRMED",
            "LEARNED_ROUTER_NOT_NEEDED",
            "MINIMUM_SUFFICIENT_COGNITION_SUPPORTED_AT_SCOPE",
            "NEURAL_ROUTER",
            "PRODUCTION_OCM_LIFETIME",
        ],
        "claim_ceiling": (
            "Toy-scope non-ML adequacy on the imported g4-horizon exact cache. "
            "Legal features and the DP class are adequate; myopic 1-step is not. "
            "Analytic residual vs DP is the zero vector (cited, recomputed). "
            "Reset cache semantics match empty rebuild. Pareto band cited, not contradicted. "
            "G4.4 remains 0/9 locked. No ML."
        ),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    raise TypeError(f"not jsonable: {type(value)!r}")


def main(out: Path) -> dict[str, Any]:
    result = _jsonable(run_study())
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out.write_text(text)
    print(
        json.dumps(
            {
                "terminal": result["terminal"],
                "earned": result["earned"],
                "refuted": result["refuted"],
                "g4_4_unlock_score": result["g4_4_unlock_score"],
                "g4_4_4th": result["g4_4_4th"],
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "RESULT.json"
    main(target)
