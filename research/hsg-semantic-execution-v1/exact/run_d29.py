"""D29 -- crossover frontier: Q*(rho) on the frozen RV_B1 machinery.

Protocol: ECONOMY_FRONTIER_PROTOCOLS_V1.json (D29_crossover_frontier), frozen
at 3d82387c before this file ran. Registered prediction under test:
QUERY_ECOLOGY_AMENDMENT_V1.claim_shape_rules.predictions_registered
(rho_star_bracket [0.51, 0.905]).

Machinery discipline ('swap the reader, never the metric'): every frozen RV_B1
module is IMPORTED UNCHANGED (worlds, d20 counters, incremental abstraction,
ceiling guards, op metrics). The only new code is the query-stream generator's
rho dial and the study sweep around it. multi_query_dial below is a
line-for-line copy of rv_b1.multi_query with the query stream injected as a
parameter; the loop, counters and guards are not edited.

rho dial semantics (frozen):
  - Position 0 is the world's ORIGINAL frozen Bad set, exactly as in RV_B1.
  - For positions q >= 1 novelty is decided per-position by the frozen-style
    substream _rng('D29NOV', world_id, q): NOVEL iff rng.random() < rho.
    This is prefix-consistent (novelty of position q never depends on the
    final stream length), so the Q sweep reads cumulative costs off ONE
    stream per (world, rho) -- the same nested-prefix semantics as RV_B1's
    own multi-query rollup.
  - A NOVEL position draws its Bad set from the SAME frozen RVBQ substream
    _rng('RVBQ', world_id, q) that rv_b1.query_bad_sets uses at that
    position -- no new seed is invented for novel draws. At rho = 1.0 every
    position is novel and the stream is byte-identical to the frozen RV_B1
    query stream (asserted at run time, plus an exact-numbers cross-check
    against the committed RV_B1_RESULTS.json).
  - A REPEAT position copies the Bad set of a uniformly chosen earlier
    position via _rng('D29RPT', world_id, q).randrange(q): a query already
    inside the reusable capital's support.
  - Realized novel fraction (position 0 counts as novel) is measured per
    stream prefix and recorded in every receipt; the dial value rho is the
    nominal novel-region fraction of the dialable segment (positions >= 1).

Controls: rho=1.0 stream identity vs rv_b1.query_bad_sets; rho=1.0 aggregate
totals vs the committed RV_B1_RESULTS.json per_q numbers; per-cell
shuffle-equal-n null (deterministic permutations of the exact query multiset,
5 draws) with a draw-invariance verdict on the 1-bit crossing comparison;
ceiling and verdict-match guards on every run (original and shuffled).

Python 3.8 compatible, stdlib only. Runs on a disjoint host, never Mac mini.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time

from exact.worlds import _rng
from exact.worlds_d19d20 import ow5s_worlds
from exact.d20 import _direct_ops, _new_counters, direct_bfs, validate
from exact.rv_b1 import (IncAbstraction, _inc_ops, abstract_bfs_inc,
                         build_pred, query_bad_sets)

RHO_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
Q_GRID = (1, 2, 4, 8, 16, 32)
SHUFFLE_DRAWS = 5

HERE = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------- rho dial ----
def rho_query_stream(w, rho, length):
    """Query stream with the frozen rho dial. Returns (bads, novel_flags)."""
    bads = [list(w["bad"])]
    novel = [True]
    size = max(1, w["n"] // 8)
    for q in range(1, length):
        is_novel = _rng("D29NOV", w["id"], q).random() < rho
        if is_novel:
            rng = _rng("RVBQ", w["id"], q)
            bads.append(sorted(rng.sample(w["states"], size)))
            novel.append(True)
        else:
            src = _rng("D29RPT", w["id"], q).randrange(q)
            bads.append(list(bads[src]))
            novel.append(False)
    return bads, novel


def multi_query_dial(w, bads):
    """rv_b1.multi_query UNCHANGED except the query stream is injected."""
    dctr = _new_counters()
    direct_cum, direct_verdicts = [], []
    for bad in bads:
        wq = dict(w)
        wq["bad"] = bad
        direct_verdicts.append(direct_bfs(wq, dctr))
        direct_cum.append(_direct_ops(dctr))

    ctr = _new_counters()
    ctr["pred_index_ops"] = 0
    ctr["incremental_build_ops"] = 0
    pred = build_pred(w, ctr)
    inc = IncAbstraction(w, w["start_blocks"], ctr)
    k0, n = len(inc.blocks), w["n"]
    ceiling = n - k0
    total_rounds = 0
    inc_cum, inc_verdicts, rounds_cum = [], [], []
    for bad in bads:
        while True:
            verdict, path = abstract_bfs_inc(w, inc, ctr, bad=bad)
            if verdict == "SAFE":
                term = "SAFE"
                break
            wq = dict(w)
            wq["bad"] = bad
            status, spec = validate(wq, inc.blocks, path, ctr)
            if status == "VALID":
                term = "UNSAFE"
                break
            idx, part_a, part_b = spec
            if not part_a or not part_b:
                term = "NO_PROGRESS_DETECTED"
                break
            inc.split(idx, part_a, part_b, pred, ctr)
            total_rounds += 1
            if total_rounds > ceiling:
                term = "CEILING_VIOLATED_ACROSS_QUERIES"
                break
        inc_verdicts.append(term)
        inc_cum.append(_inc_ops(ctr))
        rounds_cum.append(total_rounds)

    return {"queries": len(bads), "direct_cum": direct_cum,
            "inc_cum": inc_cum, "direct_verdicts": direct_verdicts,
            "inc_verdicts": inc_verdicts, "total_rounds": total_rounds,
            "rounds_cum": rounds_cum, "ceiling": ceiling,
            "final_blocks": len(inc.blocks), "n": n, "k0": k0,
            "partition_is_discrete": len(inc.blocks) == n,
            "ceiling_held_across_queries": total_rounds <= ceiling,
            "verdicts_match": direct_verdicts == inc_verdicts,
            "inc_counters": dict(ctr),
            "retained_state_bytes": _retained_bytes(inc)}


def _retained_bytes(inc):
    """MEASURED auxiliary HDI-14 bytes/state family: capital the abstraction
    retains across queries (partition + abstract edges), deterministic
    serialization. NOT part of the frozen op metric; charging it would only
    add abstraction-side cost, so the measured Q*(rho) is conservative for
    the direct arm."""
    obj = {"blocks": sorted(sorted(b) for b in inc.blocks),
           "at": dict((str(u), sorted(str(v) for v in sorted(inc.at[u])))
                      for u in sorted(inc.at))}
    return len(json.dumps(obj, sort_keys=True).encode("utf-8"))


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _rho_tag(rho):
    return ("%g" % rho)


# HDI-14 cost ledger: every family charged-or-justified for BOTH arms.
HDI14_LEDGER = {
    "acquisition": {
        "abstraction": ["abstraction_build_ops", "pred_index_ops"],
        "direct": "STRUCTURAL_ZERO: the direct arm acquires no capital; "
                  "direct_bfs holds no cross-query state"},
    "retrieval": {
        "abstraction": ["abstract_states_expanded",
                        "abstract_transitions_examined"],
        "direct": ["states_expanded", "transitions_examined"]},
    "rejected_candidates": {
        "abstraction": ["validation_ops"],
        "direct": "STRUCTURAL_ZERO: direct search proposes no candidate "
                  "answer to reject"},
    "verification": {
        "abstraction": ["verification_calls"],
        "direct": ["verification_calls"]},
    "adaptation": {
        "abstraction": ["incremental_build_ops"],
        "direct": "STRUCTURAL_ZERO: no capital to adapt"},
    "bytes_state": {
        "abstraction": "MEASURED: retained_state_bytes (auxiliary, "
                       "deterministic serialization of partition + edges)",
        "direct": "MEASURED: 0 (nothing retained between queries)"}
}


def ledger_complete():
    """HDI-14 rule: a family with neither a charged counter nor a justified
    structural zero emits CANNOT_CHECK (never silently 0)."""
    missing = []
    for fam, arms in sorted(HDI14_LEDGER.items()):
        for arm in ("abstraction", "direct"):
            v = arms[arm]
            if not (isinstance(v, list) and v) and not (
                    isinstance(v, str) and ("STRUCTURAL_ZERO" in v
                                            or "MEASURED" in v)):
                missing.append([fam, arm])
    return (not missing), missing


# ---------------------------------------------------------------- run ----
def run_d29(freeze_commit, host_label):
    t0w, t0c = time.time(), time.process_time()
    worlds = sorted(ow5s_worlds(), key=lambda w: w["id"])
    maxq = max(Q_GRID)
    receipts = []

    # control 1: rho=1.0 stream identity with the frozen query generator
    frozen_identity_failures = []
    for w in worlds:
        bads, novel = rho_query_stream(w, 1.0, maxq)
        if bads != query_bad_sets(w, maxq):
            frozen_identity_failures.append(w["id"])

    # control 2: rho=1.0 aggregate totals reproduce the committed RV_B1
    # numbers exactly at the frozen Q points (Q <= 16)
    frozen_results_path = os.path.join(HERE, "results", "RV_B1_RESULTS.json")
    frozen_per_q = None
    if os.path.exists(frozen_results_path):
        with open(frozen_results_path, encoding="utf-8") as f:
            frozen_per_q = json.load(f)["multi_query_amortisation"]["per_q"]
    frozen_numbers_failures = []
    # rho=1.0 per-Q totals summed over worlds (the frozen per_q numbers are
    # 30-world aggregates); compared AFTER the world loop
    rho1_sums = dict((Q, [0, 0]) for Q in Q_GRID)

    led_ok, led_missing = ledger_complete()
    instrument_defects = []
    if frozen_identity_failures:
        instrument_defects.append(
            "RHO1_STREAM_IDENTITY_FAILED:" + ",".join(frozen_identity_failures))
    if not led_ok:
        instrument_defects.append("HDI14_LEDGER_INCOMPLETE:"
                                  + json.dumps(led_missing))

    # per-cell aggregates: cells[(rho, Q)] -> per-draw totals over 30 worlds
    cells = {}
    for rho in RHO_GRID:
        for Q in Q_GRID:
            cells[(rho, Q)] = {
                "direct": [0] * (1 + SHUFFLE_DRAWS),
                "inc": [0] * (1 + SHUFFLE_DRAWS),
                "world_wins": 0, "novel_realized": [],
                "vacuous_shuffle_draws": 0, "runs_defective": 0}

    for w in worlds:
        for rho in RHO_GRID:
            bads, novel = rho_query_stream(w, rho, maxq)
            full = multi_query_dial(w, bads)
            if not full["ceiling_held_across_queries"] \
                    or not full["verdicts_match"]:
                instrument_defects.append(
                    "ORIGINAL_RUN_DEFECT:%s:rho=%s:ceiling=%s:verdicts=%s"
                    % (w["id"], _rho_tag(rho),
                       full["ceiling_held_across_queries"],
                       full["verdicts_match"]))
            receipts.append({
                "row_type": "stream", "job": "D29", "world": w["id"],
                "rho": rho, "stream_len": maxq,
                "novel_flags": [int(v) for v in novel],
                "novel_fraction_realized_at_maxq":
                    round(sum(novel) / float(maxq), 4),
                "bad_set_digests": [hashlib.sha256(
                    json.dumps(b, sort_keys=True).encode()).hexdigest()[:16]
                    for b in bads],
                "total_refinements": full["total_rounds"],
                "final_blocks": full["final_blocks"],
                "partition_is_discrete": full["partition_is_discrete"],
                "retained_state_bytes": full["retained_state_bytes"],
                "ceiling_held": full["ceiling_held_across_queries"],
                "verdicts_match": full["verdicts_match"]})

            for Q in Q_GRID:
                key = (rho, Q)
                d_ops = full["direct_cum"][Q - 1]
                i_ops = full["inc_cum"][Q - 1]
                cell = cells[key]
                cell["direct"][0] += d_ops
                cell["inc"][0] += i_ops
                cell["world_wins"] += int(i_ops <= d_ops)
                cell["novel_realized"].append(round(
                    sum(novel[:Q]) / float(Q), 4))

                shuffle_bits = [i_ops <= d_ops]
                for k in range(1, 1 + SHUFFLE_DRAWS):
                    sh = list(bads[:Q])
                    _rng("D29SHF", w["id"], _rho_tag(rho), Q, k).shuffle(sh)
                    if sh == bads[:Q]:
                        # permutation identical to the original order (always
                        # true at Q=1, sometimes for repeat-heavy streams):
                        # the draw IS the original run; charge its totals so
                        # every draw column aggregates the same 30 worlds
                        cell["vacuous_shuffle_draws"] += 1
                        cell["direct"][k] += d_ops
                        cell["inc"][k] += i_ops
                        shuffle_bits.append(i_ops <= d_ops)
                        continue
                    r2 = multi_query_dial(w, sh)
                    if not r2["ceiling_held_across_queries"] \
                            or not r2["verdicts_match"]:
                        instrument_defects.append(
                            "SHUFFLE_RUN_DEFECT:%s:rho=%s:Q=%d:k=%d"
                            % (w["id"], _rho_tag(rho), Q, k))
                        cell["runs_defective"] += 1
                    cell["direct"][k] += r2["direct_cum"][-1]
                    cell["inc"][k] += r2["inc_cum"][-1]
                    shuffle_bits.append(r2["inc_cum"][-1]
                                        <= r2["direct_cum"][-1])

                receipts.append({
                    "row_type": "cell", "job": "D29", "world": w["id"],
                    "rho": rho, "Q": Q,
                    "novel_fraction_realized": round(sum(novel[:Q])
                                                     / float(Q), 4),
                    "direct_ops": d_ops, "abstraction_ops": i_ops,
                    "ratio_abstraction_over_direct":
                        round(i_ops / max(1, d_ops), 3),
                    "abstraction_wins_world": i_ops <= d_ops,
                    "shuffle_bits": shuffle_bits,
                    "draw_invariant_world": len(set(shuffle_bits)) == 1})

                if rho == 1.0:
                    rho1_sums[Q][0] += d_ops
                    rho1_sums[Q][1] += i_ops

    for Q in Q_GRID:
        if frozen_per_q is not None and str(Q) in frozen_per_q:
            fp = frozen_per_q[str(Q)]
            if rho1_sums[Q][0] != fp["direct_ops"] \
                    or rho1_sums[Q][1] != fp["incremental_ops"]:
                frozen_numbers_failures.append(
                    [Q, rho1_sums[Q][0], fp["direct_ops"],
                     rho1_sums[Q][1], fp["incremental_ops"]])

    if frozen_numbers_failures:
        instrument_defects.append(
            "RHO1_NUMBERS_DIVERGE_FROM_COMMITTED_RV_B1:"
            + json.dumps(frozen_numbers_failures[:5]))

    # ---- rollup: per-(rho, Q) curve, Q*(rho), controls ----
    curve = {}
    for rho in RHO_GRID:
        per_q = {}
        for Q in Q_GRID:
            c = cells[(rho, Q)]
            tot_d, tot_i = c["direct"][0], c["inc"][0]
            # draw-invariance of the aggregate 1-bit comparison: direct
            # totals are order-independent by construction; the abstract
            # totals move under permutation
            agg_bits = [c["inc"][k] <= c["direct"][k]
                        for k in range(1 + SHUFFLE_DRAWS)]
            per_q[str(Q)] = {
                "direct_ops_total": tot_d,
                "abstraction_ops_total": tot_i,
                "ratio_abstraction_over_direct":
                    round(tot_i / max(1, tot_d), 3),
                "abstraction_wins": tot_i <= tot_d,
                "worlds_where_abstraction_wins": c["world_wins"],
                "worlds_total": len(worlds),
                "novel_fraction_realized_min":
                    min(c["novel_realized"]),
                "novel_fraction_realized_max":
                    max(c["novel_realized"]),
                "aggregate_bits_by_draw": agg_bits,
                "draw_invariant": len(set(agg_bits)) == 1,
                "vacuous_shuffle_draws": c["vacuous_shuffle_draws"],
                "runs_defective": c["runs_defective"]}
        curve[_rho_tag(rho)] = {"rho": rho, "per_q": per_q}

    q_star = {}
    for rho in RHO_GRID:
        q_star[_rho_tag(rho)] = None
        for Q in Q_GRID:
            if cells[(rho, Q)]["inc"][0] <= cells[(rho, Q)]["direct"][0]:
                q_star[_rho_tag(rho)] = Q
                break

    # off-grid projection, ONLY where no in-grid crossover exists, mirroring
    # the frozen runner's extrapolation_if_no_crossover discipline: linear
    # fit on the two largest frozen Q points; reported as a PROJECTION, not a
    # measurement; the grid is not extended (a new frozen study).
    off_grid_projection = {}
    for rho in RHO_GRID:
        if q_star[_rho_tag(rho)] is not None:
            continue
        q1, q2 = Q_GRID[-2], Q_GRID[-1]
        md = (cells[(rho, q2)]["direct"][0]
              - cells[(rho, q1)]["direct"][0]) / float(q2 - q1)
        mi = (cells[(rho, q2)]["inc"][0]
              - cells[(rho, q1)]["inc"][0]) / float(q2 - q1)
        fixed = cells[(rho, q2)]["inc"][0] - mi * q2
        off_grid_projection[_rho_tag(rho)] = {
            "marginal_direct_ops_per_query": round(md, 3),
            "marginal_abstraction_ops_per_query": round(mi, 3),
            "marginal_ratio_abstraction_over_direct":
                round(mi / max(1e-9, md), 3),
            "abstraction_fixed_ops": round(fixed, 1),
            "projected_crossover_Q_off_grid":
                (round(fixed / (md - mi), 2) if md > mi else None),
            "status": "PROJECTION, NOT A MEASUREMENT; grid not extended "
                      "(extending the frozen grid is a new frozen study)"}

    # draw-invariance of the ENDPOINT: recompute Q*(rho) under each shuffle
    # draw; the crossing determination must not move under permutation
    q_star_by_draw = {}
    for rho in RHO_GRID:
        per_draw = []
        for k in range(1 + SHUFFLE_DRAWS):
            qs = None
            for Q in Q_GRID:
                if cells[(rho, Q)]["inc"][k] <= cells[(rho, Q)]["direct"][k]:
                    qs = Q
                    break
            per_draw.append(qs)
        q_star_by_draw[_rho_tag(rho)] = per_draw
    unstable_crossing_cells = [
        [_rho_tag(rho), q_star_by_draw[_rho_tag(rho)]]
        for rho in RHO_GRID
        if len(set(q_star_by_draw[_rho_tag(rho)])) != 1]

    finite_rhos = [r for r in RHO_GRID if q_star[_rho_tag(r)] is not None]
    off_rho1_finite = [r for r in finite_rhos if r < 1.0]
    monotone = True
    seq = [q_star[_rho_tag(r)] for r in RHO_GRID]
    known = [v for v in seq if v is not None]
    if known != sorted(known):
        monotone = False
    # finiteness must not reappear once lost
    seen_none = False
    for v in seq:
        if v is None:
            seen_none = True
        elif seen_none:
            monotone = False

    # measured rho-star localisation interval (lo, hi]: lo = largest rho with
    # finite Q*, hi = smallest rho with null Q* (None => above grid)
    if finite_rhos:
        lo = max(finite_rhos)
        null_rhos = [r for r in RHO_GRID if q_star[_rho_tag(r)] is None]
        hi = min(null_rhos) if null_rhos else None
    else:
        lo, hi = None, min(RHO_GRID)
    bracket = [0.51, 0.905]
    if lo is not None and hi is not None:
        interval = (lo, hi)
        bracket_excluded = (hi <= bracket[0]) or (lo > bracket[1])
        bracket_sharpened = (lo >= bracket[0]) and (hi <= bracket[1])
    elif lo is not None:
        interval = (lo, None)
        bracket_excluded = lo > bracket[1]
        bracket_sharpened = False
    else:
        interval = None
        bracket_excluded = True
        bracket_sharpened = False

    clauses = {
        "finite_somewhere_off_rho1": bool(off_rho1_finite),
        "rho1_reproduces_filed_negative":
            q_star["1"] is None,
        "monotone_nondecreasing_in_rho": monotone,
        "rho_star_bracket_not_excluded": not bracket_excluded,
        "rho_star_bracket_sharpened": bracket_sharpened,
        "rho_star_measured_interval": [interval[0], interval[1]]
        if interval else None}

    falsifier_fired = (not off_rho1_finite) or (not monotone)

    if instrument_defects:
        terminal = {"verdict": "CANNOT_CHECK",
                    "reason": "; ".join(instrument_defects[:3]),
                    "defects_total": len(instrument_defects)}
    elif unstable_crossing_cells:
        terminal = {"verdict": "CANNOT_CHECK",
                    "reason": "crossing cell draw-unstable under the "
                              "shuffle-equal-n null: "
                              + json.dumps(unstable_crossing_cells[:3])}
    elif falsifier_fired:
        terminal = {"verdict": "NO_CROSSOVER_ANYWHERE_OFF_RHO1",
                    "protocol_spelling":
                        "NO_CROSSOFF_ANYWHERE_OFF_RHO1 in "
                        "ECONOMY_FRONTIER_PROTOCOLS_V1.json",
                    "statement":
                        "No finite Q*(rho) exists at any rho < 1.0 on the "
                        "frozen grid, or Q* is non-monotone in rho: the "
                        "capital-cost-floor frontier law as stated is wrong "
                        "and must be replaced (RC2 restated)."}
    else:
        terminal = {"verdict": "CROSSOVER_FRONTIER_MEASURED",
                    "statement":
                        "Q*(rho) measured finite off the rho=1 axis on the "
                        "30 frozen RV_B1 worlds; see q_star table."}

    if falsifier_fired and not instrument_defects:
        prediction_verdict = "REFUTED"
    elif (clauses["finite_somewhere_off_rho1"]
          and clauses["monotone_nondecreasing_in_rho"]
          and clauses["rho1_reproduces_filed_negative"]
          and clauses["rho_star_bracket_not_excluded"]
          and clauses["rho_star_bracket_sharpened"]):
        prediction_verdict = "CONFIRMED"
    elif instrument_defects or unstable_crossing_cells:
        prediction_verdict = "CANNOT_CHECK"
    else:
        prediction_verdict = "PARTIAL"

    out = {
        "experiment": "D29", "study": "crossover_frontier",
        "protocol": "ECONOMY_FRONTIER_PROTOCOLS_V1.json#D29_crossover_frontier",
        "protocol_section": "D29_crossover_frontier",
        "registered_prediction_source":
            "QUERY_ECOLOGY_AMENDMENT_V1.json#claim_shape_rules."
            "predictions_registered",
        "freeze_commit": freeze_commit,
        "machinery": "research/hsg-semantic-execution-v1/exact/rv_b1.py "
                     "IMPORTED UNCHANGED; the query-stream generator gains "
                     "the frozen rho dial (reader swap); metric, counters, "
                     "worlds and seeds untouched",
        "rho_dial_semantics": {
            "position_0": "the world's ORIGINAL frozen Bad set (as RV_B1)",
            "novel_position": "_rng('D29NOV', world, q).random() < rho; "
                              "draw = frozen _rng('RVBQ', world, q) sample",
            "repeat_position": "copy of position "
                               "_rng('D29RPT', world, q).randrange(q)",
            "prefix_consistent": True,
            "rho_1_stream_identical_to_frozen": not frozen_identity_failures},
        "grid": {"rho": list(RHO_GRID), "Q": list(Q_GRID)},
        "worlds": len(worlds),
        "q_star": q_star,
        "q_star_table": [{"rho": r, "Q_star": q_star[_rho_tag(r)],
                          "finite": q_star[_rho_tag(r)] is not None}
                         for r in RHO_GRID],
        "off_grid_projection_if_no_crossover": off_grid_projection,
        "total_cost_curves": curve,
        "primary_endpoint_rule":
            "Q*(rho) = smallest Q with abstraction total ops <= direct total "
            "ops, totals summed over the 30 frozen worlds; NULL if no "
            "crossing within the grid",
        "registered_prediction": {
            "text": "Q*(rho) finite iff rho < rho* in [0.51, 0.905]; "
                    "monotone non-decreasing in rho; rho=1.0 reproduces the "
                    "filed negative (crossover_Q null) as the boundary",
            "clauses": clauses,
            "verdict": prediction_verdict},
        "falsifier": {
            "text": "no finite Q*(rho) anywhere off the rho=1 axis, OR Q* "
                    "non-monotone in rho",
            "fired": falsifier_fired},
        "terminal": terminal,
        "cost_ledger_hdi14": {
            "families": HDI14_LEDGER,
            "ledger_complete": led_ok,
            "missing": led_missing,
            "note": "the frozen RV_B1 op metric IS the charged ledger "
                    "(identical counters both arms); retained-state bytes "
                    "are measured additionally and NOT added to the op "
                    "metric (charging them can only increase abstraction "
                    "cost, so measured Q* is conservative for direct)"},
        "controls": {
            "rho1_stream_identity_failures": frozen_identity_failures,
            "rho1_numbers_vs_committed_rv_b1_failures":
                frozen_numbers_failures,
            "shuffle_equal_n_null": {
                "draws": SHUFFLE_DRAWS,
                "rule": "deterministic permutations of the exact per-world "
                        "query multiset per cell; direct totals are "
                        "order-independent by construction",
                "q_star_by_draw": q_star_by_draw,
                "draw_unstable_rhos": unstable_crossing_cells}
        },
        "instrument_defects": instrument_defects,
        "wall_s": round(time.time() - t0w, 4),
        "cpu_s": round(time.process_time() - t0c, 4),
        "host": host_label,
        "python": platform.python_version(),
        "claim_ceiling": "P2 finite certificate over the 30 frozen RV_B1 "
                         "worlds and the swept grid; no universal claim"}
    return out, receipts


def main():
    freeze_commit = os.environ.get("D29_FREEZE_COMMIT", "UNSET")
    host_label = os.environ.get("D29_HOST_LABEL", platform.node())
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "receipts"), exist_ok=True)
    out, rec = run_d29(freeze_commit, host_label)

    res_path = os.path.join(HERE, "results", "D29_RHO_CROSSOVER_RESULTS.json")
    rec_path = os.path.join(HERE, "receipts", "D29_receipts.jsonl")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=repr)
        f.write("\n")
    with open(rec_path, "w", encoding="utf-8") as f:
        for row in rec:
            f.write(json.dumps(row, sort_keys=True, default=repr) + "\n")

    # host receipt binds code + protocol + outputs (byte-repro chain)
    research = os.path.dirname(os.path.dirname(HERE))
    proto = os.path.join(research, "top-tier-atomic-closure-v1",
                         "ECONOMY_FRONTIER_PROTOCOLS_V1.json")
    amend = os.path.join(research, "top-tier-atomic-closure-v1",
                         "QUERY_ECOLOGY_AMENDMENT_V1.json")
    host_rec = {
        "job": "D29", "host": host_label, "hostname": platform.node(),
        "python": platform.python_version(),
        "system": "; ".join(platform.uname()),
        "freeze_commit": freeze_commit,
        "run_d29_sha256": _sha256_file(os.path.join(HERE, "run_d29.py")),
        "rv_b1_sha256": _sha256_file(os.path.join(HERE, "rv_b1.py")),
        "d20_sha256": _sha256_file(os.path.join(HERE, "d20.py")),
        "worlds_sha256": _sha256_file(os.path.join(HERE, "worlds.py")),
        "worlds_d19d20_sha256": _sha256_file(
            os.path.join(HERE, "worlds_d19d20.py")),
        "economy_frontier_protocol_sha256":
            _sha256_file(proto) if os.path.exists(proto) else "ABSENT",
        "query_ecology_amendment_sha256":
            _sha256_file(amend) if os.path.exists(amend) else "ABSENT",
        "results_sha256": _sha256_file(res_path),
        "receipts_sha256": _sha256_file(rec_path),
        "rng_draws": "frozen substreams only (D29NOV/D29RPT/D29SHF new, "
                     "RVBQ reused); world seeds unchanged"}
    hr_path = os.path.join(HERE, "receipts",
                           "D29_HOST_RECEIPT_%s.json" % host_label)
    with open(hr_path, "w", encoding="utf-8") as f:
        json.dump(host_rec, f, indent=1, sort_keys=True)
        f.write("\n")

    print("D29 terminal:", out["terminal"]["verdict"])
    print("  Q*(rho) table:")
    for row in out["q_star_table"]:
        print("            rho=%-4s  Q*=%s" % (row["rho"], row["Q_star"]))
    print("  prediction verdict:", prediction_line(out))
    print("  instrument defects:", len(out["instrument_defects"]))
    print("  draw-unstable rhos:",
          len(out["controls"]["shuffle_equal_n_null"]["draw_unstable_rhos"]))
    print("  wall_s", out["wall_s"], "cpu_s", out["cpu_s"],
          "host", host_label)
    if out["terminal"]["verdict"] == "CANNOT_CHECK":
        return 5
    return 0


def prediction_line(out):
    rp = out["registered_prediction"]
    c = rp["clauses"]
    return "%s (finite_off_rho1=%s, rho1_null=%s, monotone=%s, interval=%s)" \
        % (rp["verdict"], c["finite_somewhere_off_rho1"],
           c["rho1_reproduces_filed_negative"],
           c["monotone_nondecreasing_in_rho"],
           c["rho_star_measured_interval"])


if __name__ == "__main__":
    sys.exit(main())
