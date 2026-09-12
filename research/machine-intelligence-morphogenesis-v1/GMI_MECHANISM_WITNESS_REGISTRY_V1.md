# GMI Mechanism Witness Registry v1

Status: **PROSPECTIVE BEHAVIORAL MEASUREMENT CONTRACT — NOT EMPIRICAL EVIDENCE**

Status date: 2026-09-12.

Refs:

- `GMI_CAUSAL_MECHANISM_PHASE_THEORY_V1.md`
- `GMI_REALIZATION_DEMAND_SIGNATURE_V1.md`
- `GMI_MISSING_MORPHOLOGY_PREDICTION_V1.md`
- `GMI_PREDICTIVE_EXPERIMENT_PROGRAMME_V1.md`

Purpose:

> Define the realization mechanisms predicted by GMI using behavioral/semantic tests that can be applied after neutral morphology search without rewarding literal architecture names or one privileged implementation encoding.

This registry is intentionally stricter than source-code classification.

---

# 1. General scoring rules

For every mechanism witness:

```text
W1  score semantics/behavior, not class/file/component names;
W2  score on protected interventions not used to design the candidate;
W3  meter all hidden preprocessing/rebuild/checkpoint/index cost;
W4  require matched semantic adequacy/capability floor;
W5  report confidence/uncertainty and censored failures;
W6  distinguish “mechanism absent” from “cannot identify from available probes”;
W7  allow multiple implementation-equivalent realizations;
W8  do not infer one witness from another merely because they co-occur in VLC.
```

Allowed witness states:

```text
PRESENT_AT_THRESHOLD
ABSENT_AT_THRESHOLD
PARTIAL_<value>
NOT_IDENTIFIABLE_WITH_REGISTERED_PROBES
NOT_APPLICABLE_AT_SCOPE
```

---

# 2. Registered semantic scopes

Before scoring a candidate, freeze an architecture-neutral semantic scope set

\[
\mathcal S = \{S_1,\ldots,S_n\}
\]

or an equivalent quotient/intervention basis derived from the obligation.

Also freeze:

```text
query scopes Q
update/intervention scopes U
protected unaffected scopes U_bar
verifier/admission events V
historical/branch probes B when beta_lin > 0
```

The candidate does not get to choose these scopes after its behavior is observed.

---

# 3. A1 — factor/materialization partition witness

## Semantic question

> Does the realization expose independently replaceable/materializable regions aligned with obligation-relevant semantic scope, rather than requiring one inseparable global serving/developmental artifact for ordinary local variation?

## Why this is not A3

A candidate can have explicit modules but still rebuild/update all modules together.

A candidate can have one physical model file yet support sparse replaceable internal artifacts.

A1 measures replaceable/materialized organization; A3 measures update work/locality.

## Behavioral witness

For each registered local semantic scope `S_i`, search only within the allowed probe protocol for the smallest realization support whose replacement/rebuild can alter protected behavior on `S_i` while preserving protected behavior outside its true semantic consequence set.

Let normalized replaceable-support size be

\[
r_i
=\frac{|Supp^{replace}_M(S_i)|}{|Z_M|}
\]

under a prospectively declared state/resource measure.

Define an A1 locality score, for example,

\[
a_1
=1-E_i[r_i]
\]

only where `|Z_M|` and support are meaningfully comparable.

For opaque families where support is not identifiable, use an interventionally defined replaceability/resource test rather than inventing pseudo-modules.

## Failure controls

```text
renaming tensor slices as modules without independent replacement
one checkpoint file containing genuinely local independently swappable regions
external hidden state that actually performs the partition
```

The first should not create A1; the second should not erase it; the third must be charged/included.

---

# 4. A2 — developmental authority vs derived serving-state separation

## Semantic question

> Can disposable serving materialization be destroyed/rebuilt without destroying the developmental information required for legal future learning/revision?

## Behavioral witness

Freeze an allowed serving-artifact invalidation operation.

A2 is supported when:

```text
1. serving artifact is removed/corrupted/invalidated;
2. persistent developmental state remains;
3. the serving artifact can be reconstructed to registered semantic equivalence;
4. future legal update/revision ability remains equivalent within tolerance;
5. reconstruction uses only declared/charged inputs and resources.
```

Measure:

```text
rebuild success probability
rebuild burden
post-rebuild semantic equivalence
post-rebuild developmental equivalence
external information reacquired
```

## Strong witness

Serving state is a derived cache/materialization with no unique developmental information at the registered scope.

## Counterexample

If deleting the serving artifact destroys optimizer/provenance/latent developmental information that cannot be reconstructed without replaying uncharged history, A2 is absent or only partial.

---

# 5. A3 — dependency-tracked incremental repair witness

## Semantic question

> Does realized update work track the true affected semantic consequence set rather than routine global recomputation?

