"""The readout grammar G_PGM of gmi-833-h-real-scale-probabilistic-graphical-v1.

Frozen by FREEZE_V1.md section 5, FREEZE_V1_SLICE_ADDENDUM.md (the two-factor
split, the readout language R, the charged-cost model) and
FREEZE_V1_SLICE_ADDENDUM_R2.md (R2.1-R2.7). Stdlib only. Exact integer
arithmetic throughout; no float enters any decision, count, comparison or
claim.

G_PGM is a family-blind language over the sha-bound bytes of the external
source D. A readout maps a held query descriptor q to a decision (0 or 1)
using only (a) the stored factor graph -- the descriptors at fit positions,
their per-factor occurrence counts and their per-factor continuation
fan-outs -- (b) the descriptor-closure vocabulary, (c) the query itself and
(d) the fit-slice majority label as the registered fallback. This module
receives no family name, no row name, no response values and no
family-specific candidate menu; structural class names are attached only by
classify(), which reads the readout name and nothing else.

The readout language, closed before any outcome, 54 arms:

    C0                     always 0
    C1                     always 1
    LEN<=L                 L = 6..12      1 iff len(q) <= L
    R1CNT>=K               K = 1..3       1 iff c1(q) >= K
    R2CNT>=K               K = 1..3       1 iff c2(q) >= K
    R1ASSOC>=K             K = 1..3       1 iff |A1(q)| >= K
    R2ASSOC>=K             K = 1..3       1 iff |A2(q)| >= K
    R1x&R2y                x in {R1CNT>=a, R1ASSOC>=a}, y in {R2CNT>=b,
                           R2ASSOC>=b}, a, b in {1,2} (16 arms)
                                           1 iff both conjuncts fire
    LEN<=L&R1ASSOC>=1&R2ASSOC>=1   L = 6..12  1 iff every conjunct fires
    LEN<=L&R1CNT>=1&R2CNT>=1       L = 6..12  1 iff every conjunct fires
    PREF_VOTE              majority stored label over the stored proper
                           prefixes q[:k], 2 <= k < len(q); an empty
                           neighbourhood reads the fit majority
    EXT_VOTE               majority stored label over the stored descriptors
                           extending q (descriptors of length > len(q));
                           an empty neighbourhood reads the fit majority
    MEM_FALLBACK           if q is stored, read out the STORED label of q --
                           the registered decision |A1(q)|>=1 AND |A2(q)|>=1
                           evaluated on q, the label the stored factor graph
                           records for its own descriptor; else the fit
                           majority

The constant-branch exclusion rule of the slice addendum excludes a
membership readout with a majority fallback whose stored branch reads out a
CONSTANT. Applied to this ecology it eliminates NOTHING: the only such arm,
MEM_FALLBACK, reads the STORED label of the query, which is two-valued over
any large fixed store, so it is admitted to the enumeration and must lose by
the winner rule (R2.6 registers the measured rejection).

The charged per-query cost (slice addendum section 6):
    C0 / C1 / a length-only arm                0
    a single factor-local condition, and the
    length-gated arms                          1   (one factor-local lookup)
    a product of one R1 condition with one R2
    condition (a joint arm)                    2   (one lookup per factor)
    MEM_FALLBACK                               2   (one membership lookup and
                                                   one stored-label read)
    PREF_VOTE / EXT_VOTE                       the number of stored
                                               descriptors referenced
"""
import hashlib

ORDER_MULT = 2654435761
LEN_THRESHOLDS = tuple(range(6, 13))
CNT_THRESHOLDS = (1, 2, 3)
ASSOC_THRESHOLDS = (1, 2, 3)
FACTOR_IDS = (1, 2)

