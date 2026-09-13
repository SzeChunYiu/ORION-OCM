# Grand GMI Realization Compilation Theorem V1

Status: **THEOREM / CONDITIONAL COMPILATION LAW + EXACT FINITE DUAL-REALIZATION WITNESS**  
Date: 2026-09-12

## 1. Gap closed

Grand GMI already derives obligation-relative semantic states, cut requirements, local transformation requirements, symmetry constraints, compositional structure, developmental reachability and substrate-specific physical lower bounds. Those results constrain an *operational morphology*. They do not by themselves prove that the morphology is a neural network, a program, a circuit, a finite-state controller, a biological controller or a quantum process.

This document closes the missing type boundary:

\[
\text{operational morphology}
\longrightarrow
\text{substrate realization family}
\longrightarrow
\text{protected response}.
\]

The theorem is deliberately neutral between neural and non-neural implementation families.

## 2. Operational morphology

For a registered GMI problem

\[
\mathcal G=(\mathbf P,\mathcal E,\Omega,\rho,Q),
\]

an **operational morphology** is a tuple

\[
\mathfrak M=(V,C,\{X_v\},\{K_v\},\sigma),
\]

where:

- `V` is a finite set of local transformation regions;
- `C` is a finite set of directed semantic/physical cuts connecting regions and the external boundary;
- `X_v` is the local admitted state/interface space at region `v`;
- `K_v` is the required local deterministic map or stochastic kernel;
- `sigma` is a legal execution/composition schedule in the declared process theory.

`M` is **adequate at tolerance epsilon** when its composed protected response `R_M` satisfies the registered obligation criterion at error at most `epsilon`.

Nothing in this definition names neurons, code, gates or biological tissue.

## 3. Realization family

A **realization family** `F` is a declared class of physical or computational devices together with:

1. an interface encoding `e` from operational symbols/states into realizable states;
2. a decoding/probe `d` back to the protected operational interface;
3. legal composition rules;
4. a physical resource map `rho_F`;
5. any approximation topology/metric used to compare protected kernels.

A device `N in F` is a **delta-realization** of an operational region `K_v` when

\[
d_F(d\circ N\circ e, K_v)\le \delta.
\]

An entire device network `N_M in F` realizes `M` when its encoded components and cuts compose legally and its protected response is within the registered global tolerance.

The definition permits heterogeneous families: one region may be neural, another symbolic, another analog or quantum, provided the composition is admitted by `P`.

## 4. RC-1 — exact compositional realization theorem

Assume every required local kernel `K_v` has an **exact** realization `N_v` in a realization family `F`, and every required cut in `C` has an exact interface-preserving realization in `F`. Assume the realization map preserves the legal composition schedule `sigma`.

Then the composed device `N_M` has the same protected response as the operational morphology:

\[
\boxed{R_{N_M}=R_{\mathfrak M}}.
\]

### Proof

Replace each local arrow `K_v` and each cut arrow by a response-equal realized arrow. Composition preservation permits substitution inside `sigma`. Equality is preserved under composition, so the external composite is response-equal. QED.

This is a compiler theorem in the operational sense: local exact implementations plus composition preservation imply an exact global implementation.

## 5. RC-2 — approximate compositional realization theorem

For approximate realization, let the declared process metric supply a valid composition stability bound

\[
d(R_{N_M},R_M)\le \Phi_\sigma(\{\delta_v\},\{\eta_c\}),
\]

where `delta_v` are local kernel errors and `eta_c` are cut/interface errors. `Phi_sigma` must come from the registered metric/process model; it is not assumed universally additive.

If

\[
\Phi_\sigma(\{\delta_v\},\{\eta_c\})\le \epsilon_{compile}
\]

and the operational morphology has obligation margin sufficient to absorb `epsilon_compile`, then the realized system remains adequate at the registered tolerance.

**Boundary.** Grand GMI does not assert that arbitrary local approximation errors simply sum. Stable composition is a typed hypothesis. Chaotic, adversarial, discontinuous or long-horizon processes can amplify small local errors.

## 6. RC-3 — finite exact neural/non-neural dual realization

Let `f:{0,1}^n -> {0,1}^m` be any finite deterministic local GMI transformation.

### Non-neural realization

A finite truth table with one entry for every input state realizes `f` exactly. Equivalently, a finite Boolean circuit or finite-state transducer can realize the same finite map after an appropriate encoding.

### Neural realization

Define the hard-threshold activation

\[
H(t)=\begin{cases}1&t>0\\0&t\le 0.\end{cases}
\]

For each binary pattern `p in {0,1}^n`, define its match count on input `x`:

\[
M_p(x)=\sum_{i:p_i=1}x_i+\sum_{i:p_i=0}(1-x_i).
\]

The hidden threshold unit

\[
h_p(x)=H(M_p(x)-n+1/2)
\]

is one exactly when `x=p` and zero otherwise.

For output bit `j`, define

\[
y_j=H\left(\sum_{p:f_j(p)=1} h_p(x)-1/2\right),
\]

