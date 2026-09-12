"""Stage F — blind known-morphology recovery at tiny scope (issue #377 §13, GMI-D6) plus the
revision-axis handover test that Stage E could not observe (PH-REV, carried over).

NEUTRAL SEARCH SPACE (no architecture labels, no update-law slot names): a candidate is a pair of
programs (f, g) over one grammar of typed nodes. f maps (input bits, state cells, store lookup) to an
output; g maps (input, label/loss, state) to state writes and/or a store insert. Both are random
trees of depth <= 3 over the SAME node menu; which nodes a candidate uses (numeric vs discrete,
store vs cells, how many cells it writes) is what the post-hoc classifier reads.

Node menu (identical for f and g): input bits x0..x3 (as fx), cells c0..c3 (fx), store lookup L
(value stored under the current input, 0 if none), constants, ADD SUB MUL GT AND OR XOR NOT NEG
THRESH SEL, label y (only in g), error e = out - y (only in g), out (only in g). g's output is a
list of writes: (cell_i <- expr) and/or (INSERT key<-x, value<-expr). Everything is charged under
basis B0 (numeric-native, store emulated) — one column, so charged cost is comparable across
candidates.

ECOLOGIES (frozen before running):
  E_bind  : 4 inputs (x in 0..3), y = BINDING_TARGET(x), all 4 inputs seen in training, feedback =
            exact (x, y) pair; score = accuracy on all 4 after 8 events.
  E_smooth: 16 inputs (x in 0..15, 4 bits), y = fx(0.25*b0 + 0.5*b1 - 0.25*b2 + 0.5*b3) (a linear
            numeric target), TRAINING on 8 inputs only, feedback = (x, y) with the scalar error e
            available in g; score = 1 - mean|out - y|/1.5 over ALL 16 inputs after 16 events
            (generalization to 8 unseen inputs is required).
SEARCH: N random candidates per ecology (seeded), then hill-climb from the top-k by single-node
mutation; the search receives only the score and the charged cost; it never sees a class label.
FROZEN PREDICTIONS (from ECOLOGY_AXES_V2 / MORPHOLOGY_SIGNATURES_V2):
  F1  E_bind winners classify to store/local discrete forms (store insert used; writes/event <= 2)
      — the M1/M5 class — and NOT to dense-numeric forms.
  F2  E_smooth winners classify to numeric dense forms (no store use, >= 3 fx cells written per
      event) — the M4 class.
  F3  (PH-REV carried over) if any local/store candidate reaches theta in E_smooth, the handover
      is computed from its cost vs the dense winners; if none does, the handover is reported
      NOT_OBSERVABLE (local forms cannot generalize there — itself the predicted phase fact).
Writes microscopes/results/STAGE_F_BLIND_RECOVERY_V1.json and STAGE_F_REPORT_V1.md.
"""
from __future__ import annotations

import json
import os
import random

from . import bases
from .core import FX_ONE, Machine, clamp, fx, sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
BINDING_TARGET = {0: 1, 1: 0, 2: 1, 3: 1}
N_RANDOM = 3000
TOPK = 12
HILL_STEPS = 40
N_CELLS = 4
G_DEPTH = 2  # frozen V1..RUN4 update-expression depth; RV-377-016 declares G_DEPTH = 3 (learning-rate scaling becomes expressible)
THETA_BIND = 1.0
THETA_SMOOTH = 0.85

N_BITS = 4
LEAVES_F = ["x0", "x1", "x2", "x3", "c0", "c1", "c2", "c3", "L", "k0", "k1", "kh", "kq"]
LEAVES_G = LEAVES_F + ["y", "e", "out"]


def set_bits(n):
    global N_BITS, LEAVES_F, LEAVES_G
    N_BITS = n
    LEAVES_F = [f"x{i}" for i in range(n)] + ["c0", "c1", "c2", "c3", "L", "k0", "k1", "kh", "kq"]
    LEAVES_G = LEAVES_F + ["y", "e", "out"]
BIN = ["ADD", "SUB", "MUL", "GT", "AND", "OR", "XOR"]
UN = ["THRESH", "NOT", "NEG"]


def rand_tree(rng, depth, leaves):
    if depth == 0 or rng.random() < 0.3:
        return rng.choice(leaves)
    r = rng.random()
    if r < 0.6:
        return [rng.choice(BIN), rand_tree(rng, depth - 1, leaves), rand_tree(rng, depth - 1, leaves)]
    if r < 0.85:
        return [rng.choice(UN), rand_tree(rng, depth - 1, leaves)]
    return ["SEL", rand_tree(rng, depth - 1, leaves), rand_tree(rng, depth - 1, leaves), rand_tree(rng, depth - 1, leaves)]


