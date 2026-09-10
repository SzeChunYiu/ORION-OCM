"""GS ensemble surrogate for promotion allocation (#221 sec 18 GS-R0, P10
parent).  SEARCH-SIDE ONLY: it ranks promotions between tiers; it is never
an OCM component (#71), never substitutes for an exact evaluation, and
surrogate predictions NEVER count as earned capability (every promoted
candidate is exactly evaluated at the next tier).

Ensemble (stdlib-only so it runs identically on every host):
  * kNN member: distance-weighted regression over normalized genome
    feature vectors (k = 7, frozen).
  * bagged decision-stump-tree members: bootstrap + random-subspace,
    depth-2 greedy MSE splits (n_trees = 24, frozen).

Two heads:
  * viability head: P(viable at T0) — ensemble fraction voting viable
    (classification view of completed T0 evals).
  * score head: predicted T1 dev_score — regression view of completed
    T1 evals (dev_score is the frozen tier-referenced scalar used by the
    zoo for COST accounting comparisons; used here ONLY to order
    promotions, never as a result).
"""
from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from morphology.direct_genome import operators_for
from morphology.schema import (
    EXECUTIVE_FAMILIES, FIELD_FAMILIES, LEARNING_FAMILIES, MEMORY_FAMILIES,
    OPERATORS, REVISION_FAMILIES, TOPOLOGY_FAMILIES, UNIT_TYPES)

# Frozen surrogate hyperparameters (recorded in GRAND_SEARCH_R1_FREEZE.json)
GS_SUR_K = 7
GS_SUR_TREES = 24
GS_SUR_DEPTH = 2
GS_SUR_SUBSPACE = 12
SURROGATE_ID = "GS_ENSEMBLE_SURROGATE_V2"

# Reuse-first (#221 sec 2a): when scikit-learn is importable the tree heads
# are sklearn HistGradientBoosting models (library defaults, random_state
# pinned for reproducibility — the only knob we set); the stdlib stump
# ensemble below remains the fallback.  WHICH impl runs is pinned by the
# freeze via the LUNARC env probe, never ambient.


def _sklearn_heads(seed: int):
    from sklearn.ensemble import (HistGradientBoostingClassifier,
                                  HistGradientBoostingRegressor)
    return (HistGradientBoostingClassifier(random_state=seed),
            HistGradientBoostingRegressor(random_state=seed + 1))

_FEATS: List[Tuple[str, str]] = (
    [("F", f) for f in FIELD_FAMILIES]
    + [("U", u) for u in UNIT_TYPES]
    + [("T", t) for t in TOPOLOGY_FAMILIES]
    + [("Pi", p) for p in EXECUTIVE_FAMILIES]
    + [("L", l) for l in LEARNING_FAMILIES]
    + [("R", r) for r in REVISION_FAMILIES]
    + [("K", k) for k in MEMORY_FAMILIES]
    + [("O", o) for o in sorted(OPERATORS)])
_FEAT_INDEX = {name: i for i, (pfx, name) in enumerate(_FEATS)}


def genome_feature_vector(g) -> List[float]:
    """Deterministic genome descriptor: 0/1 language one-hots + counts.
    Dimension = 10 + 13 + 8 + 7 + 9 + 3 + 6 + |operator language|."""
    v = [0.0] * len(_FEATS)
    v[_FEAT_INDEX[g.F_arch]] = 1.0
    n_units = max(1, len(g.U))
    for u in g.U:
        v[_FEAT_INDEX[u.unit_type]] += 1.0 / n_units
    v[_FEAT_INDEX[g.T_family]] = 1.0
    v[_FEAT_INDEX[g.Pi_arch]] = 1.0
    v[_FEAT_INDEX[g.L]] = 1.0
    v[_FEAT_INDEX[g.R]] = 1.0
    v[_FEAT_INDEX[g.K]] = 1.0
    for op in operators_for([u.unit_type for u in g.U], g.L, g.K, g.R):
        if op in _FEAT_INDEX:
            v[_FEAT_INDEX[op]] = 1.0
    return v


def _dist2(a: Sequence[float], b: Sequence[float]) -> float:
    return sum((x - y) * (x - y) for x, y in zip(a, b))


