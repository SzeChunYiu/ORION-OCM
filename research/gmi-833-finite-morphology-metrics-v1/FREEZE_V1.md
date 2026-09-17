# GMI #833-F finite collapse and morphology-metric freeze v1

Source `main`: `b30237c229b2c3fd4016de19c5fa9c155c0a7484` (merged PR #966).

## Exact closure target

This dependent tranche targets exactly three still-open Section-F rows:

1. measure the duplicate/equivalence collapse rate on every registered exact
   small-budget census;
2. develop novelty scores that factor through semantic/resource/developmental
   morphology rather than program syntax;
3. develop an exact semantic/resource/developmental morphology distance.

It also proves and executes surface-grammar-remint invariance and an explicit
finite metric-weight perturbation bound for the distance and novelty score. That
is a control on the metric itself, not a clustering experiment, so the separate
"Validate clustering stability under grammar remints and metric perturbations"
row remains open.

Scalable sampling, million/hundred-million generation, reachability fractions,
Pareto density, clustering, post-hoc family mapping, and UNKNOWN-cluster
validation remain open.

## Frozen parent

The implementation must import the merged `G0-fin-v1` candidate semantics and
fail closed unless the exact parent result blob is
`4086d6bea440d626e48d92eb35d39267a010589e` with ceiling
`GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE`.
It also pins the grammar-remint and robustness-control results already used by
that parent.

## Registered exact census and collapse measurements

Use the parent interface `I=(((),(0,),(1,)), step_cap=6)` and exact cumulative
budgets `(1,1)`, `(2,1)`, `(1,2)`, and `(2,2)`. For a census of `N` presentations
partitioned into `K` protected semantic classes with multiplicities `m_j`, emit:

- presentation-collapse count `N-K` and exact fraction `(N-K)/N`;
- unordered equivalent-pair count `sum_j binom(m_j,2)` and exact pair-collision
  fraction over `binom(N,2)` (zero by convention when `N<2`);
- singleton count/fraction and the exact multiplicity histogram.

An independent direct grouping/pair-count oracle must agree with every emitted
quantity. All fractions remain exact reduced rationals. These rates are finite,
budget- and interface-relative; no unbounded-program-equivalence rate is implied.

## Registered morphology domain and developmental law

A morphology record contains only:

- the complete protected observation table on `I`;
- the exact raw structural resource vector `(code_cells, register_cells)` within
  budget `(2,2)`;
- a nonempty development history of at most four architecture-name-free
  milestones, each itself a protected observation table plus resource vector.

The registered canonical history starts at the one-cell HALT morphology,
increases code cells and then register cells one at a time while retaining HALT
behavior, and finally adopts the target protected behavior at fixed resources
when needed. Every milestone is realized by a candidate in the exact census.
This is one declared finite development law, not a measurement of reachable
fractions under every search law.

## Exact distance and novelty

For records `x,y`, define integer component metrics:

- `s(x,y)`: Hamming distance between complete protected observation tables;
- `r(x,y)`: L1 distance between raw resource vectors;
- `h(x,y)`: unit-cost Levenshtein distance between complete milestone histories.

For strictly positive rational weights `w=(w_s,w_r,w_h)`, define

`d_w(x,y)=w_s s(x,y)+w_r r(x,y)+w_h h(x,y)`.

On the declared morphology-record product this is a metric. It contains no
program tokens, instruction order, implementation identity, or architecture
family label. For a nonempty morphology archive `A`, define novelty
`nu_w(x;A)=min_{a in A} d_w(x,a)`. The registered archive is the set of distinct
morphologies at budget `(1,1)`; all `(2,2)` presentations are scored.

## Remint and perturbation obligations

- Every one of the `5!` certified operation-token remints must preserve every
  one of the 576 registered morphology records, hence every distance and novelty
  value. A semantics-changing pseudo-remint must be detected.
- The base weights are `(5,3,2)`. The registered perturbed weights are
  `(501/100,299/100,201/100)`, so every coordinate changes by at most `1/100`.
- On the registered domain, `s<=3`, `r<=2`, and `h<=4`, hence
  `|d_w-d_w'|<=9/100`; the same uniform bound holds for archive novelty.
- Exact replay must verify the bound for every unordered pair of distinct
  morphology records and every candidate novelty score. It must also verify
  preservation of every strict novelty ordering and the threshold classification
  at `11/2`; ties and perturbations outside the registered bound are not claimed
  stable.

## Required theorems and falsifiers

- **COLLAPSE-1:** all exact collapse statistics agree with an independently
  written oracle and reconstruct their census sizes.
- **MORPH-METRIC-1:** all three components and their positive rational weighted
  sum satisfy metric axioms; exhaustive replay covers the 47 distinct registered
  morphology records.
- **NOVELTY-1:** archive novelty is syntax-free, zero exactly on archive
  morphologies, and 1-Lipschitz in its query under `d_w`.
- **REMINT-1:** certified surface remints preserve the full morphology records;
  a semantics-changing decoder swap does not.
- **PERTURB-1:** the analytic `9/100` bound and all registered stability
  consequences hold exactly using rational arithmetic.
- Boolean-as-integer inputs, nonpositive weights, malformed observation tables,
  invalid resource bounds, empty/overlong/inconsistent histories, empty archives,
  and duplicate presentation inputs fail closed.

Allowed terminal only after theorem ledger, independent replay, normal and
optimized tests, deterministic byte-stable receipt, and exact three-row
reconciliation preview:

`GMI_833_FINITE_COLLAPSE_AND_SEMANTIC_RESOURCE_DEVELOPMENTAL_METRICS_AT_REGISTERED_SCOPE`
