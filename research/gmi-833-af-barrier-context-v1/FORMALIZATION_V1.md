# AF0–AF3 formalization V1 — developmental response, information provenance, and barrier context

Authority: issue #833, AF addendum comment `5693269426`.
Pre-implementation freeze: `FREEZE_V1.md`, first committed alone at `b5a96cfb07f99f7493e5946dff42929eee653503`.

Claim ceiling:

`GMI_AF0_AF3_DEVELOPMENTAL_RESPONSE_PROVENANCE_AND_BARRIER_CONTEXT_FORMALIZED_AT_REGISTERED_FINITE_SCOPE`

This package is a refinement/typing layer over existing #233 HST/HSG and #833 objects. It does not claim new computability, information-theory, NFL, abstract-interpretation, or learning-theory parent theorems.

## 1. AF0 — parent subtraction and barrier-language discipline

The complete parent register is `GMI_BARRIER_PARENT_LEDGER_V1.json`. Repository parents are pinned by Git blob SHA; HSG-T51 is additionally bound to #233 comment `5609406015`, updated `2026-09-09T22:07:34Z`, heading `HSG-T51 — Closed-computable novelty information bound`.

The package distinguishes two logically different families of claims:

1. **Mathematical effective-computation claims.** Turing/Church/Rice/Gödel/Blum results are statements under formal machine, computability, proof-system, property-class, or complexity-measure premises. Changing those premises can change the status of a problem without contradicting the parent result.
2. **Physical-computation theses.** Whether every physically realizable process is simulable in a specified effective model is an empirical/modeling thesis whose status depends on precision, preparation, noise, readout, repeatability, time, energy, space, and error contracts. No simulated oracle or arbitrary-real model is itself evidence that a physical thesis has been falsified.

The machine rule is therefore:

`BROKE_PARENT` is admissible only when the exact original premise set is retained, the problem and output contracts are extensionally unchanged at the registered scope, and an independently checkable contradiction is supplied. Every other success is typed as restriction, approximation, semidecision, abstention, list/set output, certificate, interaction/query, oracle/advice, randomness, resource relaxation, substrate expansion, or another declared displacement.

This is a governance rule about claim language; it is not an algorithm for deciding arbitrary mathematical contradictions.

## 2. AF1 — developmental capability response object

For substrate/context `S`, initial organization `M0`, developmental law family `Delta`, information/provenance channels `Pi`, resource vector `R`, horizon/protocol `H`, requirement family `Q`, and verifier/governance contract `V`, define

`Gamma^S_{M0,Delta}(Pi,R,H,Q,V)`

as the set of reachable profiles

`g = (c, r, pi, m, h)`

where:

- `c` is the exact registered capability vector;
- `r` is the raw registered resource vector;
- `pi` is the set/multiset of provenance channels actually consumed by that path;
- `m` is the terminal realization/machine state;
- `h` is the finite registered development history.

No architecture name occurs in the definition and no universal scalar intelligence score is presumed. Pareto/resource structure remains primary.

### 2.1 Relation to existing #833/#233 objects

- **Capability:** the `c` coordinate consumes the external capability contract already separated from mechanism in #833. `Gamma` does not redefine task success.
- **Reachability:** `Gamma` is a profile-valued lift of resource/horizon-bounded reachability under `Delta`; a realizable object can be in the substrate possibility set without being reachable from this `M0` under this development law.
- **Morphology/realization:** morphology remains a property/equivalence class of the terminal realization `m`; it is not a primitive in the definition of developmental capability.
- **Resources:** every profile retains raw resource coordinates. Scalarization, when used, is an explicit downstream price/utility functional, never part of `Gamma` by definition.
- **HST/HSG:** HST supplies developmental/search state and update geometry; HSG supplies generalized spaces/kernels/resources. `Gamma` is the response surface obtained after fixing the AF context and asking what verified profiles are reachable.

### 2.2 Current capability is only a slice

Let `h=0` mean no registered development transition has occurred. The current realized-capability slice is

`Current(M0,Q,V) = { c(g) : g in Gamma and development_steps(g)=0 }`.

It is not generally sufficient to identify the full `Gamma`.

Finite microscope F1 starts two systems at the same `C0` policy and identical current identity-task accuracy `1/2`. One system admits a registered one-entry repair and reaches accuracy `1`; the other is frozen and remains at `1/2`. Thus equal current capability does not imply equal developmental response.

Finite microscope F2 starts from `ID` and `NOT`, with current identity-task accuracies `1` and `0`, but a common registered reset/set development law makes the post-development reachable machine set the same four unary Boolean policies. Thus different current capability does not imply different reachable envelope.

These are finite counterexamples to identification claims, not a universal empirical law about development.

### 2.3 Possibility space is not reachability

Define `M(S)` as the data/history-independent class of realizations admitted by substrate/representation contract `S`. Define

`Reach(M0,Delta,Pi,R,H,V) subseteq M(S)`.

Membership in `M(S)` is only possibility. F1's substrate permits all four unary Boolean policies, while the frozen `C0` developmental law reaches only `C0`; `NOT` is the exact witness in `M(S) \ Reach`.

