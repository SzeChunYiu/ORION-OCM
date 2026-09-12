"""RV-377-053 - the designated successor of RV-377-052, executing the negative it left standing.

WHAT WAS NEGATIVE. RV-377-052 froze three exact laws and ran them out of sample on the eight-cell grid
`dn_partialorder.CELLS_R2`. Two held completely (precision-gate 80 of 80, negative-twin 16 of 16). The SERVE LAW

    exec_per_query(POSET) < exec_per_query(PROG_SEARCH)   iff   L > w

FAILED, 28 of 32, refuted in the single cell `w6_L6` where L = w and the candidate won anyway. RV-377-052 recorded
the failure, moved the serve law to FALSIFIED_AND_REPLACED, and registered a REPLACEMENT closed form

    poset_cheaper   iff   (L >= 6 or w <= 2)                                   [REGISTERED_FOR_EXPERIMENT]

as "pending a cell at L = 5". That cell was never run, and `next_revival_id: RV-377-053` was never written. This
module is that record.

WHY THE REPLACEMENT IS NOT GOOD ENOUGH, AND WHAT REPLACES IT INSTEAD. RV-377-052's own `new_theory_constraint`
says it plainly:

    "a cost law separating a candidate from a parent must be stated as a comparison of each row's own scaling
     FUNCTION, not as an inequality between the coordinates: N10's candidate scales in w and its search parent in
     the reachable set, and any inequality between w and L is an artefact of the grid on which it was fitted."

`(L >= 6 or w <= 2)` is another inequality between the coordinates, fitted to the sixteen cells of CELLS and
CELLS_R2 (on which it happens to hold 16 of 16). Promoting it would repeat the exact error that produced the
falsified law. So this record tests it out of sample AND, in the same run, tests the thing the constraint actually
asks for: each row's own scaling function, derived from the charged code rather than fitted to a grid.

THE DERIVATION (from `dn_partialorder.Poset.query` and `dn_partialorder.ProgSearch.query`, not from any data).

  POSET serves by `_le(i, j)`, which walks the w clock components and charges ONE `gt` per component, returning 0
  at the first component where clock[i][k] > clock[j][k]. `query` calls `_le(i, j)` and, only if that returns 0,
  `_le(j, i)`. Therefore, per query, at wide precision:

      truth(i,j) = 1  (i precedes j)   -> `_le(i,j)` compares all w components and returns 1.  EXACTLY w ops.
      truth(i,j) = 2  (j precedes i)   -> `_le(i,j)` exits early at some k1 in 1..w, then `_le(j,i)` runs the full
                                          w.                                        EXACTLY k1 + w ops, so in (w, 2w].
      truth(i,j) = 0  (concurrent)     -> both calls exit early.                     EXACTLY k1 + k2 ops, in [2, 2w].

  There is NO L TERM ANYWHERE. The clock has one component per CHAIN, and the number of chains is w. L changes only
  which queries exist and what their truths are - the ecology's query mix - never the cost of serving one of them.
  The 6% drift in POSET's measured mean across L at fixed w, which RV-377-052 reported, is entirely the mix moving.

  PROG_SEARCH serves by `_path(i, j)`, a DFS over the immediate-dependency edge list that charges ONE `EQ` per
  EDGE EXAMINED. Its per-query cost is the size of the explored edge set, which grows with the reachable set, hence
  in BOTH w and L. That is the asymmetry: one row's serve is a function of width alone, the other's is a function
  of the reachable subgraph.

  Both are therefore EXACTLY PREDICTABLE FROM THE DEPENDENCY GRAPH ALONE, with no Machine, no charging and no fit:
  the vector clock is the componentwise longest-path vector, and the DFS is deterministic given the successor-list
  order. `predict_poset_ops` and `predict_search_ops` below compute both by pure graph traversal. If the derivation
  is right they reproduce the charged counters to the unit. That is a far stronger claim than any inequality
  between w and L, and it is what this record freezes.

THE GRID. Widths 5, 7, 9, 16 and chain lengths 5, 7, 10. NOT ONE of these appears in `CELLS` (w in {1,2,4,8},
L in {4,8,12}) or in `CELLS_R2` (w in {2,3,4,6,12}, L in {4,6,8,12}), so all twelve cells are out of sample for
every law on record, and L = 5 - the cell RV-377-052 named as the one its replacement form was "pending" - is
present at four widths.

CALIBRATION DISCLOSED (protocol rule 17). Before freezing, three cells were run to size the grid's runtime:
`w5_L5`, `w9_L10` and `w16_L5`. Their POSET and PROG_SEARCH serve means at wide precision were seen. They are
reported here with the rest but are EXCLUDED from the adjudication count of every closed-form clause; the nine
cells `w5_L7 w5_L10 w7_L5 w7_L7 w7_L10 w9_L5 w9_L7 w16_L7 w16_L10` were not run before the freeze and carry the
verdict. The per-query structural clauses C1-C4 and the exact-predictor clause C5 are checked on all twelve, since
no summary statistic of a calibration cell could have been used to write a per-query identity.
"""
import json
import os
import time

