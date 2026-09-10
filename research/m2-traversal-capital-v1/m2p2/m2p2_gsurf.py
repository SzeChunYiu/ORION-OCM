#!/usr/bin/env python3
"""M2-P2 G-SURF: the per-world blocking surface-derivability entry gate.

Imports the m2_probe_v3_feature_sufficiency.py machinery UNMODIFIED (feature
families FS0..FS5 computed from target surface alone; each fitted twice — _dev on
the dev-phase traversal, _free on the full reachable grammar with zero
developmental outcomes; ORDER-mode ladder scoring against budgets
1000,4000,16000,64000,200000) and applies it to one compiled M2-P2 world
(M2P2_WORLD_*.json emitted by m2p2_compile.py).

CALIBRATION (M2P2_GSURF_CALIBRATION.md, all runs pre-author-session): the #349
letter ("free-fit ~= chance while dev-fit >> chance") does NOT transfer to
hidden-family worlds. On m2p1's own recorded positives (E5, E6 — both
HISTORY_INDUCED_SEARCH_PRIOR with G4 PASS) the dev fit gains ZERO ladder points:
the developmental signal lives in fragment structure, which no explicit feature
cell expresses; absence of FS-expressible dev signal therefore does NOT mean "no
recoverable signal". Conversely, fine cells (FS2/FS5) can win tens of ladder
points over the constant cell on sparse-target worlds without approaching what
the scored arms measure.

Recalibrated frozen rule (parameter-free except the pre-registered majority line):

  CHANCE = the best ZERO-history ordering = max(FS0 constant fit, ASC, DESC)
  FREE   = the best history-free ordering  = max(CHANCE family, FS1..FS5 free fits)
  ORACLE = the true-length ordering (the ceiling of any length-class ordering)
  fire SURFACE_DERIVABLE iff FREE captures >= 50% of the oracle headroom
       (FREE - CHANCE) >= 0.5 * (ORACLE - CHANCE)
  otherwise PASS (the world proceeds to the scored arms, where the decisive
  surface test is the scored-stage G4 exactly as m2p1: CONTINUED vs the best
  history-free surface ordering, paired)

Ground truth respected: E5 free-captures 0%, E6 ~2% (both PASS); the majority
line fires only in the degenerate regime where a grammar-only rule IS the family
ordering, making the scored comparison uninterpretable.

The dev-phase traversal is defined exactly as the probe defines it: every normal
form whose first_index <= dev_prefix, where dev_prefix = max first_index over the
world's initial stream. The _dev fits are still computed and reported (they are
evidence), but no longer gate.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, random, statistics, sys, time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path

LANE = "LANE_M2_TRAVERSAL_CAPITAL_OPUS"
SCHEMA = "OCM_M2P2_GSURF_V1"

LADDER = [1000, 4000, 16000, 64000, 200000]
CAPTURE_MAJORITY = 0.5   # frozen: fire iff surface captures >= 50% of oracle headroom


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
    ap.add_argument("--world", required=True, help="compiled M2P2_WORLD_*.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260911)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo / "research" / "m1-native-acquisition"))
    import ocm.learning.methods as M
    import m1_partitions as P

    # ---- grammar enumeration: first_index / min_length / within / counts
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

    # ---- feature sets: identical to m2_probe_v3_feature_sufficiency.py
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

    # ---- compiled world streams
    world = json.loads(Path(a.world).read_text())
    streams = world["streams"]
    def nfs_of(name):
        return [strip0(tuple(Fraction(c) for c in r["coefficients"]))
                for r in streams[name]]
    future = nfs_of("protected")
    train = nfs_of("train")
    dev_prefix = max(first_index[nf] for nf in train)
    trav = [nf for nf in min_length if first_index[nf] <= dev_prefix]
    prior = Counter(min_length[nf] for nf in train).most_common(1)[0][0]

    def fit(fn, nfs, labels=None):
        t = defaultdict(Counter)
        labels = labels if labels is not None else [min_length[nf] for nf in nfs]
        for nf, L in zip(nfs, labels):
            t[fn(nf)][L] += 1
        return {f: max(cn.items(), key=lambda kv: (kv[1], -kv[0]))[0] for f, cn in t.items()}

    rng = random.Random(a.seed)
    out = {"schema": SCHEMA, "lane": LANE, "status": "ENTRY_GATE_NOT_A_SCORED_RUN",
           "owner_issue": 165, "hardening_parent": 323,
           "gate_id": "G-SURF", "blocking": True,
           "provenance": "m2_probe_v3_feature_sufficiency.py discipline imported "
                         "unmodified (FS0..FS5, _dev/_free dual fit, ORDER-mode "
                         "ladder, shuffled-label null)",
           "world_id": world.get("world_id", json.dumps(world.get("ecology_variant", "unknown"))),
           "world_file": str(Path(a.world)),
           "pass_rule": {"capture_majority_line": CAPTURE_MAJORITY,
                         "rule": "fire SURFACE_DERIVABLE iff the best history-free "
                                 "ordering captures >= 50% of the oracle headroom; "
                                 "dev fits are evidence, never a gate"},
           "host": {"hostname": platform.node(), "python": platform.python_version()},
           "bound_sources": {"methods.py": sha256_file(repo / "src" / "ocm" / "learning" / "methods.py"),
                             "world_json": sha256_file(Path(a.world)),
                             "git_head": os.popen(f"/usr/bin/git -C {repo} rev-parse HEAD").read().strip()},
           "dev_traversal": {"prefix_slots": dev_prefix, "distinct_normal_forms": len(trav)},
           "constant_label": prior, "ladder": LADDER,
           "future_n": len(future), "train_n": len(train),
           "feature_sets": {}}

    for fsname, fn in FSETS.items():
        rule_dev = fit(fn, trav)
        rule_free = fit(fn, list(min_length.keys()))
        shuf = [min_length[nf] for nf in trav]
        rng.shuffle(shuf)
        rule_shuf = fit(fn, trav, shuf)
        entry = {"cells_dev": len(rule_dev), "cells_free": len(rule_free), "fits": {}}
        for rname, rule in (("dev", rule_dev), ("free", rule_free), ("shuffled", rule_shuf)):
            preds = [rule.get(fn(nf), prior) for nf in future]
            acc = sum(1 for nf, p in zip(future, preds) if p == min_length[nf]) / len(future)
            for mode, bf in (("ORDER", b_order), ("PRUNE", b_prune)):
                vals = [bf(nf, p) for nf, p in zip(future, preds)]
                ok = [v for v in vals if v is not None]
                entry["fits"][f"{rname}_{mode}"] = {
                    "accuracy": round(acc, 4),
                    "mean_B": round(statistics.fmean(ok), 1) if ok else None,
                    "solved_unbounded": len(ok), "n": len(vals),
                    "ladder_total": sum(sum(1 for v in vals if v is not None and v <= q)
                                        for q in LADDER)}
        base = [b_order_seq(nf, list(range(9))) for nf in future]
        desc = [b_order_seq(nf, list(range(8, -1, -1))) for nf in future]
        orc = [b_prune(nf, min_length[nf]) for nf in future]
        entry["fits"]["ANCHOR_ASC_baseline"] = {
            "mean_B": round(statistics.fmean(base), 1),
            "ladder_total": sum(sum(1 for v in base if v <= q) for q in LADDER)}
        entry["fits"]["ANCHOR_DESC"] = {
            "mean_B": round(statistics.fmean(desc), 1),
            "ladder_total": sum(sum(1 for v in desc if v <= q) for q in LADDER)}
        entry["fits"]["ANCHOR_ORACLE_true"] = {
            "mean_B": round(statistics.fmean(orc), 1),
            "ladder_total": sum(sum(1 for v in orc if v <= q) for q in LADDER)}
        out["feature_sets"][fsname] = entry

    lt = lambda fs, fitname: out["feature_sets"][fs]["fits"][fitname]["ladder_total"]
    anchors = out["feature_sets"]["FS0_constant"]["fits"]
    asc_lt = anchors["ANCHOR_ASC_baseline"]["ladder_total"]
    desc_lt = anchors["ANCHOR_DESC"]["ladder_total"]
    oracle_lt = anchors["ANCHOR_ORACLE_true"]["ladder_total"]
    # CHANCE: the best ZERO-history ordering (constant cell, ascending, descending)
    chance = max(lt("FS0_constant", "free_ORDER"), asc_lt, desc_lt)
    # FREE: the best history-free ordering (chance family + richer surface fits)
    free_candidates = {"FS0_constant": lt("FS0_constant", "free_ORDER"),
                       "ANCHOR_ASC": asc_lt, "ANCHOR_DESC": desc_lt}
    free_candidates.update({fs: lt(fs, "free_ORDER") for fs in FSETS
                            if fs != "FS0_constant"})
    best_free = max(free_candidates.values())
    best_free_name = max(free_candidates, key=free_candidates.get)
    best_dev = max(lt(fs, "dev_ORDER") for fs in FSETS)
    headroom = oracle_lt - chance
    free_margin = best_free - chance
    capture = (free_margin / headroom) if headroom > 0 else (1.0 if free_margin > 0 else 0.0)
    if headroom > 0 and free_margin >= CAPTURE_MAJORITY * headroom:
        verdict = "SURFACE_DERIVABLE"      # a grammar-only rule IS the family ordering
    else:
        verdict = "PASS"                   # scored arms run; scored G4 decides
    out["gsurf"] = {
        "chance_ladder": chance, "free_best_ladder": best_free,
        "free_best_name": best_free_name, "dev_best_ladder": best_dev,
        "oracle_ladder": oracle_lt, "oracle_headroom": headroom,
        "free_margin": free_margin, "free_capture_fraction": round(capture, 4),
        "capture_majority_line": CAPTURE_MAJORITY,
        "verdict": verdict,
        "rule": "fire SURFACE_DERIVABLE iff the best history-free ordering "
                "captures >= 50% of the oracle ordering headroom on the future "
                "stream; dev fits are reported as evidence and do not gate"}
    out["timing_seconds"] = round(time.perf_counter() - t0, 2)
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({"world": out["world_id"], "capture": round(capture, 4),
                      "free_margin": free_margin, "headroom": headroom,
                      "best_free_name": best_free_name, "verdict": verdict,
                      "timing": out["timing_seconds"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
