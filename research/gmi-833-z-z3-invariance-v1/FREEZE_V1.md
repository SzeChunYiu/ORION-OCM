# GMI #833 Section Z / Z3 — invariance and representation independence, freeze v1

Source `main`: `349c2e62c4ae01f52cf66f61e4dacdbdfcf10071`.

Committed **before** any registry, executor, oracle, receipt or test in
`research/gmi-833-z-z3-invariance-v1/` exists. `git log` must show this commit
strictly preceding the first implementation commit of this package, and the
package workflow gates on exactly that ordering.

## Claim ceiling

```
GMI_833_Z3_FINITE_TRANSFORMATION_REGISTRY_INVARIANCE_EQUIVARIANCE_AND_THE_DECLARED_STATE_BIT_NON_INVARIANT_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

## The exact rows this tranche may reconcile

Section Z lives in issue comment `5684819296`, subsection
`### Z3 — Invariance and representation independence`. The five rows are, verbatim:

1. `- [ ] Define the transformations under which a scientific GMI prediction should remain invariant: renaming, semantics-preserving recoding, compiler/substrate changes, equivalent grammar transformations, unit changes and equivalent state encodings.`
2. `- [ ] Prove invariance/equivariance results under appropriate transformed resource accounting.`
3. `- [ ] Construct adversarial semantics-preserving recodings designed to flip morphology conclusions.`
4. `- [ ] Require flagship conclusions to survive those recodings or explicitly characterize the non-invariant quantity.`
5. `- [ ] Quantify grammar-induced description-length and reachability bias.`

**No neighboring row is earned here.** Nothing in Z1, Z2, Z4–Z18, nothing in the
issue body, nothing in any other comment. The trailing
`## Groundbreaking flagship closure rule` prose block carries no rows.

Row 4 is a disjunction (`survive ... or explicitly characterize the
non-invariant quantity`). This package commits to delivering **both branches**,
not to picking the cheaper one: the surviving group is exhibited *and* the
non-invariant quantity is characterized with an exact census. A run that
delivers only one branch is reported as a partial result and the row stays open.

## Registered universe (pinned, not rebuilt)

The finite architecture-name-free binary mechanism universe `U` already frozen by
`gmi-833-heldout-20-transitions-v1`:

- `16` stateless candidates: an output table over the index `(mode, cur)`;
- `65536` one-state-bit candidates: a next-state table and an output table, both
  over the index `(state, mode, cur)`;
- `|U| = 65552`.

Scored interface: all `8` input sequences of length `3`, both modes
(`mode 0` = copy current input, `mode 1` = emit the previous input), scored at
timesteps `t = 1, 2`. Hence `N = 16` scored moments per mode. Each candidate `u`
carries the exact integer triple `sigma(u) = (bits(u), e_now(u), e_delay(u))`
with `bits(u)` the **declared** state-bit count.

Objective at a world `(p, eta, lambda)` with `p, eta, lambda` rational, `eta > 0`:

```
J(u) = eta * ( (1-p) * e_now(u)/16 + p * e_delay(u)/16 ) + lambda * bits(u)
```

Registered worlds: the `60` worlds of `gmi-833-heldout-20-transitions-v1`
(`20` cases, each at `lambda_low`, `lambda_high` and the exact boundary
`lambda* = eta*p/2`).

## Row 1 — the transformation registry (frozen now)

`TRANSFORMATION_REGISTRY_V1.json` is the machine-readable artifact. Each entry
carries `id`, `row1_category`, `status` (`CLAIMED_IRRELEVANT` or
`DECLARED_RELEVANT`), an exact definition, and the quantity it must or must not
move. The registry covers every category the row names.

