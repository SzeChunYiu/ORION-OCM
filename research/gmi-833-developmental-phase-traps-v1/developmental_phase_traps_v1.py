#!/usr/bin/env python3
"""Exact finite developmental phase, trap, and reachability laws for issue #910."""

from __future__ import annotations

from collections import deque
from fractions import Fraction
from hashlib import sha1
from itertools import product
import json
from pathlib import Path
from typing import Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
CLAIM_CEILING = (
    "GMI_833_FINITE_DEVELOPMENTAL_PHASE_HYSTERESIS_TRAP_ESCAPE_"
    "AND_REACHABILITY_MASS_AT_REGISTERED_SCOPE"
)
FORBIDDEN_PROMOTIONS = (
    "CONTINUOUS_THERMODYNAMIC_PHASE_TRANSITION",
    "UNIVERSAL_HYSTERESIS",
    "ALL_DEVELOPMENTAL_TRAPS_ESCAPABLE",
    "STATIONARY_OR_ASYMPTOTIC_MARKOV_CONCLUSION",
    "REAL_SYSTEM_VALIDATION",
    "COMPLETE_GMI",
)
PARENT_PINS = (
    (
        "developmental_potential_909",
        "research/gmi-833-developmental-potential-evolvability-v1/RESULT_V1.json",
        "6ba3a53f6184b341a851bfd60683c3afff828980",
        "claim_ceiling",
        "GMI_833_FINITE_DEVELOPMENTAL_POTENTIAL_EVOLVABILITY_AND_CAPITAL_SEPARATION_AT_REGISTERED_SCOPE",
    ),
    (
        "history_switching_898",
        "research/gmi-833-history-switching-hysteresis-v1/RESULT_V1.json",
        "37b6b37a97d32fec604edeae7ca19971db4015b7",
        "claim_ceiling",
        "GMI_FINITE_HISTORY_SWITCHING_AND_HYSTERESIS_SELECTION_AT_REGISTERED_SCOPE",
    ),
    (
        "finite_search_budget_877",
        "research/gmi-833-finite-search-budget-morphology-v1/RESULT_V1.json",
        "4ea315e651475cc8afcc39860a0d2ac621e9f571",
        "claim_ceiling",
        "GMI_FINITE_SEARCH_PREFIX_MORPHOLOGY_SELECTION_DERIVED_AT_REGISTERED_SCOPE",
    ),
    (
        "global_vs_reachable_874",
        "research/gmi-833-global-vs-reachable-morphology-v1/RESULT_V1.json",
        "37a0dda56649c02de1dd733b20a1266d481a3d30",
        "claim_ceiling",
        "GMI_FINITE_GLOBAL_VS_REACHABLE_MORPHOLOGY_SELECTION_SEPARATED_AT_REGISTERED_SCOPE",
    ),
    (
        "section_e_reachability",
        "research/gmi-section-e-reachability-v1/RESULT_E1.json",
        "369d3bd09279c4136ffeed469d0ffb0b6b5d443b",
        None,
        None,
    ),
)


