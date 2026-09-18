"""Route B -- source-separated oracle for the Z12 prediction-scoring protocol.

Imports nothing from route A and shares no helper module. It opens the pinned
blobs itself, reduces every record to the integer key (|A|, |S|, |T|, |S int T|),
aggregates integer counts per key, and derives every score from those counts by
integer arithmetic over Fractions. The morphology class optima are obtained by
exhaustive enumeration of all 65,552 registered candidates with this file's own
semantics implementation, not from the closed-form boundary law.

Run:  python3 -I -B independent_scoring_oracle_v1.py
"""
import json
import os
import sys
from fractions import Fraction

_HERE = os.path.dirname(os.path.abspath(__file__))
_RES = os.path.dirname(_HERE)


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def _j(*parts):
    return os.path.join(_RES, *parts)


# ----------------------------------------------------- independent semantics
def _seqs():
    out = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                out.append((a, b, c))
    return tuple(out)


_SEQ = _seqs()


def _errs_stateless(table):
    acc = [0, 0]
    for mode in (0, 1):
        for seq in _SEQ:
            for t in (1, 2):
                cur = seq[t]
                out = (table >> (2 * mode + cur)) & 1
                tgt = cur if mode == 0 else seq[t - 1]
                if out != tgt:
                    acc[mode] += 1
    return acc[0], acc[1]


def _errs_stateful(nxt, table):
    acc = [0, 0]
    for mode in (0, 1):
        for seq in _SEQ:
            st = 0
            for t in range(3):
                cur = seq[t]
                idx = 4 * st + 2 * mode + cur
                out = (table >> idx) & 1
                if t in (1, 2):
                    tgt = cur if mode == 0 else seq[t - 1]
                    if out != tgt:
                        acc[mode] += 1
                st = (nxt >> idx) & 1
    return acc[0], acc[1]


def histogram():
    """(state_bits, e_now, e_delay) -> multiplicity, over all 65,552 candidates."""
    hist = {}
    for table in range(16):
        key = (0,) + _errs_stateless(table)
        hist[key] = hist.get(key, 0) + 1
    for nxt in range(256):
        for table in range(256):
            key = (1,) + _errs_stateful(nxt, table)
            hist[key] = hist.get(key, 0) + 1
    return hist


def class_optima(hist, p, eta, lam):
    """min objective per state_bits class, by scanning the histogram."""
    best = {}
    for (bits, e0, e1), _mult in hist.items():
        val = eta * ((1 - p) * Fraction(e0, 16) + p * Fraction(e1, 16)) + lam * bits
        if bits not in best or val < best[bits]:
            best[bits] = val
    return best


# ---------------------------------------------------------- record reduction
def reduce_records(records):
    """records: list of (A_size, S_tuple, T_tuple) -> integer key counts."""
    counts = {}
    for a_size, S, T in records:
        s = set(S)
        t = set(T)
        key = (a_size, len(s), len(t), len(s & t))
        counts[key] = counts.get(key, 0) + 1
    return counts


def scores_from_counts(counts):
    n = 0
    refute = 0
    mass_n = 0
    covered = 0
    vac = 0
    size_sum = 0
    size_max = 0
    excess = 0
    abstain = 0
    unident = 0
    unsound = 0
    brier = Fraction(0)
    ebins = {}
    for (a_size, k, m, inter), mult in counts.items():
        n += mult
        if k == 0:
            refute += mult
            if m == 0:
                covered += mult
            continue
        mass_n += mult
        if inter == m:
            covered += mult
        if k == a_size and m != a_size:
            vac += mult
        size_sum += k * mult
        if k > size_max:
            size_max = k
        excess += (k - m) * mult
        if k > 1:
            abstain += mult
        if m > 1:
            unident += mult
            if k == 1:
                unsound += mult
        q = Fraction(1, k)
        tq = Fraction(1, m) if m else Fraction(0)
        # Brier over the whole alphabet, from counts alone
        b = (q - tq) ** 2 * inter + q * q * (k - inter) + tq * tq * (m - inter)
        brier += b * mult
        slot = ebins.setdefault(k, [Fraction(0), 0, q])
        slot[0] += tq * inter * mult
        slot[1] += k * mult
    ecal = Fraction(0)
    table = []
    for k in sorted(ebins):
        total, pairs, q = ebins[k]
        mean_y = total / pairs
        err = abs(mean_y - q)
        if err > ecal:
            ecal = err
        table.append({"set_size": k, "claimed_probability": "%d/%d" % (q.numerator, q.denominator),
                      "pairs": pairs,
                      "mean_realized_mass": "%d/%d" % (mean_y.numerator, mean_y.denominator),
                      "calibration_error": "%d/%d" % (err.numerator, err.denominator)})

    def f(x):
        return "%d/%d" % (x.numerator, x.denominator)

    return {
        "records": n,
        "REFUTE_WORLD_excluded_from_mass_scores": refute,
        "mass_scored_records": mass_n,
        "COV_1_covered": covered,
        "COV_1_coverage": f(Fraction(covered, n)),
        "VAC_1_vacuous": vac,
        "VAC_1_rate": f(Fraction(vac, mass_n)),
        "SHP_1_mean_set_size": f(Fraction(size_sum, mass_n)),
        "SHP_1_max_set_size": size_max,
        "SHP_1_mean_excess": f(Fraction(excess, mass_n)),
        "ABS_1_abstaining": abstain,
        "ABS_1_abstention_rate": f(Fraction(abstain, mass_n)),
        "ABS_1_unidentifiable": unident,
        "ABS_1_soundness_violations": unsound,
        "BRI_1_mean_brier": f(brier / mass_n),
        "CAL_1_max_error": f(ecal),
        "CAL_1_bins": table,
    }


