# Grand GMI Master Theory V2

Status: **AUTHORITATIVE FORMAL SYNTHESIS — CAUSAL-PROCESS ONTOLOGY CLOSED; EXACT/EMPIRICAL SOLVABILITY REMAINS SCOPE-DEPENDENT**  
Date: 2026-09-12  
Supersedes `GRAND_GMI_MASTER_THEORY_V1.md` as the current synthesis; historical theorem files and negative results remain authoritative for their local scopes.

## 0. Primitive declaration

Grand GMI admits any machine intelligence physically represented as a causal process with a declared operational boundary. Its primitive problem is

\[
\boxed{\mathfrak G=(\mathbf P,\mathcal B,\mathcal E,\Omega,\Theta,\rho,\mathcal D,\varepsilon)}
\]

with process theory `P`, boundary/free side resources `B`, ecology `E`, obligation `Omega`, probes/interventions `Theta`, resource vector `rho`, development/search law `D`, and approximation tolerance `epsilon`.

No neuron, symbol, program, Transformer, agent count, probability prior over ecology, memory module, tool, optimizer or architecture family is primitive.

## 1. Canonical semantic object

For each history `h`, let `Q_h` be its complete protected future response profile under every declared ecology coordinate, intervention, continuation and obligation probe. Exact semantic equivalence is

\[
h\equiv_0h'\iff Q_h=Q_{h'}.
\]

The exact semantic state is the quotient

\[
\boxed{S^*=\mathcal H/\!\equiv_0}.
\]

Approximation is not formed by the generally nontransitive rule `d<=epsilon`. A declared response pseudometric `d_Q` supplies covering/packing or explicitly transitive coarse-graining objects instead.

Enlarging obligation, ecology, intervention family or horizon can only refine exact semantic state.

## 2. Two irreducible task spectra

For every causal cut `C`,

\[
\boxed{\kappa(C,\varepsilon)=\inf\{\text{cut resource required for the obligation within }\varepsilon\}}.
\]

At finite zero-error one-way scope this is exactly the chromatic requirement of the semantic-conflict hypergraph. Memory, prompting, retrieval, communication, context, verifier information and external stores are cut specializations.

For each local process region `v`,

\[
\boxed{\tau(v,\varepsilon)=\inf\{\rho_{comp}(T):T\text{ realizes the required local semantic transformation}\}}.
\]

`kappa` and `tau` cannot be collapsed to one information scalar: tasks with the same final semantic width can have arbitrarily different exact transformation/query complexity.

## 3. Physical realization and resources

The process theory determines which transformations/carriers are physically legal. Semantic requirements become physical lower bounds only through valid substrate laws/resource monotones.

If a zero-error semantic cut requires `m` messages, the physical cut must provide process-relative zero-error capacity at least `m` under the declared free side resources. Bare binary/classical and finite-dimensional quantum carriers are specializations; pre-shared entanglement or other free resources can change the physical capacity.

Semantic compression does not itself imply thermodynamic erasure. Response-equivalent implementations can route cost differently among energy, memory, time, communication, retained garbage and reset operations. Landauer-type costs apply only to the declared physical reset under the appropriate thermodynamic hypotheses.

## 4. Development is recursive GMI

Morphology, parameters, memories, update rules, populations or self-descriptions may themselves be the state of a lifted GMI process. Consequently learning, meta-learning, architecture search, program synthesis, test-time adaptation, self-modification and evolution need no new foundational primitive.

A development law is architecture-neutral only when it descends to the declared operational quotient; syntax-sensitive search otherwise reintroduces a search prior.

## 5. Symmetry, composition and distributed systems

Declared symmetries act on the semantic quotient. Under invariant objectives/resources and the stated convexity conditions, randomized orbit averaging produces an equivariant representative with identical capability and no worse convex invariant resource; a unique deterministic optimum must be equivariant. Nonconvex resource meters can invalidate the no-worse conclusion.

A distributed/multi-agent machine is one composed causal process with internal semantic cuts. Centralization can preserve external response semantics without preserving communication, privacy, latency or energy. Under genuine product factorization of ecology, obligation, feasible process class and separately retained coordinates, attainable sets/frontiers tensorize; coupled obligations need not.