| id | row-1 category named by the row | status | definition |
|---|---|---|---|
| `T1_RENAME` | renaming | `CLAIMED_IRRELEVANT` | a bijection of the surface identifiers `c00000...c65551`; `sigma` travels with the candidate |
| `T2_STATE_ENCODING` | equivalent state encodings | `CLAIMED_IRRELEVANT` | negation of the state bit: `st -> 1 - st`, with `nxt` and `table` re-indexed accordingly |
| `T3_IO_CONJUGATION` | semantics-preserving recoding | `CLAIMED_IRRELEVANT` | negate the input symbol and the output symbol simultaneously; the target is negated with them, so the error counts are preserved |
| `T4_COMPILER` | compiler/substrate changes | `CLAIMED_IRRELEVANT` | re-emission of each candidate through the composite `T2 ∘ T3 ∘ T1`: a different concrete encoding of the same transducer, with the declared resource vector transported |
| `T5_UNIT` | unit changes | `CLAIMED_IRRELEVANT` (equivariant) | common positive rational rescaling `(eta, lambda) -> (c*eta, c*lambda)` over the registered ladder `c ∈ {1/7, 1/2, 2, 3, 11/5, 100}` |
| `T6_GRAMMAR_ISO` | equivalent grammar transformations | `CLAIMED_IRRELEVANT` | an isometric relabeling of the description grammar: a bijection of description words preserving semantic class, description length and mutation adjacency (the `gmi-833-g0-grammar-bias-v1` isometry notion, transported to this universe) |
| `H1_PSEUDO_RENAME` | (adversarial) | `DECLARED_RELEVANT` | a bijection of the surface identifiers under which `bits` stays attached to the **slot** while `(e_now, e_delay)` travels with the candidate — a semantics-moving map disguised as a rename |
| `H2_ETA_ONLY` | (adversarial) | `DECLARED_RELEVANT` | `eta -> c*eta` with `lambda` fixed: not a unit change, and it must move the boundary |
| `H3_DEAD_PADDING` | (adversarial, semantics-preserving) | `DECLARED_RELEVANT` for declared-bit labelling, `CLAIMED_IRRELEVANT` for effective-bit labelling | replace a candidate by a behaviourally identical candidate whose declared state bit is not live |
| `H4_GRAMMAR_NON_ISO` | (adversarial) | `DECLARED_RELEVANT` | a same-semantics grammar relabeling that changes description length / mutation adjacency |

A transformation registered `DECLARED_RELEVANT` that turns out to move nothing is
a defect of this package, not a result: the registry check requires every
`DECLARED_RELEVANT` entry to be shown able to move its named quantity, and every
`CLAIMED_IRRELEVANT` entry to be shown not to move it on the clean data.

## Row 2 — the invariance and equivariance statements (frozen now)

Labelled `[DERIVED-AT-FREEZE]` where the algebra was done before this freeze was
written, and `[UNCOMPUTED]` where the number is not known to the author at freeze
time. Honesty about which is which is part of the freeze.

- `IV-2a` `[DERIVED-AT-FREEZE]` **Invariance.** For every registered world and
  every transformation in the group generated by `T1, T2, T3, T4`, the multiset
  `{J(u) : u ∈ U}` and the winner class set (labelled by declared bits) are
  unchanged. Verification: exhaustive over `60` worlds x `200` seeded `T1`
  permutations, plus `T2`, `T3` and `T4` applied to the whole universe.
- `IV-2b` `[DERIVED-AT-FREEZE]` **Equivariance under transformed resource
  accounting.** Under `T5`, `J -> c*J` for every candidate, `lambda* -> c*lambda*`,
  and the argmin set is unchanged. Therefore the prediction is a function of the
  dimensionless pair `(p, mu)` with `mu = lambda/eta` alone, and the boundary is
  `mu* = p/2`. This is exactly the sense in which resource accounting must be
  *transformed along with* the prediction: the price and the error weight are not
  separately meaningful, only their ratio is.
- `IV-2c` `[UNCOMPUTED]` the exact number of distinct values in the objective
  multiset at a registered world, and the exact number of distinct `sigma`
  classes in `U`. Both are reported, not predicted.

