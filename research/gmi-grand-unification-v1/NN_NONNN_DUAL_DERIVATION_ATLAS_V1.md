# Grand GMI Neural / Non-Neural Dual Derivation Atlas V1

Status: **END-TO-END SYNTHESIS / EXACT FINITE WORKED ATLAS**  
Date: 2026-09-12

## 1. Purpose

Grand GMI now has the abstract pieces required to derive realized intelligence forms: semantic quotients, semantic cuts, local transformation complexity, symmetry, distributed composition, realization compilation, morphology selection, architecture refinement, developmental reachability, physical-resource transport, deployment adequacy and family-frontier phase laws.

The remaining explanatory problem is to show the chain running end-to-end on concrete obligations without silently replacing an operational property by an architecture name.

This atlas does that for several exact finite tasks. Each row separates four questions:

1. **What does the obligation force?**
2. **What operational morphology follows?**
3. **How can a neural process realize it?**
4. **How can a non-neural process realize it?**

Family selection occurs only after resource/reachability/deployment evidence is added.

## 2. Master rule

For a registered problem

\[
\mathcal G=(\mathbf P,\mathcal E,\Omega,\rho,Q),
\]

Grand GMI first derives obligation-relative operational necessities, not implementation syntax:

\[
\mathcal G
\to S^*
\to (\kappa,\tau)
\to \text{symmetry/memory/routing/coupling constraints}
\to \text{operational morphology}.
\]

Only then do realization theorems compile that morphology into candidate families:

\[
\text{operational morphology}
\to \{\text{NN},\text{non-NN},\text{hybrid},...\}.
\]

Finally physical, developmental and deployment evidence selects among those candidates:

\[
\{Y_F\}_F
\to \text{reachable robust frontier}
\to \text{family / architecture verdict}.
\]

Therefore the theory can derive a neural network **without defining intelligence as a neural network**, and can derive a non-neural intelligence by exactly the same logic.

## 3. Atlas A — exact finite Boolean intelligence

### Obligation

For `x in {0,1}^3`, output the parity bit

\[
y=x_1\oplus x_2\oplus x_3.
\]

### GMI derivation

The protected output has two response classes, but the local transformation must compute the parity relation over eight possible inputs. A one-bit final cut is sufficient once parity has been computed; the transformation complexity is not determined by that one output bit alone.

### Neural realization

The finite realization compiler constructs a threshold network by creating one hidden threshold detector for each positive minterm and an output threshold OR over those detectors. This exactly realizes parity.

### Non-neural realization

A truth table, Boolean XOR circuit or straight-line program exactly realizes the same response relation.

### Verdict

Semantics alone gives **FAMILY_COEXISTENCE**. Neurality is not derived until a registered resource/reachability criterion excludes the exact non-neural alternatives; non-neurality is not derived until the converse exclusion is certified.

This is the canonical demonstration that `one output bit` does not mean `one unit of computation` and that realizability is weaker than family necessity.

## 4. Atlas B — persistent memory / recurrence

### Obligation

Observe a symbol `a` from an alphabet of size `m`, pass through an interval containing no information about `a`, then reproduce `a` exactly.

### GMI derivation

The temporal boundary is a semantic cut. Exact delayed reproduction requires at least `m` distinguishable persistent semantic states; otherwise two obligation-distinct messages collide and cannot later be decoded.

Thus recurrence/persistent state is operationally necessary whenever the future obligation depends on information absent from the intervening ecology.

### Neural realization

A recurrent neural state can encode the `m` semantic states. For binary `m=2`, one protected binary recurrent state suffices at the semantic level; larger `m` can use a distributed code.

### Non-neural realization

A finite-state machine with at least `m` distinguishable states realizes the same memory obligation exactly.

### Verdict

Grand GMI can derive **PERSISTENT_STATE_REQUIRED** and a lower bound on state distinguishability. It does not thereby derive the historical software class `RNN`. RNN-like recurrence and FSM state are alternative realizations until the family frontier selects one.

## 5. Atlas C — translation equivariance / local shared computation

### Obligation

On a cyclic binary string `x=(x_0,...,x_{n-1})`, produce

\[
y_i=x_i\oplus x_{i+1\;mod\;n}.
\]

The ecology and obligation commute with cyclic translation.

### GMI derivation

The symmetry layer permits an equivariant representative. The transformation also factorizes into repeated local radius-one relations, so the operational morphology is a shared local equivariant map.

### Neural realization

A convolution-like neural implementation applies the same local XOR-realizing threshold subnetwork at every position.

### Non-neural realization

