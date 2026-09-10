"""D19 -- provenance + revocation worlds.

Protocol: D19_D20_PROTOCOL_V1.json (frozen at 11d165b, before this file ran).

Three arms:
  A1 substitution   -- solve provenance N[X] once, revoke by x := 0.
  A2 recomputation  -- re-derive support from scratch with the leaf dead,
                       honouring blockers. Exhaustive, algebra-free truth.
  A3 detector       -- refuse to certify A1 when a negative dependency is
                       present, with its own terminal CANNOT_CHECK_NEGATION_PRESENT.

Every revocation subset of the source set is EXHAUSTED, never sampled.
Every hostile is paired with a clean control that must stay silent.
Python 3.8 compatible, stdlib only, no float in any decision predicate.
"""
from __future__ import annotations

import itertools
import time

from exact.engine import Hypergraph, ProvenanceNX
from exact.worlds_d19d20 import ow4n_worlds, ow4_with_blocker_field

NEGATION_TERMINAL = "CANNOT_CHECK_NEGATION_PRESENT"


# ------------------------------------------------------------ helpers ----
def _incoming(world):
    inc = dict((n, []) for n in world["nodes"])
    for e in world["edges"]:
        inc[e["conclusion"]].append(e)
    return inc


def assert_stratified(world):
    """Premises and blockers must index strictly below their conclusion, so a
    single pass in node order decides every node. Asserted, never assumed."""
    pos = dict((n, i) for i, n in enumerate(world["nodes"]))
    for e in world["edges"]:
        c = pos[e["conclusion"]]
        for p in e["premises"]:
            if pos[p] >= c:
                raise ValueError("non-stratified premise %s -> %s in %s"
                                 % (p, e["conclusion"], world["id"]))
        for b in e.get("blockers", []):
            if pos[b] >= c:
                raise ValueError("non-stratified blocker %s -> %s in %s"
                                 % (b, e["conclusion"], world["id"]))
    return True


def detect_negation(world):
    """A3: distinct terminal when any negative dependency is present."""
    n_block = sum(len(e.get("blockers", [])) for e in world["edges"])
    return (NEGATION_TERMINAL if n_block else "POSITIVE_ONLY"), n_block


def prov_solve(world):
    """A1 base solve. Leaf annotation fires on SOURCES only (nodes with no
    incoming hyperedge). Blockers are structurally invisible to the engine --
    that laundering is exactly what the negation arm measures."""
    hg = Hypergraph(world["nodes"], world["edges"])
    vals, stats = hg.solve(ProvenanceNX(),
                           leaf_annotation=lambda n: {frozenset([n]): 1})
    return vals, stats


def subst0(poly, dead):
    """Revoke every variable in `dead` by substituting it to 0."""
    return dict((m, c) for m, c in poly.items() if not (m & dead))


def accepted_by_substitution(polys, nodes, dead):
    return set(n for n in nodes if subst0(polys[n], dead))


def recompute_support(world, dead, counters=None):
    """A2 ground truth. Node supported iff it is a live source, or some
    incoming edge has every premise supported and NO blocker supported."""
    inc = _incoming(world)
    sup, nv, ev = {}, 0, 0
    for n in world["nodes"]:
        nv += 1
        ins = sorted(inc[n], key=lambda e: e["id"])
        if not ins:
            sup[n] = (n not in dead)
            continue
        ok = False
        for e in ins:
            ev += 1
            if all(sup[p] for p in e["premises"]) \
                    and not any(sup[b] for b in e.get("blockers", [])):
                ok = True
                break
        sup[n] = ok
    if counters is not None:
        counters["node_visits"] += nv
        counters["edge_visits"] += ev
    return set(n for n in world["nodes"] if sup[n])


def _subsets(items):
    items = sorted(items)
    for r in range(len(items) + 1):
        for c in itertools.combinations(items, r):
            yield frozenset(c)


