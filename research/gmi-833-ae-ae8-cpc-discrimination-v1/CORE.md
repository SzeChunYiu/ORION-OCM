# gmi-833-ae-ae8-cpc-discrimination-v1

Section AE8 of issue #833 asks whether `Compression + Prediction + Control` is a
theorem, a variational principle, a decomposition, a heuristic or a slogan — and
forbids calling it the master law unless it beats a bag-of-laws baseline and
survives parent discrimination. This package runs both tests exactly, on a
finite preregistered roster, with two independent routes.

The registered universe is the three-bit cube with the uniform measure. A model
is a code map plus a per-cell prediction and action; its term vector
`(cost, predictive loss, control regret)` is **derived** from that object. The
model space has `4110` members; each of the `12` worlds carries `4`; the weight
grid has `45` triples of eighths.

Information quantities here are irrational. They are carried as exact rational
combinations of prime logarithms and compared by one integer product comparison,
so the package contains no float and no numeric bound at all.

## The headline numbers

| what | exact value |
|---|---|
| classifier ladder | `THEOREM` no, `VARIATIONAL_PRINCIPLE` no, **`DECOMPOSITION` yes**, `HEURISTIC` no, `SLOGAN` yes → verdict **`DECOMPOSITION`** |
| CPC agreement, unrestricted roster | `4` of `12`; the random control reaches `7`, and `74` of `200` draws reach `4` or more — **CPC does not beat chance there** |
| CPC agreement once the preference is restricted to what the term vector determines | **`12` of `12`** at grid index `8` |
| phenomena proved irreducible to CPC | **`4` of `5`** — communication `(29, 0, 1/4)`, development `(16, 1/2, 1/2)`, history `(16, 1/2, 1/2)`, uncertainty `(16, 1/4, 1/2)`; verification **not proved** |
| bag-of-laws baseline | `3` valid laws covering `10` of `12` worlds, agreeing on all `10`, at `54` bits; one law `REFUTED_ON_ROSTER` (correct on `3` of its `4`), two never applicable |
| master-law test | CPC `4/12` at `12` bits vs baseline `10/12` at `54` bits — neither dominates; worlds where CPC differs from every parent: **`0`** → **`CPC_MASTER_LAW_CLAIM_WITHHELD`** |
| agreement with the registered preference, out of 12 | predictive information `5`, CPC `4`, active inference `3`, algorithm selection `3`, control as inference `3`, resource-rational `3`, MDL `2`, bounded rationality `1`, rate-distortion `1` |
| observationally equivalent pairs | exactly one: bounded rationality and cardinality-`1` rate-distortion control |
| corollary search | `AE6_LOCALITY` and `AE15_MODEL_NECESSITY` are corollaries; `AE2_NO_PREDICTIVE_INFORMATION` and `AE12_AMBIGUITY_INDEPENDENCE` are not; two laws never apply |
| null | `200` trials, histogram `{0:7, 1:22, 2:43, 3:54, 4:28, 5:32, 6:13, 7:1}`, largest `7`, mean `627/200` |
| hostiles | `5` of `5` proved potent, then proved detected |
| prospective predictions | `6` of `6` confirmed |

## The load-bearing result

`J_lambda(m)` depends on `m` only through its term vector. So two models with
equal term vectors get equal objective value at **every** weight, and the choice
between them falls to the frozen name order. The package searches the whole
`4110`-model space and finds, for four of the five named phenomena, pairs of
structurally different models whose **derived** term vectors are equal
element-wise and which differ in exactly one computed structural attribute. Each
such pair is a proof, at the registered scope, that the phenomenon cannot be
reduced to CPC without an additional term. Because the objective values are
exactly equal, exchanging the two names exchanges the choice, so the
impossibility does not depend on which tie-break was frozen.

`verification` is reported as **not proved irreducible**: the search found no
qualifying pair. That is a statement about what was found, not a claim that
verification reduces.

## Why the verdict is a refusal

The row permits the master-law claim only on two conditions. CPC does not beat
the baseline — `4/12` at `12` bits against `10/12` at `54` bits is
Pareto-incomparable — and it differs from every parent principle on `0` worlds.
Both legs fail, so the receipt emits `CPC_MASTER_LAW_CLAIM_WITHHELD` and the
manifest forbids `CPC_IS_THE_GMI_MASTER_LAW`. Withholding is the closure the row
asks for, and it is not evidence against the parents; that reading is itself a
registered forbidden promotion.

The baseline is built so it can fail: laws are validated on their own coverage,
one is reported `REFUTED_ON_ROSTER` and excluded, and the survivors leave `2`
worlds uncovered. A baseline that covered everything by construction could
neither be beaten nor missed.

## Two routes

Route A groups models by term vector to find collisions, relabels partitions
canonically, takes ceiling logarithms with `int.bit_length`, and holds
logarithmic values as one `Fraction` per prime. Route B compares every pair
directly, builds cells with a dictionary keyed on the code value, computes
ceiling logarithms with an explicit loop, and decides the sign of a logarithmic
combination by cross-multiplying its positive and negative parts into two
integers. Route B has no executable import of route A and imports only the
standard library; the test parses its syntax tree and asserts both. The two
agree on every preference, every agreement vector, the whole pairwise matrix and
every collision.

## Disclosed gaps

The register names *the frozen predicted disagreement sets* but does not
enumerate them per world, so this package's per-world disagreements are reported
as measurements. The one genuinely preregistered discriminating world it can
point to is AE12's `W_DISC1`, whose register commit precedes every
implementation blob here. The register also does not pin a decision rule for the
word *beats*; the Pareto rule used is stated in the receipt.

## Reproduce

```bash
python3 -I -B  research/gmi-833-ae-ae8-cpc-discrimination-v1/test_ae8_cpc_discrimination_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae8-cpc-discrimination-v1/test_ae8_cpc_discrimination_v1.py -v
python3 -I -B  research/gmi-833-ae-ae8-cpc-discrimination-v1/ae8_cpc_discrimination_v1.py
python3 -I -B  research/gmi-833-ae-ae8-cpc-discrimination-v1/independent_cpc_oracle_v1.py
```

Claim ceiling:
`GMI_833_AE8_CPC_CLASSIFIED_AND_DISCRIMINATED_AGAINST_REGISTERED_MASTER_PRINCIPLES_ON_A_FINITE_PREREGISTERED_WORLD_ROSTER`.
Everything is claimed at the registered finite scope; the manifest lists what is
not instantiated.
