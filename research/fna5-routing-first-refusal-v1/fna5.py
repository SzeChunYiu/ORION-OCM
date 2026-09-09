"""FNA-5/D7 driver: non-neural routing FIRST-REFUSAL study over the operator-selection world.

Ladder evaluated in order A1 -> A2 -> A3a -> A3b -> A4 -> A5; the smallest arm meeting the
FROZEN sufficiency criterion wins first refusal; A6 is a neural diagnostic with no adoption
authority. Controls: incumbent first-PASS baseline (clean, never degraded), oracle upper
bound (labelled, never a result), shuffle-equal-n null per learned arm. Full lifecycle
charging: feature extraction, model build, per-query inference, drift maintenance, index
rebuilds, persistent model bytes. No free preprocessing.

Deterministic under the frozen salt. Python 3.8 stdlib only. Research-only: no production
source touched, no router deployed, #71 stays LEARNED_ROUTER_NOT_YET_AUTHORIZED.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import inspect
import json
import platform
import random
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

import fna5_world as W
import fna5_selectors as S

EPS_MARGIN = 0.05      # frozen non-inferiority margin on total charged work
PASS_FLOOR = 0.98      # frozen first-attempt pass floor (oracle = 1.0 by construction)
MAINT_WINDOW = 240     # frozen drift maintenance window (tiny: 60)
LADDER = ["A1_ANALYTIC_GUARDED", "A2_COST_MODEL", "A3A_KNN", "A3B_LOGISTIC",
          "A4_TREE", "A5_LINUCB"]
FORBIDDEN = ("TRANSFORMER_REPLACED", "LLM_EQUIVALENT", "GENERAL_SUPERIORITY", "AGI",
             "ROUTER_AUTHORIZED", "DEPLOYED")


def evaluate_rows(world, records, arm_name, rowfn, build_work=0):
    """rowfn(rec) -> row from W.run_arm_choice / W.run_baseline; aggregates one arm block."""
    rows = [rowfn(rec) for rec in records]
    n = len(rows)
    fam_agree = sum(1 for r, rec in zip(rows, records)
                    if r["family"] == rec["oracle_family"]) / n
    op_agree = sum(1 for r, rec in zip(rows, records)
                   if r["choice"].op_id == rec["oracle_choice_id"]) / n
    exec_total = sum(r["exec_work"] for r in rows)
    over_total = sum(r["inference_work"] + r["feature_work"] for r in rows)
    return {"arm": arm_name, "n": n, "family_agreement": round(fam_agree, 4),
            "op_agreement": round(op_agree, 4),
            "first_pass_rate": round(sum(1 for r in rows if r["passed_first"]) / n, 4),
            "fallback_rate": round(sum(1 for r in rows if r["fallback"]) / n, 4),
            "mean_exec_work": round(exec_total / n, 2),
            "mean_overhead_work": round(over_total / n, 2),
            "build_work": build_work,
            "mean_total_work": round((exec_total + over_total + build_work) / n, 2)}


def sufficiency(eval_block, oracle_exec_mean):
    total = eval_block["mean_total_work"]
    ok_cost = total <= (1.0 + EPS_MARGIN) * oracle_exec_mean
    ok_pass = eval_block["first_pass_rate"] >= PASS_FLOOR
    bare = eval_block["mean_exec_work"] + eval_block["mean_overhead_work"]
    return {"cost_ok": ok_cost, "pass_ok": ok_pass,
            "sufficient": bool(ok_cost and ok_pass),
            "acquisition_dominates_flag": bool(
                (bare <= (1.0 + EPS_MARGIN) * oracle_exec_mean) and not ok_cost)}



def bandit_null_records(records):
    """Context-shuffle null for the bandit: permute FEATURE VECTORS within applicability
    strata while executions/rewards stay real. The bandit's feedback is its own
    executions, so permuting outcome pools nullifies almost nothing for it; shuffling
    contexts destroys exactly the conditional information its thetas could learn."""
    import dataclasses
    rng = random.Random(W.derive_seed("null-ctx"))
    strata = {}
    for i, r in enumerate(records):
        key = tuple(sorted({it.family for it in r["insts"]}))
        strata.setdefault(key, []).append(i)
    feats = {i: r["query"].features for i, r in enumerate(records)}
    for key in sorted(strata):
        pool = strata[key]
        perm = pool[:]
        rng.shuffle(perm)
        for i, j in zip(pool, perm):
            feats[i] = records[j]["query"].features
    out = []
    for i, r in enumerate(records):
        q2 = dataclasses.replace(r["query"], features=feats[i])
        out.append(dict(r, query=q2))
    return out


def harness_validation(world, queries):
    """Mandatory: the capsule's routing surface must agree with the naive structural scan
    (the FNA harness-validation convention). Any disagreement is a CANNOT_CHECK."""
    for q in queries:
        insts, _ = W.applicable(world, q)
        naive = tuple(it for it in world["catalogue"]
                      if it.anchor is None or it.anchor in q.active_set)
        if tuple(it.op_id for it in insts) != tuple(it.op_id for it in naive):
            return False
        if not any(it.family == "scan" for it in insts):
            return False                 # oracle existence: fallback always reachable
    return True


def apply_drift(world):
    """Frozen catalogue mutation: remove window:60, add sample:48 on a new anchor, bump the
    scan cost law to version 2 (x1.6), re-draw theta1, shift theta2 +0.05."""
    rng = random.Random(W.derive_seed("drift", "theta1"))
    world["catalogue"] = [it for it in world["catalogue"] if it.op_id != "window:60"]
    new = W.Instance("sample:48", "sample", "drift:0", 48, 12.0, 1.1, dict(world["realized"]))
    pos = next(i for i, it in enumerate(world["catalogue"]) if it.family == "scan")
    world["catalogue"].insert(pos, new)
    world["state"]["theta1"] = 0.35 + rng.uniform(-0.08, 0.08)
    world["state"]["theta2"] = world["state"]["theta2"] + 0.05
    world["state"]["scan_version_mult"] = 1.6
    W.rebuild_index(world)


def refresh_records(world, queries, old=None):
    """(Re)compute features + applicability + oracle under the CURRENT world state."""
    recs, diag = [], 0
    for q in queries:
        q.features, q.feature_work = W.extract_features(world, q)
        insts, sel_work = W.applicable(world, q)
        orc = W.run_oracle(world, q, insts)
        diag += orc["identify_work"]
        recs.append({"qid": q.qid, "query": q, "insts": insts, "sel_work": sel_work,
                     "oracle_choice_id": orc["choice"].op_id,
                     "oracle_family": orc["family"], "oracle_exec": orc["exec_work"],
                     "exec_by_id": orc["outcomes"]})
    return recs, diag


def base_commit():
    try:
        import subprocess
        out = subprocess.run(["/usr/bin/git", "rev-parse", "HEAD"], cwd=str(HERE),
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() if out.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tiny", action="store_true", help="reduced config for tests")
    args = ap.parse_args()
    t_wall0, t_cpu0 = time.perf_counter(), time.process_time()
    params = W.WorldParams.tiny_params() if args.tiny else W.WorldParams()
    world = W.build_world(params)
    queries = [W.make_query(world, i) for i in range(params.n_queries)]
    if not harness_validation(world, queries[:60]):
        receipt = {"schema": W.SCHEMA, "terminal": "CANNOT_CHECK_HARNESS_DISAGREES_WITH_NAIVE_SCAN"}
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt))
        return
    records, oracle_diag_build = refresh_records(world, queries)
    dev = [r for r in records if W.split_of(r["qid"]) == "DEV"]
    ev = [r for r in records if W.split_of(r["qid"]) == "EVAL"]
    dr = [r for r in records if W.split_of(r["qid"]) == "DRIFT"]
    assert not (set(r["qid"] for r in dev) & set(r["qid"] for r in ev))
    assert not (set(r["qid"] for r in dev) & set(r["qid"] for r in dr))
    state = world["state"]
    oracle_exec_mean = sum(r["oracle_exec"] for r in ev) / len(ev)

    def row_baseline(rec):
        return W.run_baseline(world, rec["query"], rec["insts"])

    def row_analytic(rec):
        choice, inf = W.analytic_choice(world, rec["query"], rec["insts"])
        q = rec["query"]
        return W.run_arm_choice(world, q, rec["insts"], choice, inf, q.feature_work)

    def row_for(arm):
        def row(rec):
            choice, inf = arm.choose(rec["query"], rec["insts"], state)
            q = rec["query"]
            return W.run_arm_choice(world, q, rec["insts"], choice, inf, q.feature_work)
        return row

    arms = [S.CostModelArm(), S.KnnArm(), S.LogisticArm(), S.TreeArm(), S.LinUcbArm()]
    mlp = S.MlpArm()
    fit_times = {}
    blocks = {"BASELINE_INCUMBENT": evaluate_rows(world, ev, "BASELINE_INCUMBENT", row_baseline)}
    blocks["A0_ORACLE"] = {"arm": "A0_ORACLE", "n": len(ev),
                           "mean_exec_work": round(oracle_exec_mean, 2),
                           "family_agreement": 1.0, "op_agreement": 1.0,
                           "first_pass_rate": 1.0, "fallback_rate": 0.0,
                           "mean_overhead_work": 0.0, "build_work": 0,
                           "mean_total_work": round(oracle_exec_mean, 2)}
    blocks["A1_ANALYTIC_GUARDED"] = evaluate_rows(
        world, ev, "A1_ANALYTIC_GUARDED", row_analytic)
    build_meta = {}
    for a in arms:
        t0 = time.perf_counter()
        if isinstance(a, S.LinUcbArm):
            bw = a.train(dev, world, lambda it, q: W.execute_via_spec(world, it, q))
        else:
            bw = a.fit(dev)
        fit_times[a.name] = round(time.perf_counter() - t0, 3)
        spent = getattr(a, "exec_spent_build", 0)
        blocks[a.name] = evaluate_rows(world, ev, a.name, row_for(a), bw + spent)
        build_meta[a.name] = {"model_bytes": a.model_bytes(), "exec_spent_build": spent}
        if hasattr(a, "exec_spent_build"):
            a.dev_exec_total = a.exec_spent_build
            a.exec_spent_build = 0          # counter reset: drift charges only drift exec
    t0 = time.perf_counter()
    mlp.fit(dev)
    fit_times[mlp.name] = round(time.perf_counter() - t0, 3)
    blocks[mlp.name] = evaluate_rows(world, ev, mlp.name, row_for(mlp), mlp.build_work)
    build_meta[mlp.name] = {"model_bytes": mlp.model_bytes(), "diagnostic_only": True}

    # shuffle-equal-n null: destroy feature->outcome information, keep marginals/structure
    null_records = S.make_null_records(dev)
    null_blocks = {}
    for a in arms:
        na = a.__class__()
        if isinstance(na, S.LinUcbArm):
            real_map = {r["qid"]: r["exec_by_id"] for r in dev}
            nbw = na.train(bandit_null_records(dev), world,
                           lambda it, q: real_map[q.qid][it.op_id])  # real reward, shuffled ctx
        else:
            nbw = na.fit(null_records)
        null_blocks[a.name] = evaluate_rows(world, ev, a.name + "_NULL", row_for(na), nbw)
    nmlp = S.MlpArm()
    nmlp.fit(null_records)
    null_blocks[nmlp.name] = evaluate_rows(world, ev, nmlp.name + "_NULL", row_for(nmlp),
                                           nmlp.build_work)

    # ------------------------------- drift phase -------------------------------
    t0 = time.perf_counter()
    apply_drift(world)
    drift_index_build = world["index_build_work"]
    mw_n = 60 if params.tiny else MAINT_WINDOW
    mw_queries = [W.make_query(world, params.n_queries + i) for i in range(mw_n)]
    mw_records, label_acq = refresh_records(world, mw_queries)
    drift_records, _ = refresh_records(world, [r["query"] for r in dr])
    maint = {}
    for a in arms:
        t1 = time.perf_counter()
        if isinstance(a, S.LinUcbArm):
            mw_work = a.train(mw_records, world, lambda it, q: W.execute_via_spec(world, it, q))
            charge = a.exec_spent_build   # bandit pays only its own online acquisitions
            a.exec_spent_build = 0
        else:
            mw_work = a.fit(mw_records)
            charge = label_acq            # label re-acquisition charged at oracle identify
        maint[a.name] = {"refit_work": mw_work, "label_acquisition_work": charge,
                         "seconds": round(time.perf_counter() - t1, 3)}
        blocks[a.name + "_DRIFT"] = evaluate_rows(
            world, drift_records, a.name + "_DRIFT", row_for(a), charge + mw_work)
    blocks["BASELINE_INCUMBENT_DRIFT"] = evaluate_rows(
        world, drift_records, "BASELINE_INCUMBENT_DRIFT", row_baseline)
    blocks["A1_ANALYTIC_GUARDED_DRIFT"] = evaluate_rows(
        world, drift_records, "A1_ANALYTIC_GUARDED_DRIFT", row_analytic)
    drift_oracle_mean = sum(r["oracle_exec"] for r in drift_records) / len(drift_records)
    drift_seconds = round(time.perf_counter() - t0, 3)

    # ------------------------------- terminals -------------------------------
    suff = {name: sufficiency(blk, oracle_exec_mean) for name, blk in blocks.items()
            if name in LADDER or name == mlp.name}
    first_refusal = next((n for n in LADDER if suff.get(n, {}).get("sufficient")), None)
    if first_refusal in ("A1_ANALYTIC_GUARDED", "A2_COST_MODEL"):
        parent = ("explicit analytic/guarded rule" if first_refusal == "A1_ANALYTIC_GUARDED"
                  else "conventional algorithm-selection cost model (Rice 1976 portfolio)")
        terminal = "PARENT_SUFFICIENT_FOR_ROUTING"
        terminal_parent = parent
    elif first_refusal is not None:
        terminal = "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE"
        terminal_parent = first_refusal
    elif suff.get(mlp.name, {}).get("sufficient"):
        terminal = "REPRESENTATION_INSUFFICIENT"
        terminal_parent = "neural reference sufficient, no non-neural arm was"
    else:
        terminal = "NO_FUNCTIONAL_PARITY_ROUTING"
        terminal_parent = "none"
    acq_flag = {n: s["acquisition_dominates_flag"] for n, s in suff.items()
                if s["acquisition_dominates_flag"]}

    authored_rule_bytes = len(inspect.getsource(W.analytic_choice))
    receipt = {
        "schema": W.SCHEMA, "salt": W.SALT, "base_commit": base_commit(),
        "params": {"n_queries": params.n_queries, "n_atoms": params.n_atoms,
                   "tiny": params.tiny, "maint_window": mw_n,
                   "eps_margin": EPS_MARGIN, "pass_floor": PASS_FLOOR,
                   "splits": "DEV<=3, EVAL 4..7, DRIFT 8..9 of salted md5 bucket"},
        "realized_world_constants": {k: round(v, 5) for k, v in
                                     sorted(world["realized"].items())},
        "drift_state": {"theta1": round(world["state"]["theta1"], 5),
                        "theta2": round(world["state"]["theta2"], 5),
                        "scan_version_mult": world["state"]["scan_version_mult"],
                        "index_rebuild_work": drift_index_build},
        "oracle_exec_mean_EVAL": round(oracle_exec_mean, 2),
        "oracle_family_dist_EVAL": dict(sorted(collections.Counter(
            r["oracle_family"] for r in ev).items())),
        "oracle_family_dist_DRIFT": dict(sorted(collections.Counter(
            r["oracle_family"] for r in drift_records).items())),
        "oracle_identify_work_total": oracle_diag_build + label_acq,
        "arms_EVAL": blocks,
        "sufficiency": suff,
        "first_refusal_arm": first_refusal,
        "terminal": terminal, "terminal_parent": terminal_parent,
        "acquisition_dominates_flags": acq_flag,
        "null_control": null_blocks,
        "maintenance": maint,
        "drift_oracle_exec_mean": round(drift_oracle_mean, 2),
        "prior_information_bytes": {"A1_authored_rule_source": authored_rule_bytes,
                                    **{k: v["model_bytes"] for k, v in build_meta.items()}},
        "build_meta": build_meta, "fit_seconds": fit_times,
        "drift_seconds": drift_seconds,
        "gate_71": "LEARNED_ROUTER_NOT_YET_AUTHORIZED (unchanged; study-only, nothing deployed)",
        "host": {"python": platform.python_version(), "platform": platform.platform()},
        "wall_seconds": round(time.perf_counter() - t_wall0, 3),
        "cpu_seconds": round(time.process_time() - t_cpu0, 3),
        "rss_native_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "limitations": [
            "One authored task world, one population, one author (E1/L1), not E3.",
            "Exact O(1)-certificate checker: failures are always caught, never delivered.",
            "Boundary noise makes a Bayes-irreducible gap; eps must absorb it.",
            "A6 is a 1-hidden-layer diagnostic; it bounds nothing about neural capacity.",
            "Wall/CPU numbers are descriptive single-host measurements."],
    }
    core = json.dumps({k: receipt[k] for k in ("arms_EVAL", "terminal", "first_refusal_arm")},
                      sort_keys=True)
    receipt["receipt_digest"] = hashlib.sha256(core.encode()).hexdigest()
    blob = json.dumps(receipt, indent=2, sort_keys=False) + "\n"
    for bad in FORBIDDEN:
        assert bad not in blob, "FORBIDDEN_CLAIM_IN_RECEIPT"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(blob)
    print(json.dumps({"output": str(args.out), "terminal": terminal,
                      "first_refusal_arm": first_refusal,
                      "oracle_exec_mean": round(oracle_exec_mean, 2)}))


if __name__ == "__main__":
    main()
