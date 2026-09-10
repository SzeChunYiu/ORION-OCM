#!/usr/bin/env python3
"""DEV-CAL-1 runner (#323 sec 5; DEV_CAL_1_PROTOCOL_FREEZE_V1).

Executes the prospectively frozen 2x2 calibration: cells A/B/C/D x
{ORACLE_HISTORY, RESET, SHUFFLED_HISTORY} x 30 worlds x 3 seeds, with the
fail-closed structural-certificate checker, the history purity checker
(hostile + clean controls), the full HDI-14 cost ledger, live search-geometry
receipts (SEARCH_GEOMETRY_RECEIPT_SCHEMA_V1), shuffle-equal-n null,
draw-invariance control, bootstrap CIs, and the frozen terminal decision.

OCM_CONTINUED: OMITTED_WITH_REASON (recorded in results and every receipt
set): no natural OCM developmental history exists for these world families
in the machinery (the D27 lifetime2 runtime operates on Form-Oracle genome
tasks, not typed-operator decomposition worlds); constructing one would be a
fabricated history, which the protocol forbids.

Usage:
  python3 -m exact.run_devcal1 --shard k/n     # k in 1..n, writes shard files
  python3 -m exact.run_devcal1 --merge N       # merges shards, decides terminal
Exit codes: 0 = completed; 4 = terminal ASSAY_DEFECT; 3 = CANNOT_CHECK setup.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
RECEIPTS = os.path.join(HERE, "receipts")

SEEDS = (0, 1, 2)
ARMS = ("ORACLE_HISTORY", "RESET", "SHUFFLED_HISTORY")
BOOT_N = 10000
PERM_N = 10000
EFFECT_THRESHOLD = 0.20

OCM_CONTINUED_OMISSION = {
    "arm": "OCM_CONTINUED",
    "status": "OMITTED_WITH_REASON",
    "reason": "no natural OCM developmental history exists for the DEV-CAL-1 "
              "world families anywhere in the machinery; the only runnable "
              "OCM runtime (research/ocm-form-oracle-v1 evaluation.lifetime2 "
              "over morphology genomes) operates on Form-Oracle tasks and "
              "cannot consume typed-operator decomposition worlds without "
              "new adapter code, which would fabricate rather than record a "
              "developmental history; protocol forbids fabrication",
}


def _bootstrap_ci(values, stat_fn, n=BOOT_N, seed=20260910):
    rng = random.Random(seed)
    stats = []
    vals = list(values)
    if not vals:
        return None
    for _ in range(n):
        sample = [vals[rng.randrange(len(vals))] for _ in range(len(vals))]
        stats.append(stat_fn(sample))
    stats.sort()
    return (stats[int(0.025 * n)], stats[int(0.975 * n)])


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def run_world(arm, world, seed, acquisition):
    import exact.devcal1_search as S
    rec = S.run_search(arm, world, seed)
    if rec.get("status") != "OK":
        return rec
    if arm in ("ORACLE_HISTORY", "SHUFFLED_HISTORY"):
        rec["cost_ledger"]["acquisition"] = acquisition
        rec["total_burden_incl_acquisition"] = (
            rec["recorded_before_solution_discovery"]
            ["work_to_first_verified_success"] + acquisition)
        # purity: checker-computed m_star_in_history (never asserted)
        oracle, shuffled = S.build_histories(world)
        history = oracle if arm == "ORACLE_HISTORY" else shuffled
        target = world["target"]
        solution_obj = {
            "method": [list(map(list, rec["_m_star_shape"])),
                       rec["_m_star_slot"]],
            "value": target["goal"],
        }
        from exact.devcal1_certificates import purity_check
        pure, detail = purity_check(history, world, solution_obj)
        rec["purity"] = {"pure": pure, **detail}
        rec["m_star_in_history"] = (False if pure is True
                                    else True if pure is False else None)
        if pure is not True:
            rec["classification_override"] = "SOLUTION_EPISODIC"
    return rec


def shard_main(k, n):
    import exact.devcal1_worlds as W
    import exact.devcal1_search as S
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(RECEIPTS, exist_ok=True)
    t0 = time.time()
    worlds = W.all_worlds()
    receipts = []
    partial = {"shard": "%d/%d" % (k, n), "worlds": {}}
    # acquisition costs: measured once per world (seed 0 source search)
    acquisition = {}
    for w in worlds:
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        src = S.source_acquisition_cost(w, 0)
        if src.get("status") != "OK":
            raise SystemExit("DC1 source search failed for %s: %s"
                             % (wid, src.get("status")))
        acquisition[wid] = src["work"]
    for wi, w in enumerate(worlds):
        if (wi % n) + 1 != k:
            continue
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        for arm in ARMS:
            for seed in SEEDS:
                rec = run_world(arm, w, seed, acquisition[wid])
                rec.pop("_m_star_shape", None)
                rec.pop("_m_star_slot", None)
                receipts.append(rec)
        partial["worlds"][wid] = {
            "acquisition": acquisition[wid],
            "n_receipts": len(receipts),
        }
    with open(os.path.join(RECEIPTS,
                           "DEVCAL1_receipts_shard%d.jsonl" % k), "w",
              encoding="utf-8") as f:
        for row in receipts:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")
    with open(os.path.join(RESULTS,
                           "DEVCAL1_partial_shard%d.json" % k), "w",
              encoding="utf-8") as f:
        json.dump(partial, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    print("shard %d/%d done: %d receipts, %.1fs" %
          (k, n, len(receipts), time.time() - t0))
    return 0


def merge_main(nshards):
    import exact.devcal1_worlds as W
    import exact.devcal1_certificates as C
    t0 = time.time()
    rows = []
    for k in range(1, nshards + 1):
        p = os.path.join(RECEIPTS, "DEVCAL1_receipts_shard%d.jsonl" % k)
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    worlds = W.all_worlds()

    # ---- world freeze table + checker verification of every cell label ----
    freeze_table = []
    label_defects = []
    cannot_check_worlds = []
    cert_type_hist = {}
    for w in worlds:
        wid = "%s-%02d" % (w["cell"], w["world_index"])
        rel = C.check_structural_relation(w)
        sur = C.check_surface_relation(w)
        declared_latent = w["declared_latent_same"]
        declared_surface = w["declared_surface_same"]
        ok_latent = rel["latent_same"] == declared_latent
        ok_surface = sur["surface_same"] == declared_surface
        if rel["cannot_check"]:
            cannot_check_worlds.append({"world": wid,
                                        "why": rel["cannot_check"]})
        if not ok_latent or not ok_surface:
            label_defects.append({"world": wid,
                                  "declared_latent_same": declared_latent,
                                  "checked_latent_same": rel["latent_same"],
                                  "declared_surface_same": declared_surface,
                                  "checked_surface_same": sur["surface_same"]})
        if rel["certificate_type"]:
            cert_type_hist[rel["certificate_type"]] = \
                cert_type_hist.get(rel["certificate_type"], 0) + 1
        freeze_table.append({
            "world": wid, "cell": w["cell"],
            "declared_latent_same": declared_latent,
            "certified_latent_same": rel["latent_same"],
            "certificate_type": rel["certificate_type"],
            "certificate_digest": rel["certificate_digest"],
            "checked_surface_same": sur["surface_same"],
            "surface_signature_digest": C.sha(C.canonical_json(sur)),
            "ecology_axes": {kk: (float(vv) if isinstance(vv, float) else vv)
                             for kk, vv in w["ecology_axes"].items()},
        })
    controls = C.hostile_and_clean_controls()

    # ---- burden tables -----------------------------------------------------
    def collect(arm, cell):
        return {("%s-%02d" % (r["cell"], int(r["world_id"].split("-")[1])),
                 r["seed"]):
                r["recorded_before_solution_discovery"]
                ["work_to_first_verified_success"]
                for r in rows
                if r["arm"] == arm and r["cell"] == cell
                and r.get("status") == "OK"}

    def collect_full(arm, cell):
        """Fully-charged burden: history arms also pay the measured upstream
        cost of EARNING their history (ledger acquisition, no amortization);
        RESET pays its search work only."""
        def burden(r):
            w = r["recorded_before_solution_discovery"][
                "work_to_first_verified_success"]
            if r["arm"] == "RESET":
                return w
            return w + r["cost_ledger"].get("acquisition", 0)
        return {("%s-%02d" % (r["cell"], int(r["world_id"].split("-")[1])),
                 r["seed"]): burden(r)
                for r in rows
                if r["arm"] == arm and r["cell"] == cell
                and r.get("status") == "OK"}

    def cell_stats(cell):
        out = {}
        pairs_or, pairs_rs, pairs_sh = [], [], []
        oracle = collect("ORACLE_HISTORY", cell)
        reset = collect("RESET", cell)
        shuffled = collect("SHUFFLED_HISTORY", cell)
        keys = sorted(set(oracle) & set(reset))
        for key in keys:
            pairs_or.append((oracle[key], reset[key]))
        keys_sh = sorted(set(shuffled) & set(reset))
        for key in keys_sh:
            pairs_sh.append((shuffled[key], reset[key]))
        red_or = [(rs - orr) / rs for orr, rs in pairs_or if rs > 0]
        red_sh = [(rs - sh) / rs for sh, rs in pairs_sh if rs > 0]
        # fully-charged variant: oracle also pays the measured upstream cost
        # of EARNING its history (source solve); no amortization (a 2-world
        # economy cannot amortize; cf. QUERY_ECOLOGY_AMENDMENT sigma axis)
        oracle_full = collect_full("ORACLE_HISTORY", cell)
        pairs_full = [(oracle_full[k], reset[k])
                      for k in sorted(set(oracle_full) & set(reset))
                      if reset[k] > 0]
        red_full = [(rs - orr) / rs for orr, rs in pairs_full if rs > 0]

        def arm_ci(d):
            v = list(d.values())
            return {"mean": _mean(v),
                    "ci": _bootstrap_ci(v, _mean)}
        out["arms"] = {"ORACLE_HISTORY": arm_ci(oracle),
                       "RESET": arm_ci(reset),
                       "SHUFFLED_HISTORY": arm_ci(shuffled)}
        out["n_pairs"] = len(pairs_or)
        out["oracle_vs_reset_reduction"] = {
            "mean": _mean(red_or),
            "ci": _bootstrap_ci(red_or, _mean),
            "threshold_met": bool(
                red_or and _mean(red_or) >= EFFECT_THRESHOLD and
                _bootstrap_ci(red_or, _mean)[0] > 0),
            "burden_cis_nonoverlapping": bool(
                oracle and reset and
                _bootstrap_ci(list(oracle.values()), _mean)[1] <
                _bootstrap_ci(list(reset.values()), _mean)[0]),
        }
        out["oracle_vs_reset_reduction_fully_charged"] = {
            "mean": _mean(red_full),
            "ci": _bootstrap_ci(red_full, _mean),
            "note": "history-arm acquisition (measured source solve) "
                    "charged per world, no amortization; reported, not a "
                    "terminal rule input",
        }
        out["shuffled_vs_reset_reduction"] = {
            "mean": _mean(red_sh),
            "ci": _bootstrap_ci(red_sh, _mean),
        }
        # shuffle-equal-n null: permutation test on paired differences
        diffs = [sh - rs for sh, rs in pairs_sh]
        obs = abs(_mean(diffs) or 0.0)
        rng = random.Random(20260910)
        ge = 0
        for _ in range(PERM_N):
            d = [x * (1 if rng.random() < 0.5 else -1) for x in diffs]
            if abs(_mean(d)) >= obs - 1e-12:
                ge += 1
        out["shuffle_equal_n_null"] = {
            "observed_mean_excess": _mean(diffs),
            "p_signflip": ge / PERM_N,
        }
        # per-seed direction (draw-invariance on the primary endpoint)
        by_key = dict(pairs_or_key(cell, oracle, reset))
        per_seed = {}
        for seed in SEEDS:
            reds = [v for (wid, s), v in by_key.items() if s == seed]
            per_seed[str(seed)] = {"mean_reduction": _mean(reds),
                                   "positive_fraction":
                                       (_mean([1 if x > 0 else 0
                                               for x in reds])
                                        if reds else None)}
        directions = [v["mean_reduction"] for v in per_seed.values()
                      if v["mean_reduction"] is not None]
        out["draw_invariance"] = {
            "per_seed": per_seed,
            "direction_agrees": bool(directions) and
            all((d > 0) == (directions[0] > 0) for d in directions),
        }
        # ledgers (HDI-14 completeness)
        fam_missing = []
        led = {a: {"acquisition": [], "storage_bytes": [], "retrieval": [],
                   "rejected_candidates": [], "verification": [],
                   "adaptation": []} for a in ARMS}
        for r in rows:
            if r["cell"] != cell or r.get("status") != "OK":
                continue
            cl = r["cost_ledger"]
            for fam in led[r["arm"]]:
                if fam not in cl or cl[fam] is None:
                    fam_missing.append({"world": r["world_id"],
                                        "arm": r["arm"], "family": fam})
                else:
                    led[r["arm"]][fam].append(cl[fam])
        out["cost_ledger_means"] = {
            a: {fam: _mean(v) for fam, v in fams.items()}
            for a, fams in led.items()}
        out["cost_ledger_missing_families"] = fam_missing
        # purity summary
        pur = [r.get("m_star_in_history") for r in rows
               if r["cell"] == cell and r["arm"] in
               ("ORACLE_HISTORY", "SHUFFLED_HISTORY")
               and r.get("status") == "OK"]
        out["purity"] = {
            "n": len(pur),
            "n_pure": sum(1 for p in pur if p is False),
            "n_impure": sum(1 for p in pur if p is True),
            "n_cannot_check": sum(1 for p in pur if p is not False
                                  and p is not True),
        }
        # rank deltas (HDI-15 secondary): oracle rank vs reset rank per key
        rank_or, rank_rs = {}, {}
        for r in rows:
            if r["cell"] != cell or r.get("status") != "OK":
                continue
            key = (r["world_id"], r["seed"])
            if r["arm"] == "ORACLE_HISTORY":
                rank_or[key] = r["recorded_before_solution_discovery"][
                    "eventual_success_rank"]
            if r["arm"] == "RESET":
                rank_rs[key] = r["recorded_before_solution_discovery"][
                    "eventual_success_rank"]
        deltas = [rank_or[k] - rank_rs[k] for k in
                  set(rank_or) & set(rank_rs)]
        out["rank_delta_oracle_minus_reset"] = {
            "mean": _mean(deltas),
            "n": len(deltas),
            "developmental_direction_count_negative": sum(
                1 for d in deltas if d < 0),
        }
        return out

    def pairs_or_key(cell, oracle, reset):
        return [((wid, seed), (reset[(wid, seed)] - oracle[(wid, seed)])
                 / reset[(wid, seed)])
                for wid, seed in sorted(set(oracle) & set(reset))
                if reset[(wid, seed)] > 0]

    stats = {c: cell_stats(c) for c in ("A", "B", "C", "D")}

    # ---- terminal decision (frozen rules) ----------------------------------
    defects = []
    for name, ctl in controls.items():
        key = "fired" if "fired" in ctl else "silent"
        if not ctl[key]:
            defects.append("checker control %s failed to %s" % (name, key))
    if label_defects:
        defects.append("%d world cell-label checker mismatches" %
                       len(label_defects))
    if cannot_check_worlds:
        defects.append("%d worlds CANNOT_CHECK structural relation" %
                       len(cannot_check_worlds))
    a = stats["A"]["oracle_vs_reset_reduction"]
    if not (a["threshold_met"] and a["burden_cis_nonoverlapping"]):
        defects.append("cell A positive control did not fire "
                       "(mean=%.4f, threshold_met=%s, nonoverlap=%s)" %
                       (a["mean"], a["threshold_met"],
                        a["burden_cis_nonoverlapping"]))
    d = stats["D"]["oracle_vs_reset_reduction"]
    if d["threshold_met"] and d["burden_cis_nonoverlapping"]:
        defects.append("cell D negative control ALARMED (leak): "
                       "mean=%.4f" % d["mean"])
    if not stats["B"]["draw_invariance"]["direction_agrees"]:
        defects.append("draw-invariance failure on primary endpoint in B")
    if any(s["cost_ledger_missing_families"] for s in stats.values()):
        defects.append("HDI-14 ledger family missing (CANNOT_CHECK)")

    b = stats["B"]["oracle_vs_reset_reduction"]
    b_fires = b["threshold_met"] and b["burden_cis_nonoverlapping"]
    purity_b = stats["B"]["purity"]
    terminal_note = None
    if defects:
        terminal = "ASSAY_DEFECT"
    elif not b_fires:
        terminal = "NO_TRANSFERABLE_HEADROOM"
    else:
        # OCM_CONTINUED omitted with recorded reason: OCM did not reach the
        # oracle's reduction (nothing did), and OCM_STRUCTURAL_TRANSFER is
        # unreachable without the arm.  Terminal per frozen rule 2.
        terminal = "TRANSFERABLE_HEADROOM_OCM_MISSES"
        if purity_b["n_impure"] > 0 or purity_b["n_cannot_check"] > 0:
            terminal_note = ("WARNING: impure/unclean history present in B; "
                             "check SOLUTION_EPISODIC classification")
    episodic = {"cell_B": purity_b,
                "rule": "if m* in history, run evidences REUSE "
                        "(SOLUTION_EPISODIC), never development"}

    results = {
        "study": "DEV-CAL-1",
        "protocol": "DEV_CAL_1_PROTOCOL_FREEZE_V1",
        "receipt_schema": "SEARCH_GEOMETRY_RECEIPT_SCHEMA_V1",
        "ecology_amendment": "QUERY_ECOLOGY_AMENDMENT_V1",
        "owner_issue": 323,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                       time.gmtime()),
        "host": os.uname().nodename,
        "wall_s": round(time.time() - t0, 3),
        "n_receipts": len(rows),
        "worlds": {"per_cell": W.WORLDS_DC1_V1["worlds_per_cell"],
                   "seeds_per_world": len(SEEDS),
                   "cert_type_histogram": cert_type_hist,
                   "label_defects": label_defects,
                   "cannot_check_worlds": cannot_check_worlds},
        "checker_controls": controls,
        "arms_run": list(ARMS),
        "ocm_continued": OCM_CONTINUED_OMISSION,
        "per_cell": stats,
        "terminal": terminal,
        "terminal_note": terminal_note,
        "terminal_defects": defects,
        "effect_threshold": EFFECT_THRESHOLD,
        "endpoint_note": "primary endpoint = per-target acquisition burden "
                         "(work_to_first_verified_success, INCLUDING "
                         "retrieval+adaptation ops for history arms; "
                         "compute+information matched across arms); the "
                         "fully-charged variant (history acquisition per "
                         "world, no amortization) is reported per cell but "
                         "is not a terminal-rule input",
        "solution_episodic_classification": episodic,
    }
    with open(os.path.join(RESULTS, "DEVCAL1_RESULTS.json"), "w",
              encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(os.path.join(RECEIPTS, "DEVCAL1_world_freeze_table.json"),
              "w", encoding="utf-8") as f:
        json.dump({"table": freeze_table}, f, indent=1, sort_keys=True,
                  default=repr)
        f.write("\n")
    print("DEV-CAL-1 terminal:", terminal)
    for cell in ("A", "B", "C", "D"):
        s = stats[cell]["oracle_vs_reset_reduction"]
        print("  cell %s: oracle-reset reduction mean=%.4f ci=%s "
              "threshold_met=%s n=%d" %
              (cell, s["mean"] or float("nan"), s["ci"],
               s["threshold_met"], stats[cell]["n_pairs"]))
    if defects:
        for dd in defects:
            print("  defect:", dd)
    print("receipts:", len(rows), "wall_s", results["wall_s"])
    return 0 if terminal != "ASSAY_DEFECT" else 4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default=None,
                    help="k/n where k in 1..n")
    ap.add_argument("--merge", type=int, default=None)
    args = ap.parse_args()
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        return shard_main(k, n)
    if args.merge:
        return merge_main(args.merge)
    print("use --shard k/n or --merge N", file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())
