"""Independent finite arithmetic, path traces and exhaustive attained decoders."""
from fractions import Fraction
from itertools import product

EDGES = ((0, 0), (0, 1), (1, 0), (1, 1))
SINGLETONS = ((0, (0,)), (0, (1,)))


def exact(value):
    if type(value) is tuple:
        return ("tuple", tuple(exact(x) for x in value))
    if type(value) is Fraction:
        return ("fraction", value.numerator, value.denominator)
    if type(value) is bool:
        return ("bool", value)
    if type(value) is int:
        return ("int", value)
    if type(value) is str:
        return ("str", value)
    if value is None:
        return ("none",)
    if type(value) is dict:
        return ("dict", tuple(sorted((exact(k), exact(v)) for k, v in value.items())))
    raise ValueError("unsupported oracle value")


def certify(actual, expected):
    if exact(actual) != exact(expected):
        raise ValueError("semantic certificate differs")
    return True


def attained_decoders(observations, targets):
    obs = tuple(exact(x) for x in observations)
    tgt = tuple(exact(x) for x in targets)
    inputs = tuple(dict.fromkeys(obs))
    outputs = tuple(dict.fromkeys(tgt))
    valid = []
    for values in product(outputs, repeat=len(inputs)):
        mapping = dict(zip(inputs, values))
        if all(mapping[a] == b for a, b in zip(obs, tgt)):
            valid.append(mapping)
    return tuple(valid)


def forward_tag(rewards, history):
    _, actions = history
    return ("VALUE", rewards[actions[0]]) if len(actions) == 1 else ("UNDEFINED", None)


def order_view(rewards):
    return tuple(tuple(a <= b for b in rewards) for a in rewards)


def masks():
    return tuple((True, bool(k & 1), bool(k & 2), True) for k in range(4))


def roster():
    result = []
    for length in range(4):
        for start in range(2):
            for tail in product(range(2), repeat=length):
                states = (start,) + tail
                word = tuple(2 * a + b for a, b in zip(states, states[1:]))
                result.append((start, word))
    return tuple(result)


def traverse(history):
    current, word = history
    for edge in word:
        source, target = EDGES[edge]
        if source != current:
            raise ValueError("ill-typed oracle history")
        current = target
    return current


def reverse_tag(mask, values, defined, history):
    target = traverse(history)
    if not all(mask[edge] for edge in history[1]):
        return ("ILLEGAL", None)
    if not defined[target]:
        return ("UNDEFINED", None)
    return ("VALUE", Fraction(values[target]))


def context_fields(mask, values, defined):
    histories = roster()
    endpoints = tuple(traverse(h) for h in histories)
    return {
        "n": len(histories), "m": 2,
        "admitted": tuple(all(mask[e] for e in h[1]) for h in histories),
        "defined": tuple(defined[e] for e in endpoints),
        "values": tuple(values[e] if defined[e] else None for e in endpoints),
        "order": ((True, True), (False, True)),
    }


def certify_context(encoded, expected, histories, decoder):
    certify(encoded.roster, histories)
    certify(encoded.decoder, decoder)
    for key, value in expected.items():
        certify(getattr(encoded.context, key), value)
    return True


def expected_views(mask, values, defined):
    histories = roster()
    tags = tuple((h, reverse_tag(mask, values, defined, h)) for h in histories)
    return {
        "weak_state": tuple((s, values[s], defined[s]) for s in range(2)),
        "active_domain": tuple((h, tag[1]) for h, tag in tags if tag[0] == "VALUE"),
        "tagged": tags,
        "domain_signature": tuple((h, tag[0] != "ILLEGAL") for h, tag in tags),
    }


def weighted(weights, profile):
    return sum((w * x for w, x in zip(weights, profile)), Fraction(0))


def thin_data(mask):
    labels = tuple(i for i in range(4) if mask[i])
    local = {a: i for i, a in enumerate(labels)}
    rows = []
    for a in labels:
        row = []
        for b in labels:
            sa, ta = EDGES[a]
            sb, tb = EDGES[b]
            row.append(local[2 * sa + tb] if ta == sb else None)
        rows.append(tuple(row))
    return {"source": tuple(EDGES[a][0] for a in labels),
            "target": tuple(EDGES[a][1] for a in labels),
            "identities": (local[0], local[3]), "rows": tuple(rows),
            "local_to_ambient": labels,
            "ambient_to_local": tuple(local.get(a) for a in range(4))}
