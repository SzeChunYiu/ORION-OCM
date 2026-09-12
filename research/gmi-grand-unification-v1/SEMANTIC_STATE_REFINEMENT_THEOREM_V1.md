# Grand GMI Semantic-State Refinement Theorem V1

Status: **EXACT SET-THEORETIC THEOREM; FINITE EXHAUSTIVE CHECK GREEN**  
Date: 2026-09-12  
Parent main: `aae4d77e49542a135d14bdaf762ec74671abe8e4`

## 0. Purpose

A grand theory needs a principled notion of abstraction and scale. GMI already defines predictive/obligation-relative state by quotienting histories that no admissible future test can distinguish. This note proves that enlarging what the system must care about can only refine that state space.

The result gives a canonical hierarchy of semantic state spaces rather than an engineer-chosen hierarchy of hidden vectors.

## 1. Semantic response quotient

Let `H` be a history set. For an ecology family `E`, obligation/test family `Omega`, and declared future intervention class `K`, let

`Q_h(e,omega,k)`

be the obligation-relevant future response of history `h` under ecology `e`, obligation coordinate `omega`, and rooted continuation/intervention `k`.

Define

`h ~_{E,Omega,K} h'`

iff `Q_h(e,omega,k)=Q_h'(e,omega,k)` for every declared coordinate.

The semantic state space is

`S(E,Omega,K)=H / ~_{E,Omega,K}`.

This generalizes the current predictive-response quotient while making the obligation/ecology dependence explicit.

## 2. Obligation refinement theorem

**Theorem SR-1.** If `Omega_1 subseteq Omega_2` with the same `E,K`, then

`~_{E,Omega_2,K} subseteq ~_{E,Omega_1,K}`.

Hence there is a unique canonical surjection

`pi_{21}: S(E,Omega_2,K) -> S(E,Omega_1,K)`

sending each finer equivalence class to the coarse class containing it.

### Proof

If two histories agree on every response coordinate in the larger family `Omega_2`, they agree on every coordinate in the subset `Omega_1`. Therefore every `Omega_2` class lies inside exactly one `Omega_1` class. Mapping each fine class to that containing coarse class is well-defined, unique, and surjective. QED.

## 3. Ecology refinement theorem

**Theorem SR-2.** If `E_1 subseteq E_2` with the same `Omega,K`, then

`~_{E_2,Omega,K} subseteq ~_{E_1,Omega,K}`

and there is the analogous canonical surjection

`S(E_2,Omega,K) -> S(E_1,Omega,K)`.

Thus admitting more possible environments can only preserve or increase the number of semantically necessary distinctions.

## 4. Intervention refinement theorem

The same statement holds if `K_1 subseteq K_2`: adding future interventions/tests can only refine semantic state.

Therefore the full state hierarchy is monotone in every declaration axis that adds distinguishability.

## 5. Horizon hierarchy

Let `Omega_T` contain all obligation-relevant future response coordinates up to horizon `T`, with `Omega_T subseteq Omega_{T+1}`. Then

`S_{T+1} ->> S_T`

canonically.

For finite exact state spaces define

`K_sem(T)=log2 |S_T|`.

Then

`K_sem(T+1) >= K_sem(T)`.

For approximate response equivalence one may replace cardinality by an epsilon-covering number; monotonicity requires a compatible nesting of metrics/tolerances and is not claimed here without those regularity declarations.

## 6. Interpretation as abstraction

A coarser obligation/ecology/horizon identifies histories that a finer problem must keep distinct. Therefore abstraction is not fundamentally 'compressing a vector'; it is passing through the canonical quotient induced by forgetting distinctions that no longer matter.

The quotient maps give a directed semantic coarse-graining system:

`... ->> S_{T+1} ->> S_T ->> ... ->> S_1`.

A representation is adequate at scale `T` exactly when it is sufficient for `S_T`; any extra distinctions are representational detail rather than task necessity.

## 7. Morphological pressure from semantic growth

The theorem alone does not derive a hardware architecture, but it creates a task-side invariant with direct morphological consequences once physical resources are added.

- If `|S_T|` stabilizes, bounded exact semantic memory is possible at increasing horizon.
- If `|S_T|` grows, any exact finite-memory realization must eventually enlarge memory, externalize state, exploit additional structure, tolerate error, or fail the obligation.
- Different growth laws can therefore create different memory/routing pressures before any named architecture is introduced.

This is a theorem about semantic necessity, not a universal claim about the empirical scaling exponent of modern networks.

## 8. Donor boundary

Predictive-state representations and computational-mechanics causal states are direct conceptual parents for prediction-defined state; sufficient-statistic theory is a parent for task-relative compression. GMI's residual here is the explicit monotone lattice over ecology, obligation, intervention and horizon declarations, connected to the cut and transformation spectra rather than treated as an isolated state representation.

## 9. Executable check

`grand_gmi_recursive_checks_v1.py` exhausts all `2^(4*3)=4096` binary response matrices for four histories and three obligation coordinates. Across all 27 nested obligation-family pairs per matrix, it checks refinement, canonical-map well-definedness, surjectivity, and nondecreasing quotient cardinality: 110,592 exact nested-pair checks.