# The registered readout language R, in the exact order of the slice addendum
# section 3: C0, C1, the 7 length arms, the 12 factor-local count arms, the 12
# factor-local fan-out arms, the 16 factor-product joint arms, the 4
# length-gated joint arms, PREF_VOTE, EXT_VOTE, MEM_FALLBACK.
READOUTS = (
    ("C0", "C1")
    + tuple("LEN<=%d" % L for L in LEN_THRESHOLDS)
    + tuple("R1CNT>=%d" % K for K in CNT_THRESHOLDS)
    + tuple("R2CNT>=%d" % K for K in CNT_THRESHOLDS)
    + tuple("R1ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)
    + tuple("R2ASSOC>=%d" % K for K in ASSOC_THRESHOLDS)
    + tuple("R1CNT>=%d&R2CNT>=%d" % (a, b)
            for a in (1, 2) for b in (1, 2))
    + tuple("R1CNT>=%d&R2ASSOC>=%d" % (a, b)
            for a in (1, 2) for b in (1, 2))
    + tuple("R1ASSOC>=%d&R2CNT>=%d" % (a, b)
            for a in (1, 2) for b in (1, 2))
    + tuple("R1ASSOC>=%d&R2ASSOC>=%d" % (a, b)
            for a in (1, 2) for b in (1, 2))
    + tuple("LEN<=%d&R1ASSOC>=1&R2ASSOC>=1" % L for L in LEN_THRESHOLDS)
    + tuple("LEN<=%d&R1CNT>=1&R2CNT>=1" % L for L in LEN_THRESHOLDS)
    + ("PREF_VOTE", "EXT_VOTE", "MEM_FALLBACK"))

# The registered two-factor split of the sha-bound token list.
FACTOR_SPLIT_RULE = ("R1 = the tokens of EVEN length (len(w) % 2 == 0); "
                     "R2 = the tokens of ODD length (len(w) % 2 == 1)")

# The registered charged-cost constants (slice addendum section 6).
ALPHABET_WIDTH = 27
SCAN_COST_MULT = 2

_CONSTANT = frozenset(("C0", "C1"))
_LENGTH_ONLY = frozenset("LEN<=%d" % L for L in LEN_THRESHOLDS)
_VOTE = frozenset(("PREF_VOTE", "EXT_VOTE"))


def conditions(name):
    """The conjuncts of a readout name, family-blind and name-only."""
    return tuple(name.split("&"))


def reads_both_factors(name):
    """True iff the name conjoins a factor-1 condition with a factor-2 one."""
    has1 = any(p.startswith("R1") for p in conditions(name))
    has2 = any(p.startswith("R2") for p in conditions(name))
    return bool(has1 and has2)


def classify(name):
    """Structural class of a readout, read from the name alone.

    Registered by the slice addendum section 3 and R2.1-R2.6: the classifier
    receives no response value, no count and no family name.
    """
    if name in _CONSTANT:
        return "CONSTANT_ARM"
    if name in _LENGTH_ONLY:
        return "DESCRIPTOR_LENGTH_THRESHOLD"
    if name in _VOTE:
        return "NEIGHBORHOOD_MAJORITY_VOTE"
    if name == "MEM_FALLBACK":
        return "STORED_LABEL_READ_WITH_FALLBACK"
    if reads_both_factors(name):
        return "FACTOR_JOINT_CONSISTENCY"
    if name.startswith("R1CNT>=") or name.startswith("R2CNT>="):
        return "SINGLE_FACTOR_MEMBERSHIP"
    if name.startswith("R1ASSOC>=") or name.startswith("R2ASSOC>="):
        return "SINGLE_FACTOR_ASSOCIATION"
    raise ValueError("readout outside the registered language: " + name)


def cost(name):
    """Registered charged per-query cost of a readout (slice addendum 6).

    PREF_VOTE / EXT_VOTE are charged the number of stored descriptors they
    reference, which is a per-query quantity and therefore returned as None
    here and accumulated by the scorer.
    """
    if name in _VOTE:
        return None
    if name == "MEM_FALLBACK":
        return 2
    if name in _CONSTANT:
        return 0
    if name in _LENGTH_ONLY:
        return 0
    if name.startswith("LEN<="):
        return 1
    if "&" in name:
        return 2
    return 1


def order_key(i):
    """The registered target-independent Knuth presentation key.

    key(i) = (i * 2654435761) mod 2**32; the descriptor list is sorted by this
    key (stable, ascending) before the arithmetic 7:1 slice. Registered by
    FREEZE_V1_SLICE_ADDENDUM.md section 1, unchanged by R2.1.
    """
    return (i * ORDER_MULT) % (2 ** 32)


def digest():
    """Stable digest of the frozen readout grammar and presentation lever.

    Over (the readout list, the presentation key, the factor split rule) --
    the three registered components of G_PGM. An extra readout, a perturbed
    key or a perturbed split rule must move this digest.
    """
    h = hashlib.sha256()
    h.update("+".join(READOUTS).encode())
    h.update(("key(i)=(i*%d) mod 2**32" % ORDER_MULT).encode())
    h.update(FACTOR_SPLIT_RULE.encode())
    return h.hexdigest()
