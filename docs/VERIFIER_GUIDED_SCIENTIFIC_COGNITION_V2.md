# Verifier-guided persistent scientific cognition — FLT, ORION-Q/QG and OCM

Status: research synthesis / parent-hardening note, 2026-09-06.  
Scientific anchors: #50, #62. Architecture/control: #69, #70, #71, #72.  
This note grants no novelty, superiority, quantum advantage, frontier-science or publication authority.

## 1. Why the September 2026 FLT result matters

Anthropic reported on 2026-09-04 that Claude agents produced an end-to-end Lean formalization of Fermat's Last Theorem in 11 days. The campaign generated about 13 million lines of Lean, proved roughly 30,300 theorems along the way and used about 29,500 in the final proof. Anthropic reports that dozens of agents worked in parallel and that the successful campaign consumed about six billion output tokens.

Primary sources:

- Anthropic research account: https://www.anthropic.com/research/formalizing-fermats-last-theorem
- released proof: https://github.com/anthropics/fermats-last-theorem
- Prove2Me: https://prove2.me and arXiv:2608.28433

The architecture lesson is stronger than `a larger model can write more Lean`.

Anthropic reports that the early multi-agent attempt suffered memory degradation and poor coordination. The successful scaffold used Prove2Me to externalize shared research state through:

1. a directed acyclic graph of theorem statements/frontier obligations;
2. separation of theorem statements from proofs, with links maintained externally;
3. searchable natural-language descriptions for reuse;
4. Lean kernel checking;
5. a persistent library in which accepted formal results become reusable building blocks.

The released FLT repository additionally exposes theorem dependencies and an offline browser over the formal artifact.

That makes the campaign a useful parent for OCM because it demonstrates a practical transition from:

```text
many large context-bound reasoners
```

toward:

```text
many proposal/search workers
+ one durable shared dependency topology
+ one exact formal authority boundary
+ reusable verified state
```

The OCM question is not whether this pattern works at all. A strong parent now demonstrates that it can work at very large formalization scale. The harder question is whether Machine Epistemics can generalize and make the pattern substantially more persistent, revisable, sparse and lifetime-efficient.

## 2. Strong parents now owed first right of refusal

The following mechanisms are not OCM novelty by themselves:

- theorem/task dependency DAGs;
- decomposition into independently closable obligations;
- machine-checked proof admission;
- immutable/pinned formal statements;
- cross-agent theorem reuse;
- semantic theorem search;
- persistent partial proof structure;
- schema extraction from proved subgraphs;
- reuse of verified results from incomplete attempts.

Prove2Me is a direct parent for the first group.

ProofEvolve is an additional strong 2026 parent for the latter group: neural proposals operate over persistent partial AND/OR proof DAGs, Lean verifies transitions, and verified sub-DAGs can be extracted into a persistent schema library across problems. Therefore `failed/partial proof experience becomes reusable verified structure` is no longer, by itself, a credible OCM residual.

OCM must compare against the strongest faithful composition of these parents plus ATMS/TMS/provenance, incremental computation, theorem-search systems and persistent agent memory.

`PARENT_SUFFICIENT` remains a successful scientific result.

## 3. The OCM generalization target

A useful canonical factorization remains:

```text
M_t = (F_t, O_t, Pi_t, C)
```

where:

- `F_t`: persistent epistemic field;
- `O_t`: executable operator/method catalogue;
- `Pi_t`: small executive/navigation policy;
- `C`: constitutional checking, authority, metering and commit boundary.

Parallel agents are not required as a new cognitive module. They can be bounded proposal executors operating against one field:

```text
shared F_t
  -> active frontier / obligations
  -> Pi_t chooses operator/work
  -> one or more workers propose deltas
  -> C validates checker + evidence + authority + scope + resource contract
  -> admitted delta yields F_(t+1)
  -> dependent obligations close/reopen
  -> success/failure experience can consolidate into reusable structure
```

The architecture should therefore test `one shared epistemic organism with heterogeneous operators`, not assume that a society of independently stateful chat agents is the machine.

## 4. Formal verification is one authority type, not science itself

The phrase `zero-tolerance evaluator` is defensible only inside a precisely formalized system.

For mathematics, Lean can establish that a theorem follows from formal definitions, axioms and imported results. This does not automatically establish that an informal mathematical name or scientific interpretation corresponds to the encoded object. The released FLT artifact itself distinguishes authoritative Lean statements from generated English descriptions.

For physics, chemistry, biology, medicine and empirical engineering, formal validity is only one layer. OCM should keep at least the following authority coordinates distinct:

```text
FORMAL_VALIDITY
COMPUTATIONAL_CERTIFICATION
MODEL_CORRESPONDENCE
EMPIRICAL_SUPPORT
STATISTICAL_IDENTIFICATION
CAUSAL_IDENTIFICATION
EXTERNAL_VALIDITY / SCOPE
RESOURCE / IMPLEMENTATION_VALIDITY
HEURISTIC_OR_UNCHECKED
```

