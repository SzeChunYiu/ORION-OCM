"""RV-377-140 -- K4 revived at the CARRIER-CLASS level: the class-rate morphology instrument.

WHAT IS PREDICTED, AND WHY THE OBJECT MOVED. `RV-377-107/109/120/121` established that cost-minimising neutral search
does not converge on GMI's predicted property VECTORS (0 of 264, invariant under 10x budget, cross-seed agreement
0.0 % at 20 000 / 100 000 / 500 000). The property vector is therefore not a well-posed prediction target. What HAS
been reproducible across seeds and ecologies is the carrier CLASS of the machines the search recovers (T5: the
carrier is observable from behaviour on 12/12 non-trivial signatures), and the class-level recovery RATES have
followed one ordering in every record since `RV-377-058`: memory recovered nearly everywhere, program sometimes,
coefficient rarely. Per the #373 revival protocol the minimal justified change is to move the predicted object from
the property vector to the carrier-class recovery-rate ordering as a function of the ecology's coordinates.

THREE INSTRUMENTS, all exact, all charged, none new in kind:

  closed_forms(coeffs)   the theory's OWN admissibility model for one ecology, evaluated trajectory-free: the
                         registered retrieval rows (exemplar_table = S5, hamming_knn_k3 = S5h, soft_retrieval = S5a)
                         and search rows (program_search = S2a, compiled_search) replayed under all six registered
                         interventions (rule 36), the best constant over the full fx grid (rule 40), and the
                         hand-built coefficient witness scan of `RV-377-102` (gradient_net over H_GRID x LR_GRID,
                         all six interventions, margin in fx units). Memory admissibility here IS the closed form of
                         `RV-377-059/060/062` -- cap_S5 = 1 - |k|/12 and cap_S5h = (48 - |k|)/48 on the symmetric
                         family -- written out analytically for an arbitrary coefficient vector under the registered
                         standard protocol (`closed_form_check` verifies the identity on the symmetric family, and
                         shows that the IR zoo row hamming_knn_k3 is NOT that closed form).
  select_fresh(n)        the DETERMINISTIC choice of fresh ecologies: walk RV-377-102's discriminating enumeration in
                         canonical order, skip every ecology ever B1-searched, and take the lowest canonical indices
                         that jointly cover four declared conditions (witness-bearing, witness-free, memory-predicted-
                         present, memory-predicted-absent). Every cell examined is written to the receipt, so the
                         rule is auditable and could not have been steered by any search result.
  rescore_receipt(path)  the class reading of a B1 receipt under the FULL control set: for each carrier elite,
                         rule 36 (all six interventions on the raw elite), rule 40 (margin over the best constant in
                         fx units), rule 32 (atrophy under every intervention, `atrophy_ir.prune_all_interventions`),
                         rule 23 (the class label is the carrier of the ATROPHIED genotype), rule 41 (a survival at
                         zero deletions is flagged LOAD_BEARING_UNTESTED). The recovered CLASS SET of a run is the
                         set of atrophied carriers of elites that clear rules 36 and 40.

No change to the search, the grammar, the VM, the ecology DSL, theta or the interventions.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time

from . import atrophy_ir, b1, bases, ecology, morph, smooth, zoo
from .core import sha256_of
from .eco_axis import COEF_GRID, FX_UNIT, H_GRID, LR_GRID, best_constant

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = smooth.THETA
COL = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
INTERVENTIONS = list(ecology.INTERVENTIONS)
MEMORY_ROWS = ("exemplar_table", "hamming_knn_k3", "soft_retrieval")
SEARCH_ROWS = ("program_search", "compiled_search")
MEMORY_CLASSES = ("TABLE", "KVSTORE")
S2_GRAMMAR_COEFFS = (-1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0)
# thresholds of the law, fixed here BEFORE any fresh ecology is selected or run (no threshold changes after outcomes)
MEMORY_MARGIN_FX = 1.0        # rule 40 floor: one fx unit of mean absolute error over the best constant
THETA_BAND_FX = 1.0           # the instrument's resolution: a closed form within one fx unit of theta is AT the quantization floor and
                              # the law ABSTAINS there (RV-377-059 abstained on the one cell its inputs could not fix; rule 40 already
                              # treats one fx unit as the smallest separation the 8-bit instrument can assert)
WITNESS_MARGIN_FX = 1.5       # the E_sym5 | DENSE margin of RV-377-113, the smallest margin any rule-36 coefficient recovery has had
# every ecology ever B1-searched before this record -- fresh means none of these (the E_cr* entries are the OUTPUT of
# select_fresh and are excluded from its own skip set so the walk is reproducible after registration)
SEARCHED_COEFFS = {tuple(ecology.REGISTRY[n]["coeffs"]) for n in ecology.REGISTRY
                   if ecology.REGISTRY[n]["family"] == "smooth" and not n.startswith("E_cr")}


def _caps6(spec, g, basis):
    out = {}
    for iv in INTERVENTIONS:
        try:
            out[iv] = ecology.run_genotype(spec, g, basis, iv)["capability"]
        except Exception:
            return None
    return out


def _exact_in_s2_grammar(coeffs):
    return all(any(abs(c - gc) < 1e-12 for gc in S2_GRAMMAR_COEFFS) for c in coeffs)


def closed_forms(coeffs, name=None, witness_scan=True):
    """the theory's admissibility model for ONE ecology, with no search involved."""
    basis = bases.ALL[COL]
    spec = ecology.spec_smooth(coeffs, name)
    target = ecology.target_of(spec)
    bc, c_best = best_constant(target, smooth.UNSEEN)
    rows = {}
    for n in MEMORY_ROWS + SEARCH_ROWS:
        caps = _caps6(spec, zoo.ZOO[n](), basis)
        mn = min(caps.values()) if caps else None
        rows[n] = {"by_intervention": caps, "standard": caps["standard"] if caps else None, "min_over_six": mn,
                   "argmin": (min(caps, key=caps.get) if caps else None),
                   "admissible_all_six": (mn is not None and mn >= THETA),
                   "margin_fx_units": (round((mn - bc) / FX_UNIT, 3) if mn is not None else None)}
    # the MEMORY closed form is the theory's own (RV-377-059/060/062: cap_S5 = 1 - |k|/12, cap_S5h = (48 - |k|)/48 on the
    # symmetric family), evaluated analytically for the asymmetric vector under the registered standard protocol; the
    # replayed IR zoo rows are recorded beside it but are NOT the closed form (hamming_knn_k3 is a k = 3 nearest machine,
    # not the S5h min-distance average, and `closed_form_check` shows the two differ while the analytic form is exact)
    s5, s5h = closed_form_S5(coeffs), closed_form_S5h(coeffs)
    M = max(s5, s5h); mem_best = "S5h_analytic" if s5h >= s5 else "S5_analytic"
    prog = rows["program_search"]
    witness = None
    if witness_scan:
        best = None
        for h in H_GRID:
            for lr in LR_GRID:
                g = zoo.gradient_net(h, lr)
                # RV-377-102's stage structure: the five other interventions are charged only where standard clears theta
                try:
                    std = ecology.run_genotype(spec, g, basis, "standard")["capability"]
                except Exception:
                    continue
                caps = _caps6(spec, g, basis) if std >= THETA else {"standard": std}
                if not caps: continue
                mn = min(caps.values())
                if best is None or mn > best["min_over_six"]:
                    best = {"h": h, "lr": lr, "min_over_six": mn, "standard": caps["standard"],
                            "by_intervention": caps, "margin_fx_units": round((mn - bc) / FX_UNIT, 3)}
        witness = best
    W = witness["min_over_six"] if witness else None
    out = {"coeffs": list(coeffs), "name": spec["name"], "spec_id": ecology.spec_id(spec),
           "best_constant": bc, "best_constant_value": c_best, "discriminating": bc < THETA,
           "rows": rows,
           "memory": {"closed_form": M, "closed_form_row": mem_best, "analytic_S5": s5, "analytic_S5h": s5h,
                      "excess_over_theta_fx_units": round((M - THETA) / FX_UNIT, 3),
                      "margin_over_constant_fx_units": round((M - bc) / FX_UNIT, 3),
                      "predicted_present": (M - THETA) / FX_UNIT >= THETA_BAND_FX and (M - bc) / FX_UNIT >= MEMORY_MARGIN_FX,
                      "predicted_absent": M < THETA,
                      "abstain_at_quantization_floor": THETA <= M < THETA + THETA_BAND_FX * FX_UNIT,
                      "ir_zoo_rows_replayed_min_over_six": {n: rows[n]["min_over_six"] for n in MEMORY_ROWS}},
           "program": {"standard": prog["standard"], "min_over_six": prog["min_over_six"],
                       "exact_in_grammar": _exact_in_s2_grammar(coeffs),
                       "exact_by_replay": prog["standard"] == 1.0,
                       "closed_form_admissible": prog["admissible_all_six"] and prog["margin_fx_units"] >= MEMORY_MARGIN_FX},
           "coefficient": {"best_hand_built_row": witness,
                           "witness_bearing": (witness is not None and W >= THETA and witness["margin_fx_units"] >= WITNESS_MARGIN_FX),
                           "any_rule36_gradient_row": (witness is not None and W >= THETA)}}
    return out