### 2.4 Provenance-tagged development

The registered channel vocabulary is:

1. `INITIAL_OR_INHERITED_ORGANIZATION`
2. `EXTERNAL_OBSERVATION`
3. `REWARD_OR_EVALUATOR_SIGNAL`
4. `ENDOGENOUS_COMPUTE`
5. `STOCHASTIC_VARIATION`
6. `ORACLE_ADVICE_OR_TOOL`
7. `SOCIAL_OR_CULTURAL_TRANSFER`
8. `PHYSICAL_OR_ENVIRONMENTAL_SIGNAL`

A path cannot omit a consumed channel. In particular, a target-correlated oracle string, evaluator response, social message, measurement channel, or target-specific initialization is imported information/power. An arbitrary real parameter used as a nonuniform advice store belongs on an initialization/advice/physical-precision ledger; it is never free `emergence from nothing`.

The previously checked #833-L distinction between current capability and developmental potential remains a valid coarse specialization. AF upgrades the scientific object from a scalar/max-potential summary to a set-valued, provenance- and resource-bearing response surface.

## 3. AF2 — null-experience developmental envelope

Define a null slice only after naming which channels are absent:

`Gamma_null = Gamma(Pi_external=0,R,H,Q,V)`.

The literal warning is binding:

`NO_EXTERNAL_DATA != NOTHING`.

A machine may still contain inherited structure, execute deterministic computation, consume resources, or (under weaker nulls) draw endogenous randomness.

### 3.1 Null-condition hierarchy

The registered hierarchy is explicit rather than collapsing all nulls into one word:

1. `NO_SENSORY_OBSERVATIONS`: no external observation channel.
2. `NO_REWARD_OR_EVALUATOR_FEEDBACK`: no reward/evaluator signal.
3. `NO_TASK_SPECIFIC_DATA`: no task-specific observational/evaluator data; task-independent initialization may remain.
4. `NO_EXTERNAL_INTERACTION`: no external observation, reward, oracle/tool, social-transfer, or physical/environmental channel after initialization.
5. `NO_ENDOGENOUS_RANDOMNESS`: no stochastic-variation channel.
6. `NO_TASK_SPECIFIC_INITIALIZATION`: the initial organization is independent of the target/task variable.
7. `ABSOLUTE_REGISTERED_NULL_EXCEPT_SUBSTRATE_AND_DYNAMICS`: only registered substrate/dynamics and target-independent initialization remain; no imported target-correlated channel or endogenous randomness is licensed.

The conditions are coordinates/restrictions, not an assertion that every neighboring pair is a strict set inclusion for every implementation. The emitted machine receipt states exactly which channels each condition forbids.

### 3.2 AF-T01 — Null Target-Information Acquisition

Let `Theta` be the registered target random variable and let `Z=(M0,W)` contain the complete initial state, internal randomness, and every channel admitted by the chosen null contract. Assume `Theta` is independent of `Z`. If the terminal machine is a deterministic measurable function `Mt=f(Z)`, then

`I(Theta;Mt)=0`.

Proof: independence gives `I(Theta;Z)=0`. Since `Theta -> Z -> Mt` is a Markov chain with `Mt=f(Z)`, the data-processing inequality gives `I(Theta;Mt) <= I(Theta;Z)=0`; mutual information is nonnegative, so equality holds.

Ownership: this is an elementary Shannon-information specialization, not a new AF information theorem.

Load-bearing assumptions are complete channel accounting and target-independence of the upstream state. If a hidden target-correlated channel enters, the theorem simply does not apply.

### 3.3 Shannon target information is not HSG-T51 algorithmic information

HSG-T51 states, for a closed deterministic computable process `s_n=F^n(s_0)`, the algorithmic-information upper bound

`K(s_n) <= K(F)+K(s_0)+K(n)+O(1)`.

That parent is about description length/Kolmogorov complexity. AF-T01 is about mutual information with a registered random target. Neither quantity is synonymous with usefulness, organized complexity, logical depth, or capability. This package therefore parent-subtracts HSG-T51 rather than reusing its wording for a Shannon claim.

### 3.4 Three exact controls

- **F3 computational unfolding:** target information is already dormant in initial state. Deterministic internal compute changes accessible action accuracy `1/2 -> 1`, while the registered target-information content stays `1 bit -> 1 bit`. Terminal: `COMPUTATIONAL_UNFOLDING_WITHOUT_EXTERNAL_DATA`.
- **F4 random novelty:** an independent fair random bit has output entropy `1 bit` but `I(Theta;R)=0` and expected target accuracy `1/2`. Terminal: `RANDOM_NOVELTY_WITHOUT_TARGET_ALIGNMENT`.
- **F5 oracle advice:** a target-correlated oracle bit gives `I(Theta;A)=1 bit` and perfect accuracy, but only with `ORACLE_ADVICE_OR_TOOL` provenance. Terminal: `IMPORTED_ORACLE_OR_ADVICE_POWER`.
- **F5b nonuniform initialization:** target-correlated content encoded in an advice string/arbitrary-real-style initial parameter is tagged `INITIAL_OR_INHERITED_ORGANIZATION` and classified `IMPORTED_INFORMATION_OR_ADVICE`; its information content/precision remains chargeable by the downstream resource/physical contract.

