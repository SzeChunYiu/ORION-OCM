"""The readout grammar G_AM of gmi-833-h-real-scale-associative-memory-v1.

Frozen by FREEZE_V1.md section 5, FREEZE_V1_SLICE_ADDENDUM.md (the readout
language R) and FREEZE_V1_SLICE_ADDENDUM_R2.md (R2.1-R2.4). Stdlib only.
Exact integer arithmetic throughout.

G_AM is a family-blind language over the sha-bound bytes of the external
source D. A readout maps a held query cue q to a decision (0 or 1) using only
(a) the stored association table -- the trie fan-out over the descriptors at
fit positions -- (b) the descriptor-closure vocabulary, (c) the query itself
and (d) the fit-slice majority label as the registered fallback. This module
receives no family name, no row name, no response values and no
family-specific candidate menu; structural class names are attached only by
classify(), which reads the readout name and nothing else.

The readout language, closed before any outcome:

    C0           always 0
    C1           always 1
    LEN<=L       L = 7..12           1 iff len(q) <= L
    ASSOC>=K     K = 1..3            1 iff |A(q)| >= K, where A(q) is the
                                     stored association of q (the distinct
                                     letters stored immediately after q among
                                     stored descriptors)
    PREF_VOTE    majority label over stored proper prefixes q[:k],
                 2 <= k < len(q); empty -> fit majority
    EXT_VOTE     majority label over stored descriptors extending q
                 (descriptors of words starting with q of length > len(q));
                 empty -> fit majority
    MEM_FALLBACK if q is stored, 1 iff |A(q)| >= 2 over the stored table;
                 else the fit majority

The constant-branch exclusion rule of the slice addendum: a membership
readout with a majority fallback whose stored branch reads out a constant is
excluded from the enumeration (semantically constant on held). Applied to
this ecology the rule eliminates NOTHING: the only such arm, MEM_FALLBACK,
reads the STORED association size of the query, which is two-valued over any
large fixed store, so it is admitted and must lose by the data (it does, at
the rank stage; the winner rule rejects it).

The charged per-query cost (FREEZE_V1_SLICE_ADDENDUM_R2.md R2.3):
    C0/C1/LEN      0
    ASSOC>=K       1   (one association fan-out lookup)
    MEM_FALLBACK   2   (one membership lookup and one fan-out lookup)
    PREF/EXT_VOTE  the number of stored descriptors referenced
"""
import hashlib

LEN_THRESHOLDS = tuple(range(7, 13))
ASSOC_THRESHOLDS = (1, 2, 3)
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)
            + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK"))
ORDER_MULT = 2654435761

_CONSTANT = frozenset(("C0", "C1"))
_LENGTH = frozenset("LEN<=%d" % L for L in LEN_THRESHOLDS)
_ASSOC = frozenset("ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)


def classify(name):
    """Structural class of a readout, read from the name alone."""
    if name in _CONSTANT:
        return "CONSTANT_ARM"
    if name in _LENGTH:
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name == "ASSOC>=1":
        return "CUE_ASSOCIATION_RETRIEVAL"
    if name == "ASSOC>=2":
        return "CUE_ASSOCIATION_FANOUT"
    if name in _ASSOC:
        return "CUE_ASSOCIATION_SIZE_THRESHOLD"
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return "NEIGHBORHOOD_MAJORITY_VOTE"
    if name == "MEM_FALLBACK":
        return "STORED_ASSOCIATION_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def order_key(i):
    """The registered target-independent Knuth presentation key.

    key(i) = (i * 2654435761) mod 2**32; the descriptor list is sorted by this
    key (stable, ascending) before the arithmetic 7:1 slice. Registered by
    FREEZE_V1_SLICE_ADDENDUM.md.
    """
    return (i * ORDER_MULT) % (2 ** 32)


def digest():
    """Stable digest of the frozen readout grammar and presentation lever."""
    h = hashlib.sha256()
    h.update("+".join(READOUTS).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    return h.hexdigest()
