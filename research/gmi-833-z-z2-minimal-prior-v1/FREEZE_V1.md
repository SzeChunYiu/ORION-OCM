# GMI #833 Section Z / Z2 — minimal unavoidable prior: pre-implementation freeze

Committed **before** any executor, oracle, test, receipt or result file of this
package exists. Nothing below was computed; every number named here is either a
registered constant taken from an on-`main` parent or an explicitly hypothesised
value that the enumeration may refute.

- `source_main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue: SzeChunYiu/ORION-OCM#833, Section Z, issue comment `5684819296`
- branch: `research/833-sec-z3`
- freeze written: 2026-09-18T15:53:32Z

## 0. Claim ceiling

```
GMI_833_Z2_EXACT_ENCODING_INDUCED_PRIOR_AND_MINIMUM_SUFFICIENT_INDUCTIVE_BIAS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

**No neighboring row is earned here.** This tranche may reconcile exactly the
five `- [ ] ` rows under the `### Z2 — Minimal unavoidable prior / architecture-agnostic derivation`
anchor of issue comment `5684819296`, reproduced verbatim:

```
- [ ] Prove or characterize why literally prior-free search is impossible/ill-posed.
- [ ] Define the minimum unavoidable inductive/computational bias required for learnability/searchability.
- [ ] Replace informal `prior-free` language in flagship claims with a defensible term such as `architecture-agnostic`, `architecture-uncommitted`, or `minimal-architecture-prior`, based on literature audit.
- [ ] Establish the strongest P3/P4 derivation standard that can be defended mathematically.
- [ ] Demonstrate known-form recovery without architecture-specific primitives or per-family grammar redesign.
```

No row of Z1, Z3, Z4, Z5, Z6, Z7 or any other subsection is earned here, and no
row of the issue **body** is earned here.

## 1. Registered universe (taken from parents, not invented here)

`U` = the registered finite binary mechanism universe already used by
`research/gmi-833-heldout-20-transitions-v1` (freeze commit
`ddb3df7a44a6a4fb47fdc362a1fa02e34b7a3a75`) and by
`research/gmi-833-z-z7-impossibility-v1`:

- sequence length `L = 3`, all `2^3 = 8` input sequences, two modes
  (`0` = immediate copy of the current bit, `1` = delayed recall of the
  previous bit), scored at `t = 1, 2` giving `N = (L-1) * 2^L = 16` scored
  moments per mode;
- `16` stateless candidates (output table on `(mode, cur)`, 4 bits);
- `65536` one-bit stateful candidates (`nxt` and `table`, each a truth table on
  `(state, mode, cur)`, 8 bits each);
- `|U| = 65552`.

Registered objective (from the same parent):
`J(c) = eta * p * e_delay(c)/N + eta * (1-p) * e_now(c)/N + lambda * bits(c)`
with the registered boundary law `lambda* = eta*p/2` at the property level.
This package does **not** re-derive that law and does not re-earn its rows.

**Full-behaviour vector** (the semantic object of this package, fixed here):
`beh(c)` is the `2 * 8 * 3 = 48`-bit tuple of outputs emitted by `c` at every
`(mode, sequence, t)` with `t in {0,1,2}`, from canonical initial state `0`.
Two candidates are *semantically equal* iff `beh` is equal. `K` denotes the
number of resulting classes; `K` is **unknown at this freeze**.

## 2. Registered structural feature vocabulary (the bias alphabet)

A *1-bit structural bias* is a function `f : U -> {0,1}` drawn from this frozen
list, used as "prefer `f(c) = 0`":

```
B1  bits(c) == 0                      (Occam-on-state)
B2  bits(c) == 1                      (anti-Occam-on-state)
B3  popcount(table) <= 4              (sparse output table)
B4  popcount(table) > 4
B5  nxt is None or nxt in {0,255}     (state never changes)
B6  not B5
B7  index(c) < |U|/2                  (enumeration-order half)
B8  index(c) >= |U|/2
```

No other feature may be promoted to "the minimum bias" without being added to
this list in a committed amendment.

## 3. Held-out prediction family (frozen before any counting)

`P` = the family of prediction problems `(O, m)` where the observation set `O`
is the set of ALL scored moments of mode `0` together with the mode-`1` moments
of the first `k` sequences in lexicographic order, and the held-out moment `m`
is the mode-`1` moment at `t = 2` of sequence `s` for each `s` not among those
first `k`. `k` ranges over `0..7`; `s` ranges over the remaining sequences.
`|P|` is therefore `sum_{k=0..7} (8-k) = 36` problems. This is fixed now.

