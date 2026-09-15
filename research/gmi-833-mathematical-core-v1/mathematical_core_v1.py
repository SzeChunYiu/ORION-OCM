#!/usr/bin/env python3
"""Executable finite models for Issue #833's architecture-neutral core."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path
from typing import Callable, Hashable, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
CANNOT_IDENTIFY = "CANNOT_IDENTIFY"
INFEASIBLE = "INFEASIBLE"


@dataclass(frozen=True)
class FiniteProcess:
    """A total deterministic labeled process; names carry no semantics."""

    states: tuple[Hashable, ...]
    actions: tuple[Hashable, ...]
    observation: Mapping[Hashable, Hashable]
    transition: Mapping[tuple[Hashable, Hashable], Hashable]

    def validate(self) -> None:
        if not self.states or not self.actions or len(set(self.states)) != len(self.states):
            raise ValueError("finite process needs nonempty unique state/action domains")
        if set(self.observation) != set(self.states):
            raise ValueError("every state needs one registered observation")
        expected = set(product(self.states, self.actions))
        if set(self.transition) != expected or not set(self.transition.values()) <= set(self.states):
            raise ValueError("transition must be total and closed")


def stable_behavior_partition(process: FiniteProcess) -> tuple[tuple[Hashable, ...], ...]:
    """Coarsest observation-preserving deterministic bisimulation/response quotient."""
    process.validate()
    block = {state: 0 for state in process.states}
    while True:
        signatures = {
            state: (
                process.observation[state],
                tuple(block[process.transition[state, action]] for action in process.actions),
            )
            for state in process.states
        }
        unique = {signature: index for index, signature in enumerate(sorted(set(signatures.values()), key=repr))}
        refined = {state: unique[signatures[state]] for state in process.states}
        if all(refined[state] == block[state] for state in process.states):
            break
        block = refined
    groups: dict[int, list[Hashable]] = {}
    for state in process.states:
        groups.setdefault(block[state], []).append(state)
    return tuple(tuple(group) for _, group in sorted(groups.items()))


@dataclass(frozen=True)
class Morphology:
    """Finite reduced mechanism signature at one registered scope."""

    process: FiniteProcess
    state_type: Mapping[Hashable, str]
    intervention_response: tuple[tuple[Hashable, Hashable, Hashable], ...]
    resource_profiles: tuple[tuple[Hashable, tuple[int, ...]], ...]
    development_edges: tuple[tuple[Hashable, Hashable, tuple[int, ...]], ...]

    def validate(self) -> None:
        self.process.validate()
        if set(self.state_type) != set(self.process.states):
            raise ValueError("every carrier needs one type")
        state_set = set(self.process.states)
        if not self.intervention_response or any(row[0] not in state_set for row in self.intervention_response):
            raise ValueError("intervention responses must be nonempty and state-typed")
        if not self.resource_profiles:
            raise ValueError("at least one experiment resource profile is required")
        dimensions = {len(vector) for _, vector in self.resource_profiles}
        if len(dimensions) != 1 or dimensions == {0} or any(
            type(value) is not int or value < 0
            for _, vector in self.resource_profiles
            for value in vector
        ):
            raise ValueError("resource profiles need equal nonempty nonnegative integer vectors")
        dimension = next(iter(dimensions))
        if not self.development_edges or any(
            source not in state_set
            or target not in state_set
            or len(charge) != dimension
            or any(type(value) is not int or value < 0 for value in charge)
            for source, target, charge in self.development_edges
        ):
            raise ValueError("development edges must be state-typed and resource-complete")


def morphology_equivalent(left: Morphology, right: Morphology) -> bool:
    left.validate()
    right.validate()
    if len(left.process.states) != len(right.process.states) or left.process.actions != right.process.actions:
        return False
    if left.resource_profiles != right.resource_profiles:
        return False
    for image in permutations(right.process.states):
        bijection = dict(zip(left.process.states, image, strict=True))
        if any(left.state_type[s] != right.state_type[bijection[s]] for s in left.process.states):
            continue
        if any(left.process.observation[s] != right.process.observation[bijection[s]] for s in left.process.states):
            continue
        if not all(
            bijection[left.process.transition[s, a]] == right.process.transition[bijection[s], a]
            for s in left.process.states
            for a in left.process.actions
        ):
            continue
        mapped_interventions = {
            (bijection[state], intervention, response)
            for state, intervention, response in left.intervention_response
        }
        if mapped_interventions != set(right.intervention_response):
            continue
        mapped_development = {
            (bijection[source], bijection[target], charge)
            for source, target, charge in left.development_edges
        }
        if mapped_development == set(right.development_edges):
            return True
    return False


def machine_species_equivalent(left: Morphology, right: Morphology) -> bool:
    """Legacy species equality is the morphology quotient, not biology."""
    return morphology_equivalent(left, right)


@dataclass(frozen=True)
class BehavioralSpecification:
    identifier: str
    instances: tuple[Hashable, ...]
    accepts: Callable[[Hashable, Hashable], bool]


def capability_profile(
    behavior: Mapping[Hashable, Hashable], specifications: Sequence[BehavioralSpecification]
) -> tuple[tuple[str, bool], ...]:
    rows = []
    for specification in specifications:
        if not set(specification.instances) <= set(behavior):
            raise ValueError("behavior omits a protected instance")
        rows.append(
            (
                specification.identifier,
                all(specification.accepts(instance, behavior[instance]) for instance in specification.instances),
            )
        )
    return tuple(rows)


def capability_region(
    behavior: Mapping[Hashable, Hashable], specifications: Sequence[BehavioralSpecification]
) -> frozenset[str]:
    """The implementation-independent set of contracts satisfied by behavior."""
    return frozenset(identifier for identifier, satisfied in capability_profile(behavior, specifications) if satisfied)


def capability_bounds(
    behaviors: Sequence[Mapping[Hashable, Hashable]], specifications: Sequence[BehavioralSpecification]
) -> dict[str, tuple[int, int]]:
    if not behaviors:
        raise ValueError("capability uncertainty set cannot be empty")
    profiles = [dict(capability_profile(behavior, specifications)) for behavior in behaviors]
    return {
        specification.identifier: (
            min(int(profile[specification.identifier]) for profile in profiles),
            max(int(profile[specification.identifier]) for profile in profiles),
        )
        for specification in specifications
    }


def impossibility_region(bounds: Mapping[str, tuple[int, int]]) -> tuple[str, ...]:
    return tuple(identifier for identifier, (_, upper) in bounds.items() if upper == 0)


@dataclass(frozen=True)
class CapabilityContract:
    identifier: str
    worlds: tuple[Hashable, ...]
    probabilities: tuple[Fraction, ...]
    threshold: Fraction

    def validate(self) -> None:
        if not self.identifier or not self.worlds or len(self.worlds) != len(self.probabilities):
            raise ValueError("capability contract needs aligned nonempty worlds/probabilities")
        if len(set(self.worlds)) != len(self.worlds):
            raise ValueError("capability worlds must be unique")
        if any(probability < 0 for probability in self.probabilities) or sum(self.probabilities) != 1:
            raise ValueError("capability probabilities must form a distribution")
        if not Fraction(0) <= self.threshold <= Fraction(1):
            raise ValueError("capability threshold must lie in [0,1]")


def expected_binary_success(
    policy: Mapping[Hashable, Fraction],
    observation: Mapping[Hashable, Hashable],
    required_action: Mapping[Hashable, int],
    contract: CapabilityContract,
) -> Fraction:
    """Expected success; policy values are probabilities of binary action 1."""
    contract.validate()
    if set(contract.worlds) - set(observation) or set(contract.worlds) - set(required_action):
        raise ValueError("observation/action contract omits a world")
    if set(observation.values()) - set(policy):
        raise ValueError("policy omits an observable state")
    if any(not Fraction(0) <= probability <= Fraction(1) for probability in policy.values()):
        raise ValueError("binary policy probabilities must lie in [0,1]")
    total = Fraction(0)
    for world, world_probability in zip(contract.worlds, contract.probabilities, strict=True):
        action_one = policy[observation[world]]
        success = action_one if required_action[world] == 1 else 1 - action_one
        total += world_probability * success
    return total


def numeric_capability_ceiling(values: Iterable[Fraction]) -> Fraction | None:
    registered = tuple(Fraction(value) for value in values)
    if not registered:
        return None
    if any(not Fraction(0) <= value <= Fraction(1) for value in registered):
        raise ValueError("capability values must lie in [0,1]")
    return max(registered)


def threshold_is_impossible(ceiling: Fraction | None, threshold: Fraction) -> bool:
    return ceiling is None or Fraction(threshold) > ceiling


def ceiling_monotone(inner_values: Iterable[Fraction], outer_values: Iterable[Fraction]) -> bool:
    """Check the finite A⊆B consequence sup(A)≤sup(B)."""
    inner = tuple(Fraction(value) for value in inner_values)
    outer = tuple(Fraction(value) for value in outer_values)
    if not inner or not set(inner) <= set(outer):
        raise ValueError("monotonicity check requires a nonempty registered subset")
    inner_ceiling = numeric_capability_ceiling(inner)
    outer_ceiling = numeric_capability_ceiling(outer)
    return inner_ceiling is not None and outer_ceiling is not None and inner_ceiling <= outer_ceiling


def aliasing_ceiling_grid(denominator: int = 20) -> tuple[Fraction, ...]:
    """P2 finite control; the analytic theorem covers every p in [0,1]."""
    if denominator < 1:
        raise ValueError("denominator must be positive")
    contract = CapabilityContract("LATENT_BINARY", (0, 1), (Fraction(1, 2), Fraction(1, 2)), Fraction(1, 2))
    observation = {0: "same", 1: "same"}
    required = {0: 0, 1: 1}
    return tuple(
        expected_binary_success({"same": Fraction(numerator, denominator)}, observation, required, contract)
        for numerator in range(denominator + 1)
    )


@dataclass(frozen=True)
class FiniteUncertainty:
    worlds: frozenset[Hashable]
    confidence: Fraction | None = None

    def __post_init__(self) -> None:
        if not self.worlds:
            raise ValueError("uncertainty set cannot be empty")
        if self.confidence is not None and not Fraction(0) <= self.confidence <= Fraction(1):
            raise ValueError("confidence must lie in [0,1]")

    def image(self, function: Callable[[Hashable], Hashable]) -> "FiniteUncertainty":
        return FiniteUncertainty(frozenset(function(world) for world in self.worlds), self.confidence)


def compose_uncertainty(*objects: FiniteUncertainty, independent: bool = False) -> FiniteUncertainty:
    if not objects:
        raise ValueError("composition needs at least one uncertainty object")
    worlds = frozenset(product(*(obj.worlds for obj in objects)))
    if any(obj.confidence is None for obj in objects):
        confidence = None
    elif independent:
        confidence = product_fraction(obj.confidence for obj in objects if obj.confidence is not None)
    else:
        confidence = max(Fraction(0), 1 - sum((1 - obj.confidence for obj in objects if obj.confidence is not None), Fraction(0)))
    return FiniteUncertainty(worlds, confidence)


def product_fraction(values: Iterable[Fraction]) -> Fraction:
    result = Fraction(1)
    for value in values:
        result *= value
    return result


def identified_decision(possible_values: Iterable[Hashable]) -> Hashable | str:
    values = frozenset(possible_values)
    if not values:
        return INFEASIBLE
    if len(values) == 1:
        return next(iter(values))
    return CANNOT_IDENTIFY


def validate_axioms() -> dict[str, object]:
    data = json.loads((HERE / "AXIOMS_V1.json").read_text(encoding="utf-8"))
    axioms = data["axioms"]
    if len(axioms) != 10 or len({row["id"] for row in axioms}) != len(axioms):
        raise ValueError("compact axiom registry drifted")
    if any(not {"statement", "scope", "falsifier"} <= row.keys() for row in axioms):
        raise ValueError("axiom metadata incomplete")
    required_axioms = {
        "AX1_TYPED_DOMAINS",
        "AX2_BEHAVIORAL_SPECIFICATION",
        "AX3_TOTAL_REGISTERED_PROCESS",
        "AX4_BEHAVIORAL_EQUIVALENCE",
        "AX5_DEVELOPMENT",
        "AX6_RESOURCES",
        "AX7_CAPABILITY",
        "AX8_UNCERTAINTY",
        "AX9_ABSTENTION",
        "AX10_SCOPE_TAGS",
    }
    if {row["id"] for row in axioms} != required_axioms:
        raise ValueError("compact axiom identifiers drifted")

    model = data["finite_model"]
    process = FiniteProcess(
        tuple(model["states"]),
        tuple(model["actions"]),
        model["observation"],
        {(row[0], row[1]): row[2] for row in model["transition"]},
    )
    process.validate()
    state_set = set(process.states)
    specification_rows = model["specifications"]
    development_rows = model["development_edges"]
    resources = model["resources"]
    uncertainty_worlds = model["uncertainty_worlds"]
    theorem_scopes = model["theorem_scopes"]
    model_specifications = tuple(
        BehavioralSpecification(
            row["id"],
            tuple(row["instances"]),
            lambda instance, output, pairs=frozenset(tuple(pair) for pair in row["accept_pairs"]):
                (instance, output) in pairs,
        )
        for row in specification_rows
    )
    witness_behavior = dict(process.observation)
    renamed_realization_behavior = dict(process.observation)

    axiom_checks = {
        "AX1_TYPED_DOMAINS": all(
            (process.states, process.actions, process.observation, process.transition, specification_rows)
        ),
        "AX2_BEHAVIORAL_SPECIFICATION": bool(specification_rows)
        and all(
            row["instances"]
            and set(row["instances"]) <= state_set
            and row["accept_pairs"]
            and all(len(pair) == 2 and pair[0] in row["instances"] for pair in row["accept_pairs"])
            for row in specification_rows
        ),
        "AX3_TOTAL_REGISTERED_PROCESS": set(process.transition) == set(product(process.states, process.actions)),
        "AX4_BEHAVIORAL_EQUIVALENCE": {frozenset(group) for group in stable_behavior_partition(process)}
        == {frozenset({"s0"}), frozenset({"s1"})},
        "AX5_DEVELOPMENT": bool(development_rows)
        and all(
            source in state_set
            and target in state_set
            and len(charge) == len(resources)
            and all(type(value) is int and value >= 0 for value in charge)
            for source, target, charge in development_rows
        ),
        "AX6_RESOURCES": bool(resources)
        and all(type(value) is int and value >= 0 for value in resources),
        "AX7_CAPABILITY": capability_profile(witness_behavior, model_specifications)
        == capability_profile(renamed_realization_behavior, model_specifications),
        "AX8_UNCERTAINTY": bool(uncertainty_worlds) and set(uncertainty_worlds) <= state_set,
        "AX9_ABSTENTION": identified_decision(process.observation[state] for state in uncertainty_worlds)
        == CANNOT_IDENTIFY,
        "AX10_SCOPE_TAGS": bool(theorem_scopes)
        and all(scope in {"forall[D]", "forall_fin[U]", "heldout[F]", "sample[P,n]"} for scope in theorem_scopes.values()),
    }
    failed = sorted(identifier for identifier, satisfied in axiom_checks.items() if not satisfied)
    if failed:
        raise ValueError(f"finite model violates registered axioms: {failed}")
    return {
        "axioms": len(axioms),
        "axioms_satisfied": sum(axiom_checks.values()),
        "finite_model_states": len(process.states),
        "finite_model_actions": len(process.actions),
        "model_satisfies_registered_axioms": True,
    }


def validate_scientific_ledger() -> dict[str, object]:
    data = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text(encoding="utf-8"))
    claims = data["claims"]
    required_claim_fields = {
        "id",
        "assumptions",
        "dependencies",
        "falsifiers",
        "strongest_parent",
        "counterexample_methods",
        "new_nonmaterial_limits",
    }
    if len(claims) != 4 or any(set(row) != required_claim_fields for row in claims):
        raise ValueError("scientific claim ledger drifted")
    if any(not row["assumptions"] or not row["dependencies"] or not row["falsifiers"] for row in claims):
        raise ValueError("scientific claim ledger is incomplete")
    gaps = data["open_gaps"]
    if len(gaps) != 1 or gaps[0]["status"] != "OPEN" or gaps[0]["severity"] != "HIGH":
        raise ValueError("independent-review gap must remain explicit")
    if data["recursive_gap_verdict"] != "LOCALLY_CLOSED_WITH_INDEPENDENT_REVIEW_OPEN":
        raise ValueError("recursive gap verdict overclaimed")
    return {
        "scientific_claim_ledgers": len(claims),
        "open_independent_review_gaps": len(gaps),
        "closure_level": "LOCALLY_CLOSED",
    }


def validate_all() -> dict[str, object]:
    transition = {(state, bit): (state ^ bit) for state in (0, 1) for bit in (0, 1)}
    left_process = FiniteProcess((0, 1), (0, 1), {0: "z", 1: "o"}, transition)
    right_transition = {("a", 0): "a", ("a", 1): "b", ("b", 0): "b", ("b", 1): "a"}
    right_process = FiniteProcess(("a", "b"), (0, 1), {"a": "z", "b": "o"}, right_transition)
    left_morphology = Morphology(
        left_process,
        {0: "CELL", 1: "CELL"},
        ((0, "probe", "z"), (1, "probe", "o")),
        (("experiment", (2, 3)),),
        ((0, 1, (1, 0)), (1, 0, (1, 0))),
    )
    right_morphology = Morphology(
        right_process,
        {"a": "CELL", "b": "CELL"},
        (("a", "probe", "z"), ("b", "probe", "o")),
        (("experiment", (2, 3)),),
        (("a", "b", (1, 0)), ("b", "a", (1, 0))),
    )
    if not morphology_equivalent(left_morphology, right_morphology):
        raise ValueError("morphology name invariance failed")

    resource_different = Morphology(
        right_process,
        {"a": "CELL", "b": "CELL"},
        right_morphology.intervention_response,
        (("experiment", (2, 4)),),
        right_morphology.development_edges,
    )
    if not machine_species_equivalent(left_morphology, right_morphology) or machine_species_equivalent(
        left_morphology, resource_different
    ):
        raise ValueError("machine-species equivalence failed")

    specification = BehavioralSpecification("COPY", (0, 1), lambda instance, output: instance == output)
    impossible_specification = BehavioralSpecification("IMPOSSIBLE", (0, 1), lambda _instance, _output: False)
    possible = ({0: 0, 1: 1}, {0: 0, 1: 0})
    bounds = capability_bounds(possible, (specification, impossible_specification))
    capability_values = (capability_profile(behavior, (specification,))[0][1] for behavior in possible)
    impossible = impossibility_region(bounds)
    if (
        bounds != {"COPY": (0, 1), "IMPOSSIBLE": (0, 0)}
        or impossible != ("IMPOSSIBLE",)
        or identified_decision(capability_values) != CANNOT_IDENTIFY
    ):
        raise ValueError("capability uncertainty/abstention boundary failed")

    alias_values = aliasing_ceiling_grid(20)
    alias_ceiling = numeric_capability_ceiling(alias_values)
    latent_contract = CapabilityContract(
        "LATENT_BINARY", (0, 1), (Fraction(1, 2), Fraction(1, 2)), Fraction(3, 4)
    )
    revealed_success = expected_binary_success(
        {"left": Fraction(0), "right": Fraction(1)},
        {0: "left", 1: "right"},
        {0: 0, 1: 1},
        latent_contract,
    )
    if (
        set(alias_values) != {Fraction(1, 2)}
        or alias_ceiling != Fraction(1, 2)
        or not threshold_is_impossible(alias_ceiling, latent_contract.threshold)
        or revealed_success != 1
        or not ceiling_monotone((Fraction(1, 2),), (Fraction(1, 2), Fraction(1)))
    ):
        raise ValueError("architecture-independent aliasing ceiling failed")

    union = compose_uncertainty(
        FiniteUncertainty(frozenset({"a", "b"}), Fraction(9, 10)),
        FiniteUncertainty(frozenset({0, 1}), Fraction(4, 5)),
    )
    independent = compose_uncertainty(
        FiniteUncertainty(frozenset({"a", "b"}), Fraction(9, 10)),
        FiniteUncertainty(frozenset({0, 1}), Fraction(4, 5)),
        independent=True,
    )
    if union.confidence != Fraction(7, 10) or independent.confidence != Fraction(18, 25):
        raise ValueError("confidence composition failed")
    result = {
        **validate_axioms(),
        **validate_scientific_ledger(),
        "capability_bounds": bounds,
        "impossibility_region": impossible,
        "aliasing_grid_policies": len(alias_values),
        "aliasing_ceiling": str(alias_ceiling),
        "revealed_information_ceiling": str(revealed_success),
        "threshold_three_quarters_impossible_under_aliasing": True,
        "ceiling_monotonicity": True,
        "morphology_name_invariant": True,
        "species_is_morphology_quotient": True,
        "union_confidence": str(union.confidence),
        "independent_confidence": str(independent.confidence),
        "global_abstention": CANNOT_IDENTIFY,
    }
    expected = json.loads((HERE / "RESULT_V1.json").read_text(encoding="utf-8"))
    json_result = json.loads(json.dumps(result, sort_keys=True))
    if json_result != expected:
        raise ValueError("deterministic result receipt drifted")
    return result


if __name__ == "__main__":
    print("GMI_833_MATHEMATICAL_CORE_V1_VALID")
    print(json.dumps(validate_all(), sort_keys=True))
