"""The readout grammar G_PP of gmi-833-h-real-scale-particle-population-v1.

Frozen by FREEZE_V1.md section 5, FREEZE_V1_SLICE_ADDENDUM.md (the registered
particle vote, the registered query set and the readout language R) and
FREEZE_V1_SLICE_ADDENDUM_R2.md (R2.1-R2.7). Stdlib only. Exact integer
arithmetic throughout.

G_PP is a family-blind language over the sha-bound bytes of the external source
D. A readout maps a scored held query descriptor q to a decision (0 or 1) using
only (a) the stored particle population of q -- the stored descriptors that are
one-letter extensions of q, their recorded full-source votes and their stored
occurrence counts -- (b) the stored-context table (membership count and trie
fan-out), (c) the descriptor-closure vocabulary, (d) the query itself and (e)
the fit-slice majority label as the registered fallback. This module receives no
family name, no row name, no response values and no family-specific candidate
menu; structural class names are attached only by classify(), which reads the
readout name and nothing else.

The readout language, closed before any outcome (63 arms):

    C0             always 0
    C1             always 1
    LEN<=L         L = 6..12          1 iff len(q) <= L
    CNT>=K         K = 1..3           1 iff cnt(q) >= K, where cnt(q) is the
                                      number of stored descriptors equal to q
    ASSOC>=K       K = 1..3           1 iff |A(q)| >= K, where A(q) is the set
                                      of distinct letters stored immediately
                                      after q among stored descriptors of
                                      length >= 3
    LEN<=L&CNT>=j  L = 6..12, j = 1..3    1 iff both conjuncts fire
    LEN<=L&ASSOC>=j L = 6..12, j = 1..3   1 iff both conjuncts fire
    PLUR           strict plurality over q's stored particles of their
                   FULL-SOURCE votes v(p); no stored particle -> fit majority
    PLUR_W         strict majority by STORED-OCCURRENCE WEIGHT over q's stored
                   particles of their full-source votes v(p); empty -> fit
                   majority
    PREF_VOTE      majority true-label over stored proper prefixes q[:k],
                   2 <= k < len(q); empty -> fit majority
    EXT_VOTE       majority true-label over stored descriptors extending q
                   (descriptors of words starting with q, length > len(q));
                   empty -> fit majority
    MEM_FALLBACK   if q is stored, the strict plurality over q's stored
                   particles of their STORED-TABLE votes (stored-count(p) >=
                   VOTE_K -- the only vote the stored table can record for a
                   particle); no stored particle -> fit majority; if q is not
                   stored -> fit majority
    PARTICLE_1     if q is stored, ONE stored particle's full-source vote
                   v(p); if q is not stored -> fit majority

The constant-branch exclusion rule of the slice addendum: a membership readout
with a majority fallback whose stored branch reads out a constant is excluded
from the enumeration (semantically constant on the scored held set). Applied to
this ecology the rule eliminates NOTHING: the only such arm, MEM_FALLBACK,
reads the STORED-TABLE plurality of the query, which is two-valued over any
large fixed store (over the held scored queries its stored branch reads positive
on 31,880 and negative on 21,279, with 3 queries left without a stored
particle), so it is admitted and must lose by the data (it does, at every
stage; the winner rule rejects it).

The registered particle vote (FREEZE_V1_SLICE_ADDENDUM.md): VOTE_K = 3, i.e.
v(p) = 1 iff source-count(p) >= 3. The registered query set is the descriptors
q with at least two particles (|pop(q)| >= 2).

The charged per-query cost (FREEZE_V1_SLICE_ADDENDUM_R2.md R2.3):
    C0/C1/LEN                                    0
    CNT>=K / ASSOC>=K / a conjunction             1
    PARTICLE_1                                   1
    MEM_FALLBACK                                 2
    PLUR / PLUR_W   the number of stored particles of the query
    PREF/EXT_VOTE   the number of stored descriptors referenced
"""
import hashlib

LEN_THRESHOLDS = tuple(range(6, 13))
CNT_THRESHOLDS = (1, 2, 3)
ASSOC_THRESHOLDS = (1, 2, 3)
VOTE_K = 3
MIN_POP = 2
ORDER_MULT = 2654435761
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("CNT>=%d" % K for K in CNT_THRESHOLDS)
            + tuple("ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)
            + tuple("LEN<=%d&CNT>=%d" % (L, j)
                    for L in LEN_THRESHOLDS for j in CNT_THRESHOLDS)
            + tuple("LEN<=%d&ASSOC>=%d" % (L, j)
                    for L in LEN_THRESHOLDS for j in ASSOC_THRESHOLDS)
            + ("PLUR", "PLUR_W", "PREF_VOTE", "EXT_VOTE",
               "MEM_FALLBACK", "PARTICLE_1"))

_CONSTANT = frozenset(("C0", "C1"))
_LENGTH = frozenset("LEN<=%d" % L for L in LEN_THRESHOLDS)
_CONJ = frozenset(r for r in READOUTS if "&" in r)
_PLURAL = frozenset(("PLUR", "PLUR_W"))


def classify(name):
    """Structural class of a readout, read from the name alone."""
    if name in _CONSTANT:
        return "CONSTANT_ARM"
    if name in _LENGTH:
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name == "CNT>=1":
        return "STORED_EXEMPLAR_MEMBERSHIP"
    if name.startswith("CNT>="):
        return "STORED_EXEMPLAR_COUNT_THRESHOLD"
    if name == "ASSOC>=1":
        return "CUE_ASSOCIATION_RETRIEVAL"
    if name == "ASSOC>=2":
        return "CUE_ASSOCIATION_FANOUT"
    if name in _CONJ:
        return "THRESHOLD_CONJUNCTION"
    if name.startswith("ASSOC>="):
        return "CUE_ASSOCIATION_SIZE_THRESHOLD"
    if name in _PLURAL:
        return "POPULATION_PLURALITY"
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return "NEIGHBORHOOD_MAJORITY_VOTE"
    if name == "MEM_FALLBACK":
        return "STORED_TABLE_READ_WITH_FALLBACK"
    if name == "PARTICLE_1":
        return "STORED_SINGLE_PARTICLE_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def order_key(i):
    """The registered target-independent Knuth presentation key.

    key(i) = (i * 2654435761) mod 2**32; the descriptor list is sorted by this
    key (stable, ascending) before the arithmetic 7:1 slice. Registered by
    FREEZE_V1_SLICE_ADDENDUM.md.
    """
    return (i * ORDER_MULT) % (2 ** 32)


def digest():
    """Stable digest of the frozen readout grammar, particle vote and lever."""
    h = hashlib.sha256()
    h.update("+".join(READOUTS).encode())
    h.update(("VOTE_K=%d;MIN_POP=%d" % (VOTE_K, MIN_POP)).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    return h.hexdigest()
