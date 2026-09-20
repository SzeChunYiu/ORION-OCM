"""Actual V15 code contexts and explicit common-value decoding."""
from dataclasses import dataclass
from core_v23 import Context, checked, index, need, observe, parameters, rational


def validate_encoding(context, decoder):
    checked(context)
    need(context.n == context.m, "one identity code per history required")
    need(type(decoder) is tuple and len(decoder) == context.m, "decoder dimension")
    ids = []
    for pair in decoder:
        need(type(pair) is tuple and len(pair) == 2, "decoded ID/score pair")
        need(type(pair[0]) is str and bool(pair[0]), "nonempty string ID required")
        rational(pair[1])
        ids.append(pair[0])
    need(len(set(ids)) == len(ids), "decoder IDs must be injective")
    need(all(not context.defined[i] or context.values[i] == i
             for i in range(context.n)), "defined histories retain identity codes")
    need(context.order == tuple(tuple(y[1] <= x[1] for y in decoder) for x in decoder),
         "coded order must reflect decoded score order")


@dataclass(frozen=True)
class Encoded:
    context: Context
    decoder: tuple

    def __post_init__(self):
        validate_encoding(self.context, self.decoder)


def at(family, t):
    values = parameters(family, t)
    n = len(family.ids)
    context = Context(n, n, family.admitted, family.defined,
                      tuple(i if family.defined[i] else None for i in range(n)),
                      tuple(tuple(y <= x for y in values) for x in values))
    return Encoded(context, tuple(zip(family.ids, values)))


def decoded(encoded, history):
    need(type(encoded) is Encoded, "validated Encoded context required")
    validate_encoding(encoded.context, encoded.decoder)
    index(history, encoded.context.n)
    tag, value = observe(encoded.context, history)
    return (tag, encoded.decoder[value] if tag == "VALUE" else None)
