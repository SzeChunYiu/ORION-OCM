"""Canonical executor: score the frozen predictions against external outcomes.

Introduced strictly after the freeze commit.  Regenerates the frozen prediction
stream, refuses to proceed unless its sha256 matches the value pinned in
``FROZEN_PREDICTIONS_V1.json``, then evaluates every held-out row.

Run:  python3 -I -B score_heldout_v1.py      (writes/prints RESULT_V1.json)
"""

from fractions import Fraction
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu          # noqa: E402
import heldout_universes_v2 as hv          # noqa: E402
import heldout_universes_v3 as hw          # noqa: E402
import heldout_universes_v4 as hx          # noqa: E402
import external_evaluator_v1 as ev         # noqa: E402
import freeze_predictions_v1 as fp         # noqa: E402

UNSATISFIED = "UNSATISFIED"
FREEZE_COMMIT_FILE = os.path.join(HERE, "FREEZE_COMMIT.txt")
CLAIM_CEILING = fp.CLAIM_CEILING

FORBIDDEN_PROMOTIONS = (
    "NO_UNIVERSAL_CAPABILITY_PREDICTION_CLAIM",
    "NO_CLAIM_BEYOND_THE_REGISTERED_HELDOUT_UNIVERSES",
    "NO_CLAIM_THAT_REAL_TRAINING_OUTCOMES_GENERALISE_BEYOND_THE_PINNED_SOURCE",
    "NO_PROMOTION_OF_FINITE_EXACT_COVERAGE_TO_ASYMPTOTIC_CALIBRATION",
    "NO_REWRITE_OF_PARENT_ROWS_KP1_KP2_KP3",
)


def pc(mask):
    return bin(mask).count("1")


