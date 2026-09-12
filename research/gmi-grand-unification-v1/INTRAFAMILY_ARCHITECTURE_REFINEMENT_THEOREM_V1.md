# Grand GMI Intra-Family Architecture Refinement Theorem V1

Status: **THEOREM / OPERATIONAL ARCHITECTURE-PROPERTY DERIVATION WITH NAMED-FAMILY BOUNDARY**  
Date: 2026-09-12

## 1. Gap closed

Grand GMI can now derive whether the reachable resource frontier is neural, non-neural, hybrid, coexistent or empirically undecided. That verdict is still too coarse for questions such as:

- why convolution-like structure rather than a dense unstructured network?
- why recurrent state rather than a stateless feed-forward map?
- why content-dependent routing/attention rather than fixed routing?
- why a finite-state controller rather than a learned recurrent network?
- why a graph/message-passing morphology rather than a sequence morphology?

The answer cannot be an architecture-name lookup. Grand GMI must derive **operational properties** from the registered obligation, ecology, cuts, symmetries, transformation lower bounds, physical resources and reachability, then apply the existing morphology-selection criterion inside the selected family.

## 2. Operational architecture signature

For a morphology `m`, define a registered architecture signature

\[
\sigma(m)=(D_m,L_m,G_m,R_m,S_m,U_m),
\]

where:

- `D_m` is the dependency relation: which upstream variables can causally affect each protected downstream output;
- `L_m` is locality/range structure;
- `G_m` is the equivariance/symmetry action preserved by the protected process;
- `R_m` is routing/communication structure, including fixed vs content-dependent interfaces;
- `S_m` is persistent state/memory structure across temporal cuts;
- `U_m` is developmental/update structure.

These are operational properties. Source syntax, framework class names and parameter tensor names are not protected unless explicitly registered.

## 3. AR-1 — architecture-property derivation criterion

Let `M*` be the selected reachable morphology set under the registered Pareto or explicit selection rule. An architecture property `A` is derived at the registered scope iff

\[
\forall m\in M^*,\quad A(\sigma(m)).
\]

This is the Morphology Selection criterion applied at a finer resolution.

A property may be derived even when the implementation family is not. For example, every selected realization may require persistent state while some are neural recurrent networks and others are finite-state controllers.

Conversely, selecting the neural family does not derive convolution, recurrence, attention, graph aggregation or sparsity unless those finer properties survive the same universal selected-set test.

## 4. AR-2 — symmetry gives a representative, not automatic necessity

If the hypotheses of the existing Symmetry-to-Morphology Theorem hold, an equivariant frontier representative exists. That result alone does not imply that every frontier realization is syntactically equivariant or parameter tied.

Therefore:

- task symmetry can justify searching an equivariant operational class;
- unique selected optimum can force equivariance of the protected behavior;
- weight sharing as physical storage reuse requires an additional resource/reachability argument;
- historical labels such as `CNN`, `GNN` or `Deep Sets` do not follow from symmetry alone.

This prevents a common invalid inference: `translation-invariant task -> CNN is the unique intelligence form`.

## 5. AR-3 — local equivariant operator theorem

Suppose the registered obligation decomposes over sites `i` as

\[
y_i = f(N_r(i)),
\]

where `N_r(i)` is a radius-`r` neighborhood, the same protected local response law is required at every site under a transitive symmetry group, nonlocal dependencies are forbidden or resource-dominated, and every selected morphology uses the same local protected operator class.

Then the selected architecture has a **local shared/equivariant operational structure**.

This is convolution-like or stencil-like behavior. The theorem does not distinguish among a convolutional neural network, a hand-coded stencil, a cellular automaton, an analog local operator or another substrate realization unless additional family/resource evidence does so.

## 6. AR-4 — temporal-state necessity theorem

Let two histories `h_0,h_1` become observationally identical to the environment after a temporal cut but require different later protected outputs under some admitted continuation. Then the cut-conflict theorem requires distinct persistent messages/states across that cut.

If every selected realization must carry such a state, **recurrence/state retention is architecture-derived**.

The implementation may be:

- an RNN/LSTM/state-space neural system;
- a finite-state controller;
- a program variable or memory cell;
- a physical latch;
- a biological internal state;
- another process-theoretic memory.

Thus Grand GMI can derive recurrence without deriving neurality.

## 7. AR-5 — content-dependent routing theorem

Suppose the obligation requires choosing among sources according to a context variable `q`, and under the registered access constraints every fixed source-routing policy fails on at least one admitted case while a context-conditioned routing process is adequate.