def rand_candidate(rng):
    f = rand_tree(rng, 3, LEAVES_F)
    n_writes = rng.choice([1, 1, 2, 3, 4])
    writes = []
    for _ in range(n_writes):
        if rng.random() < 0.3:
            writes.append(["INSERT", rand_tree(rng, G_DEPTH, LEAVES_G)])
        else:
            writes.append([f"c{rng.randrange(N_CELLS)}", rand_tree(rng, G_DEPTH, LEAVES_G)])
    return {"f": f, "g": writes}


def mutate(rng, cand):
    c = json.loads(json.dumps(cand))
    if rng.random() < 0.5:
        c["f"] = rand_tree(rng, 3, LEAVES_F)
    else:
        i = rng.randrange(len(c["g"]))
        if rng.random() < 0.3:
            c["g"][i] = ["INSERT", rand_tree(rng, G_DEPTH, LEAVES_G)]
        else:
            c["g"][i] = [f"c{rng.randrange(N_CELLS)}", rand_tree(rng, G_DEPTH, LEAVES_G)]
    return c


def ev(M, t, env):
    if isinstance(t, str):
        if t.startswith("x"):
            return fx(1.0) if env["bits"][int(t[1])] else 0
        if t.startswith("c"):
            return M.read(t)
        if t == "L":
            v = M.op("S_LOOKUP", "st", env["x"])
            return 0 if v is None else v
        return {"k0": 0, "k1": fx(1.0), "kh": fx(0.5), "kq": fx(0.25), "y": env.get("y", 0), "e": env.get("e", 0), "out": env.get("out", 0)}[t]
    op = t[0]
    if op == "SEL":
        return M.op("SEL", 1 if ev(M, t[1], env) > 0 else 0, ev(M, t[2], env), ev(M, t[3], env))
    if op in ("AND", "OR", "XOR"):
        a, b = ev(M, t[1], env), ev(M, t[2], env)
        return fx(1.0) if M.op(op, a > 0, b > 0) else 0
    if op == "NOT":
        return fx(1.0) if M.op("NOT", ev(M, t[1], env) > 0) else 0
    if op == "GT":
        return fx(1.0) if M.op("GT", ev(M, t[1], env), ev(M, t[2], env)) else 0
    if op in ("ADD", "SUB", "MUL"):
        return M.op(op, ev(M, t[1], env), ev(M, t[2], env))
    if op in ("THRESH", "NEG"):
        return M.op(op, ev(M, t[1], env))
    raise KeyError(op)


def run_candidate(cand, ecology, seed=0):
    M = Machine(bases.B0, seed=seed)
    for i in range(N_CELLS):
        M.declare(f"c{i}", "fx", 0)
    M.declare_store("st")
    M.declare_program(8)
    train, all_x, target, events, kind = ecology["train"], ecology["all_x"], ecology["target"], ecology["events"], ecology["kind"]
    bits = lambda x: [(x >> i) & 1 for i in range(N_BITS)]
    max_writes = 0
    used_store = False
    fx_writes = set()
    for t in range(events):
        x = train[t % len(train)]
        y = target[x]
        M.phase("exec")
        env = {"x": x, "bits": bits(x)}
        out = ev(M, cand["f"], env)
        M.phase("upd")
        env2 = dict(env, y=y if kind == "smooth" else (fx(1.0) if y else 0), out=out)
        env2["e"] = clamp(out - env2["y"])
        for target_cell, expr in cand["g"]:
            val = ev(M, expr, env2)
            if target_cell == "INSERT":
                M.op("S_DELETE", "st", x)
                M.op("S_INSERT", "st", x, val)
                used_store = True
            else:
                M.write(target_cell, val)
                fx_writes.add(target_cell)
        max_writes = max(max_writes, len(M.L.writes_in_event))
        M.end_event()
    M.phase("exec")
    if kind == "bind":
        correct = 0
        for x in all_x:
            out = ev(M, cand["f"], {"x": x, "bits": bits(x)})
            correct += int((out > fx(0.5)) == bool(target[x]))
        score = correct / len(all_x)
    else:
        err = 0.0
        for x in all_x:
            out = ev(M, cand["f"], {"x": x, "bits": bits(x)})
            err += abs(out - target[x]) / FX_ONE
        score = max(0.0, 1.0 - err / len(all_x) / 1.5)
    cost = dict(M.L.c)
    return {"score": round(score, 4), "cost": cost, "max_writes": max_writes, "used_store": used_store, "n_fx_cells_written": len(fx_writes)}


