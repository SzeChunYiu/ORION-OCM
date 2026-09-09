#!/usr/bin/env python3
"""GS-R0 freeze tool — writes GRAND_SEARCH_R1_FREEZE.json (TOOL-stamped,
BEFORE any scored run; #221 sec 18 GS-R0, amend-3 timing-erratum
discipline).

Refuses when:
  - the ancestor chain V1 -> A1 -> A2 -> A3 -> A4 is broken anywhere;
  - any scored GS result already exists (results/GS_R1_* with a .status,
    or archives/GS_R1_*, or manifests/GS_R1_TASKS.json already bound);
  - GS search/evaluation modules fail their import-time self-checks.

Usage: python3 hpc/freeze_gs.py <CAPSULE_ROOT>
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import time

FREEZE_NAME = "GRAND_SEARCH_R1_FREEZE.json"

_chain = ["FREEZE_V1.json", "FREEZE_V1_AMEND_1.json",
          "FREEZE_V1_AMEND_2.json", "FREEZE_V1_AMEND_3.json",
          "FREEZE_V1_AMEND_4.json"]


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def code_digest(root: str) -> str:
    h = hashlib.sha256()
    for d in ("morphology", "evaluation", "search", "hpc"):
        for fn in sorted(os.listdir(os.path.join(root, d))):
            if fn.endswith(".py"):
                h.update(open(os.path.join(root, d, fn), "rb").read())
    return h.hexdigest()


def _refusal_guard(root: str) -> None:
    """Never freeze after scored GS outcomes exist (amend-3 lesson)."""
    res = os.path.join(root, "results")
    for fn in os.listdir(res):
        if fn.startswith("GS_R1_") and (
                fn.endswith(".json") or fn.endswith(".status")):
            raise SystemExit("REFUSED: scored GS result exists: %s" % fn)
    for d in ("archives", "manifests"):
        dd = os.path.join(root, d)
        if os.path.isdir(dd):
            for fn in os.listdir(dd):
                if fn.startswith("GS_R1_"):
                    raise SystemExit(
                        "REFUSED: scored GS artifact exists: %s/%s" % (d, fn))
    m = os.path.join(root, "manifests", "GS_R1_TASKS.json")
    if os.path.exists(m):
        raise SystemExit("REFUSED: task manifest already bound — refreeze "
                         "requires explicit supersession, not a fresh freeze")


def _baselines(root: str) -> dict:
    """Frozen acceleration baselines: amend-2/3/4 per-arm per-tier costs,
    pinned by sha256 AT FREEZE TIME (before GS outcomes exist).  The
    matched-tier comparison scalar is amend-3's T2 arms (same 40k-eval
    budget class the GS arms run): distinct-elite T2 morphologies per
    CPU-hour.  Amend-2/4 cells embedded for the record with their own
    metrics where present."""
    out = {"files": {}, "amend3_t2_arms": {}, "matched_tier": "T2"}
    best = None
    a3p = os.path.join(root, "results", "AGGREGATE_AMEND3.json")
    if os.path.exists(a3p):
        a3 = json.load(open(a3p))
        out["files"]["AGGREGATE_AMEND3.json"] = sha256_file(a3p)
        for arm, cell in sorted(a3.get("cells", {}).items()):
            ch = cell.get("cpu_hours") or 0.0
            ne = cell.get("n_elites") or 0.0
            if ch > 0:
                mph = ne / ch
                out["amend3_t2_arms"][arm] = {
                    "evals": cell.get("evals"), "cpu_hours": ch,
                    "n_elites": ne, "morphologies_per_cpu_hour": mph}
                if best is None or mph > best[1]:
                    best = (arm, mph)
    for fn in ("AGGREGATE_AMEND2.json", "AGGREGATE_AMEND4.json"):
        p = os.path.join(root, "results", fn)
        if os.path.exists(p):
            out["files"][fn] = sha256_file(p)
    out["frozen_baseline"] = {
        "arm": best[0] if best else None,
        "morphologies_per_cpu_hour": best[1] if best else None,
        "definition": "max over amend-3 T2 cells of n_elites/cpu_hours "
                      "(distinct-elite morphologies per CPU-hour at the "
                      "matched 40k-eval T2 budget)"}
    if best is None:
        raise SystemExit("REFUSED: no amend-3 baseline cells found")
    return out


def _environment(root: str) -> dict:
    """Reuse-first (#221 sec 2a): the scoring host's env probe is a REQUIRED
    freeze input — the archive/surrogate implementations are pinned from it,
    never left ambient.  Refuses without GS_ENV_PROBE.json."""
    p = os.path.join(root, "GS_ENV_PROBE.json")
    if not os.path.exists(p):
        raise SystemExit(
            "REFUSED: GS_ENV_PROBE.json missing — run hpc/env_probe.py on "
            "the scoring host (LUNARC) BEFORE freezing; a frozen campaign "
            "must not depend on ambient environment")
    probe = json.load(open(p))
    assert probe.get("schema") == "GS_ENV_PROBE_V1"
    ch = probe["choices"]
    assert ch["novelty_archive_impl"] in ("builtin", "ribs")
    assert ch["surrogate_impl"] in ("builtin", "sklearn")
    out = {
        "env_probe_sha256": sha256_file(p),
        "probe_host": probe["host"], "probe_python": probe["python"],
        "packages": probe["packages"],
        "novelty_archive_impl": ch["novelty_archive_impl"],
        "surrogate_impl": ch["surrogate_impl"],
        "impl_semantics": {
            "ribs": "pyribs ProximityArchive admission (k=15, static "
                    "novelty_threshold=0.0, capacity=cap, seed pinned); "
                    "cap-overflow REJECTS instead of evicting the least "
                    "novel (documented delta vs builtin)",
            "sklearn": "HistGradientBoosting heads, library defaults, "
                       "random_state pinned",
        },
    }
    m = os.path.join(root, "results", "REUSE_VECTORIZE_MEASUREMENT.json")
    if os.path.exists(m):
        mm = json.load(open(m))
        out["reuse_measurement_sha256"] = sha256_file(m)
        out["vectorizable_fraction_loop_vs_exact"] = mm.get(
            "vectorizable_fraction_loop_vs_exact")
        out["exact_t0_ms_per_candidate"] = mm.get(
            "exact_t0_ms_per_candidate")
    return out


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
    a3 = json.load(open(os.path.join(ROOT, "FREEZE_V1_AMEND_3.json")))
    a4 = json.load(open(os.path.join(ROOT, "FREEZE_V1_AMEND_4.json")))
    assert shas["FREEZE_V1.json"] == a3["freeze_v1_sha256"], "V1 sha drift in A3"
    assert shas["FREEZE_V1_AMEND_1.json"] == a3["amend_1_sha256"], "A1 drift in A3"
    assert shas["FREEZE_V1_AMEND_2.json"] == a3["amend_2_sha256"], "A2 drift in A3"
    assert shas["FREEZE_V1_AMEND_4.json"] == \
        a4.get("amend_4_sha256", shas["FREEZE_V1_AMEND_4.json"]), "A4 self-bind drift"
    assert sha256_file(os.path.join(
        ROOT, "FREEZE_V1_AMEND_3.json")) == a4["amend_3_sha256"], "A3 sha drift in A4"

    # ---- GS constants embedded verbatim from the modules (single source)
    from morphology.gs_bound import (GS_BOUND_V1,
                                     gs_bound_closed_form_size)
    from search.novelty_viability import (GS_NOVELTY_BOUNDS, GS_NOVELTY_DIMS,
                                          GS_NOVELTY_REGISTRY)
    from search.successive_halving import (GS_ETA, GS_LATE_BLOOMER_FRACTION,
                                           GS_MIN_PROMOTE, GS_RUNGS)
    from search.surrogate_allocate import (GS_SUR_DEPTH, GS_SUR_K,
                                           GS_SUR_SUBSPACE, GS_SUR_TREES,
                                           SURROGATE_ID)
    from evaluation.t3_ecology import T3_FAMILIES, t3_draw
    from search.novelty_viability import viability_gate  # noqa: F401
    # admission bar declared PROSPECTIVELY per arm (#221 amend-5): every
    # arm states the bar its candidates must clear BEFORE any scored run.
    ADMISSION_BAR = ("viability_gate == True (hard gates GATE_CORRECTNESS, "
                     "GATE_INVARIANTS, GATE_PROTECTED_ISOLATION, "
                     "GATE_REVOCATION_FIDELITY, GATE_CAPABILITY_FLOOR "
                     "solved_fraction >= 0.5) at the arm's tier ladder; "
                     "identical across all arms — lane/rank choice never "
                     "relaxes it, and GS-R1h batch tasks inherit it "
                     "unaltered (allocation-only)")

    n_gs = gs_bound_closed_form_size()
    assert isinstance(n_gs, int) and n_gs == 143881920, n_gs

    t3_key = "gs-t3-" + secrets.token_hex(32)
    created_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    freeze = {
        "freeze_id": "GRAND_SEARCH_R1",
        "schema": "GRAND_SEARCH_R1_FREEZE_V1",
        "created_utc": created_utc,
        "created_utc_by": "hpc/freeze_gs.py at freeze time (tool-stamped; "
                          "amend-3 timing-erratum discipline)",
        "governing_plan": "issue #221 sec 18 (operator directive 2026-09-09)",
        "ancestor_chain_sha256": {fn: shas[fn] for fn in _chain},
        "amends": "FREEZE_V1_AMEND_4.json",
        "supersedes_sha256": None,
        "code_digest": code_digest(ROOT),
        "environment": environment,
        "search_bound": {
            "bound_id": "GS_BOUND_V1",
            "size": n_gs,
            "vocab": {k: (list(v) if isinstance(v, (tuple, list)) else v)
                      for k, v in GS_BOUND_V1.items()
                      if isinstance(v, (tuple, list, str, int))},
            "note": "O_basis derived from (units, L, K, R) via operators_for "
                    "— sampling over operators = sampling their enablers",
            "amend5_note": "CENSUS_BOUND_V1 and census-observed maxima are "
                           "DESCRIPTIVE statistics of the amend-1..4 runs, "
                           "never bounds on the mutated space: sampling and "
                           "mutation draw from GS_BOUND_V1's vocabulary "
                           "(12 unit types vs the census's 9), which is the "
                           "sole declared bound of this campaign"},
        "novelty_space": {
            "registry": list(GS_NOVELTY_REGISTRY),
            "dims": list(GS_NOVELTY_DIMS),
            "bounds": [list(b) for b in GS_NOVELTY_BOUNDS],
            "k_nn": 15, "archive_cap": 4096, "archive_floor": 64,
        },
        "successive_halving": {
            "eta": GS_ETA, "rungs": list(GS_RUNGS),
            "late_bloomer_fraction": GS_LATE_BLOOMER_FRACTION,
            "min_promote": GS_MIN_PROMOTE,
            "tier_defs": {
                "T0": "evaluation/evaluate.py evaluate_genome tier T0 "
                      "(V1 exact micro-worlds)",
                "T1": "evaluation/gs_t1.py evaluate_t1 = run_lifetime2("
                      "reset=False), tier-labelled T1 (GS definition; "
                      "evaluate.py T1 stays NotImplementedError for MZ-D7)",
                "T2": "evaluation/evaluate.py evaluate_genome tier T2 "
                      "(developmental lifetime + reset control)"},
        },
        "surrogate": {
            "surrogate_id": SURROGATE_ID,
            "k": GS_SUR_K, "n_trees": GS_SUR_TREES,
            "depth": GS_SUR_DEPTH, "subspace": GS_SUR_SUBSPACE,
            "role": "ranks promotions ONLY; never an OCM component (#71); "
                    "predictions never count as earned capability"},
        "failure_memory": {
            "schema": "GS_FAILURE_V1",
            "auto_append": "every failed evaluation task (gate failure or "
                           "crash) appends candidate_id/tier/counterexample/"
                           "one-stage attribution",
            "next_round_use": "gate/sampler prior — never a skip rule "
                              "(skipping would bias cost comparisons)"},
        "arms": {
            "GSA1_units": {"algorithm": "novelty+viability SH", "lane": "units",
                           "rank": "novelty", "seeds": [0, 1, 2, 3, 4, 5],
                           "t0_budget_per_seed": 45000, "n0": 729,
                           "admission_bar": ADMISSION_BAR},
            "GSA2_hetero": {"algorithm": "novelty+viability SH", "lane": "hetero",
                            "rank": "novelty", "seeds": [0, 1, 2, 3, 4, 5],
                            "t0_budget_per_seed": 45000, "n0": 729,
                            "admission_bar": ADMISSION_BAR},
            "GSA3_farch": {"algorithm": "novelty+viability SH", "lane": "farch",
                           "rank": "novelty", "seeds": [0, 1, 2, 3, 4, 5],
                           "t0_budget_per_seed": 45000, "n0": 729,
                           "admission_bar": ADMISSION_BAR},
            "GSA4_obasis": {"algorithm": "novelty+viability SH", "lane": "obasis",
                            "rank": "novelty", "seeds": [0, 1, 2, 3, 4, 5],
                            "t0_budget_per_seed": 45000, "n0": 729,
                           "admission_bar": ADMISSION_BAR},
            "GSA5_surrogate": {"algorithm": "surrogate-ranked SH",
                               "lane": "hetero", "rank": "surrogate_allocation",
                               "seeds": [0, 1, 2, 3, 4, 5],
                               "t0_budget_per_seed": 45000, "n0": 729,
                               "admission_bar": ADMISSION_BAR + "; surrogate "
                               "ranks promotions ONLY, never waives a gate"},
            "GSR_random_control": {"algorithm": "SH, random rank",
                                   "lane": "uniform", "rank": "random",
                                   "seeds": [0, 1, 2, 3, 4, 5],
                                   "t0_budget_per_seed": 45000, "n0": 729,
                                   "admission_bar": ADMISSION_BAR},
            "GSE_sweep": {"algorithm": "exhaustive enumeration of "
                                       "GS_BOUND_V1 (sharded, viability only)",
                          "shards": 288, "shard_size": n_gs // 288,
                          "admission_bar": ADMISSION_BAR + "; no SH ladder — "
                          "every enumerated candidate faces the gates once"},
        },
        "wall_clock_budget_h": 24,
        "heldout_t3": {
            "t3_key_id": "GSHeldoutT3V1:" + hashlib.sha256(
                t3_key.encode()).hexdigest()[:16],
            "key_sha256": hashlib.sha256(t3_key.encode()).hexdigest(),
            "families": list(T3_FAMILIES),
            "draw": t3_draw(t3_key),
            "evaluated_only_on": "R1 survivors (T2-viable distinct "
                                 "phenotypes across GSA arms)",
            "floor": "CAPABILITY_FLOOR_V1 = 0.5 (unchanged)"},
        "t3_key": t3_key,
        "baselines_acceleration": _baselines(ROOT),
        "metric_acceleration": {
            "gs": "distinct T2-viable phenotype digests per CPU-hour per "
                  "GSA arm, all seeds and all failed evals charged",
            "baseline": "frozen_baseline.morphologies_per_cpu_hour "
                        "(amend-3 T2, matched 40k-eval budget)"},
        "terminal_rules_first_match": [
            {"order": 1, "id": "CANNOT_CHECK_NO_SCORED_DISPOSITIONS",
             "vocab": "CANNOT_CHECK_NO_SCORED_DISPOSITIONS",
             "condition": "zero search-arm tasks completed with evals"},
            {"order": 2, "id": "MORPHOLOGY_SEARCH_COST_DOMINATES__SWEEP",
             "vocab": "MORPHOLOGY_SEARCH_COST_DOMINATES",
             "condition": "GSE sweep fully complete AND its distinct-viable "
                          "morphologies-per-CPU-hour >= best GSA arm"},
            {"order": 3, "id": "ACCELERATION_POSITIVE",
             "vocab": "DIVERSE_HIGH_PERFORMING_MORPHOLOGIES_FOUND_AT_SCOPE",
             "condition": "best GSA arm morphologies-per-CPU-hour > frozen "
                          "baseline AND >=2 distinct F_arch families among "
                          "that arm's distinct T2-viable survivors"},
            {"order": 4, "id": "ACCELERATION_NEGATIVE",
             "vocab": "MORPHOLOGY_SEARCH_COST_DOMINATES",
             "condition": "all completed GSA arms <= frozen baseline"},
            {"order": 5, "id": "SURROGATE_NOT_TRUSTWORTHY",
             "vocab": "SURROGATE_NOT_TRUSTWORTHY",
             "condition": "GSA5 completed AND GSA5 morphologies-per-CPU-hour "
                          "< median(GSA1..GSA4 completed)"},
            {"order": 6, "id": "MIXED_INTERMEDIATE_NO_TERMINAL",
             "vocab": "CANNOT_CHECK_PARTIAL_DISPOSITIONS",
             "condition": "otherwise (honest partials; round repeats)"},
        ],
        "per_survivor_rules": [
            {"id": "SURVIVOR_T3_GENERALIZATION_HOLD",
             "condition": "survivor feasible on held-out T3"},
            {"id": "SURVIVOR_T3_GENERALIZATION_FAIL",
             "condition": "otherwise"},
        ],
        "forbidden_terminals": ["AGI", "GENERAL_INTELLIGENCE_PROVEN",
                                "NEW_FORM_OF_INTELLIGENCE_PROVEN",
                                "SUPERIOR_TO_NEURAL_INTELLIGENCE",
                                "OPEN_ENDED_EVOLUTION_SOLVED"],
        "status": "frozen_before_scored_runs",
    }

    path = os.path.join(ROOT, FREEZE_NAME)
    if os.path.exists(path):
        raise SystemExit("REFUSED: %s exists — refreeze must supersede by "
                         "recorded sha, never silently rewrite" % FREEZE_NAME)
    with open(path, "w") as fh:
        json.dump(freeze, fh, indent=2, sort_keys=True)
        fh.write("\n")
    fs = sha256_file(path)
    print("FROZE %s" % path)
    print("freeze_sha256=%s" % fs)
    print("created_utc=%s" % created_utc)
    print("code_digest=%s" % freeze["code_digest"])
    print("t3_key_id=%s" % freeze["heldout_t3"]["t3_key_id"])
    print("env_impls=%s" % json.dumps(
        {k: freeze["environment"][k] for k in
         ("novelty_archive_impl", "surrogate_impl")}, sort_keys=True))
    print("baseline=%s %s" % (freeze["baselines_acceleration"]
                              ["frozen_baseline"]["arm"],
                              freeze["baselines_acceleration"]
                              ["frozen_baseline"]["morphologies_per_cpu_hour"]))


if __name__ == "__main__":
    main()