## 6. Causal meaning and autonomous viability

A physical distinction is semantic only if interventions on it can alter a protected obligation response or resource/developmental disposition at the declared boundary. Obligation-null physical detail is quotiented away.

A declared constitution/viability predicate induces an endogenous obligation for self-maintaining systems, after which the same semantic/cut/resource/development machinery applies. Bare physical dynamics do not select arbitrary values: identical dynamics can support opposite constitutions and opposite optimal actions.

## 7. Substrate law: classical, continuous and quantum

A protected-response-preserving implementation map preserves response-defined GMI semantics while resource coordinates can change. Thus semantics are realization-invariant under the declared operational implementation, while morphology selection remains substrate dependent.

Finite classical stochastic GMI embeds in the commuting/diagonal sector of finite-dimensional quantum process GMI. Finite-dimensional quantum states, channels, instruments and effects use the same response quotient; tomography, no-cloning, dense coding and other quantum-information results enter as substrate constraints/capacities rather than new intelligence definitions.

For standard-Borel stochastic process models, the same response semantics remain well typed under the required measurability assumptions. Infinite exact quotients can exist without an automatically convenient measurable representation. Compact finite-dimensional profile images guarantee Pareto existence; noncompact sets can have an unattained infimum and empty frontier. `kappa` and `tau` are infima until attainment is proved.

## 8. Morphology and family selection

For physical regime `theta`, define the attainable profile set and physical frontier

\[
\mathcal A_{\mathfrak G,\theta}=\{(Q(M),\rho(M)):M\in Phys_{\mathbf P}(\theta)\},
\qquad
\boxed{\mathcal F_{\mathfrak G,\theta}=Pareto(\mathcal A_{\mathfrak G,\theta})}.
\]

Development gives a separate reachable frontier over `Phys intersect Reach_D(B)`.

A morphology property `P` is **derived** only if every relevant selected/reachable Pareto morphology has `P`, or a separately declared selection rule uniquely selects one operational class having `P`. Candidate omission is not derivation.

The same rule applies to implementation families. Neural, program/symbolic, table, analog, biological, quantum or hybrid identity is selected only after response adequacy, physical feasibility, resources and reachability are included. Exact finite witnesses now demonstrate neural selection, non-neural selection, hybrid selection and substrate-driven family inversion with unchanged protected semantics.

## 9. Realization compiler boundary

Finite deterministic Boolean/finite-transducer behaviors admit multiple exact realization families, including neural and non-neural constructions. Therefore representability alone cannot establish architecture necessity. Realization compilation proves existence; morphology/family selection proves preference/necessity.

This separation is normative:

\[
\boxed{\text{semantic derivation}\ne\text{realization existence}\ne\text{family selection}.}
\]

## 10. Necessity–construction closure

Let `X_con(theta)` be explicitly constructible profiles, `X_phys(theta)` the true physical set, and `X_nec(theta)` the outer set surviving all proved necessities:

\[
X_{con}\subseteq X_{phys}\subseteq X_{nec}.
\]

If the constructive frontier meets/dominates the necessary outer frontier, the performance/resource frontier is closed. Unique morphology additionally requires that each physical frontier fiber lie in one declared morphology-equivalence class.

This is the universal GMI closure pattern; merely defining a feasible set is not a derivation.

## 11. Phenomenology reduction closure

The frozen phenomenology atlas reduces sensing, representation and feature learning, memory/recurrence, attention, retrieval, prompting/in-context learning, planning/search/verifiers, test-time compute, scratchpads/tools, world models, robustness/OOD, overparameterization, ensembles/MoE/sparsity, equivariant architectures, neural/symbolic systems, theorem proving, continual/meta-learning, architecture search, self-modification/evolution, multi-agent communication, embodiment/homeostasis, exploration/hierarchy/scaling/emergence and quantum advantage to the master objects above.

A mechanism with no effect on any protected master primitive/derived object has no distinguishable intelligence effect at that resolution.

Reduction coverage is not architecture derivation; family selection remains the final quantifier.