A *learner* sees `O` and the observed outputs of an unknown target `c* in U`,
forms the version space `V = {c in U : c agrees with c* on O}`, and must emit a
bit for `m`. Accuracy is measured with `c*` ranging over **all** of `U`, so the
score is an exact rational with denominator `|U| * |P|`.

Three reference learners are frozen:

- `L_free` — preference-free: emits a fair coin, scoring exactly `1/2` by
  definition. It is a *definitional* baseline and is labelled as such, never
  counted as a discovered result.
- `L_syn` — majority over `V` counted with **uniform weight per syntactic
  candidate**;
- `L_sem` — majority over `V` counted with **uniform weight per semantic class**
  present in `V`.

Ties are broken to `0` in both majority learners; the tie-break is part of the
freeze.

## 4. Re-encoding group (for the P3/P4 standard)

`G` = the group generated by (a) the 2 relabelings of the state bit
(`s -> 1-s`, applied consistently to `nxt` and `table` addressing), and (b) the
8 permutations of the candidate *index* space that preserve `beh` fibres.
Element (a) is a genuine re-encoding of the mechanism; element (b) is a pure
renaming. A quantity is **P3-defensible** iff it is invariant under all of `G`.

## 5. Frozen hypotheses — each may be refuted by the enumeration

| id | statement | falsifier |
|---|---|---|
| `H1` | `K < 65552`, i.e. the syntactic encoding is strictly redundant over semantics | `K = 65552` |
| `H2` | the exact total-variation distance `D_TV` between the syntax-induced semantic prior (`n_c / |U|`) and uniform-over-classes (`1/K`) is strictly positive | `D_TV = 0` |
| `H3` `[NAIVE]` | `max_c n_c >= 2 * min_c n_c` | the ratio is `< 2` |
| `H4` | for the canonical index order, the ratio (last-class first-hit index) / (first-class first-hit index) is `>= 100` | ratio `< 100` |
| `H5` | `A_syn != A_sem` on the frozen family `P`, i.e. the two natural "no-preference" reference measures give different exact accuracies | `A_syn == A_sem` |
| `H6` | some feature in §2 gives accuracy `> 1/2` AND some feature in §2 gives accuracy `< 1/2` | one of the two directions is empty |
| `H7` | the semantic-class partition and the `argmin` set of `J` over the registered `5x4` `(p,eta)` grid are invariant under every element of `G`, while the canonical-order first-hit ranking is NOT invariant under at least one element of `G` | no non-invariance witness exists |
| `H8` | one fixed primitive set and one fixed property-first specification language, containing no family-name token, selects exactly the member set of each of the 6 registered named families (`F_STATELESS`, `F_DEAD_TABLE`, `F_FROZEN_STATE`, `F_MOORE`, `F_MEALY_PURE`, `F_IDENTITY_STATE`), with a byte-identical grammar digest across all 6 runs | any family's selected set differs from its member set, or the digest moves |
| `H9` | in the live `research/gmi-833-*` corpus at `source_main`, the number of sites where bare `prior-free` appears as **live flagship prose** is `0`, every residual site falling in one of the frozen categories of §6 | `>= 1` live site |

`H3` is marked `[NAIVE]` because it is a guess about a distribution nobody has
computed; it is written down so that its refutation is a recorded result rather
than a silent edit.

## 6. Frozen site categories for the terminology audit (row 3)

A residual occurrence of bare `prior-free` in `research/gmi-833-*` is classified
into exactly one of:

- `MIRROR` — the file is a byte-snapshot/mirror of an issue body or comment
  (`*MIRROR*`, `*SNAPSHOT*`, `comments/comment_*.md`, and this package's own
  quotation of the Z2 rows);
- `AUTHORITY` — the file is the terminology authority itself (crosswalk,
  banned-terms list, migration freeze/log, CI gate) where the banned token is
  definitional;
- `QUALIFIED_TERM` — the occurrence is inside a hyphen-bound registered term
  (`architecture-prior-free`) or a named condition (`P3/P4 prior-free
  condition`) that the crosswalk sanctions;
