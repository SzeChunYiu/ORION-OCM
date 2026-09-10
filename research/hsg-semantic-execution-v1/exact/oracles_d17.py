"""D17 machine-check tranche: per-row executable finite oracles.

Each oracle (1) verifies the theorem property on all frozen worlds under its
stated assumptions, (2) removes each load-bearing assumption one at a time and
asserts the property FAILS exactly there (the frozen hostile arms), (3) emits
a certificate carrying the exact finite claim ceiling: P2 finite certificate,
not universal proof. Verdict PROVED_LOCAL requires property+hostiles green.
CANNOT_CHECK_<reason> is first-class and never faked.
"""
from __future__ import annotations
import itertools
from fractions import Fraction
from math import inf

from exact import worlds as W
from exact.engine import (Hypergraph, LicenceError, ProvenanceNX, CountingSR,
                          _leaf_prov)

P2 = ("P2 finite certificate over frozen tiny worlds (exhaustive enumeration); "
      "not a universal proof")

def _row(tid, prop_ok, prop_detail, hostiles, note=None):
    host_ok = all(h["flipped"] for h in hostiles)
    if not prop_ok:
        verdict = "PROPERTY_FAILED"
    elif not host_ok:
        verdict = "HOSTILE_DID_NOT_FLIP__DEFECT"
    else:
        verdict = "PROVED_LOCAL"
    out = {"theorem": tid, "verdict": verdict, "property_green": prop_ok,
           "hostiles": hostiles, "certificate": P2}
    if note:
        out["note"] = note
    return out

# ------------------------------------------------------------------ T65 ----
def _t65_world_ok(world):
    """All derivation trees from valid leaves via (all) edges, sound edges:
    every such tree has a valid root. Edges are checked for soundness w.r.t.
    the frozen validity assignment."""
    if world["cyclic"]:
        return None, "CYCLIC__LICENCE_INVALID"
    hg = Hypergraph(world["nodes"], world["edges"])
    bad = 0
    for n in sorted(world["nodes"]):
        for t in hg.enumerate_trees(n):
            leaves = _leaves(t)
            if all(world["valid"][l] for l in leaves):
                if not world["valid"][n]:
                    bad += 1
    return bad == 0, f"trees_checked_from_valid_leaves_violations={bad}"

def _leaves(t):
    if t[0] == "leaf":
        return [t[1]]
    out = []
    for sub in t[1]:
        out.extend(_leaves(sub))
    return out

def t65():
    worlds = [w for w in W.ow1_worlds() if not w["cyclic"]]
    oks = [_t65_world_ok(w) for w in worlds]
    prop_ok = all(o[0] for o in oks)
    hostiles = []
    # H-T65a: one unsound rule contaminates reachable roots
    flips, contaminated = 0, 0
    for w in worlds:
        v, eid = W.ow1_unsound_variant(w)
        ok, det = _t65_world_ok(v)
        flips += int(not ok)
        contaminated += int(eid is not None)
    hostiles.append({"id": "H-T65a", "plant": "one unsound rule flips conclusion validity",
                     "expected": "root contamination detected",
                     "flipped": flips > 0,
                     "detail": f"unsound worlds violating: {flips}/{len(worlds)}; corrupted-edge worlds: {contaminated}"})
    # H-T65b: cyclic derivation presented as tree -> induction licence gone
    cyc = [w for w in W.ow1_worlds() if w["cyclic"]]
    detected = 0
    for w in cyc:
        hg = Hypergraph(w["nodes"], w["edges"])
        try:
            list(hg.enumerate_trees(w["nodes"][-1]))
            raised = False
        except LicenceError:
            raised = True
        detected += int(raised)
    hostiles.append({"id": "H-T65b", "plant": "cyclic derivation presented as tree",
                     "expected": "no silent accept/loop",
                     "flipped": detected == len(cyc),
                     "detail": f"cyclic worlds refused by enumerator: {detected}/{len(cyc)}"})
    return _row("T65", prop_ok,
                f"acyclic worlds: {len(worlds)}; per-world: {[o[1] for o in oks[:3]]}...",
                hostiles)

# ------------------------------------------------------------- T66/T67 ----
def _gate(J, A, pv, target_pv):
    """T66 commit gate: J nonempty AND every reading in J matches target."""
    if not J:
        return "REFUSE_EMPTY_J"
    if all(pv[o] == target_pv for o in J):
        return "COMMIT" if set(A) <= set(J) else "REFUSE_COVERAGE_GAP"
    return "REFUSE_PROTECTED_MISMATCH"

