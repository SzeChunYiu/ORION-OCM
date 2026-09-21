"""The readout grammar G_NN of gmi-833-h-real-scale-nearest-neighbor-v1.

Frozen by FREEZE_V1.md section 5, FREEZE_V1_SLICE_ADDENDUM.md (the readout
language R) and FREEZE_V1_SLICE_ADDENDUM_R2.md (R2.1-R2.4). Stdlib only.
Exact integer arithmetic throughout.

G_NN is a family-blind language over the sha-bound bytes of the external
source D. A readout maps a held query descriptor q to a decision (0 or 1)
using only (a) the stored exemplar table -- the set of descriptors at fit
positions -- (b) the descriptor-closure vocabulary, (c) the query itself and
(d) the fit-slice majority label as the registered fallback. This module
receives no family name, no row name, no response values and no
family-specific candidate menu; structural class names are attached only by
classify(), which reads the readout name and nothing else.

The readout language, closed before any outcome:

    C0           always 0
    C1           always 1
    LEN<=L       L = 7..12           1 iff len(q) <= L
    CNT>=K       K = 1..3            1 iff q occurs >= K times among stored
                                     descriptors
    PREF_VOTE    majority label over stored proper prefixes q[:k],
                 2 <= k < len(q); ties -> 0; empty -> fit majority
    EXT_VOTE     majority label over stored descriptors extending q
                 (descriptors of words starting with q of length > len(q));
                 ties -> 0; empty -> fit majority

The membership-with-majority-fallback readout is excluded: on a held query its
stored branch reads out 1 (a stored occurrence plus the held occurrence makes
the descriptor shared), so it is semantically C1 and cannot separate. The
elimination is structural and outcome-free and holds because the fit shared
fraction exceeds 1/2, which the executor asserts before enumeration.

The charged per-query cost (FREEZE_V1_SLICE_ADDENDUM_R2.md R2.3):
    C0/C1/LEN      0
    CNT>=K         1   (one vocabulary-index lookup)
    PREF/EXT_VOTE  the number of stored descriptors referenced
"""
import hashlib

LEN_THRESHOLDS = tuple(range(7, 13))
CNT_THRESHOLDS = (1, 2, 3)
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("CNT>=%d" % K for K in CNT_THRESHOLDS)
            + ("PREF_VOTE", "EXT_VOTE"))
ORDER_MULT = 2654435761

_CONSTANT = frozenset(("C0", "C1"))
_LENGTH = frozenset("LEN<=%d" % L for L in LEN_THRESHOLDS)
_COUNT = frozenset("CNT>=%d" % K for K in CNT_THRESHOLDS)


def classify(name):
    """Structural class of a readout, read from the name alone."""
    if name in _CONSTANT:
        return "CONSTANT_ARM"
    if name in _LENGTH:
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name == "CNT>=1":
        return "STORED_EXEMPLAR_MEMBERSHIP"
    if name in _COUNT:
        return "STORED_EXEMPLAR_COUNT_THRESHOLD"
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return "NEIGHBORHOOD_MAJORITY_VOTE"
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
