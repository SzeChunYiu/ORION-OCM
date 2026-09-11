# GMI Neural-Explanation Completeness Audit v1

Status: **CLAIM-BOUNDARY / GAP-CLOSURE AUDIT**

Refs: `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`, `GMI_NEURAL_PREDICTION_TO_INTELLIGENCE_THEOREMS_V1.md`, `GMI_THEORY_GAP_LEDGER_V1.md`.

## 0. Why this audit exists

The phrase

> "explain why neural networks are so good"

is scientifically dangerous because it can hide several different questions behind one sentence.

A complete explanation must separately answer:

```text
Q1  Why is a neural system allowed to count as machine intelligence?
Q2  Can the architecture represent the required cognition?
Q3  Can the declared development rule reach a useful realization?
Q4  Why does the learned realization generalize rather than merely memorize?
Q5  Why does learned representation reduce downstream burden?
Q6  Why is the update/credit mechanism computationally feasible at scale?
Q7  Why can predictive/self-supervised objectives produce broad transferable state?
Q8  Why do depth, attention and parameter sharing help?
Q9  Why does expensive training pay off economically?
Q10 Why do accelerators and software stacks matter to the observed frontier?
Q11 Why can increasing data/model/compute continue to improve performance?
Q12 Why are neural networks not best for every obligation?
```

The v1 neural derivation now gives every question a typed answer, theorem family, measurable response term, or explicit open empirical subproblem.

That is **explanatory closure**, not a claim that all of deep-learning mathematics is solved.

---

# 1. Definition of structural explanatory completeness

For an obligation `O`, a neural explanation is structurally complete only if it supplies the tuple

\[
\mathcal E_N(\mathcal O)
=
(S_{\mathcal O},
 A,
 U,
 D,
 \Pi,
 G,
 \kappa,
 V,C,
 \rho_N,
 P),
\]

where:

- `S_O` — target semantic developmental quotient or registered approximation;
- `A` — neural architecture/realization family;
- `U` — actual development/update algorithm;
- `D` — information/development protocol;
- `Pi` — proxy objective / training signal;
- `G` — protected generalization/transfer relation;
- `kappa` — semantic interpretation/compiler;
- `V,C` — external verifier and constitution;
- `rho_N` — complete lifecycle resource meter;
- `P` — exogenous substrate/resource prices.

A statement of neural superiority that omits one of these when it materially affects the result is incomplete.

---

# 2. NEC-1 — architecture labels are never sufficient explanations

The following explanations are rejected as incomplete:

```text
"it is deep"
"it has many parameters"
"it uses attention"
"it is a Transformer"
"it uses SGD"
"it predicts the next token"
"it scales"
```

Each names a mechanism family, not a causal account.

The theory must show which protected burden or semantic term changes under an intervention on that mechanism.

---

# 3. NEC-2 — complete adequacy factorization

Every neural adequacy claim must be decomposable into at least:

\[
\epsilon_{total}
\lesssim
\epsilon_{repr}
+\epsilon_{opt}
+\epsilon_{gen}
+\epsilon_{int}
+\epsilon_{dyn},
\]

plus hard failure probabilities and resource burden.

Status: **CLOSED_FORMAL_AT_SCOPE**.

Reason: `GMI_NEURAL_MACHINE_INTELLIGENCE_DERIVATION_V1.md`, NMI-1.

This does not give a universal numeric bound. It gives the complete causal locations where error can enter.

---

# 4. NEC-3 — why neural systems can be machine intelligence

Required explanation:

```text
machine intelligence is morphology-neutral;
neural state realizes the same semantic developmental contract;
adequacy is judged by protected future semantics + resources, not by implementation label.
```

Status: **CLOSED_FORMAL_AT_SCOPE**.

This follows from the cross-paradigm realization normal form and semantic quotient theorem.

---

# 5. NEC-4 — representability

Required question:

> Is the target computation/state transition contained in, or well approximated by, the neural realization family?

