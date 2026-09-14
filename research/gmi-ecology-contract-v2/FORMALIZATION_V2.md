# GMI ecology contract V2 — exact A2 formalization

Issue #602 A2. This is a G1 registration theorem: it fixes the environment object required by later morphology/capability/development claims. It does not prove a G5 phase law, G6 capability predictor, or empirical natural-cognition result.

## 1. Parent subtraction

This contract does not claim to invent stochastic environments or multi-agent decision theory.

- A POMDP already supplies latent state, action, transition, observation and reward/feedback structure under partial observability.
- Markov/stochastic games make multiple adaptive agents and joint actions explicit rather than treating all secondary actors as fixed environment noise.
- Dec-POMDPs make local observations/actions of multiple agents explicit.
- Blackwell comparison orders information structures by decision value; active acquisition must therefore be evaluated net of its cost rather than credited because it supplies more bits.
- SCM / `do` semantics distinguish an intervention that sets a mechanism from an ordinary observation or uncontrolled action.

The GMI-specific residual here is the prospective registration discipline needed by #602: recurrence/reuse, drift, structure, topology, embodiment, separate hard budgets and prices, verifier latency/cost/asymmetric loss, information-acquisition burden, protected train/development/held-out splits, and exact remint anti-leakage.

## 2. Ecology object

At finite registered scope define

```text
E = (
  I,          # agents and their adaptation contracts
  X, O,       # latent state abstraction and per-agent observation channels
  A, J,       # ordinary actions and interventions
  F, V,       # development feedback and final verifier
  D_tau, H,   # task distribution/schedule and horizons
  Delta,      # drift / regime process
  Rho,        # recurrence / reuse law
  Xi,         # compositional, symmetry, relational structure
  G,          # social interaction / communication topology
  B_body,     # sensor / actuator / workspace constraints
  (b,p),      # hard budget vector and optional price vector
  C_info,     # active information-acquisition costs and delays
  S_split     # construction/train, development, held-out partition
).
```

Noise and partial observability are properties of `O`, `F`, and the state transition law, but are registered separately because two ecologies can have the same visible alphabet and radically different information structure. Verification economics are properties of `V` but are separately metered because accuracy, latency, verification work, false adoption and false rejection have different decision consequences.

A second adaptive agent is not representable merely by saying "stochastic transition noise" when its policy changes as a function of history. Each adaptive participant `i in I` therefore has a declared history-dependent adaptation contract at the environmental interface level. The contract is intentionally agnostic to its internal architecture.

## 3. Ordinary action versus intervention

An ordinary joint action `a in A` enters the registered environment transition law

```text
P_E(x_{t+1} | x_t, a_t, z_t).
```

An intervention `j in J` names a target mechanism and the modularity promise describing what is externally set and what remains invariant. In an SCM-style specialization, `do(X=x)` replaces the structural equation for `X` while leaving the other declared mechanisms unchanged.

The two channels may coincide operationally in a particular world, but they are not identified by definition. This prevents observational prediction, ordinary control and experimental intervention from being silently conflated in later causal claims.

## 4. Hard budgets and prices

Let a resource vector be `r in R^k_{>=0}`, a hard budget `b in R^k_{>=0}`, and a prospectively frozen price vector `p in R^k_{>=0}`.

Feasibility is

```text
r feasible under b  iff  r_j <= b_j for every coordinate j.
```

A price scalar, when permitted, is

```text
c_p(r) = p^T r.
```

### Theorem A2-R — prices cannot replace hard budgets [P1 + exact witness]

There is no general decision rule using only `p^T r` that reconstructs componentwise feasibility under `b`.

**Witness.** Take

```text
b = (1,2),  p = (1,1),
r = (2,0),  s = (0,2).
```

Then `p^T r = p^T s = 2`, but `r` violates the first hard budget while `s <= b`. Hence equal scalar price can hide opposite feasibility. QED.

**Consequence.** #602 A2 is correct to require prices and hard budgets separately. Scalarization may rank feasible points only after feasibility and only when `p` was frozen before protected scoring.

## 5. Verification economics

A verifier contract is

```text
V = (judge, latency, resource_cost, L_FA, L_FR),
```

where `L_FA` is false-adoption loss and `L_FR` is false-rejection loss.

These quantities are not reducible to verifier accuracy alone. Two verifiers can have identical correctness probabilities and verification work but different latency under a finite horizon; likewise identical accuracy can have different expected loss when false adoption is much more costly than false rejection. Later capability/phase laws therefore consume the full vector rather than a Boolean `has_verifier` flag.

## 6. Information acquisition

For active probe/query channel `q`, register a nonnegative resource cost vector `c(q)`, latency `ell(q)`, and a query budget. Passive observations and active acquisition are distinct: if the machine must act to reveal information, that acquisition enters the lifecycle burden before any value-of-information claim.

The strongest parent is the corresponding no-probe / cheaper-information policy under the same public information and downstream resources. More information by itself is not a capability result.

## 7. Multiple adaptive agents and social topology

