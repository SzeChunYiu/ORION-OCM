#!/usr/bin/env python3
"""GS-R2 freeze tool (JOB B, #221 sec 18 GS-R2 / GSA6 revival levers) —
writes GRAND_SEARCH_R2_FREEZE.json TOOL-stamped BEFORE any scored run.

R2 question (from the R1 bottleneck table GSA5_RATE_READ_V1 + the HSG
uncertainty ledger entry local_evolvability_levers): do the GSA6 revival
levers (novelty-gated allocation, promotion dedup-by-phenotype_digest,
cumulative surrogate; PR #270, default-off flags) recover the 2.267x
distinct-yield loss and the 2.171x CPU factor vs the GSA2/GSA5 parents,
and does the fixed surrogate (holdout-MAE NaN fix, always-on) finally
yield a usable holdout_mae_t1?

Refuses when: ancestor chain broken (V1->A4 AND the R1 freeze), any
scored GS_R2 artifact exists, or the env probe is missing.

Usage: python3 hpc/freeze_gs_r2.py <CAPSULE_ROOT>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

FREEZE_NAME = "GRAND_SEARCH_R2_FREEZE.json"
_chain = ["FREEZE_V1.json", "FREEZE_V1_AMEND_1.json",
          "FREEZE_V1_AMEND_2.json", "FREEZE_V1_AMEND_3.json",
          "FREEZE_V1_AMEND_4.json", "GRAND_SEARCH_R1_FREEZE.json"]


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_files_sha256(root: str):
    """Per-file sha chain of every module the campaign runs (JOB B: the
    freeze names the files, not just the aggregate digest)."""
    out = {}
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                out["%s/%s" % (d, fn)] = sha256_file(
                    os.path.join(root, d, fn))
    return out


def code_digest(root: str) -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


def _refusal_guard(root: str) -> None:
    res = os.path.join(root, "results")
    if os.path.isdir(res):
        for fn in os.listdir(res):
            if fn.startswith("GS_R2_") and (
                    fn.endswith(".json") or fn.endswith(".status")):
                raise SystemExit("REFUSED: scored GS_R2 result exists: %s"
                                 % fn)
    for d in ("archives", "manifests"):
        dd = os.path.join(root, d)
        if os.path.isdir(dd):
            for fn in os.listdir(dd):
                if fn.startswith("GS_R2_"):
                    raise SystemExit(
                        "REFUSED: scored GS_R2 artifact exists: %s/%s"
                        % (d, fn))
    if os.path.exists(os.path.join(root, "manifests", "GS_R2_TASKS.json")):
        raise SystemExit("REFUSED: R2 task manifest already bound — "
                         "refreeze requires recorded supersession")


def _environment(root: str) -> dict:
    p = os.path.join(root, "GS_ENV_PROBE.json")
    if not os.path.exists(p):
        raise SystemExit("REFUSED: GS_ENV_PROBE.json missing — run "
                         "hpc/env_probe.py on the scoring host BEFORE "
                         "freezing")
    probe = json.load(open(p))
    assert probe.get("schema") == "GS_ENV_PROBE_V1"
    ch = probe["choices"]
    out = {"env_probe_sha256": sha256_file(p),
           "probe_host": probe["host"], "probe_python": probe["python"],
           "packages": probe["packages"],
           "novelty_archive_impl": ch["novelty_archive_impl"],
           "surrogate_impl": ch["surrogate_impl"]}
    m = os.path.join(root, "results", "REUSE_VECTORIZE_MEASUREMENT.json")
    if os.path.exists(m):
        out["reuse_measurement_sha256"] = sha256_file(m)
    return out


def _parents(root: str) -> dict:
    """Frozen parent evidence: the R1 GSAB1 aggregate stats pinned by the
    committed rate read (sha-chained at freeze time)."""
    rr = os.path.join(root, "results", "GSA5_RATE_READ_V1.json")
    if not os.path.exists(rr):
        raise SystemExit("REFUSED: results/GSA5_RATE_READ_V1.json missing")
    d = json.load(open(rr))
    dec = d["decomposition"]
    return {
        "source": "results/GSA5_RATE_READ_V1.json",
        "source_sha256": sha256_file(rr),
        "r1_freeze_sha256_of_parents": d["data"]["freeze_sha256"],
        "GSA2_hetero": {"morphologies_per_cpu_hour": 354046.0,
                        "distinct_t2_viable_per_seed": 5062.7,
                        "cpu_seconds_per_seed": 51.258},
        "GSA5_surrogate": {"morphologies_per_cpu_hour": 72150.0,
                           "distinct_t2_viable_per_seed": 2233.3,
                           "cpu_seconds_per_seed": 111.257},
        "factors": {"distinct_yield": dec["factor_distinct_yield"]["value"],
                    "cpu_per_seed": dec["factor_cpu_per_seed"]["value"]},
        "note": "GSAB1 seeds 0-5, lane hetero, n0=729, t0 45000 — R2 arms "
                "match this allocation exactly so lever deltas are "
                "one-stage attributable",
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    ROOT = os.path.abspath(sys.argv[1])
    sys.path.insert(0, ROOT)
    _refusal_guard(ROOT)
    environment = _environment(ROOT)
    shas = {}
    for fn in _chain:
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p):
            raise SystemExit("REFUSED: ancestor freeze missing: %s" % fn)
        shas[fn] = sha256_file(p)
    r1 = json.load(open(os.path.join(ROOT, "GRAND_SEARCH_R1_FREEZE.json")))

    from search.successive_halving import (GS_ETA,
                                           GS_LATE_BLOOMER_FRACTION,
                                           GS_MIN_PROMOTE, GS_RUNGS)
    from search.surrogate_allocate import (GS_SUR_DEPTH, GS_SUR_K,
                                           GS_SUR_SUBSPACE, GS_SUR_TREES,
                                           SURROGATE_ID)
    from evaluation.t3_ecology import T3_FAMILIES
    from evaluation.t3_ecology_m104 import (CROSSOVER_M, DEFAULT_N_CALLS)

    ADMISSION_BAR = r1["arms"]["GSA2_hetero"]["admission_bar"]
    _ng = "novelty gate: rank key s/(nov+1e-9), archive-admitted novelty"
    _dp = "dedup: promotions collapse to distinct phenotype_digests, " \
          "cross-round seen-set excludes already-promoted digests"
    _sc = "cumulative surrogate: ONE EnsembleSurrogate carried across " \
          "rounds, monotone training growth, batched allocation_scores"
    _base = {"algorithm": "surrogate-ranked SH + GSA6 revival levers",
             "lane": "hetero", "rank": "surrogate_allocation",
             "seeds": [0, 1, 2, 3, 4, 5], "t0_budget_per_seed": 45000,
             "n0": 729, "admission_bar": ADMISSION_BAR}
    # NOTE: the lever flags are FLAT arm-config keys (novelty_gate,
    # dedup_promotion, surrogate_cumulative) — exactly what hpc/gs_run.py
    # reads via arm_cfg.get(...); a nested dict would silently read False.
    arms = {
        "GSA6_NG": dict(_base, novelty_gate=True, dedup_promotion=False,
                        surrogate_cumulative=False, lever_note=_ng),
        "GSA6_DP": dict(_base, novelty_gate=False, dedup_promotion=True,
                        surrogate_cumulative=False, lever_note=_dp),
        "GSA6_SC": dict(_base, novelty_gate=False, dedup_promotion=False,
                        surrogate_cumulative=True, lever_note=_sc),
        "GSA6_ALL": dict(_base, novelty_gate=True, dedup_promotion=True,
                         surrogate_cumulative=True,
                         lever_note="full package: %s; %s; %s" % (
                             _ng, _dp, _sc)),
        "GSA5P_fixed": dict(_base, novelty_gate=False, dedup_promotion=False,
                            surrogate_cumulative=False,
                            lever_note="parent replication on fixed code "
                            "(GSA5_HOLDOUT_MAE_NAN fix always-on): "
                            "re-measures the parent rate + a usable "
                            "holdout_mae_t1 on THIS code digest"),
    }

    freeze = {
        "freeze_id": "GRAND_SEARCH_R2",
        "schema": "GRAND_SEARCH_R2_FREEZE_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "created_utc_by": "hpc/freeze_gs_r2.py at freeze time",
        "governing_plan": "issue #221 sec 18 GS-R2 (bottleneck-table "
                          "design: GSA5_RATE_READ_V1 implications 1-3) + "
                          "HSG UNCERTAINTY_LEDGER_V1 local_evolvability_"
                          "levers + GSA6 JOB B dispatcher directive "
                          "2026-09-10",
        "evidence_class": "EXPLORATORY_ADAPTIVE",
        "evidence_class_rule": "every R2 outcome is decision support for "
                               "the NEXT allocation decision; no R2 rule "
                               "is a programme terminal (sec-15 "
                               "vocabulary only via inherited R1 rules; "
                               "R2-specific ids are lever verdicts)",
        "decision_ledger_rule": "NO sbatch without its decision line "
                                "durably appended to ADAPTIVITY_LEDGER."
                                "jsonl FIRST (GS-R1h discipline); the "
                                "initial array's decision line cites this "
                                "freeze sha256",
        "ancestor_chain_sha256": {fn: shas[fn] for fn in _chain},
        "r1_freeze_superseded": False,
        "code_digest": code_digest(ROOT),
        "code_files_sha256": code_files_sha256(ROOT),
        "environment": environment,
        "parents": _parents(ROOT),
        "arms": arms,
        "successive_halving": r1["successive_halving"],
        "novelty_space": r1["novelty_space"],
        "search_bound": r1["search_bound"],
        "surrogate": {"surrogate_id": SURROGATE_ID, "k": GS_SUR_K,
                      "n_trees": GS_SUR_TREES, "depth": GS_SUR_DEPTH,
                      "subspace": GS_SUR_SUBSPACE,
                      "role": r1["surrogate"]["role"],
                      "holdout_mae_fix": "GSA5_HOLDOUT_MAE_NAN fix "
                                         "(PR #270) is ALWAYS ON in R2; "
                                         "gs_run asserts holdout_mae_t1 "
                                         "finite when present"},
        "novelty_gate_rank_key": "s/(nov+1e-9)",
        "failure_memory": r1["failure_memory"],
        "wall_clock_budget_h": 2,
        "heldout_t3": {
            "t3_key_id": r1["heldout_t3"]["t3_key_id"],
            "key_sha256": r1["heldout_t3"]["key_sha256"],
            "families": list(T3_FAMILIES),
            "draw": r1["heldout_t3"]["draw"],
            "replication": "R1 T3 key reused VERBATIM — same battery, "
                           "evaluated on R2 survivors (replication of the "
                           "R1 endpoint on fixed-surrogate code)",
            "evaluated_only_on": "R2 survivors (distinct T2-viable "
                                 "phenotypes across R2 arms)",
            "floor": r1["heldout_t3"]["floor"],
            "m104_extension": {
                "module": "evaluation/t3_ecology_m104.py",
                "n_calls": DEFAULT_N_CALLS,
                "tasks_per_call": len(T3_FAMILIES),
                "m_total_min": DEFAULT_N_CALLS * len(T3_FAMILIES),
                "crossover_m": CROSSOVER_M,
                "bound_ref": "HST_TRANSFER_BOUND_V1: eps(104)=0.22393 "
                             "<= admission bar 0.224507 — first m where "
                             "the PAC-Bayes transfer slack meets the "
                             "zoo's own predicate; subkeys are "
                             "key|tag|i derivations of the SAME frozen "
                             "R1 key (no new randomness)",
            },
        },
        "t3_key": r1["t3_key"],
        "cpu_placement": {
            "priority": [["nuc", "lu2026-2-51"], ["lu48", "lu2026-2-51"],
                         ["hep", "hep2023-1-3"]],
            "tasks_per_node_cores": 1,
            "time_limit_per_task": "02:00:00",
            "determinism_replicates": "laptop billy (py3.8, builtin impl "
                                      "probe) never enters selection",
        },
        "terminal_rules_first_match": [
            {"order": 1, "id": "CANNOT_CHECK_NO_SCORED_DISPOSITIONS",
             "vocab": "CANNOT_CHECK_NO_SCORED_DISPOSITIONS",
             "condition": "zero R2 search-arm tasks completed with evals"},
            {"order": 2, "id": "LEVER_PACKAGE_BEATS_PARENTS",
             "vocab": "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE",
             "condition": "GSA6_ALL morphologies-per-CPU-hour > "
                          "max(GSA2 parent 354046, GSA5 parent 72150, "
                          "GSA5P_fixed replication) AND GSA6_ALL "
                          "distinct-per-seed > GSA2 parent 5062.7"},
            {"order": 3, "id": "LEVER_PACKAGE_BEATS_SURROGATE_PARENT_ONLY",
             "vocab": "MORPHOLOGY_SEARCH_COST_DOMINATES",
             "condition": "GSA6_ALL mph > max(GSA5 parent 72150, "
                          "GSA5P_fixed) but NOT above GSA2 parent"},
            {"order": 4, "id": "LEVER_PACKAGE_NO_GAIN",
             "vocab": "MORPHOLOGY_SEARCH_COST_DOMINATES",
             "condition": "GSA6_ALL mph <= max(GSA5 parent 72150, "
                          "GSA5P_fixed)"},
            {"order": 5, "id": "MIXED_INTERMEDIATE_NO_TERMINAL",
             "vocab": "CANNOT_CHECK_PARTIAL_DISPOSITIONS",
             "condition": "otherwise (honest partials; single-lever "
                          "attribution table still written; round "
                          "repeats)"},
        ],
        "per_survivor_rules": r1["per_survivor_rules"],
        "surrogate_fixed_read": {
            "endpoint": "holdout_mae_t1 finite in EVERY completed "
                        "surrogate-ranked run (GSA5_RATE_READ defect "
                        "GSA5_HOLDOUT_MAE_NAN: was NaN 5/6 seeds, 0.0 "
                        "1/6); distribution recorded per arm",
            "not_a_terminal": True},
        "forbidden_terminals": r1["forbidden_terminals"],
        "status": "frozen_before_scored_runs",
    }
    path = os.path.join(ROOT, FREEZE_NAME)
    if os.path.exists(path):
        raise SystemExit("REFUSED: %s exists — supersede by recorded sha, "
                         "never silently rewrite" % FREEZE_NAME)
    with open(path, "w") as fh:
        json.dump(freeze, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("FROZE %s" % path)
    print("freeze_sha256=%s" % sha256_file(path))
    print("created_utc=%s" % freeze["created_utc"])
    print("code_digest=%s" % freeze["code_digest"])
    print("t3_key_id=%s (R1 replication) m104=%dx%d" % (
        freeze["heldout_t3"]["t3_key_id"], DEFAULT_N_CALLS,
        len(T3_FAMILIES)))
    print("arms=%s" % ",".join(sorted(arms)))


if __name__ == "__main__":
    main()
