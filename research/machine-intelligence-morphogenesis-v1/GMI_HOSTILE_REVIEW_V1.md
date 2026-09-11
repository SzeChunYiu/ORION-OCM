# GMI-v1 hostile formal review

Status: **attack log before F0 closure**. This file records defects found in the synthesis and the required corrections. A theory is not hardened by leaving elegant but ambiguous definitions untouched.

## H1 — external history is not a sufficient machine state

### Defect

The first draft quotiented histories `h` directly. Two runs can have identical externally recorded histories while differing in:

```text
optimizer momentum
random generator state
replay memory
posterior approximation state
hidden recurrent state
learned library/index state
morphology/topology configuration
```

Those differences can change future behavior and learning.

### Fix

Define a developmental situation

\[
d=(\chi,h,\xi)
\]

with current theory-level machine configuration `chi`, registered history `h`, and relevant current context `xi`; quotient situations, not histories.

### Status

`FIXED_IN_GMI_THEORY_V1`.

---

## H2 — arbitrary 'legal development' can smuggle in human engineering

### Defect

The phrase

```text
(Q,B) reachable under legal development
```

is ambiguous. If an external engineer is allowed to rewrite the model, install a theorem prover or hand-supply a task solution for free, the resulting frontier measures the combined human+machine system rather than the machine under study.

### Fix

Every cognitive obligation must declare a **development protocol** `D` specifying:

```text
initialization / supplied pretrained state
which information sources are available
which machine-initiated updates are legal
which externally initiated updates/interventions are legal
which human inputs are permitted and how charged
which tools/donors may be installed/called
whether morphology change is machine-proposed, externally supplied or forbidden
reset/continuation semantics
```

The feasible set is reachable only under `D`.

Different `D` values define different experimental systems and may not be silently compared.

---

## H3 — one scalar verifier threshold does not cover math/code/science

### Defect

A stopping time written as

\[
T_q=\inf\{t:V(outcome_t)\ge q\}
\]

assumes an ordered scalar verifier output. Real GMI obligations include:

```text
Lean kernel acceptance
unit-test/execution contracts
multi-dimensional safety/authority obligations
statistical evidence thresholds
partial verified progress
abstention / cannot-check terminals
```

### Fix

For task `tau`, define an externally registered **admissibility predicate/contract**

\[
A_\tau(y,e;V,C)\in\{0,1\}
\]

or a declared partially ordered evidence/capability contract. Define first-admissible stopping time

\[
T_A=\inf\{t:A_\tau(y_t,e_t;V,C)=1\}.
\]

Capability vectors may retain graded quality/reliability beyond binary admission.

---

## H4 — hidden environment state must not become free machine information

### Defect

If `xi` in the developmental situation contains the true hidden world state, GMI can accidentally grant the machine information it does not possess.

### Fix

`xi` may contain registered public/context state and experimental conditions, but hidden environment variables unavailable to the machine are integrated over the ecology/environment law conditioned on legal observations. If the analysis uses an ontic world state for theorem purposes, it must be explicitly distinguished from the machine's information state and cannot be used by `K/U/Gamma` unless observed legally.

---

## H5 — future-equivalence intervention class can be too strong or too weak

### Defect

'For every future intervention' is meaningless without fixing which interventions are admissible. Allowing arbitrary state surgery distinguishes everything; allowing only the machine's default trajectory can merge states whose difference matters under legitimate future teaching/probes.

### Fix

Add a registered intervention/probe class `J` to the obligation. State equivalence is relative to `J` and the development protocol `D`.

The resulting minimal state is therefore explicitly

\[
z=[d]_{\sim_{\mathcal O,D,J}}.
\]

This mirrors the fact that Myhill-Nerode, PSR and bisimulation minimality are always relative to an observation/action semantics.

---

## H6 — intelligence profile can confuse machine ability with starting capital

### Defect

A pretrained 1T-token model and an untrained architecture have radically different frontiers. Ranking only `M` while omitting starting developmental situation can attribute supplied capital to architecture.

### Fix

The primary profile is

\[
\mathcal I_{M,d,D}:E\mapsto\mathcal F_M(E\mid d,D).
\]

Claims about a morphology *family* must either:

- fix comparable initialization/development protocols; or
- charge acquisition of starting capital; or
- explicitly state that the comparison is of deployed systems, not architecture-only intelligence.

---

## H7 — resource accounting is not invariant under measurement choice

### Defect

Raw resource vectors can contain incomparable coordinates (tokens, Joules, FLOPs, checker calls, human minutes). Adding coordinates may change Pareto relations.

### Fix

GMI does not claim a canonical universal vector. Each obligation freezes its metering coordinates and provenance. Cross-study comparison requires a declared coordinate mapping; scalarization requires prospective prices/utility.

This is a limitation, not something to hide.

---

## H8 — reachable frontier may be uncomputable

### Defect

For rich/Turing-complete systems, the complete feasible set/frontier may be uncomputable or impossible to enumerate.

### Fix

Distinguish:

```text
semantic/theory frontier     all legal reachable points under the model
certified empirical frontier observed/proved points at registered scope
outer/inner bounds           theorem/statistical bounds where available
```

Experiments never claim to have enumerated the universal semantic frontier.

---

## H9 — K1/K2/K3 require causal counterfactuals, not labels

### Defect

Observing lower later cost after training does not identify what caused the saving.

### Fix

Each capital level requires matched counterfactual arms and a pre-solution/pre-acquisition mediator where feasible:

```text
K1: RESET/history shuffle/library-only + proposal/control/representation mediator
K2: matched acquisition procedure lacking the inherited developmental state
K3: matched morphology/improvement generator without the inherited generator state
```

The capital labels are evidence classes, not properties assigned by inspection.

---

## H10 — theory synthesis can become unfalsifiable if every parent is simply absorbed

### Defect

A framework that says 'all existing theories are special cases' but has no exclusion conditions can become taxonomy rather than science.

### Fix

GMI-v1 has two separate falsification levels:

**Synthesis failure:** a major machine-intelligence family or parent theorem cannot be expressed without changing core definitions or smuggling family-specific semantics into the supposedly invariant fields.

**New-law failure:** the synthesis works descriptively, but no compact cross-paradigm predictive invariant beats family-specific parent products.

The second failure does not erase the first contribution, but it caps GMI as a unifying metrology/framework rather than a new empirical law.

---

# Required F0 corrections

Before F0 can be called complete:

- [x] situation not history-only;
- [ ] add development protocol `D` and intervention class `J` to the obligation everywhere;
- [ ] replace scalar verifier threshold with admissibility contract;
- [ ] distinguish semantic vs certified empirical frontier;
- [ ] update theory contract / axioms / HST alignment;
- [ ] add starting-state/protocol to generality notation;
- [ ] verify reference implementation has no hidden scalar-intelligence assumption.

Current terminal:

```text
GMI_F0_HOSTILE_REVIEW_ACTIVE
THEORY_NOT_YET_FROZEN
```