Status: **CLOSED_BY_PARENT_RESULTS_FOR_REGISTERED FUNCTION CLASSES; OPEN FOR ARBITRARY OBLIGATIONS**.

Parents include universal approximation, sequence universal approximation, and idealized computational universality.

Important: representability is a possibility result, not a success explanation.

---

# 6. NEC-5 — representation efficiency

Required question:

> Is the target represented with lower parameter/state/compute burden because the architecture matches structure in the task?

Status: **CONDITIONAL THEORY CLOSED; EMPIRICAL REGIME OPEN**.

Parent depth-separation and compositional approximation results establish explicit families where deep structure gives exponential or strong savings.

GMI prediction: the advantage should track task composition/dependency geometry, not the word "deep".

---

# 7. NEC-6 — learned representation

Required question:

> Does development discover coordinates that make many protected distinctions cheaper to decode/use?

Status: **MEASUREMENT CONTRACT CLOSED; UNIVERSAL MECHANISM OPEN**.

Operational measure:

\[
\Delta B_{repr}
=
B(best\ matched\ downstream\ on\ raw\ input)
-
B(best\ matched\ downstream\ on\ learned\ representation).
\]

A positive protected burden gap supports the mechanism.

Human interpretability of neurons is not required.

---

# 8. NEC-7 — scalable credit assignment

Required question:

> How can a huge parameter state receive useful update information without one search per parameter?

Status: **CLOSED_COMPUTATIONALLY_AT_SCOPE**.

Reverse-mode automatic differentiation/backpropagation computes all parameter derivatives of a scalar objective with computational cost of the same asymptotic order as evaluating the graph, subject to memory/recomputation costs.

This explains the feasibility of updating very large differentiable states.

It does not guarantee semantic alignment or good minima.

---

# 9. NEC-8 — optimization/reachability

Required question:

> Why does the actual update algorithm find a good enough function in a nonconvex family?

Status: **PARTIALLY CLOSED / REGIME-DEPENDENT**.

Known parent theory proves convergence in specific overparameterized/kernel/mean-field or restricted regimes.

There is no accepted universal theorem that predicts practical deep-network training across all modern settings.

GMI treatment:

```text
optimization response is a family-specific response law;
overparameterization is a search-geometry mechanism;
protected experiments must measure reachability, not assume it.
```

No hidden explanatory gap remains: the unknown is localized to `epsilon_opt` / search response.

---

# 10. NEC-9 — generalization

Required question:

> Why does the learned function work outside the exact development sample?

Status: **STRUCTURAL EXPLANATION CLOSED; UNIVERSAL QUANTITATIVE LAW OPEN**.

The necessary GMI statement is:

> generalization occurs when the effective bias induced jointly by architecture, initialization, optimizer, objective, data and schedule aligns with regularities that remain valid in the protected ecology.

Random-label memorization proves raw capacity is insufficient.

Parent theories provide multiple useful mechanisms — margins/norms, stability, PAC-Bayes, benign interpolation, implicit bias, feature learning, manifold/spectral structure — but no single mechanism is universally established.

---

# 11. NEC-10 — why predictive pretraining transfers

Required question:

> Why should predicting observations teach state useful for other tasks?

Status: **CLOSED_FORMAL_AT_EXACT FINITE SCOPE**.

NPI-1 states:

\[
\sim_{pred}\subseteq\sim_{\mathcal O}
\iff
q_{\mathcal O}=g\circ q_{pred}.
\]

If the target semantic quotient factors through predictive state, prediction can supply all target-relevant distinctions in principle.

This is the central non-hand-wavy transfer theorem.

---

# 12. NEC-11 — why next-token prediction can learn broad latent structure

Required question:

> Why is next-token prediction not necessarily a narrow one-step task?

Status: **CLOSED_FORMAL_AT_IDEAL SCOPE**.

Exact conditionals for every reachable history determine arbitrary finite continuation distributions by the chain rule.

Therefore any latent distinction that changes continuation laws belongs to predictive state.

This explains broad state pressure without asserting a unique human-readable representation.

---

# 13. NEC-12 — limits of predictive learning

