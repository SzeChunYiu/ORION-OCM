# Morphology equivalence and architecture-independent capability — v1

**Issue:** #848, child of #833 Section C  
**Freeze:** `research/gmi-833-morphcap-v1/FREEZE_V1.md`  
**Claim ceiling:** `GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE`

This tranche supplies scoped mathematical objects. It does not classify all architectures, re-prove the eleven historical capability ceilings, or claim a universal intelligence metric.

## 1. Registered scope

Fix a scientific scope

`Omega = (A,O,J,V,R,D,C)`

where `A` is the external action/input alphabet, `O` protected outputs, `J` the set of permitted intervention labels, `V` verifier/admissibility semantics, `R` the ordered lifecycle-resource coordinates, `D` the registered developmental/reachability relation type, and `C` the family of external capability contracts.

For a finite realization `M`, first restrict to its reachable protected state carrier and quotient only states already identified as equivalent by the protected-response quotient from the #833 foundation. At this reduced level define the **registered mechanism signature**

`Sig_Omega(M) = (X,x0,lambda,delta,iota,rho,Delta)`

with:

- `X`: reduced reachable state set;
- `x0`: initial marker;
- `lambda : X -> O`: protected output label;
- `delta : X x A -> X`: registered transition relation/function at this exact deterministic microscope;
- `iota : X x J -> I`: registered intervention-response labels;
- `rho in R_+^d`: raw registered lifecycle resource vector;
- `Delta subseteq X x X`: registered developmental/reachability relation.

Architecture names, source-code identifiers, tensor names, symbolic labels, and family names are absent.

The deterministic finite signature used by the executable witness is only one exact microscope. For stochastic or set-valued systems the corresponding object is a labeled relational/probabilistic structure; this tranche does not claim the deterministic encoding is universal.

## 2. MORPH-1 — morphology equivalence

For two signatures over the same external scope, define

`M approx_Omega N`

iff there exists a bijection `f : X_M -> X_N` such that:

1. `f(x0_M)=x0_N`;
2. `lambda_M(x)=lambda_N(f(x))`;
3. `f(delta_M(x,a)) = delta_N(f(x),a)` for every registered action `a`;
4. `iota_M(x,j)=iota_N(f(x),j)` for every registered intervention `j`;
5. `rho_M=rho_N` coordinatewise;
6. `(x,y) in Delta_M` iff `(f(x),f(y)) in Delta_N`.

This is isomorphism of the registered architecture-name-free mechanism structures.

### Theorem MORPH-1

`approx_Omega` is an equivalence relation.

**Proof.** Reflexivity uses the identity bijection. Symmetry uses the inverse of any structure-preserving bijection; every preservation equation reverses because `f` is bijective. Transitivity uses composition: if `f` preserves every component from `M` to `N` and `g` preserves every component from `N` to `P`, then `g∘f` is bijective and preserves initial marker, outputs, labeled transitions, intervention labels and developmental edges by substitution; resource equality is transitive. `□`

The executable certificate independently canonicalizes every finite witness over all state permutations and compares canonical structures. Two pure state renamings therefore receive exactly the same fingerprint.

### Why behavior alone is weaker

Suppose `N` copies the ordinary protected transition/output behavior of `M` but has resource vector `rho_N != rho_M`. Then all ordinary action traces can agree while condition 5 fails. Likewise, a changed intervention response violates condition 4 even if unperturbed traces agree. Thus morphology equivalence is intentionally stronger than behavioral equivalence at this scope.

This prevents the term `morphology` from degenerating into either source-code syntax or task-output equality alone.

## 3. SPECIES-1 — machine species

The legacy object called a **machine species** is defined, without extra ontology, as the quotient class

`Species_Omega(M) := [M]_(approx_Omega)`.

The preferred paper term is **computational-mechanism equivalence class**. “Species” may remain as an internal/analogy label only when its scoped equivalence relation is supplied. No biological essentialism, universal taxonomy, or claim that every possible machine belongs to one empirically identifiable natural kind follows.

## 4. CAP-1 — architecture-independent capability

A registered capability contract is

`c = (T,mu,u,V,b,tau)`

where:

- `T` is an external task/ecology space;
- `mu` is its registered measure/distribution;
- `u` is a protected utility/acceptance functional on verified traces;
- `V` is the external verifier/admissibility rule;
- `b` is a lifecycle-resource budget vector;
- `tau` is the success threshold.

For a realization `M`, let

`C_c(M) = E_(t~mu)[u(trace_M(t))]`

when the registered execution is admissible, verified as required, and its resource record lies within `b`. The exact finite witness uses rational weighted averages. If no admissible execution exists, capability is not fabricated; the contract is unsatisfied.

Define the **capability region**

`Cap_Omega(M) = { c in C : M satisfies c }`.

No architecture label occurs in this definition. A transformer, automaton, program, hybrid, or unknown mechanism is evaluated by the same external contract when the contract is applicable.

### Theorem CAP-1 — morphology invariance

If `M approx_Omega N` and `c` is measurable solely from components preserved by the registered mechanism isomorphism, then

`C_c(M)=C_c(N)`

