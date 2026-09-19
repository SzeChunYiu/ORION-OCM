# GMI #833 Section Z / Z4 — universality classes of machine intelligence:
# pre-implementation freeze

Committed **before** any executor, oracle, test, receipt or result file of this
package exists. Every definition and hypothesis below is fixed now; none was
read off an enumeration.

- `source_main`: `5e57d4292266bccf435136e1f7d72caa32e920a0`
- issue: SzeChunYiu/ORION-OCM#833, Section Z, issue comment `5684819296`
- branch: `research/833-sec-z3`

## 0. Claim ceiling and the exact rows in scope

```
GMI_833_Z4_RESOURCE_RESPONSE_UNIVERSALITY_CLASSES_AND_SURVIVING_DISTINCTIONS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

**No neighboring row is earned here.** This tranche may reconcile exactly three
of the five `- [ ] ` rows under the `### Z4 — Universality classes of machine intelligence`
anchor of issue comment `5684819296`, reproduced verbatim:

```
- [ ] Define class membership by scaling/resource/developmental behavior rather than names.
- [ ] Search for universal exponents, frontiers or asymptotic forms where mathematically justified.
- [ ] Determine which morphology distinctions remain scientifically irreducible after quotienting implementation details.
```

The other two rows of `Z4` are **deliberately left open** and this freeze
forbids this package from touching them:

```
- [ ] Test whether many named architectures collapse into broader GMI universality classes.
- [ ] Determine whether MLP/CNN/Transformer/etc. are fundamental GMI classes or implementations inside broader classes.
```

Row 4 names MLP, CNN and Transformer and carries no *where justified* clause.
Answering it from a binary transducer universe whose named families are Moore
and Mealy would be closure by narrowing. Row 1 says "many named architectures"
with no scope clause either, and the issue's own enumeration of named
architectures is row 4's list; answering row 1 from the registered transducer
families would be the same move. Both stay open. Row 3, by contrast, carries
the explicit clause **where mathematically justified**, which is what licenses a
scoped answer there.

## 1. Registered universe and budget ladder

The registered binary mechanism universe of
`research/gmi-833-heldout-20-transitions-v1`: sequence length `L`, two task
modes, canonical initial state `0`, `16` stateless output tables and
`256 * 256` one-bit transducers.

The **budget ladder** swept by this package is

```
state bits    b in {0, 1}                       2 rungs
sequence len  L in {2, 3, 4}                    3 rungs
```

`2 * 3 = 6` ladder cells. The number of rungs on each axis is reported in the
receipt as an explicit integer, because row 3's answer depends on it.

## 2. Row 2 — class membership by resource/scaling behaviour, defined now

A candidate's **resource-response profile** is the tuple

```
RRP(c) = ( (kn(L), kd(L)) for L in {2, 3, 4},
           dominance(c, L) for L in {2, 3, 4} )
```

where `kn(L)`, `kd(L)` are the exact integer error counts on the immediate and
delayed channels at sequence length `L`, and `dominance(c, L)` is `1` iff `c`
lies on the exact Pareto frontier of `(kn, kd, bits)` at that `L`, else `0`.
Nothing in `RRP` is a name: it is error behaviour as the resource axis moves,
plus the candidate's position relative to the frontier at each rung.

Two candidates are in the same **resource-response class** iff `RRP` is equal.
A stateless candidate is lifted to every `L` by the same table; a stateful one
is replayed at each `L` from state `0`.

**Vacuity guard, required before any verdict is used.** A class definition is
degenerate if it puts every candidate in one class or every candidate in its
own. The class-count and the class-size histogram are published, and the
definition is declared non-degenerate only if the largest class holds strictly
fewer than the whole universe and the number of singleton classes is strictly
less than the number of classes.

## 3. Row 3 — frontiers, exponents, asymptotics

Three questions, each with a fixed answer criterion:

- **Frontiers**: the exact Pareto frontier of `(kn, kd)` within each state-bit
  block at each `L`, and within each registered named family. Reported as exact
  integer sets. This half is delivered unconditionally.
- **Exponents**: an exponent is *mathematically justified* only if the axis it
  is fitted on has enough rungs to identify it and the quantity is not exactly
  determined by a closed form. The rung counts of §1 are printed beside the
  verdict. A power law fitted to a `2`-rung or `3`-rung ladder is not
  identified, and the honest answer is a refusal **with the rung count stated**.
- **Asymptotic forms**: where a quantity has an exact closed form in `L`, that
  closed form is the asymptotic answer and no fitting is involved. The frozen
  candidates are: the minimum delayed error count attainable without state, and
  the minimum attainable with one bit.

## 4. Row 5 — "scientifically irreducible", defined now

A distinction between two sets of candidates is **irreducible after quotienting
implementation details** iff it satisfies **both**:

