#!/usr/bin/env python3
"""M2 feature-sufficiency ladder (LANE_M2_TRAVERSAL_CAPITAL_OPUS).

V2 showed: (i) the oracle's advantage on the 8 M1 acquisition targets is a constant
21845-slot offset, and (ii) at the honest 144-row scope real oracle headroom exists
(+104 ladder successes) but NO predictor over the frozen semantic class captures any
of it.  This pass asks whether that is a property of OCM/history or of the frozen
FEATURE SET, by fitting the SAME explicit modal-length rule over richer coordinates.

For each feature set we fit twice:
  _dev   : on the dev-phase traversal only (what history could carry)
  _free  : on the full reachable ecology  (grammar-only, ZERO developmental outcomes)
If _dev ~= _free everywhere, the information was never developmental.

Feature sets (all explicit, non-neural, computed from the target surface alone):
  FS0_constant     no features
  FS1_frozen_band  the frozen semantic class (degree band x support band x coeff class)
  FS2_frozen_fine  exact degree x support x coeff class
  FS3_squares      n_squares = log2(degree)   [exact: every `square` doubles degree]
  FS4_sq_mag       n_squares x max-coefficient bit length
  FS5_sq_mag_sup   n_squares x max-coeff bitlen x support x is_rational
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, statistics, sys, time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2_FEATURE_SUFFICIENCY_V3"


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


def bitlen(fr: Fraction) -> int:
    return max(abs(fr.numerator).bit_length(), abs(fr.denominator).bit_length())


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

    def b_order_seq(nf, seq):
        tl, used = min_length[nf], 0
        for L in seq:
            if L == tl:
                return used + within[(nf, L)]
            used += counts[L]
        return None

    def b_order(nf, ph):
        return b_order_seq(nf, [ph] + [L for L in range(9) if L != ph])

    def b_prune(nf, ph):
        return within.get((nf, ph))

    # ---------------- feature sets
    def fs0(nf):
        return ()

    def fs1(nf):
        c = P.semantic_class([str(x) for x in nf])
        return (c["degree_band"], c["support_band"], c["coefficient_class"])

    def fs2(nf):
        c = P.semantic_class([str(x) for x in nf])
        return (c["degree"], c["support"], c["coefficient_class"])

    def n_squares(nf):
        deg = len(nf) - 1
        return deg.bit_length() - 1 if deg > 0 and (deg & (deg - 1)) == 0 else -1

    def fs3(nf):
        return (n_squares(nf),)

    def fs4(nf):
        return (n_squares(nf), max(bitlen(c) for c in nf))

    def fs5(nf):
        return (n_squares(nf), max(bitlen(c) for c in nf),
                sum(1 for c in nf if c != 0), any(c.denominator != 1 for c in nf))

    FSETS = {"FS0_constant": fs0, "FS1_frozen_band": fs1, "FS2_frozen_fine": fs2,
             "FS3_squares": fs3, "FS4_sq_mag": fs4, "FS5_sq_mag_sup": fs5}

    parts = json.loads(Path(a.partitions).read_text())
    streams = parts["streams"]
    prot = [strip0(tuple(Fraction(c) for c in r["coefficients"])) for r in streams["protected"]]
    train = [strip0(tuple(Fraction(c) for c in r["coefficients"])) for r in streams["train"]]
    dev_prefix = max(first_index[nf] for nf in train)
    trav = [nf for nf in min_length if first_index[nf] <= dev_prefix]
    prior = Counter(min_length[nf] for nf in train).most_common(1)[0][0]

    def fit(fn, nfs, labels=None):
        t = defaultdict(Counter)
        labels = labels if labels is not None else [min_length[nf] for nf in nfs]
        for nf, L in zip(nfs, labels):
            t[fn(nf)][L] += 1
        return {f: max(cn.items(), key=lambda kv: (kv[1], -kv[0]))[0] for f, cn in t.items()}

    scopes = {"acquisition_targets_8": prot[:8], "protected_144": prot,
              "full_ecology_20321": list(min_length.keys())}
    rng = random.Random(a.seed)

    out = {"schema": SCHEMA, "lane": LANE, "status": "PRE_FREEZE_PROBE_NOT_A_SCORED_RUN",
           "owner_issue": 165, "hardening_parent": 323,
           "host": {"hostname": platform.node(), "python": platform.python_version()},
           "bound_sources": {"methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
                             "partitions.json": sha256_file(Path(a.partitions)),
                             "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip()},
           "dev_traversal": {"prefix_slots": dev_prefix, "distinct_normal_forms": len(trav)},
           "constant_label": prior, "ladder": ladder, "feature_sets": {}}

    for fsname, fn in FSETS.items():
        rule_dev = fit(fn, trav)
        rule_free = fit(fn, list(min_length.keys()))
        shuf = [min_length[nf] for nf in trav]
        rng.shuffle(shuf)
        rule_shuf = fit(fn, trav, shuf)
        entry = {"cells_dev": len(rule_dev), "cells_free": len(rule_free), "scopes": {}}
        for sname, nfs in scopes.items():
            row = {}
            for rname, rule in (("dev", rule_dev), ("free", rule_free), ("shuffled", rule_shuf)):
                preds = [rule.get(fn(nf), prior) for nf in nfs]
                acc = sum(1 for nf, p in zip(nfs, preds) if p == min_length[nf]) / len(nfs)
                for mode, bf in (("ORDER", b_order), ("PRUNE", b_prune)):
                    vals = [bf(nf, p) for nf, p in zip(nfs, preds)]
                    ok = [v for v in vals if v is not None]
                    row[f"{rname}_{mode}"] = {
                        "accuracy": round(acc, 4),
                        "mean_B": round(statistics.fmean(ok), 1) if ok else None,
                        "solved_unbounded": len(ok), "n": len(vals),
                        "ladder_total": sum(sum(1 for v in vals if v is not None and v <= q) for q in ladder)}
            # anchors
            base = [b_order_seq(nf, list(range(9))) for nf in nfs]
            orc = [b_prune(nf, min_length[nf]) for nf in nfs]
            row["ANCHOR_ASC_baseline"] = {
                "mean_B": round(statistics.fmean(base), 1),
                "ladder_total": sum(sum(1 for v in base if v <= q) for q in ladder)}
            row["ANCHOR_ORACLE_true"] = {
                "mean_B": round(statistics.fmean(orc), 1),
                "ladder_total": sum(sum(1 for v in orc if v <= q) for q in ladder)}
            entry["scopes"][sname] = row
        out["feature_sets"][fsname] = entry

    out["timing_seconds"] = round(time.perf_counter() - t0, 2)
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"written": a.out, "timing": out["timing_seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
