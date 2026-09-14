#!/usr/bin/env python3
"""Exact witness for developmental-history trajectory length prediction.

Given a morphology M and ecology E, the developmental trajectory (infant to
child to adult) is predicted by the same PVR-3 pressure that determines the
adult morphology. The trajectory length (in state transitions) is proportional
to log(running_need / initial_capacity).

Morphologies: neural (high capacity, high gain), symbolic (low capacity, moderate gain),
              negative (zero gain — the negative twin).

Ecologies: simple (low serving obligation), moderate, complex (high obligation).

Python 3.8 safe, unittest, no network.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
import math


# ---------------------------------------------------------------------------
# Morphology definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Morphology:
    """A morphology archetype with developmental parameters."""
    name: str
    initial_capacity: float   # out-of-box competence before any transitions
    gain_rate: float          # capacity gain per transition (0 for negative twin)
    transition_cost: float    # cost of each developmental transition
    build_cost: float         # fixed construction cost B_build
    complexity_penalty: float # penalty for ecology complexity


# ---------------------------------------------------------------------------
# Ecology definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Ecology:
    """An ecology type with running_need parameter."""
    name: str
    running_need: float       # cumulative serving obligation over lifetime


# ---------------------------------------------------------------------------
# Trajectory computation
# ---------------------------------------------------------------------------

def trajectory_length(morph: Morphology, eco: Ecology) -> int:
    """Compute the number of developmental transitions needed.

    T(M, E) = ceil(log(running_need / initial_capacity) / gain_rate)

    Returns 0 if running_need <= initial_capacity (no development needed).
    Returns -1 for the negative twin (gain_rate = 0) — impossible to reach
    adult competence.
    """
    if eco.running_need <= morph.initial_capacity:
        return 0
    if morph.gain_rate <= 0:
        return -1  # negative twin: never reaches adult competence
    ratio = eco.running_need / morph.initial_capacity
    return math.ceil(math.log(ratio) / morph.gain_rate)


def burden_at_state(morph: Morphology, eco: Ecology, s: int) -> float:
    """Compute burden B(M, s, E) at developmental state s (transitions completed).

    B(M, s, E) = B_build + running_need * exp(-s * gain_rate) + s * transition_cost
    """
    return (
        morph.build_cost
        + eco.running_need * math.exp(-s * morph.gain_rate)
        + s * morph.transition_cost
    )


def developmental_trajectory(morph: Morphology, eco: Ecology) -> List[float]:
    """Compute the sequence of burden values through development.

    Returns [B(M, 0, E), B(M, 1, E), ..., B(M, T, E)].
    """
    T = trajectory_length(morph, eco)
    if T < 0:
        # Negative twin: return a fixed-length trajectory (10 states)
        T = 10
    return [burden_at_state(morph, eco, s) for s in range(T + 1)]


# ---------------------------------------------------------------------------
# Morphology registration
# ---------------------------------------------------------------------------

def register_morphologies() -> List[Morphology]:
    """Register 3 morphologies with calibrated parameters.

    Neural: high initial capacity, high gain, high build cost.
    Symbolic: low initial capacity, moderate gain, low build cost.
    Negative twin: zero gain rate — the negative control.
    """
    return [
        Morphology(
            name="neural",
            initial_capacity=8.0,
            gain_rate=0.5,
            transition_cost=2.0,
            build_cost=20.0,
            complexity_penalty=1.0,
        ),
        Morphology(
            name="symbolic",
            initial_capacity=4.0,
            gain_rate=0.3,
            transition_cost=1.0,
            build_cost=8.0,
            complexity_penalty=2.0,
        ),
        Morphology(
            name="negative",
            initial_capacity=6.0,
            gain_rate=0.0,       # zero gain — negative twin
            transition_cost=1.5,
            build_cost=12.0,
            complexity_penalty=1.5,
        ),
    ]


def register_ecologies() -> List[Ecology]:
    """Register 3 ecology types with increasing complexity."""
    return [
        Ecology(name="simple", running_need=10.0),
        Ecology(name="moderate", running_need=50.0),
        Ecology(name="complex", running_need=200.0),
    ]


# ---------------------------------------------------------------------------
# Phase computation
# ---------------------------------------------------------------------------

def compute_phase_table(
    morphologies: List[Morphology],
    ecologies: List[Ecology],
) -> Dict[str, Dict[str, int]]:
    """Compute trajectory lengths for all morphology-ecology pairs.

    Returns {eco_name: {morph_name: T}}.
    """
    table: Dict[str, Dict[str, int]] = {}
    for eco in ecologies:
        table[eco.name] = {}
        for morph in morphologies:
            table[eco.name][morph.name] = trajectory_length(morph, eco)
    return table


def verify_trajectory_monotonicity(
    morphologies: List[Morphology],
    ecologies: List[Ecology],
) -> Dict[str, bool]:
    """Verify Theorem 1: trajectory length increases with ecology complexity.

    For morphologies with gain_rate > 0, T(M, E_simple) <= T(M, E_moderate) <= T(M, E_complex).
    """
    results: Dict[str, bool] = {}
    for morph in morphologies:
        if morph.gain_rate <= 0:
            continue  # skip negative twin
        lengths = [trajectory_length(morph, eco) for eco in ecologies]
        # Check monotonic increase
        results[morph.name] = all(
            lengths[i] <= lengths[i + 1] for i in range(len(lengths) - 1)
        )
    return results


def verify_negative_twin_fails(
    morphologies: List[Morphology],
    ecologies: List[Ecology],
) -> Dict[str, bool]:
    """Verify Theorem 3: negative twin's trajectory length is not correlated
    with ecology complexity (it returns -1 for all ecologies)."""
    results: Dict[str, bool] = {}
    for morph in morphologies:
        if morph.gain_rate > 0:
            continue
        lengths = [trajectory_length(morph, eco) for eco in ecologies]
        # All should be -1 (impossible to reach adult competence)
        results[morph.name] = all(T == -1 for T in lengths)
    return results


def verify_trajectory_separates_morphologies(
    morphologies: List[Morphology],
    ecologies: List[Ecology],
) -> bool:
    """Verify Theorem 2: among adult-phase winners, the one with highest
    initial_capacity has the shortest trajectory.

    For each ecology, among morphologies that can reach adult competence (T >= 0),
    the one with highest initial_capacity should have T <= all others.
    """
    for eco in ecologies:
        candidates = []
        for morph in morphologies:
            T = trajectory_length(morph, eco)
            if T >= 0:
                candidates.append((morph.initial_capacity, T))
        if len(candidates) < 2:
            continue
        # Sort by initial_capacity descending
        candidates.sort(key=lambda x: -x[0])
        # Highest capacity should have shortest trajectory
        best_cap, best_T = candidates[0]
        for cap, T in candidates[1:]:
            if T < best_T:
                return False  # violation: lower capacity has shorter trajectory
    return True


# ---------------------------------------------------------------------------
# Full results
# ---------------------------------------------------------------------------

def build_results() -> dict:
    """Compute all results and assertions."""
    morphologies = register_morphologies()
    ecologies = register_ecologies()
    phase_table = compute_phase_table(morphologies, ecologies)
    monotonicity = verify_trajectory_monotonicity(morphologies, ecologies)
    negative_twin = verify_negative_twin_fails(morphologies, ecologies)
    separation = verify_trajectory_separates_morphologies(morphologies, ecologies)

    # Compute trajectories for detailed output
    trajectories = {}
    for morph in morphologies:
        trajectories[morph.name] = {}
        for eco in ecologies:
            traj = developmental_trajectory(morph, eco)
            trajectories[morph.name][eco.name] = {
                "length": len(traj) - 1,
                "burden_values": [round(b, 4) for b in traj],
            }

    # Additional assertions
    assertions = {}

    # A1: Trajectory length increases with ecology complexity
    assertions["A1_monotonicity"] = all(monotonicity.values())

    # A2: Simple ecology gives short trajectory for all morphologies
    simple_lengths = [phase_table["simple"][m.name] for m in morphologies if m.gain_rate > 0]
    assertions["A2_simple_short"] = all(T <= 5 for T in simple_lengths)

    # A3: Complex ecology gives long trajectory, especially for rigid morphologies
    complex_lengths = [phase_table["complex"][m.name] for m in morphologies if m.gain_rate > 0]
    assertions["A3_complex_long"] = all(T >= 3 for T in complex_lengths)

    # A4: Negative twin fails (constant trajectory rejected)
    assertions["A4_negative_twin_fails"] = all(negative_twin.values())

    # A5: Neural has shorter trajectory than symbolic at complex ecology
    neural_T = phase_table["complex"]["neural"]
    symbolic_T = phase_table["complex"]["symbolic"]
    assertions["A5_neural_shorter_at_complex"] = neural_T <= symbolic_T

    # A6: Neural reaches adult competence at simple ecology (T=0 or small)
    assertions["A6_neural_adult_simple"] = phase_table["simple"]["neural"] <= 2

    # A7: Trajectory separation holds
    assertions["A7_separation"] = separation

    # A8: All trajectory lengths are non-negative for non-negative twins
    for morph in morphologies:
        if morph.gain_rate > 0:
            for eco in ecologies:
                T = phase_table[eco.name][morph.name]
                assertions[f"A8_nonneg_{morph.name}_{eco.name}"] = T >= 0

    # A9: Burden is decreasing along trajectory for non-negative twins
    for morph in morphologies:
        if morph.gain_rate > 0:
            for eco in ecologies:
                traj = trajectories[morph.name][eco.name]["burden_values"]
                is_decreasing = all(traj[i] >= traj[i + 1] for i in range(len(traj) - 1))
                assertions[f"A9_burden_decreasing_{morph.name}_{eco.name}"] = is_decreasing

    # A10: Gain rate zero implies infinite/impossible trajectory
    for morph in morphologies:
        if morph.gain_rate <= 0:
            for eco in ecologies:
                T = phase_table[eco.name][morph.name]
                assertions[f"A10_zero_gain_{morph.name}_{eco.name}"] = T == -1

    all_pass = all(assertions.values())

    return {
        "morphologies": [
            {"name": m.name, "initial_capacity": m.initial_capacity,
             "gain_rate": m.gain_rate, "transition_cost": m.transition_cost,
             "build_cost": m.build_cost, "complexity_penalty": m.complexity_penalty}
            for m in morphologies
        ],
        "ecologies": [
            {"name": e.name, "running_need": e.running_need}
            for e in ecologies
        ],
        "phase_table": phase_table,
        "trajectories": trajectories,
        "monotonicity_check": monotonicity,
        "negative_twin_check": negative_twin,
        "separation_check": separation,
        "assertions": assertions,
        "all_pass": all_pass,
    }


def main() -> None:
    result = build_results()
    out_path = __import__("pathlib").Path(__file__).with_name("RESULT_V1.json")
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_pass": result["all_pass"],
        "assertions": result["assertions"],
        "phase_table": result["phase_table"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