Additional registered terminals are `NO_TARGET_INFORMATION_ACQUIRED` and `UNEXERCISED_CAPABILITY`; neither is synonymous with `INCAPABLE`.

## 4. AF3 — barrier context and barrier surfaces

A barrier claim is indexed by

`chi=(S,Pi,Q,R,H,eps,delta,V)`

where the axes mean substrate semantics, information provenance, problem/query class, resources, horizon/interaction protocol, approximation tolerance, confidence/failure allowance, and output/verifier contract.

The registered status vocabulary is:

- `DECIDABLE`
- `SEMI_DECIDABLE`
- `CERTIFIABLE`
- `SOUND_INCOMPLETE_APPROXIMATION`
- `PROBABILISTIC_APPROXIMATION`
- `IDENTIFIABLE_IN_LIMIT`
- `NOT_IDENTIFIABLE_AT_SCOPE`
- `UNDECIDABLE_RELATIVE_TO_S`
- `RESOURCE_INFEASIBLE_AT_SCOPE`
- `PHYSICAL_STATUS_UNKNOWN`

A **barrier surface** is the subset/boundary of context space where this typed status or the attainable capability set changes. V1 does not assert smoothness, topology, or a numeric distance-to-barrier.

### 4.1 Transition/displacement record

Every record contains source/target contexts and statuses, changed axes, original and retained premise sets, added power or weakened requirement, transition class(es), and the nearest residual barrier.

The frozen classes are domain restriction, promise problem, approximation, semidecision, abstention, list/set output, certificate, interaction/query, oracle/advice, randomness, resource relaxation, substrate expansion, and literal contradiction.

The finite F7 records instantiate four parent-owned patterns:

- unrestricted exact verification -> sound incomplete abstraction: `APPROXIMATION + CERTIFICATE`; unrestricted exact-decision barrier remains;
- unrestricted class -> finite promise slice: `DOMAIN_RESTRICTION + PROMISE_PROBLEM`; outside-promise instances remain;
- single answer -> finite list: `LIST_OR_SET_OUTPUT`; single-answer identification remains distinct;
- base effective substrate -> oracle-relative substrate: `ORACLE_OR_ADVICE + SUBSTRATE_EXPANSION`; relative/higher barriers remain.

These records validate typing and provenance. They are not independent proofs of the parent undecidability/identifiability results.

### 4.2 AF-T02 — optional-extension monotonicity

Suppose a target context adds only optional strategies/resources/channels, preserves every old strategy with identical semantics and zero mandatory overhead, and preserves the objective/order. Then the old feasible/reachable profile set embeds in the new set, so the best achievable value under the fixed registered objective cannot worsen.

Ownership: direct context-level corollary of HST-T01/superset dominance.

F6 fixes a counterexample to any unconditional version. Base strategy `A` has benefit `10`, cost `2`, net `8`. Optional strategy `B` has benefit `11`, cost `4`; because `A` remains available, optimum stays `8`. A mandatory overhead `12` applied to every strategy changes the best net to `-4`. Thus `more resources/channels always helps` is false without optionality/zero-overhead premises.

### 4.3 AF-T03 — no barrier-breaking by premise change

`BROKE_*` is rejected unless:

1. every original parent premise is retained;
2. the source/target problem contracts are the same;
3. the source/target output contracts are the same;
4. a contradiction witness is independently verified;
5. the transition is classified only as `LITERAL_CONTRADICTION`.

The hostile relabels the finite-promise restriction as `BROKE_TURING`; it fails because the unbounded-domain premise was removed. The guard also forbids `SOLVED_FOREVER` and requires a nearest residual barrier for every non-contradictory displacement.

## 5. Evidence classes and exact scope

The analytic content is limited to the explicitly stated elementary corollaries/specializations:

- AF-T01: Shannon independence + data-processing specialization;
- AF-T02: set inclusion/superset dominance inherited from HST-T01;
- AF-T03: claim-governance validation rule, not a theorem about arbitrary formal systems.

The executable layer is a finite exact microscope and schema validator. It certifies the registered fixtures and hostiles only. The independent oracle re-derives F1/F2, possibility-vs-reachability, mutual-information controls, overhead arithmetic, transition census, and parent pins without importing the main executor.

## 6. What remains outside this tranche

AF4+ remains open: relative computability/Turing jumps, verification-lattice experiments, NFL/complexity/learnability barrier surfaces, physical/hypercomputation contracts, all-machine finite atlases, endogenous barrier discovery, open-ended developmental dynamics, costs of displacement, new-theorem protocol, and expanded experiment matrices.

No result here establishes universal self-improvement, universal computability escape, physical hypercomputation, a final intelligence definition, or `COMPLETE_GMI`.