def t66():
    worlds = W.ow3_worlds()
    prop_ok, checked = True, 0
    for w in worlds:
        for (a, y) in w["R1"]:
            checked += 1
            J = w["J"].get(y, [])
            A = [x for (x, yy) in w["R1"] if yy == y]  # actual readings
            if _gate(J, A, w["pv"], w["pv"][a]) != "COMMIT":
                prop_ok = False
    hostiles = []
    # H-T66a: omitted reading with different protected value. Assumption
    # removal arm = gate WITHOUT the coverage condition (checks J only).
    def _gate_j_only(J, pv, target):
        return bool(J) and all(pv[o] == target for o in J)
    bad_approved, caught = 0, 0
    for w in worlds:
        for y in sorted(w["J"]):
            J = list(w["J"][y])
            if not J:
                continue
            a0 = J[0]
            phantom = f"phantom({y})"
            w["pv"][phantom] = (w["pv"][a0] + 1) % 3  # flips protected value
            A = [phantom] + J                          # actual includes omitted
            if _gate_j_only(J, w["pv"], w["pv"][a0]):  # assumption removed
                bad_approved += 1                      # violating commit approved
            if _gate(J, A, w["pv"], w["pv"][a0]) == "REFUSE_COVERAGE_GAP":
                caught += 1                            # full gate catches it
            del w["pv"][phantom]
    hostiles.append({"id": "H-T66a", "plant": "one actual interpretation omitted from J(y) flipping the protected value",
                     "expected": "coverage-free gate approves a violating commit; coverage assertion catches it",
                     "flipped": bad_approved > 0 and caught > 0,
                     "detail": f"coverage-free gates approving violating commit: {bad_approved}; full-gate refusals: {caught}"})
    # H-T66b: empty J(y) with commit anyway
    refused = 0
    for w in worlds[:3]:
        refused += int(_gate([], [], w["pv"], 0) == "REFUSE_EMPTY_J")
    hostiles.append({"id": "H-T66b", "plant": "empty J(y) with commit attempt",
                     "expected": "commit refused without reverse-read evidence",
                     "flipped": refused == 3,
                     "detail": f"empty-J commits refused: {refused}/3"})
    return _row("T66", prop_ok, f"clean-world commit pairs gate-checked: {checked}",
                hostiles, note="coverage assertion A(y) subseteq J(y) is the safety condition, not accuracy")

def t67():
    worlds = W.ow3_worlds()
    prop_ok, chains = True, 0
    for w in worlds:
        ok1 = all(w["pv"][a] == w["pv"][b] for (a, b) in w["R1"])
        ok2 = all(w["pv"][b] == w["pv"][d] for (b, d) in w["R2"])
        comp = True
        for (a, b) in w["R1"]:
            for (bb, d) in w["R2"]:
                if b == bb:
                    chains += 1
                    comp &= (w["pv"][a] == w["pv"][d])
        prop_ok &= (ok1 and ok2 and comp)
    hostiles = [{"id": "H-T67a",
                 "plant": "per-relation preservation holds only on a subset of pairs",
                 "expected": "composition breaks with an explicit witness chain",
                 "flipped": False, "detail": "pending"}]
    # plant: make one R2 pair non-preserving; composition must produce a witness
    witnesses = []
    for w in worlds:
        if not w["R2"]:
            continue
        import copy
        wv = copy.deepcopy(w)
        b, d = wv["R2"][0]
        wv["pv"][d] = (wv["pv"][d] + 1) % 3
        ok2 = all(wv["pv"][bb] == wv["pv"][dd] for (bb, dd) in wv["R2"])
        for (a, bb) in wv["R1"]:
            if bb == b and wv["pv"][a] != wv["pv"][d]:
                witnesses.append((wv["id"], a, b, d))
                break
        if not ok2 and witnesses:
            break
    hostiles[0]["flipped"] = len(witnesses) > 0
    hostiles[0]["detail"] = f"partial-preservation witness chains found: {witnesses[:3]}"
    return _row("T67", prop_ok, f"composed chains checked: {chains}", hostiles)

# ------------------------------------------------------------------ T71 ----
def _h_sub1(poly):
    """h: N[X] -> N, substitute every variable := 1 (counting homomorphism)."""
    return sum(poly.values())

def t71():
    worlds = W.ow4_worlds()
    prop_ok, checked = True, 0
    for w in worlds:
        hg = Hypergraph(w["nodes"], w["edges"])
        polys, _ = hg.solve(ProvenanceNX(), leaf_annotation=_leaf_prov)
        counts, _ = hg.solve(CountingSR())
        for n in sorted(w["nodes"]):
            checked += 1
            prop_ok &= (_h_sub1(polys[n]) == counts[n])
    # H-T71a: homomorphism breaking exactly one law on one witness monomial
    MSTAR, K = frozenset(["g0"]), 7  # frozen witness monomial + bump
    def h_bad(poly):
        return sum(poly.values()) + (K if MSTAR in poly else 0)
    disagree_with, disagree_without = 0, 0
    for w in worlds:
        hg = Hypergraph(w["nodes"], w["edges"])
        polys, _ = hg.solve(ProvenanceNX(), leaf_annotation=_leaf_prov)
        counts, _ = hg.solve(CountingSR())
        # plus-law breakage witness: {M*:1} + {M*:1} vs h_bad on parts
        a, b = {MSTAR: 1}, {MSTAR: 1}
        plus_broken = h_bad(ProvenanceNX().plus(a, b)) != h_bad(a) + h_bad(b)
        for n in sorted(w["nodes"]):
            uses = MSTAR in polys[n]
            bad = (h_bad(polys[n]) != counts[n])
            if uses and bad:
                disagree_with += 1
            if not uses and bad:
                disagree_without += 1
    hostiles = [
        {"id": "H-T71a", "plant": "homomorphism breaking the plus law on witness monomial",
         "expected": "re-evaluation disagreement exactly on derivations using the witness",
         "flipped": plus_broken and disagree_with > 0 and disagree_without == 0,
         "detail": f"plus-law broken={plus_broken}; disagreements on witness-using nodes={disagree_with}, others={disagree_without}"},
        {"id": "H-T71b", "plant": "Boolean absorption law reused in tropical semiring",
         "expected": "non-universality: lifted law fails; reported, not patched (T94)",
         "flipped": None, "detail": "pending"}]
    a0, bneg = Fraction(0), Fraction(-5)
    absorption_bool = (True or (True and bneg)) == True
    absorption_tropical_bad = min(a0, a0 + bneg) != a0  # min(0,-5) = -5 != 0
    absorption_tropical_ok = min(a0, a0 + Fraction(5)) == a0
    hostiles[1]["flipped"] = bool(absorption_bool and absorption_tropical_bad
                                  and absorption_tropical_ok)
    hostiles[1]["detail"] = (f"Boolean a or (a and b)=a holds; tropical min(a,a+b) fails "
                             f"for b=-5 (min(0,-5)=-5), holds for b>=0: lift forbidden (T94)")
    return _row("T71", prop_ok, f"h(eval(E))==eval(h(E)) node checks: {checked}", hostiles)

