"""Normalize the finite proper-tree DRD input before any branch is explored."""
from exact_numeric import _items, _rational


def prepare_model(hypotheses, safe_actions, action_cost, probes, outcomes, probe_cost):
    # Hypothesis IDs retain the original mutually sortable/hashable domain.
    states = tuple(sorted(_items(hypotheses, "hypotheses")))
    probes = _items(probes, "probes", True)
    safe = {state: _items(safe_actions[state], "safe actions", True) for state in states}
    if any(action is None for actions in safe.values() for action in actions):
        raise ValueError("None is reserved for the absence of a stopping action")
    costs = {(state, action): _rational(action_cost[state, action])
             for state in states for action in safe[state]}
    probe_costs = {probe: _rational(probe_cost[probe]) for probe in probes}
    if any(cost < 0 for cost in probe_costs.values()):
        raise ValueError("probe costs must be nonnegative")
    observed = {(probe, state): outcomes[probe, state] for probe in probes for state in states}
    for result in observed.values():
        hash(result)  # deterministic outcome IDs must be hashable partition keys
    return states, safe, costs, probes, observed, probe_costs
