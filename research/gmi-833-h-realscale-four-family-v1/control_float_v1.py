#!/usr/bin/env python3
"""D-12 float64 control (host-side only; NEVER part of CI green checks).

Repeats the kappa-sweep static tasks in IEEE754 double precision (numpy
least squares) and reports, per kappa point: the max |float64 prediction -
exact prediction| and the first kappa at which the float64 control's
selected stratum disagrees with the exact search.  This measures where
float numerics end and exact arithmetic continues — the real-scale
conditioning boundary as an ENGINEERING property, separate from the
selection boundaries the exact runs establish scientifically.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import battery_realscale_v1 as bat
import search_realscale_v1 as S

HERE = Path(__file__).resolve().parent


def dyadic_to_float(d: bat.Dyadic) -> float:
    return float(d.mant) * (2.0 ** d.exp)


def run() -> dict:
    reg = json.loads((HERE / "BATTERY_REGISTRY_V1.json").read_text())
    tasks = [t for t in reg["tasks"]
             if t["gen"] in ("affine", "pair_lift") and t.get("arm") == "kappa_sweep"]
    rows = []
    first_disagree_kappa = None
    for task in tasks:
        data = bat.materialize(task)
        X = np.array([[dyadic_to_float(v) for v in row] for row in data["X_train"] + data["X_test"]])
        y = np.array([dyadic_to_float(v) for v in data["y_train"] + data["y_test"]])
        half = len(y) // 2
        # float64 fits per stratum (linear strata only; the control question
        # is numerical, not structural)
        preds = {}
        for stratum in ("S_CONST", "S_ADD", "S_LIFT"):
            if stratum == "S_CONST":
                F_tr = np.ones((half, 1))
                F_te = np.ones((len(y) - half, 1))
            elif stratum == "S_ADD":
                F_tr = np.column_stack([np.ones(half), X[:half]])
                F_te = np.column_stack([np.ones(len(y) - half), X[half:]])
            else:
                p = X.shape[1]
                cols_tr = [X[:half, a] * X[:half, b]
                           for a in range(p) for b in range(a + 1, p)]
                cols_te = [X[half:, a] * X[half:, b]
                           for a in range(p) for b in range(a + 1, p)]
                F_tr = np.column_stack([np.ones(half), X[:half]] + cols_tr)
                F_te = np.column_stack([np.ones(len(y) - half), X[half:]] + cols_te)
            beta, *_ = np.linalg.lstsq(F_tr, y[:half], rcond=None)
            preds[stratum] = F_te @ beta
        exact = S.proc1_select(data, S.make_band(task))
        # compare float64 vs exact predictions for the champion's class
        champ = exact["champion_stratum"]
        if champ in preds:
            iface = S.Interface(data, 0)
            fit = S.fit_stratum(iface, champ)
            if isinstance(fit["pred_te"], tuple):
                ints, D = fit["pred_te"]
                unit = 2.0 ** iface.y_shift
                exact_pred = np.array([v * unit / D for v in ints])
            else:
                unit = 2.0 ** iface.y_shift
                exact_pred = np.array([float(p_) * unit for p_ in fit["pred_te"]])
            max_gap = float(np.max(np.abs(preds[champ] * unit - exact_pred))) \
                if champ != "S_MONO" else None
            float_best = min(preds, key=lambda k: float(np.mean((preds[k] * unit - y[half:] * unit) ** 2)))
            agree = float_best == champ or champ in ("S_MONO", "S_ORD", "S_TABLE")
            if not agree and first_disagree_kappa is None:
                first_disagree_kappa = task["kappa_exp"]
            rows.append({"id": task["id"], "kappa_exp": task["kappa_exp"],
                         "champion": exact["champion"], "max_abs_gap": max_gap,
                         "float_argmin": float_best})
    return {
        "schema": "GMI833HRealScaleFloatControlV1",
        "rows": rows,
        "first_float_disagreement_kappa_exp": first_disagree_kappa,
        "kappa_at_first_disagreement": (2.0 ** (4 * first_disagree_kappa))
        if first_disagree_kappa is not None else None,
        "note": "host-side numpy control (D-12); no CI dependency; exact runs carry all green checks",
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=1))