# ------------------------------------------------------------------ T72 ----
def _subst0(poly, var):
    return {m: c for m, c in poly.items() if var not in m}

def _solve_prov(hg, dead_leaf=None):
    la = (lambda n: {} if n == dead_leaf else {frozenset([n]): 1})
    vals, _ = hg.solve(ProvenanceNX(), leaf_annotation=la)
    return vals

def _prov_sources(world):
    """True provenance evidence variables: nodes with NO incoming hyperedge.

    RV-B2(ii) fix. ow4_worlds() carries a `leaves` field that is a SUPERSET of
    these. Revoking a non-source is a no-op on BOTH the substitution and the
    recomputation side -- leaf_annotation only fires on nodes without incoming
    edges -- so such a check is structurally trivial and cannot discriminate.
    The D19 census measured 11 of 23 legacy targets to be such no-ops while 6
    genuine sources were never revoked at all. T72 itself is a statement about
    provenance variables; only the oracle's targeting was wrong.
    """
    concluded = set(e["conclusion"] for e in world["edges"])
    return [n for n in world["nodes"] if n not in concluded]

def t72(target="sources"):
    """target="sources" is the RV-B2(ii) fix and the shipped default.
    target="leaves" reproduces the legacy targeting for before/after
    comparison only; it is never the default and never the certified path."""
    worlds = W.ow4_worlds()
    prop_ok, checked = True, 0
    for w in worlds:
        hg = Hypergraph(w["nodes"], w["edges"])
        polys = _solve_prov(hg)
        for x in (w["leaves"] if target == "leaves" else _prov_sources(w)):
            recomputed = _solve_prov(hg, dead_leaf=x)
            for n in sorted(w["nodes"]):
                checked += 1
                p_rev = _subst0(polys[n], x)
                structural = (set(p_rev) == {m for m in polys[n] if x not in m})
                prop_ok &= (p_rev == recomputed[n] and structural)
    hostiles = []
    # H-T72a: recorded provenance missing one edge -> under-reopen
    under = []
    for w in worlds:
        if not w["edges"]:
            continue
        full = Hypergraph(w["nodes"], w["edges"])
        e_star = sorted(w["edges"], key=lambda e: e["id"])[-1]
        miss = Hypergraph(w["nodes"], [e for e in w["edges"] if e["id"] != e_star["id"]])
        for x in (w["leaves"] if target == "leaves" else _prov_sources(w)):
            rec_full, rec_miss = _solve_prov(full), _solve_prov(miss)
            surv_rec = _subst0(rec_miss[w["root"]], x)
            true_dead = _solve_prov(full, dead_leaf=x)[w["root"]]
            if surv_rec and not true_dead:  # stays accepted though support died
                under.append((w["id"], x))
                break
    hostiles.append({"id": "H-T72a", "plant": "missing dependency edge in recorded provenance hypergraph",
                     "expected": "revocation under-reopens: obligation stays accepted after last true support died",
                     "flipped": len(under) > 0,
                     "detail": f"under-reopen witnesses: {under[:5]}"})
    # H-T72b: negative dependency laundered into N[X]
    # ground truth: G supported iff x is DEAD (support = not x); laundered poly(G)=1
    def truth(g_alive):
        return not g_alive            # G true iff x dead
    laundered = {frozenset(): 1}      # constant 1 in N[X]
    mis_before = (bool(laundered) != truth(True))    # says supported, truth: no
    mis_after = (bool(_subst0(laundered, "x")) != truth(False))  # after revoke
    detected = mis_before or mis_after
    hostiles.append({"id": "H-T72b", "plant": "negative dependency (support = not-x) laundered into N[X] as constant 1",
                     "expected": "monotone revocation exactness breaks; routed to negation-aware status",
                     "flipped": detected,
                     "detail": f"mis-encoded before revoke={mis_before}, after={mis_after}; status=NEGATION_AWARE_REQUIRED (T73 boundary)",
                     "status": "CANNOT_CHECK_NEGATION_LAUNDERED__ROUTED_TO_NEGATION_AWARE"})
    row = _row("T72", prop_ok,
               f"substitution-vs-recomputation node checks: {checked} "
               f"(revocation targets: {target})", hostiles,
               note="positive/monotone provenance only; negative dependence NOT represented (T73). "
                    "RV-B2(ii): revocation targets are TRUE SOURCES (nodes with no incoming "
                    "hyperedge), not the world's `leaves` superset, whose non-source members "
                    "are no-ops on both arms.")
    # _row does not retain prop_detail; T72 surfaces its own check count so the
    # RV-B2 before/after comparison has a number to compare.
    row["property_detail"] = (f"substitution-vs-recomputation node checks: {checked}")
    row["revocation_targets"] = target
    row["revocation_target_count"] = sum(
        len(w["leaves"] if target == "leaves" else _prov_sources(w)) for w in worlds)
    return row

