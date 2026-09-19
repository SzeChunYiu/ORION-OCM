# -*- coding: utf-8 -*-
"""AJ15 flagship experiment -- route A, BLIND stage.

Runs the single end-to-end flagship protocol frozen in FREEZE_V1.md:

  B1  the bounded 260-presentation universe, every candidate enumerated; per regime the
      exact solvers and, among them, those whose output depends on a reachable internal
      state; the frozen regime prediction is checked and the verdict is CONFIRMED or
      FALSIFIED (never softened);
  B2  the 4-state universe (16,777,216 presentations, NOT enumerated) searched by S1, a
      random-restart single-entry hill-climb under a frozen budget; every found solver is
      certified on ALL words by a product-state check against a reference transducer;
      the honest failure terminal NOT_RECOVERED_AT_SCOPE is exercised on delay3;
  nulls N1 N2 N3; hostiles H3 H4 H5 H6 with `applicable` flags.

This file must not read the adjudicator registry and must not contain its vocabulary; the
post-hoc stage audits that.  Stdlib only; exact integers and Fractions; no floats.

    python3 -I -B aj15_flagship_v1.py [--out BLIND_OUTCOME_V1.json]
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import random
import sys
from collections import Counter, deque
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

CFG = _load_json(os.path.join(HERE, "SEARCH_CONFIG_V1.json"))
BITS = (0, 1)

# ----------------------------------------------------------------------------------------
# Specifications (total functions on binary words), shared by B1 and B2.
# ----------------------------------------------------------------------------------------


def spec_identity(w):
    return tuple(w)


def spec_not(w):
    return tuple(1 - x for x in w)


def spec_delay(k):
    def f(w):
        return tuple((0,) * k + tuple(w))[: len(w)]
    return f


def spec_toggle(w):
    return tuple(i % 2 for i in range(len(w)))


def spec_const0(w):
    return (0,) * len(w)


SPECS = {
    "identity": spec_identity,
    "not": spec_not,
    "delay1": spec_delay(1),
    "delay2": spec_delay(2),
    "delay3": spec_delay(3),
    "toggle": spec_toggle,
    "const0": spec_const0,
}


def words_upto(h):
    out = [()]
    for n in range(1, h + 1):
        out.extend(itertools.product(BITS, repeat=n))
    return out


# ----------------------------------------------------------------------------------------
# Machines.  A presentation is ('S', (o0, o1)) for a one-symbol map or ('M', rows) where
# rows = ((n00, o00), (n01, o01), (n10, o10), (n11, o11)) indexed by (state, symbol).
# For B2 a machine is a tuple of 8 (next, out) pairs indexed by state*2+symbol, 4 states.
# ----------------------------------------------------------------------------------------


def b1_candidates():
    out = [("S", x) for x in itertools.product(BITS, repeat=2)]
    for bits in itertools.product(BITS, repeat=8):
        out.append(("M", tuple((bits[2 * i], bits[2 * i + 1]) for i in range(4))))
    return out


def b1_table(c):
    typ, data = c
    if typ == "S":
        return {(0, 0): (0, data[0]), (0, 1): (0, data[1])}
    return {(0, 0): data[0], (0, 1): data[1], (1, 0): data[2], (1, 1): data[3]}


def run_table(t, word):
    s = 0
    out = []
    for x in word:
        s, y = t[(s, x)]
        out.append(y)
    return tuple(out)


def b1_equivalent(a, b):
    ta, tb = b1_table(a), b1_table(b)
    q = [(0, 0)]
    seen = set()
    while q:
        sa, sb = q.pop()
        if (sa, sb) in seen:
            continue
        seen.add((sa, sb))
        for x in BITS:
            na, ya = ta[(sa, x)]
            nb, yb = tb[(sb, x)]
            if ya != yb:
                return False
            q.append((na, nb))
    return True


def reachable_states(t, n_states):
    seen = {0}
    q = deque([0])
    while q:
        s = q.popleft()
        for x in BITS:
            n = t[(s, x)][0]
            if n not in seen:
                seen.add(n)
                q.append(n)
    return sorted(seen)


def state_dependent_output(t, n_states):
    """True iff two REACHABLE states emit different outputs on the same symbol."""
    reach = reachable_states(t, n_states)
    for x in BITS:
        outs = {t[(s, x)][1] for s in reach}
        if len(outs) > 1:
            return True
    return False


# ----------------------------------------------------------------------------------------
# B1: quotient, development graph, atlas digest (re-derivation of the AJ11 universe).
# ----------------------------------------------------------------------------------------


def b1_quotient(cs):
    par = list(range(len(cs)))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    checks = 0
    eqpairs = 0
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            checks += 1
            if b1_equivalent(cs[i], cs[j]):
                eqpairs += 1
                a, b = find(i), find(j)
                if a != b:
                    par[b] = a
    groups = {}
    for i in range(len(cs)):
        groups.setdefault(find(i), []).append(i)
    roots = sorted(groups, key=lambda r: min(groups[r]))
    cls = {}
    for ci, r in enumerate(roots):
        for i in groups[r]:
            cls[i] = ci
    return groups, cls, checks, eqpairs


def b1_development_distances(cs):
    index = {c: i for i, c in enumerate(cs)}
    adj = [set() for _ in cs]
    for i, c in enumerate(cs[:4]):
        b = list(c[1])
        for k in range(2):
            z = b[:]
            z[k] ^= 1
            j = index[("S", tuple(z))]
            adj[i].add(j)
            adj[j].add(i)
    for i, c in enumerate(cs[4:], start=4):
        bits = [b for row in c[1] for b in row]
        for k in range(8):
            z = bits[:]
            z[k] ^= 1
            rows = tuple((z[2 * r], z[2 * r + 1]) for r in range(4))
            j = index[("M", rows)]
            adj[i].add(j)
            adj[j].add(i)
    for i, c in enumerate(cs[:4]):
        o = c[1]
        lift = ("M", ((0, o[0]), (0, o[1]), (0, o[0]), (0, o[1])))
        adj[i].add(index[lift])
    d = [None] * len(cs)
    d[0] = 0
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if d[v] is None:
                d[v] = d[u] + 1
                q.append(v)
    assert all(x is not None for x in d)
    return d


def pareto(vectors):
    def dom(a, b):
        return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))
    return [i for i, v in enumerate(vectors)
            if not any(dom(w, v) for j, w in enumerate(vectors) if j != i)]


B1_TASKS = ("identity", "not", "delay1", "toggle", "const0")


def b1_capabilities(cs, window):
    ws = words_upto(window)
    caps = []
    for c in cs:
        t = b1_table(c)
        caps.append(tuple(all(run_table(t, w) == SPECS[name](w) for w in ws) for name in B1_TASKS))
    return caps


def build_b1(window=4):
    cs = b1_candidates()
    groups, cls, pair_checks, eqpairs = b1_quotient(cs)
    caps = b1_capabilities(cs, window)
    dist = b1_development_distances(cs)
    rows = []
    vectors = []
    for i, c in enumerate(cs):
        res = {"state_cells": 0 if c[0] == "S" else 1, "truth_rows": 2 if c[0] == "S" else 4}
        rows.append({
            "candidate_id": "M%03d" % i,
            "presentation": "STATELESS" if c[0] == "S" else "ONE_BIT_FEEDBACK",
            "operational_class": "C%03d" % cls[i],
            "capability_exact": [int(x) for x in caps[i]],
            "resources": res,
            "development_distance_from_S00": dist[i],
        })
        vectors.append(tuple(0 if x else 1 for x in caps[i]) + (res["state_cells"], res["truth_rows"]))
    front = pareto(vectors)
    atlas = {"schema": "AJ11_COMPLETE_BOUNDED_ATLAS_V1",
             "scope": {"candidate_count": 260, "operational_class_count": len(groups),
                       "tasks": list(B1_TASKS), "max_word_length": window},
             "rows": rows}
    canonical = json.dumps(atlas, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {"candidates": cs, "groups": groups, "cls": cls, "pair_checks": pair_checks,
            "equivalent_pairs": eqpairs, "caps": caps, "dist": dist, "front": front,
            "atlas": atlas, "digest": digest}


def b1_regimes(b1):
    """Per regime: exact solvers, and how many have a reachable-state-dependent output."""
    cs = b1["candidates"]
    out = {}
    for ti, name in enumerate(B1_TASKS):
        solvers = [i for i, cap in enumerate(b1["caps"]) if cap[ti]]
        dep = []
        for i in solvers:
            t = b1_table(cs[i])
            n = 1 if cs[i][0] == "S" else 2
            if state_dependent_output(t, n):
                dep.append(i)
        cap_class = {b1["cls"][i] for i in solvers}
        out[name] = {
            "exact_solvers": len(solvers),
            "exact_solver_ids": ["M%03d" % i for i in solvers],
            "operational_classes_among_solvers": len(cap_class),
            "with_state_dependent_output": len(dep),
            "state_dependent_ids": ["M%03d" % i for i in dep],
            "memoryless_realizable": name in ("identity", "not", "const0"),
        }
    return out


# ----------------------------------------------------------------------------------------
# B2: 4-state machines, S1 search, all-words certification.
# ----------------------------------------------------------------------------------------

B2_STATES = 4
B2_OPTIONS = [(n, o) for n in range(B2_STATES) for o in BITS]  # 8 options per entry


def b2_run(m, word):
    s = 0
    out = []
    for x in word:
        n, y = m[s * 2 + x]
        s = n
        out.append(y)
    return tuple(out)


def b2_mismatch(m, spec_outputs, ws):
    bad = 0
    for w, want in zip(ws, spec_outputs):
        if b2_run(m, w) != want:
            bad += 1
    return bad


def b2_as_table(m):
    return {(s, x): m[s * 2 + x] for s in range(B2_STATES) for x in BITS}


def reference_transducer(name):
    """A finite reference machine for each B2 specification, as a dict
    state -> {symbol: (next_state, out)}.  delay-k is a k-bit shift register."""
    if name == "identity":
        return {0: {0: (0, 0), 1: (0, 1)}}
    if name.startswith("delay"):
        k = int(name[5:])
        states = list(itertools.product(BITS, repeat=k))  # register contents, oldest first
        idx = {s: i for i, s in enumerate(states)}
        ref = {}
        for s in states:
            ref[idx[s]] = {}
            for x in BITS:
                nxt = tuple(s[1:]) + (x,)
                ref[idx[s]][x] = (idx[nxt], s[0])
        return ref
    raise ValueError(name)


def product_certify(m, name):
    """Exact all-words equivalence between a B2 machine and the reference transducer."""
    ref = reference_transducer(name)
    q = [(0, 0)]
    seen = set()
    while q:
        sm, sr = q.pop()
        if (sm, sr) in seen:
            continue
        seen.add((sm, sr))
        for x in BITS:
            nm, ym = m[sm * 2 + x]
            nr, yr = ref[sr][x]
            if ym != yr:
                return False
            q.append((nm, nr))
    return True


def s1_search(name, seed, budget, restart_after, window=6):
    rng = random.Random(seed)
    ws = words_upto(window)
    want = [SPECS[name](w) for w in ws]
    evals = 0
    restarts = 0
    best_overall = None
    while evals < budget:
        cur = tuple(rng.choice(B2_OPTIONS) for _ in range(8))
        cur_bad = b2_mismatch(cur, want, ws)
        evals += 1
        restarts += 1
        stale = 0
        if best_overall is None or cur_bad < best_overall[0]:
            best_overall = (cur_bad, cur)
        while cur_bad > 0 and evals < budget and stale < restart_after:
            k = rng.randrange(8)
            alt = [o for o in B2_OPTIONS if o != cur[k]]
            cand = cur[:k] + (rng.choice(alt),) + cur[k + 1:]
            cand_bad = b2_mismatch(cand, want, ws)
            evals += 1
            if cand_bad < cur_bad:
                stale = 0
            else:
                stale += 1
            if cand_bad <= cur_bad:
                cur, cur_bad = cand, cand_bad
                if cur_bad < best_overall[0]:
                    best_overall = (cur_bad, cur)
        if cur_bad == 0:
            t = b2_as_table(cur)
            return {"terminal": "RECOVERED", "evaluations": evals, "restarts": restarts,
                    "machine": [list(e) for e in cur],
                    "reachable_states": len(reachable_states(t, B2_STATES)),
                    "state_dependent_output": state_dependent_output(t, B2_STATES),
                    "all_words_certified": product_certify(cur, name)}
    return {"terminal": "NOT_RECOVERED_AT_SCOPE", "evaluations": evals, "restarts": restarts,
            "best_mismatch_within_budget": best_overall[0], "machine": None,
            "reachable_states": None, "state_dependent_output": None,
            "all_words_certified": None}


def run_b2(budget=None, restart_after=None, seed=None):
    s1 = CFG["B2"]["search_S1"]
    budget = s1["budget_evaluations_per_regime"] if budget is None else budget
    restart_after = s1["restart_after_non_improving_evaluations"] if restart_after is None else restart_after
    seed = s1["seed"] if seed is None else seed
    out = {}
    for name in CFG["B2"]["tasks"]:
        out[name] = s1_search(name, seed, budget, restart_after, CFG["B2"]["evaluation_window_max_word_length"])
    return out


# ----------------------------------------------------------------------------------------
# Verdict against the frozen prediction table.
# ----------------------------------------------------------------------------------------


def verdict_b1(regimes, predictions):
    failures = []
    for name, pred in predictions.items():
        r = regimes[name]
        if pred["predicted_exact_solvers_with_state_dependent_output"] == "NONE":
            if r["with_state_dependent_output"] != 0:
                failures.append("%s: predicted NONE, observed %d of %d" % (name, r["with_state_dependent_output"], r["exact_solvers"]))
        else:
            if r["exact_solvers"] == 0 or r["with_state_dependent_output"] != r["exact_solvers"]:
                failures.append("%s: predicted ALL, observed %d of %d" % (name, r["with_state_dependent_output"], r["exact_solvers"]))
    return failures


def verdict_b2(b2, predictions):
    failures = []
    for name, pred in predictions.items():
        r = b2[name]
        if r["terminal"] != pred["predicted_terminal"]:
            failures.append("%s: predicted %s, observed %s" % (name, pred["predicted_terminal"], r["terminal"]))
            continue
        if r["terminal"] == "RECOVERED":
            if not r["all_words_certified"]:
                failures.append("%s: found solver fails all-words certification" % name)
            want_dep = pred["predicted_state_dependent_output"] == "ALL"
            if bool(r["state_dependent_output"]) != want_dep:
                failures.append("%s: state dependence %s, predicted %s" % (name, r["state_dependent_output"], pred["predicted_state_dependent_output"]))
    return failures


# ----------------------------------------------------------------------------------------
# Nulls.
# ----------------------------------------------------------------------------------------


def null_n1(draws, seed):
    rng = random.Random(seed)
    hits = 0
    for _ in range(draws):
        bits = [rng.getrandbits(1) for _ in range(8)]
        rows = tuple((bits[2 * i], bits[2 * i + 1]) for i in range(4))
        t = b1_table(("M", rows))
        if state_dependent_output(t, 2):
            hits += 1
    return {"draws": draws, "state_dependent_output_hits": hits,
            "rate": str(Fraction(hits, draws)),
            "strictly_between_0_and_1": 0 < hits < draws}


def null_n2(regimes, b2):
    obs_b1 = tuple(regimes[n]["with_state_dependent_output"] > 0 for n in B1_TASKS)
    matches_b1 = 0
    total_b1 = 0
    for present in itertools.combinations(range(5), 2):
        total_b1 += 1
        vec = tuple(i in present for i in range(5))
        if vec == obs_b1:
            matches_b1 += 1
    realizable = [n for n in CFG["B2"]["tasks"] if b2[n]["terminal"] == "RECOVERED"]
    obs_b2 = tuple(bool(b2[n]["state_dependent_output"]) for n in realizable)
    matches_b2 = 0
    total_b2 = 0
    for vec in itertools.product((False, True), repeat=len(realizable)):
        total_b2 += 1
        if vec == obs_b2:
            matches_b2 += 1
    return {"B1": {"assignments": total_b1, "matching_observed": matches_b1,
                   "chance": str(Fraction(matches_b1, total_b1))},
            "B2": {"assignments": total_b2, "matching_observed": matches_b2,
                   "chance": str(Fraction(matches_b2, total_b2)),
                   "realizable_regimes": realizable},
            "joint_chance": str(Fraction(matches_b1, total_b1) * Fraction(matches_b2, total_b2))}


def null_n3(draws, seed, window=6):
    rng = random.Random(seed)
    ws = words_upto(window)
    want = [SPECS["delay2"](w) for w in ws]
    hits = 0
    for _ in range(draws):
        m = tuple(rng.choice(B2_OPTIONS) for _ in range(8))
        if b2_mismatch(m, want, ws) == 0:
            hits += 1
    return {"draws": draws, "exact_delay2_solvers": hits, "rate": str(Fraction(hits, draws))}


# ----------------------------------------------------------------------------------------
# Hostiles owned by the blind stage (H3..H6).  Each must MOVE its quantity (applicable)
# and be DETECTED by the registered check.
# ----------------------------------------------------------------------------------------


def hostiles(b1, regimes, b2, preds_b1):
    out = {}
    # H3: invert the prediction for identity.
    bad = json.loads(json.dumps(preds_b1))
    bad["identity"]["predicted_exact_solvers_with_state_dependent_output"] = "ALL"
    f = verdict_b1(regimes, bad)
    out["H3"] = {"planted": "prediction for identity inverted to ALL",
                 "applicable": bad != preds_b1, "detected": len(f) > 0,
                 "verdict_under_hostile": "FALSIFIED" if f else "CONFIRMED", "failures": f}
    # H4: budget 1 for delay2.
    r = s1_search("delay2", CFG["B2"]["search_S1"]["seed"], 1, 1)
    out["H4"] = {"planted": "S1 budget 1 on delay2",
                 "applicable": b2["delay2"]["terminal"] == "RECOVERED",
                 "detected": r["terminal"] == "NOT_RECOVERED_AT_SCOPE",
                 "terminal_under_hostile": r["terminal"], "evaluations": r["evaluations"]}
    # H5: evaluation window truncated to words of length <= 1.
    cs = b1["candidates"]
    ws1 = words_upto(1)
    spurious = [i for i, c in enumerate(cs) if all(run_table(b1_table(c), w) == SPECS["delay1"](w) for w in ws1)]
    genuine = regimes["delay1"]["exact_solvers"]
    # the registered check: every claimed solver must be exact on the full window
    ws4 = words_upto(4)
    rejected = [i for i in spurious if not all(run_table(b1_table(cs[i]), w) == SPECS["delay1"](w) for w in ws4)]
    out["H5"] = {"planted": "delay1 evaluated on words of length <= 1 only",
                 "applicable": len(spurious) > genuine,
                 "detected": len(rejected) == len(spurious) - genuine and len(rejected) > 0,
                 "claimed_solvers_under_hostile": len(spurious), "genuine": genuine,
                 "rejected_by_full_window_check": len(rejected)}
    # H6: perturb one atlas row.
    atlas = json.loads(json.dumps(b1["atlas"]))
    atlas["rows"][7]["development_distance_from_S00"] += 1
    d = hashlib.sha256(json.dumps(atlas, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    out["H6"] = {"planted": "row M007 development distance +1",
                 "applicable": d != b1["digest"],
                 "detected": d != CFG["B1"]["aj11_atlas_sha256_expected"],
                 "digest_under_hostile": d}
    return out


# ----------------------------------------------------------------------------------------
# Main.
# ----------------------------------------------------------------------------------------


def git_commit_time(sha):
    import subprocess
    git = "/usr/bin/git" if os.path.exists("/usr/bin/git") else "git"
    root = os.path.dirname(os.path.dirname(HERE))
    p = subprocess.Popen([git, "-C", root, "log", "-1", "--format=%ci", sha],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o, _ = p.communicate()
    return o.decode("utf-8").strip() if p.returncode == 0 else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "BLIND_OUTCOME_V1.json"))
    args = ap.parse_args(argv)

    b1 = build_b1(CFG["B1"]["evaluation_window_max_word_length"])
    assert len(b1["candidates"]) == 260
    regimes = b1_regimes(b1)
    b2 = run_b2()
    preds_b1 = CFG["regime_predictions_operational_vocabulary"]["B1"]
    preds_b2 = CFG["regime_predictions_operational_vocabulary"]["B2"]
    f1 = verdict_b1(regimes, preds_b1)
    f2 = verdict_b2(b2, preds_b2)
    hs = hostiles(b1, regimes, b2, preds_b1)
    nulls = {"N1": null_n1(CFG["nulls"]["N1"]["draws"], CFG["nulls"]["N1"]["seed"]),
             "N2": null_n2(regimes, b2),
             "N3": null_n3(CFG["nulls"]["N3"]["draws"], CFG["nulls"]["N3"]["seed"])}
    problems = list(f1) + list(f2)
    for hid, h in hs.items():
        if not h["applicable"]:
            problems.append("%s: hostile cannot move its quantity (vacuous)" % hid)
        if not h["detected"]:
            problems.append("%s: hostile not detected" % hid)
    if b1["digest"] != CFG["B1"]["aj11_atlas_sha256_expected"]:
        problems.append("atlas digest drift: %s" % b1["digest"])
    if not nulls["N1"]["strictly_between_0_and_1"]:
        problems.append("N1 null is degenerate")
    if nulls["N3"]["exact_delay2_solvers"] != 0:
        problems.append("N3 null found chance solvers")

    universe_commit = "83d79b44f6ac78d71e781a995224c06a165e4591"
    registry_freeze_commit = "aec01b0e4208a6e03423e5c6c020b1cddc43a5e4"
    out = {
        "schema": "AJ15_BLIND_OUTCOME_V1",
        "stage": "BLIND",
        "registry_read": False,
        "family_labels_used": False,
        "config_sha256": hashlib.sha256(_read_bytes(os.path.join(HERE, "SEARCH_CONFIG_V1.json"))).hexdigest(),
        "universe_provenance": {
            "B1_constructed_in": "gmi-833-aj4-process-organizations-v1",
            "B1_construction_commit": universe_commit,
            "B1_construction_time": git_commit_time(universe_commit),
            "registry_freeze_commit": registry_freeze_commit,
            "registry_freeze_time": git_commit_time(registry_freeze_commit),
        },
        "B1": {
            "presentations": len(b1["candidates"]),
            "operational_classes": len(b1["groups"]),
            "pair_checks": b1["pair_checks"],
            "equivalent_pairs": b1["equivalent_pairs"],
            "class_size_histogram": {str(k): v for k, v in sorted(Counter(len(g) for g in b1["groups"].values()).items())},
            "development_all_reachable": True,
            "development_max_distance": max(b1["dist"]),
            "pareto_front": ["M%03d" % i for i in b1["front"]],
            "atlas_sha256": b1["digest"],
            "evaluation_window": CFG["B1"]["evaluation_window_max_word_length"],
            "regimes": regimes,
            "prediction_failures": f1,
            "verdict": "FALSIFIED" if f1 else "CONFIRMED",
        },
        "B2": {
            "presentations": 8 ** 8,
            "enumerated": False,
            "search": "S1",
            "regimes": b2,
            "prediction_failures": f2,
            "verdict": "FALSIFIED" if f2 else "CONFIRMED",
        },
        "hostiles": hs,
        "nulls": nulls,
        "problems": problems,
        "verdict": "FALSIFIED" if (f1 or f2) else ("RED" if problems else "CONFIRMED"),
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"verdict": out["verdict"], "problems": problems,
                      "B1": {n: (r["with_state_dependent_output"], r["exact_solvers"]) for n, r in regimes.items()},
                      "B2": {n: (r["terminal"], r["evaluations"]) for n, r in b2.items()},
                      "digest": b1["digest"][:16]}, sort_keys=True))
    return 0 if out["verdict"] == "CONFIRMED" else 1


if __name__ == "__main__":
    sys.exit(main())
