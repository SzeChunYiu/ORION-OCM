"""RV-377-123 -- a purpose-built world where TI-1 yields an EXACT capability number.

RV-377-122 failed its own sanity gate because a generic machine on 22 heterogeneous worlds
measured noise.  The repair is not 22 bespoke adapters.  It is one world whose protected
variable, channel content and query count are all controlled, so that theorem TI-1 gives a
closed-form capability prediction that ANY machine must obey.

THE WORLD.  W is a uniformly random bitstring of length L, drawn AFTER the machine is frozen.
  M = 2^L protected worlds.
  Development D reveals r distinct index/bit pairs of W, chosen uniformly.
  Query Q asks for the bit of W at a uniformly drawn index.
  Expected answer is W[index].

THE LAW.  P and R are independent of W, so an index never revealed carries no information the
machine can have.  On a revealed index the answer is determined; on an unrevealed index every
machine is reduced to a coin.  Therefore for ANY machine F(P,D,Q,A,R):

    accuracy(r)  <=  r/L  +  (1 - r/L) * 1/2  =  1/2 + r/(2L)

with equality for a machine that stores D and guesses elsewhere.

This is a prediction about UNSEEN FORMS.  It names no architecture.  It bounds every machine
in the channel class -- including ones nobody has built -- because it constrains what
information can reach the answer, not how the answer is computed.  A machine that beat it
would have to obtain bits of W from P or R, contradicting their independence.
"""
from __future__ import annotations
import random


def make_world(L, r, seed):
    rng = random.Random(seed)
    W = [rng.randrange(2) for _ in range(L)]
    idx = list(range(L)); rng.shuffle(idx)
    revealed = sorted(idx[:r])
    development = [{"index": i, "bit": W[i]} for i in revealed]
    return {"L": L, "r": r, "W": W, "development": development, "revealed": set(revealed)}


def queries(L, n, seed):
    rng = random.Random(seed ^ 0xBEEF)
    return [rng.randrange(L) for _ in range(n)]


def bound(L, r):
    """TI-1 capability ceiling for ANY machine in this channel class."""
    return 0.5 + r / (2.0 * L)


# ---- machines.  All see only (development, query).  None sees W. -----------------------
def m_table(dev, q, rng):
    for it in dev:
        if it["index"] == q: return it["bit"]
    return rng.randrange(2)

def m_always_zero(dev, q, rng):
    return 0

def m_majority(dev, q, rng):
    for it in dev:
        if it["index"] == q: return it["bit"]
    ones = sum(it["bit"] for it in dev)
    return 1 if ones * 2 > len(dev) else 0

def m_extrapolate(dev, q, rng):
    """tries to be clever: nearest revealed index by distance, copies its bit."""
    for it in dev:
        if it["index"] == q: return it["bit"]
    if not dev: return rng.randrange(2)
    best = min(dev, key=lambda it: abs(it["index"] - q))
    return best["bit"]

def m_parity(dev, q, rng):
    """assumes a parity structure that is not there."""
    for it in dev:
        if it["index"] == q: return it["bit"]
    return sum(it["bit"] for it in dev) % 2

MACHINES = {"table": m_table, "always_zero": m_always_zero, "majority": m_majority,
            "extrapolate": m_extrapolate, "parity": m_parity}


def measure(machine, L, r, n_queries, seed):
    w = make_world(L, r, seed)
    qs = queries(L, n_queries, seed)
    rng = random.Random(seed ^ 0x5EED)
    hit = sum(1 for q in qs if MACHINES[machine](w["development"], q, rng) == w["W"][q])
    return hit / len(qs)


def measure_ablated(machine, L, r, n_queries, seed, alt_seed):
    """development reminted from an INDEPENDENT world: the r=0 information case."""
    w = make_world(L, r, seed)
    alt = make_world(L, r, alt_seed)
    qs = queries(L, n_queries, seed)
    rng = random.Random(seed ^ 0x5EED)
    hit = sum(1 for q in qs if MACHINES[machine](alt["development"], q, rng) == w["W"][q])
    return hit / len(qs)