A machine proof of

```text
assumptions -> consequence
```

cannot establish that the assumptions describe nature.

A mathematically consistent protein, circuit, physical theory or treatment is not thereby experimentally valid.

This distinction is central to Machine Epistemics: `C` should not be one universal proof kernel. It should enforce a typed checker/authority contract whose meaning depends on the claim class.

## 5. ORION-Q/QG contributes control science now

The most useful transfer from the previous quantum research is not a quantum metaphor. It is a set of exact research-control operators and adverse lessons that were developed under strict resource/authority discipline.

### 5.1 Regime geometry -> operator regime maps

ORION-QG #740 generalized compilation studies into a programme that maps:

- donor-optimal regions;
- elementary trade regimes with minimal witnesses;
- sufficiency bounds;
- exact membership predicates from input structure;
- prospective cost forecasts.

OCM analogue:

```text
local field/query features
-> certified operating regime
-> admissible operator set
-> resource/trade frontier
-> selected action
```

This can become an explicit mature endpoint for `Pi_t`, or a target into which a small learned router is distilled.

### 5.2 Authority-indexed abstraction routing -> exact parent for #72/#71

ORION-Q MAX-R4E-A #908 tested an exact authority-indexed abstraction router on frozen real compiler receipts.

Its policy was conceptually:

```text
filter routes by query authority/sufficiency
-> choose the least detailed authorized route
-> refine/escalate when compact state is insufficient
-> CANNOT_AUTHORIZE when the requested claim exceeds supplied authority
```

The protected result recorded:

- 10/10 route-correct for the authority-indexed policy;
- zero false-authority uses;
- zero overcompression;
- zero avoidable rich-state uses;
- 7/7 compact-authorized opportunities captured.

The result was intentionally narrow, but it is already a strong exact parent for OCM executive control.

A learned router must therefore beat or complement this parent; it must not replace exact authority filtering with a probability score.

### 5.3 QG-derived research skills -> reusable OCM meta-operators

ORION-Q MAX-R4E #903 defined several transferable research operators. Their OCM mappings are:

```text
EXACT_REFEREE_FIRST
  prefer a cheap exact adjudicator before learned approximation or larger search.

SAFE_ABSTRACT / UNSAFE_QUOTIENT_VETO
  use a quotient only under a theorem/contract that preserves the needed distinction.

BOUNDED_DEFECT_LOCALIZATION
  if a theorem localizes all nontrivial freedom to a small defect/support set,
  activate/search only that set and account for bulk analytically.

COARSE_TO_FINE_AUTHORIZED_REPRESENTATION
  use the least detailed representation sufficient for this query;
  REFINE when a different/finer distinction is required.

SATURATION_OR_CONTINUATION_CHECK
  do not extrapolate a finite pattern before a justified crossover/saturation bound.

RESOURCE_RESPONSIBILITY_ESCALATION
  if an inner proxy is not the layer controlling end-to-end cost,
  stop over-optimizing it and move to the responsible layer.

ANTI_OVERCOMPRESSION / INFORMATION_BARRIER
  a counterexample to a quotient identifies hidden information that must remain
  until a stronger theorem or narrower query scope licenses its removal.
```

These should be treated as strong parents or candidate explicit schemas inside `O_t`, not renamed as OCM discoveries.

### 5.4 Hidden coupling -> hostile control for modularity/compression

ORION-QG produced cases where separable/local selection works only when the relevant coupling summary is retained, and cases where overcompressed state cannot determine continuation/value.

OCM consequence:

> locality is not established merely because data are stored in modules.

A local operator is safe only if the active field contains every coupling variable on which the decision actually depends, or the controller returns `REFINE_REQUIRED` / `JUMP`.

This is a direct hostile control for #69, #70 and #72.

### 5.5 Robust observation geometry -> evidence reliability

QG-37 #937 studied exact identification when one selected probe response may be adversarially corrupted. In its frozen model, unique radius-one recovery requires sufficient response-code distance and redundant distinguishing probes.

The reusable OCM lesson is not the quantum-specific cardinality. It is:

```text
reliability contract
-> choose enough discriminating observations
-> certify decoder/identification robustness
-> otherwise obtain more evidence or abstain
```

This gives `QUERY / OBSERVE / EXPERIMENT` an evidence-reliability scope rather than assuming every observation is equally authoritative.

### 5.6 Resource-responsibility escalation -> general scientific control

ORION-Q MAX-R4 #698 is a useful adverse example. A favorable structural/proxy regime disappeared when circuit-grounded implementation cost was charged, shifting the active obstruction to another layer.

This is a general OCM research operator:

```text
local optimization appears favorable
-> bind proxy to end-to-end objective
-> identify cost/responsibility decomposition
-> if another layer dominates, escalate there
```

