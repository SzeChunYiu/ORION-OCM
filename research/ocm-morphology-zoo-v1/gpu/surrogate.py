"""Search-side ensemble surrogate for the GS GPU lane (#221 sec 18, worker O).

Search-side ONLY (zoo #71 / sec 7 P10 constraint): this surrogate NEVER
counts as earned capability, never enters an OCM organism, and its
predictions are used only to RANK promotions — every promoted candidate is
re-evaluated exactly.  Exact reevaluation is the ground truth; the
surrogate is a ranking accelerator.

Members (all optional, detected at import — py3.8..3.14 hosts differ):
  * ridge_stdlib   — closed-form ridge regression solved by pure-python
                     Gaussian elimination with partial pivoting (bit-stable,
                     no dependencies; runs on billy-old py3.14 without numpy)
  * extra_trees    — sklearn ExtraTreesRegressor (random_state frozen)
  * grad_boost     — sklearn GradientBoostingRegressor (random_state frozen)
  * torch_mlp      — torch MLP on CUDA when present else CPU,
                     torch.manual_seed(seed), fp64, full-batch Adam
Ensemble prediction = RANK-AVERAGE of member predictions (robust to member
scale/offset).  Calibration = stdlib Spearman rho per member and for the
ensemble on a held-out split; recorded in the stamp, never overwritten.

Determinism: the stdlib member is bit-deterministic everywhere; sklearn
members are deterministic per (version, random_state) — the version is
stamped; the torch member is deterministic per (version, device, seed) —
torch.use_deterministic_algorithms(True) is requested when available.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Sequence, Tuple

SURROGATE_SEED = 2210  # frozen; every member derives its own seed from it
RIDGE_LAMBDA = 1.0     # frozen L2 prior (charged as surrogate complexity)
TORCH_EPOCHS = 400
TORCH_LR = 1e-3

try:  # optional accelerators — NEVER required
    import sklearn as _sk
    from sklearn.ensemble import (ExtraTreesRegressor as _ExtraTrees,
                                  GradientBoostingRegressor as _GradBoost)
    _SK_VERSION = _sk.__version__
except Exception:  # pragma: no cover - host dependent
    _ExtraTrees = None  # type: ignore
    _GradBoost = None  # type: ignore
    _SK_VERSION = None

try:
    import torch as _torch
    _TORCH_VERSION = _torch.__version__
except Exception:  # pragma: no cover - host dependent
    _torch = None  # type: ignore
    _TORCH_VERSION = None


# ------------------------------------------------------------- rank helpers
def rankdata_average(xs: Sequence[float]) -> List[float]:
    """Average ranks (1..n), ties get their mean rank. Pure stdlib."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman_rho(a: Sequence[float], b: Sequence[float]) -> float:
    """Spearman rank correlation, pure stdlib (ties via average ranks)."""
    n = len(a)
    if n < 2 or len(b) != n:
        return 0.0
    ra, rb = rankdata_average(a), rankdata_average(b)
    ma = sum(ra) / n
    mb = sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    if da <= 0.0 or db <= 0.0:
        return 0.0
    return num / (da * db)


