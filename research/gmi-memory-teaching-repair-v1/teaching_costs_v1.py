"""Complete logical-event prices for two specified adequate lifetime policies."""
from collections import Counter
from fractions import Fraction as F
from teaching_machine_v1 import acquire, teach, pack, receive, serve, event

KINDS = ("hypothesis_scan", "label_check", "choose", "oracle", "model_write",
         "message_scan", "target_check", "selection_compare", "cardinality_check",
         "message_read", "format_check", "serve", "runtime_install",
         "runtime_bit_time", "model_bit_time", "temporary_bit_time",
         "message_write", "model_release", "message_release", "synthesis_workspace")

def prices(oracle=1000):
    result = {key: F(1) for key in KINDS}
    result["oracle"] = F(oracle)
    return result

def total(events, rates):
    if set(rates) != set(KINDS):
        raise ValueError("every registered event needs a price")
    if any(type(v) not in (int, F) or v < 0 for v in rates.values()):
        raise ValueError("exact nonnegative prices required")
    if not set(events) <= set(KINDS):
        raise ValueError("unpriced event")
    if any(type(n) is not int or n < 0 for n in events.values()):
        raise ValueError("invalid event count")
    return sum((F(rates[k])*n for k, n in events.items()), F(0))

def runtime(trace, reservation, horizon):
    if type(reservation) is not int or reservation < 1:
        raise ValueError("positive declared common runtime reservation")
    if type(horizon) is not int or horizon < 0:
        raise ValueError("invalid retention horizon")
    event(trace, "runtime_install", reservation)
    event(trace, "runtime_bit_time", reservation*horizon)

def finish(h, queries, trace, horizon):
    event(trace, "model_bit_time", 2*horizon)
    answers = serve(h, queries, trace)
    event(trace, "model_release", 2)
    return answers

def independent(h, queries=(0, 1), horizon=1, reservation=256):
    trace = Counter()
    runtime(trace, reservation, horizon)
    learned = acquire(lambda x: h[x], trace)
    answers = finish(learned, queries, trace, horizon)
    return dict(events=dict(trace), model=learned, answers=answers)

def sender(h, mode, horizon=1):
    trace = Counter()
    # Fixed complete search: 9 messages of four bits, each possible two-bit output,
    # and nine one-bit feasibility marks. Reserve all 63 bits during synthesis.
    event(trace, "synthesis_workspace", 63)
    event(trace, "temporary_bit_time", 63)
    message = teach(h, mode, trace)
    bits = pack(message, mode)
    event(trace, "message_write", len(bits))
    event(trace, "temporary_bit_time", len(bits)*horizon)
    return dict(events=dict(trace), bits=bits, message=message)

def receiver(bits, mode, queries=(0, 1), horizon=1, reservation=256):
    trace = Counter()
    runtime(trace, reservation, horizon)
    learned = receive(bits, mode, trace)
    answers = finish(learned, queries, trace, horizon)
    return dict(events=dict(trace), model=learned, answers=answers)

def comparison(h, mode, rates, n, **kwargs):
    if type(n) is not int or n < 1:
        raise ValueError("positive agent count")
    # Teacher acquisition and synthesis precede its model release.
    queries, horizon = kwargs.get("queries", (0,1)), kwargs.get("horizon",1)
    own_trace = Counter()
    runtime(own_trace, kwargs.get("reservation",256), horizon)
    learned = acquire(lambda x:h[x], own_trace)
    send = sender(learned, mode, horizon=horizon)
    answers = finish(learned, queries, own_trace, horizon)
    own = dict(events=dict(own_trace), model=learned, answers=answers)
    recv = receiver(send["bits"], mode, **kwargs)
    # Event maps are lifecycle totals. The multicast buffer is released only
    # after all n-1 identical receiver deliveries; one trace prices each copy.
    send["events"]["message_release"] = len(send["bits"])
    if own["model"] != recv["model"]:
        raise ValueError("common-task adequacy failed")
    C, S, U = (total(row["events"], rates) for row in (own, send, recv))
    taught = Counter(own["events"])
    taught.update(send["events"])
    for _ in range(n-1):
        taught.update(recv["events"])
    fresh = {k: n*v for k, v in own["events"].items()}
    return dict(C=C, S=S, U=U, independent=total(fresh, rates),
                taught=total(taught, rates), taught_events=dict(taught),
                independent_events=fresh)

def first_saving(C, S, U):
    if any(type(v) not in (int, F) or v < 0 for v in (C, S, U)):
        raise ValueError("invalid complete lifetime costs")
    return None if C <= U else S // (C-U) + 2
