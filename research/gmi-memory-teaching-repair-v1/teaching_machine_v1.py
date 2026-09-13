"""Exact finite teacher, mode-dependent learner, and event-level logical costs."""
from itertools import product
from collections import Counter

HYPOTHESES = tuple(product((0, 1), repeat=2))
MESSAGES = tuple(product((-1, 0, 1), repeat=2))

def event(trace, name, count=1):
    trace[name] += count

def learn(message, mode, trace=None):
    trace = Counter() if trace is None else trace
    if mode not in (0, 1) or message not in MESSAGES:
        raise ValueError("invalid learner interface")
    consistent = []
    for h in HYPOTHESES:
        event(trace, "hypothesis_scan")
        ok = True
        for x, label in enumerate(message):
            event(trace, "label_check")
            ok = ok and (label == -1 or h[x] == label)
        if ok:
            consistent.append(h)
    event(trace, "choose")
    return consistent[0 if mode == 0 else -1]

def acquire(oracle, trace):
    h = []
    for x in range(2):
        event(trace, "oracle")
        value = oracle(x)
        event(trace, "label_check")
        if type(value) is not int or value not in (0, 1):
            raise ValueError("oracle contract violated")
        h.append(value)
        event(trace, "model_write")
    return tuple(h)

def teach(h, mode, trace=None):
    trace = Counter() if trace is None else trace
    if h not in HYPOTHESES:
        raise ValueError("unregistered target")
    candidates = []
    for message in MESSAGES:
        event(trace, "message_scan")
        truthful = True
        for x, label in enumerate(message):
            event(trace, "label_check")
            truthful = truthful and (label == -1 or h[x] == label)
        decoded = learn(message, mode, trace)
        event(trace, "target_check", 2)
        if truthful and decoded == h:
            candidates.append(message)
    # Nine fixed candidates; explicit cardinality and lexicographic comparisons.
    event(trace, "selection_compare", len(candidates))
    best = min(candidates, key=lambda m: (sum(x != -1 for x in m), m))
    event(trace, "cardinality_check", 2*len(candidates))
    return best

def pack(message, mode):
    if message not in MESSAGES or mode not in (0, 1):
        raise ValueError("invalid message")
    return str(mode)+"".join(format(x+1, "02b") for x in message)

def receive(bits, mode, trace=None):
    trace = Counter() if trace is None else trace
    if not isinstance(bits, str) or len(bits) != 5 or any(x not in "01" for x in bits):
        raise ValueError("invalid message framing")
    event(trace, "message_read", 5)
    event(trace, "format_check", 5)
    if bits[0] != str(mode):
        raise ValueError("learner mode mismatch")
    message = tuple(int(bits[i:i+2], 2)-1 for i in (1, 3))
    if message not in MESSAGES:
        raise ValueError("invalid label symbol")
    h = learn(message, mode, trace)
    for x, label in enumerate(message):
        event(trace, "label_check")
        if label != -1 and h[x] != label:
            raise ValueError("inconsistent learner")
    event(trace, "model_write", 2)
    return h

def serve(h, queries, trace):
    answers = []
    for x in queries:
        if x not in (0, 1):
            raise ValueError("unknown query")
        event(trace, "serve")
        answers.append(h[x])
    return tuple(answers)

def truth_table_oracle(message, mode):
    # Separate truth-relation enumeration, no call to learn/teach.
    rows = {h for h in product((0, 1), repeat=2)
            if all(label == -1 or h[x] == label for x, label in enumerate(message))}
    return min(rows) if mode == 0 else max(rows)

def encoder_oracle(h, mode):
    rows = [m for m in product((-1, 0, 1), repeat=2)
            if all(v == -1 or h[x] == v for x, v in enumerate(m))
            and truth_table_oracle(m, mode) == h]
    return min(rows, key=lambda m: (2-m.count(-1), m))
