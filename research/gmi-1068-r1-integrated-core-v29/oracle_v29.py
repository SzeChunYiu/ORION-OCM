"""Independent literal paths, endpoint trees, and attained-function enumeration."""
from itertools import product

ENDPOINTS = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))
EDGES = ((0, 1), (1, 2), (0, 2))
LABELS = (0, 1, 3, 4, 5, 6)
OBJECTS = (2, 0, 1)
RESTRICTED = (0, 1, 3, 5)


def chain_data():
    rows = tuple(tuple(ENDPOINTS.index((s, v)) if t == u else None
                       for u, v in ENDPOINTS) for s, t in ENDPOINTS)
    return (3, tuple(s for s, _ in ENDPOINTS), tuple(t for _, t in ENDPOINTS),
            (0, 3, 5), rows)


def queries():
    a = lambda i: ("arrow", i)
    e = lambda i: ("empty", i)
    seq = lambda x, y: ("seq", x, y)
    result = [a(i) for i in range(7)] + [e(i) for i in range(3)]
    result += [seq(a(i), a(j)) for i in range(7) for j in range(7)]
    result += [seq(e(i), e(j)) for i in range(3) for j in range(3)]
    for arrow, (source, target) in zip(LABELS, ENDPOINTS):
        result += [seq(e(OBJECTS.index(source)), a(arrow)),
                   seq(a(arrow), e(OBJECTS.index(target)))]
    result += [seq(seq(a(1), a(5)), e(0)), seq(a(1), seq(a(5), e(0)))]
    return tuple(result)


def leaves(tree):
    return leaves(tree[1]) + leaves(tree[2]) if tree[0] == "seq" else (tree,)


def present(tree, included):
    available = {LABELS[i] for i in included}
    return all(tag == "empty" or label in available for tag, label in leaves(tree))


def response(tree, included=tuple(range(6)), objects=OBJECTS, labels=LABELS):
    """Literal independent endpoint chaining; returns ambient index or None."""
    available = {labels[i]: ENDPOINTS[i] for i in included}
    reverse = {ENDPOINTS[i]: labels[i] for i in included}

    def visit(node):
        if node[0] == "arrow":
            return available.get(node[1])
        if node[0] == "empty":
            obj = objects[node[1]]
            return (obj, obj)
        left, right = visit(node[1]), visit(node[2])
        if left is None or right is None or left[1] != right[0]:
            return None
        return left[0], right[1]
    endpoints = visit(tree)
    return None if endpoints is None else reverse[endpoints]


def typed_tree(tree, included):
    if tree[0] == "seq":
        return "seq", typed_tree(tree[1], included), typed_tree(tree[2], included)
    if tree[0] == "empty":
        return "empty", OBJECTS[tree[1]]
    return "arrow", included.index(LABELS.index(tree[1]))


def bundle(value, included):
    if value is None:
        return None
    original = LABELS.index(value)
    return (*ENDPOINTS[original], included.index(original))


def all_paths(graph):
    n, edges = graph
    result = []
    def walk(start, current, word):
        result.append((start, word))
        for i, (source, target) in enumerate(edges):
            if source == current:
                walk(start, target, word + (i,))
    for start in range(n):
        walk(start, start, ())
    return tuple(result)


def path_endpoint(graph, path):
    current, word = path
    for edge in word:
        source, target = graph[1][edge]
        if source != current:
            return None
        current = target
    return current


def exact(value):
    if value is None:
        return ("none",)
    if type(value) in (bool, int, str):
        return type(value).__name__, value
    if type(value) is tuple:
        return "tuple", tuple(exact(x) for x in value)
    if type(value) is list:
        return "list", tuple(exact(x) for x in value)
    if type(value) is dict:
        return "dict", frozenset((exact(k), exact(v)) for k, v in value.items())
    raise ValueError("unsupported independent exact value")


def certify(actual, expected):
    if exact(actual) != exact(expected):
        raise ValueError("independent semantic certificate mismatch")


def attained_decoders(codes, responses):
    observations = tuple(dict.fromkeys(exact(x) for x in codes))
    targets = tuple(dict.fromkeys(exact(x) for x in responses))
    successful = []
    for values in product(targets, repeat=len(observations)):
        decoder = dict(zip(observations, values))
        if all(decoder[exact(c)] == exact(r) for c, r in zip(codes, responses)):
            successful.append(decoder)
    return successful


def mapped(responses, mapping):
    return tuple(tuple(None if x is None else mapping[x] for x in row)
                 for row in responses)


def report_truth(source, target, query_map, output_map, codes):
    restricted = tuple(tuple(row[q] for q in query_map) for row in target)
    return dict(commutes=mapped(source, output_map) == restricted,
                output_injective=len(set(output_map)) == len(output_map),
                source_recoverable=bool(attained_decoders(codes, source)),
                restricted_target_recoverable=bool(attained_decoders(codes, restricted)),
                full_target_recoverable=bool(attained_decoders(codes, target)))