- `NEGATION` — the sentence explicitly denies prior-freeness ("does not mean
  prior-free", "literally prior-free is ill-posed");
- `LIVE_FLAGSHIP` — none of the above: bare `prior-free` asserted as a property
  of the work. This is the category `H9` claims is empty.

The classifier is validated before its verdict is used: a planted
`LIVE_FLAGSHIP` sentence must fire, and the known-clean set must produce no
alarm.

## 7. Nulls (the true result must beat them)

- `N1` (encoding prior): a **control encoding** is constructed whose semantic
  classes are equal-sized by construction; the same `D_TV` estimator must return
  exactly `0` on it. A positive `D_TV` on the control would prove the estimator,
  not the universe, is the source of the finding.
- `N2` (minimum bias): `200` structural features drawn pseudo-randomly from
  seeds `4100..4299` (each a random subset predicate on the candidate's raw
  bits) are scored on `P`. The registered best feature must beat the null
  distribution; if a majority of random features also beat `1/2` by the same
  margin, the finding is generic and must be reported as such.
- `N3` (known-form recovery): `200` pseudo-random property specifications from
  seeds `4300..4499` are run through the same selector; the count that selects
  exactly a registered family member set is recorded. The recovery claim is only
  meaningful if this count is small.
- `N4` (learner leakage): the version-space construction is checked to be
  independent of the held-out moment — a learner that reads `m`'s true output
  must be detectable.

## 8. Hostiles — each must be shown able to fire before any verdict is trusted

| id | deliberate defect | the check that must flag it |
|---|---|---|
| `HS1` | semantic equality redefined as equality of `(e_now, e_delay)` only | class-count guard: `K` must match the `beh`-based definition of §1 |
| `HS2` | a "re-encoding" that is not a bijection of `U` | group-action guard: permutation check on `G` elements |
| `HS3` | a property specification carrying a family-name token (`moore`, `mealy`, `stateless`, `transformer`, ...) | lexical no-smuggling audit over the spec vocabulary |
| `HS4` | a learner that peeks at the held-out moment | leakage guard `N4`: accuracy exactly `1` and version space unchanged by `m` |
| `HS5` | a document containing a planted live flagship `prior-free` sentence | site classifier must return `LIVE_FLAGSHIP` |
| `HS6` | a bound of the Z7 `C4` shape — an inequality over quantities confined to its own codomain | vacuity classifier must return `NON_BINDING` |
| `HS7` | the class histogram replaced by a uniform one | `D_TV` must move to `0` (proves `D_TV` responds to the quantity it measures) |

Every hostile is required to *move the quantity it perturbs*; a hostile that a
checker flags for an unrelated reason does not count as detected.

## 9. Two materially independent routes

Route A (`z2_minimal_prior_v1.py`) replays every candidate over the 8 sequences
and both modes, builds `beh` by simulation, and decides every hypothesis by
scanning the resulting list.

Route B (`independent_minimal_prior_oracle_v1.py`) does not import Route A. It
reconstructs the universe algebraically from the truth-table bit patterns, keys
semantics by an independently computed 48-bit integer, and recomputes `K`,
`D_TV`, `A_syn`, `A_sem`, the feature scores and the family member sets by a
different traversal order. Both routes must agree exactly on every reported
number before any verdict is emitted.

## 10. Arithmetic discipline

Exact integers and `fractions.Fraction` only. No float appears in any claim.
Stdlib only; both routes and the test run under `python3 -I -B` and the test
additionally under `python3 -I -O -B` on Python 3.8.

## 11. Forbidden promotions

```
PRIOR_FREE_SEARCH_EXISTS
UNIVERSAL_NO_FREE_LUNCH_PROVED
MINIMUM_BIAS_IS_UNIVERSALLY_ONE_BIT
REAL_SYSTEM_LEARNABILITY
ARCHITECTURE_FAMILY_RECOVERY_BEYOND_REGISTERED_UNIVERSE
MLP_CNN_TRANSFORMER_CLASSIFIED
TERMINOLOGY_MIGRATION_RE_EARNED_HERE
P3_CERTIFICATE_IMPLIES_NECESSITY
PARENT_RESULTS_RE_EARNED_HERE
SEMANTIC_CLASS_COUNT_IS_A_UNIVERSAL_CONSTANT
```

The corpus edit that removed bare `prior-free` from flagship prose belongs to
`research/gmi-833-terminology-migration-v1`, and the literature audit backing
the replacement term belongs to
`research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md` rows 9 and
26. This package contributes only the *verification instrument* for row 3 and
reconciles the row by citing those parents; it does not re-earn them.
