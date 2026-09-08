"""Exact finite lifecycle-table checks; not runtime admission or model adequacy.

All inputs are ordinary built-in containers and must not be concurrently mutated.
Observations use exact JSON values (no floats); costs/probabilities use int/Fraction.
Every public check validates and detaches its input before comparing contracts.
A receipt is a reproducibility record, NOT external authority or a signature.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

OBSERVATIONS = frozenset({
    "answer", "status", "warrant", "scope", "authority", "polarity",
    "support", "dependencies", "receipt", "failure",
})
MANIFEST = frozenset({"source", "constitution", "operators", "projection", "ecology"})
STOP = "$STOP"


def _keys(value, expected):
    if (type(value) is not dict or any(type(k) is not str for k in value)
            or set(value) != set(expected)):
        raise ValueError("missing, extra, or non-dict contract fields")


def _name(value):
    if type(value) is not str or not value:
        raise ValueError("IDs must be nonempty built-in strings")
    return value


def _sequence(value):
    if type(value) not in (list, tuple):
        raise TypeError("expected a built-in list or tuple")
    return tuple(value)


def _ids(values, allow_empty=False):
    values = tuple(_name(v) for v in _sequence(values))
    if len(set(values)) != len(values) or (not values and not allow_empty):
        raise ValueError("IDs must be distinct and nonempty")
    return values


def _number(value):
    if type(value) not in (int, Fraction):
        raise TypeError("use built-in int or Fraction, never bool/float")
    value = Fraction(value)
    if value < 0:
        raise ValueError("negative cost or probability")
    return value


def _json_value(value):
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is list:
        return [_json_value(v) for v in value]
    if type(value) is dict and all(type(k) is str for k in value):
        return {k: _json_value(v) for k, v in value.items()}
    raise TypeError("observations must contain only exact built-in JSON values")


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _contract(observation, cost, dimensions):
    _keys(observation, OBSERVATIONS)
    cost = tuple(_number(v) for v in _sequence(cost))
    if len(cost) != dimensions:
        raise ValueError("resource dimension mismatch")
    return _json(_json_value(observation)), cost


def _snapshot(model):
    _keys(model, {"manifest", "resources", "states"})
    _keys(model["manifest"], MANIFEST)
    manifest = tuple((k, _name(model["manifest"][k])) for k in sorted(MANIFEST))
    source = dict(manifest)["source"]
    if len(source) != 40 or any(c not in "0123456789abcdef" for c in source):
        raise ValueError("source must be a lowercase Git commit identity")
    resources = _ids(model["resources"])
    raw = model["states"]
    if type(raw) is not dict or not raw:
        raise ValueError("nonempty finite state table required")
    states = tuple(sorted(_name(s) for s in raw))
    nodes = []
    for state in states:
        entry = raw[state]
        _keys(entry, {"stop", "actions"})
        _keys(entry["stop"], {"observation", "cost"})
        stop = _contract(entry["stop"]["observation"], entry["stop"]["cost"], len(resources))
        actions = []
        for action in _sequence(entry["actions"]):
            _keys(action, {"id", "observation", "cost", "outcomes"})
            name = _name(action["id"])
            if name == STOP:
                raise ValueError("reserved STOP action identity")
            contract = _contract(action["observation"], action["cost"], len(resources))
            mass = defaultdict(Fraction)
            total = Fraction()
            for row in _sequence(action["outcomes"]):
                row = _sequence(row)
                if len(row) != 2:
                    raise ValueError("outcome must be (probability, successor)")
                probability, successor = _number(row[0]), _name(row[1])
                if successor not in raw:
                    raise ValueError("successor outside state table, including zero-mass entries")
                total += probability
                mass[successor] += probability
            if total != 1:
                raise ValueError("kernel must sum exactly to one")
            outcomes = tuple((p, s) for s, p in sorted(mass.items()) if p)
            actions.append((name, contract, outcomes))
        if len({a[0] for a in actions}) != len(actions):
            raise ValueError("duplicate action identity")
        nodes.append((state, stop, tuple(actions)))
    return manifest, resources, tuple(nodes)


def _partition(nodes, partition):
    if (type(partition) is not dict or any(type(k) is not str for k in partition)
            or set(partition) != {n[0] for n in nodes}):
        raise ValueError("partition must cover exactly the state table")
    return {state: _name(partition[state]) for state, _, _ in nodes}


def _mass(outcomes, partition):
    result = defaultdict(Fraction)
    for probability, successor in outcomes:
        result[partition[successor]] += probability
    return tuple(sorted(result.items()))


def _signature(node, partition):
    _, stop, actions = node
    return stop, tuple((name, contract, _mass(outcomes, partition))
                       for name, contract, outcomes in actions)


def _witness(nodes, partition):
    representatives = {}
    for node in nodes:
        state, stop, actions = node
        block = partition[state]
        if block not in representatives:
            representatives[block] = node
            continue
        other, other_stop, other_actions = representatives[block]
        reason, action = None, None
        if stop != other_stop:
            reason, action = "STOP_CONTRACT", STOP
        elif tuple(a[0] for a in actions) != tuple(a[0] for a in other_actions):
            reason = "ORDERED_ACTIONS"
        else:
            for current, reference in zip(actions, other_actions):
                if current[1] != reference[1]:
                    reason, action = "ACTION_CONTRACT", current[0]
                    break
                if _mass(current[2], partition) != _mass(reference[2], partition):
                    reason, action = "SUCCESSOR_BLOCK_MASS", current[0]
                    break
        if reason:
            return {"left": other, "right": state, "reason": reason, "action": action}
    return None


def _wire(value):
    if type(value) is Fraction:
        return {"rational": [value.numerator, value.denominator]}
    if type(value) is tuple:
        return [_wire(v) for v in value]
    return value


def check_partition(model, partition):
    """Necessary and sufficient for the declared *ordered contract* bisimulation.

    This is stronger than mere value equivalence. It does not establish that a
    supplied table contains every behavior or cost of the real OCM runtime.
    """
    snapshot = _snapshot(model)
    partition = _partition(snapshot[2], partition)
    witness = _witness(snapshot[2], partition)
    return {
        "schema": "OCM_FINITE_LIFECYCLE_V1",
        "scope": "EXPOSED_FINITE_TABLE_ONLY",
        "status": "REJECTED" if witness else "TABLE_CONTRACT_VALID",
        "model_sha256": sha256(_json(_wire(snapshot)).encode()).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "partition": partition,
        "witness": witness,
    }


def verify_receipt(model, partition, receipt):
    """Recompute, rather than trust a claimed terminal or a copied hash."""
    expected = check_partition(model, partition)
    return _json(_json_value(receipt)) == _json(expected)


def coarsest_partition(model):
    """Exact finite refinement; no sparse-runtime or speedup claim.

    Returns the coarsest ordered-contract bisimulation, not a minimum cognitive
    machine. The fixed finite table and declared observables define minimality.
    """
    _, _, nodes = _snapshot(model)
    partition = {s: "0" for s, _, _ in nodes}
    while True:
        groups, refined = {}, {}
        for node in nodes:
            signature = _signature(node, partition)
            if signature not in groups:
                groups[signature] = str(len(groups))
            refined[node[0]] = groups[signature]
        if refined == partition:
            return refined
        partition = refined


def common_actions_checked(version, good_actions):
    """Nonempty version-space decision sufficiency, not realizability proof."""
    version = _ids(version)
    if type(good_actions) is not dict:
        raise TypeError("good_actions must be an explicit state table")
    if any(state not in good_actions for state in version):
        raise ValueError("hypothesis outside declared state table")
    choices = [set(_ids(good_actions[state], True)) for state in version]
    return frozenset.intersection(*(frozenset(c) for c in choices))


def meta_problem(model, weights):
    """Translate to the existing finite_meta_dp; do not duplicate its solver.

    Coordinates must be additive costs. Peak memory is NOT an additive cost.
    Weights are declared nonnegative rational prices, not learned/tuned here.
    """
    _, resources, nodes = _snapshot(model)
    weights = tuple(_number(w) for w in _sequence(weights))
    if len(weights) != len(resources):
        raise ValueError("weight dimension mismatch")
    def scalar(contract):
        return sum((x * w for x, w in zip(contract[1], weights)), Fraction())
    return {
        "states": tuple(s for s, _, _ in nodes),
        "stop_cost": {s: scalar(stop) for s, stop, _ in nodes},
        "cognitive_actions": {s: tuple(a[0] for a in actions) for s, _, actions in nodes},
        "action_cost": {(s, a): scalar(c) for s, _, actions in nodes for a, c, _ in actions},
        "transitions": {(s, a): kernel for s, _, actions in nodes for a, _, kernel in actions},
    }
