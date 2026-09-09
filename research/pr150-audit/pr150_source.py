#!/usr/bin/env python3
"""Exploratory synthetic falsification harness for Machine Epistemics evolvability theory V0.

Status: E2 exploratory only. This is not OCM evidence and establishes no neural-network
superiority. It tests qualitative boundary hypotheses about diagnosis cost, causal
factorization, coupling, drift, and lifetime amortization.

Stdlib only; deterministic seeds.
"""
from __future__ import annotations
import argparse, json, math, random, statistics


def entropy(ps):
    return -sum(p * math.log(p + 1e-15, 2) for p in ps if p > 0)


def normalize(xs):
    s = sum(xs)
    return [x / s for x in xs] if s else [1 / len(xs)] * len(xs)


def diagnosis_sweep(seed=20260908, episodes=5000):
    def one(noise, probe_cost):
        rng = random.Random(seed + int(noise * 1000) * 31 + int(probe_cost * 1000))
        F, P = 8, 6
        sig = []
        for f in range(F):
            b = [(f >> i) & 1 for i in range(3)]
            sig.append(b + [b[0] ^ b[1], b[1] ^ b[2], b[0] ^ b[2]])
        cover = [{f} for f in range(F)] + [{0, 1, 2}, {2, 3, 4}, {4, 5, 6}, {0, 6, 7}]
        blind_order = sorted(range(len(cover)), key=lambda j: -len(cover[j]))
        blind, guided, probes, repairs, acc = [], [], [], [], []
        for _ in range(episodes):
            f = rng.randrange(F)
            c = 0
            for j in blind_order:
                c += 1
                if f in cover[j]:
                    break
            blind.append(c)

            post = [1 / F] * F
            used = []
            while max(post) < 0.8 and len(used) < 4:
                h0, best, best_ig = entropy(post), None, -1
                for p in range(P):
                    if p in used:
                        continue
                    py1 = sum(post[g] * ((1-noise) if sig[g][p] else noise) for g in range(F))
                    exp_h = 0.0
                    for y, py in ((1, py1), (0, 1-py1)):
                        if py <= 1e-15:
                            continue
                        py_post = normalize([
                            post[g] * ((1-noise) if sig[g][p] == y else noise)
                            for g in range(F)
                        ])
                        exp_h += py * entropy(py_post)
                    ig = h0 - exp_h
                    if ig > best_ig + 1e-12:
                        best_ig, best = ig, p
                if best is None:
                    break
                y = sig[f][best] if rng.random() > noise else 1 - sig[f][best]
                used.append(best)
                post = normalize([
                    post[g] * ((1-noise) if sig[g][best] == y else noise)
                    for g in range(F)
                ])

            order = sorted(
                range(len(cover)),
                key=lambda j: (-sum(post[g] for g in cover[j]), -len(cover[j]), j),
            )
            rc = 0
            for j in order:
                rc += 1
                if f in cover[j]:
                    break
            guided.append(len(used) * probe_cost + rc)
            probes.append(len(used))
            repairs.append(rc)
            acc.append(max(range(F), key=lambda g: post[g]) == f)
        mb, mg = statistics.mean(blind), statistics.mean(guided)
        return {
            "noise": noise,
            "probe_cost": probe_cost,
            "blind_mean_cost": mb,
            "guided_mean_cost": mg,
            "blind_over_guided": mb / mg,
            "guided_fault_accuracy": sum(acc) / episodes,
            "guided_mean_probes": statistics.mean(probes),
            "guided_mean_repair_evals": statistics.mean(repairs),
        }
    return [one(n, c) for n in (0.05, 0.15, 0.30, 0.45) for c in (0.05, 0.20, 0.80)]


class NK:
    def __init__(self, n, K, rng, scopes=None):
        self.n, self.K = n, K
        if scopes is None:
            scopes = []
            for i in range(n):
                cand = [j for j in range(n) if j != i]
                rng.shuffle(cand)
                scopes.append(tuple([i] + sorted(cand[:K])))
        self.scopes = scopes
        self.tables = [[rng.random() for _ in range(1 << len(sc))] for sc in scopes]
        self.affected = [[] for _ in range(n)]
        for ci, sc in enumerate(scopes):
            for b in sc:
                self.affected[b].append(ci)

    def comp(self, x, i):
        idx = 0
        for p, b in enumerate(self.scopes[i]):
            if (x >> b) & 1:
                idx |= 1 << p
        return self.tables[i][idx]

    def components(self, x):
        return [self.comp(x, i) for i in range(self.n)]

    def fitness(self, x):
        return sum(self.components(x)) / self.n

    def optimum(self):
        return max(self.fitness(x) for x in range(1 << self.n))


def drift_scopes(scopes, n, K, rng, drift):
    out = []
    for i, sc in enumerate(scopes):
        deps = list(sc[1:])
        for idx in range(len(deps)):
            if rng.random() < drift:
                cand = [j for j in range(n) if j != i and j not in deps]
                if cand:
                    deps[idx] = rng.choice(cand)
        uniq = []
        for d in deps:
            if d not in uniq:
                uniq.append(d)
        while len(uniq) < K:
            d = rng.randrange(n)
            if d != i and d not in uniq:
                uniq.append(d)
        out.append(tuple([i] + sorted(uniq[:K])))
    return out


def discover_factorization(land, rng):
    x = rng.randrange(1 << land.n)
    base = land.components(x)
    cost = 1
    inferred = [set() for _ in range(land.n)]
    for bit in range(land.n):
        changed = land.components(x ^ (1 << bit))
        cost += 1
        for i, (u, v) in enumerate(zip(base, changed)):
            if abs(u - v) > 1e-12:
                inferred[bit].add(i)
    return [sorted(s) for s in inferred], cost


