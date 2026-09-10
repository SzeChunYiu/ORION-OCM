#!/usr/bin/env python3
"""M2 revival pass (LANE_M2_TRAVERSAL_CAPITAL_OPUS): residual structural headroom
ABOVE a history-free constant guess.

Probe V1 showed the KNOWN_STRUCTURE_ORACLE's whole advantage on the 8 acquisition
targets is a constant 21845-slot offset (all programs of length <= 7), because 7/8
targets sit at the maximum length.  V1 therefore cannot distinguish "structural
knowledge" from "guess 8".  This pass removes the constant and asks whether ANY
structure remains for history to carry, over the full protected stream (n=144) and
the full reachable ecology (n=20321 normal forms).

Orderings compared (all complete unless marked PRUNE):
  ASC          baseline: methods.solve's own ascending-length enumeration
  DESC         history-free reordering: length 8 first, then 7..0.  No features, no history.
  ORACLE_PRUNE true minimum length only (M1's KNOWN_STRUCTURE_ORACLE)
  ORACLE_ORDER true minimum length block first, then the rest ascending
  P_*_ORDER    predicted length block first, then the rest ascending
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, statistics, sys, time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2_RESIDUAL_HEADROOM_PROBE_V2"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def strip0(c):
    c = list(c)
    while len(c) > 1 and c[-1] == 0:
        c.pop()
    return tuple(c)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--partitions", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ladder", default="1000,4000,16000,64000,200000")
    ap.add_argument("--seed", type=int, default=20260910)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo / "research" / "m1-native-acquisition"))
    import ocm.learning.methods as M
    import m1_partitions as P
    ladder = [int(s) for s in a.ladder.split(",")]

    # ---- exact enumeration
    first_index, min_length, within, counts = {}, {}, {}, {}
    slot = 0
    for L in range(9):
        w = 0
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            w += 1
            nf = M.normal_form(prog)
            if nf not in first_index:
                first_index[nf], min_length[nf] = slot, L
            within.setdefault((nf, L), w)
        counts[L] = w
    total = slot
    TAIL = sum(counts[L] for L in range(8))  # 21845

    ORDERS = {"ASC": list(range(9)), "DESC": [8, 7, 6, 5, 4, 3, 2, 1, 0]}

    def b_order(nf, seq):
        tl = min_length[nf]
        used = 0
        for L in seq:
            if L == tl:
                return used + within[(nf, L)]
            used += counts[L]
        return None

    def b_pred_order(nf, ph):
        """predicted block first, then ascending over the rest"""
        return b_order(nf, [ph] + [L for L in range(9) if L != ph])

    def b_pred_prune(nf, ph):
        return within.get((nf, ph))

    # ---- predictors (explicit, non-neural)
    parts = json.loads(Path(a.partitions).read_text())
    streams = parts["streams"]
    prot = [{"row": r, "nf": strip0(tuple(Fraction(c) for c in r["coefficients"]))} for r in streams["protected"]]
    train = [{"row": r, "nf": strip0(tuple(Fraction(c) for c in r["coefficients"]))} for r in streams["train"]]
    dev_prefix = max(first_index[r["nf"]] for r in train)
    trav = {nf: L for nf, L in min_length.items() if first_index[nf] <= dev_prefix}

    def feat(nf):
        c = P.semantic_class([str(x) for x in nf])
        return (c["degree_band"], c["support_band"], c["coefficient_class"])

    def fit(pairs, fb):
        t = defaultdict(Counter)
        for f, l in pairs:
            t[f][l] += 1
        return ({f: max(cn.items(), key=lambda kv: (kv[1], -kv[0]))[0] for f, cn in t.items()}, fb)

    prior = Counter(min_length[r["nf"]] for r in train).most_common(1)[0][0]
    p_trav = fit([(feat(nf), L) for nf, L in trav.items()], prior)
    p_free = fit([(feat(nf), L) for nf, L in min_length.items()], prior)
    rng = random.Random(a.seed)
    labs = [L for _, L in [(feat(nf), L) for nf, L in trav.items()]]
    rng.shuffle(labs)
    p_shuf = fit([(feat(nf), L) for (nf, _), L in zip(trav.items(), labs)], prior)
    preds = {"P_traversal": p_trav, "P_analytic_free": p_free, "P_shuffled": p_shuf,
             "P_constant": ({}, prior)}

    def pget(pr, nf):
        return pr[0].get(feat(nf), pr[1])

    # ---- scopes
    scopes = {"protected_144": [r["nf"] for r in prot],
              "acquisition_targets_8": [r["nf"] for r in prot[:8]],
              "full_ecology_20321": list(min_length.keys())}

    out_scopes = {}
    for sname, nfs in scopes.items():
        arms = {}
        arms["ASC_baseline"] = [b_order(nf, ORDERS["ASC"]) for nf in nfs]
        arms["DESC_history_free"] = [b_order(nf, ORDERS["DESC"]) for nf in nfs]
        arms["ORACLE_PRUNE_true"] = [b_pred_prune(nf, min_length[nf]) for nf in nfs]
        arms["ORACLE_ORDER_true"] = [b_pred_order(nf, min_length[nf]) for nf in nfs]
        for pn, pr in preds.items():
            arms[f"{pn}_ORDER"] = [b_pred_order(nf, pget(pr, nf)) for nf in nfs]
            arms[f"{pn}_PRUNE"] = [b_pred_prune(nf, pget(pr, nf)) for nf in nfs]
        stats = {}
        for an, vals in arms.items():
            ok = [v for v in vals if v is not None]
            stats[an] = {
                "n": len(vals), "solved_unbounded": len(ok),
                "mean_B": round(statistics.fmean(ok), 1) if ok else None,
                "median_B": statistics.median(ok) if ok else None,
                "ladder_successes": {str(q): sum(1 for v in vals if v is not None and v <= q) for q in ladder},
                "ladder_total": sum(sum(1 for v in vals if v is not None and v <= q) for q in ladder),
            }
        # accuracy of each predictor in this scope
        acc = {pn: round(sum(1 for nf in nfs if pget(pr, nf) == min_length[nf]) / len(nfs), 4)
               for pn, pr in preds.items()}
        out_scopes[sname] = {"arms": stats, "predictor_accuracy": acc,
                             "true_length_distribution": dict(Counter(min_length[nf] for nf in nfs))}

    out = {"schema": SCHEMA, "lane": LANE, "status": "PRE_FREEZE_PROBE_NOT_A_SCORED_RUN",
           "owner_issue": 165, "hardening_parent": 323,
           "host": {"hostname": platform.node(), "python": platform.python_version(),
                    "uname": " ".join(platform.uname()[:3])},
           "bound_sources": {"methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
                             "m1_partitions.py": sha256_file(repo / "research" / "m1-native-acquisition" / "m1_partitions.py"),
                             "partitions.json": sha256_file(Path(a.partitions)),
                             "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip()},
           "grammar": {"total_programs": total, "per_length_counts": counts,
                       "distinct_normal_forms": len(min_length),
                       "programs_shorter_than_max": TAIL},
           "dev_traversal": {"prefix_slots": dev_prefix, "distinct_normal_forms": len(trav),
                             "fraction_of_ecology": round(len(trav) / len(min_length), 4)},
           "constant_predictor_label": prior,
           "ladder": ladder, "scopes": out_scopes,
           "timing_seconds": round(time.perf_counter() - t0, 2)}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"written": a.out, "constant_label": prior,
                      "timing": out["timing_seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
