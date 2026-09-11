#!/usr/bin/env python3
"""Expand the RSI natural-failure packet from every completed world on this host.

L6 needs a SLOPE across generations, and a 9-case packet moves by one flipped case. This
lane has ~30 more completed worlds with known outcomes. Labels are assigned by a
MECHANICAL rule from evaluator-side facts (ground truth only -- never exposed to the
diagnoser), so no case is hand-labelled:

    admitted                                   -> C0_NO_FAILURE
    refused, motif recovery incomplete         -> C1_INCOMPLETE_RECOVERY
    refused, recovery complete, 2g > b_min     -> C2_ARRANGEMENT_DEPTH
    no hidden motifs in the ecology            -> C3_UNSTRUCTURED_ECOLOGY
    admitted then harmful under drift          -> C5_ECOLOGY_SHIFT   (not on this host)

Probes are internally computable: composability, guided depth, held-out win rate, CI
shape, MDL compression response (re-mine + re-validate on the registered
validate_generator), and oracle_also_fails from the world's own ORACLE_FAMILY arm.
"""
from __future__ import annotations
import argparse, json, statistics, sys
from fractions import Fraction
from pathlib import Path


def tile_tokens(prog, lib):
    n = len(prog); best = [None] * (n + 1); best[0] = 0
    for i in range(n):
        if best[i] is None: continue
        for f in lib:
            j = i + len(f)
            if j <= n and tuple(prog[i:j]) == tuple(f) and (best[j] is None or best[i] + 1 < best[j]):
                best[j] = best[i] + 1
    return best[n]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--glob", default="*")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "src")); sys.path.insert(0, str(Path(__file__).parent))
    import ocm.learning.methods as M
    from m2_mdl_selection import mdl_select
    budget = M.SearchBudget(slots=200000, max_length=8)
    cum = {}; s = 0
    for L in range(9):
        s += 4 ** L; cum[L] = s

    cases = []
    for d in sorted(Path(a.runs).glob(a.glob)):
        eco_p, dev_p = d / "ECOLOGY.json", d / "dev_state.json"
        if not (eco_p.exists() and dev_p.exists()): continue
        eco, dev = json.loads(eco_p.read_text()), json.loads(dev_p.read_text())
        motifs = {tuple(m) for m in eco.get("hidden_motifs", [])}
        frags = [tuple(f) for f in dev["fragments"]]
        val = eco["streams"]["validation"]
        if not val: continue
        rec = len([f for f in frags if f in motifs])
        # ---- mechanical ground-truth label (evaluator-side; hidden from the diagnoser)
        if not motifs: label = "C3_UNSTRUCTURED_ECOLOGY"
        elif dev["admission"]: label = "C0_NO_FAILURE"
        elif rec < len(motifs): label = "C1_INCOMPLETE_RECOVERY"
        else:
            toks = [r.get("motif_tokens") or 3 for r in val]; k = max(toks)
            T = len(frags) + 4; g = sum(T ** i for i in range(1, k + 1))
            Lmin = min(r["canonical_length"] for r in val); bmin = cum[Lmin - 1] + 1 if Lmin > 0 else 1
            label = "C2_ARRANGEMENT_DEPTH" if 2 * g > bmin else "C4_ESTIMATOR_VARIANCE"
        # ---- internally computable probes
        comp = sum(1 for r in val if tile_tokens(tuple(r["canonical_program"]), frags) is not None) / len(val)
        toks_needed = max((tile_tokens(tuple(r["canonical_program"]), frags) or 9) for r in val)
        att_p = d / "ATTRIBUTION.json"
        if att_p.exists():
            rows = json.loads(att_p.read_text())["all_rows"]
            deltas = [r["baseline_slots"] - r["candidate_slots"] for r in rows]
            mean_d = statistics.fmean(deltas); sd = statistics.pstdev(deltas) if len(deltas) > 1 else 0
            ci_low = mean_d - 1.96 * sd / (len(deltas) ** 0.5)
        else:
            eu = dev.get("eu_admission", {}); mean_d, ci_low = eu.get("mean_delta", 0.0), eu.get("ci95_low", 0.0)
        # mdl_response: re-mine, re-validate, same registered units, same validation stream
        progs = [tuple(r["canonical_program"]) for r in eco["streams"]["train"]]
        mdl = tuple(f for f in mdl_select(progs, cap=16) if 2 <= len(f) <= 8)[:16]
        held = []
        for i, r in enumerate(val):
            nf = tuple(Fraction(x) for x in r["coefficients"])
            while len(nf) > 1 and nf[-1] == 0: nf = nf[:-1]
            held.append(M.PolynomialTask(f"pk:{i}", nf))
        ids = tuple(dev["training_task_ids"])
        def better(lib):
            if not lib: return 0
            rep = M.validate_generator(M.GeneratorMethod(lib, ids), held, budget)
            return sum(1 for r in rep["held_out"] if r["candidate"]["slots"] < r["baseline"]["slots"])
        mb, fb = better(mdl), better(tuple(frags))
        # oracle_also_fails from the world's own calibration arm, if it ran
        of = None; sp = d / "SUMMARY.json"
        if sp.exists():
            arms = json.loads(sp.read_text()).get("arms", {})
            if "ORACLE_FAMILY" in arms and "RESET" in arms:
                of = arms["ORACLE_FAMILY"]["ladder_total"] <= arms["RESET"]["ladder_total"]
        cases.append({"name": d.name, "true_cause": label, "recovered": f"{rec}/{len(motifs)}",
                      "composable_frac": round(comp, 3), "tokens_needed": toks_needed,
                      "better": dev["held_out_strictly_better"], "heldout": dev["validated_on"],
                      "mean_delta": round(mean_d, 1), "ci95_low": round(ci_low, 1),
                      "worst_ratio": 2.0, "mined_max_len": max((len(f) for f in frags), default=0),
                      "mdl_gain": round(mb / max(len(val), 1), 3), "mdl_response": mb - fb,
                      "oracle_fails": bool(of) if of is not None else False, "drift": False})
        print("%-18s %-24s rec=%-6s comp=%.2f tok=%d mdl_resp=%+d oracle_fails=%s" % (
            d.name, label, cases[-1]["recovered"], comp, toks_needed, mb - fb, of), flush=True)
    Path(a.out).write_text(json.dumps({"schema": "OCM_RSI_PACKET_V2", "cases": cases}, indent=1))
    print("packet:", len(cases), "cases ->", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