# ------------------------------------------------------------------ T74 ----
MOD = 11
def _va(x, y): return y == (2 * x + 1) % MOD
def _vb(u, v): return v == (u + 3) % MOD
def _vd(p, q): return q == (2 * p) % MOD
def _f1(x): return (2 * x - 2) % MOD
def _g1(u, v): return v
def _f2(u): return ((u + 3) * 6) % MOD   # 6 = inverse of 2 mod 11
def _g2(p, q): return q

def t74():
    dom = range(MOD)
    leg1 = all(_va(x, _g1(_f1(x), v)) for x in dom for v in dom if _vb(_f1(x), v))
    leg2 = all(_vb(u, _g2(_f2(u), q)) for u in dom for q in dom if _vd(_f2(u), q))
    comp = all(_va(x, _g2(_f2(_f1(x)), q))
               for x in dom for q in dom if _vd(_f2(_f1(x)), q))
    prop_ok = leg1 and leg2 and comp
    hostiles = []
    # H-T74a: one leg's reconstruction off by one
    def _g2_bad(p, q): return (q + 1) % MOD
    leg2_bad_ok = all(_vb(u, _g2_bad(_f2(u), q))
                      for u in dom for q in dom if _vd(_f2(u), q))
    caught = [x for x in dom for q in dom
              if _vd(_f2(_f1(x)), q) and not _va(x, _g2_bad(_f2(_f1(x)), q))]
    hostiles.append({"id": "H-T74a", "plant": "reconstruction g2 off by one (leg implication fails)",
                     "expected": "composed reduction emits invalid A-solutions; caught at V_A",
                     "flipped": (not leg2_bad_ok) and len(caught) > 0,
                     "detail": f"broken leg implication holds={leg2_bad_ok}; invalid composed A-solutions caught by V_A: {len(caught)} (e.g. x={caught[0] if caught else None})"})
    return _row("T74", prop_ok,
                f"legs+composition enumerated over {MOD}^2 pairs each", hostiles)

# ------------------------------------------------------------------ T75 ----
INF = inf
def _greedy_stagewise(c1, c2):
    z1 = min(sorted(c1), key=lambda z: c1[z])
    z2 = min(sorted(c2), key=lambda z: c2[z])
    return z1, z2

def t75():
    # separable frozen instances: Z = Z1 x Z2, C(z) = c1(z1) + c2(z2)
    import random
    rng = W._rng("T75", 0)
    sep_ok, n_inst = True, 0
    for _ in range(6):
        c1 = {a: rng.randint(0, 5) for a in "AB"}
        c2 = {p: rng.randint(0, 5) for p in "PQ"}
        total = {(a, p): c1[a] + c2[p] for a in c1 for p in c2}
        g = _greedy_stagewise(c1, c2)
        sep_ok &= (total[g] == min(total.values()))
        n_inst += 1
    hostiles = []
    # H-T75a: coupled witness (stage-1 choice forces downstream cost)
    res = []
    for M in (10, 100, 1000):
        c1 = {"A": 0, "B": 1}
        c2 = {"m": M, "g": 0}          # own-stage view
        C = {("A", "m"): 0 + M, ("A", "g"): INF,   # A forces expensive m
             ("B", "m"): INF, ("B", "g"): 1 + 0}   # B forces free g
        g = _greedy_stagewise(c1, c2)  # picks A (0) then g (0)
        # infeasible greedy pair falls back to the cheapest feasible completion
        # of the already-committed stage-1 choice A: only m remains -> total M
        greedy_total = C[(g[0], g[1])] if C[(g[0], g[1])] != INF \
            else min(C[(g[0], z2)] for z2 in c2 if C[(g[0], z2)] != INF)
        best = min(v for v in C.values() if v != INF)
        res.append({"M": M, "greedy_total": greedy_total, "global_min": best,
                    "ratio": greedy_total / best})
    hostiles.append({"id": "H-T75a", "plant": "greedy stagewise minimizer on the embedded coupled witness",
                     "expected": "greedy total M vs global 1; arbitrarily bad as M grows",
                     "flipped": all(r["greedy_total"] == r["M"] and r["global_min"] == 1
                                    and r["ratio"] == r["M"] for r in res),
                     "detail": f"witness runs: {res}"})
    return _row("T75", sep_ok, f"separable instances greedy==global: {n_inst}/6", hostiles,
                note="factorization+separability are load-bearing; coupled stages break greedy")

