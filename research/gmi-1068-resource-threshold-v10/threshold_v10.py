"""Exact distinguishing expenditure for finite visible-cost machines."""
from heapq import heappop, heappush
from itertools import combinations


def validate(machine):
    if not isinstance(machine, (list, tuple)) or len(machine) != 2:
        raise ValueError("machine must be (observations, rows)")
    observations, rows = machine
    if not isinstance(observations, (list, tuple)) or not observations:
        raise ValueError("nonempty observation sequence required")
    n = len(observations)
    natural = lambda v: type(v) is int and v >= 0
    if not all(natural(v) for v in observations):
        raise ValueError("observations must be natural integers")
    if not isinstance(rows, (list, tuple)) or len(rows) != n:
        raise ValueError("one row per state required")
    if not all(isinstance(row, (list, tuple)) for row in rows):
        raise ValueError("rows must be sequences")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("common action alphabet required")
    for row in rows:
        for edge in row:
            if edge is not None and (
                not isinstance(edge, (list, tuple)) or len(edge) != 3
                or not all(natural(v) for v in edge) or edge[2] >= n
            ):
                raise ValueError("edge must be (output, natural cost, target)")
    return n, width


def run(machine, state, word, budget=None, hide_cost=False):
    n, width = validate(machine)
    if type(state) is not int or not 0 <= state < n:
        raise ValueError("invalid initial state")
    if budget is not None and (type(budget) is not int or budget < 0):
        raise ValueError("invalid resource")
    if not isinstance(word, (list, tuple)) or any(
        type(a) is not int or not 0 <= a < width for a in word
    ):
        raise ValueError("invalid action word")
    observations, rows = machine
    response = [("obs", observations[state])]
    for action in word:
        edge = rows[state][action]
        if edge is None or (budget is not None and edge[1] > budget):
            response.append(("illegal",))
            break
        output, cost, state = edge
        response.append(("edge", output) if hide_cost else ("edge", output, cost))
        response.append(("obs", observations[state]))
        if budget is not None:
            budget -= cost
    return tuple(response)


def graph(machine):
    """Return sink alternatives and same-event successors per unordered pair."""
    n, _ = validate(machine)
    obs, rows = machine
    terminals, links = {}, {}
    for p in combinations(range(n), 2):
        s, t = p
        terminals[p], links[p] = [], []
        if obs[s] != obs[t]:
            terminals[p].append((0, ()))
        for a, (left, right) in enumerate(zip(rows[s], rows[t])):
            if left is None and right is None:
                continue
            if left is None or right is None:
                terminals[p].append(((left or right)[1], (a,)))
            elif (left[0], left[1]) != (right[0], right[1]):
                terminals[p].append((min(left[1], right[1]), (a,)))
            elif left[2] != right[2]:
                successor = tuple(sorted((left[2], right[2])))
                links[p].append((left[1], a, successor))
    return terminals, links


def solve(machine):
    n, _ = validate(machine)
    terminals, links = graph(machine)
    reverse = {p: [] for p in terminals}
    distance, choices, settled, heap = {}, {}, set(), []
    for p, edges in links.items():
        for cost, action, successor in edges:
            reverse[successor].append((p, cost, action))
    for p, alternatives in terminals.items():
        if alternatives:
            cost, word = min(alternatives)
            distance[p] = cost
            choices[p] = ("terminal", word)
            heappush(heap, (cost, p))
    while heap:
        cost, p = heappop(heap)
        if p in settled or distance[p] != cost:
            continue
        settled.add(p)
        for predecessor, edge_cost, action in reverse[p]:
            candidate = cost + edge_cost
            if predecessor not in settled and (
                predecessor not in distance or candidate < distance[predecessor]
            ):
                distance[predecessor] = candidate
                choices[predecessor] = ("step", action, p)
                heappush(heap, (candidate, predecessor))
    distances = [[None] * n for _ in range(n)]
    witnesses = [[None] * n for _ in range(n)]
    for p, cost in distance.items():
        word, current, seen = [], p, set()
        while True:
            if current in seen:
                raise RuntimeError("cyclic settled witness")
            seen.add(current)
            choice = choices[current]
            if choice[0] == "terminal":
                word.extend(choice[1])
                break
            word.append(choice[1])
            current = choice[2]
        s, t = p
        distances[s][t] = distances[t][s] = cost
        witnesses[s][t] = witnesses[t][s] = tuple(word)
    return {"distances": distances, "witnesses": witnesses}


def classes(result, budget):
    if type(budget) is not int or budget < 0:
        raise ValueError("invalid resource")
    representatives, labels = [], []
    for state, row in enumerate(result["distances"]):
        for label, representative in enumerate(representatives):
            d = row[representative]
            if d is None or budget < d:
                labels.append(label)
                break
        else:
            labels.append(len(representatives))
            representatives.append(state)
    return labels


def verify(machine, result):
    from certificate_v10 import verify as check
    return check(machine, result)
