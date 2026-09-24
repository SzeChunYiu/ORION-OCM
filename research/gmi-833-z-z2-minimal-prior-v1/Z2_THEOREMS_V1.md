# Z2 named results — minimal unavoidable prior at registered binary-transducer scope

Scope for every result below, and never wider: the registered finite universe
`U` of `|U| = 65552` binary mechanisms (16 stateless output tables, 65536
one-bit transducers), sequence length `3`, both task modes, canonical initial
state `0`, the objective
`J = eta*p*e_delay/16 + eta*(1-p)*e_now/16 + lambda*bits` and the registered
`5x4` `(p, eta)` grid with `lambda in {lambda*/2, 3*lambda*/2}`,
`lambda* = eta*p/2`. Every quantity is an exact integer or `Fraction`.

Claim ceiling:

```
GMI_833_Z2_EXACT_ENCODING_INDUCED_PRIOR_AND_MINIMUM_SUFFICIENT_INDUCTIVE_BIAS_AT_REGISTERED_BINARY_TRANSDUCER_SCOPE
```

---

## `MP-1` — the syntactic encoding is a strictly non-uniform prior over semantics

**Statement.** Under full-behaviour equality (the 48-bit output vector over
both modes, all 8 sequences and `t in {0,1,2}` from initial state `0`), `U`
collapses to exactly `K = 21904` semantic classes. Class sizes run from `1` to
`785`. The measure that uniform-over-syntax induces on those classes is at exact
total-variation distance

```
D_TV = 3535488 / 5608793   (about 0.6304)
```

from uniform-over-classes.

**Quantifiers.** For this `U` and this semantic equality only. `K`, the
histogram and `D_TV` are properties of the registered universe, not constants of
any wider theory.

**Consequence for "prior-free".** "Search without a prior" has no referent until
a reference measure is named, and the two most natural namings — one unit of
mass per syntactic candidate, one per semantic class — are different measures at
distance `0.6304`. Choosing either is a commitment; declining to choose leaves
the phrase undefined.

**Falsifiers.** `K = |U|` (encoding not redundant) would make the two measures
coincide and refute the result; `D_TV = 0` would do the same. Both were computed,
not assumed.

**Null / no-alarm.** A control encoding with equal-sized classes returns
`D_TV = 0` from the same estimator (`N1`), and the hostile `HS7` that replaces
the real histogram with a uniform one also returns `0`. The estimator therefore
responds to the quantity it measures rather than to its own shape.

**Strongest parents.** Wolpert & Macready, *No Free Lunch Theorems for
Optimization*, IEEE Trans. Evolutionary Computation 1(1), 1997,
doi:10.1109/4235.585893 — the averaged-performance identity. Mitchell, *The
Need for Biases in Learning Generalizations*, Rutgers CBM-TR-117, 1980 — that a
bias-free learner cannot generalize. `MP-1` is not either of those: it is an
exact statement about one registered encoding's induced measure, and the parents
own the general propositions.

**Forbidden extrapolations.** `UNIVERSAL_NO_FREE_LUNCH_PROVED`,
`SEMANTIC_CLASS_COUNT_IS_A_UNIVERSAL_CONSTANT`.

**Assumptions.** The registered universe `U` of `FREEZE_V1.md` section 1, taken
from `research/gmi-833-heldout-20-transitions-v1`: `65552` candidates, sequence
length `3`, both modes and canonical initial state `0`. Semantic equality is
equality of the 48-bit full-behaviour vector `beh`, and the two measures
compared are uniform-over-syntax (`n_c / |U|`) and uniform-over-classes (`1/K`);
exact integers and `Fraction` only (`FREEZE_V1.md` section 10).

