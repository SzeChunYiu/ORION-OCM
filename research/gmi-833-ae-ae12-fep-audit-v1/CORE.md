# gmi-833-ae-ae12-fep-audit-v1

Section AE12 of issue #833 asks whether the free energy principle and active
inference are the strongest parent for unified perception, learning and action —
and, if so, to say so rather than to claim novelty. This package answers that on
a finite roster of registered dyadic worlds, in exact rational arithmetic, with
two independent computational routes.

Every registered probability is `0` or an integer power of `1/2`. That is the
whole reason each entropy, divergence, free energy and expected free energy below
is an exact rational number of bits rather than a transcendental number.

## The headline numbers

| what | exact value |
|---|---|
| free-energy minimiser vs the Bayes posterior, every registered world and observation | **equal**; minimum `= -log2 P(o)` exactly |
| `W_SPLIT`: evidence at each of four observations | `1/4`, so minimum free energy `2` bits |
| `W_CORR`: minimum over the full family vs the mean-field subfamily | `1` bit vs `2` bits — the restriction costs exactly **`1` bit** |
| `W_TRI_MIS` at `o0`: true posterior vs the model's | `(1/2, 1/2, 0)` vs `(1/2, 0, 1/2)` |
| `W_AMB`: expected-free-energy gap, for **every** preference distribution | exactly **`1` bit**; the risk terms cancel because both actions predict `(1/2, 1/2)` |
| utility orders no preference prior can reproduce, over permutations of the registered utility values | `4` of `6`, with `2` strict contradictions |
| `W_DISC1`: expected free energies | `(1, 0, 1)` bits — expected free energy picks `a1`, cardinality-`1` rate-distortion picks `a0`, CPC picks `a0` or `a1` over `45` weights, **no weight matches both** |
| `W_AGREE1`: expected free energies | `(1, 3/2, 3)` bits — all three principles pick `b0` |
| Markov blanket partitions | `4` on `SYS_MB_OK`, **`0`** on `SYS_MB_FAIL` |
| null: exhaustive census of the registered-shape space | `2` of `27`, rate `2/27`; sampled `15` of `200`, rate `3/40`; `0` alarms on three clean worlds |
| hostiles | `5` of `5` proved potent, then proved detected |
| prospective predictions | `6` confirmed, **`2` refuted and reported as refuted** |

## What is earned, and what is the parent's

The parent owns perception. On every registered world, with the full dyadic
family and a correctly specified model, free-energy minimisation returns exactly
the Bayes posterior and the minimum is exactly the surprisal. The receipt emits
`PARENT_SUFFICIENT` there and the manifest forbids
`GMI_NOVEL_OVER_ACTIVE_INFERENCE`. Marking parent sufficiency is the success
terminal this row asks for.

The boundary of that sufficiency is three assumptions, each proved necessary by a
registered world where dropping it breaks the equality — an unrestricted
variational family (price: exactly `1` bit), a correctly specified model (price:
a named posterior disagreement), and, for the action half, a preference prior
that can encode the utility. The third fails outright: the ambiguity term of
expected free energy never sees the preference prior, so when two actions induce
identical predicted outcome distributions the expected-free-energy order is
pinned at the ambiguity gap for **every** preference distribution, and the
utility orders that contradict it cannot be recovered by any prior.

## Two routes

Route A computes the free energy as surprisal plus the divergence to the exact
posterior and reads the minimiser off that decomposition; it takes exact
logarithms by `int.bit_length` and decides conditional independence by the
cross-product identity. Route B evaluates the raw definition on every member of
the registered family and takes a brute-force argmin; it takes logarithms by an
integer halving loop, builds the mean-field subfamily by an explicit
factorisation test rather than as a Cartesian product, and decides conditional
independence by comparing conditional distributions. Route B has no executable
import of route A; the test parses its syntax tree and asserts that. The two
agree on every value.

## Two refuted predictions

`AE12-P4` predicted an expected-utility difference of `1/2` on `W_AMB`. The
registered utility in fact makes the two actions exactly indifferent: the
difference is `0`. Attribution: the registered utility vector, not the audit. The
earned statement is stronger than the registered one — the gap is `1` bit for
every preference distribution, not merely for the registered dyadic family, and
`2` permutations of the registered utility values give strict contradictions.

`AE12-P5` predicted that the CPC family would reach all three actions of
`W_DISC1`. It reaches two: `a2` has exactly equal predictive loss and control
regret to `a1` and strictly larger cost, so it is term-vector dominated and no
weight can select it. The discrimination the row asks for is untouched.

Neither the freeze nor the register was edited.

## Reproduce

```bash
python3 -I -B  research/gmi-833-ae-ae12-fep-audit-v1/test_ae12_fep_audit_v1.py -v
python3 -I -O -B research/gmi-833-ae-ae12-fep-audit-v1/test_ae12_fep_audit_v1.py -v
python3 -I -B  research/gmi-833-ae-ae12-fep-audit-v1/ae12_fep_audit_v1.py
python3 -I -B  research/gmi-833-ae-ae12-fep-audit-v1/independent_fep_oracle_v1.py
```

The executor writes `RESULT_V1.json` to stdout, byte-identical under `-B` and
`-O -B` and on CPython 3.8 and 3.12.

Claim ceiling:
`GMI_833_AE12_FEP_ACTIVE_INFERENCE_PARENT_BOUNDARY_FIXED_ON_REGISTERED_FINITE_DYADIC_ROSTER`.
Horizons beyond `1`, continuous spaces, non-dyadic probabilities, real neural or
biological systems and every energetic quantity are outside the registered scope
and are listed in the manifest as not instantiated.