# ------------------------------------------------- primary comparison ----
def compare_arms(worlds, population):
    """Exhaustive A1-vs-A2 comparison over every revocation subset."""
    rows, t0 = [], time.process_time()
    tot = {"pairs": 0, "accept_agree": 0, "reopen_agree": 0,
           "a1_ops": 0, "a2_ops": 0, "touched": 0,
           "alt_support_rescues": 0, "nodes_multi_support": 0}
    for w in sorted(worlds, key=lambda w: w["id"]):
        assert_stratified(w)
        terminal, n_block = detect_negation(w)
        polys, base_stats = prov_solve(w)
        a1_ops = base_stats["node_visits"] + base_stats["edge_visits"]
        a2c = {"node_visits": 0, "edge_visits": 0}
        inc = _incoming(w)
        multi = [n for n in w["nodes"] if len(inc[n]) >= 2]
        a1_base = accepted_by_substitution(polys, w["nodes"], frozenset())
        a2_base = recompute_support(w, frozenset(), a2c)
        pairs = acc_ok = reo_ok = 0
        touched_tot = rescues = 0
        first_disagreement = None
        for S in _subsets(w["sources"]):
            a1 = accepted_by_substitution(polys, w["nodes"], S)
            a1_ops += sum(len(polys[n]) for n in w["nodes"])
            a2 = recompute_support(w, S, a2c)
            acc_match = (a1 == a2)
            reo_match = ((a1_base - a1) == (a2_base - a2))
            pairs += 1
            acc_ok += int(acc_match)
            reo_ok += int(reo_match)
            touched_tot += len(a2_base ^ a2)
            if not (acc_match and reo_match) and first_disagreement is None:
                first_disagreement = {
                    "revoked": sorted(S),
                    "a1_only": sorted(a1 - a2), "a2_only": sorted(a2 - a1)}
            for n in multi:                       # alternate-support rescue
                mons = polys[n]
                died = [m for m in mons if m & S]
                lived = [m for m in mons if not (m & S)]
                if died and lived and n in a2:
                    rescues += 1
        rows.append({
            "population": population, "world": w["id"],
            "nodes": len(w["nodes"]), "edges": len(w["edges"]),
            "sources": len(w["sources"]), "blockers": n_block,
            "detector": terminal,
            "revocation_subsets_exhausted": pairs,
            "accepted_set_agreement": "%d/%d" % (acc_ok, pairs),
            "reopened_set_agreement": "%d/%d" % (reo_ok, pairs),
            "exact_agreement": bool(acc_ok == pairs and reo_ok == pairs),
            "first_disagreement": first_disagreement,
            "touched_state_total": touched_tot,
            "nodes_with_multi_support": len(multi),
            "alt_support_rescues": rescues,
            "a1_lifecycle_ops": a1_ops,
            "a2_lifecycle_ops": a2c["node_visits"] + a2c["edge_visits"]})
        tot["pairs"] += pairs
        tot["accept_agree"] += acc_ok
        tot["reopen_agree"] += reo_ok
        tot["a1_ops"] += a1_ops
        tot["a2_ops"] += a2c["node_visits"] + a2c["edge_visits"]
        tot["touched"] += touched_tot
        tot["alt_support_rescues"] += rescues
        tot["nodes_multi_support"] += len(multi)
    tot["cpu_s"] = round(time.process_time() - t0, 6)
    return rows, tot


# ------------------------------------------------------- H-T72a arm ----
def missing_edge_arm(worlds, drop_one_edge):
    """Planted missing-edge hostile and its clean control share ONE code path.

    drop_one_edge=True  -> H-T72a: the RECORDED provenance omits one edge while
                           ground truth keeps it. Expect under-reopen witnesses.
    drop_one_edge=False -> CLEAN CONTROL: complete record. Expect exactly zero.
    """
    witnesses, trials = [], 0
    for w in sorted(worlds, key=lambda w: w["id"]):
        edge_ids = [e["id"] for e in sorted(w["edges"], key=lambda e: e["id"])]
        drops = edge_ids if drop_one_edge else [None]
        for drop in drops:
            rec = dict(w)
            rec["edges"] = [e for e in w["edges"] if e["id"] != drop]
            polys, _ = prov_solve(rec)
            for x in sorted(w["sources"]):
                trials += 1
                S = frozenset([x])
                rec_alive = bool(subst0(polys[w["root"]], S))
                truth_alive = w["root"] in recompute_support(w, S)
                if rec_alive and not truth_alive:
                    witnesses.append({"world": w["id"], "dropped_edge": drop,
                                      "revoked": x, "root": w["root"]})
    return witnesses, trials