Required question:

> What does passive prediction fail to force into representation?

Status: **CLOSED_FORMAL_AT_SCOPE**.

NPI-2/NPI-6 establish the aliasing no-go.

Prediction alone need not preserve distinctions that matter only for:

```text
interventions;
causal consequences;
provenance/authority;
historical lineage;
future learning response;
OOD obligations absent from the development stream.
```

This blocks universal-intelligence claims from next-token prediction alone.

---

# 14. NEC-13 — controlled/interactive intelligence

Required question:

> What replaces passive prediction for agents whose actions change what happens?

Status: **CLOSED_FORMAL_AT_QUOTIENT LEVEL; LEARNING LAW OPEN**.

Use action-conditioned predictive state `S_cpred` and test whether target semantic state factors through it.

Parent predictive-state representations supply the relevant state concept.

---

# 15. NEC-14 — why attention helps

Required explanation:

```text
content-conditioned interaction/routing;
shared parameters;
context-sensitive composition;
parallelizable training;
compatibility with deep representation learning.
```

Status: **MECHANISM ACCOUNT CLOSED; UNIVERSAL OPTIMALITY REJECTED**.

Transformer universal-approximation results establish broad capacity, not universal superiority.

The advantage must be measured against alternatives under matched burden.

---

# 16. NEC-15 — why parameter sharing helps

A shared parameterization reduces burden when many positions/examples/tasks instantiate related local transformations or symmetries.

Status: **CONDITIONAL CLOSED**.

Negative twin:

```text
remove the shared regularity while preserving nominal input dimension.
```

Predicted result: sharing-specific sample/parameter advantage shrinks.

---

# 17. NEC-16 — why expensive pretraining pays

Required question:

> Why spend enormous compute before deployment?

Status: **CLOSED_LIFECYCLE_THEOREM**.

Neural pretraining is favored over alternative online computation after the reuse threshold

\[
N_{use}
>
\frac{C_{train}^{N}-C_{build}^{A}}
     {c_{query}^{A}-c_{query}^{N}}
\]

when the denominator is positive, with update/maintenance terms added as required.

This is the formal amortization explanation.

---

# 18. NEC-17 — why foundation models can support many tasks

Required question:

> Why can one pretrained state be reused across many downstream obligations?

Status: **CLOSED_CONDITIONAL_THEOREM**.

If for tasks `O_i`

\[
q_{\mathcal O_i}=g_i\circ q_{pred},
\]

then one shared predictive representation can support all tasks through task-specific projections.

The lifecycle advantage holds when

\[
B(q_{pred})+\sum_i B(g_i)
<
\sum_i B(q_{\mathcal O_i}\text{ learned separately}).
\]

---

# 19. NEC-18 — why in-context learning can look like rapid learning

Required explanation:

```text
frozen weights + changing context/activation state
can implement a different conditional computation without parameter update.
```

Status: **TYPE CLOSED; MECHANISM/SCALING EMPIRICAL**.

GMI records this as context-state adaptation in `Q/Z` unless weights or persistent developmental state change.

This prevents conflating fast execution-state adaptation with long-term learning.

---

# 20. NEC-19 — why overparameterization can help

Required explanation:

```text
extra realization degrees of freedom can improve search geometry;
semantic-state minimality does not require parameter minimality.
```

Status: **CONDITIONAL PARENT THEORY; PRACTICAL UNIVERSALITY OPEN**.

This resolves the logical paradox without claiming parameter count predicts generalization.

---

# 21. NEC-20 — why neural interpolation need not imply classical overfitting

Status: **PARENT THEORY EXISTS IN IMPORTANT REGIMES; NOT UNIVERSAL**.

Benign interpolation/double-descent phenomena show that zero training error is compatible with good test performance in high-dimensional settings.

GMI interpretation:

```text
training interpolation is neither sufficient nor disqualifying;
protected risk is the required quantity.
```

---

# 22. NEC-21 — why scale can keep helping

Required explanation:

> What does more data/model/compute buy?