A cellular automaton, stencil program or repeated XOR gate array applies the identical local rule at every position.

### Verdict

Grand GMI derives **LOCAL_TRANSLATION_EQUIVARIANT + SHARED_LOCAL_RULE** under the registered symmetry/locality hypotheses. It does not uniquely derive `CNN` because the non-neural stencil/automaton is operationally equivalent on the protected relation.

If substrate/resource evidence leaves only the neural shared-kernel realization on the selected frontier, the certificate can then return a neural/convolution-like verdict.

## 6. Atlas D — context-dependent routing / gating

### Obligation

Given context bit `c` and sources `x_0,x_1`, output

\[
y=\begin{cases}x_0,&c=0\\x_1,&c=1.\end{cases}
\]

### GMI derivation

No fixed one-source route can be exact on all eight `(c,x_0,x_1)` cases. The routing decision must depend on obligation-relevant context. The semantic cut therefore carries both source information and a control distinction sufficient to choose the relevant source.

### Neural realization

A gating network or two-expert MoE-like process computes a context-conditioned gate and selects/composes the expert outputs.

### Non-neural realization

A digital multiplexer or `if/else` program performs exactly the same conditional route.

### Verdict

Grand GMI derives **DYNAMIC_CONTEXT_ROUTING_REQUIRED**, not `MoE` as syntax. MoE-like neural routing becomes derived only after non-neural multiplexers and other operationally equivalent routers are excluded by the registered frontier.

## 7. Atlas E — permutation-invariant aggregation / graph-set intelligence

### Obligation

Receive an unordered collection of three binary observations and output whether any observation is `1`:

\[
y=\mathbf 1[\sum_i x_i\ge 1].
\]

### GMI derivation

The obligation is invariant under every permutation of the three inputs. Any unique deterministic optimum under the symmetry hypotheses must therefore be permutation invariant at the protected level. The relevant global information is an aggregate sufficient statistic for the obligation.

### Neural realization

A Deep-Sets/message-passing-like neural process can apply shared node transforms, aggregate by a symmetric sum/max operation, then threshold.

### Non-neural realization

An OR-reduction tree, distributed consensus/reduction algorithm or ordinary loop over the set computes the identical invariant relation.

### Verdict

Grand GMI derives **PERMUTATION_INVARIANT_AGGREGATION**. A GNN/Deep-Sets label is a refinement requiring additional graph/locality/coupling constraints and family-selection evidence.

## 8. Atlas F — content-addressed selection / attention-like computation

### Obligation

A query selects one of several key-value records by key equality and returns its associated value. The relevant record is not fixed by position; it depends on query-content relation.

### GMI derivation

The downstream obligation depends on comparing the query against multiple candidate keys and routing the matching value. A fixed positional route fails when the matching record moves. This forces a content-dependent comparison-and-routing operation at the registered resolution.

### Neural realization

An attention-like network can construct query/key match scores and use them to route or combine values.

### Non-neural realization

A dictionary/hash lookup, associative memory or explicit key-comparison program performs the same content-addressed selection.

### Verdict

Grand GMI may derive **CONTENT_DEPENDENT_GLOBAL_ROUTING / ASSOCIATIVE_LOOKUP**, but not uniquely `Transformer`. Transformer syntax additionally packages normalization, residual pathways, feed-forward blocks, positional mechanisms and other design choices not forced by content-addressed routing alone.

## 9. Atlas G — exact symbolic controller

### Obligation

A finite semantic quotient has states `S`, exact transition relation `T:S x I -> S`, and exact action map `A:S -> O`. No approximation error is admitted.

### GMI derivation

If the quotient is minimal under protected response equivalence, any exact implementation must realize enough persistent distinctions for those quotient states and the exact transition/action maps.

### Neural realization

A threshold/recurrent network can encode the finite states and exact transition table.

### Non-neural realization

A minimal deterministic finite-state controller directly realizes the quotient.

### Possible family derivation

If a certified non-neural controller has exact verification and a resource upper bound that robustly dominates the lower bound for every adequate neural realization, the family phase law yields **DERIVED_NON_NEURAL**.

The important point is that the non-neural verdict comes from the quotient plus comparative physical evidence, not from declaring symbolic systems intrinsically more intelligent.

## 10. Atlas H — continuous/high-dimensional approximation

### Obligation

A protected response is continuous on a compact registered domain and must be approximated within tolerance `epsilon`.

### GMI derivation

Finite-resolution semantic geometry gives a finite cover at positive tolerance when the response space is totally bounded. The transformation layer specifies the approximation obligation; an imported universal-approximation theorem may supply a neural realization when its hypotheses hold.