# ------------------------------------------------- legacy-leaf census ----
def legacy_leaf_census(control_worlds):
    """Measured observation: the frozen T72 oracle revokes over each world's
    `leaves` field. Count how far that set is from the true source set.
    Revoking a non-source is a no-op on BOTH arms, so such a check is
    structurally trivial. This measures it; it does not re-judge T72."""
    rows, trivial, real, missed = [], 0, 0, 0
    for w in sorted(control_worlds, key=lambda w: w["id"]):
        leaves = set(w.get("legacy_leaves", []))
        src = set(w["sources"])
        non_source = sorted(leaves - src)
        unrevoked = sorted(src - leaves)
        trivial += len(non_source)
        real += len(leaves & src)
        missed += len(unrevoked)
        rows.append({"world": w["id"], "legacy_leaves": sorted(leaves),
                     "true_sources": sorted(src),
                     "non_source_targets_noop": non_source,
                     "sources_never_revoked": unrevoked})
    return {"per_world": rows,
            "legacy_targets_that_are_true_sources": real,
            "legacy_targets_that_are_noops": trivial,
            "true_sources_legacy_never_revokes": missed}


# ------------------------------------------------------------- run ----
def run_d19():
    t0w, t0c = time.time(), time.process_time()
    ctl = ow4_with_blocker_field()      # OW4, zero blockers: CLEAN CONTROL
    neg = ow4n_worlds()                 # OW4N, >=1 blocker: negation arm

    ctl_rows, ctl_tot = compare_arms(ctl, "OW4_control_positive")
    neg_rows, neg_tot = compare_arms(neg, "OW4N_negative_dependencies")

    # ---- H-T72a planted missing edge + its clean control
    h72a_w, h72a_trials = missing_edge_arm(ctl, drop_one_edge=True)
    ctl72a_w, ctl72a_trials = missing_edge_arm(ctl, drop_one_edge=False)

    # ---- H-D19b negation laundering + its clean control
    neg_detector_fired = sum(1 for r in neg_rows
                             if r["detector"] == NEGATION_TERMINAL)
    ctl_detector_fired = sum(1 for r in ctl_rows
                             if r["detector"] == NEGATION_TERMINAL)
    neg_disagreeing = sum(1 for r in neg_rows if not r["exact_agreement"])
    ctl_disagreeing = sum(1 for r in ctl_rows if not r["exact_agreement"])

    hostiles = [
        {"id": "H-T72a",
         "plant": "one hyperedge deleted from the recorded provenance "
                  "hypergraph while ground truth keeps it",
         "expected": "under-reopen: a node stays accepted under substitution "
                     "although its true last support died",
         "flipped": len(h72a_w) > 0,
         "witnesses": len(h72a_w), "trials": h72a_trials,
         "first_witnesses": h72a_w[:5],
         "clean_control_witnesses": len(ctl72a_w),
         "clean_control_trials": ctl72a_trials,
         "clean_control_silent": len(ctl72a_w) == 0},
        {"id": "H-D19b",
         "plant": "negative dependency present (OW4N blockers) but evaluated "
                  "with positive-only N[X], which launders the blocker",
         "expected": "positive substitution disagrees with recomputation on "
                     "OW4N and the detector fires on every OW4N world",
         "flipped": bool(neg_disagreeing > 0
                         and neg_detector_fired == len(neg_rows)),
         "ow4n_worlds_disagreeing": neg_disagreeing,
         "ow4n_worlds": len(neg_rows),
         "detector_fired_on_ow4n": neg_detector_fired,
         "clean_control_worlds_disagreeing": ctl_disagreeing,
         "clean_control_detector_fired": ctl_detector_fired,
         "clean_control_silent": bool(ctl_disagreeing == 0
                                      and ctl_detector_fired == 0),
         "terminal": NEGATION_TERMINAL},
    ]

    control_exact = bool(ctl_tot["accept_agree"] == ctl_tot["pairs"]
                         and ctl_tot["reopen_agree"] == ctl_tot["pairs"])
    verdict = ("EXACT_AGREEMENT" if control_exact else "DISAGREEMENT_FOUND")
    if not all(h["clean_control_silent"] for h in hostiles):
        verdict = "CONTROL_FALSE_ALARM"
    elif not all(h["flipped"] for h in hostiles):
        verdict = "HOSTILE_DID_NOT_FLIP"

    out = {
        "experiment": "D19", "protocol": "D19_D20_PROTOCOL_V1.json",
        "freeze_commit": "11d165b77ada54cc3dbc286f5ecc9369a7560896",
        "evidence_class": "CONFIRMATORY_FIXED",
        "verdict": verdict,
        "positive_control": {
            "population": "OW4 (8 worlds, zero blockers)",
            "revocation_subsets_exhausted": ctl_tot["pairs"],
            "accepted_set_agreement": "%d/%d" % (ctl_tot["accept_agree"],
                                                 ctl_tot["pairs"]),
            "reopened_set_agreement": "%d/%d" % (ctl_tot["reopen_agree"],
                                                 ctl_tot["pairs"]),
            "exact": control_exact,
            "touched_state_total": ctl_tot["touched"],
            "nodes_with_multi_support": ctl_tot["nodes_multi_support"],
            "alt_support_rescues": ctl_tot["alt_support_rescues"],
            "a1_lifecycle_ops": ctl_tot["a1_ops"],
            "a2_lifecycle_ops": ctl_tot["a2_ops"],
            "substitution_vs_recomputation_op_ratio":
                round(ctl_tot["a2_ops"] / max(1, ctl_tot["a1_ops"]), 3)},
        "negation_population": {
            "population": "OW4N (8 worlds, >=1 blocker each)",
            "revocation_subsets_exhausted": neg_tot["pairs"],
            "accepted_set_agreement": "%d/%d" % (neg_tot["accept_agree"],
                                                 neg_tot["pairs"]),
            "reopened_set_agreement": "%d/%d" % (neg_tot["reopen_agree"],
                                                 neg_tot["pairs"]),
            "terminal": NEGATION_TERMINAL,
            "note": "positive-only N[X] is NOT certified on this population; "
                    "the disagreement IS the T73 boundary made empirical"},
        "hostiles": hostiles,
        "legacy_leaf_census": legacy_leaf_census(ctl),
        "per_world_control": ctl_rows,
        "per_world_negation": neg_rows,
        "claim_ceiling": "P2 finite certificate over frozen tiny worlds, "
                         "revocation subsets exhausted; not a universal proof.",
        "wall_s": round(time.time() - t0w, 4),
        "cpu_s": round(time.process_time() - t0c, 4)}

    rec = []
    for r in ctl_rows + neg_rows:
        rec.append({"job": "D19", "world_id": r["world"],
                    "population": r["population"],
                    "obligation_nodes": r["nodes"], "hyperedges": r["edges"],
                    "provenance_sources": r["sources"],
                    "negative_dependencies": r["blockers"],
                    "revocation_subsets_exhausted":
                        r["revocation_subsets_exhausted"],
                    "accepted_set_agreement": r["accepted_set_agreement"],
                    "reopened_set_agreement": r["reopened_set_agreement"],
                    "exact_agreement": r["exact_agreement"],
                    "touched_state": r["touched_state_total"],
                    "alt_support_rescues": r["alt_support_rescues"],
                    "a1_lifecycle_ops": r["a1_lifecycle_ops"],
                    "a2_lifecycle_ops": r["a2_lifecycle_ops"],
                    "negative_or_cannot_check_status":
                        r["detector"] if r["blockers"] else None,
                    "certificate_ceiling":
                        "P2 finite certificate, not universal proof"})
    return out, rec