with the constant-zero case wired to zero.

Exactly one hidden pattern detector fires, therefore `y_j=f_j(x)` for every input.

Hence every finite deterministic transformation has both:

- an exact threshold-network realization; and
- an exact non-neural table/circuit realization.

Therefore **finite GMI semantics alone cannot make neural syntax necessary**.

## 7. RC-4 — realization non-identifiability theorem

Let `N_1 in F_1` and `N_2 in F_2` have equal protected response under every registered ecology, intervention and probe:

\[
R_{N_1}=R_{N_2}.
\]

If the registered resource coordinates are also equal, then every GMI statement defined only on those protected responses/resources assigns them the same semantic status.

Consequently, no such statement can identify whether the hidden realization was neural or non-neural.

If an added intervention, probe or resource coordinate separates the two devices, they cease to be equivalent at the enlarged registered boundary. Thus implementation identifiability is **registration relative**.

## 8. RC-5 — family-density compilation schema

For an infinite or continuous operational region, suppose a realization family `F` is dense in the registered kernel class `K` under metric `d`, meaning

\[
\forall K\in\mathcal K,\ \forall\delta>0,\ \exists N\in F:\ d(N,K)<\delta.
\]

Then every finite operational morphology whose local kernels lie in `K` is approximable by members of `F` whenever the composition stability condition of RC-2 holds.

This schema is where standard universal-approximation, circuit approximation, numerical approximation, analog-control approximation or quantum-compilation results may be imported. Their hypotheses remain load-bearing. Grand GMI does not turn a parent approximation theorem into a universal fact about every neural or non-neural family.

## 9. What it means for GMI to "derive a neural network"

There are now three distinct claims:

1. **Operational derivation:** Grand GMI derives properties that every adequate morphology must satisfy: semantic distinctions, cut widths, transformation requirements, symmetry/coupling structure and resource bounds.
2. **Realizability:** RC-1/RC-2 show that a neural family can instantiate those properties when its local compiler obligations are met.
3. **Selection:** to derive that a neural family is *preferred or necessary*, one must additionally prove a family-conditioned resource/frontier statement that excludes or dominates the competing non-neural realizations.

Only (1)+(2) says "a neural network is a valid derived realization." It does **not** say "neural networks are the unique form of intelligence."

## 10. Exact XOR witness

Take the protected obligation

\[
y=x_1\oplus x_2.
\]

A non-neural realization is the four-entry truth table or one XOR logic gate.

A threshold-network realization is, for example,

\[
a=H(x_1+x_2-1/2),\qquad
b=H(x_1+x_2-3/2),
\]

\[
y=H(a-b-1/2).
\]

Both produce the same protected response on all four inputs. The semantic quotient sees the same task behavior; substrate accounting may distinguish their memory, gates, multiply-accumulate operations, latency, area, energy, trainability, robustness or developmental reachability.

The witness is intentionally small. It proves coexistence of neural and non-neural realizations, not an empirical superiority claim.

## 11. Interaction with existing Grand GMI layers

The compiler sits after the architecture-free layers:

\[
\mathcal G
\to S^*
\to \{\kappa(C)\}
\to \{\tau(R)\}
\to \text{symmetry/coupling constraints}
\to \mathfrak M
\to \text{realization family }F
\to N_M.
\]

- Semantic Cut determines what distinguishability must cross interfaces.
- Information/Computation Separation determines both communication and local transformation obligations.
- Symmetry-to-Morphology constrains operational equivariance/weight sharing without naming source syntax.
- Compositional/Distributed GMI determines when modules can factor and when internal communication is necessary.
- Recursive Morphogenesis constrains which operational/realized morphologies are reachable under admitted updates.
- Substrate Lifting and the Physical Resource Bridge determine how response equivalence and physical costs transport across realizations.
- Quantum Process GMI provides a non-classical realization family with operationally typed probes and interventions.
- Measurable/Continuous GMI supplies the regularity boundary for infinite/continuous process models and warns that infima need not be attained.

## 12. Anti-overclaiming boundary

This theorem does **not** prove:

- that a named architecture such as CNN, Transformer, GNN, RNN, MLP or MoE is uniquely optimal;
- that neural networks dominate programs, circuits, controllers or biological/quantum realizations;
- that every continuous GMI kernel has a finite neural realization;
- that a minimum-resource realization exists without an attainment theorem;
- that local approximation error remains harmless without a stability bound;
- that implementation syntax can be recovered from protected behavior alone.

It does prove the missing realization bridge and the exact finite coexistence of neural and non-neural implementations.

## 13. New remaining gap

After RC-1--RC-5, the central unresolved derivation question is no longer "can an operational intelligence be neural or non-neural?" Both are possible.

The next gap is:

> Given the GMI-derived operational constraints and a declared substrate/resource model, when does one morphology or realization family lie on the attainable Pareto frontier while another does not?

That is a **morphology selection** problem, not a semantic-definition problem.
