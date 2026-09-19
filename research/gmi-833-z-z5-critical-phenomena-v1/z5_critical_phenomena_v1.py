"""Route A -- exact critical phenomena and scaling for the finite morphology
transition (#833 Section Z, subsection Z5).

Route A simulates. Every candidate is replayed over every input sequence at
every rung of the size ladder, and every threshold, gap, derivative jump and
scaling number is read off the scanned values. Stdlib only, exact rational
arithmetic (`fractions.Fraction`); no float appears in any claim.

Run:  python3 -I -B z5_critical_phenomena_v1.py
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
TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")

STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"

L_LADDER = (2, 3, 4, 5)
L_REGISTERED = 3
A_LADDER = (2, 3, 4)
SCALE_LADDER = ("1/7", "1/2", "2", "3", "11/5", "100")
NULL_SEEDS = tuple(range(9100, 9300))


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


# ------------------------------------------------------- binary universe (A)
def sequences(length, alphabet=2):
    return tuple(itertools.product(range(alphabet), repeat=length))


def stateless_errors_L(table, seqs, length):
    """table maps index (2*mode + cur) -> output bit. Returns (e_now, e_delay)."""
    e = [0, 0]
    for mode in (0, 1):
        for seq in seqs:
            for t in range(1, length):
                cur = seq[t]
                got = (table >> (2 * mode + cur)) & 1
                want = cur if mode == 0 else seq[t - 1]
                if got != want:
                    e[mode] += 1
    return e[0], e[1]


def stateful_errors_L(nxt, table, seqs, length):
    """index = 4*state + 2*mode + cur; nxt and table are 8-bit masks."""
    e = [0, 0]
    for mode in (0, 1):
        for seq in seqs:
            st = 0
            for t in range(length):
                cur = seq[t]
                idx = 4 * st + 2 * mode + cur
                got = (table >> idx) & 1
                if t >= 1:
                    want = cur if mode == 0 else seq[t - 1]
                    if got != want:
                        e[mode] += 1
                st = (nxt >> idx) & 1
    return e[0], e[1]


def build_universe(length):
    """Exact (bits, e_now, e_delay) for all 65552 candidates at sequence length L."""
    seqs = sequences(length)
    out = []
    for table in range(16):
        e0, e1 = stateless_errors_L(table, seqs, length)
        out.append((0, e0, e1))
    for nxt in range(256):
        for table in range(256):
            e0, e1 = stateful_errors_L(nxt, table, seqs, length)
            out.append((1, e0, e1))
    return out


def summarize(universe):
    """Collapse to the multiset of (bits, e_now, e_delay); the objective depends
    on a candidate only through this triple, so the argmin class set is
    unchanged. The test asserts agreement against the flat scan."""
    counts = {}
    for trip in universe:
        counts[trip] = counts.get(trip, 0) + 1
    return tuple(sorted(counts.items()))


def value(trip, p, eta, lam, N):
    bits, e0, e1 = trip
    return eta * ((1 - p) * Fraction(e0, N) + p * Fraction(e1, N)) + lam * bits


def argmin_classes(summary, p, eta, lam, N):
    best = None
    classes = set()
    for trip, _mult in summary:
        val = value(trip, p, eta, lam, N)
        if best is None or val < best:
            best = val
            classes = set([STATELESS if trip[0] == 0 else PERSISTENT])
        elif val == best:
            classes.add(STATELESS if trip[0] == 0 else PERSISTENT)
    return best, frozenset(classes)


def argmin_classes_flat(universe, p, eta, lam, N):
    best = None
    classes = set()
    for trip in universe:
        val = value(trip, p, eta, lam, N)
        if best is None or val < best:
            best = val
            classes = set([STATELESS if trip[0] == 0 else PERSISTENT])
        elif val == best:
            classes.add(STATELESS if trip[0] == 0 else PERSISTENT)
    return best, frozenset(classes)


def best_in_class(summary, bits, p, eta, lam, N):
    best = None
    for trip, _mult in summary:
        if trip[0] != bits:
            continue
        val = value(trip, p, eta, lam, N)
        if best is None or val < best:
            best = val
    return best


# --------------------------------------------------------------- A-ary side
def stateless_errors_A(table, seqs, length, A):
    """table is a tuple of 2*A outputs indexed by A*mode + cur."""
    e = [0, 0]
    for mode in (0, 1):
        for seq in seqs:
            for t in range(1, length):
                cur = seq[t]
                got = table[A * mode + cur]
                want = cur if mode == 0 else seq[t - 1]
                if got != want:
                    e[mode] += 1
    return e[0], e[1]


def min_stateless_delay_fraction(A, length):
    """Exhaustive over all A^(2A) stateless tables; exact minimum of
    e_delay / N as a Fraction."""
    seqs = sequences(length, A)
    N = (length - 1) * (A ** length)
    best = None
    count_tables = 0
    attained_now = set()
    for table in itertools.product(range(A), repeat=2 * A):
        count_tables += 1
        _e0, e1 = stateless_errors_A(table, seqs, length, A)
        frac = Fraction(e1, N)
        if best is None or frac < best:
            best = frac
        attained_now.add(_e0)
    return best, count_tables, N, sorted(attained_now)


def one_register_machine_errors(A, length):
    """Exhibit the natural one-A-ary-register machine (next state := current
    symbol; output := current symbol in mode 0, stored symbol in mode 1) and
    score it by simulation. Returns (e_now, e_delay, N)."""
    seqs = sequences(length, A)
    N = (length - 1) * (A ** length)
    e = [0, 0]
    for mode in (0, 1):
        for seq in seqs:
            st = 0
            for t in range(length):
                cur = seq[t]
                got = cur if mode == 0 else st
                if t >= 1:
                    want = cur if mode == 0 else seq[t - 1]
                    if got != want:
                        e[mode] += 1
                st = cur
    return e[0], e[1], N


def delay_error_set_A(A, length):
    """The exact set of attained e_delay/N fractions across all stateless tables."""
    seqs = sequences(length, A)
    N = (length - 1) * (A ** length)
    out = set()
    for table in itertools.product(range(A), repeat=2 * A):
        _e0, e1 = stateless_errors_A(table, seqs, length, A)
        out.add(Fraction(e1, N))
    return sorted(out), N


# ------------------------------------------------------------------- worlds
def load_worlds():
    doc = load_json(TRANS)
    if doc.get("schema") != "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1":
        raise SystemExit("transition receipt schema drift")
    worlds = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam in (("low", Fraction(case["lambda_low"])),
                         ("high", Fraction(case["lambda_high"])),
                         ("boundary", star)):
            worlds.append({"case": case["case"], "tag": tag, "p": p, "eta": eta,
                           "lam": lam, "lam_star": star})
    return worlds


def predict(p, eta, lam, multiplier=Fraction(1)):
    star = multiplier * eta * p / 2
    if lam < star:
        return frozenset([PERSISTENT])
    if lam > star:
        return frozenset([STATELESS])
    return frozenset([PERSISTENT, STATELESS])


def fs(x):
    return str(Fraction(x))



# --------------------------------------------------------- row 6 register
REGISTER_ENTRIES = (
    {"id": "SP-1",
     "prediction": "CP-4a: lambda* shows zero finite-size drift in sequence length L",
     "label": "[DERIVED-AT-FREEZE]",
     "file": "research/gmi-833-z-z5-critical-phenomena-v1/FREEZE_V1.md",
     "anchor": "**zero finite-size drift**, finite-size exponent `0`"},
    {"id": "SP-2",
     "prediction": "CP-3d: the critical window has width exactly zero at every finite size",
     "label": "[DERIVED-AT-FREEZE]",
     "file": "research/gmi-833-z-z5-critical-phenomena-v1/FREEZE_V1.md",
     "anchor": "`CP-3d` `[DERIVED-AT-FREEZE]` **Zero critical width.**"},
    {"id": "SP-3",
     "prediction": "S4-naive: lambda* is independent of the symbol alphabet size A",
     "label": "[NAIVE EXTRAPOLATION OF THE REGISTERED LAW]",
     "file": "research/gmi-833-z-z5-critical-phenomena-v1/FREEZE_V1.md",
     "anchor": "`S4-naive` \u2014 the registered law's literal extrapolation"},
    {"id": "SP-4",
     "prediction": "S4-derived: lambda*(A) = eta * p * (1 - 1/A) in the registers accounting convention",
     "label": "[DERIVED-AT-FREEZE]",
     "file": "research/gmi-833-z-z5-critical-phenomena-v1/FREEZE_V1.md",
     "anchor": "`S4-derived` `[DERIVED-AT-FREEZE]` \u2014 this package's derivation:"},
    {"id": "SP-5",
     "prediction": "CP-3b: the jump in dJ*/dlambda across the transition equals the jump in the order parameter",
     "label": "[DERIVED-AT-FREEZE]",
     "file": "research/gmi-833-z-z5-critical-phenomena-v1/FREEZE_V1.md",
     "anchor": "**Exact latent-quantity relation.**"},
    {"id": "SP-PARENT-SHIFTED",
     "prediction": "the deliberately wrong boundary 2*lambda*, a registered negative control of the parent transition package",
     "label": "[PARENT NEGATIVE CONTROL]",
     "file": "research/gmi-833-heldout-20-transitions-v1/FREEZE_V1.md",
     "anchor": None},
)

REPO = os.path.dirname(RESEARCH)


def blob_sha(path):
    with open(path, "rb") as fh:
        data = fh.read()
    head = ("blob %d\0" % len(data)).encode("ascii")
    return hashlib.sha1(head + data).hexdigest()


def build_register(report):
    """Publish every registered scaling prediction with its adjudicated verdict,
    failures and successes side by side, each pinned by path, git blob sha and a
    verbatim anchor that must occur exactly once in the pinned file."""
    alpha = dict([(r["A"], r) for r in report["CP_5"]["ladder"]])
    verdicts = {
        "SP-1": "CONFIRMED" if report["CP_4"]["zero_finite_size_drift"] else "REFUTED",
        "SP-2": "CONFIRMED" if report["gates_preview_zero_width"] else "REFUTED",
        "SP-3": "REFUTED" if report["CP_5"]["S4_naive_refuted"] else "CONFIRMED",
        "SP-4": "CONFIRMED" if report["CP_5"]["S4_derived_confirmed"] else "REFUTED",
        "SP-5": "CONFIRMED" if report["CP_3"]["derivative_jump_is_one"] else "REFUTED",
        "SP-PARENT-SHIFTED": "REFUTED",
    }
    evidence = {
        "SP-1": "lambda_star_drift_violations = 0 at every rung L in {2,3,4,5}",
        "SP-2": "critical_width_violations = %d over 60 worlds x 3 probe offsets"
                % report["CP_3"]["critical_width_violations"],
        "SP-3": ("enumerated min stateless delay fraction is %s at A=3 and %s at A=4, "
                 "not 1/2" % (alpha[3]["min_stateless_delay_fraction"],
                              alpha[4]["min_stateless_delay_fraction"])),
        "SP-4": ("enumerated min stateless delay fraction equals (A-1)/A at every "
                 "A in {2,3,4}: %s, %s, %s"
                 % (alpha[2]["min_stateless_delay_fraction"],
                    alpha[3]["min_stateless_delay_fraction"],
                    alpha[4]["min_stateless_delay_fraction"])),
        "SP-5": "derivative jump values = %s" % report["CP_3"]["derivative_jump_values"],
        "SP-PARENT-SHIFTED": "falsified in all 20 parent transition cases",
    }
    ceiling_change = {
        "SP-3": {"retired": "lambda* = eta * p / 2 stated without an alphabet qualifier",
                 "replacement": "lambda*(A) = eta * p * (1 - 1/A); the registered form "
                                "eta*p/2 is the A = 2 case only",
                 "forbidden_promotion_added": "LAMBDA_STAR_IS_ETA_P_OVER_TWO_IN_GENERAL"},
    }
    entries = []
    violations = 0
    for spec in REGISTER_ENTRIES:
        full = os.path.join(REPO, spec["file"])
        exists = os.path.exists(full)
        anchor_count = None
        sha = None
        if exists:
            sha = blob_sha(full)
            if spec["anchor"] is not None:
                with open(full) as fh:
                    anchor_count = fh.read().count(spec["anchor"])
        ok = exists and (spec["anchor"] is None or anchor_count == 1)
        if not ok:
            violations += 1
        entry = {"id": spec["id"], "prediction": spec["prediction"],
                 "label": spec["label"], "verdict": verdicts[spec["id"]],
                 "evidence": evidence[spec["id"]], "pinned_path": spec["file"],
                 "pinned_blob_sha": sha, "anchor": spec["anchor"],
                 "anchor_occurrences": anchor_count, "pin_ok": ok}
        if spec["id"] in ceiling_change:
            entry["claim_ceiling_change"] = ceiling_change[spec["id"]]
        entries.append(entry)
    doc = {"schema": "GMI_833_Z5_FAILED_SCALING_PREDICTION_REGISTER_V1",
           "issue": 833, "subsection": "Z5",
           "note": ("failures and successes are published side by side; a refuted "
                    "prediction carries the exact claim-ceiling text it retires"),
           "entries": entries, "anchor_violations": violations}
    with open(os.path.join(HERE, "FAILED_SCALING_PREDICTION_REGISTER_V1.json"), "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return doc


# ------------------------------------------------------------------ the run
def main():
    worlds = load_worlds()
    report = {"schema": "GMI_833_Z5_CRITICAL_PHENOMENA_RESULT_V1",
              "issue": 833, "section": "Z", "subsection": "Z5",
              "source_main": "349c2e62c4ae01f52cf66f61e4dacdbdfcf10071",
              "claim_ceiling": ("GMI_833_Z5_EXACT_FIRST_ORDER_MORPHOLOGY_TRANSITION_"
                                "ZERO_FINITE_SIZE_DRIFT_AND_THE_REFUTED_ALPHABET_"
                                "INDEPENDENT_THRESHOLD_AT_REGISTERED_FINITE_SCOPE"),
              "route": "A_simulation"}

    # ---- the registered rung, L = 3
    uni3 = build_universe(L_REGISTERED)
    sum3 = summarize(uni3)
    N3 = (L_REGISTERED - 1) * (2 ** L_REGISTERED)
    report["universe"] = {"candidates": len(uni3), "stateless": 16,
                          "stateful": 65536, "N_scored_moments": N3,
                          "distinct_sigma": len(sum3)}

    # ---- CP-1: control parameters. Homogeneity of degree 1 in (eta, lambda).
    homog_bad = []
    for w in worlds:
        _b0, c0 = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        for cs in SCALE_LADDER:
            c = Fraction(cs)
            b1, c1 = argmin_classes(sum3, w["p"], c * w["eta"], c * w["lam"], N3)
            if c1 != c0:
                homog_bad.append({"case": w["case"], "tag": w["tag"], "c": cs})
    # mu = lambda/eta determines the verdict: two worlds with equal (p, mu) agree
    mu_map = {}
    mu_bad = []
    for w in worlds:
        key = (w["p"], w["lam"] / w["eta"])
        _b, cl = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        if key in mu_map and mu_map[key] != cl:
            mu_bad.append({"case": w["case"], "tag": w["tag"]})
        mu_map[key] = cl
    report["CP_1"] = {"homogeneity_violations": len(homog_bad),
                      "scale_ladder": list(SCALE_LADDER),
                      "distinct_p_mu_keys": len(mu_map),
                      "p_mu_determinism_violations": len(mu_bad),
                      "order_parameter": "state bits of the argmin, values {0,1}"}

    # ---- CP-2: analytic threshold from the attained error lattice
    sless = sorted(set([(t[1], t[2]) for t in uni3 if t[0] == 0]))
    sful = sorted(set([(t[1], t[2]) for t in uni3 if t[0] == 1]))
    delay_vals_stateless = sorted(set([e1 for _e0, e1 in sless]))
    now_vals_stateless = sorted(set([e0 for e0, _e1 in sless]))
    report["CP_2"] = {
        "stateless_attained_pairs": [list(x) for x in sless],
        "stateless_delay_values": delay_vals_stateless,
        "stateless_now_values": now_vals_stateless,
        "stateless_delay_is_uniform_half": delay_vals_stateless == [N3 // 2],
        "stateful_attained_pair_count": len(sful),
        "stateful_contains_zero_zero": (0, 0) in sful,
        "threshold_formula": "lambda_star = eta * p / 2",
    }

    # threshold check: analytic lambda* equals the exact crossing of the two
    # class-restricted minima, at every registered world
    cross_bad = []
    for w in worlds:
        b0 = best_in_class(sum3, 0, w["p"], w["eta"], Fraction(0), N3)
        # class-1 minimum at lambda = 0 is the pure error part; add lam*bits later
        b1 = best_in_class(sum3, 1, w["p"], w["eta"], Fraction(0), N3)
        # crossing lambda solves b0 == b1 + lambda  ->  lambda = b0 - b1
        crossing = b0 - b1
        if crossing != w["lam_star"]:
            cross_bad.append({"case": w["case"], "tag": w["tag"],
                              "crossing": fs(crossing), "lam_star": fs(w["lam_star"])})
    report["CP_2"]["analytic_crossing_mismatches"] = len(cross_bad)
    report["CP_2"]["analytic_crossing_examples"] = cross_bad[:3]

    # ---- CP-3: behaviour near the transition
    deltas = [Fraction(1, 10 ** k) for k in (3, 6, 9)]
    deriv_rows = []
    tie_bad = []
    width_bad = []
    gap_rows = []
    for w in worlds:
        star = w["lam_star"]
        jstar, cls_star = argmin_classes(sum3, w["p"], w["eta"], star, N3)
        if cls_star != frozenset([STATELESS, PERSISTENT]):
            tie_bad.append({"case": w["case"], "classes": sorted(cls_star)})
        for d in deltas:
            jl, cl_l = argmin_classes(sum3, w["p"], w["eta"], star - d, N3)
            jr, cl_r = argmin_classes(sum3, w["p"], w["eta"], star + d, N3)
            left_slope = (jstar - jl) / d
            right_slope = (jr - jstar) / d
            deriv_rows.append({"case": w["case"], "delta": fs(d),
                               "left_slope": fs(left_slope),
                               "right_slope": fs(right_slope),
                               "jump": fs(left_slope - right_slope)})
            if cl_l != frozenset([PERSISTENT]) or cl_r != frozenset([STATELESS]):
                width_bad.append({"case": w["case"], "delta": fs(d)})
        b0 = best_in_class(sum3, 0, w["p"], w["eta"], w["lam"], N3)
        b1 = best_in_class(sum3, 1, w["p"], w["eta"], w["lam"], N3)
        gap_rows.append({"case": w["case"], "tag": w["tag"], "gap": fs(b0 - b1)})
    jumps = sorted(set([r["jump"] for r in deriv_rows]))
    boundary_worlds = [w for w in worlds if w["tag"] == "boundary"]
    report["CP_3"] = {
        "boundary_worlds_checked": len(boundary_worlds),
        "exact_ties_at_boundary": len(boundary_worlds) - len(tie_bad),
        "tie_violations": len(tie_bad),
        "derivative_jump_values": jumps,
        "derivative_jump_is_one": jumps == ["1"],
        "critical_width_violations": len(width_bad),
        "deltas_probed": [fs(d) for d in deltas],
        "gap_examples": gap_rows[:4],
        "value_function": "J*(lambda) = min(eta*p/2, lambda)",
    }
    # J* closed form check over all worlds
    jstar_bad = []
    for w in worlds:
        j, _c = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        closed = min(w["eta"] * w["p"] / 2, w["lam"])
        if j != closed:
            jstar_bad.append({"case": w["case"], "tag": w["tag"]})
    report["CP_3"]["closed_form_value_mismatches"] = len(jstar_bad)
    report["gates_preview_zero_width"] = len(width_bad) == 0

    # ---- CP-4: finite-size scaling in L
    rungs = []
    for L in L_LADDER:
        uni = build_universe(L)
        smm = summarize(uni)
        N = (L - 1) * (2 ** L)
        sl = sorted(set([(t[1], t[2]) for t in uni if t[0] == 0]))
        dv = sorted(set([e1 for _e0, e1 in sl]))
        bad = []
        for w in worlds:
            b0 = best_in_class(smm, 0, w["p"], w["eta"], Fraction(0), N)
            b1 = best_in_class(smm, 1, w["p"], w["eta"], Fraction(0), N)
            crossing = b0 - b1
            if crossing != w["lam_star"]:
                bad.append({"case": w["case"], "crossing": fs(crossing)})
            _j, cl = argmin_classes(smm, w["p"], w["eta"], w["lam_star"], N)
            if cl != frozenset([STATELESS, PERSISTENT]):
                bad.append({"case": w["case"], "tie": sorted(cl)})
        rungs.append({"L": L, "N_scored_moments": N, "candidates": len(uni),
                      "distinct_sigma": len(smm),
                      "stateless_delay_values": dv,
                      "stateless_delay_is_uniform_half": dv == [N // 2],
                      "lambda_star_drift_violations": len(bad),
                      "stateful_attained_pair_count":
                          len(set([(t[1], t[2]) for t in uni if t[0] == 1]))})
    report["CP_4"] = {"ladder": rungs,
                      "zero_finite_size_drift": all(r["lambda_star_drift_violations"] == 0
                                                    for r in rungs),
                      "sharp_at_every_rung": all(r["stateless_delay_is_uniform_half"]
                                                 for r in rungs)}

    # ---- CP-5: alphabet ladder, S4-naive against S4-derived
    alpha = []
    for A in A_LADDER:
        best, ntables, N, now_vals = min_stateless_delay_fraction(A, L_REGISTERED)
        derived = Fraction(A - 1, A)
        naive = Fraction(1, 2)
        vals, _N2 = delay_error_set_A(A, L_REGISTERED)
        m0, m1, mN = one_register_machine_errors(A, L_REGISTERED)
        alpha.append({"A": A, "tables_enumerated": ntables, "N_scored_moments": N,
                      "stateless_min_e_now": min(now_vals),
                      "stateless_now_value_count": len(now_vals),
                      "one_register_witness_e_now": m0,
                      "one_register_witness_e_delay": m1,
                      "one_register_witness_is_zero_error": (m0 == 0 and m1 == 0),
                      "min_stateless_delay_fraction": fs(best),
                      "S4_derived_prediction": fs(derived),
                      "S4_derived_matches": best == derived,
                      "S4_naive_prediction": fs(naive),
                      "S4_naive_matches": best == naive,
                      "lambda_star_over_eta_p": fs(best),
                      "attained_delay_fractions": [fs(v) for v in vals],
                      "delay_is_uniform": len(vals) == 1})
    report["CP_5"] = {
        "ladder": alpha,
        "accounting_convention": "state cost charged in registers (one A-ary register costs 1)",
        "excluded_convention": "cost in bits (log2 A per register): irrational at A=3, forbidden by the exact-arithmetic rule",
        "product_form_licensed":
            all(r["delay_is_uniform"] and r["stateless_min_e_now"] == 0 for r in alpha),
        "product_form_note":
            ("the best 0-register cost factorises as eta*p*(min delay fraction) only "
             "because the delay fraction is constant across the whole stateless family "
             "and e_now = 0 is attainable; both are checked, not assumed"),
        "S4_naive_refuted": any((not r["S4_naive_matches"]) for r in alpha),
        "S4_derived_confirmed": all(r["S4_derived_matches"] for r in alpha),
        "zero_error_one_register_machine_exists":
            all(r["one_register_witness_is_zero_error"] for r in alpha),
        "law": "lambda_star(A) = eta * p * (1 - 1/A); equals eta*p/2 only at A = 2",
    }

    # ---- hostiles
    hostiles = {}
    # H1 doubled boundary
    endpoints = [w for w in worlds if w["tag"] in ("low", "high")]
    mis_true = 0
    mis_h1 = 0
    for w in endpoints:
        _j, actual = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        if predict(w["p"], w["eta"], w["lam"]) != actual:
            mis_true += 1
        if predict(w["p"], w["eta"], w["lam"], Fraction(2)) != actual:
            mis_h1 += 1
    hostiles["H1_DOUBLE_BOUNDARY"] = {
        "quantity": "endpoint mismatch count",
        "clean": mis_true, "hostile": mis_h1,
        "moved": mis_true == 0 and mis_h1 > 0,
        "checked": len(endpoints)}
    # H2 alphabet-blind: claims lambda*(3) = eta p /2
    a3 = [r for r in alpha if r["A"] == 3][0]
    hostiles["H2_ALPHABET_BLIND"] = {
        "quantity": "claimed lambda*(A=3)/(eta p)",
        "clean": a3["min_stateless_delay_fraction"],
        "hostile": fs(Fraction(1, 2)),
        "moved": a3["min_stateless_delay_fraction"] != fs(Fraction(1, 2))}
    # H3 scorer offset: score t=0 as a delay moment
    seqs3 = sequences(L_REGISTERED)
    off = set()
    for table in range(16):
        e1 = 0
        for seq in seqs3:
            for t in range(0, L_REGISTERED):
                cur = seq[t]
                got = (table >> (2 * 1 + cur)) & 1
                want = seq[t - 1] if t >= 1 else 0
                if got != want:
                    e1 += 1
        off.add(e1)
    hostiles["H3_SCORER_OFFSET"] = {
        "quantity": "stateless e_delay value set",
        "clean": delay_vals_stateless,
        "hostile": sorted(off),
        "moved": sorted(off) != delay_vals_stateless}
    # H4 truncated universe
    trunc = summarize([t for t in uni3 if t[0] == 0])
    flips = 0
    for w in worlds:
        _j, full = argmin_classes(sum3, w["p"], w["eta"], w["lam"], N3)
        _j2, cut = argmin_classes(trunc, w["p"], w["eta"], w["lam"], N3)
        if full != cut:
            flips += 1
    hostiles["H4_TRUNCATED_UNIVERSE"] = {
        "quantity": "winner class set over 60 worlds",
        "clean": 0, "hostile": flips, "moved": flips > 0}
    # H5 silent refit: a tampered anchor or a tampered pin must fail the check
    freeze_path = os.path.join(REPO,
                               "research/gmi-833-z-z5-critical-phenomena-v1/FREEZE_V1.md")
    with open(freeze_path) as fh:
        freeze_text = fh.read()
    good_anchor = "**zero finite-size drift**, finite-size exponent `0`"
    bad_anchor = good_anchor.replace("zero", "nonzero")
    hostiles["H5_SILENT_REFIT"] = {
        "quantity": "anchor occurrence count in the pinned file",
        "clean": freeze_text.count(good_anchor),
        "hostile": freeze_text.count(bad_anchor),
        "moved": freeze_text.count(good_anchor) == 1 and freeze_text.count(bad_anchor) != 1}
    report["hostiles"] = hostiles

    # ---- null: 200 randomized scaling laws f(A), adjudicated by ENUMERATION
    #
    # Instrument note. The first implementation of this null compared each
    # random f(A) against the closed-form 1 - 1/A and never touched the
    # enumerated data, so it would have scored 200/200 even if the enumeration
    # had been wrong or absent -- a null that tests nothing. It is replaced by a
    # decision-procedure-level adjudicator: a claimed threshold is *caught* only
    # when it produces a morphology verdict that disagrees with the verdict
    # obtained from the enumerated stateless optimum and the exhibited
    # zero-error one-register witness. See FREEZE_V1_AMENDMENT_1.md.
    enum_frac = {}
    for r in alpha:
        enum_frac[r["A"]] = Fraction(r["min_stateless_delay_fraction"])
    witness_ok = all(r["one_register_witness_is_zero_error"] for r in alpha)

    def true_threshold(A, p, eta):
        """lambda* from enumerated evidence only: the best 0-register cost is
        eta*p*(enumerated minimum delay fraction) because the enumerated
        e_now-minimising table attains delay minimum too (checked below); the
        best 1-register cost is lambda because the exhibited witness has zero
        error."""
        return eta * p * enum_frac[A]

    def true_verdict(A, p, eta, lam):
        c0 = eta * p * enum_frac[A]
        c1 = lam
        if c1 < c0:
            return PERSISTENT
        if c0 < c1:
            return STATELESS
        return "TIE"

    def claimed_verdict(fA, p, eta, lam):
        star = eta * p * fA
        if lam < star:
            return PERSISTENT
        if lam > star:
            return STATELESS
        return "TIE"

    probe_cases = [(Fraction("1/5"), Fraction(1)), (Fraction("2/5"), Fraction(2)),
                   (Fraction("3/5"), Fraction(3)), (Fraction("4/5"), Fraction(1))]
    delta = Fraction(1, 10 ** 12)
    ladder_num = list(range(1, 12))
    truth_f = dict([(A, enum_frac[A]) for A in A_LADDER])

    def draw_f(seed):
        rnd = random.Random(seed)
        for _attempt in range(64):
            f = {}
            for A in A_LADDER:
                num = rnd.choice(ladder_num)
                den = rnd.choice(ladder_num)
                f[A] = Fraction(num, den)
            if any(f[A] != truth_f[A] for A in A_LADDER):
                return f
        return None

    def adjudicate(f, alphabets):
        """Catch f iff some probe world gives a claimed verdict that differs
        from the enumerated verdict. Returns (caught, guard_ok)."""
        guard_ok = True
        for A in alphabets:
            star_claim = None
            for p, eta in probe_cases:
                star_claim = eta * p * f[A]
                star_true = true_threshold(A, p, eta)
                if star_claim != star_true and abs(star_claim - star_true) <= delta:
                    guard_ok = False
                for lam in (star_claim - delta, star_claim + delta):
                    if lam <= 0:
                        continue
                    if claimed_verdict(f[A], p, eta, lam) != true_verdict(A, p, eta, lam):
                        return True, guard_ok
        return False, guard_ok

    full_caught = 0
    a2_caught = 0
    guard_failures = 0
    drawn = 0
    blind_f = []
    for seed in NULL_SEEDS:
        f = draw_f(seed)
        if f is None:
            continue
        drawn += 1
        cf, g1 = adjudicate(f, A_LADDER)
        ca, g2 = adjudicate(f, (2,))
        if not (g1 and g2):
            guard_failures += 1
        if cf:
            full_caught += 1
        if ca:
            a2_caught += 1
        else:
            blind_f.append(dict([(str(A), fs(f[A])) for A in A_LADDER]))
    blind_json = sorted(set([json.dumps(b, sort_keys=True) for b in blind_f]))
    blind_at_two = all(Fraction(json.loads(x)["2"]) == truth_f[2] for x in blind_json)
    report["null"] = {
        "seeds": len(NULL_SEEDS),
        "laws_drawn": drawn,
        "adjudicator": ("verdict-level: a claimed threshold is caught only when its "
                        "morphology verdict disagrees with the verdict computed from "
                        "the enumerated stateless optimum and the exhibited zero-error "
                        "one-register witness"),
        "enumerated_thresholds_over_eta_p": dict([(str(A), fs(truth_f[A])) for A in A_LADDER]),
        "one_register_witness_verified": witness_ok,
        "probe_worlds": len(probe_cases),
        "guard_failures": guard_failures,
        "full_ladder_caught": full_caught,
        "full_ladder_survived": drawn - full_caught,
        "A2_only_caught": a2_caught,
        "A2_only_blind": drawn - a2_caught,
        "A2_only_blind_distinct_f": len(blind_json),
        "A2_only_blind_all_agree_at_A2": blind_at_two,
        "A2_only_blind_characterization":
            ("an A=2-only adjudicator is blind to exactly those laws that agree with the "
             "enumerated threshold at A=2, whatever they claim at A=3 and A=4; the blind "
             "set is verified to consist entirely of such laws"),
        "A2_only_blind_examples": [json.loads(x) for x in blind_json[:5]],
    }

    # ---- row 6: the failed-scaling-prediction register
    reg = build_register(report)
    report["register"] = {"entries": len(reg["entries"]),
                          "failures": len([e for e in reg["entries"]
                                           if e["verdict"] == "REFUTED"]),
                          "successes": len([e for e in reg["entries"]
                                            if e["verdict"] == "CONFIRMED"]),
                          "anchor_violations": reg["anchor_violations"]}
    gates_extra = {"register_anchors_unique": reg["anchor_violations"] == 0,
                   "register_publishes_a_real_failure":
                       any(e["verdict"] == "REFUTED" for e in reg["entries"]),
                   "register_publishes_successes_alongside":
                       any(e["verdict"] == "CONFIRMED" for e in reg["entries"])}

    # ---- gates (register is built above; see build_register)
    gates = {
        "homogeneity_exact": len(homog_bad) == 0,
        "p_mu_determines_verdict": len(mu_bad) == 0,
        "stateless_delay_uniform_half": delay_vals_stateless == [N3 // 2],
        "analytic_threshold_matches_crossing": len(cross_bad) == 0,
        "exact_tie_at_boundary": len(tie_bad) == 0,
        "derivative_jump_equals_one": jumps == ["1"],
        "closed_form_value_function": len(jstar_bad) == 0,
        "zero_critical_width": len(width_bad) == 0,
        "zero_finite_size_drift": report["CP_4"]["zero_finite_size_drift"],
        "S4_naive_refuted": report["CP_5"]["S4_naive_refuted"],
        "S4_derived_confirmed": report["CP_5"]["S4_derived_confirmed"],
        "product_form_licensed": report["CP_5"]["product_form_licensed"],
        "hostiles_all_moved": all(h["moved"] for h in hostiles.values()),
        "null_full_ladder_clean": (drawn - full_caught) == 0,
        "null_laws_drawn_complete": drawn == len(NULL_SEEDS),
        "null_guard_clean": guard_failures == 0,
        "null_A2_blindness_characterized": blind_at_two,
        "one_register_witness_verified": witness_ok,
    }
    gates.update(gates_extra)
    report["gates"] = gates
    report["verdict"] = "GREEN" if all(gates.values()) else "RED"
    report["forbidden_promotions"] = [
        "UNIVERSAL_CRITICAL_EXPONENTS", "CONTINUOUS_PHASE_TRANSITION",
        "THERMODYNAMIC_LIMIT_ESTABLISHED", "REAL_SUBSTRATE_SCALING",
        "PHYSICAL_SUBSTRATE_INVARIANCE", "SCALING_LAW_HOLDS_FOR_ALL_ACCOUNTING",
        "ALPHABET_LADDER_COVERS_ARCHITECTURES",
        "LAMBDA_STAR_IS_ETA_P_OVER_TWO_IN_GENERAL"]

    path = os.path.join(HERE, "RESULT_V1.json")
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("Z5 verdict:", report["verdict"])
    for k in sorted(gates):
        print("  %-38s %s" % (k, gates[k]))
    if report["verdict"] != "GREEN":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