**Dependencies.** Hypotheses `H1` and `H2` with their falsifiers (`FREEZE_V1.md`
section 5), the control encoding `N1` (section 7) and the hostile `HS7` (section
8); the universe pinned in `MANIFEST_V1.json` from
`research/gmi-833-heldout-20-transitions-v1`; the `MP1_encoding_prior` block of
`RESULT_V1.json`, recomputed by route B, which keys semantics by an
independently computed 48-bit integer. The behavioural quotient itself is the
Nerode (1958) / Myhill (1957) construction credited in `PARENT_DISCLOSURE_V1.md`
section 1.

---

## `MP-2` — a family-blind enumeration order is a very large commitment

**Statement.** In canonical index order, the first member of some semantic class
is reached at probe `1` and the first member of another at probe `65547`; the
ratio is exactly `65547`. An enumerative search that claims to prefer nothing
still reaches one behaviour immediately and another only after exhausting almost
the entire universe.

**Quantifiers.** This order, this universe. A different order gives a different
profile — which is the point, and is `MP-5`'s `H7d` witness.

**Falsifier.** A ratio below `100` would have refuted the hypothesis as frozen.

**Assumptions.** The universe and the `K = 21904` semantic classes of `MP-1`;
candidates are probed one at a time in the registered canonical index order, and
a class's first hit is the probe number of its first member in that order. The
ratio is a property of this order and this universe only, as the Quantifiers
paragraph says.

**Dependencies.** The semantic classes of `MP-1`; hypothesis `H4` and its frozen
threshold `100` (`FREEZE_V1.md` section 5); the `MP1c_enumeration_order` block
of `RESULT_V1.json`, matched by route B; `MP-5`'s `H7d` witness, which shows the
first-hit profile moving under `g_rename`.

**Strongest parents.** No parent is registered for `MP-2` specifically in
`PARENT_DISCLOSURE_V1.md`. The nearest are Wolpert & Macready (1997), whose
averaged-performance identity is stated over non-repeating searches, and the
family-blind recovery protocol of `research/gmi-833-blind-recovery-v2-v1`, whose
enumerative searches carry an order of this kind; `MP-2` is an exact finite
profile, not a general theorem.

---

## `MP-3` — zero bits of preference is exactly chance; one bit is not

**Setting.** `36` frozen held-out prediction problems; the learner sees the
outputs of an unknown target on the observation set and must emit the held-out
bit; the target ranges over all `65552` candidates, giving `2359872` scored
pairs. Of these, `453744` are *determined* — the version space carries only one
held-out value, so every learner is right for free — and `1906128` are
*undetermined*. The determined fraction is exactly `3151/16388`.

**Statement.**

| commitment | exact undetermined accuracy |
|---|---|
| none: no preference and no reference measure | `1/2` |
| one bit of structural preference, best of `12 + 288` | `23315/39711` (about `0.5871`) |
| one bit of structural preference, worst of `12 + 288` | `5671/11346` (about `0.49982`) |
| a full uniform measure over the `65552` candidates | `80663/119133` (about `0.6771`) |
| a full uniform measure over the `21904` classes | `80663/119133` (identical) |

The best one-bit preference is `out_depends_on_state AND NOT
next_depends_on_input`; the worst are the `9` specifications containing
`next_depends_on_state`. So at this scope **one bit of structural preference is
enough to beat chance and enough to fall below it**: bias is both unavoidable and
not automatically benign.

**The minimum unavoidable bias, stated exactly.** On the undetermined
subpopulation a learner with no preference is pinned to `1/2` — not by
convention but because the version space contains both answers and nothing in
the learner's input separates them. One bit suffices to exceed it. The minimum
is therefore exactly one bit at this scope, and the quantity it buys is
`23315/39711 - 1/2 = 3459/39711` of exact accuracy.

**Null.** `200` pseudo-random one-bit structural features (seeds `4100..4299`):
`159` land strictly above `1/2`, `41` exactly at `1/2`, `0` below, and `0` reach
the best registered or swept feature; the best null is `274345/476532` (about
`0.5757`). The finding that one bit helps is therefore generic in direction but
the *magnitude* of the best structural feature is not reproduced by any random
one, and the sub-chance half is not generic at all — no random feature achieves
it, only structured ones do.