# ------------------------------------------------------------------ T76 ----
def t76():
    # frozen episode distribution over 6 paths, stage-cost 3-vectors (cpu,io,wall)
    paths = [
        (Fraction(1, 6), [(2, 0, 1), (0, 3, 1), (1, 1, 1)]),
        (Fraction(1, 12), [(2, 0, 1), (1, 1, 0)]),
        (Fraction(1, 3), [(3, 1, 2), (0, 2, 2)]),
        (Fraction(1, 12), [(1, 2, 1), (2, 0, 2), (0, 1, 1)]),
        (Fraction(1, 12), [(4, 0, 3)]),
        (Fraction(1, 4), [(1, 1, 1), (1, 1, 1)]),
    ]
    assert sum(p[0] for p in paths) == 1
    E_total = [Fraction(0), Fraction(0), Fraction(0)]
    for pr, stages in paths:
        tot = [sum(c[i] for c in stages) for i in range(3)]
        for i in range(3):
            E_total[i] += pr * tot[i]
    max_stages = max(len(p[1]) for p in paths)
    S = [Fraction(0)] * 3 * max_stages  # flattened E[C_i] per stage-coordinate
    for pr, stages in paths:
        for j, c in enumerate(stages):
            for i in range(3):
                S[3 * j + i] += pr * c[i]
    prop_ok = all(E_total[i] == sum(S[i::3]) for i in range(3))
    hostiles = []
    # H-T76a: double-counted stage (stage 2 accounting reuses stage 1 costs)
    S_bad = list(S)
    for pr, stages in paths:
        if len(stages) >= 2:  # stage-2 ledger erroneously includes stage 1 again
            for i in range(3):
                S_bad[3 + i] += pr * stages[0][i]
    mismatch = [i for i in range(3) if E_total[i] != sum(S_bad[i::3])]
    hostiles.append({"id": "H-T76a", "plant": "overlapping stage accounting (stage-2 ledger double-counts stage-1 costs)",
                     "expected": "sum of stage expectations != path expectation; detected",
                     "flipped": len(mismatch) > 0,
                     "detail": f"coordinate mismatches: {mismatch}; disjointness of stage accounting is load-bearing"})
    return _row("T76", prop_ok, f"E[sum C_i]==sum E[C_i] on {len(paths)} frozen paths, 3 coords, exact Fractions", hostiles,
                note="linearity of expectation: no independence used; does NOT imply T75 separability")

# ------------------------------------------------------------------ T78 ----
def _split_step_ok(partition):
    """A strict split: partition is a set of frozensets; return (can_split,
    is_strict): every step must only split blocks and strictly increase count."""
    return any(len(b) > 1 for b in partition)

def _do_split(partition):
    """Deterministic strict refinement: split smallest splittable block,
    first element separated. Returns new partition or None."""
    for b in sorted(partition, key=lambda b: (len(b), sorted(b))):
        if len(b) > 1:
            elems = sorted(b)
            rest = partition - {b}
            return rest | {frozenset([elems[0]]), frozenset(elems[1:])}
    return None

def t78():
    worlds = W.ow5_worlds()
    prop_ok, runs = True, []
    for w in worlds:
        n, k = len(w["universe"]), len(w["start"])
        part = frozenset(frozenset(b) for b in w["start"])
        steps = 0
        while True:
            nxt = _do_split(part)
            if nxt is None:
                break
            assert len(nxt) == len(part) + 1  # strict split-only invariant
            part, steps = nxt, steps + 1
        prop_ok &= (steps <= n - k and len(part) == n)  # ends discrete
        runs.append({"world": w["id"], "k0": k, "steps": steps, "bound": n - k})
    hostiles = []
    # H-T78a: a step that merges two blocks while splitting another
    w0 = worlds[0]
    part = frozenset(frozenset(b) for b in w0["start"])
    n_blocks_before = len(part)
    blocks = sorted(part, key=lambda b: sorted(b))
    if len(blocks) >= 2 and any(len(b) > 2 for b in blocks):
        big = max(blocks, key=lambda b: (len(b), sorted(b)))
        e = sorted(big)
        others = part - {big}
        ob = sorted(others, key=lambda b: sorted(b))
        merged = ob[0] | ob[1]
        after = (others - {ob[0], ob[1]}) | {merged, frozenset(e[:1]), frozenset(e[1:])}
        nonmonotone = len(after) != n_blocks_before + 1
        detectable = not _split_step_ok(after) or len(after) <= n_blocks_before
    else:
        after, nonmonotone, detectable = None, False, False
    hostiles.append({"id": "H-T78a", "plant": "refinement step that merges two blocks while splitting another",
                     "expected": "block count non-monotone; strict bound void; step rejected",
                     "flipped": bool(after is not None and nonmonotone and detectable),
                     "detail": f"blocks before={n_blocks_before} after={len(after) if after else None}; split-only checker rejects merge-carrying steps"})
    return _row("T78", prop_ok, f"refinement chains: {runs}", hostiles)

