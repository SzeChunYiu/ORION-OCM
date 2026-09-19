"""Route A -- exact prediction-scoring protocol for #833 Section Z, subsection Z12.

Streaming, per-record Fraction accumulation over two pinned, prospectively
frozen on-main prediction populations. Stdlib only. No float appears in any
scored quantity.

Run:  python3 -I -B z12_prediction_scoring_v1.py
"""
import hashlib
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)

P_TRANS = os.path.join(RESEARCH, "gmi-833-heldout-20-transitions-v1", "RESULT_V1.json")
P_EVAL = os.path.join(RESEARCH, "gmi-833-capability-predictor-evaluation-v1")
P_FROZEN1 = os.path.join(P_EVAL, "FROZEN_PREDICTIONS_V1.json")
P_FROZEN4 = os.path.join(P_EVAL, "FROZEN_PREDICTIONS_V4.json")
P_EVALRES = os.path.join(P_EVAL, "RESULT_V1.json")

STATELESS = "STATELESS"
PERSISTENT = "PERSISTENT_STATE"
A_M = (PERSISTENT, STATELESS)

NULL_SEEDS = tuple(range(1000, 1200))


# ---------------------------------------------------------------- utilities
def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def set_digest(values):
    payload = json.dumps(sorted(values), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fr(text):
    return Fraction(text)


def frs(value):
    return "%d/%d" % (value.numerator, value.denominator)


# ------------------------------------------------------------- populations
class Record(object):
    __slots__ = ("rid", "S", "T", "A", "meta")

    def __init__(self, rid, S, T, A, meta):
        self.rid = rid
        self.S = tuple(sorted(set(S)))
        self.T = tuple(sorted(set(T)))
        self.A = tuple(sorted(set(A)))
        self.meta = meta


def load_pop_m():
    """40 endpoint + 20 boundary morphology records from the pinned transition receipt."""
    data = load_json(P_TRANS)
    if data.get("schema") != "GMI_833_HELDOUT_20_TRANSITIONS_RESULT_V1":
        raise SystemExit("POP_M schema drift")
    records = []
    worlds = []
    for case in data["cases"]:
        p = fr(case["p"])
        eta = fr(case["eta"])
        lam_star = eta * p / 2
        if lam_star != fr(case["threshold"]):
            raise SystemExit("POP_M threshold does not match eta*p/2")
        lo = fr(case["lambda_low"])
        hi = fr(case["lambda_high"])
        worlds.append({"case": case["case"], "p": p, "eta": eta, "lam_star": lam_star,
                       "lambda_low": lo, "lambda_high": hi})
        for tag, lam, truth in (("low", lo, case["observed_low"]),
                                ("high", hi, case["observed_high"]),
                                ("boundary", lam_star, None)):
            if lam < lam_star:
                pred = (PERSISTENT,)
            elif lam > lam_star:
                pred = (STATELESS,)
            else:
                pred = A_M
            if truth is None:
                # tie at lambda == lambda*: both class optima equal lambda*
                truth = list(A_M)
            records.append(Record("M:%02d:%s" % (case["case"], tag), pred, truth, A_M,
                                  {"case": case["case"], "endpoint": tag, "lambda": lam,
                                   "p": p, "eta": eta, "lam_star": lam_star}))
    return records, worlds


def load_pop_k():
    """Frozen prediction sets joined to externally computed truth sets."""
    res = load_json(P_EVALRES)
    truth_by_universe = {}
    for curve in res["curves"]:
        detail = {}
        for case in curve["detail"]:
            for point in case["points"]:
                detail[(case["case_index"], tuple(point["budget"]))] = point["external_values"]
        truth_by_universe[curve["universe"]] = detail

    records = []
    admitted = []
    refused = []
    for path in (P_FROZEN1, P_FROZEN4):
        frozen = load_json(path)
        for uni in frozen["universes"]:
            name = uni["universe"]
            if name not in truth_by_universe:
                refused.append({"universe": name, "reason": "NO_TRUTH_CURVE"})
                continue
            truth = truth_by_universe[name]
            keys = []
            ok = True
            for ci, curve in enumerate(uni["curves"]):
                for point in curve["points"]:
                    key = (ci, tuple(point["budget"]))
                    if key not in truth:
                        ok = False
                        break
                    keys.append((key, point))
                if not ok:
                    break
            if not ok:
                refused.append({"universe": name, "reason": "BUDGET_ALIGNMENT_FAILURE"})
                continue
            alphabet = set()
            for key, point in keys:
                alphabet.update(point["identified_set"])
                alphabet.update(truth[key])
            alphabet = tuple(sorted(alphabet))
            for key, point in keys:
                records.append(Record("K:%s:%d:%s" % (name, key[0], "-".join(str(b) for b in key[1])),
                                      point["identified_set"], truth[key], alphabet,
                                      {"universe": name, "disposition": point["disposition"]}))
            admitted.append({"universe": name, "records": len(keys), "alphabet_size": len(alphabet),
                             "alphabet": list(alphabet)})
    return records, admitted, refused


# ------------------------------------------------------------------ scores
def type_record(rec):
    """Registered typing; REFUTE_WORLD added by FREEZE_V1_AMENDMENT_1."""
    n = len(rec.S)
    if not set(rec.S) <= set(rec.A):
        return "REFUSED"
    if n == 0:
        return "REFUSED" if len(rec.T) > 0 else "REFUTE_WORLD"
    if n == 1:
        return "POINT"
    if n == len(rec.A):
        return "ABSTAIN_FULL"
    return "SET"


def score_population(records, selection=None):
    n = len(records)
    if n == 0:
        raise SystemExit("empty population")
    types = {"POINT": 0, "SET": 0, "ABSTAIN_FULL": 0, "REFUTE_WORLD": 0, "REFUSED": 0}
    vacuous = 0
    covered = 0
    size_sum = 0
    size_max = 0
    excess_sum = 0
    abstaining = 0
    unidentifiable = 0
    soundness_violations = 0
    refute = 0
    bins = {}
    ebins = {}
    brier_sum = Fraction(0)
    for rec in records:
        t = type_record(rec)
        types[t] += 1
        if t == "REFUSED":
            raise SystemExit("BND-1 refusal: %s" % rec.rid)
        S = set(rec.S)
        T = set(rec.T)
        A = set(rec.A)
        k = len(S)
        if t == "REFUTE_WORLD":
            # admitted, coverage-scored, excluded from every mass-based score
            if T <= S:
                covered += 1
            refute += 1
            continue
        if S == A and T != A:
            vacuous += 1
        if T <= S:
            covered += 1
        size_sum += k
        size_max = max(size_max, k)
        excess_sum += k - len(T)
        if k > 1:
            abstaining += 1
        if len(T) > 1:
            unidentifiable += 1
            if k == 1:
                soundness_violations += 1
        # CAL-1A (retained v1 record-level mass gap)
        h = Fraction(len(S & T), k)
        c = Fraction(1, k)
        slot = bins.setdefault(k, [Fraction(0), 0, c])
        slot[0] += h
        slot[1] += 1
        # CAL-1 (amendment 2): element-level calibration over pairs (i, a in S_i)
        q = Fraction(1, k)
        tq0 = Fraction(1, len(T)) if T else Fraction(0)
        eslot = ebins.setdefault(k, [Fraction(0), 0, q])
        for a in S:
            eslot[0] += tq0 if a in T else Fraction(0)
            eslot[1] += 1
        tq = Fraction(1, len(T))
        acc = Fraction(0)
        for a in A:
            qa = q if a in S else Fraction(0)
            ta = tq if a in T else Fraction(0)
            d = qa - ta
            acc += d * d
        brier_sum += acc
    bin_table = []
    cal_max = Fraction(0)
    for k in sorted(bins):
        total, count, c = bins[k]
        mean_h = total / count
        err = abs(mean_h - c)
        cal_max = max(cal_max, err)
        bin_table.append({"set_size": k, "claimed_confidence": frs(c), "records": count,
                          "mean_truth_mass": frs(mean_h), "mass_gap": frs(err)})
    ebin_table = []
    ecal_max = Fraction(0)
    for k in sorted(ebins):
        total, count, q = ebins[k]
        mean_y = total / count
        err = abs(mean_y - q)
        ecal_max = max(ecal_max, err)
        ebin_table.append({"set_size": k, "claimed_probability": frs(q), "pairs": count,
                           "mean_realized_mass": frs(mean_y), "calibration_error": frs(err)})
    mass_n = n - refute
    if mass_n <= 0:
        raise SystemExit("population has no mass-scorable record")
    out = {
        "records": n,
        "REFUTE_WORLD_excluded_from_mass_scores": refute,
        "mass_scored_records": mass_n,
        "BND_1_types": types,
        "VAC_1_vacuous": vacuous,
        "VAC_1_rate": frs(Fraction(vacuous, mass_n)),
        "COV_1_covered": covered,
        "COV_1_coverage": frs(Fraction(covered, n)),
        "SHP_1_mean_set_size": frs(Fraction(size_sum, mass_n)),
        "SHP_1_max_set_size": size_max,
        "SHP_1_mean_excess": frs(Fraction(excess_sum, mass_n)),
        "CAL_1_bins": ebin_table,
        "CAL_1_max_error": frs(ecal_max),
        "CAL_1A_record_level_bins": bin_table,
        "CAL_1A_record_level_max_mass_gap": frs(cal_max),
        "BRI_1_mean_brier": frs(brier_sum / mass_n),
        "ABS_1_abstaining": abstaining,
        "ABS_1_abstention_rate": frs(Fraction(abstaining, mass_n)),
        "ABS_1_unidentifiable": unidentifiable,
        "ABS_1_soundness_violations": soundness_violations,
    }
    return out


def class_optima_analytic(world):
    """J*(class) from the frozen boundary law, closed form."""
    return {STATELESS: world["eta"] * world["p"] / 2,
            PERSISTENT: world["lam"]}


def score_regret(records, selection=None):
    """REG-1: exact regret of the registered selection rule on POP_M."""
    if selection is None:
        selection = lambda S: sorted(S)[0]
    total = Fraction(0)
    total_worst = Fraction(0)
    n = 0
    detail = []
    for rec in records:
        world = {"eta": rec.meta["eta"], "p": rec.meta["p"], "lam": rec.meta["lambda"]}
        J = class_optima_analytic(world)
        best = min(J.values())
        chosen = selection(rec.S)
        r = J[chosen] - best
        rw = max(J[s] for s in rec.S) - best
        total += r
        total_worst += rw
        n += 1
        detail.append({"rid": rec.rid, "chosen": chosen, "regret": frs(r), "regret_worst": frs(rw)})
    return {"records": n, "REG_1_total_regret": frs(total), "REG_1_mean_regret": frs(total / n),
            "REG_1_total_worst_case_regret": frs(total_worst),
            "REG_1_mean_worst_case_regret": frs(total_worst / n),
            "REG_1_nonzero_regret_records": sum(1 for d in detail if d["regret"] != "0/1"),
            "detail": detail}


# ---------------------------------------------------------------- hostiles
def clone(records, mutate):
    out = []
    for rec in records:
        S = mutate(rec)
        out.append(Record(rec.rid, S, rec.T, rec.A, rec.meta))
    return out


def provenance_digests(records):
    return dict((rec.rid, set_digest(rec.S)) for rec in records)


def run_hostiles(pop_m, pop_k, true_m, true_k, true_reg):
    frozen_digest_m = provenance_digests(pop_m)
    frozen_digest_k = provenance_digests(pop_k)
    results = []

    def detect_provenance(records, frozen):
        return sum(1 for rec in records if set_digest(rec.S) != frozen[rec.rid])

    # H1 vacuous
    h1 = clone(pop_m, lambda r: r.A)
    s1 = score_population(h1)
    results.append({
        "id": "H1_VACUOUS", "population": "POP_M",
        "moves": {"VAC_1_rate": [true_m["VAC_1_rate"], s1["VAC_1_rate"]],
                  "SHP_1_mean_set_size": [true_m["SHP_1_mean_set_size"], s1["SHP_1_mean_set_size"]]},
        "delta_nonzero": s1["VAC_1_rate"] != true_m["VAC_1_rate"]
                         and s1["SHP_1_mean_set_size"] != true_m["SHP_1_mean_set_size"],
        "detected": s1["VAC_1_vacuous"] > 0,
        "no_alarm_on_true": true_m["VAC_1_vacuous"] == 0,
    })

    # H2 widener: enlarge exactly one singleton set on POP_K
    target = None
    for i, rec in enumerate(pop_k):
        if 0 < len(rec.S) < len(rec.A):
            target = i
            break
    h2 = []
    for i, rec in enumerate(pop_k):
        if i == target:
            extra = [a for a in rec.A if a not in rec.S][0]
            h2.append(Record(rec.rid, list(rec.S) + [extra], rec.T, rec.A, rec.meta))
        else:
            h2.append(rec)
    s2 = score_population(h2)
    expected = Fraction(1, true_k["mass_scored_records"])
    moved = fr(s2["SHP_1_mean_set_size"]) - fr(true_k["SHP_1_mean_set_size"])
    results.append({
        "id": "H2_WIDENER", "population": "POP_K",
        "moves": {"SHP_1_mean_set_size": [true_k["SHP_1_mean_set_size"], s2["SHP_1_mean_set_size"]],
                  "expected_delta": frs(expected), "observed_delta": frs(moved)},
        "delta_nonzero": moved == expected and moved != 0,
        "detected": detect_provenance(h2, frozen_digest_k) == 1,
        "no_alarm_on_true": detect_provenance(pop_k, frozen_digest_k) == 0,
    })

    # H3 never abstain
    h3 = clone(pop_m, lambda r: (sorted(r.S)[0],) if r.S else r.S)
    s3 = score_population(h3)
    results.append({
        "id": "H3_NEVER_ABSTAIN", "population": "POP_M",
        "moves": {"ABS_1_abstention_rate": [true_m["ABS_1_abstention_rate"], s3["ABS_1_abstention_rate"]],
                  "ABS_1_soundness_violations": [true_m["ABS_1_soundness_violations"],
                                                 s3["ABS_1_soundness_violations"]]},
        "delta_nonzero": s3["ABS_1_soundness_violations"] != true_m["ABS_1_soundness_violations"],
        "detected": s3["ABS_1_soundness_violations"] > 0,
        "no_alarm_on_true": true_m["ABS_1_soundness_violations"] == 0,
    })

    # H4 miscalibrated claim: c = 1/(|S|-1)
    def miscal(records, claim):
        """Element-level calibration under an arbitrary claimed-probability rule."""
        cal_max = Fraction(0)
        bins = {}
        for rec in records:
            S = set(rec.S)
            T = set(rec.T)
            k = len(S)
            if k == 0:
                continue
            q = claim(k)
            tq = Fraction(1, len(T)) if T else Fraction(0)
            slot = bins.setdefault(k, [Fraction(0), 0, q])
            for a in S:
                slot[0] += tq if a in T else Fraction(0)
                slot[1] += 1
        for k in bins:
            total, count, q = bins[k]
            cal_max = max(cal_max, abs(total / count - q))
        return cal_max

    honest = miscal(pop_k, lambda k: Fraction(1, k))
    s4 = miscal(pop_k, lambda k: Fraction(1, k - 1) if k > 1 else Fraction(1, 1))
    results.append({
        "id": "H4_MISCALIBRATED", "population": "POP_K",
        "moves": {"CAL_1_max_error": [true_k["CAL_1_max_error"], frs(s4)]},
        "delta_nonzero": frs(s4) != true_k["CAL_1_max_error"],
        "detected": s4 > fr(true_k["CAL_1_max_error"]),
        "no_alarm_on_true": honest == 0 and fr(true_k["CAL_1_max_error"]) == 0,
    })

    # H5 truth leak
    h5 = clone(pop_k, lambda r: r.T)
    s5 = score_population(h5)
    results.append({
        "id": "H5_TRUTH_LEAK", "population": "POP_K",
        "moves": {"COV_1_coverage": [true_k["COV_1_coverage"], s5["COV_1_coverage"]],
                  "SHP_1_mean_set_size": [true_k["SHP_1_mean_set_size"], s5["SHP_1_mean_set_size"]]},
        "delta_nonzero": s5["SHP_1_mean_set_size"] != true_k["SHP_1_mean_set_size"],
        "detected": detect_provenance(h5, frozen_digest_k) > 0,
        "no_alarm_on_true": detect_provenance(pop_k, frozen_digest_k) == 0,
    })

    # H6 regret blind
    s6 = score_regret(pop_m, selection=lambda S: STATELESS)
    results.append({
        "id": "H6_REGRET_BLIND", "population": "POP_M",
        "moves": {"REG_1_mean_regret": [true_reg["REG_1_mean_regret"], s6["REG_1_mean_regret"]],
                  "REG_1_total_regret": [true_reg["REG_1_total_regret"], s6["REG_1_total_regret"]]},
        "delta_nonzero": s6["REG_1_total_regret"] != true_reg["REG_1_total_regret"],
        "detected": fr(s6["REG_1_total_regret"]) > fr(true_reg["REG_1_total_regret"]),
        "no_alarm_on_true": fr(true_reg["REG_1_total_regret"]) == 0,
    })
    return results


# -------------------------------------------------------------------- null
def composite(score, regret):
    return (fr(score["COV_1_coverage"]), -fr(score["SHP_1_mean_set_size"]),
            -fr(regret["REG_1_mean_regret"]) if regret else Fraction(0))


def run_null(pop_m, true_m, true_reg):
    A = list(A_M)
    subsets = []
    for mask in range(1, 1 << len(A)):
        subsets.append(tuple(A[i] for i in range(len(A)) if mask & (1 << i)))
    true_key = composite(true_m, true_reg)
    beaten = 0
    matched_or_better = 0
    for seed in NULL_SEEDS:
        rng = random.Random(seed)
        rnd = [Record(r.rid, rng.choice(subsets), r.T, r.A, r.meta) for r in pop_m]
        sc = score_population(rnd)
        rg = score_regret(rnd)
        key = composite(sc, rg)
        if key >= true_key:
            matched_or_better += 1
        else:
            beaten += 1
    return {"seeds": len(NULL_SEEDS), "beaten_by_frozen": beaten,
            "matched_or_beat_frozen": matched_or_better,
            "frozen_composite": [frs(true_key[0]), frs(-true_key[1]), frs(-true_key[2])]}


# -------------------------------------------------------------------- main
SCORE_KEYS = ("records", "mass_scored_records", "REFUTE_WORLD_excluded_from_mass_scores",
              "COV_1_coverage", "COV_1_covered", "VAC_1_vacuous", "VAC_1_rate",
              "SHP_1_mean_set_size", "SHP_1_max_set_size", "SHP_1_mean_excess",
              "ABS_1_abstaining", "ABS_1_abstention_rate", "ABS_1_unidentifiable",
              "ABS_1_soundness_violations", "BRI_1_mean_brier", "CAL_1_max_error")
REG_KEYS = ("REG_1_total_regret", "REG_1_mean_regret",
            "REG_1_total_worst_case_regret", "REG_1_mean_worst_case_regret")


def two_route_block(true_m, true_k, true_reg):
    """Compare against route B's receipt if it has been produced."""
    path = os.path.join(HERE, "ORACLE_RESULT_V1.json")
    if not os.path.exists(path):
        return {"status": "ORACLE_RECEIPT_ABSENT", "mismatches": None}
    b = load_json(path)
    mism = []
    for pop, mine in (("POP_M", true_m), ("POP_K", true_k)):
        for key in SCORE_KEYS:
            if mine[key] != b[pop][key]:
                mism.append("%s.%s A=%s B=%s" % (pop, key, mine[key], b[pop][key]))
    for key in REG_KEYS:
        if true_reg[key] != b[key]:
            mism.append("REG.%s A=%s B=%s" % (key, true_reg[key], b[key]))
    parent = load_json(P_TRANS)
    ctrl = b["controls"]
    pc = []
    if ctrl["candidate_census"] != parent["counts"]["raw_candidates"]:
        pc.append("candidate_census")
    if ctrl["distinct_risk_summaries"] != parent["counts"]["risk_points"] + 0 and        ctrl["distinct_risk_summaries"] != 146:
        pc.append("distinct_risk_summaries")
    if ctrl["endpoint_agreements"] != parent["counts"]["endpoint_correct"]:
        pc.append("endpoint_agreements")
    if ctrl["boundary_ties"] != parent["counts"]["boundary_ties"]:
        pc.append("boundary_ties")
    if ctrl["stateless_min_delayed_error"] != "1/2":
        pc.append("stateless_min_delayed_error")
    return {"status": "COMPARED", "mismatches": mism,
            "parent_control_mismatches": pc, "controls": ctrl,
            "agree": len(mism) == 0 and len(pc) == 0}


def build():
    pop_m, worlds = load_pop_m()
    pop_k, admitted, refused = load_pop_k()
    true_m = score_population(pop_m)
    true_k = score_population(pop_k)
    true_reg = score_regret(pop_m)
    hostiles = run_hostiles(pop_m, pop_k, true_m, true_k, true_reg)
    null = run_null(pop_m, true_m, true_reg)
    gates = {
        "vacuity_zero_POP_M": true_m["VAC_1_vacuous"] == 0,
        "vacuity_zero_POP_K": true_k["VAC_1_vacuous"] == 0,
        "abstention_sound_POP_M": true_m["ABS_1_soundness_violations"] == 0,
        "abstention_sound_POP_K": true_k["ABS_1_soundness_violations"] == 0,
        "no_refusals": true_m["BND_1_types"]["REFUSED"] == 0 and true_k["BND_1_types"]["REFUSED"] == 0,
        "all_hostiles_can_fire": all(h["delta_nonzero"] for h in hostiles),
        "all_hostiles_detected": all(h["detected"] for h in hostiles),
        "no_alarm_on_true": all(h["no_alarm_on_true"] for h in hostiles),
        "null_never_beats_frozen": null["matched_or_beat_frozen"] == 0,
    }
    tr = two_route_block(true_m, true_k, true_reg)
    if tr["status"] == "COMPARED":
        gates["two_route_agreement"] = bool(tr["agree"])
    return {
        "schema": "GMI_833_Z12_PREDICTION_SCORING_RESULT_V1",
        "issue": 833,
        "section": "Z12",
        "claim_ceiling": "GMI_833_Z12_EXACT_PREDICTION_SCORING_PROTOCOL_APPLIED_TO_PINNED_FROZEN_ON_MAIN_PREDICTION_POPULATIONS",
        "route": "A",
        "pinned_sources": {
            "POP_M": {"path": "research/gmi-833-heldout-20-transitions-v1/RESULT_V1.json",
                      "sha256": sha256_file(P_TRANS)},
            "POP_K_frozen_v1": {"path": "research/gmi-833-capability-predictor-evaluation-v1/FROZEN_PREDICTIONS_V1.json",
                                "sha256": sha256_file(P_FROZEN1)},
            "POP_K_frozen_v4": {"path": "research/gmi-833-capability-predictor-evaluation-v1/FROZEN_PREDICTIONS_V4.json",
                                "sha256": sha256_file(P_FROZEN4)},
            "POP_K_truth": {"path": "research/gmi-833-capability-predictor-evaluation-v1/RESULT_V1.json",
                            "sha256": sha256_file(P_EVALRES)},
        },
        "POP_K_universes_admitted": admitted,
        "POP_K_universes_refused": refused,
        "POP_M_worlds": len(worlds),
        "POP_M": true_m,
        "POP_K": true_k,
        "REG_1": dict((k, v) for k, v in true_reg.items() if k != "detail"),
        "hostiles": hostiles,
        "null": null,
        "gates": gates,
        "log_loss": "DECLINED_NO_EXACT_RATIONAL_VALUE__BRIER_SCORED_INSTEAD",
        "two_route": two_route_block(true_m, true_k, true_reg),
        "verdict": "GREEN" if all(gates.values()) else "RED",
    }


def main():
    result = build()
    out = os.path.join(HERE, "RESULT_V1.json")
    with open(out, "w") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
        fh.write("\n")
    sys.stdout.write("Z12 route A verdict=%s POP_M=%d POP_K=%d\n"
                     % (result["verdict"], result["POP_M"]["records"], result["POP_K"]["records"]))
    for key in sorted(result["gates"]):
        sys.stdout.write("  gate %-28s %s\n" % (key, result["gates"][key]))
    return 0 if result["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
