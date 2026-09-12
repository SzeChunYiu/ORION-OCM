# Grand GMI Neural / Non-Neural End-to-End Derivations V1

Status: **WORKED DERIVATION LAYER WITH EXACT FINITE WITNESSES**  
Date: 2026-09-12

## 1. Purpose

The Grand GMI stack now contains the formal pieces needed to discuss implementation form:

\[
\mathcal G
\to S^*
\to \kappa
\to \tau
\to \text{symmetry/coupling}
\to \mathcal A
\to \text{realization}
\to \text{family-conditioned frontier}
\to \text{selected morphology}.
\]

This document executes that chain on small problems. The examples are deliberately finite enough to check exhaustively. Their resource numbers are **declared proof-witness models**, not measurements of real CPUs, GPUs, brains or accelerators.

The aim is to show exactly where a neural, non-neural, hybrid or underdetermined verdict enters—and where it does not.

---

# 2. Derivation A — exact hazard controller selects non-neural intelligence

## 2.1 GMI problem

Let the ecology expose one hazard bit

\[
h\in\{0,1\},
\]

and let the action be

\[
a\in\{0,1\},
\]

where `1` means stop. The obligation is exact:

\[
\Omega(h,a)=1\iff a=h.
\]

Take a classical finite process presentation. Register zero error and resource coordinates `(energy,memory,latency)`.

## 2.2 Semantic quotient

The two ecology states cannot be merged. If `h=0` and `h=1` were represented by one semantic state, the controller would have to choose the same action for both, violating one case.

Therefore

\[
|S^*|=2.
\]

## 2.3 Semantic cut

Put a cut between sensor and controller. With no downstream side information, the acceptable action sets are

\[
\Gamma(0)=\{0\},\qquad \Gamma(1)=\{1\}.
\]

Their intersection is empty, so the conflict graph is `K_2`. Therefore

\[
\chi(H_C)=2,
\qquad
b_C^0=\lceil\log_2 2\rceil=1.
\]

Exactly one protected bit must cross the sensor/controller cut.

## 2.4 Local transformation complexity

The controller computes the identity function `a=h`. One query of `h` is necessary and sufficient in the ordinary deterministic decision-tree model:

\[
\tau_{query}=1.
\]

No persistent memory is required after the action is emitted.

## 2.5 Realizations

Two exact realizations are immediate.

**Non-neural:** a wire, one-entry-per-input table, or two-state exact controller implementing `a=h`.

**Neural:** one hard-threshold unit

\[
a=H(h-1/2).
\]

Both satisfy the same protected obligation.

## 2.6 Declared substrate model and selection

For this proof witness, declare both realizations reachable and assign

\[
\rho(P)=(1,1,1),
\qquad
\rho(N)=(2,2,2).
\]

`P` strictly dominates `N` in every registered resource coordinate. By cross-family domination, the neural realization is absent from the selected frontier.

### Verdict

\[
\boxed{\text{non-neural family derived at this registered scope}.}
\]

What was actually derived is an exact one-bit sensor/controller process. The non-neural family verdict comes only after the declared substrate resource comparison.

---

# 3. Derivation B — translation-symmetric local obligation selects a neural realization

## 3.1 GMI problem

Let the ecology be a binary ring

\[
x=(x_0,\ldots,x_{n-1})\in\{0,1\}^n,
\]

with cyclic indexing. The protected output is the local-pair detector

\[
y_i=x_i\land x_{i+1}
\qquad (i\bmod n).
\]

The obligation is exact reproduction of the full output vector `y`.

## 3.2 Local semantic necessity

For each local output `y_i`, both input bits are obligation relevant:

- fix `x_{i+1}=1`; changing `x_i` changes `y_i`;
- fix `x_i=1`; changing `x_{i+1}` changes `y_i`.

If the two sensor values cross separate exact cuts into the local region, each cut must distinguish two messages. Thus each local input cut has

\[
\chi(H_C)=2,
\qquad
b_C^0=1.
\]

## 3.3 Local computation

The required local kernel is Boolean AND. A deterministic decision tree has worst-case query complexity two: on input prefix `1`, the second bit must still be queried, and there exist inputs requiring both observations.

Thus the local transformation obligation is not a constant or one-input map.

## 3.4 Symmetry-to-morphology

The cyclic group `C_n` acts by rotating the input and output indices. The obligation commutes with that action:

\[
f(gx)=g f(x).
\]

Under the symmetry theorem's registered convexity/invariance hypotheses, an equivariant frontier representative exists. In this finite exact construction we can exhibit one directly: use the **same two-input local kernel at every site**.

This derives an operational morphology with repeated local computation and parameter/rule sharing. It is convolution-like, but the architecture name "CNN" has not yet been selected.

## 3.5 Neural realization

A shared hard-threshold unit at every site computes

\[
y_i=H(x_i+x_{i+1}-3/2).
\]

The same weights and bias are reused under cyclic translation. This is an exact neural realization of the repeated local operational kernel.

## 3.6 Non-neural realization

An array of identical AND gates, a cellular-automaton-style rule, or a loop executing the same Boolean operation at every site gives the identical protected response and the identical operational equivariance.

Therefore symmetry and locality alone still do not prove neural necessity.

## 3.7 Declared substrate model and selection

Now register a substrate/resource model for the two candidate families:

\[
\rho(N_{shared})=(2,2,2),
\qquad
\rho(P_{shared})=(4,5,3).
\]

Assume both are reachable and no omitted candidate has a nondominated profile. Then the shared neural realization strictly dominates the registered non-neural realization.

### Verdict

\[
\boxed{\text{neural family derived in this declared candidate/substrate scope}.}
\]

The derivation is conditional on the resource model. The architecture-free part derives **local repeated equivariant computation**; the substrate comparison selects the neural implementation.