def _reads(t, acc):
    if isinstance(t, str):
        if t.startswith("c") and t[1:].isdigit(): acc.add(t)
        if t == "L": acc.add("L")
        return acc
    for sub in t[1:]: _reads(sub, acc)
    return acc


def eliminate_dead_writes(cand):
    """RV-377-008 instrument: drop g-writes whose target is never read (transitively) on any path to f's output.
    Live set = cells/store read by f, closed under 'a live target's expression reads'. Returns (pruned candidate, n_dropped)."""
    live = _reads(cand["f"], set())
    changed = True
    while changed:
        changed = False
        for target, expr in cand["g"]:
            key = "L" if target == "INSERT" else target
            if key in live:
                before = len(live); _reads(expr, live)
                if len(live) != before: changed = True
    kept = [w for w in cand["g"] if (("L" if w[0] == "INSERT" else w[0]) in live)]
    return {"f": cand["f"], "g": kept}, len(cand["g"]) - len(kept)


def classify_locality(res):
    """RUN3 classifier (declared in CLAIM_LADDER_V2 F'): keyed on write locality and numeric-vs-store use, not on store-primitive use alone."""
    if res["max_writes"] <= 2 and (res["used_store"] or res["n_fx_cells_written"] <= 2):
        return "LOCAL_MEMORY (store or cell-memory; M1/M5 class)"
    if not res["used_store"] and res["n_fx_cells_written"] >= 3:
        return "NUMERIC_DENSE (M4 class)"
    if not res["used_store"]:
        return "NUMERIC_SPARSE"
    return "STORE_PLUS_NUMERIC (hybrid)"


def classify_locality_v2(res, cand=None):
    """RV-377-016 addendum (not used by any committed receipt): adds an INERT class — no live write depends on the
    feedback (e, y, out) — so fixed programs found by search are not reported as memory forms. cand is the
    canonicalized candidate; without it the function falls back to classify_locality."""
    if cand is not None:
        feeds = {"e", "y", "out"}
        live_uses_feedback = any(_reads(expr, set()) is not None and (feeds & set(_leaves(expr))) for _, expr in cand["g"])
        if not live_uses_feedback:
            return "INERT (fixed program; M0/M2 class)"
    return classify_locality(res)


def _leaves(t, acc=None):
    acc = [] if acc is None else acc
    if isinstance(t, str):
        acc.append(t); return acc
    for sub in t[1:]: _leaves(sub, acc)
    return acc


def classify(res):
    """post-hoc label-free class from observables (MORPHOLOGY_SIGNATURES_V2 reading)."""
    if res["used_store"] and res["max_writes"] <= 2:
        return "STORE_LOCAL (M1/M5 class)"
    if not res["used_store"] and res["n_fx_cells_written"] >= 3:
        return "NUMERIC_DENSE (M4 class)"
    if not res["used_store"] and res["n_fx_cells_written"] in (1, 2):
        return "NUMERIC_SPARSE"
    if res["used_store"]:
        return "STORE_PLUS_NUMERIC (hybrid)"
    return "INERT/OTHER"


SMOOTH8_COEFFS = (0.375, -0.625, 0.875, -0.375, 0.125, -0.125, 0.125, 0.125)  # declared before RUN4: the four major coefficients are not expressible from the constant leaves inside a 4-term depth-3 tree
SMOOTH8_TRAIN = sorted({(37 * i + 11) % 256 for i in range(16)})  # 16 seen inputs (deterministic)


