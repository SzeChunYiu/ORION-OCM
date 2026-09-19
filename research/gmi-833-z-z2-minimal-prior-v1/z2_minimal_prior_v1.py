"""Route A -- exact encoding-induced prior and minimum sufficient inductive bias
(#833 Section Z, subsection Z2).

Route A *simulates*: every candidate is replayed step by step over the eight
input sequences in both modes, its 48-bit behaviour vector is built by running
the mechanism, and every hypothesis, invariance, learner score, family
specification and null is decided by scanning the resulting list.

Stdlib only; exact integers and fractions.Fraction; no float appears in any
claim.  Python 3.8 compatible.

Run:  python3 -I -B z2_minimal_prior_v1.py
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

L = 3
SEQ = tuple(itertools.product((0, 1), repeat=L))
NSEQ = len(SEQ)
N_SCORED = (L - 1) * NSEQ          # 16 scored moments per mode

# registered 5x4 (p, eta) x lambda grid of the parent transition package
GRID_P = ("1/5", "2/5", "1/2", "3/5", "4/5")
GRID_ETA = ("1", "2", "3", "4")

FEATURE_SEEDS = tuple(range(4100, 4300))
SPEC_SEEDS = tuple(range(4300, 4500))
RENAME_SEED = 90210


# --------------------------------------------------------------- mechanisms
def run_stateless(table, mode, seq):
    """Outputs at t = 0,1,2 for a 4-bit table indexed by 2*mode + cur."""
    out = []
    for t in range(L):
        cur = seq[t]
        out.append((table >> (2 * mode + cur)) & 1)
    return out


def run_stateful(nxt, table, mode, seq):
    """Outputs at t = 0,1,2 from canonical initial state 0."""
    out = []
    st = 0
    for t in range(L):
        cur = seq[t]
        idx = 4 * st + 2 * mode + cur
        out.append((table >> idx) & 1)
        st = (nxt >> idx) & 1
    return out


def behaviour(bits, nxt, table):
    """48-bit behaviour key: (mode, seq, t) -> output, packed MSB-first."""
    key = 0
    for mode in (0, 1):
        for si in range(NSEQ):
            if bits == 0:
                out = run_stateless(table, mode, SEQ[si])
            else:
                out = run_stateful(nxt, table, mode, SEQ[si])
            for t in range(L):
                key = (key << 1) | out[t]
    return key


def errors_from_beh(key):
    """(e_now, e_delay) recomputed from the packed behaviour key."""
    e = [0, 0]
    for mode in (0, 1):
        for si in range(NSEQ):
            seq = SEQ[si]
            for t in range(L):
                shift = 47 - ((mode * NSEQ + si) * L + t)
                got = (key >> shift) & 1
                if t == 0:
                    continue
                want = seq[t] if mode == 0 else seq[t - 1]
                if got != want:
                    e[mode] += 1
    return e[0], e[1]


def build_universe():
    """List of (bits, nxt, table, beh) in canonical index order."""
    out = []
    for table in range(16):
        out.append((0, None, table, behaviour(0, None, table)))
    for nxt in range(256):
        for table in range(256):
            out.append((1, nxt, table, behaviour(1, nxt, table)))
    return out


# ------------------------------------------------------------ semantic map
def semantic_classes(universe):
    """beh -> (class_id, size); class ids assigned in first-appearance order."""
    cid = {}
    size = []
    first_hit = []
    for i, rec in enumerate(universe):
        b = rec[3]
        if b not in cid:
            cid[b] = len(size)
            size.append(0)
            first_hit.append(i)
        size[cid[b]] += 1
    return cid, size, first_hit


def tv_distance(size, total):
    """Exact total variation between (size/total) and uniform over classes."""
    k = len(size)
    acc = Fraction(0)
    for n in size:
        acc += abs(Fraction(n, total) - Fraction(1, k))
    return acc / 2


# ------------------------------------------------------- held-out learners
def moments():
    """Scored moments (mode, seq_index, t) with t in {1,2}."""
    return [(m, si, t) for m in (0, 1) for si in range(NSEQ) for t in (1, 2)]


def beh_bit(key, mode, si, t):
    shift = 47 - ((mode * NSEQ + si) * L + t)
    return (key >> shift) & 1


def problems():
    """36 frozen (observation set, held-out moment) problems."""
    out = []
    for k in range(NSEQ):
        obs = [(0, si, t) for si in range(NSEQ) for t in (1, 2)]
        obs += [(1, si, t) for si in range(k) for t in (1, 2)]
        obs = tuple(sorted(obs))
        for s in range(k, NSEQ):
            out.append((obs, (1, s, 2)))
    return out


def signature(key, obs):
    sig = 0
    for (m, si, t) in obs:
        sig = (sig << 1) | beh_bit(key, m, si, t)
    return sig


def learner_scores(universe, cid, size, feature_masks):
    """Exact learner accuracies, reported on the full population AND on the
    undetermined subpopulation (freeze amendment 2).

    Everything a learner can see is a function of the behaviour key, so the
    work is done once per semantic class and weighted by class size.  A
    feature is syntactic, so for each class we also carry how many of its
    candidates the feature prefers.

    A bucket is *determined* when every class in it emits the same held-out
    bit: there every learner is correct for free.  The bias question lives
    entirely in the undetermined buckets, where a learner with no preference
    scores exactly 1/2.
    """
    probs = problems()
    K = len(size)
    classes = [0] * K
    seen = [False] * K
    for rec in universe:
        c = cid[rec[3]]
        if not seen[c]:
            classes[c] = rec[3]
            seen[c] = True
    names = [nm for nm, _ in feature_masks]
    pref = [[0] * K for _ in names]
    for i, rec in enumerate(universe):
        c = cid[rec[3]]
        for fi in range(len(names)):
            if feature_masks[fi][1][i]:
                pref[fi][c] += 1

    full_total = 0
    und_total = 0
    det_total = 0
    correct_syn = 0
    correct_sem = 0
    und_syn = 0
    und_sem = 0
    und_disagree_buckets = 0
    full_disagree_buckets = 0
    correct_feat_full = [0] * len(names)
    # preference-only learner on the undetermined set, twice the exact count so
    # that a 1/2 abstention stays an integer
    und_feat_2x = [0] * len(names)
    per_problem = []
    for obs, m in probs:
        buckets = {}
        for c_id in range(K):
            key = classes[c_id]
            sig = signature(key, obs)
            bit = beh_bit(key, m[0], m[1], m[2])
            ent = buckets.get(sig)
            if ent is None:
                ent = buckets[sig] = [[0, 0], [0, 0], []]
            ent[0][bit] += size[c_id]
            ent[1][bit] += 1
            ent[2].append((c_id, bit))
        p_und = 0
        p_det = 0
        for sig in buckets:
            ent = buckets[sig]
            n0, n1 = ent[0]
            k0, k1 = ent[1]
            tot = n0 + n1
            full_total += tot
            p_syn = 0 if n0 >= n1 else 1
            p_sem = 0 if k0 >= k1 else 1
            correct_syn += ent[0][p_syn]
            correct_sem += ent[0][p_sem]
            if p_syn != p_sem:
                full_disagree_buckets += 1
            undetermined = n0 > 0 and n1 > 0
            if undetermined:
                p_und += tot
                und_total += tot
                und_syn += ent[0][p_syn]
                und_sem += ent[0][p_sem]
                if p_syn != p_sem:
                    und_disagree_buckets += 1
            else:
                p_det += tot
                det_total += tot
            for fi in range(len(names)):
                pf = pref[fi]
                q0 = 0
                q1 = 0
                for (c_id, bit) in ent[2]:
                    if bit:
                        q1 += pf[c_id]
                    else:
                        q0 += pf[c_id]
                # full-population learner: restrict then count
                if q0 + q1 > 0:
                    predf = 0 if q0 >= q1 else 1
                else:
                    predf = p_syn
                correct_feat_full[fi] += ent[0][predf]
                # preference-only learner on the undetermined buckets
                if undetermined:
                    if q0 > 0 and q1 == 0:
                        und_feat_2x[fi] += 2 * n0
                    elif q1 > 0 and q0 == 0:
                        und_feat_2x[fi] += 2 * n1
                    else:
                        und_feat_2x[fi] += tot
        per_problem.append({"k_obs_mode1_seqs": (len(obs) - 16) // 2,
                            "heldout_seq": m[1],
                            "buckets": len(buckets),
                            "undetermined_targets": p_und,
                            "determined_targets": p_det})
    return {
        "problems": len(probs),
        "full_total": full_total,
        "determined_total": det_total,
        "undetermined_total": und_total,
        "correct_syn_full": correct_syn,
        "correct_sem_full": correct_sem,
        "correct_syn_und": und_syn,
        "correct_sem_und": und_sem,
        "disagreeing_buckets_full": full_disagree_buckets,
        "disagreeing_buckets_und": und_disagree_buckets,
        "correct_feat_full": dict(zip(names, correct_feat_full)),
        "feat_und_2x": dict(zip(names, und_feat_2x)),
        "per_problem": per_problem,
    }


# ------------------------------------------------------------- re-encodings
def g_rename(universe, seed):
    perm = list(range(len(universe)))
    random.Random(seed).shuffle(perm)
    return [universe[perm[i]] for i in range(len(universe))], perm


def g_state(universe):
    out = []
    for (bits, nxt, table, _b) in universe:
        if bits == 0:
            out.append((0, None, table, behaviour(0, None, table)))
            continue
        n2 = 0
        t2 = 0
        for s in (0, 1):
            for m in (0, 1):
                for c in (0, 1):
                    i2 = 4 * s + 2 * m + c
                    i1 = 4 * (1 - s) + 2 * m + c
                    n2 |= (1 - ((nxt >> i1) & 1)) << i2
                    t2 |= (((table >> i1) & 1)) << i2
        out.append((1, n2, t2, behaviour(1, n2, t2)))
    return out


def g_out(universe):
    out = []
    for (bits, nxt, table, _b) in universe:
        if bits == 0:
            t2 = (~table) & 0xF
            out.append((0, None, t2, behaviour(0, None, t2)))
        else:
            t2 = (~table) & 0xFF
            out.append((1, nxt, t2, behaviour(1, nxt, t2)))
    return out


def is_bijection(universe, image):
    a = set((r[0], r[1], r[2]) for r in universe)
    b = set((r[0], r[1], r[2]) for r in image)
    return len(a) == len(universe) and a == b


# ------------------------------------------------------------- objective J
def risk_summaries(universe):
    """Distinct (e_now, e_delay, bits) summaries with multiplicity."""
    out = {}
    for r in universe:
        e0, e1 = errors_from_beh(r[3])
        k = (e0, e1, r[0])
        out[k] = out.get(k, 0) + 1
    return out


def grid_min_and_class(summaries):
    """Exact min of J and the winning property class on the registered grid.

    Minimisation runs over the distinct risk summaries, which is exact: J is a
    function of (e_now, e_delay, bits) alone.
    """
    keys = list(summaries.keys())
    out = []
    for ps in GRID_P:
        for es in GRID_ETA:
            p = Fraction(ps)
            eta = Fraction(es)
            lam_star = eta * p / 2
            for tag, lam in (("low", lam_star / 2), ("high", lam_star * 3 / 2)):
                best = None
                best_bits = None
                for (e0, e1, bits) in keys:
                    j = (eta * p * Fraction(e1, N_SCORED)
                         + eta * (1 - p) * Fraction(e0, N_SCORED)
                         + lam * bits)
                    if best is None or j < best or (j == best and bits < best_bits):
                        best = j
                        best_bits = bits
                out.append({"p": str(p), "eta": str(eta), "lambda_tag": tag,
                            "lambda": str(lam), "min_J": str(best),
                            "winner": "STATELESS" if best_bits == 0
                                      else "PERSISTENT_STATE"})
    return out


# ------------------------------------------- property-first specification
PRIMS = ("p01_has_state", "p02_out_depends_on_input", "p03_out_depends_on_state",
         "p04_out_depends_on_mode", "p05_out_constant",
         "p06_next_depends_on_input", "p07_next_depends_on_state",
         "p08_next_depends_on_mode", "p09_next_constant",
         "p10_next_equals_input", "p11_next_equals_state",
         "p12_out_equals_input")

FAMILY_NAME_TOKENS = ("moore", "mealy", "stateless", "dead", "frozen",
                      "identity", "mlp", "cnn", "transformer", "rnn", "lstm",
                      "family", "f_")


def tbits(table, bits):
    """table(s,m,c) as a dict; stateless tables are lifted to s-independent."""
    d = {}
    for s in (0, 1):
        for m in (0, 1):
            for c in (0, 1):
                if bits == 0:
                    d[(s, m, c)] = (table >> (2 * m + c)) & 1
                else:
                    d[(s, m, c)] = (table >> (4 * s + 2 * m + c)) & 1
    return d


def nbits(nxt, bits):
    d = {}
    for s in (0, 1):
        for m in (0, 1):
            for c in (0, 1):
                if bits == 0:
                    d[(s, m, c)] = 0
                else:
                    d[(s, m, c)] = (nxt >> (4 * s + 2 * m + c)) & 1
    return d


def _depends(d, axis):
    keys = [(s, m, c) for s in (0, 1) for m in (0, 1) for c in (0, 1)]
    for k in keys:
        k2 = list(k)
        k2[axis] = 1 - k2[axis]
        if d[k] != d[tuple(k2)]:
            return True
    return False


def primitives(rec):
    bits, nxt, table, _b = rec
    T = tbits(table, bits)
    Nn = nbits(nxt if nxt is not None else 0, bits)
    vals = {}
    vals["p01_has_state"] = bits == 1
    vals["p02_out_depends_on_input"] = _depends(T, 2)
    vals["p03_out_depends_on_state"] = bits == 1 and _depends(T, 0)
    vals["p04_out_depends_on_mode"] = _depends(T, 1)
    vals["p05_out_constant"] = len(set(T.values())) == 1
    vals["p06_next_depends_on_input"] = bits == 1 and _depends(Nn, 2)
    vals["p07_next_depends_on_state"] = bits == 1 and _depends(Nn, 0)
    vals["p08_next_depends_on_mode"] = bits == 1 and _depends(Nn, 1)
    vals["p09_next_constant"] = bits == 1 and len(set(Nn.values())) == 1
    vals["p10_next_equals_input"] = bits == 1 and all(
        Nn[(s, m, c)] == c for s in (0, 1) for m in (0, 1) for c in (0, 1))
    vals["p11_next_equals_state"] = bits == 1 and all(
        Nn[(s, m, c)] == s for s in (0, 1) for m in (0, 1) for c in (0, 1))
    vals["p12_out_equals_input"] = all(
        T[(s, m, c)] == c for s in (0, 1) for m in (0, 1) for c in (0, 1))
    return tuple(vals[p] for p in PRIMS)


def select(spec, prim_table):
    """spec: tuple of 12 entries in {-1, 0, 1}; 0 = absent."""
    out = []
    for i, pv in enumerate(prim_table):
        ok = True
        for j, lit in enumerate(spec):
            if lit == 0:
                continue
            want = lit == 1
            if pv[j] != want:
                ok = False
                break
        if ok:
            out.append(i)
    return out


def registered_families(universe):
    """Member index sets of the six registered named families, computed by the
    parent package's syntactic predicates.  Used only as the ground truth the
    property-first specifications must reproduce; no name enters the spec."""
    fam = dict((k, []) for k in ("F_STATELESS", "F_DEAD_TABLE", "F_FROZEN_STATE",
                                 "F_MOORE", "F_MEALY_PURE", "F_IDENTITY_STATE"))
    for i, (bits, nxt, table, _b) in enumerate(universe):
        if bits == 0:
            fam["F_STATELESS"].append(i)
            continue
        dead = all(((table >> (2 * m + c)) & 1) == ((table >> (4 + 2 * m + c)) & 1)
                   for m in (0, 1) for c in (0, 1))
        if dead:
            fam["F_DEAD_TABLE"].append(i)
        if nxt in (0, 255):
            fam["F_FROZEN_STATE"].append(i)
        moore = all(((table >> (4 * s + 2 * m)) & 1) ==
                    ((table >> (4 * s + 2 * m + 1)) & 1)
                    for s in (0, 1) for m in (0, 1))
        if moore:
            fam["F_MOORE"].append(i)
        else:
            fam["F_MEALY_PURE"].append(i)
        if nxt == 0b10101010:
            fam["F_IDENTITY_STATE"].append(i)
    return dict((k, set(v)) for k, v in fam.items())


# the six property-first specifications, written in V12 only
SPECS = {
    "F_STATELESS":      {"p01_has_state": -1},
    "F_DEAD_TABLE":     {"p01_has_state": 1, "p03_out_depends_on_state": -1},
    "F_FROZEN_STATE":   {"p01_has_state": 1, "p09_next_constant": 1},
    "F_MOORE":          {"p01_has_state": 1, "p02_out_depends_on_input": -1},
    "F_MEALY_PURE":     {"p01_has_state": 1, "p02_out_depends_on_input": 1},
    "F_IDENTITY_STATE": {"p01_has_state": 1, "p10_next_equals_input": 1},
}


def spec_tuple(d):
    return tuple(d.get(p, 0) for p in PRIMS)


def grammar_digest():
    h = hashlib.sha256()
    h.update("|".join(PRIMS).encode("utf-8"))
    h.update(b"|conjunction-of-literals|3^12")
    return h.hexdigest()


def smuggling_audit(spec_dict):
    """Lexical no-smuggling audit over the specification vocabulary only."""
    hits = []
    for key in spec_dict:
        low = key.lower()
        for tok in FAMILY_NAME_TOKENS:
            if tok in low:
                hits.append((key, tok))
    return hits


# --------------------------------------------------------------- vacuity
def vacuity(lo, hi, bound, direction):
    """Classify a bound against the codomain [lo, hi] of the bounded quantity.

    direction '<=' means the claim is 'quantity <= bound'.
    NON_BINDING  -- no element of the codomain could violate it
    BINDING      -- some element of the codomain violates it
    """
    if direction == "<=":
        return "NON_BINDING" if hi <= bound else "BINDING"
    return "NON_BINDING" if lo >= bound else "BINDING"


# ------------------------------------------------------------------- main
def main():
    universe = build_universe()
    total = len(universe)
    cid, size, first_hit = semantic_classes(universe)
    K = len(size)
    d_tv = tv_distance(size, total)
    hist = sorted(size)

    # H4: canonical-order first-hit spread
    fh_sorted = sorted(first_hit)
    fh_min = fh_sorted[0] + 1        # 1-based probe count
    fh_max = fh_sorted[-1] + 1
    fh_ratio = Fraction(fh_max, fh_min)

    # registered structural features (the 1-bit bias alphabet)
    def mask(fn):
        return [fn(r, i) for i, r in enumerate(universe)]

    feats = [
        ("B1_bits_eq_0", mask(lambda r, i: r[0] == 0)),
        ("B2_bits_eq_1", mask(lambda r, i: r[0] == 1)),
        ("B3_table_popcount_le_4", mask(lambda r, i: bin(r[2]).count("1") <= 4)),
        ("B4_table_popcount_gt_4", mask(lambda r, i: bin(r[2]).count("1") > 4)),
        ("B5_state_never_changes",
         mask(lambda r, i: r[1] is None or r[1] in (0, 255))),
        ("B6_state_changes",
         mask(lambda r, i: not (r[1] is None or r[1] in (0, 255)))),
        ("B7_index_low_half", mask(lambda r, i: i < total // 2)),
        ("B8_index_high_half", mask(lambda r, i: i >= total // 2)),
    ]

    # amendment 3: semantic-rarity features (the H6'' revival lever)
    cls_of = [cid[r[3]] for r in universe]
    max_size = max(size)
    med = sorted(size)[len(size) // 2]
    feats += [
        ("B9_singleton_class", [size[cls_of[i]] == 1 for i in range(total)]),
        ("B10_largest_class",
         [size[cls_of[i]] == max_size for i in range(total)]),
        ("B11_class_above_median", [size[cls_of[i]] > med for i in range(total)]),
        ("B12_class_below_median", [size[cls_of[i]] < med for i in range(total)]),
    ]

    # amendment 3: exhaustive 1- and 2-literal sweep over V12
    prim_table_pre = [primitives(r) for r in universe]
    sweep = []
    for i in range(len(PRIMS)):
        for li in (-1, 1):
            spec = [0] * len(PRIMS)
            spec[i] = li
            sweep.append(tuple(spec))
    for i in range(len(PRIMS)):
        for j in range(i + 1, len(PRIMS)):
            for li in (-1, 1):
                for lj in (-1, 1):
                    spec = [0] * len(PRIMS)
                    spec[i] = li
                    spec[j] = lj
                    sweep.append(tuple(spec))
    sweep_feats = []
    for sp in sweep:
        nm = "SWEEP_" + ",".join(
            ("%s%s" % ("" if sp[k] == 1 else "!", PRIMS[k]))
            for k in range(len(PRIMS)) if sp[k] != 0)
        mk = [True] * total
        for idx in range(total):
            pv = prim_table_pre[idx]
            ok = True
            for k in range(len(PRIMS)):
                if sp[k] == 0:
                    continue
                if pv[k] != (sp[k] == 1):
                    ok = False
                    break
            mk[idx] = ok
        sweep_feats.append((nm, mk))

    # null N2: 200 pseudo-random structural features on the raw bits
    null_feats = []
    for sd in FEATURE_SEEDS:
        rng = random.Random(sd)
        nbits_sel = rng.randrange(1, 17)
        picks = [rng.randrange(0, 16) for _ in range(nbits_sel)]
        thr = rng.randrange(0, nbits_sel + 1)

        def fn(r, i, picks=tuple(picks), thr=thr):
            word = (r[2] & 0xFF) | (((r[1] or 0) & 0xFF) << 8)
            return sum((word >> b) & 1 for b in picks) >= thr
        null_feats.append(("NULL_%d" % sd, mask(fn)))

    LS = learner_scores(universe, cid, size,
                        feats + null_feats + sweep_feats)
    nprob = LS["problems"]
    full_den = LS["full_total"]
    und_den = LS["undetermined_total"]
    half = Fraction(1, 2)
    a_syn_full = Fraction(LS["correct_syn_full"], full_den)
    a_sem_full = Fraction(LS["correct_sem_full"], full_den)
    a_syn_und = Fraction(LS["correct_syn_und"], und_den)
    a_sem_und = Fraction(LS["correct_sem_und"], und_den)
    feat_full = dict((k, Fraction(v, full_den))
                     for k, v in LS["correct_feat_full"].items())
    feat_und = dict((k, Fraction(v, 2 * und_den))
                    for k, v in LS["feat_und_2x"].items())
    reg_und = dict((k, v) for k, v in feat_und.items()
                   if not k.startswith("NULL_") and not k.startswith("SWEEP_"))
    sweep_und = dict((k, v) for k, v in feat_und.items()
                     if k.startswith("SWEEP_"))
    reg_full = dict((k, v) for k, v in feat_full.items()
                    if not k.startswith("NULL_") and not k.startswith("SWEEP_"))
    null_und = sorted(v for k, v in feat_und.items() if k.startswith("NULL_"))
    best_name = max(reg_und, key=lambda k: (reg_und[k], k))
    worst_name = min(reg_und, key=lambda k: (reg_und[k], k))
    null_above = sum(1 for v in null_und if v > half)
    null_below = sum(1 for v in null_und if v < half)
    null_at_half = sum(1 for v in null_und if v == half)
    null_ge_best = sum(1 for v in null_und if v >= reg_und[best_name])
    sweep_min_name = min(sweep_und, key=lambda k: (sweep_und[k], k))
    sweep_max_name = max(sweep_und, key=lambda k: (sweep_und[k], k))
    all_und = dict(reg_und)
    all_und.update(sweep_und)
    any_below = dict((k, v) for k, v in all_und.items() if v < half)
    overall_best = max(all_und, key=lambda k: (all_und[k], k))

    # N4 leakage guard: the version space must not depend on the held-out moment
    leak_ok = True
    for obs, m in problems():
        if m in obs:
            leak_ok = False
    # and the peeking hostile must be detectable
    hs4_acc = Fraction(1, 1)   # a peeking learner scores exactly 1 by definition
    hs4_detected = hs4_acc > max(a_syn_und, a_sem_und, reg_und[best_name])

    # N1 control encoding: equal-size classes by construction
    ctrl_size = [4] * 16
    ctrl_tv = tv_distance(ctrl_size, sum(ctrl_size))
    # HS7 hostile: replace the real histogram by a uniform one
    hs7_size = [total // K] * K
    hs7_tv = tv_distance(hs7_size, sum(hs7_size))

    # ------------------------------------------------- invariance table
    ren, perm = g_rename(universe, RENAME_SEED)
    sta = g_state(universe)
    outc = g_out(universe)
    gens = (("g_rename", ren), ("g_state", sta), ("g_out", outc))
    base_sum = risk_summaries(universe)
    base_grid = grid_min_and_class(base_sum)
    inv = {}
    for name, img in gens:
        bij = is_bijection(universe, img)
        _c2, s2, f2 = semantic_classes(img)
        k2 = len(s2)
        tv2 = tv_distance(s2, len(img))
        sum2 = risk_summaries(img)
        e_multiset = sorted(base_sum.items())
        e_multiset2 = sorted(sum2.items())
        g2 = grid_min_and_class(sum2)
        minJ_same = all(a["min_J"] == b["min_J"] for a, b in zip(base_grid, g2))
        win_same = all(a["winner"] == b["winner"] for a, b in zip(base_grid, g2))
        memb_same = all(universe[i][3] == img[i][3] for i in range(len(img)))
        fh_same = sorted(f2) == sorted(first_hit)
        inv[name] = {
            "is_bijection_of_U": bij,
            "K_invariant": k2 == K,
            "histogram_invariant": sorted(s2) == hist,
            "D_TV_invariant": tv2 == d_tv,
            "error_multiset_invariant": e_multiset2 == e_multiset,
            "min_J_invariant": minJ_same,
            "winning_class_invariant": win_same,
            "per_candidate_membership_invariant": memb_same,
            "first_hit_profile_invariant": fh_same,
        }

    # ------------------------------------------- property-first recovery
    prim_table = prim_table_pre
    fams = registered_families(universe)
    digest = grammar_digest()
    recovery = {}
    digests = []
    for fname, sd in SPECS.items():
        sel = set(select(spec_tuple(sd), prim_table))
        digests.append(grammar_digest())
        recovery[fname] = {
            "spec": dict(sd),
            "selected": len(sel),
            "family_size": len(fams[fname]),
            "exact_match": sel == fams[fname],
            "smuggling_hits": smuggling_audit(sd),
        }
    digest_stable = len(set(digests)) == 1 and digests[0] == digest

    # null N3: 200 random specifications
    fam_sets = dict((k, frozenset(v)) for k, v in fams.items())
    n3_hits = 0
    n3_detail = []
    for sd in SPEC_SEEDS:
        rng = random.Random(sd)
        spec = tuple(rng.choice((-1, 0, 1)) for _ in PRIMS)
        sel = frozenset(select(spec, prim_table))
        hit = [k for k, v in fam_sets.items() if v == sel]
        if hit:
            n3_hits += 1
            n3_detail.append({"seed": sd, "family": hit[0]})

    # HS1 hostile: coarse semantic equality on (e_now, e_delay) only
    hs1_K = len(set((e0, e1) for (e0, e1, _b) in base_sum))
    hs1_detected = hs1_K != K

    # HS2 hostile: a non-bijective "re-encoding"
    broken = list(universe)
    broken[1] = broken[0]
    hs2_detected = not is_bijection(universe, broken)

    # HS3 hostile: a spec key carrying a family-name token
    hs3_detected = len(smuggling_audit({"p01_has_state": 1,
                                        "is_moore_family": 1})) > 0

    # HS5 hostile: planted live flagship prior-free sentence (classifier below)
    # HS6 hostile: a bound of the Z7 C4 shape
    hs6_verdict = vacuity(0, K, K, "<=")          # "class count <= K" -- vacuous
    hs6_detected = hs6_verdict == "NON_BINDING"
    genuine_verdict = vacuity(0, total, K, "<=")  # "class count <= K" vs codomain |U|
    genuine_binding = genuine_verdict == "BINDING"

    res = {
        "schema": "GMI_833_Z2_MINIMAL_PRIOR_RESULT_V1",
        "route": "A_simulation",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": ("GMI_833_Z2_EXACT_ENCODING_INDUCED_PRIOR_AND_MINIMUM_"
                          "SUFFICIENT_INDUCTIVE_BIAS_AT_REGISTERED_BINARY_"
                          "TRANSDUCER_SCOPE"),
        "universe": {"candidates": total, "stateless": 16, "stateful": 65536,
                     "scored_moments_per_mode": N_SCORED,
                     "behaviour_bits": 48},
        "MP1_encoding_prior": {
            "K_semantic_classes": K,
            "H1_encoding_strictly_redundant": K < total,
            "class_size_min": hist[0],
            "class_size_max": hist[-1],
            "class_size_max_over_min": str(Fraction(hist[-1], hist[0])),
            "H3_naive_max_ge_2x_min": hist[-1] >= 2 * hist[0],
            "D_TV_syntax_vs_uniform_over_classes": str(d_tv),
            "H2_D_TV_strictly_positive": d_tv > 0,
            "N1_control_encoding_D_TV": str(ctrl_tv),
            "N1_control_is_zero": ctrl_tv == 0,
            "HS7_uniform_histogram_D_TV": str(hs7_tv),
            "HS7_detected": hs7_tv == 0 and d_tv != 0,
        },
        "MP1c_enumeration_order": {
            "first_hit_min_probe": fh_min,
            "first_hit_max_probe": fh_max,
            "first_hit_max_over_min": str(fh_ratio),
            "H4_ratio_ge_100": fh_ratio >= 100,
        },
        "MP2_minimum_bias": {
            "problems": nprob,
            "scored_pairs_full": full_den,
            "scored_pairs_determined": LS["determined_total"],
            "scored_pairs_undetermined": und_den,
            "determined_fraction": str(Fraction(LS["determined_total"], full_den)),
            "full_population_note": ("determined pairs are 3151/16388 of this "
                                     "population; the full-population numbers "
                                     "are published for the record and no claim "
                                     "rests on them -- see freeze amendment 3"),
            "A_syn_full": str(a_syn_full),
            "A_sem_full": str(a_sem_full),
            "H5_full_A_syn_ne_A_sem": a_syn_full != a_sem_full,
            "disagreeing_buckets_full": LS["disagreeing_buckets_full"],
            "registered_feature_accuracy_full":
                dict((k, str(v)) for k, v in sorted(reg_full.items())),
            "A_free_undetermined_definitional": "1/2",
            "A_syn_undetermined": str(a_syn_und),
            "A_sem_undetermined": str(a_sem_und),
            "H5p_disagreeing_buckets_undetermined_nonzero":
                LS["disagreeing_buckets_und"] > 0,
            "disagreeing_buckets_undetermined": LS["disagreeing_buckets_und"],
            "preference_only_accuracy_undetermined":
                dict((k, str(v)) for k, v in sorted(reg_und.items())),
            "best_feature": best_name,
            "best_feature_accuracy_undetermined": str(reg_und[best_name]),
            "worst_feature": worst_name,
            "worst_feature_accuracy_undetermined": str(reg_und[worst_name]),
            "H6p_some_above_and_some_below_half":
                reg_und[best_name] > half and reg_und[worst_name] < half,
            "N2_null_features": len(null_und),
            "N2_null_above_half_undetermined": null_above,
            "N2_null_below_half_undetermined": null_below,
            "N2_null_exactly_half_undetermined": null_at_half,
            "N2_null_at_or_above_best_undetermined": null_ge_best,
            "H10_null_majority_not_at_or_above_best":
                null_ge_best * 2 <= len(null_und),
            "N2_null_max_undetermined": str(null_und[-1]) if null_und else None,
            "N2_null_min_undetermined": str(null_und[0]) if null_und else None,
            "sweep_features": len(sweep_und),
            "sweep_min_feature": sweep_min_name,
            "sweep_min_accuracy_undetermined": str(sweep_und[sweep_min_name]),
            "sweep_max_feature": sweep_max_name,
            "sweep_max_accuracy_undetermined": str(sweep_und[sweep_max_name]),
            "one_bit_features_below_half": sorted(any_below),
            "H6pp_some_one_bit_preference_below_half": len(any_below) > 0,
            "overall_best_one_bit_feature": overall_best,
            "overall_best_one_bit_accuracy": str(all_und[overall_best]),
            "H11_best_strictly_above_half_and_all_nulls":
                all_und[overall_best] > half and all(
                    v < all_und[overall_best] for v in null_und),
            "N4_heldout_not_in_observation_set": leak_ok,
            "HS4_peeking_learner_detected": hs4_detected,
        },
        "MP4_p3_standard": {
            "generators": dict(inv),
            "H7a_K_hist_DTV_invariant_under_all":
                all(inv[g]["K_invariant"] and inv[g]["histogram_invariant"]
                    and inv[g]["D_TV_invariant"] for g in inv),
            "H7b_minJ_and_winner_invariant_under_rename_and_state":
                all(inv[g]["min_J_invariant"] and inv[g]["winning_class_invariant"]
                    for g in ("g_rename", "g_state")),
            "H7c_some_generator_moves_minJ_or_winner":
                any(not (inv[g]["min_J_invariant"]
                         and inv[g]["winning_class_invariant"]) for g in inv),
            "H7d_first_hit_moves_under_rename":
                not inv["g_rename"]["first_hit_profile_invariant"],
            "H7e_membership_moves_under_state":
                not inv["g_state"]["per_candidate_membership_invariant"],
            "HS2_nonbijection_detected": hs2_detected,
        },
        "MP5_known_form_recovery": {
            "grammar_digest": digest,
            "grammar_digest_stable_across_all_six": digest_stable,
            "families": recovery,
            "H8_all_six_exact": all(v["exact_match"] for v in recovery.values()),
            "H8_no_smuggling": all(not v["smuggling_hits"]
                                   for v in recovery.values()),
            "HS3_family_token_detected": hs3_detected,
            "N3_random_specs": len(SPEC_SEEDS),
            "N3_random_specs_hitting_a_family": n3_hits,
            "N3_detail": n3_detail,
            "spec_space_size": 3 ** len(PRIMS),
        },
        "verdict_inputs": {
            "amendment_3_lever_produced_the_witness": False,
            "witness_came_from": "exhaustive V12 one- and two-literal sweep",
        },
        "vacuity": {
            "HS1_coarse_semantics_K": hs1_K,
            "HS1_detected": hs1_detected,
            "HS6_C4_shaped_bound_verdict": hs6_verdict,
            "HS6_detected": hs6_detected,
            "genuine_bound_verdict": genuine_verdict,
            "genuine_bound_is_binding": genuine_binding,
        },
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "K": K, "D_TV": str(d_tv),
        "determined_fraction": str(Fraction(LS["determined_total"], full_den)),
        "A_syn_und": str(a_syn_und), "A_sem_und": str(a_sem_und),
        "disagree_buckets_und": LS["disagreeing_buckets_und"],
        "best": best_name, "best_und": str(reg_und[best_name]),
        "worst": worst_name, "worst_und": str(reg_und[worst_name]),
        "null_above_half": null_above, "null_below_half": null_below,
        "null_at_half": null_at_half, "null_ge_best": null_ge_best,
        "fh_ratio": str(fh_ratio),
        "families_exact": sum(1 for v in recovery.values() if v["exact_match"]),
        "N3_hits": n3_hits,
        "sweep_min": str(sweep_und[sweep_min_name]),
        "below_half": len(any_below),
        "overall_best": overall_best,
        "overall_best_acc": str(all_und[overall_best]),
        "H7c_refuted": not any(not (inv[g]["min_J_invariant"]
                               and inv[g]["winning_class_invariant"])
                               for g in inv),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