# ------------------------------------------------------------------ the analytic closed forms, for the identity check
def closed_form_S5(coeffs):
    """exemplar table: serves 0 on every unseen key; cap = 1 - mean_x |t(x)| / (16 * 1.5). Equals 1 - |k|/12 on E_sym(k)."""
    t = smooth.make_target(coeffs)
    err = sum(abs(t[x]) for x in smooth.UNSEEN) / smooth.FX_ONE / len(smooth.UNSEEN)
    return round(max(0.0, 1 - err / 1.5), 4)


def closed_form_S5h(coeffs):
    """Hamming-1 neighbour average (registered SHR averaging over the four seen neighbours of every unseen key, the
    store complete after the standard 16-event protocol). Equals (48 - |k|)/48 on E_sym(k) for |k| <= 12."""
    t = smooth.make_target(coeffs)
    err = 0
    for x in smooth.UNSEEN:
        nb = [x ^ (1 << i) for i in range(4)]
        acc = sum(t[y] for y in nb)
        # the registered row averages by arithmetic shift: sum >> 2 for a count of 4
        served = acc >> 2
        err += abs(served - t[x])
    err = err / smooth.FX_ONE / len(smooth.UNSEEN)
    return round(max(0.0, 1 - err / 1.5), 4)


def closed_form_check():
    """the identity of the replayed rows with the RV-377-059/060/062 closed forms on the symmetric family."""
    basis = bases.ALL[COL]
    out = {}
    for v in (-8, -6, -4, -2, 2, 4, 6, 8):
        co = (v / 16,) * 4
        spec = ecology.spec_smooth(co)
        s5 = ecology.run_genotype(spec, zoo.exemplar_table(), basis, "standard")["capability"]
        s5h = ecology.run_genotype(spec, zoo.hamming_knn(3), basis, "standard")["capability"]
        out[f"E_sym({v})"] = {"S5_replay": s5, "S5_form": round(1 - abs(v) / 12, 4), "S5_analytic": closed_form_S5(co),
                              "S5h_replay": s5h, "S5h_form": round((48 - abs(v)) / 48, 4), "S5h_analytic": closed_form_S5h(co)}
    return out


