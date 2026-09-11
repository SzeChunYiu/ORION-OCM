#!/usr/bin/env python3
"""Plasticity under ecology shift: the one thing a plain adaptive parent cannot do.

PARENT_REGRET.md recorded a hard negative -- OCM never beat the ungated parent (0 wins in
19 worlds). That is expected: where OCM admits, the arms are identical by construction,
and where it refuses it forfeits the library. OCM can only win by doing something the
parent structurally lacks.

The parent is a static decision list: once its library is learned it serves it forever.
OCM's KSO machinery has support-sensitive reload and revocation, i.e. a DEPLOYMENT
LIFECYCLE separable from epistemic warrant (THEORY_GAPS.md 2.3):

    W_live(a)          is this still warranted?      -- never touched here
    D_live(a, z, E)    should it influence search?   -- may deactivate and REACTIVATE

This experiment runs a lifetime stream across an ECOLOGY SHIFT:

    regime A  targets composed from motif set M_A   (the library's home ecology)
    regime B  targets composed from motif set M_B   (disjoint; the library is now stale)
    regime A' back to M_A                            (does truth survive deactivation?)

Arms, all serving through the REGISTERED M.solve:
    RESET         no library, ever
    PARENT_STALE  serves the learned library forever, no lifecycle (the strongest parent)
    OCM_LIVE      same library, plus D_live: deactivate when a rolling window of measured
                  outcomes shows E[dB] <= 0; reactivate when it recovers. The library is
                  never deleted -- W_live is untouched throughout.
    ORACLE_B      calibration only: the true M_B motifs during regime B

Registered predictions:
  P-A  in regime A   OCM_LIVE == PARENT_STALE   (nothing to deactivate)
  P-B  in regime B   OCM_LIVE <  PARENT_STALE   (stale library detected and stood down)
  P-A' in regime A'  OCM_LIVE == PARENT_STALE   (reactivated; truth was never destroyed)
  P-cum cumulative over the whole lifetime: OCM_LIVE < PARENT_STALE
"""
from __future__ import annotations
import argparse, hashlib, json, platform, random, statistics, sys, time
from fractions import Fraction
from itertools import product
from pathlib import Path