Then **content/context-dependent routing is architecture-derived**.

If the source set is large or variable and the routing operation computes compatibility between a query and candidate keys/content, the operational property is attention-like. But `Transformer` is not uniquely derived unless all selected realizations additionally satisfy the registered Transformer operational definition and competing dynamic-routing realizations are excluded.

A programmatic multiplexer, associative memory, routing circuit or neural attention head may share the same protected routing property.

## 8. AR-6 — permutation/graph aggregation theorem

Suppose the ecology is a set or graph whose node labels are operationally arbitrary, the obligation is invariant/equivariant under admitted relabelings, information is constrained to local graph neighborhoods, and selected morphologies must aggregate neighbor information while preserving the relabeling action.

Then a **permutation-equivariant local aggregation** property is derived.

This is message-passing/GNN-like at the operational level. It can also be realized by distributed programs, graph algorithms, cellular processes or analog networks. A historical GNN software family is selected only after family/resource/reachability comparison.

## 9. AR-7 — sparse conditional expert routing theorem

Suppose the obligation decomposes into contexts for which distinct local transformations are adequate, only a strict subset of those transformations may be active under the registered compute/energy budget, and the context identifies which subset is required.

If every selected morphology therefore implements context-conditioned sparse activation of transformation modules, **expert-routing sparsity** is architecture-derived.

This is MoE-like operational structure. The experts need not themselves be neural.

## 10. AR-8 — named architecture criterion

A named architecture `Name` is derived only if:

1. `Name` has an operational definition in terms of protected architecture-signature properties, not merely code heritage;
2. the family containing `Name` is feasible/reachable;
3. every selected morphology satisfies that operational definition, or a declared unique selection rule selects its equivalence class;
4. competing operationally distinct realizations are excluded by obligation, resource, substrate or reachability evidence.

Consequently:

- local translation-equivariant processing may derive `convolution-like` without uniquely deriving `CNN`;
- persistent state may derive `recurrent` without uniquely deriving `RNN`;
- dynamic query-dependent routing may derive `attention-like` without uniquely deriving `Transformer`;
- permutation-equivariant neighbor aggregation may derive `message-passing` without uniquely deriving `GNN`;
- sparse context-conditioned modules may derive `expert routing` without uniquely deriving a neural `MoE`.

This is a feature, not a weakness: Grand GMI explains which physical/operational properties intelligence needs before attaching implementation names.

## 11. Exact finite witnesses

The accompanying checker freezes three architecture-property derivations.

### 11.1 Local translation-equivariant rule

On a four-site binary ring,

\[
y_i=x_i\oplus x_{i+1}.
\]

Across all 16 inputs and all four cyclic shifts, the target map commutes with translation. Every output coordinate depends only on the radius-one local pair. A shared XOR stencil and a shared local neural threshold construction can implement the same protected map.

Verdict: `LOCAL_TRANSLATION_EQUIVARIANT` is task-level structure; neurality is not implied.

### 11.2 Delayed bit reproduction

A bit is observed, then disappears, then must be reproduced later. A one-state machine cannot distinguish the two histories; a two-state recurrent machine can.

Verdict: `PERSISTENT_STATE_REQUIRED`. Both a neural recurrent realization and a two-state FSM satisfy the property.

### 11.3 Context-dependent source selection

Two stored bits `(x0,x1)` are followed by query `q`; output must be `x_q`. Any routing rule that always chooses one fixed source fails on some cases; context-conditioned routing is exact on all eight `(x0,x1,q)` cases.

Verdict: `DYNAMIC_ROUTING_REQUIRED`. A neural attention-like selector and a programmatic multiplexer share the property.

## 12. Expanded derivation chain

The architecture-level chain is now

\[
\mathcal G
\to S^*
\to \kappa,\tau
\to \text{symmetry/coupling/dependency constraints}
\to \text{family selection}
\to \sigma(m)
\to \text{selected operational architecture properties}
\to \text{named architecture only if the operational definition is forced}.
\]

This gives Grand GMI a principled answer to both neural and non-neural architecture questions: first derive what the process must *do structurally*, then let substrate/resource/developmental evidence decide how that structure is realized.

## 13. Boundary

This theorem does not claim that current CNNs, Transformers, RNNs, GNNs or MoEs are globally optimal for real-world tasks. It supplies the conditional derivation rules that a real claim would have to satisfy.

Nor does it collapse non-neural intelligence into neural metaphors. The same derived operational property can belong to distinct physical families; family identity remains a separate morphology/resource conclusion.