**Falsifiers.** A registered or swept feature at or below `1/2` for the upper
claim; a null at or above the best feature for the non-genericity claim; any
determined/undetermined bookkeeping error, which both routes recompute
independently.

**Forbidden extrapolations.** `MINIMUM_BIAS_IS_UNIVERSALLY_ONE_BIT`,
`REAL_SYSTEM_LEARNABILITY`, `BIAS_CANNOT_HURT_IN_GENERAL`.

**Assumptions.** The `36`-problem held-out family and the version-space learner
of `FREEZE_V1.md` section 3, with the target ranging over all of `U`; accuracy
is scored on the undetermined subpopulation, and one bit of preference is the
preference-only learner `L_f_pure`, which abstains for `1/2` unless the
preferred part of the version space is unanimous (`FREEZE_V1_AMENDMENT_2.md`
section 2). The one-bit alphabet is the `12` registered features `B1`..`B12`
plus the exhaustive `288`-feature one- and two-literal sweep over `V12`
(`FREEZE_V1_AMENDMENT_3.md`).

**Dependencies.** Hypotheses `H6'`, `H10` (`FREEZE_V1_AMENDMENT_2.md`), `H6''`
and `H11` (`FREEZE_V1_AMENDMENT_3.md`); the null `N2` and the leakage guard `N4`
with hostile `HS4` (`FREEZE_V1.md` sections 7-8); the vocabulary `V12` of
`FREEZE_V1_AMENDMENT_1.md`; `MP-1`'s semantic classes, used by `L_sem` and by
`B9`..`B12`; the `MP2_minimum_bias` block of `RESULT_V1.json`, whose
determined/undetermined split both routes recompute.

**Strongest parents.** Mitchell, *The Need for Biases in Learning
Generalizations* (1980), which owns the proposition that a learner with no bias
cannot generalize; `MP-3` is its exact finite instance on one universe and one
frozen prediction family (`PARENT_DISCLOSURE_V1.md`). Blumer, Ehrenfeucht,
Haussler & Warmuth (1987) own compression-bias learnability guarantees; no Occam
bound or sample-complexity claim is made here.

---

## `MP-4` — the two natural reference measures are decision-identical here

**Statement.** Over all `36` problems, the candidate-weighted majority and the
class-weighted majority issue **different** predictions on exactly `0` version-
space buckets, in both the full and the undetermined population, and their exact
accuracies coincide (`54511/73746` full, `80663/119133` undetermined).

**Why it is recorded as a refutation.** The freeze hypothesised `H5`: that the
two measures would disagree, and that the disagreement would be the sharpest
evidence that "prior-free" is ill-posed. It does not disagree. The
ill-posedness argument survives on `MP-1` (the measures differ, at `D_TV`
`0.6304`) and `MP-3` (a preference-free learner is pinned at `1/2`), but the
decision-level leg is gone and is published as gone.

**Forbidden extrapolation.** `REFERENCE_MEASURE_CHOICE_IS_ALWAYS_DECISION_IRRELEVANT`
— this is a fact about this universe and this prediction family.

**Assumptions.** The `36`-problem family and version-space buckets of `MP-3`,
with the two majority learners of `FREEZE_V1.md` section 3: `L_syn` weights each
syntactic candidate equally and `L_sem` each semantic class present, ties broken
to `0`. The comparison is made on both the full and the undetermined population.

**Dependencies.** Hypothesis `H5` (`FREEZE_V1.md` section 5) and `H5'`
(`FREEZE_V1_AMENDMENT_2.md`); the semantic classes of `MP-1`; `A_syn_*`,
`A_sem_*` and `disagreeing_buckets_*` in the `MP2_minimum_bias` block of
`RESULT_V1.json`, matched by route B. The surviving ill-posedness argument rests
on `MP-1` and `MP-3`, as stated above.

**Falsifiers.** The frozen falsifier of `H5'` is a count of `0` disagreeing
buckets, which is what was measured, so `H5` and `H5'` stand refuted. The
recorded result itself would be overturned by one version-space bucket on which
the two majorities predict differently, or by unequal exact accuracies on either
population, in either route.