## Row 3 — the adversarial recodings (frozen now)

The adversary's goal is a map that preserves the external behaviour of every
candidate and yet flips a morphology conclusion.

**Behavioural equivalence (frozen definition).** Two candidates are behaviourally
equivalent iff they produce the identical output symbol at every position of
every one of the `8` sequences in both modes — the full `8 * 2 * 3 = 48`-symbol
output trace, not merely the `32` scored moments. A candidate is
**behaviourally stateless** iff its trace equals the trace of some stateless
candidate.

`H3_DEAD_PADDING` is the adversarial family: the behaviourally-stateless members
of the declared-stateful half of `U`.

- `[DERIVED-AT-FREEZE]` the *table-ignores-state* subfamily has exactly
  `16 * 256 = 4096` members, because the output table is then determined by the
  stateless table on both state values and `nxt` is free.
- `[UNCOMPUTED]` the **true** behavioural census `N_BS` of behaviourally
  stateless declared-stateful candidates. It is at least `4096`, and it is
  strictly larger if, for example, a candidate whose `nxt` never leaves the start
  state is behaviourally stateless without its table ignoring the state. The
  syntactic count `4096` is registered here as a **hypothesis about the
  instrument**: if `N_BS > 4096`, the syntactic definition undercounts the
  adversarial family and the undercount is recorded as an instrument failure with
  its repair, exactly as required for the counterexample discipline.

**The flip, stated precisely.** A morphology verdict needs two conventions: an
*accounting* convention (what `lambda` is charged on) and a *labelling*
convention (what the reported class name is read off). The registered corpus
charges and labels declared bits, which is internally consistent. The adversarial
claim is therefore not that the theory is wrong, but that:

- `IV-4a` `[DERIVED-AT-FREEZE]` under the group `T1, T2, T3, T4, T5` — which
  preserves both semantics **and** declared bits — the flagship winner class set
  **survives** unchanged on all `60` registered worlds. Row 4, branch 1.
- `IV-4b` `[DERIVED-AT-FREEZE]` the **declared state-bit count is not a semantic
  invariant**: `H3_DEAD_PADDING` exhibits behaviourally identical candidates with
  different declared bits. Consequently, if accounting and labelling are drawn
  from different conventions — charge effective state, label declared state —
  the winner class set on registered worlds **changes**. The exact number of
  registered worlds whose verdict flips under that mixed convention is
  `[UNCOMPUTED]` and is reported.
- `IV-5` `[DERIVED-AT-FREEZE]` the invariant replacement is
  `bits_eff(u) = min { bits(v) : v behaviourally equivalent to u }`. Under
  consistent effective-bit accounting **and** effective-bit labelling, the verdict
  is invariant under the full group including `H3_DEAD_PADDING`. Verified
  exhaustively; the exact winner class sets under the effective convention are
  `[UNCOMPUTED]` and are reported.

Row 4 closes only if both `IV-4a` and `IV-4b`/`IV-5` land.

## Row 5 — description-length and reachability bias (frozen now)

Description grammar (frozen): a candidate's description word is its bit string —
`4` bits for a stateless table, `16` bits for a stateful `(nxt, table)` pair —
and the description length is the bit count `4` or `16`. Mutation graph (frozen):
single-bit flips inside a description word, plus the two registered
`widen` / `narrow` edges that convert between the `4`-bit and `16`-bit forms by
padding with the state-ignoring embedding and by projecting onto state `0`.
Registered start: the all-zero `4`-bit stateless word.

Quantities, all exact rationals with denominator `|U| = 65552` or a semantic
class count:

- `IV-6a` `[UNCOMPUTED]` **description-length bias**: the number of distinct
  behavioural classes in `U`, and for each class its multiplicity and its minimum
  description length. Reported as a histogram; the bias is the deviation of the
  multiplicity distribution from uniform, quantified by the exact ratio
  `max multiplicity / min multiplicity` and by the exact fraction of `U` occupied
  by the single largest class.
