# Finite collapse and morphology-metric theorems v1

## Definitions and scope

Use the exact finite candidate set and protected observation map from merged PR
#966. The registered interface is the three input words `(), (0), (1)` with
step cap 6. All equivalence and rates below are relative to this interface.

For a finite presentation census `P`, let `q:P -> S` send each program to its
complete protected observation table. Write `N=|P|`, `K=|q(P)|`, and let the
nonempty fiber sizes be `m_1,...,m_K`.

A registered morphology record is a triple `(s,r,h)` where `s` is a complete
protected table, `r=(code_cells,register_cells)` is the raw resource vector, and
`h` is a legal finite milestone history ending at `(s,r)`. Histories start at the
one-cell HALT morphology. A step either adds one resource cell without changing
protected behavior or adopts a new protected behavior at fixed resources. The
registered domain has `r<=(2,2)` and history length at most four.

## COLLAPSE-1 — exact duplicate/equivalence collapse rates

**Theorem.** The number of presentations removed by the exact semantic quotient
is `N-K`, hence its presentation-collapse fraction is `(N-K)/N`. The number of
unordered pairs that collide semantically is

`C = sum_j m_j(m_j-1)/2`,

so the pair-collision fraction is `C / (N(N-1)/2)` when `N>=2`.

**Proof.** Replacing each nonempty fiber of size `m_j` by one representative
removes `m_j-1` members. Summing gives
`sum_j(m_j-1)=sum_j m_j-K=N-K`. Within a fiber, exactly `binom(m_j,2)` unordered
pairs have equal images under `q`; pairs from distinct fibers cannot collide.
The fibers partition `P`, so summing counts every and only colliding pair. QED.

The implementation computes these quantities from the parent's canonical
quotient and compares them to an independently written first-occurrence/direct
pair-scan oracle. Histogram reconstruction is also exact.

## MORPH-METRIC-1 — semantic/resource/developmental product metric

Define:

- `s(x,y)` as Hamming distance on the three protected observations, treating
  each complete `(terminal_status, output_trace)` row as one atomic coordinate;
- `r(x,y)` as L1 distance on the two raw resource coordinates;
- `h(x,y)` as unit-cost Levenshtein distance on complete milestone sequences.

Each is a metric on its own factor carrier: Hamming and L1 are sums of discrete
coordinate metrics, while unit-cost Levenshtein is the shortest-path distance in
the undirected insertion/deletion/substitution edit graph. Therefore each is
nonnegative, symmetric, zero exactly on equal factor values, and satisfies the
triangle inequality.

For strictly positive rational weights `w_s,w_r,w_h`, define

`d_w(x,y)=w_s s(x,y)+w_r r(x,y)+w_h h(x,y)`.

**Theorem.** `d_w` is a metric on morphology records.

**Proof.** A positive linear combination preserves nonnegativity, symmetry, and
the triangle inequality. If `d_w(x,y)=0`, every nonnegative summand is zero; the
three factor values therefore agree and the complete records are equal. The
converse is immediate. QED.

The exact replay independently checks all metric axioms on all distinct values
of each factor and on all 47 distinct registered morphology records.

## NOVELTY-1 — nearest-archive morphology novelty

For a nonempty finite archive `A`, define `nu_w(x;A)=min_{a in A} d_w(x,a)`.

**Theorem.** `nu_w(x;A)=0` exactly when `x` is an archive morphology, and
`|nu_w(x;A)-nu_w(y;A)| <= d_w(x,y)`.

**Proof.** A finite minimum is zero exactly when one archive distance is zero,
which by metric identity is exactly membership in `A`. For any `a in A`, the
triangle inequality gives `d(x,a)<=d(x,y)+d(y,a)`. Taking the minimum over `a`
gives `nu(x)<=d(x,y)+nu(y)`; swapping `x,y` and combining proves the absolute
bound. QED.

The archive is the set of four distinct `(1,1)` morphologies, not source-code
strings. In the 576-presentation census, distinct program texts with identical
semantics/resources/histories have distance zero and identical novelty. A
separate same-final-morphology witness with a different legal development order
has positive developmental distance. Thus the construction is neither syntactic
distance nor a behavior-only score.

## REMINT-1 — certified grammar-surface invariance

A certified remint is a bijection on the five operation surface tokens followed
by its certified inverse decoder. It changes no typed operation, operand,
protected observation, resource vector, or developmental milestone.

**Theorem.** Every registered morphology record, `d_w`, and `nu_w` is invariant
under a certified remint.

**Proof.** Exact decoding recovers the same typed program. Each input to the
morphology record is therefore equal. Equal records give equal component
distances, weighted distances, and archive minima. QED.

All 120 token bijections are replayed on all 576 presentations (69,120 record
checks). A decoder swap that changes `INC` into `READ` changes protected behavior
and has strictly positive morphology distance, so it is rejected rather than
counted as an invariant remint.

## PERTURB-1 — explicit bounded metric and novelty stability

Let `w=(5,3,2)` and `w'=(501/100,299/100,201/100)`. Every coordinate changes by
at most `epsilon=1/100`. On the registered domain, `s<=3`, `r<=2`, and `h<=4`.

**Theorem.** For every registered pair,

`|d_w(x,y)-d_w'(x,y)| <= epsilon(3+2+4)=9/100`.

For any fixed nonempty archive, the same bound holds for novelty:

`|nu_w(x;A)-nu_w'(x;A)| <= 9/100`.

**Proof.** Expand the weighted sums and apply the triangle inequality to their
coefficient differences. For minima, if every archive distance changes by at
most `delta`, then the minimum can increase by at most `delta`; applying the
same argument in the reverse direction bounds the decrease. QED.

Base novelty scores are integral. Consequently any distinct base scores differ
by at least one, exceeding twice the uniform bound, so every strict ordering is
preserved. The threshold `11/2` has margin at least `1/2 > 9/100` from every
base score, so all registered threshold classifications are preserved. Exact
rational replay checks all distinct-morphology pairs, all 576 novelty scores,
all strict presentation-score orderings, and all threshold labels.

## Boundary

These are exact finite, interface-relative measurements and metric theorems.
They do not decide unbounded program equivalence, establish a unique/unbiased
grammar, measure all search-law reachability or Pareto density, run clustering,
validate clustering stability, map clusters to known families, or validate an
UNKNOWN cluster. Metric stability is necessary evidence for a later clustering
study but is not substituted for that still-open task.
