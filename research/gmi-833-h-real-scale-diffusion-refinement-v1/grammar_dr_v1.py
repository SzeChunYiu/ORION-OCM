"""The readout grammar G_DR of gmi-833-h-real-scale-diffusion-refinement-v1.

Frozen by FREEZE_V1.md section 5 and
FREEZE_V1_SLICE_ADDENDUM_H33_V1.md. Stdlib only. Exact integer arithmetic
throughout.

G_DR is a family-blind language over the sha-bound bytes of the external source
D. A readout maps a held query (a descriptor q of length >= 3 whose full-source
support presents at least two candidates, together with the presented candidate
c(q) of FREEZE_V1.md section 4) to a decision (0 or 1) using only (a) the
stored candidate set S_store(q) of the slice, (b) the registered alphabet order
and its successor sigma, (c) the descriptor q and its slice occurrence count,
and (d) the fit-slice majority label as the registered fallback.

No readout reads the labeller's support set S_full or the refinement index r:
those are labeller-only quantities. A readout may take a refinement step
through the STORE's own candidate set, which is a strict sub-table of the full
set and is a different quantity.

The readout language, closed before any outcome:

    C0 / C1          constants
    LEN<=L           L = 6..12      1 iff len(q) <= L
    CNT>=K           K = 1..3       1 iff q occurs >= K times among the
                                    slice's positions
    CARD>=K          K = 1..4       1 iff |S_store(q)| >= K
    REFINE<=k                        1 iff CARD >= 1 and walk(S_store, c) <= k
    REFINE>=k                        1 iff CARD >= 1 and walk(S_store, c) >= k
    REFINEIN<=k      k = 1..3        1 iff CARD >= 2 and walk(S_store, c) <= k
    DRAW>=K          K = 1..4        1 iff CARD >= 2 and the forward registered
                                    step distance to the nearest stored
                                    candidate is >= K
    DRAW0                            1 iff CARD >= 1 and walk(S_store, c) == 0
    MEM_FALLBACK     the registered label FORM evaluated on the store's own
                                    table if q is stored, else the fit majority

The step-index ladder is the registered base ladder unioned with the registered
T* of FREEZE_V1.md section 4 (addendum, "one registered meta-rule of the
ladder's construction"); readouts(extra) builds it, and the digest covers
whatever ladder is passed in.

Structural classes (post-hoc, read from the name alone):
    CONSTANT_ARM / DESCRIPTOR_LENGTH_THRESHOLD / STORE_MEMBERSHIP_COUNT
    REFINEMENT_INDEX / SINGLE_DRAW_SOURCE / STORED_LABEL_READ_WITH_FALLBACK

Charged per-query cost (slice addendum, charged-cost model):
    C0/C1/LEN        0
    CNT/CARD/REFINE/DRAW0/DRAW>=   1
    MEM_FALLBACK     2
"""
import hashlib

LEN_THRESHOLDS = (6, 7, 8, 9, 10, 11, 12)
CNT_THRESHOLDS = (1, 2, 3)
CARD_THRESHOLDS = (1, 2, 3, 4)
REFINE_BASE = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 256)
REFINEIN_THRESHOLDS = (1, 2, 3)
DRAW_THRESHOLDS = (1, 2, 3, 4)

ORDER_MULT = 2654435761
ALPHABET_WIDTH = 27          # the registered alphabet-array constant
STEP_CAP = 256               # the registered cap on the refinement walk

_REFINE_PREFIXES = ("REFINE<=", "REFINE>=", "REFINEIN<=")


def ladder(extra=()):
    """The registered step-index ladder, unioned with the registered T*."""
    return tuple(sorted(set(REFINE_BASE) | set(extra)))


def readouts(extra=()):
    lad = ladder(extra)
    return (("C0", "C1")
            + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
            + tuple("CNT>=%d" % K for K in CNT_THRESHOLDS)
            + tuple("CARD>=%d" % K for K in CARD_THRESHOLDS)
            + tuple("REFINE<=%d" % k for k in lad)
            + tuple("REFINE>=%d" % k for k in lad)
            + tuple("REFINEIN<=%d" % k for k in REFINEIN_THRESHOLDS)
            + tuple("DRAW>=%d" % k for k in DRAW_THRESHOLDS)
            + ("DRAW0", "MEM_FALLBACK"))


READOUTS = readouts()


def classify(name):
    """Structural class of a readout, read from the name alone."""
    if name in ("C0", "C1"):
        return "CONSTANT_ARM"
    if name.startswith("LEN<="):
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name.startswith(("CNT>=", "CARD>=")):
        return "STORE_MEMBERSHIP_COUNT"
    if name.startswith(_REFINE_PREFIXES):
        return "REFINEMENT_INDEX"
    if name == "DRAW0" or name.startswith("DRAW>="):
        return "SINGLE_DRAW_SOURCE"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    raise ValueError("readout outside the registered language: " + name)


def cost(name):
    if name in ("C0", "C1") or name.startswith("LEN<="):
        return 0
    if name == "MEM_FALLBACK":
        return 2
    if name in READOUTS:
        return 1
    raise ValueError("readout outside the registered language: " + name)


def order_key(i):
    """The registered target-independent Knuth presentation key."""
    return (i * ORDER_MULT) % (2 ** 32)


def digest(arms=None):
    """Stable digest of the frozen readout grammar and presentation lever."""
    arms = READOUTS if arms is None else tuple(arms)
    h = hashlib.sha256()
    h.update("+".join(arms).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    h.update(("cap=%d" % STEP_CAP).encode())
    return h.hexdigest()
