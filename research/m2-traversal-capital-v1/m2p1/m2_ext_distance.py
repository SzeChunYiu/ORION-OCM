#!/usr/bin/env python3
"""d=1 vs d=2 in a substrate that permits the test (P=6). The decisive gap-4 experiment.

Registered grammar P=4 is infeasible by a window of -1.87 motifs (M2_SUBSTRATE_REQ), so
the mechanism is exercised at P=6 (window +6.15) using the exactness-controlled analogue
(EXACT_MATCH on 60 probes against M.solve).

Matched design: identical motif alphabet, identical k, identical train_n, identical
library-selection rule. ONLY the arrangement distance of the protected stream differs, so
a difference between the two grades is attributable to distance and nothing else.

    d = 1   every target is one motif substitution from a training arrangement
    d = 2   every target is at least two substitutions from EVERY training arrangement

Part coverage is 1.0 in both grades by construction -- the same motifs are available -- so
this isolates generalisation over ARRANGEMENTS from reuse of parts, which is exactly the
distinction the hostile review of #356 said was untested.

Arms: RESET (no library) and CONTINUED_MDL (compression-selected library), plus SHUFFLED
as the structure control. Registered prediction: if the mechanism only interpolates,
benefit collapses at d=2; if it generalises over arrangements, benefit decays but survives.
"""
from __future__ import annotations
import argparse, hashlib, json, random, statistics, sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from m2_extgrammar import normal_form, solve, primitive_programs
from m2_mdl_selection import mdl_select

PRIMS6 = ("inc", "dec", "double", "square", "triple", "neg")


