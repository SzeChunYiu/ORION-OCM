"""Local optimality inequalities plus actual witnesses; no solver replay."""
from threshold_v10 import graph, run, validate


def verify(machine, result):
    n, width = validate(machine)
    if not isinstance(result, dict) or set(result) != {"distances", "witnesses"}:
        raise ValueError("wrong certificate fields")
    d, words = result["distances"], result["witnesses"]
    for matrix in (d, words):
        if not isinstance(matrix, (list, tuple)) or len(matrix) != n:
            raise ValueError("wrong matrix height")
        if any(not isinstance(row, (list, tuple)) or len(row) != n for row in matrix):
            raise ValueError("wrong matrix width")
    for s in range(n):
        for t in range(n):
            cost, word = d[s][t], words[s][t]
            if cost is not None and (type(cost) is not int or cost < 0):
                raise ValueError("distance must be natural or infinity")
            if cost != d[t][s] or word != words[t][s]:
                raise ValueError("asymmetric certificate")
            if cost is None:
                if word is not None:
                    raise ValueError("infinite pair must have no witness")
                continue
            if s == t:
                raise ValueError("diagonal cannot distinguish")
            if not isinstance(word, (list, tuple)) or any(
                type(a) is not int or not 0 <= a < width for a in word
            ):
                raise ValueError("invalid witness")
            if run(machine, s, word, cost) == run(machine, t, word, cost):
                raise ValueError("witness does not distinguish")
            if cost > 0 and run(machine, s, word, cost - 1) != run(machine, t, word, cost - 1):
                raise ValueError("witness already distinguishes below declared cost")
    terminals, links = graph(machine)
    for (s, t), alternatives in terminals.items():
        value = d[s][t]
        for sink_cost, _ in alternatives:
            if value is None or value > sink_cost:
                raise ValueError("violated local sink upper bound")
        for edge_cost, _, (u, v) in links[(s, t)]:
            successor = d[u][v]
            if successor is not None and (value is None or value > edge_cost + successor):
                raise ValueError("violated successor upper bound")
    return True
