# Information lower bound for universal developmental signatures v1

Status: **elementary counting lower bound / programme constraint.** No novelty claim is made for the pigeonhole argument.

## Setup

Fix a finite registered target set

\[
T=\{t_1,\ldots,t_n\}
\]

and suppose measured developmental burden is quantized to

\[
\{1,2,\ldots,L\}.
\]

Assume a morphology class `C` is **burden-universal at this finite scope**: for every vector

\[
c=(c_1,\ldots,c_n)\in\{1,\ldots,L\}^n
\]

there exists some machine `M_c in C` whose exact burden on the registered targets is that vector.

This assumption is easy for a sufficiently general finite-program/state-machine class by the construction in `BURDEN_VECTOR_NONIDENTIFIABILITY_V1.md`.

Let a pre-target structural signature be

\[
\sigma(M)\in\Sigma
\]

with at most `2^b` distinct possible values; equivalently the signature contains at most `b` bits.

Suppose a predictor `F` must recover **every exact target burden** from the signature and target identity:

\[
F(\sigma(M),t_i)=c_i(M)
\]

for all machines in `C` and all registered targets.

## Lower bound

There are `L^n` distinct burden vectors.

If two machines with different burden vectors shared the same signature value, then `F` would receive identical `(signature,target)` input for some target on which the burdens differ and could not be exact for both.

Therefore exact prediction requires the signature map to distinguish all `L^n` burden vectors:

\[
|\Sigma|\ge L^n.
\]

Hence

\[
\boxed{b\ge n\log_2 L.}
\]

## Interpretation

For an unrestricted machine class, an exact universal “compact developmental geometry signature” cannot be dramatically smaller than the finite burden function it is supposed to predict.

So a useful low-dimensional/low-bit signature is possible only because the admitted morphology/ecology family has **structure**:

```text
factorization
smoothness
shared subproblems
restricted update laws
low-rank/statistical regularity
compositionality
bounded treewidth / locality
shared inductive bias
```

The scientific content must lie in those restrictions and in a theorem/empirical law showing that they really permit compression/prediction.

## Why this matters for cross-paradigm GMI

A claim such as

> six scalar invariants predict developmental burden for every possible machine intelligence

is impossible in the exact unrestricted finite setting unless those scalars silently encode enough information to distinguish the entire burden function.

Therefore Track B must state:

```text
morphology family / admissible update class
ecology family
precision/tolerance
signature bit/measurement budget
prediction guarantee
```

for every compact-invariant claim.

## Approximate extension

If prediction only needs error tolerance `epsilon`, the exact `L^n` count is replaced by the covering/packing number of admissible burden functions under the registered loss metric.

This suggests a stronger future object:

\[
\log N(\epsilon,\mathcal B, d)
\]

—the number of bits needed to distinguish developmental-burden profiles to tolerance `epsilon`.

That connects Track B to ordinary statistical/information complexity rather than creating a new universal scalar by fiat.

## Upward research target

The important positive question becomes:

> Do major machine-intelligence morphology families occupy a surprisingly low-complexity subset of developmental-burden space, and can shared structural variables explain that compression prospectively?

This is measurable.

For example, compare:

```text
program/library families
probabilistic graphical/model families
controlled neural optimization families
OCM/history-induced search families
```

at matched target/ecology parameterizations and estimate the effective dimension/covering complexity of their burden surfaces.

A shared low-dimensional manifold with predictive structural coordinates would be a much stronger result than an arbitrary tuple definition.

## Terminal

```text
NO_SMALL_EXACT_UNIVERSAL_SIGNATURE_FOR_BURDEN_UNIVERSAL_CLASS
COMPACT_SIGNATURE_REQUIRES_RESTRICTED_STRUCTURED_FAMILY
BURDEN_SURFACE_COMPLEXITY_BECOMES_A_LIVE_GMI_OBJECT
```
