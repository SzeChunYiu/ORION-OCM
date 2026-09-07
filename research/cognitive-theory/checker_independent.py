#!/usr/bin/env python3
"""Independent E2 checker of EXACT_MODELS_V1; no primary-checker imports.

Closure uses all-pairs composition to a fixed point. Costs use exact-weight
layers, not graph search. Lifecycle minimization uses all future deletion
signatures. Diagnosis uses finite information-set dynamic programming over
all attainable terminal outcome vectors, not evaluator-state policies.
"""
import argparse
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path


EXPECTED_MODEL_SHA256 = "cfb923eacabe2062255a032791d7329e0e2909eb92a237de9c4d811d54dbd10f"


def compose(first, second):
    """Apply first, then second."""
    return tuple(second[x] for x in first)


def closure_pairwise(generators, size):
    known = {tuple(range(size)), *generators}
    rounds = 0
    while True:
        expanded = known | {compose(a, b) for a in known for b in known}
        rounds += 1
        if expanded == known:
            return known, rounds
        known = expanded


def exact_weight_layers(generators, size, budget):
    layers = [{tuple(range(size))}]
    for cost in range(1, budget + 1):
        layer = set()
        for transform, weight in generators:
            if weight <= cost:
                layer.update(compose(p, transform) for p in layers[cost - weight])
        layers.append(layer)
    minimum = {}
    for cost, layer in enumerate(layers):
        for transform in layer:
            minimum.setdefault(transform, cost)
    return minimum, layers


def rotation(n, amount):
    return tuple((x + amount) % n for x in range(n))


def powerset(values):
    return [subset for n in range(len(values) + 1)
            for subset in itertools.combinations(values, n)]


def cyclic_pool(pool):
    targets = [rotation(6, x) for x in range(6)]
    records = []
    for subset in powerset(pool):
        generators = [rotation(6, x) for x in subset]
        closure, rounds = closure_pairwise(generators, 6)
        minimum, _ = exact_weight_layers([(g, 1) for g in generators], 6, 5)
        lengths = [minimum.get(t) for t in targets]
        records.append({"basis": list(subset), "closure_size": len(closure),
                        "closure_exponents": [x for x, t in enumerate(targets) if t in closure],
                        "lengths": lengths, "pair_composition_rounds": rounds,
                        "generates_all": len(closure) == 6})
    generating = [r for r in records if r["generates_all"]]
    inclusion_minimal = [r["basis"] for r in generating
                         if not any(set(s["basis"]) < set(r["basis"]) for s in generating)]
    minima, minimizers = {}, {}
    for budget in range(6):
        feasible = [r for r in records
                    if all(v is not None and v <= budget for v in r["lengths"])]
        key = str(budget)
        minima[key] = min((len(r["basis"]) for r in feasible), default=None)
        minimizers[key] = [r["basis"] for r in feasible if len(r["basis"]) == minima[key]]
    return {"candidate_pool": list(pool), "subset_count": len(records),
            "rank": min(len(r["basis"]) for r in generating),
            "inclusion_minimal_bases": inclusion_minimal,
            "minimum_cardinality_by_budget": minima,
            "minimum_bases_by_budget": minimizers, "subsets": records}


def check_w1():
    full, restricted = cyclic_pool((1, 2, 3, 4, 5)), cyclic_pool((1, 2, 3))
    weighted, _ = exact_weight_layers([(rotation(6, x), x) for x in (1, 2, 3)], 6, 5)
    distances = {}
    directed = {}
    for a, b in ((1, 2), (2, 4), (1, 4)):
        over_b, _ = exact_weight_layers([(rotation(5, b), 1)], 5, 4)
        over_a, _ = exact_weight_layers([(rotation(5, a), 1)], 5, 4)
        pair = [over_b[rotation(5, a)], over_a[rotation(5, b)]]
        distances[f"{a},{b}"] = max(pair)
        directed[f"{a},{b}"] = {"a_compiled_over_b": pair[0], "b_compiled_over_a": pair[1]}
    flip = (1, 0)
    flip_closure, _ = closure_pairwise([flip], 2)
    constant = tuple(flip[x] if x == 1 else x for x in range(2))
    return {"full_pool": full, "restricted_pool": restricted,
            "weighted_macro_lengths": [weighted[rotation(6, x)] for x in range(6)],
            "z5_mutual_distances": distances, "z5_directed_lengths": directed,
            "threshold_three_transitive": not (distances["1,2"] <= 3 and distances["2,4"] <= 3
                                                and distances["1,4"] > 3),
            "flip": {"closure": sorted(flip_closure), "initial_zero_orbit": sorted({f[0] for f in flip_closure}),
                     "conditional_map": constant, "conditional_in_word_closure": constant in flip_closure}}


