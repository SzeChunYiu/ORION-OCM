"""Finite authored accounting register, never native execution prices."""
from fractions import Fraction as F

CATEGORIES = ("service", "holding", "update", "replay", "control")

def rational(x):
    if type(x) not in (int, F) or x < 0:
        raise ValueError("exact finite nonnegative charge required")
    return F(x)

def total(setup, rounds, terminal):
    result = rational(setup) + rational(terminal)
    for row in rounds:
        if set(row) != set(CATEGORIES):
            raise ValueError("incomplete cost ledger")
        result += sum(rational(row[k]) for k in CATEGORIES)
    return result

def bounds_decision(raw, compact):
    rl, ru = map(rational, raw)
    cl, cu = map(rational, compact)
    if rl > ru or cl > cu:
        raise ValueError("inconsistent cost interval")
    if cu < rl:
        return "COMPACT_STRICT"
    if ru < cl:
        return "RAW_STRICT"
    if rl == ru == cl == cu:
        return "TIE"
    return "UNRESOLVED"

def answers(h):
    a, b = h & 1, (h >> 1) & 1
    return (a, b, a ^ b, 1-a, a | b)

def convert(raw):
    if type(raw) is not tuple or len(raw) != 5 or any(type(x) is not int or x not in (0, 1) for x in raw):
        raise ValueError("five exact bits required")
    a, b = raw[:2]
    if raw != (a, b, a ^ b, 1-a, a | b):
        raise ValueError("not in the registered redundant class")
    return (a, b)

def decode(code, query):
    if type(code) is not tuple or len(code) != 2 or any(type(x) is not int or x not in (0, 1) for x in code):
        raise ValueError("two exact bits required")
    if type(query) is not int or not 0 <= query < 5:
        raise ValueError("unregistered query")
    a, b = code
    return (a, b, a ^ b, 1-a, a | b)[query]

def round_cost(service, holding, **extra):
    row = dict.fromkeys(CATEGORIES, 0)
    row.update(service=service, holding=holding)
    row.update(extra)
    return row

def controls():
    checks = 0
    for h in range(16):
        code = convert(answers(h))
        for query in range(5):
            if decode(code, query) != answers(h)[query]:
                raise ValueError("conversion loses retained answer")
            checks += 1
    horizons = []
    for h in (0, 3, 4):
        r = total(0, [round_cost(1, 5)] * h, 0)
        c = total(7, [round_cost(2, 2)] * h, 0)
        if c-r != 7-2*h:
            raise ValueError("charged benefit identity")
        horizons.append({"rounds": h, "raw": str(r), "compact": str(c),
                         "compact_minus_raw": str(c-r)})
    raw = total(0, [round_cost(1, 5)] * 4, 0)
    expensive = total(7, [round_cost(2, 2, replay=1)] * 4, 0)
    if not expensive > raw:
        raise ValueError("replay cost must reverse this comparison")
    return {"converter_decoder_checks": checks, "horizons": horizons,
            "same_width_saving_added_replay": {"raw": str(raw), "compact": str(expensive)},
            "interval_missing_upper": bounds_decision((24, 24), (0, 30)),
            "interval_separated": bounds_decision((24, 24), (22, 23)),
            "native_prices_or_measurements": False}
