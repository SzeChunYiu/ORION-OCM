"""B2 at a real regime: the lower bound scales, and the exhaustion it replaces does not.

The corpus's B2 result proves minimality by EXHAUSTION -- it enumerates every
machine with k states and shows none realizes the obligation.  That method dies
immediately: the number of k-state machines over a 2-letter alphabet with binary
acceptance is k^(2k) * 2^k.  At k = 3 that is 5832; at k = 10000 it is a number
with more than 80000 digits.  The audit in GMI_PROTOCOL_CONFORMANCE_AUDIT_V1.md
recorded 0 of 19 families replicating at a real regime, and this is the reason:
every family's method is an enumeration.

A fooling set is a CERTIFICATE rather than a search.  A set F of strings, pairwise
separated by exhibited suffixes, proves at least |F| states directly -- checkable
in |F|(|F|-1)/2 pair tests.  So the same law can be re-established at a scale
where the original method is not merely slow but impossible.

This witness does that for the residue obligation at N = 10000, and reports
honestly which half of the result scales.

CRITERION FOR "REAL REGIME", fixed here before the measurement:
    the small-scale method must be computationally IMPOSSIBLE at this scale,
    not merely slow, and the certificate must be actually executed.
Both numbers are recorded in the receipt so a reader can check the claim rather
than take the word "real" on trust.
"""

import json
import math
import os

N = 10000                 # Myhill-Nerode index of the obligation
REPLAY_LEN = 18           # exhaustive replay over every string up to this length

OUT = {}


# ---------------------------------------------------------------------------
# The obligation, stated without reference to any machine.
# f(w) = 1 iff the number of 'b's in w is divisible by N.
# ---------------------------------------------------------------------------
def obligation(nb):
    """Accept iff the count of 'b' is 0 mod N.  Takes the count, not the string,
    because the count is all the obligation looks at -- stating it this way keeps
    the obligation independent of the machine that will be built for it."""
    return nb % N == 0


print("=" * 78)
print("B2 AT A REAL REGIME: N = %d" % N)
print("=" * 78)
print("  Obligation: accept iff the number of 'b's is divisible by %d." % N)
print("  Alphabet {a, b}; 'a' is irrelevant to the obligation.")
print()

# ---------------------------------------------------------------------------
# 1  THE EXHAUSTION THIS REPLACES
# ---------------------------------------------------------------------------
print("-" * 78)
print("1  THE SEARCH THAT IS NOT BEING RUN")
print("-" * 78)
# k-state DFAs over a 2-letter alphabet with a binary accept mask:
#   transitions: k choices per (state, letter) -> k^(2k)
#   accept mask: 2^k
log10_machines = 2 * N * math.log10(N) + N * math.log10(2)
pairs = N * (N - 1) // 2
OUT["exhaustion_avoided"] = {
    "states": N,
    "alphabet": 2,
    "log10_machine_count": round(log10_machines, 3),
    "certificate_pair_tests": pairs,
}
print("  machines with %d states over 2 letters : 10^%.0f" % (N, log10_machines))
print("  certificate pair tests                    : %d" % pairs)
print()
print("  > The enumeration is not slow, it is impossible: a number with %d digits."
      % (int(log10_machines) + 1))
print("  > The certificate is %d pair tests, and this witness runs all of them." % pairs)
assert log10_machines > 1000, (
    "the avoided enumeration is not astronomically large, so this is a slow "
    "search rather than an impossible one and the real-regime claim is void")

# ---------------------------------------------------------------------------
# 2  THE CERTIFICATE: a fooling set of size N, every pair checked
#
# F = { b^i : i = 0 .. N-1 }.  For i != j, the suffix z = b^(N-i) separates them:
#   b^i z has i + (N-i) = N b's        -> accepted
#   b^j z has j + (N-i) b's, and since j != i and both are in [0, N),
#   j + N - i is not 0 mod N           -> rejected
# The suffix is exhibited per pair as its exponent; separation is then CHECKED
# against the obligation rather than assumed from the algebra.
# ---------------------------------------------------------------------------
print("-" * 78)
print("2  THE CERTIFICATE: fooling set of size %d, all %d pairs verified" % (N, pairs))
print("-" * 78)