It still does not establish that a historical CNN software definition is uniquely necessary. A finer within-family theorem would be required for that name.

---

# 4. Derivation C — factored obligation selects a hybrid neural/non-neural intelligence

## 4.1 Product obligation

Combine two independent protected obligations:

1. Region A performs the translation-symmetric local detector of Derivation B.
2. Region B performs the exact one-bit hazard controller of Derivation A.

The protected output is the pair `(y,a)`. Assume the ecology, obligation, error budget and physical resources factor exactly between the two regions, so the Compositional GMI product theorem and the separable family-selection theorem apply.

## 4.2 Local family profiles

Use the following exact proof-witness resource profiles:

For region A:

\[
\rho_A(N)=(1,2),
\qquad
\rho_A(P)=(5,5).
\]

For region B:

\[
\rho_B(N)=(5,5),
\qquad
\rho_B(P)=(1,2).
\]

Resources compose additively and there is no uncounted interface penalty.

## 4.3 Global assignments

The four family assignments are

\[
NN=(6,7),
\qquad
NP=(2,4),
\qquad
PN=(10,10),
\qquad
PP=(6,7).
\]

The neural/program assignment `NP` strictly dominates all three alternatives.

### Verdict

\[
\boxed{\text{hybrid neural + non-neural intelligence derived}.}
\]

The hybrid is not a compromise added by hand. It is the selected realization of a factored operational morphology whose regions have different substrate/resource optima.

If the obligation becomes coupled, interface costs become large, or resource composition becomes nonadditive, this proof no longer applies and the assignment must be recomputed.

---

# 5. Derivation D — XOR remains family-underdetermined

## 5.1 Obligation

Let

\[
y=x_1\oplus x_2.
\]

The semantic response has two output classes, and both inputs are locally relevant.

## 5.2 Exact neural realization

One threshold construction is

\[
a=H(x_1+x_2-1/2),
\qquad
b=H(x_1+x_2-3/2),
\]

\[
y=H(a-b-1/2).
\]

## 5.3 Exact non-neural realization

A four-entry truth table or XOR gate is exact.

## 5.4 Incomparable resources

Declare

\[
\rho(N)=(2,4),
\qquad
\rho(P)=(4,2).
\]

Neither point dominates the other.

### Verdict

\[
\boxed{\text{family not derived}.}
\]

Both realizations remain on the Pareto frontier. A claim that Grand GMI "chooses neural" or "chooses symbolic" here would be false unless another resource coordinate, budget, reachability restriction or explicit selection constitution were added.

This example is as important as the positive selections because it shows that the framework is allowed to return **underdetermined**.

---

# 6. What is architecture-free and what is substrate-conditional?

| Stage | Derived without naming NN/non-NN? | Needs substrate/family data? |
|---|---|---|
| semantic quotient `S*` | yes | no |
| cut requirement `kappa` | yes | physical carrier cost does |
| local transform requirement `tau` | yes | implementation cost does |
| symmetry/coupling property | yes under theorem hypotheses | syntax still no |
| operational morphology class | yes/conditional on registered constraints | not necessarily family |
| neural/non-neural realizability | compiler theorem | family hypotheses |
| neural vs non-neural selection | no | **yes** |
| named architecture uniqueness | no | **yes, plus within-family exclusion** |
| developmental realized form | reachability theorem | update physics/budget |

The framework therefore derives intelligence in two layers:

1. **semantic/operational intelligence:** what distinctions, transformations, cuts and responses are required for the obligation;
2. **physical morphology:** which realizable implementation lies on the registered reachable resource frontier.

Neurality belongs to layer 2 unless it is explicitly promoted to a protected semantic property.

# 7. Non-neural does not mean non-learning

A non-neural realization can still be adaptive. In Recursive Morphogenesis, the morphology state and update action can represent:

- program synthesis;
- rule induction;
- finite-state controller adaptation;
- evolutionary search;
- Bayesian or symbolic update;
- lookup/table refinement;
- analog control adaptation;
- quantum-control policy update.

Conversely, a fixed neural network need not be developmentally adaptive at all. "Neural" and "learning/intelligent" are different axes in Grand GMI.

# 8. Neural does not mean uniquely brain-like

A neural realization is one implementation family for operational kernels. Weight sharing may be forced by symmetry, recurrence by temporal cuts, routing by context-dependent communication, or memory by delayed obligation distinctions. But these operational properties can often be realized by non-neural processes too.

Therefore the strongest valid claim has the form:

> Given problem `G`, substrate `P`, candidate universe `F`, resource map `rho`, tolerance `epsilon`, reachability budget `B`, and selection rule `Sigma`, every selected realization has property `P_arch`.

That is a derivation. "This architecture is popular and can solve the task" is not.

# 9. Relation to phenomenology reduction

The phenomenology-saturation layer reduces memory, routing, in-context state, continual retention and tool use to the existing Grand GMI master objects. The present document adds the implementation step: those operational roles may then be compiled into and selected among neural, non-neural or hybrid realizations using the Realization Compilation, Morphology Selection and Family Selection theorems.

Thus a phenomenon such as memory does not become "neural memory" until the family-conditioned frontier selects a neural realization of the required temporal cut/state capacity.

# 10. Remaining gap after the worked traces

The logical derivation pipeline is now executable end to end on finite examples. What remains is **closure accounting**, not another missing conceptual arrow:

- state precisely which parts of the NN/non-NN derivation chain are theorem-closed;
- state which parts remain computationally hard or empirically uncalibrated;
- connect the new compiler/selection layers into the Grand GMI master theorem and README;
- avoid accidentally upgrading the older morphogenesis completeness claims (B1--B8) that remain unearned at their registered empirical scope.

The next round is that closure/boundary integration.
