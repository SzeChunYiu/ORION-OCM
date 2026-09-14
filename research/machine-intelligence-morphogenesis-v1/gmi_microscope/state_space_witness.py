"""B9: compressed dynamical state, and when the update can be affine.

GMI_FINITE_STATE_DERIVATION_V1 established that the minimal number of states is
the quotient index, and that recurrent state beats carrying history once the
history exceeds |Q|. That leaves the question this family is actually about:
having got |Q| states, how cheaply can the UPDATE be written?

Derived here:

  1  the compressed state: |Q| distinctions in ceil(log2 |Q|) bits
  2  when the update is AFFINE in that encoding, searched exhaustively over
     every code assignment and every matrix -- and when no such realization
     exists at all
  3  the long-horizon regime against attention and against explicit memory
  4  neutral recovery in a long-sequence ecology, with no state-space macro

Exhaustive enumeration; exact integer arithmetic over GF(2).
"""

import itertools
import json

OUT = {}

SIGMA = ("a", "b")


# ---------------------------------------------------------------------------
# obligations, given as minimal DFAs (states, transition, accept)
# ---------------------------------------------------------------------------
def dfa_parity():
    """Even number of b. Two states, and the update is a flip on b."""
    delta = {(0, "a"): 0, (0, "b"): 1, (1, "a"): 1, (1, "b"): 0}
    return 2, delta, {0: True, 1: False}


def dfa_mod4():
    """Count of b modulo 4. Four states in a cycle."""
    delta = {}
    for q in range(4):
        delta[(q, "a")] = q
        delta[(q, "b")] = (q + 1) % 4
    return 4, delta, {q: (q == 0) for q in range(4)}


def dfa_ends_ab():
    """Ends with 'ab'. Four states, and the update is NOT a group action."""
    # 0 = nothing, 1 = saw a, 2 = saw ab, 3 = other
    delta = {
        (0, "a"): 1, (0, "b"): 3,
        (1, "a"): 1, (1, "b"): 2,
        (2, "a"): 1, (2, "b"): 3,
        (3, "a"): 1, (3, "b"): 3,
    }
    return 4, delta, {0: False, 1: False, 2: True, 3: False}


MACHINES = {"parity_b": dfa_parity, "count_b_mod4": dfa_mod4,
            "ends_with_ab": dfa_ends_ab}


def bits_for(n):
    b = 1
    while (1 << b) < n:
        b += 1
    return b


def as_vec(v, width):
    return tuple((v >> i) & 1 for i in range(width))


def affine_realizable(n, delta, width):
    """Is there a code assignment and, per symbol, a matrix A and bias c over
    GF(2) with code(delta(q,x)) = A code(q) + c ?

    Exhaustive over every injective code assignment and every matrix. This is
    the question the family turns on, and it is answered by search rather than
    by inspecting the transition table for structure.
    """
    codes_all = list(itertools.permutations(range(1 << width), n))
    mats = list(itertools.product([tuple(r) for r in
                                   itertools.product((0, 1), repeat=width)],
                                  repeat=width))
    biases = list(itertools.product((0, 1), repeat=width))

    def apply(A, c, v):
        return tuple((sum(A[i][j] * v[j] for j in range(width)) + c[i]) % 2
                     for i in range(width))

    for assign in codes_all:
        code = {q: as_vec(assign[q], width) for q in range(n)}
        ok = True
        for x in SIGMA:
            found = False
            for A in mats:
                for c in biases:
                    if all(apply(A, c, code[q]) == code[delta[(q, x)]]
                           for q in range(n)):
                        found = True
                        break
                if found:
                    break
            if not found:
                ok = False
                break
        if ok:
            return True, assign
    return False, None


print("=" * 78)
print("1-2  THE COMPRESSED STATE, AND WHETHER ITS UPDATE CAN BE AFFINE")
print("=" * 78)
print("  |Q| distinctions fit in ceil(log2 |Q|) bits. Whether the TRANSITION is")
print("  affine in that encoding is a separate question, answered by searching")
print("  every code assignment and every GF(2) matrix -- not by inspection.")
print()
print("  %-16s %-8s %-10s %-10s %s" % ("obligation", "|Q|", "one-hot", "bits", "affine update"))
rows = []
for name, mk in MACHINES.items():
    n, delta, _acc = mk()
    w = bits_for(n)
    ok, assign = affine_realizable(n, delta, w)
    rows.append({"obligation": name, "states": n, "one_hot": n, "bits": w,
                 "affine": ok})
    print("  %-16s %-8d %-10d %-10d %s" % (name, n, n, w, ok))
OUT["compression"] = rows

aff = [r["affine"] for r in rows]
assert any(aff) and not all(aff), (
    "every machine must not have the same answer -- if all are affine or none "
    "is, the search distinguishes nothing and the family has no content")
assert all(r["bits"] < r["one_hot"] or r["states"] <= 2 for r in rows), \
    "the binary encoding should be smaller than one-hot above two states"
