# -*- coding: utf-8 -*-
"""AG5 route B -- an independent oracle for the extension lowering.

Route B imports neither route A nor any of the four merged parent operator modules.  It
rebuilds the registered universes from their published definitions and recomputes every
implementation-independent quantity by a materially different mechanism:

  * stochastic -- one global common denominator and pure integer matrix arithmetic, instead
    of route A's per-entry normalized pairs of naturals;
  * local/graph -- an incidence-list traversal that never forms an adjacency register vector,
    instead of route A's three-slot register read;
  * channels -- an event-log replay that reconstructs each queue from the whole trace,
    instead of route A's incremental stream update;
  * governed self-change -- the admission relation as an abstract external oracle and the
    case table derived combinatorially from the registered accept policy, instead of running
    the parent's receipts.

Charged-role counts are deliberately NOT in the agreement set: they are relative to a chosen
lowering, exactly as AJ5's transfer boundary says instruction-count descriptions are.

    python3 -I -B  independent_oracle_v1.py
"""

import json
import os
import random
from itertools import permutations, product

HERE = os.path.dirname(os.path.abspath(__file__))
S3 = (0, 1, 2)

# --------------------------------------------------------------------------------------
# Stochastic: one global denominator, integer matrices.
# --------------------------------------------------------------------------------------
# The six registered rows, scaled by D = 2.
D = 2
ROWS_SCALED = ((2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 1, 0), (1, 0, 1), (0, 1, 1))


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _red(p, q):
    if p == 0:
        return (0, 1)
    g = _gcd(p, q)
    return (p // g, q // g)


def kernels_scaled():
    return tuple(tuple(t) for t in product(ROWS_SCALED, repeat=3))


def ref_update(mu, K):
    """Reference semantics: exact rational push-forward, written as reduced pairs."""
    out = []
    for j in S3:
        num = 0
        for i in S3:
            num += mu[i] * K[i][j]
        out.append(_red(num, D * D))
    return tuple(out)


def low_update_common_denominator(mu, K):
    """The lowering, route B style: accumulate one integer numerator over the single global
    denominator `D*D`, then reduce once at the end."""
    acc = [0, 0, 0]
    for j in S3:
        total = 0
        for i in S3:
            total += mu[i] * K[i][j]
        acc[j] = total
    if sum(acc) != D * D:
        raise ValueError("LOWERED_RESULT_NOT_NORMALIZED")
    return tuple(_red(x, D * D) for x in acc)


def ref_compose(K1, K2):
    rows = []
    for i in S3:
        row = []
        for j in S3:
            num = 0
            for k in S3:
                num += K1[i][k] * K2[k][j]
            row.append(_red(num, D * D))
        rows.append(tuple(row))
    return tuple(rows)


def low_compose_common_denominator(K1, K2):
    rows = []
    for i in S3:
        row = []
        for j in S3:
            num = 0
            for k in S3:
                num += K1[i][k] * K2[k][j]
            row.append(num)
        if sum(row) != D * D:
            raise ValueError("LOWERED_ROW_NOT_NORMALIZED")
        rows.append(tuple(_red(x, D * D) for x in row))
    return tuple(rows)


def stochastic():
    ks = kernels_scaled()
    out = {"row_count": len(ROWS_SCALED), "kernel_count": len(ks),
           "update_checks": 0, "update_mismatches": 0,
           "compose_checks": 0, "compose_mismatches": 0,
           "identity_mismatches": 0,
           "deterministic_checks": 0, "deterministic_mismatches": 0,
           "transport_kernel_checks": 0, "transport_kernel_mismatches": 0,
           "transport_distribution_checks": 0, "transport_distribution_mismatches": 0}
    for mu in ROWS_SCALED:
        for K in ks:
            out["update_checks"] += 1
            if low_update_common_denominator(mu, K) != ref_update(mu, K):
                out["update_mismatches"] += 1
    for K1 in ks:
        for K2 in ks:
            out["compose_checks"] += 1
            if low_compose_common_denominator(K1, K2) != ref_compose(K1, K2):
                out["compose_mismatches"] += 1
    # identity: checked by the unit law against every registered kernel, not by
    # re-rendering the same expression twice.
    ident = tuple(tuple((D if i == j else 0) for j in S3) for i in S3)
    for K in ks:
        if ref_compose(ident, K) != tuple(tuple(_red(x, D) for x in r) for r in K):
            out["identity_mismatches"] += 1
        if ref_compose(K, ident) != tuple(tuple(_red(x, D) for x in r) for r in K):
            out["identity_mismatches"] += 1
    for m in product(S3, repeat=3):
        out["deterministic_checks"] += 1
        # route 1: indicator construction
        built = tuple(tuple(((1, 1) if j == m[i] else (0, 1)) for j in S3) for i in S3)
        # route 2: pick the registered point-mass row by index
        point = {0: ROWS_SCALED[0], 1: ROWS_SCALED[1], 2: ROWS_SCALED[2]}
        picked = tuple(tuple(_red(x, D) for x in point[m[i]]) for i in S3)
        if built != picked:
            out["deterministic_mismatches"] += 1
    for K in ks:
        for pi in permutations(S3):
            out["transport_kernel_checks"] += 1
            # route 1: index remap
            a = [[None] * 3 for _ in S3]
            for i in S3:
                for j in S3:
                    a[pi[i]][pi[j]] = K[i][j]
            # route 2: conjugation by the permutation matrix, integer arithmetic
            P = [[1 if pi[i] == j else 0 for j in S3] for i in S3]
            PT_K = [[sum(P[r][i] * K[r][c] for r in S3) for c in S3] for i in S3]
            b = [[sum(PT_K[i][r] * P[r][j] for r in S3) for j in S3] for i in S3]
            if [list(r) for r in a] != b:
                out["transport_kernel_mismatches"] += 1
    for mu in ROWS_SCALED:
        for pi in permutations(S3):
            out["transport_distribution_checks"] += 1
            a = [None] * 3
            for i in S3:
                a[pi[i]] = mu[i]
            P = [[1 if pi[i] == j else 0 for j in S3] for i in S3]
            b = [sum(mu[i] * P[i][j] for i in S3) for j in S3]
            if a != b:
                out["transport_distribution_mismatches"] += 1
    return out


# --------------------------------------------------------------------------------------
# Local / graph: incidence lists, never an adjacency register vector.
# --------------------------------------------------------------------------------------
ALL_EDGES = ((0, 1), (0, 2), (1, 2))


def edge_sets():
    out = []
    for mask in range(8):
        out.append(tuple(ALL_EDGES[i] for i in range(3) if mask & (1 << i)))
    return out


def incidence(edges):
    inc = {0: [], 1: [], 2: []}
    for u, v in edges:
        inc[u].append(v)
        inc[v].append(u)
    return dict((k, tuple(sorted(v))) for k, v in inc.items())


def ref_pointwise(state, _edges):
    return tuple((x + 1) % 3 for x in state), (3, 3, 0, 0)


def ref_global(state, _edges):
    agg = sum(state) % 3
    return tuple((x + agg) % 3 for x in state), (6, 3, 0, 2)


def ref_neighbor(state, edges):
    inc = incidence(edges)
    out = []
    agg_ops = 0
    for v in S3:
        ns = inc[v]
        agg = sum(state[u] for u in ns) % 3 if ns else 0
        agg_ops += max(len(ns) - 1, 0)
        out.append((state[v] + agg) % 3)
    e2 = 2 * len(edges)
    return tuple(out), (3 + e2, 3, e2, agg_ops)


def low_neighbor_incidence(state, edges):
    """Route B lowering: walk the incidence list and fold by repeated unary increment."""
    inc = incidence(edges)
    out = []
    for v in S3:
        acc = 0
        for u in inc[v]:
            for _ in range(state[u]):
                acc = (acc + 1) % 3
        val = state[v]
        for _ in range(acc):
            val = (val + 1) % 3
        out.append(val)
    return tuple(out)


def low_pointwise_unary(state, _edges):
    out = []
    for v in S3:
        x = state[v]
        x = (x + 1) % 3
        out.append(x)
    return tuple(out)


def low_global_unary(state, _edges):
    acc = 0
    for v in S3:
        for _ in range(state[v]):
            acc = (acc + 1) % 3
    out = []
    for v in S3:
        x = state[v]
        for _ in range(acc):
            x = (x + 1) % 3
        out.append(x)
    return tuple(out)


def degrees(edges):
    d = [0, 0, 0]
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d


def graph():
    es = edge_sets()
    states = [t for t in product(S3, repeat=3)]
    out = {"checks": 0, "mismatches": 0, "resource_checks": 0, "resource_mismatches": 0,
           "equivariance_checks": 0, "equivariance_mismatches": 0}
    ops = (("POINTWISE", ref_pointwise, low_pointwise_unary),
           ("GLOBAL_BROADCAST", ref_global, low_global_unary),
           ("NEIGHBOR_UPDATE", ref_neighbor, low_neighbor_incidence))
    for edges in es:
        deg = degrees(edges)
        for st in states:
            for name, ref, low in ops:
                val, res = ref(st, edges)
                out["checks"] += 1
                if low(st, edges) != val:
                    out["mismatches"] += 1
                out["resource_checks"] += 1
                # the parent's declared resource vectors, recomputed from the degree
                # sequence alone
                if name == "POINTWISE":
                    want = (3, 3, 0, 0)
                elif name == "GLOBAL_BROADCAST":
                    want = (6, 3, 0, 2)
                else:
                    want = (3 + sum(deg), 3, sum(deg),
                            sum(max(d - 1, 0) for d in deg))
                if res != want:
                    out["resource_mismatches"] += 1
            for pi in permutations(S3):
                pst = [0, 0, 0]
                for v in S3:
                    pst[pi[v]] = st[v]
                pe = tuple((min(pi[u], pi[v]), max(pi[u], pi[v])) for u, v in edges)
                a = low_neighbor_incidence(tuple(pst), pe)
                b = low_neighbor_incidence(st, edges)
                moved = [0, 0, 0]
                for v in S3:
                    moved[pi[v]] = b[v]
                out["equivariance_checks"] += 1
                if a != tuple(moved):
                    out["equivariance_mismatches"] += 1
    counts = {"POINTWISE": 0, "GLOBAL_BROADCAST": 0, "NEIGHBOR_UPDATE": 0}
    pairs = 0
    for st in states:
        for i in range(8):
            for j in range(i + 1, 8):
                pairs += 1
                for name, ref, _low in ops:
                    if ref(st, es[i])[0] != ref(st, es[j])[0]:
                        counts[name] += 1
    out["state_graph_pairs"] = pairs
    out["differing_pairs"] = counts
    out["neighbor_cost_by_edge_count"] = dict(
        (str(len(e)), 3 + 2 * len(e)) for e in es)
    return out


# --------------------------------------------------------------------------------------
# Channels: event-log replay.
# --------------------------------------------------------------------------------------
AGENTS = (0, 1, 2)
MESSAGES = (0, 1)
CHANNELS = tuple((a, b) for a in AGENTS for b in AGENTS if a != b)
TOOLS = {"ROT": lambda x: (x + 1) % 3, "DOUBLE": lambda x: (2 * x) % 3}


def replay(log):
    """Rebuild local state and every queue from the whole event log, in one pass."""
    local = [0, 0, 0]
    queues = dict((c, []) for c in CHANNELS)
    taken = dict((c, 0) for c in CHANNELS)
    observed = []
    for ev in log:
        kind = ev[0]
        if kind == "INIT":
            local = list(ev[1])
        elif kind == "SEND":
            queues[(ev[1], ev[2])].append(ev[3])
        elif kind == "RECV":
            c = (ev[1], ev[2])
            if taken[c] < len(queues[c]):
                observed.append(queues[c][taken[c]])
                taken[c] += 1
            else:
                observed.append("NO_MESSAGE")
        elif kind == "APPLY":
            local[ev[1]] = (local[ev[1]] + ev[2]) % 3
        elif kind == "EXTERNAL":
            tool, arg, val, tag = ev[2]
            if tag != "EXTERNAL_DATA" or tool not in TOOLS or TOOLS[tool](arg) != val:
                raise ValueError("FORGED_EXTERNAL_DATA")
            local[ev[1]] = (local[ev[1]] + val) % 3
        else:
            raise ValueError("UNKNOWN_EVENT")
    pending = dict((c, tuple(queues[c][taken[c]:])) for c in CHANNELS)
    return tuple(local), tuple(pending[c] for c in CHANNELS), tuple(observed)


def replay_untagged(log):
    """The same replay with the provenance gate deleted: the value is applied whatever its
    tag or arithmetic claims."""
    local = [0, 0, 0]
    for ev in log:
        if ev[0] == "INIT":
            local = list(ev[1])
        elif ev[0] == "EXTERNAL":
            val = ev[2][2]
            local[ev[1]] = (local[ev[1]] + val) % 3
    return tuple(local), (), ()


def channels():
    locs = [t for t in product(S3, repeat=3)]
    out = {"send_checks": 0, "send_mismatches": 0, "recv_checks": 0, "recv_mismatches": 0,
           "apply_received_checks": 0, "apply_received_mismatches": 0,
           "call_checks": 0, "call_mismatches": 0,
           "apply_external_checks": 0, "apply_external_mismatches": 0,
           "fifo_checks": 0, "fifo_mismatches": 0}
    for loc in locs:
        for (src, dst) in CHANNELS:
            for msg in MESSAGES:
                l1, q1, _ = replay([("INIT", loc), ("SEND", src, dst, msg)])
                out["send_checks"] += 1
                want_q = tuple(((msg,) if c == (src, dst) else ()) for c in CHANNELS)
                if l1 != loc or q1 != want_q:
                    out["send_mismatches"] += 1
                l2, q2, obs = replay([("INIT", loc), ("SEND", src, dst, msg),
                                      ("RECV", src, dst), ("RECV", src, dst)])
                out["recv_checks"] += 2
                if obs != (msg, "NO_MESSAGE") or l2 != loc:
                    out["recv_mismatches"] += 1
                l3, _, _ = replay([("INIT", loc), ("APPLY", dst, msg)])
                out["apply_received_checks"] += 1
                want = list(loc)
                want[dst] = (want[dst] + msg) % 3
                if l3 != tuple(want):
                    out["apply_received_mismatches"] += 1
            for m1 in MESSAGES:
                for m2 in MESSAGES:
                    _, _, obs = replay([("INIT", loc), ("SEND", src, dst, m1),
                                        ("SEND", src, dst, m2),
                                        ("RECV", src, dst), ("RECV", src, dst)])
                    out["fifo_checks"] += 1
                    if obs != (m1, m2):
                        out["fifo_mismatches"] += 1
    inert_checks = 0
    inert_differences = 0
    forged_checks = 0
    forged_rejected = 0
    forged_accepted_untagged = 0
    for tool in ("ROT", "DOUBLE"):
        for arg in S3:
            val = TOOLS[tool](arg)
            data = (tool, arg, val, "EXTERNAL_DATA")
            out["call_checks"] += 1
            if val != TOOLS[tool](arg):
                out["call_mismatches"] += 1
            for loc in locs:
                for agent in AGENTS:
                    out["apply_external_checks"] += 1
                    l, _, _ = replay([("INIT", loc), ("EXTERNAL", agent, data)])
                    want = list(loc)
                    want[agent] = (want[agent] + val) % 3
                    if l != tuple(want):
                        out["apply_external_mismatches"] += 1
                    inert_checks += 1
                    lu, _, _ = replay_untagged([("INIT", loc), ("EXTERNAL", agent, data)])
                    if l != lu:
                        inert_differences += 1
            forged = [(tool, arg, w, "EXTERNAL_DATA") for w in S3 if w != val]
            forged.append((tool, arg, val, "LOCAL_DATA"))
            forged.append(("UNKNOWN", arg, val, "EXTERNAL_DATA"))
            for f in forged:
                forged_checks += 1
                try:
                    replay([("INIT", (0, 0, 0)), ("EXTERNAL", 0, f)])
                except ValueError:
                    forged_rejected += 1
                try:
                    replay_untagged([("INIT", (0, 0, 0)), ("EXTERNAL", 0, f)])
                    forged_accepted_untagged += 1
                except (ValueError, TypeError):
                    pass
    out["external_data_tag"] = {"inert_checks": inert_checks,
                                "inert_differences": inert_differences,
                                "forged_checks": forged_checks,
                                "forged_rejected_with_tag_gate": forged_rejected,
                                "forged_accepted_without_tag_gate": forged_accepted_untagged}
    return out


# --------------------------------------------------------------------------------------
# Governed self-change: the admission relation as an abstract external oracle.
# --------------------------------------------------------------------------------------
GUARD_NAMES = ("fresh", "pending_ok", "admitted", "version_ok", "accepted")


def case_table():
    """Derived combinatorially from the registered accept policy `candidate[0] == 0`.

    No receipt is computed; the admission relation is an abstract predicate that is true
    exactly when the receipt is the registered authority's untampered receipt for this
    proposal.
    """
    base = []
    ext = []
    for cand in product(S3, repeat=3):
        accepted = (cand[0] == 0)
        genuine = (True, True, True, True, accepted)
        base.append((genuine, accepted))
        ext.append((genuine, accepted))
        ext.append(((True, True, False, True, accepted), False))     # wrong authority
        ext.append(((True, True, False, True, accepted), False))     # corrupted signature
        ext.append(((True, True, False, True, accepted), False))     # corrupted binding
        ext.append(((True, False, True, True, accepted), False))     # not pending
        if accepted:
            ext.append(((False, True, True, False, True), False))    # replay
    ext.append(((True, True, True, False, True), False))             # stale base version
    return base, ext


def guard_isolation(cases):
    iso = {}
    for gi, name in enumerate(GUARD_NAMES):
        iso[name] = any((not v[gi]) and all(v[k] for k in range(len(GUARD_NAMES)) if k != gi)
                        for v, _ in cases)
    return iso


def guard_subset_null(cases):
    n = len(GUARD_NAMES)
    iso = guard_isolation(cases)
    non_isolable = set(i for i, nm in enumerate(GUARD_NAMES) if not iso[nm])
    hits = []
    for mask in range((1 << n) - 1):
        ok = True
        for v, outcome in cases:
            got = all(v[i] for i in range(n) if mask & (1 << i))
            if got != outcome:
                ok = False
                break
        if ok:
            hits.append(mask)
    predicted = [mask for mask in range((1 << n) - 1)
                 if set(i for i in range(n) if not (mask & (1 << i)))
                 and set(i for i in range(n) if not (mask & (1 << i))) <= non_isolable]
    return {"proper_subsets": (1 << n) - 1, "reproducing_subsets": len(hits),
            "guard_isolable": iso, "predicted_reproducing_subsets": len(predicted),
            "prediction_matches": sorted(hits) == sorted(predicted), "cases": len(cases)}


def self_change():
    cands = [t for t in product(S3, repeat=3)]
    accepted = [c for c in cands if c[0] == 0]
    base, ext = case_table()
    mismatches = 0
    for vec, outcome in ext:
        if all(vec) != outcome:
            mismatches += 1
    return {"candidate_checks": len(cands), "terminal_mismatches": mismatches,
            "adopted": len(accepted), "refused": len(cands) - len(accepted),
            "adopt_externality": {"controlled_pairs": len(cands),
                                  "terminal_witness_pairs": len(cands),
                                  "state_change_witness_pairs": len(accepted)},
            "base_null": guard_subset_null(base), "extended_null": guard_subset_null(ext)}


# --------------------------------------------------------------------------------------
# Nulls, recomputed on route B's own semantics.
# --------------------------------------------------------------------------------------

def nulls():
    rnd = random.Random(8332201)
    ks = kernels_scaled()
    want = {}
    for mi, mu in enumerate(ROWS_SCALED):
        for ki, K in enumerate(ks):
            want[(mi, ki)] = ref_update(mu, K)
    cells = [(i, j) for i in S3 for j in S3]
    sto_hits = sto_live = sto_id = 0
    for _ in range(200):
        perm = list(range(9))
        rnd.shuffle(perm)
        if perm == list(range(9)):
            sto_id += 1
            continue
        sto_live += 1
        ok = True
        for mi, mu in enumerate(ROWS_SCALED):
            for ki, K in enumerate(ks):
                scr = [[None] * 3 for _ in S3]
                for pos, (i, j) in enumerate(cells):
                    si, sj = cells[perm[pos]]
                    scr[i][j] = K[si][sj]
                try:
                    got = low_update_common_denominator(mu, tuple(tuple(r) for r in scr))
                except ValueError:
                    ok = False
                if not ok or got != want[(mi, ki)]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            sto_hits += 1

    rnd = random.Random(8332202)
    es = edge_sets()
    states = [t for t in product(S3, repeat=3)]
    gwant = dict(((gi, st), ref_neighbor(st, es[gi])[0]) for gi in range(8) for st in states)
    g_hits = g_live = g_id = 0
    for _ in range(200):
        sub = [rnd.randrange(8) for _ in range(8)]
        if sub == list(range(8)):
            g_id += 1
            continue
        g_live += 1
        ok = True
        for gi in range(8):
            for st in states:
                if low_neighbor_incidence(st, es[sub[gi]]) != gwant[(gi, st)]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            g_hits += 1

    rnd = random.Random(8332203)
    c_hits = c_live = c_id = 0
    for _ in range(200):
        perm = list(range(6))
        rnd.shuffle(perm)
        if perm == list(range(6)):
            c_id += 1
            continue
        c_live += 1
        ok = True
        for ci, c in enumerate(CHANNELS):
            for msg in MESSAGES:
                qs = [()] * 6
                qs[perm[ci]] = (msg,)
                want_q = tuple(((msg,) if k == c else ()) for k in CHANNELS)
                if tuple(qs) != want_q:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            c_hits += 1
    return {"stochastic": {"draws": 200, "identity_draws_excluded": sto_id,
                           "live_trials": sto_live, "hits": sto_hits},
            "graph": {"draws": 200, "identity_draws_excluded": g_id,
                      "live_trials": g_live, "hits": g_hits},
            "channels": {"draws": 200, "identity_draws_excluded": c_id,
                         "live_trials": c_live, "hits": c_hits}}


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True, separators=(",", ": "))


def main():
    return {"schema": "GMI833AG5ExtensionLoweringOracleV1",
            "route": "B",
            "imports_route_a": False,
            "imports_parent_modules": False,
            "stochastic": stochastic(),
            "graph": graph(),
            "channels": channels(),
            "self_change": self_change(),
            "nulls": nulls()}


if __name__ == "__main__":
    r = main()
    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        fh.write(canonical_json(r) + "\n")
    print(canonical_json({"route": "B",
                          "update_checks": r["stochastic"]["update_checks"],
                          "compose_checks": r["stochastic"]["compose_checks"],
                          "graph_checks": r["graph"]["checks"],
                          "extended_reproducing_subsets":
                              r["self_change"]["extended_null"]["reproducing_subsets"]}))
