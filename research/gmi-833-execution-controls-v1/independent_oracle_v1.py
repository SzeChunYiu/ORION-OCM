#!/usr/bin/env python3
"""Route B: a source-separated oracle for #859 (freeze 3682a045).

Imports nothing from route A (robustness_record_v1, substrate_v1,
encoding_e2_v1, search_procedures_v1, execution_controls_v1), nothing from the
#901 code and nothing from the #855 code.  The frozen case grid is parsed from
the text of the #901 FREEZE_V1.md table.  Every fact is recomputed by its own
simulation, its own search procedures, its own Pareto/scalarization code, its
own reading of the E2 rule-list syntax, and its own statement of the five
admission conditions; the result is written to ORACLE_RESULT_V1.json, whose
`shared_facts` must equal route A's.

Usage: python3 -I -B independent_oracle_v1.py [--check]
"""
from __future__ import annotations

from fractions import Fraction as Q
from math import gcd
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
FREEZE_901 = HERE.parent / "gmi-833-heldout-20-transitions-v1" / "FREEZE_V1.md"
OUT = "ORACLE_RESULT_V1.json"
SEQS = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
COORDS = ["candidate_count", "primitive_envelope", "non_k_operator_inventory", "evaluator_id", "sequence_set",
          "budget", "tie_rule", "stopping_rule", "representable_k_free_behaviour_set"]
ST, PS = "STATELESS", "PERSISTENT_STATE"
# the #855 denylist registered by #859 for this substrate (data, not code)
DENYLIST = ["recurrent", "persistent_state", "stateless", "delay_line", "lstm_gate", "gru_cell", "rnn_cell", "shift_register"]


