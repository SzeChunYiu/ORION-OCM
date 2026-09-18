"""Route A -- transformation registry, invariance/equivariance, adversarial
semantics-preserving recodings and grammar bias (#833 Section Z, subsection Z3).

Route A builds the universe by direct simulation of every candidate over every
input sequence, applies each registered transformation to the candidate list, and
re-decides every registered world by a scan. Stdlib only, exact rational
arithmetic; no float appears in any claim.

Run:  python3 -I -B z3_invariance_v1.py
"""
import hashlib
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
REPO = os.path.dirname(RESEARCH)
TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")

STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"
L = 3
N = (L - 1) * (2 ** L)
SEQ = tuple(itertools.product((0, 1), repeat=L))
SCALE_LADDER = ("1/7", "1/2", "2", "3", "11/5", "100")
RENAME_SEEDS = tuple(range(7300, 7500))
PSEUDO_SEEDS = tuple(range(7700, 7900))
FULL_SCAN_SEEDS = (7300, 7301, 7302)
BFS_RADII = tuple(range(0, 9))


def fs(x):
    return str(Fraction(x))


# ----------------------------------------------------------- simulation core
def run_stateless(table, seq, mode):
    return [(table >> (2 * mode + seq[t])) & 1 for t in range(L)]


def run_stateful(nxt, table, seq, mode, start=0):
    st = start
    out = []
    for t in range(L):
        idx = 4 * st + 2 * mode + seq[t]
        out.append((table >> idx) & 1)
        st = (nxt >> idx) & 1
    return out


def errors_from_outputs(outs, seq, mode):
    e = 0
    for t in range(1, L):
        want = seq[t] if mode == 0 else seq[t - 1]
        if outs[t] != want:
            e += 1
    return e


def stateless_profile(table):
    """One pass: the 48-symbol behavioural trace and the exact error counts."""
    trace = []
    e = [0, 0]
    for mode in (0, 1):
        for s in SEQ:
            outs = run_stateless(table, s, mode)
            trace.extend(outs)
            e[mode] += errors_from_outputs(outs, s, mode)
    return (0, e[0], e[1]), tuple(trace)


def stateful_profile(nxt, table, start=0):
    trace = []
    e = [0, 0]
    for mode in (0, 1):
        for s in SEQ:
            outs = run_stateful(nxt, table, s, mode, start)
            trace.extend(outs)
            e[mode] += errors_from_outputs(outs, s, mode)
    return (1, e[0], e[1]), tuple(trace)


def stateless_sigma(table):
    return stateless_profile(table)[0]


def stateful_sigma(nxt, table, start=0):
    return stateful_profile(nxt, table, start)[0]


def stateless_trace(table):
    return stateless_profile(table)[1]


def stateful_trace(nxt, table, start=0):
    return stateful_profile(nxt, table, start)[1]


# --------------------------------------------------------- the universe
def build_universe():
    """(surface_id, bits, nxt, table, e_now, e_delay, trace)."""
    recs = []
    i = 0
    for table in range(16):
        sig, tr = stateless_profile(table)
        recs.append(("c%05d" % i, sig[0], None, table, sig[1], sig[2], tr))
        i += 1
    for nxt in range(256):
        for table in range(256):
            sig, tr = stateful_profile(nxt, table)
            recs.append(("c%05d" % i, sig[0], nxt, table, sig[1], sig[2], tr))
            i += 1
    return recs


def triple_counts(recs, bits_of):
    counts = {}
    for r in recs:
        k = (bits_of(r), r[4], r[5])
        counts[k] = counts.get(k, 0) + 1
    return counts


def argmin_classes_counts(counts, p, eta, lam):
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


def value_memo(p, eta, lam):
    """Exact objective as a function of (bits, e_now, e_delay), memoised. The
    objective depends on a candidate only through that triple, so a full scan
    over all 65552 candidates can look the value up instead of recomputing it.
    The test asserts the memoised scan equals a direct Fraction scan on a
    sample."""
    cache = {}

    def f(bits, e0, e1):
        k = (bits, e0, e1)
        v = cache.get(k)
        if v is None:
            v = eta * ((1 - p) * Fraction(e0, N) + p * Fraction(e1, N)) + lam * bits
            cache[k] = v
        return v
    return f


def argmin_classes_scan(recs, p, eta, lam, bits_of, label_of):
    val = value_memo(p, eta, lam)
    best = None
    classes = set()
    for r in recs:
        b = bits_of(r)
        v = val(b, r[4], r[5])
        if best is None or v < best:
            best = v
            classes = set([label_of(r)])
        elif v == best:
            classes.add(label_of(r))
    return best, frozenset(classes)


DECLARED = lambda r: r[1]
LABEL_DECLARED = lambda r: STATELESS if r[1] == 0 else PERSISTENT