def check_w2():
    supports = [frozenset(s) for s in ((), ("a",), ("b",), ("a", "b"))]
    names = ["empty", "a", "b", "ab"]
    index = {s: i for i, s in enumerate(supports)}
    outputs = [bool(s) for s in supports]
    named = {token: tuple(index[s - {token}] for s in supports) for token in ("a", "b")}
    closure, _ = closure_pairwise(list(named.values()), 4)
    # Every sequence is equivalent to deleting exactly its set of named tokens.
    future_deletions = [frozenset(s) for s in powerset(("a", "b"))]
    signatures = {names[i]: [bool(s - removed) for removed in future_deletions]
                  for i, s in enumerate(supports)}
    pair_witnesses = []
    for i, j in itertools.combinations(range(4), 2):
        witnesses = [sorted(removed) for removed in future_deletions
                     if bool(supports[i] - removed) != bool(supports[j] - removed)]
        witness = min(witnesses, key=lambda x: (len(x), x))
        pair_witnesses.append({"states": [names[i], names[j]], "deletion_suffix": witness})
    transition_errors = []
    # Keys (current output UNKNOWN/VERIFIED, event a/b); outputs label states.
    for machine in itertools.product((False, True), repeat=4):
        errors = sum(machine[2 * int(bool(s)) + e] != bool(s - {token})
                     for s in supports for e, token in enumerate(("a", "b")))
        transition_errors.append({"machine_outputs_Ua_Ub_Va_Vb": list(machine), "errors": errors})
    generators = []
    nonidentity = sorted(closure - {tuple(range(4))})
    for subset in powerset(nonidentity):
        generated, _ = closure_pairwise(subset, 4)
        if generated == closure:
            generators.append(subset)
    return {"states": names, "current_output_class_count": len(set(outputs)),
            "future_signature_class_count": len({tuple(v) for v in signatures.values()}),
            "future_deletion_sets": [sorted(s) for s in future_deletions],
            "future_signatures": signatures, "distinguishing_suffixes": pair_witnesses,
            "maximum_shortest_distinguishing_suffix": max(len(p["deletion_suffix"]) for p in pair_witnesses),
            "deletion_maps": named, "deletion_monoid": sorted(closure), "deletion_monoid_size": len(closure),
            "deletion_monoid_rank": min(map(len, generators)),
            "answer_only_machine_count": len(transition_errors),
            "answer_only_minimum_errors": min(x["errors"] for x in transition_errors),
            "answer_only_pair_denominator": 8, "answer_only_machines": transition_errors}


def diagnosis_mode(informative):
    """Complete finite belief DP, quotienting trees by terminal outcome vectors.

    Proof of completeness by budget induction: every policy first stops with
    one of three labels, retries, or (if affordable) audits. Each action makes
    exactly the registered observation partition. Cartesian products of all
    child outcome vectors enumerate every observation-contingent continuation.
    Positive action costs strictly reduce budget. Identical outcome vectors may
    be merged because hidden state is static and the scored objective depends
    only on terminal labels. No action is selected with private h access.
    """
    transitions = {}

    @lru_cache(None)
    def solve(belief, budget):
        outcomes = {tuple(label for _ in belief) for label in (-1, 0, 1)}
        node_key = f"{','.join(map(str, belief))}|{budget}"
        action_rows = []
        for action, cost in (("retry", 1), ("audit", 2)):
            if cost > budget:
                continue
            partitions = {}
            for h in belief:
                observation = str(h) if action == "audit" and informative else ("FAIL" if action == "retry" else "CONST")
                partitions.setdefault(observation, []).append(h)
            groups = [(observation, tuple(states)) for observation, states in sorted(partitions.items())]
            continuation_sets = [solve(states, budget - cost) for _, states in groups]
            for children in itertools.product(*continuation_sets):
                assembled = {}
                for (_, states), child in zip(groups, children):
                    assembled.update(zip(states, child))
                outcomes.add(tuple(assembled[h] for h in belief))
            action_rows.append({"action": action, "cost": cost,
                                "observations": [{"observation": observation, "belief": list(states),
                                                  "remaining_budget": budget - cost} for observation, states in groups]})
        transitions[node_key] = {"belief": list(belief), "remaining_budget": budget,
                                 "feasible_actions": action_rows, "terminal_labels": [-1, 0, 1],
                                 "attainable_outcome_vectors": sorted(outcomes)}
        return tuple(sorted(outcomes))

    by_budget = {}
    for budget in range(3):
        outcomes = solve((0, 1), budget)
        forced = [v for v in outcomes if -1 not in v]
        correct = max(sum(label == h for h, label in enumerate(v)) for v in forced)
        sound = [v for v in outcomes if all(label in (-1, h) for h, label in enumerate(v))]
        coverage = max(sum(label != -1 for label in v) for v in sound)
        by_budget[str(budget)] = {"forced_correct_max_count": correct, "world_count": 2,
                                 "forced_accuracy": correct / 2, "sound_committed_max_count": coverage,
                                 "sound_committed_coverage": coverage / 2,
                                 "outcome_vector_count": len(outcomes), "forced_outcome_vector_count": len(forced),
                                 "sound_outcome_vectors": sound}
    return {"audit_mode": "informative" if informative else "constant", "by_budget": by_budget,
            "belief_nodes": [transitions[k] for k in sorted(transitions)],
            "enumeration": "Complete positive-cost belief DP; all terminal outcome vectors, quotienting behavior-equivalent adaptive trees."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write JSON here; otherwise stdout")
    args = parser.parse_args()
    model = Path(__file__).with_name("EXACT_MODELS_V1.md")
    digest = hashlib.sha256(model.read_bytes()).hexdigest()
    if digest != EXPECTED_MODEL_SHA256:
        raise SystemExit(f"Frozen model hash mismatch: {digest}")
    result = {"schema": "independent_finite_checker_v1", "evidence_class": "E2_EXPLORATORY",
              "external_replication": False, "model_sha256": digest,
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "w1": check_w1(), "w2": check_w2(),
              "w3": {"informative": diagnosis_mode(True), "constant": diagnosis_mode(False)}}
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
