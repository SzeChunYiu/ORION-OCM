"""Independent explicit action traces and complete finite history-policy trees."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import product


def resident_weight(model, resident):
    return sum(model.sizes[v] for v in resident)


def simple_traces(model, memory, start):
    """All within-phase simple resident-set traces, with no graph/shortest-path helper."""
    n, traces = len(model.parents), []
    def visit(resident, seen, trace):
        traces.append((trace, resident))
        for v in range(n):
            if v in resident:
                target, action = resident-{v}, ("drop", v)
            else:
                prerequisites = {i for i in range(n) if model.parents[v] & (1 << i)}
                if not model.admitted & (1 << v) or not prerequisites <= resident:
                    continue
                if resident_weight(model, resident)+model.sizes[v]+model.scratch[v] > memory:
                    continue
                target, action = resident | {v}, ("build", v)
            target = frozenset(target)
            if target not in seen:
                visit(target, seen | {target}, trace+(action,))
    initial = frozenset(start)
    visit(initial, {initial}, ())
    return tuple(traces)


def stage_plans(model, memory, request, start):
    plans = []
    for before, ready in simple_traces(model, memory, start):
        if request in ready:
            for after, keep in simple_traces(model, memory, ready):
                plans.append((before+(("serve", request),)+after, keep))
    return tuple(plans)


def event_image(model, resident, seeds):
    """Independent reachability on the dependency edges; includes missing ancestors."""
    affected = {i for i in range(len(model.parents)) if seeds & (1 << i)}
    while True:
        enlarged = affected | {v for v, parents in enumerate(model.parents)
                               if any(parents & (1 << i) for i in affected)}
        if enlarged == affected:
            return frozenset(resident-affected)
        affected = enlarged


def execute_stage(model, memory, request, start, actions):
    resident, work, peak, served = set(start), F(0), resident_weight(model, start), 0
    for action, v in actions:
        if action == "build":
            prerequisites = {i for i in range(len(model.parents)) if model.parents[v] & (1 << i)}
            if v in resident or not model.admitted & (1 << v) or not prerequisites <= resident:
                raise ValueError("uncertified or unavailable proof dependencies")
            footprint = resident_weight(model, resident)+model.sizes[v]+model.scratch[v]
            if footprint > memory:
                raise ValueError("transient proof workspace exceeds memory")
            peak = max(peak, footprint)
            work += F(model.build[v])
            resident.add(v)
        elif action == "drop":
            if v not in resident:
                raise ValueError("cannot drop a missing artifact")
            resident.remove(v)
            work += F(model.release[v])
        elif action == "serve":
            if v != request or v not in resident or served:
                raise ValueError("request served without a current certificate")
            served += 1
            work += F(model.service[v])
        else:
            raise ValueError("unknown stage operation")
    if served != 1:
        raise ValueError("stage did not satisfy its request")
    return frozenset(resident), work, peak


def event_paths(events):
    choices = [tuple(i for i, (_, probability) in enumerate(row) if probability > 0) for row in events]
    return tuple(product(*choices))


def policy_bill(model, memory, requests, events, policy, path, initial=0):
    resident = frozenset(v for v in range(len(model.parents)) if initial & (1 << v))
    work, peak, current = F(0), resident_weight(model, resident), policy
    for t, request in enumerate(requests):
        actions, children = current
        resident, stage_work, stage_peak = execute_stage(model, memory, request, resident, actions)
        work += stage_work
        peak = max(peak, stage_peak)
        if t < len(events):
            work += F(model.holding)*resident_weight(model, resident)+F(model.observe)
            outcome = path[t]
            after_event = event_image(model, resident, events[t][outcome][0])
            work += sum((F(model.release[v]) for v in resident-after_event), F(0))
            resident = after_event
            current = dict(children)[outcome]
    return work, peak


def policy_oracle(model, memory, requests, events, initial=0):
    """Enumerate complete policy trees, then execute every positive-probability history."""
    @lru_cache(None)
    def trees(t, resident):
        if t == len(requests):
            return ((),)
        result = []
        for actions, kept in stage_plans(model, memory, requests[t], resident):
            if t == len(requests)-1:
                result.append((actions, ()))
                continue
            outcomes = tuple(i for i, (_, p) in enumerate(events[t]) if p > 0)
            children = [trees(t+1, event_image(model, kept, events[t][i][0])) for i in outcomes]
            for selected in product(*children):
                result.append((actions, tuple(zip(outcomes, selected))))
        return tuple(result)
    start = frozenset(v for v in range(len(model.parents)) if initial & (1 << v))
    policies, paths = trees(0, start), event_paths(events)
    best_mean = best_worst = None
    for policy in policies:
        bills = [policy_bill(model, memory, requests, events, policy, path, initial)[0] for path in paths]
        mean = F(0)
        for path, bill in zip(paths, bills):
            probability = F(1)
            for t, outcome in enumerate(path):
                probability *= F(events[t][outcome][1])
            mean += probability*bill
        worst = max(bills)
        best_mean = mean if best_mean is None else min(best_mean, mean)
        best_worst = worst if best_worst is None else min(best_worst, worst)
    return {"expected": best_mean, "worstcase": best_worst,
            "policies": len(policies), "histories": len(paths)}


def execute_synthesized(model, memory, requests, events, result, initial=0):
    totals = []
    for path in event_paths(events):
        state, work, peak, probability = initial, F(0), sum(model.sizes[v] for v in range(len(model.parents)) if initial & (1 << v)), F(1)
        for t, request in enumerate(requests):
            route, ready, after, kept = result["policy"][t, state]
            actions = route+(("serve", request),)+after
            resident = frozenset(v for v in range(len(model.parents)) if state & (1 << v))
            resident, charge, used = execute_stage(model, memory, request, resident, actions)
            if sum(1 << v for v in resident) != kept:
                raise AssertionError("constructed policy retention mismatch")
            work += charge
            peak = max(peak, used)
            if t < len(events):
                seeds, chance = events[t][path[t]]
                work += F(model.holding)*resident_weight(model, resident)+F(model.observe)
                probability *= F(chance)
                after_event = event_image(model, resident, seeds)
                work += sum((F(model.release[v]) for v in resident-after_event), F(0))
                resident = after_event
            state = sum(1 << v for v in resident)
        totals.append((probability, work, peak))
    return {"expected": sum((p*w for p, w, _ in totals), F(0)),
            "worstcase": max(w for _, w, _ in totals), "peak": max(k for _, _, k in totals),
            "histories": len(totals)}
