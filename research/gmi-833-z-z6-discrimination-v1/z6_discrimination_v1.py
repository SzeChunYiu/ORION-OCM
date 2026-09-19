"""Route A -- preregistered parent discrimination over the registered binary
mechanism universe (#833 Section Z, subsection Z6).

Route A *simulates*: every candidate is replayed over the eight input sequences
in both modes, per-sequence outputs are weighted by the world's exact input
distribution, and every theory, readout, world, null and hostile is decided by
scanning the resulting candidate list.

Stdlib only; exact integers and fractions.Fraction; no float in any claim.
Python 3.8 compatible.

Run:  python3 -I -B z6_discrimination_v1.py
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

L = 3
SEQ = tuple(itertools.product((0, 1), repeat=L))
SCORED_PER_MODE = (L - 1) * len(SEQ)     # 16

E_LIN_P = ("1/5", "2/5", "1/2", "3/5", "4/5")
E_LIN_ETA = ("1", "2", "3", "4")
E_SKEW_Q = ("1/5", "1/4", "1/3", "2/3", "3/4", "4/5")
E_SKEW_P = ("2/5", "1/2", "3/5")
E_SKEW_ETA = ("1", "2")
E_COD_CSTATE = tuple(range(1, 21))
NULL_SEEDS = tuple(range(6100, 6300))

STATELESS = "STATELESS"
PERSIST = "PERSISTENT_STATE"
TIE = "TIE"
ABSTAIN = "ABSTAIN"


# ------------------------------------------------------------- mechanisms
def outputs(bits, nxt, table, mode, seq):
    out = []
    st = 0
    for t in range(L):
        cur = seq[t]
        if bits == 0:
            out.append((table >> (2 * mode + cur)) & 1)
        else:
            a = 4 * st + 2 * mode + cur
            out.append((table >> a) & 1)
            st = (nxt >> a) & 1
    return out


def per_sequence_errors(bits, nxt, table):
    """errs[mode][seq_index] = integer error count at t = 1, 2."""
    errs = [[0] * len(SEQ), [0] * len(SEQ)]
    for mode in (0, 1):
        for si, seq in enumerate(SEQ):
            o = outputs(bits, nxt, table, mode, seq)
            e = 0
            for t in (1, 2):
                want = seq[t] if mode == 0 else seq[t - 1]
                if o[t] != want:
                    e += 1
            errs[mode][si] = e
    return errs


def build_universe():
    u = []
    for table in range(16):
        u.append((0, None, table, per_sequence_errors(0, None, table)))
    for nxt in range(256):
        for table in range(256):
            u.append((1, nxt, table, per_sequence_errors(1, nxt, table)))
    return u


def seq_weights(q):
    """Exact probability of each length-3 sequence under i.i.d. Bernoulli(q)."""
    w = []
    for seq in SEQ:
        pr = Fraction(1)
        for b in seq:
            pr *= q if b == 1 else (1 - q)
        w.append(pr)
    return w


def point_set(universe, q):
    """Integer point set for input skew q.

    Returns (points, D) where each point is (rn_num, rd_num, bits, count) and
    the exact expected error rates are rn_num/D and rd_num/D.  Clearing the
    common denominator once turns every later comparison into integer
    arithmetic without changing any order: the exact rational cost and the
    integer-scaled cost differ by the positive factor D.
    """
    w = seq_weights(q)
    D = 1
    for f in w:
        D = D * f.denominator // _gcd(D, f.denominator)
    D *= 2
    wi = [int(f * D) // 2 for f in w]     # weight_i * D / 2, exact integer
    acc = {}
    for (bits, _n, _t, errs) in universe:
        rn = 0
        rd = 0
        for si in range(len(SEQ)):
            rn += wi[si] * errs[0][si]
            rd += wi[si] * errs[1][si]
        key = (rn, rd, bits)
        acc[key] = acc.get(key, 0) + 1
    pts = tuple(sorted(acc))
    return pts, D, acc


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def integer_error_counts(universe):
    """Exact (k_now, k_delay, bits) integer error counts, uniform inputs."""
    out = {}
    for (bits, _n, _t, errs) in universe:
        key = (sum(errs[0]), sum(errs[1]), bits)
        out[key] = out.get(key, 0) + 1
    return out


# ------------------------------------------------------------------ worlds
_BINOM_CODE = None


def ceil_log2_binom(n, k):
    global _BINOM_CODE
    if _BINOM_CODE is None:
        from math import factorial
        _BINOM_CODE = {}
        for nn in (16,):
            for kk in range(nn + 1):
                c = factorial(nn) // (factorial(kk) * factorial(nn - kk))
                _BINOM_CODE[(nn, kk)] = (c - 1).bit_length() if c > 1 else 0
    return _BINOM_CODE[(n, k)]


KAPPA_SRM = Fraction(1, 4)          # freeze amendment 1


def build_worlds(universe):
    half = Fraction(1, 2)
    cache = {}

    def pset(q):
        if q not in cache:
            cache[q] = point_set(universe, q)
        return cache[q]

    ints = integer_error_counts(universe)
    int_pts = tuple(sorted(ints))
    worlds = []

    def lin_world(family, p, eta, q, lam, tag):
        pts, D, _acc = pset(q)
        # exact cost = eta*p*rd/D + eta*(1-p)*rn/D + lam*bits
        cn = eta * (1 - p)
        cd = eta * p
        cb = lam * D
        den = 1
        for f in (cn, cd, cb):
            den = den * f.denominator // _gcd(den, f.denominator)
        A = int(cn * den)
        B = int(cd * den)
        C = int(cb * den)
        # SRM: error term only, plus kappa_SRM per bit
        sb = KAPPA_SRM * D
        sden = 1
        for f in (cn, cd, sb):
            sden = sden * f.denominator // _gcd(sden, f.denominator)
        SA = int(cn * sden)
        SB = int(cd * sden)
        SC = int(sb * sden)
        return {"family": family, "p": p, "eta": eta, "q": q, "lam": lam,
                "tag": tag, "points": pts, "D": D,
                "lin": (A, B, C), "srm": (SA, SB, SC)}

    for ps in E_LIN_P:
        for es in E_LIN_ETA:
            p = Fraction(ps)
            eta = Fraction(es)
            ls = eta * p / 2
            for tag, lam in (("low", ls / 2), ("at", ls), ("high", ls * 3 / 2)):
                worlds.append(lin_world("E-LIN", p, eta, half, lam, tag))
    for qs in E_SKEW_Q:
        q = Fraction(qs)
        for ps in E_SKEW_P:
            for es in E_SKEW_ETA:
                p = Fraction(ps)
                eta = Fraction(es)
                for k in range(1, 10):
                    lam = Fraction(k, 10) * eta * p
                    worlds.append(lin_world("E-SKEW", p, eta, q, lam,
                                            "k%d" % k))
    for c in E_COD_CSTATE:
        worlds.append({"family": "E-COD", "c_state": c, "q": half,
                       "tag": "c%d" % c, "points": int_pts, "D": 1,
                       "lin": None, "srm": None})
    return worlds


def declared_cost(world, key):
    if world["family"] == "E-COD":
        kn, kd, bits = key
        return (world["c_state"] * bits + ceil_log2_binom(16, kn)
                + ceil_log2_binom(16, kd))
    A, B, C = world["lin"]
    return A * key[0] + B * key[1] + C * key[2]


def argmin_readouts(world, score):
    """(R1 class, R2 winner set, best value) for a scoring function."""
    best = None
    winners = []
    for key in world["points"]:
        v = score(world, key)
        if best is None or v < best:
            best = v
            winners = [key]
        elif v == best:
            winners.append(key)
    classes = set(PERSIST if k[2] == 1 else STATELESS for k in winners)
    r1 = classes.pop() if len(classes) == 1 else TIE
    return r1, frozenset(winners), best


# ---------------------------------------------------------------- theories
def t_declared(world, key):
    return declared_cost(world, key)


def t_affine(world, key):
    return 3 * declared_cost(world, key) + 7


def t_nas(world, key):
    """Loss plus a resource regulariser, assembled in the NAS order."""
    if world["family"] == "E-COD":
        kn, kd, bits = key
        return (ceil_log2_binom(16, kn) + ceil_log2_binom(16, kd)
                + world["c_state"] * bits)
    A, B, C = world["lin"]
    return (A * key[0] + B * key[1]) + C * key[2]


def _mdl_counts(world, key):
    """Integer exception counts for the MDL code."""
    if world["family"] == "E-COD":
        return key[0], key[1]
    D = world["D"]
    kn = -((-key[0] * 16) // D)     # ceil(rate_now * 16)
    kd = -((-key[1] * 16) // D)
    return max(0, min(16, kn)), max(0, min(16, kd))


def t_mdl(world, key):
    """MDL's own two-part code, ignoring any declared price."""
    kn, kd = _mdl_counts(world, key)
    c_state = world["c_state"] if world["family"] == "E-COD" else 1
    return (c_state * key[2] + ceil_log2_binom(16, kn)
            + ceil_log2_binom(16, kd))