Let registered update `u` have true semantic cone

\[
C(u)\subseteq\mathcal S.
\]

Measure complete update/rebuild/verification work

\[
B_M^{update}(u)
\]

and, where identifiable, work/state changes outside the true cone.

Candidate scores:

\[
a_3^{blast}
=1-
E_u\left[
\frac{|Touched_M(u)\setminus Map(C(u))|}
{|Z_M|}
\right]
\]

and a scaling response

\[
B_M^{update}(u)
\quad\text{vs}\quad
|C(u)|.
\]

A3 is stronger when update burden follows cone size across prospectively varied cones with small intercept/overhead relative to global rebuild.

## Required hostile

Hold physical partition fixed while making semantic dependencies dense.

If update work remains artificially local despite the true protected cone becoming global, suspect semantic under-checking or benchmark mismatch.

---

# 6. A4 — speculative candidate isolation witness

## Semantic question

> For a rejectable update, does the incumbent admitted state remain semantically available/recoverable until external admission succeeds?

## Acceptance protocol

For each protected rejectable update:

```text
1. record incumbent semantic state S_old;
2. begin candidate construction;
3. issue protected queries during construction/verification;
4. force/observe a verifier rejection;
5. issue the same protected queries after rejection;
6. repeat for accepted candidates.
```

A4 strong witness requires:

```text
pre-admission protected queries observe S_old (or the explicitly allowed snapshot semantics);
rejection leaves/restores exact registered incumbent semantics;
acceptance changes authority only after the admission event;
all rollback/staging information and work are metered.
```

Define

\[
a_4
=1-P(\text{unauthorized incumbent-semantic change before admission})
\]

with exact `a4=1` required when the obligation is exact.

## Implementation-equivalence requirement

The witness must accept, when semantically equivalent:

```text
shadow copy
copy-on-write
undo/redo log
persistent root/pointer swap
transactional workspace
other reversible staging
```

The witness is not “number of full copies.”

---

# 7. A5 — historical/branch persistence witness

## Applicability

Score A5 only when `beta_lin` registers historical/branch/coexisting-state obligations or when measuring optional persistence economics.

## Semantic question

> After successful admissions, can the required old/branched semantic states still be addressed according to the registered lineage contract?

Freeze probes such as:

```text
as-of historical query
branch-specific query
rollback-to-admitted-state
provenance lineage query
concurrent snapshot query
```

Define exact success over registered required history set `H_req`:

\[
a_5
=\frac{1}{|H_{req}|}
\sum_{h\in H_{req}}
1[\text{required semantic state }h\text{ is exactly recoverable/addressable}].
\]

Also meter:

```text
storage growth
lookup burden
garbage-collection/retirement burden
merge/conflict burden where applicable
```

## Critical distinction

A candidate may have `a4=1, a5=0` if it stages safely but discards all old state after admission.

A candidate may have `a4=0, a5=1` if it preserves history but exposes unverified updates immediately.

Do not infer either from the other.

---

# 8. A6 — interface/routing semantic stability witness

## Semantic question

> When a local semantic scope changes, do unrelated composition/routing contracts retain their registered meaning?

Before a local update `u`, freeze protected composition probes on:

```text
unaffected local scopes
cross-scope compositions not semantically downstream of u
routing/selection decisions whose correct semantics should remain invariant
```

After update, measure semantic contract drift.

Define, for exact scope,

\[
a_6
=1-P(\text{unjustified interface/routing semantic drift outside }C(u)).
\]

For approximate obligations use the prospectively frozen semantic distance/admissibility contract.

Also meter the amount of global router/interface retraining required per local content update.

## Failure control

A router may remain numerically unchanged while the meaning of its inputs/outputs silently changes.

Therefore source-code immutability is not sufficient; score semantic composition behavior.

---

# 9. A7 — local realization heterogeneity witness

Status: **SECONDARY / HARDER TO IDENTIFY**.

## Semantic question

> Do different local semantic scopes use materially different realization response classes under one shared composition/authority contract, and is that heterogeneity economically justified?

Do not score heterogeneity from class names such as `NeuralModule` or `SymbolicModule`.

Possible operational evidence:

```text
different local transition/update kernels with prospectively distinguishable response behavior;
different resource-response curves under matched semantic probes;
different verifier/learning mechanisms whose behavior cannot be reduced to superficial encoding changes within the registered equivalence;
```

A7 should remain `NOT_IDENTIFIABLE` unless the experiment freezes a valid realization-equivalence test.

Heterogeneity is not automatically beneficial; it must improve the registered frontier after composition and maintenance cost.

---

# 10. Mechanism vector

For candidate `M`, report

\[
\phi(M)
=
(a_1,a_2,a_3,a_4,a_5,a_6,a_7)
\]

with uncertainty/status metadata.

