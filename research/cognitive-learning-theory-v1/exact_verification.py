"""Complete finite checks of parent-owned decision/support theory.

This is V2 / E2 exact mathematical calibration, not a self-evolution efficacy
benchmark. No OCM outcome file, F4 donor, protected task, or stochastic sample is
read. Fixed, finite, noiseless model classes and a supplied acceptable-action
relation are explicit priors. Runtime cost of choosing probes is not free.

Run from repository root with Python's standard library only:
    python research/cognitive-learning-theory-v1/exact_verification.py --out NEW.json
Existing result paths are never overwritten.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import permutations, product
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def members(mask, n):
    return [i for i in range(n) if mask & (1 << i)]


def intersection_masks(values, universe):
    result = universe
    for value in values:
        result &= value
    return result


def version_space_checks():
    """FC1: direct filtering versus intersection of observation preimages."""
    comparisons = empty = removal_checks = 0
    tables = tuple(product((0, 1), repeat=3))
    for observations in product(tables, repeat=2):
        for evidence in product((-1, 0, 1), repeat=2):
            direct = {h for h in range(3) if all(v == -1 or observations[p][h] == v
                                                for p, v in enumerate(evidence))}
            preimages = [{h for h in range(3) if observations[p][h] == v}
                         for p, v in enumerate(evidence) if v != -1]
            indirect = set(range(3)).intersection(*preimages)
            assert direct == indirect
            comparisons += 1
            empty += not direct
            for removed in range(4):
                remaining = tuple(-1 if removed & (1 << p) else v
                                  for p, v in enumerate(evidence))
                reopened = {h for h in range(3) if all(v == -1 or observations[p][h] == v
                                                      for p, v in enumerate(remaining))}
                assert direct <= reopened
                removal_checks += 1
    return {"theory_ids": ["FC1"], "hypotheses": 3, "binary_probes": 2,
            "complete_observation_tables": 64, "partial_evidence_assignments": 9,
            "dual_algorithm_comparisons": comparisons, "empty_version_spaces": empty,
            "all_evidence_removal_checks": removal_checks,
            "claim": "Evidence removal enlarges a version space; realizability is not established by a nonempty space."}


def impact_union_checks():
    """FC2: bitwise union versus exhaustive search over every safe footprint."""
    worlds = soundness_checks = 0
    for effects in product(range(8), repeat=3):
        for version in range(1, 8):
            relevant = [effects[h] for h in members(version, 3)]
            union = 0
            for effect in relevant:
                union |= effect
            # Independent set formulation enumerates ALL proposed footprints.
            possible = [set(members(effect, 3)) for effect in relevant]
            sound_sets = []
            for footprint in range(8):
                candidate = set(members(footprint, 3))
                safe = all(all(obligation in candidate for obligation in effect) for effect in possible)
                assert safe == (union & ~footprint == 0)
                if safe:
                    sound_sets.append(candidate)
                soundness_checks += 1
            least = set.intersection(*sound_sets)
            assert least == set(members(union, 3))
            assert sum(candidate == least for candidate in sound_sets) == 1
            worlds += 1
    return {"theory_ids": ["FC2"], "hypotheses": 3, "obligations": 3,
            "complete_effect_assignments": 512, "nonempty_version_spaces": 7,
            "worlds": worlds, "all_footprint_checks": soundness_checks,
            "counterexample_to_guaranteed_locality": {
                "possible_impacts": [[], [0, 1, 2]], "true_impact": [],
                "least_sound_footprint": [0, 1, 2]},
            "claim": "The union is the unique least universally covering footprint, conditional on complete impact models; coverage alone is not a repair/authority certificate."}


@lru_cache(None)
def explicit_trees(available):
    """Every deterministic action-labelled binary tree without repeated probes."""
    trees = list(range(3))  # Three beneficial actions; abstention is excluded.
    for probe in available:
        children = explicit_trees(tuple(p for p in available if p != probe))
        trees.extend((probe, left, right) for left in children for right in children)
    return tuple(trees)


def evaluate_tree(tree, hypothesis, observations, costs):
    spent = 0
    while not isinstance(tree, int):
        probe, left, right = tree
        spent += costs[probe]
        tree = right if observations[probe][hypothesis] else left
    return tree, spent


def dp_probe_cost(good, observations, costs):
    """FC4 Bellman recursion on version spaces, independent of tree syntax."""
    @lru_cache(None)
    def solve(version):
        hypotheses = members(version, 3)
        if intersection_masks((good[h] for h in hypotheses), 7):
            return 0
        best = float("inf")
        for p in range(2):
            cells = [sum(1 << h for h in hypotheses if observations[p][h] == outcome)
                     for outcome in (0, 1)]
            if not all(cells):
                continue
            best = min(best, costs[p] + max(solve(cell) for cell in cells))
        return best
    return solve(7)


def decision_checks():
    """FC3/4: exhaustive trees versus DP over the complete declared universe."""
    trees = explicit_trees((0, 1))
    assert len(trees) == 291
    assignments = tuple(product(range(1, 8), repeat=3))
    outcomes = tuple(product((0, 1), repeat=3))
    counts = Counter()
    histogram = Counter()
    for observations in product(outcomes, repeat=2):
        cells = {}
        for h in range(3):
            cells.setdefault(tuple(probe[h] for probe in observations), []).append(h)
        for costs in product((1, 2), repeat=2):
            # This algorithm evaluates every full tree directly for every world.
            # Compressing identical action vectors loses no safety or cost option.
            action_vectors = {}
            for tree in trees:
                executions = [evaluate_tree(tree, h, observations, costs) for h in range(3)]
                actions = tuple(action for action, _ in executions)
                cost = max(spent for _, spent in executions)
                action_vectors[actions] = min(cost, action_vectors.get(actions, float("inf")))
            for good in assignments:
                direct = min((cost for actions, cost in action_vectors.items()
                              if all(good[h] & (1 << actions[h]) for h in range(3))),
                             default=float("inf"))
                dynamic = dp_probe_cost(good, observations, costs)
                assert direct == dynamic
                adequate = all(intersection_masks((good[h] for h in cell), 7)
                               for cell in cells.values())
                assert adequate == (direct != float("inf"))
                counts["systems"] += 1
                counts["decision_feasible"] += bool(adequate)
                counts["decision_feasible_without_model_identification"] += bool(
                    adequate and any(len(cell) > 1 for cell in cells.values()))
                counts["zero_probe_feasible"] += direct == 0
                histogram["infinite" if direct == float("inf") else str(direct)] += 1
    pairwise = (3, 6, 5)  # {a,b}, {b,c}, {a,c}
    assert all(pairwise[i] & pairwise[j] for i in range(3) for j in range(i))
    assert intersection_masks(pairwise, 7) == 0
    assert dp_probe_cost(pairwise, ((0, 0, 0), (0, 0, 0)), (1, 1)) == float("inf")
    assert counts["systems"] == 343 * 64 * 4
    return {"theory_ids": ["FC3", "FC4"], "hypotheses": 3,
            "beneficial_nonabstention_actions": 3, "nonempty_acceptable_action_assignments": 343,
            "binary_resettable_noiseless_probes": 2, "complete_observation_tables": 64,
            "strictly_positive_cost_vectors": 4, "all_nonrepeat_action_trees": len(trees),
            **dict(counts), "optimal_worst_case_probe_cost_histogram": dict(sorted(histogram.items())),
            "pairwise_intersection_counterexample": {"acceptable_actions": [["a", "b"], ["b", "c"], ["a", "c"]],
                "pairwise_intersections_nonempty": True, "common_action_exists": False},
            "claim": "All 87808 complete systems agree: adequate probes identify an acceptable decision without requiring structural identification, and Bellman cost equals exhaustive tree cost.",
            "parent_status": "PARENT_THEOREM_RECONSTRUCTION_NOT_NOVELTY",
            "direct_parent": "Javdani et al., 2014, Decision Region Determination / HEC, https://arxiv.org/abs/1402.5886",
            "resource_limit": "Costs count physical probes only; policy synthesis/computation is not claimed free or measured by this theorem."}


def all_monotone_truth_tables(n):
    size = 1 << n
    return tuple(tuple((bits >> x) & 1 for x in range(size))
                 for bits in range(1 << size)
                 if all(not (x & ~y == 0) or not (bits >> x & 1) or (bits >> y & 1)
                        for x in range(size) for y in range(size)))


def all_antichains(n):
    size = 1 << n
    return tuple(tuple(x for x in range(size) if family >> x & 1)
                 for family in range(1 << size)
                 if all(x == y or (x & ~y != 0)
                        for x in range(size) if family >> x & 1
                        for y in range(size) if family >> y & 1))


def support_checks():
    """FC5: truth-table filtering versus independent minimal-support enumeration."""
    rows = []
    for n in range(4):
        truth_tables = all_monotone_truth_tables(n)
        antichains = all_antichains(n)
        reconstructed = {tuple(int(any(support & ~live == 0 for support in family))
                               for live in range(1 << n)): family for family in antichains}
        assert set(reconstructed) == set(truth_tables)
        assert len(reconstructed) == len(antichains)
        full = (1 << n) - 1
        missed_models = invisible = 0
        for truth in truth_tables:
            minimal = tuple(x for x in range(1 << n) if truth[x] and
                            not any(y != x and y & ~x == 0 and truth[y] for y in range(1 << n)))
            assert minimal == reconstructed[truth]
            if not truth[full]:
                continue
            single_essential = {i for i in range(n) if not truth[full & ~(1 << i)]}
            actually_used = {i for support in minimal for i in range(n) if support & (1 << i)}
            missed_models += single_essential != actually_used
            invisible += bool(not single_essential and not truth[0])
        rows.append({"variables": n, "complete_boolean_truth_tables_examined": 1 << (1 << n),
                     "monotone_functions": len(truth_tables), "minimal_support_antichains": len(antichains),
                     "functions_with_dependencies_missed_by_full_state_single_deletion": missed_models,
                     "nonconstant_functions_whose_single_deletions_all_preserve_truth": invisible})
    # Redundancy creates an exact indistinguishable observation pair.
    or_three = tuple(int(bool(x)) for x in range(8))
    unconditional = (1,) * 8
    observed_masks = (7, 6, 5, 3)
    assert [or_three[x] for x in observed_masks] == [unconditional[x] for x in observed_masks]
    assert or_three[0] != unconditional[0]
    return {"theory_ids": ["FC5"], "complete_domains": rows,
            "higher_order_support_example": {"minimal_support": [0, 1], "rule": "a AND b"},
            "redundant_support_counterexample": {"models": ["a OR b OR c", "TRUE"],
                "full_state_and_every_single_deletion_identical": True,
                "all_three_revoked_outputs": [0, 1]},
            "claim": "Single-deletion evidence does not identify all alternative supports or multi-revocation effects.",
            "assumption": "Fixed Boolean obligation monotone in available assumptions; no source-specific F4 induced-rule monotonicity is asserted."}


def ranked_consistency_checks():
    """Sufficient monotonicity conditions for fixed target selection; not F4 code."""
    systems = pair_checks = 0
    # Three hypotheses, three examples, all 512 conjunctive consistency tables,
    # all six data-independent strict ranks. Target is full-evidence selection.
    for matrix in product((0, 1), repeat=9):
        for rank in permutations(range(3)):
            def selected(evidence):
                return next((h for h in rank if all(matrix[3 * h + e]
                                                   for e in members(evidence, 3))), None)
            target = selected(7)
            if target is None:
                continue
            indicators = [selected(evidence) == target for evidence in range(8)]
            for smaller in range(8):
                for larger in range(8):
                    if smaller & ~larger == 0:
                        assert not indicators[smaller] or indicators[larger]
                        pair_checks += 1
            systems += 1
    return {"theory_ids": ["FC5"], "hypotheses": 3, "examples": 3,
            "all_consistency_tables": 512, "all_fixed_strict_rankings": 6,
            "systems_with_full_evidence_target": systems, "nested_evidence_pairs_checked": pair_checks,
            "conditions": ["fixed hypothesis set", "data-independent strict ranking",
                "consistency is conjunction of per-example constraints", "target consistent with all registered evidence"],
            "data_dependent_rank_counterexample": {"evidence_masks": [0, 1, 2, 3],
                "selected_hypotheses": [0, 1, 1, 0], "both_hypotheses_consistent_everywhere": True,
                "fixed_target": 0, "monotonicity_fails": "empty -> singleton"},
            "claim": "The abstract sufficient-condition theorem passes; whether an actual learner satisfies the conditions remains CANNOT_CHECK here."}


def lifecycle_checks():
    """Epistemic trace quotient: partition refinement versus all deletion subsets."""
    rows = []
    for n in range(4):
        models = all_monotone_truth_tables(n)
        states = tuple((m, live) for m in range(len(models)) for live in range(1 << n))
        position = {state: i for i, state in enumerate(states)}
        outputs = tuple(models[m][live] for m, live in states)
        transitions = tuple(tuple(position[(m, live & ~(1 << action))] for action in range(n))
                            for m, live in states)
        classes = outputs
        iterations = 0
        while True:
            identities = {}
            refined = tuple(identities.setdefault((outputs[i], tuple(classes[j] for j in transitions[i])),
                                                 len(identities)) for i in range(len(states)))
            iterations += 1
            if refined == classes:
                break
            classes = refined
        # No automata refinement used here: every finite deletion word reduces
        # to its subset because deletion is idempotent and commutative.
        signatures = tuple(tuple(models[m][live & ~removed] for removed in range(1 << n))
                           for m, live in states)
        comparisons = 0
        for i in range(len(states)):
            for j in range(len(states)):
                assert (classes[i] == classes[j]) == (signatures[i] == signatures[j])
                comparisons += 1
        rows.append({"assumptions": n, "models": len(models), "complete_states": len(states),
                     "complete_transitions": len(states) * n, "immediate_output_classes": len(set(outputs)),
                     "lifecycle_equivalence_classes": len(set(classes)), "refinement_iterations": iterations,
                     "dual_algorithm_state_pair_checks": comparisons})
    return {"theory_ids": ["FC5"], "complete_domains": rows,
            "lifecycle_actions": "Revoke each registered assumption; all finite action words covered by deletion-subset normal forms.",
            "counterexample": {"states": ["TRUE with a live", "a with a live"],
                "immediate_answers": [1, 1], "after_revoke_a": [1, 0]},
            "claim": "Immediate answer equality is strictly weaker than future revocation-trace equivalence.",
            "boundary": "No reinstatement/authority change action is in this finite alphabet; no general lifecycle equivalence outside it is claimed."}


def verify():
    sections = {"version_spaces": version_space_checks(), "conservative_impact_union": impact_union_checks(),
                "decision_sufficiency_and_probe_cost": decision_checks(), "supports": support_checks(),
                "ranked_consistency_sufficiency": ranked_consistency_checks(), "epistemic_lifecycle": lifecycle_checks()}
    return {"schema": "ocm.cognitive-learning-theory.exact-verification.v1",
            "status": "ALL_DECLARED_FINITE_CHECKS_PASS", "verification_route": "V2",
            "evidence_class": "E2_EXACT_MATHEMATICAL_CALIBRATION",
            "scientific_disposition": "PARENT_THEOREM_RECONSTRUCTION",
            "empirical_efficacy": "NOT_TESTED", "protected_data_or_experiments": "NOT_ACCESSED",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "result_sections_sha256": hashlib.sha256(canonical(sections)).hexdigest(),
            "sections": sections,
            "limitations": ["finite checks support the stated scoped propositions, not unbounded proofs",
                "independent algorithms are authored within one AI-assisted research team, not external replication",
                "model realizability, impact completeness, checker authority and actual donor assumptions are not inferred",
                "supplied model/action/probe languages are priors; acquisition advantage is unmeasured",
                "no new cognitive primitive or publication readiness follows from these checks"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists() or args.out.is_symlink():
        parser.error("choose a new output path; retained results are immutable")
    result = verify()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "scientific_disposition": result["scientific_disposition"],
                      "sections_sha256": result["result_sections_sha256"], "output": str(args.out)}, sort_keys=True))