**Strongest parents.** No parent is registered for the decision-level comparison
itself; the nearest are the parents of `MP-1` and `MP-3`, Wolpert & Macready
(1997) and Mitchell (1980) (`PARENT_DISCLOSURE_V1.md`). The forbidden promotion
`REFERENCE_MEASURE_CHOICE_IS_ALWAYS_DECISION_IRRELEVANT`
(`FREEZE_V1_AMENDMENT_3.md` section 4) keeps this a fact about this universe and
this prediction family.

---

## `MP-5` — what a P3/P4 derivation may lean on, and what it may not

**Statement.** Three re-encodings of `U`, each verified a bijection — `g_rename`
(index permutation), `g_state` (state-bit relabeling), `g_out` (global output
complement) — give the invariance table

| quantity | `g_rename` | `g_state` | `g_out` |
|---|---|---|---|
| `K`, class histogram, `D_TV` | invariant | invariant | invariant |
| multiset of `(e_now, e_delay, bits)` | invariant | invariant | invariant |
| `min J` and the winning property class, all `40` grid cells | invariant | invariant | invariant |
| per-candidate class membership | **moves** | **moves** | **moves** |
| canonical-order first-hit profile | **moves** | invariant | invariant |

**The standard.** At this scope a P3 derivation claim is defensible exactly when
its quantity lies in the invariant block: the behaviour multiset, the semantic
class structure, and the optimum and winner of the declared objective. A claim
about candidate identity, enumeration order or syntactic description length is
not defensible at P3, because the registered re-encodings move it while changing
nothing about the mechanism population.