def exact(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or type(value) not in (int, Fraction):
        raise ValueError("numeric registrations must use exact integers or Fractions")
    return Fraction(value)


def exact_vector(
    values: Sequence[int | Fraction], *, positive_total: bool = False
) -> tuple[Fraction, ...]:
    vector = tuple(exact(value) for value in values)
    if not vector or any(value < 0 for value in vector):
        raise ValueError("resource vectors must be nonempty and nonnegative")
    if positive_total and not any(value > 0 for value in vector):
        raise ValueError("at least one resource coordinate must be positive")
    return vector


def validate_states(states: Iterable[str], initial: str | None = None) -> tuple[str, ...]:
    carrier = tuple(states)
    if (
        not carrier
        or any(type(state) is not str or not state for state in carrier)
        or len(set(carrier)) != len(carrier)
    ):
        raise ValueError("state carrier must contain unique nonempty architecture-neutral names")
    if initial is not None and initial not in carrier:
        raise ValueError("initial state must belong to the state carrier")
    return carrier


def repo_root(start: Path | None = None) -> Path:
    current = (start or HERE).resolve()
    while current.parent != current:
        if (current / ".git").exists() or (current / "research").is_dir():
            return current
        current = current.parent
    return HERE.parents[1]


def git_blob_sha(data: bytes) -> str:
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def audit_parents(root: Path | None = None) -> dict[str, object]:
    root = root or repo_root()
    rows = []
    for name, path, expected_blob, field, expected_claim in PARENT_PINS:
        target = root / path
        if not target.is_file():
            rows.append(
                {
                    "name": name,
                    "path": path,
                    "actual_blob": None,
                    "blob_ok": False,
                    "claim_ok": False,
                }
            )
            continue
        data = target.read_bytes()
        actual_blob = git_blob_sha(data)
        claim_ok = True
        if field is not None:
            try:
                claim_ok = json.loads(data).get(field) == expected_claim
            except (UnicodeDecodeError, json.JSONDecodeError):
                claim_ok = False
        rows.append(
            {
                "name": name,
                "path": path,
                "actual_blob": actual_blob,
                "blob_ok": actual_blob == expected_blob,
                "claim_ok": claim_ok,
            }
        )
    return {"rows": rows, "all_ok": all(row["blob_ok"] and row["claim_ok"] for row in rows)}


def vector_leq(left: Sequence[Fraction], right: Sequence[Fraction]) -> bool:
    return len(left) == len(right) and all(
        x <= y for x, y in zip(left, right)
    )


def add_vectors(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    if len(left) != len(right):
        raise ValueError("resource vectors must align")
    return tuple(x + y for x, y in zip(left, right))


def normalize_edges(
    states: Sequence[str],
    edges: Sequence[tuple[str, str, Sequence[int | Fraction]]],
    dimension: int,
) -> tuple[tuple[str, str, tuple[Fraction, ...]], ...]:
    carrier = set(states)
    normalized = []
    for source, target, raw_cost in edges:
        if source not in carrier or target not in carrier:
            raise ValueError("developmental edges must stay inside the state carrier")
        cost = exact_vector(raw_cost)
        if len(cost) != dimension:
            raise ValueError("edge costs must align with the registered resource dimension")
        normalized.append((source, target, cost))
    return tuple(normalized)


def pareto_path_costs(
    states: Iterable[str],
    initial: str,
    edges: Sequence[tuple[str, str, Sequence[int | Fraction]]],
    dimension: int,
) -> dict[str, tuple[tuple[Fraction, ...], ...]]:
    """Return every nondominated source-to-state path-cost label."""
    carrier = validate_states(states, initial)
    if isinstance(dimension, bool) or type(dimension) is not int or dimension <= 0:
        raise ValueError("resource dimension must be a positive integer")
    normalized = normalize_edges(carrier, edges, dimension)
    labels: dict[str, list[tuple[Fraction, ...]]] = {state: [] for state in carrier}
    zero = tuple(Fraction(0) for _ in range(dimension))
    labels[initial] = [zero]
    queue = deque([(initial, zero)])
    while queue:
        state, accumulated = queue.popleft()
        if accumulated not in labels[state]:
            continue
        for source, target, edge_cost in normalized:
            if source != state:
                continue
            candidate = add_vectors(accumulated, edge_cost)
            if any(vector_leq(existing, candidate) for existing in labels[target]):
                continue
            labels[target] = [
                existing
                for existing in labels[target]
                if not vector_leq(candidate, existing)
            ]
            labels[target].append(candidate)
            queue.append((target, candidate))
    return {
        state: tuple(sorted(costs))
        for state, costs in labels.items()
        if costs
    }


def ray_cost_threshold(
    cost: Sequence[int | Fraction], ray: Sequence[int | Fraction]
) -> Fraction | None:
    path_cost = exact_vector(cost)
    direction = exact_vector(ray, positive_total=True)
    if len(path_cost) != len(direction):
        raise ValueError("path cost and budget ray must align")
    ratios = []
    for value, rate in zip(path_cost, direction):
        if rate == 0:
            if value > 0:
                return None
        else:
            ratios.append(value / rate)
    return max(ratios, default=Fraction(0))


def phase_schedule(
    states: Iterable[str],
    initial: str,
    edges: Sequence[tuple[str, str, Sequence[int | Fraction]]],
    scores: Mapping[str, int | Fraction],
    ray: Sequence[int | Fraction],
) -> dict[str, object]:
    """Exact state-entry thresholds and complete reachable score argmax sets."""
    carrier = validate_states(states, initial)
    direction = exact_vector(ray, positive_total=True)
    if set(scores) != set(carrier):
        raise ValueError("every and only registered states need an external score")
    exact_scores = {state: exact(scores[state]) for state in carrier}
    labels = pareto_path_costs(carrier, initial, edges, len(direction))
    thresholds: dict[str, Fraction | None] = {}
    witness_costs: dict[str, tuple[Fraction, ...] | None] = {}
    for state in carrier:
        candidates = []
        for cost in labels.get(state, ()):
            threshold = ray_cost_threshold(cost, direction)
            if threshold is not None:
                candidates.append((threshold, cost))
        if not candidates:
            thresholds[state] = None
            witness_costs[state] = None
        else:
            threshold, cost = min(candidates)
            thresholds[state] = threshold
            witness_costs[state] = cost

    event_thresholds = sorted({value for value in thresholds.values() if value is not None})
    events = []
    previous_argmax = None
    for index, budget_scale in enumerate(event_thresholds):
        reachable = tuple(
            state
            for state in carrier
            if thresholds[state] is not None and thresholds[state] <= budget_scale
        )
        best_score = max(exact_scores[state] for state in reachable)
        argmax = tuple(state for state in reachable if exact_scores[state] == best_score)
        next_threshold = (
            event_thresholds[index + 1] if index + 1 < len(event_thresholds) else None
        )
        events.append(
            {
                "threshold": budget_scale,
                "next_threshold": next_threshold,
                "entrants": tuple(
                    state for state in carrier if thresholds[state] == budget_scale
                ),
                "reachable": reachable,
                "argmax": argmax,
                "best_score": best_score,
                "argmax_changed": previous_argmax is None or argmax != previous_argmax,
            }
        )
        previous_argmax = argmax
    return {
        "ray": direction,
        "thresholds": thresholds,
        "threshold_witness_costs": witness_costs,
        "pareto_path_costs": labels,
        "events": tuple(events),
    }


def validate_switching(
    forms: Iterable[str],
    base_costs: Mapping[str, int | Fraction],
    switching: Mapping[tuple[str, str], int | Fraction],
) -> tuple[tuple[str, ...], dict[str, Fraction], dict[tuple[str, str], Fraction]]:
    carrier = validate_states(forms)
    if set(base_costs) != set(carrier):
        raise ValueError("base-cost domain must equal the form carrier")
    required = {(previous, current) for previous in carrier for current in carrier}
    if set(switching) != required:
        raise ValueError("switching-cost domain must be complete")
    base = {form: exact(base_costs[form]) for form in carrier}
    switch = {edge: exact(switching[edge]) for edge in required}
    if any(value < 0 for value in base.values()) or any(
        value < 0 for value in switch.values()
    ):
        raise ValueError("base and switching costs must be nonnegative")
    return carrier, base, switch


def switching_selection(
    forms: Iterable[str],
    base_costs: Mapping[str, int | Fraction],
    switching: Mapping[tuple[str, str], int | Fraction],
    previous: str,
) -> tuple[str, ...]:
    carrier, base, switch = validate_switching(forms, base_costs, switching)
    if previous not in carrier:
        raise ValueError("previous form must belong to the carrier")
    totals = {form: base[form] + switch[(previous, form)] for form in carrier}
    optimum = min(totals.values())
    return tuple(form for form in carrier if totals[form] == optimum)


def symmetric_switching(kappa: int | Fraction) -> dict[tuple[str, str], Fraction]:
    burden = exact(kappa)
    if burden < 0:
        raise ValueError("switching burden must be nonnegative")
    return {
        ("A", "A"): Fraction(0),
        ("A", "B"): burden,
        ("B", "A"): burden,
        ("B", "B"): Fraction(0),
    }


def two_form_hysteresis(delta: int | Fraction, kappa: int | Fraction) -> dict[str, object]:
    difference, burden = exact(delta), exact(kappa)
    switch = symmetric_switching(burden)
    offset = max(Fraction(0), -difference)
    base = {"A": offset, "B": offset + difference}
    selections = {
        previous: switching_selection(("A", "B"), base, switch, previous)
        for previous in ("A", "B")
    }
    if difference < -burden:
        region = "B_BOTH_HISTORIES"
    elif difference == -burden:
        region = "NEGATIVE_BOUNDARY_TIE"
    elif difference < burden:
        region = "HISTORY_DEPENDENT_BAND"
    elif difference == burden:
        region = "POSITIVE_BOUNDARY_TIE"
    else:
        region = "A_BOTH_HISTORIES"
    return {
        "delta": difference,
        "kappa": burden,
        "region": region,
        "selections": selections,
    }


def origin_additive_erasure(
    forms: Iterable[str],
    base_costs: Mapping[str, int | Fraction],
    origin_terms: Mapping[str, int | Fraction],
    destination_terms: Mapping[str, int | Fraction],
) -> dict[str, object]:
    carrier = validate_states(forms)
    if set(origin_terms) != set(carrier) or set(destination_terms) != set(carrier):
        raise ValueError("origin/destination terms must cover the form carrier")
    switching = {
        (previous, current): exact(origin_terms[previous]) + exact(destination_terms[current])
        for previous in carrier
        for current in carrier
    }
    selections = {
        previous: switching_selection(carrier, base_costs, switching, previous)
        for previous in carrier
    }
    return {
        "switching": switching,
        "selections": selections,
        "history_erased": len(set(selections.values())) == 1,
    }


def reset_erasure(
    forms: Iterable[str],
    base_costs: Mapping[str, int | Fraction],
    switching: Mapping[tuple[str, str], int | Fraction],
    reset_to: str,
) -> dict[str, tuple[str, ...]]:
    carrier, _, _ = validate_switching(forms, base_costs, switching)
    if reset_to not in carrier:
        raise ValueError("reset state must belong to the form carrier")
    selection = switching_selection(carrier, base_costs, switching, reset_to)
    return {previous: selection for previous in carrier}


def deterministic_escape(
    states: Iterable[str],
    initial: str,
    targets: Iterable[str],
    edges: Sequence[tuple[str, str, Sequence[int | Fraction]]],
    budget: Sequence[int | Fraction],
) -> dict[str, object]:
    """Find a budget-feasible simple target path, if and only if one exists."""
    carrier = validate_states(states, initial)
    target_set = set(targets)
    if not target_set or not target_set.issubset(carrier):
        raise ValueError("target set must be nonempty and contained in the carrier")
    bound = exact_vector(budget)
    normalized = normalize_edges(carrier, edges, len(bound))
    outgoing = {state: [] for state in carrier}
    for source, target, cost in normalized:
        outgoing[source].append((target, cost))
    for state in carrier:
        outgoing[state].sort(key=lambda item: (item[0], item[1]))
    zero = tuple(Fraction(0) for _ in bound)
    witnesses: list[tuple[tuple[str, ...], tuple[Fraction, ...]]] = []

    def visit(
        state: str,
        path: tuple[str, ...],
        cost: tuple[Fraction, ...],
    ) -> None:
        if state in target_set:
            witnesses.append((path, cost))
            return
        for successor, edge_cost in outgoing[state]:
            if successor in path:
                continue
            candidate = add_vectors(cost, edge_cost)
            if vector_leq(candidate, bound):
                visit(successor, path + (successor,), candidate)

    visit(initial, (initial,), zero)
    witness = min(witnesses, key=lambda item: (len(item[0]), item[0], item[1])) if witnesses else None
    return {
        "escape_exists": witness is not None,
        "is_local_trap": witness is None,
        "witness_path": None if witness is None else witness[0],
        "witness_cost": None if witness is None else witness[1],
    }


def validate_markov(
    states: Iterable[str],
    kernel: Mapping[str, Mapping[str, int | Fraction]],
    initial: Mapping[str, int | Fraction],
) -> tuple[tuple[str, ...], dict[str, dict[str, Fraction]], dict[str, Fraction]]:
    carrier = validate_states(states)
    carrier_set = set(carrier)
    if set(kernel) != carrier_set or set(initial) != carrier_set:
        raise ValueError("kernel and initial distribution must exactly cover the carrier")
    normalized_kernel: dict[str, dict[str, Fraction]] = {}
    for source in carrier:
        row = kernel[source]
        if set(row) != carrier_set:
            raise ValueError("every transition row must exactly cover the carrier")
        normalized = {target: exact(row[target]) for target in carrier}
        if any(value < 0 for value in normalized.values()) or sum(
            normalized.values(), Fraction(0)
        ) != 1:
            raise ValueError("each transition row must be an exact probability distribution")
        normalized_kernel[source] = normalized
    distribution = {state: exact(initial[state]) for state in carrier}
    if any(value < 0 for value in distribution.values()) or sum(
        distribution.values(), Fraction(0)
    ) != 1:
        raise ValueError("initial law must be an exact probability distribution")
    return carrier, normalized_kernel, distribution


def _validate_horizon_targets(
    carrier: Sequence[str], targets: Iterable[str], horizon: int
) -> set[str]:
    if isinstance(horizon, bool) or type(horizon) is not int or horizon < 0:
        raise ValueError("finite horizon must be a nonnegative integer")
    target_set = set(targets)
    if not target_set or not target_set.issubset(carrier):
        raise ValueError("predicted target set must be nonempty and inside the carrier")
    return target_set


def markov_reachability(
    states: Iterable[str],
    kernel: Mapping[str, Mapping[str, int | Fraction]],
    initial: Mapping[str, int | Fraction],
    targets: Iterable[str],
    horizon: int,
) -> dict[str, object]:
    """Exact endpoint and cumulative first-hit masses by finite-horizon DP."""
    carrier, transition, distribution = validate_markov(states, kernel, initial)
    target_set = _validate_horizon_targets(carrier, targets, horizon)
    distributions = [distribution]
    endpoint_mass = [sum((distribution[state] for state in target_set), Fraction(0))]
    alive = {
        state: (Fraction(0) if state in target_set else distribution[state])
        for state in carrier
    }
    cumulative = [endpoint_mass[0]]
    new_hits = [endpoint_mass[0]]
    alive_mass = [sum(alive.values(), Fraction(0))]
    for _ in range(horizon):
        next_distribution = {state: Fraction(0) for state in carrier}
        for source in carrier:
            for target in carrier:
                next_distribution[target] += distribution[source] * transition[source][target]
        distribution = next_distribution
        distributions.append(distribution)
        endpoint_mass.append(sum((distribution[state] for state in target_set), Fraction(0)))

        propagated_alive = {state: Fraction(0) for state in carrier}
        for source in carrier:
            for target in carrier:
                propagated_alive[target] += alive[source] * transition[source][target]
        newly_hit = sum((propagated_alive[state] for state in target_set), Fraction(0))
        alive = {
            state: (Fraction(0) if state in target_set else propagated_alive[state])
            for state in carrier
        }
        new_hits.append(newly_hit)
        cumulative.append(cumulative[-1] + newly_hit)
        alive_mass.append(sum(alive.values(), Fraction(0)))

    normalized = all(
        sum(row.values(), Fraction(0)) == 1 for row in distributions
    )
    first_hit_accounting = all(
        cumulative[index] + alive_mass[index] == 1
        for index in range(horizon + 1)
    )
    monotone = all(
        cumulative[index] <= cumulative[index + 1] for index in range(horizon)
    )
    return {
        "distributions": tuple(distributions),
        "endpoint_mass": tuple(endpoint_mass),
        "new_first_hit_mass": tuple(new_hits),
        "cumulative_first_hit_mass": tuple(cumulative),
        "alive_mass": tuple(alive_mass),
        "normalization_holds": normalized,
        "first_hit_accounting_holds": first_hit_accounting,
        "cumulative_monotonicity_holds": monotone,
    }


def path_enumeration_oracle(
    states: Iterable[str],
    kernel: Mapping[str, Mapping[str, int | Fraction]],
    initial: Mapping[str, int | Fraction],
    targets: Iterable[str],
    horizon: int,
) -> dict[str, object]:
    """Independent explicit positive-path enumeration oracle."""
    carrier, transition, distribution = validate_markov(states, kernel, initial)
    target_set = _validate_horizon_targets(carrier, targets, horizon)
    endpoint_mass = [Fraction(0) for _ in range(horizon + 1)]
    cumulative = [Fraction(0) for _ in range(horizon + 1)]
    path_prefixes = [0 for _ in range(horizon + 1)]
    positive_target_path_exists = False

    def walk(state: str, time: int, probability: Fraction, first_hit: int | None) -> None:
        nonlocal positive_target_path_exists
        path_prefixes[time] += 1
        if state in target_set:
            endpoint_mass[time] += probability
            if first_hit is None:
                first_hit = time
        if first_hit is not None:
            cumulative[time] += probability
            positive_target_path_exists = True
        if time == horizon:
            return
        for successor in carrier:
            edge_probability = transition[state][successor]
            if edge_probability > 0:
                walk(successor, time + 1, probability * edge_probability, first_hit)

    for state in carrier:
        if distribution[state] > 0:
            walk(state, 0, distribution[state], None)
    return {
        "endpoint_mass": tuple(endpoint_mass),
        "cumulative_first_hit_mass": tuple(cumulative),
        "positive_target_path_exists": positive_target_path_exists,
        "positive_path_prefixes": tuple(path_prefixes),
    }


def stochastic_escape(
    states: Iterable[str],
    kernel: Mapping[str, Mapping[str, int | Fraction]],
    initial: Mapping[str, int | Fraction],
    targets: Iterable[str],
    horizon: int,
) -> dict[str, object]:
    dynamic = markov_reachability(states, kernel, initial, targets, horizon)
    enumerated = path_enumeration_oracle(states, kernel, initial, targets, horizon)
    masses_agree = (
        dynamic["endpoint_mass"] == enumerated["endpoint_mass"]
        and dynamic["cumulative_first_hit_mass"]
        == enumerated["cumulative_first_hit_mass"]
    )
    positive_mass = dynamic["cumulative_first_hit_mass"][-1] > 0
    return {
        "positive_escape_mass": positive_mass,
        "positive_probability_path_exists": enumerated["positive_target_path_exists"],
        "iff_holds": positive_mass == enumerated["positive_target_path_exists"],
        "dp_enumeration_agree": masses_agree,
        "dynamic": dynamic,
        "enumeration": enumerated,
    }


def _simple_path_cost_oracle(
    states: Sequence[str],
    initial: str,
    edges: Sequence[tuple[str, str, Sequence[int | Fraction]]],
    dimension: int,
) -> dict[str, tuple[tuple[Fraction, ...], ...]]:
    normalized = normalize_edges(states, edges, dimension)
    outgoing = {state: [] for state in states}
    for source, target, cost in normalized:
        outgoing[source].append((target, cost))
    costs: dict[str, set[tuple[Fraction, ...]]] = {state: set() for state in states}
    zero = tuple(Fraction(0) for _ in range(dimension))

    def walk(state: str, path: tuple[str, ...], cost: tuple[Fraction, ...]) -> None:
        costs[state].add(cost)
        for successor, edge_cost in outgoing[state]:
            if successor not in path:
                walk(successor, path + (successor,), add_vectors(cost, edge_cost))

    walk(initial, (initial,), zero)
    return {state: tuple(sorted(values)) for state, values in costs.items() if values}


def exhaustive_census() -> dict[str, int]:
    states = ("s0", "s1", "s2")
    cost_alphabet = ((0, 1), (1, 0), (1, 1), (2, 0))
    rays = ((1, 1), (1, 2), (0, 1))
    phase_worlds = 0
    phase_events = 0
    for edge_costs in product(cost_alphabet, repeat=3):
        edges = (
            ("s0", "s1", edge_costs[0]),
            ("s1", "s2", edge_costs[1]),
            ("s0", "s2", edge_costs[2]),
        )
        oracle_costs = _simple_path_cost_oracle(states, "s0", edges, 2)
        for ray in rays:
            expected_thresholds = {}
            for state in states:
                candidates = [
                    threshold
                    for cost in oracle_costs.get(state, ())
                    if (threshold := ray_cost_threshold(cost, ray)) is not None
                ]
                expected_thresholds[state] = min(candidates) if candidates else None
            for score_values in product(range(3), repeat=3):
                result = phase_schedule(
                    states,
                    "s0",
                    edges,
                    dict(zip(states, score_values)),
                    ray,
                )
                if result["thresholds"] != expected_thresholds:
                    raise AssertionError("phase threshold disagrees with simple-path oracle")
                for event in result["events"]:
                    reachable = event["reachable"]
                    best = max(score_values[states.index(state)] for state in reachable)
                    expected_argmax = tuple(
                        state
                        for state in reachable
                        if score_values[states.index(state)] == best
                    )
                    if event["argmax"] != expected_argmax:
                        raise AssertionError("phase argmax lost a tie or selected a nonmaximum")
                    phase_events += 1
                phase_worlds += 1

    hysteresis_cases = 0
    for kappa in range(3):
        for delta in range(-3, 4):
            result = two_form_hysteresis(delta, kappa)
            selections = result["selections"]
            if delta < -kappa and set(selections.values()) != {("B",)}:
                raise AssertionError("negative exterior hysteresis law failed")
            if -kappa < delta < kappa and kappa > 0 and selections != {"A": ("A",), "B": ("B",)}:
                raise AssertionError("interior hysteresis law failed")
            if delta > kappa and set(selections.values()) != {("A",)}:
                raise AssertionError("positive exterior hysteresis law failed")
            hysteresis_cases += 1

    directed_edges = tuple(
        (source, target, (1,))
        for source in states
        for target in states
        if source != target
    )
    deterministic_cases = 0
    for mask in range(1 << len(directed_edges)):
        graph = tuple(edge for index, edge in enumerate(directed_edges) if mask & (1 << index))
        adjacency = {state: set() for state in states}
        for source, target, _ in graph:
            adjacency[source].add(target)
        for budget in range(4):
            reachable_by_steps = {"s0"}
            frontier = {"s0"}
            for _ in range(budget):
                frontier = {target for source in frontier for target in adjacency[source]}
                reachable_by_steps |= frontier
            for target_mask in range(1, 1 << len(states)):
                targets = {
                    state for index, state in enumerate(states) if target_mask & (1 << index)
                }
                result = deterministic_escape(states, "s0", targets, graph, (budget,))
                if result["escape_exists"] != bool(reachable_by_steps & targets):
                    raise AssertionError("deterministic feasible-path iff failed")
                deterministic_cases += 1

    row_options = tuple(
        tuple(Fraction(count, 2) for count in counts)
        for counts in product(range(3), repeat=3)
        if sum(counts) == 2
    )
    stochastic_cases = 0
    for rows in product(row_options, repeat=3):
        kernel = {
            source: dict(zip(states, row))
            for source, row in zip(states, rows)
        }
        for initial_state in states:
            initial = {state: Fraction(state == initial_state) for state in states}
            for target_mask in range(1, 1 << len(states)):
                targets = {
                    state for index, state in enumerate(states) if target_mask & (1 << index)
                }
                for horizon in range(4):
                    result = stochastic_escape(states, kernel, initial, targets, horizon)
                    dynamic = result["dynamic"]
                    if not (
                        result["iff_holds"]
                        and result["dp_enumeration_agree"]
                        and dynamic["normalization_holds"]
                        and dynamic["first_hit_accounting_holds"]
                        and dynamic["cumulative_monotonicity_holds"]
                    ):
                        raise AssertionError("finite stochastic reachability law failed")
                    stochastic_cases += 1
    return {
        "phase_worlds": phase_worlds,
        "phase_threshold_events": phase_events,
        "hysteresis_cases": hysteresis_cases,
        "deterministic_escape_cases": deterministic_cases,
        "stochastic_dp_enumeration_cases": stochastic_cases,
    }


def validate_ledgers() -> dict[str, object]:
    ledger = json.loads((HERE / "SCIENTIFIC_LEDGER_V1.json").read_text())
    required = {
        "id",
        "assumptions",
        "dependencies",
        "falsifiers",
        "strongest_parent",
        "counterexample_methods",
        "limits",
    }
    claims = ledger.get("claims", [])
    if len(claims) != 5 or any(set(row) != required for row in claims):
        raise ValueError("scientific ledger schema or claim count drifted")
    if any(
        not row["assumptions"] or not row["falsifiers"] or not row["limits"]
        for row in claims
    ):
        raise ValueError("scientific ledger contains an empty closure field")
    gaps = ledger.get("open_gaps", [])
    if len(gaps) != 1 or gaps[0].get("status") != "OPEN":
        raise ValueError("independent hostile review must remain explicitly open")
    return {
        "claim_ledgers": len(claims),
        "open_review_gaps": len(gaps),
        "closure_level": "LOCALLY_CLOSED",
    }


def validate_package_contracts() -> dict[str, object]:
    manifest = json.loads((HERE / "MANIFEST_V1.json").read_text())
    reconciliation = json.loads(
        (HERE / "ISSUE_833_RECONCILIATION_DEVELOPMENTAL_PHASE_TRAPS_V1.json").read_text()
    )
    expected_rows = {
        "- [ ] Derive developmental phase transitions.",
        "- [ ] Derive path dependence and hysteresis.",
        "- [ ] Derive conditions for escaping local developmental traps.",
        "- [ ] Prove/measure reachability mass for predicted morphologies.",
    }
    replacements = reconciliation.get("replacements", [])
    manifest_ok = (
        manifest.get("issue") == 910
        and manifest.get("source_pr") == 924
        and manifest.get("parent_issue") == 833
        and manifest.get("freeze_commit") == "68e581aea6a83383f53ca4c538f4cd325ff12d97"
        and manifest.get("frozen_main") == "9e508041766bdb46cbab35c07439c0d3d7ea5c59"
        and manifest.get("prerequisite_pr") == 909
        and manifest.get("claim_ceiling") == CLAIM_CEILING
        and manifest.get("target_rows") == 4
        and tuple(manifest.get("forbidden_promotions", ())) == FORBIDDEN_PROMOTIONS
    )
    reconciliation_ok = (
        reconciliation.get("schema") == "GMI_ISSUE_RECONCILIATION_V2"
        and reconciliation.get("issue") == 833
        and reconciliation.get("source_issue") == 910
        and reconciliation.get("source_pr") == 924
        and reconciliation.get("prerequisite_pr") == 909
        and reconciliation.get("claim_ceiling") == CLAIM_CEILING
        and tuple(reconciliation.get("forbidden_promotions", ()))
        == FORBIDDEN_PROMOTIONS
        and len(replacements) == 4
        and {row.get("old") for row in replacements} == expected_rows
        and all(
            row.get("anchor") == "# L. Development, morphogenesis, and evolvability"
            for row in replacements
        )
        and all(
            row.get("new", "").startswith("- [x]")
            and "PR #924 / #910" in row.get("new", "")
            for row in replacements
        )
    )
    return {
        "manifest_ok": manifest_ok,
        "reconciliation_ok": reconciliation_ok,
        "reconciliation_rows": len(replacements),
        "source_pr": reconciliation.get("source_pr"),
        "prerequisite_pr": reconciliation.get("prerequisite_pr"),
    }


def build_receipt(parent_audit: dict[str, object] | None = None) -> dict[str, object]:
    parent_audit = parent_audit or {"all_ok": True, "rows": []}
    phase = phase_schedule(
        ("root", "A", "B", "C", "D"),
        "root",
        (
            ("root", "A", (1, 0)),
            ("root", "B", (0, 2)),
            ("A", "C", (1, 1)),
            ("B", "C", (1, 0)),
            ("root", "D", (3, 0)),
        ),
        {"root": 0, "A": 2, "B": 2, "C": 5, "D": 5},
        (1, 1),
    )
    zero_ray_hostile = phase_schedule(
        ("root", "blocked"),
        "root",
        (("root", "blocked", (1, 0)),),
        {"root": 0, "blocked": 10},
        (0, 1),
    )
    hysteresis = two_form_hysteresis(0, 1)
    negative_boundary = two_form_hysteresis(-1, 1)
    positive_boundary = two_form_hysteresis(1, 1)
    erasure = origin_additive_erasure(
        ("A", "B", "C"),
        {"A": 0, "B": 1, "C": 2},
        {"A": 0, "B": 1, "C": 2},
        {"A": 2, "B": 0, "C": 1},
    )
    reset = reset_erasure(
        ("A", "B"), {"A": 0, "B": 0}, symmetric_switching(1), "A"
    )

    trap_states = ("start", "local", "target")
    closed_edges = (
        ("start", "local", (1,)),
        ("local", "start", (0,)),
    )
    open_edges = closed_edges + (("local", "target", (1,)),)
    closed_deterministic = deterministic_escape(
        trap_states, "start", {"target"}, closed_edges, (2,)
    )
    open_deterministic = deterministic_escape(
        trap_states, "start", {"target"}, open_edges, (2,)
    )
    closed_kernel = {
        "start": {"start": 0, "local": 1, "target": 0},
        "local": {"start": 1, "local": 0, "target": 0},
        "target": {"start": 0, "local": 0, "target": 1},
    }
    open_kernel = {
        "start": {"start": 0, "local": 1, "target": 0},
        "local": {
            "start": Fraction(2, 3),
            "local": 0,
            "target": Fraction(1, 3),
        },
        "target": {"start": 0, "local": 0, "target": 1},
    }
    initial = {"start": 1, "local": 0, "target": 0}
    closed_stochastic = stochastic_escape(
        trap_states, closed_kernel, initial, {"target"}, 2
    )
    open_stochastic = stochastic_escape(
        trap_states, open_kernel, initial, {"target"}, 2
    )

    mass_states = ("source", "target", "other")
    mass_kernel = {
        "source": {
            "source": 0,
            "target": Fraction(1, 2),
            "other": Fraction(1, 2),
        },
        "target": {"source": 0, "target": 0, "other": 1},
        "other": {"source": 0, "target": 0, "other": 1},
    }
    mass_initial = {"source": 1, "target": 0, "other": 0}
    mass = markov_reachability(
        mass_states, mass_kernel, mass_initial, {"target"}, 2
    )
    mass_oracle = path_enumeration_oracle(
        mass_states, mass_kernel, mass_initial, {"target"}, 2
    )
    census = exhaustive_census()
    ledgers = validate_ledgers()
    package_contracts = validate_package_contracts()
    expected_census = {
        "phase_worlds": 5184,
        "phase_threshold_events": 11097,
        "hysteresis_cases": 21,
        "deterministic_escape_cases": 1792,
        "stochastic_dp_enumeration_cases": 18144,
    }
    checks = {
        "parents_exactly_pinned_including_909": bool(parent_audit["all_ok"]),
        "phase_thresholds_exact": phase["thresholds"]
        == {"root": 0, "A": 1, "B": 2, "C": 2, "D": 3},
        "phase_complete_tied_argmax": phase["events"][-1]["argmax"] == ("C", "D"),
        "phase_changes_only_at_entry_thresholds": all(
            event["threshold"] in set(phase["thresholds"].values())
            for event in phase["events"]
        ),
        "zero_ray_coordinate_blocks_positive_cost": zero_ray_hostile["thresholds"]["blocked"] is None,
        "hysteresis_equal_ecology_path_dependence": hysteresis["selections"]
        == {"A": ("A",), "B": ("B",)},
        "hysteresis_boundary_ties_preserved": negative_boundary["selections"]
        == {"A": ("A", "B"), "B": ("B",)}
        and positive_boundary["selections"] == {"A": ("A",), "B": ("A", "B")},
        "history_erasure_controls_hold": erasure["history_erased"]
        and len(set(reset.values())) == 1,
        "closed_trap_and_added_edge_twin": closed_deterministic["is_local_trap"]
        and open_deterministic["witness_path"] == ("start", "local", "target"),
        "stochastic_positive_path_iff": closed_stochastic["iff_holds"]
        and not closed_stochastic["positive_escape_mass"]
        and open_stochastic["iff_holds"]
        and open_stochastic["positive_escape_mass"],
        "markov_dp_normalized_and_monotone": mass["normalization_holds"]
        and mass["first_hit_accounting_holds"]
        and mass["cumulative_monotonicity_holds"],
        "endpoint_distinct_from_cumulative_first_hit": mass["endpoint_mass"]
        == (0, Fraction(1, 2), 0)
        and mass["cumulative_first_hit_mass"]
        == (0, Fraction(1, 2), Fraction(1, 2)),
        "independent_path_enumeration_exact": mass["endpoint_mass"]
        == mass_oracle["endpoint_mass"]
        and mass["cumulative_first_hit_mass"]
        == mass_oracle["cumulative_first_hit_mass"],
        "bounded_censuses_complete": census == expected_census,
        "scientific_ledgers_complete": ledgers
        == {"claim_ledgers": 5, "open_review_gaps": 1, "closure_level": "LOCALLY_CLOSED"},
        "manifest_and_reconciliation_exact": package_contracts
        == {
            "manifest_ok": True,
            "reconciliation_ok": True,
            "reconciliation_rows": 4,
            "source_pr": 924,
            "prerequisite_pr": 909,
        },
    }
    return {
        "schema": "GMI833DevelopmentalPhaseTrapsResultV1",
        "issue": 910,
        "source_pr": 924,
        "parent_issue": 833,
        "prerequisite_pr": 909,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": FORBIDDEN_PROMOTIONS,
        "parent_audit": parent_audit,
        "census": census,
        "witness": {
            "phase": phase,
            "zero_ray_hostile": zero_ray_hostile,
            "hysteresis": hysteresis,
            "negative_boundary": negative_boundary,
            "positive_boundary": positive_boundary,
            "origin_additive_erasure": erasure,
            "reset_erasure": reset,
            "closed_deterministic_trap": closed_deterministic,
            "added_edge_deterministic_twin": open_deterministic,
            "closed_stochastic_trap": closed_stochastic,
            "added_edge_stochastic_twin": open_stochastic,
            "reachability_mass": mass,
            "path_enumeration_oracle": mass_oracle,
        },
        "scientific_ledger": ledgers,
        "package_contracts": package_contracts,
        "checks": checks,
        "verdict": "GREEN" if all(checks.values()) else "RED",
    }


def canonicalize(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [canonicalize(item) for item in value]
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): canonicalize(item)
            for key, item in sorted(value.items(), key=lambda pair: repr(pair[0]))
        }
    return value


def canonical_json(value) -> str:
    return json.dumps(canonicalize(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    print(canonical_json(build_receipt(audit_parents())), end="")
