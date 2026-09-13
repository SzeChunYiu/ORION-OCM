# Grand GMI Semantic-State Refinement Theorem V1

Status: **EXACT SET-THEORETIC THEOREM; FINITE EXHAUSTIVE CHECK GREEN**  
Date: 2026-09-12; response-preservation/adequacy correction: 2026-09-13
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

The refinement comparisons use the **same admitted history set** and a common
response map: a larger declaration must restrict to the original responses
on the old coordinates. Changing a kernel, history universe or interpretation
while adding probes is not mere coordinate refinement.

Every compared rooted response must be defined. A stochastic trajectory law
alone fixes conditional responses only almost surely. All-history claims need
declared rooted kernels/versions at null histories, or must restrict to a
registered domain where those responses are defined. An almost-sure quotient
must not be promoted into an all-intervention guarantee without that extension.

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

Thus admitting more possible environments can only preserve or increase the
number of distinctions needed to preserve the complete declared response map.

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

## 6. Full response preservation and task adequacy are different

Write `q_T:H -> S_T` for the quotient map and `r:H -> R` for a deterministic
representation. **SR-3 — response-preservation criterion.** There exists a
readout `f` with `Q_h^T=f(r(h))` on the registered histories iff

`r(h)=r(h') => Q_h^T=Q_h'^T`,

equivalently iff `q_T=g o r` for a map `g` on `r(H)`.

Proof: a readout cannot assign different response profiles to one value of
`r`. Conversely the displayed implication makes `f(r(h))=Q_h^T` independent
of the representative. The same construction gives `g(r(h))=[h]_T`. QED.

This is an exact statement about recovering **all registered responses**.
It is not an iff criterion for satisfying a set-valued obligation by choosing
one allowed behavior. Extra distinctions can also matter for physical cost,
development or later interventions even when they do not affect `Q^T`.
The canonical maps `... ->> S_(T+1) ->> S_T` remain valid response abstractions.

**Relational counterexample.** With no downstream side information, let
`Gamma(h0)={a,b}` and `Gamma(h1)={a,c}`. Probing all three actions gives success
rows `(1,1,0)` and `(1,0,1)`, so the full response quotient has two classes.
Nevertheless a constant representation with action `a` satisfies the
obligation at both histories and requires only one cut symbol.

**Three-way incompatibility witness.** Acceptable sets `{a,b}`, `{b,c}` and
`{a,c}` give three distinct full response profiles. Every pair has a common
action but the three-way intersection is empty: one symbol fails, two suffice.
Pairwise compatibility is therefore not an equivalence relation sufficient
for deciding joint adequacy. SC-1's semantic conflict hypergraph gives the
correct one-way zero-error requirement, including this higher-order conflict.

The exact deterministic-function special case is retained. With no side
information and `Gamma(h)={f(h)}`, two different required outputs are
incompatible. The minimum alphabet is `|im f|`, equal to the number of
distinct success rows. ACL-3's memory bound also remains valid because it
explicitly assumes pairwise incompatible terminal actions and no surviving
distinguishing external observation.

## 7. From response classes to realizable memory

If every future protected response must be reconstructed from an internal
state and fixed identical downstream side information, SR-3 requires at
least `|S_T|` distinct state values. This is a deterministic exact
response-preservation bound at that cut. It is not a universal memory bound
for merely satisfying `Omega`, stochastic mixtures, or unrestricted external
information. For relational task success use SC-1's conflict condition and
the actual permitted communication/control protocol.

**Growth alone is insufficient for task-memory necessity.** Consider a
binary sequence environment. At each step action `safe` always satisfies the
obligation and action `probe` succeeds exactly when the current hidden bit is
1; both advance the sequence. Full response probes over the next `T` steps
distinguish all `2^T` prefixes. The one-state controller that always chooses
`safe` still satisfies every finite-horizon obligation. Thus increasing
full response diversity need not increase the memory required for success.

Cardinality also does not by itself implement a recursively updated state.
For deterministic history extension `h -> h·a`, a stationary quotient update
`U([h],a)=[h·a]` exists iff the equivalence is a **right congruence**:

`h~h' => h·a~h'·a`

for equally legal extensions. This follows by the same representative-
independence argument as RM-3. Legal action domains must be class-consistent
or their differences included among the protected distinctions.

If the full registered tests are closed under prefixing by every admitted
action, and response semantics satisfy the corresponding concatenation law,
equality of full responses implies this congruence: test after `a` by using
the prefixed test before `a`. Without closure the implication fails. For
example current-output probes merge two zero-output states `u,v`, while an
action sends `u` back to itself and `v` to an output-one state.

At finite horizon the automatic update is from remaining-horizon classes
`S_T` to `S_(T-1)`, where tests and legality are truncated consistently;
equality of `T`-step responses need not define a stationary update on `S_T`.
For stochastic processes, equality of suitable joint future laws and the
registered conditional-update convention is required; equality of a marginal
current-response vector alone is not a lumpability theorem.

When a finite response quotient has lawful output and update maps in the
declared physical class, it supplies a bounded-state implementation of those
responses. Finite/stabilizing class counts alone do not establish those maps,
their computability, physical realization or resource cost. Infinite-horizon
claims additionally require that the finite tests determine the protected
infinite-horizon response family. These conditions preserve the valid
predictive-state interpretation without deriving task memory from a class
count that the task need not preserve.

## 8. Donor boundary

Predictive-state representations and computational-mechanics causal states are direct conceptual parents for prediction-defined state; sufficient-statistic theory is a parent for task-relative compression. GMI's residual here is the explicit monotone lattice over ecology, obligation, intervention and horizon declarations, connected to the cut and transformation spectra rather than treated as an isolated state representation.

## 9. Executable check

`grand_gmi_recursive_checks_v1.py` exhausts all `2^(4*3)=4096` binary response matrices for four histories and three obligation coordinates. Across all 27 nested obligation-family pairs per matrix, it checks refinement, canonical-map well-definedness, surjectivity, and nondecreasing quotient cardinality: 110,592 exact nested-pair checks.

That historical checker does not establish an iff between task success and
response preservation. The additive `SEMANTIC_ADEQUACY_CORRECTION_V1.md` and
`GRAND_GMI_SEMANTIC_ADEQUACY_RECEIPT_V1.json` record counterexamples, exact
relational/function checks and finite continuation/congruence checks.