class _StumpTree:
    """Depth-2 greedy regression tree on a random feature subspace."""

    def __init__(self, feats: List[int], rng: random.Random) -> None:
        self.feats = feats          # candidate feature indices
        self.rng = rng
        self.rules: List[Tuple[int, float, int, int]] = []  # (feat, thr, L, R)
        self.leaf_value = [0.0]

    def fit(self, X: List[List[float]], y: List[float]) -> "_StumpTree":
        self._build(0, X, y, 0)
        self._flat()
        return self

    def _build(self, node: int, X: List[List[float]], y: List[float],
               depth: int) -> float:
        if not X or depth >= GS_SUR_DEPTH:
            val = sum(y) / max(1, len(y))
            self.leaf_value[node] = val
            return val
        best: Optional[Tuple[float, int, float]] = None
        my = sum(y) / len(y)
        sse0 = sum((t - my) ** 2 for t in y)
        for fi in self.feats:
            vals = sorted({row[fi] for row in X})
            for thr in vals:
                L = [(row, t) for row, t in zip(X, y) if row[fi] <= thr]
                R = [(row, t) for row, t in zip(X, y) if row[fi] > thr]
                if not L or not R:
                    continue
                ml = sum(t for _, t in L) / len(L)
                mr = sum(t for _, t in R) / len(R)
                sse = (sum((t - ml) ** 2 for _, t in L)
                       + sum((t - mr) ** 2 for _, t in R))
                if best is None or sse < best[0]:
                    best = (sse, fi, thr)
        if best is None or best[0] >= sse0 - 1e-12:
            self.leaf_value[node] = my
            return my
        _, fi, thr = best
        LX = [row for row in X if row[fi] <= thr]
        Ly = [t for row, t in zip(X, y) if row[fi] <= thr]
        RX = [row for row in X if row[fi] > thr]
        Ry = [t for row, t in zip(X, y) if row[fi] > thr]
        while len(self.leaf_value) < 4 * node + 4:
            self.leaf_value.append(0.0)
        self.rules.append((fi, thr, node, 1))
        self.leaf_value[node] = float("nan")  # internal marker
        self._build(2 * node + 1, LX, Ly, depth + 1)
        self.rules[-1] = (fi, thr, node, 2)
        self._build(2 * node + 2, RX, Ry, depth + 1)
        return 0.0

    def _flat(self) -> None:
        # collapse rules into a dict for prediction
        self.split: Dict[int, Tuple[int, float]] = {
            node: (fi, thr) for fi, thr, node, _ in self.rules}

    def predict(self, x: Sequence[float]) -> float:
        node = 0
        depth = 0
        while node in self.split and depth < GS_SUR_DEPTH:
            fi, thr = self.split[node]
            node = 2 * node + (1 if x[fi] <= thr else 2)
            depth += 1
        return self.leaf_value[node] if node < len(self.leaf_value) else 0.0