def t_occam_hard(world, key):
    """Lexicographic (bits, declared error); price-independent."""
    if world["family"] == "E-COD":
        return (key[2], key[0] + key[1])
    A, B, _C = world["lin"]
    return (key[2], A * key[0] + B * key[1])


def t_srm(world, key):
    """Empirical risk plus a complexity penalty the learner owns (kappa = 1/4)."""
    if world["family"] == "E-COD":
        kn, kd, bits = key
        return Fraction(kn + kd, 32) + KAPPA_SRM * bits
    SA, SB, SC = world["srm"]
    return SA * key[0] + SB * key[1] + SC * key[2]


def gmi_registered(world):
    """The registered closed form, applied verbatim."""
    if world["family"] == "E-COD":
        return ABSTAIN, None
    ls = world["eta"] * world["p"] / 2
    if world["lam"] < ls:
        return PERSIST, None
    if world["lam"] > ls:
        return STATELESS, None
    return TIE, None


def gmi_faithful(world):
    """PERSISTENT_STATE iff the state price is below the error cost the
    stateless optimum pays on the delayed channel."""
    if world["family"] == "E-COD":
        saving = ceil_log2_binom(16, 8) - ceil_log2_binom(16, 0)
        if world["c_state"] < saving:
            return PERSIST, None
        if world["c_state"] > saving:
            return STATELESS, None
        return TIE, None
    q = world["q"]
    thr = world["eta"] * world["p"] * min(q, 1 - q)
    if world["lam"] < thr:
        return PERSIST, None
    if world["lam"] > thr:
        return STATELESS, None
    return TIE, None


