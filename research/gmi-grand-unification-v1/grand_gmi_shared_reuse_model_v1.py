"""Weighted certificate DAG configurations with explicit workspace and invalidation."""
from dataclasses import dataclass
from fractions import Fraction as F
from heapq import heappop, heappush


@dataclass(frozen=True)
class Register:
    parents: tuple
    sizes: tuple
    build: tuple
    service: tuple
    scratch: tuple
    release: tuple
    holding: F = F(0)
    admitted: int = -1
    observe: F = F(0)


def nonnegative(value):
    return type(value) in (int, F) and value >= 0


def validate(model, memory):
    n = len(model.parents)
    if not n or type(memory) is not int or memory < 0:
        raise ValueError("nonempty DAG and finite nonnegative integer memory required")
    if any(len(row) != n for row in (model.sizes, model.build, model.service, model.scratch, model.release)):
        raise ValueError("one resource entry per node required")
    if any(type(v) is not int or v <= 0 for v in model.sizes):
        raise ValueError("positive integer artifact sizes required")
    if any(type(v) is not int or v < 0 for v in model.scratch):
        raise ValueError("nonnegative integer workspace sizes required")
    if any(type(pred) is not int or not 0 <= pred < 1 << v for v, pred in enumerate(model.parents)):
        raise ValueError("topologically indexed DAG required")
    if any(not nonnegative(v) for v in model.build+model.service+model.release+(model.holding, model.observe)):
        raise ValueError("finite nonnegative exact rational costs required")
    if type(model.admitted) is not int or not -1 <= model.admitted < 1 << n:
        raise ValueError("invalid builder-admission mask")
    return n


def members(mask, n):
    return tuple(v for v in range(n) if mask >> v & 1)


def mass(model, mask):
    return sum(model.sizes[v] for v in members(mask, len(model.parents)))


def invalidated(model, seeds):
    affected = seeds
    for v, parents in enumerate(model.parents):
        if parents & affected:
            affected |= 1 << v
    return affected


def graph(model, memory):
    n = validate(model, memory)
    states = tuple(mask for mask in range(1 << n) if mass(model, mask) <= memory)
    edges = {}
    for mask in states:
        row = []
        for v in range(n):
            bit = 1 << v
            if mask & bit:
                row.append((mask ^ bit, F(model.release[v]), ("drop", v)))
            elif model.admitted & bit and model.parents[v] & mask == model.parents[v]:
                if mass(model, mask)+model.sizes[v]+model.scratch[v] <= memory:
                    row.append((mask | bit, F(model.build[v]), ("build", v)))
        edges[mask] = tuple(row)
    return states, edges


def distances(states, edges):
    result, paths, settled, inspected = {}, {}, 0, 0
    for start in states:
        dist, routes, queue = {start: F(0)}, {start: ()}, [(F(0), start)]
        while queue:
            cost, state = heappop(queue)
            if cost != dist[state]:
                continue
            settled += 1
            for target, charge, action in edges[state]:
                inspected += 1
                proposed = cost+charge
                if target not in dist or proposed < dist[target]:
                    dist[target] = proposed
                    routes[target] = routes[state]+(action,)
                    heappush(queue, (proposed, target))
        result[start], paths[start] = dist, routes
    return result, paths, {"settled_configurations": settled, "inspected_edges": inspected}


def validate_task(model, memory, requests, events, initial):
    n = validate(model, memory)
    if type(initial) is not int or not 0 <= initial < 1 << n or mass(model, initial) > memory:
        raise ValueError("invalid initial certified resident set")
    if any(type(v) is not int or not 0 <= v < n for v in requests):
        raise ValueError("invalid requested node")
    if len(events) != max(0, len(requests)-1):
        raise ValueError("one observed event distribution per interval required")
    for outcomes in events:
        for seeds, prob in outcomes:
            if type(seeds) is not int or not 0 <= seeds < 1 << n or not nonnegative(prob):
                raise ValueError("invalid observed invalidation distribution")
        if not outcomes or sum(F(prob) for _, prob in outcomes) != 1:
            raise ValueError("event probabilities must sum exactly to one")
    return n


def solve(model, memory, requests, events, initial=0, objective="expected", release_all=False):
    validate_task(model, memory, requests, events, initial)
    if objective not in ("expected", "worstcase") or type(release_all) is not bool:
        raise ValueError("registered objective and release mode required")
    states, edges = graph(model, memory)
    dist, routes, development = distances(states, edges)
    future = {state: F(0) for state in states}
    policy, terminal_choices, path_choices = {}, 0, 0
    for t in reversed(range(len(requests))):
        terminal, keep_at = {}, {}
        final = t == len(requests)-1
        for ready in states:
            if not ready >> requests[t] & 1:
                continue
            best, kept = None, None
            for keep in ((0,) if release_all else states):
                terminal_choices += 1
                if keep not in dist[ready]:
                    continue
                value = F(model.service[requests[t]])+dist[ready][keep]
                if not final:
                    children = []
                    for seeds, prob in events[t]:
                        if prob > 0:
                            removed = keep & invalidated(model, seeds)
                            tail = future[keep & ~removed]
                            cleanup = sum((F(model.release[v]) for v in members(removed, len(model.parents))), F(0))
                            children.append((F(prob), None if tail is None else cleanup+tail))
                    if any(v is None for _, v in children):
                        continue
                    value += F(model.holding)*mass(model, keep)+F(model.observe)
                    value += (sum((prob*v for prob, v in children), F(0))
                              if objective == "expected" else max(v for _, v in children))
                if best is None or value < best:
                    best, kept = value, keep
            if best is not None:
                terminal[ready], keep_at[ready] = best, kept
        current = {}
        for start in states:
            options = []
            for ready, tail in terminal.items():
                path_choices += 1
                if ready in dist[start]:
                    options.append((dist[start][ready]+tail, ready))
            if options:
                value, ready = min(options)
                current[start] = value
                keep = keep_at[ready]
                policy[t, start] = (routes[start][ready], ready, routes[ready][keep], keep)
            else:
                current[start] = None
        future = current
    development |= {"terminal_retention_choices": terminal_choices,
                    "configuration_path_comparisons": path_choices}
    return {"value": future[initial], "policy": policy, "states": states,
            "edges": edges, "development": development}