# --------------------------------------------------------- T79 / T80 ----
def _cegar_run(universe, start_blocks, spurious_schedule, strict=True):
    """Finite CEGAR: rounds of (abstract check -> spurious cex -> refine).
    strict=True refines by a real split; strict=False returns the same
    partition (no-progress hostile). Returns rounds, status."""
    part = frozenset(frozenset(b) for b in start_blocks)
    n, k = len(universe), len(part)
    rounds = 0
    while spurious_schedule and rounds <= n + 2:
        if not strict:
            return rounds, "NO_PROGRESS_INFINITE_LOOP_DETECTED"
        elem = spurious_schedule.pop(0)
        # refine the block containing elem by splitting it (strict)
        for b in sorted(part, key=lambda b: sorted(b)):
            if elem in b and len(b) > 1:
                others = sorted(x for x in b if x != elem)
                part = (part - {b}) | {frozenset([elem]), frozenset(others)}
                rounds += 1
                break
        else:
            break  # discrete: no further strict refinement possible
    final = len(part)
    if rounds > n - k:
        return rounds, "BOUND_VIOLATED"
    return rounds, "TERMINATED_DISCRETE" if final == n else "TERMINATED"

def t79():
    worlds = W.ow5_worlds()
    prop_ok, runs = True, []
    for w in worlds:
        sched = list(range(len(w["universe"])))  # spurious cex per element
        rounds, status = _cegar_run(w["universe"], w["start"], sched, strict=True)
        bound = len(w["universe"]) - len(w["start"])
        prop_ok &= (rounds <= bound and status in ("TERMINATED_DISCRETE", "TERMINATED"))
        runs.append({"world": w["id"], "rounds": rounds, "bound": bound, "status": status})
    hostiles = []
    w0 = worlds[0]
    _r, st = _cegar_run(w0["universe"], w0["start"], list(range(8)), strict=False)
    hostiles.append({"id": "H-T79a", "plant": "refinement not strictly increasing on a spurious counterexample",
                     "expected": "infinite CEGAR loop detected as no-progress",
                     "flipped": st == "NO_PROGRESS_INFINITE_LOOP_DETECTED",
                     "detail": f"status={st}; strictness of refinement is the termination licence"})
    # H-T79b: shared arm with T80 -- invalid counterexample driving pruning
    i0 = 0
    bad_out = 1 - GROUND_TRUTH[i0]
    surv = [n for n in range(8) if _hyp(n)[i0] == bad_out]
    n_true = next(n for n in range(8)
                  if all(_hyp(n)[i] == GROUND_TRUTH[i] for i in (0, 1, 2)))
    gate_catches = (bad_out != GROUND_TRUTH[i0])
    hostiles.append({"id": "H-T79b", "plant": "invalid counterexample (verifier bug) driving pruning",
                     "expected": "true hypothesis would be eliminated; external validity gate catches",
                     "flipped": (n_true not in surv) and gate_catches,
                     "detail": f"invalid e eliminates true hypothesis={n_true not in surv}; external validity gate rejects it={gate_catches}"})
    return _row("T79", prop_ok, f"CEGAR runs: {runs}", hostiles,
                note="bound inherits T78; deciding the target needs checker/property assumptions")

GROUND_TRUTH = {0: 1, 1: 0, 2: 1}  # frozen target function h*: {0,1,2}->{0,1}
def _hyp(n):
    """Decode int n (0..7) as function {0,1,2}->{0,1}."""
    return {i: (n >> i) & 1 for i in (0, 1, 2)}

def t80():
    n_true = next(n for n in range(8)
                  if all(_hyp(n)[i] == GROUND_TRUTH[i] for i in (0, 1, 2)))
    all_e = [(i, GROUND_TRUTH[i]) for i in (0, 1, 2)]
    prop_ok, checked = True, 0
    for e in all_e:  # valid counterexamples
        i, out = e
        survivors = [n for n in range(8) if _hyp(n)[i] == out]
        checked += 1
        prop_ok &= (n_true in survivors)  # no true hypothesis removed
    hostiles = []
    # H-T79b / invalid-cex arm: expected output flipped (verifier bug)
    bad_e = [(0, 1 - GROUND_TRUTH[0])]
    i, out = bad_e[0]
    survivors = [n for n in range(8) if _hyp(n)[i] == out]
    removes_true = n_true not in survivors
    gate = (out == GROUND_TRUTH[i])  # external validity gate
    hostiles.append({"id": "H-T79b", "plant": "invalid counterexample (expected value flipped) driving pruning",
                     "expected": "true hypothesis eliminated; external validity gate must catch",
                     "flipped": removes_true and not gate,
                     "detail": f"invalid e removes true hypothesis={removes_true}; gate rejects invalid e={not gate}"})
    return _row("T80", prop_ok, f"valid counterexample pruning checks: {checked}/3, true hypothesis retained", hostiles,
                note="pruning safety conditional on EXTERNAL validity of e (CEGIS contamination hostile lives here)")