# ------------------------------------------------------------------------------- deterministic fresh-ecology choice
COVERAGE = ("witness_bearing", "witness_free", "memory_present", "memory_absent")


def _conditions(cf):
    return {"witness_bearing": cf["coefficient"]["witness_bearing"],
            "witness_free": not cf["coefficient"]["any_rule36_gradient_row"],
            "memory_present": cf["memory"]["predicted_present"],
            "memory_absent": cf["memory"]["predicted_absent"]}


def select_fresh(n=4, tag="V43_CLASSRATE_SELECT", max_walk=200):
    """walk the discriminating enumeration in canonical order; add a cell iff it covers a not-yet-covered condition;
    once every condition is covered, fill with the next lowest indices; stop at n."""
    t0 = time.time()
    walk, chosen, covered = [], [], set()
    idx_disc = -1
    for idx, co in enumerate(itertools.product(COEF_GRID, repeat=4)):
        t = smooth.make_target(co)
        bc, _ = best_constant(t, smooth.UNSEEN)
        if bc >= THETA: continue
        idx_disc += 1
        if len(chosen) >= n or idx_disc >= max_walk: break
        if tuple(co) in SEARCHED_COEFFS:
            walk.append({"canonical_index": idx, "discriminating_index": idx_disc, "coeffs": list(co), "skipped": "already B1-searched (registered)"})
            continue
        cf = closed_forms(co, name=f"cand{idx}")
        cond = _conditions(cf)
        new = {c for c, v in cond.items() if v} - covered
        take = bool(new) or covered >= set(COVERAGE)
        walk.append({"canonical_index": idx, "discriminating_index": idx_disc, "coeffs": list(co), "conditions": cond,
                     "covers_new": sorted(new), "chosen": take, "closed_forms": cf})
        print(json.dumps({"idx": idx, "coeffs": list(co), "cond": cond, "chosen": take,
                          "M": cf["memory"]["closed_form"], "P": cf["program"]["min_over_six"],
                          "W": (cf["coefficient"]["best_hand_built_row"] or {}).get("min_over_six")}), flush=True)
        if take:
            covered |= new
            chosen.append({"name": f"E_cr{len(chosen) + 1}", "canonical_index": idx, "coeffs": list(co), "conditions": cond, "closed_forms": cf})
    receipt = {"schema": "ClassRateFreshEcologySelectionV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377],
               "revival_record": "RV-377-140", "run_tag": tag, "theta": THETA,
               "rule": "walk RV-377-102's discriminating enumeration (itertools.product over COEF_GRID, best constant < theta) in canonical order; skip every coefficient vector already B1-searched; add a cell iff it satisfies at least one coverage condition not yet satisfied by the chosen set, or every condition is already covered; stop at n",
               "coverage_conditions": list(COVERAGE), "thresholds": {"memory_margin_fx": MEMORY_MARGIN_FX, "theta_band_fx": THETA_BAND_FX, "witness_margin_fx": WITNESS_MARGIN_FX},
               "searched_coeffs_skipped": sorted(list(c) for c in SEARCHED_COEFFS),
               "n_requested": n, "chosen": chosen, "walk": walk, "n_examined": len(walk),
               "closed_form_identity_check": closed_form_check(), "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "a selection receipt; the chosen ecologies' closed forms are the theory's inputs, computed before any search on them"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, f"STAGE_CLASSRATE_SELECTION_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for c in chosen: print("CHOSEN", c["name"], c["coeffs"], c["conditions"], flush=True)
    return receipt


# --------------------------------------------------------------------------------- the class reading of a B1 receipt
def rescore_receipt(path, spec, bc, basis=None):
    basis = basis or bases.ALL[COL]
    r = json.load(open(path))
    rows = {}
    for carrier, v in r["best_by_carrier"].items():
        if not v.get("admissible"): continue
        g = morph.from_json(v["genotype"])
        caps = _caps6(spec, g, basis)
        if caps is None:
            rows[carrier] = {"error": "genotype did not evaluate under some intervention"}; continue
        mn = min(caps.values()); margin = round((mn - bc) / FX_UNIT, 3)
        row = {"raw_carrier": carrier, "capability_committed": v["capability"], "standard_replayed": caps["standard"],
               "replay_matches_receipt": abs(caps["standard"] - v["capability"]) < 1e-9,
               "by_intervention": caps, "min_over_six": mn, "binding": min(caps, key=caps.get),
               "rule36_admissible": mn >= THETA, "rule40_margin_fx_units": margin, "rule40_separates": margin >= MEMORY_MARGIN_FX,
               "n_nodes_raw": v["n_nodes"]}
        if row["rule36_admissible"]:
            small, info = atrophy_ir.prune_all_interventions(g, spec, basis)
            row.update({"atrophied_carrier": b1.carrier_of(small), "n_nodes_atrophied": info.get("n_nodes"),
                        "n_removed": info.get("n_removed"), "removed_kinds": info.get("removed_kinds"),
                        "atrophy_evaluations_charged": info.get("evaluations_charged"),
                        "atrophied_min_over_six": info.get("min_capability"),
                        "load_bearing_tested": (info.get("n_removed") or 0) > 0,
                        "label_survives_atrophy": b1.carrier_of(small) == carrier,
                        "atrophied_fingerprint": morph.fingerprint(small)})
            row["class_recovered"] = row["atrophied_carrier"] if (row["rule40_separates"] and row["atrophied_carrier"] != "NONE") else None
        else:
            row["class_recovered"] = None
        rows[carrier] = row
        print(json.dumps({"receipt": os.path.basename(path), "carrier": carrier, "std": caps["standard"], "min6": mn,
                          "bind": row["binding"], "r36": row["rule36_admissible"], "margin": margin,
                          "atrophied": row.get("atrophied_carrier"), "removed": row.get("n_removed"), "class": row["class_recovered"]}), flush=True)
    classes = sorted({v["class_recovered"] for v in rows.values() if isinstance(v, dict) and v.get("class_recovered")})
    return {"receipt": os.path.basename(path), "ecology": r.get("ecology"), "seed": r.get("seed"), "n_evaluations": r.get("n_evaluations"),
            "receipt_sha256": r.get("receipt_sha256"), "best_constant": bc, "rows": rows, "classes_recovered": classes,
            "memory_class_recovered": any(c in MEMORY_CLASSES for c in classes),
            "program_class_recovered": "PROGRAM" in classes, "coefficient_class_recovered": "DENSE" in classes}


def _spec_and_bc(eco_name, coeffs=None):
    spec = ecology.REGISTRY[eco_name] if eco_name in ecology.REGISTRY else ecology.spec_smooth(coeffs, eco_name)
    target = ecology.target_of(spec)
    bc, _ = best_constant(target, smooth.UNSEEN)
    return spec, bc


def rates(readings):
    """per-ecology class recovery rates over seeds."""
    by = {}
    for rd in readings:
        e = by.setdefault(rd["ecology"], {"seeds": [], "memory": 0, "program": 0, "coefficient": 0, "classes_by_seed": {}})
        e["seeds"].append(rd["seed"]); e["classes_by_seed"][f"S{rd['seed']}"] = rd["classes_recovered"]
        e["memory"] += rd["memory_class_recovered"]; e["program"] += rd["program_class_recovered"]; e["coefficient"] += rd["coefficient_class_recovered"]
    for e in by.values():
        n = len(e["seeds"]); e["n_seeds"] = n
        for k in ("memory", "program", "coefficient"): e[f"{k}_rate"] = f"{e[k]}/{n}"
    return by


def diagnose(tag="V43_CLASSRATE_DIAG"):
    """the class reading of every committed B1 receipt on a discriminating ecology, under the full control set."""
    t0 = time.time()
    files = []
    for f in sorted(os.listdir(RES)):
        if f.startswith("STAGE_B1_V33_B1_IR_RECOVERY_E_") or f.startswith("STAGE_B1_V42_B1_WITNESS_E_") or f.startswith("STAGE_B1_ABL_FULL_E_"):
            files.append(f)
    readings, excluded = [], {}
    for f in files:
        r = json.load(open(os.path.join(RES, f)))
        eco = r["ecology"]
        spec, bc = _spec_and_bc(eco)
        if bc >= THETA:
            excluded[f] = f"NON_DISCRIMINATING under rule 40 (best constant {bc} >= theta)"; continue
        rd = rescore_receipt(os.path.join(RES, f), spec, bc)
        rd["harness"] = "ABL_FULL_S0_baseline(RV-377-110)" if "ABL_FULL" in f else "V33/V42"
        readings.append(rd)
    primary = [rd for rd in readings if rd["harness"] != "ABL_FULL_S0_baseline(RV-377-110)"]
    receipt = {"schema": "ClassRateDiagnosisV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377], "revival_record": "RV-377-140",
               "run_tag": tag, "theta": THETA, "interventions": INTERVENTIONS, "thresholds": {"memory_margin_fx": MEMORY_MARGIN_FX},
               "reading": "class = carrier of the genotype atrophied under EVERY registered intervention (rules 23 + 32); an elite counts only if its RAW form clears theta under all six interventions (rule 36) and its minimum over six beats the best constant by >= 1 fx unit (rule 40); a survival at zero deletions is recorded LOAD_BEARING_UNTESTED (rule 41) and still labelled by its (unchanged) carrier",
               "receipts_examined": files, "excluded": excluded, "readings": readings,
               "rates_primary_three_seed_runs": rates(primary), "rates_including_rv110_baselines": rates(readings),
               "closed_forms_of_searched_ecologies": {n: closed_forms(ecology.REGISTRY[n]["coeffs"], n) for n in ecology.REGISTRY if ecology.REGISTRY[n]["family"] == "smooth" and n != "E_sym3"},
               "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "a re-reading of committed receipts under controls written after most of them; the class label is the atrophied carrier, which is a claim about what the machine reads, not about which machine it is"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_CLASSRATE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("RATES (primary):", json.dumps(receipt["rates_primary_three_seed_runs"], indent=1))
    return receipt


def score_fresh(tag="V43_CLASSRATE", host="billy", selection_tag="V43_CLASSRATE_SELECT", seeds=(0, 1, 2)):
    """the class reading of the fresh-ecology receipts, keyed by host."""
    t0 = time.time()
    sel = json.load(open(os.path.join(RES, f"STAGE_CLASSRATE_SELECTION_{selection_tag}.json")))
    readings, missing = [], []
    for c in sel["chosen"]:
        spec, bc = _spec_and_bc(c["name"], c["coeffs"])
        for s in seeds:
            f = f"STAGE_B1_{tag}_{host}_{c['name']}_S{s}.json"
            p = os.path.join(RES, f)
            if not os.path.exists(p): missing.append(f); continue
            readings.append(rescore_receipt(p, spec, bc))
    receipt = {"schema": "ClassRateFreshScoringV1", "status": "EXECUTED_EXACT_AT_SCOPE" if not missing else "INCOMPLETE__RECEIPTS_MISSING",
               "issue": [377], "revival_record": "RV-377-140", "run_tag": tag, "host": host, "theta": THETA,
               "selection_receipt_sha256": sel["receipt_sha256"], "missing": missing, "readings": readings, "rates": rates(readings),
               "seconds": round(time.time() - t0, 1)}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_CLASSRATE_FRESH_{tag}_{host}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("RATES (fresh):", json.dumps(receipt["rates"], indent=1)); print("missing:", missing)
    return receipt


def score_dir(directory, pattern, eco_name, out_tag, revival="RV-377-118"):
    """the same class reading applied to receipts in another checkout's results directory -- used for the lane-B
    nine-seed replication of G15 step (ii) (STAGE_B1_V41_G15_REPLICATE_billy_E_sym5_S{1..9}), whose freeze
    (RV-377-118, predictions B1-B3) asked for the DENSE carrier under all six interventions against the best constant
    in fx units; RV-377-141 adds the rule-32 atrophy the original witness never had."""
    import glob
    t0 = time.time()
    spec, bc = _spec_and_bc(eco_name)
    files = sorted(glob.glob(os.path.join(directory, pattern)))
    readings = [rescore_receipt(f, spec, bc) for f in files]
    per_seed = {}
    for rd in readings:
        d = rd["rows"].get("DENSE")
        per_seed[f"S{rd['seed']}"] = {
            "classes_recovered": rd["classes_recovered"],
            "DENSE_raw_admissible_standard": d is not None,
            "DENSE_min_over_six": (d or {}).get("min_over_six"), "DENSE_binding": (d or {}).get("binding"),
            "DENSE_rule36": (d or {}).get("rule36_admissible"), "DENSE_rule40_margin_fx": (d or {}).get("rule40_margin_fx_units"),
            "DENSE_atrophied_carrier": (d or {}).get("atrophied_carrier"), "DENSE_removed_kinds": (d or {}).get("removed_kinds"),
            "raw_vs_atrophied": {c: (v.get("atrophied_carrier") if isinstance(v, dict) else None) for c, v in rd["rows"].items()}}
    receipt = {"schema": "ClassRateDirectoryScoringV1", "status": "EXECUTED_EXACT_AT_SCOPE" if files else "NO_RECEIPTS_FOUND",
               "issue": [377], "revival_record": revival, "run_tag": out_tag, "ecology": eco_name, "best_constant": bc, "theta": THETA,
               "directory": directory, "pattern": pattern, "receipts": [os.path.basename(f) for f in files],
               "readings": readings, "per_seed": per_seed, "rates": rates(readings),
               "n_seeds_DENSE_raw_admissible_standard": sum(1 for v in per_seed.values() if v["DENSE_raw_admissible_standard"]),
               "n_seeds_DENSE_rule36": sum(1 for v in per_seed.values() if v["DENSE_rule36"]),
               "n_seeds_DENSE_rule36_and_rule40": sum(1 for v in per_seed.values() if v["DENSE_rule36"] and (v["DENSE_rule40_margin_fx"] or -1) >= MEMORY_MARGIN_FX),
               "n_seeds_DENSE_survives_atrophy": sum(1 for v in per_seed.values() if v["DENSE_atrophied_carrier"] == "DENSE"),
               "binding_interventions_on_DENSE": sorted({v["DENSE_binding"] for v in per_seed.values() if v["DENSE_binding"]}),
               "seconds": round(time.time() - t0, 1)}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_CLASSRATE_{out_tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("per seed:", json.dumps(per_seed, indent=1)); print("rates:", json.dumps(receipt["rates"]))
    return receipt


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "diagnose"
    if cmd == "select": select_fresh(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif cmd == "diagnose": diagnose()
    elif cmd == "score": score_fresh(host=sys.argv[2] if len(sys.argv) > 2 else "billy")
    elif cmd == "check": print(json.dumps(closed_form_check(), indent=1))
    elif cmd == "score_dir": score_dir(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else: raise SystemExit(f"unknown command {cmd}")
