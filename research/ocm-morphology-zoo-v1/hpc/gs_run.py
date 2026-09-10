#!/usr/bin/env python3
"""GS-R1 search-arm worker (#221 sec 18).  One task = (arm, seed).

Arms (frozen in GRAND_SEARCH_R1_FREEZE.json):
  GSA1_units/GSA2_hetero/GSA3_farch/GSA4_obasis — novelty+viability
      successive halving (viability gate, novelty driver, SH promotions)
  GSA5_surrogate — successive halving with ensemble-surrogate allocation
      ranking (surrogate retrained each round on completed evals ONLY)
  GSR_random_control — successive halving, random rank (control)

Every sampled genome is evaluated and charged (no ledger-based skips);
failures append to this task's FAILURES shard.  Output:
  results/GS_R1_<ARM>_s<seed>.json + .status   (retained on failure too)
  manifests/receipts/GS_R1_<ARM>_s<seed>.json  (sha-chained per round)
  archives/GS_R1_<ARM>_s<seed>_archive.json    (novelty archive dump)
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(sys.argv[1])
ARM = sys.argv[2]
SEED = int(sys.argv[3])
TASK_SPEC = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
sys.path.insert(0, ROOT)

# Adaptive-batch tasks (GS-R1h) override ALLOCATION ONLY: lane,
# lane_weights, rank kind, budgets, seed, task id.  Frozen things (eta,
# insurance, gates, terminal rules, T3 key) can never come from a spec.
_FORBIDDEN_SPEC_KEYS = {"eta", "insurance_fraction", "gates",
                        "terminal_rules", "t3_key", "freeze"}
if TASK_SPEC is not None:
    bad = _FORBIDDEN_SPEC_KEYS & set(TASK_SPEC)
    assert not bad, "REFUSED: batch spec touches frozen keys: %s" % bad
    assert ARM.startswith(TASK_SPEC.get("base_arm", ARM.split("_")[0])) or \
        TASK_SPEC.get("base_arm") == ARM, "spec base_arm mismatch"
    SEED = int(TASK_SPEC.get("seed", SEED))
_RUN_ID_BASE = (TASK_SPEC["task_id"] if TASK_SPEC else "%s_s%d" % (ARM, SEED))
RUN_ID = "GS_R1_%s" % _RUN_ID_BASE
os.environ["ZOO_FAILURES_JSONL"] = os.path.join(
    ROOT, "results", "FAILURES_%s.jsonl" % _RUN_ID_BASE)

import hashlib  # noqa: E402
import math  # noqa: E402


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_digest(root: str) -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


from evaluation.objectives import dev_score  # noqa: E402
from evaluation.receipts import append_record, make_receipt, verify_receipt  # noqa: E402
from morphology.gs_bound import grammar_signature, lane_sampler  # noqa: E402
from morphology.gs_bound import weighted_sampler  # noqa: E402
from search.failure_memory import read_failures  # noqa: E402
from search.novelty_viability import make_novelty_archive, novelty_score  # noqa: E402
from search.novelty_viability import novelty_vector_of  # noqa: E402
from search.successive_halving import run_successive_halving  # noqa: E402
from search.surrogate_allocate import EnsembleSurrogate  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402


def genome_of(rec):
    return OCMMorphologyGenomeV1.from_json_obj(rec["genome"])


def trim(rec):
    out = {
        "genotype_digest": rec["genotype_digest"],
        "phenotype_digest": rec["phenotype_digest"],
        "genome": rec["genome"],
        "grammar_signature": grammar_signature(genome_of(rec)),
        "n_units": rec.get("n_units"),
        "F_arch": rec["genome"]["F_arch"],
        "round": rec.get("round"),
    }
    for t in ("t1", "t2"):
        if t in rec:
            ev = rec[t]["evaluation"]
            out[t] = {
                "feasible": rec[t]["feasible"],
                "solved_fraction": ev.get("solved_fraction"),
                "persistent_bytes": ev.get("persistent_bytes"),
                "dev_score": dev_score(ev),
            }
    return out


def main() -> None:
    freeze_path = os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")
    freeze = json.load(open(freeze_path))
    fsha = sha256_file(freeze_path)
    env_sha = os.environ.get("GS_FREEZE_SHA", "")
    assert env_sha in ("", fsha), "freeze sha mismatch: env=%s file=%s" % (
        env_sha[:16], fsha[:16])
    assert code_digest(ROOT) == freeze["code_digest"], "code drift vs freeze"
    arm_cfg = dict(freeze["arms"][ARM])
    if TASK_SPEC is not None:  # GS-R1h adaptive batch: allocation overrides
        assert TASK_SPEC.get("freeze_sha256") in (None, fsha), \
            "batch spec not bound to this freeze"
        arm_cfg.update({k: TASK_SPEC[k] for k in
                        ("lane", "rank", "t0_budget_per_seed", "n0")
                        if k in TASK_SPEC})
    t0_budget = int(TASK_SPEC["t0_budget"]) if TASK_SPEC and \
        "t0_budget" in TASK_SPEC else int(arm_cfg["t0_budget_per_seed"])
    n0 = int(arm_cfg["n0"])
    lane = arm_cfg["lane"]
    rank_kind = arm_cfg["rank"]

    deadline = None
    if os.environ.get("GS_STOP_TS"):
        deadline = float(os.environ["GS_STOP_TS"])

    # impls pinned by the freeze's env probe (reuse-first, #221 sec 2a)
    env = freeze["environment"]
    rng_archive = make_novelty_archive(
        env["novelty_archive_impl"],
        cap=freeze["novelty_space"]["archive_cap"],
        floor=freeze["novelty_space"]["archive_floor"],
        k=freeze["novelty_space"]["k_nn"], seed=SEED)
    surrogate = EnsembleSurrogate(seed=SEED, impl=env["surrogate_impl"])

    if rank_kind == "novelty":
        def rank_prepare(viable):
            vecs = []
            for rec in viable:
                rec["_vec"] = novelty_vector_of(rec)
                vecs.append(rec["_vec"])
            pool = rng_archive.pool() + vecs
            for rec in viable:
                rec["_nov"] = novelty_score(
                    rec["_vec"], pool, freeze["novelty_space"]["k_nn"])
                rng_archive.consider(rec, rec["_vec"])

        rank_fn = lambda r: r["_nov"]  # noqa: E731
        on_round_end = None
    elif rank_kind == "surrogate_allocation":
        holder = {"sur": surrogate}  # rank_prepare must see the RETRAINED head

        def rank_prepare(viable):
            for rec in viable:
                rec["_s"] = holder["sur"].allocation_score(genome_of(rec))

        def on_round_end(_round, t0_records, t1_records, _t2_records):
            # retrain on COMPLETED evals only (T0 outcomes; T1 dev scores)
            sur = EnsembleSurrogate(seed=SEED, impl=env["surrogate_impl"])
            sur.train_t0(t0_records)
            pairs = [(genome_of(r), dev_score(r["t1"]["evaluation"]))
                     for r in t1_records if r.get("t1")]
            if pairs:
                sur.train_t1(pairs)
            stats.update(sur.stats)
            _mae = stats.get("holdout_mae_t1")
            assert _mae is None or math.isfinite(_mae), \
                "GSA5_HOLDOUT_MAE_NAN: surrogate holdout MAE not finite"
            stats["n_retrains"] = stats.get("n_retrains", 0) + 1
            sur_state.append({"n_train_t0": sur.stats["n_train_t0"],
                              "n_train_t1": sur.stats["n_train_t1"]})
            holder["sur"] = sur

        stats = {}
        sur_state = []
        rank_fn = lambda r: r.get("_s", 0.0)  # noqa: E731
    else:  # random control
        rank_prepare = None
        import random as _r
        _rr = _r.Random(SEED ^ 0x525252)
        rank_fn = lambda r: _rr.random()  # noqa: E731
        on_round_end = None
        stats = {}

    t_wall = time.time()
    t_cpu = time.process_time()
    import random
    if TASK_SPEC and TASK_SPEC.get("lane_weights"):
        sampler = weighted_sampler(TASK_SPEC["lane_weights"], random.Random(SEED))
    elif lane != "uniform":
        # lane_sampler is a FACTORY: it returns the lane's sampler (a
        # function or round-robin instance), NOT a genome.  The frozen
        # R1 campaign wrapped the factory itself as the draw, so every
        # GSA cohort element was a sampler object (AttributeError in
        # compile_genome, silently swallowed by the SH loop's bare
        # except — 45000 zero-cost "evals"/arm, no ledger).  Deferred to
        # the next freeze (scored R1 artifacts exist); R1 lane arms are
        # repaired additively via the adaptive-batch lane_weights path.
        _lane_draw = lane_sampler(lane, None)
        sampler = (lambda r: _lane_draw(r))
    else:
        sampler = None

    progress_path = os.path.join(ROOT, "results", RUN_ID + ".progress.jsonl")

    def on_progress(p):
        """GS-R1h honest partials: one append-only line per SH round."""
        line = dict(p)
        line["run_id"] = RUN_ID
        if rank_kind == "novelty":
            line["novelty_archive_size"] = rng_archive.size()
        if rank_kind == "surrogate_allocation" and stats:
            line["surrogate_stats"] = dict(stats)
        with open(progress_path, "a") as fh:
            fh.write(json.dumps(line, sort_keys=True) + "\n")

    res = run_successive_halving(
        t0_budget=t0_budget, seed=SEED, sampler=sampler, parent_pool=[],
        rank_fn=rank_fn, eta=freeze["successive_halving"]["eta"],
        insurance_fraction=freeze["successive_halving"]["late_bloomer_fraction"],
        n0=n0, wall_deadline=deadline,
        rank_prepare=rank_prepare, on_round_end=on_round_end,
        on_progress=on_progress)
    cpu_s = time.process_time() - t_cpu
    wall_s = time.time() - t_wall

    # ---- sha-chained receipt (one summary record; chain verified)
    receipt = make_receipt(
        run_id=RUN_ID,
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        host=os.environ.get("ZOO_HOST", os.uname().nodename),
        tier="T0+T1+T2", config_digest=fsha)

    survivors = [trim(r) for r in res["survivors"]]
    distinct = sorted({s["phenotype_digest"] for s in survivors})
    receipt = append_record(receipt, 0, {
        "rounds": res["rounds"], "counts": res["counts"],
        "viable_counts": res["viable_counts"],
        "distinct_t2_viable_phenotypes": len(distinct),
        "cpu_hours": round(cpu_s / 3600.0, 6)})
    assert verify_receipt(receipt), "receipt verify failed"
    out = {
        "run_id": RUN_ID, "arm": ARM, "seed": SEED, "lane": lane,
        "rank": rank_kind, "algorithm": res["algorithm"],
        "eta": res["eta"], "insurance_fraction": res["insurance_fraction"],
        "rounds": res["rounds"], "counts": res["counts"],
        "viable_counts": res["viable_counts"],
        "t1_t2_eval_failures": res["t1_t2_eval_failures"],
        "n_survivors": len(survivors),
        "distinct_t2_viable_phenotypes": len(distinct),
        "cpu_seconds": round(cpu_s, 3), "wall_seconds": round(wall_s, 3),
        "cpu_hours": round(cpu_s / 3600.0, 6),
        "distinct_t2_viable_per_cpu_hour": (
            round(len(distinct) / (cpu_s / 3600.0), 6) if cpu_s > 0 else None),
        "deadline_hit": bool(deadline is not None and time.time() >= deadline),
        "surrogate_stats": stats if rank_kind == "surrogate_allocation" else None,
        "n_failure_entries": len(read_failures()),
        "freeze_sha256": fsha,
        "environment": {k: env[k] for k in
                        ("novelty_archive_impl", "surrogate_impl")},
        "survivors": survivors,
        "receipt": receipt,
    }
    arch_path = os.path.join(ROOT, "archives", RUN_ID + "_archive.json")
    with open(arch_path, "w") as fh:
        json.dump({"run_id": RUN_ID,
                   "n_archive": rng_archive.size(),
                   "records": [
                       {"phenotype_digest": r["phenotype_digest"],
                        "genotype_digest": r["genotype_digest"],
                        "genome": r["genome"],
                        "novelty": r.get("novelty")}
                       for r in rng_archive.records.values()]}, fh, indent=1)
    rpath = os.path.join(ROOT, "results", RUN_ID + ".json")
    with open(rpath, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    with open(os.path.join(ROOT, "manifests", "receipts",
                           RUN_ID + ".json"), "w") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    with open(os.path.join(ROOT, "results", RUN_ID + ".status"), "w") as fh:
        fh.write("ok\n")
    print("DONE %s rounds=%d counts=%s distinct=%d cpu_h=%.4f" % (
        RUN_ID, res["rounds"], res["counts"], len(distinct), cpu_s / 3600.0))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # retain crash evidence
        import traceback
        with open(os.path.join(
                ROOT, "results", RUN_ID + ".status"), "w") as fh:
            fh.write("fail %r\n" % (e,))
        with open(os.path.join(
                ROOT, "logs", RUN_ID + ".crash"), "w") as fh:
            fh.write(traceback.format_exc())
        raise