Status: **EMPIRICAL LAW + PARTIAL PARENT THEORY**.

Scaling laws show broad power-law-like response regimes. Recent theory identifies variance-limited and resolution-limited mechanisms in simplified and partially realistic settings.

GMI places scaling in the morphology response map

\[
R_N(C,D,P),
\]

not in the definition of intelligence.

The open empirical variables are regime boundaries and exponents.

---

# 23. NEC-22 — hardware is causal, not incidental

Required question:

> Why did this morphology become practical now rather than under any substrate?

Status: **TYPE CLOSED / RESPONSE EMPIRICAL**.

Tensor accelerator prices belong in exogenous context `P`.

A hardware-price intervention that changes frontier membership is predicted and scientifically legitimate.

This prevents software-only mythology.

---

# 24. NEC-23 — data abundance and objective density

Required question:

> Why can neural learners consume web-scale or sensor-scale experience efficiently?

Status: **MECHANISM ACCOUNT CLOSED / QUALITY RELATION EMPIRICAL**.

Self-supervised objectives can derive many training constraints from raw streams. Shared parameters allow each example to update reusable structure.

But the signal must correlate with protected semantics; dense misinformation gives dense wrong credit.

---

# 25. NEC-24 — verification and truth

Required question:

> Does high neural confidence make an answer authoritative?

Status: **CLOSED_NEGATIVE**.

No.

External `V,C` remain separate from neural proxy objectives.

Neural systems can be intelligent proposal/prediction engines while exact truth/proof/provenance is supplied by other mechanisms.

---

# 26. NEC-25 — continual learning and forgetting

Required question:

> Are standard neural updates optimal when the world changes and old competence must be preserved?

Status: **OPEN RESPONSE; FAILURE MECHANISM KNOWN**.

Standard deep learners can lose plasticity or forget under continual learning.

GMI predicts that high local-revision + strict retention/lineage demand can move frontier optimality toward replay, modularity, external memory, versioning, local compilation, or hybrid structures.

This is not a gap in the explanatory type system; it is an active morphology-selection regime.

---

# 27. NEC-26 — exact symbolic obligations

Required question:

> Why not use neural networks for everything?

Status: **CLOSED_CONDITIONAL NEGATIVE**.

When obligations demand exact proof, exact arithmetic, certified provenance, branch history, reproducible state, or hard worst-case guarantees, neural approximation may be burden-dominated by symbolic/exact mechanisms or hybrids.

The theory therefore predicts neural/non-neural composition rather than universal neural replacement.

---

# 28. NEC-27 — causal/OOD transfer

Status: **OPEN_BLOCKING_UNIVERSAL CLAIMS**.

No passive observational objective can universally identify distinctions that only matter under unseen interventions or distribution changes.

To claim broad causal/OOD intelligence, the development protocol must include suitable invariance assumptions, interventions, environment variation, tools, or stronger structure.

Terminal when absent:

```text
OBSERVATIONAL_TRAINING_INSUFFICIENT_FOR_REGISTERED_INTERVENTION_SCOPE
```

---

# 29. NEC-28 — precise semantic interpretation of hidden features

Status: **NOT REQUIRED FOR BEHAVIORAL ADEQUACY; OPEN FOR MECHANISTIC INTERPRETABILITY**.

GMI only requires a sound semantic realization map at the claimed scope, not one-neuron/one-concept correspondence.

Mechanistic interpretability remains a separate scientific programme.

---

# 30. NEC-29 — consciousness / subjective experience

Status: **OUT OF SCOPE**.

The current GMI definition concerns externally registered machine-intelligence obligations, developmental competence and resource-bounded realization.

It neither requires nor explains phenomenal consciousness.

No claim about subjective experience is licensed by neural performance.

---

# 31. NEC-30 — no-free-lunch boundary

A morphology cannot be best for every possible ecology without assumptions about task/data structure and resource prices.

Status: **CLOSED_CONCEPTUAL BOUNDARY**.

Therefore "neural networks are universally best" is not a target theorem.