# ------------------------------------------------- stdlib ridge (always on)
def _standardize(X: Sequence[Sequence[float]]) -> Tuple[List[List[float]],
                                                        List[float], List[float]]:
    d = len(X[0]) if X else 0
    means = [sum(row[j] for row in X) / len(X) for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((row[j] - means[j]) ** 2 for row in X) / len(X)
        stds.append(math.sqrt(var) if var > 0 else 1.0)
    Z = [[(row[j] - means[j]) / stds[j] for j in range(d)] for row in X]
    return Z, means, stds


def _solve_symmetric(A: List[List[float]], b: List[float]) -> List[float]:
    """Gaussian elimination with partial pivoting (pure python, stable)."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            continue
        M[col], M[piv] = M[piv], M[col]
        inv = 1.0 / M[col][col]
        for r in range(col + 1, n):
            f = M[r][col] * inv
            if f != 0.0:
                for c in range(col, n + 1):
                    M[r][c] -= f * M[col][c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][c] * x[c] for c in range(r + 1, n))
        x[r] = s / M[r][r] if abs(M[r][r]) > 1e-12 else 0.0
    return x


class RidgeStdlib:
    """Closed-form ridge on standardized inputs + bias column."""

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[float]) -> None:
        Z, self.means, self.stds = _standardize(X)
        d = len(Z[0])
        Zb = [row + [1.0] for row in Z]
        A = [[0.0] * (d + 1) for _ in range(d + 1)]
        for row in Zb:
            for i in range(d + 1):
                for j in range(i, d + 1):
                    A[i][j] += row[i] * row[j]
        for i in range(d + 1):
            for j in range(i):
                A[i][j] = A[j][i]
        for i in range(d):
            A[i][i] += RIDGE_LAMBDA
        b = [sum(row[i] * t for row, t in zip(Zb, y)) for i in range(d + 1)]
        self.w = _solve_symmetric(A, b)

    def predict(self, X: Sequence[Sequence[float]]) -> List[float]:
        return [sum((row[j] - self.means[j]) / self.stds[j] * self.w[j]
                    for j in range(len(self.means)))
                + self.w[-1] for row in X]


# --------------------------------------------------------- torch MLP member
class TorchMLP:
    """fp64 MLP, full-batch Adam, manual_seed frozen; CUDA when present."""

    def __init__(self, seed: int = SURROGATE_SEED + 2) -> None:
        self.seed = seed
        self.device = "cuda" if _torch.cuda.is_available() else "cpu"

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[float]) -> None:
        d = len(X[0])
        t = _torch
        # cuBLAS GEMM determinism on cuda needs this env var set BEFORE the
        # cublas handle is created, else F.linear raises under
        # use_deterministic_algorithms (LUNARC A40 probe, job 3587276)
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        t.manual_seed(self.seed)
        if hasattr(t, "use_deterministic_algorithms"):
            try:
                t.use_deterministic_algorithms(True)
            except Exception:
                pass
        hidden = 32 if len(X) < 2000 else 64
        self.model = t.nn.Sequential(
            t.nn.Linear(d, hidden), t.nn.Tanh(),
            t.nn.Linear(hidden, hidden // 2), t.nn.Tanh(),
            t.nn.Linear(hidden // 2, 1)).double().to(self.device)
        Xt = t.tensor(X, dtype=t.float64, device=self.device)
        yt = t.tensor([[v] for v in y], dtype=t.float64, device=self.device)
        mu = Xt.mean(dim=0, keepdim=True)
        sd = Xt.std(dim=0, keepdim=True).clamp_min(1e-9)
        Xt = (Xt - mu) / sd
        opt = t.optim.Adam(self.model.parameters(), lr=TORCH_LR)
        self.model.train()
        for _ in range(TORCH_EPOCHS):
            opt.zero_grad()
            loss = t.nn.functional.mse_loss(self.model(Xt), yt)
            loss.backward()
            opt.step()
        self.model.eval()
        self._mu, self._sd = mu, sd

    def predict(self, X: Sequence[Sequence[float]]) -> List[float]:
        t = _torch
        with t.no_grad():
            Xt = t.tensor(X, dtype=t.float64, device=self.device)
            Xt = (Xt - self._mu) / self._sd
            out = self.model(Xt).squeeze(-1).tolist()
        return [float(v) for v in out]


# ------------------------------------------------------------ the ensemble
class SurrogateEnsemble:
    """Rank-average of all available members; exact reeval is ground truth."""

    def __init__(self, seed: int = SURROGATE_SEED,
                 use_torch: bool = True, use_sklearn: bool = True) -> None:
        self.seed = seed
        self.members: Dict[str, Any] = {}
        self.stamp: Dict[str, Any] = {"seed": seed, "members": [],
                                      "sklearn_version": _SK_VERSION,
                                      "torch_version": _TORCH_VERSION,
                                      "n_train": 0, "calibration": None,
                                      "trained": False}
        if use_sklearn and _ExtraTrees is not None:
            self.members["extra_trees"] = _ExtraTrees(
                n_estimators=64, random_state=seed + 1)
        if use_sklearn and _GradBoost is not None:
            self.members["grad_boost"] = _GradBoost(
                n_estimators=100, random_state=seed + 2)
        if use_torch and _torch is not None:
            self.members["torch_mlp"] = TorchMLP(seed + 3)
        # always present — guarantees a trainable surrogate on every host
        self.members["ridge_stdlib"] = RidgeStdlib()

    def fit(self, X: Sequence[Sequence[float]], y: Sequence[float]) -> Dict[str, Any]:
        X = [[float(v) for v in row] for row in X]
        y = [float(v) for v in y]
        fitted = []
        # iterate a SNAPSHOT: the handler pops the failed member out of
        # self.members, which would otherwise raise "dictionary changed
        # size during iteration" and kill the lane (LUNARC job 3587248)
        for name, m in list(self.members.items()):
            try:
                m.fit(X, y)
                fitted.append(name)
            except Exception as exc:  # member failure never kills the lane
                self.members.pop(name, None)
                self.stamp.setdefault("member_failures", []).append(
                    "%s:%s" % (name, type(exc).__name__))
        self.stamp.update({"members": fitted, "n_train": len(y),
                           "trained": True})
        return dict(self.stamp)

    def predict_member(self, name: str, X: Sequence[Sequence[float]]) -> List[float]:
        X = [[float(v) for v in row] for row in X]
        return [float(v) for v in self.members[name].predict(X)]

    def predict(self, X: Sequence[Sequence[float]]) -> List[float]:
        """Rank-average over fitted members (scale-free member fusion)."""
        if not self.stamp.get("trained"):
            raise RuntimeError("surrogate not trained")
        if not X:
            return []
        preds = [self.predict_member(name, X) for name in self.stamp["members"]]
        out = [0.0] * len(X)
        for p in preds:
            r = rankdata_average(p)
            for i in range(len(X)):
                out[i] += r[i]
        return out

    def calibrate(self, Xh: Sequence[Sequence[float]],
                  yh: Sequence[float]) -> Dict[str, float]:
        """Spearman rho per member + ensemble on held-out data; frozen into
        the stamp.  An uncalibrated member (rho ~ 0) still ranks — the GS
        gate treats ensemble rho as the reported number."""
        cal: Dict[str, float] = {}
        for name in self.stamp["members"]:
            cal[name] = round(spearman_rho(self.predict_member(name, Xh), yh), 6)
        cal["ensemble"] = round(spearman_rho(self.predict(Xh), yh), 6)
        self.stamp["calibration"] = cal
        return cal


def available_members() -> List[str]:
    """Which members this host can train (recon/stamp helper)."""
    e = SurrogateEnsemble(use_torch=False, use_sklearn=False)
    names = list(e.members)
    if _ExtraTrees is not None and _GradBoost is not None:
        names += ["extra_trees", "grad_boost"]
    if _torch is not None:
        names += ["torch_mlp"]
    return sorted(names)