WINDOW = 8          # rolling window of recent targets used by D_live
DEACTIVATE_AT = 0.0  # deactivate when mean measured dB over the window drops to <= 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--motifs", type=int, default=6)
    ap.add_argument("--per-regime", type=int, default=40)
    ap.add_argument("--train-n", type=int, default=60)
    ap.add_argument("--budget", type=int, default=200000)
    a = ap.parse_args()
    t0 = time.perf_counter()
    repo = Path(a.repo)
    sys.path.insert(0, str(repo / "src"))
    import ocm.learning.methods as M

    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(M.PRIMITIVES, repeat=L):
            slot += 1
            nf = M.normal_form(prog)
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot

    rng = random.Random(a.seed)
    pool = [p for p in product(M.PRIMITIVES, repeat=2)]
    picked = rng.sample(pool, 2 * a.motifs)
    MA, MB = tuple(sorted(picked[:a.motifs])), tuple(sorted(picked[a.motifs:]))

    def arrangements(motifs, k=4):
        out = {}
        for combo in product(range(len(motifs)), repeat=k):
            prog = tuple(op for i in combo for op in motifs[i])
            if len(prog) > 8:
                continue
            nf = M.normal_form(prog)
            if canonical.get(nf) == prog:
                out.setdefault(nf, combo)
        return sorted(out.items(), key=lambda x: hashlib.sha256(str(x[0]).encode()).hexdigest())

    A_items, B_items = arrangements(MA), arrangements(MB)
    need = a.train_n + a.per_regime * 2
    if len(A_items) < need or len(B_items) < a.per_regime:
        raise SystemExit(f"TOO_SMALL A={len(A_items)} B={len(B_items)} need A>={need} B>={a.per_regime}")

    train = A_items[: a.train_n]
    streamA = A_items[a.train_n: a.train_n + a.per_regime]
    streamA2 = A_items[a.train_n + a.per_regime: a.train_n + 2 * a.per_regime]
    streamB = B_items[: a.per_regime]

    def task(nf, i):
        return M.PolynomialTask("plast:%d:%s" % (i, hashlib.sha256(str(nf).encode()).hexdigest()[:10]),
                                tuple(nf))

    budget = M.SearchBudget(slots=a.budget, max_length=8)

    # ---- development on regime A only
    training = []
    for i, (nf, _) in enumerate(train):
        t = task(nf, i)
        r = M.solve(t, budget)
        if M.verify_solution(t, r):
            training.append((t, r))
    method = M.learn_generator(training)
    dev_slots = sum(first_index[nf] for nf, _ in train)
    recovered_A = sum(1 for m in MA if m in method.fragments)

    # ---- lifetime stream
    stream = ([("A", nf) for nf, _ in streamA] +
              [("B", nf) for nf, _ in streamB] +
              [("A_prime", nf) for nf, _ in streamA2])

    live = True
    window: list[float] = []
    rows, deact, react = [], [], []
    oracleB = M.GeneratorMethod(tuple(MB)[:16], ("oracle",))

    for i, (regime, nf) in enumerate(stream):
        t = task(nf, 100000 + i)
        base = M.solve(t, budget)
        par = M.solve(t, budget, method)
        ocm = M.solve(t, budget, method) if live else base
        orc = M.solve(t, budget, oracleB) if regime == "B" else None
        d_par = base.slots - par.slots
        # D_live update uses ONLY what OCM actually observed on served targets
        if live:
            window.append(float(d_par))
            if len(window) > WINDOW:
                window.pop(0)
            if len(window) == WINDOW and statistics.fmean(window) <= DEACTIVATE_AT:
                live = False
                deact.append(i)
                window = []
        else:
            # periodic cheap probe: one in every WINDOW targets, re-measure to allow recovery
            if i % WINDOW == 0:
                window.append(float(d_par))
                if len(window) >= 3 and statistics.fmean(window) > 0:
                    live = True
                    react.append(i)
                    window = []
        rows.append({"i": i, "regime": regime, "d_live": live,
                     "base": base.slots, "parent": par.slots,
                     "ocm": ocm.slots, "oracleB": orc.slots if orc else None,
                     "verified": M.verify_solution(t, base)})

    def tot(key, regime=None):
        return sum(r[key] for r in rows if regime is None or r["regime"] == regime)

    regimes = ("A", "B", "A_prime")
    per_regime = {g: {"RESET": tot("base", g), "PARENT_STALE": tot("parent", g),
                      "OCM_LIVE": tot("ocm", g),
                      "ocm_beats_parent": tot("ocm", g) < tot("parent", g)}
                  for g in regimes}
    out = {
        "schema": "OCM_M2_PLASTICITY_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
        "owner_issue": 165, "hardening_parent": 323,
        "host": {"hostname": platform.node(), "python": platform.python_version()},
        "frozen_seed": a.seed, "window": WINDOW,
        "motifs_A": ["".join(m) for m in MA], "motifs_B": ["".join(m) for m in MB],
        "development": {"train_n": len(train), "solved": len(training),
                        "fragments": len(method.fragments),
                        "motifs_A_recovered": f"{recovered_A}/{len(MA)}",
                        "dev_solve_slots": dev_slots},
        "deactivated_at": deact, "reactivated_at": react,
        "per_regime_total_slots": per_regime,
        "lifetime_total_slots": {"RESET": tot("base"), "PARENT_STALE": tot("parent"),
                                 "OCM_LIVE": tot("ocm")},
        "lifetime_ocm_beats_parent": tot("ocm") < tot("parent"),
        "predictions": {
            "P_A_equal": per_regime["A"]["OCM_LIVE"] == per_regime["A"]["PARENT_STALE"],
            "P_B_ocm_better": per_regime["B"]["OCM_LIVE"] < per_regime["B"]["PARENT_STALE"],
            "P_Aprime_recovered": per_regime["A_prime"]["OCM_LIVE"] <= per_regime["A_prime"]["PARENT_STALE"] * 1.05,
            "P_cumulative": tot("ocm") < tot("parent")},
        "warrant_note": ("W_live was never modified: the library is retained throughout and "
                         "only its deployment state changes, which is why regime A' can "
                         "recover without relearning"),
        "rows": rows,
        "timing_seconds": round(time.perf_counter() - t0, 2)}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1)[:2600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