The target is:

> predict which ecology/resource regimes make neural mechanisms frontier-optimal, and predict the reversals when those regime variables are changed.

This is exactly the morphology-selection problem GMI is designed to solve.

---

# 32. Atomic closure table

| Explanatory atom | Status after neural v1 | Location |
|---|---|---|
| intelligence criterion independent of implementation | closed | GMI theory / realization normal form |
| neural specialization of realization state | closed | NMI v1 §2 |
| adequacy error factorization | closed at registered scope | NMI-1 |
| broad neural representability | parent-closed for major classes | NMI-2 |
| quotient lower bound on neural state | closed | NMI-3 |
| prediction-to-target sufficiency criterion | closed exact finite scope | NPI-1 |
| prediction-only insufficiency criterion | closed exact finite scope | NPI-2 |
| next-step to continuation prediction | closed | NPI-3 |
| controlled prediction for agents | closed quotient-level | NPI-6/7 |
| provenance/lineage separation | closed negative | NPI-8/9 |
| developmental-state distinction | closed | NPI-10 |
| approximate predictive transfer | contract defined, empirical modulus open | NPI-11 |
| depth/composition advantage | parent-closed for explicit families | NMI-6 |
| learned-representation benefit metric | closed measurement contract | NMI-7 |
| scalable gradient credit | parent-closed computationally | NMI-8 |
| overparameterized reachability | partial/conditional | NMI-9 |
| generalization | structural account closed, universal quantitative law open | NMI-10 |
| dense self-supervision | mechanism closed, semantic quality empirical | NMI-11 |
| amortization threshold | closed | NMI-12 |
| hardware-price role | closed type-level | NMI-13 |
| Transformer mechanism bundle | closed explanatory decomposition | NMI-14 |
| neural-friendly demand regime | frozen hypothesis | NMI-15 |
| lifetime burden decomposition | closed | NMI-16 |
| scaling response type | closed, exponents/regimes empirical | NMI §19 |
| external authority separation | closed | NMI §20 |
| canonical neural falsifiers | closed | NMI §21 |

---

# 33. Claim ceiling after this audit

It is now defensible to say:

> **GMI contains a structurally complete causal explanation of how a neural network can realize machine intelligence and why deep gradient-trained neural systems can be exceptionally effective in data-rich, reusable, approximately verifiable, tensor-cheap ecologies. The explanation is conditional and falsifiable: it decomposes success into representability, learned representation, scalable credit assignment, development/search geometry, generalization alignment, predictive-state reuse, amortization, dynamic routing, substrate economics and scaling response.**

It is **not** defensible to say:

```text
GMI has solved every quantitative phenomenon in deep learning;
SGD generalization is universally solved;
next-token prediction guarantees universal intelligence;
Transformers are mathematically optimal for all cognition;
scaling laws continue without bound;
neural networks eliminate the need for verification or exact mechanisms.
```

The distinction is important.

A theory is not made complete by calling unknown response functions "emergence". GMI v1 instead assigns each unknown a typed location and a falsifiable measurement programme.

---

# 34. Next experimental consequences

The neural theory now predicts concrete reversals suitable for E1/E2-style validation:

1. `rho_use` intervention should produce an amortization crossover;
2. compositional vs non-compositional task families should change depth advantage;
3. passive-prediction collisions should selectively break causal/provenance/lineage tasks;
4. action-conditioned predictive training should repair a subset of causal/control collisions;
5. hardware repricing should alter morphology frontier membership;
6. strict retention/local-revision demand should favor augmented modular/versioned neural or hybrid systems over plain monoliths;
7. reminting surface identity while preserving predictive structure should preserve mechanism-level transfer if the theory is not using world IDs;
8. random-label structure destruction should preserve fit capacity but destroy generalization advantage;
9. decreasing downstream task overlap with predictive state should reduce pretraining transfer benefit;
10. increasing number/reuse of tasks that factor through one predictive state should strengthen foundation-model economics.

These are more informative than asking whether neural networks "work" in aggregate.