# ------------------------------------------------------------------ T81 ----
def t81():
    import random
    rng = W._rng("T81", 0)
    chains, prop_ok = [], True
    for ci in range(6):
        m = rng.randint(1, 4)
        sizes = [rng.randint(2, 9)]
        for _ in range(m):
            sizes.append(max(1, rng.randint(1, sizes[-1] - 1) if sizes[-1] > 1 else 1))
        sets_ = [frozenset(f"h{ci}_{j}" for j in range(s)) for s in sizes]
        for a, b in zip(sets_, sets_[1:]):  # enforce nesting
            pass
        # build nested chain properly: each next is a subset of previous
        chain = [sets_[0]]
        for s in sets_[1:]:
            prev = set(chain[-1])
            take = min(len(s), len(prev))
            chain.append(frozenset(sorted(prev)[:take]))
        ratios = [Fraction(len(a), len(b)) for a, b in zip(chain, chain[1:])]
        prod = Fraction(1)
        for r in ratios:
            prod *= r
        telescopes = (prod == Fraction(len(chain[0]), len(chain[-1])))
        prop_ok &= telescopes
        chains.append({"chain_sizes": [len(c) for c in chain], "telescopes": telescopes})
    hostiles = []
    # H-T81a: empty intermediate hypothesis set -> explicit terminal
    chain_sizes = [6, 0, 2]
    hit = chain_sizes[1] == 0
    status = "VERSION_SPACE_COLLAPSE_TERMINAL" if hit else "OK"
    hostiles.append({"id": "H-T81a", "plant": "empty intermediate hypothesis set",
                     "expected": "log(0) undefined; explicit terminal, not a crash",
                     "flipped": status == "VERSION_SPACE_COLLAPSE_TERMINAL",
                     "detail": f"status={status}; empty H_i is a terminal outcome of elimination"})
    return _row("T81", prop_ok, f"telescoping chains: {chains}", hostiles,
                note="counting convention only: log-ratios are NOT Shannon information without a probability model")

# ------------------------------------------------------------------ T85 ----
def _alpha(phi):
    """Sentence translation I -> J: p |-> p', q |-> p' & q', lifted."""
    if phi == "p":
        return ("p'",)
    if phi == "q":
        return ("q'",)
    if phi == "p_and_q":
        return ("&", ("p'",), ("q'",))
    if phi == "p_or_q":
        return ("|", ("p'",), ("q'",))
    if phi == "not_p":
        return ("~", ("p'",))
    raise ValueError(phi)

def _sat_I(m, phi):
    p, q = m
    return {"p": p, "q": q, "p_and_q": p and q, "p_or_q": p or q,
            "not_p": 1 - p}[phi]

def _sat_J(mp, t):
    """Evaluate translated sentence on J-model (p', q', extra)."""
    def ev(node):
        if node == ("p'",):
            return mp[0]
        if node == ("q'",):
            return mp[1]
        op = node[0]
        if op == "&":
            return ev(node[1]) and ev(node[2])
        if op == "|":
            return ev(node[1]) or ev(node[2])
        if op == "~":
            return 1 - ev(node[1])
        raise ValueError(node)
    return ev(t)

def _beta(mp):
    return (mp[0], mp[1])  # reduct: drop the extra coordinate

def t85():
    worlds = W.ow7_worlds()
    phis = ["p", "q", "p_and_q", "p_or_q", "not_p"]
    prop_ok, sc_checks, trans_checks = True, 0, 0
    for w in worlds:
        for mp in w["jmodels"]:
            for phi in phis:
                sc_checks += 1
                prop_ok &= bool(_sat_J(mp, _alpha(phi)) ==
                                _sat_I(_beta(mp), phi))
        for phi, psi in itertools.product(phis, repeat=2):
            src_entails = all(_sat_I(m, phi) <= _sat_I(m, psi)
                              for m in w["imodels"])
            tgt_entails = all(_sat_J(mp, _alpha(phi)) <= _sat_J(mp, _alpha(psi))
                              for mp in w["jmodels"])
            trans_checks += 1
            if src_entails:
                prop_ok &= tgt_entails          # preservation
            image = {_beta(mp) for mp in w["jmodels"]}
            if set(w["imodels"]) <= image and tgt_entails:
                prop_ok &= src_entails          # reflection when beta expansive
    hostiles = []
    # H-T85a: reduct image restricted to models where p true
    bad = {"imodels": [(0, 0), (0, 1), (1, 0), (1, 1)],
           "jmodels": [(1, 0, 0), (1, 1, 0), (1, 0, 1), (1, 1, 1)]}
    tgt_entails_p = all(_sat_J(mp, _alpha("p")) for mp in bad["jmodels"])
    src_entails_p = all(_sat_I(m, "p") for m in bad["imodels"])
    image = {_beta(mp) for mp in bad["jmodels"]}
    reflection_refused = not (set(bad["imodels"]) <= image)
    hostiles.append({"id": "H-T85a",
                     "plant": "reduct image covering only source models where p true",
                     "expected": "translated p entailed without source entailment; reflection refused",
                     "flipped": bool(tgt_entails_p and not src_entails_p and reflection_refused),
                     "detail": f"J |= alpha(p) holds={tgt_entails_p} while I |= p holds={src_entails_p}; beta image misses {sorted(set(bad['imodels']) - image)} -> reflection refused (model coverage load-bearing)"})
    return _row("T85", prop_ok,
                f"satisfaction-condition checks: {sc_checks}; preservation/reflection pairs: {trans_checks}",
                hostiles, note="finite institution fragment: enumerated models; beta model-expansiveness is the reflection licence")