- `IV-6b` `[UNCOMPUTED]` **reachability bias**: for each radius `r = 0..8` the
  exact fraction of `U` within `r` mutation steps of the registered start, split
  by declared morphology class and by effective morphology class. The bias is the
  exact difference between a class's share of the ball at radius `r` and its
  share of `U`.

Both are quantities, not verdicts; the row asks to *quantify*, and the numbers are
published whatever they are.

## Two materially independent routes

- **Route A** `z3_invariance_v1.py`: builds `U` by direct simulation of every
  candidate over the `8` sequences (the same decomposition as the parent
  packages), applies each transformation to the candidate list, and re-decides
  every world by a scan over candidates.
- **Route B** `independent_invariance_oracle_v1.py`: rebuilds `U` by a different
  decomposition — a closed-form algebraic construction of `(e_now, e_delay)` from
  the table bits via per-index contribution counting, with behavioural traces
  recomputed from a reachability-closure of the state machine rather than by
  replaying sequences — and re-derives every invariance verdict, every census and
  every bias histogram from that construction. Route B imports nothing from route
  A and nothing from the Z12 or Z15 packages.

Agreement is required on: `|U|`, every `sigma`, `N_BS`, every behavioural class
count, every winner class set, every bias number, and every hostile verdict.

## Null the true result must beat

`200` seeded `H1_PSEUDO_RENAME` instances. Each is a map that *looks* like a
rename and is not. The invariance checker must **detect** each one by observing a
changed winner class set on at least one of the `60` registered worlds.

Target: `200/200` detected, `0/200` surviving undetected. If any survive, the
survivors are characterized exactly — which `sigma` vectors landed in the
declared-stateless slots, and why that leaves the verdict fixed — and the
detector is revived rather than the result being reported as green. The clean
no-alarm case is the matched run of `200` genuine `T1_RENAME` instances, which
must produce `0/200` alarms.

## Hostiles, each with the quantity it must move

| hostile | quantity | required movement |
|---|---|---|
| `H1_PSEUDO_RENAME` | winner class set over `60` worlds | must change on at least one world |
| `H2_ETA_ONLY` | `lambda*` and the verdict | `lambda*` must move by the exact factor `c`, and at least one world must flip |
| `H3_DEAD_PADDING` under mixed conventions | winner class set | must change on at least one world |
| `H4_GRAMMAR_NON_ISO` | description-length histogram and reachability fractions | must change at least one bin |
| `H5_TRUNCATED_UNIVERSE` | `|U|`, `sigma` histogram, every verdict | dropping the stateful half must change the verdict on at least one world |

A hostile that cannot move its quantity is a defect: the run fails.

## Forbidden promotions

`REPRESENTATION_INDEPENDENCE_IN_GENERAL`, `INVARIANCE_UNDER_ALL_RECODINGS`,
`SEARCH_INVARIANCE_FROM_SEMANTIC_INVARIANCE`,
`REAL_COMPILER_OR_HARDWARE_SUBSTRATE_INVARIANCE`,
`GRAMMAR_NEUTRALITY`, `COMPLETE_TRANSFORMATION_REGISTRY`,
`DECLARED_STATE_BIT_ACCOUNTING_IS_WRONG`,
`FLAGSHIP_THEORY_FALSIFIED_BY_RECODING`.

In particular: the registry is the set of transformations this package registers,
not a claim that no other transformation exists; and the non-invariance of
declared state bits is a statement about conventions, not a falsification of the
boundary law.

## Falsifiers of this package itself

- Any `CLAIMED_IRRELEVANT` transformation that moves a winner class set on clean
  data.
- Any `DECLARED_RELEVANT` transformation that cannot be shown to move its named
  quantity.
- Route A and route B disagreeing on any census, verdict, or bias number.
- A pseudo-rename surviving the detector without an exact characterization of why.
- Row 4 delivering only one of its two branches.
