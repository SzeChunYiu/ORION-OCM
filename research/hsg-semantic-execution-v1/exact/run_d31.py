"""D31 -- episodic depth law: substitution-vs-recomputation op ratio as a
function of the solution depth d of the recomputation the substitution would
replace, on the frozen D19 machinery.

Protocol: ECONOMY_FRONTIER_PROTOCOLS_V1.json (D31_episodic_depth_law), frozen at
75f032fe before this file ran (the D31 section is byte-identical on origin/main
at 85f7ecf7, verified before the scored run). Registered prediction under test:
ratio is monotone non-increasing in d and crosses 1 at finite d* (D19's 1.07 at
d=1 is the shallow boundary). Falsifier: ratio never drops below 1 with depth
-> EPISODIC_NEVER_PAYS.

Machinery discipline: every frozen D19 module is IMPORTED UNCHANGED (engine,
worlds, worlds_d19d20, d19.compare_arms / prov_solve / subst0 /
recompute_support / assert_stratified). The ONLY new code is the frozen
recompute-depth dial ON THE QUERY FAMILY, exactly as the protocol words it:
"solution depth d of the recomputation the substitution would replace". The
dial is carried by a NEW additive world family OW4D (see ow4d_worlds below);
compare_arms itself runs frozen, line for line, on every arm.

Boundary arm (d = the frozen population): compare_arms on the frozen D19
clean-control population (ow4_with_blocker_field, the 8 frozen OW4 worlds,
seeds untouched) must reproduce the committed D19_RESULTS.json per-world and
aggregate a1/a2 numbers EXACTLY (598/640, ratio 1.07) -- zero divergence, any
divergence is an instrument defect and the run scores nothing.

Ratio convention (recorded, first-class): the frozen field
"substitution_vs_recomputation_op_ratio" carries the value a2_ops/a1_ops =
640/598 = 1.07 (recomputation-over-substitution). The registered D31 anchor
("D19's 1.07 at d=1 is the shallow boundary") therefore anchors the PRIMARY
endpoint r(d) = a2/a1 in the frozen formula. NOTE: NEGATIVES_ROOT_CAUSE_V1.md
("substitution (cheapest capital there is) costs 1.07x recomputation") and the
amendment's SOLUTION_EPISODIC payback_law read the same 1.07 with the OPPOSITE
numerator (capital-over-direct); under that reading the boundary value would be
598/640 = 0.934, already below 1. D31 scores the registered clauses in the
frozen value-anchored convention, emits the inverted reading r_inv = a1/a2
alongside every table entry, and files the gloss defect as a measured finding
(protocol_gloss_defect below) rather than silently picking a reading.

Controls (fail-closed, RC3 both directions):
  - boundary fidelity: live compare_arms == committed D19 numbers (per world
    AND aggregate) -- clean no-alarm control for the op auditor;
  - hostile P1 (op-counter plant): a copy of the per-subset substitution
    charge that counts only SURVIVING monomials (subst0 first, then len) --
    undercharges a1 exactly the way a defective counter would; the independent
    op auditor must FLAG it on every dial world;
  - hostile P2 (truth plant): one world's root membership flipped under one
    revocation subset; the independent brute-force derivation-tree truth
    checker must FLAG it; clean rows silent;
  - brute-force cross-check on EVERY world and node: DP N[X] polynomial ==
    enumerated derivation-tree aggregate (independent engine path);
  - exact_agreement (a1 vs a2 accepted sets) must hold on every dial world
    (zero blockers) -- any disagreement is an instrument defect.

Shuffle-equal-n null: not applicable, recorded reason (deterministic
exhaustive machinery, no sample, no draw, no adaptive selection).

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
from exact.worlds_d19d20 import ow4_with_blocker_field
from exact.d19 import (NEGATION_TERMINAL, _subsets, assert_stratified,
                       compare_arms, detect_negation, prov_solve, subst0)
from exact.engine import Hypergraph, brute_force_value

D_GRID = (1, 2, 4, 8, 16, 32)
N_WORLDS_PER_D = 8
PLANTS = ("survivors_only", "root_flip")
RATIO = "substitution_vs_recomputation_op_ratio"   # frozen field name
HERE = os.path.dirname(os.path.abspath(__file__))


def _d_tag(d):
    return str(d)


# --------------------------------------------------- OW4D depth-dial family ----
def ow4d_worlds(d):
    """Depth-dial query family: controlled solution-depth layered DAGs.

    Additive to the frozen world sets under the frozen additive rule (never
    regenerates an existing world id, never reuses an existing `_rng` key
    prefix; new prefix "D31D"). Mirrors the frozen OW4 generator's densities
    (chain-plus-alternative supports, dual-edge probability 0.6, premise
    fan-in 1-2) while making the ROOT'S SOLUTION DEPTH exactly d:

      layer 0 : nsrc in 1..3 source nodes (no incoming hyperedge)
      layer i : A_i = witness node, exactly 1 edge whose premise is drawn
                from layer i-1 or a source (chain can never shortcut);
                B_i = braid node, one CHAIN edge from B_{i-1} (source if
                i=1) keeping root depth exactly d, plus with probability
                0.6 one ALTERNATIVE-support edge whose premises are
                SOURCES distinct from the chain premise (fan-in 1-2,
                mirroring the frozen k = rng.randint(1, min(j, 2))). Source
                premises keep derivation-tree counts LINEAR in d (an alt
                premise from the braid would multiply tree counts
                Fibonacci-style and break the tiny-exhaustive licence).
      root    : B_d.  All premises index strictly lower layers -> stratified.

    Node names and edge ids follow the frozen OW4 style (g<i>, s<i>); node
    list order is topological. Zero blockers by construction (clean-control
    population). This family is FIXED (this code) before any scored run; the
    densities are mirrored from the frozen generator, not tuned to a curve.
    """
    out = []
    for wi in range(N_WORLDS_PER_D):
        rng = _rng("D31D", d, wi)
        nsrc = rng.randint(1, 3)
        names = ["g%d" % i for i in range(nsrc)]
        srcs = list(names)
        edges, eid = [], 0

        def add_edge(premises, conclusion):
            nonlocal eid
            edges.append({"id": "s%d" % eid,
                          "premises": list(premises),
                          "conclusion": conclusion})
            eid += 1

        prev_a, prev_b = None, None
        for i in range(1, d + 1):
            a_i = "g%d" % len(names)
            names.append(a_i)
            b_i = "g%d" % len(names)
            names.append(b_i)
            # A_i: single chain edge from layer i-1 (or a source at i=1)
            if i > 1:
                cand = [n for n in (prev_b, prev_a) if n is not None] + srcs
            else:
                cand = list(srcs)
            add_edge([rng.choice(cand)], a_i)
            # B_i: chain edge from B_{i-1} (source at i=1) -- keeps root
            # derivation depth exactly d
            chain = prev_b if i > 1 else rng.choice(srcs)
            premises_b = [chain]
            add_edge(premises_b, b_i)
            # B_i: alternative support with the frozen 0.6 dual-edge
            # probability, premise(s) from SOURCES other than the chain
            # premise (fan-in 1-2). Sources-only keeps root derivation-tree
            # counts LINEAR in d (a braid-premise alt edge would multiply
            # them Fibonacci-style and break the tiny-exhaustive licence);
            # skipped when the chain premise is the only source.
            if rng.random() < 0.6:
                alt_pool = [s for s in srcs if s != chain]
                if alt_pool:
                    k = rng.randint(1, min(2, len(alt_pool)))
                    alt = rng.sample(sorted(alt_pool), k)
                    add_edge(alt, b_i)
            prev_a, prev_b = a_i, b_i

        incoming = dict((n, 0) for n in names)
        for e in edges:
            incoming[e["conclusion"]] += 1
        out.append({
            "id": "OW4D-d%02d-%02d" % (d, wi), "nodes": names,
            "edges": edges, "sources": srcs, "root": names[-1],
            "n_blockers": 0, "depth": d,
            "leaves": list(srcs)})
    return out


# ------------------------------------------------------------ helpers ----
def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _retained_bytes(polys):
    """MEASURED auxiliary HDI-14 bytes/state family: capital the substitution
    arm retains between queries (the provenance polynomials), deterministic
    serialization. NOT part of the frozen op metric; charging it can only add
    substitution-side cost, so measured ratios are conservative for
    recomputation."""
    obj = dict((n, len(p)) for n, p in sorted(polys.items()))
    return len(json.dumps(obj, sort_keys=True).encode("utf-8"))


def derivation_depth(world):
    """Independent measurement of the root's solution depth (longest
    premise chain), computed from the world alone. Must equal the dial d."""
    inc = dict((n, []) for n in world["nodes"])
    for e in world["edges"]:
        inc[e["conclusion"]].append(e)
    memo = {}

    def depth(n):
        if n not in memo:
            memo[n] = 0 if not inc[n] else 1 + max(depth(p)
                                                   for e in inc[n]
                                                   for p in e["premises"])
        return memo[n]

    return depth(world["root"])


# ------------------------------------------------- independent auditors ----
def _audit_polys(world):
    """Independent N[X] DP for the op auditor (own code path, never calls
    prov_solve): sources carry {frozenset({n}): 1}; every other node sums
    over incoming edges the product of its premises' polynomials, monomials
    keyed by leaf-set frozensets. Must equal prov_solve's values on clean
    rows -- that identity is exactly what the no-alarm control pins."""
    inc = dict((n, []) for n in world["nodes"])
    for e in world["edges"]:
        inc[e["conclusion"]].append(e)
    poly = {}
    for n in world["nodes"]:
        ins = inc[n]
        if not ins:
            poly[n] = {frozenset([n]): 1}
            continue
        acc = {}
        for e in ins:
            term = {frozenset(): 1}
            for p in e["premises"]:
                nxt = {}
                for m1 in term:
                    for m2 in poly[p]:
                        nxt[m1 | m2] = nxt.get(m1 | m2, 0) + 1
                term = nxt
            for m, c in term.items():
                acc[m] = acc.get(m, 0) + c
        poly[n] = acc
    return poly


def _audit_a2_charge(world):
    """Independent a2 charge (own code path, never calls recompute_support):
    the frozen charge counts every node once per pass and, per node, every
    incoming edge in id order UNTIL the first fully supporting edge (the
    early break is part of the frozen semantics -- committed OW4-00 a2=115,
    not the naive (2^k+1)*(V+E)=126), for the explicit base pass PLUS one
    pass per revocation subset (the empty subset is charged twice: it is
    both the base call and a member of the exhausted subset list)."""
    inc = dict((n, []) for n in world["nodes"])
    for e in world["edges"]:
        inc[e["conclusion"]].append(e)

    def pass_charge(dead):
        nv = ev = 0
        sup = {}
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
        return nv + ev

    total = pass_charge(frozenset())           # the explicit base call
    for s in _subsets(world["sources"]):
        total += pass_charge(s)
    return total


def audit_ops(worlds, rows, charge="frozen"):
    """Auditor A (op counters, INDEPENDENT of compare_arms internals: its own
    N[X] DP and its own charge loops). Recomputes each world's
      a1 = (V+E) [one solve pass] + (number of revocation subsets) *
           sum_n len(poly_n)                          [charge="frozen"]
           -- or, under the PLANTED 'survivors_only' charge (hostile P1),
           sum over subsets of sum_n len(surviving monomials of poly_n),
           which undercharges exactly the way a defective counter would;
      a2 = base pass + one pass per subset, each pass counting every node
            plus every edge examined up to the first supporting edge
            (early break included).
    Returns per-world mismatches against the compare_arms rows. The frozen
    charge on clean rows is the no-alarm control; the planted charge must be
    FLAGGED on every dial world (alarm direction)."""
    by_world = dict((r["world"], r) for r in rows)
    violations = []
    for w in worlds:
        poly = _audit_polys(w)
        subsets = list(_subsets(w["sources"]))
        v_e = len(w["nodes"]) + len(w["edges"])
        if charge == "frozen":
            a1 = v_e + len(subsets) * sum(len(poly[n]) for n in w["nodes"])
        else:
            a1 = v_e
            for s in subsets:
                a1 += sum(len([m for m in poly[n] if not (m & s)])
                          for n in w["nodes"])
        a2 = _audit_a2_charge(w)
        r = by_world[w["id"]]
        if r["a1_lifecycle_ops"] != a1 or r["a2_lifecycle_ops"] != a2:
            violations.append([w["id"], charge, r["a1_lifecycle_ops"], a1,
                               r["a2_lifecycle_ops"], a2])
    return violations


def root_truth_table(world):
    """Auditor B input: the root's acceptance under every revocation subset,
    computed by brute-force DERIVATION-TREE enumeration (independent of both
    subst0 and recompute_support): root alive iff some derivation tree of the
    root has no leaf in S. {frozenset(S): bool}."""
    hg = Hypergraph(world["nodes"], world["edges"])
    trees = list(hg.enumerate_trees(world["root"]))

    def tree_leaves(t):
        if t[0] == "leaf":
            return set([t[1]])
        out = set()
        for sub in t[1]:
            out |= tree_leaves(sub)
        return out

    leaves = [tree_leaves(t) for t in trees]
    table = {}
    for s in _subsets(world["sources"]):
        table[s] = any(not (lv & s) for lv in leaves)
    return table


def audit_truth(worlds, flip=None):
    """Auditor B (truth, independent of both arm semantics): root membership
    under every revocation subset via brute-force derivation trees, compared
    against the substitution arm's root membership (subst0 on the root poly)
    and the recomputation arm's (recompute_support). flip=(world_id, k) plants
    ONE inverted root membership row (hostile P2) by flipping the recorded
    substitution membership of the k-th subset of that world; the auditor must
    flag it, and clean rows must stay silent."""
    from exact.d19 import accepted_by_substitution, recompute_support
    violations = []
    flipped = False
    for w in worlds:
        polys, _ = prov_solve(w)
        truth = root_truth_table(w)
        subsets = sorted(_subsets(w["sources"]))
        for k, s in enumerate(subsets):
            sub_alive = w["root"] in accepted_by_substitution(
                polys, w["nodes"], s)
            rec_alive = w["root"] in recompute_support(w, s)
            if flip is not None and flip[0] == w["id"] \
                    and flip[1] == k and not flipped:
                sub_alive = not sub_alive
                flipped = True
            if sub_alive != truth[s] or rec_alive != truth[s]:
                violations.append([w["id"], sorted(s), sub_alive,
                                   rec_alive, truth[s]])
    return violations, flipped


def brute_poly_crosscheck(worlds):
    """Instrument-side cross-check (charged to NEITHER arm): every node's DP
    N[X] polynomial must equal the brute-force derivation-tree aggregate
    (independent engine path), on every world, every node."""
    bad = []
    for w in worlds:
        hg = Hypergraph(w["nodes"], w["edges"])
        polys, _ = prov_solve(w)
        for n in sorted(w["nodes"]):
            bf = brute_force_value(hg, n, "ProvenanceNX")
            if polys[n] != bf:
                bad.append([w["id"], n])
    return bad


# HDI-14 cost ledger: every family charged-or-justified for BOTH arms.
HDI14_LEDGER = {
    "acquisition": {
        "substitution": ["base_solve_ops (one prov_solve pass, V+E)"],
        "recomputation": "STRUCTURAL_ZERO: recomputation acquires no "
                         "capital; every answer is re-derived from the "
                         "world alone"},
    "retrieval": {
        "substitution": ["per-subset poly-scan ops "
                         "(sum_n len(poly), frozen a1 marginal charge)"],
        "recomputation": ["per-subset full pass ops "
                          "(node_visits+edge_visits, frozen a2 charge)"]},
    "rejected_candidates": {
        "substitution": "STRUCTURAL_ZERO: no candidate answer is proposed "
                        "and rejected; acceptance is read off the "
                        "polynomial",
        "recomputation": "STRUCTURAL_ZERO: recomputation IS the ground "
                         "truth; it rejects nothing"},
    "verification": {
        "substitution": "STRUCTURAL_ZERO: no oracle is consulted inside "
                        "the arm; agreement checks are instrument-side",
        "recomputation": "STRUCTURAL_ZERO: the arm is the oracle"},
    "adaptation": {
        "substitution": "STRUCTURAL_ZERO: D19 substitution never rewrites "
                        "the retained polynomials on revocation; subst0 is "
                        "applied read-only per query (charged as retrieval)",
        "recomputation": "STRUCTURAL_ZERO: no capital to adapt"},
    "bytes_state": {
        "substitution": "MEASURED: retained_state_bytes (auxiliary, "
                        "deterministic serialization of the polynomials' "
                        "monomial counts)",
        "recomputation": "MEASURED: 0 (nothing retained between queries)"}
}


def ledger_complete():
    """HDI-14 rule: a family with neither a charged counter nor a justified
    structural zero emits CANNOT_CHECK (never silently 0)."""
    missing = []
    for fam, arms in sorted(HDI14_LEDGER.items()):
        for arm in ("substitution", "recomputation"):
            v = arms[arm]
            if not (isinstance(v, list) and v) and not (
                    isinstance(v, str) and ("STRUCTURAL_ZERO" in v
                                            or "MEASURED" in v)):
                missing.append([fam, arm])
    return (not missing), missing


RECEIPT_COVERAGE = {
    "B_exec vector": "INAPPLICABLE_BY_DESIGN: D19 machinery has no B_exec "
                     "notion",
    "abstraction/refinement count": "INAPPLICABLE_BY_DESIGN: no abstraction "
                                    "loop in the D19 arms",
    "counterexample + version-space shrinkage":
        "INAPPLICABLE_BY_DESIGN: no CEGAR loop; revocation subsets are "
        "exhausted, not counterexample-driven",
    "protected round-trip errors": "INAPPLICABLE_BY_DESIGN: no round trip "
                                   "(interpret/reflect/join) is executed",
    "reduction/proof/rewrite path": "INAPPLICABLE_BY_DESIGN: no reduction or "
                                    "rewrite machinery is exercised",
}


def receipt_row(job, w, r, polys, cpu_s, wall_s, n_root_trees, accepted0):
    """One machine receipt row: every APPLICABLE family of the frozen 13
    emitted or explicitly marked cannot_check (RECEIPT_COVERAGE_V1 rule for
    new studies); inapplicable families are omitted from the row schema by
    design and recorded in RECEIPT_COVERAGE / the results file."""
    mons = [len(polys[n]) for n in sorted(w["nodes"])]
    return {
        "job": job, "world": w["id"], "depth_d": w.get("depth"),
        "row_type": "arm", "terminal": r["detector"],
        "wall_cpu_gpu_io_storage": {
            "wall_s": round(wall_s, 6), "cpu_s": round(cpu_s, 6),
            "gpu": "cannot_check: no GPU is used by this machinery",
            "io": "cannot_check: fully in-memory, no I/O performed",
            "storage": "cannot_check: no persistent storage touched"},
        "obligation_nodes_hyperedges_derivations_sccs": {
            "nodes": r["nodes"], "hyperedges": r["edges"],
            "root_derivation_trees": n_root_trees, "sccs": 0},
        "provenance_supports_alternatives": {
            "root_monomials": len(polys[w["root"]]),
            "total_monomials": sum(mons),
            "nodes_with_multi_support": r["nodes_with_multi_support"],
            "alt_support_rescues": r["alt_support_rescues"]},
        "negative_or_cannot_check_status": r["detector"]
        if r["blockers"] else "POSITIVE_ONLY",
        # active k / total N family: k = nodes accepted under the empty
        # revocation (live substitution support), n = all nodes
        "k": accepted0, "n": r["nodes"],
        "ambiguity_size_entropy": {
            "max_monomials_per_node": max(mons),
            "mean_monomials_per_node": round(
                sum(mons) / float(max(1, len(mons))), 3),
            "entropy": "cannot_check: the machinery forms no probability "
                       "distribution (exact integer counts only)"},
        "operator_library_reuse_identities": {
            "reused_frozen_modules": ["exact.d19.compare_arms",
                                      "exact.d19.prov_solve",
                                      "exact.d19.subst0",
                                      "exact.engine.Hypergraph",
                                      "exact.engine.ProvenanceNX",
                                      "exact.worlds._rng"],
            "note": "imported unchanged; sha256 bound in the host receipt"},
        "revocation_subsets_exhausted": r["revocation_subsets_exhausted"],
        "accepted_set_agreement": r["accepted_set_agreement"],
        "reopened_set_agreement": r["reopened_set_agreement"],
        "exact_agreement": r["exact_agreement"],
        "touched_state": r["touched_state_total"],
        "a1_lifecycle_ops": r["a1_lifecycle_ops"],
        "a2_lifecycle_ops": r["a2_lifecycle_ops"],
        "ratio_frozen_formula": round(
            r["a2_lifecycle_ops"] / max(1, r["a1_lifecycle_ops"]), 4),
        "retained_state_bytes": _retained_bytes(polys),
        "certificate_ceiling": "P2 finite certificate, not universal proof"}


# ---------------------------------------------------------------- run ----
def run_d31(freeze_commit, host_label):
    t0w, t0c = time.time(), time.process_time()
    receipts = []
    instrument_defects = []
    led_ok, led_missing = ledger_complete()
    if not led_ok:
        instrument_defects.append("HDI14_LEDGER_INCOMPLETE:"
                                  + json.dumps(led_missing))

    committed_path = os.path.join(HERE, "results", "D19_RESULTS.json")
    committed = None
    if os.path.exists(committed_path):
        with open(committed_path, encoding="utf-8") as f:
            committed = json.load(f)
    else:
        instrument_defects.append("COMMITTED_D19_RESULTS_ABSENT")

    # ---- boundary arm: frozen population, frozen call, committed numbers
    ctl = ow4_with_blocker_field()
    b_rows, b_tot = compare_arms(ctl, "OW4_control_positive")
    boundary_failures = []
    if committed is not None:
        if len(b_rows) != len(committed["per_world_control"]):
            instrument_defects.append(
                "BOUNDARY_ROW_COUNT_DIVERGES:%d vs %d"
                % (len(b_rows), len(committed["per_world_control"])))
        for r, c in zip(b_rows, committed["per_world_control"]):
            for k in ("nodes", "edges", "sources",
                      "revocation_subsets_exhausted", "exact_agreement",
                      "touched_state_total", "alt_support_rescues",
                      "a1_lifecycle_ops", "a2_lifecycle_ops"):
                if r[k] != c[k]:
                    boundary_failures.append(
                        [r["world"], k, r[k], c[k]])
        cp = committed["positive_control"]
        if b_tot["a1_ops"] != cp["a1_lifecycle_ops"] \
                or b_tot["a2_ops"] != cp["a2_lifecycle_ops"] \
                or b_tot["pairs"] != cp["revocation_subsets_exhausted"]:
            boundary_failures.append(
                ["AGGREGATE", b_tot["a1_ops"], cp["a1_lifecycle_ops"],
                 b_tot["a2_ops"], cp["a2_lifecycle_ops"]])
    if boundary_failures:
        instrument_defects.append(
            "BOUNDARY_DIVERGES_FROM_COMMITTED_D19:"
            + json.dumps(boundary_failures[:5]))
    boundary_ratio = round(b_tot["a2_ops"] / max(1, b_tot["a1_ops"]), 3)
    if committed is not None \
            and boundary_ratio != committed["positive_control"][RATIO]:
        instrument_defects.append(
            "BOUNDARY_RATIO_DIVERGES:%s" % boundary_ratio)
    # clean no-alarm controls on the frozen population too (both auditors)
    ops_b = audit_ops(ctl, b_rows, charge="frozen")
    if ops_b:
        instrument_defects.append(
            "OP_AUDITOR_FALSE_ALARM_BOUNDARY:" + json.dumps(ops_b[:3]))
    truth_b, _ = audit_truth(ctl, flip=None)
    if truth_b:
        instrument_defects.append(
            "TRUTH_AUDITOR_FALSE_ALARM_BOUNDARY:"
            + json.dumps(truth_b[:3]))
    bf_b = brute_poly_crosscheck(ctl)
    if bf_b:
        instrument_defects.append(
            "BRUTE_POLY_CROSSCHECK_FAILED_BOUNDARY:"
            + json.dumps(bf_b[:3]))

    # boundary receipts with per-row timing: the same frozen call per world
    # must reproduce each row of the full-list call exactly (both directions
    # of that identity are checked; a mismatch is an instrument defect)
    b_rows_full = dict((r["world"], r) for r in b_rows)
    for w in sorted(ctl, key=lambda x: x["id"]):
        tw0, tw1 = time.process_time(), time.time()
        rw, _ = compare_arms([w], "OW4_control_positive")
        cpu_w, wall_w = time.process_time() - tw0, time.time() - tw1
        if rw[0] != b_rows_full[w["id"]]:
            instrument_defects.append(
                "BOUNDARY_PER_WORLD_CALL_DIVERGES:" + w["id"])
        polys, _ = prov_solve(w)
        hg = Hypergraph(w["nodes"], w["edges"])
        trees = len(list(hg.enumerate_trees(w["root"])))
        a0 = len([n for n in w["nodes"]
                  if subst0(polys[n], frozenset())])
        receipts.append(receipt_row("D31-boundary", w, rw[0], polys,
                                    cpu_w, wall_w, trees, a0))

    # ---- dial arms + hostile plants + independent auditors
    per_d = {}
    plant_report = {}
    for d in D_GRID:
        tag = "OW4D-d%02d" % d
        worlds_d = sorted(ow4d_worlds(d), key=lambda x: x["id"])
        d_rows = []
        for w in worlds_d:
            assert_stratified(w)                     # raises => defect path
            term, n_block = detect_negation(w)
            if term == NEGATION_TERMINAL or n_block:
                instrument_defects.append(
                    "DIAL_WORLD_NOT_POSITIVE_ONLY:" + w["id"])
            if derivation_depth(w) != d:
                instrument_defects.append(
                    "DIAL_DEPTH_MISMATCH:%s:%d" % (w["id"],
                                                   derivation_depth(w)))
            t0, t1 = time.process_time(), time.time()
            r, _tot = compare_arms([w], tag)
            cpu_w, wall_w = time.process_time() - t0, time.time() - t1
            if not r[0]["exact_agreement"]:
                instrument_defects.append(
                    "DIAL_ARM_DISAGREEMENT:%s:%s" % (
                        w["id"], r[0]["accepted_set_agreement"]))
            d_rows.append((w, r[0], cpu_w, wall_w))

        # brute-force polynomial cross-check (instrument side, all nodes)
        bf_bad = brute_poly_crosscheck(worlds_d)
        if bf_bad:
            instrument_defects.append(
                "BRUTE_POLY_CROSSCHECK_FAILED:" + json.dumps(bf_bad[:3]))

        rows_only = [r for (_w, r, _c, _s) in d_rows]
        # auditor A, no-alarm direction (frozen charge on clean rows)
        ops_clean = audit_ops(worlds_d, rows_only, charge="frozen")
        if ops_clean:
            instrument_defects.append(
                "OP_AUDITOR_FALSE_ALARM:" + json.dumps(ops_clean[:3]))
        # auditor A, alarm direction: planted survivors-only charge
        ops_plant = audit_ops(worlds_d, rows_only,
                              charge="survivors_only")
        plant_report["survivors_only@d=%d" % d] = {
            "flagged_worlds": len(ops_plant),
            "flipped": len(ops_plant) >= 1,
            "reason_if_silent": None if ops_plant else
            "no dial world changed its poly length under any revocation: "
            "alarm direction unvalidated"}
        if not ops_plant:
            instrument_defects.append(
                "HOSTILE_DID_NOT_FLIP:survivors_only@d=%d" % d)

        # auditor B, no-alarm direction (truth table on clean rows)
        truth_clean, _ = audit_truth(worlds_d, flip=None)
        if truth_clean:
            instrument_defects.append(
                "TRUTH_AUDITOR_FALSE_ALARM:" + json.dumps(truth_clean[:3]))
        # auditor B, alarm direction: one planted root-membership flip
        flip_world = worlds_d[0]["id"]
        truth_plant, flipped = audit_truth(worlds_d, flip=(flip_world, 1))
        plant_report["root_flip@d=%d" % d] = {
            "flagged_violations": len(truth_plant),
            "flip_injected": flipped,
            "flipped": bool(flipped and truth_plant),
            "reason_if_silent": None if (flipped and truth_plant) else
            "planted flip was not exercised or not flagged: alarm "
            "direction unvalidated"}
        if not (flipped and truth_plant):
            instrument_defects.append(
                "HOSTILE_DID_NOT_FLIP:root_flip@d=%d" % d)

        # aggregation over the 8 worlds of this d
        a1 = sum(r["a1_lifecycle_ops"] for r in rows_only)
        a2 = sum(r["a2_lifecycle_ops"] for r in rows_only)
        per_d[_d_tag(d)] = {
            "d": d, "worlds": len(worlds_d),
            "nodes_total": sum(r["nodes"] for r in rows_only),
            "edges_total": sum(r["edges"] for r in rows_only),
            "sources_total": sum(r["sources"] for r in rows_only),
            "subsets_total": sum(r["revocation_subsets_exhausted"]
                                 for r in rows_only),
            "a1_lifecycle_ops_total": a1,
            "a2_lifecycle_ops_total": a2,
            "wall_s": round(sum(wl for (_w, _r, _c, wl) in d_rows), 4),
            "cpu_s": round(sum(c for (_w, _r, c, _s) in d_rows), 4)}
        for w, r, cpu_w, wall_w in d_rows:
            polys, _ = prov_solve(w)
            hg = Hypergraph(w["nodes"], w["edges"])
            trees = len(list(hg.enumerate_trees(w["root"])))
            a0 = len([n for n in w["nodes"]
                      if subst0(polys[n], frozenset())])
            receipts.append(receipt_row("D31-dial", w, r, polys,
                                        cpu_w, wall_w, trees, a0))

    # ---- ratio curve in the FROZEN convention r(d) = a2/a1 (the formula
    # that anchors the registered 1.07), plus the inverted reading
    # r_inv(d) = a1/a2 (capital-over-direct, the amendment's prose reading)
    for tag, c in per_d.items():
        c[RATIO] = round(c["a2_lifecycle_ops_total"]
                         / max(1, c["a1_lifecycle_ops_total"]), 4)
        c["ratio_recomputation_over_substitution"] = c[RATIO]
        c["ratio_substitution_over_recomputation"] = round(
            c["a1_lifecycle_ops_total"]
            / max(1, c["a2_lifecycle_ops_total"]), 4)
    seq = [per_d[_d_tag(d)][RATIO] for d in D_GRID]
    seq_inv = [per_d[_d_tag(d)]["ratio_substitution_over_recomputation"]
               for d in D_GRID]
    mono_viol = [[D_GRID[i - 1], D_GRID[i], seq[i - 1], seq[i]]
                 for i in range(1, len(seq)) if seq[i] > seq[i - 1]]
    crossed = [d for d in D_GRID if per_d[_d_tag(d)][RATIO] < 1.0]
    d_star = crossed[0] if crossed else None
    # with the boundary anchor prepended (protocol gloss: the frozen
    # population IS the d=1 shallow boundary value 1.07)
    seq_anchored = [boundary_ratio] + seq
    mono_anchored_viol = [
        ["boundary", D_GRID[0], seq_anchored[0], seq_anchored[1]]]
    mono_anchored_viol += [[D_GRID[i - 1], D_GRID[i],
                            seq_anchored[i], seq_anchored[i + 1]]
                           for i in range(1, len(seq))]
    mono_anchored_viol = [v for v in mono_anchored_viol
                          if v[2] < v[3]]
    boundary_reproduced = not boundary_failures and (
        committed is None or boundary_ratio
        == committed["positive_control"][RATIO])

    clauses = {
        "boundary_arm_reproduces_committed_D19": boundary_reproduced,
        "ratio_monotone_non_increasing_in_d": not mono_viol,
        "ratio_monotone_with_boundary_anchor": not mono_anchored_viol,
        "ratio_crosses_below_1": bool(crossed),
        "d_star": d_star,
        "grid_points_below_1": crossed,
        "monotonicity_violations": mono_viol,
        "monotonicity_violations_with_anchor": mono_anchored_viol,
        "inverted_convention_crosses_below_1": [
            d for d in D_GRID
            if per_d[_d_tag(d)][
                "ratio_substitution_over_recomputation"] < 1.0]}
    falsifier_fired = not crossed

    if instrument_defects:
        terminal = {"verdict": "CANNOT_CHECK",
                    "reason": "; ".join(instrument_defects[:3]),
                    "defects_total": len(instrument_defects)}
    elif falsifier_fired:
        terminal = {
            "verdict": "EPISODIC_NEVER_PAYS",
            "protocol_spelling": "EPISODIC_NEVER_PAYS in "
                                 "ECONOMY_FRONTIER_PROTOCOLS_V1.json",
            "statement":
                "r(d) = a2/a1 never drops below 1 on the frozen-convention "
                "depth grid: recomputation never becomes cheaper than "
                "substitution on these worlds, so the substitution arm "
                "(episodic capital) never loses to recomputation at any "
                "measured depth. NOTE (gloss defect, first-class): the "
                "protocol's falsifier sentence reads this same event as "
                "'episodic capital NEVER pays', which is the inverted-"
                "convention reading; see ratio_convention."}
    else:
        terminal = {
            "verdict": "EPISODIC_DEPTH_FRONTIER_MEASURED",
            "d_star": d_star,
            "statement":
                "r(d) = a2/a1 crosses below 1 at d* = %d on the frozen-"
                "convention grid: beyond d* recomputation is cheaper than "
                "substitution, i.e. the substitution arm's retained "
                "polynomial capital stops paying. Under the inverted "
                "(capital-over-direct) reading the SAME crossing reads as "
                "episodic capital STARTING to pay at d*; see "
                "ratio_convention and protocol_gloss_defect." % d_star}

    if instrument_defects or not boundary_reproduced:
        prediction_verdict = "CANNOT_CHECK"
    elif clauses["ratio_monotone_non_increasing_in_d"] and crossed:
        prediction_verdict = "CONFIRMED"
    elif falsifier_fired:
        prediction_verdict = "REFUTED"
    else:
        prediction_verdict = "PARTIAL"

    out = {
        "experiment": "D31", "study": "episodic_depth_law",
        "protocol": "ECONOMY_FRONTIER_PROTOCOLS_V1.json#D31_episodic_depth_law",
        "protocol_section": "D31_episodic_depth_law",
        "freeze_commit": freeze_commit,
        "machinery": "research/hsg-semantic-execution-v1/exact/d19.py "
                     "IMPORTED UNCHANGED; the recompute-depth dial lives on "
                     "the QUERY FAMILY (new additive world family OW4D, "
                     "prefix D31D, densities mirrored from the frozen OW4 "
                     "generator) exactly as the protocol words it; "
                     "compare_arms runs frozen line for line on every arm",
        "worlds_note": "the boundary arm uses THE frozen D19 worlds exactly "
                       "(ow4_with_blocker_field, seeds untouched, committed "
                       "numbers reproduced); the depth grid d=[1..32] "
                       "cannot exist on 4-7-node worlds, so the dial arms "
                       "use the pre-fixed additive family OW4D(d, wi) under "
                       "the frozen seed discipline (SEED unchanged, new "
                       "prefix D31D, no existing id or key prefix reused), "
                       "mirroring the frozen OW4 generator densities "
                       "(dual-edge prob 0.6, fan-in 1-2, chain+alternative "
                       "supports); family code frozen before the scored run",
        "ratio_convention": {
            "frozen_formula": "r(d) = a2_lifecycle_ops / a1_lifecycle_ops "
                              "= recomputation over substitution; this is "
                              "the formula that yields the committed D19 "
                              "value 640/598 = 1.07 and anchors the "
                              "registered prediction",
            "inverted_reading": "r_inv(d) = a1/a2 = substitution "
                                "(capital) over recomputation (direct), "
                                "the reading the negatives doc and the "
                                "amendment's SOLUTION_EPISODIC payback_law "
                                "give the same 1.07; at the boundary that "
                                "reading evaluates to 598/640 = 0.934 "
                                "(already below 1)",
            "scoring": "registered clauses are scored in the frozen "
                       "value-anchored convention (primary); the inverted "
                       "reading is emitted alongside every table entry "
                       "and its crossing set is reported in clauses"},
        "protocol_gloss_defect": {
            "finding": "the frozen field name "
                       "'substitution_vs_recomputation_op_ratio' carries "
                       "the value a2/a1 = 640/598 = 1.07 (recomputation "
                       "costs 1.07x substitution; committed numbers: a1 "
                       "subst 598 < a2 recompute 640), while "
                       "NEGATIVES_ROOT_CAUSE_V1.md reads it as "
                       "'substitution (cheapest capital there is) costs "
                       "1.07x recomputation' and the amendment's "
                       "SOLUTION_EPISODIC payback_law builds on that "
                       "inverted direction; the registered D31 prediction "
                       "anchor ('1.07 at d=1') and its falsifier prose "
                       "inherit the two opposite conventions",
            "classification": "first-class measured output of D31; scored "
                              "under the value-anchored convention, "
                              "corrected in the annotation, never tuned"},
        "grid": {"d": list(D_GRID)},
        "worlds_per_d": N_WORLDS_PER_D,
        "boundary_arm": {
            "population": "OW4 frozen clean control (8 worlds)",
            "a1_lifecycle_ops": b_tot["a1_ops"],
            "a2_lifecycle_ops": b_tot["a2_ops"],
            RATIO: boundary_ratio,
            "committed_ratio": (committed["positive_control"][RATIO]
                                if committed else None),
            "subsets": b_tot["pairs"],
            "divergences": boundary_failures},
        "depth_dial": per_d,
        "registered_prediction": {
            "text": "ratio is monotone non-increasing in d and crosses 1 "
                    "at finite d* (D19's 1.07 at d=1 is the shallow "
                    "boundary)",
            "clauses": clauses,
            "verdict": prediction_verdict},
        "falsifier": {
            "text": "ratio never drops below 1 with depth -- then episodic "
                    "capital NEVER pays on these worlds and the ceiling "
                    "hardens to a law",
            "fired": falsifier_fired},
        "terminal": terminal,
        "cost_ledger_hdi14": {
            "families": HDI14_LEDGER,
            "ledger_complete": led_ok,
            "missing": led_missing,
            "note": "the frozen D19 op metric IS the charged ledger "
                    "(identical counter semantics both arms); "
                    "retained-state bytes are measured additionally and "
                    "NOT added to the op metric (charging them can only "
                    "increase substitution cost, so measured ratios are "
                    "conservative for recomputation)"},
        "receipt_coverage": {
            "rule": "RECEIPT_COVERAGE_V1.json rule_for_new_studies",
            "emitted_or_cannot_check": [
                "raw terminal", "wall/CPU/GPU/IO/storage",
                "obligation nodes/hyperedges/derivations/SCCs",
                "provenance supports/alternatives",
                "negative/CANNOT_CHECK status", "active k / total N",
                "ambiguity size/entropy (entropy part cannot_check)",
                "operator/library reuse identities"],
            "inapplicable_by_design": RECEIPT_COVERAGE},
        "controls": {
            "boundary_identity_vs_committed": boundary_reproduced,
            "op_auditor": {
                "clean_rows_silent": not any(
                    x.startswith("OP_AUDITOR_FALSE_ALARM")
                    for x in instrument_defects),
                "charge": "a1 = (V+E) + n_subsets * sum_n len(poly); "
                          "a2 = base pass + one pass per subset, each "
                          "pass = all nodes + edges examined up to the "
                          "first supporting edge (early break included, "
                          "empty subset charged twice); recomputed from "
                          "the world alone via the auditor's own N[X] DP "
                          "and charge loops"},
            "truth_auditor": {
                "clean_rows_silent": not any(
                    x.startswith("TRUTH_AUDITOR_FALSE_ALARM")
                    for x in instrument_defects),
                "charge": "root membership under every subset via "
                          "brute-force derivation-tree enumeration, "
                          "compared against BOTH arms"},
            "brute_poly_crosscheck_clean": not any(
                x.startswith("BRUTE_POLY") for x in instrument_defects),
            "hostile_plants": plant_report,
            "shuffle_equal_n_null": {
                "applicable": False,
                "reason": "no random element anywhere in the measured "
                          "comparison: frozen worlds and seeds, "
                          "deterministic arms, revocation subsets "
                          "EXHAUSTED (never sampled), no query stream, "
                          "no draw, no adaptive selection over a sample; "
                          "a draw-invariance control has nothing to "
                          "attach to"}},
        "instrument_defects": instrument_defects,
        "wall_s": round(time.time() - t0w, 4),
        "cpu_s": round(time.process_time() - t0c, 4),
        "host": host_label,
        "python": platform.python_version(),
        "claim_ceiling": "P2 finite certificate over the frozen D19 "
                         "population and the OW4D depth grid; no "
                         "universal claim"}
    return out, receipts


def prediction_line(out):
    rp = out["registered_prediction"]
    c = rp["clauses"]
    return ("%s (boundary=%s, monotone=%s, crossed=%s, d*=%s)") % (
        rp["verdict"], c["boundary_arm_reproduces_committed_D19"],
        c["ratio_monotone_non_increasing_in_d"],
        c["ratio_crosses_below_1"], c["d_star"])


def main():
    freeze_commit = os.environ.get("D31_FREEZE_COMMIT", "UNSET")
    host_label = os.environ.get("D31_HOST_LABEL", platform.node())
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "receipts"), exist_ok=True)
    out, rec = run_d31(freeze_commit, host_label)

    res_path = os.path.join(HERE, "results", "D31_EPISODIC_DEPTH_RESULTS.json")
    rec_path = os.path.join(HERE, "receipts", "D31_receipts.jsonl")
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
        "job": "D31", "host": host_label, "hostname": platform.node(),
        "python": platform.python_version(),
        "system": "; ".join(platform.uname()),
        "freeze_commit": freeze_commit,
        "run_d31_sha256": _sha256_file(os.path.join(HERE, "run_d31.py")),
        "d19_sha256": _sha256_file(os.path.join(HERE, "d19.py")),
        "engine_sha256": _sha256_file(os.path.join(HERE, "engine.py")),
        "worlds_sha256": _sha256_file(os.path.join(HERE, "worlds.py")),
        "worlds_d19d20_sha256": _sha256_file(
            os.path.join(HERE, "worlds_d19d20.py")),
        "committed_d19_results_sha256":
            _sha256_file(os.path.join(HERE, "results", "D19_RESULTS.json")),
        "economy_frontier_protocol_sha256":
            _sha256_file(proto) if os.path.exists(proto) else "ABSENT",
        "query_ecology_amendment_sha256":
            _sha256_file(amend) if os.path.exists(amend) else "ABSENT",
        "results_sha256": _sha256_file(res_path),
        "receipts_sha256": _sha256_file(rec_path),
        "rng_draws": "frozen substreams only (new prefix D31D for the "
                     "dial family); world seeds unchanged"}
    hr_path = os.path.join(HERE, "receipts",
                           "D31_HOST_RECEIPT_%s.json" % host_label)
    with open(hr_path, "w", encoding="utf-8") as f:
        json.dump(host_rec, f, indent=1, sort_keys=True)
        f.write("\n")

    print("D31 terminal:", out["terminal"]["verdict"])
    print("  boundary arm: a1=%d a2=%d ratio=%s (committed %s)"
          % (out["boundary_arm"]["a1_lifecycle_ops"],
             out["boundary_arm"]["a2_lifecycle_ops"],
             out["boundary_arm"][RATIO],
             out["boundary_arm"]["committed_ratio"]))
    print("  depth dial (d: V E subsets  a1  a2  r=a2/a1  r_inv):")
    for d in D_GRID:
        c = out["depth_dial"][_d_tag(d)]
        print("    d=%-3d V=%-4d E=%-4d sub=%-3d a1=%-7d a2=%-7d "
              "r=%-7s r_inv=%-7s wall=%-6s cpu=%s"
              % (d, c["nodes_total"], c["edges_total"], c["subsets_total"],
                 c["a1_lifecycle_ops_total"], c["a2_lifecycle_ops_total"],
                 c[RATIO],
                 c["ratio_substitution_over_recomputation"],
                 c["wall_s"], c["cpu_s"]))
    print("  prediction verdict:", prediction_line(out))
    print("  plants:", json.dumps(
        dict((k, v["flipped"]) for k, v in
             out["controls"]["hostile_plants"].items()), sort_keys=True))
    print("  instrument defects:", len(out["instrument_defects"]))
    print("  wall_s", out["wall_s"], "cpu_s", out["cpu_s"],
          "host", host_label)
    if out["terminal"]["verdict"] == "CANNOT_CHECK":
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