class EnsembleSurrogate:
    """Two heads (P(viable@T0), predicted T1 score).  impl="sklearn" uses
    HistGradientBoosting heads (reuse-first); impl="builtin" uses the kNN +
    bagged stump ensemble.  The impl is pinned by the freeze."""

    def __init__(self, seed: int = 0, impl: str = "builtin") -> None:
        self.seed = seed
        self.impl = impl
        self.X: List[List[float]] = []
        self.y_viable: List[float] = []      # 1.0 / 0.0 from completed T0
        self.y_t1: List[Tuple[List[float], float]] = []  # (x, T1 dev_score)
        self.trees_v: List[_StumpTree] = []
        self.trees_s: List[_StumpTree] = []
        self.clf = None
        self.reg = None
        if impl == "sklearn":
            self.clf, self.reg = _sklearn_heads(seed)
        elif impl != "builtin":
            raise ValueError("unknown surrogate impl %r" % impl)
        self.stats: Dict[str, Any] = {"surrogate_id": SURROGATE_ID,
                                      "surrogate_impl": impl,
                                      "n_train_t0": 0, "n_train_t1": 0,
                                      "holdout_mae_t1": None}

    # ---------------------------------------------------------------- train
    def train_t0(self, records: Sequence[Dict[str, Any]]) -> None:
        """records: completed T0 evaluation records (feasible + failed)."""
        for r in records:
            self.X.append(genome_feature_vector(
                _genome(r)))
            self.y_viable.append(1.0 if r.get("feasible") else 0.0)
        rng = random.Random(self.seed)
        if self.impl == "sklearn" and len(self.X) >= 16 and \
                len(set(self.y_viable)) >= 2:
            self.clf, _ = _sklearn_heads(self.seed)
            self.clf.fit(self.X, self.y_viable)
        elif len(self.X) >= 16:
            self.trees_v = [
                _StumpTree(self._subspace(rng), rng).fit(
                    *_bootstrap(self.X, self.y_viable, rng))
                for _ in range(GS_SUR_TREES)]
        self.stats["n_train_t0"] = len(self.X)

    def train_t1(self, pairs: Sequence[Tuple[Any, float]]) -> None:
        """pairs: (genome, T1 dev_score) from COMPLETED T1 evaluations."""
        X = [genome_feature_vector(g) for g, _ in pairs]
        y = [float(s) for _, s in pairs]
        rng = random.Random(self.seed + 1)
        if len(X) >= 16:
            # honest holdout MAE when there is enough data
            if len(X) >= 64:
                h = rng.sample(range(len(X)), len(X) // 4)
                hset = set(h)
                trX = [X[i] for i in range(len(X)) if i not in hset]
                trY = [y[i] for i in range(len(X)) if i not in hset]
                hold_trees = [
                    _StumpTree(self._subspace(rng), rng).fit(
                        *_bootstrap(trX, trY, rng))
                    for _ in range(GS_SUR_TREES)]
                errs = [abs(self._tree_vote(hold_trees, X[i]) - y[i])
                        for i in h]
                self.stats["holdout_mae_t1"] = round(
                    sum(errs) / len(errs), 6)
            if self.impl == "sklearn":
                _, self.reg = _sklearn_heads(self.seed)
                self.reg.fit(X, y)
            else:
                self.trees_s = [
                    _StumpTree(self._subspace(rng), rng).fit(
                        *_bootstrap(X, y, rng))
                    for _ in range(GS_SUR_TREES)]
            self.y_t1 = list(zip(X, y))
        self.stats["n_train_t1"] = max(self.stats["n_train_t1"],
                                       len(X))

    def _subspace(self, rng: random.Random) -> List[int]:
        d = len(self.X[0]) if self.X else len(_FEATS)
        return rng.sample(range(d), min(GS_SUR_SUBSPACE, d))

    # ------------------------------------------------------------ predict
    def _knn(self, x: Sequence[float], ys: Sequence[float]) -> float:
        if not self.X:
            return 0.5 if not ys else sum(ys) / len(ys)
        ds = sorted(((_dist2(x, xi), yi) for xi, yi in zip(self.X, ys)),
                    key=lambda t: t[0])
        take = ds[: min(GS_SUR_K, len(ds))]
        num = sum(yi / (d + 1e-9) for d, yi in take)
        den = sum(1.0 / (d + 1e-9) for d, _ in take)
        return num / den if den else 0.0

    def _tree_vote(self, trees: Sequence[_StumpTree],
                   x: Sequence[float]) -> float:
        if not trees:
            return 0.0
        return sum(t.predict(x) for t in trees) / len(trees)

    def p_viable(self, g) -> float:
        x = genome_feature_vector(g)
        if self.impl == "sklearn" and self.clf is not None and \
                hasattr(self.clf, "classes_"):
            return float(min(1.0, max(0.0, self.clf.predict_proba([x])[0][1])))
        pk = self._knn(x, self.y_viable)
        pt = self._tree_vote(self.trees_v, x)
        if self.trees_v:
            return 0.5 * (min(1.0, max(0.0, pk)) + min(1.0, max(0.0, pt)))
        return min(1.0, max(0.0, pk))

    def predicted_t1_score(self, g) -> float:
        x = genome_feature_vector(g)
        if self.impl == "sklearn" and self.reg is not None and \
                hasattr(self.reg, "n_iter_"):
            return float(self.reg.predict([x])[0])
        ys = [y for _, y in self.y_t1]
        pk = self._knn(x, ys) if ys else 0.0
        pt = self._tree_vote(self.trees_s, x)
        return 0.5 * (pk + pt) if (ys and self.trees_s) else (pt or pk)

    def allocation_score(self, g) -> float:
        """Promotion rank key: expected value of the T1 score among
        predicted-viable candidates (P(viable) x predicted score)."""
        return self.p_viable(g) * max(0.0, self.predicted_t1_score(g))


def rank_promotions(candidates: Sequence[Any], surrogate: EnsembleSurrogate,
                    n: int) -> List[Any]:
    """Order candidates by surrogate allocation score; top-n ONLY — this
    never marks anyone viable, never substitutes an exact evaluation, and
    is used exclusively to choose which viable candidates earn T1/T2
    evaluations next."""
    ordered = sorted(candidates,
                     key=lambda g: -surrogate.allocation_score(g))
    return ordered[: max(0, n)]


def _bootstrap(X: List[List[float]], y: List[float],
               rng: random.Random) -> Tuple[List[List[float]], List[float]]:
    idx = [rng.randrange(len(X)) for _ in range(len(X))]
    return [X[i] for i in idx], [y[i] for i in idx]


def _genome(rec: Dict[str, Any]):
    from morphology.schema import OCMMorphologyGenomeV1
    return OCMMorphologyGenomeV1.from_json_obj(rec["genome"])
