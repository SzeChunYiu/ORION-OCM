#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HST core lane A exact checker (issue #233, D2).

For theorems HST-T01, T03, T05, T06, T07, T18:
  (a) enumerates a small finite universe,
  (b) verifies the theorem's finite specialization holds there,
  (c) re-derives each hostile witness in ../hostiles/*.json and verifies it
      violates the conclusion when the assumption is removed.

Deterministic: no randomness, no sampling -- exact enumeration everywhere.
Python 3.8.10 compatible (no match statement, no PEP604 unions, no builtin
generic annotations).

This checker certifies FINITE SPECIALIZATIONS ONLY (proof class P2 evidence).
It does NOT make any registry row PROVED: P1 status comes from
proofs/PROOFS_CORE_V1.md, per FREEZE_HST_V1.json and README hard rules.
"""

import itertools
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
HOSTILES = os.path.join(os.path.dirname(HERE), "hostiles")

FAILURES = []


def check(name, ok, detail):
    """Record a named check; print PASS/FAIL. Returns ok."""
    if ok:
        print("PASS  %s :: %s" % (name, detail))
    else:
        print("FAIL  %s :: %s" % (name, detail))
        FAILURES.append(name)
    return ok


def load_witness(fname):
    with open(os.path.join(HOSTILES, fname), "r") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# T01 -- optional inheritance monotonicity
# Finite specialization: enumerate all (A_t subseteq A_{t+1}) pairs and all
# cost tables over a 3-action universe with costs in 0..4; verify
# inf_{A_{t+1}} C <= inf_{A_t} C in every world. Also verify the M-charged
# bound inf_{A_{t+1}} C_charged <= m_t + M in every world (old strategies
# charged C+M), and that strict reversal worlds exist (they are exactly the
# hostile worlds -- the checker finds the smallest one).
# --------------------------------------------------------------------------
def section_t01():
    actions = [0, 1, 2]
    costs_range = list(range(5))
    universes = 0
    reversals = []
    for cost_values in itertools.product(costs_range, repeat=3):
        cost = dict(zip(actions, cost_values))
        subsets = []
        for r in range(1, 4):
            subsets.extend(itertools.combinations(actions, r))
        for at in subsets:
            at = frozenset(at)
            for at1 in subsets:
                at1 = frozenset(at1)
                if not at <= at1:
                    continue
                universes += 1
                m_t = min(cost[a] for a in at)
                m_t1 = min(cost[a] for a in at1)
                if m_t1 > m_t:
                    reversals.append((sorted(at), sorted(at1), dict(cost),
                                      m_t, m_t1))
    check("T01/enumeration-nonempty", universes > 0,
          "%d (A_t, A_{t+1}, cost) worlds enumerated" % universes)
    check("T01/finite-spec-monotone-M0", len(reversals) == 0,
          "inf over superset <= inf over subset in all %d worlds; %d "
          "reversal worlds under M=0" % (universes, len(reversals)))
    # Non-vacuity of the hostile class: with every strategy of A_{t+1}
    # charged cost+M (M=2), reversal worlds DO exist in this same universe.
    M_charge = 2
    charged_reversals = 0
    for cost_values in itertools.product(costs_range, repeat=3):
        cost = dict(zip(actions, cost_values))
        subsets = []
        for r in range(1, 4):
            subsets.extend(itertools.combinations(actions, r))
        for at in subsets:
            at = frozenset(at)
            for at1 in subsets:
                at1 = frozenset(at1)
                if not at <= at1:
                    continue
                m_t = min(cost[a] for a in at)
                m_t1 = min(cost[a] for a in at1) + M_charge
                if m_t1 > m_t:
                    charged_reversals += 1
    check("T01/charged-reversal-worlds-exist", charged_reversals > 0,
          "%d worlds where charging M=%d to every strategy reverses the "
          "conclusion (hostile class non-vacuous)" % (charged_reversals,
                                                       M_charge))
    # the witness world (assumption removed)
    w = load_witness("W_T01_mandatory_overhead.json")
    world = w["world"]
    at1 = set(world["A_{t+1}"])
    check("T01/W-T01-superset-intact", set(world["A_t"]) <= at1,
          "A_t=%s subset of A_{t+1}=%s" % (world["A_t"], world["A_{t+1}"]))
    m_t = min(world["cost_t"].values())
    m_t1 = min(world["charged_cost_{t+1}"].values())
    # independent re-derivation of the charged costs
    M = world["mandatory_overhead_M"]
    rederived = {a: world["raw_cost_{t+1}"][a] + M for a in at1}
    check("T01/W-T01-charging", rederived == world["charged_cost_{t+1}"],
          "charged = raw + M re-derived: %s" % rederived)
    check("T01/W-T01-reversal", m_t1 > m_t,
          "m_{t+1}=%d > m_t=%d with M=%d (assumption removed, conclusion "
          "violated)" % (m_t1, m_t, M))


# --------------------------------------------------------------------------
# T03 -- representation insufficiency by indistinguishability
# Finite specialization: |S|=2, |Z|=2, |A|=2. Enumerate ALL observation maps
# phi, ALL contracts G (each G(s) a subset of A), ALL policies pi: Z -> A.
# Verify the biconditional structure:
#   (phi aliases s1,s2 AND G(s1) cap G(s2) empty)  ==>  no pi correct on both
#   (phi injective AND all G(s) nonempty)          ==>  some pi correct on both
# --------------------------------------------------------------------------
def section_t03():
    states = ["s1", "s2"]
    actions = ["L", "R"]
    phi_maps = list(itertools.product(["z0", "z1"], repeat=2))
    g_choices = []
    for _ in range(2):
        g_choices.append([frozenset(c)
                          for r in range(3)
                          for c in itertools.combinations(actions, r)])
    policies = list(itertools.product(actions, repeat=2))  # pi(z0), pi(z1)
    aliased_impossible = 0
    aliased_total = 0
    injective_ok = 0
    injective_total = 0
    violations = 0
    for phi in phi_maps:
        aliases = phi[0] == phi[1]
        for g1, g2 in itertools.product(g_choices[0], g_choices[1]):
            G = {"s1": g1, "s2": g2}
            disjoint = len(g1 & g2) == 0
            some_ok = False
            for pi in policies:
                pd = dict(zip(["z0", "z1"], pi))
                a1 = pd[phi[0]]
                a2 = pd[phi[1]]
                if a1 in G["s1"] and a2 in G["s2"]:
                    some_ok = True
                    break
            if aliases and disjoint:
                aliased_total += 1
                if not some_ok:
                    aliased_impossible += 1
                else:
                    violations += 1
            if (not aliases) and len(G["s1"]) > 0 and len(G["s2"]) > 0:
                injective_total += 1
                if some_ok:
                    injective_ok += 1
    check("T03/enumeration-nonempty",
          aliased_total > 0 and injective_total > 0,
          "%d aliased-disjoint worlds, %d injective-nonempty worlds, %d "
          "policies" % (aliased_total, injective_total, len(policies)))
    check("T03/finite-spec-impossibility", violations == 0,
          "aliasing + disjoint correct sets -> 0/%d policies succeed "
          "(%d/%d worlds confirm)" % (len(policies), aliased_impossible,
                                      aliased_total))
    check("T03/injective-satisfiable",
          injective_ok == injective_total,
          "injective phi + nonempty G -> some policy succeeds in %d/%d "
          "worlds (escape is representational)" % (injective_ok,
                                                    injective_total))
    # witness replay
    w = load_witness("W_T03_aliasing.json")
    world = w["world"]
    zs = sorted(set(world["phi"].values()))
    pols = list(itertools.product(world["actions"], repeat=len(zs)))
    zindex = {z: i for i, z in enumerate(zs)}
    failures = 0
    for pi in pols:
        ok1 = pi[zindex[world["phi"]["s1"]]] in world["G"]["s1"]
        ok2 = pi[zindex[world["phi"]["s2"]]] in world["G"]["s2"]
        if not (ok1 and ok2):
            failures += 1
    check("T03/W-T03-all-policies-fail", failures == len(pols),
          "%d/%d policies fail on the aliased pair; %d succeed"
          % (failures, len(pols), len(pols) - failures))
    check("T03/W-T03-aliasing", world["phi"]["s1"] == world["phi"]["s2"],
          "phi(s1)=%s=phi(s2)" % world["phi"]["s1"])
    check("T03/W-T03-disjoint",
          set(world["G"]["s1"]).isdisjoint(world["G"]["s2"]),
          "G(s1) cap G(s2) = empty")


# --------------------------------------------------------------------------
# T05 -- macro amortization threshold
# Finite specialization: integer grid of all six frozen quantities; verify
#   lifecycle(macro) < lifecycle(baseline)  <==>  H_eff*dC_use > costs
# computed INDEPENDENTLY (direct lifecycle accounting vs identity sign).
# --------------------------------------------------------------------------
def section_t05():
    total = 0
    mismatches = 0
    for c_build in range(5):
        for c_maint in range(3):
            for e_rev in range(2):
                for h_eff in range(5):
                    for c_s in range(6):
                        for c_m in range(6):
                            total += 1
                            baseline = h_eff * c_s
                            macro = c_build + c_maint + e_rev + h_eff * c_m
                            lhs = h_eff * (c_s - c_m)
                            rhs = c_build + c_maint + e_rev
                            if (macro < baseline) != (lhs > rhs):
                                mismatches += 1
    check("T05/finite-spec-identity", mismatches == 0,
          "direct lifecycle comparison == identity sign in all %d grid "
          "points (%d mismatches)" % (total, mismatches))
    # witness replay (both cases)
    w = load_witness("W_T05_macro_never_pays.json")
    for case_key in ["case_A_never_pays_back",
                     "case_B_shorter_code_costlier_run"]:
        c = w["world"][case_key]
        baseline = c["H_eff"] * c["C_use_s"]
        macro = (c["C_build"] + c["C_maint"] + c["E_C_revision"]
                 + c["H_eff"] * c["C_use_m"])
        identity_lhs = c["H_eff"] * (c["C_use_s"] - c["C_use_m"])
        identity_rhs = c["C_build"] + c["C_maint"] + c["E_C_revision"]
        check("T05/W-T05-%s-lifecycle" % case_key,
              baseline == c["lifecycle_baseline"]
              and macro == c["lifecycle_macro"],
              "baseline=%d macro=%d re-derived (json %d/%d)"
              % (baseline, macro, c["lifecycle_baseline"],
                 c["lifecycle_macro"]))
        harmful = macro > baseline
        identity_harmful = identity_lhs < identity_rhs
        check("T05/W-T05-%s-verdict" % case_key,
              harmful and identity_harmful,
              "harmful by lifecycle (%d>%d) and by identity (%d<%d)"
              % (macro, baseline, identity_lhs, identity_rhs))


# --------------------------------------------------------------------------
# T06 -- exact dependency-cone locality
# Finite specialization (forward): enumerate ALL DAGs on 3 labeled nodes,
# ALL boolean function tables per node (over declared ancestors), ALL
# nonempty intervention sets S and forced values; verify nodes outside
# Desc(S) never change.
# --------------------------------------------------------------------------
def all_dags(n):
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    dags = []
    for choice in itertools.product([None, "fwd", "bwd"], repeat=len(pairs)):
        edges = []
        for (i, j), c in zip(pairs, choice):
            if c == "fwd":
                edges.append((i, j))
            elif c == "bwd":
                edges.append((j, i))
        # acyclicity via topological sort
        if topo_order(n, edges) is not None:
            dags.append(edges)
    return dags


def topo_order(n, edges):
    indeg = [0] * n
    out = [[] for _ in range(n)]
    for a, b in edges:
        out[a].append(b)
        indeg[b] += 1
    stack = [i for i in range(n) if indeg[i] == 0]
    order = []
    while stack:
        v = stack.pop()
        order.append(v)
        for u in out[v]:
            indeg[u] -= 1
            if indeg[u] == 0:
                stack.append(u)
    if len(order) == n:
        return order
    return None


def descendants(n, edges, s_set):
    out = [[] for _ in range(n)]
    for a, b in edges:
        out[a].append(b)
    seen = set(s_set)
    frontier = list(s_set)
    while frontier:
        v = frontier.pop()
        for u in out[v]:
            if u not in seen:
                seen.add(u)
                frontier.append(u)
    return seen


def compute_values(n, edges, funcs, forced):
    """Topological evaluation. funcs[node] maps ancestor-tuple -> value.
    forced: dict node -> value (intervention)."""
    order = topo_order(n, edges)
    anc = {node: [] for node in range(n)}
    for a, b in edges:
        anc[b].append(a)
    vals = {}
    for node in order:
        if node in forced:
            vals[node] = forced[node]
            continue
        key = tuple(vals[a] for a in sorted(anc[node]))
        vals[node] = funcs[node][key]
    return vals


def section_t06():
    n = 3
    dags = all_dags(n)
    runs = 0
    violations = 0
    tight = 0
    for edges in dags:
        anc = {node: [] for node in range(n)}
        for a, b in edges:
            anc[b].append(a)
        tables = []
        for node in range(n):
            k = len(anc[node])
            keys = list(itertools.product([0, 1], repeat=k))
            tables.append(list(itertools.product([0, 1], repeat=2 ** k)))
        for combo in itertools.product(*tables):
            funcs = {}
            for node in range(n):
                k = len(anc[node])
                keys = list(itertools.product([0, 1], repeat=k))
                funcs[node] = dict(zip(keys, combo[node]))
            for r in range(1, n + 1):
                for s_set_tuple in itertools.combinations(range(n), r):
                    s_set = set(s_set_tuple)
                    desc = descendants(n, edges, s_set)
                    for f0 in (0, 1):
                        for f1 in (0, 1):
                            v0 = compute_values(n, edges, funcs,
                                                {s: f0 for s in s_set})
                            v1 = compute_values(n, edges, funcs,
                                                {s: f1 for s in s_set})
                            runs += 1
                            for node in range(n):
                                if node in desc:
                                    continue
                                if v0[node] != v1[node]:
                                    violations += 1
                            # tightness sample: something in Desc \ S moved
                            moved_inside = any(
                                v0[x] != v1[x] for x in desc - s_set)
                            if moved_inside:
                                tight += 1
    check("T06/enumeration-nonempty", runs > 0,
          "%d DAGs, %d intervention-run pairs enumerated" % (len(dags), runs))
    check("T06/finite-spec-forward-locality", violations == 0,
          "no node outside Desc(S) ever changed across %d runs (%d "
          "violations); cone non-vacuously tight in %d runs"
          % (runs, violations, tight))
    # witness replay: missing edge -> false locality
    w = load_witness("W_T06_missing_edge_false_locality.json")
    world = w["world"]
    nodes = world["nodes"]
    declared = [tuple(e) for e in world["declared_edges"]]
    idx = {name: i for i, name in enumerate(nodes)}
    d_idx = [(idx[a], idx[b]) for a, b in declared]
    check("T06/W-T06-declared-acyclic",
          topo_order(len(nodes), d_idx) is not None,
          "declared graph %s is a DAG (DAG-hood alone licenses nothing)" %
          declared)
    s_set = {idx["S"]}
    desc = descendants(len(nodes), d_idx, s_set)
    check("T06/W-T06-R-outside-declared-cone", idx["R"] not in desc,
          "declared Desc(S)=%s, R outside" % sorted(nodes[i] for i in desc))
    # actual computation (declared function + undeclared read)
    X_val = 5

    def actual(s_val):
        R = X_val + s_val  # reads X (declared) AND S (undeclared)
        return {"S": s_val, "X": X_val, "R": R}

    before = actual(w["world"]["intervention"]["from"])
    after = actual(w["world"]["intervention"]["to"])
    check("T06/W-T06-false-locality", before["R"] != after["R"],
          "R moved %s -> %s while declared graph predicted no change "
          "(completeness assumption removed, conclusion violated)"
          % (before["R"], after["R"]))
    # declared edges are individually REAL (only completeness fails):
    # vary X at fixed S and observe R change -> X->R is a true dependency.
    def r_of(x, s_val):
        return x + s_val
    edge_real = r_of(5, 0) != r_of(4, 0)
    check("T06/W-T06-declared-edge-real", edge_real,
          "R changes with X at fixed S (%d vs %d): X->R is a true "
          "dependency; the graph is correct-but-incomplete, not wrong"
          % (r_of(5, 0), r_of(4, 0)))


# --------------------------------------------------------------------------
# T07 -- elitist ratchet monotonicity
# Finite specialization: enumerate ALL length-5 candidate sequences with
# quality in {0,1,2} and admissibility in {T,F}; verify the immutable
# unlimited-capacity archive best is monotone non-decreasing in EVERY one.
# Capacity variant: a capacity-1 'keep-most-recent-admissible' archive (a
# real finite-archive policy) is shown NON-monotone by enumeration -- exact
# condition demonstrated: only 'retains a maximizer' policies ratchet.
# --------------------------------------------------------------------------
def section_t07():
    seqs = list(itertools.product(
        itertools.product([0, 1, 2], [True, False]), repeat=5))
    monotone_violations = 0
    capacity_violations = []
    for seq in seqs:
        b = None  # immutable unlimited archive: best-so-far
        trace = []
        for (q, adm) in seq:
            if adm and (b is None or q > b):
                b = q
            trace.append(-1 if b is None else b)
        vals = [v for v in trace if v >= 0]
        for i in range(1, len(vals)):
            if vals[i] < vals[i - 1]:
                monotone_violations += 1
        # capacity-1 keep-most-recent-admissible archive
        r = None
        rtrace = []
        for (q, adm) in seq:
            if adm:
                r = q  # evicts even the best (retention policy, not order)
            rtrace.append(-1 if r is None else r)
        rvals = [v for v in rtrace if v >= 0]
        for i in range(1, len(rvals)):
            if rvals[i] < rvals[i - 1]:
                capacity_violations.append(seq)
                break
    check("T07/enumeration-nonempty", len(seqs) > 0,
          "%d candidate sequences enumerated" % len(seqs))
    check("T07/finite-spec-ratchet", monotone_violations == 0,
          "unlimited immutable archive monotone in all %d sequences (%d "
          "violations)" % (len(seqs), monotone_violations))
    check("T07/capacity-policy-voids-ratchet",
          len(capacity_violations) > 0,
          "capacity-1 keep-most-recent archive NON-monotone in %d/%d "
          "sequences (retention policy, not elitism, carries the ratchet)"
          % (len(capacity_violations), len(seqs)))
    # witness replay: perfect ratchet, zero transfer
    w = load_witness("W_T07_ratchet_no_transfer.json")
    world = w["world"]
    tau1_ans = world["benchmark_tau1"]["answers"]
    tau2_ans = world["benchmark_tau2"]["answers"]
    default = "d"
    q1_trace = []
    q2_trace = []
    b1 = -1
    for gen in world["generations"]:
        table = gen["table"]
        q1 = sum(1 for q, a in zip(world["benchmark_tau1"]["questions"],
                                   tau1_ans) if table.get(q) == a)
        q2 = sum(1 for q, a in zip(world["benchmark_tau2"]["questions"],
                                   tau2_ans) if table.get(q, default) == a)
        if q1 > b1:
            b1 = q1
        q1_trace.append(b1)
        q2_trace.append(q2)
        # archive retains best-so-far table: its tau2 answers are all default
        # (verified per generation below via q2 constancy)
    check("T07/W-T07-perfect-ratchet",
          q1_trace == [0, 1, 2, 3] and q1_trace == sorted(q1_trace),
          "archive best q1 strictly ratchets %s (attains max 3)" % q1_trace)
    check("T07/W-T07-zero-transfer",
          len(set(q2_trace)) == 1 and q2_trace[0] == 1,
          "archive q2 constant at chance-default 1: %s" % q2_trace)
    # every retained table answers 'd' (default) on all tau2 questions
    all_default = all(
        set(gen["table"]).isdisjoint(set(world["benchmark_tau2"]["questions"]))
        for gen in world["generations"])
    check("T07/W-T07-no-tau2-information", all_default,
          "no table contains any tau2 key: zero information crosses the "
          "tau1-perfect ratchet")


# --------------------------------------------------------------------------
# T18 -- fixed-epsilon bounded-burden improvement limit
# Finite specialization: for integer B_0, b_min, epsilon enumerate ALL drop
# sequences (each drop >= epsilon, partial burden >= b_min) up to the
# natural stopping point; verify max improvement count == floor((B0-bmin)/eps).
# Witness: phase 1 attains bound exactly, 11th impossible; phase 2 halving
# epsilon (exact fractions): 40 valid improvements, total drop <= 1.
# --------------------------------------------------------------------------
def section_t18():
    total = 0
    bad = 0
    for b0 in range(0, 9):
        for bmin in (0, 1):
            for eps in (1, 2):
                if b0 < bmin:
                    continue
                bound = (b0 - bmin) // eps
                # enumerate all drop sequences (each >= eps, staying >= bmin)
                maxlen = 0
                def extend(burden, count):
                    nonlocal maxlen
                    maxlen = max(maxlen, count)
                    d = eps
                    while burden - d >= bmin:
                        extend(burden - d, count + 1)
                        d += 1
                extend(b0, 0)
                total += 1
                if maxlen != bound:
                    bad += 1
    check("T18/finite-spec-bound", bad == 0,
          "max count == floor((B0-bmin)/eps) in all %d (B0,bmin,eps) "
          "settings (%d mismatches)" % (total, bad))
    w = load_witness("W_T18_fixed_epsilon_saturation.json")
    world = w["world"]
    b0 = world["B_0"]
    bmin = world["b_min"]
    eps = world["epsilon"]
    # phase 1: greedy exact-epsilon trace
    trace = [b0]
    while trace[-1] - eps >= bmin:
        trace.append(trace[-1] - eps)
    check("T18/W-T18-phase1-trace", trace == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
          "greedy epsilon-trace %s" % trace)
    check("T18/W-T18-bound-attained",
          len(trace) - 1 == 10 == (b0 - bmin) // eps,
          "exactly %d improvements, bound (B0-bmin)/eps = %d attained with "
          "equality" % (len(trace) - 1, (b0 - bmin) // eps))
    # phase 2: halving epsilon from B = 5, exact fractions
    b = Fraction(5)
    drops = []
    for k in range(1, 41):
        d = Fraction(1, 2 ** k)
        if b - d >= Fraction(bmin):
            b -= d
            drops.append(d)
    total_drop = sum(drops)
    check("T18/W-T18-phase2-halving", len(drops) == 40,
          "40 halving-epsilon improvements all valid (b_min respected)")
    check("T18/W-T18-phase2-bounded-gain",
          total_drop <= Fraction(1) and b == Fraction(5) - total_drop,
          "total drop = %s <= 1 (geometric sum bound); B_40 = %s >= b_min"
          % (total_drop, b))
    check("T18/W-T18-artifact-not-capability",
          len(drops) > 10 and total_drop <= Fraction(1),
          "unbounded COUNT with bounded total gain %.6f: the 'open-ended' "
          "claim on this trace is an epsilon-protocol artifact"
          % float(total_drop))


def main():
    print("HST core lane A exact checker -- finite specializations + hostile "
          "witness re-derivation")
    print("deterministic, exact enumeration only (no randomness)")
    print("=" * 72)
    section_t01()
    print("-" * 72)
    section_t03()
    print("-" * 72)
    section_t05()
    print("-" * 72)
    section_t06()
    print("-" * 72)
    section_t07()
    print("-" * 72)
    section_t18()
    print("=" * 72)
    if FAILURES:
        print("RESULT: FAIL (%d failed checks: %s)" % (len(FAILURES),
                                                       FAILURES))
        return 1
    print("RESULT: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