from .dn_partialorder import (Arith, ROWS, THETA, PRECISIONS, _basis, ecology, sha256_of, RES)
from .core import Machine

CELLS_R3 = {
    "w5_L5":   {"w": 5,  "L": 5},
    "w5_L7":   {"w": 5,  "L": 7},
    "w5_L10":  {"w": 5,  "L": 10},
    "w7_L5":   {"w": 7,  "L": 5},
    "w7_L7":   {"w": 7,  "L": 7},
    "w7_L10":  {"w": 7,  "L": 10},
    "w9_L5":   {"w": 9,  "L": 5},
    "w9_L7":   {"w": 9,  "L": 7},
    "w9_L10":  {"w": 9,  "L": 10},
    "w16_L5":  {"w": 16, "L": 5},
    "w16_L7":  {"w": 16, "L": 7},
    "w16_L10": {"w": 16, "L": 10},
}
CALIBRATION_CELLS = ("w5_L5", "w9_L10", "w16_L5")
FROZEN_CELLS = tuple(c for c in CELLS_R3 if c not in CALIBRATION_CELLS)
COLUMN = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"


# ------------------------------------------------------------------- pure-graph predictors (no Machine, no charge)
def clocks_of(eco, order):
    """the vector clock every POSET node ends up holding, computed as a longest-path vector over the DAG.
    This is `Poset.observe` with the arithmetic removed: componentwise max over predecessors, then +1 on own chain."""
    w, n = eco["w"], eco["n"]
    clock = [[0] * w for _ in range(n)]
    for e in order:
        v = [0] * w
        for p in eco["preds"][e]:
            for k in range(w):
                if clock[p][k] > v[k]:
                    v[k] = clock[p][k]
        v[eco["chain_of"][e]] += 1
        clock[e] = v
    return clock


def _le_cost(clock, w, i, j):
    """ops charged by `Poset._le(i, j)`: one GT per component examined, stopping at the first strict excess."""
    for k in range(w):
        if clock[i][k] > clock[j][k]:
            return k + 1, 0
    return w, 1


def predict_poset_ops(eco, clock, q):
    """exact charged op count of `Poset.query(q)` at wide precision, by graph alone."""
    w = eco["w"]
    i, j = q
    c1, ok1 = _le_cost(clock, w, i, j)
    if ok1:
        return c1
    c2, _ = _le_cost(clock, w, j, i)
    return c1 + c2


def succ_of(eco, order):
    """the successor lists `ProgSearch.observe` builds, in the order it builds them (the DFS is order-sensitive)."""
    succ = [[] for _ in range(eco["n"])]
    for e in order:
        for p in eco["preds"][e]:
            succ[p].append(e)
    return succ


def _path_cost(succ, i, j):
    """ops charged by `ProgSearch._path(i, j)`: one EQ per edge examined, LIFO stack, `seen` seeded with i."""
    seen = {i}
    stack = [i]
    ops = 0
    while stack:
        u = stack.pop()
        for v in succ[u]:
            ops += 1
            if v == j:
                return ops, 1
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return ops, 0


def predict_search_ops(eco, succ, q):
    """exact charged op count of `ProgSearch.query(q)`, by graph alone."""
    i, j = q
    c1, ok1 = _path_cost(succ, i, j)
    if ok1:
        return c1
    c2, _ = _path_cost(succ, j, i)
    return c1 + c2