1. it survives the **semantic quotient** — the two sets are not merged by
   behavioural equality (equal `48`-bit behaviour vectors at `L = 3`), i.e. some
   behaviour class lies wholly in one set and some wholly in the other, and no
   behaviour class straddles them; and
2. it survives **every registered re-encoding generator** — `g_rename`,
   `g_state`, `g_out` of `research/gmi-833-z-z2-minimal-prior-v1`, in the sense
   that the *behavioural* content of the distinction (the set of behaviour
   classes on each side, and the attainable `(kn, kd, bits)` frontier of each
   side) is carried to itself.

A distinction failing (1) is an implementation detail. A distinction passing (1)
but failing (2) is an encoding artifact. Only both is irreducible.

The distinctions tested are the pairwise separations among the six registered
named families `F_STATELESS`, `F_DEAD_TABLE`, `F_FROZEN_STATE`, `F_MOORE`,
`F_MEALY_PURE`, `F_IDENTITY_STATE`, plus the `bits = 0` / `bits = 1` split.

## 5. Frozen hypotheses — each may be refuted

| id | statement | falsifier |
|---|---|---|
| `U1` | the resource-response class definition is non-degenerate by the §2 guard | largest class is the whole universe, or every class is a singleton |
| `U2` | the number of resource-response classes is strictly between the number of behaviour classes at `L = 3` and the number of registered named families | it falls outside that interval |
| `U3` | the `bits = 0` / `bits = 1` split is **irreducible** by the §4 definition | it fails either clause |
| `U4` | the `F_MOORE` / `F_MEALY_PURE` split is **irreducible** by the §4 definition | it fails either clause |
| `U5` `[NAIVE]` | every one of the `15` pairwise family separations is irreducible | at least one collapses |
| `U6` | at least one registered family separation **fails** clause 1 — i.e. some named distinction is an implementation detail, not a behaviour | all fifteen survive clause 1 |
| `U7` | the minimum delayed error count attainable without state is exactly `(L-1) * 2^(L-1)` at every `L` in `{2,3,4}`, i.e. exactly half the scored moments, and the minimum with one bit is exactly `0` | any rung disagrees |
| `U8` | the `(kn, kd)` Pareto frontier of `F_MOORE` and that of `F_MEALY_PURE` differ at `L = 3` | they coincide |
| `U9` | no exponent is identified on either ladder axis, because both have fewer than `4` rungs; the receipt prints `2` and `3` | a rung count differs from those integers |

`U5` is marked `[NAIVE]`: it is a guess, written down so that its refutation is
a recorded result. `U6` is its deliberate opposite, so that exactly one of them
must survive.

## 6. Nulls

- `N1` (the class definition is not measuring noise): `200` pseudo-random
  partitions of the universe with the same class-count as `RRP`, seeds
  `7100..7299`, are tested against clause 1 of §4 for the `bits` split; a random
  partition must almost never respect a behavioural boundary.
- `N2` (irreducibility is not free): `200` pseudo-random bipartitions of the
  universe, seeds `7300..7499`, are run through the full §4 test; the count that
  comes out irreducible is reported. If most random splits are irreducible the
  criterion is vacuous.
- `N3` (the frontier is real): the frontier computation is re-run on a shuffled
  copy of the universe and must return the same set.

## 7. Hostiles — each must be shown able to fire

| id | deliberate defect | the check that must flag it |
|---|---|---|
| `HS1` | a class definition keyed on the candidate index (a name in disguise) | the `RRP` no-name guard: the profile must be invariant under `g_rename` |
| `HS2` | a "Pareto frontier" that includes a dominated point | frontier soundness check |
| `HS3` | an irreducibility verdict from clause 1 alone | both clauses must be recorded separately per distinction |
| `HS4` | an exponent reported from a `2`-rung ladder | rung-count guard |
| `HS5` | a degenerate class definition (all-one or all-singletons) | the §2 vacuity guard |

## 8. Two materially independent routes

Route A (`z4_universality_v1.py`) replays every candidate at every `L` and
decides every class, frontier, distinction and null by scanning the resulting
list. Route B (`independent_universality_oracle_v1.py`) does not import Route A:
it rebuilds the universe in a different order, keys profiles by a different
type, computes frontiers by pairwise domination instead of by sorting, and
derives the stateless delayed minimum analytically rather than by enumeration.

## 9. Arithmetic and forbidden promotions

Exact integers only; no float appears in any claim; stdlib only; runs under
`python3 -I -B` and `python3 -I -O -B` on Python 3.8.

```
MLP_CNN_TRANSFORMER_CLASSIFIED
NAMED_ARCHITECTURES_COLLAPSE_PROVED
UNIVERSAL_EXPONENT_FOUND
ASYMPTOTIC_LAW_BEYOND_L4
CLASS_DEFINITION_IS_CANONICAL
IRREDUCIBILITY_BEYOND_REGISTERED_RE_ENCODINGS
Z4_ROW1_OR_ROW4_EARNED
PARENT_RESULTS_RE_EARNED_HERE
```
