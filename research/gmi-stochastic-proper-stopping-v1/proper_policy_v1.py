"""Complete finite stationary construction; the SPS proof supplies policy coverage."""
from itertools import product
from stopping_model_v1 import rational
from stopping_model_v1 import goal_ancestors, safe_actions, solve_linear, viable_domain


def evaluate(model, domain, policy):
    """Return exact (costs, expected action counts), or None if not proper."""
    choices = {s: (a,) for s, a in zip(domain, policy)}
    allowed = safe_actions(model, domain)
    if len(policy) != len(domain) or any(a not in allowed[s]
                                         for s, a in zip(domain, policy)):
        raise ValueError("policy must select a safe action at every domain state")
    if goal_ancestors(model, choices) != set(domain):
        return None
    matrix = [
        [int(i == j) - model.rows[s][policy[i]].probability[t]
         for j, t in enumerate(domain)] for i, s in enumerate(domain)
    ]
    costs = [model.rows[s][a].cost for s, a in zip(domain, policy)]
    return solve_linear(matrix, costs), solve_linear(matrix, [1]*len(domain))


def construct(model):
    domain = viable_domain(model)
    n = model.goal
    policy_out, cost_out, steps_out = [None]*n, [None]*n, [None]*n
    if not domain:
        return {"viable": (), "policy": tuple(policy_out),
                "cost": tuple(cost_out), "steps": tuple(steps_out),
                "proper_tables": 0, "stationary_tables": 0}
    allowed = safe_actions(model, domain)
    records, tables = [], 0
    for policy in product(*(allowed[s] for s in domain)):
        tables += 1
        result = evaluate(model, domain, policy)
        if result is not None:
            pairs = tuple(zip(*result))
            records.append((policy, pairs))
    if not records:
        raise RuntimeError("viability failed to produce a proper policy")
    minima = tuple(min(pairs[i] for _, pairs in records)
                   for i in range(len(domain)))
    common = next((p for p, pairs in records if pairs == minima), None)
    if common is None:
        raise RuntimeError("statewise minima have no common policy witness")
    for s, a, (cost, steps) in zip(domain, common, minima):
        policy_out[s], cost_out[s], steps_out[s] = a, cost, steps
    return {"viable": domain, "policy": tuple(policy_out),
            "cost": tuple(cost_out), "steps": tuple(steps_out),
            "proper_tables": len(records), "stationary_tables": tables}


def bellman_slacks(model, result):
    """Exact scalar inequalities; they alone do not certify progress."""
    domain = result["viable"]
    values = result["cost"] + (0,)
    return {
        (s, a): model.rows[s][a].cost
        + sum(p*values[y] for y, p in
              enumerate(model.rows[s][a].probability) if p)
        - values[s]
        for s, indices in safe_actions(model, domain).items() for a in indices
    }


def certify(model, result):
    """Validate complete J/L Bellman inequalities and selected expected drift."""
    domain, n = viable_domain(model), model.goal
    if tuple(result["viable"]) != domain:
        raise ValueError("certificate omits or invents viable states")
    for key in ("cost", "steps", "policy"):
        if len(result[key]) != n:
            raise ValueError("complete state tables required")
        if any(result[key][s] is not None for s in range(n) if s not in domain):
            raise ValueError("infeasible states must be explicit")
    values, lengths = {}, {}
    for s in domain:
        values[s], lengths[s] = rational(result["cost"][s]), rational(result["steps"][s])
        if values[s] < 0 or lengths[s] < 0:
            raise ValueError("finite nonnegative certificate required")
    values[n], lengths[n] = 0, 0
    for s, indices in safe_actions(model, domain).items():
        selected = result["policy"][s]
        if type(selected) is not int or selected not in indices:
            raise ValueError("unsafe or missing selected action")
        for i in indices:
            a = model.rows[s][i]
            slack = a.cost + sum(p*values[y] for y, p in enumerate(a.probability) if p)-values[s]
            if slack < 0 or (i == selected and slack != 0):
                raise ValueError("cost Bellman certificate failed")
            if slack == 0:
                gap = 1 + sum(p*lengths[y] for y, p in enumerate(a.probability) if p)-lengths[s]
                if gap < 0 or (i == selected and gap != 0):
                    raise ValueError("expected-step progress certificate failed")
    return True
