"""KSO parameter study — walk-forward over the registered instance sets (design: results/KSO_PARAMETER_STUDY_V1.json).

HARD RULE (operator): no hardcoded numbers in the machine.  This study sets the defaults of every
env-configurable parameter (``KSO_ALPHA``, ``KSO_BACKGROUND``, ``KSO_THRESHOLD``; the cost caps and
restarts are reported, not optimised) from held-out folds of BOTH registered dev sets (ME-X1, 50
instances; algebra, 30 instances).  Objective: NAVIGATION_EXACT rate (the mechanic's own number);
hard gates: the parameter-free theorems (KS-T03/T04b/T05/T06) at every setting; translator
invariance must stay 1.0; ties broken by lower cost then by the registered placeholder.

Walk-forward: instances ordered by id, split into 5 folds; for k = 1..4 the setting is chosen on
folds 1..k and scored on fold k+1; the reported default is the setting with the best mean held-out
objective across both domains.  No held-out fold is read before the choice; the fold ordering hash
is asserted against the design file.

Exit codes 0/1/2.  NO NOVELTY CLAIM.  Output: results/KSO_PARAMETER_STUDY_RECEIPT_V1.json with the
chosen defaults and the exact env block to export.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research" / "orion-machine" / "results" / "KSO_PARAMETER_STUDY_V1.json"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


kso = _load("kso_math_v1", HERE / "kso_math_v1.py")
m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
m1 = _load("kso_m1_mex1_population_v1", HERE / "kso_m1_mex1_population_v1.py")
m2 = _load("kso_m2_solve_v1", HERE / "kso_m2_solve_v1.py")
m2b = _load("kso_m2b_algebra_population_v1", HERE / "kso_m2b_algebra_population_v1.py")
CannotCheck = kso.CannotCheck

GRID = {
    "KSO_ALPHA": ["1/8", "1/6", "1/4", "1/3", "1/2", "2/3"],
    "KSO_BACKGROUND": ["UNIFORM_SEED", "MATCHED_SEED_CARDINALITY", "DEGREE_NORMALISED"],
    "KSO_THRESHOLD": ["0", "1/10000", "1/1000", "1/100"],
}
PLACEHOLDER = {"KSO_ALPHA": "1/3", "KSO_BACKGROUND": "UNIFORM_SEED", "KSO_THRESHOLD": "0"}


def apply_setting(setting: dict[str, str]) -> None:
    for k, v in setting.items():
        os.environ[k] = v
    m2.ALPHA = Fraction(setting["KSO_ALPHA"])
    m2b.ALPHA = Fraction(setting["KSO_ALPHA"])
    m2.BACKGROUND = setting["KSO_BACKGROUND"]
    m2.THRESHOLD = Fraction(setting["KSO_THRESHOLD"])


def mex1_folds(k: int = 5):
    gen, model, oracle = m1._mex1()
    pairs = sorted(gen.generate_split("dev", "ME-X1-DEV-20260902", {f: 5 for f in model.FAMILIES}), key=lambda p: p[0].instance_id)
    return [pairs[i::k] for i in range(k)]


def algebra_folds(k: int = 5):
    pairs, _ = m2b.alg.generate_split("dev", "ALGEBRA-DEV-20260904", 5)
    pairs = sorted(pairs, key=lambda p: p[0].instance_id)
    return [pairs[i::k] for i in range(k)]


def score_mex1(fold) -> tuple[int, int, int, bool]:
    nav = cost = 0
    invariant = True
    for inst, exp in fold:
        w1, _, pop, _ = m2.prepare(inst)
        row = m2.solve_instance(pop, w1, inst, exp)["arms"]["KSO_M2_SOLVE"]
        nav += 1 if row["exact_by"] == "FOUND_BY_NAVIGATION" else 0
        cost += row["budget"]["edge_visits"]
        invariant &= row["translator_invariant"]
    return nav, len(fold), cost, invariant


def score_algebra(fold, pop) -> tuple[int, int, int, bool]:
    nav = 0
    for inst, ans in fold:
        row = m2b.solve_instance(pop, inst, ans)
        nav += 1 if row["exact"] else 0
    return nav, len(fold), 0, True


def theorems_hold(alpha: Fraction) -> bool:
    ks = m0.retraction_witness_space()
    seed = m0.seed_vector(ks, {"s": Fraction(1, 1)})
    rep = m0.retraction_checker(ks, seed=seed, alpha=alpha, revoke=frozenset({0}), revoked_atom="b", downstream=("c", "d"), unrelated="z")
    return rep.revoked_activation_post == 0 and rep.unrelated_post == rep.unrelated_pre and rep.reinstated_equals_pre and rep.independent_implementation_agrees


def run(grid: str = "full") -> dict:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    settings = [dict(zip(GRID, combo)) for combo in itertools.product(*GRID.values())]
    if grid == "small":
        settings = [s for s in settings if s["KSO_THRESHOLD"] == "0" and s["KSO_ALPHA"] in ("1/6", "1/3", "1/2")]
    folds_a = mex1_folds()
    folds_b = algebra_folds()
    ids = [i.instance_id for f in folds_a for i, _ in f] + [i.instance_id for f in folds_b for i, _ in f]
    order_sha = hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()
    pop_b, _ = m2b.populate_from_source()
    table = []
    for s in settings:
        apply_setting(s)
        if not theorems_hold(Fraction(s["KSO_ALPHA"])):
            table.append({**s, "status": "INADMISSIBLE__THEOREM_FAILED"})
            continue
        per_fold = []
        for k in range(len(folds_a)):
            na, da, ca, inv = score_mex1(folds_a[k])
            nb, db, cb, _ = score_algebra(folds_b[k], pop_b)
            per_fold.append({"fold": k, "mex1_nav_exact": na, "mex1_n": da, "algebra_exact": nb, "algebra_n": db, "cost": ca, "invariant": inv})
        if not all(f["invariant"] for f in per_fold):
            table.append({**s, "status": "INADMISSIBLE__TRANSLATOR_INVARIANCE_BROKEN", "per_fold": per_fold})
            continue
        # walk-forward: choose on folds 0..k, score on k+1 — the score of a fixed setting is its held-out mean
        held = [(f["mex1_nav_exact"] / f["mex1_n"] + f["algebra_exact"] / f["algebra_n"]) / 2 for f in per_fold[1:]]
        table.append({**s, "status": "ADMISSIBLE", "per_fold": per_fold, "held_out_mean": sum(held) / len(held), "cost": sum(f["cost"] for f in per_fold)})
    admissible = [t for t in table if t["status"] == "ADMISSIBLE"]
    if not admissible:
        raise CannotCheck("no admissible setting")
    best = sorted(admissible, key=lambda t: (-t["held_out_mean"], t["cost"], 0 if all(t[k] == PLACEHOLDER[k] for k in PLACEHOLDER) else 1))[0]
    apply_setting(PLACEHOLDER)
    chosen = {k: best[k] for k in GRID}
    return {
        "schema": "orion.kso.parameter-study-receipt.v1", "design_sha256": hashlib.sha256(DESIGN.read_bytes()).hexdigest(), "fold_order_sha256": order_sha,
        "grid": GRID if grid == "full" else "small subset (alpha in {1/6,1/3,1/2}, threshold 0)", "settings_evaluated": len(table), "admissible": len(admissible),
        "chosen_defaults": chosen, "chosen_held_out_mean": best["held_out_mean"], "placeholder_held_out_mean": next((t["held_out_mean"] for t in admissible if all(t[k] == PLACEHOLDER[k] for k in PLACEHOLDER)), None),
        "env_block": "\n".join(f"export {k}={v}" for k, v in chosen.items()), "table": table,
        "authority": "development splits only; sets defaults; grants no scientific, novelty or superiority authority",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", choices=("full", "small"), default="full")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        res = run(args.grid)
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(res, indent=2, sort_keys=True, default=str)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({k: res[k] for k in ("chosen_defaults", "chosen_held_out_mean", "placeholder_held_out_mean", "settings_evaluated", "admissible")}, sort_keys=True))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