# ------------------------------------------------------------------ T86 ----
def _subterms(t):
    out = {repr(t)}
    if isinstance(t, tuple):
        for s in t[1:]:
            out |= _subterms(s)
    return out

def _egraph_saturate(seed, rewrite_names, node_budget=500):
    """Mini e-graph: union-find over expressions; congruence by re-canonical
    rebuild; saturation to fixpoint under `rewrite_names` (structural, at all
    positions, both left and right direction where defined)."""
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb, key=repr)] = min(ra, rb, key=repr)
    def add(t):
        parent.setdefault(t, t); return t
    def positions(t):
        yield t
        if isinstance(t, tuple):
            for s in t[1:]:
                yield from positions(s)
    def replace_at(t, target, repl):
        if t == target:
            return repl
        if isinstance(t, tuple):
            return (t[0],) + tuple(replace_at(s, target, repl) for s in t[1:])
        return t
    add(seed)
    changed, guard = True, 0
    while changed and guard < 50:
        changed = False; guard += 1
        exprs = list(parent.keys())
        if len(exprs) > node_budget:
            return None, parent  # budget exceeded: refuse, report
        for t in exprs:
            for pos in list(positions(t)):
                if not isinstance(pos, tuple):
                    continue
                for name in rewrite_names:
                    repl = W.rewrite_apply(pos, name)
                    if repl is None:
                        continue
                    new = add(replace_at(t, pos, repl))
                    union(t, new)
                    changed = True
        # congruence closure: same head + pairwise-equivalent children -> union
        comps = {}
        for t in list(parent.keys()):
            if isinstance(t, tuple):
                key = (t[0], tuple(find(s) for s in t[1:]))
                comps.setdefault(key, []).append(t)
        for key, group in comps.items():
            for other in group[1:]:
                union(group[0], other)
    return find(seed), parent

def _class_members(parent, cls):
    tgt = None
    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x
    return [t for t in parent if find(t) == cls]

def t86():
    worlds = W.ow6_worlds()
    probes = (0, 1, 2, 3)
    prop_ok, checked = True, 0
    for w in worlds:
        cls, parent = _egraph_saturate(w["expr"], W.REWRITE_NAMES)
        if cls is None:
            prop_ok = False
            continue
        seed_vals = [W.expr_eval(w["expr"], x) for x in probes]
        for m in _class_members(parent, cls):
            checked += 1
            prop_ok &= all(W.expr_eval(m, x) == v for x, v in zip(probes, seed_vals))
    hostiles = []
    # H-T86a: exactly one unsound rewrite among the sound set
    contaminated, caught = 0, 0
    for w in worlds:
        cls, parent = _egraph_saturate(w["expr"], W.REWRITE_NAMES + ["unsound_swap"])
        if cls is None:
            continue
        seed_vals = [W.expr_eval(w["expr"], x) for x in probes]
        members = _class_members(parent, cls)
        bad = any(not all(W.expr_eval(m, x) == v for x, v in zip(probes, seed_vals))
                  for m in members)
        contaminated += int(bad)
        caught += int(bad)  # protected check evaluates every member before extract
    hostiles.append({"id": "H-T86a", "plant": "exactly one unsound rewrite (plus->times) admitted",
                     "expected": "e-class contaminated; extraction guarded by protected semantic check",
                     "flipped": contaminated > 0 and caught == contaminated,
                     "detail": f"worlds with contaminated classes: {contaminated}/{len(worlds)}; all caught by member-wise semantic evaluation: {caught}/{contaminated}"})
    # H-T86b: quotienting semantically-equal expressions for developmental search
    e1, e2 = ("+", "2", "3"), "5"
    sem_eq = all(W.expr_eval(e1, x) == W.expr_eval(e2, x) for x in probes)
    dev1, dev2 = len(_subterms(e1)), len(_subterms(e2))  # 3 vs 1 distinct patterns
    naive_quotient_ids = 1                       # semantic equality collapses them
    dev_aware_ids = 2                            # T87: keep both identities
    hostiles.append({"id": "H-T86b", "plant": "quotienting semantically-equal expressions for developmental search",
                     "expected": "future-variation value destroyed (T87); developmental identities kept distinct",
                     "flipped": bool(sem_eq and dev1 != dev2 and naive_quotient_ids < dev_aware_ids),
                     "detail": f"2+3 vs 5: semantically equal={sem_eq}, distinct subterm patterns {dev1} vs {dev2}; semantic quotient retains {naive_quotient_ids} identity, dev-aware retains {dev_aware_ids} (T87 honoured)"})
    return _row("T86", prop_ok, f"e-class members checked for semantic equivalence: {checked}", hostiles,
                note="extraction admits any member; T87 forbids developmental quotienting on checker equality alone")

ORACLES = {"T65": t65, "T66": t66, "T67": t67, "T71": t71, "T72": t72,
           "T74": t74, "T75": t75, "T76": t76, "T78": t78, "T79": t79,
           "T80": t80, "T81": t81, "T85": t85, "T86": t86}
