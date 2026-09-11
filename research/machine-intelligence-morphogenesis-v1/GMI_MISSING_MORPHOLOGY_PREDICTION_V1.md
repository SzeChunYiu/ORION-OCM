# GMI Missing-Morphology Prediction v1 — Versioned Local Compilation (VLC)

Status date: 2026-09-11.

Status: **PROSPECTIVE PROPERTY-FIRST PREDICTION. THIS FILE MUST BE FROZEN BEFORE ANY CONFIRMATORY VLC MORPHOLOGY SEARCH OR SCORED CONFIRMATORY MICRO-EXPERIMENT.**

This is Track B's first serious attempt to move from explanatory synthesis to a morphology prediction that can fail.

The prediction is deliberately about **realization properties**, not an architecture name. A catchy name is useful only as a handle after the properties are frozen.

Exploratory disclosure: during protocol design, a small non-confirmatory cost-model pilot using a different seed/configuration was inspected to check that the proposed measurement machinery is numerically sane. No pilot row may count toward any acceptance terminal below. Confirmatory seeds/configurations are frozen in `GMI_PREDICTIVE_EXPERIMENT_PROGRAMME_V1.md` and must be executed only after this prediction is committed.

---

## 1. Expert review lenses used before freezing

Five independent hostile lenses were applied to the prediction:

1. **formal / learning theory** — checks that the prediction follows from pre-outcome obligation structure rather than architecture labels;
2. **continual learning** — checks retention, plasticity, local interference and long-horizon update economics;
3. **systems / PL / verification** — checks incremental rebuild, versioning, proof/verification boundaries and serving/update separation;
4. **morphogenesis / architecture search** — checks that the target is recoverable from neutral primitives without naming the answer;
5. **parent-subtraction / novelty** — checks MoE, modular continual learning, TMS/ATMS, SISA/unlearning, knowledge compilation, probabilistic circuits, neuro-symbolic systems, program/library learning, proof-carrying code and dynamic software-update parents.

Consensus before freeze:

- the property vector is **predictable from GMI demand coordinates**;
- each component has strong parents;
- the conjunction is scientifically testable as a morphology class;
- novelty over parent products is **not established** and must be earned after recovery.

---

# 2. Target demand regime

Use the obligation-side signature from `GMI_REALIZATION_DEMAND_SIGNATURE_V0.md`:

\[
\Xi(\Omega)=(\sigma,\delta,\gamma,\nu,\chi,\eta,\lambda,\pi).
\]

The predicted morphology region is characterized by the following conjunction.

## R* — revocable high-reuse local-dependency regime

```text
sigma   high      many future-relevant distinctions; flat global state is expensive
delta   low       evidence/update effects have small true descendant cones
gamma   mixed     some subproblems provide dense learnable credit; others only exact/sparse checks
nu      medium-high  assumptions/data/operators are frequently invalidated or revised
chi     strong/local  verifier can certify local replacements or counterexamples
eta     high      successful cognition is reused many times, so compilation/amortization matters
lambda  strict    unrelated old competence must remain stable while fresh competence is acquired
pi      heterogeneous  serving throughput and update/revision cost both matter
```

The important tension is:

> `eta` says **compile/amortize aggressively**, while `nu + low delta + strict lambda` say **do not entangle the whole machine in each update**.

A single monolithic dense realization can exploit `eta` well but tends to pay more for exact local invalidation/revision. A purely explicit symbolic/recompute realization can localize revision but can give up too much serving amortization in statistical/high-throughput subproblems. GMI therefore predicts a realization that separates developmental authority from disposable fast execution artifacts at **local semantic factor** scale.

---

# 3. Predicted morphology properties

The target is provisionally called **Versioned Local Compilation (VLC) morphology**.

A candidate counts as matching the prediction only if all mandatory properties P1–P6 are present as measured behaviors; source-code labels are irrelevant.

## P1 — sparse semantic factorization

Persistent developmental state is split into independently addressable factors/modules whose boundaries approximately align with measured dependency/intervention locality.

Prediction:

```text
update blast radius / total persistent state << 1
```

in the R* regime.

## P2 — authority / serving separation

Each factor has an authoritative developmental representation and may also have one or more disposable compiled/amortized serving realizations.

Compiled state is not the sole source of truth.

This allows expensive cognition/learning to be paid once and reused while retaining an auditable update boundary.

## P3 — local rebuild / unlearning cone

When a factor is revised, withdrawn or contradicted, only its registered dependency cone and downstream compiled artifacts are invalidated/rebuilt in the ordinary case.

The primary scaling prediction is:

\[
B_{revise}^{VLC}=O(|Cone(u)|)+\text{local recompilation}
\]

rather than routine whole-system retraining/reconstruction.

No asymptotic novelty is claimed until the comparator assumptions are formalized.

## P4 — verify-before-swap versioning

Updates are staged in a shadow/new version, checked under the external verifier, then atomically adopted. The previous version remains available until adoption succeeds.

Predicted consequence under strict `lambda`:

```text
unaffected-query regression during an update approaches the routing/dependency false-localization rate,
not the raw rebuild duration.
```

## P5 — stable typed composition/routing boundary

Factor interfaces and composition/routing are explicit enough that updating factor `i` does not silently rewrite the meaning of unrelated factor interfaces.

The router itself may learn, but the R* prediction is that high-frequency content updates and global routing updates occur on separated timescales; otherwise local update isolation collapses.

This is consistent with recent MoE continual-learning theory showing that continual convergence can require stopping/fixing the router after sufficient training, but VLC does not assume an MoE implementation.

## P6 — local realization polymorphism

Where the local demand signature differs, different factors may use different internal realizations while sharing the same contract/dependency/version protocol.

Examples allowed by the prediction include:

```text
learned differentiable factor
symbolic / program factor
probabilistic factor
retrieval/memory factor
compiled exact rule/table/circuit
```

P6 is a **secondary** prediction. P1–P5 are the mandatory core.

---

# 4. Lifecycle phase derivation

For a coarse two-realization comparison, let

```text
A_M      fixed acquisition/build cost of morphology M
c_M      per-query serving cost
u_M      cost of an update/revision if the whole relevant realization is rebuilt
U        number of update events
H        number of useful queries/uses
alpha_M  expected fraction of M rebuilt per local update
v_M      version/verification overhead per update
```

Then a first-order lifecycle approximation is

\[
C_M=A_M+Hc_M+U(\alpha_M u_M+v_M).
\]

For a monolithic realization, ordinary local invalidation may have `alpha_mono` near 1 under exact-revision obligations. For a locality-aligned factored realization, `alpha_VLC` tracks the measured dependency cone fraction `delta` plus router/composition overhead.

For two candidates `VLC` and `G`, the crossover occurs when

\[
(A_{VLC}-A_G)+H(c_{VLC}-c_G)
+U[(\alpha_{VLC}u_{VLC}+v_{VLC})-(\alpha_Gu_G+v_G)] = 0.
\]

Writing `U = nu H` gives the update-rate boundary

\[
\boxed{
\nu^*
=
\frac{(A_{VLC}-A_G)/H+(c_{VLC}-c_G)}
{\alpha_Gu_G+v_G-\alpha_{VLC}u_{VLC}-v_{VLC}}
}
\]

when the denominator is positive.

This equation is ordinary lifecycle economics, not claimed novel mathematics. Its role is to make the morphology prediction quantitative and falsifiable:

- below `nu*`, a more globally amortized realization can dominate;
- above `nu*`, locality-aligned versioned compilation should move toward the frontier **if** `delta` remains small and `lambda/chi` make exact safe revision valuable.

---

# 5. Negative-twin predictions

A valid theory prediction must say where the morphology should **not** appear.

## T1 — stationary / very low invalidation

Set `nu -> 0` while preserving large `eta`.

Prediction:

```text
more globally amortized / integrated realizations move toward the frontier;
versioning/local-rebuild overhead loses value.
```

## T2 — dense dependency cone