def seq_edit(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--motifs", type=int, default=10)
    ap.add_argument("--tokens", type=int, default=4)
    ap.add_argument("--train-n", type=int, default=45)
    ap.add_argument("--prot-n", type=int, default=25)
    ap.add_argument("--val-n", type=int, default=15)
    ap.add_argument("--slots", type=int, default=2100000,
                    help="must cover the FULL grammar at this P: sum_{L<=8} P^L = 2,015,539 "
                         "at P=6. The P=4 default of 200k leaves length-8 targets unreachable, "
                         "which silently produced an empty library in the first run.")
    ap.add_argument("--seed-start", type=int, default=0)
    a = ap.parse_args()

    prims = PRIMS6
    # canonical index: first program (ascending length, product order) per normal form
    canonical, first_index = {}, {}
    slot = 0
    for L in range(9):
        for prog in product(prims, repeat=L):
            slot += 1
            nf = normal_form(prog, prims)
            while len(nf) > 1 and nf[-1] == 0:
                nf = nf[:-1]
            if nf not in canonical:
                canonical[nf], first_index[nf] = prog, slot
        if L >= 8:
            break
    print("canonical normal forms:", len(canonical), flush=True)

    results = []
    for s in range(a.seed_start, a.seed_start + a.seeds):
        rng = random.Random(1000 + s)
        pool = [p for p in product(prims, repeat=2)]
        motifs = tuple(sorted(rng.sample(pool, a.motifs)))
        arr = {}
        for combo in product(range(a.motifs), repeat=a.tokens):
            prog = tuple(op for i in combo for op in motifs[i])
            if len(prog) > 8:
                continue
            nf = normal_form(prog, prims)
            while len(nf) > 1 and nf[-1] == 0:
                nf = nf[:-1]
            if canonical.get(nf) == prog:
                arr.setdefault(nf, combo)
        items = sorted(arr.items(), key=lambda x: hashlib.sha256(str(x[0]).encode()).hexdigest())
        if len(items) < a.train_n + a.val_n + a.prot_n:
            print(f"seed {s}: too small ({len(items)})", flush=True)
            continue
        train = items[: a.train_n]
        tseq = [c for _, c in train]
        rest = items[a.train_n:]
        graded = {1: [], 2: []}
        for nf, c in rest:
            d = min(seq_edit(c, t) for t in tseq)
            if d == 1:
                graded[1].append(nf)
            elif d >= 2:
                graded[2].append(nf)
        if len(graded[1]) < a.prot_n or len(graded[2]) < a.prot_n:
            print(f"seed {s}: grades short d1={len(graded[1])} d2={len(graded[2])}", flush=True)
            continue

        # develop once: solve training targets, select library by MDL
        solved = []
        for nf, _ in train:
            r = solve(nf, prims, slots=a.slots)
            if r["status"] == "VERIFIED":
                solved.append(r["program"])
        if len(solved) < len(train) // 2:
            # GUARD: a mostly-unsolved training set means the budget does not reach the
            # targets. Reporting 0% here would be CONTINUED == RESET with nothing served,
            # which is not a distance result. Fail loudly instead.
            print(f"seed {1000+s}: BUDGET_INSUFFICIENT solved={len(solved)}/{len(train)}", flush=True)
            results.append({"seed": 1000 + s, "status": "BUDGET_INSUFFICIENT",
                            "solved": len(solved), "train": len(train)})
            continue
        lib = tuple(f for f in mdl_select(solved, cap=16) if 2 <= len(f) <= 8)[:16]
        rec = len([f for f in lib if f in motifs])

        shuf_pool = [p for p in pool if p not in set(motifs)]
        shuf = tuple(rng.sample(shuf_pool, min(len(lib), len(shuf_pool))))

        row = {"seed": 1000 + s, "arrangements": len(items),
               "motifs_recovered": f"{rec}/{a.motifs}", "library": len(lib)}
        for d in (1, 2):
            tg = graded[d][: a.prot_n]
            base = [solve(nf, prims, slots=a.slots) for nf in tg]
            cont = [solve(nf, prims, slots=a.slots, fragments=lib) for nf in tg]
            sh = [solve(nf, prims, slots=a.slots, fragments=shuf) for nf in tg]
            mb = statistics.fmean(x["slots"] for x in base)
            mc = statistics.fmean(x["slots"] for x in cont)
            ms = statistics.fmean(x["slots"] for x in sh)
            row[f"d{d}"] = {
                "n": len(tg),
                "mean_B_reset": round(mb, 1),
                "mean_B_continued": round(mc, 1),
                "mean_B_shuffled": round(ms, 1),
                "reduction_vs_reset": round(1 - mc / mb, 4) if mb else None,
                "strictly_better": sum(1 for x, y in zip(cont, base) if x["slots"] < y["slots"]),
                "worst_ratio": round(max(x["slots"] / y["slots"] for x, y in zip(cont, base)), 3),
            }
        print("seed %d rec=%s lib=%d | d1 %.1f%% (%d/%d) | d2 %.1f%% (%d/%d)" % (
            1000 + s, row["motifs_recovered"], len(lib),
            100 * row["d1"]["reduction_vs_reset"], row["d1"]["strictly_better"], a.prot_n,
            100 * row["d2"]["reduction_vs_reset"], row["d2"]["strictly_better"], a.prot_n), flush=True)
        results.append(row)

    ok = [r for r in results if "d1" in r]
    d1 = [r["d1"]["reduction_vs_reset"] for r in ok]
    d2 = [r["d2"]["reduction_vs_reset"] for r in ok]
    out = {"schema": "OCM_M2_EXT_DISTANCE_V1", "lane": "LANE_M2_TRAVERSAL_CAPITAL_OPUS",
           "substrate": {"primitives": list(prims), "P": len(prims), "max_length": 8,
                         "note": "RESEARCH ANALOGUE, not the registered grammar; the "
                                 "solver is EXACT_MATCH-controlled against M.solve at P=4"},
           "design": {"motifs": a.motifs, "tokens_k": a.tokens, "train_n": a.train_n,
                      "protected_per_grade": a.prot_n,
                      "matched": "identical alphabet, k, train_n and selection rule; "
                                 "only arrangement distance differs"},
           "seeds": results,
           "mean_reduction_d1": round(statistics.fmean(d1), 4) if d1 else None,
           "mean_reduction_d2": round(statistics.fmean(d2), 4) if d2 else None,
           "d2_positive_seeds": sum(1 for x in d2 if x > 0),
           "d1_positive_seeds": sum(1 for x in d1 if x > 0),
           "terminal": ("BENEFIT_SURVIVES_AT_D2" if d2 and statistics.fmean(d2) > 0
                        and sum(1 for x in d2 if x > 0) > len(d2) / 2
                        else "BENEFIT_COLLAPSES_AT_D2" if d2 else "CANNOT_CHECK")}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print("\nmean reduction d1=%s d2=%s | d2 positive in %s/%s seeds\nTERMINAL: %s" % (
        out["mean_reduction_d1"], out["mean_reduction_d2"],
        out["d2_positive_seeds"], len(d2), out["terminal"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
