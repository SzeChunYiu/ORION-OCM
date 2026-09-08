from __future__ import annotations
import argparse, json, statistics
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Sequence
from factor_core_v2 import *
from factor_arms_v2 import *

def run_seed(seed: int, regime: str) -> dict:
    world = World.make(seed, regime)
    arms = [FactorLocal(), SymbolicCompact(), SymbolicMemory(), LazySymbolic(), GlobalRefit(), ResetFactor()]
    surrogate = SurrogateParent()
    evo_cost = Cost()
    generations = []
    for g in range(1, GENERATIONS + 1):
        world.advance(g)
        train = episodes(world, seed, regime, g, "train", TRAIN_N)
        fresh = episodes(world, seed, regime, g, "eval", EVAL_N)
        oracle = tuple(world.supports)
        ident = identifiable_supports(train, oracle)
        row = {"seed": seed, "regime": regime, "generation": g, "arms": {}}
        for arm in arms:
            before = arm.cost.as_dict()
            arm.update(train, g)
            if isinstance(arm, LazySymbolic):
                arm.materialize()
            ec = Cost(); acc, _ = predict_actions(arm.models, fresh, ec)
            arm.cost.prediction_literal_evals += ec.prediction_literal_evals
            sp, sr, sf1, nident = exact_support_metrics(arm.models, oracle, ident)
            rp, rr = relevance_metrics(arm.models, oracle)
            delta = {k: arm.cost.as_dict()[k] - before[k] for k in before}
            row["arms"][arm.name] = {
                "heldout_accuracy": acc, "support_precision": sp, "support_recall": sr, "support_f1": sf1,
                "identifiable_supports": nident, "relevance_precision": rp, "relevance_recall": rr,
                **delta, "state_bytes": retained_state_bytes(arm),
                "effective_coupling": delta["update_components_touched"] / ACTIONS,
            }
        before = surrogate.cost.as_dict(); surrogate.update(train, g); acc = surrogate.accuracy(fresh)
        delta = {k: surrogate.cost.as_dict()[k] - before[k] for k in before}
        row["arms"][surrogate.name] = {
            "heldout_accuracy": acc, "support_precision": None, "support_recall": None, "support_f1": None,
            "identifiable_supports": sum(map(len, ident)), "relevance_precision": None, "relevance_recall": None,
            **delta, "state_bytes": surrogate.size(), "effective_coupling": delta["update_components_touched"] / ACTIONS,
        }
        global_budget = max(1, row["arms"]["global_refit_parent"]["primitive_literal_evals"] // ACTIONS)
        erng = rng_for(seed, f"evolution|{regime}|g{g}"); before_e = evo_cost.as_dict(); evo_models = []
        for a in range(ACTIONS):
            m, c = evolutionary_fit(train, a, erng, global_budget); evo_models.append(m); evo_cost.add(c)
        ec = Cost(); eacc, _ = predict_actions(evo_models, fresh, ec); evo_cost.prediction_literal_evals += ec.prediction_literal_evals
        sp, sr, sf1, nident = exact_support_metrics(evo_models, oracle, ident); rp, rr = relevance_metrics(evo_models, oracle)
        de = {k: evo_cost.as_dict()[k] - before_e[k] for k in before_e}
        row["arms"]["evolutionary_parent"] = {
            "heldout_accuracy": eacc, "support_precision": sp, "support_recall": sr, "support_f1": sf1,
            "identifiable_supports": nident, "relevance_precision": rp, "relevance_recall": rr,
            **de, "state_bytes": state_bytes(evo_models), "effective_coupling": de["update_components_touched"] / ACTIONS,
        }
        loo = loo_relevance(train); true_rel = {i for supports in oracle for c in supports for i in c}; tp = len(loo & true_rel)
        row["arms"]["loo_dependency_ablation"] = {
            "heldout_accuracy": None, "support_precision": None, "support_recall": None, "support_f1": None,
            "identifiable_supports": sum(map(len, ident)), "relevance_precision": tp/len(loo) if loo else 0.0,
            "relevance_recall": tp/len(true_rel) if true_rel else 1.0, "primitive_literal_evals": 0,
            "induction_candidates": 0, "update_components_touched": ACTIONS, "prediction_literal_evals": 0,
            "validation_examples": 0, "maintenance_ops": D*ACTIONS, "rediscovery_ops": ACTIONS,
            "state_bytes": len(json.dumps(sorted(loo)).encode()), "effective_coupling": 1.0,
        }
        generations.append(row)
    return {"seed": seed, "regime": regime, "generations": generations}

def median(xs: Sequence[float]) -> float | None:
    return statistics.median(xs) if xs else None

def _life_work(r, arm):
    return sum(g["arms"][arm]["primitive_literal_evals"] + g["arms"][arm]["maintenance_ops"] for g in r["generations"])

def _dominates(parent, factor, pwork, fwork):
    sfp, sff = parent["support_f1"], factor["support_f1"]
    support_ok = sff is None or sfp is None or sfp >= sff - 0.01
    return (parent["heldout_accuracy"] >= factor["heldout_accuracy"] - 0.01 and support_ok
            and parent["effective_coupling"] <= factor["effective_coupling"]
            and pwork <= fwork and parent["state_bytes"] <= factor["state_bytes"]
            and (pwork < fwork or parent["state_bytes"] < factor["state_bytes"]
                 or parent["effective_coupling"] < factor["effective_coupling"]))

def summarize(results: Sequence[dict]) -> dict:
    out = {}
    for regime in sorted({r["regime"] for r in results}):
        subset = [r for r in results if r["regime"] == regime]; out[regime] = {}
        for arm in sorted(subset[0]["generations"][0]["arms"]):
            finals = [r["generations"][-1]["arms"][arm] for r in subset]
            life = [g["arms"][arm] for r in subset for g in r["generations"]]
            out[regime][arm] = {
                "g8_median_accuracy": median([x["heldout_accuracy"] for x in finals if x["heldout_accuracy"] is not None]),
                "g8_median_support_f1": median([x["support_f1"] for x in finals if x["support_f1"] is not None]),
                "g8_median_effective_coupling": median([x["effective_coupling"] for x in finals]),
                "lifetime_median_effective_coupling": median([x["effective_coupling"] for x in life]),
                "lifetime_primitive_literal_evals_median_per_seed": median([sum(g["arms"][arm]["primitive_literal_evals"] for g in r["generations"]) for r in subset]),
                "lifetime_maintenance_ops_median_per_seed": median([sum(g["arms"][arm]["maintenance_ops"] for g in r["generations"]) for r in subset]),
                "g8_median_state_bytes": median([x["state_bytes"] for x in finals]),
            }
        dom = {"symbolic_compact_parent": 0, "symbolic_incremental_memory_parent": 0, "any_symbolic_parent": 0}
        for r in subset:
            f = r["generations"][-1]["arms"]["factor_local"]; fw = _life_work(r, "factor_local"); any_dom = False
            for name in ("symbolic_compact_parent", "symbolic_incremental_memory_parent"):
                p = r["generations"][-1]["arms"][name]; d = _dominates(p, f, _life_work(r, name), fw)
                dom[name] += int(d); any_dom |= d
            dom["any_symbolic_parent"] += int(any_dom)
        dom["n"] = len(subset); out[regime]["factor_vs_symbolic_frontier"] = dom
    return out

def _run_task(t): return run_seed(t[0], t[1])

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--seeds",default="1,2,3,4,5,6,7,8"); ap.add_argument("--regimes",default="sparse_stable,dense,drift"); ap.add_argument("--out",required=True); ap.add_argument("--jobs",type=int,default=1); a=ap.parse_args()
    seeds=[int(x) for x in a.seeds.split(",") if x]; regimes=[x for x in a.regimes.split(",") if x]; tasks=[(s,r) for s in seeds for r in regimes]
    if a.jobs>1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex: results=list(ex.map(_run_task,tasks))
    else: results=[_run_task(t) for t in tasks]
    payload={"experiment":"E150-factorization-survival-v2","seeds":seeds,"regimes":regimes,"constants":{"D":D,"actions":ACTIONS,"generations":GENERATIONS,"train_n":TRAIN_N,"eval_n":EVAL_N,"max_width":MAX_WIDTH},"results":results,"summary":summarize(results),"neural_parent":"CANNOT_CHECK_NEURAL_MATCHED","note":"No task ID, regime label, seed, hidden support, cause label, donor identity or routing key is learner-visible."}
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n"); print(json.dumps(payload["summary"],indent=2,sort_keys=True))
if __name__ == "__main__": main()