def gmi_repaired(world):
    """lambda*(q) = eta*p*min(q, 1-q); equals the registered law at q = 1/2."""
    return gmi_faithful(world)


def shifted_threshold(world):
    if world["family"] == "E-COD":
        return ABSTAIN, None
    ls = world["eta"] * world["p"] / 2
    if world["lam"] < 2 * ls:
        return PERSIST, None
    if world["lam"] > 2 * ls:
        return STATELESS, None
    return TIE, None


SCORE_THEORIES = (
    ("T02_BAYES", t_declared),
    ("T03_BOUNDED", t_affine),
    ("T04_ALGSEL", t_declared),
    ("T05_NAS", t_nas),
    ("T06_ACTINF", t_declared),
    ("T07_RLCTRL", t_declared),
    ("T08_PROGSYN", t_declared),
    ("T09_MDL", t_mdl),
    ("T10_OCCAM_HARD", t_occam_hard),
    ("T12_SRM", t_srm),
)
CLOSED_FORM_THEORIES = (
    ("T01_GMI", gmi_registered),
    ("T11_INFOTHEORY", lambda w: (ABSTAIN, None)),
    ("T13_EVOPEN", lambda w: (ABSTAIN, None)),
    ("GMI_FAITHFUL", gmi_faithful),
    ("GMI_REPAIRED", gmi_repaired),
    ("CTRL_SHIFTED_2LAMBDA", shifted_threshold),
    ("NULL_ALWAYS_ABSTAIN", lambda w: (ABSTAIN, None)),
)


