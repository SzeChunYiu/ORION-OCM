"""The readout grammar G_DT of gmi-833-h-real-scale-decision-trees-v1.

Frozen by FREEZE_V1.md section 5, FREEZE_V1_SLICE_ADDENDUM.md (the readout
language R) and FREEZE_V1_SLICE_ADDENDUM_R2.md (R2.1-R2.4). Stdlib only.
Exact integer arithmetic throughout.

G_DT is a family-blind language over the sha-bound bytes of the external
source D. A readout maps a held query descriptor q to a decision (0 or 1)
using only (a) the stored-context rule table -- the descriptors at fit
positions, their membership counts and their trie fan-outs -- (b) the
descriptor-closure vocabulary, (c) the query itself and (d) the fit-slice
majority label as the registered fallback. This module receives no family
name, no row name, no response values and no family-specific candidate menu;
structural class names are attached only by classify(), which reads the
readout name and nothing else.

The readout language, closed before any outcome:

    C0           always 0
    C1           always 1
    LEN<=L       L = 6..12           1 iff len(q) <= L
    CNT>=K       K = 1..3            1 iff cnt(q) >= K, where cnt(q) is the
                                     number of stored descriptors equal to q
    ASSOC>=K     K = 1..3            1 iff |A(q)| >= K, where A(q) is the set
                                     of distinct letters stored immediately
                                     after q among stored descriptors of
                                     length >= 3
    LEN<=L&CNT>=j  L = 6..12, j = 1..3   1 iff both conjuncts fire
    LEN<=L&ASSOC>=j L = 6..12, j = 1..3  1 iff both conjuncts fire
    PREF_VOTE    majority label over stored proper prefixes q[:k],
                 2 <= k < len(q); empty -> fit majority
    EXT_VOTE     majority label over stored descriptors extending q
                 (descriptors of words starting with q of length > len(q));
                 empty -> fit majority
    MEM_FALLBACK if q is stored, read out the STORED label of q
                 (the registered decision len(q)<=9 AND source-count(q)>=2
                 evaluated on q -- the label the stored rule table records);
                 else the fit majority

The constant-branch exclusion rule of the slice addendum: a membership
readout with a majority fallback whose stored branch reads out a constant is
excluded from the enumeration (semantically constant on held). Applied to
this ecology the rule eliminates NOTHING: the only such arm, MEM_FALLBACK,
reads the STORED label of the query, which is two-valued over any large fixed
store, so it is admitted and must lose by the data (it does, at the rank
stage; the winner rule rejects it).

The charged per-query cost (FREEZE_V1_SLICE_ADDENDUM_R2.md R2.3):
    C0/C1/LEN      0
    CNT>=K / ASSOC>=K / a conjunction   1   (one stored-context lookup)
    MEM_FALLBACK   2   (one membership lookup and one stored-label read)
    PREF/EXT_VOTE  the number of stored descriptors referenced
"""
import hashlib

LEN_THRESHOLDS = tuple(range(6, 13))
CNT_THRESHOLDS = (1, 2, 3)
ASSOC_THRESHOLDS = (1, 2, 3)
READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("CNT>=%d" % K for K in CNT_THRESHOLDS)
            + tuple("ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)
            + tuple("LEN<=%d&CNT>=%d" % (L, j)
                    for L in LEN_THRESHOLDS for j in CNT_THRESHOLDS)
            + tuple("LEN<=%d&ASSOC>=%d" % (L, j)
                    for L in LEN_THRESHOLDS for j in ASSOC_THRESHOLDS)
            + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK"))
ORDER_MULT = 2654435761

_CONSTANT = frozenset(("C0", "C1"))
_LENGTH = frozenset("LEN<=%d" % L for L in LEN_THRESHOLDS)
_CONJ = frozenset(r for r in READOUTS if "&" in r)


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
    if name in ("PREF_VOTE", "EXT_VOTE"):
        return "NEIGHBORHOOD_MAJORITY_VOTE"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
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
