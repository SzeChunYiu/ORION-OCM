"""Route B -- independent oracle for #833 Section Z, subsection Z3.

Route B uses three constructions that route A does not:

1. error counts come from a per-index **occupancy** recurrence over
   (state, previous symbol, current symbol) -- no input word is ever replayed;
2. behavioural statelessness is decided by a **reachability closure** on the
   state machine: a machine is behaviourally stateless exactly when, for each
   mode and each current symbol, the output is constant over every state the
   machine can occupy at a scored position;
3. behavioural traces, where needed, come from a level-by-level prefix-to-state
   dynamic program over prefix integers rather than from sequence replay.

It imports nothing from route A and nothing from the Z5, Z7, Z12 or Z15 packages.

Run:  python3 -I -B independent_invariance_oracle_v1.py
"""
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")

STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"
L = 3
N = (L - 1) * (2 ** L)
SCALE_LADDER = ("1/7", "1/2", "2", "3", "11/5", "100")


def fs(x):
    return str(Fraction(x))


# ------------------------------------------------------- occupancy recurrence
def occupancy(nxt, mode):
    """Exact number of scored moments (t >= 1) at each (state, prev, cur)."""
    occ = {}
    cfg = {(0, -1, 0): 2 ** (L - 1), (0, -1, 1): 2 ** (L - 1)}
    for t in range(L):
        new = {}
        for key in cfg:
            st, prev, cur = key
            mult = cfg[key]
            if t >= 1:
                occ[key] = occ.get(key, 0) + mult
            ns = (nxt >> (4 * st + 2 * mode + cur)) & 1
            if t + 1 < L:
                half = mult // 2
                for nc in (0, 1):
                    k2 = (ns, cur, nc)
                    new[k2] = new.get(k2, 0) + half
        cfg = new
    return occ


def errors(occ, table, mode):
    e = 0
    for key in occ:
        st, prev, cur = key
        out = (table >> (4 * st + 2 * mode + cur)) & 1
        want = cur if mode == 0 else prev
        if out != want:
            e += occ[key]
    return e


def stateless_errors(table, mode):
    per = (L - 1) * (2 ** (L - 2))
    e = 0
    for cur in (0, 1):
        out = (table >> (2 * mode + cur)) & 1
        for prev in (0, 1):
            want = cur if mode == 0 else prev
            if out != want:
                e += per
    return e


# ------------------------------------------------------- reachability closure
def reachable_states(nxt, mode):
    """Every state the machine can occupy at a position t in 0..L-1."""
    seen = set([0])
    layer = set([0])
    for _t in range(L - 1):
        nl = set()
        for st in layer:
            for c in (0, 1):
                nl.add((nxt >> (4 * st + 2 * mode + c)) & 1)
        layer = nl
        seen |= nl
    return seen


def behaviourally_stateless(nxt, table):
    """Constant output over every occupiable state, for each (mode, cur)."""
    for mode in (0, 1):
        R = reachable_states(nxt, mode)
        for cur in (0, 1):
            vals = set([(table >> (4 * st + 2 * mode + cur)) & 1 for st in R])
            if len(vals) != 1:
                return False
    return True


# --------------------------------------------- prefix DP for behavioural class
def trace_key(nxt, table):
    """Level-by-level prefix-to-state DP; the class key is the resulting output
    array, obtained without replaying any sequence."""
    parts = []
    for mode in (0, 1):
        states = [0]                      # state after the empty prefix
        for t in range(L):
            outs = []
            nxt_states = []
            for pi, st in enumerate(states):
                for c in (0, 1):
                    outs.append((table >> (4 * st + 2 * mode + c)) & 1)
                    nxt_states.append((nxt >> (4 * st + 2 * mode + c)) & 1)
            parts.append(tuple(outs))
            states = nxt_states
    return tuple(parts)


def stateless_trace_key(table):
    parts = []
    for mode in (0, 1):
        width = 1
        for t in range(L):
            outs = []
            for _pi in range(width):
                for c in (0, 1):
                    outs.append((table >> (2 * mode + c)) & 1)
            parts.append(tuple(outs))
            width *= 2
    return tuple(parts)


def load_worlds():
    with open(TRANS) as fh:
        doc = json.load(fh)
    out = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            out.append({"case": case["case"], "tag": tag, "p": p, "eta": eta, "lam": lam})
    return out


def argmin_classes(counts, p, eta, lam):
    best = None
    classes = set()
    for (bits, e0, e1) in counts:
        v = eta * ((1 - p) * Fraction(e0, N) + p * Fraction(e1, N)) + lam * bits
        if best is None or v < best:
            best = v
            classes = set([STATELESS if bits == 0 else PERSISTENT])
        elif v == best:
            classes.add(STATELESS if bits == 0 else PERSISTENT)
    return best, frozenset(classes)


def io_conjugate(nxt, table):
    nn = 0
    nt = 0
    for st in (0, 1):
        for m in (0, 1):
            for c in (0, 1):
                src = 4 * st + 2 * m + (1 - c)
                dst = 4 * st + 2 * m + c
                if 1 - ((table >> src) & 1):
                    nt |= 1 << dst
                if (nxt >> src) & 1:
                    nn |= 1 << dst
    return nn, nt


def io_conjugate_stateless(table):
    nt = 0
    for m in (0, 1):
        for c in (0, 1):
            if 1 - ((table >> (2 * m + (1 - c))) & 1):
                nt |= 1 << (2 * m + c)
    return nt


