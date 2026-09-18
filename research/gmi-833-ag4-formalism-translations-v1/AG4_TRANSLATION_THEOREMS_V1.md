# AG4 named results — the fifteen family pairs, adjudicated

Scope for every result below: the ten registered finite specializations of `FREEZE_V1.md`
section 2 — `8,032` objects over a two-element state space, two labels, two observations and
the frozen rational weight grid `{0, 1/2, 1}` — with behaviour decided on the window `W = 4`.
Every count is a complete enumeration; nothing is sampled.

---

## `AG4T-1` — all thirty directed translations, adjudicated

**Statement.** Of the `30` directed translations among the six families, `16` are `TOTAL` over
the source family's whole registered range and `14` are `PARTIAL` with an exact domain; none is
`EMPTY`. At the pair level: `4` are mutually total, `8` are total in one direction only, and `3`
are partial in both directions.

```text
MUTUALLY_TOTAL     A-D   B-C   B-E   C-E
TOTAL_ONE_WAY      A-B   A-C   A-E   A-F   B-D   C-D   D-E   D-F
PARTIAL_BOTH_WAYS  B-F   C-F   E-F
```

**The exact domains.** Every partial translation publishes how much of its source range it
covers, over the complete enumeration:

| translation | domain | of | obstruction |
|---|---|---|---|
| `B -> A`, `B -> D`, `B -> F` | `274` | `1,024` | blocking, nondeterminism |
| `C -> A`, `C -> D`, `C -> F` | `542` | `1,412` | blocking, nondeterminism, non-point-mass kernel |
| `E -> A`, `E -> D`, `E -> F` | `478` | `1,348` | blocking, nondeterminism, non-point-mass kernel |
| `F -> A`, `F -> B`, `F -> C`, `F -> E` | `3,728` | `4,160` | arity |
| `F -> D` | `3,728` | `4,160` | arity, monoidal structure |

**How a `PARTIAL` verdict is proved.** For every untranslatable source object the executor
searches the target family's **whole** registered range for an object with the same behaviour in
the coarsest class the pair spans, and finds none. The witnesses are re-verified by a separate
detector after the table is built; a planted witness that does in fact translate is caught in
`8` of the `14` partial entries immediately.

**Quantifiers.** For all objects of the source family's registered range.

**Falsifiers.** One `TOTAL` verdict with a behaviour mismatch; one `PARTIAL` witness that
translates after all; a verdict that changes when the window is `W - 1` instead of `W`.

**Strongest parents.** Universal algebra, structural operational semantics, the coalgebraic
treatment of state-based systems, the powerset and distribution monads, symmetric monoidal
categories and Markov kernels. The classical isomorphism between labelled transition systems and
coalgebras for the powerset functor is a parent result and is recovered here, not claimed:
`B -> C` and `C -> B` are both total.

**Forbidden extrapolations.** `ALL_PROCESS_FORMALISMS_EQUIVALENT`,
`UNIQUE_LOWEST_PROCESS_FORMALISM`, `THE_SIX_FAMILIES_ARE_EXHAUSTIVE`,
`TRANSLATION_PRESERVES_COST`.

---

## `AG4T-2` — the obstruction map is closed, and every partial verdict lands in it

**Statement.** The eight obstruction tokens were fixed before any run. Every one of the `14`
partial translations is explained by a token from that list and by nothing else; a token outside
the list is rejected by a vocabulary detector. Their incidence across the `30` directed
translations:

```text
BLOCKING_NOT_TOTAL                                 9
NONDETERMINISM_NOT_FUNCTIONAL                      9
NON_DIRAC_KERNEL                                   6
ARITY_NOT_REPRESENTABLE                            5
MONOIDAL_STRUCTURE_NOT_DERIVABLE_FROM_COMPOSITION  1
WEIGHTS_NOT_RECOVERABLE                            0
NO_CHOSEN_GENERATING_FAMILY                        0
FUNCTOR_NOT_IN_RANGE                               0
```

The three zeros are reported, not hidden. `WEIGHTS_NOT_RECOVERABLE` and
`NO_CHOSEN_GENERATING_FAMILY` never appear as obstructions because neither ever blocks a
translation at this scope: the first is a **fibre**, not a barrier, and the second is a failure of
canonicity rather than of existence. Both are measured directly in `AG4T-3` instead.
`FUNCTOR_NOT_IN_RANGE` never fires because every registered coalgebra's functor is inside the
registered range by construction.

