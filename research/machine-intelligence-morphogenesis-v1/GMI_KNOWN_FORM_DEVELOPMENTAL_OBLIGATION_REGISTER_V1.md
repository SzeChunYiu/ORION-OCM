# GMI known-form developmental obligation register v1

Status: **SUCCESSOR DESIGN AFTER OLD K4 STATIC-EVALUATOR FAILURE / NOT YET PROTECTED EVIDENCE**

Date: 2026-09-12.

Purpose: replace the old K4 capability-rubric obligations with concrete post-freeze worlds in which target-specific information can enter only through registered channels.

For every row:

1. the generic mechanism grammar is frozen first;
2. protected world `W` is drawn afterward;
3. target-specific parameters are absent from the initial machine;
4. only the declared `D` development transcript, `Q` query, and `A` external authority may reveal `W`;
5. admissibility is measured by executing the task;
6. held-out queries/episodes are never used to update the final state;
7. a target-specific program/table injected after `W` is drawn is charged as development/external intervention, not free description.

The new implementation-invariant coordinate is `target_information_source`.

## Registered families

| ID | obligation | protected world drawn after freeze | development channel `D` | serve query `Q` | authority `A` | expected target-information source | held-out score |
|---|---|---|---|---|---|---|---|
| A01 | reusable linear response | coefficient vector on frozen finite grid | labeled input/output pairs | unseen input | none | DEVELOPMENT + QUERY | prediction loss on unseen inputs |
| A02 | reusable fixed-basis / kernel response | coefficients over frozen basis/similarity dictionary | labeled examples | unseen input | none | DEVELOPMENT + QUERY | held-out prediction loss |
| A03 | arbitrary volatile recall | independent key/value records | insert/teaching events | key | none | DEVELOPMENT + QUERY | exact recall on taught protected keys plus update probes |
| A04 | uncertainty-sensitive decision | hidden-hypothesis prior/likelihood world | ambiguous observations | decision context / utility | none | DEVELOPMENT + QUERY | protected expected utility / calibrated posterior decisions |
| A05 | exact constraint satisfaction | finite constraint instance | none | complete constraint instance | none | QUERY | exact valid solution / UNSAT certificate |
| A06 | exact program/search answer | finite search/program instance and verifier | none | complete instance | none | QUERY | exact verified answer with search burden |
| A07 | nonlinear sequential dependence | finite recurrent transducer parameters | training sequences | held-out sequence/prefix | none | DEVELOPMENT + QUERY | sequence prediction/output loss |
| A08 | linear dynamical response | finite linear state-space parameters | trajectories | held-out controls/observations | none | DEVELOPMENT + QUERY | held-out trajectory/output loss |
| A09 | translation-equivariant response | local kernel/operator parameters | shifted labeled examples | held-out translated input | none | DEVELOPMENT + QUERY | held-out equivariant prediction loss |
| A10 | relational propagation | local graph update/readout rule | labeled graphs | held-out graph | none | DEVELOPMENT + QUERY | node/graph target loss |
| A11 | content-dependent mixing | content-to-dependency rule | examples exposing changing dependencies | held-out sequence/set | none | DEVELOPMENT + QUERY | dependency-sensitive output loss + routing burden |
| A12 | sparse content mixing | sparse dependency rule / support law | labeled examples | held-out sequence/set | none | DEVELOPMENT + QUERY | output loss + charged active-edge burden |
| A13 | conditional specialization | mode partition, mode-specific response laws | multi-mode examples | held-out item | none | DEVELOPMENT + QUERY | held-out loss + router/load burden |
| A14 | volatile attributable factual recall | protected external corpus and update stream | optional stable-core development only | question/key | current corpus | QUERY + EXTERNAL_AUTHORITY | exact/current answer + provenance + update burden |
| A15 | small targeted revision | low-rank update to frozen base map | post-base revision examples | held-out input | none | DEVELOPMENT + QUERY | post-update error + retained-base behavior |
| A16 | variance reduction | data distribution and noise process | bootstrap/subsample training evidence | held-out input | none | DEVELOPMENT + QUERY | held-out risk and member-correlation cost |
| A17 | certified answer under unreliable proposal | protected finite problem instance | none | problem + checker input | none | QUERY (+ RANDOMNESS for proposals, no world information) | accepted-answer error + proposal/check cost |
| A18 | goal reuse under unknown dynamics | transition/reward dynamics | exploration/transition observations | changing goal + state | none | DEVELOPMENT + QUERY | return across held-out goals + planning burden |
| A19 | single-goal control | transition/reward dynamics + fixed goal | interaction trajectory | state/observation | none | DEVELOPMENT + QUERY | held-out return |
| A20 | sequential generation | distribution parameters with natural order | iid training samples | prefix/condition | none | DEVELOPMENT + QUERY | protected log loss/sample quality + serve steps |
| A21 | joint iterative generation | protected joint distribution / score field | iid training samples | condition/noise seed | none | DEVELOPMENT + QUERY | protected distributional quality + iteration burden |
| A22 | compressed latent generation | latent decoder/manifold parameters | iid training samples | condition/noise/latent request | none | DEVELOPMENT + QUERY | protected reconstruction/generation quality + latent burden |

