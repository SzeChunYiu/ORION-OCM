"""RV-377-028: fast exact evaluator + functional-equivalence cache (FEC) + checkpointed regularized evolution for the
authorized 10^6-evaluation dense-form recovery runs.

The fast evaluator compiles a candidate's trees into Python closures and replays EXACTLY the semantics of blind.ev /
blind.run_candidate (same fixed-point ops, same store semantics, same event protocol, same score) without the charged
Machine; charged costs are not computed inside the search loop (tie-break is program size, declared). Every elite and
winner is re-evaluated with the charged Machine at the end and the scores are asserted equal (fidelity check in the
receipt). test_gmi_microscope.py checks fidelity on random candidates.

FEC (AutoML-Zero, Real et al. 2020): a probe signature (outputs on the seen inputs after 5 and 10 events on the first
target, plus the final cells) keys a cache of full scores; a candidate whose probe signature was seen before is scored
from the cache (counted as an FEC hit, not as an evaluation).
"""
from __future__ import annotations

import json
import os
import random
import time

from . import blind
from .core import clamp, fx

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
K = {"k0": 0, "k1": fx(1.0), "kh": fx(0.5), "kq": fx(0.25)}
ONE = fx(1.0)


def compile_tree(t):
    if isinstance(t, str):
        if t[0] == "x" and t[1:].isdigit():
            i = int(t[1:]); return lambda c, e: ONE if e["bits"][i] else 0
        if t[0] == "c" and t[1:].isdigit():
            i = int(t[1:]); return lambda c, e: c[i]
        if t == "L":
            return lambda c, e: e["st"].get(e["x"], 0)
        if t in K:
            v = K[t]; return lambda c, e: v
        if t in ("y", "e", "out"):
            name = t; return lambda c, e: e.get(name, 0)
        raise KeyError(t)
    op = t[0]
    if op == "SEL":
        a, b, d = compile_tree(t[1]), compile_tree(t[2]), compile_tree(t[3])
        return lambda c, e: b(c, e) if a(c, e) > 0 else d(c, e)
    if op in ("AND", "OR", "XOR", "GT", "ADD", "SUB", "MUL"):
        a, b = compile_tree(t[1]), compile_tree(t[2])
        if op == "AND": return lambda c, e: ONE if (a(c, e) > 0 and b(c, e) > 0) else 0
        if op == "OR": return lambda c, e: ONE if (a(c, e) > 0 or b(c, e) > 0) else 0
        if op == "XOR": return lambda c, e: ONE if ((a(c, e) > 0) != (b(c, e) > 0)) else 0
        if op == "GT": return lambda c, e: ONE if a(c, e) > b(c, e) else 0
        if op == "ADD": return lambda c, e: clamp(a(c, e) + b(c, e))
        if op == "SUB": return lambda c, e: clamp(a(c, e) - b(c, e))
        if op == "MUL": return lambda c, e: clamp((a(c, e) * b(c, e) + 8) >> 4)
    if op in ("THRESH", "NOT", "NEG"):
        a = compile_tree(t[1])
        if op == "THRESH": return lambda c, e: (lambda v: v if v > 0 else 0)(a(c, e))
        if op == "NOT": return lambda c, e: 0 if a(c, e) > 0 else ONE
        if op == "NEG": return lambda c, e: clamp(-a(c, e))
    raise KeyError(op)


def compile_candidate(cand):
    return compile_tree(cand["f"]), [(tc, compile_tree(ex)) for tc, ex in cand["g"]]


def _bits(x, n):
    return [(x >> i) & 1 for i in range(n)]


def fast_score(fc, eco, target, n_bits, probe=None):
    """Replay of blind.run_candidate for one target; returns (score, probe_signature or None)."""
    f, writes = fc
    train, all_x, events, kind = eco["train"], eco["all_x"], eco["events"], eco.get("kind", "smooth")
    cells = [0, 0, 0, 0]; st = {}
    sig = [] if probe else None
    n_ev = probe if probe else events
    for t in range(n_ev):
        x = train[t % len(train)]; y = target[x]
        env = {"x": x, "bits": _bits(x, n_bits), "st": st}
        out = f(cells, env)
        yy = y if kind != "bind" else (ONE if y else 0)
        env["y"] = yy; env["out"] = out; env["e"] = clamp(out - yy)
        for tc, ex in writes:
            val = ex(cells, env)
            if tc == "INSERT": st[x] = val
            else: cells[int(tc[1])] = clamp(val)
        if probe and (t + 1) % 5 == 0:
            sig.extend(f(cells, {"x": xx, "bits": _bits(xx, n_bits), "st": st}) for xx in train)
    if probe:
        sig.extend(cells); return None, tuple(sig)
    if kind == "bind":
        correct = sum(int((f(cells, {"x": x, "bits": _bits(x, n_bits), "st": st}) > fx(0.5)) == bool(target[x])) for x in all_x)
        return round(correct / len(all_x), 4), None
    err = 0
    for x in all_x:
        err += abs(f(cells, {"x": x, "bits": _bits(x, n_bits), "st": st}) - target[x])
    return round(max(0.0, 1.0 - err / 16 / len(all_x) / 1.5), 4), None


