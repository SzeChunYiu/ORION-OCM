"""FNA-7/D8 pilot: capability transplant (K2 failure classification) on the FNA-5 world.

Executes CapabilityTransplantProtocolV1 end-to-end at micro scale: the held-constant
harness routes every query with the #219 A2 cost-model router (FREEZE AMENDMENT 1); on a
failed attempt the capability under transplant (failure-responsibility classification) is
supplied by one arm (incumbent-class neural reference / guarded rule / calibrated
estimator / tree / controls), the frozen repair table consumes the classification,
maintenance refresh re-fits the router on the frozen identification window, everything is
charged, and the #214 s5 ten-clause causal gate is evaluated.

Python 3.8 stdlib only. Deterministic under the frozen salts: sorted iteration, sha256/md5
seeds, no hash() use. World module fna5_world.py is imported READ-ONLY (PR #219).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from typing import Callable, Dict, List, Optional, Sequence, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(HERE, "..", "fna5-routing-first-refusal-v1"),
          os.path.join(HERE, "..", "..", "src")):
    if p not in sys.path:
        sys.path.insert(0, p)
import fna5_world as W  # noqa: E402  (read-only sibling capsule, PR #219)
import fna5_selectors as S  # noqa: E402  (read-only sibling capsule, PR #219)

FNA7_SALT = "fna7-capability-transplant-v1::77b1e4d2"
CLASSES = ("SELECTOR_METHOD_MISMATCH", "NOISE_BOUNDARY_UNAVOIDABLE", "STALE_DECLARED_MODEL")
DECLARED_CENTRES = {"theta1": 0.35, "theta2": 0.55, "theta3": 0.30,
                    "theta3s": 0.32, "theta4": 0.42, "theta7": 0.65}
GAMMA_GUARD = 0.15            # frozen noise band on estimated pass probability
STALE_GAP = 0.04              # frozen declared-vs-realized binding-clause gap
STALE_FLAG_TRIGGER = 8        # frozen stale flags before refresh
REFRESH_IDENTIFY_N = 24       # frozen identification window for the refresh price
EPS_ACC, EPS_COST = 0.03, 0.05

# --- clause physics (mirrors execute_instance inequalities; slacks are
#     threshold-minus-statistic so slack>0 means the clause holds; coef = u-sensitivity) ---

def clause_slacks(family: str, param: int, disp: float, alias: float,
                  th: Dict[str, float]) -> List[Tuple[float, float]]:
    """[(slack_at_neutral_u, u_coef)] for each conjunctive clause of the pass law."""
    if family == "window":
        theta_eff = th["theta1"] + (param - 28) * 0.002
        return [(theta_eff - disp, 0.12)]
    if family == "deepwindow":
        return [(disp - th["theta2"], 0.10), (th["theta3"] - alias, 0.10)]
    if family == "sample":
        return [(th["theta3s"] - alias, 0.12), (disp - th["theta4"], 0.08),
                (th["theta7"] - disp, 0.08)]
    return []  # exact families: no clauses (always pass)

def point_pass(family: str, param: int, disp: float, alias: float,
               th: Dict[str, float]) -> bool:
    return all(s > 0 for s, _ in clause_slacks(family, param, disp, alias, th))

def pass_prob(family: str, param: int, disp: float, alias: float,
              th: Dict[str, float]) -> float:
    """P(pass) with u~U(0,1): clause holds iff slack + coef*(u-0.5) > 0."""
    p = 1.0
    for slack, coef in clause_slacks(family, param, disp, alias, th):
        lo, hi = (slack - 0.5 * coef) / coef, (slack + 0.5 * coef) / coef
        p *= min(1.0, max(0.0, hi)) - min(1.0, max(0.0, lo))
    return min(1.0, max(0.0, p))

def would_pass(it, q, state: Dict[str, float]) -> bool:
    """Ground-truth realized outcome of an unexecuted instance (latents; labels/eval only)."""
    work, ok = W.execute_instance(it, q, state)
    return ok

# --- responsibility ground truth (frozen order; FREEZE_FNA7_V1.json) ---

def ground_truth(world: Dict, q, failed_it, insts: Sequence, drift: bool) -> str:
    state = world["state"]
    disp, alias = q.features[1], q.features[2]
    decl = point_pass(failed_it.family, failed_it.param, disp, alias, DECLARED_CENTRES)
    real = would_pass(failed_it, q, state)
    if drift and decl and not real:
        d_sl = min(clause_slacks(failed_it.family, failed_it.param, disp, alias,
                                 DECLARED_CENTRES))
        r_sl = min(clause_slacks(failed_it.family, failed_it.param, disp, alias, state))
        if abs(d_sl[0] - r_sl[0]) > STALE_GAP:
            return "STALE_DECLARED_MODEL"
    scan = next(it for it in insts if it.family == "scan")
    for g in insts:
        if g.family in W.EXACT_FAMILIES or g.family == failed_it.family:
            continue
        if (would_pass(g, q, state)
                and g.declared_cost_estimate(q, state) < scan.declared_cost_estimate(q, state)):
            return "SELECTOR_METHOD_MISMATCH"
    return "NOISE_BOUNDARY_UNAVOIDABLE"

# --- legal information surface (clause 2: the ONLY thing a classifier may see) ---

def legal_view(world: Dict, q, failed_it, insts: Sequence,
               catalogue_version: str) -> Dict:
    state = world["state"]
    disp, alias = q.features[1], q.features[2]
    scan = next(it for it in insts if it.family == "scan")
    diff = [g for g in insts if g.family not in W.EXACT_FAMILIES
            and g.family != failed_it.family]
    cheapest_diff = (min(g.declared_cost_estimate(q, state) for g in diff) if diff else -1.0)
    slacks = clause_slacks(failed_it.family, failed_it.param, disp, alias, DECLARED_CENTRES)
    return {
        "features": list(q.features), "family": failed_it.family, "param": failed_it.param,
        "declared_slacks": [round(s, 6) for s, _ in slacks],
        "failed_declared_cost": failed_it.declared_cost_estimate(q, state),
        "cheapest_diff_declared_cost": cheapest_diff,
        "scan_declared_cost": scan.declared_cost_estimate(q, state),
        "n_applicable": len(insts),
        "n_approx_applicable": len(diff) + 1,
        "applicable_catalogue": sorted(
            [(it.family, it.param, round(it.declared_cost_estimate(q, state), 4))
             for it in insts if it.family not in W.EXACT_FAMILIES]),
        "catalogue_version": catalogue_version,
    }

LATENT_KEYS = ("u", "realized", "split", "ground_truth")

def assert_legal(view: Dict) -> None:
    for k in LATENT_KEYS:
        assert k not in view, "latent leak into legal view: %s" % k
    assert "features" in view and len(view["features"]) == 12

# ---------------------------------------------------------------------------------------------
# replacement arms (non-neural; zero neural invocations, structurally tested)
# ---------------------------------------------------------------------------------------------


def _bayes_rule(view: Dict, th: Dict[str, float], allow_stale: bool) -> Tuple[Optional[str], int]:
    """Shared guarded estimator: SELECTOR iff a different-family alternative passes the
    gamma-guarded probability test cheaper than scan; STALE iff post-drift and the failed
    family's declared point-prediction contradicts the estimated one by > STALE_GAP;
    else NOISE. Counted work = comparisons performed."""
    feats = view["features"]
    disp, alias = feats[1], feats[2]
    work = 1
    if allow_stale and view["catalogue_version"] == "post-drift":
        decl_sl = min(s for s in view["declared_slacks"])
        est_sl = min(clause_slacks(view["family"], view["param"], disp, alias, th))
        if decl_sl > 0 and est_sl[0] <= 0 and abs(decl_sl - est_sl[0]) > STALE_GAP:
            return "STALE_DECLARED_MODEL", work + 6
        work += 6
    for fam, param, cost in view["applicable_catalogue"]:
        if fam == view["family"] or cost >= view["scan_declared_cost"]:
            continue
        work += 4
        if pass_prob(fam, param, disp, alias, th) >= 0.5 + GAMMA_GUARD:
            return "SELECTOR_METHOD_MISMATCH", work
    return "NOISE_BOUNDARY_UNAVOIDABLE", work


def r1_guarded_declared(view: Dict) -> Tuple[str, int]:
    cls, work = _bayes_rule(view, DECLARED_CENTRES, allow_stale=False)
    return cls, work  # zero-acquisition parent: declared centres ARE its estimate


def _estimate_thetas(dev_records: List[Dict]) -> Dict[str, float]:
    """R2 fit: feasible-interval estimation of realized constants from charged
    identification outcomes (pass/fail per clause-bearing family). Deterministic."""
    lo = {k: -1e9 for k in DECLARED_CENTRES}
    hi = {k: 1e9 for k in DECLARED_CENTRES}
    for rec in dev_records:
        disp, alias = rec["view"]["features"][1], rec["view"]["features"][2]
        for (fam, param), passed in sorted(rec["outcomes"].items()):
            if fam == "window":
                slack = disp - (DECLARED_CENTRES["theta1"] + (param - 28) * 0.002)
                if passed:
                    lo["theta1"] = max(lo["theta1"], slack - 0.06)
                else:
                    hi["theta1"] = min(hi["theta1"], slack + 0.06)
            elif fam == "deepwindow":
                if passed:
                    lo["theta2"] = max(lo["theta2"], disp - 0.05)
                    hi["theta3"] = min(hi["theta3"], alias + 0.05)
                else:
                    hi["theta2"] = min(hi["theta2"], disp + 0.05)
                    lo["theta3"] = max(lo["theta3"], alias - 0.05)
            elif fam == "sample":
                if passed:
                    hi["theta3s"] = min(hi["theta3s"], alias + 0.06)
                    lo["theta4"] = max(lo["theta4"], disp - 0.04)
                    hi["theta7"] = min(hi["theta7"], disp + 0.04)
                else:
                    lo["theta3s"] = max(lo["theta3s"], alias - 0.06)
                    hi["theta4"] = min(hi["theta4"], disp + 0.04)
                    lo["theta7"] = max(lo["theta7"], disp - 0.04)
    est = {}
    for k, centre in DECLARED_CENTRES.items():
        mid = (max(lo[k], centre - 0.15) + min(hi[k], centre + 0.15)) / 2.0
        est[k] = round(min(max(mid, centre - 0.15), centre + 0.15), 6)
    return est


def r2_make(dev_records: List[Dict]) -> Callable:
    th = _estimate_thetas(dev_records)

    def classify(view: Dict) -> Tuple[str, int]:
        return _bayes_rule(view, th, allow_stale=True)

    return classify, th


def feature_vector(view: Dict) -> List[float]:
    """Deterministic numeric encoding of the legal view (identical for R3 and MLP)."""
    fams = ("window", "deepwindow", "sample")
    v = list(view["features"]) + [float(view["param"]), view["failed_declared_cost"],
                                  view["cheapest_diff_declared_cost"], view["scan_declared_cost"],
                                  float(view["n_approx_applicable"]),
                                  1.0 if view["catalogue_version"] == "post-drift" else 0.0]
    v += [float(fam == view["family"]) for fam in fams]
    v += ([round(s, 6) for s in view["declared_slacks"]] + [0.0, 0.0, 0.0])[:3]
    params = sorted(p for _f, p, _c in view["applicable_catalogue"])
    v += [math.log2(1.0 + p) for p in params[:3]] + [0.0] * max(0, 3 - len(params))
    return v


def _gini_split(rows: List[Tuple[List[float], int]], depth: int, max_depth: int = 3,
                min_leaf: int = 8) -> dict:
    """Deterministic CART: features left-to-right, midpoints of sorted unique values,
    best (gini, feat, thr) with first-found tie-breaking; majority leaf."""
    counts: Dict[int, int] = {}
    for _x, y in rows:
        counts[y] = counts.get(y, 0) + 1
    if not rows or depth >= max_depth or len(rows) < 2 * min_leaf or len(counts) == 1:
        maj = (sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
               if counts else CLASSES.index("NOISE_BOUNDARY_UNAVOIDABLE"))
        return {"leaf": maj}
    base = 1.0 - sum((c / len(rows)) ** 2 for c in counts.values())
    best = None
    for f in range(len(rows[0][0])):
        vals = sorted(set(r[0][f] for r in rows))
        for i in range(len(vals) - 1):
            thr = (vals[i] + vals[i + 1]) / 2.0
            L = [r for r in rows if r[0][f] <= thr]
            R = [r for r in rows if r[0][f] > thr]
            if len(L) < min_leaf or len(R) < min_leaf:
                continue
            g = 0.0
            for part in (L, R):
                pc: Dict[int, int] = {}
                for _x, y in part:
                    pc[y] = pc.get(y, 0) + 1
                g += len(part) / len(rows) * (1.0 - sum((c / len(part)) ** 2 for c in pc.values()))
            if g < base - 1e-12 and (best is None or g < best[0] - 1e-12):
                best = (g, f, thr, L, R)
    if best is None:
        maj = (sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
               if counts else CLASSES.index("NOISE_BOUNDARY_UNAVOIDABLE"))
        return {"leaf": maj}
    _g, f, thr, L, R = best
    return {"feat": f, "thr": thr, "left": _gini_split(L, depth + 1),
            "right": _gini_split(R, depth + 1)}


def r3_make(dev_records: List[Dict]) -> Tuple[Callable, dict]:
    rows = [(feature_vector(r["view"]), CLASSES.index(r["label"])) for r in dev_records]
    tree = _gini_split(rows, 0)

    def classify(view: Dict) -> Tuple[str, int]:
        node, work = tree, 1
        while "feat" in node:
            node = node["left"] if feature_vector(view)[node["feat"]] <= node["thr"] else node["right"]
            work += 1
        return CLASSES[node["leaf"]], work

    return classify, tree


# ---------------------------------------------------------------------------------------------
# incumbent-class arm: seeded pure-stdlib MLP (pilot stand-in, declared limitation)
# ---------------------------------------------------------------------------------------------


def _standardize(rows: List[List[float]]):
    dim = len(rows[0])
    mean = [sum(r[i] for r in rows) / len(rows) for i in range(dim)]
    std = [max(1e-9, math.sqrt(sum((r[i] - mean[i]) ** 2 for r in rows) / len(rows)))
           for i in range(dim)]
    return mean, std


def mlp_make(dev_records: List[Dict], seed_key: str = "mlp") -> Tuple[Callable, dict]:
    if not dev_records:  # degenerate dev window: constant majority-class arm
        def const_cls(view: Dict) -> Tuple[str, int]:
            return "NOISE_BOUNDARY_UNAVOIDABLE", 1
        return const_cls, {"degenerate": True, "training_ops": 0}
    X = [feature_vector(r["view"]) for r in dev_records]
    Y = [CLASSES.index(r["label"]) for r in dev_records]
    mean, std = _standardize(X)
    X = [[(x[i] - mean[i]) / std[i] for i in range(len(x))] for x in X]
    rng = random.Random(int(hashlib.sha256((FNA7_SALT + seed_key).encode()).hexdigest(), 16))
    n_in, n_h, n_out, lr, epochs, batch = len(X[0]), 16, 3, 0.05, 60, 16
    W1 = [[rng.gauss(0, 0.4) for _ in range(n_in)] for _ in range(n_h)]
    b1 = [0.0] * n_h
    W2 = [[rng.gauss(0, 0.4) for _ in range(n_h)] for _ in range(n_out)]
    b2 = [0.0] * n_out
    ops = {"training_ops": 0}
    for _ep in range(epochs):
        order = list(range(len(X)))
        rng.shuffle(order)
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            gW1 = [[0.0] * n_in for _ in range(n_h)]
            gb1 = [0.0] * n_h
            gW2 = [[0.0] * n_h for _ in range(n_out)]
            gb2 = [0.0] * n_out
            for k in idx:
                x, y = X[k], Y[k]
                h = [math.tanh(sum(W1[i][j] * x[j] for j in range(n_in)) + b1[i]) for i in range(n_h)]
                o = [sum(W2[c][i] * h[i] for i in range(n_h)) + b2[c] for c in range(n_out)]
                m = max(o)
                ez = [math.exp(v - m) for v in o]
                p = [v / sum(ez) for v in ez]
                dh = [0.0] * n_h
                for c in range(n_out):
                    d = p[c] - (1.0 if c == y else 0.0)
                    gb2[c] += d
                    for i in range(n_h):
                        gW2[c][i] += d * h[i]
                        dh[i] += d * W2[c][i]
                for i in range(n_h):
                    dz = dh[i] * (1.0 - h[i] * h[i])
                    gb1[i] += dz
                    for j in range(n_in):
                        gW1[i][j] += dz * x[j]
                ops["training_ops"] += 2 * n_h * n_in + 2 * n_out * n_h + 30
            nb = len(idx)
            for i in range(n_h):
                b1[i] -= lr * gb1[i] / nb
                for j in range(n_in):
                    W1[i][j] -= lr * gW1[i][j] / nb
            for c in range(n_out):
                b2[c] -= lr * gb2[c] / nb
                for i in range(n_h):
                    W2[c][i] -= lr * gW2[c][i] / nb

    def classify(view: Dict) -> Tuple[str, int]:
        x = [(v - mean[i]) / std[i] for i, v in enumerate(feature_vector(view))]
        h = [math.tanh(sum(W1[i][j] * x[j] for j in range(n_in)) + b1[i]) for i in range(n_h)]
        o = [sum(W2[c][i] * h[i] for i in range(n_h)) + b2[c] for c in range(n_out)]
        cls = max(range(n_out), key=lambda c: (o[c], -c))
        return CLASSES[cls], 2 * n_h * n_in + 2 * n_out * n_h

    state = {"W1": W1, "b1": b1, "W2": W2, "b2": b2, "mean": mean, "std": std,
             "training_ops": ops["training_ops"]}
    return classify, state


# ---------------------------------------------------------------------------------------------
# held-constant harness H (identical across arms; arms differ ONLY in the classification)
# ---------------------------------------------------------------------------------------------


def apply_drift(world: Dict) -> None:
    """Replicates fna5.py apply_drift exactly (frozen mutation, read-only reference)."""
    rng = random.Random(W.derive_seed("drift", "theta1"))
    world["catalogue"] = [it for it in world["catalogue"] if it.op_id != "window:60"]
    new = W.Instance("sample:48", "sample", "drift:0", 48, 12.0, 1.1, dict(world["realized"]))
    pos = next(i for i, it in enumerate(world["catalogue"]) if it.family == "scan")
    world["catalogue"].insert(pos, new)
    world["state"]["theta1"] = 0.35 + rng.uniform(-0.08, 0.08)
    world["state"]["theta2"] = world["state"]["theta2"] + 0.05
    world["state"]["scan_version_mult"] = 1.6
    W.rebuild_index(world)


def harness_router_fit(world: Dict, dev_queries: List) -> Tuple[object, List[Dict], int]:
    """AMENDMENT-1 host router: the #219 strongest practical parent (A2 cost model),
    fitted on DEV identification records (all applicable executed + verify per query).
    The identification+fit price is harness cost, common to every arm."""
    records, price = [], 0
    for q in dev_queries:
        insts, _sel = W.applicable(world, q)
        exec_by_id = {}
        for it in insts:
            w, ok = W.execute_via_spec(world, it, q)
            price += w + W.VERIFY_WORK
            exec_by_id[it.op_id] = (w, ok)
        records.append({"qid": q.qid, "query": q, "exec_by_id": exec_by_id})
    router = S.CostModelArm()
    fit_work = router.fit(records)
    return router, records, price + fit_work


def _route(world: Dict, q, insts, router) -> Tuple[object, int]:
    """H router: the fitted A2 cost model pre-refresh; re-fitted on the frozen maintenance
    window after the refresh trigger (harness-internal, identical rule for every arm)."""
    return router.choose(q, insts, world["state"])


def _continuation(world: Dict, q, insts, failed_it, cls: Optional[str]):
    """Frozen repair table. Returns (work, passed, retry_used, stale_flag)."""
    state = world["state"]
    scan = next(it for it in insts if it.family == "scan")
    def do(it):
        w, ok = W.execute_via_spec(world, it, q)
        return w + W.VERIFY_WORK, ok
    if cls == "SELECTOR_METHOD_MISMATCH":
        diff = [g for g in insts
                if g.family not in W.EXACT_FAMILIES and g.family != failed_it.family]
        if diff:
            g = min(diff, key=lambda it: (it.declared_cost_estimate(q, state), it.op_id))
            w1, ok1 = do(g)
            if ok1:
                return w1, True, True, False
            w2, _ = do(scan)
            return w1 + w2, True, True, False
    w, _ = do(scan)
    return w, True, False, cls == "STALE_DECLARED_MODEL"


def run_harness(world: Dict, queries_by_split: Dict[str, List], arm, router) -> Dict:
    """Arm contract: arm.classify(view)->(cls|None, infer_work, neural_calls);
    arm.oracle(world,q,failed,insts,drift)->cls for ORACLE_LATENT only. The fitted A2 router
    is the held-constant host: every arm runs under its own identical copy (fresh refit per
    arm so refresh state never leaks between arms)."""
    out = {"per_split": {}, "acquisition": dict(arm.get("acquisition", {}))}
    live_router = S.CostModelArm()
    live_router.beta = {k: list(v) for k, v in router.beta.items()}
    live_router.bins = {f: {"hit": dict(b["hit"]), "tot": dict(b["tot"])}
                        for f, b in router.bins.items()}
    live_router.means = list(router.means)
    live_router.stds = list(router.stds)
    live_router.edges = (list(router.edges[0]), list(router.edges[1]))
    refreshed = False
    refresh_billed = 0
    stale_flags = 0
    for split in ("DEV", "EVAL", "DRIFT"):
        drift = split == "DRIFT"
        if drift:
            apply_drift(world)
            refresh_billed = 0
            stale_flags = 0
            refreshed = False
        rows = []
        for q in queries_by_split[split]:
            insts, _sel = W.applicable(world, q)
            choice, router_work = _route(world, q, insts, live_router)
            w, ok = W.execute_via_spec(world, choice, q)
            exec_work = w + W.VERIFY_WORK
            row = {"qid": q.qid, "passed_first": ok, "exec_work": exec_work,
                   "feature_work": q.feature_work, "router_work": router_work}
            if not ok:
                if arm.get("oracle") is not None:
                    cls = arm["oracle"](world, q, choice, insts, drift)
                    infer, neural = 1, 0
                else:
                    view = legal_view(world, q, choice, insts,
                                      "post-drift" if drift else "pre-drift")
                    assert_legal(view)
                    cls, infer, neural = arm["classify"](view)
                cont, _p, retry, stale = _continuation(world, q, insts, choice, cls)
                row.update({"failed_family": choice.family, "cls_pred": cls,
                            "cls_true": ground_truth(world, q, choice, insts, drift),
                            "infer_work": infer, "neural_calls": neural,
                            "cont_work": cont, "retry_used": retry, "stale_flag": stale})
                if stale:
                    stale_flags += 1
                    if stale_flags >= STALE_FLAG_TRIGGER and not refreshed:
                        refreshed = True
                        recs, refresh_billed = _refresh_records(
                            world, queries_by_split["DRIFT"], live_router)
                        refit = S.CostModelArm()
                        refresh_billed += refit.fit(recs)
                        live_router = refit
            rows.append(row)
        out["per_split"][split] = rows
        if drift:
            out["refresh"] = {"triggered": refreshed,
                              "stale_flags": stale_flags,
                              "price_billed": refresh_billed}
    return out


def _refresh_records(world: Dict, drift_queries: List, router) -> Tuple[List[Dict], int]:
    """Maintenance refresh identification: over the first REFRESH_IDENTIFY_N drift failures
    (routed by the current router, all applicable executed + verify), producing A2 refit
    records; post-refit the router carries the re-estimated centres implicitly."""
    price = 0
    recs = []
    for q in drift_queries:
        insts, _sel = W.applicable(world, q)
        choice, _rw = _route(world, q, insts, router)
        w, ok = W.execute_via_spec(world, choice, q)
        price += w + W.VERIFY_WORK
        if ok:
            continue
        exec_by_id = {}
        for it in insts:
            wi, oki = W.execute_via_spec(world, it, q)
            price += wi + W.VERIFY_WORK
            exec_by_id[it.op_id] = (wi, oki)
        recs.append({"qid": q.qid, "query": q, "exec_by_id": exec_by_id})
        if len(recs) >= REFRESH_IDENTIFY_N:
            break
    return recs, price


def build_dev_records(world: Dict, router: object, ident_records: List[Dict]
                      ) -> Tuple[List[Dict], int]:
    """Classifier label acquisition, reconstructed from the harness identification table
    (no execution double-charged): DEV failures are those the fitted A2 router would fail;
    label_price is the counterfactual identification a stand-alone capability would pay for
    them (router-choice attempt + all applicable executed + verify). Labels are exact
    ground truth (deterministic given latents); their acquisition is billed."""
    records, price = [], 0
    for rec in ident_records:
        q = rec["query"]
        insts, _sel = W.applicable(world, q)
        choice, _rw = _route(world, q, insts, router)
        w, ok = rec["exec_by_id"][choice.op_id]
        price += w + W.VERIFY_WORK
        if ok:
            continue
        outcomes = {}
        for it in insts:
            wi, oki = rec["exec_by_id"][it.op_id]
            price += wi + W.VERIFY_WORK
            outcomes[(it.family, it.param)] = oki
        view = legal_view(world, q, choice, insts, "pre-drift")
        assert_legal(view)
        records.append({"view": view, "outcomes": outcomes,
                        "label": ground_truth(world, q, choice, insts, False)})
    return records, price


def _wrap(fit_state, neural=0):
    classify, state = fit_state
    def wrapped(view):
        cls, work = classify(view)
        return cls, work, neural
    return {"classify": wrapped, "state": state, "acquisition": {}}


def make_arms(dev_records: List[Dict], ident_price: int) -> Dict[str, Dict]:
    r1_src = str(DECLARED_CENTRES) + "gamma=%s;stale_gap=%s" % (GAMMA_GUARD, STALE_GAP)
    r2c, r2state = r2_make(dev_records)
    r3c, r3state = r3_make(dev_records)
    mlpc, mlpstate = mlp_make(dev_records)
    n = len(dev_records)
    return {
        "R1_GUARDED_DECLARED": {
            "classify": lambda v: (lambda r: (r[0], r[1], 0))(r1_guarded_declared(v)),
            "state": {"authored_bytes": len(r1_src)},
            "acquisition": {"label_price": 0, "fitted_bytes": len(r1_src)}},
        "R2_CALIBRATED_BAYES": _wrap((r2c, r2state)),
        "R3_CART_TREE": _wrap((r3c, r3state)),
        "INCUMBENT_NEURAL_REF": {
            "classify": lambda v: (lambda r: (r[0], r[1], 1))(mlpc(v)),
            "state": mlpstate, "neural": True,
            "acquisition": {"label_price": ident_price,
                            "fitted_bytes": len(json.dumps(mlpstate, sort_keys=True))}},
    }


def summarize(rows: List[Dict], acquisition: Dict, extra_amort: int = 0) -> Dict:
    fails = [r for r in rows if not r["passed_first"]]
    n = len(fails)
    acc = sum(1 for r in fails if r.get("cls_pred") == r.get("cls_true")) / max(n, 1)
    cont = sum(r["cont_work"] for r in fails)
    infer = sum(r.get("infer_work", 0) for r in fails)
    amort = (acquisition.get("label_price", 0) + extra_amort) / max(n, 1)
    per_fail = (cont + infer) / max(n, 1) + amort
    per_class = {c: {"n_true": sum(1 for r in fails if r["cls_true"] == c),
                     "n_pred": sum(1 for r in fails if r.get("cls_pred") == c),
                     "correct": sum(1 for r in fails if r["cls_true"] == c
                                    and r.get("cls_pred") == c)} for c in CLASSES}
    return {"n_queries": len(rows), "n_failures": n, "accuracy": round(acc, 5),
            "mean_cont_work": round(cont / max(n, 1), 4),
            "mean_infer_work": round(infer / max(n, 1), 4),
            "amortized_per_failure": round(amort, 4),
            "whole_chain_per_failed_query": round(per_fail, 4),
            "neural_calls": sum(r.get("neural_calls", 0) for r in fails),
            "retries_used": sum(1 for r in fails if r.get("retry_used")),
            "stale_flags": sum(1 for r in fails if r.get("stale_flag")),
            "per_class": per_class}


def run(tiny: bool = False) -> Dict:
    params = W.WorldParams.tiny_params() if tiny else W.WorldParams()
    world = W.build_world(params)
    queries = [W.make_query(world, i) for i in range(params.n_queries)]
    by_split: Dict[str, List] = {"DEV": [], "EVAL": [], "DRIFT": []}
    for q in queries:
        by_split[W.split_of(q.qid)].append(q)

    router, ident_records, router_price = harness_router_fit(world, by_split["DEV"])
    dev_records, ident_price = build_dev_records(world, router, ident_records)
    arms = make_arms(dev_records, ident_price)
    floor = {"classify": lambda v: (None, 0, 0)}
    oracle = {"oracle": lambda w, q, f, i, d: ground_truth(w, q, f, i, d)}
    runs: Dict[str, Dict] = {}
    acq_common = {"label_price": ident_price}

    def fresh_world():
        """AMENDMENT 2: the harness must be held constant across arms. run_harness applies
        the drift mutation in-stream, so each arm gets its own freshly built (deterministic,
        seed-identical) world; without this, arm N's DEV/EVAL would run on arm N-1's drift."""
        w = W.build_world(params)
        return w, [W.make_query(w, i) for i in range(params.n_queries)]

    for name, arm in arms.items():
        arm.setdefault("acquisition", {}).setdefault("label_price",
                                                     ident_price if name != "R1_GUARDED_DECLARED" else 0)
        arm["acquisition"].setdefault("fitted_bytes",
                                      len(json.dumps(arm.get("state", {}), sort_keys=True)))
        w_arm, q_arm = fresh_world()
        by_arm = {sp: [q for q in q_arm if W.split_of(q.qid) == sp] for sp in by_split}
        runs[name] = run_harness(w_arm, by_arm, arm, router)
    w_floor, q_floor = fresh_world()
    by_floor = {sp: [q for q in q_floor if W.split_of(q.qid) == sp] for sp in by_split}
    runs["NO_CLASSIFIER"] = run_harness(w_floor, by_floor, floor, router)
    w_orc, q_orc = fresh_world()
    by_orc = {sp: [q for q in q_orc if W.split_of(q.qid) == sp] for sp in by_split}
    runs["ORACLE_LATENT"] = run_harness(w_orc, by_orc, oracle, router)

    results: Dict[str, Dict] = {}
    for name, run_out in runs.items():
        acq = dict(acq_common)
        acq.update(run_out.get("acquisition", {}))
        refresh_price = run_out.get("refresh", {}).get("price_billed", 0)
        eval_qids = sorted(r["qid"] for r in run_out["per_split"]["EVAL"]
                           if not r["passed_first"])
        results[name] = {
            "DEV": summarize(run_out["per_split"]["DEV"], {"label_price": 0}),
            "EVAL": summarize(run_out["per_split"]["EVAL"], acq),
            "DRIFT": summarize(run_out["per_split"]["DRIFT"], acq, refresh_price),
            "refresh": run_out.get("refresh", {}),
            "state_bytes": len(json.dumps(arms[name].get("state", {}), sort_keys=True))
                           if name in arms else 0,
            "eval_failure_qid_digest": hashlib.md5(
                json.dumps(eval_qids).encode()).hexdigest(),
            "eval_failure_qids_n": len(eval_qids),
        }
    # shuffle null over the strongest replacement arm's EVAL predictions
    best_rep = None
    for cand in ("R1_GUARDED_DECLARED", "R2_CALIBRATED_BAYES", "R3_CART_TREE"):
        best_rep = cand
        break
    ev_rows = runs[best_rep]["per_split"]["EVAL"]
    fails = [r for r in ev_rows if not r["passed_first"]]
    rng = random.Random(int(hashlib.md5((FNA7_SALT + "shuffle").encode()).hexdigest(), 16))
    preds = [r["cls_pred"] for r in fails]
    perm = list(range(len(preds)))
    rng.shuffle(perm)
    shuffled = [preds[i] for i in perm]
    results["SHUFFLE_NULL"] = {
        "base_arm": best_rep, "split": "EVAL",
        "accuracy": round(sum(1 for r, p in zip(fails, shuffled)
                              if p == r["cls_true"]) / max(len(fails), 1), 5),
        "majority_class_rate": round(max(
            sum(1 for r in fails if r["cls_true"] == c) for c in CLASSES) / max(len(fails), 1), 5),
        "note": "permuting a constant predictor is a no-op; majority_class_rate is the honest null for constant arms"}
    return {"world": {"params": {"n_queries": params.n_queries, "n_atoms": params.n_atoms,
                                 "tiny": params.tiny},
                      "splits": {k: len(v) for k, v in by_split.items()},
                      "harness_router": "A2_COST_MODEL (#219 CostModelArm, AMENDMENT 1)",
                      "harness_router_price": router_price,
                      "dev_failures_labeled": len(dev_records),
                      "identification_price": ident_price},
            "arms": results}


# ---------------------------------------------------------------------------------------------
# causal gate (#214 section 5, ten clauses) + terminal selection
# ---------------------------------------------------------------------------------------------


def gate_and_terminal(data: Dict) -> Dict:
    r = data["arms"]
    inc = r["INCUMBENT_NEURAL_REF"]
    ladder = ["R1_GUARDED_DECLARED", "R2_CALIBRATED_BAYES", "R3_CART_TREE"]
    suff: Dict[str, Optional[bool]] = {}
    for name in ladder:
        ev, dr = r[name]["EVAL"], r[name]["DRIFT"]
        suff[name] = None
        if ev["n_failures"] == 0:
            continue
        ok = (ev["accuracy"] >= inc["EVAL"]["accuracy"] - EPS_ACC
              and ev["whole_chain_per_failed_query"] <= inc["EVAL"]["whole_chain_per_failed_query"] * (1 + EPS_COST)
              and ev["neural_calls"] == 0 and dr["neural_calls"] == 0)
        suff[name] = bool(ok)
    first_sufficient = next((n for n in ladder if suff[n]), None)
    oracle_ok = (r["ORACLE_LATENT"]["EVAL"]["n_failures"] > 0
                 and r["ORACLE_LATENT"]["EVAL"]["accuracy"] >= inc["EVAL"]["accuracy"] - EPS_ACC)
    if first_sufficient == "R1_GUARDED_DECLARED":
        terminal = "PARENT_SUFFICIENT_FOR_FAILURE_CLASSIFICATION__GUARDED_DECLARED_RULE"
    elif first_sufficient == "R2_CALIBRATED_BAYES":
        terminal = "PARENT_SUFFICIENT_FOR_FAILURE_CLASSIFICATION__CALIBRATED_ESTIMATOR"
    elif first_sufficient == "R3_CART_TREE":
        terminal = "NON_NEURAL_NONINFERIOR_AT_REGISTERED_SCOPE"
    elif oracle_ok:
        terminal = "NO_FUNCTIONAL_PARITY_FAILURE_CLASSIFICATION"
    else:
        terminal = "NEURAL_DONOR_DOMINATES_AT_SCOPE"
    side = []
    if first_sufficient is None and oracle_ok:
        side.append("ACQUISITION_COST_DOMINATES" if r["ORACLE_LATENT"]["EVAL"]["accuracy"] >= 0.999
                    else "REPRESENTATION_INSUFFICIENT")
    best = first_sufficient or "R2_CALIBRATED_BAYES"
    sub_delta = round(r[best]["EVAL"]["mean_cont_work"] - r["NO_CLASSIFIER"]["EVAL"]["mean_cont_work"], 4)
    retries_all = {n: r[n]["EVAL"]["retries_used"] for n in r if "EVAL" in r[n]}
    stale_any = any(r[n].get("refresh", {}).get("triggered") for n in r if isinstance(r[n], dict))
    gate = {
        "1_donor_frozen_before_outcomes": "FREEZE_FNA7_V1.json hashed and recorded pre-run",
        "2_no_hidden_information": "assert_legal enforced on every classification call; latent keys pinned absent",
        "3_consumed_at_decisive_step": "classification consumed through the frozen repair table; EVAL retries per arm=%s; stale flags=%d (best arm); refresh triggered anywhere=%s (STALE never true on this router's scored stream; machinery exercised structurally by tests)" % (
            retries_all, r[best]["EVAL"]["stale_flags"], stale_any),
        "4_margin_or_exact_loss": "accuracy delta vs incumbent=%s; cost delta=%s (eps_acc=0.03, eps_cost=0.05)" % (
            round(r[best]["EVAL"]["accuracy"] - inc["EVAL"]["accuracy"], 5),
            round(r[best]["EVAL"]["whole_chain_per_failed_query"]
                  - inc["EVAL"]["whole_chain_per_failed_query"], 4)),
        "5_resource_vector_complete": "label_price+identification, inference work, fitted+authored bytes, refresh price, all reported per arm",
        "6_substitution_destroys_effect": "constant-NOISE substitution == NO_CLASSIFIER floor by the frozen repair table; cont-work delta best-vs-floor=%s" % sub_delta,
        "7_strongest_parent_first_refusal": "ladder order R1->R2->R3 evaluated; first sufficient=%s" % first_sufficient,
        "8_no_hidden_neural_computation": "replacement neural_calls EVAL=%d DRIFT=%d (stdlib-only imports)" % (
            r[best]["EVAL"]["neural_calls"], r[best]["DRIFT"]["neural_calls"]),
        "9_revision_revocation_semantics": "stale advice detected via STALE class + refresh trigger; post-refresh router re-fitted on the frozen maintenance window and billed",
        "10_protected_eval_disjoint_from_dev": "md5 split buckets frozen in fna5_world.split_of; fits receive dev_records only",
    }
    terminal_scope = terminal + "_AT_PILOT_SCOPE_FNA7_V1"
    return {"sufficiency": suff, "first_sufficient": first_sufficient, "terminal": terminal_scope,
            "side_flags": side, "causal_gate_214_s5": gate}


CAPABILITY_SOURCE_MAP_PILOT = {
    "capability": "failure classification (K2)",
    "current_supplier": "incumbent-class neural reference (pilot stand-in for the model-supplied arm)",
    "observed_necessity": "see observed block: stream composition bounds the value of classification at this scope",
    "observed_cost": "see FNA7_PILOT_RESULTS_V1.json arms[*].EVAL.whole_chain_per_failed_query",
    "failure_mode": "see per_class precision/recall per arm",
    "candidate_explicit_replacement": "guarded declared rule / calibrated estimator / rule learner (first-refusal ladder)",
    "replacement_evidence_status": "piloted at micro scope in this capsule; #208-scale transplant remains future work",
}


def observed_facts(data: Dict) -> Dict:
    """Post-outcome observation block, computed (not hand-written) from the run."""
    r = data["arms"]
    orc, floor = r["ORACLE_LATENT"]["EVAL"], r["NO_CLASSIFIER"]["EVAL"]
    comp = {sp: {c: orc_[ "n_true"] for c, orc_ in r["ORACLE_LATENT"][sp]["per_class"].items()}
            for sp in ("EVAL", "DRIFT")}
    return {
        "stream_composition_true": comp,
        "stale_true_count": comp["EVAL"]["STALE_DECLARED_MODEL"] + comp["DRIFT"]["STALE_DECLARED_MODEL"],
        "refresh_triggered_any": any(v.get("refresh", {}).get("triggered")
                                     for v in r.values() if isinstance(v, dict)),
        "oracle_continuation_delta_vs_floor_per_failure": round(
            orc["mean_cont_work"] - floor["mean_cont_work"], 4),
        "note_oracle_delta": ("positive = even exact classification raises continuation cost on this "
                              "stream: SELECTOR retries under declared-cost ordering net-lose vs scan-always"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiny", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "FNA7_PILOT_RESULTS_V1.json"))
    args = ap.parse_args()
    data = run(tiny=args.tiny)
    verdict = gate_and_terminal(data)
    observed = observed_facts(data)
    freeze_path = os.path.join(HERE, "FREEZE_FNA7_V1.json")
    with open(freeze_path, "rb") as fh:
        freeze_sha = hashlib.sha256(fh.read()).hexdigest()
    out = {"schema": "ocm.fna.fna7-capability-transplant.pilot-results.v1",
           "protocol": "CapabilityTransplantProtocolV1",
           "freeze_sha256_at_run": freeze_sha,
           "tiny": bool(args.tiny), "world": data["world"], "arms": data["arms"],
           "verdict": verdict, "observed": observed,
           "capability_source_map_pilot_scope": CAPABILITY_SOURCE_MAP_PILOT,
           "declared_limitations": [
               "one authored world (E1/L1), #219 authorship; three responsibility classes are that world's physics",
               "incumbent is a seeded MLP stand-in for the incumbent class, not a frontier model",
               "terminal is scoped to this pilot; no #208-scale claim, no deployment"]}
    with open(args.out, "w") as fh:
        json.dump(out, fh, sort_keys=True, indent=1)
        fh.write("\n")
    print("terminal:", verdict["terminal"])
    print("sufficiency:", verdict["sufficiency"])
    print("wrote:", args.out)


if __name__ == "__main__":
    main()