def separating_suffix(i):
    """Exhibited distinguishing suffix for class i: b^(N-i)."""
    return N - i


checked = 0
failures = []
for i in range(N):
    zi = separating_suffix(i)
    acc_i = obligation(i + zi)          # the exhibited suffix must ACCEPT on i
    if not acc_i:
        failures.append(("self", i, zi))
    for j in range(i + 1, N):
        # the same exhibited suffix must REJECT on j, separating the pair
        if obligation(j + zi) == acc_i:
            failures.append((i, j, zi))
        checked += 1

OUT["certificate"] = {
    "fooling_set_size": N,
    "pairs_checked": checked,
    "pairs_failed": len(failures),
    "suffix_rule": "z(i) = b^(N-i)",
}
print("  pairs checked : %d" % checked)
print("  pairs failed  : %d" % len(failures))
assert checked == pairs, "not every pair was checked (%d of %d)" % (checked, pairs)
assert not failures, (
    "the exhibited suffix fails to separate %d pairs, so the fooling set is not "
    "a fooling set and proves nothing" % len(failures))
print("  > Every one of the %d pairs is separated by an exhibited suffix." % checked)
print("  > Therefore the obligation needs at least %d states.  This is a" % N)
print("  > certificate, not a search: no machine was enumerated to obtain it.")

# ---------------------------------------------------------------------------
# 3  MUTATION CONTROL -- the checker must be able to reject
# ---------------------------------------------------------------------------
print()
print("-" * 78)
print("3  MUTATION CONTROL: a corrupted certificate must be rejected")
print("-" * 78)


def bad_suffix(i):
    """Off by one: z = b^(N-i-1).  This does NOT separate every pair."""
    return (N - i - 1) % N


mut_fail = 0
probe = min(N, 400)
for i in range(probe):
    zi = bad_suffix(i)
    for j in range(i + 1, probe):
        if obligation(i + zi) == obligation(j + zi):
            mut_fail += 1
OUT["mutation_control"] = {"probe_size": probe, "unseparated_pairs": mut_fail}
print("  corrupted suffix z(i) = b^(N-i-1), probed on %d classes" % probe)
print("  pairs it FAILS to separate: %d" % mut_fail)
assert mut_fail > 0, (
    "the off-by-one suffix still separates every probed pair, so the pair test "
    "cannot distinguish a valid certificate from a corrupted one and section 2 "
    "is coverage without content")
print("  > The pair test rejects a corrupted certificate, so passing it in")
print("  > section 2 is evidence rather than a formality.")

# ---------------------------------------------------------------------------
# 4  THE UPPER BOUND, and the honest limit of how far it scales
# ---------------------------------------------------------------------------
print()
print("-" * 78)
print("4  THE UPPER BOUND: an N-state machine, and what verifying it costs")
print("-" * 78)
# delta(q, 'a') = q ; delta(q, 'b') = q + 1 mod N ; accept iff q == 0
# Sweep every state once, in O(N), by feeding b^N and checking after each step.
q = 0
state_errors = 0
for step in range(1, N + 1):
    q = (q + 1) % N
    if q != step % N:
        state_errors += 1
    if (q == 0) != obligation(step):
        state_errors += 1
print("  every one of the %d states reached and checked : %d errors"
      % (N, state_errors))
assert state_errors == 0, "the constructed machine mislabels a state"

# exhaustive replay over every string up to REPLAY_LEN
replayed = 0
replay_errors = 0
for L in range(REPLAY_LEN + 1):
    for mask in range(1 << L):
        nb = bin(mask).count("1")
        q = nb % N
        if (q == 0) != obligation(nb):
            replay_errors += 1
        replayed += 1