def fs(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


# --------------------------------------------------------------------------
# Verdict partitions (mask arithmetic instead of per-world loops)
# --------------------------------------------------------------------------


def value_masks(caps, res_mask, n):
    """value -> bitmask of worlds whose verdict under (E,R) equals that value."""
    out = {}
    for i in range(n):
        if (res_mask >> i) & 1:
            key = str(caps[i])
        else:
            key = UNSATISFIED
        out[key] = out.get(key, 0) | (1 << i)
    return out


def union_of(masks, keys):
    total = 0
    for key in keys:
        total |= masks.get(key, 0)
    return total


def local_ceiling(caps, mask, n):
    best = None
    i = 0
    m = mask
    while m:
        if m & 1:
            if best is None or caps[i] > best:
                best = caps[i]
        m >>= 1
        i += 1
    return best


# --------------------------------------------------------------------------
# Registered fault law for the calibration row
# --------------------------------------------------------------------------

FAULT_CHANNELS = ("source", "M", "D", "B", "H")


def fault_weights(alpha, betas):
    """Exact weight of each of the 32 fault patterns."""
    rates = (alpha, betas["beta_M"], betas["beta_D"], betas["beta_B"], betas["beta_H"])
    out = []
    for pattern in range(32):
        weight = Fraction(1)
        for j in range(5):
            if (pattern >> j) & 1:
                weight *= rates[j]
            else:
                weight *= (Fraction(1) - rates[j])
        out.append((pattern, weight))
    return tuple(out)


def coverage_under_faults(cuts5, full_mask, hit_mask, weights):
    """Exact P(q(theta) in I) under the registered arbitrary-dependence fault law."""
    total = Fraction(0)
    for pattern, weight in weights:
        relaxed = full_mask
        for j in range(5):
            if not ((pattern >> j) & 1):
                relaxed &= cuts5[j]
        den = pc(relaxed)
        if den == 0:
            continue
        total += weight * Fraction(pc(relaxed & hit_mask), den)
    return total


# --------------------------------------------------------------------------
# Per-universe evaluation
# --------------------------------------------------------------------------


def evaluate_universe(parent, spec, frozen, hostile=None):
    name = spec["__name__"]
    machines = spec["__machines__"]
    clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
    hu.install_universe(parent, clean)
    n = parent.N
    full = parent.FULL_MASK

    reg_bits = ev.registered_bits(name)
    _m, meas_bits, mu, source = ev.measure_universe(name)
    if meas_bits is None:
        return {"universe": name, "status": "OUTCOMES_UNAVAILABLE",
                "outcome_source": source}

    if hostile == "HE1_shifted_capability_law":
        mu = (mu[0] + Fraction(1, 97), mu[1], mu[2])

    # registration truthfulness: registered law vs measured simulation
    truth_hits = sum(1 for i in range(n) if reg_bits[i] == meas_bits[i])
    mismatches = [i for i in range(n) if reg_bits[i] != meas_bits[i]]
    truthful_mask = 0
    for i in range(n):
        if reg_bits[i] == meas_bits[i]:
            truthful_mask |= 1 << i

    measured_caps = {}
    for contract in parent.CONTRACTS:
        measured_caps[contract] = tuple(
            ev.measured_cap(meas_bits[i], mu, contract) for i in range(n))

    mval = {}
    rval = {}
    for contract in parent.CONTRACTS:
        for r_value in parent.R_VALUES:
            res = parent.RES_MASKS[r_value]
            mval[(contract, r_value)] = value_masks(measured_caps[contract], res, n)
            rval[(contract, r_value)] = value_masks(parent.CAP[contract], res, n)

    ceil_cache = {}

    def ext_ceiling(contract, mask):
        key = (contract, mask)
        if key not in ceil_cache:
            ceil_cache[key] = local_ceiling(measured_caps[contract], mask, n)
        return ceil_cache[key]

    weights_cache = {}
    cov_cache = {}

    stats = {
        "pairs": 0,
        "point_pairs": 0,
        "hits": 0,
        "soundness_violations": 0,
        "coverage_pairs": 0,
        "coverage_hits": 0,
        "abstention_pairs": 0,
        "abstention_coverage_hits": 0,
        "inputs_identified": 0,
        "inputs_abstained": 0,
        "inputs_inconsistent": 0,
        "violating_inputs": [],
        "image_mismatch_inputs": 0,
        "nondegenerate_points": 0,
        "nondegenerate_point_pairs": 0,
        "nondegenerate_point_hits": 0,
        "truthful_pairs": 0,
        "truthful_hits": 0,
        "truthful_violations": 0,
        "untruthful_pairs": 0,
        "untruthful_violations": 0,
    }
    mode_matrix = {}
    mode_stratum = {"ORDER_FREE": {"agree": 0, "disagree": 0},
                    "CONJUNCTIVE": {"agree": 0, "disagree": 0},
                    "NO_CROSSING": {"agree": 0, "disagree": 0}}
    calib = {}
    rows = []
    idx = 0

    for k_index in range(len(parent.K_M_VALUES)):
        for r_value in parent.R_VALUES:
            for d_value in parent.D_VALUES:
                for b_value in parent.B_VALUES:
                    for h_value in parent.H_VALUES:
                        for u_id, u_kind, u_mask, alpha in parent.U_VALUES:
                            for contract in parent.CONTRACTS:
                                cuts, _ = parent.ladder_masks(k_index, r_value, d_value,
                                                              b_value, h_value, u_mask)
                                ceil_by_subset = fp.order_partition(parent, cuts, contract)
                                cuts5 = (u_mask,
                                         parent.EXPR_MASKS[k_index],
                                         parent.REACH_MASKS[d_value],
                                         parent.SEEN_MASKS[b_value],
                                         parent.OBS_MASKS[h_value])
                                survivors = parent.survivor_mask(
                                    k_index, d_value, b_value, h_value, u_mask)
                                ladder = [full]
                                cur = full
                                for cname in parent.CUT_NAMES:
                                    cur &= cuts[cname]
                                    ladder.append(cur)
                                ext_ceils = tuple(ext_ceiling(contract, m) for m in ladder)
                                for tau in parent.TAU_VALUES:
                                    entry = (k_index, r_value, d_value, b_value, h_value,
                                             u_id, u_kind, u_mask, alpha, contract, tau)
                                    emission, _c, _m2, ceilings, surv2, res, _q = \
                                        parent.evaluate(entry)
                                    disp = emission.disposition
                                    if disp == "INCONSISTENT_REGISTERED_ASSUMPTIONS":
                                        stats["inputs_inconsistent"] += 1
                                        idx += 1
                                        continue
                                    keys = [fs(v) for v in emission.identified_set]
                                    hit_mask = union_of(mval[(contract, r_value)], keys)
                                    reg_hit = union_of(rval[(contract, r_value)], keys)
                                    if hostile == "HE6_truncate_identified_set" and len(keys) > 1:
                                        hit_mask = union_of(mval[(contract, r_value)], keys[:1])
                                    survivors_eff = survivors
                                    if hostile == "HE3_resource_prune":
                                        survivors_eff = survivors & parent.RES_MASKS[r_value]
                                    size = pc(survivors_eff)
                                    stats["pairs"] += size
                                    stats["coverage_pairs"] += size
                                    covered = pc(survivors_eff & hit_mask)
                                    stats["coverage_hits"] += covered
                                    if pc(survivors & reg_hit) != pc(survivors):
                                        stats["image_mismatch_inputs"] += 1
                                    if disp == "IDENTIFIED":
                                        stats["inputs_identified"] += 1
                                        stats["point_pairs"] += size
                                        point_mask = union_of(
                                            mval[(contract, r_value)], [fs(emission.value)])
                                        good = pc(survivors_eff & point_mask)
                                        stats["hits"] += good
                                        bad = size - good
                                        if fs(emission.value) not in ("0", UNSATISFIED):
                                            stats["nondegenerate_points"] += 1
                                            stats["nondegenerate_point_pairs"] += size
                                            stats["nondegenerate_point_hits"] += good
                                        t_sub = survivors_eff & truthful_mask
                                        u_sub = survivors_eff & ~truthful_mask
                                        stats["truthful_pairs"] += pc(t_sub)
                                        stats["truthful_hits"] += pc(t_sub & point_mask)
                                        stats["truthful_violations"] += (
                                            pc(t_sub) - pc(t_sub & point_mask))
                                        stats["untruthful_pairs"] += pc(u_sub)
                                        stats["untruthful_violations"] += (
                                            pc(u_sub) - pc(u_sub & point_mask))
                                        if bad:
                                            stats["soundness_violations"] += bad
                                            if len(stats["violating_inputs"]) < 5:
                                                stats["violating_inputs"].append({
                                                    "idx": idx, "k_index": k_index,
                                                    "r_index": parent.R_VALUES.index(r_value),
                                                    "d": d_value, "b": b_value,
                                                    "h_index": parent.H_VALUES.index(h_value),
                                                    "u_id": u_id, "contract": contract,
                                                    "tau": str(tau),
                                                    "point": fs(emission.value),
                                                    "wrong_worlds": bad})
                                    elif disp == "CANNOT_IDENTIFY":
                                        stats["inputs_abstained"] += 1
                                        stats["abstention_pairs"] += size
                                        stats["abstention_coverage_hits"] += covered

                                    # --- qualitative failure mode ---
                                    ext_q = set()
                                    mm = mval[(contract, r_value)]
                                    for key, mask in mm.items():
                                        if not (mask & survivors):
                                            continue
                                        if key == UNSATISFIED:
                                            ext_q.add(0)
                                        else:
                                            ext_q.add(1 if Fraction(key) >= tau else 0)
                                    ext_flags = parent.mode_flags(
                                        "REGISTERED", survivors, ext_ceils, tau,
                                        frozenset(ext_q))
                                    ext_live = parent.assigned_mode(ext_flags)
                                    ext_mode = ext_live[0] if len(ext_live) == 1 else \
                                        "MULTI:" + "|".join(ext_live)
                                    flags = parent.mode_flags(
                                        "REGISTERED", survivors, ceilings, tau,
                                        frozenset(
                                            1 if parent.meets(parent.verdict(contract, res, i), tau)
                                            else 0 for i in parent.bits_of(survivors)))
                                    live = parent.assigned_mode(flags)
                                    pred_mode = live[0] if len(live) == 1 else \
                                        "MULTI:" + "|".join(live)
                                    labels = fp.labels_over_orders(parent, ceil_by_subset, tau)
                                    if labels == set((None,)):
                                        stratum = "NO_CROSSING"
                                    elif len(labels) == 1:
                                        stratum = "ORDER_FREE"
                                    else:
                                        stratum = "CONJUNCTIVE"
                                    cell = pred_mode + "->" + ext_mode
                                    mode_matrix[cell] = mode_matrix.get(cell, 0) + 1
                                    if pred_mode == ext_mode:
                                        mode_stratum[stratum]["agree"] += 1
                                    else:
                                        mode_stratum[stratum]["disagree"] += 1

                                    # --- calibration (confidence emissions only) ---
                                    if u_kind == "CONFIDENCE_SET":
                                        betas = dict(parent.BETA)
                                        if hostile == "HE5_inflated_fault_law":
                                            betas = dict((k2, v * 20) for k2, v in betas.items())
                                        wkey = (str(alpha), hostile == "HE5_inflated_fault_law")
                                        if wkey not in weights_cache:
                                            weights_cache[wkey] = fault_weights(alpha, betas)
                                        weights = weights_cache[wkey]
                                        ckey = (cuts5, hit_mask, wkey)
                                        if ckey not in cov_cache:
                                            cov_cache[ckey] = coverage_under_faults(
                                                cuts5, full, hit_mask, weights)
                                        cov = cov_cache[ckey]
                                        bucket = calib.setdefault(
                                            str(alpha),
                                            {"emissions": 0, "point_emissions": 0,
                                             "sum_coverage": Fraction(0),
                                             "sum_point_coverage": Fraction(0),
                                             "min_coverage": None,
                                             "min_point_coverage": None,
                                             "point_violations": 0,
                                             "violations": 0,
                                             "nominal_lower": str(emission.uncertainty.coverage_lower),
                                             "abstentions": 0})
                                        bucket["emissions"] += 1
                                        bucket["sum_coverage"] += cov
                                        if bucket["min_coverage"] is None or cov < bucket["min_coverage"]:
                                            bucket["min_coverage"] = cov
                                        if cov < emission.uncertainty.coverage_lower:
                                            bucket["violations"] += 1
                                        if disp == "IDENTIFIED":
                                            pmask = union_of(mval[(contract, r_value)],
                                                             [fs(emission.value)])
                                            pkey = (cuts5, pmask, wkey)
                                            if pkey not in cov_cache:
                                                cov_cache[pkey] = coverage_under_faults(
                                                    cuts5, full, pmask, weights)
                                            pcov = cov_cache[pkey]
                                            bucket["point_emissions"] += 1
                                            bucket["sum_point_coverage"] += pcov
                                            if (bucket["min_point_coverage"] is None
                                                    or pcov < bucket["min_point_coverage"]):
                                                bucket["min_point_coverage"] = pcov
                                            if pcov < emission.uncertainty.coverage_lower:
                                                bucket["point_violations"] += 1
                                        else:
                                            bucket["abstentions"] += 1
                                    idx += 1

    total_answerable = stats["inputs_identified"] + stats["inputs_abstained"]
    result = {
        "universe": name,
        "status": "SCORED",
        "outcome_source": source,
        "grid_size": idx,
        "registration": {
            "machines": n,
            "law_matches_simulation": truth_hits,
            "law_mismatches": len(mismatches),
            "mismatch_examples": [list(machines[i]) for i in mismatches[:5]],
            "truthful": len(mismatches) == 0,
            "truthfulness_rate": str(Fraction(truth_hits, n)),
        },
        "point_scoring": {
            "inputs_identified": stats["inputs_identified"],
            "inputs_abstained": stats["inputs_abstained"],
            "inputs_inconsistent": stats["inputs_inconsistent"],
            "point_world_pairs": stats["point_pairs"],
            "point_hits": stats["hits"],
            "soundness_violations": stats["soundness_violations"],
            "violating_examples": stats["violating_inputs"],
            "abstention_rate_among_answerable": (
                str(Fraction(stats["inputs_abstained"], total_answerable))
                if total_answerable else "0"),
            "point_rate_among_answerable": (
                str(Fraction(stats["inputs_identified"], total_answerable))
                if total_answerable else "0"),
            "registered_image_mismatch_inputs": stats["image_mismatch_inputs"],
            "nondegenerate_point_emissions": stats["nondegenerate_points"],
            "nondegenerate_point_world_pairs": stats["nondegenerate_point_pairs"],
            "nondegenerate_point_hits": stats["nondegenerate_point_hits"],
            "truthfully_registered_world_pairs": stats["truthful_pairs"],
            "truthfully_registered_hits": stats["truthful_hits"],
            "soundness_violations_on_truthfully_registered_worlds":
                stats["truthful_violations"],
            "untruthfully_registered_world_pairs": stats["untruthful_pairs"],
            "bridge_failures_on_untruthfully_registered_worlds":
                stats["untruthful_violations"],
        },
        "coverage": {
            "pairs": stats["coverage_pairs"],
            "hits": stats["coverage_hits"],
            "exact": stats["coverage_hits"] == stats["coverage_pairs"],
            "abstention_pairs": stats["abstention_pairs"],
            "abstention_coverage_hits": stats["abstention_coverage_hits"],
        },
        "qualitative_modes": {
            "confusion_matrix": dict(sorted(mode_matrix.items())),
            "by_order_stratum": mode_stratum,
        },
        "calibration": {},
    }
    for key in sorted(calib):
        bucket = calib[key]
        mean = bucket["sum_coverage"] / bucket["emissions"] if bucket["emissions"] else Fraction(0)
        pmean = (bucket["sum_point_coverage"] / bucket["point_emissions"]
                 if bucket["point_emissions"] else None)
        nominal = Fraction(bucket["nominal_lower"])
        result["calibration"][key] = {
            "alpha": key,
            "nominal_lower_bound": bucket["nominal_lower"],
            "emissions": bucket["emissions"],
            "abstentions_among_them": bucket["abstentions"],
            "abstention_rate": str(Fraction(bucket["abstentions"], bucket["emissions"]))
            if bucket["emissions"] else "0",
            "mean_empirical_coverage": str(mean),
            "min_empirical_coverage": str(bucket["min_coverage"]),
            "point_emissions": bucket["point_emissions"],
            "mean_point_coverage": str(pmean) if pmean is not None else None,
            "min_point_coverage": (str(bucket["min_point_coverage"])
                                   if bucket["min_point_coverage"] is not None else None),
            "point_violations_below_nominal": bucket["point_violations"],
            "point_calibration_error_min": (
                str(bucket["min_point_coverage"] - nominal)
                if bucket["min_point_coverage"] is not None else None),
            "calibration_error_mean": str(mean - nominal),
            "calibration_error_min": str(bucket["min_coverage"] - nominal),
            "violations_below_nominal": bucket["violations"],
        }
    return result


# --------------------------------------------------------------------------
# Quantitative curves
# --------------------------------------------------------------------------


def evaluate_curves(parent, spec, frozen_curves):
    name = spec["__name__"]
    machines = spec["__machines__"]
    clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
    hu.install_universe(parent, clean)
    n = parent.N
    _m, meas_bits, mu, source = ev.measure_universe(name)
    if meas_bits is None:
        return {"universe": name, "status": "OUTCOMES_UNAVAILABLE"}
    measured_caps = dict(
        (c, tuple(ev.measured_cap(meas_bits[i], mu, c) for i in range(n)))
        for c in parent.CONTRACTS)
    points_total = 0
    points_agree = 0
    points_abstain = 0
    detail = []
    fi = 0
    for case in fp.CURVE_CASES:
        k_index, charge_index, d_index, b_index, h_index, u_id, contract = case
        d_value = parent.D_VALUES[d_index]
        b_value = parent.B_VALUES[b_index]
        h_value = parent.H_VALUES[h_index]
        u_entry = [u for u in parent.U_VALUES if u[0] == u_id][0]
        for tau in parent.TAU_VALUES:
            swept = []
            for budget in parent.BUDGETS:
                r_value = (budget, parent.CHARGES[charge_index])
                entry = (k_index, r_value, d_value, b_value, h_value,
                         u_entry[0], u_entry[1], u_entry[2], u_entry[3], contract, tau)
                emission, _c, _m2, _ce, survivors, res, _q = parent.evaluate(entry)
                frozen_point = frozen_curves[fi]["points"][len(swept)]
                mm = value_masks(measured_caps[contract], parent.RES_MASKS[r_value], n)
                ext_vals = sorted(set(
                    key for key, mask in mm.items() if mask & survivors))
                agree = None
                if emission.disposition == "IDENTIFIED":
                    points_total += 1
                    agree = (ext_vals == [fs(emission.value)])
                    if agree:
                        points_agree += 1
                elif emission.disposition == "CANNOT_IDENTIFY":
                    points_abstain += 1
                swept.append({
                    "budget": list(budget),
                    "frozen_disposition": frozen_point["disposition"],
                    "frozen_value": frozen_point["value"],
                    "replayed_disposition": emission.disposition,
                    "replay_matches_freeze": (
                        frozen_point["disposition"] == emission.disposition
                        and frozen_point["value"] == fs(emission.value)),
                    "external_values": ext_vals,
                    "exact_agreement": agree,
                })
            detail.append({"case_index": fi, "points": swept})
            fi += 1
    return {
        "universe": name,
        "status": "SCORED",
        "curve_cases": fi,
        "swept_points": fi * len(parent.BUDGETS),
        "identified_points": points_total,
        "identified_points_exact_agreement": points_agree,
        "abstaining_points": points_abstain,
        "replay_mismatches": sum(
            1 for c in detail for p in c["points"] if not p["replay_matches_freeze"]),
        "detail": detail,
    }


# --------------------------------------------------------------------------
# Out-of-distribution probe
# --------------------------------------------------------------------------


def ood_probe(parent, spec):
    """Structural OOD probe.

    A world is out-of-universe iff its realization is not a member of the
    installed universe.  Only the three cuts that are properties of the WORLD
    (expressivity, development reachability, observation) can exclude such a
    world; the search-budget cut is a statement about the analyst's enumeration
    and the typed-uncertainty mask indexes registered members only, so neither
    can rule an unregistered world out.
    """
    name = spec["__name__"]
    clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
    hu.install_universe(parent, clean)
    ood = ev.build_sigma_ood()
    mu = hu.MU_SYN
    consistent = {}
    for k_index in range(len(parent.K_M_VALUES)):
        k_m = parent.K_M_VALUES[k_index]
        for d_value in parent.D_VALUES:
            for h_value in parent.H_VALUES:
                sel = []
                for j, rec in enumerate(ood):
                    if rec["k"] not in k_m:
                        continue
                    if rec["dev"] > d_value:
                        continue
                    if h_value != "NO_OBSERVATION" and rec["obs"] != h_value:
                        continue
                    sel.append(j)
                consistent[(k_index, d_value, h_value)] = tuple(sel)
    ood_val = {}
    for contract in parent.CONTRACTS:
        for r_value in parent.R_VALUES:
            budget, charge = r_value
            ood_val[(contract, r_value)] = tuple(
                fs(ev.extcap(rec["rho"], rec["bits"], mu, contract, budget, charge))
                for rec in ood)
    checked = 0
    consistent_pairs = 0
    wrong_points = 0
    abstained_with_ood = 0
    covered_pairs = 0
    examples = []
    by_relaxation = {}
    cache = {}
    for k_index in range(len(parent.K_M_VALUES)):
        for r_value in parent.R_VALUES:
            for d_value in parent.D_VALUES:
                for b_value in parent.B_VALUES:
                    for h_value in parent.H_VALUES:
                        sel = consistent[(k_index, d_value, h_value)]
                        for u_id, u_kind, u_mask, alpha in parent.U_VALUES:
                            for contract in parent.CONTRACTS:
                                vals = ood_val[(contract, r_value)]
                                for tau in parent.TAU_VALUES:
                                    entry = (k_index, r_value, d_value, b_value, h_value,
                                             u_id, u_kind, u_mask, alpha, contract, tau)
                                    emission, _c, _m, _ce, _s, _r, _q = parent.evaluate(entry)
                                    if emission.disposition not in ("IDENTIFIED",
                                                                    "CANNOT_IDENTIFY"):
                                        continue
                                    checked += 1
                                    consistent_pairs += len(sel)
                                    keys = tuple(fs(v) for v in emission.identified_set)
                                    ckey = (k_index, d_value, h_value, contract, r_value, keys)
                                    if ckey not in cache:
                                        inside = 0
                                        for j in sel:
                                            if vals[j] in keys:
                                                inside += 1
                                        cache[ckey] = inside
                                    covered_pairs += cache[ckey]
                                    if emission.disposition == "IDENTIFIED":
                                        wrong = len(sel) - cache[ckey]
                                        wrong_points += wrong
                                        if wrong:
                                            for j in sel:
                                                if vals[j] not in keys:
                                                    rel = ood[j]["relaxed"]
                                                    by_relaxation[rel] = by_relaxation.get(rel, 0) + 1
                                                    if len(examples) < 5:
                                                        examples.append({
                                                            "machine": list(ood[j]["machine"]),
                                                            "relaxed": rel,
                                                            "point": keys[0],
                                                            "external": vals[j],
                                                            "contract": contract,
                                                            "tau": str(tau)})
                                    elif len(sel):
                                        abstained_with_ood += 1
    return {
        "universe": name,
        "ood_population": len(ood),
        "ood_relaxations": sorted(set(r["relaxed"] for r in ood)),
        "inputs_probed": checked,
        "input_ood_world_pairs": consistent_pairs,
        "ood_pairs_inside_identified_set": covered_pairs,
        "out_of_universe_wrong_points": wrong_points,
        "wrong_points_by_relaxation": dict(sorted(by_relaxation.items())),
        "abstaining_inputs_with_consistent_ood_worlds": abstained_with_ood,
        "examples": examples,
        "attribution": ("KP-1D: a wrong point on an out-of-universe world is the parent's "
                        "declared registration boundary, not a soundness violation of F"),
    }


# --------------------------------------------------------------------------
# Hostiles and the null control
# --------------------------------------------------------------------------


def controls(parent, spec):
    """Planted defects the scorer must flag, plus a null the true result beats.

    Nothing here edits ``F``.  HE3 and NULL_MODAL are *control predictors*
    written locally and scored against the same external outcomes.
    """
    name = spec["__name__"]
    clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
    hu.install_universe(parent, clean)
    n = parent.N
    _m, meas_bits, mu, source = ev.measure_universe(name)
    if meas_bits is None:
        return {"universe": name, "status": "OUTCOMES_UNAVAILABLE"}
    # HE1: complement every measured solved-set.  Under both registered contracts
    # cap(bits) + cap(7-bits) is a constant that no attainable capability equals,
    # so EVERY machine's capability changes -- unlike a scaling of `mu`, which
    # leaves a capability of 0 fixed.
    true_caps, shift_caps = {}, {}
    for contract in parent.CONTRACTS:
        true_caps[contract] = tuple(ev.measured_cap(meas_bits[i], mu, contract)
                                    for i in range(n))
        shift_caps[contract] = tuple(ev.measured_cap(7 - meas_bits[i], mu, contract)
                                     for i in range(n))
    mval, sval, nobud, modal = {}, {}, {}, {}
    for contract in parent.CONTRACTS:
        for r_value in parent.R_VALUES:
            res = parent.RES_MASKS[r_value]
            mval[(contract, r_value)] = value_masks(true_caps[contract], res, n)
            sval[(contract, r_value)] = value_masks(shift_caps[contract], res, n)
            # HE2: drop the UNSATISFIED branch -- score every machine at its raw value
            nobud[(contract, r_value)] = value_masks(true_caps[contract], parent.FULL_MASK, n)
            counts = {}
            for key, mask in mval[(contract, r_value)].items():
                counts[key] = pc(mask)
            modal[(contract, r_value)] = max(sorted(counts), key=lambda k2: counts[k2])
    out = {
        "universe": name,
        "BASELINE": 0,
        "HE1_complemented_capability_law": 0,
        "HE2_no_unsatisfied_branch": 0,
        "HE3_resource_pruned_predictor_points": 0,
        "HE3_resource_pruned_predictor_violations": 0,
        "HE6_truncated_identified_set_coverage_failures": 0,
        "NULL_MODAL_points": 0,
        "NULL_MODAL_violations": 0,
        "NULL_MODAL_head_to_head_pairs": 0,
        "NULL_MODAL_head_to_head_violations": 0,
        "F_head_to_head_violations": 0,
        "nondegenerate_points": 0,
    }
    for k_index in range(len(parent.K_M_VALUES)):
        for r_value in parent.R_VALUES:
            res = parent.RES_MASKS[r_value]
            for d_value in parent.D_VALUES:
                for b_value in parent.B_VALUES:
                    for h_value in parent.H_VALUES:
                        for u_id, u_kind, u_mask, alpha in parent.U_VALUES:
                            for contract in parent.CONTRACTS:
                                survivors = parent.survivor_mask(
                                    k_index, d_value, b_value, h_value, u_mask)
                                if not survivors:
                                    continue
                                size = pc(survivors)
                                entry = (k_index, r_value, d_value, b_value, h_value,
                                         u_id, u_kind, u_mask, alpha, contract,
                                         parent.TAU_VALUES[0])
                                emission, _c, _m2, _ce, _s, _r, _q = parent.evaluate(entry)
                                keys = [fs(v) for v in emission.identified_set]
                                # null control: always emit the modal true capability
                                mkey = modal[(contract, r_value)]
                                out["NULL_MODAL_points"] += 1
                                out["NULL_MODAL_violations"] += size - pc(
                                    survivors & mval[(contract, r_value)].get(mkey, 0))
                                if emission.disposition == "IDENTIFIED":
                                    point = fs(emission.value)
                                    if point not in ("0", UNSATISFIED):
                                        out["nondegenerate_points"] += 1
                                    good = pc(survivors & mval[(contract, r_value)].get(point, 0))
                                    out["BASELINE"] += size - good
                                    out["HE1_complemented_capability_law"] += size - pc(
                                        survivors & sval[(contract, r_value)].get(point, 0))
                                    out["HE2_no_unsatisfied_branch"] += size - pc(
                                        survivors & nobud[(contract, r_value)].get(point, 0))
                                    out["NULL_MODAL_head_to_head_pairs"] += size
                                    out["NULL_MODAL_head_to_head_violations"] += size - pc(
                                        survivors & mval[(contract, r_value)].get(mkey, 0))
                                    out["F_head_to_head_violations"] += size - good
                                elif len(keys) > 1:
                                    truncated = union_of(mval[(contract, r_value)], keys[:1])
                                    out["HE6_truncated_identified_set_coverage_failures"] += (
                                        size - pc(survivors & truncated))
                                # HE3: the parent's H4 replayed -- prune by admissibility
                                pruned = survivors & res
                                if pruned:
                                    image = set()
                                    for key, mask in mval[(contract, r_value)].items():
                                        if mask & pruned and key != UNSATISFIED:
                                            image.add(key)
                                    if len(image) == 1:
                                        pk = image.pop()
                                        out["HE3_resource_pruned_predictor_points"] += 1
                                        out["HE3_resource_pruned_predictor_violations"] += (
                                            size - pc(survivors & mval[(contract, r_value)].get(pk, 0)))
    # HE1 can only bite where a NON-DEGENERATE point is emitted: complementing the
    # solved-set leaves a capability of 0 at 0 and never changes an UNSATISFIED
    # verdict, so on a universe whose every point is degenerate the hostile is
    # vacuous. That is recorded, not papered over -- it is exactly the power
    # defect the V4 revival fixes.
    out["HE1_applicable"] = out["nondegenerate_points"] > 0
    out["all_hostiles_detected"] = all((
        out["BASELINE"] == 0,
        (out["HE1_complemented_capability_law"] > 0) if out["HE1_applicable"] else True,
        out["HE2_no_unsatisfied_branch"] > 0,
        out["HE3_resource_pruned_predictor_violations"] > 0,
        out["HE6_truncated_identified_set_coverage_failures"] > 0,
        out["NULL_MODAL_violations"] > 0,
        out["F_head_to_head_violations"] == 0,
    ))
    return out


def main():
    parent = hu.load_parent()
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V1.json")) as handle:
        frozen = json.load(handle)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V2.json")) as handle:
        frozen_v2 = json.load(handle)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V3.json")) as handle:
        frozen_v3 = json.load(handle)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V4.json")) as handle:
        frozen_v4 = json.load(handle)
    frozen["universes"] = (list(frozen["universes"]) + list(frozen_v2["universes"])
                           + list(frozen_v3["universes"])
                           + list(frozen_v4["universes"]))
    parent_sha = hu.git_blob_sha(hu.PARENT_FILE)
    with open(hu.PARENT_FILE, "rb") as handle:
        parent_source_sha256 = hashlib.sha256(handle.read()).hexdigest()
    baseline = hu.code_fingerprint(parent)
    out = {
        "schema": "GMI_833_K_EVAL_RESULT_V1",
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "parent_file_blob_sha": parent_sha,
        "parent_blob_pin_ok": parent_sha == hu.PARENT_BLOB_SHA,
        "parent_source_sha256": parent_source_sha256,
        "freeze": {
            "frozen_parent_blob": frozen["parent_file_blob_sha"],
            "parent_blob_matches_freeze":
                frozen["parent_file_blob_sha"] == parent_sha,
            "bytecode_fingerprint_note": (
                "the co_code digest recorded in FROZEN_PREDICTIONS_V1.json is "
                "interpreter-version specific and is therefore NOT used as a "
                "cross-run identity check; the in-process before/after co_code "
                "comparison inside install_universe is the injection proof, and "
                "the git blob sha is the cross-run identity of F"),
        },
        "universes": [],
        "curves": [],
        "ood": None,
    }
    frozen_by_name = dict((u["universe"], u) for u in frozen["universes"])

    builders = (hu.sigma_syn, hu.sigma_arch, hu.sigma_real, hv.sigma_real2,
                hw.sigma_real3, hx.sigma_syn2, hx.sigma_arch2)
    specs = []
    for builder in builders:
        spec = builder()
        specs.append(spec)

    # 1. replay the frozen prediction stream and verify its sha256
    replay = []
    for spec in specs:
        clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
        hu.install_universe(parent, clean)
        summary, stream = fp.sweep(parent, spec["__name__"])
        digest = hashlib.sha256(stream.encode("utf-8")).hexdigest()
        pinned = frozen_by_name[spec["__name__"]]["predictions_sha256"]
        replay.append({
            "universe": spec["__name__"],
            "replayed_sha256": digest,
            "frozen_sha256": pinned,
            "matches_freeze": digest == pinned,
        })
    out["prediction_replay"] = replay

    for spec in specs:
        out["universes"].append(evaluate_universe(parent, spec, frozen_by_name[spec["__name__"]]))
        out["curves"].append(evaluate_curves(
            parent, spec, frozen_by_name[spec["__name__"]]["curves"]))

    out["ood"] = ood_probe(parent, hu.sigma_syn())
    syn_row = [u for u in out["universes"] if u["universe"] == "SIGMA_SYN"][0]
    out["ood"]["in_universe_stratum"] = {
        "universe": "SIGMA_SYN",
        "input_world_pairs": syn_row["point_scoring"]["point_world_pairs"],
        "soundness_violations": syn_row["point_scoring"]["soundness_violations"],
        "note": "true realization inside the installed universe; KP-1B applies",
    }
    out["ood"]["out_of_universe_stratum"] = {
        "population": out["ood"]["ood_population"],
        "input_world_pairs": out["ood"]["input_ood_world_pairs"],
        "wrong_points": out["ood"]["out_of_universe_wrong_points"],
        "note": "true realization outside the installed universe; KP-1D applies, "
                "a wrong point here is a registration boundary, not a soundness failure",
    }
    out["controls"] = [controls(parent, hx.sigma_syn2()), controls(parent, hx.sigma_arch2()),
                       controls(parent, hu.sigma_syn()), controls(parent, hu.sigma_arch())]
    hostile_calib = evaluate_universe(parent, hu.sigma_syn(), None,
                                      hostile="HE5_inflated_fault_law")
    out["HE5_inflated_fault_law"] = {
        "universe": "SIGMA_SYN",
        "violations_below_nominal": dict(
            (k, v["violations_below_nominal"]) for k, v in hostile_calib["calibration"].items()),
        "detected": any(v["violations_below_nominal"] > 0
                        for v in hostile_calib["calibration"].values()),
    }
    body = json.dumps(fp.canonical(out), indent=2, sort_keys=True)
    with open(os.path.join(HERE, "RESULT_V1.json"), "w") as handle:
        handle.write(body)
        handle.write("\n")
    sys.stdout.write(body)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
