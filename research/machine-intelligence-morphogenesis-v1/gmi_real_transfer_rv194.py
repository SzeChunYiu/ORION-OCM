"""RV-377-194: real-transfer crossover cells re-tested off-band (B: mass-weighted variance term + registered band +
power-sized off-band grid; F: within-train retention probe + admissibility band) with the cost-charged CV parent.

Frozen by GMI_REAL_TRANSFER_RV_377_194_FREEZE.md before the run. Machines, prices, thresholds and helpers are imported
unchanged from gmi_real_transfer_v3.py (RV-377-190 freeze); that file is not edited. Receipts record the freeze SHA
passed on the command line; seeds derive from it with tag GMI-RT-V3R3.

Per replicate: (1) protected split, (2) development (deployed models; fixes prices), (3) law descriptors from
training-split quantities only (0 extra fits), (4) parents (3-fold CV, counted fits; F also the free holdout parent),
(5) commit + hash of every prediction, (6) protected test touched only after the hash.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import platform
import sys
import time
import warnings

import numpy as np
import sklearn
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_california_housing, load_digits
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gmi_real_transfer_v3 import (M_MODES, N_TRAIN_B, OLD_POS, P_B, Q, REPLICATES, Z_OFFSETS, cheapest,  # noqa: E402
                                  continual_strategies, cost_F, margin_k5, mlp, new_task_labels, sha_of)

warnings.filterwarnings("ignore", category=ConvergenceWarning)

SCHEMA = "GMIRealTransferRV194"
REVIVAL_ID = "RV-377-194"
SEED_TAG = "GMI-RT-V3R3"
Z_BAND = 2.0            # frozen: band half-width in test standard errors
OFF_BAND_Q = 0.75       # frozen: fraction of band-outside replicates required (8 -> 6, the K5 V1 rule)
PROBE_FRAC = 0.20       # F: within-train probe fraction
N_TEST_B = 8000         # B: registered test size (power calculation, freeze §2.1 B3)
GRIDS = {
    "F_CONTINUAL_REAL": {"parameter": "label_agreement", "values": [0.6, 0.8, 0.9, 0.95, 1.0], "band_cells": [0.95]},
    "B_SPECIALIZATION_REAL": {"parameter": "injected_tau", "values": [0.0, 0.1, 0.3, 0.5, 0.65, 0.8, 1.0],
                              "band_cells": [0.0, 0.1, 0.3]},
}
F_STRATS = ("REWRITE", "REPLAY", "EXPANSION")
B_STRATS = ("SHARED", "SPECIALIZED")


def seed_for(freeze_sha: str, lane: str, value: float, rep: int) -> int:
    h = hashlib.sha256(f"{SEED_TAG}|{freeze_sha}|{lane}|{value}|{rep}".encode()).hexdigest()
    return int(h[:16], 16) % (2 ** 32)


def adm_F(acc):
    return [s for s, v in acc.items() if v["old"] >= Q["F_CONTINUAL_min_old_accuracy"] and v["new"] >= Q["F_CONTINUAL_min_new_accuracy"]]


# ================================================================ lane F: within-train probe + retention descriptor
def lane_F(seed, agreement, data):
    X, cls = data["digits"]
    Xtr, Xte, ctr, cte = train_test_split(X, cls, test_size=0.25, random_state=seed, stratify=cls)
    btr = Xtr.mean(1); bte = Xte.mean(1)
    sc = StandardScaler().fit(Xtr); Xtr = sc.transform(Xtr); Xte = sc.transform(Xte)
    thr = float(np.median(btr[ctr == 5])) if (ctr == 5).any() else 0.0
    y_old_tr = np.isin(ctr, list(OLD_POS)).astype(int); y_old_te = np.isin(cte, list(OLD_POS)).astype(int)
    y_new_tr = new_task_labels(ctr, agreement, thr, btr); y_new_te = new_task_labels(cte, agreement, thr, bte)
    # ---- probe split (F1): 20 % of the training split held out from development, stratified by digit class
    idx_dev, idx_P = train_test_split(np.arange(len(Xtr)), test_size=PROBE_FRAC, random_state=seed, stratify=ctr)
    perm = np.random.RandomState(seed).permutation(idx_dev); h = len(perm) // 2
    io, i_n = perm[:h], perm[h:]
    Xo, yo = Xtr[io], y_old_tr[io]; Xn, yn = Xtr[i_n], y_new_tr[i_n]
    XP, yP_old, yP_new = Xtr[idx_P], y_old_tr[idx_P], y_new_tr[idx_P]
    a_hat = float(np.mean(y_old_tr == y_new_tr))
    # ---- development (deployed models; 4 fits; fixes the prices)
    t0 = time.perf_counter()
    old = mlp(seed, warm=True).fit(Xo, yo)
    strategies = continual_strategies(Xo, yo, Xn, yn, seed, ref_old=old)
    cost = {s: cost_F(v[2], v[3], v[4]) for s, v in strategies.items()}
    wall_dev = time.perf_counter() - t0
    # ---- law descriptors (0 extra fits): e_hat on rows the old model never saw; rho_s on the disputed probe rows
    t0 = time.perf_counter()
    X_unseen = np.vstack([Xn, XP]); y_unseen_old = np.concatenate([y_old_tr[i_n], yP_old])
    e_hat = float(np.mean(old.predict(X_unseen) != y_unseen_old))
    disputed = yP_old != yP_new
    n_disp = int(disputed.sum())
    rho = {}
    for s in ("REPLAY", "REWRITE"):
        rho[s] = float(np.mean(strategies[s][0].predict(XP[disputed]) != yP_old[disputed])) if n_disp else 0.0
    d = 1.0 - a_hat
    pred_acc = {
        "REWRITE": {"old": 1.0 - e_hat - rho["REWRITE"] * d, "new": 1.0 - e_hat - (1.0 - rho["REWRITE"]) * d},
        "REPLAY": {"old": 1.0 - e_hat - rho["REPLAY"] * d, "new": 1.0 - e_hat - (1.0 - rho["REPLAY"]) * d},
        "EXPANSION": {"old": 1.0 - e_hat, "new": 1.0 - e_hat},
    }
    pred_adm = adm_F(pred_acc)
    gmi_pred = cheapest(pred_adm, cost)
    wall_law = time.perf_counter() - t0
    # ---- free parent: holdout selection on P (0 extra fits)
    ho_acc = {s: {"old": float(np.mean(v[0].predict(XP) == yP_old)), "new": float(np.mean(v[1].predict(XP) == yP_new))}
              for s, v in strategies.items()}
    ho_adm = adm_F(ho_acc); ho_pred = cheapest(ho_adm, cost)
    # ---- K5 parent: 3-fold CV of every strategy on the development halves (12 extra fits)
    t0 = time.perf_counter()
    kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    cv_old = {s: [] for s in strategies}; cv_new = {s: [] for s in strategies}
    cv_fits = 0
    for (tro, teo), (trn, ten) in zip(kf.split(Xo, yo), kf.split(Xn, yn)):
        st = continual_strategies(Xo[tro], yo[tro], Xn[trn], yn[trn], seed); cv_fits += 4
        for s, (mo, mn, *_rest) in st.items():
            cv_old[s].append(float(np.mean(mo.predict(Xo[teo]) == yo[teo])))
            cv_new[s].append(float(np.mean(mn.predict(Xn[ten]) == yn[ten])))
    cv_acc = {s: {"old": float(np.mean(cv_old[s])), "new": float(np.mean(cv_new[s]))} for s in strategies}
    cv_adm = adm_F(cv_acc); cv_pred = cheapest(cv_adm, cost)
    wall_cv = time.perf_counter() - t0
    prediction = {"gmi_predicted_winner": gmi_pred, "gmi_predicted_admissible": pred_adm, "gmi_predicted_acc": pred_acc,
                  "descriptors": {"a_hat": a_hat, "e_hat": e_hat, "rho_REPLAY": rho["REPLAY"], "rho_REWRITE": rho["REWRITE"],
                                  "n_probe": int(len(idx_P)), "n_disputed_probe": n_disp, "n_unseen_for_e_hat": int(len(X_unseen))},
                  "cv_predicted_winner": cv_pred, "cv_predicted_admissible": cv_adm, "cv_acc": cv_acc,
                  "holdout_predicted_winner": ho_pred, "holdout_predicted_admissible": ho_adm, "holdout_acc": ho_acc,
                  "cost": cost, "selection_cost": {"law_extra_fits": 0, "holdout_extra_fits": 0, "cv_extra_fits": cv_fits,
                                                   "wall_dev_s": wall_dev, "wall_law_s": wall_law, "wall_cv_s": wall_cv}}
    committed = copy.deepcopy(prediction); phash = sha_of(committed)
    # ---- protected test (touched only now)
    obs_acc = {s: {"old": float(np.mean(v[0].predict(Xte) == y_old_te)), "new": float(np.mean(v[1].predict(Xte) == y_new_te))}
               for s, v in strategies.items()}
    admissible = adm_F(obs_acc); observed = cheapest(admissible, cost)
    n_te = int(len(Xte))
    sd_bar = {"old": math.sqrt(Q["F_CONTINUAL_min_old_accuracy"] * (1 - Q["F_CONTINUAL_min_old_accuracy"]) / n_te),
              "new": math.sqrt(Q["F_CONTINUAL_min_new_accuracy"] * (1 - Q["F_CONTINUAL_min_new_accuracy"]) / n_te)}
    return committed, phash, {"observed_winner": observed, "admissible": admissible, "observed_acc": obs_acc,
                              "test_agreement": float(np.mean(y_old_te == y_new_te)), "sd_bar": sd_bar,
                              "n_train_old": int(len(Xo)), "n_train_new": int(len(Xn)), "n_test": n_te,
                              "state": {s: v[2] for s, v in strategies.items()}, "work": {s: v[4] for s, v in strategies.items()}}


def band_inside_F(pred, obs):
    """F2: disagreement unresolved by the test iff every strategy whose predicted admissibility differs from the observed one
    has each criterion at issue within Z_BAND test sd of its bar."""
    if pred["gmi_predicted_winner"] == obs["observed_winner"]:
        return False, []
    bars = {"old": Q["F_CONTINUAL_min_old_accuracy"], "new": Q["F_CONTINUAL_min_new_accuracy"]}
    pa, oa = set(pred["gmi_predicted_admissible"]), set(obs["admissible"])
    diffs = [s for s in F_STRATS if (s in pa) != (s in oa)]
    if not diffs:
        return False, []
    detail = []
    for s in diffs:
        if s in oa:   # predicted inadmissible, observed admissible: criteria the law predicted failing
            at_issue = [c for c in ("old", "new") if pred["gmi_predicted_acc"][s][c] < bars[c]]
        else:         # observed inadmissible: criteria failing on the test
            at_issue = [c for c in ("old", "new") if obs["observed_acc"][s][c] < bars[c]]
        zs = [abs(obs["observed_acc"][s][c] - bars[c]) / obs["sd_bar"][c] for c in at_issue]
        detail.append({"strategy": s, "criteria": at_issue, "z": zs})
    inside = all(z <= Z_BAND for dd in detail for z in dd["z"]) and any(dd["z"] for dd in detail)
    return bool(inside), detail


# ================================================================ lane B: mass-weighted term, band, off-band grid
def lane_B(seed, tau, data):
    X, y = data["housing"]
    rs = np.random.RandomState(seed)
    idx = rs.permutation(len(X))[: N_TRAIN_B + N_TEST_B]
    itr, ite = idx[:N_TRAIN_B], idx[N_TRAIN_B:]
    Xraw_tr, Xraw_te = X[itr], X[ite]
    lo, hi = np.percentile(Xraw_tr, [1, 99], axis=0)                       # RV-377-193 world stage, unchanged
    Xraw_tr = np.clip(Xraw_tr, lo, hi); Xraw_te = np.clip(Xraw_te, lo, hi)
    sx = StandardScaler().fit(Xraw_tr); Xtr = sx.transform(Xraw_tr); Xte = sx.transform(Xraw_te)
    mu, sd = float(np.mean(y[itr])), float(np.std(y[itr]))
    ytr = (y[itr] - mu) / sd; yte = (y[ite] - mu) / sd
    km = KMeans(n_clusters=M_MODES, n_init=10, random_state=seed).fit(Xtr)
    mtr = km.labels_; mte = km.predict(Xte)
    ytr = ytr + tau * Z_OFFSETS[mtr]; yte = yte + tau * Z_OFFSETS[mte]
    p = Xtr.shape[1] + 1; n = len(Xtr)
    n_j = np.array([(mtr == j).sum() for j in range(M_MODES)])
    # ---- development = the deployed shared and per-mode fits (they are also the descriptor fits; 0 extra)
    t0 = time.perf_counter()
    shared = Ridge(alpha=1.0).fit(Xtr, ytr)
    r = ytr - shared.predict(Xtr)
    experts = {}
    sse_shared = float((r ** 2).sum()); sse_exp = 0.0
    for j in range(M_MODES):
        sel = mtr == j
        if sel.sum() >= 2:
            experts[j] = Ridge(alpha=1.0).fit(Xtr[sel], ytr[sel]); sse_exp += float(((ytr[sel] - experts[j].predict(Xtr[sel])) ** 2).sum())
        else:
            experts[j] = shared; sse_exp += float((r[sel] ** 2).sum())
    wall_dev = time.perf_counter() - t0
    # ---- law descriptors (RV-377-192 Chow form) and the mass-weighted law (B1)
    t0 = time.perf_counter()
    sigma2_hat = sse_exp / max(1, n - M_MODES * p)
    tau2_hat = max(0.0, (sse_shared - sse_exp) / n - sigma2_hat * p * (M_MODES - 1) / n)
    price_shared = P_B["state_per_model"] * 1 + P_B["work_per_sample"] * n
    price_spec = P_B["state_per_model"] * M_MODES + P_B["work_per_sample"] * (n + N_TEST_B * P_B["route_work_per_query"])
    exp_shared = sigma2_hat + tau2_hat + sigma2_hat * p / n + price_shared
    exp_spec = sigma2_hat + sigma2_hat * p * M_MODES / n + price_spec            # B1: sigma^2 p m / n (mass-weighted)
    pred_adm = [s for s, v in (("SHARED", exp_shared - price_shared), ("SPECIALIZED", exp_spec - price_spec))
                if v <= Q["B_SPECIALIZATION_max_test_mse"]]
    exp = {"SHARED": exp_shared, "SPECIALIZED": exp_spec}
    gmi_pred = cheapest(pred_adm, exp)
    wall_law = time.perf_counter() - t0
    # ---- K5 parent: 3-fold CV of both routes (counted fits)
    t0 = time.perf_counter()
    kf = KFold(n_splits=3, shuffle=True, random_state=seed)
    cv = {"SHARED": [], "SPECIALIZED": []}; cv_fits = 0
    for tr, te in kf.split(Xtr):
        sh = Ridge(alpha=1.0).fit(Xtr[tr], ytr[tr]); cv_fits += 1
        cv["SHARED"].append(float(np.mean((sh.predict(Xtr[te]) - ytr[te]) ** 2)))
        pr = np.zeros(len(te))
        for j in range(M_MODES):
            sel = mtr[tr] == j; tsel = mtr[te] == j
            if tsel.any():
                if sel.sum() >= 2:
                    mdl = Ridge(alpha=1.0).fit(Xtr[tr][sel], ytr[tr][sel]); cv_fits += 1
                else:
                    mdl = sh
                pr[tsel] = mdl.predict(Xtr[te][tsel])
        cv["SPECIALIZED"].append(float(np.mean((pr - ytr[te]) ** 2)))
    cv_mse = {s: float(np.mean(v)) for s, v in cv.items()}
    cv_obj = {"SHARED": cv_mse["SHARED"] + price_shared, "SPECIALIZED": cv_mse["SPECIALIZED"] + price_spec}
    cv_adm = [s for s in cv_mse if cv_mse[s] <= Q["B_SPECIALIZATION_max_test_mse"]]
    cv_pred = cheapest(cv_adm, cv_obj)
    wall_cv = time.perf_counter() - t0
    prediction = {"gmi_predicted_winner": gmi_pred, "gmi_predicted_admissible": pred_adm, "gmi_expected_objective": exp,
                  "gmi_predicted_gap_shared_minus_spec": exp_shared - exp_spec,
                  "descriptors": {"tau2_hat": tau2_hat, "tau_hat": float(np.sqrt(tau2_hat)), "sigma2_hat": sigma2_hat,
                                  "n_per_mode": n_j.tolist(), "p": p, "variance_term_spec": sigma2_hat * p * M_MODES / n,
                                  "variance_term_equal_weight_old_form": sigma2_hat * p * float(np.mean(1.0 / np.maximum(n_j, 1)))},
                  "cv_predicted_winner": cv_pred, "cv_predicted_admissible": cv_adm, "cv_mse": cv_mse,
                  "price": {"SHARED": price_shared, "SPECIALIZED": price_spec},
                  "selection_cost": {"law_extra_fits": 0, "cv_extra_fits": cv_fits, "wall_dev_s": wall_dev, "wall_law_s": wall_law, "wall_cv_s": wall_cv}}
    committed = copy.deepcopy(prediction); phash = sha_of(committed)
    # ---- protected test (touched only now)
    pred_te = np.zeros(len(Xte))
    for j in range(M_MODES):
        sel = mte == j
        if sel.any():
            pred_te[sel] = experts[j].predict(Xte[sel])
    e2 = {"SHARED": (shared.predict(Xte) - yte) ** 2, "SPECIALIZED": (pred_te - yte) ** 2}
    n_te = len(Xte)
    mse = {s: float(np.mean(v)) for s, v in e2.items()}
    se_mse = {s: float(np.std(v, ddof=1) / math.sqrt(n_te)) for s, v in e2.items()}
    d = e2["SHARED"] - e2["SPECIALIZED"]
    se_delta = float(np.std(d, ddof=1) / math.sqrt(n_te))
    obj = {"SHARED": mse["SHARED"] + price_shared, "SPECIALIZED": mse["SPECIALIZED"] + price_spec}
    admissible = [s for s in mse if mse[s] <= Q["B_SPECIALIZATION_max_test_mse"]]
    observed = cheapest(admissible, obj)
    return committed, phash, {"observed_winner": observed, "admissible": admissible, "test_mse": mse, "objective": obj,
                              "observed_gap_shared_minus_spec": obj["SHARED"] - obj["SPECIALIZED"],
                              "se_delta": se_delta, "se_mse": se_mse, "n_train": int(n), "n_test": int(n_te), "router_errors": 0}


def band_inside_B(pred, obs):
    if pred["gmi_predicted_winner"] == obs["observed_winner"]:
        return False, []
    pa, oa = set(pred["gmi_predicted_admissible"]), set(obs["admissible"])
    diffs = [s for s in B_STRATS if (s in pa) != (s in oa)]
    if not diffs:   # both admissible on both sides: disagreement is the objective ordering
        z = abs(obs["observed_gap_shared_minus_spec"]) / obs["se_delta"] if obs["se_delta"] > 0 else float("inf")
        return bool(z <= Z_BAND), [{"quantity": "delta", "z": z}]
    detail = [{"strategy": s, "quantity": "mse_vs_bar", "z": abs(obs["test_mse"][s] - Q["B_SPECIALIZATION_max_test_mse"]) / obs["se_mse"][s]} for s in diffs]
    return bool(all(dd["z"] <= Z_BAND for dd in detail)), detail


LANES = {"F_CONTINUAL_REAL": (lane_F, band_inside_F), "B_SPECIALIZATION_REAL": (lane_B, band_inside_B)}


# ================================================================ scoring (freeze §3)
def score_cell(receipts, band_by_construction):
    n = len(receipts)
    inside = [r for r in receipts if r["band_inside"]]; out = [r for r in receipts if not r["band_inside"]]
    n_in, n_out = len(inside), len(out)

    def tallies(rs):
        agree = sum(1 for r in rs if r["agreement"])
        inadm = sum(1 for r in rs if r["prediction"]["gmi_predicted_winner"] != "NONE"
                    and r["prediction"]["gmi_predicted_winner"] not in r["observation"]["admissible"])
        oppose = sum(1 for r in rs if (not r["agreement"]) and r["prediction"]["gmi_predicted_winner"] in r["observation"]["admissible"])
        mm = float(np.mean([r["margin"] for r in rs])) if rs else 0.0
        return agree, oppose, inadm, mm

    agree_all, oppose_all, inadm_all, mm_all = tallies(receipts)
    agree_out, oppose_out, inadm_out, mm_out = tallies(out)
    if band_by_construction:
        verdict = "INSIDE_BAND_BY_CONSTRUCTION"
    elif n_in >= 4:
        verdict = "INSIDE_BAND_MEASURED"
    else:
        q = math.ceil(OFF_BAND_Q * n_out)
        if inadm_out >= q:
            verdict = "THEORY_RED"
        elif inadm_out >= 1:
            verdict = "INCONCLUSIVE"
        elif agree_out >= q and mm_out > 0:
            verdict = "GREEN"
        elif oppose_out >= q and mm_out < 0:
            verdict = "THEORY_RED"
        else:
            verdict = "INCONCLUSIVE"
    pred_counts, obs_counts = {}, {}
    for r in receipts:
        pred_counts[r["prediction"]["gmi_predicted_winner"]] = pred_counts.get(r["prediction"]["gmi_predicted_winner"], 0) + 1
        obs_counts[r["observation"]["observed_winner"]] = obs_counts.get(r["observation"]["observed_winner"], 0) + 1
    cv_same = sum(1 for r in receipts if r["prediction"]["cv_predicted_winner"] == r["prediction"]["gmi_predicted_winner"])
    cv_right = sum(1 for r in receipts if r["prediction"]["cv_predicted_winner"] == r["observation"]["observed_winner"])
    gmi_right = sum(1 for r in receipts if r["prediction"]["gmi_predicted_winner"] == r["observation"]["observed_winner"])
    out_d = {"n": n, "cell_class": "BAND" if band_by_construction else "OFF_BAND", "n_band_inside": n_in, "n_band_outside": n_out,
             "agree_all": agree_all, "oppose_all": oppose_all, "predicted_inadmissible_all": inadm_all, "mean_margin_all": mm_all,
             "agree_out": agree_out, "oppose_out": oppose_out, "predicted_inadmissible_out": inadm_out, "mean_margin_out": mm_out,
             "verdict": verdict, "predicted_counts": pred_counts, "observed_counts": obs_counts,
             "cv_same_as_gmi": cv_same, "cv_correct": cv_right, "gmi_correct": gmi_right,
             "cv_extra_fits_mean": float(np.mean([r["prediction"]["selection_cost"]["cv_extra_fits"] for r in receipts])),
             "law_extra_fits": 0,
             "wall_law_s_mean": float(np.mean([r["prediction"]["selection_cost"]["wall_law_s"] for r in receipts])),
             "wall_cv_s_mean": float(np.mean([r["prediction"]["selection_cost"]["wall_cv_s"] for r in receipts]))}
    lane = receipts[0]["lane"]
    if lane == "B_SPECIALIZATION_REAL":
        resid = [r["prediction"]["gmi_predicted_gap_shared_minus_spec"] - r["observation"]["observed_gap_shared_minus_spec"] for r in receipts]
        out_d["calibration"] = {"gap_pred_minus_obs": resid, "mean_abs": float(np.mean(np.abs(resid))),
                                "n_within_0_05": int(sum(1 for x in resid if abs(x) <= 0.05)),
                                "se_delta_mean": float(np.mean([r["observation"]["se_delta"] for r in receipts])),
                                "shared_inadmissible_observed": sum(1 for r in receipts if "SHARED" not in r["observation"]["admissible"]),
                                "shared_inadmissible_predicted": sum(1 for r in receipts if "SHARED" not in r["prediction"]["gmi_predicted_admissible"])}
    else:
        resid = [100.0 * (r["prediction"]["gmi_predicted_acc"]["REPLAY"]["old"] - r["observation"]["observed_acc"]["REPLAY"]["old"]) for r in receipts]
        ho_same = sum(1 for r in receipts if r["prediction"]["holdout_predicted_winner"] == r["prediction"]["gmi_predicted_winner"])
        ho_right = sum(1 for r in receipts if r["prediction"]["holdout_predicted_winner"] == r["observation"]["observed_winner"])
        out_d["holdout_same_as_gmi"] = ho_same; out_d["holdout_correct"] = ho_right
        out_d["calibration"] = {"replay_old_pred_minus_obs_pp": resid, "mean_pp": float(np.mean(resid)), "mean_abs_pp": float(np.mean(np.abs(resid))),
                                "rho_REPLAY_mean": float(np.mean([r["prediction"]["descriptors"]["rho_REPLAY"] for r in receipts])),
                                "rho_REWRITE_mean": float(np.mean([r["prediction"]["descriptors"]["rho_REWRITE"] for r in receipts])),
                                "e_hat_mean": float(np.mean([r["prediction"]["descriptors"]["e_hat"] for r in receipts])),
                                "replay_observed_admissible": sum(1 for r in receipts if "REPLAY" in r["observation"]["admissible"])}
    return out_d


def run_task(args):
    lane, value, rep, freeze_sha, data = args
    seed = seed_for(freeze_sha, lane, value, rep)
    t0 = time.time()
    fn, band_fn = LANES[lane]
    committed, phash, observation = fn(seed, value, data)
    assert sha_of(committed) == phash, "prediction mutated after commit"
    pred = committed["gmi_predicted_winner"]
    agreement = (pred == observation["observed_winner"]) and (pred == "NONE" or pred in observation["admissible"])
    if lane == "F_CONTINUAL_REAL":
        margin = margin_k5(pred, observation["admissible"], committed["cost"])
    else:
        margin = margin_k5(pred, observation["admissible"], observation["objective"])
    inside, detail = band_fn(committed, observation)
    return {"schema": SCHEMA, "revival_id": REVIVAL_ID, "lane": lane, "parameter": GRIDS[lane]["parameter"], "value": value,
            "cell_class": "BAND" if value in GRIDS[lane]["band_cells"] else "OFF_BAND",
            "replicate": rep, "seed": seed, "freeze_sha": freeze_sha, "prediction": committed, "prediction_sha256": phash,
            "observation": observation, "agreement": bool(agreement), "margin": float(margin),
            "band_inside": bool(inside), "band_detail": detail, "z_band": Z_BAND,
            "wall_s": time.time() - t0, "environment": {"python": sys.version.split()[0], "sklearn": sklearn.__version__,
                                                        "numpy": np.__version__, "platform": platform.platform(), "host": platform.node()}}


def lane_terminal(lane, cells, lane_rs):
    off = [c for v, c in cells.items() if c["cell_class"] == "OFF_BAND"]
    off_rs = [r for r in lane_rs if r["cell_class"] == "OFF_BAND"]
    all_green = all(c["verdict"] == "GREEN" for c in off)
    any_red = any(c["verdict"] == "THEORY_RED" for c in off)
    cv_same_off = sum(1 for r in off_rs if r["prediction"]["cv_predicted_winner"] == r["prediction"]["gmi_predicted_winner"])
    n_off = len(off_rs)
    parent_ok = cv_same_off >= math.ceil(0.9 * n_off)
    if lane == "B_SPECIALIZATION_REAL":
        if any_red:
            t = "B_SPECIALIZATION_REAL_MASS_WEIGHTED_LAW_RED_OFF_BAND"
        elif all_green and parent_ok:
            t = "B_SPECIALIZATION_REAL_GREEN_OFF_BAND_UNDER_MASS_WEIGHTED_TERM__FREE_LAW_EQUALS_CV_OFF_BAND__CROSSOVER_CELLS_INSIDE_BAND_BY_CONSTRUCTION"
        elif all_green:
            t = "B_SPECIALIZATION_REAL_GREEN_OFF_BAND_UNDER_MASS_WEIGHTED_TERM__PARENT_SUFFICIENT_CV"
        else:
            t = "B_SPECIALIZATION_REAL_OFF_BAND_INCONCLUSIVE_OR_SIZING_MISS"
    else:
        ho_same = sum(1 for r in lane_rs if r["prediction"]["holdout_predicted_winner"] == r["prediction"]["gmi_predicted_winner"])
        p10 = ho_same >= math.ceil(0.9 * len(lane_rs))
        if not all_green:
            t = "F_CONTINUAL_REAL_PROBE_DESCRIPTOR_KILLED" if any(c["verdict"] in ("THEORY_RED", "INCONCLUSIVE") for c in off) else "F_CONTINUAL_REAL_OFF_BAND_SIZING_MISS"
        elif parent_ok:
            t = "F_CONTINUAL_REAL_GREEN_OFF_CROSSOVER_UNDER_PROBE_RETENTION_LAW__0_95_INSIDE_BAND_BY_CONSTRUCTION_ON_DIGITS"
        else:
            t = "F_CONTINUAL_REAL_GREEN_OFF_CROSSOVER__PARENT_SUFFICIENT_CV"
        if p10:
            t += "__PARENT_SUFFICIENT_HOLDOUT"
    return t, {"off_band_cells": len(off), "off_band_green": sum(1 for c in off if c["verdict"] == "GREEN"),
               "cv_same_as_gmi_off_band": cv_same_off, "n_off_band_replicates": n_off, "parent_free_substitute_ok": parent_ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze-sha", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--lanes", default=",".join(LANES))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--replicates", type=int, default=REPLICATES)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    hs = fetch_california_housing(); dg = load_digits()
    data = {"housing": (hs.data, hs.target), "digits": (dg.data, dg.target)}
    data_sha = {"housing": hashlib.sha256(np.ascontiguousarray(hs.data).tobytes() + np.ascontiguousarray(hs.target).tobytes()).hexdigest(),
                "digits": hashlib.sha256(np.ascontiguousarray(dg.data).tobytes() + np.ascontiguousarray(dg.target).tobytes()).hexdigest()}
    lanes = a.lanes.split(",")
    tasks = [(lane, v, r, a.freeze_sha, data) for lane in lanes for v in GRIDS[lane]["values"] for r in range(a.replicates)]
    from concurrent.futures import ProcessPoolExecutor
    receipts = []
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for rec in ex.map(run_task, tasks):
            receipts.append(rec)
            with open(os.path.join(a.out_dir, f"{rec['lane']}__{rec['value']}__r{rec['replicate']}.json"), "w") as f:
                json.dump(rec, f, indent=1, sort_keys=True, default=float)
            print(f"{rec['lane']} {rec['value']} r{rec['replicate']} [{rec['cell_class']}] pred={rec['prediction']['gmi_predicted_winner']} "
                  f"cv={rec['prediction']['cv_predicted_winner']} obs={rec['observation']['observed_winner']} adm={rec['observation']['admissible']} "
                  f"agree={rec['agreement']} band_in={rec['band_inside']} margin={rec['margin']:.4f} {rec['wall_s']:.1f}s", flush=True)
    cells, lane_results, lane_stats = {}, {}, {}
    for lane in lanes:
        lane_cells = {}
        for v in GRIDS[lane]["values"]:
            rs = [r for r in receipts if r["lane"] == lane and r["value"] == v]
            lane_cells[v] = score_cell(rs, v in GRIDS[lane]["band_cells"])
            cells[f"{lane}:{v}"] = lane_cells[v]
        lane_rs = [r for r in receipts if r["lane"] == lane]
        lane_results[lane], lane_stats[lane] = lane_terminal(lane, lane_cells, lane_rs)
    ok = {lane: ("GREEN_OFF_BAND" in lane_results[lane] or "GREEN_OFF_CROSSOVER_UNDER" in lane_results[lane]) and "PARENT_SUFFICIENT_CV" not in lane_results[lane]
          for lane in lanes}
    if any("PARENT_SUFFICIENT_CV" in lane_results[lane] for lane in lanes):
        terminal = "REAL_TRANSFER_PHASE_LAWS_PARENT_SUFFICIENT_CV"
    elif all(ok.values()):
        terminal = "REAL_TRANSFER_LAWS_FREE_PREOUTCOME_PREDICTOR_EQUALS_CV_OFF_BAND__CV_WINS_AT_CROSSOVERS"
    else:
        terminal = "REAL_TRANSFER_RV_377_194_OFF_BAND_NOT_GREEN_ON_" + "_".join(lane for lane in lanes if not ok[lane])
    agg = {"schema": SCHEMA + "Aggregate", "revival_id": REVIVAL_ID, "freeze_sha": a.freeze_sha, "seed_tag": SEED_TAG, "z_band": Z_BAND,
           "n_test_B": N_TEST_B, "probe_frac_F": PROBE_FRAC, "dataset_sha256": data_sha, "tasks": len(receipts), "expected_tasks": len(tasks),
           "cell_results": cells, "lane_results": lane_results, "lane_stats": lane_stats, "terminal": terminal,
           "environment": receipts[0]["environment"] if receipts else None}
    with open(os.path.join(a.out_dir, "REAL_TRANSFER_RV194_AGGREGATE.json"), "w") as f:
        json.dump(agg, f, indent=1, sort_keys=True, default=float)
    print(json.dumps({"lane_results": lane_results, "lane_stats": lane_stats, "terminal": terminal}, indent=1))


if __name__ == "__main__":
    main()
