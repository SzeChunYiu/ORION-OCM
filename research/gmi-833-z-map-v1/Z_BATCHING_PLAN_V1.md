# Section Z batching plan v1 — 15 closed, 116 remaining

This round closed 15 of 131 rows with two packages built to the full #833
closure standard. The plan below assigns every remaining row to a package,
orders the packages, and names where the real scientific work sits.

## Closed this round

| package | rows | subsection |
|---|---:|---|
| `gmi-833-z-z12-prediction-scoring-v1` | 9 | Z12 (all) |
| `gmi-833-z-z15-decisive-falsifiers-v1` | 6 | Z15 (all) |

Both are one-package-per-subsection, which is the grain Z is built on: each
subsection is a single protocol decomposed into its required ingredients, so a
package that discharges the protocol discharges the whole subsection.

## Tier 1 — next, and closable on the same pattern (25 rows, 5 packages)

These need no discovery. The finite universes and the frozen artifacts are
already on `main`; what is missing is the proof or the instrument.

| order | package | rows | why it is ready |
|---:|---|---:|---|
| 1 | `gmi-833-z-z3-invariance-v1` | Z3: 5 | the remint/equivariance machinery exists (`gmi-833-remint-equivariance-v1`, `gmi-833-g0-grammar-bias-v1`, `gmi-833-transform-geometry-v1`); this round's `Z15-F4` already demonstrates the invariant/non-invariant transformation *pair*, which is the hard part of row 3. Row 4's *or explicitly characterize the non-invariant quantity* is the row's own disjunction and a legitimate branch. |
| 2 | `gmi-833-z-z5-critical-phenomena-v1` | Z5: 6 | `λ* = ηp/2` is already an analytic critical threshold with 20 prospectively frozen transitions; finite-size scaling over the budget ladder is exhaustive, and row 6 (*preserve failed scaling predictions*) is served by the register pattern Z15 established. |
| 3 | `gmi-833-z-z7-impossibility-v1` | Z7: 6 | resource-dependent impossibility regions are exactly the infeasible cells of the finite grid; the capability predictor already emits `INCONSISTENT_REGISTERED_ASSUMPTIONS`, which is a *proved* impossibility, not a failure to answer. |
| 4 | `gmi-833-z-z2-minimal-prior-v1` | Z2: 5 | an exact finite no-free-lunch over the `(2,2)` protected-semantic quotient proves row 1; row 2 follows as the minimal bias that restores learnability; row 3 has an existing lane (`gmi-833-terminology-migration-v1`). Rows 4-5 are harder and may need a second pass. |
| 5 | `gmi-833-z-z4-universality-v1` | Z4: 5 | quotient named families by scaling/resource behaviour and measure which distinctions survive; the 146-summary reduction of the 65,552-candidate universe is exactly such a quotient and is already exercised by both packages shipped this round. |

## Tier 2 — the blocked harness (8 rows, 1 multi-pass package)

`gmi-833-z-z17-flagship-robustness-v1` — **Z17: 8 rows.** The rows say *central
conclusions* and *the flagship claim*, plural and definite. Running the eight
robustness axes against one designated conclusion and ticking the rows would be
closure by narrowing, so this package must first commit a **register of central
conclusions** — `BASELINE_V1.md` section 1, assertions A1-A14, is the natural
authority — and then run all eight axes per entry. The axes themselves are
cheap once the register exists: leave-one-family-out over the 5x4 world grid,
alternate neutral grammars, alternate search/development laws, alternate
resource accounting, seeds and remints, independent implementations (which the
two-route rule already forces), exact sensitivity to every free parameter
(analytic, since `λ* = ηp/2`), and a greedy minimization for the smallest
supporting evidence subset.

Do not start Z17 before the register is written; that ordering is the whole
difficulty.

## Tier 3 — genuine new science (43 rows, 5 packages)

This is where the scientific work actually sits. None of it is harnessable.

| package | rows | the hard part |
|---|---:|---|
| `gmi-833-z-z1-master-principle-v1` | Z1: 6 | a compact variational/selection principle from which the registered laws follow as corollaries, a compression measure (independent predictions per free theoretical degree of freedom), and — the sharpest row — a **proof** that some named laws cannot be compressed into it. That negative row is the one most likely to produce a real result. |
| `gmi-833-z-z6-discrimination-v1` | Z6: 6 | preregistered environments where GMI and a strongest parent genuinely disagree. The likely finding is that MDL, Bayesian decision theory and bounded rationality are **observationally equivalent** to the boundary law on the finite quotient — row 6 is that finding's honest terminal, but it must be *earned* by an equivalence proof, never assumed to avoid the work. |
| `gmi-833-z-z8-hostile-ood-v1` | Z8: 10 | an independent hostile-world generator covering nine named ingredient classes (near-ties, verifier noise, causal aliasing, shift, resource-accounting changes, history conflicts, grammar changes, search-law changes) with predictions frozen before the worlds reach the scorer. Near-ties are already available for free: the 20 boundary worlds *are* exact near-ties. |
| `gmi-833-z-z11-benchmark-v1` | Z11: 9 | a benchmark whose scoring target is theory prediction rather than model accuracy; synthetic exact worlds are ready, hidden ecologies and negative controls are not. |
| `gmi-833-z-z13-w4-gate-v1` + `gmi-833-z-z16-groundbreaking-v1` | Z13: 12, Z16: 6 | the actual discovery gate. Z16 cannot close before Z13 or an equivalent produces a result, so these two are one dependency chain, not two packages. Existing lanes: `gmi-833-blind-recovery-v2-v1`, `gmi-833-maturity-rescore-v3-w4-v1`. |

## Tier 4 — external gates (32 rows, 4 packages)

Z9 (7), Z10 (10), Z14 (7), Z18 (8). Each names a person or an independent team
as the instrument. Under the standing directive these close with the strongest
legitimate proxy, labelled `HUMAN_GATE_BYPASSED__MODEL_PROXY` and never
presented as externally obtained. They are deliberately last: a proxy assembled
in a hurry is exactly the `POST_HOC_SUSPECT` class audit #976 filed, and these
32 rows are the ones an auditor will read first.

Z10 additionally needs real measured resource data (CPU/GPU/wall-time/memory/
I/O/energy) across five materially different domains, which is real engineering
rather than a proxy question.

## Dependency order

```
Tier 1 (Z3, Z5, Z7, Z2, Z4)         -- independent of each other, run in parallel
        |
Z17 register of central conclusions -- blocks all 8 Z17 rows
        |
Tier 3 Z1, Z6, Z8, Z11              -- Z6 depends on Z1's principle being stated
        |
Z13 -> Z16                          -- Z16 cannot close before a discovery exists
        |
Tier 4 Z9, Z10, Z14, Z18            -- last, and only with unhurried proxies
```

## Two lessons this round that should carry forward

1. **Validate the instrument before reporting its numbers.** The Z12
   calibration score was frozen at the wrong binning level and reported `7/8`
   error on a predictor with coverage exactly `1`; it also made its own hostile
   undetectable. Both were caught only because the freeze required every hostile
   to be *shown able to fire*.
2. **Run the null before believing the falsifier.** Z15's `F1` looked decisive
   until its 200-seed null caught `143/200`. The survivors turned out to occupy
   exactly the analytically predicted blind interval, and the fix used evidence
   the frozen design already contained. Every Tier-1 package should budget for
   one such diagnose-and-revive cycle rather than treating the first green as
   the result.
