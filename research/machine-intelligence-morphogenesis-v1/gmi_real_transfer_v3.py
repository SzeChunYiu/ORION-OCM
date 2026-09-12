"""RV-377-190: real-transfer of three frozen K5 held-family phase laws to real off-the-shelf learners on real data.

Frozen by GMI_REAL_TRANSFER_PHASE_LAWS_RV_377_190_FREEZE.md. Nothing in this file may change after the freeze
commit; the receipts record the freeze SHA passed on the command line and every seed is derived from it.

Machines are scikit-learn estimators only (no ORION/GMI code inside any machine). The K5 laws, price vectors,
quality thresholds and the V1/V2 scoring rules are transcribed from the frozen K5 contracts:
GMI_K5_BH_PHASE_FREEZE_V1.json, GMI_K5_BH_SCORING_FREEZE_V1.json, GMI_K5_BH_ADMISSIBILITY_SCORING_ADDENDUM_V2.json,
GMI_K5_BH_CONTINUAL_CORRIGENDUM_V3.json, GMI_K5_BH_REVIVAL_PLAN_V8.json (reachability clause, RV-377-170).

Per replicate the runner (1) draws the protected split, (2) computes pre-outcome descriptors on the training split
only, (3) commits the GMI-law prediction and the parent (CV) prediction, hashing both, (4) only then touches the
test split. Prediction dicts are deep-copied and hashed before step (4) and the hash is re-checked at write time.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import sys
import time
import warnings

import numpy as np
import sklearn
from sklearn.cluster import KMeans
from sklearn.datasets import fetch_california_housing, load_digits
from sklearn.decomposition import PCA
from sklearn.exceptions import ConvergenceWarning
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import StratifiedKFold, KFold, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=ConvergenceWarning)

SCHEMA = "GMIRealTransferPhaseLawsV3"
REVIVAL_ID = "RV-377-190"

# ---------------------------------------------------------------- frozen grids, thresholds, prices (K5 contracts)
GRIDS = {
    "F_CONTINUAL_REAL": {"parameter": "label_agreement", "values": [0.6, 0.8, 0.9, 0.95, 1.0]},
    "B_SPECIALIZATION_REAL": {"parameter": "injected_tau", "values": [0.0, 0.1, 0.3, 0.8]},
    "C_FEATURE_LEARNING_REAL": {"parameter": "real_signal_s", "values": [0.0, 0.3, 0.6, 1.0]},
}
REPLICATES = 8
Q = {  # GMI_K5_BH_SCORING_FREEZE_V1.json quality_thresholds, unchanged
    "B_SPECIALIZATION_max_test_mse": 0.50,
    "C_FEATURE_LEARNING_max_test_error": 0.18,
    "F_CONTINUAL_min_old_accuracy": 0.95,
    "F_CONTINUAL_min_new_accuracy": 0.90,
}
# K5 price vectors (gmi_k5_bh_experiments.py, unchanged)
P_F = {"state_per_param": 1.0, "replay_per_stored_scalar": 0.001, "work": 1e-5}
P_B = {"state_per_model": 0.002, "work_per_sample": 1e-5, "route_work_per_query": 0.02}
P_C = {"error_pp": 100.0, "state": 0.02, "step": 0.005, "movement": 0.01}


REVIVAL = {"active": False, "world": False}
# --revival: RV-377-191 (F descriptor) + RV-377-192 (B descriptor); --revival2: RV-377-193 (B world stage: feature
# tails winsorised at training-split 1st/99th percentiles; the RV-377-192 descriptor is kept). See the revival freezes.


def seed_for(freeze_sha: str, lane: str, value: float, rep: int) -> int:
    tag = "GMI-RT-V3R2" if REVIVAL["world"] else ("GMI-RT-V3R" if REVIVAL["active"] else "GMI-RT-V3")
    h = hashlib.sha256(f"{tag}|{freeze_sha}|{lane}|{value}|{rep}".encode()).hexdigest()
    return int(h[:16], 16) % (2 ** 32)


def sha_of(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=float).encode()).hexdigest()


def cheapest(admissible, cost):
    return "NONE" if not admissible else min(admissible, key=lambda s: (cost[s], s))


def margin_k5(pred, admissible, cost):
    """K5 convention: alt-min minus predicted if predicted admissible and alternatives exist; +1 if predicted is the
    only admissible; -1 if predicted inadmissible (or NONE predicted while something is admissible)."""
    if pred == "NONE":
        return 1.0 if not admissible else -1.0
    if pred not in admissible:
        return -1.0
    alts = [cost[s] for s in admissible if s != pred]
    return (min(alts) - cost[pred]) if alts else 1.0


# ================================================================ lane 1: F_CONTINUAL on sklearn digits
OLD_POS = {0, 1, 2, 3, 4}
FLIP_ORDER = [5, 4, 6, 3]  # full-class flips, applied in this order


def new_task_labels(classes: np.ndarray, agreement: float, half_flip_thresh: float | None, bright: np.ndarray):
    """y_new for agreement a. a=1.0: identical to old. 0.9/0.8/0.6: 1/2/4 full-class flips. 0.95: half of class 5
    (samples with mean intensity above the training-split median of class-5 mean intensities) joins the positives."""
    pos = set(OLD_POS)
    y_old = np.isin(classes, list(OLD_POS)).astype(int)
    if agreement == 1.0:
        return y_old.copy()
    if agreement == 0.95:
        y = y_old.copy()
        y[(classes == 5) & (bright > half_flip_thresh)] = 1
        return y
    k = {0.9: 1, 0.8: 2, 0.6: 4}[agreement]
    for c in FLIP_ORDER[:k]:
        pos ^= {c}
    return np.isin(classes, list(pos)).astype(int)


def mlp(seed, warm=False, hidden=64, max_iter=300):
    return MLPClassifier(hidden_layer_sizes=(hidden,), max_iter=max_iter, random_state=seed, warm_start=warm,
                         n_iter_no_change=max_iter, tol=0.0)


def n_params(m: MLPClassifier) -> int:
    return int(sum(c.size for c in m.coefs_) + sum(b.size for b in m.intercepts_))


def continual_strategies(Xo, yo, Xn, yn, seed, ref_old=None):
    """Return dict strategy -> (old_model, new_model, state, replay, work). old_model is the model answering old-task
    queries, new_model the one answering new-task queries."""
    old = mlp(seed, warm=True).fit(Xo, yo) if ref_old is None else ref_old
    e0 = int(old.n_iter_)
    work_old = e0 * len(Xo)
    p = n_params(old)
    out = {}
    # REWRITE: continue training the old model (warm start) on new data only; n_iter_ accumulates, so continued
    # epochs = n_iter_ - e0
    rw = copy.deepcopy(old); rw.fit(Xn, yn)
    out["REWRITE"] = (rw, rw, p, 0.0, work_old + (int(rw.n_iter_) - e0) * len(Xn))
    # REPLAY: continue training the old model on stored old data + new data
    rp = copy.deepcopy(old); rp.fit(np.vstack([Xo, Xn]), np.concatenate([yo, yn]))
    out["REPLAY"] = (rp, rp, p, P_F["replay_per_stored_scalar"] * Xo.size, work_old + (int(rp.n_iter_) - e0) * (len(Xo) + len(Xn)))
    # EXPANSION: keep old model, train a separate new model
    nw = mlp(seed ^ 0x5EED).fit(Xn, yn)
    out["EXPANSION"] = (old, nw, p + n_params(nw), 0.0, work_old + int(nw.n_iter_) * len(Xn))
    return out


def cost_F(state, replay, work):
    return P_F["state_per_param"] * state + replay + P_F["work"] * work


def lane_F(seed, agreement, data):
    X, cls = data["digits"]
    Xtr, Xte, ctr, cte = train_test_split(X, cls, test_size=0.25, random_state=seed, stratify=cls)
    btr = Xtr.mean(1); bte = Xte.mean(1)  # raw mean pixel intensity (before scaling)
    sc = StandardScaler().fit(Xtr); Xtr = sc.transform(Xtr); Xte = sc.transform(Xte)
    thr = float(np.median(btr[ctr == 5])) if (ctr == 5).any() else 0.0
    y_old_tr = np.isin(ctr, list(OLD_POS)).astype(int); y_old_te = np.isin(cte, list(OLD_POS)).astype(int)
    y_new_tr = new_task_labels(ctr, agreement, thr, btr); y_new_te = new_task_labels(cte, agreement, thr, bte)
    # old half / new half of the training split (disjoint samples, same distribution: the K5 world's structure)
    idx = np.random.RandomState(seed).permutation(len(Xtr)); h = len(idx) // 2
    io, i_n = idx[:h], idx[h:]
    Xo, yo = Xtr[io], y_old_tr[io]; Xn, yn = Xtr[i_n], y_new_tr[i_n]
    # ---- descriptors (training split only)
    a_hat = float(np.mean(y_old_tr == y_new_tr))
    omega_hat = float(np.cos(np.pi * (1.0 - a_hat)))
    if REVIVAL["active"]:
        # RV-377-191 (descriptor stage): e_hat from 5-fold CV of the old model over the whole old half (sd ~0.007
        # instead of ~0.017 from a 108-sample holdout); the deployed old model is trained on the full old half.
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed); errs = []
        for tr_i, te_i in skf.split(Xo, yo):
            errs.append(float(np.mean(mlp(seed, warm=True).fit(Xo[tr_i], yo[tr_i]).predict(Xo[te_i]) != yo[te_i])))
        e_hat = float(np.mean(errs)); Xo_fit, yo_fit = Xo, yo
        old = mlp(seed, warm=True).fit(Xo_fit, yo_fit)
    else:
        # inner holdout of the OLD half gives the learner's base error e_hat; the old model is then the holdout-trained one
        Xo_fit, Xo_ho, yo_fit, yo_ho = train_test_split(Xo, yo, test_size=0.2, random_state=seed, stratify=yo)
        old = mlp(seed, warm=True).fit(Xo_fit, yo_fit)
        e_hat = float(np.mean(old.predict(Xo_ho) != yo_ho))
    pred_acc = {
        "REWRITE": {"old": 1.0 - (1.0 - a_hat) - e_hat, "new": 1.0 - e_hat},
        "REPLAY": {"old": 1.0 - e_hat - (1.0 - a_hat) / 2.0, "new": 1.0 - e_hat - (1.0 - a_hat) / 2.0},
        "EXPANSION": {"old": 1.0 - e_hat, "new": 1.0 - e_hat},
    }
    pred_adm = [s for s, v in pred_acc.items()
                if v["old"] >= Q["F_CONTINUAL_min_old_accuracy"] and v["new"] >= Q["F_CONTINUAL_min_new_accuracy"]]
    # development receipts (training only) fix the price of each strategy
    strategies = continual_strategies(Xo_fit, yo_fit, Xn, yn, seed, ref_old=old)
    cost = {s: cost_F(v[2], v[3], v[4]) for s, v in strategies.items()}
    gmi_pred = cheapest(pred_adm, cost)
    # ---- parent: 3-fold CV on the training split (each half folded), same rule on CV estimates
    kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    cv_old = {s: [] for s in strategies}; cv_new = {s: [] for s in strategies}
    folds_o = list(kf.split(Xo, yo)); folds_n = list(kf.split(Xn, yn))
    for (tro, teo), (trn, ten) in zip(folds_o, folds_n):
        st = continual_strategies(Xo[tro], yo[tro], Xn[trn], yn[trn], seed)
        for s, (mo, mn, *_rest) in st.items():
            cv_old[s].append(float(np.mean(mo.predict(Xo[teo]) == yo[teo])))
            cv_new[s].append(float(np.mean(mn.predict(Xn[ten]) == yn[ten])))
    cv_acc = {s: {"old": float(np.mean(cv_old[s])), "new": float(np.mean(cv_new[s]))} for s in strategies}
    cv_adm = [s for s, v in cv_acc.items()
              if v["old"] >= Q["F_CONTINUAL_min_old_accuracy"] and v["new"] >= Q["F_CONTINUAL_min_new_accuracy"]]
    cv_pred = cheapest(cv_adm, cost)
    prediction = {"gmi_predicted_winner": gmi_pred, "gmi_predicted_admissible": pred_adm, "gmi_predicted_acc": pred_acc,
                  "descriptors": {"a_hat": a_hat, "omega_hat_k5": omega_hat, "e_hat": e_hat},
                  "cv_predicted_winner": cv_pred, "cv_predicted_admissible": cv_adm, "cv_acc": cv_acc, "cost": cost}
    committed = copy.deepcopy(prediction); phash = sha_of(committed)
    # ---- protected test (touched only now)
    obs_acc = {s: {"old": float(np.mean(v[0].predict(Xte) == y_old_te)), "new": float(np.mean(v[1].predict(Xte) == y_new_te))}
               for s, v in strategies.items()}
    admissible = [s for s, v in obs_acc.items()
                  if v["old"] >= Q["F_CONTINUAL_min_old_accuracy"] and v["new"] >= Q["F_CONTINUAL_min_new_accuracy"]]
    observed = cheapest(admissible, cost)
    return committed, phash, {"observed_winner": observed, "admissible": admissible, "observed_acc": obs_acc,
                              "test_agreement": float(np.mean(y_old_te == y_new_te)),
                              "n_train_old": int(len(Xo_fit)), "n_train_new": int(len(Xn)), "n_test": int(len(Xte)),
                              "state": {s: v[2] for s, v in strategies.items()}, "work": {s: v[4] for s, v in strategies.items()}}


# ================================================================ lane 2: B_SPECIALIZATION on California housing
M_MODES = 4
Z_OFFSETS = np.array([-3.0, -1.0, 1.0, 3.0]) / np.sqrt(5.0)  # K5 world: unit-variance mode offsets scaled by tau
N_TRAIN_B = 400
N_TEST_B = 2000


def lane_B(seed, tau, data):
    X, y = data["housing"]
    rs = np.random.RandomState(seed)
    idx = rs.permutation(len(X))[: N_TRAIN_B + N_TEST_B]
    itr, ite = idx[:N_TRAIN_B], idx[N_TRAIN_B:]
    Xraw_tr, Xraw_te = X[itr], X[ite]
    if REVIVAL["world"]:
        # RV-377-193 (world stage): bound the feature tails at the training-split 1st/99th percentiles (pre-outcome;
        # the same clip is applied to the test rows). Nothing else changes.
        lo, hi = np.percentile(Xraw_tr, [1, 99], axis=0)
        Xraw_tr = np.clip(Xraw_tr, lo, hi); Xraw_te = np.clip(Xraw_te, lo, hi)
    sx = StandardScaler().fit(Xraw_tr); Xtr = sx.transform(Xraw_tr); Xte = sx.transform(Xraw_te)
    mu, sd = float(np.mean(y[itr])), float(np.std(y[itr]))
    ytr = (y[itr] - mu) / sd; yte = (y[ite] - mu) / sd
    km = KMeans(n_clusters=M_MODES, n_init=10, random_state=seed).fit(Xtr)
    mtr = km.labels_; mte = km.predict(Xte)
    ytr = ytr + tau * Z_OFFSETS[mtr]; yte = yte + tau * Z_OFFSETS[mte]  # injected heterogeneity (the only synthetic element)
    p = Xtr.shape[1] + 1
    # ---- descriptors (training split only): shared fit, residual decomposition (K5 form: offsets + within noise)
    shared = Ridge(alpha=1.0).fit(Xtr, ytr)
    r = ytr - shared.predict(Xtr)
    n = len(Xtr); n_j = np.array([(mtr == j).sum() for j in range(M_MODES)])
    means = np.array([r[mtr == j].mean() if n_j[j] else 0.0 for j in range(M_MODES)])
    within = float(sum(((r[mtr == j] - means[j]) ** 2).sum() for j in range(M_MODES)) / max(1, n - M_MODES))
    between = float((n_j * means ** 2).sum() / n)
    # noise floor of the weighted between-mode variance of residual means under zero true offsets: (m-1) sigma^2 / n
    tau2_hat = max(0.0, between - within * (M_MODES - 1) / n)
    sigma2_hat = within
    if REVIVAL["active"]:
        # RV-377-192 (theory/descriptor stage): heterogeneity relative to what the SHARED model class can represent,
        # i.e. parameter (slope + offset) heterogeneity across modes (Chow form): in-sample SSE reduction of the
        # per-mode fits over the shared fit, minus the overfitting allowance p (m-1) sigma^2 / n; sigma^2 from the
        # per-mode fits. The K5 grand-mean world is the special case p = 1 (offsets only).
        sse_shared = float((r ** 2).sum()); sse_exp = 0.0
        for j in range(M_MODES):
            sel = mtr == j
            if sel.sum() >= 2:
                ej = Ridge(alpha=1.0).fit(Xtr[sel], ytr[sel]); sse_exp += float(((ytr[sel] - ej.predict(Xtr[sel])) ** 2).sum())
            else:
                sse_exp += float((r[sel] ** 2).sum())
        sigma2_hat = sse_exp / max(1, n - M_MODES * p)
        tau2_hat = max(0.0, (sse_shared - sse_exp) / n - sigma2_hat * p * (M_MODES - 1) / n)
    price_shared = P_B["state_per_model"] * 1 + P_B["work_per_sample"] * n
    price_spec = P_B["state_per_model"] * M_MODES + P_B["work_per_sample"] * (n + N_TEST_B * P_B["route_work_per_query"])
    exp_shared = sigma2_hat + tau2_hat + sigma2_hat * p / n + price_shared
    exp_spec = sigma2_hat + sigma2_hat * p * float(np.mean(1.0 / np.maximum(n_j, 1))) + price_spec
    pred_adm = [s for s, v in (("SHARED", exp_shared - price_shared), ("SPECIALIZED", exp_spec - price_spec))
                if v <= Q["B_SPECIALIZATION_max_test_mse"]]
    exp = {"SHARED": exp_shared, "SPECIALIZED": exp_spec}
    gmi_pred = cheapest(pred_adm, exp)
    # ---- parent: 3-fold CV of both routes on the training split
    kf = KFold(n_splits=3, shuffle=True, random_state=seed)
    cv = {"SHARED": [], "SPECIALIZED": []}
    for tr, te in kf.split(Xtr):
        sh = Ridge(alpha=1.0).fit(Xtr[tr], ytr[tr]); cv["SHARED"].append(float(np.mean((sh.predict(Xtr[te]) - ytr[te]) ** 2)))
        pr = np.zeros(len(te))
        for j in range(M_MODES):
            sel = mtr[tr] == j; tsel = mtr[te] == j
            if tsel.any():
                mdl = Ridge(alpha=1.0).fit(Xtr[tr][sel], ytr[tr][sel]) if sel.sum() >= 2 else sh
                pr[tsel] = mdl.predict(Xtr[te][tsel])
        cv["SPECIALIZED"].append(float(np.mean((pr - ytr[te]) ** 2)))
    cv_mse = {s: float(np.mean(v)) for s, v in cv.items()}
    cv_obj = {"SHARED": cv_mse["SHARED"] + price_shared, "SPECIALIZED": cv_mse["SPECIALIZED"] + price_spec}
    cv_adm = [s for s in cv_mse if cv_mse[s] <= Q["B_SPECIALIZATION_max_test_mse"]]
    cv_pred = cheapest(cv_adm, cv_obj)
    prediction = {"gmi_predicted_winner": gmi_pred, "gmi_predicted_admissible": pred_adm, "gmi_expected_objective": exp,
                  "descriptors": {"tau2_hat": tau2_hat, "tau_hat": float(np.sqrt(tau2_hat)), "sigma2_hat": sigma2_hat,
                                  "between_raw": between, "n_per_mode": n_j.tolist(), "p": p},
                  "cv_predicted_winner": cv_pred, "cv_predicted_admissible": cv_adm, "cv_mse": cv_mse,
                  "price": {"SHARED": price_shared, "SPECIALIZED": price_spec}}
    committed = copy.deepcopy(prediction); phash = sha_of(committed)
    # ---- protected test
    experts = {j: (Ridge(alpha=1.0).fit(Xtr[mtr == j], ytr[mtr == j]) if (mtr == j).sum() >= 2 else shared) for j in range(M_MODES)}
    pred_te = np.zeros(len(Xte))
    for j in range(M_MODES):
        sel = mte == j
        if sel.any():
            pred_te[sel] = experts[j].predict(Xte[sel])
    mse = {"SHARED": float(np.mean((shared.predict(Xte) - yte) ** 2)), "SPECIALIZED": float(np.mean((pred_te - yte) ** 2))}
    obj = {"SHARED": mse["SHARED"] + price_shared, "SPECIALIZED": mse["SPECIALIZED"] + price_spec}
    admissible = [s for s in mse if mse[s] <= Q["B_SPECIALIZATION_max_test_mse"]]
    observed = cheapest(admissible, obj)
    return committed, phash, {"observed_winner": observed, "admissible": admissible, "test_mse": mse, "objective": obj,
                              "n_train": int(n), "n_test": int(len(Xte)), "router_errors": 0}


# ================================================================ lane 3: C_FEATURE_LEARNING on sklearn digits
PCA_D = 16
RFF_D = 288          # fixed-feature state = 288 + 1 = 289
MLP_H = 16           # trainable state = 16*16 + 16 + 16 + 1 = 289 (matched)
MLP_BUDGET = 200     # frozen development budget D_real: 200 epochs, adam, lr 1e-3, no early stopping


def make_mlp_C(seed):
    return MLPClassifier(hidden_layer_sizes=(MLP_H,), max_iter=MLP_BUDGET, random_state=seed, n_iter_no_change=MLP_BUDGET,
                         tol=0.0, learning_rate_init=1e-3, alpha=1e-4)


def flat(m):
    return np.concatenate([c.ravel() for c in m.coefs_] + [b.ravel() for b in m.intercepts_])


def fit_fixed(Ztr, ytr, seed):
    rff = RBFSampler(gamma=1.0 / PCA_D, n_components=RFF_D, random_state=seed).fit(Ztr)
    lr = LogisticRegression(max_iter=500, C=1.0).fit(rff.transform(Ztr), ytr)
    return rff, lr


def fit_trainable(Ztr, ytr, seed):
    init = make_mlp_C(seed); init.set_params(max_iter=1, learning_rate_init=1e-12, n_iter_no_change=1)
    init.fit(Ztr[:2], np.array([0, 1]))  # ~initial weights (same random_state, same shapes)
    w0 = flat(init)
    m = make_mlp_C(seed).fit(Ztr, ytr)
    return m, float(np.linalg.norm(flat(m) - w0))


def obj_C(err, state, steps, movement):
    return P_C["error_pp"] * err + P_C["state"] * state + P_C["step"] * steps + P_C["movement"] * movement


def lane_C(seed, s, data):
    X, cls = data["digits"]
    y_real = (cls >= 5).astype(int)
    Xtr, Xte, ytr_real, yte_real = train_test_split(X, y_real, test_size=0.25, random_state=seed, stratify=y_real)
    sc = StandardScaler().fit(Xtr); pca = PCA(n_components=PCA_D, random_state=seed).fit(sc.transform(Xtr))
    Ztr = pca.transform(sc.transform(Xtr)); Zte = pca.transform(sc.transform(Xte))
    zs = StandardScaler().fit(Ztr); Ztr = zs.transform(Ztr); Zte = zs.transform(Zte)
    # world: linear surrogate of the real target (training split), blended with the real label at strength s
    lin = LogisticRegression(max_iter=1000).fit(Ztr, ytr_real)
    g_tr = lin.decision_function(Ztr); g_sd = float(np.std(g_tr)) or 1.0
    g_te = lin.decision_function(Zte)
    ytr = ((1 - s) * g_tr / g_sd + s * (2 * ytr_real - 1) >= 0).astype(int)
    yte = ((1 - s) * g_te / g_sd + s * (2 * yte_real - 1) >= 0).astype(int)
    # ---- descriptors (training split only) + development receipts
    rff, lr = fit_fixed(Ztr, ytr, seed)
    e_fix_tr = float(np.mean(lr.predict(rff.transform(Ztr)) != ytr))
    m, movement = fit_trainable(Ztr, ytr, seed)
    e_mlp_tr = float(np.mean(m.predict(Ztr) != ytr))
    state_f, state_m = RFF_D + 1, n_params(m)
    steps_f, steps_m = int(np.max(lr.n_iter_)), int(m.n_iter_)
    delta_pp = P_C["state"] * (state_m - state_f) + P_C["step"] * (steps_m - steps_f) + P_C["movement"] * movement
    gain_pred_pp = 100.0 * (e_fix_tr - e_mlp_tr)
    pred_adm = [n for n, e in (("FIXED_FEATURE", e_fix_tr), ("TRAINABLE_FEATURE", e_mlp_tr)) if e <= Q["C_FEATURE_LEARNING_max_test_error"]]
    if not pred_adm:
        gmi_pred = "NONE"
    elif len(pred_adm) == 1:
        gmi_pred = pred_adm[0]
    else:
        gmi_pred = "TRAINABLE_FEATURE" if gain_pred_pp > delta_pp else "FIXED_FEATURE"
    # ---- parent: 3-fold CV of both realizations on the training split, same objective rule
    kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
    cv_e = {"FIXED_FEATURE": [], "TRAINABLE_FEATURE": []}
    for tr, te in kf.split(Ztr, ytr):
        r2, l2 = fit_fixed(Ztr[tr], ytr[tr], seed); cv_e["FIXED_FEATURE"].append(float(np.mean(l2.predict(r2.transform(Ztr[te])) != ytr[te])))
        m2 = make_mlp_C(seed).fit(Ztr[tr], ytr[tr]); cv_e["TRAINABLE_FEATURE"].append(float(np.mean(m2.predict(Ztr[te]) != ytr[te])))
    cv_err = {k: float(np.mean(v)) for k, v in cv_e.items()}
    cv_obj = {"FIXED_FEATURE": obj_C(cv_err["FIXED_FEATURE"], state_f, steps_f, 0.0),
              "TRAINABLE_FEATURE": obj_C(cv_err["TRAINABLE_FEATURE"], state_m, steps_m, movement)}
    cv_adm = [k for k, e in cv_err.items() if e <= Q["C_FEATURE_LEARNING_max_test_error"]]
    cv_pred = cheapest(cv_adm, cv_obj)
    prediction = {"gmi_predicted_winner": gmi_pred, "gmi_predicted_admissible": pred_adm,
                  "descriptors": {"s_hat_fixed_train_error": e_fix_tr, "trainable_train_error": e_mlp_tr,
                                  "gain_pred_pp": gain_pred_pp, "delta_pp": delta_pp, "steps_fixed": steps_f,
                                  "steps_trainable": steps_m, "state_fixed": state_f, "state_trainable": state_m,
                                  "feature_movement": movement},
                  "cv_predicted_winner": cv_pred, "cv_predicted_admissible": cv_adm, "cv_err": cv_err}
    committed = copy.deepcopy(prediction); phash = sha_of(committed)
    # ---- protected test
    e_fix = float(np.mean(lr.predict(rff.transform(Zte)) != yte)); e_mlp = float(np.mean(m.predict(Zte) != yte))
    obj = {"FIXED_FEATURE": obj_C(e_fix, state_f, steps_f, 0.0), "TRAINABLE_FEATURE": obj_C(e_mlp, state_m, steps_m, movement)}
    admissible = [k for k, e in (("FIXED_FEATURE", e_fix), ("TRAINABLE_FEATURE", e_mlp)) if e <= Q["C_FEATURE_LEARNING_max_test_error"]]
    observed = cheapest(admissible, obj)
    return committed, phash, {"observed_winner": observed, "admissible": admissible, "objective": obj,
                              "fixed_test_error": e_fix, "trainable_test_error": e_mlp, "gain_pp": 100.0 * (e_fix - e_mlp),
                              "n_train": int(len(Ztr)), "n_test": int(len(Zte)),
                              "test_label_flip_fraction_vs_linear": float(np.mean(yte != (g_te >= 0)))}


LANES = {"F_CONTINUAL_REAL": lane_F, "B_SPECIALIZATION_REAL": lane_B, "C_FEATURE_LEARNING_REAL": lane_C}


# ================================================================ scoring (V1 stochastic rule + V2 addendum)
def score_cell(receipts):
    n = len(receipts)
    inadm = sum(1 for r in receipts if r["prediction"]["gmi_predicted_winner"] != "NONE"
                and r["prediction"]["gmi_predicted_winner"] not in r["observation"]["admissible"])
    agree = sum(1 for r in receipts if r["agreement"])
    oppose = sum(1 for r in receipts if (not r["agreement"]) and r["prediction"]["gmi_predicted_winner"] in r["observation"]["admissible"])
    mean_margin = float(np.mean([r["margin"] for r in receipts]))
    if inadm >= 6:
        verdict = "THEORY_RED"
    elif inadm >= 1:
        verdict = "INCONCLUSIVE"
    elif agree >= 6 and mean_margin > 0:
        verdict = "GREEN"
    elif oppose >= 6 and mean_margin < 0:
        verdict = "THEORY_RED"
    else:
        verdict = "INCONCLUSIVE"
    cv_same = sum(1 for r in receipts if r["prediction"]["cv_predicted_winner"] == r["prediction"]["gmi_predicted_winner"])
    cv_right = sum(1 for r in receipts if r["prediction"]["cv_predicted_winner"] == r["observation"]["observed_winner"])
    gmi_right = sum(1 for r in receipts if r["prediction"]["gmi_predicted_winner"] == r["observation"]["observed_winner"])
    return {"n": n, "agree": agree, "oppose": oppose, "predicted_inadmissible": inadm, "mean_margin": mean_margin,
            "verdict": verdict, "cv_same_as_gmi": cv_same, "cv_correct": cv_right, "gmi_correct": gmi_right}


def run_task(args):
    lane, value, rep, freeze_sha, data = args[:5]
    if len(args) > 5 and args[5]:
        REVIVAL["active"] = True      # worker processes: re-activate the revival variant
    if len(args) > 6 and args[6]:
        REVIVAL["world"] = True
    seed = seed_for(freeze_sha, lane, value, rep)
    t0 = time.time()
    committed, phash, observation = LANES[lane](seed, value, data)
    assert sha_of(committed) == phash, "prediction mutated after commit"
    pred = committed["gmi_predicted_winner"]
    # V2 addendum: agreement iff predicted == observed AND predicted is admissible (NONE agrees iff observed is NONE)
    agreement = (pred == observation["observed_winner"]) and (pred == "NONE" or pred in observation["admissible"])
    if lane == "F_CONTINUAL_REAL":
        margin = margin_k5(pred, observation["admissible"], committed["cost"])
    else:
        margin = margin_k5(pred, observation["admissible"], observation["objective"])
    rid = REVIVAL_ID if not REVIVAL["active"] else {"F_CONTINUAL_REAL": "RV-377-191", "B_SPECIALIZATION_REAL": "RV-377-192"}.get(lane, REVIVAL_ID)
    if REVIVAL["world"] and lane == "B_SPECIALIZATION_REAL":
        rid = "RV-377-193"
    return {"schema": SCHEMA, "revival_id": rid, "revival_variant": REVIVAL["active"], "world_variant": REVIVAL["world"],
            "lane": lane, "parameter": GRIDS[lane]["parameter"], "value": value,
            "replicate": rep, "seed": seed, "freeze_sha": freeze_sha, "prediction": committed, "prediction_sha256": phash,
            "observation": observation, "agreement": bool(agreement), "margin": float(margin),
            "wall_s": time.time() - t0, "environment": {"python": sys.version.split()[0], "sklearn": sklearn.__version__,
                                                        "numpy": np.__version__, "platform": platform.platform(), "host": platform.node()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze-sha", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--lanes", default=",".join(LANES))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--revival", action="store_true", help="RV-377-191/192 descriptor-stage variants (F, B lanes)")
    ap.add_argument("--revival2", action="store_true", help="RV-377-193 world-stage variant (B lane; implies --revival)")
    a = ap.parse_args()
    if a.revival2:
        a.revival = True; REVIVAL["world"] = True
    if a.revival:
        REVIVAL["active"] = True
    os.makedirs(a.out_dir, exist_ok=True)
    hs = fetch_california_housing(); dg = load_digits()
    data = {"housing": (hs.data, hs.target), "digits": (dg.data, dg.target)}
    data_sha = {"housing": hashlib.sha256(np.ascontiguousarray(hs.data).tobytes() + np.ascontiguousarray(hs.target).tobytes()).hexdigest(),
                "digits": hashlib.sha256(np.ascontiguousarray(dg.data).tobytes() + np.ascontiguousarray(dg.target).tobytes()).hexdigest()}
    tasks = [(lane, v, r, a.freeze_sha, data, a.revival, a.revival2) for lane in a.lanes.split(",") for v in GRIDS[lane]["values"] for r in range(REPLICATES)]
    from concurrent.futures import ProcessPoolExecutor
    receipts = []
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for rec in ex.map(run_task, tasks):
            receipts.append(rec)
            with open(os.path.join(a.out_dir, f"{rec['lane']}__{rec['value']}__r{rec['replicate']}.json"), "w") as f:
                json.dump(rec, f, indent=1, sort_keys=True, default=float)
            print(f"{rec['lane']} {rec['value']} r{rec['replicate']} pred={rec['prediction']['gmi_predicted_winner']} "
                  f"cv={rec['prediction']['cv_predicted_winner']} obs={rec['observation']['observed_winner']} "
                  f"adm={rec['observation']['admissible']} agree={rec['agreement']} margin={rec['margin']:.4f} {rec['wall_s']:.1f}s", flush=True)
    cells, lanes = {}, {}
    for lane in a.lanes.split(","):
        verdicts = []
        for v in GRIDS[lane]["values"]:
            rs = [r for r in receipts if r["lane"] == lane and r["value"] == v]
            cells[f"{lane}:{v}"] = score_cell(rs); verdicts.append(cells[f"{lane}:{v}"]["verdict"])
        lanes[lane] = "GREEN" if all(x == "GREEN" for x in verdicts) else ("THEORY_RED" if "THEORY_RED" in verdicts else "INCONCLUSIVE")
        lane_rs = [r for r in receipts if r["lane"] == lane]
        lanes[lane + "__parent"] = ("PARENT_SUFFICIENT_CV" if all(r["prediction"]["cv_predicted_winner"] == r["prediction"]["gmi_predicted_winner"] for r in lane_rs)
                                    else "GMI_LAW_DIFFERS_FROM_CV_ON_%d_OF_%d_REPLICATES" % (
                                        sum(r["prediction"]["cv_predicted_winner"] != r["prediction"]["gmi_predicted_winner"] for r in lane_rs), len(lane_rs)))
    green = sum(1 for lane in a.lanes.split(",") if lanes[lane] == "GREEN")
    agg = {"schema": SCHEMA + "Aggregate", "revival_id": REVIVAL_ID if not a.revival else ("RV-377-193" if a.revival2 else "RV-377-191/192"),
           "revival_variant": a.revival, "world_variant": a.revival2,
           "freeze_sha": a.freeze_sha, "dataset_sha256": data_sha,
           "tasks": len(receipts), "expected_tasks": len(tasks), "cell_results": cells, "lane_results": lanes,
           "terminal": f"REAL_TRANSFER_PHASE_LAWS_GREEN_ON_{green}_OF_{len(a.lanes.split(','))}_LANES",
           "environment": receipts[0]["environment"] if receipts else None}
    with open(os.path.join(a.out_dir, "REAL_TRANSFER_AGGREGATE_V3.json"), "w") as f:
        json.dump(agg, f, indent=1, sort_keys=True, default=float)
    print(json.dumps({"lane_results": lanes, "terminal": agg["terminal"]}, indent=1))


if __name__ == "__main__":
    main()
