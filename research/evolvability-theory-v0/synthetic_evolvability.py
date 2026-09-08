#!/usr/bin/env python3
"""Exploratory synthetic falsification harness for Machine Epistemics evolvability theory V0.2.

Status: E2 exploratory only. This is not OCM evidence and establishes no superiority
over neural, AutoML, causal-discovery, active-diagnosis, or open-ended-search parents.

The harness tests:
1. diagnosis value under probe noise/cost;
2. factorization/coupling/drift phase behavior;
3. an information-theoretic self-identifiability lower bound (Fano);
4. learning a self-model from resolved interventions versus a direct probabilistic parent;
5. monotonic self-improvement versus a governed shadow stepping-stone archive and a
   broader mutation/search parent on a deceptive landscape.

Stdlib only; deterministic seeds.
"""
from __future__ import annotations
import argparse, itertools, json, math, random, statistics


def entropy(ps):
    return -sum(p * math.log(p + 1e-15, 2) for p in ps if p > 0)


def normalize(xs):
    s = sum(xs)
    return [x / s for x in xs] if s else [1 / len(xs)] * len(xs)


def binary_entropy(p):
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def fano_required_information(m, error):
    """Uniform m-way identification: I(Z;Y) >= log2(m)-h2(e)-e log2(m-1)."""
    if m < 2:
        return 0.0
    return max(0.0, math.log2(m) - binary_entropy(error) - error * math.log2(m - 1))


def identifiability_bounds():
    rows = []
    for m in (8, 30, 100):
        for error in (0.01, 0.05, 0.10):
            info = fano_required_information(m, error)
            rows.append({
                "candidate_causes": m,
                "target_error": error,
                "required_mutual_information_bits_lower_bound": info,
                "probe_count_lower_bounds": {
                    str(bits): math.ceil(info / bits)
                    for bits in (0.10, 0.25, 0.50, 1.0, 2.0)
                },
            })
    return rows


def diagnosis_sweep(seed=20260908, episodes=3000):
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


def lifetime(seed, K, drift, evo_budget, generations=24, reps=5, n=10):
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


def make_self_system(rng, n_components=30, n_symptoms=80, causes_per_component=6):
    return [set(rng.sample(range(n_symptoms), causes_per_component)) for _ in range(n_components)]


def observe_self_fault(rng, causal, faults, n_symptoms=80, p_causal=0.82, p_background=0.03):
    out = []
    for symptom in range(n_symptoms):
        active = any(symptom in causal[c] for c in faults)
        p = p_causal if active else p_background
        out.append(1 if rng.random() < p else 0)
    return out


class SelfModelCounts:
    def __init__(self, n_components, n_symptoms, alpha=1.0):
        self.n_components = n_components
        self.n_symptoms = n_symptoms
        self.pos = [[alpha] * n_symptoms for _ in range(n_components)]
        self.neg = [[alpha] * n_symptoms for _ in range(n_components)]
        self.n = [2 * alpha] * n_components
        self.global_pos = [alpha] * n_symptoms
        self.global_n = 2 * alpha

    def update(self, component, symptoms):
        self.n[component] += 1
        self.global_n += 1
        for s, v in enumerate(symptoms):
            if v:
                self.pos[component][s] += 1
                self.global_pos[s] += 1
            else:
                self.neg[component][s] += 1

    def explicit_graph_scores(self, symptoms):
        scores = []
        for c in range(self.n_components):
            score = 0.0
            for s, v in enumerate(symptoms):
                if v:
                    pc = self.pos[c][s] / self.n[c]
                    pg = self.global_pos[s] / self.global_n
                    score += math.log((pc + 1e-9) / (pg + 1e-9))
            scores.append(score)
        return scores

    def direct_bernoulli_parent_scores(self, symptoms):
        scores = []
        for c in range(self.n_components):
            score = -math.log(self.n_components)
            for s, v in enumerate(symptoms):
                pc = self.pos[c][s] / self.n[c]
                pc = min(max(pc, 1e-5), 1 - 1e-5)
                score += math.log(pc if v else 1 - pc)
            scores.append(score)
        return scores


def rank_until_all_causes(scores, causes):
    order = sorted(range(len(scores)), key=lambda c: (-scores[c], c))
    rank = {c: i + 1 for i, c in enumerate(order)}
    return max(rank[c] for c in causes)


def one_self_intervention(seed, training_episodes, test_episodes=120, pair_faults=False):
    rng = random.Random(seed)
    n_components, n_symptoms = 30, 80
    causal = make_self_system(rng, n_components, n_symptoms)
    model = SelfModelCounts(n_components, n_symptoms)

    for _ in range(training_episodes):
        c = rng.randrange(n_components)
        symptoms = observe_self_fault(rng, causal, [c], n_symptoms)
        model.update(c, symptoms)

    explicit, parent, blind = [], [], []
    for _ in range(test_episodes):
        causes = rng.sample(range(n_components), 2 if pair_faults else 1)
        symptoms = observe_self_fault(rng, causal, causes, n_symptoms)
        explicit.append(rank_until_all_causes(model.explicit_graph_scores(symptoms), causes))
        parent.append(rank_until_all_causes(model.direct_bernoulli_parent_scores(symptoms), causes))
        order = list(range(n_components))
        rng.shuffle(order)
        rank = {c: i + 1 for i, c in enumerate(order)}
        blind.append(max(rank[c] for c in causes))
    return statistics.mean(explicit), statistics.mean(parent), statistics.mean(blind)


