"""Stage 1c: commit the survivor set and a real search-slice sample per scope.

FREEZE_V1.md section 9 requires the source-separated oracle to re-derive every
selection. The oracle has no access to D1-D3, so this stage commits, for each
scope, the decisive part of the search in exact integers:

  * `survivors`: the top 8 of the frozen screen's ranking, read verbatim from
    the committed `scope_<S>.json::search.screen_top20` — not recomputed, so
    the survivor set is exactly the one the run used;
  * `sample`: the first `N_SAMPLE` rows of that scope's V2 search slice, as
    exact integers with their registered denominators;
  * `primary_ranking`: the primary implementation's ranking of those 8 on that
    same sample, under the same reduced fitting budget the oracle will use.

The oracle then re-ranks them with its own arithmetic, its own evaluator and its
own optimiser, and must agree on the winner's structural class.
"""
from __future__ import print_function
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grammar_v1 as G           # noqa: E402
import grammar_v2 as G2          # noqa: E402
import run_real_scale_v1 as R    # noqa: E402
import run_real_scale_v2 as V2   # noqa: E402

OUT = V2.OUT
N_SAMPLE = 200
N_SURV = 8
SWEEPS = 2
GRID = (-4, -3, -2, -1, 1, 2, 3, 4)


def reduced_fit(body, head, rs, rows, ys, d, loss):
    """Reduced-budget coordinate descent in floats, matching the oracle's
    schedule exactly: start at zero, step 1 halved each sweep, grid GRID."""
    X = np.asarray(rows, dtype=np.float64)
    y = np.asarray(ys, dtype=np.float64)
    bf, hn, hs = R.body_fn(body), R.head_fn_np(head), R.head_fn_scalar(head)
    p = np.zeros(d)
    bias = 0.0
    best = R.loss_of(loss, R.predict(bf, hn, hs, rs, X, p, bias), y)
    step = 1.0
    for _ in range(SWEEPS):
        for j in range(d + 1):
            cur = p[j] if j < d else bias
            for k in GRID:
                v = cur + k * step
                if j < d:
                    p[j] = v
                else:
                    bias = v
                L = R.loss_of(loss, R.predict(bf, hn, hs, rs, X, p, bias), y)
                if L < best:
                    best, cur = L, v
                if j < d:
                    p[j] = cur
                else:
                    bias = cur
        step *= 0.5
    return best


def main():
    src, d1b, pcm, lines, _ = R.load_sources()
    for name in ("H01", "H02", "H03", "H04"):
        t0 = time.time()
        with open(os.path.join(OUT, "scope_%s.json" % name)) as f:
            scope = json.load(f)
        if name == "H01":
            eco = R.ecology_H01(d1b)
        elif name == "H02":
            eco = V2.reorder(R.ecology_H02(pcm))
        elif name == "H03":
            eco = V2.reorder(R.ecology_H03(lines))
            eco["loss"] = "absolute"
        else:
            eco = V2.reorder(R.ecology_H04(pcm))
        sl = V2.slices_v2(eco)
        surv = scope["search"]["screen_top20"][:N_SURV]
        idx = sl["search"][:N_SAMPLE]
        rows, yy = R.design(eco, idx)
        rank = []
        svs = []
        for e in surv:
            b, h = R.parse_expr(e["body"]), R.parse_expr(e["head"])
            st = G._depends_on(h, "STATE", None, ["S", "BIAS"])
            svs.append({"body": e["body"], "head": e["head"],
                        "reads_state": bool(st)})
            L = reduced_fit(b, h, st, rows, yy, eco["d"], eco["loss"])
            rank.append({"body": e["body"], "head": e["head"], "loss": L,
                         "nodes": G.size(b) + G.size(h)})
        rank.sort(key=lambda r: (r["loss"], r["nodes"], r["body"], r["head"]))
        rec = {"scope": "SIGMA_" + name, "loss": eco["loss"], "d": eco["d"],
               "n_sample": int(len(idx)), "sweeps": SWEEPS, "grid": list(GRID),
               "survivor_source":
                   "scope_%s.json::search.screen_top20[:8], verbatim" % name,
               "survivors": svs,
               "primary_ranking": rank,
               "primary_winner_class": G.classify(
                   R.parse_expr(rank[0]["body"]),
                   R.parse_expr(rank[0]["head"]))["class"]}
        if eco["kind"] == "onehot":
            rec["syms"] = [int(v) for v in eco["sym"][idx]]
            rec["y"] = [int(v) for v in eco["y"][idx]]
        else:
            rec["Xi"] = [[int(v) for v in r] for r in eco["Xi"][idx]]
            rec["yi"] = [int(v) for v in eco["yi"][idx]]
            rec["xden"] = (list(eco["xden"]) if isinstance(eco["xden"], tuple)
                           else int(eco["xden"]))
            rec["yden"] = int(eco["yden"])
        with open(os.path.join(OUT, "search_sample_%s.json" % name), "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        print("[%s] survivors=%d sample=%d primary winner %s | %s (%s) %.1fs"
              % (name, len(svs), len(idx), rank[0]["body"], rank[0]["head"],
                 rec["primary_winner_class"], time.time() - t0))


if __name__ == "__main__":
    main()
