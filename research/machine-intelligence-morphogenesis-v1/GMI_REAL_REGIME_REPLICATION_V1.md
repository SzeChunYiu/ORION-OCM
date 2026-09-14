# The first real-regime replication: a certificate where the corpus used a search

Date: 2026-09-14. Addresses checklist section **T. Real-scale transfer**, and the gap
`GMI_PROTOCOL_CONFORMANCE_AUDIT_V1.md` measured at **0 of 19**.
Witness: `gmi_microscope/real_regime_finite_state_witness.py`.
Receipt: `microscopes/results/STAGE_REAL_REGIME_FINITE_STATE_V1.json`.

The protocol audit counted how many of the nineteen derived families replicate at a real
regime and found **none**. This document moves one half of one family off that number, and
says precisely which half.

## 1  Why every family scored zero

The reason is uniform across the corpus and it is not carelessness: **every family's method
is an enumeration.** B2 proves minimality by enumerating all machines with `k` states and
showing none realizes the obligation. B4 searches a circuit space. B14 decides a census by
exhausting 512 relations. These methods are exact — which is what makes the corpus's numbers
trustworthy — and they die at the first order of magnitude.

For B2 the wall is explicit. The number of `k`-state machines over a two-letter alphabet with
a binary accept mask is `k^(2k) · 2^k`. At `k = 3` that is 5832. At `k = 10000` it is a number
with **83011 digits**.

## 2  The criterion, fixed before the measurement

A replication that merely runs a slow search faster is not a real-regime replication. The
criterion recorded in the witness, and in the receipt, before any number was produced:

> the small-scale method must be computationally **impossible** at this scale, not merely
> slow, and the certificate that replaces it must be **actually executed**.

Both quantities are in the receipt (`exhaustion_avoided`) so a reader can check the claim
instead of accepting the word "real":

| quantity | value |
|---|---:|
| states `N` | 10 000 |
| machines the enumeration would visit | 10^83010 |
| pair tests the certificate requires | 49 995 000 |
| pair tests actually executed | **49 995 000** |

## 3  What replaces the search

A fooling set is a **certificate**, not a search. A set of strings that are pairwise separated
by exhibited suffixes proves a lower bound directly, in `|F|(|F|−1)/2` pair tests, with no
machine ever enumerated.

The obligation is *accept iff the number of `b`s is divisible by N*. The fooling set is
`F = { bⁱ : i = 0 … N−1 }`, and the suffix exhibited for class `i` is `z(i) = b^(N−i)`:

* `bⁱ z(i)` has `i + (N−i) = N` occurrences — accepted;
* `bʲ z(i)` has `j + N − i` occurrences, and since `i ≠ j` with both in `[0, N)`, that is not
  `0 mod N` — rejected.

**The algebra is not what is being trusted.** For every one of the 49 995 000 pairs the witness
evaluates the obligation on both extended strings and checks that the verdicts differ.
`certificate.pairs_failed` is **0**.

## 4  The checker can reject — verified, not assumed

A pair test that accepts everything would pass section 3 while proving nothing. The witness
therefore runs a **mutation control**: it corrupts the suffix rule to `z(i) = b^(N−i−1)` and
re-runs the pair test on a 400-class probe.

That corrupted certificate fails to separate **79 401** pairs (`mutation_control`). So the test
demonstrably distinguishes a valid certificate from an invalid one, and passing it in section 3
is evidence rather than a formality.

## 5  What does *not* replicate, and why that is stated rather than buried

The small-scale B2 result is two-sided: a lower bound of `N` from the fooling set, and an upper
bound of `N` from an exhibited machine **verified correct by replaying every input**. At this
scale the upper bound is the weaker half.

| check | coverage | result |
|---|---|---|
| state sweep | all **10 000** states reached and labelled | 0 errors |
| exhaustive replay | every string of length ≤ 18 — **524 287** strings | 0 errors |
| states those strings can reach | **19** of 10 000 | — |

The sweep touches every state but feeds a single string. The replay covers every string up to
length 18, but such strings contain at most 18 `b`s and so reach only 19 states. Neither is
exhaustive replay over all inputs, which does not scale.

**So the upper bound rests on an argument** — that the transition is residue addition — **while
the lower bound rests on 49 995 000 executed checks.** The receipt records this as
`verdict.upper_bound_replicates = false`, and a CI pin fails if that ever silently flips.

## 6  The bound belongs to the obligation, not to the method

A certificate that inflates would produce a large bound for anything. The matched negative
control runs the same construction on *accept iff the string contains at least one `b`*, whose
Myhill–Nerode index is 2 at every length. The construction certifies **2**, against **10 000**
for the main obligation (`negative_control`).

## 7  What this changes

**It does not revise the `0 of 19`.** That number was true of the corpus as audited, and this is
the first movement away from it — not evidence that it was wrong. The honest statement is:

> For one family, the **lower-bound half** of the result now replicates at a scale where the
> original method is impossible. The upper-bound half does not, and no family has yet replicated
> both halves.

The generalizable part is the shape rather than the arithmetic: **wherever a family's small-scale
result is obtained by exhaustive search, ask whether a certificate exists for the same claim.**
Lower bounds often have one — fooling sets, adversary arguments, dimension counts. Upper bounds
usually do not, because exhibiting a construction is easy while verifying it everywhere is not.
That asymmetry predicts which halves of the corpus will scale and which will not, and it is
checkable against the other eighteen families.

## 8  Scope

One family, one obligation, one scale. `N = 10000`, alphabet `{a, b}`, exact integer arithmetic
throughout, no sampling. The lower bound is certified by exhaustive pairwise checking; the upper
bound is verified on all states and on every string up to length 18, which is not every input.
Runtime 32 s. The result says nothing about families whose native coordinate is not a state count.