def local_search(land, rng, affected, budget=16):
    x = rng.randrange(1 << land.n)
    comps = land.components(x)
    cost = 1.0
    while True:
        best_delta, best_bit, best_changes = 0.0, None, None
        exhausted = False
        for bit in range(land.n):
            inds = affected[bit]
            add = len(inds) / land.n
            if cost + add > budget:
                exhausted = True
                break
            y = x ^ (1 << bit)
            delta, changes = 0.0, []
            for i in inds:
                nv = land.comp(y, i)
                delta += nv - comps[i]
                changes.append((i, nv))
            cost += add
            if delta > best_delta + 1e-12:
                best_delta, best_bit, best_changes = delta, bit, changes
        if best_bit is None:
            break
        x ^= 1 << best_bit
        for i, nv in best_changes:
            comps[i] = nv
        if exhausted or cost >= budget:
            break
    return sum(comps) / land.n, cost


def evolutionary_search(land, rng, budget):
    pop = []
    for _ in range(min(6, budget)):
        x = rng.randrange(1 << land.n)
        pop.append((land.fitness(x), x))
    evals = len(pop)
    while evals < budget:
        pop.sort(reverse=True)
        elites, new = pop[:3], pop[:3]
        while len(new) < 6 and evals < budget:
            _, p = rng.choice(elites)
            y = p ^ (1 << rng.randrange(land.n))
            if rng.random() < 0.2:
                y ^= 1 << rng.randrange(land.n)
            new.append((land.fitness(y), y))
            evals += 1
        pop = new
    return max(pop)[0], evals


def lifetime(seed, K, drift, evo_budget, generations=30, reps=8, n=10):
    master = random.Random(seed)
    rows = []
    for _ in range(reps):
        rng = random.Random(master.randrange(1 << 60))
        scopes, inferred = None, None
        fq, eq = [], []
        fc = ec = 0.0
        rediscoveries = 0
        recalls = []
        for _g in range(generations):
            if scopes is not None and drift:
                scopes = drift_scopes(scopes, n, K, rng, drift)
            land = NK(n, K, rng, scopes=scopes)
            scopes = land.scopes
            opt = land.optimum()

            if inferred is None:
                inferred, c = discover_factorization(land, rng)
                fc += c
                rediscoveries += 1
            else:
                x = rng.randrange(1 << n)
                base = land.components(x)
                fc += 1
                bit = rng.randrange(n)
                changed = land.components(x ^ (1 << bit))
                fc += 1
                observed = {i for i, (u, v) in enumerate(zip(base, changed)) if abs(u-v) > 1e-12}
                if observed != set(inferred[bit]):
                    inferred, c = discover_factorization(land, rng)
                    fc += c
                    rediscoveries += 1

            tp = den = 0
            for bit in range(n):
                true, pred = set(land.affected[bit]), set(inferred[bit])
                tp += len(true & pred)
                den += len(true)
            recalls.append(tp / den)

            f, c = local_search(land, rng, inferred, budget=16)
            fc += c
            e, c = evolutionary_search(land, rng, budget=evo_budget)
            ec += c
            fq.append(f / opt)
            eq.append(e / opt)
        rows.append((statistics.mean(fq), statistics.mean(eq), fc, ec, rediscoveries, statistics.mean(recalls)))
    return {
        "K": K, "drift": drift, "generations": generations, "reps": reps,
        "evolutionary_budget_per_generation": evo_budget,
        "factor_quality_over_optimum": statistics.mean(r[0] for r in rows),
        "evolutionary_quality_over_optimum": statistics.mean(r[1] for r in rows),
        "factor_total_full_equivalent_cost": statistics.mean(r[2] for r in rows),
        "evolutionary_total_full_eval_cost": statistics.mean(r[3] for r in rows),
        "mean_refactorizations": statistics.mean(r[4] for r in rows),
        "mean_structure_recall": statistics.mean(r[5] for r in rows),
    }


def lifetime_sweeps():
    conditions = [(1, 0.0), (2, 0.0), (2, 0.03), (2, 0.10), (5, 0.0), (5, 0.03), (5, 0.10)]
    high = [lifetime(20260908 + K*100 + int(d*1000), K, d, 48) for K, d in conditions]
    matched = [lifetime(999 + K*10 + int(d*100), K, d, 18) for K, d in [(1,0.0),(2,0.0),(2,0.03),(5,0.0)]]
    return {"high_budget_parent": high, "approximately_matched_cost_parent": matched}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    args = ap.parse_args()
    result = {
        "status": "E2_EXPLORATORY_SYNTHETIC_ONLY",
        "claim_authority": "NO_OCM_OR_NEURAL_SUPERIORITY_CLAIM",
        "seed_family": "20260908",
        "diagnosis": diagnosis_sweep(),
        "factorization_lifetime": lifetime_sweeps(),
        "interpretation_rules": [
            "Diagnosis is useful only when saved repair search exceeds probe cost.",
            "Factorization is useful only under a declared quality/resource comparison; it is not universally higher-quality.",
            "Sparse/stable interaction structure permits large evaluation savings; dense coupling reduces or removes the quality advantage.",
            "Drift creates maintenance/refactorization cost and can erase amortization.",
            "Evolutionary search here is not the strongest possible learned black-box parent; parent superiority is not established.",
        ],
    }
    txt = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        open(args.output, "w", encoding="utf-8").write(txt)
    else:
        print(txt)

if __name__ == "__main__":
    main()