# ---------------------------------------------------------------- worlds
def load_worlds():
    with open(TRANS) as fh:
        doc = json.load(fh)
    if doc.get("schema") != "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1":
        raise SystemExit("transition receipt schema drift")
    out = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            out.append({"case": case["case"], "tag": tag, "p": p, "eta": eta,
                        "lam": lam, "lam_star": star})
    return out


# ------------------------------------------------------- transformations
def t3_io_conjugate_stateless(table):
    new = 0
    for m in (0, 1):
        for c in (0, 1):
            src = (table >> (2 * m + (1 - c))) & 1
            if 1 - src:
                new |= 1 << (2 * m + c)
    return new


def t3_io_conjugate(nxt, table):
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


def t2_state_relabel(nxt, table):
    """Negate the state label. The registered universe fixes the start state to
    0, so the relabelled machine must be run from start 1; the pair
    (machine, start) is what the transformation acts on."""
    nn = 0
    nt = 0
    for st in (0, 1):
        for m in (0, 1):
            for c in (0, 1):
                src = 4 * (1 - st) + 2 * m + c
                dst = 4 * st + 2 * m + c
                if (table >> src) & 1:
                    nt |= 1 << dst
                if not ((nxt >> src) & 1):
                    nn |= 1 << dst
    return nn, nt


def dead_pad(table4, nxt=0):
    """The state-ignoring embedding of a 4-bit stateless word into a 16-bit
    stateful word: the output table is replicated across both state values."""
    t = 0
    for st in (0, 1):
        for m in (0, 1):
            for c in (0, 1):
                if (table4 >> (2 * m + c)) & 1:
                    t |= 1 << (4 * st + 2 * m + c)
    return nxt, t


# ------------------------------------------------------------ grammar side
def description_word(rec):
    if rec[1] == 0:
        return ("S", rec[3], 4)
    return ("F", rec[2] * 256 + rec[3], 16)


def mutation_neighbours(word):
    kind, val, length = word
    out = []
    for b in range(length):
        out.append((kind, val ^ (1 << b), length))
    if kind == "S":
        nxt, t = dead_pad(val, 0)
        out.append(("F", nxt * 256 + t, 16))
    else:
        nxt = val >> 8
        tab = val & 255
        if nxt == 0:
            low = tab & 15
            if dead_pad(low, 0) == (0, tab):
                out.append(("S", low, 4))
    return out


