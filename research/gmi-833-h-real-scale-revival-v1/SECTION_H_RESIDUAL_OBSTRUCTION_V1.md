# The five Section-H rows at 7 of 11, and what blocks them

Registered in `FREEZE_V1.md` section 11 before this package had an executor, so
that it is analysis rather than an afterthought. **It closes no checkbox**,
emits no gate certificate, appears in no `replacements[]` entry of
`ISSUE_833_RECONCILIATION_H2_V1.json`, and a test asserts it contains no
closure marker.

## Why these five were not attempted here

`gmi-833-h-family-requirement-ledger-v1` scores five rows at 7 of 11, all at
`SIGMA_CENSUS`: Bayesian inference/belief-state systems; Feed-forward neural
networks; CNN/equivariant local-weight-sharing systems; Flow-like transport
systems; Energy-based systems. Their four missing coordinates are `R05`, `R07`,
`R08`, `R11`.

Because `FGS-2` forbids gluing a coordinate earned at one scope onto
coordinates earned at another, closing any of these rows means earning **all
eleven** at a new real-scale scope, exactly as this package does for its three.
That is not a budget problem. The obstruction is upstream of `R05`–`R11`: at a
new scope, `R02` and `R04` would have to be earned too, and the lower grammar
`G_S` of `FREEZE_V1.md` section 5 **cannot express any of these five families
at all**. Running a family-blind search over `G_S` on a Bayesian or
convolutional ecology cannot recover the named form, because the named form is
outside the image of the grammar. A run would produce a real number and a
meaningless one.

`G_S` offers one indexed accumulate `ACC <- ADD(ACC, BODY(ARG_i, PARAM_i))`,
one delay cell, six generic operations, a three-node `BODY` and a four-node
`HEAD`. That is, in effect, a single parameterised fold followed by a scalar
map: one linear-threshold unit with an optional one-step memory.

## Per row, the missing construct

| row | the named form needs | what `G_S` has | the missing construct |
|---|---|---|---|
| Bayesian inference/belief-state systems. | a normalised belief updated multiplicatively across observations: a ratio of two sums over the same index set | `RECIP` of a scalar, and one accumulate | **two accumulates over one shared index set, and their ratio** — normalisation is not a scalar reciprocal |
| Feed-forward neural networks. | at least two layers: several distinct folds whose outputs are themselves folded | exactly one accumulate and one scalar head | **a vector of accumulators feeding a second accumulate** — composition depth greater than one |
| CNN/equivariant local-weight-sharing systems. | one parameter reused at many shifted positions, with a translation group action | `PARAM_i` bound one-to-one with `ARG_i`, so every position has its own parameter | **an index map from position to parameter slot (tied parameters), plus a declared group action to be equivariant to** |
| Flow-like transport systems. | an invertible map together with its volume change | forward evaluation with no invertibility constraint and no derivative | **an invertible-composition construct and a log-volume accumulator** |
| Energy-based systems. | a scalar energy over a joint configuration, and an operator that searches the response space | forward evaluation of a program on a given input | **an argmin or partition-function operator over the response space** — the grammar has no construct that ranges over responses |

Two of the five, feed-forward networks and convolutional systems, need only
constructs that are compositional refinements of what is already there — a
second accumulate stage, and a tied-parameter index map. Those are the cheapest
successors. The other three need a construct of a different kind: a ratio of
folds, an invertibility requirement with a volume term, or an operator over the
response space.

## What a successor grammar would have to register

Any successor must keep the four properties that make the present result
meaningful, or the eleven coordinates stop being comparable:

1. Family-blind: the generator receives no family name, no family identifier
   and no family-specific candidate menu; structural names are attached
   afterwards by a classifier that reads expression trees only.
2. Exhaustively enumerated and semantically quotiented on a fixed exact
   rational probe grid, with a digest checked before and after every search.
3. A registered node budget, so `R06` remains an exact statement about
   minimality within an enumerated set rather than a claim about all programs.
4. A charged cost model fixed before any run, so `R07` is a statement about
   resources and not about the search that happened to be affordable.

Adding a second accumulate stage multiplies the enumeration by the number of
`BODY` classes, so a successor will need either a smaller node budget per stage
or a stronger quotient. That is the concrete next engineering problem for these
rows, and it is why they are reported here as open rather than attempted.

## Status

`BLOCKED_STRUCTURAL` remains **0** for Section H: nothing above is a proof of
impossibility. Each obstruction names its own removal. These five rows stay
open, with the missing construct named.
