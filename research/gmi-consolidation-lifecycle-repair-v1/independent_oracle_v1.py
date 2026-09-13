"""Independent complete pair-graph distinguishability and census."""
from collections import deque
from itertools import product
from finite_machine_v1 import Machine, refine, quotient, execute

def distinguishing_word(m, s, t):
    todo = deque([(s, t, ())])
    seen = set()
    while todo:
        u, v, word = todo.popleft()
        if (u, v) in seen:
            continue
        seen.add((u, v))
        if m.q[u] != m.q[v]:
            return word
        for a in range(len(m.nxt[u])):
            if m.out[u][a] != m.out[v][a]:
                return word + (a,)
            todo.append((m.nxt[u][a], m.nxt[v][a], word + (a,)))
    return None

def machines(n, actions):
    for q in product(range(2), repeat=n):
        for flat in product(range(n), repeat=n * actions):
            nxt = tuple(tuple(flat[s*actions:(s+1)*actions]) for s in range(n))
            for out in product(range(2), repeat=n * actions):
                yield Machine(q, nxt, tuple(tuple(out[s*actions:(s+1)*actions])
                                           for s in range(n)))

def census():
    totals = {"machines": 0, "ordered_state_pairs": 0,
              "equivalent_pairs": 0, "distinguishable_pairs": 0}
    for n, a in ((2, 2), (3, 1)):
        for m in machines(n, a):
            e = refine(m)
            small, actual_e = quotient(m, e)
            if e != actual_e:
                raise ValueError("noncanonical quotient")
            for s, t in product(range(n), repeat=2):
                witness = distinguishing_word(m, s, t)
                equivalent = witness is None
                if equivalent != (e[s] == e[t]):
                    raise ValueError("independent pair oracle disagrees")
                if witness is not None and execute(m, s, witness)[0] == execute(m, t, witness)[0]:
                    raise ValueError("false distinguishing word")
                totals["ordered_state_pairs"] += 1
                totals["equivalent_pairs" if equivalent else "distinguishable_pairs"] += 1
            for s in range(n):
                if small.q[e[s]] != m.q[s]:
                    raise ValueError("quotient label mismatch")
                for a in range(len(m.nxt[s])):
                    if small.out[e[s]][a] != m.out[s][a] or small.nxt[e[s]][a] != e[m.nxt[s][a]]:
                        raise ValueError("quotient step mismatch")
            totals["machines"] += 1
    return totals