# ------------------------------------------------------------------- instrumented run (per-query charged op counts)
def run_perquery(row, basis, eco, precision="wide", interleaving=0):
    """`dn_partialorder.run` with the exec counter snapshotted around EVERY query, so the per-query charged cost is
    recorded rather than only its mean. Nothing about the charging changes."""
    M = Machine(basis, seed=0)
    ref = ROWS[row](eco, Arith(M, precision))
    M.phase("exec")
    ref.init(M)
    order = eco["interleavings"][interleaving]
    for e in order:
        M.phase("upd")
        ref.observe(M, e)
        M.end_event()
    M.phase("upd")
    ref.finalize(M)
    M.end_event()
    M.phase("exec")
    before_serve = M.L.c["exec"]
    per_q = []
    correct = 0
    for q in eco["queries"]:
        b = M.L.c["exec"]
        a = ref.query(M, q)
        per_q.append(M.L.c["exec"] - b)
        correct += int(a == eco["truth"][q])
    nq = len(eco["queries"])
    return {"row": row, "precision": precision, "capability": round(correct / nq, 4),
            "per_query_ops": per_q, "n_queries": nq,
            "exec_per_query": round((M.L.c["exec"] - before_serve) / nq, 4)}


# ------------------------------------------------------------------- the six clauses
def main(tag="V29_N10_SERVE_LAW", revival="RV-377-053"):
    t0 = time.time()
    basis = _basis(COLUMN)
    cells, clauses = {}, {}
    for cname, spec in CELLS_R3.items():
        w, L = spec["w"], spec["L"]
        eco = ecology(w, L)
        order = eco["interleavings"][0]
        clock = clocks_of(eco, order)
        succ = succ_of(eco, order)
        rec = {"w": w, "L": L, "n": eco["n"], "n_queries": eco["n_queries"], "n_edges": eco["n_edges"],
               "n_ordered_pairs": eco["n_ordered_pairs"], "n_concurrent_pairs": eco["n_concurrent_pairs"],
               "calibration_disclosed": cname in CALIBRATION_CELLS}
        po = {p: run_perquery("POSET", basis, eco, precision=p) for p in PRECISIONS}
        ps = {p: run_perquery("PROG_SEARCH", basis, eco, precision=p) for p in PRECISIONS}
        rec["poset_serve"] = {p: po[p]["exec_per_query"] for p in PRECISIONS}
        rec["search_serve"] = {p: ps[p]["exec_per_query"] for p in PRECISIONS}
        rec["poset_capability"] = {p: po[p]["capability"] for p in PRECISIONS}
        rec["search_capability"] = {p: ps[p]["capability"] for p in PRECISIONS}
        rec["poset_cheaper_wide"] = po["wide"]["exec_per_query"] < ps["wide"]["exec_per_query"]

        # ---- C1 structural bound: no query costs POSET more than 2w, at EITHER precision
        c1 = {p: max(po[p]["per_query_ops"]) <= 2 * w for p in PRECISIONS}
        rec["c1_max_poset_ops"] = {p: max(po[p]["per_query_ops"]) for p in PRECISIONS}
        rec["c1_bound_2w"] = 2 * w
        rec["c1_holds"] = all(c1.values())

        # ---- C2/C3 exact per-query cost by truth class, at wide precision
        fwd = [o for q, o in zip(eco["queries"], po["wide"]["per_query_ops"]) if eco["truth"][q] == 1]
        rev = [o for q, o in zip(eco["queries"], po["wide"]["per_query_ops"]) if eco["truth"][q] == 2]
        con = [o for q, o in zip(eco["queries"], po["wide"]["per_query_ops"]) if eco["truth"][q] == 0]
        rec["c2_forward_all_equal_w"] = bool(fwd) and all(o == w for o in fwd)
        rec["c2_forward_distinct_costs"] = sorted(set(fwd))
        rec["c3_reverse_in_w_2w"] = bool(rev) and all(w < o <= 2 * w for o in rev)
        rec["c3_reverse_range"] = [min(rev), max(rev)] if rev else None
        rec["c3_concurrent_range"] = [min(con), max(con)] if con else None
        rec["c3_concurrent_in_2_2w"] = bool(con) and all(2 <= o <= 2 * w for o in con)
        rec["n_forward"], rec["n_reverse"], rec["n_concurrent"] = len(fwd), len(rev), len(con)

        # ---- C5 exact graph predictor reproduces the charged counter, query by query, at wide precision
        pred_po = [predict_poset_ops(eco, clock, q) for q in eco["queries"]]
        pred_ps = [predict_search_ops(eco, succ, q) for q in eco["queries"]]
        rec["c5_poset_exact"] = pred_po == po["wide"]["per_query_ops"]
        rec["c5_search_exact"] = pred_ps == ps["wide"]["per_query_ops"]
        rec["c5_poset_mismatches"] = sum(1 for a, b in zip(pred_po, po["wide"]["per_query_ops"]) if a != b)
        rec["c5_search_mismatches"] = sum(1 for a, b in zip(pred_ps, ps["wide"]["per_query_ops"]) if a != b)
        rec["c5_predicted_poset_serve"] = round(sum(pred_po) / len(pred_po), 4)
        rec["c5_predicted_search_serve"] = round(sum(pred_ps) / len(pred_ps), 4)

        # ---- C6 the RV-377-052 registered replacement closed form, out of sample
        rec["c6_fitted_form_predicts_poset_cheaper"] = (L >= 6 or w <= 2)
        rec["c6_holds"] = rec["poset_cheaper_wide"] == rec["c6_fitted_form_predicts_poset_cheaper"]
        rec["c6_old_falsified_form_predicts"] = L > w
        rec["c6_old_form_holds"] = rec["poset_cheaper_wide"] == (L > w)
        cells[cname] = rec

    dec = [c for c in CELLS_R3 if c not in CALIBRATION_CELLS]
    # ---- C4 L-independence of the forward cost at fixed width
    byw = {}
    for cname, spec in CELLS_R3.items():
        byw.setdefault(spec["w"], []).append(cells[cname]["c2_forward_distinct_costs"])
    clauses["C4_forward_cost_is_width_alone"] = {
        "per_width_distinct_forward_costs": {str(k): sorted({x for lst in v for x in lst}) for k, v in byw.items()},
        "holds": all(sorted({x for lst in v for x in lst}) == [k] for k, v in byw.items())}
    clauses["C1_poset_bounded_by_2w"] = {"holds": all(cells[c]["c1_holds"] for c in CELLS_R3),
                                         "n_cells": len(CELLS_R3)}
    clauses["C2_forward_costs_exactly_w"] = {"holds": all(cells[c]["c2_forward_all_equal_w"] for c in CELLS_R3),
                                             "n_cells": len(CELLS_R3)}
    clauses["C3_reverse_and_concurrent_in_range"] = {
        "holds": all(cells[c]["c3_reverse_in_w_2w"] and cells[c]["c3_concurrent_in_2_2w"] for c in CELLS_R3),
        "n_cells": len(CELLS_R3)}
    clauses["C5_graph_predictor_is_exact"] = {
        "poset_cells_exact": sum(1 for c in CELLS_R3 if cells[c]["c5_poset_exact"]),
        "search_cells_exact": sum(1 for c in CELLS_R3 if cells[c]["c5_search_exact"]),
        "n_cells": len(CELLS_R3),
        "holds": all(cells[c]["c5_poset_exact"] and cells[c]["c5_search_exact"] for c in CELLS_R3)}
    clauses["C6_fitted_closed_form_out_of_sample"] = {
        "decisive_cells": dec, "n_decisive": len(dec),
        "n_holding": sum(1 for c in dec if cells[c]["c6_holds"]),
        "failing_cells": [c for c in dec if not cells[c]["c6_holds"]],
        "all_twelve_holding": sum(1 for c in CELLS_R3 if cells[c]["c6_holds"]),
        "holds": all(cells[c]["c6_holds"] for c in dec)}
    clauses["C6b_original_falsified_form_out_of_sample"] = {
        "n_holding_of_twelve": sum(1 for c in CELLS_R3 if cells[c]["c6_old_form_holds"]),
        "failing_cells": [c for c in CELLS_R3 if not cells[c]["c6_old_form_holds"]]}

    # ---- C7 the boundary is a genuine surface: same sign(L-w) with opposite verdicts, and same L with opposite verdicts
    same_sign, same_L = [], []
    names = list(CELLS_R3)
    for a in names:
        for b in names:
            if a >= b:
                continue
            ca, cb = cells[a], cells[b]
            if ca["poset_cheaper_wide"] == cb["poset_cheaper_wide"]:
                continue
            sa = (ca["L"] > ca["w"]) - (ca["L"] < ca["w"])
            sb = (cb["L"] > cb["w"]) - (cb["L"] < cb["w"])
            if sa == sb:
                same_sign.append([a, b])
            if ca["L"] == cb["L"]:
                same_L.append([a, b])
    clauses["C7_boundary_is_a_surface"] = {
        "opposite_verdicts_same_sign_of_L_minus_w": same_sign[:12], "n_same_sign": len(same_sign),
        "opposite_verdicts_same_L": same_L[:12], "n_same_L": len(same_L),
        "holds": bool(same_sign) and bool(same_L)}

    receipt = {
        "schema": "StageDNN10ServeLawV1", "run_tag": tag, "revival_record": revival, "issue": 377,
        "theta": THETA, "column": COLUMN, "precisions": list(PRECISIONS), "interleaving": 0,
        "cells_spec": CELLS_R3, "calibration_cells_disclosed": list(CALIBRATION_CELLS),
        "decisive_cells_for_closed_form_clauses": dec,
        "out_of_sample_statement": "widths 5, 7, 9, 16 and chain lengths 5, 7, 10 appear in neither CELLS "
                                   "(w in 1,2,4,8; L in 4,8,12) nor CELLS_R2 (w in 2,3,4,6,12; L in 4,6,8,12)",
        "laws_declared": {
            "C1": "every POSET query costs at most 2w charged ops, at either precision",
            "C2": "at wide precision every query whose truth is 'i precedes j' costs EXACTLY w charged ops",
            "C3": "at wide precision a reverse-ordered query costs in (w, 2w] and a concurrent query in [2, 2w]",
            "C4": "the set of distinct forward-query costs at a given width is exactly {w}, the SAME set at every L: "
                  "POSET's serve carries no L term, and the drift RV-377-052 measured is the query mix moving",
            "C5": "a pure-graph predictor with no Machine and no charging - componentwise longest-path vector clocks "
                  "for POSET, order-faithful DFS for PROG_SEARCH - reproduces the charged per-query op count of both "
                  "rows EXACTLY, query by query, in every cell",
            "C6": "the closed form registered by RV-377-052, 'poset_cheaper iff (L >= 6 or w <= 2)', holds out of "
                  "sample on the nine non-calibration cells",
            "C6b": "the closed form RV-377-052 FALSIFIED, 'poset_cheaper iff L > w', re-tested on this grid",
            "C7": "the cheaper-verdict boundary is a surface in (w, L), not an inequality between them: there exist "
                  "two cells with the same sign of L - w and opposite verdicts, AND two cells with the same L and "
                  "opposite verdicts"},
        "cells": cells, "clauses": clauses,
        "claim_ceiling": "exact charged replay at scope; one declared poset per cell at the registered cross rate, "
                         "one interleaving, one column; the graph predictors are derived from the row source and "
                         "carry no free parameter; no new domain is claimed and N10's REDUCED_TO_PARENT verdict is "
                         "not reopened by this record",
        "seconds": round(time.time() - t0, 1)}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, f"STAGE_DN_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for cname in CELLS_R3:
        r = cells[cname]
        mark = " [calib]" if r["calibration_disclosed"] else ""
        print(f'{cname:9s} n={r["n"]:4d} nq={r["n_queries"]:6d} poset={r["poset_serve"]["wide"]:8.4f} '
              f'search={r["search_serve"]["wide"]:9.4f} cheaper={str(r["poset_cheaper_wide"]):5s} '
              f'C1={str(r["c1_holds"]):5s} C2={str(r["c2_forward_all_equal_w"]):5s} '
              f'C5po={str(r["c5_poset_exact"]):5s} C5ps={str(r["c5_search_exact"]):5s} '
              f'C6={str(r["c6_holds"]):5s}{mark}')
    for k, v in clauses.items():
        print(k, "->", json.dumps({kk: vv for kk, vv in v.items() if kk != "per_width_distinct_forward_costs"}))
    print("seconds", receipt["seconds"], "sha", receipt["receipt_sha256"][:16])
    return receipt


if __name__ == "__main__":
    main()
