# AE3 theorems v1

Claim ceiling
`GMI_833_AE3_COMPRESSION_NOTIONS_SEPARATED_FROM_LEARNING_ON_A_REGISTERED_FINITE_CODING_LANGUAGE_FAMILY`.
Freeze `eddae65b3f1b3116a3502b65e916a48b165eae7b`; source main
`349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`.

## 0. Registered objects

Domain `X = {0,1}^3` uniform; target `Y = f(X)`; census = all `256` targets.
Training set `S0 = { x : x2 = 0 }`; held-out set its complement.

A **coding language** is the program set
`{ rule_i } ∪ { ¬rule_i } ∪ { rule_i XOR rule_j } ∪ { literal tables }` over a
registered 16-function rule basis, with integer code lengths `(a, b, c, d)`.
Kraft feasibility `16·2^-a + 16·2^-b + 256·2^-c + 256·2^-d ≤ 1` is checked with
exact `Fraction`. `L1 = (6,7,11,9)` and `L2 = (5,7,11,10)` are both Kraft-tight
(sum exactly `1`). `L3` is a run-length code: `4 + 4·runs`, literal fallback `9`.

`K_L(t)` is the minimum code length of a program whose output table is `t`. It
is computable by exhaustive enumeration over a finite program set. **It is not
`K` and is not an estimate of `K`.**

## 1. AE3-1 — the three notions are pairwise non-equivalent

- `A(t) = K_L(t)` — lossless description compression.
- `B(t) = min { k : some k-junta attains task accuracy ≥ 3/4 }` — task-relevant
  lossy compression, a rate at fixed distortion.
- `C(t) = min { K_L(h) : h attains out-of-sample accuracy 1 }` — model /
  generalization compression.

**Statement.** For every ordered pair `(P, Q)` of distinct notions there exist
targets with `P` equal and `Q` different. Exhaustively over the 256-target
census:

| pair | equal-value pairs | conflicting |
|---|---:|---:|
| `A → B` | 25,636 | **17,406** |
| `A → C` | 25,636 | **14,258** |
| `B → A` | 10,280 | **2,050** |
| `B → C` | 10,280 | **5,568** |
| `C → A` | 15,232 | **3,854** |
| `C → B` | 15,232 | **10,520** |

**Falsifier.** Any pair with `0` conflicts. **Forbidden extrapolation.** That
the notions are unrelated — `C ≤ A` always holds, since the target itself is a
perfect generalizer; the claim is non-equivalence, not independence.

## 2. AE3-2 — equal compression, opposite usefulness

Task `Y = x1 XOR x2`. Corpora `O = x0` and `O = x1 XOR x2` both code to `6` bits
in `L1` against a `9`-bit literal. The representation each induces is the map
`x ↦ O(x)`; the best predictor measurable with respect to it attains `1/2`
(exactly the blind baseline) in the first case and `1` in the second.

Compression is therefore not evidence of task usefulness even at identical
compression ratio on the same task.

## 3. AE3-3 — a useful predictor is not the shortest description

Target `01111000` (indexed `x = x0 + 2x1 + 4x2`). The shortest program
consistent with `S0` costs `6` bits, its argmin is a **singleton** (so no tie is
being hidden), and its out-of-sample accuracy is exactly `0`. The shortest
program that generalizes perfectly costs `7` bits. Length excess `1`;
generalization gap `1`.

**Scope.** This is language-relative by construction, and AE3-8 measures exactly
how relative.

## 4. AE3-4 — memorization does not determine generalization

For `Y = x0 AND x1` there are exactly `16` hypotheses with perfect training
accuracy on `S0`; their out-of-sample accuracies are `{0, 1/4, 1/2, 3/4, 1}`.
The 9-bit memoriser scores `1/2`; a 6-bit rule scores `1`. Over the whole census
of (target, consistent hypothesis) pairs, `6,094,848` of `8,386,560`
equal-training-accuracy pairs differ out of sample.

This is an exact finite instance of the no-free-lunch situation, not a new
theorem.

## 5. AE3-5 — MDL and Bayes, with the parent theorems subtracted

Two-part code `L(h) + 3·errors(h)` and a Bayes posterior with prior
`2^-K_L(h)` and likelihood `2^-errors(h)`, all exact. On `Y = x0 AND x1` the MDL
argmin has `2` members at `6` bits — `x0 AND x1` and `maj` — with out-of-sample
accuracies `1` and `1/2`. So the MDL argmin is **not** contained in the risk
argmax and MDL can select a strictly worse hypothesis. The MAP argmax behaves
identically.