It prevents the cognitive machine from becoming exceptionally good at optimizing the wrong quantity.

## 6. Safe compression should be query-relative, not one global hierarchy

#70 should not assume there is one universally best compressed representation of `F_t`.

Different queries can require incomparable summaries. The correct object is closer to:

```text
S_Q(F_t)
```

where `Q` is a registered query/decision class and `S_Q` is certified to preserve the distinctions needed for that class and its lifecycle obligations.

A summary may answer only inside its certified scope:

```text
query within scope    -> use compact summary
finer query required  -> REFINE_REQUIRED
no route authoritative -> CANNOT_AUTHORIZE
```

Counterexamples to a candidate summary should be retained as `InformationBarrier` witnesses, not discarded as inconvenient failures.

## 7. A causal experiment suggested by the FLT campaign

The strongest near-term formal-science experiment is not `can OCM prove FLT?`.

Use the same underlying reasoner(s), Lean/tool access, task packet and compute/token budget, then compare organizational mechanisms:

```text
B0 independent workers + ordinary files/messages
B1 Prove2Me-like dependency DAG + verified shared library
B2 B1 + typed support/failure/scope/reopening state
B3 B2 + query-relative safe compression + authority-aware sparse control
B4 B3 + tiny learned proposal/order policy, if deterministic parents leave a residual
```

Freeze task identities, theorem library, axioms/checker, budgets and refusal semantics before results.

Measure at least:

```text
verified obligations solved
duplicate work
abandoned/stale work
successful theorem/method reuse
checker calls
tokens / CPU / wall time
durable bytes
active/touched state k
k/N
context reconstruction cost
false authority / invalid promotion
reopen cone after a changed/revoked dependency
recovery/revalidation work
```

Then repeat the same organizational comparison in one materially different verified procedural or empirical-science setting. Otherwise the result remains theorem-engineering-specific.

## 8. Why ultra-efficient OCM is still an open target

The FLT campaign is a major capability result, but Anthropic reports about six billion output tokens. It does not establish an ultra-efficient cognitive machine.

OCM can therefore pursue a nontrivial systems/science target:

> preserve the capability advantages of durable shared verified state while reducing repeated context reconstruction, duplicated search and broad recomputation through compact persistent structure, sparse active cognition, reusable operators and exact local revision.

This target must count all state, indexes, archival bytes, verification, maintenance and acquisition work. Moving information out of parameters does not make it free.

## 9. Genuine quantum computation remains gated

ORION-V2's OCM quantum lane reached the correct current negative terminal: `NO_ELIGIBLE_OPERATOR` — no concrete classical OCM operation with a sufficiently precise access model had yet earned a quantum lift.

Preserve that result.

Quantum computation, if useful later, belongs as one declared backend inside `O_t`, not as vague cognitive vocabulary. A candidate quantum operator must bind:

```text
semantic classical operation/problem
input/access/oracle model
state preparation / oracle construction cost
query/gate model
error/readout model
fault-tolerance assumptions where applicable
strongest classical/dequantized comparator
end-to-end resource vector
checker/output authority
```

Only after this contract exists should OCM test whether a quantum implementation produces incremental value.

Classical vector spaces, stochastic branching, interference-like scoring, associative memory or `superposition` metaphors are not quantum advantage and should be compared against ordinary classical parents.

## 10. Candidate scientific claim after parent subtraction

Do **not** claim:

- `we invented theorem DAGs`;
- `we invented multi-agent formalization`;
- `we invented verified partial-proof reuse`;
- `formal proof makes all science deterministic`;
- `quantum ideas make cognition quantum`;
- `external memory makes the machine small for free`.

A stronger, testable candidate is:

> **Verifier-guided persistent scientific cognition:** a shared epistemically governed field can amortize scientific work across tasks by preserving verified partial results, failures, dependency topology, authority scope and reusable operators, while activating only a sparse query-relevant subfield and reopening exactly the affected knowledge after change.

The candidate residual over strong parents is specifically the combination of:

```text
heterogeneous checker/authority types
+ exact lifecycle revision/reopening
+ query-relative certified compression
+ sparse active cognition
+ reusable operator/regime learning
+ resource-responsibility control
+ whole-lifetime acquisition/search economics
```

This should be tested causally. If the strengthened parent product reproduces the signature, report `PARENT_SUFFICIENT`.

## 11. Issue ownership

No new architecture issue is required for this synthesis.

- #62 owns persistent scientific/epistemic experience and the matched shared-field experiment.
- #69 owns vessel minimality and worker-vs-field subtraction.
- #70 owns query-relative safe compression and information barriers.
- #71 owns tiny learned routing only after exact parents are strong.
- #72 owns authority-aware navigation, regime routing, robust observation and responsibility escalation.
- #50 remains the scientific/lifetime anchor.

The next implementation step should reuse those owners rather than create a parallel `vibe science` subsystem.
