"""Exact finite R0D Decision Region Determination calibration.

Research-only.  This module instantiates the frozen R0D protocol with tiny exact
problems so that four parents can be compared without ML or hidden oracle state:

* P-ID   -- identify the exact hypothesis before acting;
* P-ECD  -- stop once a registered disjoint decision class is known;
* P-DRD  -- stop once all surviving hypotheses share a protected action;
* P-PAID -- exact Bellman choice between stopping and buying another probe.

All arithmetic is Fraction-exact.  The microbenchmarks are synthetic witnesses,
not reproductions of DEV-5/6/X1.  Those source lanes are carried only as immutable
provenance/calibration references in the emitted receipt.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Mapping


F = Fraction
PARENTS = ("P-ID", "P-ECD", "P-DRD", "P-PAID")
TERMINAL = "R0D_EXECUTABLE_PARENT_ESTABLISHED_SYNTHETIC_ONLY"

SOURCE_CUSTODY = {
    "DEV5": {
        "commit": "a0c4931629263ee92fe676e479445b188af5df6e",
        "receipt": "research/cognitive-ladder/results/DEV5_UNANIMITY_V1.json",
        "role": "same-language singleton-vs-unanimity decision-rule ablation",
        "settings": 36,
    },
    "DEV6": {
        "commit": "f676a34e022fff710a05cede0ea6027a8c390e28",
        "receipt": "research/developmental-spine/results/DEV6_HONEST_CONSULTATION_PRICE_V1.json",
        "role": "honest proportional consultation-price audit",
        "honest_price_ratio_range": ["0.2923502856247197", "0.9704311019045002"],
    },
    "X1": {
        "commit": "2ba88a80593a8e3ddcbedaf6520da5bc7fddbed3",
        "receipt": "research/cognitive-ladder/results/X1_UNANIMITY_TRANSFER_V1.json",
        "role": "cross-domain one-line determined(candidate) ablation",
        "matched_capability": {
            "with_determination_interventions": 198,
            "without_determination_interventions": 529,
            "with_determination_work": 8039,
            "without_determination_work": 4936,
        },
    },
}


class Unsolvable(RuntimeError):
    pass


@dataclass(frozen=True)
class Problem:
    hypotheses: tuple[str, ...]
    safe_actions: Mapping[str, frozenset[str]]
    action_costs: Mapping[str, F]
    probes: tuple[str, ...]
    probe_costs: Mapping[str, F]
    outcomes: Mapping[tuple[str, str], str]
    equivalence_class: Mapping[str, str] | None = None

    def validate(self) -> None:
        if not self.hypotheses or len(set(self.hypotheses)) != len(self.hypotheses):
            raise ValueError("hypotheses must be a nonempty unique tuple")
        if len(set(self.probes)) != len(self.probes):
            raise ValueError("probe names must be unique")
        for h in self.hypotheses:
            actions = self.safe_actions.get(h)
            if not actions:
                raise ValueError(f"hypothesis {h!r} has no protected action")
            for action in actions:
                if action not in self.action_costs:
                    raise ValueError(f"missing action cost for {action!r}")
            for probe in self.probes:
                if (h, probe) not in self.outcomes:
                    raise ValueError(f"missing deterministic outcome for {(h, probe)!r}")
        for value in tuple(self.action_costs.values()) + tuple(self.probe_costs.values()):
            if value < 0:
                raise ValueError("costs must be nonnegative")
        if set(self.probes) != set(self.probe_costs):
            raise ValueError("probe costs must cover exactly the registered probes")
        if self.equivalence_class is not None and set(self.equivalence_class) != set(self.hypotheses):
            raise ValueError("equivalence-class map must cover exactly the hypotheses")


@dataclass(frozen=True)
class Solution:
    total_cost: F
    worst_probe_count: int
    root_choice: str
    terminal_action: str | None

    def as_json(self) -> dict:
        return {
            "total_cost": _fraction_json(self.total_cost),
            "worst_probe_count": self.worst_probe_count,
            "root_choice": self.root_choice,
            "terminal_action": self.terminal_action,
        }


def _fraction_json(value: F) -> dict:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "exact": str(value),
        "decimal": float(value),
    }


def common_actions(problem: Problem, version: frozenset[str]) -> frozenset[str]:
    if not version:
        raise ValueError("empty version space")
    it = iter(sorted(version))
    common = set(problem.safe_actions[next(it)])
    for h in it:
        common.intersection_update(problem.safe_actions[h])
    return frozenset(common)


def cheapest_common_action(problem: Problem, version: frozenset[str]) -> tuple[str, F] | None:
    actions = common_actions(problem, version)
    if not actions:
        return None
    action = min(actions, key=lambda a: (problem.action_costs[a], a))
    return action, problem.action_costs[action]


def split(problem: Problem, version: frozenset[str], probe: str) -> tuple[frozenset[str], ...]:
    groups: dict[str, set[str]] = {}
    for h in sorted(version):
        groups.setdefault(problem.outcomes[(h, probe)], set()).add(h)
    return tuple(frozenset(group) for _, group in sorted(groups.items()))


def solve(
    problem: Problem,
    parent: str,
    *,
    policy_lookup_cost: F = F(0),
    region_predicate_cost: F = F(0),
) -> Solution:
    """Solve one finite deterministic worst-case episode exactly.

    ``policy_lookup_cost`` charges the deployed controller at every visited
    information state.  ``region_predicate_cost`` is additionally charged to
    P-ECD/P-DRD/P-PAID at every visited state; it represents a naive or otherwise
    explicit decision-region computation that is not already maintained.

    P-PAID is allowed to continue probing after a common action becomes safe when
    the resulting cheaper action can repay the probe and cognition cost.
    """
    problem.validate()
    if parent not in PARENTS:
        raise ValueError(f"unknown parent {parent!r}")
    if policy_lookup_cost < 0 or region_predicate_cost < 0:
        raise ValueError("controller costs must be nonnegative")
    if parent == "P-ECD" and problem.equivalence_class is None:
        raise ValueError("P-ECD requires a registered disjoint equivalence class")

    root = frozenset(problem.hypotheses)

    @lru_cache(maxsize=None)
    def dp(version: frozenset[str]) -> Solution:
        common = cheapest_common_action(problem, version)
        overhead = policy_lookup_cost
        if parent in ("P-ECD", "P-DRD", "P-PAID"):
            overhead += region_predicate_cost

        if parent == "P-ID" and len(version) == 1:
            assert common is not None
            action, action_cost = common
            return Solution(overhead + action_cost, 0, "STOP", action)

        if parent == "P-ECD":
            labels = {problem.equivalence_class[h] for h in version}  # type: ignore[index]
            if len(labels) == 1:
                if common is None:
                    raise ValueError("registered ECD class has no common protected action")
                action, action_cost = common
                return Solution(overhead + action_cost, 0, "STOP", action)

        if parent == "P-DRD" and common is not None:
            action, action_cost = common
            return Solution(overhead + action_cost, 0, "STOP", action)

        candidates: list[Solution] = []
        if parent == "P-PAID" and common is not None:
            action, action_cost = common
            candidates.append(Solution(overhead + action_cost, 0, "STOP", action))

        for probe in problem.probes:
            children = split(problem, version, probe)
            if len(children) <= 1:
                continue
            child_solutions = [dp(child) for child in children]
            worst_total = max(child.total_cost for child in child_solutions)
            worst_probes = 1 + max(child.worst_probe_count for child in child_solutions)
            candidates.append(Solution(
                overhead + problem.probe_costs[probe] + worst_total,
                worst_probes,
                f"PROBE:{probe}",
                None,
            ))

        if not candidates:
            raise Unsolvable(f"{parent} cannot reach a protected decision from {sorted(version)!r}")
        return min(candidates, key=lambda s: (s.total_cost, s.worst_probe_count, s.root_choice))

    return dp(root)


def observation_action_collisions(problem: Problem) -> list[dict]:
    """Find legal-transcript collisions whose worlds share no protected action."""
    problem.validate()
    buckets: dict[tuple[str, ...], set[str]] = {}
    for h in problem.hypotheses:
        transcript = tuple(problem.outcomes[(h, probe)] for probe in problem.probes)
        buckets.setdefault(transcript, set()).add(h)
    out = []
    for transcript, worlds in sorted(buckets.items()):
        version = frozenset(worlds)
        if len(version) > 1 and not common_actions(problem, version):
            out.append({"transcript": list(transcript), "worlds": sorted(worlds)})
    return out


def partition_problem() -> Problem:
    hypotheses = ("h0", "h1", "h2", "h3")
    safe = {
        "h0": frozenset({"A"}), "h1": frozenset({"A"}),
        "h2": frozenset({"B"}), "h3": frozenset({"B"}),
    }
    outcomes = {
        ("h0", "region"): "L", ("h1", "region"): "L",
        ("h2", "region"): "R", ("h3", "region"): "R",
        ("h0", "within"): "0", ("h2", "within"): "0",
        ("h1", "within"): "1", ("h3", "within"): "1",
    }
    return Problem(
        hypotheses=hypotheses,
        safe_actions=safe,
        action_costs={"A": F(0), "B": F(0)},
        probes=("region", "within"),
        probe_costs={"region": F(1), "within": F(1)},
        outcomes=outcomes,
        equivalence_class={"h0": "A", "h1": "A", "h2": "B", "h3": "B"},
    )


def economic_problem(probe_cost: F) -> Problem:
    return Problem(
        hypotheses=("h0", "h1"),
        safe_actions={
            "h0": frozenset({"safe", "cheap0"}),
            "h1": frozenset({"safe", "cheap1"}),
        },
        action_costs={"safe": F(10), "cheap0": F(1), "cheap1": F(1)},
        probes=("which",),
        probe_costs={"which": probe_cost},
        outcomes={("h0", "which"): "0", ("h1", "which"): "1"},
    )


def misspecification_collision_problem() -> Problem:
    return Problem(
        hypotheses=("declared_like", "out_of_class_hostile"),
        safe_actions={
            "declared_like": frozenset({"A"}),
            "out_of_class_hostile": frozenset({"C"}),
        },
        action_costs={"A": F(0), "C": F(0)},
        probes=("legal_probe",),
        probe_costs={"legal_probe": F(1)},
        outcomes={
            ("declared_like", "legal_probe"): "same",
            ("out_of_class_hostile", "legal_probe"): "same",
        },
    )


def build_receipt() -> dict:
    lookup = F(1, 4)  # prospectively registered synthetic controller lookup price
    partition = partition_problem()
    cheap = economic_problem(F(2))
    dear = economic_problem(F(10))

    early = {
        parent: solve(partition, parent, policy_lookup_cost=lookup).as_json()
        for parent in PARENTS
    }
    naive_drd = solve(
        partition, "P-DRD", policy_lookup_cost=lookup, region_predicate_cost=F(1)
    )
    id_reference = solve(partition, "P-ID", policy_lookup_cost=lookup)

    economic_continue = {
        parent: solve(cheap, parent, policy_lookup_cost=lookup).as_json()
        for parent in ("P-ID", "P-DRD", "P-PAID")
    }
    economic_stop = {
        parent: solve(dear, parent, policy_lookup_cost=lookup).as_json()
        for parent in ("P-ID", "P-DRD", "P-PAID")
    }

    collisions = observation_action_collisions(misspecification_collision_problem())
    return {
        "study": "R0D_PAID_DECISION_REGION_EXECUTABLE_V1",
        "authority": "synthetic exact parent calibration; no operational terminal",
        "terminal": TERMINAL,
        "ml_authorized": False,
        "registered_synthetic_prices": {
            "policy_lookup_per_information_state": _fraction_json(lookup),
            "partition_probe": _fraction_json(F(1)),
            "naive_region_predicate_per_information_state": _fraction_json(F(1)),
            "economic_common_safe_action": _fraction_json(F(10)),
            "economic_specific_action": _fraction_json(F(1)),
        },
        "cases": {
            "decision_region_stops_before_identity": early,
            "predicate_cost_can_dominate": {
                "P-ID": id_reference.as_json(),
                "P-DRD-naive-scan": naive_drd.as_json(),
                "fewer_probes_but_more_total_cost": (
                    naive_drd.worst_probe_count < id_reference.worst_probe_count
                    and naive_drd.total_cost > id_reference.total_cost
                ),
            },
            "safe_but_economic_to_continue": economic_continue,
            "safe_and_economic_to_stop": economic_stop,
            "observation_hypothesis_class_hostile": {
                "collision_count": len(collisions),
                "collisions": collisions,
                "interpretation": "same complete legal transcript, disjoint protected actions",
            },
        },
        "source_custody": SOURCE_CUSTODY,
        "claim_boundary": [
            "microbenchmarks are synthetic witnesses, not DEV-5/6/X1 reproductions",
            "no learned selector/router and no production routing change",
            "P-PAID is exact only for the finite declared model and registered scalar prices",
            "out-of-class hostile demonstrates that region confidence is not authority under misspecification",
            "operational R0D terminal remains unearned until a real frozen donor population is run",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--github-notice", action="store_true")
    args = parser.parse_args(argv)
    receipt = build_receipt()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if args.github_notice:
        cases = receipt["cases"]
        print("::notice title=R0D paid decision region::"
              f"early DRD={cases['decision_region_stops_before_identity']['P-DRD']['total_cost']['exact']} "
              f"vs ID={cases['decision_region_stops_before_identity']['P-ID']['total_cost']['exact']}; "
              f"naive-predicate-dominates={cases['predicate_cost_can_dominate']['fewer_probes_but_more_total_cost']}; "
              f"terminal={receipt['terminal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
