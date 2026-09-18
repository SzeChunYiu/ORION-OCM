# AE13 named results v1

Scope, fixed by `FREEZE_V1.md`: three binary variables, all **25** labelled
DAGs, every conditional probability table drawn from the frozen rational grid
`{0, 1/4, 1/2, 3/4, 1}` — **547,625** structural causal models in total — and
single-variable atomic interventions taken by truncated factorisation. Every
probability is an exact integer numerator over `64` (observational) or `16`
(truncated), or a `Fraction`. No float appears anywhere.

---

## CI-1 — observational data does not *generally* identify causal structure

**Statement.** The 25 DAGs partition into **11** Markov equivalence classes.
For **every one of the 7** classes containing more than one DAG there exist two
parameterisations of **different** member DAGs whose observational joints agree
on **all 8 atoms** as exact rationals while their interventional answers differ.
Census: **80,788,144** such cross-DAG disagreeing pairs over **26,601** joints
realised by two or more DAGs of one class, out of **99,033** distinct joints.

**Both quantifiers are carried.** The **4** singleton classes — the empty graph
and the three colliders — **are** identified, and their pair counts are reported
as `0` rather than omitted. The claim is therefore *not generally identified*
and never *never identified*; `OBSERVATIONAL_DATA_NEVER_IDENTIFIES_CAUSAL_STRUCTURE`
is a registered forbidden promotion.

**Assumptions.** Causal sufficiency (no latent confounders), three binary
variables, the frozen CPT grid, single-variable atomic interventions.

**Falsifiers.** A multi-DAG class in which no grid parameterisation yields a
disagreement — this is exactly what a first query set produced for the `A–B`
class, and the cause was the **query set**, not causality: no registered query
touched that skeleton. The query set now covers every skeleton and the receipt
says so.

**Strongest parents.** Verma & Pearl 1990; Andersson, Madigan & Perlman 1997
(doi:10.1214/aos/1031833662); Pearl 2009. `PARENT_SUFFICIENT` on the
equivalence characterisation itself.

**Forbidden extrapolations.** `CAUSAL_DISCOVERY_IMPOSSIBILITY_PROVED`,
`LATENT_CONFOUNDER_GENERAL_CASE_PROVED`,
`CONTINUOUS_VARIABLE_EXTENSION_PROVED`.

---

## CI-2 — the named equivalence class, enumerated exhaustively

**Statement.** `A → C` and `C → A` with `B` isolated, `P(A=1) = 1/2`,
`P(C=1|A=1) = 3/4`, `P(C=1|A=0) = 1/4`. The joint
`(3/16, 1/16, 3/16, 1/16, 1/16, 3/16, 1/16, 3/16)` sums exactly to `1` and is
reproduced by exactly **1** grid parameterisation of the other DAG, found by
exhaustive search rather than by inversion. `ACE_A_on_C` is `1/2` under the
first and `0` under the second; `ACE_C_on_A` is `0` and `1/2`. The
identification interval of each is the whole `[0, 1/2]`.

**Falsifier.** A member of the class whose answer falls outside the reported
interval. The interval is min/max over the exhaustively enumerated class, so
none exists at this scope.

---

## CI-3 — when interventions are required

**Statement.** Interventions are required for a specification `(query, tol)`
**iff** the half-width of the query's identification interval over the
observational equivalence class exceeds `tol`.

**Tested on both sides and at the boundary.** With worst-case half-width `1/2`:
required at `tol = 31/64`, **not** required at `tol = 1/2` exactly, not required
at `33/64`. The equality case is exhibited rather than skipped — a threshold
rule that never shows its boundary has not been tested there.

**Census.** Per query, **5,356** of **26,601** joint groups have a
non-degenerate interval and **21,245** are identified observationally. The four
registered queries give **identical** counts, which is forced: the census is
invariant under every relabelling of `{A, B, C}` and the six ordered variable
pairs form a single orbit, so the equality is a consistency check on the census
rather than a coincidence.

---

## CI-4 — the value of intervention, and its zero

**Statement.** An atomic intervention answers its own query exactly, so its
value is exactly half the identification-interval width; acquire iff that
exceeds the price. The worst case over the census is `1/2`.

