"""Prospective prediction generator for the #833 Section-K evaluation tranche.

This file runs the UNMODIFIED parent predictor ``F`` against the held-out
universes and writes every prediction, together with a per-case order-free /
conjunctive flag and the power statistics, to ``FROZEN_PREDICTIONS_V1.json``
and ``FROZEN_PREDICTIONS_V1.tsv``.

It contains no outcome oracle: nothing here can observe the true externally
evaluated capability of any machine.  The external evaluator is introduced in a
strictly later commit, and CI asserts that ordering.

Run:  python3 -I -B freeze_predictions_v1.py
"""

from fractions import Fraction
import hashlib
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import heldout_universes_v1 as hu  # noqa: E402

CLAIM_CEILING = (
    "GMI_833_HELDOUT_AND_OOD_EVALUATION_OF_THE_EXACT_CAPABILITY_PREDICTOR"
    "_AT_REGISTERED_FINITE_SCOPE"
)


def frac_str(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def canonical(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return dict((str(k), canonical(v)) for k, v in sorted(value.items(), key=lambda kv: str(kv[0])))
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    if isinstance(value, frozenset):
        return sorted(str(v) for v in value)
    return value


def canonical_json(value):
    return json.dumps(canonical(value), sort_keys=True, separators=(",", ":"))


# --------------------------------------------------------------------------
# Order-free / conjunctive partition (prediction side only)
# --------------------------------------------------------------------------

def order_partition(parent, cuts, contract):
    """Ceilings for every subset-intersection of the five registered cuts."""
    names = parent.CUT_NAMES
    ceil_by_subset = {}
    for size in range(len(names) + 1):
        for combo in itertools.combinations(range(len(names)), size):
            mask = parent.FULL_MASK
            for j in combo:
                mask &= cuts[names[j]]
            ceil_by_subset[combo] = parent.ceiling(contract, mask)
    return ceil_by_subset


def labels_over_orders(parent, ceil_by_subset, tau):
    names = parent.CUT_NAMES
    out = set()
    for order in itertools.permutations(range(len(names))):
        label = None
        acc = ()
        for position in range(len(names) + 1):
            key = tuple(sorted(acc))
            if parent.below(ceil_by_subset[key], tau):
                if position == 0:
                    label = "FM_INFORMATION_CEILING"
                else:
                    label = parent.CUT_TO_MODE[names[order[position - 1]]]
                break
            if position < len(names):
                acc = acc + (order[position],)
        out.add(label)
    return out


# --------------------------------------------------------------------------
# Prediction sweep
# --------------------------------------------------------------------------


def sweep(parent, spec_name):
    rows = []
    counts = {
        "dispositions": {},
        "modes": {},
        "sites": {},
        "order_free": 0,
        "conjunctive": 0,
        "no_crossing": 0,
        "exceptions": 0,
    }
    tau_point = {}
    tau_nondegenerate = {}
    idx = 0
    k_len = len(parent.K_M_VALUES)
    for k_index in range(k_len):
        for r_value in parent.R_VALUES:
            for d_value in parent.D_VALUES:
                for b_value in parent.B_VALUES:
                    for h_value in parent.H_VALUES:
                        for u_id, u_kind, u_mask, alpha in parent.U_VALUES:
                            for contract in parent.CONTRACTS:
                                cuts, _masks = parent.ladder_masks(
                                    k_index, r_value, d_value, b_value, h_value, u_mask)
                                ceil_by_subset = order_partition(parent, cuts, contract)
                                for tau in parent.TAU_VALUES:
                                    entry = (k_index, r_value, d_value, b_value,
                                             h_value, u_id, u_kind, u_mask, alpha,
                                             contract, tau)
                                    try:
                                        (emission, cuts2, masks2, ceilings,
                                         survivors, res, qtau) = parent.evaluate(entry)
                                    except BaseException:
                                        counts["exceptions"] += 1
                                        idx += 1
                                        continue
                                    flags = parent.mode_flags("REGISTERED", survivors,
                                                              ceilings, tau, qtau)
                                    live = parent.assigned_mode(flags)
                                    mode = live[0] if len(live) == 1 else "MULTI:" + "|".join(live)
                                    labels = labels_over_orders(parent, ceil_by_subset, tau)
                                    if labels == set((None,)):
                                        of = "NO_CROSSING"
                                        counts["no_crossing"] += 1
                                    elif len(labels) == 1:
                                        of = "ORDER_FREE"
                                        counts["order_free"] += 1
                                    else:
                                        of = "CONJUNCTIVE"
                                        counts["conjunctive"] += 1
                                    disp = emission.disposition
                                    counts["dispositions"][disp] = counts["dispositions"].get(disp, 0) + 1
                                    counts["modes"][mode] = counts["modes"].get(mode, 0) + 1
                                    counts["sites"][emission.site] = counts["sites"].get(emission.site, 0) + 1
                                    key = str(tau)
                                    if disp == "IDENTIFIED":
                                        tau_point[key] = tau_point.get(key, 0) + 1
                                    if survivors:
                                        met = set()
                                        for i in parent.bits_of(survivors):
                                            met.add(parent.meets(parent.verdict(contract, res, i), tau))
                                        if len(met) == 2:
                                            tau_nondegenerate[key] = tau_nondegenerate.get(key, 0) + 1
                                    rows.append("\t".join((
                                        str(idx),
                                        str(k_index),
                                        str(parent.R_VALUES.index(r_value)),
                                        str(d_value),
                                        str(b_value),
                                        str(parent.H_VALUES.index(h_value)),
                                        u_id,
                                        contract,
                                        str(tau),
                                        disp,
                                        frac_str(emission.value),
                                        ";".join(frac_str(v) for v in emission.identified_set),
                                        mode,
                                        of,
                                        str(parent.popcount(survivors)),
                                        emission.uncertainty.kind,
                                        frac_str(emission.uncertainty.alpha),
                                        frac_str(emission.uncertainty.coverage_lower),
                                    )))
                                    idx += 1
    stream = "\n".join(rows) + "\n"
    digest = hashlib.sha256(stream.encode("utf-8")).hexdigest()
    total = idx
    points = counts["dispositions"].get("IDENTIFIED", 0)
    abstain = counts["dispositions"].get("CANNOT_IDENTIFY", 0)
    power = {
        "grid_size": total,
        "point_emissions": points,
        "abstentions": abstain,
        "inconsistent": counts["dispositions"].get("INCONSISTENT_REGISTERED_ASSUMPTIONS", 0),
        "cannot_check": counts["dispositions"].get("CANNOT_CHECK", 0),
        "point_rate": str(Fraction(points, total)) if total else "0",
        "abstention_rate": str(Fraction(abstain, total)) if total else "0",
        "abstention_rate_among_answerable": (
            str(Fraction(abstain, points + abstain)) if (points + abstain) else "0"),
        "point_emissions_by_tau": dict(sorted(tau_point.items())),
        "nondegenerate_cases_by_tau": dict(sorted(tau_nondegenerate.items())),
    }
    return {
        "universe": spec_name,
        "predictions_sha256": digest,
        "counts": counts,
        "power": power,
    }, stream


def spec_digest(spec):
    payload = {
        "universe": [[list(rec[:3]) if not isinstance(rec[0], str) else list(rec[:3]),
                      rec[3], list(rec[4]), rec[5], list(rec[6])] for rec in spec["UNIVERSE"]],
        "search_rank": list(spec["SEARCH_RANK"]),
        "cap": dict((c, [str(v) for v in spec["CAP"][c]]) for c in spec["CONTRACTS"]),
        "budgets": [list(b) for b in spec["BUDGETS"]],
        "charges": [list(c) for c in spec["CHARGES"]],
        "d_values": list(spec["D_VALUES"]),
        "b_values": list(spec["B_VALUES"]),
        "h_values": [list(h) if not isinstance(h, str) else h for h in spec["H_VALUES"]],
        "tau_values": [str(t) for t in spec["TAU_VALUES"]],
        "u_values": [[u[0], u[1], u[2], str(u[3]) if u[3] is not None else None]
                     for u in spec["U_VALUES"]],
        "mu": [str(m) for m in spec["MU"]],
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest(), payload


# --------------------------------------------------------------------------
# Quantitative resource/capability curves (KE-5), frozen prediction side
# --------------------------------------------------------------------------

CURVE_CASES = (
    # (k_index, charge_index, d_index, b_index, h_index, u_id, contract)
    (7, 0, 2, 4, 0, "U0", "E_full"),
    (7, 0, 2, 4, 0, "U2", "E_v0"),
    (3, 0, 2, 4, 0, "U0", "E_full"),
    (7, 0, 1, 4, 0, "U0", "E_full"),
    (7, 0, 2, 3, 0, "U0", "E_full"),
    (6, 0, 2, 4, 1, "U0", "E_full"),
    (7, 0, 2, 4, 2, "U0", "E_full"),
    (5, 0, 2, 4, 0, "U2", "E_full"),
)


def build_curves(parent):
    """Sweep the resource coordinate: every registered budget, charge fixed."""
    curves = []
    for case in CURVE_CASES:
        k_index, charge_index, d_index, b_index, h_index, u_id, contract = case
        d_value = parent.D_VALUES[d_index]
        b_value = parent.B_VALUES[b_index]
        h_value = parent.H_VALUES[h_index]
        u_entry = [u for u in parent.U_VALUES if u[0] == u_id][0]
        for tau in parent.TAU_VALUES:
            points = []
            for budget in parent.BUDGETS:
                r_value = (budget, parent.CHARGES[charge_index])
                entry = (k_index, r_value, d_value, b_value, h_value,
                         u_entry[0], u_entry[1], u_entry[2], u_entry[3], contract, tau)
                emission, _c, _m, _ce, survivors, _res, _q = parent.evaluate(entry)
                points.append({
                    "budget": list(budget),
                    "disposition": emission.disposition,
                    "value": frac_str(emission.value),
                    "identified_set": [frac_str(v) for v in emission.identified_set],
                    "survivors": parent.popcount(survivors),
                })
            curves.append({
                "case": {"k_index": k_index, "charge_index": charge_index,
                         "d": d_value, "b": b_value, "h_index": h_index,
                         "u_id": u_id, "contract": contract, "tau": str(tau)},
                "swept_coordinate": "R.budget",
                "points": points,
            })
    return curves


def main():
    parent = hu.load_parent()
    parent_sha = hu.git_blob_sha(hu.PARENT_FILE)
    baseline_fp = hu.code_fingerprint(parent)
    out = {
        "schema": "GMI_833_K_EVAL_FROZEN_PREDICTIONS_V1",
        "claim_ceiling": CLAIM_CEILING,
        "parent_file_blob_sha": parent_sha,
        "parent_code_fingerprint_before": baseline_fp[0],
        "parent_function_count": baseline_fp[1],
        "sigma_1_size": parent.N,
        "universes": [],
    }
    streams = {}
    base = hu.sigma_1()
    out["sigma_1_rho3_values"] = sorted(set(rec[4][3] for rec in base))
    prior = [("SIGMA_1", base)]
    for builder in (hu.sigma_syn, hu.sigma_arch, hu.sigma_real):
        spec = builder()
        name = spec["__name__"]
        cert = [hu.disjointness_certificate(b_raw, b_name, spec["UNIVERSE"], name)
                for b_name, b_raw in prior]
        prior.append((name, tuple(spec["UNIVERSE"])))
        clean = dict((k, v) for k, v in spec.items() if not k.startswith("__"))
        fp = hu.install_universe(parent, clean)
        sdig, _payload = spec_digest(spec)
        summary, stream = sweep(parent, name)
        summary["spec_sha256"] = sdig
        summary["disjointness"] = cert
        summary["curves"] = build_curves(parent)
        summary["parent_code_fingerprint_after"] = fp[0]
        summary["parent_code_unchanged"] = (fp[0] == baseline_fp[0])
        out["universes"].append(summary)
        streams[name] = stream
    out["parent_code_fingerprint_after_all"] = hu.code_fingerprint(parent)[0]
    out["prediction_stream_format"] = (
        "idx\tk_index\tr_index\td\tb\th_index\tu_id\tcontract\ttau\tdisposition\t"
        "value\tidentified_set\tmode\torder_class\tsurvivors\tu_kind\talpha\tcoverage_lower")
    out["sample_rule"] = "every 101st row of each universe stream"
    out["real_system_protocol"] = {
        "source": hu.REAL_SOURCE,
        "word_length": hu.REAL_WORD_LEN,
        "train_windows": list(hu.REAL_TRAIN_WINDOWS),
        "protected_eval_windows": list(hu.REAL_EVAL_WINDOWS),
        "training": hu.REAL_TRAINING,
        "systems": [list(m) for m in hu.REAL_MACHINES],
        "registered_solved_bits": dict(
            ("|".join(str(x) for x in m), hu.real_solved_law(m)) for m in hu.REAL_MACHINES),
        "mu": [str(x) for x in hu.MU_REAL],
        "contracts": {c: list(v) for c, v in sorted(hu.VERIFIED.items())},
    }
    body = canonical_json(out)
    with open(os.path.join(HERE, "FROZEN_PREDICTIONS_V1.json"), "w") as handle:
        handle.write(json.dumps(json.loads(body), indent=2, sort_keys=True))
        handle.write("\n")
    sample_rows = []
    for name in sorted(streams):
        lines = streams[name].rstrip("\n").split("\n")
        sample_rows.append("# universe=%s rows=%d rule=every_101st_row" % (name, len(lines)))
        for i in range(0, len(lines), 101):
            sample_rows.append(name + "\t" + lines[i])
    with open(os.path.join(HERE, "FROZEN_PREDICTION_SAMPLE_V1.tsv"), "w") as handle:
        handle.write("\n".join(sample_rows) + "\n")
    sys.stdout.write(json.dumps(json.loads(body), indent=2, sort_keys=True))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