Do not force all values to binary.

A threshold vector

\[
\tau=(\tau_1,\ldots,\tau_7)
\]

may be frozen for discrete mechanism-core scoring.

The threshold must be set on development worlds or parent/measurement calibration, not after protected morphology outcomes.

---

# 11. Frontier mechanism core scoring

Given protected near-frontier set

\[
\mathcal F_\epsilon(c),
\]

define empirical mechanism core estimate

\[
\widehat K^*(c)
=
\{k:\forall M\in\mathcal F_\epsilon(c),\;a_k(M)\ge\tau_k\}
\]

subject to uncertainty.

When confidence intervals cross thresholds, report uncertainty rather than forcing a label.

Suggested statuses:

```text
CORE_SUPPORTED
CORE_REJECTED
CORE_UNCERTAIN
OPTIONAL_SHELL
NOT_IDENTIFIABLE
```

---

# 12. Mechanism causal-ablation protocol

A source-code ablation is not automatically a causal mechanism intervention.

For candidate mechanism `A_k`, require:

```text
same semantic obligation
same capability floor
matched resource/search budget where possible
same other mechanism witnesses within preregistered tolerance
only A_k changed, OR joint changes explicitly reported
```

If removing an implementation component simultaneously changes A1, A3 and A6, the experiment identifies a joint bundle, not the isolated effect of A1.

Use paired constructions or multiple implementations when possible.

---

# 13. Mechanism equivalence tournament

For A4/A5 in particular, E1/E3 should include multiple low-level realizations.

Example tournament:

```text
E-A  full shadow artifact
E-B  copy-on-write/delta artifact
E-C  undo/redo log
E-D  persistent immutable root/history
```

Under matched obligation semantics:

```text
A4 scoring should agree on speculative-isolation behavior;
A5 scoring should depend only on retained historical addressability;
R_M/resource burden may differ strongly across E-A..E-D.
```

If the GMI predictor treats only E-A as “versioned,” the theory has learned an encoding label, not a mechanism.

---

# 14. Required collision hostiles

## C1 — modules without locality

Explicit modules; every update invalidates all modules.

Expected:

```text
A1 possibly high
A3 low
```

## C2 — locality without explicit modules

Opaque/monolithic storage; internal dependency mechanism changes work only in true local cone.

Expected:

```text
A1 may be low/unidentified
A3 high
```

## C3 — safe staging without history

Candidate validated privately, incumbent preserved until commit, old state deleted immediately after.

Expected:

```text
A4 high
A5 low
```

## C4 — history without safe staging

Every committed state preserved, but updates become authoritative before external verification.

Expected:

```text
A4 low
A5 high
```

## C5 — frozen router with semantic drift

Router weights unchanged; local representation change silently alters route meaning elsewhere.

Expected:

```text
source-level “router unchanged” must not create A6;
A6 low if protected composition semantics drift.
```

## C6 — hidden external repair engine

Candidate appears locally repairable because an unmetered external service performs global recomputation.

Expected:

```text
A3/resource claim invalid until service enters Z/tool contract and ledger.
```

---

# 15. E1/E2/E3 output schema

Every candidate evaluation should emit at least:

```text
candidate_id
family_id [kept from architecture-neutral predictor]
semantic_admissibility
capability_vector
raw_burden_vector
Xi_obl measurement reference
P context reference
mechanism_witnesses:
  A1..A7 values/status/CI
history/development reference
search/discovery burden
failure/censor reason
```

Architecture-neutral GMI predictors receive everything except forbidden family/label/protected-outcome fields according to the frozen protocol.

---

# 16. Kill conditions specific to witness validity

```text
SOURCE_LABEL_SUBSTITUTED_FOR_BEHAVIOR
MECHANISM_WITNESS_USES_PROTECTED_OUTCOME_TO_DEFINE_ITSELF
HIDDEN_STATE_CREATED_FALSE_LOCALITY
SEMANTIC_UNDERCHECK_CREATED_FALSE_MECHANISM
MECHANISM_ABLATION_CHANGED_MULTIPLE_UNREPORTED_MECHANISMS
IMPLEMENTATION_EQUIVALENCE_TEST_FAILED
MECHANISM_NOT_IDENTIFIABLE_WITH_REGISTERED_PROBES
```

A `NOT_IDENTIFIABLE` result is scientifically preferable to a fabricated binary label.

---

# 17. Current terminal

```text
GMI_MECHANISM_WITNESS_REGISTRY_SPECIFIED_V1
MECHANISM_VALIDATION_NOT_YET_EXECUTED
```

Claim ceiling:

> A1-A7 now have architecture-neutral behavioral targets sufficient to design stronger E1-E3 tests. The registry does not establish that the mechanisms are correctly measured in real systems, that the proposed demand coordinates predict them, or that VLC is novel.