def fast_run_candidate(cand, eco, n_bits=8):
    fc = compile_candidate(cand)
    if eco.get("kind") == "smooth_div":
        scores = [fast_score(fc, dict(eco, kind="smooth"), t, n_bits)[0] for t in eco["targets"]]
        return round(sum(scores) / len(scores), 4)
    return fast_score(fc, eco, eco["target"], n_bits)[0]


def size(t):
    return 1 if isinstance(t, str) else 1 + sum(size(x) for x in t[1:])


def cand_size(cand):
    return size(cand["f"]) + sum(1 + size(ex) for _, ex in cand["g"])


def evolve_fast(eco, rng, seed, P=100, S=25, evaluations=1000000, log_every=10000, ckpt_path=None, ckpt_every=50000, n_bits=8, resume=None):
    """Regularized evolution (Real et al. 2019 Alg. 1) with the fast evaluator, genotype cache, FEC and checkpoints.
    fitness key = (score, -size). Returns (best, pop, traj, n_eval, hits, fec_hits)."""
    from collections import deque
    probe_target = eco["targets"][0] if eco.get("kind") == "smooth_div" else eco["target"]
    probe_eco = dict(eco, kind="smooth") if eco.get("kind") == "smooth_div" else eco
    geno = {}; fec = {}; n_eval = 0; hits = 0; fec_hits = 0
    def ev_c(c):
        nonlocal n_eval, hits, fec_hits
        k = json.dumps(c, sort_keys=True)
        if k in geno: hits += 1; return geno[k]
        fc = compile_candidate(c)
        _, sig = fast_score(fc, probe_eco, probe_target, n_bits, probe=10)
        if sig in fec:
            fec_hits += 1; s = fec[sig]; geno[k] = s; return s
        if eco.get("kind") == "smooth_div":
            scores = [fast_score(fc, dict(eco, kind="smooth"), t, n_bits)[0] for t in eco["targets"]]
            s = round(sum(scores) / len(scores), 4)
        else:
            s = fast_score(fc, eco, eco["target"], n_bits)[0]
        n_eval += 1; geno[k] = s; fec[sig] = s; return s
    key = lambda cr: (cr[1], -cand_size(cr[0]))
    pop = deque(); traj = []; next_log = log_every; next_ckpt = ckpt_every; t0 = time.time()
    if resume:
        pop = deque((c, s) for c, s in resume["pop"]); best = tuple(resume["best"]); traj = [tuple(x) for x in resume["traj"]]
        n_eval = resume["n_eval"]; hits = resume["hits"]; fec_hits = resume["fec_hits"]; rng.setstate(_rng_from(resume["rng"]))
        for c, s in pop: geno[json.dumps(c, sort_keys=True)] = s
        next_log = (n_eval // log_every + 1) * log_every; next_ckpt = (n_eval // ckpt_every + 1) * ckpt_every
    else:
        while len(pop) < P:
            c = blind.rand_candidate(rng); pop.append((c, ev_c(c)))
        best = max(pop, key=key); traj = [(n_eval, best[1])]
    while n_eval < evaluations:
        sample = [pop[rng.randrange(len(pop))] for _ in range(S)]
        parent = max(sample, key=key)
        child = blind.mutate_gp(rng, parent[0]); cr = (child, ev_c(child))
        pop.append(cr); pop.popleft()
        if key(cr) > key(best): best = cr
        if n_eval >= next_log:
            traj.append((n_eval, best[1])); next_log += log_every
            print(json.dumps({"n_eval": n_eval, "best": best[1], "geno_hits": hits, "fec_hits": fec_hits, "sec": round(time.time() - t0, 1)}), flush=True)
        if ckpt_path and n_eval >= next_ckpt:
            json.dump({"pop": list(pop), "best": list(best), "traj": traj, "n_eval": n_eval, "hits": hits, "fec_hits": fec_hits, "rng": _rng_to(rng.getstate()), "seed": seed},
                      open(ckpt_path, "w")); next_ckpt += ckpt_every
    traj.append((n_eval, best[1]))
    return best, list(pop), traj, n_eval, hits, fec_hits


def _rng_to(state):
    return [state[0], list(state[1]), state[2]]


def _rng_from(s):
    return (s[0], tuple(s[1]), s[2])


def main_evolve_fast(seed, evaluations=1000000, tag="RUN9_SMOOTH8_DIV_REGEVO_FEC", P=100, S=25, diversity=True, resume=False):
    """RV-377-028: the RV-023 search at 10^6 evaluations with FEC, fast evaluator and checkpoints (authorized compute)."""
    blind.G_DEPTH = 3; blind.set_bits(8)
    rng = random.Random(seed)
    e = blind.ecology_div() if diversity else blind.ecologies(run4=True)["E_smooth8"]
    ckpt = os.path.join(RES, f"CKPT_{tag}_S{seed}.json")
    res = json.load(open(ckpt)) if resume and os.path.exists(ckpt) else None
    t0 = time.time()
    best, pop, traj, n_eval, hits, fec_hits = evolve_fast(e, rng, seed, P=P, S=S, evaluations=evaluations, ckpt_path=ckpt, resume=res)
    wall = time.time() - t0
    evaluate = blind.run_candidate_div if diversity else blind.run_candidate
    theta = blind.THETA_SMOOTH
    def canon(c, s):
        c2, dropped = blind.eliminate_dead_writes(c); r2 = evaluate(c2, e, seed)
        return c2, r2, dropped, r2["score"] == s
    seen = set(); winners = []; top = []; fidelity = []
    ranked = sorted(pop + [best], key=lambda cr: cr[1], reverse=True)
    for c, s in ranked:
        k = json.dumps(c, sort_keys=True)
        if k in seen: continue
        seen.add(k)
        if s >= theta:
            c2, r2, dropped, ok = canon(c, s); fidelity.append(ok)
            winners.append({"score": s, "charged_score": r2["score"], "class": blind.classify_locality_v2(r2, c2), "max_writes": r2["max_writes"], "used_store": r2["used_store"], "n_fx_cells_written": r2["n_fx_cells_written"], "dropped_writes": dropped, "f": json.dumps(c2["f"]), "g": json.dumps(c2["g"])})
    for c, s in ranked[:3]:
        c2, r2, dropped, ok = canon(c, s); fidelity.append(ok)
        top.append({"score": s, "charged_score": r2["score"], "class": blind.classify_locality_v2(r2, c2), "max_writes": r2["max_writes"], "used_store": r2["used_store"], "n_fx_cells_written": r2["n_fx_cells_written"], "f": json.dumps(c2["f"]), "g": json.dumps(c2["g"])})
    classes = [w["class"] for w in winners]
    frac_dense = (sum(1 for c in classes if c.startswith("NUMERIC_DENSE")) / len(classes)) if classes else None
    planted = evaluate(blind.eliminate_dead_writes(blind.PLANTED_LEARNER_SMOOTH8_LR4)[0], e, seed)
    receipt = {"schema": "StageFBlindRecoveryRegEvoFECV1", "status": "EXECUTED_AT_TINY_SCOPE", "issue": 377, "revival_record": "RV-377-028", "seed": seed, "run_tag": tag,
               "search_family": f"regularized (aging) evolution, Real et al. 2019 Alg. 1: P={P}, S={S}, Koza subtree mutation on f and g, genotype cache + functional-equivalence cache (probe: 10 events on target 0, outputs on the seen inputs after events 5 and 10, final cells); fast exact evaluator; tie-break by program size",
               "grammar": {"n_bits": 8, "n_cells": blind.N_CELLS, "f_depth": 3, "g_depth": blind.G_DEPTH, "leaves_f": blind.LEAVES_F, "leaves_g": blind.LEAVES_G},
               "existence_certificate": "PLANTED_LEARNER_SMOOTH8_LR4 recomputed in this ecology (see planted_learner_score_in_this_ecology)",
               "ecology": {"kind": e["kind"], "inputs": 256, "train": e["train"], "events": e["events"], "coeffs": list(blind.SMOOTH8_COEFFS), "theta": theta, "diversity_signs": list(e["signs"]) if diversity else None},
               "planted_learner_score_in_this_ecology": planted["score"], "planted_learner_per_target": planted.get("per_target_scores"),
               "n_evaluations": n_eval, "genotype_cache_hits": hits, "fec_hits": fec_hits, "wall_seconds_this_process": round(wall, 1), "resumed_from_checkpoint": bool(res),
               "best_score": best[1], "best_score_trajectory": traj, "fast_vs_charged_fidelity_all_equal": all(fidelity), "n_fidelity_checks": len(fidelity),
               "n_winners_at_theta": len(winners), "winner_classes": classes, "fraction_numeric_dense_among_winners": frac_dense, "winners": winners[:10], "top_elites_canonicalized": top,
               "claim_ceiling": "E2 blind recovery at tiny scope with a declared population search family at 1e6 evaluations; one grammar; classification post hoc after dead-write elimination"}
    receipt["receipt_sha256"] = blind.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_F_BLIND_RECOVERY_{tag}_S{seed}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({k: receipt[k] for k in ("seed", "n_evaluations", "genotype_cache_hits", "fec_hits", "best_score", "n_winners_at_theta", "winner_classes", "fast_vs_charged_fidelity_all_equal")}), flush=True)
    for t in top: print("  ", t["score"], t["class"], "writes", t["max_writes"], "cells", t["n_fx_cells_written"], "f=", t["f"], "g=", t["g"], flush=True)
    return receipt


if __name__ == "__main__":
    import sys
    seed = int(sys.argv[1]); evals = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
    main_evolve_fast(seed, evals, resume=("--resume" in sys.argv))