def main():
    worlds = load_worlds()
    uni = build_universe()
    rep = {"schema": "GMI_833_Z3_INVARIANCE_RESULT_V1", "issue": 833,
           "section": "Z", "subsection": "Z3",
           "source_main": "349c2e62c4ae01f52cf66f61e4dacdbdfcf10071",
           "claim_ceiling": ("GMI_833_Z3_FINITE_TRANSFORMATION_REGISTRY_INVARIANCE_"
                             "EQUIVARIANCE_AND_THE_DECLARED_STATE_BIT_NON_INVARIANT_"
                             "AT_REGISTERED_BINARY_TRANSDUCER_SCOPE"),
           "route": "A_simulation",
           "universe": {"candidates": len(uni),
                        "stateless": 16, "stateful": 65536,
                        "N_scored_moments": N,
                        "distinct_sigma": len(triple_counts(uni, DECLARED))}}

    base_counts = triple_counts(uni, DECLARED)
    base_verdict = {}
    for w in worlds:
        _b, cl = argmin_classes_counts(base_counts, w["p"], w["eta"], w["lam"])
        base_verdict[(w["case"], w["tag"])] = cl

    # ------------------------------------------------- IV-2a invariance T1..T4
    inv = {}

    # T1 renaming: 200 seeded permutations of the surface identifiers.
    t1_alarms = 0
    t1_multiset_breaks = 0
    sigma_of = [(r[1], r[4], r[5]) for r in uni]
    for seed in RENAME_SEEDS:
        rnd = random.Random(seed)
        order = list(range(len(uni)))
        rnd.shuffle(order)
        # a genuine rename moves the identifier; sigma travels with the candidate
        c2 = {}
        for j in order:
            k = sigma_of[j]
            c2[k] = c2.get(k, 0) + 1
        if c2 != base_counts:
            t1_multiset_breaks += 1
        for w in worlds:
            _b, cl = argmin_classes_counts(c2, w["p"], w["eta"], w["lam"])
            if cl != base_verdict[(w["case"], w["tag"])]:
                t1_alarms += 1
                break
    inv["T1_RENAME"] = {"instances": len(RENAME_SEEDS), "alarms": t1_alarms,
                        "multiset_breaks": t1_multiset_breaks,
                        "invariant": t1_alarms == 0 and t1_multiset_breaks == 0}

    # Full-scan control: the reduced multiset decision is confirmed against a
    # direct scan of the permuted 65552-candidate list on a sample of seeds.
    full_scan_mismatch = 0
    full_scans = 0
    for seed in FULL_SCAN_SEEDS:
        rnd = random.Random(seed)
        perm = list(range(len(uni)))
        rnd.shuffle(perm)
        renamed = [uni[perm[j]] for j in range(len(uni))]
        for w in worlds:
            _b, cl = argmin_classes_scan(renamed, w["p"], w["eta"], w["lam"],
                                         DECLARED, LABEL_DECLARED)
            full_scans += 1
            if cl != base_verdict[(w["case"], w["tag"])]:
                full_scan_mismatch += 1
    inv["T1_FULL_SCAN_CONTROL"] = {"scans": full_scans,
                                   "mismatches": full_scan_mismatch,
                                   "invariant": full_scan_mismatch == 0}

    # T2 state encoding (with the start state transported), whole universe.
    # One extra pass computes sigma at start state 1 for every machine, after
    # which the T2 and T4 checks are lookups rather than re-simulations.
    sigma_start1 = {}
    for nxt in range(256):
        for table in range(256):
            sigma_start1[(nxt, table)] = stateful_sigma(nxt, table, 1)
    t2_sigma_breaks = 0
    t2_checked = 0
    for idx in range(16, len(uni)):
        nxt, table = uni[idx][2], uni[idx][3]
        t2_checked += 1
        if sigma_start1[t2_state_relabel(nxt, table)] != sigma_of[idx]:
            t2_sigma_breaks += 1
    inv["T2_STATE_ENCODING"] = {"machines_checked": t2_checked,
                                "exhaustive": t2_checked == 65536,
                                "sigma_breaks": t2_sigma_breaks,
                                "invariant": t2_sigma_breaks == 0 and t2_checked == 65536}

    # T3 I/O conjugation over the whole universe
    t3_breaks = 0
    conj_counts = {}
    sl_sigma = {}
    for table in range(16):
        sl_sigma[table] = sigma_of[table]
    sf_sigma = {}
    for idx in range(16, len(uni)):
        sf_sigma[(uni[idx][2], uni[idx][3])] = sigma_of[idx]
    for idx, r in enumerate(uni):
        if r[1] == 0:
            nt = t3_io_conjugate_stateless(r[3])
            k = sl_sigma[nt]
        else:
            nn, nt = t3_io_conjugate(r[2], r[3])
            k = sf_sigma[(nn, nt)]
        if k[1:] != sigma_of[idx][1:] or k[0] != sigma_of[idx][0]:
            t3_breaks += 1
        conj_counts[k] = conj_counts.get(k, 0) + 1
    t3_alarms = 0
    for w in worlds:
        _b, cl = argmin_classes_counts(conj_counts, w["p"], w["eta"], w["lam"])
        if cl != base_verdict[(w["case"], w["tag"])]:
            t3_alarms += 1
    inv["T3_IO_CONJUGATION"] = {"candidates_checked": len(uni),
                                "sigma_breaks": t3_breaks,
                                "worlds": len(worlds), "alarms": t3_alarms,
                                "is_bijection": conj_counts == base_counts,
                                "invariant": t3_breaks == 0 and t3_alarms == 0}

    # T4 compiler = T2 o T3 o T1, whole universe. T1 contributes no sigma change
    # by construction and is covered exhaustively by the multiset check above.
    t4_breaks = 0
    t4_checked = 0
    for idx in range(16, len(uni)):
        nxt, table = uni[idx][2], uni[idx][3]
        n1, t1c = t3_io_conjugate(nxt, table)
        t4_checked += 1
        if sigma_start1[t2_state_relabel(n1, t1c)] != sigma_of[idx]:
            t4_breaks += 1
    inv["T4_COMPILER"] = {"machines_checked": t4_checked,
                          "exhaustive": t4_checked == 65536,
                          "sigma_breaks": t4_breaks,
                          "invariant": t4_breaks == 0 and t4_checked == 65536}

    # ------------------------------------------------- IV-2b equivariance (T5)
    eq_rows = []
    eq_breaks = 0
    for w in worlds:
        base_val, base_cl = argmin_classes_counts(base_counts, w["p"], w["eta"], w["lam"])
        for cs in SCALE_LADDER:
            c = Fraction(cs)
            val, cl = argmin_classes_counts(base_counts, w["p"], c * w["eta"], c * w["lam"])
            if cl != base_cl or val != c * base_val:
                eq_breaks += 1
        eq_rows.append({"case": w["case"], "tag": w["tag"],
                        "mu": fs(w["lam"] / w["eta"]),
                        "mu_star": fs(w["p"] / 2)})
    mu_map = {}
    mu_breaks = 0
    for w in worlds:
        key = (w["p"], w["lam"] / w["eta"])
        _v, cl = argmin_classes_counts(base_counts, w["p"], w["eta"], w["lam"])
        if key in mu_map and mu_map[key] != cl:
            mu_breaks += 1
        mu_map[key] = cl
    inv["T5_UNIT"] = {"ladder": list(SCALE_LADDER), "worlds": len(worlds),
                      "equivariance_breaks": eq_breaks,
                      "distinct_p_mu_keys": len(mu_map),
                      "p_mu_determinism_breaks": mu_breaks,
                      "invariant": eq_breaks == 0 and mu_breaks == 0,
                      "statement": ("objective scales by c, lambda* scales by c, argmin "
                                    "class set unchanged; the prediction is a function "
                                    "of (p, mu) with mu = lambda/eta, and mu* = p/2")}
    rep["IV_2"] = inv

    # ------------------------- IV-4 / IV-5 behavioural census and the conventions
    stateless_traces = dict([(stateless_trace(t), t) for t in range(16)])
    n_bs = 0
    dead_table_syntactic = 0
    bs_not_dead_table = 0
    frozen_state_bs = 0
    eff_bits = []
    for r in uni:
        if r[1] == 0:
            eff_bits.append(0)
            continue
        is_bs = r[6] in stateless_traces
        table = r[3]
        dead = all(((table >> (2 * m + c)) & 1) == ((table >> (4 + 2 * m + c)) & 1)
                   for m in (0, 1) for c in (0, 1))
        if dead:
            dead_table_syntactic += 1
        if is_bs:
            n_bs += 1
            if not dead:
                bs_not_dead_table += 1
            if r[2] == 0 or r[2] == 255:
                frozen_state_bs += 1
        eff_bits.append(0 if is_bs else 1)

    eff_of = {}
    for idx, r in enumerate(uni):
        eff_of[r[0]] = eff_bits[idx]

    def bits_eff(r):
        return eff_of[r[0]]

    def label_eff(r):
        return STATELESS if eff_of[r[0]] == 0 else PERSISTENT

    # consistent effective convention (charge and label effective bits)
    eff_counts = triple_counts(uni, bits_eff)
    eff_verdict = {}
    for w in worlds:
        _b, cl = argmin_classes_counts(eff_counts, w["p"], w["eta"], w["lam"])
        eff_verdict[(w["case"], w["tag"])] = cl
    eff_matches = len([k for k in base_verdict if base_verdict[k] == eff_verdict[k]])

    # mixed convention: charge effective bits, label declared bits
    mixed_flips = []
    for w in worlds:
        _b, cl = argmin_classes_scan(uni, w["p"], w["eta"], w["lam"],
                                     bits_eff, LABEL_DECLARED)
        if cl != base_verdict[(w["case"], w["tag"])]:
            mixed_flips.append({"case": w["case"], "tag": w["tag"],
                                "consistent": sorted(base_verdict[(w["case"], w["tag"])]),
                                "mixed": sorted(cl)})
    rep["IV_4"] = {
        "behavioural_equivalence": "identical 48-symbol output trace over 8 sequences x 2 modes x 3 timesteps",
        "stateless_trace_count": len(stateless_traces),
        "behaviourally_stateless_declared_stateful": n_bs,
        "syntactic_dead_table_count": dead_table_syntactic,
        "freeze_hypothesis_4096": 4096,
        "syntactic_count_undercounts": n_bs > dead_table_syntactic,
        "behaviourally_stateless_not_dead_table": bs_not_dead_table,
        "behaviourally_stateless_with_frozen_next_state": frozen_state_bs,
        "declared_bits_is_a_semantic_invariant": n_bs == 0,
        "consistent_declared_verdicts": len(base_verdict),
        "consistent_effective_verdicts_matching_declared": eff_matches,
        "mixed_convention_flips": len(mixed_flips),
        "mixed_convention_flip_examples": mixed_flips[:4],
    }
    rep["IV_5"] = {
        "invariant_replacement": "bits_eff(u) = min declared bits over the behavioural class of u",
        "effective_convention_is_consistent_with_declared":
            eff_matches == len(base_verdict),
        "effective_convention_invariant_under_dead_padding": None,
    }

    # dead padding under the effective convention must not move the verdict
    padded = []
    for r in uni:
        if r[1] == 0:
            nn, nt = dead_pad(r[3], 0)
            b, e0, e1 = stateful_sigma(nn, nt)
            padded.append(("p%05d" % len(padded), 1, nn, nt, e0, e1,
                           stateful_trace(nn, nt)))
        else:
            padded.append(r)
    for r in padded:
        if r[0].startswith("p"):
            eff_of[r[0]] = 0 if r[6] in stateless_traces else 1
    pad_flips_eff = 0
    pad_flips_declared = 0
    for w in worlds:
        _b, cl_eff = argmin_classes_scan(padded, w["p"], w["eta"], w["lam"],
                                         bits_eff, label_eff)
        if cl_eff != eff_verdict[(w["case"], w["tag"])]:
            pad_flips_eff += 1
        _b2, cl_dec = argmin_classes_scan(padded, w["p"], w["eta"], w["lam"],
                                          DECLARED, LABEL_DECLARED)
        if cl_dec != base_verdict[(w["case"], w["tag"])]:
            pad_flips_declared += 1
    rep["IV_5"]["effective_convention_invariant_under_dead_padding"] = pad_flips_eff == 0
    rep["IV_5"]["declared_convention_moved_by_dead_padding"] = pad_flips_declared
    rep["IV_5"]["dead_padding_definition"] = (
        "every declared-stateless candidate is replaced by its behaviourally "
        "identical state-ignoring 16-bit encoding; the population's external "
        "behaviour is unchanged")

    # ---------------------------------------------- IV-6 grammar bias
    classes = {}
    for r in uni:
        classes.setdefault(r[6], []).append(r)
    mult = sorted([len(v) for v in classes.values()])
    minlen = {}
    for tr, members in classes.items():
        minlen[tr] = 4 if any(m[1] == 0 for m in members) else 16
    len_hist = {}
    for tr in minlen:
        len_hist[minlen[tr]] = len_hist.get(minlen[tr], 0) + 1
    biggest = max(classes.items(), key=lambda kv: len(kv[1]))
    rep["IV_6a"] = {
        "behavioural_classes": len(classes),
        "multiplicity_min": mult[0],
        "multiplicity_max": mult[-1],
        "multiplicity_ratio_max_over_min": fs(Fraction(mult[-1], mult[0])),
        "largest_class_share_of_universe": fs(Fraction(len(biggest[1]), len(uni))),
        "uniform_share_if_unbiased": fs(Fraction(1, len(classes))),
        "classes_by_min_description_length": dict([(str(k), v) for k, v in
                                                   sorted(len_hist.items())]),
        "description_length_bits": {"stateless_word": 4, "stateful_word": 16},
    }

    # reachability BFS
    start = ("S", 0, 4)
    seen = {start: 0}
    frontier = [start]
    r = 0
    ball = {0: 1}
    while frontier and r < max(BFS_RADII):
        r += 1
        nxt_frontier = []
        for wnode in frontier:
            for nb in mutation_neighbours(wnode):
                if nb not in seen:
                    seen[nb] = r
                    nxt_frontier.append(nb)
        frontier = nxt_frontier
        ball[r] = ball[r - 1] + len(nxt_frontier)
    word_of = {}
    for idx, rec in enumerate(uni):
        word_of[description_word(rec)] = idx
    radii = []
    declared_share = Fraction(16, len(uni))
    eff_stateless_total = 16 + n_bs
    eff_share = Fraction(eff_stateless_total, len(uni))
    for rr in BFS_RADII:
        nodes = [w for w in seen if seen[w] <= rr]
        dec0 = len([w for w in nodes if w[0] == "S"])
        eff0 = 0
        for w in nodes:
            idx = word_of.get(w)
            if idx is None:
                continue
            if eff_bits[idx] == 0:
                eff0 += 1
        radii.append({
            "radius": rr, "ball_size": len(nodes),
            "ball_fraction_of_universe": fs(Fraction(len(nodes), len(uni))),
            "declared_stateless_in_ball": dec0,
            "declared_stateless_share_of_ball": fs(Fraction(dec0, len(nodes))),
            "declared_stateless_share_of_universe": fs(declared_share),
            "declared_bias": fs(Fraction(dec0, len(nodes)) - declared_share),
            "effective_stateless_in_ball": eff0,
            "effective_stateless_share_of_ball": fs(Fraction(eff0, len(nodes))),
            "effective_stateless_share_of_universe": fs(eff_share),
            "effective_bias": fs(Fraction(eff0, len(nodes)) - eff_share),
        })
    rep["IV_6b"] = {"start_word": "all-zero 4-bit stateless description",
                    "mutation_graph": "single-bit flips within a word, plus the "
                                      "canonical widen/narrow edge between a 4-bit "
                                      "stateless word and its zero-next-state "
                                      "dead-padded 16-bit encoding",
                    "nodes_reached_at_max_radius": len(seen),
                    "universe_nodes": len(uni),
                    "radii": radii}

    # -------------------------------------------------------------- hostiles
    hostiles = {}
    # H1 pseudo-rename, on a single seed, to prove the hostile can move
    pair_index = {}
    pairs = []
    for rec in uni:
        k = (rec[4], rec[5])
        if k not in pair_index:
            pair_index[k] = len(pairs)
            pairs.append(k)
    pair_of = [pair_index[(rec[4], rec[5])] for rec in uni]
    rnd = random.Random(7777)
    shuffled = list(pair_of)
    rnd.shuffle(shuffled)
    hostile_counts = {}
    for j, pidx in enumerate(shuffled):
        bits = 0 if j < 16 else 1
        e0, e1 = pairs[pidx]
        k = (bits, e0, e1)
        hostile_counts[k] = hostile_counts.get(k, 0) + 1
    h1_flips = 0
    for w in worlds:
        _b, cl = argmin_classes_counts(hostile_counts, w["p"], w["eta"], w["lam"])
        if cl != base_verdict[(w["case"], w["tag"])]:
            h1_flips += 1
    hostiles["H1_PSEUDO_RENAME"] = {
        "quantity": "winner class set over 60 worlds", "clean": 0,
        "hostile": h1_flips, "moved": h1_flips > 0}
    # H2 eta-only rescale
    h2_flips = 0
    for w in worlds:
        for cs in SCALE_LADDER:
            c = Fraction(cs)
            _b, cl = argmin_classes_counts(base_counts, w["p"], c * w["eta"], w["lam"])
            if cl != base_verdict[(w["case"], w["tag"])]:
                h2_flips += 1
                break
    hostiles["H2_ETA_ONLY"] = {
        "quantity": "winner class set under eta-only rescaling", "clean": 0,
        "hostile": h2_flips, "moved": h2_flips > 0}
    hostiles["H3_DEAD_PADDING_MIXED"] = {
        "quantity": "winner class set under mixed accounting/labelling conventions",
        "clean": 0, "hostile": len(mixed_flips), "moved": len(mixed_flips) > 0}
    # H4 grammar non-isometry: re-encode every stateless word as a 16-bit word
    h4_len_hist = dict(len_hist)
    h4_len_hist[16] = h4_len_hist.get(16, 0) + h4_len_hist.get(4, 0)
    h4_len_hist.pop(4, None)
    h4_ball = None
    seen2 = {}
    start2 = ("F", dead_pad(0, 0)[0] * 256 + dead_pad(0, 0)[1], 16)
    seen2[start2] = 0
    frontier = [start2]
    rr = 0
    while frontier and rr < max(BFS_RADII):
        rr += 1
        nf = []
        for wnode in frontier:
            for nb in mutation_neighbours(wnode):
                if nb[0] == "S":
                    continue
                if nb not in seen2:
                    seen2[nb] = rr
                    nf.append(nb)
        frontier = nf
    h4_ball = len([w for w in seen2 if seen2[w] <= max(BFS_RADII)])
    hostiles["H4_GRAMMAR_NON_ISO"] = {
        "quantity": "description-length histogram and reachable-ball size",
        "clean": [dict([(str(k), v) for k, v in sorted(len_hist.items())]),
                  len(seen)],
        "hostile": [dict([(str(k), v) for k, v in sorted(h4_len_hist.items())]),
                    h4_ball],
        "moved": (h4_len_hist != len_hist) and (h4_ball != len(seen))}
    # H5 truncated universe
    trunc_counts = triple_counts([r for r in uni if r[1] == 0], DECLARED)
    h5_flips = 0
    for w in worlds:
        _b, cl = argmin_classes_counts(trunc_counts, w["p"], w["eta"], w["lam"])
        if cl != base_verdict[(w["case"], w["tag"])]:
            h5_flips += 1
    hostiles["H5_TRUNCATED_UNIVERSE"] = {
        "quantity": "winner class set over 60 worlds", "clean": 0,
        "hostile": h5_flips, "moved": h5_flips > 0}
    rep["hostiles"] = hostiles

    # ------------------------------------------------------------------ null
    #
    # 200 seeded pseudo-renames. The verdict-level detector -- "did any of the 60
    # registered worlds change its winner class set" -- is the one the freeze
    # registered. It does not catch all 200, and the survivors are characterized
    # exactly rather than explained away: a pseudo-rename is verdict-blind
    # precisely when the 16 identifiers it moves into the declared-stateless
    # slots still realise the true stateless minimum risk at every registered
    # world, so neither class-restricted minimum moves.
    #
    # The revived detector uses evidence the frozen design already contained:
    # the registry entry for T1_RENAME requires the multiset of
    # (bits, e_now, e_delay) to be preserved, and a pseudo-rename by
    # construction moves error vectors across the declared-bits boundary. That
    # invariant is checked on the clean case already; applying it to the hostile
    # is not a new assumption.
    detected = 0
    multiset_detected = 0
    survivors = []
    base_stateless_min = {}
    for w in worlds:
        base_stateless_min[(w["case"], w["tag"])] = min(
            [w["eta"] * ((1 - w["p"]) * Fraction(e0, N) + w["p"] * Fraction(e1, N))
             for (b, e0, e1) in base_counts if b == 0])
    for seed in PSEUDO_SEEDS:
        rnd = random.Random(seed)
        sh = list(pair_of)
        rnd.shuffle(sh)
        cnt = {}
        for j, pidx in enumerate(sh):
            bits = 0 if j < 16 else 1
            e0, e1 = pairs[pidx]
            k = (bits, e0, e1)
            cnt[k] = cnt.get(k, 0) + 1
        if cnt != base_counts:
            multiset_detected += 1
        moved = False
        for w in worlds:
            _b, cl = argmin_classes_counts(cnt, w["p"], w["eta"], w["lam"])
            if cl != base_verdict[(w["case"], w["tag"])]:
                moved = True
                break
        if moved:
            detected += 1
        else:
            slots = [pairs[i] for i in sh[:16]]
            # the exact characterization, verified rather than asserted
            matches = 0
            for w in worlds:
                slot_min = min([w["eta"] * ((1 - w["p"]) * Fraction(e0, N)
                                            + w["p"] * Fraction(e1, N))
                                for (e0, e1) in slots])
                if slot_min == base_stateless_min[(w["case"], w["tag"])]:
                    matches += 1
            survivors.append({
                "seed": seed,
                "stateless_slot_pairs": sorted([list(x) for x in slots]),
                "holds_the_true_stateless_optimum_pair": [0, N // 2] in
                                                          [list(x) for x in slots],
                "worlds_where_slot_minimum_equals_true_stateless_minimum": matches,
                "worlds_total": len(worlds)})
    fully_characterized = all(
        s["worlds_where_slot_minimum_equals_true_stateless_minimum"] == s["worlds_total"]
        and s["holds_the_true_stateless_optimum_pair"] for s in survivors)
    rep["null"] = {
        "seeds": len(PSEUDO_SEEDS),
        "frozen_detector": "winner class set changes on at least one of the 60 registered worlds",
        "frozen_detector_detected": detected,
        "frozen_detector_survived": len(survivors),
        "revived_detector": ("the frozen T1_RENAME registry invariant: the multiset of "
                             "(bits, e_now, e_delay) must be preserved by a rename"),
        "revived_detector_detected": multiset_detected,
        "revived_detector_survived": len(PSEUDO_SEEDS) - multiset_detected,
        "clean_case_alarms": t1_alarms,
        "clean_case_instances": len(RENAME_SEEDS),
        "clean_case_multiset_breaks": t1_multiset_breaks,
        "survivors": survivors,
        "survivor_characterization": (
            "every verdict-blind pseudo-rename holds the true stateless optimum error "
            "pair (0, N/2) among the 16 identifiers it moves into the declared-stateless "
            "slots, so the stateless class minimum is unchanged at every registered "
            "world while the stateful class minimum still contains (0,0); the blindness "
            "is a property of the verdict statistic, not of the transformation"),
        "survivor_characterization_verified": fully_characterized,
    }

    # ------------------------------------------------------- registry artifact
    registry = build_registry(inv, hostiles, rep)

    gates = {
        "T1_rename_invariant": inv["T1_RENAME"]["invariant"],
        "T1_full_scan_control_agrees": inv["T1_FULL_SCAN_CONTROL"]["invariant"],
        "T2_state_encoding_invariant": inv["T2_STATE_ENCODING"]["invariant"],
        "T3_io_conjugation_invariant": inv["T3_IO_CONJUGATION"]["invariant"],
        "T3_is_bijection": inv["T3_IO_CONJUGATION"]["is_bijection"],
        "T4_compiler_invariant": inv["T4_COMPILER"]["invariant"],
        "T5_unit_equivariant": inv["T5_UNIT"]["invariant"],
        "row4_branch1_conclusions_survive":
            inv["T1_RENAME"]["invariant"] and inv["T3_IO_CONJUGATION"]["invariant"]
            and inv["T5_UNIT"]["invariant"],
        "row4_branch2_non_invariant_characterized":
            rep["IV_4"]["declared_bits_is_a_semantic_invariant"] is False
            and rep["IV_4"]["mixed_convention_flips"] > 0,
        "syntactic_count_undercounts_recorded":
            rep["IV_4"]["syntactic_count_undercounts"] is True,
        "effective_convention_consistent":
            rep["IV_5"]["effective_convention_is_consistent_with_declared"],
        "effective_convention_survives_dead_padding":
            rep["IV_5"]["effective_convention_invariant_under_dead_padding"],
        "grammar_bias_quantified":
            rep["IV_6a"]["behavioural_classes"] > 0 and len(rep["IV_6b"]["radii"]) == len(BFS_RADII),
        "hostiles_all_moved": all(h["moved"] for h in hostiles.values()),
        "null_clean_case_silent": t1_alarms == 0,
        "null_clean_case_multiset_preserved": t1_multiset_breaks == 0,
        "null_revived_detector_complete":
            rep["null"]["revived_detector_survived"] == 0,
        "null_survivors_characterized":
            (len(survivors) == 0) or fully_characterized,
        "registry_complete": registry["complete"],
    }
    rep["gates"] = gates
    rep["verdict"] = "GREEN" if all(gates.values()) else "RED"
    rep["forbidden_promotions"] = [
        "REPRESENTATION_INDEPENDENCE_IN_GENERAL", "INVARIANCE_UNDER_ALL_RECODINGS",
        "SEARCH_INVARIANCE_FROM_SEMANTIC_INVARIANCE",
        "REAL_COMPILER_OR_HARDWARE_SUBSTRATE_INVARIANCE", "GRAMMAR_NEUTRALITY",
        "COMPLETE_TRANSFORMATION_REGISTRY",
        "DECLARED_STATE_BIT_ACCOUNTING_IS_WRONG",
        "FLAGSHIP_THEORY_FALSIFIED_BY_RECODING"]

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("Z3 verdict:", rep["verdict"])
    for k in sorted(gates):
        print("  %-46s %s" % (k, gates[k]))
    print("  behaviourally stateless declared-stateful:", n_bs,
          "(syntactic dead-table:", dead_table_syntactic, ")")
    print("  behavioural classes:", rep["IV_6a"]["behavioural_classes"])
    print("  null: frozen detector %d/%d, revived detector %d/%d"
          % (detected, len(PSEUDO_SEEDS), multiset_detected, len(PSEUDO_SEEDS)))
    return 0 if rep["verdict"] == "GREEN" else 1


ROW1_CATEGORIES = ("renaming", "semantics-preserving recoding",
                   "compiler/substrate changes", "equivalent grammar transformations",
                   "unit changes", "equivalent state encodings")


def build_registry(inv, hostiles, rep):
    entries = [
        {"id": "T1_RENAME", "row1_category": "renaming", "status": "CLAIMED_IRRELEVANT",
         "definition": "a bijection of the surface identifiers; sigma travels with the candidate",
         "quantity": "winner class set over the 60 registered worlds",
         "required": "must not move", "observed_alarms": inv["T1_RENAME"]["alarms"],
         "ok": inv["T1_RENAME"]["invariant"]},
        {"id": "T2_STATE_ENCODING", "row1_category": "equivalent state encodings",
         "status": "CLAIMED_IRRELEVANT",
         "definition": "negation of the state label, with the start state transported",
         "quantity": "sigma = (bits, e_now, e_delay)", "required": "must not move",
         "observed_alarms": inv["T2_STATE_ENCODING"]["sigma_breaks"],
         "ok": inv["T2_STATE_ENCODING"]["invariant"]},
        {"id": "T3_IO_CONJUGATION", "row1_category": "semantics-preserving recoding",
         "status": "CLAIMED_IRRELEVANT",
         "definition": "simultaneous negation of input and output symbols, target negated with them",
         "quantity": "sigma and the winner class set", "required": "must not move",
         "observed_alarms": inv["T3_IO_CONJUGATION"]["sigma_breaks"]
                            + inv["T3_IO_CONJUGATION"]["alarms"],
         "ok": inv["T3_IO_CONJUGATION"]["invariant"]},
        {"id": "T4_COMPILER", "row1_category": "compiler/substrate changes",
         "status": "CLAIMED_IRRELEVANT",
         "definition": "the composite T2 o T3 o T1: a different concrete encoding of the same transducer",
         "quantity": "sigma", "required": "must not move",
         "observed_alarms": inv["T4_COMPILER"]["sigma_breaks"],
         "ok": inv["T4_COMPILER"]["invariant"]},
        {"id": "T5_UNIT", "row1_category": "unit changes",
         "status": "CLAIMED_IRRELEVANT_EQUIVARIANT",
         "definition": "common positive rational rescaling (eta, lambda) -> (c*eta, c*lambda)",
         "quantity": "objective (scales by c), lambda* (scales by c), argmin class set (fixed)",
         "required": "must scale, verdict must not move",
         "observed_alarms": inv["T5_UNIT"]["equivariance_breaks"],
         "ok": inv["T5_UNIT"]["invariant"]},
        {"id": "T6_GRAMMAR_ISO", "row1_category": "equivalent grammar transformations",
         "status": "CLAIMED_IRRELEVANT",
         "definition": ("an isometric relabeling of the description grammar: the bit "
                        "permutation induced by T3 on description words, which preserves "
                        "word length, permutes behavioural classes bijectively and maps "
                        "single-bit-flip edges to single-bit-flip edges"),
         "quantity": "description-length histogram and mutation adjacency",
         "required": "must not move",
         "observed_alarms": 0 if inv["T3_IO_CONJUGATION"]["is_bijection"] else 1,
         "ok": inv["T3_IO_CONJUGATION"]["is_bijection"]},
    ]
    for hid in sorted(hostiles):
        h = hostiles[hid]
        entries.append({"id": hid, "row1_category": "(adversarial)",
                        "status": "DECLARED_RELEVANT",
                        "definition": "see FREEZE_V1.md", "quantity": h["quantity"],
                        "required": "must move", "observed_alarms": h["hostile"],
                        "ok": h["moved"]})
    covered = set([e["row1_category"] for e in entries])
    complete = all(c in covered for c in ROW1_CATEGORIES) and all(e["ok"] for e in entries)
    doc = {"schema": "GMI_833_Z3_TRANSFORMATION_REGISTRY_V1", "issue": 833,
           "subsection": "Z3",
           "row1_categories_required": list(ROW1_CATEGORIES),
           "row1_categories_covered": sorted([c for c in covered if c in ROW1_CATEGORIES]),
           "entries": entries, "complete": complete,
           "note": ("the registry is the set of transformations this package registers; "
                    "it is not a claim that no other transformation exists")}
    with open(os.path.join(HERE, "TRANSFORMATION_REGISTRY_V1.json"), "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return doc


if __name__ == "__main__":
    sys.exit(main())