## 1. Null rules

The old nulls are retained, but their legal information is corrected.

### Pre-world fixed answer

Frozen before `W`; receives only legal `Q,A`. It may not contain `W`-specific parameters. This is the correct constant/fixed-function null.

### General fixed algorithm

Allowed. It may solve arbitrary `Q` without development when `Q` fully specifies the instance (A05/A06/A17 are calibration cases). Its target-information source is `QUERY`, not free hidden knowledge.

### Post-world hard-coded program/table

Allowed only as a charged comparator. Its world-specific code length / construction effort is charged to development or external intervention. It is not a zero-development null.

### Oracle

May be reported as a ceiling but is never admissible unless the corresponding authority channel is explicitly part of the obligation.

## 2. New negative twins

Every family must have at least one matched world where the predicted information source loses its advantage.

Examples:

- A01/A02: replace reusable law by independent random labels -> memory should dominate compressed coefficients.
- A03: generate records from a tiny stable law -> compression should dominate explicit record memory.
- A04: make the state fully observed or use a utility insensitive to uncertainty -> point state may suffice.
- A05/A06/A17: remove query completeness or make verification unavailable -> fixed general solver/search must fail or pay another channel.
- A09: break translation symmetry -> full/unshared representation should become competitive.
- A11/A12: make dependency graph fixed/dense -> dynamic/sparse routing advantage disappears.
- A13: make modes identical -> specialization should disappear.
- A14: make corpus tiny and static -> internalization may dominate external authority.
- A15: make revision full rank -> low-rank adaptation should lose.
- A16: make errors perfectly correlated -> ensemble gain disappears.
- A18/A19: switch between many goals and one fixed goal -> model reuse crossover.
- A20/A21/A22: change order structure, jointness, or intrinsic latent dimension -> factorization choice changes.

## 3. Family-specific finite-scope entropy registration

Every protected generator must report a lower bound on the residual target information not already carried by `Q,A`.

Examples:

```text
A01: d coefficients from q values               >= d log2 q bits before observations
A03: N independent q-valued records             = N log2 q bits
A04: M posterior-distinguishable worlds          >= log2 M bits
A08: finite matrix tuple from M registered worlds >= log2 M bits
A13: router partition x mode laws                >= log2 |registered world set| bits
A15: rank-r update drawn from finite set U        >= log2 |U| bits
```

Where the query completely specifies the instance, the residual may be zero; this is not a failure but a prediction that development is unnecessary for that obligation.

## 4. Required measurements per protected cell

```text
world generator hash
world entropy / registered lower bound
pre-world machine hash
development transcript hash and number of bits/events exposed
query information class
authority accesses
final state hash/state size
development compute
serve compute
update locality
protected quality
channel-ablation outcomes
target_information_source
```

A property-vector recovery is invalid if its target-information source is wrong even when the old ten axes match.

## 5. Fresh K4-D verdicts

```text
K4D_RECOVERY_GREEN
THEORY_RED
INCONCLUSIVE_GRAMMAR
INCONCLUSIVE_SEARCH
INCONCLUSIVE_INFORMATION_COVERAGE
TASK_FAILED
```

`K4D_RECOVERY_GREEN` requires:

1. protected quality/admissibility;
2. frozen implementation-invariant property prediction;
3. correct `target_information_source`;
4. negative twin flip;
5. strongest admissible parent comparison;
6. target-specific information legally acquired/charged;
7. registered search-coverage condition.

## 6. Relation to the failed K4 V5 sweep

The old 0/264 result is not deleted and is not converted to success. It establishes:

```text
OLD_K4_STATIC_PROPERTY_FRONTIER = RED_AT_DEVELOPMENT_SCOPE
```

The fresh programme asks a different, more causally valid question: **given no protected target knowledge at design time, what mechanism minimizes total burden after legally acquiring the information needed by the obligation?**

## Claim ceiling

This register is a successor design, not evidence.

`KNOWN_FORM_ZERO_PRIOR_DERIVATION_GREEN_AT_REGISTERED_SCOPE = FALSE`
