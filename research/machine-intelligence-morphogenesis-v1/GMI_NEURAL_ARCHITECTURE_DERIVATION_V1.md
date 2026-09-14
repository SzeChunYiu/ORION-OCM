# Neural architecture, derived (B4, architecture half)

Date: 2026-09-14. Lane: machine-intelligence-morphogenesis-v1.
Witness: `gmi_microscope/neural_architecture_witness.py`.
Receipt: `microscopes/results/STAGE_NEURAL_ARCHITECTURE_V1.json`.
Executed on `laptop-billy`; receipt md5-verified. Reproduced in CI.

`GMI_LINEAR_FAMILY_DERIVATION_V1.md` established that a weighted sum is correct
exactly when the obligation is low-degree in the basis it is given. This asks
what a machine must add when that fails, and derives the architectural
commitments of the neural family rather than assuming them.

**The learning-rule boxes are deliberately absent.** Gradient descent, backprop,
and when gradients beat search touch a standing negative — the corpus measured
gradient descent at 0.48× with no admissible gradient machine anywhere tested.
Folding them in here would mix a derivation with an unresolved empirical result.

## Depth alone buys exactly nothing

For **390 625** two-layer linear compositions, the equivalent single weight
vector `u = v·W` is constructed and checked on every input. Compositions a
single layer could not reproduce: **0**.

> Every composition of weighted sums *is* a weighted sum. A stack of linear
> layers is not an architecture — it is a more expensive way to write one layer.

## Where linear closure fails

Every threshold unit carries a **bias**, so "depth 1" is the full class of
linear threshold functions. Without one, majority — which *is* linearly
separable — would look unreachable for the wrong reason.

| task | depth 1 | depth 2 | depth needed |
|---|---|---|---|
| `single_bit` | ✅ | ✅ | 1 |
| `majority` | ✅ | ✅ | 1 |
| `xor2` | **✗** | ✅ | **2** |

> XOR is the separator. Put beside the result above, the pair is the whole
> derivation of the neural unit: **depth without a nonlinearity buys nothing,
> and a nonlinearity without depth cannot reach XOR either.** Neither
> ingredient is optional and neither is sufficient alone.

## Parameter sharing is licensed by the obligation, not the architecture

| obligation | inputs | orbits | permutation-invariant | saving |
|---|---:|---:|---|---:|
| `majority` | 8 | 4 | ✅ | **2×** |
| `parity` | 8 | 4 | ✅ | **2×** |
| `first_bit` | 8 | 4 | **✗** | — |

`first_bit` has the same orbit count but is *not* invariant: sharing there would
merge inputs the obligation distinguishes. The witness detects that rather than
trusting it.

> Weight sharing is licensed by a symmetry **in the obligation**, never by a
> symmetry in the architecture.

## Distributed versus symbolic state

Over a product world `A × B`, symbolic cost is one state per combined input.
Distributed cost is `R + C` codes plus the `R × C` table that combines them,
where `R` and `C` are the classes each coordinate collapses to on its own —
the quotient theorem applied one coordinate at a time.

| obligation | `R` | `C` | distributed | symbolic | cheaper |
|---|---:|---:|---:|---:|---|
| factorizing | 2 | 2 | **8** | 16 | distributed |
| diagonal | 4 | 4 | 24 | **16** | **symbolic** |

The diagonal obligation collapses *nothing* — every row and column differs — so
the distributed machine buys codes it cannot use.

> Distributed representation is not a cheaper encoding in general. It is cheaper
> exactly when each coordinate's behaviour collapses on its own, and **strictly
> more expensive when it does not**.

## The negative twin

*A first version of this section looked for an obligation the net could not
reach. That was the wrong question: with a bias most 3-bit functions are
linearly separable, so the search kept succeeding.* The right question is cost.

| obligation | hidden width | net cost | table cost | verdict |
|---|---:|---:|---:|---|
| `majority` | **0** | 4 | 8 | **net wins** |
| `xor2` | 2 | **9** | 8 | **table wins** |
| `parity3` | none ≤ 2 | — | 8 | unreached at width ≤ 2 |

Majority is reached with no hidden layer at all. XOR needs one, and one hidden
layer already costs 9 against the table's 8.

> **The neural morphology is not a universal improvement. It is a bet that the
> obligation has exploitable structure.** Where the bet is right it wins by a
> wide margin; where it is wrong the machine pays for weights and buys nothing,
> and the table it was meant to replace is the correct machine.

This is the same law as the kernel result in B3: at full expressiveness a
compressing machine costs exactly what a lookup table costs.

## Scope

- 3 binary inputs, weight grid `−2…2`, bias `−3…3`, hidden width ≤ 2. The
  enumeration is capped and reports `unreached at width ≤ 2` rather than
  claiming impossibility — `parity3` may well be reachable at width 3.
- The cost model charges `D·H + H + 1` parameters against `2^D` slots. The
  *orderings* are the result; the constants are not.
- Threshold units only. Smooth activations, which is what makes the learning
  half possible, are not modelled here.
- Recurrence (box 4) is not re-derived: `GMI_FINITE_STATE_DERIVATION_V1.md`
  already establishes when finite temporal state is required and what it costs,
  and the neural case adds nothing to that argument.

**Falsifier.** Exhibit a two-layer linear composition no single layer
reproduces; or a permutation-invariant obligation where sharing merges
distinguished inputs; or an obligation that collapses per-coordinate where
symbolic coding is cheaper.
