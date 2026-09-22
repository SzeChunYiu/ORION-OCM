"""Executable form of the frozen readout grammar G_ML of
gmi-833-h-real-scale-model-free-rl-v1 (issue #833, section H,
row `Model-free RL-like learning.`, scope SIGMA_HMLR).

Stdlib only. Exact integer arithmetic throughout.

G_ML is a family-blind language over the sha-bound bytes of the external
source D. A readout maps a held query experience q to a decision (0 or 1)
using only (a) the stored experience table -- the experiences at the fit
positions, their contexts and their received outcomes, and the cell masses
accumulated from them, (b) the vocabulary index of stored contexts, (c) the
query itself, and (d) the registered fallback constant of the store stream.
This module receives no family name, no row name, no response values and no
family-specific candidate menu; structural class names are attached only by
classify(), which reads the arm name and nothing else.

The readout language R, closed before any outcome (FREEZE_V1_SLICE_ADDENDUM.md
section 2), 70 arms:

    C0              always 0
    C1              always 1
    LEN<=L          L = 6..12
    CNT>=K          K = 1..3     the context occurs >= K times among stored
    ASSOC>=K        K = 1..3     >= K distinct letters follow the context
    LEN<=L&CNT>=K   the conjunction
    LEN<=L&ASSOC>=K the conjunction
    PREF_VOTE       majority STORED outcome over stored proper prefixes
    EXT_VOTE        majority STORED outcome over stored extensions
    MEM_FALLBACK    if stored, the STORED outcome the table records
    RECENCY_LAST    if stored, the received outcome of the LAST stored
                    experience at that context
    VOTE>=j/10      j = 1..9, 1 iff 10 * P(state) >= j * N(state)

The registered fallback, used by every readout with an empty neighbourhood or
an empty cell, is the store stream's majority constant (FREEZE_V1.md section
4), asserted to be 0 by the caller before any enumeration.

The charged per-query cost (FREEZE_V1_SLICE_ADDENDUM.md section 5): C0/C1/LEN
0; CNT>=K, ASSOC>=K, a conjunction 1; RECENCY_LAST 1; MEM_FALLBACK 2;
PREF_VOTE/EXT_VOTE the number of stored descriptors referenced; VOTE>=j/10 the
store's cell mass at the query's state.
"""
import hashlib

LEN_THRESHOLDS = tuple(range(6, 13))
CNT_THRESHOLDS = (1, 2, 3)
ASSOC_THRESHOLDS = (1, 2, 3)
VOTE_THRESHOLDS = tuple(range(1, 10))
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("CNT>=%d" % K for K in CNT_THRESHOLDS)
            + tuple("ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)
            + tuple("LEN<=%d&CNT>=%d" % (L, K)
                    for L in LEN_THRESHOLDS for K in CNT_THRESHOLDS)
            + tuple("LEN<=%d&ASSOC>=%d" % (L, K)
                    for L in LEN_THRESHOLDS for K in ASSOC_THRESHOLDS)
            + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK", "RECENCY_LAST")
            + tuple("VOTE>=%d/10" % j for j in VOTE_THRESHOLDS))
ORDER_MULT = 2654435761

_CONSTANT = frozenset(("C0", "C1"))
_LENGTH = frozenset("LEN<=%d" % L for L in LEN_THRESHOLDS)


def classify(name):
    """Structural class of a readout, read from the arm name alone."""
    if name in _CONSTANT:
        return "CONSTANT_ARM"
    if name in _LENGTH:
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if "&" in name:
        return "THRESHOLD_CONJUNCTION"
    if name.startswith("CNT>="):
        return "STORED_EXEMPLAR_COUNT_THRESHOLD"
    if name.startswith("ASSOC>="):
        return "CUE_ASSOCIATION_FANOUT"
    if name.startswith("VOTE>="):
        return "REWARD_PROPENSITY_ACCUMULATION"
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return "NEIGHBORHOOD_MAJORITY_VOTE"
    if name == "MEM_FALLBACK":
        return "STORED_OUTCOME_READ_WITH_FALLBACK"
    if name == "RECENCY_LAST":
        return "STORED_LAST_OUTCOME_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def cost_of(name, cell_mass, p1, p0, e1, e0):
    """The registered charged cost of one query for `name`
    (FREEZE_V1_SLICE_ADDENDUM.md section 5)."""
    if name in ("C0", "C1") or name in _LENGTH:
        return 0
    if name.startswith("VOTE>="):
        return cell_mass
    if name == "MEM_FALLBACK":
        return 2
    if name == "RECENCY_LAST":
        return 1
    if name == "PREF_VOTE":
        return p1 + p0
    if name == "EXT_VOTE":
        return e1 + e0
    return 1


def order_key(i):
    """The registered target-independent Knuth presentation key.

    key(i) = (i * 2654435761) mod 2**32; the experience list is sorted by this
    key (stable, ascending) before the arithmetic 7:1 slice. Registered by
    FREEZE_V1_SLICE_ADDENDUM.md section 1.
    """
    return (i * ORDER_MULT) % (2 ** 32)


def digest():
    """Stable digest of the frozen readout grammar and presentation lever."""
    h = hashlib.sha256()
    h.update("+".join(READOUTS).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    return h.hexdigest()