Raise `delta` toward 1 so local changes truly affect most future consequences.

Prediction:

```text
VLC's local-rebuild advantage collapses;
coarser or global realization should move toward the frontier.
```

## T3 — weak retention / weak verifier

Relax `lambda` and/or make local verification expensive/uninformative.

Prediction:

```text
verify-before-swap and duplicate-version overhead should be rejected more often.
```

## T4 — short reuse horizon

Reduce `eta` sharply.

Prediction:

```text
compiled serving artifacts become less attractive;
cheap recompute / minimally built local factors move toward the frontier.
```

A morphology search that produces VLC-like properties equally in all twins is a failure of the phase prediction or evidence of search-encoding bias.

---

# 6. Parent-subtraction table

VLC is **not** declared new merely because it combines known ideas.

| Parent | Already owns | What VLC must show beyond it |
|---|---|---|
| sparse MoE / modular continual learning | specialization, sparse routing, reduced interference | exact/local revision economics + versioned verify-before-swap + authoritative/compiled separation under the same phase law |
| SISA / machine unlearning | partitioned retraining and cheaper removal | semantic dependency-aligned update cones, persistent cognition, composition and morphogenesis rather than only training-data removal |
| TMS / ATMS | dependency/justification tracking and local belief revision | high-throughput amortized learned/compiled cognition under the same local authority semantics |
| knowledge compilation / Soar chunking | compile expensive reasoning into faster rules | continual dependency-aware invalidation + versioned local replacement + cross-realization developmental state |
| probabilistic circuits | factorization and tractable exact inference | persistent local revision/morphogenesis and mixed realization response under registered lifecycle constraints |
| neuro-symbolic systems | mixed neural/symbolic components | property-first local factor boundaries, bounded update cone, versioned replacement and phase prediction rather than a fixed two-layer hybrid |
| program/library learning | reusable abstractions and amortized search | local revocation/verification/retention law and mixed runtime realization |
| proof-carrying code / certifying compilation | external verification of compiled artifacts | experience-driven cognition, local developmental state and morphology adaptation |
| dynamic software update / transactional deployment | versioned safe replacement | learned cognition, semantic developmental factors and ecology-conditioned morphogenesis |

A positive experiment can at first support only:

```text
THEORY_PREDICTED_VLC_PROPERTY_VECTOR_RECOVERED_AT_SCOPE
```

It cannot claim `NEW_FORM_OF_MACHINE_INTELLIGENCE` until bounded-compilation/reduction attacks against this table fail.

---

# 7. Confirmation ladder

```text
V0  qualitative phase reversal in exact finite microscope
V1  quantitative boundary prediction on disjoint confirmatory micro-regimes
V2  parent portfolio experiment: VLC-like design reaches frontier only in R* and loses in negative twins
V3  neutral low-level morphology search recovers P1-P5 without named VLC macros
V4  morphology predicted before search (U4 in UNKNOWN_MORPHOLOGY_PROGRAMME_V1)
V5  disjoint ecology replication
V6  alternate search implementation / encoding replication
V7  bounded developmental compilation/reduction attacks fail against strongest parent products
```

Only V4+ begins to support a genuine predictive morphogenesis result. V7 is required before using language stronger than “theory-predicted distinct morphology candidate.”

---

# 8. Frozen claim

Before confirmatory execution, Track B predicts:

> **In high-reuse cognitive ecologies with frequent truly local invalidation, strong local verification and strict retention, the frontier should shift toward a morphology that stores authoritative cognition in sparse dependency-aligned factors and serves through disposable locally compiled versions that are rebuilt and externally verified before atomic replacement. The same morphology should lose its advantage when invalidation vanishes, dependency cones become global, retention/verification are weak, or reuse horizon is short.**

Current prospective terminal:

```text
MISSING_MORPHOLOGY_PROPERTY_VECTOR_PREDICTED_BEFORE_CONFIRMATORY_SEARCH
VLC_NOVELTY_NOT_ESTABLISHED
CONFIRMATORY_EXECUTION_PENDING
```