**The monoidal obstruction has an explicit witness.** Two arity-two interfaces whose serial
content — the behaviour of the wire the serial composites act on — is identical, while their
joint behaviour differs. Serial composition therefore does not determine the tensor, and the
`1,280`-member serial class that contains them is published with the pair.

**Falsifier.** A partial translation needing an obstruction outside the eight.

---

## `AG4T-3` — two residuals that are not barriers

**Statement.** Two of the differences between the families are exact quantities rather than
obstructions, and both are published as fibres.

**Translation out of `D` is total but NOT canonical.** A monoid with an observation carries no
label indexing, so recovering a labelled action is a choice. Every `D`-object translates, and
each of the `24` presents between `1` and `13` distinct behaviours depending on which pair of
its elements is chosen for the two labels — fibre sizes `{1, 4, 6, 13}`. Every `D -> X` entry in
the table is marked `canonical: false` with `NO_CHOSEN_GENERATING_FAMILY` recorded as the
reason.

**A kernel's weights are a fibre over its support.** The `324` registered kernels present only
`102` distinct support behaviours; the largest fibre has `90` kernels sharing one support. The
weights are therefore not recoverable from the relational image, which is exactly what
`WEIGHTS_NOT_RECOVERABLE` names — but since the relational image always exists, it never blocks
a translation. Calling it an obstruction would have been a category error, and the freeze's own
definition of the token keeps it out of the obstruction column.

**Falsifiers.** A `D`-object with a unique behaviour under every labelling; a set of kernels in
bijection with their supports.

---

## `AG4T-4` — the anti-flattening control

**Statement.** The result reported here depends on each family being kept at its **own** full
expressive range. When every family is cut down to the one deterministic, total, arity-one core
they all contain — `8,032` objects reduced to `516` — all `30` directed translations become
`TOTAL` and all `15` pairs become mutually total.

That flattened table is what a universe designed to make every translation succeed would look
like, and it is what gate 4 of the freeze exists to refuse: a family set whose members are
mutually and totally interchangeable is not the six families the AG4 section lists. The control
is run every time and its result is published beside the true table.

**Consequence for the AG4 terminal.** An adjudication that produces obstructions in **both**
directions for three pairs, and in one direction for eight more, is evidence for
`MULTIPLE_FOUNDATIONALLY_EQUIVALENT_PROCESS_BASES` — the terminal AG4's own last row already
permits — and against any unique-bottom reading.
`ABSOLUTE_PROCESS_ONTOLOGY_PROVEN` stays a forbidden promotion, here as in the merged parent
`gmi-833-aj1-operational-process-base-v1`.

**Falsifier.** A run in which the flattened universe does not become mutually total, which would
mean the flattening was not a flattening.

---

## Evidence carried by every result above

**Two materially independent routes.** Route B imports neither route A nor any parent module. It
decodes objects from integer indices instead of nested products, computes behaviour by a dynamic
program over composed word-transition tables — a function table, a bitmask table, a `Fraction`
vector — instead of stepping one word at a time, decides translatability by binary search in a
sorted list instead of by set membership, recomputes the submonoids from scratch, and re-derives
every obstruction token from the object's own structure. Verdict, exact domain size,
translatable count, common class and obstruction set agree for all `30` directed translations,
as do the object counts, both histograms and the mutually-total list: **0 disagreements**.

**Six hostiles, all detected, each with a control proving it moves its quantity.** Comparing
behaviour in the source's own class instead of the coarsest common class (`16 -> 12` totals,
caught by the class rule); the universe flattened to one deterministic core (`8,032 -> 516`
objects, caught by the anti-flattening gate at `15/15` mutually total); a source range trimmed to
one specialization (`40,160 -> 11,320` source objects, caught by recomputing the range from the
generators); a witness that in fact translates (`14` planted, `8` caught); an obstruction outside
the frozen vocabulary (caught by the vocabulary check); and the observation window cut to one
letter (`16 -> 21` totals, caught by the window-sufficiency check).

**Null.** `0 / 200` randomized assignments of `TOTAL`/`PARTIAL`/`EMPTY` across the thirty
directed translations reproduce the published pattern.

**No-alarm case asserted.** On the true configuration every detector is silent: every witness
re-verifies as untranslatable, every obstruction is in the vocabulary, every common class matches
the rule, every source range recomputes from the generators, and the window at `W - 1` gives the
same thirty verdicts as at `W`.
