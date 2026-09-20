"""Original two-action witness on actual free paths with fixed value decoding."""
from fractions import Fraction
from core_v28 import Encoded, checked_history, contexts, need, paths, tup

ACTION_GRAPH = (1, ((0, 0), (0, 0)))
ROSTER = ((0, (0,)), (0, (1,)))
DECODER = tuple(Fraction(i) for i in range(3))
ORDER = tuple(tuple(i <= j for j in range(3)) for i in range(3))


def reward_codes(rewards):
    tup(rewards)
    need(len(rewards) == 2, "two action rewards required")
    need(all(type(x) is Fraction and x in DECODER for x in rewards), "reward outside exact grid")
    return tuple(DECODER.index(x) for x in rewards)


def forward_context(rewards):
    codes = reward_codes(rewards)
    context = contexts.Context(2, 3, (True, True), (True, True), codes, ORDER)
    return Encoded(context, ROSTER, DECODER)


def forward_observe(rewards, history):
    codes = reward_codes(rewards)
    path, _ = checked_history(ACTION_GRAPH, history)
    defined = len(path[1]) == 1
    value = codes[path[1][0]] if defined else None
    encoded = Encoded(contexts.Context(1, 3, (True,), (defined,), (value,), ORDER),
                      (path,), DECODER)
    return encoded.observe(0)


def process_observation():
    domains, generator_maps = (1,), ((0,), (0,))
    for path in ROSTER:
        need(paths.interpret(ACTION_GRAPH, path, domains, generator_maps) == (0,), "original processStep")
    return ACTION_GRAPH, domains, generator_maps


def order_view(encoded):
    need(type(encoded) is Encoded, "Encoded required")
    need(encoded.roster == ROSTER and encoded.decoder == DECODER, "fixed forward interface")
    return tuple(tuple(contexts.compare(encoded.context, i, j) for j in range(2)) for i in range(2))


def values_view(encoded):
    need(type(encoded) is Encoded, "Encoded required")
    need(encoded.roster == ROSTER and encoded.decoder == DECODER, "fixed forward interface")
    values = tuple(encoded.observe(i) for i in range(2))
    need(all(tag == "VALUE" for tag, _ in values), "forward histories must be admitted and evaluated")
    return tuple((history, values[i][1]) for i, history in enumerate(ROSTER))