def ecologies(run3=False, run4=False):
    if run4:
        tgt = {x: clamp(fx(sum(c * ((x >> i) & 1) for i, c in enumerate(SMOOTH8_COEFFS)))) for x in range(256)}
        return {"E_smooth8": {"kind": "smooth", "train": SMOOTH8_TRAIN, "all_x": list(range(256)), "target": tgt, "events": 32}}
    if run3:
        tgt16 = {x: int(((x * 7) >> 2) & 1) for x in range(16)}  # a 16-input binding target with no simple bit rule
        return {"E_bind16": {"kind": "bind", "train": list(range(16)), "all_x": list(range(16)), "target": tgt16, "events": 32}}
    e_bind = {"kind": "bind", "train": [0, 1, 2, 3], "all_x": [0, 1, 2, 3], "target": BINDING_TARGET, "events": 8}
    tgt = {x: clamp(fx(0.25 * (x & 1) + 0.5 * ((x >> 1) & 1) - 0.25 * ((x >> 2) & 1) + 0.5 * ((x >> 3) & 1))) for x in range(16)}
    e_smooth = {"kind": "smooth", "train": [0, 3, 5, 6, 9, 10, 12, 15], "all_x": list(range(16)), "target": tgt, "events": 16}
    return {"E_bind": e_bind, "E_smooth": e_smooth}


DIVERSITY_SIGNS = ((1, 1, 1, 1), (-1, -1, -1, -1), (1, -1, 1, -1), (-1, 1, -1, 1))  # RV-377-023: four fixed sign patterns on the four MAJOR coefficients


def ecology_div():
    """RV-377-023 task-DIVERSITY ecology E_smooth8_div: the same train set and protocol as E_smooth8, but the candidate is
    scored on FOUR fixed targets (the E_smooth8 coefficients with the major-coefficient signs flipped per DIVERSITY_SIGNS,
    minor coefficients unchanged); fitness = mean score. A fixed program cannot fit all four; a learner fits each."""
    targets = []
    for signs in DIVERSITY_SIGNS:
        coeffs = [c * (signs[i] if i < 4 else 1) for i, c in enumerate(SMOOTH8_COEFFS)]
        targets.append({x: clamp(fx(sum(c * ((x >> i) & 1) for i, c in enumerate(coeffs)))) for x in range(256)})
    return {"kind": "smooth_div", "train": SMOOTH8_TRAIN, "all_x": list(range(256)), "targets": targets, "target": targets[0], "events": 32, "signs": DIVERSITY_SIGNS}


def run_candidate_div(cand, eco, seed=0):
    """Mean over the diversity targets of run_candidate; writes/store flags aggregated by max/any; cost summed."""
    rs = [run_candidate(cand, dict(eco, kind="smooth", target=t), seed) for t in eco["targets"]]
    cost = {}
    for r in rs:
        for k, v in r["cost"].items(): cost[k] = cost.get(k, 0) + v
    return {"score": round(sum(r["score"] for r in rs) / len(rs), 4), "per_target_scores": [r["score"] for r in rs], "cost": cost,
            "max_writes": max(r["max_writes"] for r in rs), "used_store": any(r["used_store"] for r in rs), "n_fx_cells_written": max(r["n_fx_cells_written"] for r in rs)}


PLANTED_LEARNER_SMOOTH8 = {  # hand-written 4-coefficient gradient learner inside the SAME grammar (depth 3, 4 writes): existence check for RV-377-015
    "f": ["ADD", ["ADD", ["MUL", "c0", "x0"], ["MUL", "c1", "x1"]], ["ADD", ["MUL", "c2", "x2"], ["MUL", "c3", "x3"]]],
    "g": [["c0", ["SUB", "c0", ["MUL", "e", "x0"]]], ["c1", ["SUB", "c1", ["MUL", "e", "x1"]]], ["c2", ["SUB", "c2", ["MUL", "e", "x2"]]], ["c3", ["SUB", "c3", ["MUL", "e", "x3"]]]],
}


PLANTED_LEARNER_SMOOTH8_LR4 = {  # the RV-377-015 diagnosis learner (learning rate 1/4 via the kq leaf, update depth 3): scores 0.9258 on E_smooth8 (the existence certificate cited by RUN6/RUN7)
    "f": ["ADD", ["ADD", ["MUL", "c0", "x0"], ["MUL", "c1", "x1"]], ["ADD", ["MUL", "c2", "x2"], ["MUL", "c3", "x3"]]],
    "g": [[f"c{i}", ["SUB", f"c{i}", ["MUL", ["MUL", "e", "kq"], f"x{i}"]]] for i in range(4)],
}


def planted_check(seed=3):
    """Evaluate the planted learner on E_smooth8 (no search). Returns its run_candidate result and class after dead-write elimination."""
    set_bits(8)
    e = ecologies(run4=True)["E_smooth8"]
    c, dropped = eliminate_dead_writes(PLANTED_LEARNER_SMOOTH8)
    r = run_candidate(c, e, seed)
    return {"score": r["score"], "class": classify_locality(r), "max_writes": r["max_writes"], "used_store": r["used_store"], "n_fx_cells_written": r["n_fx_cells_written"], "cost": r["cost"], "dropped_writes": dropped}