**Intervention is not universally worth its cost.** **84,980** query-group
specifications have value of intervention exactly `0`, and one is **named** in
the receipt: `ACE_C_on_A` on a joint realised by all **25** DAGs, identified
answer `0`, interval width `0`. `INTERVENTION_ALWAYS_WORTH_ITS_COST` is a
registered forbidden promotion, and the exhibited zero is what forbids it.

---

## CI-5 — predictive state is not causal/control state

**Statement.** On the confounded subfamily `B → A`, `B → C`, `A → C` the
predictive state — the partition of the four `(A,B)` contexts by `p(C=1|A,B)` —
and the causal/control state — the partition by the interventional response
vector `(p(C=1|do(A=0)), p(C=1|do(A=1)))` at that context — are different
objects. Over the **2,187** strictly positive models (**75,938** excluded for a
zero atom, the exclusion reported):

| relation | count |
|---|---:|
| `INCOMPARABLE` | 1,458 |
| `PREDICTIVE_STRICTLY_REFINES` | 486 |
| `EQUAL` | 243 |
| `CAUSAL_STRICTLY_REFINES` | **0, proved** |

**The zero is proved, not merely unobserved.** The causal state separates only
the two values of the context `b`, so its partition has at most two blocks and
they are exactly the two `b`-classes. For it to *strictly* refine the predictive
partition, the predictive partition would have to be the single block — all four
conditionals equal — but then the two causal vectors coincide as well, the
causal partition is also the single block, and the relation is `EQUAL`, not
strict. No search could have found one.

**Forbidden extrapolation.** Reading this as a claim that prediction never helps
control. It says only that the two sufficiency notions are distinct partitions.

---

## CI-6 — strongest-parent audit, and the conflation this row exists to prevent

Six crosswalk entries, each with a citation, **3** terminating
`PARENT_SUFFICIENT` (recorded as successes). The sixth entry is the substantive
one: the computational-mechanics **causal state** (Shalizi & Crutchfield 2001,
doi:10.1023/A:1010388907793) is a **purely predictive** equivalence class of
histories with the same conditional future. It carries **no** interventional
content and is **not** the Pearlian causal structure. Sibling package
`gmi-833-ae-ae5-causal-state-audit-v1` earns the computational-mechanics rows;
this package earns the interventional ones, and
`COMPUTATIONAL_MECHANICS_CAUSAL_STATE_IS_PEARLIAN_CAUSAL_STATE` is a registered
forbidden promotion so the two cannot be silently merged later.

---

## Hostiles, each potent before detected

| id | what it corrupts | effect |
|---|---|---|
| `H1_read_intervention_off_observation` | estimates `P(A\|do(C))` by `P(A\|C=1) − P(A\|C=0)` in a world where `C` does not cause `A` | true `0`, hostile `1/2` |
| `H2_skeleton_only_equivalence` | compares skeletons and ignores v-structures | merges a collider with a fork; class count moves off `11` |
| `H3_condition_instead_of_truncate` | conditions where it should truncate, in a genuinely confounded model | `P(C=1\|do(A=1))` moves |
| `H4_single_member_interval` | reports one class member's answer as the class answer | collapses `[0, 1/2]` to a point |
| `H5_freeze_provenance` | asserts a freeze commit that is not the pinned one | caught by the workflow |

`H3` was initially **not potent** — the parameterisation it used had `P(A=1|B)`
independent of `B`, so there was no confounding and truncating and conditioning
agreed. That is recorded here because it is the exact failure mode the
potent-before-detected rule exists to catch: a hostile that cannot move the
quantity proves nothing about the detector.

## Null

Detector: *the registered causal query is not pinned to a point by the
observational joint across the world's Markov equivalence class.*

- **Clean controls**: `729` SCMs on the collider `A → C ← B`, the unique member
  of its Markov class, so the query **is** identified — **0/729** false alarms.
- **Planted positives**: `20` SCMs on `A → C` in which `A` is a fair coin and
  `C` is a symmetric noisy copy of it, so the Bayes inversion lands on the
  frozen grid and the `C → A` twin exists **by construction**. The premise is
  **verified** in the receipt (`20/20` twins found), not asserted — **20/20**
  recall.

An earlier planted family — `A → C` models with arbitrary grid CPTs — gave only
`6/81` recall, because for most of them no grid parameterisation of `C → A`
reproduces the joint at all. That family was not planted; it was discarded
before anything was reported.