# ------------------------------------------------------------- data loading
def load_m():
    doc = load_json(_j("gmi-833-heldout-20-transitions-v1", "RESULT_V1.json"))
    alpha = ("PERSISTENT_STATE", "STATELESS")
    recs = []
    worlds = []
    for case in doc["cases"]:
        p = Fraction(case["p"])
        eta = Fraction(case["eta"])
        star = eta * p / 2
        for tag, lam, truth in (("low", Fraction(case["lambda_low"]), case["observed_low"]),
                                ("high", Fraction(case["lambda_high"]), case["observed_high"]),
                                ("boundary", star, None)):
            worlds.append((case["case"], tag, p, eta, lam, truth))
            recs.append((p, eta, lam, truth, alpha))
    return recs, worlds, alpha


def load_k():
    ev = _j("gmi-833-capability-predictor-evaluation-v1")
    res = load_json(os.path.join(ev, "RESULT_V1.json"))
    truth = {}
    for curve in res["curves"]:
        for case in curve["detail"]:
            for pt in case["points"]:
                truth[(curve["universe"], case["case_index"], tuple(pt["budget"]))] = pt["external_values"]
    rows = []
    for name in ("FROZEN_PREDICTIONS_V1.json", "FROZEN_PREDICTIONS_V4.json"):
        doc = load_json(os.path.join(ev, name))
        for uni in doc["universes"]:
            u = uni["universe"]
            pts = []
            ok = True
            for ci, curve in enumerate(uni["curves"]):
                for pt in curve["points"]:
                    key = (u, ci, tuple(pt["budget"]))
                    if key not in truth:
                        ok = False
                        break
                    pts.append((pt["identified_set"], truth[key]))
                if not ok:
                    break
            if not ok:
                continue
            alpha = set()
            for S, T in pts:
                alpha.update(S)
                alpha.update(T)
            rows.extend([(len(alpha), tuple(S), tuple(T)) for S, T in pts])
    return rows


# -------------------------------------------------------------------- main
def main():
    hist = histogram()
    total = sum(hist.values())
    controls = {
        "candidate_census": total,
        "distinct_risk_summaries": len(hist),
        "stateless_min_delayed_error": None,
        "endpoint_agreements": 0,
        "boundary_ties": 0,
    }
    sl_min = min(e1 for (b, e0, e1) in hist if b == 0)
    controls["stateless_min_delayed_error"] = "%d/%d" % (Fraction(sl_min, 16).numerator,
                                                         Fraction(sl_min, 16).denominator)

    m_raw, worlds, alpha_m = load_m()
    m_records = []
    regret_total = Fraction(0)
    regret_worst = Fraction(0)
    endpoints = 0
    ties = 0
    for (cid, tag, p, eta, lam, truth) in worlds:
        opt = class_optima(hist, p, eta, lam)
        best = min(opt.values())
        winners = tuple(sorted("STATELESS" if b == 0 else "PERSISTENT_STATE"
                               for b in opt if opt[b] == best))
        star = eta * p / 2
        if lam < star:
            pred = ("PERSISTENT_STATE",)
        elif lam > star:
            pred = ("STATELESS",)
        else:
            pred = alpha_m
        if tag == "boundary":
            T = winners
            if len(winners) == 2:
                ties += 1
        else:
            T = tuple(sorted(truth))
            if T == winners:
                endpoints += 1
        m_records.append((len(alpha_m), pred, T))
        jmap = {"STATELESS": opt[0], "PERSISTENT_STATE": opt[1]}
        chosen = sorted(pred)[0]
        regret_total += jmap[chosen] - best
        regret_worst += max(jmap[s] for s in pred) - best
    controls["endpoint_agreements"] = endpoints
    controls["boundary_ties"] = ties

    k_records = load_k()
    out = {
        "schema": "GMI_833_Z12_PREDICTION_SCORING_ORACLE_V1",
        "route": "B",
        "controls": controls,
        "POP_M": scores_from_counts(reduce_records(m_records)),
        "POP_K": scores_from_counts(reduce_records(k_records)),
        "REG_1_total_regret": "%d/%d" % (regret_total.numerator, regret_total.denominator),
        "REG_1_mean_regret": "%d/%d" % ((regret_total / len(m_records)).numerator,
                                        (regret_total / len(m_records)).denominator),
        "REG_1_total_worst_case_regret": "%d/%d" % (regret_worst.numerator, regret_worst.denominator),
        "REG_1_mean_worst_case_regret": "%d/%d" % ((regret_worst / len(m_records)).numerator,
                                                   (regret_worst / len(m_records)).denominator),
    }
    with open(os.path.join(_HERE, "ORACLE_RESULT_V1.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    sys.stdout.write("Z12 route B census=%d summaries=%d endpoints=%d ties=%d\n"
                     % (total, len(hist), endpoints, ties))
    return 0


if __name__ == "__main__":
    sys.exit(main())
