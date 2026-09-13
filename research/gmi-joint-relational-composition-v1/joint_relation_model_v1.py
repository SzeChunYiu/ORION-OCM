"""Exact finite adequate-action cover model; no graph relaxation."""
from dataclasses import dataclass
from functools import lru_cache
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Relation:
    rows: tuple
    actions: int

    def __post_init__(self):
        require(type(self.actions) is int and self.actions > 0, "positive action register")
        require(type(self.rows) in (tuple, list) and bool(self.rows), "nonempty input register")
        normalized = []
        for row in self.rows:
            require(type(row) in (tuple, list, set, frozenset) and bool(row), "nonempty adequate set")
            require(all(type(a) is int and 0 <= a < self.actions for a in row), "action outside register")
            normalized.append(tuple(sorted(set(row))))
        object.__setattr__(self, "rows", tuple(normalized))


def fixed_bits(alphabet):
    require(type(alphabet) is int and alphabet > 0, "positive message alphabet")
    return (alphabet-1).bit_length()


def preimages(relation):
    return tuple(frozenset(x for x, row in enumerate(relation.rows) if a in row)
                 for a in range(relation.actions))


def from_preimages(sets, inputs):
    require(type(inputs) is int and inputs > 0, "positive input count")
    require(type(sets) in (tuple, list) and bool(sets), "nonempty preimage register")
    require(all(type(s) in (tuple, list, set, frozenset) for s in sets), "preimage sets")
    require(all(type(x) is int and 0 <= x < inputs for s in sets for x in s), "preimage input")
    return Relation(tuple(tuple(a for a, s in enumerate(sets) if x in s)
                          for x in range(inputs)), len(sets))


def joint_relation(left, right):
    return Relation(tuple(tuple(a*right.actions+b for a, b in product(x, y))
                          for x, y in product(left.rows, right.rows)), left.actions*right.actions)


def verify_protocol(relation, encoder, decoder):
    require(type(encoder) in (tuple, list) and len(encoder) == len(relation.rows), "encoder coverage")
    require(type(decoder) in (tuple, list) and bool(decoder), "nonempty decoder")
    require(all(type(a) is int and 0 <= a < relation.actions for a in decoder), "decoder action")
    require(all(type(z) is int and 0 <= z < len(decoder) for z in encoder), "message label")
    outputs = tuple(decoder[z] for z in encoder)
    require(all(a in row for a, row in zip(outputs, relation.rows)), "inadequate output")
    return dict(input_checks=len(encoder), used_symbols=len(set(encoder)),
                declared_symbols=len(decoder), outputs=outputs)


def cover_protocol(relation, decoder):
    decoder = tuple(decoder)
    require(bool(decoder), "empty cover")
    encoder = []
    for row in relation.rows:
        choices = [i for i, a in enumerate(decoder) if a in row]
        require(bool(choices), "uncovered input")
        encoder.append(choices[0])
    result = verify_protocol(relation, encoder, decoder)
    return dict(encoder=tuple(encoder), decoder=decoder, **result)


def minimum_cover(relation):
    masks = tuple(sum(1 << x for x in s) for s in preimages(relation))
    stats = dict(uncovered_states=0, candidate_branches=0)

    @lru_cache(None)
    def solve(uncovered):
        stats["uncovered_states"] += 1
        if not uncovered:
            return ()
        first = uncovered & -uncovered
        options = []
        for a, mask in enumerate(masks):
            if first & mask:
                stats["candidate_branches"] += 1
                options.append(tuple(sorted((a,)+solve(uncovered & ~mask))))
        return min(options, key=lambda cover: (len(cover), cover))

    decoder = solve((1 << len(relation.rows))-1)
    protocol = cover_protocol(relation, decoder)
    require(protocol["used_symbols"] == len(decoder), "nonminimal constructed cover")
    return protocol, stats


def incidence_bound(left, right, left_width, right_width):
    """Conditional on certified local widths; this does not independently prove them."""
    require(type(left_width) is int and left_width > 0, "left certified width")
    require(type(right_width) is int and right_width > 0, "right certified width")
    s1, s2 = max(map(len, preimages(left))), max(map(len, preimages(right)))
    n1, n2 = len(left.rows), len(right.rows)
    ceildiv = lambda a, b: (a+b-1)//b
    return dict(row=ceildiv(n1*right_width, s1), column=ceildiv(n2*left_width, s2),
                area=ceildiv(n1*n2, s1*s2), max_first_preimage=s1, max_second_preimage=s2)
