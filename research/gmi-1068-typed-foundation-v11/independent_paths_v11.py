"""Independent typed-word reconstruction and elementwise function evaluation."""
from itertools import combinations, product


def natural(value):
    return type(value) is int and value >= 0


def graph_data(graph):
    if type(graph) not in (tuple, list) or len(graph) != 2:
        raise ValueError("graph shape")
    size, edges = graph
    if not natural(size) or type(edges) not in (tuple, list):
        raise ValueError("graph data")
    if any(type(edge) not in (tuple, list) or len(edge) != 2
           or any(not natural(v) or v >= size for v in edge) for edge in edges):
        raise ValueError("edge endpoint")
    return size, tuple(tuple(edge) for edge in edges)


def vertices(graph, path):
    size, edges = graph_data(graph)
    if type(path) not in (tuple, list) or len(path) != 2:
        raise ValueError("path shape")
    start, word = path
    if not natural(start) or start >= size or type(word) not in (tuple, list):
        raise ValueError("path data")
    route = [start]
    for edge in word:
        if not natural(edge) or edge >= len(edges) or edges[edge][0] != route[-1]:
            raise ValueError("ill-typed word")
        route.append(edges[edge][1])
    return tuple(route)


def concatenate(graph, first, second):
    route1, route2 = vertices(graph, first), vertices(graph, second)
    if route1[-1] != route2[0]:
        raise ValueError("incompatible boundaries")
    # Reconstruct from individual occurrences, without calling production append.
    occurrences = tuple(edge for path in (first, second) for edge in path[1])
    return route1[0], occurrences


def complete_dag_paths(graph):
    size, edges = graph_data(graph)
    reachable = [[False] * size for _ in range(size)]
    for source, target in edges:
        reachable[source][target] = True
    for middle in range(size):
        for source in range(size):
            for target in range(size):
                reachable[source][target] |= reachable[source][middle] and reachable[middle][target]
    if any(reachable[v][v] for v in range(size)):
        raise ValueError("cyclic graph")
    answer = {(start, ()) for start in range(size)}
    # Direct word enumeration rather than the production path traversal.
    for length in range(1, size):
        for word in product(range(len(edges)), repeat=length):
            if all(edges[a][1] == edges[b][0] for a, b in zip(word, word[1:])):
                answer.add((edges[word[0]][0], word))
    return answer


def concrete_evaluation(graph, path, domains, maps):
    size, edges = graph_data(graph)
    route = vertices(graph, path)
    if type(domains) not in (tuple, list) or len(domains) != size or not all(map(natural, domains)):
        raise ValueError("object interpretation")
    if type(maps) not in (tuple, list) or len(maps) != len(edges):
        raise ValueError("generator interpretation")
    for (source, target), mapping in zip(edges, maps):
        if type(mapping) not in (tuple, list) or len(mapping) != domains[source]:
            raise ValueError("map domain")
        if any(not natural(value) or value >= domains[target] for value in mapping):
            raise ValueError("map codomain")
    answer = []
    for value in range(domains[route[0]]):
        for edge in path[1]:
            value = maps[edge][value]
        answer.append(value)
    return tuple(answer)


def primary_graphs():
    pairs = tuple(combinations(range(4), 2))
    for multiplicities in product(range(3), repeat=len(pairs)):
        yield 4, tuple(pair for pair, count in zip(pairs, multiplicities) for _ in range(count))


def restrictions(edge_count):
    for flags in product((False, True), repeat=edge_count):
        yield {index for index, keep in enumerate(flags) if keep}


def monoids_two():
    """Classify supplied tables by checking all laws; never assume associativity."""
    for entries in product(range(2), repeat=4):
        table = entries[:2], entries[2:]
        associative = all(table[table[x][y]][z] == table[x][table[y][z]]
                          for x, y, z in product(range(2), repeat=3))
        units = tuple(e for e in range(2) if all(table[e][x] == x == table[x][e] for x in range(2)))
        yield table, associative, units
