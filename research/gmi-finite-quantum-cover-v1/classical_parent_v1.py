"""Complete finite classical encoder search and graph-color parent, no quantum solver."""
from itertools import product
from quantum_witness_v1 import task_shape
from rational_matrix_v1 import identity, require


def classical_optimum(task):
    nx, ny, k, _ = task_shape(task)
    examined = 0
    for d in range(1, nx + 1):
        for code in product(range(d), repeat=nx):
            examined += 1
            decoder, valid = [], True
            for y in range(ny):
                outputs = []
                for symbol in range(d):
                    allowed = set(range(k))
                    for x in range(nx):
                        target = task["allowed"][x][y]
                        if code[x] == symbol and target is not None:
                            allowed &= target
                    if not allowed:
                        valid = False
                        break
                    outputs.append(min(allowed))
                if not valid:
                    break
                decoder.append(outputs)
            if valid:
                rays = tuple(identity(d)[symbol] for symbol in code)
                factors = []
                for y in range(ny):
                    factors.append(tuple(tuple(tuple(int(i == j and decoder[y][i] == a)
                        for j in range(d)) for i in range(d)) for a in range(k)))
                return {"dimension": d, "encoder": code, "decoder": decoder,
                        "rays": rays, "factors": factors, "encoders_examined": examined}
    raise ValueError("finite nonempty relation lost basis-encoding upper bound")


def graph_colorable(vertices, edges, colors):
    """Exhaustive backtracking; prune only an already conflicting assigned edge."""
    require(type(colors) is int and colors > 0, "positive color register")
    neighbors = {v: set() for v in range(vertices)}
    for i, j in edges:
        require(i != j and i in neighbors and j in neighbors, "simple graph edge")
        neighbors[i].add(j)
        neighbors[j].add(i)
    order = sorted(neighbors, key=lambda v: (-len(neighbors[v]), v))
    assigned, visits = {}, 0
    def search(index):
        nonlocal visits
        visits += 1
        if index == vertices:
            return True
        v = order[index]
        for color in range(colors):
            if all(assigned.get(w) != color for w in neighbors[v]):
                assigned[v] = color
                if search(index + 1):
                    return True
                del assigned[v]
        return False
    possible = search(0)
    return possible, dict(assigned) if possible else None, visits