def _paths(t, path=()):
    """all node paths of a tree (root first)"""
    yield path, t
    if not isinstance(t, str):
        for i, sub in enumerate(t[1:], 1):
            yield from _paths(sub, path + (i,))


def _replace(t, path, new):
    if not path:
        return new
    t = list(t); t[path[0]] = _replace(t[path[0]], path[1:], new); return t


def mutate_gp(rng, cand, depth_f=3):
    """RV-377-018 declared search family operator (Koza subtree mutation): replace a random subtree of f, or of one
    g-write expression, with a fresh random subtree of the depth that remains at that node; with prob 0.15 replace a
    whole g-write (target cell or INSERT) as before."""
    c = json.loads(json.dumps(cand))
    if rng.random() < 0.5:
        nodes = list(_paths(c["f"])); path, _ = rng.choice(nodes)
        c["f"] = _replace(c["f"], path, rand_tree(rng, max(0, depth_f - len(path)), LEAVES_F))
    else:
        i = rng.randrange(len(c["g"]))
        if rng.random() < 0.15:
            c["g"][i] = ["INSERT", rand_tree(rng, G_DEPTH, LEAVES_G)] if rng.random() < 0.3 else [f"c{rng.randrange(N_CELLS)}", rand_tree(rng, G_DEPTH, LEAVES_G)]
        else:
            nodes = list(_paths(c["g"][i][1])); path, _ = rng.choice(nodes)
            c["g"][i][1] = _replace(c["g"][i][1], path, rand_tree(rng, max(0, G_DEPTH - len(path)), LEAVES_G))
    return c


def evolve(ecology, rng, seed, P=100, S=25, evaluations=100000, log_every=10000, evaluate=None):
    """Regularized (aging) evolution, Real et al. 2019 Alg. 1, with genotype caching; fitness = (score, -charged cost)."""
    from collections import deque
    evaluate = evaluate or run_candidate
    cache = {}; n_eval = 0; hits = 0
    def ev_c(c):
        nonlocal n_eval, hits
        k = json.dumps(c, sort_keys=True)
        if k in cache: hits += 1; return cache[k]
        r = evaluate(c, ecology, seed); cache[k] = r; n_eval += 1; return r
    key = lambda cr: (cr[1]["score"], -sum(cr[1]["cost"].values()))
    pop = deque()
    while len(pop) < P:
        c = rand_candidate(rng); pop.append((c, ev_c(c)))
    best = max(pop, key=key); traj = [(n_eval, best[1]["score"])]; next_log = log_every
    while n_eval < evaluations:
        sample = [pop[rng.randrange(len(pop))] for _ in range(S)]
        parent = max(sample, key=key)
        child = mutate_gp(rng, parent[0]); cr = (child, ev_c(child))
        pop.append(cr); pop.popleft()
        if key(cr) > key(best): best = cr
        if n_eval >= next_log:
            traj.append((n_eval, best[1]["score"])); next_log += log_every
    traj.append((n_eval, best[1]["score"]))
    return best, list(pop), traj, n_eval, hits


