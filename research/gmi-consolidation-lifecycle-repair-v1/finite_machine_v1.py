"""Exact finite supplied machines; no native or learning imports."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Machine:
    q: tuple
    nxt: tuple
    out: tuple

    def __post_init__(self):
        if any(type(v) is not tuple for v in (self.q, self.nxt, self.out)) or any(type(r) is not tuple for r in self.nxt + self.out):
            raise ValueError("immutable complete tables required")
        n = len(self.q)
        if not n or len(self.nxt) != n or len(self.out) != n:
            raise ValueError("nonempty complete state register required")
        a = len(self.nxt[0])
        if not a or any(len(r) != a for r in self.nxt + self.out):
            raise ValueError("complete nonempty action register required")
        if any(type(x) is not int or x < 0 for x in self.q):
            raise ValueError("exact finite nonnegative labels required")
        if any(type(x) is not int or not 0 <= x < n for r in self.nxt for x in r):
            raise ValueError("invalid successor")
        if any(type(x) is not int or x < 0 for r in self.out for x in r):
            raise ValueError("invalid emission")

def labels(values):
    seen = {}
    return tuple(seen.setdefault(x, len(seen)) for x in values)

def refine(m):
    e = labels(m.q)
    while True:
        new = labels((m.q[s], tuple((m.out[s][a], e[t])
                     for a, t in enumerate(m.nxt[s]))) for s in range(len(m.q)))
        if new == e:
            return e
        e = new

def quotient(m, e):
    if len(e) != len(m.q) or any(type(x) is not int or x < 0 for x in e):
        raise ValueError("complete encoding required")
    e = labels(e)
    representatives = [e.index(i) for i in range(max(e) + 1)]
    for s in range(len(m.q)):
        t = representatives[e[s]]
        if m.q[s] != m.q[t] or m.out[s] != m.out[t]:
            raise ValueError("current/emitted label conflict")
        if tuple(e[x] for x in m.nxt[s]) != tuple(e[x] for x in m.nxt[t]):
            raise ValueError("encoded successor conflict")
    return Machine(tuple(m.q[s] for s in representatives),
                   tuple(tuple(e[t] for t in m.nxt[s]) for s in representatives),
                   tuple(m.out[s] for s in representatives)), e

def execute(m, state, word):
    if type(state) is not int or not 0 <= state < len(m.q):
        raise ValueError("invalid initial state")
    trace = [m.q[state]]
    for a in word:
        if type(a) is not int or not 0 <= a < len(m.nxt[state]):
            raise ValueError("unregistered action")
        trace.append(m.out[state][a])
        state = m.nxt[state][a]
        trace.append(m.q[state])
    return trace, state

def preserving_update(q, update):
    if not q or len(q) != len(update):
        raise ValueError("complete update required")
    decoder = {}
    for y, z in zip(q, update):
        if z in decoder and decoder[z] != y:
            return None
        decoder[z] = y
    return decoder