yes = [r["obligation"] for r in rows if r["affine"]]
no = [r["obligation"] for r in rows if not r["affine"]]
print("\n  affine in log-space: %s" % ", ".join(yes))
print("  NOT affine at any code assignment: %s" % ", ".join(no))
print()
print("  > A compressed state is always available -- %d states always fit in"
      % rows[-1]["states"])
print("  > %d bits. An AFFINE update is not. The compression is a counting fact;"
      % rows[-1]["bits"])
print("  > the linear realization is a fact about the transition structure, and")
print("  > the search above separates the two.")
print()
print("  ends_with_ab is the instructive negative: it has the same state count")
print("  as the mod-4 counter and the same 2-bit encoding, yet NO assignment of")
print("  codes makes its update affine. Its transitions are not invertible --")
print("  several states go to the same successor on 'b' -- and an affine map")
print("  over GF(2) with a fixed matrix cannot merge states and still separate")
print("  them later.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("3  LONG HORIZON: STATE AGAINST ATTENTION AGAINST EXPLICIT MEMORY")
print("=" * 78)
print("  Per-step cost of answering after n symbols. A fixed state updates once")
print("  per symbol. Attention revisits every earlier symbol. Explicit memory")
print("  stores them all and looks one up.")
print()
print("  %-10s %-16s %-18s %-18s %s"
      % ("length n", "state (work)", "attention (work)", "memory (storage)", "cheapest work"))
hz = []
W = bits_for(4)
for n in (2, 4, 8, 16, 64):
    state_work, attn_work, mem_store = n, n * (n + 1) // 2, n
    cheapest = "state" if state_work <= attn_work else "attention"
    hz.append({"n": n, "state_work": state_work, "attention_work": attn_work,
               "memory_storage": mem_store, "state_storage": W,
               "cheapest_work": cheapest})
    print("  %-10d %-16d %-18d %-18d %s"
          % (n, state_work, attn_work, mem_store, cheapest))
OUT["horizon"] = hz
assert all(h["cheapest_work"] == "state" for h in hz), \
    "a fixed state should never do more work than revisiting the whole history"
assert hz[-1]["attention_work"] > 10 * hz[-1]["state_work"], \
    "the gap between linear and quadratic work has stopped growing"
print("\n  State storage stays at %d bits at every length; explicit memory grows" % W)
print("  to %d slots and attention's work grows quadratically." % hz[-1]["memory_storage"])
print()
print("  > The state-space advantage is not that it is cleverer. It is that a")
print("  > fixed state is the only one of the three whose cost does not grow")
print("  > with the horizon -- and it buys that by DISCARDING everything the")
print("  > quotient says is not needed, which is exactly what the other two")
print("  > decline to do.")
print()
print("  That is also the limit: where the obligation's quotient is infinite or")
print("  grows with n, there is no fixed state to compress into, and attention")
print("  or memory is not a worse choice but the only one. This witness does")
print("  not exhibit such an obligation, so that half is stated and not shown.")


# ---------------------------------------------------------------------------
print()
print("=" * 78)
print("4  NEUTRAL RECOVERY IN A LONG-SEQUENCE ECOLOGY")
print("=" * 78)
print("  Candidates are described by what they carry between symbols and what")
print("  they do per symbol. No state-space, recurrence or attention macro.")
print()
print("  %-10s %-26s %-16s %s" % ("length n", "carry w bits, O(1)/symbol", "carry all n", "cheapest"))
rec = []
for n in (2, 4, 8, 16, 64):
    fixed = W + n                      # w bits carried, one update per symbol
    carry_all = n + n * (n + 1) // 2   # store everything, revisit it
    cheapest = "fixed carry" if fixed < carry_all else "carry everything"
    rec.append({"n": n, "fixed": fixed, "carry_all": carry_all,
                "cheapest": cheapest})
    print("  %-10d %-26d %-16d %s" % (n, fixed, carry_all, cheapest))
OUT["recovery"] = rec
kinds = {r["cheapest"] for r in rec}
assert "fixed carry" in kinds, "a fixed carry is never selected"
short = rec[0]
assert short["n"] == 2, "expected the shortest sequence first"
print("\n  The cheapest shape at every length beyond the shortest carries a")
print("  FIXED number of bits and does constant work per symbol. That object --")
print("  a small state advanced once per input -- is a state-space model, and")
print("  it was selected by cost from a description that never names one.")
if len(kinds) == 1:
    print()
    print("  Note honestly: the fixed carry wins at EVERY length tested here, so")
    print("  this recovery shows what is selected rather than a crossover. A")
    print("  crossover would need an obligation whose quotient grows with n, and")
    print("  this witness does not construct one.")

print()
print("=" * 78)
print("all assertions held")
print("=" * 78)

with open("microscopes/results/STAGE_STATE_SPACE_V1.json", "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
