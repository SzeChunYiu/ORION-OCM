# GMI #956 / #833-F finite candidate-space freeze v1

Source `main`: `fcbb8c08ce36b2970079ed715d5e757f28da46d2`.

## Exact closure target

This tranche targets exactly four Section-F rows:

1. formalize `M(G0,B)` under finite budget `B`;
2. define a declared-interface semantic quotient that collapses implementation duplicates;
3. define architecture-name-independent morphology/species descriptors;
4. implement complete exact enumeration for registered small budgets.

Large-budget sampling, million-scale generation, reachability fractions, Pareto-front
density, clustering, family mapping, novelty metrics, distances, and clustering
stability remain open.

## Frozen parents

The implementation must pin and fail closed on these merged result blobs:

- foundation #837: `c0c574c4ec6e237d5fdafa694eac131399625a70`;
- `G0-reg-v1` operational core #868: `5d2948b9c04c84a46f6625e043753a489895478f`;
- mechanism/capability objects #848: `bdc5c3cd42e312d8c7af52f7ba84220631a25f8a`;
- finite grammar/remint boundary #875: `e903033615946a71f2f0859cda42e5b902e0d693`;
- robustness controls #863: `c3ff199c343b6905dabe8e3aefdc5958a2c8a06a`.

## Registered formal slice

`G0-fin-v1` is the finite, typed, architecture-family-name-free slice of the
merged five-class `G0-reg-v1` core. A candidate contains:

- a positive finite register declaration `R={0,...,r-1}`;
- a nonempty labelled instruction table at labels `{0,...,n-1}`, entry label 0;
- at each label exactly one typed `READ`, `INC`, `DECJZ`, `EMIT`, or `HALT`
  instance whose register and successor operands lie in the declared carriers.

Its exact structural resource vector is the additive sum of one
`REGISTER_CELL=(0,1)` atom per declared register and one `CODE_CELL=(1,0)` atom
per instruction. Thus `rho(P)=(n,r)` and
`M(G0-fin-v1,B)={P | rho(P)<=B}` coordinatewise. The registered enumerator
requires positive integer finite bounds and returns every well-typed member of
this set exactly once. Execution resources are measured separately and never
used to hide structural cost.

## Registered semantic interface and quotient

The observation interface is an explicitly supplied, finite, duplicate-free
tuple of finite natural-number input words plus a positive finite step cap.
Execution begins at label 0 with zero registers. Its protected observation is
`(status, output_trace)`, where status distinguishes `HALTED`, `BLOCKED_INPUT`,
and `STEP_LIMIT`. Candidate programs are equivalent only when these protected
observations agree for every registered word. The semantic key is the complete
ordered observation table; the quotient is exact only relative to this declared
interface.

Unbounded program equivalence, equivalence on unregistered continuations, and
termination beyond the cap are not decided or claimed.

## Registered neutral descriptor

The descriptor is derived only from the complete protected observation table,
the exact structural resource vector, and an explicitly supplied finite
developmental distance. It may contain counts/histograms and canonical hashes,
but no architecture-family labels, source spelling, or implementation names.
Semantic quotient identity and morphology descriptor equality remain distinct:
resources or developmental distance may separate behaviorally equivalent
implementations.

## Required proofs and executable falsifiers

- **FINITE-1:** finite carriers imply a finite exact product formula for
  `|M(G0-fin-v1,B)|`.
- **ENUM-1:** constructive enumeration is sound, complete, duplicate-free, and
  agrees with an independently written direct Cartesian oracle at every
  registered small budget.
- **QUOT-1:** equality of the complete observation-table key is an equivalence
  relation and canonical first/minimum-code representatives emit each class
  exactly once.
- **DESC-1:** descriptors are invariant under certified syntax reminting and
  internal register relabelling when external observations, raw resources, and
  developmental distance are preserved; behavior-only equality alone need not
  force descriptor equality.
- Malformed grammar/budgets/interfaces/remints, non-total operand domains, and
  undeclared descriptor inputs fail closed.
- A remint hostile that changes external semantics must be detected rather than
  blessed as invariant.

Allowed terminal only after analytic proof, independent exact replay, package
contract validation, and byte-stable normal/optimized receipts:

`GMI_833_FINITE_CANDIDATE_SPACE_QUOTIENT_DESCRIPTOR_ENUMERATION_AT_REGISTERED_SCOPE`