### Neural realization

A suitable neural family can approximate the response to the required tolerance, with model size/training cost entering the registered resource vector.

### Non-neural realization

Polynomial/spline approximation, lookup/interpolation, decision diagrams, numerical programs, analog circuits or other parent-theory constructions may realize the same tolerance.

### Verdict

Universal approximation proves **neural realizability**, not neural necessity. A `DERIVED_NEURAL` verdict requires certified resource/reachability/deployment inequalities that exclude the non-neural approximators at the declared scope.

## 11. Atlas I — hybrid intelligence

### Obligation

Suppose the operational task decomposes into:

- `R_s`: a statistical/continuous perception or estimation region;
- `R_x`: an exact symbolic verification/control region;
- a registered semantic cut joining them.

### GMI derivation

The family-phase hybrid theorem composes regional upper bounds plus bridge cost.
A witnessed mixed assignment below valid whole-family lower bounds excludes
the registered pure competitors. Regional lower bounds cover monolithic
competitors only with FP-5b decomposition coverage. An exact selected hybrid
additionally requires nonempty attained selection, as in MSC-1–3.

### Realization

A neural subsystem can realize `R_s`; an FSM/program/verifier can realize `R_x`; the cut transmits exactly the obligation-relevant interface.

### Verdict

This is **DERIVED_HYBRID** only when the selected set is nonempty and all its morphologies require mixed-family regional realization. Merely attaching a symbolic tool to a neural model is not a derivation.

## 12. Where named neural architectures come from

The architecture-refinement layer can recursively refine a neural family verdict using operational properties:

| Derived operational property | Neural realization class that may satisfy it | Non-neural counterpart |
|---|---|---|
| local translation equivariance | convolution-like shared kernels | stencil / cellular automaton / shared circuit |
| persistent hidden state | recurrent/state-space neural process | FSM / state estimator / dynamic program |
| permutation-equivariant graph aggregation | GNN/message passing | distributed graph algorithm |
| content-dependent global routing | attention-like process | associative lookup / routing network |
| context-selective sparse routing | MoE-like gating | multiplexer / dispatcher / rule system |
| hierarchical composition | deep/compositional network | program/circuit tree / multistage controller |
| exact finite transition law | quantized/threshold recurrent net | automaton / transition table |

The left column is what Grand GMI can derive directly from the obligation and constraints. The middle/right columns are realization families. Selection between them comes later.

## 13. What would count as a genuine derivation of a CNN, RNN, GNN or Transformer?

A named neural architecture is derived only when:

1. its name is converted into a protected operational definition;
2. the obligation forces the defining operational properties;
3. a neural realization witness exists;
4. developmental reachability is certified under the declared training/search law;
5. deployment adequacy is certified;
6. measured/proved resource bounds exclude operationally distinct competing neural and non-neural realizations;
7. the candidate universe is explicitly scoped.

For example, translation symmetry plus local interaction can derive convolution-like weight sharing. It does **not** by itself derive every historical component of a modern CNN.

Likewise, content-addressed routing can derive attention-like computation. It does **not** by itself derive the full Transformer stack.

## 14. Exact checker coverage

The accompanying checker verifies finite instances of the atlas:

- all `8` parity-3 inputs;
- cyclic local-XOR translation equivariance for all `16` four-bit strings and all `4` cyclic shifts (`64` checks);
- context-dependent routing on all `8` selector/source triples, including the `6/8` ceiling for each fixed route and `8/8` for dynamic routing;
- permutation invariance of OR aggregation on all `8` three-bit sets under all `6` permutations (`48` checks);
- delayed-memory injectivity for `m=4` across state alphabets of sizes `1..4` (`354` encodings), with exact reproduction possible first at four states and exactly `24` bijective minimal encodings;
- opposite legal resource orderings selecting opposite families for one response-equivalent obligation;
- the hybrid inequality witness with mixed upper bound `8` below both pure-family lower bounds `12`.

## 15. Closure statement

At the formal level, Grand GMI now explains NN and non-NN intelligence through one substrate-neutral derivation grammar:

\[
\boxed{
\text{obligation}
\to \text{semantic necessities}
\to \text{operational morphology}
\to \text{multiple realizations}
\to \text{physical/developmental/deployment comparison}
\to \text{selected neural, non-neural, hybrid, coexistence or undecided form}.
}
\]

The theory does not claim that every real-world architecture verdict is already known. Real verdicts still require real resource, reachability and ecology evidence. What is closed here is the explanatory bridge: neural and non-neural intelligence are derived by the same rule rather than by separate definitions of intelligence.