def self_intervention_learning_sweep():
    rows = []
    for pair_faults in (False, True):
        for training in (50, 100, 200, 400):
            reps = [
                one_self_intervention(
                    9000 + i + training * 17 + (100000 if pair_faults else 0),
                    training,
                    pair_faults=pair_faults,
                )
                for i in range(5)
            ]
            rows.append({
                "training_resolved_interventions": training,
                "test_fault_cardinality": 2 if pair_faults else 1,
                "explicit_self_graph_mean_components_inspected": statistics.mean(x[0] for x in reps),
                "direct_probabilistic_parent_mean_components_inspected": statistics.mean(x[1] for x in reps),
                "blind_mean_components_inspected": statistics.mean(x[2] for x in reps),
                "repetitions": 5,
                "test_episodes_per_repetition": 120,
            })
    return rows


TRAP_GROUPS = ((0,1,2), (3,4,5), (6,7,8), (9,10,11))


def deceptive_fitness(x):
    total = 0.0
    for group in TRAP_GROUPS:
        ones = sum((x >> b) & 1 for b in group)
        if ones == 0:
            value = 0.8
        elif ones == 3:
            value = 1.0
        else:
            value = 0.35 + 0.10 * ones
        total += value
    return total / len(TRAP_GROUPS)


def monotonic_single_bit(budget):
    x, fx, evals = 0, deceptive_fitness(0), 1
    while evals < budget:
        bestf, bestx = fx, x
        for b in range(12):
            if evals >= budget:
                break
            y = x ^ (1 << b)
            fy = deceptive_fitness(y)
            evals += 1
            if fy > bestf + 1e-12:
                bestf, bestx = fy, y
        if bestf <= fx + 1e-12:
            break
        fx, x = bestf, bestx
    return fx, evals


def shadow_archive_search(budget, seed):
    """Deployed best never regresses; shadow archive may retain lower-fitness stepping stones."""
    rng = random.Random(seed)
    archive = {0: deceptive_fitness(0)}
    bestf, evals = 0.8, 1
    while evals < budget and len(archive) < (1 << 12):
        parent = rng.choice(tuple(archive))
        unseen_bits = [b for b in range(12) if (parent ^ (1 << b)) not in archive]
        if not unseen_bits:
            continue
        y = parent ^ (1 << rng.choice(unseen_bits))
        fy = deceptive_fitness(y)
        evals += 1
        archive[y] = fy
        bestf = max(bestf, fy)
    return bestf, evals


def broad_mutation_parent(budget, seed, max_flip=3):
    """Conventional wider search from the deployed incumbent; may cross each 3-bit trap directly."""
    rng = random.Random(seed)
    x, fx, evals = 0, deceptive_fitness(0), 1
    while evals < budget:
        candidates = []
        for k in range(1, max_flip + 1):
            candidates.extend(itertools.combinations(range(12), k))
        rng.shuffle(candidates)
        improved = False
        for bits in candidates:
            if evals >= budget:
                break
            y = x
            for b in bits:
                y ^= 1 << b
            fy = deceptive_fitness(y)
            evals += 1
            if fy > fx + 1e-12:
                x, fx = y, fy
                improved = True
                break
        if not improved:
            break
    return fx, evals


def stepping_stone_sweep():
    base_quality, base_evals = monotonic_single_bit(5000)
    rows = []
    for budget in (50, 100, 250, 500, 1000, 2500, 4000):
        archive = [shadow_archive_search(budget, seed=30000+i)[0] for i in range(10)]
        broad = [broad_mutation_parent(budget, seed=40000+i)[0] for i in range(10)]
        rows.append({
            "budget": budget,
            "monotonic_single_bit_quality": base_quality,
            "monotonic_single_bit_initial_stop_evals": base_evals,
            "shadow_archive_mean_best_quality": statistics.mean(archive),
            "shadow_archive_optimum_fraction": sum(q >= 0.999999 for q in archive) / len(archive),
            "broad_1_to_3_bit_parent_mean_best_quality": statistics.mean(broad),
            "broad_parent_optimum_fraction": sum(q >= 0.999999 for q in broad) / len(broad),
            "repetitions": 10,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output")
    args = ap.parse_args()
    result = {
        "status": "E2_EXPLORATORY_SYNTHETIC_ONLY",
        "claim_authority": "NO_OCM_OR_NEURAL_OR_AUTOML_SUPERIORITY_CLAIM",
        "seed_family": "20260908-v0.2",
        "identifiability_lower_bound": identifiability_bounds(),
        "diagnosis": diagnosis_sweep(),
        "factorization_lifetime": lifetime_sweeps(),
        "self_intervention_learning": self_intervention_learning_sweep(),
        "stepping_stone_search": stepping_stone_sweep(),
        "interpretation_rules": [
            "Low effective coupling is not sufficient for evolvability; failure causes must also be identifiable from affordable observations/interventions and the localized repair space must be searchable.",
            "Fano's inequality supplies a lower bound on diagnostic information, not an OCM-specific theorem or performance result.",
            "Learning predictive self-structure from resolved interventions can greatly reduce later fault-localization search, but the direct probabilistic parent can match or outperform it; self-model learning alone is parent-owned.",
            "A monotonic deployed lineage can be trapped by deceptive landscapes. Retaining non-deployed stepping stones can improve reachability, but a conventional broader mutation/search parent can dominate the naive archive.",
            "Factorization remains a regime hypothesis: sparse/stable interaction structure permits evaluation savings, while dense coupling and drift erode or remove the advantage.",
            "All results are synthetic E2 theory pressure. Strongest-parent closure requires real OCM studies and substantially stronger adaptive parents."
        ],
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


if __name__ == "__main__":
    main()
