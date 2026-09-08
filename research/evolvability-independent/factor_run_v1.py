from __future__ import annotations
import argparse, json, statistics
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Sequence
from factor_core_v1 import *
from factor_arms_v1 import *
def run_seed(seed: int, regime: str) -> dict:
    world = World.make(seed, regime)
    arms = [FactorLocal(), SymbolicIncremental(), LazySymbolic(), GlobalRefit(), ResetFactor()]
    surrogate = SurrogateParent()
    evo_models: list[Model] = [tuple() for _ in range(ACTIONS)]
    evo_cost = Cost()
    cumulative_train: list[Episode] = []
    generations = []
    for g in range(1, GENERATIONS + 1):
        world.advance(g)
        train = episodes(world, seed, regime, g, "train", TRAIN_N)
        fresh = episodes(world, seed, regime, g, "eval", EVAL_N)
        cumulative_train.extend(train)
        oracle = tuple(world.supports)
        ident = identifiable_supports(train, oracle)

        rows = {"seed": seed, "regime": regime, "generation": g, "arms": {}}
        for arm in arms:
            before = arm.cost.as_dict()
            arm.update(train, g)
            if isinstance(arm, LazySymbolic):
                arm.materialize()
            eval_cost = Cost()
            acc, _ = predict_actions(arm.models, fresh, eval_cost)
            arm.cost.prediction_literal_evals += eval_cost.prediction_literal_evals
            sp, sr, sf1, nident = exact_support_metrics(arm.models, oracle, ident)
            rp, rr = relevance_metrics(arm.models, oracle)
            delta = {k: arm.cost.as_dict()[k] - before[k] for k in before}
            rel_cache = arm.relevance if isinstance(arm, FactorLocal) and arm.name != "symbolic_incremental_parent" else None
            rows["arms"][arm.name] = {
                "heldout_accuracy": acc,
                "support_precision": sp,
                "support_recall": sr,
                "support_f1": sf1,
                "identifiable_supports": nident,
                "relevance_precision": rp,
                "relevance_recall": rr,
                **delta,
                "state_bytes": state_bytes(arm.models, rel_cache),
                "effective_coupling": delta["update_components_touched"] / ACTIONS,
            }

        before = surrogate.cost.as_dict()
        surrogate.update(train, g)
        acc = surrogate.accuracy(fresh)
        delta = {k: surrogate.cost.as_dict()[k] - before[k] for k in before}
        rows["arms"][surrogate.name] = {
            "heldout_accuracy": acc,
            "support_precision": None, "support_recall": None, "support_f1": None,
            "identifiable_supports": sum(map(len, ident)),
            "relevance_precision": None, "relevance_recall": None,
            **delta, "state_bytes": surrogate.size(),
            "effective_coupling": delta["update_components_touched"] / ACTIONS,
        }

        global_budget = max(1, rows["arms"]["global_refit_parent"]["primitive_literal_evals"] // ACTIONS)
        erng = rng_for(seed, f"evolution|{regime}|g{g}")
        before_e = evo_cost.as_dict()
        evo_models = []
        for a in range(ACTIONS):
            m, c = evolutionary_fit(train, a, erng, global_budget)
            evo_models.append(m)
            evo_cost.add(c)
        ec = Cost()
        eacc, _ = predict_actions(evo_models, fresh, ec)
        evo_cost.prediction_literal_evals += ec.prediction_literal_evals
        sp, sr, sf1, nident = exact_support_metrics(evo_models, oracle, ident)
        rp, rr = relevance_metrics(evo_models, oracle)
        delta_e = {k: evo_cost.as_dict()[k] - before_e[k] for k in before_e}
        rows["arms"]["evolutionary_parent"] = {
            "heldout_accuracy": eacc, "support_precision": sp, "support_recall": sr,
            "support_f1": sf1, "identifiable_supports": nident,
            "relevance_precision": rp, "relevance_recall": rr,
            **delta_e, "state_bytes": state_bytes(evo_models),
            "effective_coupling": delta_e["update_components_touched"] / ACTIONS,
        }

        loo = loo_relevance(train)
        true_rel = {i for supports in oracle for c in supports for i in c}
        tp = len(loo & true_rel)
        rows["arms"]["loo_dependency_ablation"] = {
            "heldout_accuracy": None, "support_precision": None, "support_recall": None, "support_f1": None,
            "identifiable_supports": sum(map(len, ident)),
            "relevance_precision": tp/len(loo) if loo else 0.0,
            "relevance_recall": tp/len(true_rel) if true_rel else 1.0,
            "primitive_literal_evals": 0, "induction_candidates": 0, "update_components_touched": ACTIONS,
            "prediction_literal_evals": 0, "validation_examples": 0, "maintenance_ops": D*ACTIONS,
            "rediscovery_ops": ACTIONS, "state_bytes": len(json.dumps(sorted(loo)).encode()),
            "effective_coupling": 1.0,
        }
        generations.append(rows)
    return {"seed": seed, "regime": regime, "generations": generations}


def median(xs: Sequence[float]) -> float | None:
    return statistics.median(xs) if xs else None


def summarize(results: Sequence[dict]) -> dict:
    regimes = sorted({r["regime"] for r in results})
    out = {}
    for regime in regimes:
        subset = [r for r in results if r["regime"] == regime]
        arm_names = sorted(subset[0]["generations"][0]["arms"])
        out[regime] = {}
        for arm in arm_names:
            final_rows = [r["generations"][-1]["arms"][arm] for r in subset]
            life_rows = [g["arms"][arm] for r in subset for g in r["generations"]]
            out[regime][arm] = {
                "g8_median_accuracy": median([x["heldout_accuracy"] for x in final_rows if x["heldout_accuracy"] is not None]),
                "g8_median_support_f1": median([x["support_f1"] for x in final_rows if x["support_f1"] is not None]),
                "g8_median_effective_coupling": median([x["effective_coupling"] for x in final_rows]),
                "lifetime_median_effective_coupling": median([x["effective_coupling"] for x in life_rows]),
                "lifetime_primitive_literal_evals_median_per_seed": median([
                    sum(g["arms"][arm]["primitive_literal_evals"] for g in r["generations"]) for r in subset]),
                "lifetime_maintenance_ops_median_per_seed": median([
                    sum(g["arms"][arm]["maintenance_ops"] for g in r["generations"]) for r in subset]),
                "g8_median_state_bytes": median([x["state_bytes"] for x in final_rows]),
            }
        wins = 0
        equal_or_parent = 0
        for r in subset:
            f = r["generations"][-1]["arms"]["factor_local"]
            p = r["generations"][-1]["arms"]["symbolic_incremental_parent"]
            fwork = sum(g["arms"]["factor_local"]["primitive_literal_evals"] + g["arms"]["factor_local"]["maintenance_ops"] for g in r["generations"])
            pwork = sum(g["arms"]["symbolic_incremental_parent"]["primitive_literal_evals"] + g["arms"]["symbolic_incremental_parent"]["maintenance_ops"] for g in r["generations"])
            if f["heldout_accuracy"] >= p["heldout_accuracy"] - 0.01 and fwork < pwork and f["state_bytes"] <= p["state_bytes"]:
                wins += 1
            else:
                equal_or_parent += 1
        out[regime]["factor_vs_strongest_parent"] = {"factor_vector_wins": wins, "parent_equal_or_better": equal_or_parent, "n": len(subset)}
    return out


def _run_task(task: tuple[int, str]) -> dict:
    return run_seed(task[0], task[1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8")
    ap.add_argument("--regimes", default="sparse_stable,dense,drift")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=1)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s]
    regimes = [s for s in args.regimes.split(",") if s]
    tasks = [(seed, regime) for seed in seeds for regime in regimes]
    if args.jobs > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as ex:
            results = list(ex.map(_run_task, tasks))
    else:
        results = [run_seed(seed, regime) for seed, regime in tasks]
    payload = {
        "experiment": "E150-factorization-survival-v1",
        "seeds": seeds,
        "regimes": regimes,
        "constants": {"D": D, "actions": ACTIONS, "generations": GENERATIONS, "train_n": TRAIN_N, "eval_n": EVAL_N, "max_width": MAX_WIDTH},
        "results": results,
        "summary": summarize(results),
        "neural_parent": "CANNOT_CHECK_NEURAL_MATCHED",
        "note": "No task ID, regime label, seed, hidden support, cause label, donor identity or routing key is learner-visible.",
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
