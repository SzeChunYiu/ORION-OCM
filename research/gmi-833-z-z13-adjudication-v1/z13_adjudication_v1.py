"""Route A -- adjudication of the frozen prediction Z13-P1 (#833 Section Z, Z13).

Route A works by *next-state enumeration with per-address majority outputs*:
for each next-state function the error-minimising output table is read off
directly, and channel optima, thresholds and property scores follow from that.
Route B (independent_z13_oracle_v1.py) never does this: it enumerates the full
(output table, next-state) product where that is feasible, witnesses the b=2
optima constructively against a trivial lower bound, and recomputes every
threshold by scanning an exact lambda grid rather than by differencing E.

Protocol is fixed by FREEZE_V1.md and FREEZE_V1_AMENDMENT_1.md, both committed
before this file existed.

Stdlib only; exact integers and fractions.Fraction; no float in any claim.
Python 3.8 compatible.

Run:  python3 -I -B z13_adjudication_v1.py
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

L = 4
SEQ = tuple(itertools.product((0, 1), repeat=L))
WINDOW = (2, 3)                       # declared common scored window
MODES = (0, 1, 2)
NSCORED = len(SEQ) * len(WINDOW)      # 32
BUDGETS = (0, 1, 2)

ETAS = (1, 2, 3)
PDEN = 8                              # declared world grid denominator


# --------------------------------------------------------------- mechanics
def n_states(b):
    return 2 ** b


def n_addr(b):
    return n_states(b) * 2


def simulate_errors(b, out, nxt, m, window=WINDOW, seqs=SEQ, length=L):
    """Exact integer error count of one mode channel."""
    e = 0
    for seq in seqs:
        st = 0
        for t in range(length):
            cur = seq[t]
            a = st * 2 + cur
            if t in window:
                if out[a] != seq[t - m]:
                    e += 1
            st = nxt[a]
    return e


def majority_errors(b, nxt, m, window=WINDOW, seqs=SEQ, length=L):
    """Min error over ALL output tables for this next-state function, plus the
    set of optimal output tables.  Per-address majority (MAJORITY-OPTIMALITY)."""
    tal = [[0, 0] for _ in range(n_addr(b))]
    for seq in seqs:
        st = 0
        for t in range(length):
            cur = seq[t]
            a = st * 2 + cur
            if t in window:
                tal[a][seq[t - m]] += 1
            st = nxt[a]
    err = 0
    choices = []
    for a in range(n_addr(b)):
        z, o = tal[a]
        err += min(z, o)
        if z < o:
            choices.append((1,))
        elif o < z:
            choices.append((0,))
        else:
            choices.append((0, 1))
    tables = [tuple(c) for c in itertools.product(*choices)]
    return err, tables


def all_nxt(b):
    if b == 0:
        return [tuple([0] * n_addr(0))]
    return [tuple(t) for t in itertools.product(range(n_states(b)), repeat=n_addr(b))]


def channel_optimum(b, m, collect=True):
    """(min error, [(nxt, out), ...] optimal configurations).

    At b = 2 the optimal-configuration set is astronomically large (unvisited
    addresses are free), so only a single witness is retained there; the error
    value is still exact and exhaustive over next-state functions.
    """
    best = None
    cfgs = []
    for nxt in all_nxt(b):
        e, tables = majority_errors(b, nxt, m)
        if best is None or e < best:
            best = e
            cfgs = [(nxt, tables[0])] if not collect else [(nxt, t) for t in tables]
        elif e == best and collect:
            cfgs.extend((nxt, t) for t in tables)
    return best, cfgs


# ----------------------------------------------------------- universe size
def universe_size(b):
    """Exact count of (out, nxt) triples over the three modes."""
    per_mode = (2 ** n_addr(b)) * (n_states(b) ** n_addr(b))
    return per_mode ** 3


# ----------------------------------------------------------------- worlds
def worlds():
    out = []
    for a in range(PDEN + 1):
        for bb in range(PDEN + 1 - a):
            c = PDEN - a - bb
            p = (Fraction(a, PDEN), Fraction(bb, PDEN), Fraction(c, PDEN))
            for eta in ETAS:
                out.append((eta, p))
    return out


def E_profile(R, eta, p):
    """E(b) = eta * sum_m p_m * R[(b,m)] for each budget."""
    return dict((b, eta * sum(p[m] * R[(b, m)] for m in MODES)) for b in BUDGETS)


def argmin_budgets(E, lam):
    best = None
    arg = []
    for b in BUDGETS:
        c = E[b] + lam * b
        if best is None or c < best:
            best, arg = c, [b]
        elif c == best:
            arg.append(b)
    return best, arg


# ------------------------------------------------------------- properties
DETERMINED = {}


def determined_modes(b):
    if b in DETERMINED:
        return DETERMINED[b]
    det = []
    for m in MODES:
        seen = set()
        for nx in all_nxt(b):
            seen.add(majority_errors(b, nx, m)[0])
            if len(seen) > 1:
                break
        if len(seen) > 1:
            det.append(m)
    DETERMINED[b] = det
    return det


def props(b, cfg_by_mode, R):
    """cfg_by_mode[m] = (nxt, out).  Returns the property record."""
    pa_modes = []
    for m in MODES:
        nxt, out = cfg_by_mode[m]
        dep_state = any(out[0 * 2 + c] != out[1 * 2 + c] for c in (0, 1)) if b >= 1 else False
        dep_input = any(out[s * 2 + 0] != out[s * 2 + 1] for s in range(n_states(b)))
        pa_modes.append(bool(dep_state and dep_input))
    ident = dict((m, all(cfg_by_mode[m][0][s * 2 + c] == c
                         for s in range(n_states(b)) for c in (0, 1))) for m in MODES)
    r = dict((m, Fraction(simulate_errors(b, cfg_by_mode[m][1], cfg_by_mode[m][0], m), NSCORED))
             for m in MODES)
    pb_all = all(ident[m] for m in MODES)
    det = determined_modes(b)
    pb_det = all(ident[m] for m in det) if det else pb_all
    pc = (r[0] == 0 and r[1] == 0 and r[2] > 0 and r[2] == R[(1, 2)]) if b == 1 else False
    return {"P_a_modes": pa_modes, "P_a": any(pa_modes),
            "P_b_all": pb_all, "P_b_determined": pb_det,
            "determined_modes": det,
            "identity_next_by_mode": dict((str(m), ident[m]) for m in MODES),
            "P_c": pc,
            "r": dict((str(m), str(r[m])) for m in MODES)}


def families(b, cfg_by_mode):
    fam = set()
    if b == 0:
        fam.add("F_STATELESS")
    ns = n_states(b)
    if b >= 1 and all(cfg_by_mode[m][1][0 * 2 + c] == cfg_by_mode[m][1][1 * 2 + c]
                      for m in MODES for c in (0, 1)):
        fam.add("F_DEAD_TABLE")
    if all(len(set(cfg_by_mode[m][0])) == 1 for m in MODES):
        fam.add("F_FROZEN_STATE")
    if all(cfg_by_mode[m][1][s * 2 + 0] == cfg_by_mode[m][1][s * 2 + 1]
           for m in MODES for s in range(ns)):
        fam.add("F_MOORE")
    else:
        fam.add("F_MEALY_PURE")
    if all(cfg_by_mode[m][0][s * 2 + c] == c for m in MODES for s in range(ns) for c in (0, 1)):
        fam.add("F_IDENTITY_STATE")
    return sorted(fam)


# ------------------------------------------------------------------ remints
def remint_state_relabel(b, cfg, perm):
    """Re-encode a candidate under a state relabelling; behaviour must be preserved.
    perm maps old state -> new state; initial state 0 must map to 0."""
    nxt, out = cfg
    ns = n_states(b)
    inv = [0] * ns
    for s in range(ns):
        inv[perm[s]] = s
    nn = [0] * n_addr(b)
    no = [0] * n_addr(b)
    for s in range(ns):
        for c in (0, 1):
            nn[perm[s] * 2 + c] = perm[nxt[s * 2 + c]]
            no[perm[s] * 2 + c] = out[s * 2 + c]
    return (tuple(nn), tuple(no))


def remint_input_relabel(b, cfg):
    """Swap input symbols 0<->1 in the machine.  The task is relabelled too."""
    nxt, out = cfg
    nn = [0] * n_addr(b)
    no = [0] * n_addr(b)
    for s in range(n_states(b)):
        for c in (0, 1):
            nn[s * 2 + c] = nxt[s * 2 + (1 - c)]
            no[s * 2 + c] = 1 - out[s * 2 + (1 - c)]
    return (tuple(nn), tuple(no))


def errors_relabelled_task(b, out, nxt, m):
    """Error count when BOTH the machine and the task carry the 0<->1 relabel."""
    e = 0
    for seq in SEQ:
        rseq = tuple(1 - x for x in seq)
        st = 0
        for t in range(L):
            cur = rseq[t]
            a = st * 2 + cur
            if t in WINDOW:
                if out[a] != rseq[t - m]:
                    e += 1
            st = nxt[a]
    return e


# --------------------------------------------------- independent searchers
def hillclimb_channel(b, m, seed, restarts=24, steps=400):
    """Seeded randomised hill-climb over next-state space; majority outputs."""
    rng = random.Random(seed)
    na = n_addr(b)
    ns = n_states(b)
    best = None
    for _ in range(restarts):
        cur = [rng.randrange(ns) for _ in range(na)]
        ce = majority_errors(b, tuple(cur), m)[0]
        for _ in range(steps):
            i = rng.randrange(na)
            old = cur[i]
            new = rng.randrange(ns)
            if new == old:
                continue
            cur[i] = new
            e = majority_errors(b, tuple(cur), m)[0]
            if e <= ce:
                ce = e
            else:
                cur[i] = old
        if best is None or ce < best:
            best = ce
    return best


def greedy_from(b, m, start):
    na = n_addr(b)
    ns = n_states(b)
    cur = list(start)
    ce = majority_errors(b, tuple(cur), m)[0]
    improved = True
    while improved:
        improved = False
        for i in range(na):
            for v in range(ns):
                if v == cur[i]:
                    continue
                old = cur[i]
                cur[i] = v
                e = majority_errors(b, tuple(cur), m)[0]
                if e < ce:
                    ce, improved = e, True
                else:
                    cur[i] = old
    return ce


def greedy_channel(b, m, multistart=True):
    """Deterministic coordinate descent.  Single-start from the all-zero
    next-state function, and a deterministic multi-start variant over a fixed
    start set.  Both are reported: the single start is a weak searcher and its
    stalls are part of the row-5 evidence, not something to hide."""
    na = n_addr(b)
    ns = n_states(b)
    starts = [tuple([0] * na)]
    if multistart:
        starts.append(tuple([ns - 1] * na))
        starts.append(tuple((i % 2) % ns for i in range(na)))          # next = cur
        starts.append(tuple((i // 2) % ns for i in range(na)))          # next = state
        for k in range(4):
            starts.append(tuple(((i * (k + 1) + k) % ns) for i in range(na)))
    vals = [greedy_from(b, m, st) for st in starts]
    return min(vals), vals[0]


# -------------------------------------------------------------------- main
def main():
    res = {"schema": "GMI_833_Z13_ADJUDICATION_RESULT_V1", "issue": 833,
           "subsection": "Z13", "route": "A",
           "adjudicated": "research/gmi-833-z-z13-property-prediction-freeze-v1/FREEZE_V1.md",
           "adjudicated_blob_sha": "25febfa62cbf73f1f239f3de29436ecd043e67d9",
           "adjudicated_freeze_commit": "0cc617fc71334b08a60d476993785a7fd3c04a6f",
           "scored_window": list(WINDOW), "L": L, "scored_moments_per_mode": NSCORED}

    # ---- universe
    res["universe"] = {"size_by_budget": dict((str(b), str(universe_size(b))) for b in BUDGETS),
                       "size_total": str(sum(universe_size(b) for b in BUDGETS)),
                       "enumerated_exhaustively": ["b=0", "b=1"],
                       "b2_method": "next-state enumeration with per-address majority outputs "
                                    "(MODE-INDEPENDENCE + MAJORITY-OPTIMALITY); the full "
                                    "(out, nxt) product at b=2 is 2**72 and is NOT enumerated"}

    # ---- channel optima
    R = {}
    OPT = {}
    for b in BUDGETS:
        for m in MODES:
            e, cfgs = channel_optimum(b, m, collect=(b <= 1))
            R[(b, m)] = Fraction(e, NSCORED)
            OPT[(b, m)] = cfgs
    res["channel_optima"] = dict(("b%d_m%d" % (b, m),
                                  {"R": str(R[(b, m)]), "errors": R[(b, m)] * NSCORED,
                                   "n_optimal_configs": len(OPT[(b, m)])})
                                 for b in BUDGETS for m in MODES)
    for k in res["channel_optima"]:
        res["channel_optima"][k]["errors"] = int(res["channel_optima"][k]["errors"])

    R12 = R[(1, 2)]
    R01 = R[(0, 1)]
    res["key_floors"] = {"R0_delay2_given_b1": str(R12),
                         "R0_delay1_given_b0": str(R01),
                         "R0_delay2_given_b0": str(R[(0, 2)]),
                         "R0_delay1_given_b1": str(R[(1, 1)]),
                         "R0_all_channels_given_b2_is_zero":
                             all(R[(2, m)] == 0 for m in MODES)}

    # ---- thresholds over the declared world grid
    W = worlds()
    h1 = h2 = 0
    nonempty_true = nonempty_frozen = 0
    mismatch_witness = None
    p2zero_rows = []
    per_world = []
    for (eta, p) in W:
        E = E_profile(R, eta, p)
        lo_true = E[1] - E[2]
        hi_true = E[0] - E[1]
        lo_frozen = eta * p[2] * R12
        hi_frozen = eta * p[2] * R12 + eta * p[1] * R01
        if lo_true == lo_frozen:
            h1 += 1
        if hi_true == hi_frozen:
            h2 += 1
        elif mismatch_witness is None:
            mismatch_witness = {"eta": eta, "p": [str(x) for x in p],
                                "upper_true": str(hi_true), "upper_frozen": str(hi_frozen),
                                "excess": str(hi_frozen - hi_true)}
        if hi_true > lo_true:
            nonempty_true += 1
        if hi_frozen > lo_frozen:
            nonempty_frozen += 1
        per_world.append((eta, p, lo_true, hi_true, lo_frozen, hi_frozen))
        if p[2] == 0:
            p2zero_rows.append((eta, p, lo_true, hi_true))

    res["thresholds"] = {
        "n_worlds": len(W),
        "H1_lower_endpoint_matches_frozen": "%d/%d" % (h1, len(W)),
        "H2_upper_endpoint_matches_frozen": "%d/%d" % (h2, len(W)),
        "frozen_upper_excess_closed_form": "eta*p2*(R0(d2|b=1) - (R0(d2|b=0) - R0(d2|b=1)))",
        "frozen_upper_excess_value": "eta*p2*%s" % str(R12 - (R[(0, 2)] - R12)),
        "first_upper_mismatch_witness": mismatch_witness,
        "true_niche_nonempty_worlds": nonempty_true,
        "frozen_niche_nonempty_worlds": nonempty_frozen,
        "true_niche_width_closed_form": "eta*(p1*(R0(d1|b=0)-R0(d1|b=1)) + p2*(R0(d2|b=0)-2*R0(d2|b=1)))",
    }

    # niche width and the true collapse condition, exactly
    wid_terms = {"p1_coeff": R[(0, 1)] - R[(1, 1)] - (R[(1, 1)] - R[(2, 1)]),
                 "p2_coeff": R[(0, 2)] - R[(1, 2)] - (R[(1, 2)] - R[(2, 2)])}
    res["thresholds"]["width_coefficients"] = dict((k, str(v)) for k, v in wid_terms.items())
    res["thresholds"]["true_collapse_condition"] = (
        "p1*(%s) + p2*(%s) <= 0" % (wid_terms["p1_coeff"], wid_terms["p2_coeff"]))

    # ---- H-5: the frozen matched negative ecology at p2 = 0
    p2z_widths = sorted(set(str(hi - lo) for (_e, _p, lo, hi) in p2zero_rows))
    p2z_collapsed = sum(1 for (_e, _p, lo, hi) in p2zero_rows if hi <= lo)
    # widest-niche check: is p2=0 where the niche is WIDEST for fixed p1?
    widest = {}
    for (eta, p, lo, hi, _lf, _hf) in per_world:
        key = (eta, p[1])
        w = hi - lo
        if key not in widest or w > widest[key][0]:
            widest[key] = (w, p[2])
    p2_zero_is_argmax = all(v[1] == 0 for k, v in widest.items() if k[1] > 0)
    res["negative_ecology"] = {
        "frozen_claim": "at p2 = 0 the interval (lambda_2*, lambda_1*) collapses and the "
                        "intermediate morphology must lose its advantage everywhere",
        "p2_zero_worlds": len(p2zero_rows),
        "p2_zero_worlds_with_collapsed_interval": p2z_collapsed,
        "p2_zero_observed_widths": p2z_widths,
        "p2_zero_is_the_widest_niche_at_fixed_p1": p2_zero_is_argmax,
        "H5_mechanism_claim_holds": p2z_collapsed == len(p2zero_rows),
    }

    # ---- properties of what actually wins at b = 1
    cfgs_by_mode = dict((m, OPT[(1, m)]) for m in MODES)
    sample = {}
    for m in MODES:
        sample[m] = cfgs_by_mode[m][0]
    pr = props(1, sample, R)
    res["recovered_b1_optimum"] = {
        "n_optimal_morphologies": len(cfgs_by_mode[0]) * len(cfgs_by_mode[1]) * len(cfgs_by_mode[2]),
        "n_optimal_configs_per_mode": dict((str(m), len(cfgs_by_mode[m])) for m in MODES),
        "example": dict((str(m), {"nxt": list(sample[m][0]), "out": list(sample[m][1])}) for m in MODES),
        "properties": pr,
        "families": families(1, sample),
    }

    # P-b AND P-c satisfiability at b = 1, over the FULL b=1 candidate set
    ident_nxt = tuple(c for _s in range(n_states(1)) for c in (0, 1))
    # exhaustive: the bundle requires r_delay1 = 0 and r_delay2 = R12 simultaneously
    d1_opt_nxts = set(n for (n, _o) in OPT[(1, 1)])
    d2_opt_nxts = set(n for (n, _o) in OPT[(1, 2)])
    res["satisfiability"] = {
        "identity_next_function": list(ident_nxt),
        "delay1_zero_error_next_functions": sorted(list(d1_opt_nxts)),
        "delay2_floor_next_functions": sorted(list(d2_opt_nxts)),
        "identity_attains_delay1_zero": ident_nxt in d1_opt_nxts,
        "identity_attains_delay2_floor": ident_nxt in d2_opt_nxts,
        "delay2_error_under_identity_next":
            str(Fraction(majority_errors(1, ident_nxt, 2)[0], NSCORED)),
        "P_b_all_and_P_c_satisfiable_at_b1":
            bool(ident_nxt in d1_opt_nxts and ident_nxt in d2_opt_nxts),
        "P_b_determined_and_P_c_satisfiable_at_b1":
            bool(len(d1_opt_nxts & d2_opt_nxts) > 0 and ident_nxt in d1_opt_nxts
                 and ident_nxt in d2_opt_nxts),
        "P_b_all_is_definitionally_F_IDENTITY_STATE": True,
        "logical_note": "P-b/all holds of a candidate iff that candidate is in "
                        "F_IDENTITY_STATE; so any candidate satisfying P-a and P-b/all and "
                        "P-c that were a unique minimiser in the niche would make P-d FALSE. "
                        "H-3 and H-4 are therefore jointly unsatisfiable by logic alone, "
                        "independently of every number in this receipt.",
    }

    # ---- shared-next sensitivity line (C-1, never a second chance at a HIT)
    shared = {}
    for (eta, p) in [(1, (Fraction(1, 3),) * 3), (1, (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4)))]:
        best = None
        argset = []
        for nxt in all_nxt(1):
            es = [majority_errors(1, nxt, m)[0] for m in MODES]
            w = sum(p[m] * Fraction(es[m], NSCORED) for m in MODES)
            if best is None or w < best:
                best, argset = w, [(nxt, tuple(es))]
            elif w == best:
                argset.append((nxt, tuple(es)))
        shared["eta%d_p%s" % (eta, "_".join(str(x) for x in p))] = {
            "min_weighted_error": str(best),
            "n_argmin": len(argset),
            "argmin_includes_identity_next": any(n == ident_nxt for (n, _e) in argset),
            "identity_delay2_errors": [list(e) for (n, e) in argset if n == ident_nxt],
            "argmin": [{"nxt": list(n), "errs": list(e)} for (n, e) in argset[:6]],
        }
    res["shared_next_sensitivity"] = shared

    # ---- remints (Z13 row 4)
    remint = {"state_relabel_identity_preserved": True, "input_relabel_preserved": True,
              "control_broken_relabel_changes_numbers": False}
    for b in (1, 2):
        for m in MODES:
            e0 = R[(b, m)] * NSCORED
            for perm in itertools.permutations(range(n_states(b))):
                if perm[0] != 0:
                    continue
                for (nxt, out) in OPT[(b, m)][:8]:
                    nn, no = remint_state_relabel(b, (nxt, out), list(perm))
                    if simulate_errors(b, no, nn, m) != e0:
                        remint["state_relabel_identity_preserved"] = False
    for m in MODES:
        e0 = R[(1, m)] * NSCORED
        for (nxt, out) in OPT[(1, m)][:8]:
            nn, no = remint_input_relabel(1, (nxt, out))
            if errors_relabelled_task(1, no, nn, m) != e0:
                remint["input_relabel_preserved"] = False
    # control: a NON-remint -- scramble the next-state addresses and leave the
    # output table alone.  This is not a re-encoding, so it must change numbers.
    changed = 0
    tried = 0
    for m in MODES:
        e0 = R[(1, m)] * NSCORED
        for (nxt, out) in OPT[(1, m)][:8]:
            bad = (nxt[1], nxt[0], nxt[3], nxt[2])
            tried += 1
            if simulate_errors(1, out, bad, m) != e0:
                changed += 1
    remint["control_tried"] = tried
    remint["control_broken_relabel_changes_numbers"] = changed > 0
    remint["control_n_changed"] = changed
    res["remints"] = remint

    # ---- independent search algorithms (Z13 row 5)
    srch = {}
    for b in (1, 2):
        for m in MODES:
            tgt = int(R[(b, m)] * NSCORED)
            hc = hillclimb_channel(b, m, seed=90000 + 10 * b + m)
            gr_multi, gr_single = greedy_channel(b, m)
            srch["b%d_m%d" % (b, m)] = {
                "exhaustive": tgt, "hillclimb": hc,
                "greedy_multistart": gr_multi, "greedy_single_start": gr_single,
                "agree": bool(hc == tgt and gr_multi == tgt),
                "single_start_stalled": bool(gr_single != tgt)}
    res["independent_searches"] = srch

    # ---- MAJORITY-OPTIMALITY verification inside Route A at b in {0,1}
    mo_ok = True
    for b in (0, 1):
        for m in MODES:
            for nxt in all_nxt(b):
                e_major, _t = majority_errors(b, nxt, m)
                e_full = min(simulate_errors(b, out, nxt, m)
                             for out in itertools.product((0, 1), repeat=n_addr(b)))
                if e_major != e_full:
                    mo_ok = False
    res["majority_optimality_checked_b01"] = mo_ok

    # ---- hostiles: each must MOVE the quantity it perturbs
    host = {}
    # H_A: wrong scored window (t in {1,2,3}) -> delay2 target undefined at t=1; use {1,2}
    eA = min(majority_errors(1, nx, 2, window=(1, 2))[0] for nx in all_nxt(1))
    host["window_shift"] = {"detected": Fraction(eA, NSCORED) != R12,
                            "perturbed": str(Fraction(eA, NSCORED)), "true": str(R12)}
    # H_B: grammar restricted to the predicted template (F_IDENTITY_STATE only)
    eB = majority_errors(1, ident_nxt, 2)[0]
    host["template_injected_grammar"] = {"detected": Fraction(eB, NSCORED) != R12,
                                         "perturbed": str(Fraction(eB, NSCORED)), "true": str(R12)}
    # H_C: mode entries shared (breaks MODE-INDEPENDENCE): one nxt for d1 and d2
    best_shared = min(max(majority_errors(1, nx, 1)[0], 0) + majority_errors(1, nx, 2)[0]
                      for nx in all_nxt(1))
    true_sep = int(R[(1, 1)] * NSCORED) + int(R12 * NSCORED)
    host["mode_entries_shared"] = {"detected": best_shared != true_sep,
                                   "perturbed": best_shared, "true": true_sep}
    # H_D: level-instead-of-marginal threshold (the exact defect in Z13-P1)
    host["level_instead_of_marginal"] = {"detected": (R12) != (R[(0, 2)] - R12),
                                         "perturbed": str(R12), "true": str(R[(0, 2)] - R12)}
    # H_E: sequence length shortened to L = 3 (the frozen universe says L = 4)
    SEQ3 = tuple(itertools.product((0, 1), repeat=3))
    eE = min(majority_errors(1, nx, 2, window=(2,), seqs=SEQ3, length=3)[0]
             for nx in all_nxt(1))
    host["sequence_length_shortened"] = {
        "detected": Fraction(eE, len(SEQ3)) != R12,
        "perturbed": str(Fraction(eE, len(SEQ3))), "true": str(R12)}
    # H_F: delay-2 channel scored against the delay-1 target (off-by-one task)
    eF = min(majority_errors(1, nx, 1)[0] for nx in all_nxt(1))
    host["delay2_target_off_by_one"] = {"detected": Fraction(eF, NSCORED) != R12,
                                        "perturbed": str(Fraction(eF, NSCORED)), "true": str(R12)}
    # H_G: first-seen output instead of the per-address majority
    def first_seen_errors(b, nxt, m):
        seen = {}
        e = 0
        trace = []
        for seq in SEQ:
            st = 0
            for t in range(L):
                a = st * 2 + seq[t]
                if t in WINDOW:
                    trace.append((a, seq[t - m]))
                st = nxt[a]
        for (a, want) in trace:
            if a not in seen:
                seen[a] = want
            elif seen[a] != want:
                e += 1
        return e
    gaps = [(first_seen_errors(1, nx, 2) - majority_errors(1, nx, 2)[0], nx)
            for nx in all_nxt(1)]
    worst = max(gaps)
    host["first_seen_output_not_majority"] = {
        "detected": worst[0] > 0,
        "perturbed": "max per-next-state excess over the majority optimum = %d errors "
                     "at nxt=%s" % (worst[0], list(worst[1])),
        "true": "0 excess by MAJORITY-OPTIMALITY",
        "n_next_functions_where_first_seen_is_strictly_worse":
            sum(1 for (g, _n) in gaps if g > 0)}
    # H_H: skewed input law -> floors must move
    def skew_floor(q):
        best = None
        for nxt in all_nxt(1):
            t2 = [[Fraction(0), Fraction(0)] for _ in range(n_addr(1))]
            for seq in SEQ:
                pr = Fraction(1)
                for x in seq:
                    pr *= q if x == 1 else (1 - q)
                st = 0
                for t in range(L):
                    a = st * 2 + seq[t]
                    if t in WINDOW:
                        t2[a][seq[t - 2]] += pr
                    st = nxt[a]
            e = sum(min(v) for v in t2)
            if best is None or e < best:
                best = e
        return best / len(WINDOW)
    sf = skew_floor(Fraction(1, 5))
    host["skewed_input_law"] = {"detected": sf != R12, "perturbed": str(sf), "true": str(R12)}

    # CONTROL (not a hostile): the initial state is a state-relabelling symmetry,
    # so moving it must NOT change the floor.  A "hostile" here would be inert by
    # theorem; it is registered as a no-alarm control and scored for silence.
    def sim_from(st0, b, out, nxt, m):
        e = 0
        for seq in SEQ:
            st = st0
            for t in range(L):
                a = st * 2 + seq[t]
                if t in WINDOW and out[a] != seq[t - m]:
                    e += 1
                st = nxt[a]
        return e
    eCtl = min(min(sim_from(1, 1, out, nxt, 2)
                   for out in itertools.product((0, 1), repeat=n_addr(1)))
               for nxt in all_nxt(1))
    res["no_alarm_control"] = {
        "perturbation": "initial state 0 -> 1 at b = 1",
        "expected": "UNCHANGED (state relabelling is a symmetry of the b=1 universe; "
                    "see the remint check)",
        "observed": str(Fraction(eCtl, NSCORED)), "true": str(R12),
        "silent_as_required": Fraction(eCtl, NSCORED) == R12}
    res["hostiles"] = host
    res["hostiles_all_detected"] = all(v["detected"] for v in host.values())

    # ---- null: random threshold laws, scored against the enumeration itself.
    # The null must be beaten by the true result, and must be grounded in the
    # enumerated data rather than in the author's own closed form -- the exact
    # instrument failure Z5 recorded and repaired.
    rng = random.Random(131313)
    GRID = [Fraction(n, 16) for n in range(0, 17)]
    trials = 200
    null_scores = []
    true_pair = (R[(0, 1)] - R[(1, 1)], R[(0, 2)] - R[(1, 2)] - (R[(1, 2)] - R[(2, 2)]))
    for _ in range(trials):
        a = rng.choice(GRID)
        bq = rng.choice(GRID)
        sc = 0
        for (eta, p, lo_t, hi_t, _lf, _hf) in per_world:
            if eta * (a * p[1] + bq * p[2]) == hi_t:
                sc += 1
        null_scores.append(((str(a), str(bq)), sc))
    best_null = max(sc for (_ab, sc) in null_scores)
    n_perfect = sum(1 for (_ab, sc) in null_scores if sc == len(W))
    # the marginal law itself, scored the same way
    marg = sum(1 for (eta, p, lo_t, hi_t, _lf, _hf) in per_world
               if eta * ((R[(0, 1)] - R[(1, 1)]) * p[1] + (R[(0, 2)] - R[(1, 2)]) * p[2]) == hi_t)
    frozen_score = sum(1 for (eta, p, lo_t, hi_t, _lf, hf) in per_world if hf == hi_t)
    res["null"] = {
        "description": "200 seeded two-parameter threshold laws eta*(a*p1 + b*p2), "
                       "a, b drawn from k/16, scored against the enumerated upper endpoint "
                       "in all %d worlds" % len(W),
        "trials": trials,
        "best_null_score": "%d/%d" % (best_null, len(W)),
        "nulls_reaching_all_worlds": n_perfect,
        "marginal_law_score": "%d/%d" % (marg, len(W)),
        "frozen_Z13P1_law_score": "%d/%d" % (frozen_score, len(W)),
        "marginal_law_coefficients": [str(true_pair[0]), str(R[(0, 2)] - R[(1, 2)])],
    }
    # vacuity probe kept separately: the frozen bundle is unsatisfiable, so a
    # random-candidate count of 0 is a theorem, not evidence.  Reported as such.
    rngv = random.Random(242424)
    hits = 0
    for _ in range(200):
        b_rand = rngv.choice([0, 1, 2])
        nx = tuple(rngv.randrange(n_states(b_rand)) for _ in range(n_addr(b_rand)))
        ou = tuple(rngv.randrange(2) for _ in range(n_addr(b_rand)))
        cfg = dict((m, (nx, ou)) for m in MODES)
        pp = props(b_rand, cfg, R)
        if b_rand == 1 and pp["P_a"] and pp["P_b_all"] and pp["P_c"]:
            hits += 1
    res["vacuity_probe"] = {
        "trials": 200, "random_candidates_satisfying_the_frozen_bundle": hits,
        "note": "0 here is entailed by the unsatisfiability proof and is NOT counted "
                "as independent evidence"}

    # ---- verdict
    H = {
        "H1_lower_endpoint": h1 == len(W),
        "H2_upper_endpoint": h2 == len(W),
        "H3_minimiser_satisfies_Pa_Pb_Pc": bool(pr["P_a"] and pr["P_b_all"] and pr["P_c"]),
        "H4_Pd_nonvacuous": bool(res["satisfiability"]["P_b_all_and_P_c_satisfiable_at_b1"]),
        "H5_negative_ecology": res["negative_ecology"]["H5_mechanism_claim_holds"],
    }
    res["HIT_conditions"] = H
    res["verdict"] = "HIT" if all(H.values()) else "MISS"
    res["P_d_status"] = ("VACUOUSLY_TRUE"
                         if not res["satisfiability"]["P_b_all_and_P_c_satisfiable_at_b1"]
                         else "SUBSTANTIVE")

    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"verdict": res["verdict"], "HIT_conditions": H,
                      "R0_delay2_given_b1": str(R12),
                      "H1": res["thresholds"]["H1_lower_endpoint_matches_frozen"],
                      "H2": res["thresholds"]["H2_upper_endpoint_matches_frozen"],
                      "p2zero_widths": p2z_widths,
                      "hostiles_all_detected": res["hostiles_all_detected"],
                      "null_best": res["null"]["best_null_score"],
                      "marginal_law": res["null"]["marginal_law_score"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