def main():
    worlds = load_worlds()
    # universe
    sl = []
    for table in range(16):
        sl.append((0, None, table, stateless_errors(table, 0), stateless_errors(table, 1)))
    sf = []
    bs_flags = {}
    for nxt in range(256):
        o0 = occupancy(nxt, 0)
        o1 = occupancy(nxt, 1)
        for table in range(256):
            sf.append((1, nxt, table, errors(o0, table, 0), errors(o1, table, 1)))
            bs_flags[(nxt, table)] = behaviourally_stateless(nxt, table)
    uni = sl + sf

    counts = {}
    for r in uni:
        k = (r[0], r[3], r[4])
        counts[k] = counts.get(k, 0) + 1

    rep = {"schema": "GMI_833_Z3_INVARIANCE_ORACLE_V1",
           "route": "B_occupancy_reachability_prefixDP", "imports_route_a": False,
           "universe": {"candidates": len(uni), "stateless": 16, "stateful": 65536,
                        "N_scored_moments": N, "distinct_sigma": len(counts)}}

    base = {}
    for w in worlds:
        _v, cl = argmin_classes(counts, w["p"], w["eta"], w["lam"])
        base[(w["case"], w["tag"])] = cl

    # T3 invariance
    conj_counts = {}
    sl_sig = dict([(r[2], (r[0], r[3], r[4])) for r in sl])
    sf_sig = dict([((r[1], r[2]), (r[0], r[3], r[4])) for r in sf])
    t3_breaks = 0
    for r in uni:
        if r[0] == 0:
            k = sl_sig[io_conjugate_stateless(r[2])]
        else:
            nn, nt = io_conjugate(r[1], r[2])
            k = sf_sig[(nn, nt)]
        if k[1:] != (r[3], r[4]):
            t3_breaks += 1
        conj_counts[k] = conj_counts.get(k, 0) + 1
    t3_alarms = 0
    for w in worlds:
        _v, cl = argmin_classes(conj_counts, w["p"], w["eta"], w["lam"])
        if cl != base[(w["case"], w["tag"])]:
            t3_alarms += 1

    # T5 equivariance
    eq_breaks = 0
    for w in worlds:
        v0, c0 = argmin_classes(counts, w["p"], w["eta"], w["lam"])
        for cs in SCALE_LADDER:
            c = Fraction(cs)
            v1, c1 = argmin_classes(counts, w["p"], c * w["eta"], c * w["lam"])
            if c1 != c0 or v1 != c * v0:
                eq_breaks += 1
    rep["IV_2"] = {"T3_sigma_breaks": t3_breaks, "T3_alarms": t3_alarms,
                   "T3_is_bijection": conj_counts == counts,
                   "T5_equivariance_breaks": eq_breaks}

    # behavioural census and the conventions
    n_bs = len([1 for k in bs_flags if bs_flags[k]])
    dead_table = 0
    for nxt in range(256):
        pass
    for (nxt, table) in bs_flags:
        pass
    dead_table = 0
    for table in range(256):
        ok = True
        for m in (0, 1):
            for c in (0, 1):
                if ((table >> (2 * m + c)) & 1) != ((table >> (4 + 2 * m + c)) & 1):
                    ok = False
        if ok:
            dead_table += 256
    eff_counts = {}
    for r in uni:
        if r[0] == 0:
            b = 0
        else:
            b = 0 if bs_flags[(r[1], r[2])] else 1
        k = (b, r[3], r[4])
        eff_counts[k] = eff_counts.get(k, 0) + 1
    eff_match = 0
    for w in worlds:
        _v, cl = argmin_classes(eff_counts, w["p"], w["eta"], w["lam"])
        if cl == base[(w["case"], w["tag"])]:
            eff_match += 1

    # mixed convention: charge effective bits, label declared bits
    mixed_flips = 0
    for w in worlds:
        best = None
        cls = set()
        for r in uni:
            if r[0] == 0:
                beff = 0
            else:
                beff = 0 if bs_flags[(r[1], r[2])] else 1
            v = w["eta"] * ((1 - w["p"]) * Fraction(r[3], N)
                            + w["p"] * Fraction(r[4], N)) + w["lam"] * beff
            lab = STATELESS if r[0] == 0 else PERSISTENT
            if best is None or v < best:
                best = v
                cls = set([lab])
            elif v == best:
                cls.add(lab)
        if frozenset(cls) != base[(w["case"], w["tag"])]:
            mixed_flips += 1
    rep["IV_4"] = {"behaviourally_stateless_declared_stateful": n_bs,
                   "syntactic_dead_table_count": dead_table,
                   "syntactic_count_undercounts": n_bs > dead_table,
                   "consistent_effective_verdicts_matching_declared": eff_match,
                   "mixed_convention_flips": mixed_flips,
                   "declared_bits_is_a_semantic_invariant": n_bs == 0}

    # behavioural classes by prefix DP
    classes = {}
    for table in range(16):
        classes.setdefault(stateless_trace_key(table), [0, 0])[0] += 1
    for nxt in range(256):
        for table in range(256):
            classes.setdefault(trace_key(nxt, table), [0, 0])[1] += 1
    mult = sorted([v[0] + v[1] for v in classes.values()])
    with_stateless = len([1 for v in classes.values() if v[0] > 0])
    rep["IV_6a"] = {"behavioural_classes": len(classes),
                    "multiplicity_min": mult[0], "multiplicity_max": mult[-1],
                    "classes_with_a_stateless_member": with_stateless,
                    "largest_class_share_of_universe": fs(Fraction(mult[-1], len(uni)))}

    with open(os.path.join(HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("route B oracle written:", rep["universe"])
    print("  behaviourally stateless:", n_bs, " classes:", len(classes),
          " mixed flips:", mixed_flips)
    return 0


if __name__ == "__main__":
    sys.exit(main())