def dumps_pretty(x) -> str:
    return json.dumps(x, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pid(s, en, ed) -> str:
    return "s%sn%sd%s" % (s, en, ed)


# ---------------------------------------------------------------- frozen cases
def frozen_cases():
    rows = []
    for line in FREEZE_901.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*([0-9/]+)\s*\|\s*([0-9/]+)\s*\|\s*([0-9/]+)\s*\|\s*([0-9/]+)\s*\|\s*([0-9/]+)\s*\|", line)
        if m:
            rows.append(tuple([int(m.group(1))] + [Q(m.group(k)) for k in range(2, 7)]))
    if [r[0] for r in rows] != list(range(1, 21)):
        raise SystemExit("cannot parse the 20 frozen #901 cases")
    return rows


CASES = frozen_cases()
WORLDS = []
for cid, p, eta, thr, lo, hi in CASES:
    for kind, lam in (("low", lo), ("high", hi), ("boundary", thr)):
        WORLDS.append(("c%02d_%s" % (cid, kind), cid, kind, p, eta, lam))
WIDS = [w[0] for w in WORLDS]


def weights(w, n=16):
    _, _, _, p, eta, lam = w
    return (eta * (1 - p) / n, eta * p / n, lam)


# ---------------------------------------------------------------- simulation
def sim_stateless(table, seqs, targets, prev_macro=False):
    now = lag = 0
    sig = []
    for mode in (0, 1):
        for seq in seqs:
            for t in (1, 2):
                idx = 2 * mode + (seq[t - 1] if (prev_macro and mode == 1) else seq[t])
                y = (table >> idx) & 1
                sig.append(y)
                want = seq[t] if targets[mode] == "C" else seq[t - 1]
                if y != want:
                    if mode == 0:
                        now += 1
                    else:
                        lag += 1
    return now, lag, tuple(sig)


def census(seqs=SEQS, targets=("C", "P"), ablate=False, stateful=True, prev_macro=False):
    """Candidates in #901 order: (id, s, en, ed, k, sig-or-None)."""
    out = []
    for table in range(16):
        en, ed, sig = sim_stateless(table, seqs, targets, prev_macro)
        out.append(("q%05d" % table, 0, en, ed, False, sig))
    if not stateful:
        return out
    for nxt in range(256):
        nu = 0 if ablate else nxt
        k = nu not in (0, 255)
        visits = []   # (mode, address, target-bit) per scored step, straight simulation
        for mode in (0, 1):
            for seq in seqs:
                s = 0
                for t in range(3):
                    x = seq[t]
                    a = 4 * s + 2 * mode + x
                    if t:
                        visits.append((mode, a, x if targets[mode] == "C" else seq[t - 1]))
                    s = (nu >> a) & 1
        for o in range(256):
            en = ed = 0
            for mode, a, want in visits:
                if ((o >> a) & 1) != want:
                    if mode:
                        ed += 1
                    else:
                        en += 1
            sig = None if k else tuple((o >> a) & 1 for _, a, _ in visits)
            out.append(("q%05d" % (16 + nxt * 256 + o), 1, en, ed, k, sig))
    return out


def hist(c):
    h = {}
    for x in c:
        key = (x[1], x[2], x[3])
        h[key] = h.get(key, 0) + 1
    return dict(sorted(h.items()))


def argmin(h, wt):
    a, b, c = wt
    vals = {r: a * r[1] + b * r[2] + c * r[0] for r in h}
    lo = min(vals.values())
    win = sorted(r for r, v in vals.items() if v == lo)
    return lo, win, sorted({PS if r[0] else ST for r in win})


def kfree_mult(c):
    m = {}
    for x in c:
        if not x[4]:
            m[x[5]] = m.get(x[5], 0) + 1
    return {"classes": len(m), "min_per_class": min(m.values()), "max_per_class": max(m.values()), "total_k_free": sum(m.values())}


# ---------------------------------------------------------------- E2, read from its registered syntax
def e2_census(scale=Q(1)):
    """Own interpreter for the registered E2 syntax: Gray-ordered rule lists over
    states P/R, modes U/V, data a/b; address bit2 = mode, bit1 = state, bit0 = input;
    rule-list index j -> Gray code; surface id W + base-26(j); stateful block first."""
    g = lambda n: n ^ (n >> 1)
    addr3 = [g(i) for i in range(8)]
    addr2 = [g(i) for i in range(4)]
    words = [(a, b, c) for a in "ab" for b in "ab" for c in "ab"]

    def wid(j):
        s = ""
        for _ in range(4):
            s = chr(65 + j % 26) + s
            j //= 26
        return "W" + s

    def rules3(code, alpha):
        return {("PR"[(addr3[i] >> 1) & 1], "UV"[(addr3[i] >> 2) & 1], "ab"[addr3[i] & 1]): alpha[(code >> i) & 1] for i in range(8)}

    emits = [rules3(g(lo), "ab") for lo in range(256)]
    out = {}
    for hi in range(256):
        step = rules3(g(hi), "PR")
        for lo in range(256):
            em = emits[lo]
            u = v = 0
            for mode in "UV":
                for w in words:
                    st = "P"
                    for t in range(3):
                        key = (st, mode, w[t])
                        if t and em[key] != (w[t] if mode == "U" else w[t - 1]):
                            if mode == "U":
                                u += 1
                            else:
                                v += 1
                        st = step[key]
            out[wid(hi * 256 + lo)] = (1, Q(u), Q(v) * scale)
    for k in range(16):
        em = {("UV"[(addr2[i] >> 1) & 1], "ab"[addr2[i] & 1]): "ab"[(g(k) >> i) & 1] for i in range(4)}
        u = v = 0
        for mode in "UV":
            for w in words:
                for t in (1, 2):
                    if em[(mode, w[t])] != (w[t] if mode == "U" else w[t - 1]):
                        if mode == "U":
                            u += 1
                        else:
                            v += 1
        out[wid(65536 + k)] = (0, Q(u), Q(v) * scale)
    return out


# ---------------------------------------------------------------- searches
def s2_order(points, price):
    return sorted(points, key=lambda r: (price * r[0], r[1] + r[2], r[0], r[1], r[2]))


def value(r, wt):
    return wt[0] * r[1] + wt[1] * r[2] + wt[2] * r[0]


def s1_letters(order, wt):
    """S1 acceptance letters over the full census, with exact values scaled to integers."""
    vals = {r: value(r, wt) for r in set(order)}
    scale = 1
    for v in vals.values():
        scale = scale * v.denominator // gcd(scale, v.denominator)
    ints = {r: int(v * scale) for r, v in vals.items()}
    best, acc, win = None, [], []
    for r in order:
        v = ints[r]
        if best is None or v < best:
            best, win = v, [r]
            acc.append("N")
        elif v == best:
            win.append(r)
            acc.append("T")
        else:
            acc.append("R")
    return Q(best, scale), win, acc


def run(order, wt, prune=None, stop=None):
    best, trace, acc, win = None, [], [], []
    for r in order:
        if stop is not None and best is not None and stop(r) > best:
            break
        if prune is not None and best is not None and prune(r) > best:
            continue
        v = value(r, wt)
        trace.append(r)
        if best is None or v < best:
            best, win = v, [r]
            acc.append("N")
        elif v == best:
            win.append(r)
            acc.append("T")
        else:
            acc.append("R")
    return best, win, trace, acc


def tdig(trace):
    return hashlib.sha256(json.dumps([list(r) for r in trace], separators=(",", ":")).encode("ascii")).hexdigest()[:16]


def adig(acc):
    return hashlib.sha256("".join(acc).encode("ascii")).hexdigest()[:16]


def dominated(u, v):
    return all(a <= b for a, b in zip(u, v)) and u != v


# ---------------------------------------------------------------- the oracle
def build():
    checks = {}
    gp = census()
    gm = census(ablate=True)
    ge = census(targets=("C", "C"))
    h1a = census(stateful=False)
    h1b = census(ablate=True, prev_macro=True)
    half = [s for s in SEQS if s[0] == 0]
    h1c = census(seqs=half, ablate=True)
    H = hist(gp)
    checks["census_65552"] = len(gp) == 65552
    checks["risk_points_146"] = len(H) == 146
    checks["stateless_delay_floor_8"] = min(x[3] for x in gp if x[1] == 0) == 8

    # descriptors, own representation (coordinate-by-coordinate equality)
    ops_sl, ops_prev = {"OUT", "IN", "MODE"}, {"OUT", "IN", "MODE", "PREV"}
    ops_sf = {"NEXT", "OUT", "IN", "MODE", "REG_R", "REG_W"}

    def desc(c, seqs, stateful, prev, budget, targets="CP"):
        n = 2 * len(seqs)
        env = {"sl": 16}
        if stateful:
            env["sf"] = 65536
        return {"candidate_count": len(c), "primitive_envelope": env,
                "non_k_operator_inventory": (ops_prev if prev else ops_sl) | (ops_sf if stateful else set()),
                "evaluator_id": ("targets", targets, "normalizer", n), "sequence_set": set(seqs), "budget": budget,
                "tie_rule": "all", "stopping_rule": "exhaustive",
                "representable_k_free_behaviour_set": {x[5] for x in c if not x[4]}}

    dplus = desc(gp, SEQS, True, False, 65552)
    twins = {"G_MINUS": desc(gm, SEQS, True, False, 65552),
             "H1A_CAPACITY_DELETE_STATEFUL": desc(h1a, SEQS, False, False, 16),
             "H1B_MACRO_PREV": desc(h1b, SEQS, True, True, 65552),
             "H1C_HALVED_SEQUENCE_SET": desc(h1c, half, True, False, 65552),
             "H1D_HALVED_BUDGET": desc(gm, SEQS, True, False, 65552 // 2)}
    census_of = {"G_MINUS": gm, "H1A_CAPACITY_DELETE_STATEFUL": h1a, "H1B_MACRO_PREV": h1b,
                 "H1C_HALVED_SEQUENCE_SET": h1c, "H1D_HALVED_BUDGET": gm}
    per_mode = {"H1C_HALVED_SEQUENCE_SET": 8}
    mism = {k: [c for c in COORDS if dplus[c] != d[c]] for k, d in twins.items()}
    ktarget = {k: any(Q(x[3], per_mode.get(k, 16)) < Q(1, 2) for x in census_of[k]) for k in twins}
    kcount = {k: sum(1 for x in census_of[k] if x[4]) for k in twins}
    ops_added = {k: bool(twins[k]["non_k_operator_inventory"] - dplus["non_k_operator_inventory"]) for k in twins}

    outs = {}
    for name, c, n in (("G_PLUS", gp, 16), ("G_MINUS", gm, 16), ("E_MINUS", ge, 16),
                       ("H1A_CAPACITY_DELETE_STATEFUL", h1a, 16), ("H1B_MACRO_PREV", h1b, 16)):
        hc = hist(c)
        outs[name] = {w[0]: argmin(hc, weights(w, n)) for w in WORLDS}
    claim = {}
    for w in WORLDS:
        _, _, _, p, eta, lam = w
        thr = eta * p / 2
        claim[w[0]] = [PS] if lam < thr else ([ST] if lam > thr else [PS, ST])
    checks["phase_law_20_transitions"] = all(outs["G_PLUS"][w] [2] == claim[w] for w in WIDS)
    checks["matched_twin_all_stateless"] = all(outs["G_MINUS"][w][2] == [ST] for w in WIDS)

    # E2 (own interpreter) against E1 (own simulation) through the registered layout
    e2 = e2_census()
    e2h = {}
    for r in e2.values():
        e2h[r] = e2h.get(r, 0) + 1
    checks["e2_histogram_equals_e1"] = {(a, int(b), int(c)): m for (a, b, c), m in e2h.items()} == H
    # per-candidate check through the registered layout map E1 index -> E2 index
    def ginv(g):
        n = 0
        while g:
            n ^= g
            g >>= 1
        return n
    ga3 = [i ^ (i >> 1) for i in range(8)]
    ga2 = [i ^ (i >> 1) for i in range(4)]
    def code3(t):
        return sum((((t >> (4 * ((a >> 1) & 1) + 2 * ((a >> 2) & 1) + (a & 1))) & 1) << k) for k, a in enumerate(ga3))
    def e2_index(i):
        if i < 16:
            return 65536 + ginv(sum((((i >> a) & 1) << k) for k, a in enumerate(ga2)))
        return ginv(code3((i - 16) >> 8)) * 256 + ginv(code3((i - 16) & 255))
    def wid(j):
        out = ""
        for _ in range(4):
            out = chr(65 + j % 26) + out
            j //= 26
        return "W" + out
    image = [wid(e2_index(i)) for i in range(len(gp))]
    per_candidate_mismatch = sum(1 for i, x in enumerate(gp) if e2.get(image[i]) != (x[1], x[2], x[3]))
    checks["e2_bijective_and_per_candidate_equal"] = len(set(image)) == len(gp) == len(e2) and set(image) == set(e2) and per_candidate_mismatch == 0
    pm_h2b = sum(1 for x in gp if x[3] != 0)   # a 15/16 delay rescale moves exactly the ed>0 candidates
    h2a_census = len(e2) - 1                  # H2a: the alleged encoding silently drops one candidate

    # Pareto and scalarizations
    vec = {pid(*r): (Q(r[1]), Q(r[2]), Q(r[0])) for r in H}
    front = sorted(k for k in vec if not any(dominated(vec[j], vec[k]) for j in vec if j != k))
    scal = {}
    for w in WORLDS:
        if (w[2] != "boundary" and w[1] <= 15) or w[2] == "boundary":
            wt = weights(w)
            vals = {k: sum(x * y for x, y in zip(wt, v)) for k, v in vec.items()}
            lo = min(vals.values())
            scal[w[0]] = sorted(k for k, v in vals.items() if v == lo)
    positive = [w for w in WORLDS if w[2] != "boundary" and w[1] <= 15]
    reversal = len({tuple(sorted({PS if vec[k][2] else ST for k in scal[w[0]]})) for w in positive}) > 1
    checks["pareto_two_points"] = front == ["s0n0d8", "s1n0d0"]
    checks["positive_winners_on_frontier"] = all(k in front for w in positive for k in scal[w[0]])

    # searches (own implementations of the declared procedures)
    pts = sorted(H)
    order = [(x[1], x[2], x[3]) for x in gp]
    s1d = tdig(order)
    trace, acc, conc = {}, {}, {}
    for k in ("S1_FULL_ENUMERATION", "S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE",
              "H3A_FIRST_ACCEPT_PRICE_SORTED", "H3B_REENCODED_BRANCH_BOUND"):
        trace[k], acc[k], conc[k] = {}, {}, {}
    for w in WORLDS:
        wt = weights(w)
        b1, w1, a1 = s1_letters(order, wt)
        b2, w2, t2, a2 = run(s2_order(pts, wt[2]), wt, prune=lambda r: wt[2] * r[0])
        lb3 = lambda r: wt[1] * r[2] + wt[2] * r[0]
        b3, w3, t3, a3 = run(sorted(pts, key=lambda r: (lb3(r), r)), wt, stop=lb3)
        first = s2_order(pts, wt[2])[0]
        for k, t, a, b, win in (("S1_FULL_ENUMERATION", None, a1, b1, w1), ("S2_RISK_FRONTIER_BRANCH_BOUND", t2, a2, b2, w2),
                                ("S3_BEST_FIRST_CERTIFICATE", t3, a3, b3, w3), ("H3A_FIRST_ACCEPT_PRICE_SORTED", [first], ["N"], value(first, wt), [first]),
                                ("H3B_REENCODED_BRANCH_BOUND", t2, a2, b2, w2)):
            if t is not None:
                trace[k][w[0]] = tdig(t)
            acc[k][w[0]] = adig(a)
            conc[k][w[0]] = (b, sorted({PS if r[0] else ST for r in win}))
    agree = all(conc[k][w] == conc["S1_FULL_ENUMERATION"][w] and conc[k][w][1] == claim[w]
                for k in ("S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE") for w in WIDS)
    s2_s3_distinct = any(trace["S2_RISK_FRONTIER_BRANCH_BOUND"][w] != trace["S3_BEST_FIRST_CERTIFICATE"][w] for w in WIDS)
    h3a_disagrees = any(conc["H3A_FIRST_ACCEPT_PRICE_SORTED"][w][1] != claim[w] for w in WIDS)
    h3b_reencoding = all(trace["H3B_REENCODED_BRANCH_BOUND"][w] == trace["S2_RISK_FRONTIER_BRANCH_BOUND"][w] for w in WIDS)
    checks["searchers_agree_with_claim"] = agree and s2_s3_distinct

    # lexicographic surface rule (H2c): E1 ids q..., E2 ids W... with the stateful block first
    lex_differs = 0
    for w in WORLDS:
        wt = weights(w)
        _, win, props = argmin(H, wt)
        e1_first = min(x[0] for x in gp if (x[1], x[2], x[3]) in win)
        e1_prop = ST if int(e1_first[1:]) < 16 else PS
        e2_prop = PS if any(r[0] == 1 for r in win) else ST
        lex_differs += int(e1_prop != e2_prop)

    # perturbation control (own implementation)
    tables = [H, H, {(a, int(b), int(c)): m for (a, b, c), m in e2h.items()}]
    perturbed = excluded = stable = ties = flips = 0
    for w in WORLDS:
        if w[2] == "boundary":
            continue
        _, _, _, p, eta, lam = w
        thr = eta * p / 2
        m = abs(lam - thr)
        base = argmin(H, weights(w))[2]
        for d0 in (-m / 2, Q(0), m / 2):
            for d1 in (-m / 2, Q(0), m / 2):
                for d2 in (-m / 2, Q(0), m / 2):
                    wn, wd, pr = eta * (1 - p) + d0, eta * p + d1, lam + d2
                    if wn < 0 or wd <= 0 or pr <= 0:
                        excluded += 1
                        continue
                    perturbed += 1
                    stable += int(all(argmin(t, (wn / 16, wd / 16, pr))[2] == base for t in tables))
        ties += int(all(argmin(t, (eta * (1 - p) / 16, eta * p / 16, thr))[2] == [PS, ST] for t in tables))
        flip = [ST] if base == [PS] else [PS]
        flips += int(all(argmin(t, (eta * (1 - p) / 16, eta * p / 16, 2 * thr - lam))[2] == flip for t in tables))
    checks["perturbation_stable_and_flips"] = stable == perturbed and ties == 40 and flips == 40

    # admission census: the five conditions restated from the facts above
    deny = [re.sub(r"[^a-z0-9]", "", d.lower()) for d in DENYLIST]
    q_ids = [x[0] for x in gp]
    arm_ids = {"G_PLUS": q_ids, "G_MINUS": q_ids, "E_MINUS": q_ids, "H1A_CAPACITY_DELETE_STATEFUL": q_ids[:16],
               "H1B_MACRO_PREV": q_ids, "H1C_HALVED_SEQUENCE_SET": q_ids, "H1D_HALVED_BUDGET": q_ids,
               "G_PLUS_E2": sorted(e2), "G_PLUS_E2_H2B": sorted(e2),
               "G_MINUS_LEAKY_SURFACE_IDS": ["stateless_" + i for i in q_ids], "G_MINUS_UNDISCLOSED_EVALUATION": q_ids}
    hidden_state_ops = {"H1B_MACRO_PREV"}            # the READ_PREV primitive carries unpriced hidden state
    undisclosed = {"G_MINUS_UNDISCLOSED_EVALUATION"}  # the registered hostile omits its evaluation disclosure
    ns = {}
    for arm, ids in arm_ids.items():
        leak = any(d in re.sub(r"[^a-z0-9]", "", i.lower()) for i in ids for d in deny)
        ns[arm] = "UNEVALUABLE" if arm in undisclosed else ("LEAK" if leak or arm in hidden_state_ops else "OK")
    checks["no_smuggling_registered_arms_clean_or_routed"] = all(ns[a] == "OK" for a in ("G_PLUS", "G_MINUS", "E_MINUS", "G_PLUS_E2"))
    ok_twin = {k: not mism[k] and kcount[k] == 0 and not ktarget[k] and not ops_added[k] for k in twins}
    outcome_differs = any(outs["G_PLUS"][w][2] != outs["G_MINUS"][w][2] for w in WIDS)

    search_ok = "OK" if agree and s2_s3_distinct else "SEARCH_SENSITIVE"
    scal_ok = "OK" if all(sorted({PS if vec[k][2] else ST for k in scal[w]}) == claim[w] for w in scal) else "PRICE_CONDITIONAL_CLAIM_CONTRADICTED"
    enc_ok = "OK" if checks["e2_bijective_and_per_candidate_equal"] else "ENCODING_NOT_SEMANTICALLY_EQUIVALENT"
    k_realized = any(r[2] < 8 for w in WIDS for r in outs["G_PLUS"][w][1])

    def verdict(twin="G_MINUS", twin_arm=None, enc=None, search=None, scal=None, arms=(), missing=()):
        twin_arm = twin_arm or twin
        enc = enc_ok if enc is None else enc
        search = search_ok if search is None else search
        scal = scal_ok if scal is None else scal
        fails = []
        if "MATCHED_TWIN" in missing:
            fails.append(("MATCHED_TWIN", "CONTROL_MISSING"))
        elif not ok_twin[twin]:
            fails.append(("MATCHED_TWIN", "UNMATCHED_MECHANISM_TWIN"))
        elif "NO_SMUGGLING" in missing or ns[twin_arm] == "UNEVALUABLE":
            fails.append(("MATCHED_TWIN", "TWIN_AUDIT_NOT_EVALUABLE"))
        elif not (outcome_differs and k_realized):
            fails.append(("MATCHED_TWIN", "TWIN_INTERPRETATION_UNSUPPORTED"))
        if "ENCODING" in missing:
            fails.append(("ENCODING", "CONTROL_MISSING"))
        elif enc != "OK":
            fails.append(("ENCODING", enc))
        if "SEARCH" in missing:
            fails.append(("SEARCH", "CONTROL_MISSING"))
        elif search != "OK":
            fails.append(("SEARCH", search))
        if "SCALARIZATION" in missing:
            fails.append(("SCALARIZATION", "CONTROL_MISSING"))
        elif scal != "OK":
            fails.append(("SCALARIZATION", scal))
        all_arms = ["G_PLUS", "G_MINUS", "E_MINUS", "G_PLUS_E2", twin_arm] + list(arms)
        if "NO_SMUGGLING" in missing:
            fails.append(("NO_SMUGGLING", "CONTROL_MISSING"))
        elif any(ns[a] != "OK" for a in all_arms):
            fails.append(("NO_SMUGGLING", "NO_SMUGGLING_NOT_CLEAN"))
        if not fails:
            return ["ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE", []]
        miss = [c for c, t in fails if t == "CONTROL_MISSING"]
        return ["CANNOT_ESTABLISH_D_ROBUSTNESS_" + (miss[0] if miss else fails[0][0]), [[c, t] for c, t in fails]]

    enc_h2a = "ENCODING_NOT_SEMANTICALLY_EQUIVALENT" if h2a_census != len(gp) else "OK"
    enc_h2b = "ENCODING_NOT_SEMANTICALLY_EQUIVALENT" if pm_h2b > 0 else "OK"
    enc_h2c = "ENCODING_SENSITIVE" if lex_differs else "OK"
    s_h3a = "SEARCH_SENSITIVE" if h3a_disagrees else "OK"
    s_h3b = "SEARCHERS_NOT_MATERIALLY_DISTINCT" if h3b_reencoding else "OK"
    sc_univ = "SCALARIZATION_SENSITIVE" if reversal else "OK"
    adm = {
        "GMI859_POSITIVE_WITNESS_901_FAMILY": verdict(),
        "DELETE_MATCHED_TWIN": verdict(missing=("MATCHED_TWIN",)),
        "DELETE_ENCODING": verdict(missing=("ENCODING",)),
        "DELETE_SEARCH": verdict(missing=("SEARCH",)),
        "DELETE_SCALARIZATION": verdict(missing=("SCALARIZATION",)),
        "DELETE_NO_SMUGGLING": verdict(missing=("NO_SMUGGLING",)),
        "H1A_CAPACITY": verdict(twin="H1A_CAPACITY_DELETE_STATEFUL"),
        "H1B_MACRO": verdict(twin="H1B_MACRO_PREV"),
        "H1C_SEQUENCES": verdict(twin="H1C_HALVED_SEQUENCE_SET"),
        "H1D_BUDGET": verdict(twin="H1D_HALVED_BUDGET"),
        "C1_TWIN_VALID_ENCODING_CENSUS_BROKEN_H2A": verdict(enc=enc_h2a),
        "H2B_COST_MUTATION": verdict(enc=enc_h2b, arms=("G_PLUS_E2_H2B",)),
        "H2C_SURFACE_TIE": verdict(enc=enc_h2c),
        "H3A_EARLY_STOP": verdict(search=s_h3a),
        "C2_SEARCH_REENCODINGS_ONLY_H3B": verdict(search=s_h3b),
        "H4A_UNIVERSAL_WINNER_WORDING": verdict(scal=sc_univ),
        "C3_EMPTY_SCALARIZATION_SET": verdict(scal="SCALARIZATIONS_INSUFFICIENT"),
        "C3B_ZERO_WEIGHT_PROBES_ONLY": verdict(scal="SCALARIZATIONS_INSUFFICIENT"),
        "C4_UNCLEAN_NEGATIVE_ARM": verdict(twin_arm="G_MINUS_LEAKY_SURFACE_IDS"),
        "C5_UNEVALUABLE_NEGATIVE_ARM": verdict(twin_arm="G_MINUS_UNDISCLOSED_EVALUATION"),
        "C6_TWIN_AND_SEARCH_HOSTILE": verdict(twin="H1A_CAPACITY_DELETE_STATEFUL", search=s_h3a),
        "C7_ALL_FOUR_CONTROLS_HOSTILE": verdict(twin="H1A_CAPACITY_DELETE_STATEFUL", enc=enc_h2c, search=s_h3a, scal=sc_univ),
    }
    checks["positive_witness_robust"] = adm["GMI859_POSITIVE_WITNESS_901_FAMILY"][0] == "ROBUST_AT_REGISTERED_D_CONTROLS_SCOPE"

    shared = {
        "census": len(gp), "risk_points": len(H),
        "risk_histogram_digest": sha(dumps_pretty([[pid(*r), m] for r, m in H.items()])),
        "g_minus_risk_points": [[pid(*r), m] for r, m in hist(gm).items()],
        "k_free_multiplicity": {"G_PLUS": kfree_mult(gp), "G_MINUS": kfree_mult(gm)},
        "k_carriers_in_g_plus": sum(1 for x in gp if x[4]),
        "descriptor_mismatches": mism,
        "k_target_realizable": ktarget,
        "outcome_properties": {a: {w: outs[a][w][2] for w in WIDS} for a in outs},
        "outcome_best": {a: {w: str(outs[a][w][0]) for w in WIDS} for a in ("G_PLUS", "G_MINUS", "E_MINUS")},
        "pareto_set": front,
        "scalarization_winners": scal,
        "h3a_properties": {w: conc["H3A_FIRST_ACCEPT_PRICE_SORTED"][w][1] for w in WIDS},
        "trace_digests": {k: trace[k] for k in ("S2_RISK_FRONTIER_BRANCH_BOUND", "S3_BEST_FIRST_CERTIFICATE", "H3B_REENCODED_BRANCH_BOUND")},
        "acceptance_digests": acc,
        "s1_trace_digest": s1d,
        "perturbation": {"perturbed_worlds": perturbed, "excluded_invalid": excluded,
                         "winner_state_partition_stable_all_three_encodings": stable,
                         "exact_boundary_ties_all_three_encodings": ties,
                         "mirrored_price_flips_all_three_encodings": flips},
        "admission_census": adm,
    }
    return {"schema": "GMI833ExecutionControlsOracleV1", "issue": 859, "route": "B",
            "imports": "stdlib only; no route-A module, no #901 code, no #855 code",
            "frozen_cases_parsed_from": "research/gmi-833-heldout-20-transitions-v1/FREEZE_V1.md",
            "verdict": "GREEN" if all(checks.values()) else "RED", "checks": checks, "shared_facts": shared}


def main(argv) -> int:
    text = dumps_pretty(build())
    if "--check" in argv:
        same = (HERE / OUT).read_text(encoding="utf-8") == text
        print("oracle receipt byte-identical" if same else "DRIFT: " + OUT)
        return 0 if same else 1
    (HERE / OUT).write_text(text, encoding="utf-8")
    print("%s verdict=%s sha256=%s" % (OUT, json.loads(text)["verdict"], sha(text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