and `M` satisfies `c` iff `N` satisfies `c`. Hence their registered capability regions are equal.

**Proof.** The isomorphism maps each reachable protected execution path of `M` to a path of `N` with the same external action labels and protected outputs. The verifier/utility therefore sees the same trace value. Resource vectors are equal by MORPH-1 condition 5. Weighted integration/summation over the same external task measure gives equal capability values and the same budget/threshold decision. `□`

The resource-twin hostile demonstrates the converse is not assumed: behavior equality without resource preservation can change the capability region under a budgeted contract.

## 5. CAP-2 — capability ceilings and impossibility regions

Let `A_Omega` be an externally described admissible realization class under an information/interface/resource contract. It is not defined by architecture names.

For a capability contract `c`, define

`C*_c(Omega) = sup { C_c(M) : M in A_Omega, M feasible for c }`.

At a finite registered scope with nonempty finite feasible set, `sup` is `max`. If the feasible set is empty, the implementation returns `NO_FEASIBLE_REALIZATION`/`None`; it does not fabricate a numerical ceiling.

Define the **impossibility region** to contain:

1. contracts with nonempty feasible set but `tau > C*_c(Omega)`; and
2. contracts for which no realization satisfies the external admissibility/resource requirements.

This is a property of the declared problem/information/resource class, not of a favored architecture.

### Theorem CAP-2A — admissible-class monotonicity

If `A subseteq B`, then `C*_c(A) <= C*_c(B)` whenever the left feasible set is nonempty.

**Proof.** Every feasible candidate in `A` is also available in `B`; a supremum over a superset cannot be smaller. `□`

### Theorem CAP-2B — resource monotonicity

If budget vectors satisfy `b <= b'` coordinatewise and no other contract field changes, then the feasible realization set under `b` is a subset of that under `b'`; therefore the ceiling cannot decrease.

### Threshold monotonicity

The ceiling itself is independent of the requested threshold. Once `tau > C*`, any stricter threshold `tau' >= tau` remains impossible. A higher threshold cannot turn an impossible contract possible without changing information, resources, admissible systems, utility, or ecology.

The finite witness has ceilings `1/4 -> 3/4 -> 1` under nested resource budgets and `3/4 -> 1` when the admissible candidate class is enlarged.

## 6. CAP-3 — architecture-independent information ceiling

Let latent world `W` be uniform on `{0,1}`. Before acting, the agent receives the same observation in both worlds. It chooses binary action `A`. Success is `A=W`.

Any randomized policy on the single observation is fully characterized by

`p = P(A=1)`.

Then

`P(success) = P(W=0)P(A=0) + P(W=1)P(A=1)`

`= (1/2)(1-p) + (1/2)p = 1/2`.

### Theorem CAP-3

Under this frozen information contract, the capability ceiling for success probability is exactly `1/2` over **all** randomized policies, independent of internal architecture. Therefore every threshold `tau > 1/2` lies in the impossibility region.

This is analytic; the executor's enumeration of `p=k/32`, `k=0..32`, is a finite certificate/hostile rather than the proof.

### Positive information twin

Reveal `W` before action. A policy choosing `A=W` succeeds with probability `1`, and no success probability can exceed `1`; the ceiling is exactly `1`. The executable grid over `(p0,p1)` contains `p0=0,p1=1` and reproduces the bound.

This twin makes the load-bearing assumption explicit: the `1/2` ceiling comes from observational aliasing, not from computational weakness.

## 7. Parent ownership and boundaries

The mathematics here is intentionally conventional:

- finite labeled-structure isomorphism owns the equivalence-relation proof;
- quotient/equivalence-class language owns SPECIES-1;
- statistical decision theory/bounded rational evaluation owns external utility and Bayes-style information ceilings;
- supremum/feasible-set order owns the monotonicity results;
- state-abstraction/bisimulation literature owns richer stochastic and approximate mechanism equivalences.

The GMI contribution at this stage is only a disciplined common contract connecting these objects to the #833 architecture-uncommitted foundation while preserving resource/intervention/developmental distinctions.

Nearest false promotions:

- same task outputs do **not** imply same morphology;
- a finite registered mechanism quotient is not a universal ontology;
- one information-theoretic ceiling is not a re-proof of the historical 11 capability ceilings;
- a ceiling over `A_Omega` says nothing about systems excluded by the registered admissibility/information contract;
- architecture-independent evaluation does not imply architecture-independent learnability, reachability, or optimality.

## 8. Claim boundary

Allowed:

`GMI_MORPHOLOGY_AND_CAPABILITY_OBJECTS_AT_REGISTERED_FINITE_SCOPE`

Forbidden from this tranche alone:

- `UNIVERSAL_MORPHOLOGY_ONTOLOGY`
- `ALL_MACHINE_SPECIES_CLASSIFIED`
- `ALL_CAPABILITY_CEILINGS_REPROVED`
- `REAL_WORLD_CAPABILITY_CEILING`
- `UNIVERSAL_INTELLIGENCE_MEASURE`
- `COMPLETE_GMI`

Section K remains responsible for re-auditing and re-proving the eleven historical capability ceilings under the upgraded foundation.