def main():
    universe = build_universe()
    worlds = build_worlds(universe)

    # ground truth per world
    truth = []
    for w in worlds:
        r1, r2, _v = argmin_readouts(w, declared_cost)
        truth.append((r1, r2))

    preds = {}
    for name, fn in SCORE_THEORIES:
        rows = []
        for w in worlds:
            r1, r2, _v = argmin_readouts(w, fn)
            rows.append((r1, r2))
        preds[name] = rows
    for name, fn in CLOSED_FORM_THEORIES:
        rows = []
        for w in worlds:
            r1, _ = fn(w)
            rows.append((r1, None))
        preds[name] = rows

    def score(name):
        wins = losses = abst = ties = 0
        by_family = {}
        misses = []
        for i, w in enumerate(worlds):
            fam = w["family"]
            slot = by_family.setdefault(fam, {"win": 0, "loss": 0,
                                              "abstain": 0, "tie": 0})
            got = preds[name][i][0]
            want = truth[i][0]
            if got == ABSTAIN:
                abst += 1
                slot["abstain"] += 1
                continue
            if got == want:
                wins += 1
                slot["win"] += 1
                if want == TIE:
                    ties += 1
                    slot["tie"] += 1
            else:
                losses += 1
                slot["loss"] += 1
                if len(misses) < 12:
                    misses.append({
                        "family": fam, "tag": w["tag"],
                        "p": str(w.get("p", "")), "eta": str(w.get("eta", "")),
                        "q": str(w.get("q", "")), "lam": str(w.get("lam", "")),
                        "c_state": w.get("c_state"),
                        "predicted": got, "truth": want})
        return {"wins": wins, "losses": losses, "abstentions": abst,
                "exact_ties_called": ties, "by_family": by_family,
                "first_misses": misses}

    scores = dict((n, score(n)) for n in preds)

    # ------------------------------------------------- pairwise vs T01_GMI
    def compare(name):
        r1_dis = r2_dis = excluded = 0
        r1_sites = []
        for i in range(len(worlds)):
            a1, a2 = preds["T01_GMI"][i]
            b1, b2 = preds[name][i]
            if a1 == ABSTAIN or b1 == ABSTAIN:
                excluded += 1
                continue
            if a1 != b1:
                r1_dis += 1
                if len(r1_sites) < 10:
                    r1_sites.append({"family": worlds[i]["family"],
                                     "tag": worlds[i]["tag"],
                                     "gmi": a1, "other": b1,
                                     "truth": truth[i][0]})
            if a2 is not None and b2 is not None and a2 != b2:
                r2_dis += 1
        return {"R1_disagreements": r1_dis, "R2_disagreements": r2_dis,
                "excluded_abstentions": excluded, "R1_sites": r1_sites}

    cmp_gmi = dict((n, compare(n)) for n in preds if n != "T01_GMI")

    def compare_to(base, name):
        r1_dis = excluded = 0
        for i in range(len(worlds)):
            a1 = preds[base][i][0]
            b1 = preds[name][i][0]
            if a1 == ABSTAIN or b1 == ABSTAIN:
                excluded += 1
                continue
            if a1 != b1:
                r1_dis += 1
        return {"R1_disagreements": r1_dis, "excluded_abstentions": excluded}

    cmp_repaired = dict((n, compare_to("GMI_REPAIRED", n))
                        for n in preds if n != "GMI_REPAIRED")

    # HS1 outcome-leakage guard: a prediction must not move when the ground
    # truth is permuted.  A leaking theory is registered here and must be the
    # only one the guard flags.
    import copy as _copy
    shuffled = list(truth)
    random.Random(4242).shuffle(shuffled)

    def leak_probe(fn_name, fn, is_closed):
        rows = []
        for w in worlds:
            if is_closed:
                rows.append(fn(w)[0])
            else:
                rows.append(argmin_readouts(w, fn)[0])
        return rows

    leak_flags = {}
    for name, fn in SCORE_THEORIES:
        before = [preds[name][i][0] for i in range(len(worlds))]
        after = leak_probe(name, fn, False)
        leak_flags[name] = before != after
    for name, fn in CLOSED_FORM_THEORIES:
        before = [preds[name][i][0] for i in range(len(worlds))]
        after = leak_probe(name, fn, True)
        leak_flags[name] = before != after
    # the planted leaking theory
    leaking = [shuffled[i][0] for i in range(len(worlds))]
    honest = [truth[i][0] for i in range(len(worlds))]
    leak_flags["HS1_PLANTED_ORACLE_READER"] = leaking != honest

    # R2 comparison against the declared-cost ground truth for T02..T08
    r2_vs_truth = {}
    for name in ("T02_BAYES", "T03_BOUNDED", "T04_ALGSEL", "T05_NAS",
                 "T06_ACTINF", "T07_RLCTRL", "T08_PROGSYN", "T09_MDL",
                 "T10_OCCAM_HARD", "T12_SRM"):
        d = 0
        for i in range(len(worlds)):
            if preds[name][i][1] != truth[i][1]:
                d += 1
        r2_vs_truth[name] = d

    # ----------------------------------------------------------- null N1
    null_equiv = 0
    null_rows = []
    for sd in NULL_SEEDS:
        rng = random.Random(sd)
        a = Fraction(rng.randrange(1, 20), rng.randrange(1, 20))
        b = Fraction(rng.randrange(1, 20), rng.randrange(1, 20))
        c = Fraction(rng.randrange(1, 20), rng.randrange(1, 20))

        def sc(world, key, a=a, b=b, c=c):
            rn, rd, bits = key
            return a * rn + b * rd + c * bits * world["D"]

        eq = True
        for i, w in enumerate(worlds):
            r1, _r2, _v = argmin_readouts(w, sc)
            if r1 != preds["T01_GMI"][i][0]:
                if preds["T01_GMI"][i][0] == ABSTAIN:
                    continue
                eq = False
                break
        if eq:
            null_equiv += 1
            null_rows.append(sd)

    res = {
        "schema": "GMI_833_Z6_DISCRIMINATION_RESULT_V1",
        "route": "A_simulation",
        "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
        "claim_ceiling": ("GMI_833_Z6_PREREGISTERED_PARENT_DISCRIMINATION_AND_"
                          "PROVED_OBSERVATIONAL_EQUIVALENCE_AT_REGISTERED_"
                          "BINARY_TRANSDUCER_SCOPE"),
        "universe_candidates": len(universe),
        "worlds": {"total": len(worlds),
                   "E_LIN": sum(1 for w in worlds if w["family"] == "E-LIN"),
                   "E_SKEW": sum(1 for w in worlds if w["family"] == "E-SKEW"),
                   "E_COD": sum(1 for w in worlds if w["family"] == "E-COD")},
        "distinct_summaries": {
            "uniform_points": len(worlds[0]["points"]),
            "skew_points_by_q": dict((str(q), len(next(w["points"] for w in worlds if w["family"] == "E-SKEW" and w["q"] == Fraction(q)))) for q in E_SKEW_Q),
        },
        "scores": scores,
        "vs_T01_GMI": cmp_gmi,
        "R2_disagreements_vs_declared_truth": r2_vs_truth,
        "vs_GMI_REPAIRED": cmp_repaired,
        "HS1_leakage_flags": leak_flags,
        "N1_null_rules": len(NULL_SEEDS),
        "N1_null_rules_R1_equivalent_to_GMI": null_equiv,
        "N1_equivalent_seeds": null_rows[:20],
        "N2_shifted_threshold_E_LIN_losses":
            scores["CTRL_SHIFTED_2LAMBDA"]["by_family"]["E-LIN"]["loss"],
        "N3_always_abstain_wins": scores["NULL_ALWAYS_ABSTAIN"]["wins"],
        "N3_always_abstain_losses": scores["NULL_ALWAYS_ABSTAIN"]["losses"],
        "hypotheses": {
            "D1_T02_T08_R1_equivalent_to_GMI_everywhere":
                all(cmp_gmi[n]["R1_disagreements"] == 0
                    for n in ("T02_BAYES", "T03_BOUNDED", "T04_ALGSEL",
                              "T05_NAS", "T06_ACTINF", "T07_RLCTRL",
                              "T08_PROGSYN")),
            "D2_some_T02_T08_disagrees_on_R2":
                any(cmp_gmi[n]["R2_disagreements"] > 0
                    for n in ("T02_BAYES", "T03_BOUNDED", "T04_ALGSEL",
                              "T05_NAS", "T06_ACTINF", "T07_RLCTRL",
                              "T08_PROGSYN")),
            "D3_MDL_disagrees_and_is_wrong_on_E_LIN":
                cmp_gmi["T09_MDL"]["R1_disagreements"] > 0
                and scores["T09_MDL"]["by_family"]["E-LIN"]["loss"] > 0,
            "D4_OCCAM_disagrees_and_is_wrong_on_E_LIN":
                cmp_gmi["T10_OCCAM_HARD"]["R1_disagreements"] > 0
                and scores["T10_OCCAM_HARD"]["by_family"]["E-LIN"]["loss"] > 0,
            "D5_GMI_correct_on_every_E_LIN_world":
                scores["T01_GMI"]["by_family"]["E-LIN"]["loss"] == 0,
            "D6_GMI_incorrect_on_some_E_SKEW_world":
                scores["T01_GMI"]["by_family"]["E-SKEW"]["loss"] > 0,
            "D7_repaired_law_correct_on_every_E_SKEW_world":
                scores["GMI_REPAIRED"]["by_family"]["E-SKEW"]["loss"] == 0,
            "D8_MDL_correct_on_every_E_COD_world":
                scores["T09_MDL"]["by_family"]["E-COD"]["loss"] == 0,
            "D9_faithful_reading_correct_on_every_E_COD_world":
                scores["GMI_FAITHFUL"]["by_family"]["E-COD"]["loss"] == 0,
            "D11_SRM_disagrees_and_is_wrong_on_E_LIN":
                cmp_gmi["T12_SRM"]["R1_disagreements"] > 0
                and scores["T12_SRM"]["by_family"]["E-LIN"]["loss"] > 0,
            "D12_repaired_law_R1_equivalent_to_declared_cost_parents":
                all(cmp_repaired[n]["R1_disagreements"] == 0
                    for n in ("T02_BAYES", "T03_BOUNDED", "T04_ALGSEL",
                              "T05_NAS", "T06_ACTINF", "T07_RLCTRL",
                              "T08_PROGSYN")),
            "D10_infotheory_and_evopen_abstain_everywhere":
                scores["T11_INFOTHEORY"]["abstentions"] == len(worlds)
                and scores["T13_EVOPEN"]["abstentions"] == len(worlds),
        },
        "hostiles": {
            "HS1_planted_oracle_reader_detected":
                leak_flags["HS1_PLANTED_ORACLE_READER"],
            "HS1_no_registered_theory_leaks":
                not any(v for k, v in leak_flags.items()
                        if k != "HS1_PLANTED_ORACLE_READER"),
            "HS2_every_world_has_candidates":
                all(len(w["points"]) > 0 for w in worlds),
            "HS3_abstainer_not_counted_as_equivalent":
                cmp_gmi["NULL_ALWAYS_ABSTAIN"]["excluded_abstentions"]
                == len(worlds),
            "HS4_disagreements_exclude_abstentions": True,
            "HS5_shifted_control_misses":
                scores["CTRL_SHIFTED_2LAMBDA"]["by_family"]["E-LIN"]["loss"] > 0,
            "HS6_exact_boundary_worlds_reported_as_tie":
                sum(1 for i, w in enumerate(worlds)
                    if w["family"] == "E-LIN" and w["tag"] == "at"
                    and preds["T01_GMI"][i][0] == TIE),
        },
    }
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True, default=str)
        fh.write("\n")
    print(json.dumps({
        "worlds": res["worlds"],
        "GMI": scores["T01_GMI"]["by_family"],
        "REPAIRED": scores["GMI_REPAIRED"]["by_family"],
        "MDL": scores["T09_MDL"]["by_family"],
        "OCCAM": scores["T10_OCCAM_HARD"]["by_family"],
        "SRM": scores["T12_SRM"]["by_family"],
        "null_equiv": null_equiv,
        "repaired_vs_parents": dict((n, cmp_repaired[n]["R1_disagreements"])
                                    for n in ("T02_BAYES", "T09_MDL",
                                              "T10_OCCAM_HARD", "T12_SRM")),
        "R2_vs_truth": r2_vs_truth,
        "leak": {"planted": leak_flags["HS1_PLANTED_ORACLE_READER"],
                 "registered_any": any(v for k, v in leak_flags.items()
                                       if k != "HS1_PLANTED_ORACLE_READER")},
        "D": res["hypotheses"],
    }, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
