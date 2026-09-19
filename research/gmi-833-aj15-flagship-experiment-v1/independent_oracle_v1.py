# -*- coding: utf-8 -*-
"""AJ15 flagship experiment -- route B, BLIND stage.  Imports nothing from route A.

Materially different constructions of the same quantities:
  * machines are strings ('S'+2 bits, or 8 bits), simulated by a character loop;
  * operational equivalence is decided by trace signatures on all words of length <= 3
    (exact for two machines with <= 2 states each: their product has <= 4 states), and
    cross-checked against the signature on words <= 4;
  * the development graph is built by character edit distance; distances by a list BFS;
  * the Pareto set by a sum-sorted sweep;
  * search S2 for B2 is a residual right-congruence construction, not a hill-climb;
  * every S1 solver found by route A is re-certified on all words by an independent
    product-state check against a string shift-register reference.

This file must not read the adjudicator registry and must not contain its vocabulary.

    python3 -I -B independent_oracle_v1.py [--blind BLIND_OUTCOME_V1.json] [--out ORACLE_RESULT_V1.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

def _read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

REPO = os.path.dirname(os.path.dirname(HERE))
CFG = _load_json(os.path.join(HERE, "SEARCH_CONFIG_V1.json"))


# --------------------------------------------------------------------------------------
# words and specifications on strings
# --------------------------------------------------------------------------------------


def all_words(max_len):
    out = [""]
    frontier = [""]
    for _ in range(max_len):
        frontier = [w + c for w in frontier for c in "01"]
        out.extend(frontier)
    return out


def spec(name, w):
    if name == "identity":
        return w
    if name == "not":
        return "".join("1" if c == "0" else "0" for c in w)
    if name == "toggle":
        return "".join("01"[i % 2] for i in range(len(w)))
    if name == "const0":
        return "0" * len(w)
    if name.startswith("delay"):
        k = int(name[5:])
        return ("0" * k + w)[: len(w)]
    raise ValueError(name)


# --------------------------------------------------------------------------------------
# B1 machines as strings
# --------------------------------------------------------------------------------------


def b1_universe():
    out = []
    for k in range(4):
        out.append("S" + format(k, "02b"))
    for k in range(256):
        out.append(format(k, "08b"))
    return out


def step(m, s, x):
    """(next_state, out) for machine string m in state s reading symbol char x."""
    if m[0] == "S":
        return 0, m[1 + int(x)]
    p = 4 * s + 2 * int(x)
    return int(m[p]), m[p + 1]


def emit(m, w):
    s = 0
    out = []
    for c in w:
        s, y = step(m, s, c)
        out.append(y)
    return "".join(out)


def signature(m, max_len):
    return tuple(emit(m, w) for w in all_words(max_len))


def reachable(m, max_len):
    seen = {0}
    for w in all_words(max_len):
        s = 0
        for c in w:
            s, _ = step(m, s, c)
            seen.add(s)
    return sorted(seen)


def state_dependent(m, max_len):
    r = reachable(m, max_len)
    for x in "01":
        if len({step(m, s, x)[1] for s in r}) > 1:
            return True
    return False


def n_states(m):
    return 1 if m[0] == "S" else 2


# --------------------------------------------------------------------------------------
# B1 atlas re-derivation
# --------------------------------------------------------------------------------------

TASKS = ["identity", "not", "delay1", "toggle", "const0"]


def b1_classes(U):
    sig3 = [signature(m, 3) for m in U]
    sig4 = [signature(m, 4) for m in U]
    first = {}
    cls = []
    for i, s in enumerate(sig3):
        if s not in first:
            first[s] = len(first)
        cls.append(first[s])
    # cross-check: the partition by words <= 4 is identical
    first4 = {}
    cls4 = []
    for s in sig4:
        if s not in first4:
            first4[s] = len(first4)
        cls4.append(first4[s])
    assert cls == cls4, "signature bound 3 is not exact"
    # class ids are ranked by first member, as in AJ11
    groups = {}
    for i, c in enumerate(cls):
        groups.setdefault(c, []).append(i)
    eq_pairs = sum(len(g) * (len(g) - 1) // 2 for g in groups.values())
    return cls, groups, eq_pairs


def b1_neighbours(U):
    idx = {m: i for i, m in enumerate(U)}
    adj = [set() for _ in U]
    for i, m in enumerate(U):
        if m[0] == "S":
            for k in (1, 2):
                z = m[:k] + ("1" if m[k] == "0" else "0") + m[k + 1:]
                adj[i].add(idx[z])
                adj[idx[z]].add(i)
            a, b = m[1], m[2]
            lift = "0" + a + "0" + b + "0" + a + "0" + b
            adj[i].add(idx[lift])  # directed lift, as registered
        else:
            for k in range(8):
                z = m[:k] + ("1" if m[k] == "0" else "0") + m[k + 1:]
                adj[i].add(idx[z])
                adj[idx[z]].add(i)
    return adj


def bfs_distances(adj, start):
    dist = {start: 0}
    layer = [start]
    d = 0
    while layer:
        d += 1
        nxt = []
        for u in layer:
            for v in adj[u]:
                if v not in dist:
                    dist[v] = d
                    nxt.append(v)
        layer = nxt
    return [dist[i] for i in range(len(adj))]


def pareto_sweep(vectors):
    order = sorted(range(len(vectors)), key=lambda i: (sum(vectors[i]), vectors[i]))
    front = []
    for i in order:
        v = vectors[i]
        dominated = False
        for j in front:
            w = vectors[j]
            if all(a <= b for a, b in zip(w, v)) and w != v:
                dominated = True
                break
        if not dominated:
            front.append(i)
    return sorted(front)


def b1_atlas(window):
    U = b1_universe()
    cls, groups, eq_pairs = b1_classes(U)
    W = all_words(window)
    caps = [[1 if all(emit(m, w) == spec(t, w) for w in W) else 0 for t in TASKS] for m in U]
    dist = bfs_distances(b1_neighbours(U), 0)
    rows = []
    vectors = []
    for i, m in enumerate(U):
        res = {"state_cells": 0 if m[0] == "S" else 1, "truth_rows": 2 if m[0] == "S" else 4}
        rows.append({"candidate_id": "M%03d" % i,
                     "presentation": "STATELESS" if m[0] == "S" else "ONE_BIT_FEEDBACK",
                     "operational_class": "C%03d" % cls[i],
                     "capability_exact": caps[i], "resources": res,
                     "development_distance_from_S00": dist[i]})
        vectors.append(tuple(1 - c for c in caps[i]) + (res["state_cells"], res["truth_rows"]))
    atlas = {"schema": "AJ11_COMPLETE_BOUNDED_ATLAS_V1",
             "scope": {"candidate_count": len(U), "operational_class_count": len(groups),
                       "tasks": TASKS, "max_word_length": window}, "rows": rows}
    canon = json.dumps(atlas, sort_keys=True, separators=(",", ":")).encode("utf-8")
    regimes = {}
    for ti, t in enumerate(TASKS):
        solvers = [i for i in range(len(U)) if caps[i][ti]]
        dep = [i for i in solvers if state_dependent(U[i], 3)]
        regimes[t] = {"exact_solvers": len(solvers), "with_state_dependent_output": len(dep),
                      "exact_solver_ids": ["M%03d" % i for i in solvers],
                      "state_dependent_ids": ["M%03d" % i for i in dep],
                      "operational_classes_among_solvers": len({cls[i] for i in solvers})}
    hist = {}
    for g in groups.values():
        hist[str(len(g))] = hist.get(str(len(g)), 0) + 1
    caphist = {}
    for c in caps:
        k = "/".join(str(x) for x in c)
        caphist[k] = caphist.get(k, 0) + 1
    dhist = {}
    for d in dist:
        dhist[str(d)] = dhist.get(str(d), 0) + 1
    return {"presentations": len(U), "operational_classes": len(groups),
            "pair_checks": len(U) * (len(U) - 1) // 2, "equivalent_pairs": eq_pairs,
            "class_size_histogram": dict(sorted(hist.items())),
            "capability_vector_histogram": dict(sorted(caphist.items())),
            "development_distance_histogram": dict(sorted(dhist.items(), key=lambda kv: int(kv[0]))),
            "development_max_distance": max(dist),
            "pareto_front": ["M%03d" % i for i in pareto_sweep(vectors)],
            "atlas_sha256": hashlib.sha256(canon).hexdigest(), "regimes": regimes}


# --------------------------------------------------------------------------------------
# B2: 4-state string machines, S2 residual construction, product certification
# --------------------------------------------------------------------------------------


def b2_step(m, s, x):
    n, o = m[s * 2 + int(x)]
    return n, str(o)


def b2_emit(m, w):
    s = 0
    out = []
    for c in w:
        s, y = b2_step(m, s, c)
        out.append(y)
    return "".join(out)


def b2_reachable(m):
    seen = {0}
    layer = [0]
    while layer:
        nxt = []
        for s in layer:
            for x in "01":
                n, _ = b2_step(m, s, x)
                if n not in seen:
                    seen.add(n)
                    nxt.append(n)
        layer = nxt
    return sorted(seen)


def b2_state_dependent(m):
    r = b2_reachable(m)
    for x in "01":
        if len({b2_step(m, s, x)[1] for s in r}) > 1:
            return True
    return False


def ref_step(name, s, x):
    """Reference machine: state is the string of the last k symbols (delay-k) or ''."""
    if name == "identity":
        return "", x
    k = int(name[5:])
    return (s + x)[-k:], s[0]


def certify_all_words(m, name):
    """Product-state check of a 4-state machine against the reference; exact for all words."""
    k = 0 if name == "identity" else int(name[5:])
    start = (0, "0" * k)
    seen = {start}
    layer = [start]
    while layer:
        nxt = []
        for sm, sr in layer:
            for x in "01":
                nm, ym = b2_step(m, sm, x)
                nr, yr = ref_step(name, sr, x)
                if ym != yr:
                    return False
                if (nm, nr) not in seen:
                    seen.add((nm, nr))
                    nxt.append((nm, nr))
        layer = nxt
    return True


def s2_construct(name, prefix_len=3, cont_len=3, state_cap=4, window=6):
    P = all_words(prefix_len)
    C = all_words(cont_len)
    sig = {}
    for u in P:
        sig[u] = tuple(spec(name, u + v)[len(u):] for v in C)
    classes = {}
    for u in P:
        classes.setdefault(sig[u], []).append(u)
    n = len(classes)
    if n > state_cap:
        return {"terminal": "NOT_RECOVERED_AT_SCOPE", "residual_classes": n,
                "reason": "residual classes exceed the state cap", "machine": None,
                "reachable_states": None, "state_dependent_output": None,
                "all_words_certified": None}
    reps = {}
    for s, members in classes.items():
        reps[s] = min(members, key=lambda u: (len(u), u))
    ids = {s: i for i, s in enumerate(sorted(reps, key=lambda s: (len(reps[s]), reps[s])))}
    table = {}
    for u in P:
        if len(u) >= prefix_len:
            continue
        for x in "01":
            key = (ids[sig[u]], x)
            val = (ids[sig[u + x]], spec(name, u + x)[-1])
            if key in table and table[key] != val:
                return {"terminal": "NOT_RECOVERED_AT_SCOPE", "residual_classes": n,
                        "reason": "inconsistent transition", "machine": None,
                        "reachable_states": None, "state_dependent_output": None,
                        "all_words_certified": None}
            table[key] = val
    if len(table) < 2 * n:
        return {"terminal": "NOT_RECOVERED_AT_SCOPE", "residual_classes": n,
                "reason": "a class has no transition witness within the prefix window",
                "machine": None, "reachable_states": None, "state_dependent_output": None,
                "all_words_certified": None}
    m = tuple((table[(s, x)][0], int(table[(s, x)][1])) for s in range(n) for x in "01")
    m = m + tuple((0, 0) for _ in range(2 * (state_cap - n)))  # pad unreachable states
    W = all_words(window)
    mism = sum(1 for w in W if b2_emit(m, w) != spec(name, w))
    return {"terminal": "RECOVERED" if mism == 0 else "NOT_RECOVERED_AT_SCOPE",
            "residual_classes": n, "window_mismatches": mism,
            "machine": [list(e) for e in m], "reachable_states": len(b2_reachable(m)),
            "state_dependent_output": b2_state_dependent(m),
            "all_words_certified": certify_all_words(m, name)}


# --------------------------------------------------------------------------------------
# nulls
# --------------------------------------------------------------------------------------


def null_n1(draws, seed):
    rng = random.Random(seed)
    hits = 0
    for _ in range(draws):
        m = "".join(str(rng.getrandbits(1)) for _ in range(8))
        if state_dependent(m, 3):
            hits += 1
    return {"draws": draws, "state_dependent_output_hits": hits, "rate": str(Fraction(hits, draws))}


def null_n3(draws, seed, window=6):
    rng = random.Random(seed)
    options = [(n, o) for n in range(4) for o in (0, 1)]
    W = all_words(window)
    hits = 0
    for _ in range(draws):
        m = tuple(rng.choice(options) for _ in range(8))
        if all(b2_emit(m, w) == spec("delay2", w) for w in W):
            hits += 1
    return {"draws": draws, "exact_delay2_solvers": hits, "rate": str(Fraction(hits, draws))}


def null_n2_b1(regimes):
    obs = tuple(regimes[t]["with_state_dependent_output"] > 0 for t in TASKS)
    total = 0
    match = 0
    for mask in range(32):
        vec = tuple(bool(mask >> i & 1) for i in range(5))
        if sum(vec) != 2:
            continue
        total += 1
        if vec == obs:
            match += 1
    return {"assignments": total, "matching_observed": match, "chance": str(Fraction(match, total))}


# --------------------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", default=os.path.join(HERE, "BLIND_OUTCOME_V1.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "ORACLE_RESULT_V1.json"))
    args = ap.parse_args(argv)

    b1 = b1_atlas(CFG["B1"]["evaluation_window_max_word_length"])
    b2 = {t: s2_construct(t) for t in CFG["B2"]["tasks"]}

    # AJ11 receipt cross-check (independent oracle for a package that has none)
    aj11 = _load_json(os.path.join(REPO, "research", "gmi-833-aj11-bounded-completeness-v1", "RESULT_V1.json"))
    aj11_checks = {
        "presentations": aj11["bounded_scope"]["presentations"] == b1["presentations"],
        "operational_classes": aj11["bounded_scope"]["operational_classes"] == b1["operational_classes"],
        "class_size_histogram": aj11["operational_class_size_histogram"] == b1["class_size_histogram"],
        "capability_vector_histogram": aj11["capability_vector_histogram"] == b1["capability_vector_histogram"],
        "development_distance_histogram": aj11["development_distance_histogram"] == b1["development_distance_histogram"],
        "development_max_distance": aj11["development_max_distance"] == b1["development_max_distance"],
        "pareto_frontier": aj11["pareto_frontier_candidate_ids"] == b1["pareto_front"],
        "atlas_sha256": aj11["atlas_sha256"] == b1["atlas_sha256"],
    }

    # Certify route A's S1 solvers, if the blind outcome exists.
    s1_cert = {}
    if os.path.exists(args.blind):
        blind = _load_json(args.blind)
        for t, r in blind["B2"]["regimes"].items():
            if r["machine"] is None:
                s1_cert[t] = {"terminal": r["terminal"], "certified": None}
            else:
                m = tuple((int(a), int(b)) for a, b in r["machine"])
                s1_cert[t] = {"terminal": r["terminal"], "certified": certify_all_words(m, t),
                              "state_dependent_output": b2_state_dependent(m),
                              "reachable_states": len(b2_reachable(m))}

    nulls = {"N1": null_n1(CFG["nulls"]["N1"]["draws"], CFG["nulls"]["N1"]["seed"]),
             "N2_B1": null_n2_b1(b1["regimes"]),
             "N3": null_n3(CFG["nulls"]["N3"]["draws"], CFG["nulls"]["N3"]["seed"])}

    preds = CFG["regime_predictions_operational_vocabulary"]
    failures = []
    for t, p in preds["B1"].items():
        r = b1["regimes"][t]
        want_none = p["predicted_exact_solvers_with_state_dependent_output"] == "NONE"
        if want_none and r["with_state_dependent_output"] != 0:
            failures.append("B1 %s" % t)
        if not want_none and (r["exact_solvers"] == 0 or r["with_state_dependent_output"] != r["exact_solvers"]):
            failures.append("B1 %s" % t)
    for t, p in preds["B2"].items():
        if b2[t]["terminal"] != p["predicted_terminal"]:
            failures.append("B2 %s terminal" % t)
        elif b2[t]["terminal"] == "RECOVERED":
            if not b2[t]["all_words_certified"]:
                failures.append("B2 %s certification" % t)
            if bool(b2[t]["state_dependent_output"]) != (p["predicted_state_dependent_output"] == "ALL"):
                failures.append("B2 %s dependence" % t)
    for t, c in s1_cert.items():
        if c["terminal"] == "RECOVERED" and not c["certified"]:
            failures.append("S1 %s solver not certified by route B" % t)
    if not all(aj11_checks.values()):
        failures.append("AJ11 receipt disagreement: %s" % [k for k, v in aj11_checks.items() if not v])

    out = {"schema": "AJ15_ORACLE_RESULT_V1", "route": "B", "registry_read": False,
           "B1": b1, "B2_S2": b2, "S1_solvers_certified_by_route_B": s1_cert,
           "aj11_independent_oracle": aj11_checks, "nulls": nulls,
           "failures": failures, "verdict": "FALSIFIED" if failures else "CONFIRMED"}
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"verdict": out["verdict"], "failures": failures,
                      "B1": {t: (r["with_state_dependent_output"], r["exact_solvers"]) for t, r in b1["regimes"].items()},
                      "B2_S2": {t: (r["terminal"], r["residual_classes"]) for t, r in b2.items()},
                      "aj11": all(aj11_checks.values()), "digest": b1["atlas_sha256"][:16]}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