def main_evolve(seed, evaluations=100000, tag="RUN7_SMOOTH8_REGEVO", P=100, S=25, diversity=False):
    """RV-377-018: regularized evolution on E_smooth8 with the RV-016 grammar (G_DEPTH 3), dead-write elimination and the
    INERT-aware classifier. Existence certified (planted learner 0.9258). Writes STAGE_F_BLIND_RECOVERY_<tag>_S<seed>.json.
    diversity=True (RV-377-023): the same search on E_smooth8_div (four sign-flipped targets, mean score)."""
    global G_DEPTH
    G_DEPTH = 3; set_bits(8)
    rng = random.Random(seed)
    e = ecology_div() if diversity else ecologies(run4=True)["E_smooth8"]
    evaluate = run_candidate_div if diversity else run_candidate
    best, pop, traj, n_eval, hits = evolve(e, rng, seed, P=P, S=S, evaluations=evaluations, evaluate=evaluate)
    theta = THETA_SMOOTH
    def canon(c, r):
        c2, dropped = eliminate_dead_writes(c); r2 = evaluate(c2, e, seed)
        assert r2["score"] == r["score"]
        return c2, r2, dropped
    winners = []
    seen = set()
    for c, r in sorted(pop + [best], key=lambda cr: cr[1]["score"], reverse=True):
        k = json.dumps(c, sort_keys=True)
        if k in seen: continue
        seen.add(k)
        if r["score"] >= theta:
            c2, r2, dropped = canon(c, r)
            winners.append({"score": r["score"], "class": classify_locality_v2(r2, c2), "max_writes": r2["max_writes"], "used_store": r2["used_store"], "n_fx_cells_written": r2["n_fx_cells_written"], "dropped_writes": dropped, "f": json.dumps(c2["f"]), "g": json.dumps(c2["g"])})
    top = []
    for c, r in sorted(pop + [best], key=lambda cr: cr[1]["score"], reverse=True)[:3]:
        c2, r2, dropped = canon(c, r)
        top.append({"score": r["score"], "class": classify_locality_v2(r2, c2), "max_writes": r2["max_writes"], "used_store": r2["used_store"], "n_fx_cells_written": r2["n_fx_cells_written"], "f": json.dumps(c2["f"]), "g": json.dumps(c2["g"])})
    classes = [w["class"] for w in winners]
    frac_dense = (sum(1 for c in classes if c.startswith("NUMERIC_DENSE")) / len(classes)) if classes else None
    planted = evaluate(eliminate_dead_writes(PLANTED_LEARNER_SMOOTH8_LR4)[0], e, seed)  # existence certificate recomputed in the run's own ecology
    receipt = {"schema": "StageFBlindRecoveryRegEvoV1", "status": "EXECUTED_AT_TINY_SCOPE", "issue": 377, "revival_record": "RV-377-023" if diversity else "RV-377-018", "seed": seed, "run_tag": tag,
               "search_family": f"regularized (aging) evolution, Real et al. 2019 Alg. 1: P={P}, S={S}, Koza subtree mutation on f and g, genotype cache; fitness (score, -charged cost)",
               "grammar": {"n_bits": 8, "n_cells": N_CELLS, "f_depth": 3, "g_depth": G_DEPTH, "leaves_f": LEAVES_F, "leaves_g": LEAVES_G}, "existence_certificate": "planted 4-coefficient learning-rate-1/4 learner PLANTED_LEARNER_SMOOTH8_LR4 (RV-377-015 diagnosis): 0.9258 on E_smooth8; see planted_learner_score_in_this_ecology",
               "ecology": {"kind": e["kind"], "inputs": 256, "train": e["train"], "events": e["events"], "coeffs": list(SMOOTH8_COEFFS), "theta": theta, "diversity_signs": list(e["signs"]) if diversity else None},
               "planted_learner_score_in_this_ecology": planted["score"], "planted_learner_per_target": planted.get("per_target_scores"),
               "n_evaluations": n_eval, "cache_hits": hits, "best_score": best[1]["score"], "best_score_trajectory": traj,
               "n_winners_at_theta": len(winners), "winner_classes": classes, "fraction_numeric_dense_among_winners": frac_dense, "winners": winners[:10], "top_elites_canonicalized": top,
               "claim_ceiling": "E2 blind recovery at tiny scope with a declared population search family; one grammar; classification post hoc after dead-write elimination"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_F_BLIND_RECOVERY_{tag}_S{seed}.json"), "w"), indent=1, sort_keys=True, default=str)
    print(json.dumps({k: receipt[k] for k in ("seed", "n_evaluations", "cache_hits", "best_score", "n_winners_at_theta", "winner_classes")}))
    print("trajectory:", traj)
    for t in top: print("  ", t["score"], t["class"], "writes", t["max_writes"], "cells", t["n_fx_cells_written"], "store", t["used_store"])
    return receipt


def search(ecology, rng, seed):
    pop = [rand_candidate(rng) for _ in range(N_RANDOM)]
    scored = []
    for c in pop:
        r = run_candidate(c, ecology, seed)
        scored.append((r["score"], -sum(r["cost"].values()), c, r))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    elites = scored[:TOPK]
    for _ in range(HILL_STEPS):
        new = []
        for s, negc, c, r in elites:
            m = mutate(rng, c)
            rm = run_candidate(m, ecology, seed)
            cand = (rm["score"], -sum(rm["cost"].values()), m, rm)
            new.append(max((s, negc, c, r), cand, key=lambda t: (t[0], t[1])))
        elites = sorted(new, key=lambda t: (t[0], t[1]), reverse=True)
    return elites, scored


def main(seed=0, n_random=None, hill_steps=None, tag="V1", run3=False, run4=False, dwe=False, g_depth=2):
    global N_RANDOM, HILL_STEPS, G_DEPTH
    G_DEPTH = g_depth
    if n_random: N_RANDOM = n_random
    if hill_steps: HILL_STEPS = hill_steps
    set_bits(8 if run4 else 4)
    rng = random.Random(seed)
    eco = ecologies(run3=run3, run4=run4)
    cls_fn = classify_locality if (run3 or run4) else classify
    out = {}
    for name, e in eco.items():
        elites, scored = search(e, rng, seed)
        theta = THETA_BIND if e["kind"] == "bind" else THETA_SMOOTH
        winners = [(s, c, r) for s, _, c, r in elites if s >= theta]
        dwe_log = []
        if dwe:  # RV-377-011: canonicalize (dead-write elimination) BEFORE classification; score must be unchanged
            pruned = []
            for s, c, r in winners:
                c2, dropped = eliminate_dead_writes(c)
                r2 = run_candidate(c2, e, seed)
                assert r2["score"] == s, (s, r2["score"])
                dwe_log.append({"dropped_writes": dropped, "writes_before": r["max_writes"], "writes_after": r2["max_writes"], "class_before": cls_fn(r), "class_after": cls_fn(r2)})
                pruned.append((s, c2, r2))
            winners = pruned
        classes = [cls_fn(r) for _, _, r in winners]
        out[name] = {"n_random": N_RANDOM, "hill_steps": HILL_STEPS, "topk": TOPK, "theta": theta, "best_score": elites[0][0],
                     "top_elites": [{"score": s_, "class": cls_fn(r_), "max_writes": r_["max_writes"], "used_store": r_["used_store"], "n_fx_cells_written": r_["n_fx_cells_written"], "f": json.dumps(c_["f"]), "g": json.dumps(c_["g"])} for s_, _, c_, r_ in elites[:3]],
                     "n_winners_at_theta": len(winners), "winner_classes": classes,
                     "winner_details": [{"score": s, "class": cls_fn(r), "max_writes": r["max_writes"], "used_store": r["used_store"], "n_fx_cells_written": r["n_fx_cells_written"], "cost": r["cost"], "f": json.dumps(c["f"]), "g": json.dumps(c["g"])} for s, c, r in winners[:6]],
                     "random_baseline_fraction_at_theta": sum(1 for s, _, _, _ in scored if s >= theta) / N_RANDOM, "dead_write_elimination": dwe_log}
    def frac(name, cls_prefix):
        cl = out[name]["winner_classes"]
        return (sum(1 for c in cl if c.startswith(cls_prefix)) / len(cl)) if cl else None
    if run4:
        f1 = None; f1_dense = None; f2 = frac("E_smooth8", "NUMERIC_DENSE"); f2_store = frac("E_smooth8", "LOCAL_MEMORY")
    elif run3:
        f1 = frac("E_bind16", "LOCAL_MEMORY"); f1_dense = frac("E_bind16", "NUMERIC_DENSE"); f2 = None; f2_store = None
    else:
        f1 = frac("E_bind", "STORE_LOCAL"); f1_dense = frac("E_bind", "NUMERIC_DENSE")
        f2 = frac("E_smooth", "NUMERIC_DENSE"); f2_store = frac("E_smooth", "STORE_LOCAL")
    verdict = {
        "F1_bind_winners_store_local": {"fraction_store_local": f1, "fraction_numeric_dense": f1_dense, "holds": (f1 is not None and f1 >= 0.5 and (f1_dense or 0) < 0.5)},
        "F2_smooth_winners_numeric_dense": {"fraction_numeric_dense": f2, "fraction_store_local": f2_store, "holds": (f2 is not None and f2 >= 0.5 and (f2_store or 0) < 0.5)},
        "F3_handover": "NOT_OBSERVABLE__NO_STORE_LOCAL_CANDIDATE_REACHED_THETA_IN_E_SMOOTH" if (f2_store in (None, 0.0)) else "STORE_LOCAL_CANDIDATES_REACHED_THETA_IN_E_SMOOTH (see winner_details; handover computable)",
    }
    receipt = {"schema": "StageFBlindRecoveryV1", "status": "EXECUTED_AT_TINY_SCOPE", "issue": 377, "seed": seed, "run_tag": tag, "declared": "V1 = frozen budget (3000/40); RUN2 = declared exploratory re-run at 4x budget after V1 returned no E_smooth winner; V1 is preserved and remains the frozen result; RECLASS_RUN3 = identical replay of RUN3 (seed 2, 6000/80) with dead-write elimination before classification (RV-377-011/008); RUN4_SMOOTH8 = E_smooth8 (256 inputs, 16 seen, 8-bit leaves, declared coefficients) at 12000/160 with dead-write elimination (RV-377-011/007)", "dead_write_elimination": dwe, "n_bits": N_BITS, "g_depth": G_DEPTH, "smooth8_coeffs": list(SMOOTH8_COEFFS) if run4 else None, "ecologies": {k: {kk: vv for kk, vv in v.items() if kk != "target"} for k, v in eco.items()},
               "search": "random N + hill-climb from top-k by single-node mutation; label-free; scored by (score, -charged cost)", "results": out, "verdict": verdict,
               "claim_ceiling": "E2 exploratory at tiny scope, single search family, one basis column (B0), one seed; post-hoc label-free classification; not a confirmatory blind-recovery result (#377 §13 requires matched generic search parents, multiple encodings and seeds)."}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_F_BLIND_RECOVERY_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    L = ["# Stage F — blind recovery at tiny scope: report V1\n", f"Receipt `microscopes/results/STAGE_F_BLIND_RECOVERY_V1.json` (sha256 `{receipt['receipt_sha256'][:16]}…`).\n",
         f"Search: {N_RANDOM} random candidates + {HILL_STEPS} hill-climb steps from the top {TOPK}, per ecology, seed {seed}; the search saw only (score, charged cost).\n"]
    for name, o in out.items():
        L.append(f"## {name}\nbest score {o['best_score']}, winners at θ={o['theta']}: {o['n_winners_at_theta']} (random-baseline fraction at θ: {o['random_baseline_fraction_at_theta']}); classes: {o['winner_classes']}\n")
        for w in o["winner_details"]:
            L.append(f"- score {w['score']} · {w['class']} · writes/event {w['max_writes']} · store {w['used_store']} · fx cells written {w['n_fx_cells_written']} · cost {w['cost']}\n  f = `{w['f']}`\n  g = `{w['g']}`")
        L.append("")
    L.append("## Verdicts\n" + json.dumps(verdict, indent=1, default=str) + "\n")
    L.append(receipt["claim_ceiling"] + "\n")
    open(os.path.join(RES, f"STAGE_F_REPORT_{tag}.md"), "w").write("\n".join(L) + "\n")
    print(json.dumps(verdict, indent=1, default=str))
    for name, o in out.items():
        print(name, "best", o["best_score"], "winners", o["n_winners_at_theta"], o["winner_classes"], "baseline", o["random_baseline_fraction_at_theta"])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "run2":
        main(seed=1, n_random=12000, hill_steps=160, tag="RUN2")
    elif len(sys.argv) > 1 and sys.argv[1] == "run3":
        main(seed=2, n_random=6000, hill_steps=80, tag="RUN3_BIND16", run3=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "reclass3":
        main(seed=2, n_random=6000, hill_steps=80, tag="RECLASS_RUN3", run3=True, dwe=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "run4":
        main(seed=3, n_random=12000, hill_steps=160, tag="RUN4_SMOOTH8", run4=True, dwe=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "planted":
        print(json.dumps(planted_check(), indent=1))
    elif len(sys.argv) > 1 and sys.argv[1] == "run6":
        main(seed=5, n_random=12000, hill_steps=160, tag="RUN6_SMOOTH8_GDEPTH3", run4=True, dwe=True, g_depth=3)
    elif len(sys.argv) > 1 and sys.argv[1] == "run3b":
        main(seed=4, n_random=6000, hill_steps=80, tag="RUN3B_BIND16_SEED4", run3=True, dwe=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "run7":
        main_evolve(seed=int(sys.argv[2]), evaluations=int(sys.argv[3]) if len(sys.argv) > 3 else 100000)
    elif len(sys.argv) > 1 and sys.argv[1] == "run8":
        # RV-377-023: regularized evolution under task diversity (E_smooth8_div)
        main_evolve(seed=int(sys.argv[2]), evaluations=int(sys.argv[3]) if len(sys.argv) > 3 else 100000, tag="RUN8_SMOOTH8_DIV_REGEVO", diversity=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "run5":
        main(seed=4, n_random=120000, hill_steps=1600, tag="RUN5_SMOOTH8_10X", run4=True, dwe=True)
    else:
        main()