**The P4 clause.** P4 ("the grammar may create or compress primitives
recursively") does not enlarge the defensible block. A primitive re-compression
changes the encoding map and therefore only quantities of candidate identity and
description cost — exactly the block `g_rename` already moves. The defensible
criterion for P3 and for P4 is therefore the same invariance criterion, and P4's
additional expressive power lies entirely outside it. This package does **not**
exercise a recursive primitive-compression grammar: the `V12` vocabulary is fixed
and non-recursive, and no P4 certificate is claimed.

**`H7c` refuted.** The freeze predicted that `g_out`, which does not preserve
the task targets, would move `min J` or the winner and so exhibit an
inadmissible re-encoding. It does not: `U` is closed under output complement, so
the multiset of `(e_now, e_delay)` is carried to itself and `J`, a function of
that multiset alone, is fixed. No registered generator is inadmissible, and the
existence of an inadmissible re-encoding at this scope is left explicitly
unproven rather than asserted.

**Hostile.** `HS2`, a non-bijective "re-encoding", is detected by the group-action
guard; the guard was shown to fire before the table was trusted.

**Forbidden extrapolation.** `P3_CERTIFICATE_IMPLIES_NECESSITY`.

**Assumptions.** The three generators `g_rename`, `g_state` and `g_out` of
`FREEZE_V1_AMENDMENT_1.md`, each verified a bijection of `U` before use; the
objective `J` and the registered `5x4` `(p, eta)` grid of
`research/gmi-833-heldout-20-transitions-v1`; the `P0..P4` ladder of issue #837,
taken as given. The P4 clause is an argument about encoding maps, not an
exercise of a recursive primitive-compression grammar, and no P4 certificate is
claimed.

**Dependencies.** Hypotheses `H7a`..`H7e` (`FREEZE_V1_AMENDMENT_1.md`) and the
`H7c` refutation recorded in `FREEZE_V1_AMENDMENT_2.md` section 3; `MP-1` (`K`,
histogram, `D_TV`) and `MP-2` (first-hit profile) for the tabulated quantities;
the hostile `HS2` and its group-action guard; the `MP4_p3_standard` block of
`RESULT_V1.json`, matched by route B.

**Falsifiers.** Registered with `H7a`..`H7e`: any invariant-block quantity
moving under a generator, or per-candidate membership or the first-hit profile
staying fixed where the table says it moves, would change the table and so the
standard read from it; a generator failing the bijection check voids its column.
A registered generator that moved `min J` or the winner would reverse the `H7c`
refutation.

**Strongest parents.** Rissanen, *Modeling by shortest data description* (1978),
whose tradition owns the observation that description-length quantities depend
on the code; issue #837 owns the `P0..P4` ladder definitions
(`PARENT_DISCLOSURE_V1.md`). `MP-5` only computes which registered quantities
move under which registered re-encoding.

---

## `MP-6` — known forms recovered from one generic vocabulary

**Statement.** One primitive vocabulary `V12` of twelve generic predicates over
`(state, mode, input)` dependence and one grammar (conjunction of literals,
`3^12 = 531441` specifications, grammar digest byte-identical across all six
runs) selects **exactly** the member set of each registered named family:

| family | members | selected |
|---|---:|---|
| `F_STATELESS` | `16` | exact |
| `F_DEAD_TABLE` | `4096` | exact |
| `F_FROZEN_STATE` | `512` | exact |
| `F_MOORE` | `4096` | exact |
| `F_MEALY_PURE` | `61440` | exact |
| `F_IDENTITY_STATE` | `256` | exact |

No specification contains a family-name token; the lexical no-smuggling audit
returns zero hits on all six and fires on the planted hostile `HS3`. No
per-family grammar change occurs: the vocabulary, the enumerator and the digest
are the same object in all six runs, and only the literal assignment differs.

**Null.** `200` specifications drawn uniformly from the `531441`-element space
(seeds `4300..4499`) select exactly a registered family member set in `0` cases.
The recovery is therefore not an artifact of a space in which hitting a family is
easy.

**Strongest parents.** Moore, *Gedanken-experiments on sequential machines*,
Automata Studies, Princeton 1956; Mealy, *A method for synthesizing sequential
circuits*, Bell System Technical Journal 34(5), 1955,
doi:10.1002/j.1538-7305.1955.tb03788.x — the named forms and their defining
properties are theirs, not this package's. The family-blind recovery protocol is
owned by `research/gmi-833-blind-recovery-v2-v1` and the `gmi-833-aj9*` series;
this package contributes the exact one-vocabulary recovery over the registered
transducer universe with the `3^12` null attached.

**Forbidden extrapolation.**
`ARCHITECTURE_FAMILY_RECOVERY_BEYOND_REGISTERED_UNIVERSE`,
`MLP_CNN_TRANSFORMER_CLASSIFIED`.

**Assumptions.** The registered universe `U` and the six named families with the
member sets registered by `research/gmi-833-z-z7-impossibility-v1`; the fixed,
non-recursive vocabulary `V12` and the grammar of conjunctions of literals
(`3^12` specifications) pinned in `FREEZE_V1_AMENDMENT_1.md` before it was run.
Exact means that a specification's member set over `U` equals the family's
member set.

**Dependencies.** Hypothesis `H8` (`FREEZE_V1.md` section 5, made exact by
`FREEZE_V1_AMENDMENT_1.md`), the null `N3` (seeds `4300..4499`) and the lexical
no-smuggling audit with hostile `HS3`; the family member sets of
`research/gmi-833-z-z7-impossibility-v1` (pinned in `MANIFEST_V1.json`) as
ground truth; the `MP5_known_form_recovery` block of `RESULT_V1.json`, matched
by route B.

**Falsifiers.** Registered with `H8`: any family whose specified set differs
from its member set, or a grammar digest that moves between the six runs. A
family-name token in any specification (the `HS3` audit), or a large `N3` hit
count, would remove the meaning of the recovery.

---

## `MP-7` — the flagship corpus carries no informal `prior-free` claim

**Statement.** Over `453` markdown files under `research/gmi-833-*` at
`source_main` `5e57d4292266bccf435136e1f7d72caa32e920a0`, the token `prior-free`
occurs `88` times, classified as `AUTHORITY 40`, `QUALIFIED_TERM 29`,
`MIRROR 13`, `NEGATION 5`, `MENTION_NOT_USE 1`, and `LIVE_FLAGSHIP 0`.

**Parent ownership.** The corpus edit that produced this state belongs to
`research/gmi-833-terminology-migration-v1` (`MIGRATION_LOG_V1.md`,
`MIGRATION_LOG_V2.md`), and the literature audit backing the replacement term
belongs to `research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`
rows 9 and 26, which cite Wolpert & Macready 1997 and Mitchell 1980 and fix the
migration rule *never bare "prior-free"*. Neither is re-earned here.
`MP-7` is the **verification instrument**: the classifier and its validation.

**Instrument validation.** `4` planted live-flagship shapes (plain, bolded,
line-wrapped, and a bare assertion) all fire; `6` planted non-live shapes
(negation, qualified term, checklist mirror, backticked mention, cross-line
negation, bolded negation) are all classified away from `LIVE_FLAGSHIP`; a
known-clean line raises no occurrence at all.

**The instrument failed first.** Its first real run flagged three
`LIVE_FLAGSHIP` sites. All three were classifier defects — a backticked mention
read as a use, a negation whose marker sat on the previous physical line, and a
negation broken by markdown bold — and the validation gate had passed because
none of those shapes was planted. See `FREEZE_V1_AMENDMENT_4.md`.

**Forbidden extrapolation.** `TERMINOLOGY_MIGRATION_RE_EARNED_HERE`.

**Assumptions.** The corpus is every markdown file under `research/gmi-833-*`,
and the counts above are timestamped at `source_main`
`5e57d4292266bccf435136e1f7d72caa32e920a0`: any lane that adds or removes the
audited token moves them (`CORE.md`). Each occurrence is classified into exactly
one of the categories of `FREEZE_V1.md` section 6 as extended by
`FREEZE_V1_AMENDMENT_4.md`, after markdown emphasis is normalised and at
sentence scope; what CI asserts is the verdict, not the counts.

**Dependencies.** Hypothesis `H9` and the site categories of `FREEZE_V1.md`
sections 5-6, repaired by `FREEZE_V1_AMENDMENT_4.md`; the hostile `HS5`; the
instrument `prior_free_site_audit_v1.py`, its receipt
`PRIOR_FREE_SITE_AUDIT_V1.json` and the CI verdict check
`check_row3_verdict_v1.py`; the corpus state produced by
`research/gmi-833-terminology-migration-v1` and rows 9 and 26 of
`research/gmi-833-tranche-ab-ac-lit/GMI_TERMINOLOGY_CROSSWALK_V2.md`, both
pinned in `MANIFEST_V1.json`.

**Falsifiers.** Registered as `H9`'s falsifier: one or more occurrences
classified `LIVE_FLAGSHIP` in the live corpus, which `check_row3_verdict_v1.py`
tests on every run. Independently, a planted live-flagship shape that fails to
fire, or a planted non-live shape or known-clean line that raises an alarm,
voids the instrument, as its first run showed (`FREEZE_V1_AMENDMENT_4.md`).

**Strongest parents.** `research/gmi-833-terminology-migration-v1`, which owns
the corpus edit, and `GMI_TERMINOLOGY_CROSSWALK_V2.md` rows 9 and 26, which own
the literature audit (citing Wolpert & Macready 1997 and Mitchell 1980) and the
migration rule, as the Parent ownership paragraph states. Neither is re-earned;
`MP-7` is only the verification instrument.

---

## What none of these results establish

Nothing about real or trained systems; no universal no-free-lunch theorem; no
claim that one bit is the minimum bias outside this universe and this prediction
family; no claim about MLP, CNN or Transformer families; no P4 certificate; no
claim that the registered re-encoding group is complete; and no re-earning of
the terminology migration, the transition law `lambda* = eta*p/2`, or the
blind-recovery protocol.