Let `I={1,...,n}`. Each agent `i` has local observation channel `O_i`, ordinary action set `A_i`, and a declared adaptation interface. The joint transition law may depend on `a=(a_1,...,a_n)`.

A social topology is a time-indexed directed graph/hypergraph `G_t` whose edges declare permitted influence, observation and/or message channels. A complete graph, star, team partition, adversarial interaction or no-message graph is an explicit ecology value. This separates "there are multiple agents" from "all agents can communicate with all others".

## 8. Embodiment

`B_body` declares sensor ports, actuator ports, their rate/latency/precision, and workspace/body constraints. `NONE` or `UNCONSTRAINED` is a valid explicit value. Embodiment is therefore not imported into every GMI claim, but when it matters it cannot be added post hoc after a morphology succeeds.

## 9. Protected splits

Let

```text
S_split = (S_train, S_dev, S_heldout)
```

with pairwise-disjoint registered identities/remints and a freeze time `t_f`. Construction/search/coordinate choice before `t_f` may access only the allowed construction/train and development information. Held-out membership, remint identity and protected outcomes are hidden unless the task explicitly makes them inputs; if made visible, they cannot serve as protected evidence for invariance.

## 10. Ecology equivalence and remints

Let `N(E)` be the collection of purely nominal finite domains declared remintable: for example agent IDs, state names, observation symbols, action symbols, task IDs, regime labels, sensor/actuator names. A **declared remint** from `E` to `E'` is a family of bijections

```text
phi = {phi_D : D -> D' | D in N(E)}
```

such that applying those bijections to every occurrence of the nominal symbols makes the registered objects exactly agree, including:

- transition and observation probabilities;
- feedback and verifier semantics/economics;
- task obligations and recurrence structure;
- hard budgets and price vectors;
- structural/symmetry relations;
- social graph incidence;
- sensor/actuator constraints;
- information-acquisition costs;
- train/development/held-out membership.

Write

```text
E ~=_R E'
```

when such a declared bijection exists and remint identity is not available as a protected shortcut.

### Theorem A2-EQ — declared remint equivalence is an equivalence relation [P1]

**Reflexive.** Identity bijections on every nominal domain preserve every registered object.

**Symmetric.** Every bijection `phi_D` has a bijective inverse. Applying the inverses restores `E` from `E'` while preserving the same semantic equalities.

**Transitive.** If `phi:E->E'` and `psi:E'->E''` are semantic-preserving bijections, then every `psi_D o phi_D` is a bijection and preserves the same objects by substitution. Therefore `E ~=_R E''`.

QED.

`ecology_contract_v2.py` executes identity, inverse and composition witnesses on a finite two-adaptive-agent world. It also mutates only the verifier false-adoption loss and confirms that the result is **not** a remint under the same bijection.

### Lemma A2-L — visible remint identity destroys the intended invariance test [P1]

Suppose two remints are semantically isomorphic but a protected binary outcome is perfectly correlated with a visible `remint_id`. Then the policy `predict outcome := remint_id` attains perfect protected prediction without using the invariant task semantics. Therefore a test intended to establish remint-invariant behavior is invalid if remint identity or an equivalent encoding is visible. QED by construction.

The executable validator consequently rejects `remint_id`, `ecology_id`, protected split membership, protected outcome and architecture/family labels as agent-visible fields by default.

## 11. Structural closure theorem

Let `A2` be the exact 16 coordinate IDs frozen in `ecology_contract_v2.py`.

### Theorem A2-C — registry omission freedom at V2 scope [P1/executable]

If `ecology_contract_v2.run()` returns `PASS`, then:

1. all 16 A2 coordinate families occur exactly once and no extra coordinate is silently substituted;
2. scope, assumptions, evidence class, strongest parent, falsifier and G1 claim ceiling are present;
3. the finite witness includes two adaptive agents with explicit adaptation contracts;
4. train/development/held-out identities are pairwise disjoint;
5. hard budgets and prices share declared coordinates but are distinct objects;
6. verifier latency, cost, false-adoption and false-rejection losses are nonnegative registered values;
7. active information acquisition has explicit channel cost/latency/budget;
8. protected/remint identity fields are not agent-visible by default.

**Proof.** Each property is a direct predicate in `validate_contract`, `validate_instance`, or `run`; `PASS` occurs only after all error lists are empty. QED.

**Non-claim.** This proves a finite registration schema and its controls, not that a chosen ecology is scientifically representative or that any architecture should win within it.

## 12. Falsifier and claim ceiling

The A2 registration is falsified if a confirmatory claim depends on an ecology coordinate omitted or chosen after protected outcomes; if an adaptive agent is hidden as stationary noise; if resource feasibility is scalarized; if acquisition/verifier costs are uncharged; if protected identities leak; or if a supposed remint changes any registered semantic/economic object.

Strongest allowed terminal from this unit:

```text
A2_ECOLOGY_CONTRACT_REGISTERED_AT_G1
```

It does **not** earn `PREDICTIVE_MORPHOLOGY_PHASE_LAW_SUPPORTED_AT_REGISTERED_SCOPE`.