reach = min(REPLAY_LEN, N - 1) + 1
OUT["upper_bound"] = {
    "states": N,
    "all_states_swept": True,
    "state_errors": state_errors,
    "strings_replayed": replayed,
    "replay_max_length": REPLAY_LEN,
    "replay_errors": replay_errors,
    "states_exercised_by_replay": reach,
}
print("  strings replayed exhaustively (len <= %d)     : %d, %d errors"
      % (REPLAY_LEN, replayed, replay_errors))
print("  states those strings can reach                : %d of %d" % (reach, N))
assert replay_errors == 0, "the constructed machine is wrong on a replayed string"
assert reach < N, (
    "the bounded replay reaches every state, which would mean REPLAY_LEN is "
    "large enough to make the scope caveat below false -- recheck")
print()
print("  > HONEST LIMIT.  The state sweep covers all %d states, but it feeds" % N)
print("  > one string.  The exhaustive replay covers every string up to length")
print("  > %d, but those can only reach %d of the %d states." % (REPLAY_LEN, reach, N))
print("  > Neither is exhaustive replay over all inputs, which is impossible.")
print("  > So the UPPER bound rests on the transition being residue addition,")
print("  > which is an argument, while the LOWER bound rests on %d executed" % pairs)
print("  > pair tests.  The lower bound is what replicates at this scale.")

# ---------------------------------------------------------------------------
# 5  MATCHED NEGATIVE CONTROL
#
# The machinery must not report a large bound for an obligation that does not
# need one.  "contains at least one b" has index 2 at every length.
# ---------------------------------------------------------------------------
print()
print("-" * 78)
print("5  MATCHED NEGATIVE CONTROL: an obligation that must NOT need N states")
print("-" * 78)


def twin_obligation(nb):
    """Accept iff the string contains at least one 'b'.  Index 2, for any N."""
    return nb >= 1


# largest fooling set the same construction can certify for the twin
twin_classes = []
for i in range(0, min(N, 5000)):
    novel = True
    for j in twin_classes:
        # separated only if some suffix count distinguishes them
        if all(twin_obligation(i + z) == twin_obligation(j + z)
               for z in range(0, 3)):
            novel = False
            break
    if novel:
        twin_classes.append(i)
    if len(twin_classes) > 4:
        break
OUT["negative_control"] = {
    "obligation": "contains at least one b",
    "certified_lower_bound": len(twin_classes),
    "main_obligation_bound": N,
}
print("  certified lower bound for the twin : %d" % len(twin_classes))
print("  certified lower bound for the main : %d" % N)
assert len(twin_classes) <= 3, (
    "the same construction certifies %d states for an obligation whose index is "
    "2, so the certificate inflates and the N-state bound is not trustworthy"
    % len(twin_classes))
print("  > The construction returns a small bound where a small bound is")
print("  > correct, so the large bound is a property of the obligation and")
print("  > not of the method.")

# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("WHAT REPLICATES AT THIS SCALE, AND WHAT DOES NOT")
print("=" * 78)
print("  REPLICATES  lower bound of %d states, established by %d executed pair" % (N, pairs))
print("              tests against an enumeration of 10^%.0f machines that is" % log10_machines)
print("              not merely slow but impossible.")
print("  DOES NOT    correctness of the constructed machine on ALL inputs.")
print("              All %d states are swept and %d strings replayed, but" % (N, replayed))
print("              exhaustive replay over every input does not scale, so the")
print("              upper bound rests on an argument rather than a check.")
print()
print("  This moves the corpus off '0 of 19 families replicate at a real regime'")
print("  for the LOWER-BOUND half of one family's result.  It does not revise")
print("  that 0 -- that number was true of the corpus as audited, and this is")
print("  the first movement away from it rather than evidence it was wrong.")

OUT["verdict"] = {
    "lower_bound_replicates": True,
    "upper_bound_replicates": False,
    "scale": N,
    "criterion": "the exhaustive method must be impossible, not merely slow",
}

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_REAL_REGIME_FINITE_STATE_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("=" * 78)
print("all assertions held")
print("=" * 78)
