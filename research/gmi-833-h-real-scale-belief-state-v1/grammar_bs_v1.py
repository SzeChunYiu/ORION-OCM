"""The readout grammar G_BS of gmi-833-h-real-scale-belief-state-v1.

Frozen by FREEZE_V1.md section 5 and FREEZE_V1_SLICE_ADDENDUM_H17_V1.md.
Stdlib only. Exact integer arithmetic throughout.

G_BS is a family-blind language over the sha-bound bytes of the external
source D. A readout maps a held query (a closure position whose descriptor q
is a context) to a decision (0 or 1) using only (a) the set-valued stored
word-hypothesis table of the slice -- the whole source words having q as a
proper prefix, with evidence weight len(w) -- (b) the descriptor-closure
vocabulary, (c) the query itself and (d) the fit-slice majority label as the
registered fallback. This module receives no family name, no row name, no
response values and no family-specific candidate menu; structural class names
are attached only by classify(), which reads the readout name and nothing
else.

The readout language, closed before any outcome:

    C0 / C1          constants
    LEN<=L           L = 6..12      1 iff len(q) <= L
    CNT>=K           K = 1..3       1 iff the closure position q occurs >= K
                                    times among the slice's positions
    EXT>=K           K = 1..4       1 iff EXT(q) >= K, the raw stored-hypothesis
                                    count (the sibling's cue-association arm)
    WSUM>=T          T = 8..64      1 iff SUM(q) >= T
    WMAX>=T          T = 7..16      1 iff EXT(q) >= 1 and MAX(q) >= T
    WAVG>=T          T = 6..12      1 iff EXT(q) >= 1 and SUM >= T * EXT(q)
    WDOM>=a          a = 3..12      1 iff EXT(q) >= 2 and a * MAX >= SUM
    WPAIR>=a_T       a = 3..12, T = 6..12
                                    1 iff EXT(q) >= 2 and a * MAX >= SUM
                                    and MAX >= T
    MEM_FALLBACK     stored label of q if the position is stored, else the fit
                                    majority

where EXT/SUM/MAX are the stored aggregates of the slice:
    EXT(q) = |{w stored : len(q) < len(w), w starts with q}|
    SUM(q) = sum of len(w) over those w
    MAX(q) = max of len(w) over those w

The constant-branch exclusion rule: a membership readout with a majority
fallback whose stored branch reads out a CONSTANT would be excluded, because
on a held query its stored branch cannot separate. Applied here the rule
eliminates nothing: MEM_FALLBACK's stored branch reads the STORED POSTERIOR of
the query under the slice's own table, which is two-valued over any large
store, so it is admitted and must lose by the data. It does not lose on the
full held set at this ecology's label -- the registered falsifier 2 fires
there, and the boundary is reported -- which is precisely why the rule is
registered rather than applied as an exclusion.

Charged per-query cost (slice addendum, charged-cost model):
    C0/C1/LEN        0
    CNT>=K/EXT>=K/WSUM>=T/WMAX>=T/WAVG>=T/WDOM>=a/WPAIR>=a_T   1
    MEM_FALLBACK     2
"""
import hashlib

LEN_THRESHOLDS = tuple(range(6, 13))
CNT_THRESHOLDS = (1, 2, 3)
EXT_THRESHOLDS = (1, 2, 3, 4)
WSUM_THRESHOLDS = (8, 12, 16, 20, 24, 32, 48, 64)
WMAX_THRESHOLDS = (7, 8, 9, 10, 11, 12, 14, 16)
WAVG_THRESHOLDS = (6, 7, 8, 9, 10, 12)
WDOM_AS = (3, 4, 5, 6, 8, 10, 12)
WPAIR_PAIRS = tuple((a, t) for a in (3, 4, 5, 6, 8, 10, 12)
                    for t in (6, 7, 8, 9, 10, 12))

READOUTS = (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("CNT>=%d" % K for K in CNT_THRESHOLDS)
            + tuple("EXT>=%d" % K for K in EXT_THRESHOLDS)
            + tuple("WSUM>=%d" % T for T in WSUM_THRESHOLDS)
            + tuple("WMAX>=%d" % T for T in WMAX_THRESHOLDS)
            + tuple("WAVG>=%d" % T for T in WAVG_THRESHOLDS)
            + tuple("WDOM>=%d" % a for a in WDOM_AS)
            + tuple("WPAIR>=%d_%d" % (a, t) for a, t in WPAIR_PAIRS)
            + ("MEM_FALLBACK",))

ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27
LABEL_T_STAR = 8          # modal source-token length of the bound source

_WEIGHTED_PREFIXES = ("WSUM>=", "WMAX>=", "WAVG>=", "WDOM>=", "WPAIR>=")


def is_weighted(name):
    return name.startswith(_WEIGHTED_PREFIXES)


def classify(name):
    """Structural class of a readout, read from the name alone."""
    if name in ("C0", "C1"):
        return "CONSTANT_ARM"
    if name.startswith("LEN<="):
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name.startswith("CNT>="):
        return "STORE_MEMBERSHIP_COUNT"
    if name.startswith("EXT>="):
        return "EXTENSION_COUNT"
    if name.startswith(_WEIGHTED_PREFIXES):
        return "WEIGHTED_EVIDENCE_BELIEF"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def cost(name):
    if name in ("C0", "C1") or name.startswith("LEN<="):
        return 0
    if name == "MEM_FALLBACK":
        return 2
    if name.startswith(("CNT>=", "EXT>=")) or is_weighted(name):
        return 1
    raise ValueError("readout outside the registered language: " + name)


def order_key(i):
    """The registered target-independent Knuth presentation key."""
    return (i * ORDER_MULT) % (2 ** 32)


def digest():
    """Stable digest of the frozen readout grammar and presentation lever."""
    h = hashlib.sha256()
    h.update("+".join(READOUTS).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    h.update(("T*=%d" % LABEL_T_STAR).encode())
    return h.hexdigest()