## 12. Exact solved sector and global limits

For finite decidable registered problems, the attainable set, Pareto frontier, all operational fibers, bounded developmental reachability and the full finite selection chain are exactly computable by enumeration or stronger parent algorithms where available.

No total exact solver can cover every unrestricted Turing-complete unbounded instance: halting reduces to exact capability/reachability/frontier queries. This is a theorem boundary, not unfinished architecture work.

Global definability therefore does not imply universal algorithmic solvability.

## 13. Grand GMI V2 master law

\[
\boxed{
(\mathbf P,\mathcal B,\mathcal E,\Omega,\Theta,\rho,\mathcal D)
\Rightarrow
(S^*,d_Q)
\Rightarrow
(\kappa,\tau,G,I_\Omega)
\Rightarrow
(X_{nec},X_{con},Reach_{\mathcal D})
\Rightarrow
(\mathcal A,\mathcal F,\mathcal F^{reach},\Phi)
\Rightarrow
\text{derived operational properties / realization families}.
}
\]

In words:

> Physical law supplies possible processes. Ecology and obligation determine which distinctions and transformations matter. Causal placement determines which semantic information must cross each cut and which transformations must occur locally. Substrate laws assign physical costs and impossibilities. Development determines what can be reached. The resulting resource-conditioned reachable frontier determines which operational properties and realization families are actually derived.

## 14. Formal completion criterion

Grand GMI V2 calls the **formal theory architecture complete under the causal-process domain axiom** when all of the following hold:

1. every admitted machine is a typed causal physical process at a declared boundary;
2. exact semantic identity is canonical by protected-response equality;
3. approximate resolution is separately metrized/coarse-grained;
4. information/communication/memory are typed by semantic cuts;
5. local computation is independently typed by transformation complexity;
6. substrate physics transports necessities into physical resources/impossibilities;
7. learning/evolution/search/self-modification are recursive development processes;
8. symmetry and composition/multi-agent structure require no new ontology;
9. causal meaning and viability are obligation-relative, while arbitrary values are not derived from bare physics;
10. classical, measurable/continuous and finite-dimensional quantum process models instantiate the same semantics;
11. morphology/family claims obey reachable-frontier selection rather than candidate naming;
12. known registered phenomena reduce without an architecture-specific primitive;
13. finite registered problems admit end-to-end exact derivation traces;
14. undecidability and nonattainment boundaries are stated rather than hidden.

The current theorem stack satisfies this criterion. Accordingly:

`GRAND_GMI_V2_FORMAL_THEORY_ARCHITECTURE_CLOSED = TRUE`.

This is **not** the claim that every empirical constant, modern-scale capability curve or future phenomenon is already known. A scientific theory remains open to sharper laws, measurement and falsification after its ontology/law architecture is closed.

## 15. Falsifiers and extension rule

Grand GMI V2 must be extended or rejected if any reproducible causal machine-intelligence phenomenon satisfies one of these:

- two systems agree on the full declared master tuple, complete protected responses, resource/developmental profiles and selection objects, yet differ on a protected capability;
- a theorem's stated hypotheses hold and its derived bound/selection is violated;
- a prospectively frozen operational phase prediction fails outside its declared uncertainty/regularity boundary;
- a new physical process theory cannot be represented through systems, transformations, composition, interventions/effects and resource constraints while still exhibiting operational machine intelligence.

New architecture names alone are not extensions. New experimentally necessary operational primitives are.

## 16. Scientific programme after formal completion

The recursive foundational search now terminates at V2 unless a falsifier exposes a missing primitive. The next work is application and attempted refutation:

- derive sharper `kappa/tau` laws for language, planning, causal discovery, continual learning and theorem proving;
- replace synthetic family-selection profiles with independently measured modern hardware/process costs;
- derive resource-conditioned phase boundaries before training/search;
- freeze and test genuinely empty operational regions prospectively;
- seek independent replication, large-scale failures and physical/quantum regimes capable of breaking the current master law.

A successful falsifier reopens ontology. Otherwise further progress is law refinement and empirical science, not endless invention of foundational categories.