The crosswalk maps four parents with citations and states explicitly that the
Occam direction (short consistent hypotheses generalize) is **parent-owned and
not claimed here**, and that the PAC-Bayes bound is transcendental and is never
evaluated.

## 6. AE3-6 — the Kolmogorov boundary, enforced not asserted

`K` is uncomputable and only upper semi-computable; the invariance theorem fixes
it only up to a machine-dependent additive constant. Consequently
`KOLMOGOROV_COMPLEXITY_COMPUTED`, `GMI_COMPUTES_TRUE_SHORTEST_PROGRAM` and
`UNIVERSAL_MACHINE_INVARIANCE_PROVED` are registered forbidden promotions.

The prohibition is **machine-checked**: `uncomputable_quantity_guard` walks the
emitted receipt and flags any field asserting the value of an uncomputable
quantity. It reports `0` alarms on this receipt and detects `2 of 2` planted
claims, so both recall and the no-alarm case are demonstrated on the real
artifact.

## 7. AE3-7 — computable surrogates and their language dependence

Three surrogates: `K_L1`, `K_L2` (both Kraft-tight prefix codes) and the
run-length `K_L3`. Measured exactly over the 256 targets:

- `|K_L1 − K_L2| ≤ 1`, attained on `242` targets, `0` on `14`;
- `0` strict order flips among all `32,640` target pairs — the two rule-based
  languages induce the same ordering, differing only in absolute values;
- `|K_L1 − K_L3| ≤ 3` — the structurally different code moves further.

## 8. AE3-8 — the actually justified invariance boundary

**The unqualified claim is refused.** Over `200` Kraft-feasible independent regenerations of the
code-length vector (the row's own word is `remints`) drawn from `[4,12]^4`:

- **AE3-2** holds on exactly `162`, and its boundary is the exact predicate
  `min(rule_len, xor_len) < literal_len`, which matches observation on
  `200 of 200`. (A rule table lies in the rule set and in the XOR set — it is
  `rule XOR const0` — but not in the negation set, which is why the predicate
  omits `b`.)
- **AE3-3** holds on only `170 of 200`; all `30` exceptions are enumerated in
  the receipt rather than averaged away.
- **AE3-4** is language-independent by construction: neither training nor
  out-of-sample accuracy references a code length.

An extreme code `(1,1,1,1)` with Kraft sum `272` destroys AE3-3 outright; it is
caught by the Kraft guard, so the extreme counterexample lies outside the prefix
code family while the `30` genuine exceptions lie inside it. **The honest
boundary is therefore narrower than "all prefix codes", and that is what the
verdict `INVARIANCE_IS_CONDITIONAL_NOT_UNIVERSAL` records.**

## 9. Two routes

Route A decides code lengths structurally by membership tests against the rule
basis. Route B (`independent_code_oracle_v1.py`) materialises every program of
the language as an explicit `(table, length)` pair and minimises by enumeration;
it rebuilds the rule basis from its own boolean definitions and recomputes every
accuracy by direct counting. The two agree on every table in every registered
language, on Kraft sums, on shortest-consistent argmin sets, on notion `B`, on
out-of-sample accuracies and on run counts.

## 10. Hostiles and nulls

| id | perturbation | moves its quantity | detected |
|---|---|---|---|
| `H1_rule_basis_tamper` | flip one entry of the XOR rule | that table's code length moves `6 → 9` | yes, basis digest |
| `H2_kraft_violating_language` | `(1,1,1,1)` | destroys the AE3-3 verdict | yes, Kraft guard |
| `H3_uncomputable_quantity_claim` | plant `kolmogorov_complexity: 3` | guard alarms rise `0 → 2` | yes |
| `H4_mdl_tie_set_suppressed` | report one MDL winner of two | the argmin really has 2 members | yes, worst ≠ best out-of-sample |
| `H5_parent_blob_tamper` | corrupt a pinned blob sha | audit flips | yes |

**Null.** The AE3-2 detector (strictly compressing corpus whose representation
attains exactly the blind baseline) fires on the planted witness, on `0` of the
`2` known-clean controls, and on `25` of `200` random corpora — the base rate is
reported rather than suppressed, because the row's claim is existence, and the
no-alarm case on known-clean data is what guards against a detector that cries
wolf.
