# Parent-equivalence and subsumption boundaries for GMI #833 — v1

**Issue:** #846, child of #833 Section C  
**Freeze authority:** `research/gmi-833-parent-equivalence-v1/FREEZE_V1.md`  
**Claim ceiling:** `GMI_PARENT_EQUIVALENCE_BOUNDARIES_AT_REGISTERED_FINITE_SCOPE`

This note does not introduce a new universal state-equivalence theory. It identifies exact special cases of the behavioral/predictive equivalence objects in the #833 foundation, subtracts the classical parent mathematics, and records counterexamples that prevent stronger identification.

## 1. Objects and notation

Let `Sigma` be a finite action/input alphabet. For a deterministic total Moore-style system

`M = (Q, Sigma, delta, lambda)`

with `delta : Q x Sigma -> Q` and registered observation/output `lambda : Q -> O`, write `delta*(q,w)` for the state reached after a finite word `w in Sigma*`.

Define **exact future-response equivalence**

`q ≡_B q'  iff  forall w in Sigma*: lambda(delta*(q,w)) = lambda(delta*(q',w)).`

For a finite history set `H` and a registered family `Tau` of future tests, let `P_h(t)` be the exact predictive probability of test `t` after history `h`. Define

`h ≡_P h'  iff  forall t in Tau: P_h(t) = P_h'(t).`

The finite executable witness instantiates `Tau` as a complete registered test table. The analytic PS-1 statement below applies to any explicitly declared `Tau`; it does not infer that a finite test list is complete for an arbitrary stochastic process.

---

## 2. MN-1 — Myhill–Nerode is an exact deterministic language specialization

Assume `O={0,1}` and `lambda(q)=1` exactly when `q` is accepting. Let `q0` be the start state and

`L = { w in Sigma* : lambda(delta*(q0,w)) = 1 }`.

For each state `q`, define its right language

`L_q = { z in Sigma* : lambda(delta*(q,z)) = 1 }`.

### Theorem MN-1

For any states `p,q`,

`p ≡_B q  iff  L_p = L_q`.

For any two access histories `u,v`,

`u ≡_L v` in the Myhill–Nerode relation of `L`

iff

`delta*(q0,u) ≡_B delta*(q0,v)`.

If every state is reachable, the quotient `Q / ≡_B` has exactly the number of Myhill–Nerode classes and therefore equals the minimum reachable DFA state count.

### Proof

The first equivalence is immediate from the definitions: the binary response after suffix `z` is acceptance of `delta*(p,z)`, so equality for every suffix is exactly equality of right languages.

For access histories, by definition of Myhill–Nerode,

`u ≡_L v`

iff for every suffix `z`, `uz in L` iff `vz in L`.

Using determinism and associativity of `delta*`, this is equivalent to

`lambda(delta*(delta*(q0,u),z)) = lambda(delta*(delta*(q0,v),z))`

for every `z`, which is exactly future-response equivalence of the reached states.

Right congruence follows because if `p ≡_B q`, then for each symbol `a` and suffix `z`, equality of the response after `az` gives

`delta(p,a) ≡_B delta(q,a)`.

The minimality conclusion is the standard Myhill–Nerode theorem applied to the reachable language recognizer. `□`

### Executable witness

The frozen 4-state DFA has all four states reachable and quotient

`[{0}, {1,2}, {3}]`.

Thus the supplied DFA is intentionally non-minimal while its exact response quotient has three states.

### Boundary

This is an **exact specialization**, not a reduction of arbitrary GMI behavioral specifications to regular-language recognition. The result needs deterministic total finite-state language semantics and binary acceptance as the protected response.

---

## 3. BI-1 — deterministic future-response equivalence equals output-respecting bisimulation

Call a relation `R subseteq Q x Q` an output-respecting deterministic bisimulation when, for every `(p,q) in R`,

1. `lambda(p)=lambda(q)`, and
2. for every `a in Sigma`, `(delta(p,a), delta(q,a)) in R`.

Because the system is deterministic, the usual forth/back clauses collapse to successor preservation for the unique `a`-successors.

### Theorem BI-1

On a deterministic total system, `≡_B` is the greatest output-respecting bisimulation.

### Proof

**(i) `≡_B` is a bisimulation.** Empty word `epsilon` gives `lambda(p)=lambda(q)`. For any action `a`, if `p ≡_B q`, then for every suffix `z` the responses after `az` agree. Hence the unique successors `delta(p,a)` and `delta(q,a)` have equal responses for every `z`, so they are again `≡_B`-equivalent.

**(ii) Every output-respecting bisimulation is contained in `≡_B`.** Let `(p,q) in R`. Induct on `|w|`. At length zero, output equality is a bisimulation clause. For `w=az`, successor preservation gives `(delta(p,a),delta(q,a)) in R`; the induction hypothesis gives equal responses after `z`. Therefore responses agree after every finite `w`, so `p ≡_B q`. `□`

### Exhaustive finite certificate

The executable layer independently computes:

- future-response partitions by Moore-style signature refinement; and
- greatest output-respecting bisimulation by deleting violating pairs from a candidate relation.

It exhausts every 3-state, 2-action, binary-output deterministic total system:

`2^3 * 3^(3*2) = 5,832` machines.

The committed result records zero partition disagreements.

### Nondeterministic hostile

Trace equivalence and strong bisimulation separate as soon as branching structure matters. Consider:

- `p -a-> p_b` and `p -a-> p_c`;
- `p_b -b-> t`;
- `p_c -c-> t`;
- `q -a-> q_bc`;
- `q_bc -b-> t` and `q_bc -c-> t`.

Both starts have the finite trace set

`{epsilon, a, ab, ac}`,

but no strong bisimulation can relate `p` and `q`: matching the `a`-transition from `p` to `p_b` forces `p_b` to relate to `q_bc`, yet `q_bc` has a `c`-transition that `p_b` cannot match. Therefore the deterministic equality must not be exported to nondeterministic trace semantics.

### State-abstraction interpretation

At the deterministic exact-output scope, quotienting by `≡_B` is an exact state abstraction: the output is well-defined on each class and every action induces a well-defined successor class. Broader MDP abstraction/homomorphism/bisimulation notions add stochastic kernels, rewards, policies, approximation metrics, or task-specific value preservation; those additions are parent theory rather than consequences of BI-1.

---

## 4. PS-1 — predictive equivalence is the minimal exact predictive-sufficient quotient

Let `H` be finite and let the declared test family be `Tau`. Each history has a complete predictive-law vector

`P_h = (P_h(t))_{t in Tau}`.

A statistic `S : H -> Z` is **exact predictive-sufficient for Tau** when

`S(h)=S(h')  =>  P_h=P_h'`.

This definition is deliberately target-relative: it is sufficiency for the registered future-test law, not automatically Fisher/Neyman parameter sufficiency.

### Theorem PS-1

The quotient map

`Q_P(h) = [h]_{≡_P}`

is exact predictive-sufficient. Moreover, every exact predictive-sufficient statistic `S` refines the predictive quotient: each fiber `S^{-1}(z)` is contained in one `≡_P` class. Consequently

`|im S| >= |H / ≡_P|`.

If equality holds, `S` differs from `Q_P` only by a relabeling of quotient classes.

### Proof

If two histories have the same quotient class, their full predictive-law vectors are equal by definition, so `Q_P` is sufficient.

If `S` is sufficient and `S(h)=S(h')`, sufficiency requires `P_h=P_h'`; hence `h ≡_P h'`. Thus no fiber of `S` can cross a predictive-equivalence boundary, so the partition induced by `S` refines the quotient partition. A refinement of a finite partition cannot have fewer blocks, proving the cardinality lower bound. If the block counts are equal, refinement without splitting is possible only when the partitions are identical up to block names. `□`

### Exact witness

The registered table contains three histories:

- `hA : (1/2, 1/2)`;
- `hB : (1/2, 1/4)`;
- `hC : (1/2, 1/2)`.

The quotient is `[{hA,hC},{hB}]`. The executable hostile checks all `3^3=27` assignments of histories to statistic labels and confirms that every sufficient statistic uses at least two values and that the only minimum partition is the predictive quotient up to relabeling.

### Scope boundary

The theorem is elementary quotient/minimal-sufficient-state mathematics once the exact full predictive law over `Tau` is given. It does **not** establish how to identify the law from finite data, how many tests suffice for an arbitrary process, or whether a finite-dimensional predictive state exists.

---

## 5. PSR-1 — when predictive-state coordinates represent the quotient

For a chosen test subset `C subseteq Tau`, define the coordinate map

`phi_C(h) = (P_h(t))_{t in C}`.

Because predictively equivalent histories agree on every test, `phi_C` is constant on each predictive quotient class and therefore induces a map on `H/≡_P`.

### Theorem PSR-1

The induced coordinate map is injective on the predictive quotient iff `C` separates every pair of distinct predictive classes:

for every `h not≡_P h'`, there exists `t in C` with `P_h(t) != P_h'(t)`.

### Proof

This is exactly the definition of injectivity of the quotient-class coordinate vectors. `□`

### Incomplete-test hostile

Histories `hA` and `hB` agree on the first registered test with probability `1/2`, but differ on the second (`1/2` versus `1/4`). A coordinate representation containing only the first test maps the two distinct predictive classes to the same vector and is therefore not an injective representation of the predictive quotient. The full two-test coordinate separates them.

### Parent subtraction

Predictive state representations (PSRs) already represent dynamical state using predictions of tests. The GMI residual here is **not** the idea of predictive state. The only registered contribution is an explicit crosswalk from #833's behavioral/predictive quotient language to the parent object plus a fail-closed condition for when a chosen test-coordinate set is sufficient to represent that quotient. Learning a core test set, linear dimension/rank results, update operators, and scalable PSR estimation remain parent/open work.

---

## 6. SUF-1 — classical parameter sufficiency and predictive sufficiency are incomparable in general

Classical finite parameter sufficiency asks whether the conditional law of observed data `X` given a statistic `T(X)` is independent of parameter `theta` (equivalently, under standard conditions, the Fisher–Neyman factorization criterion). Predictive sufficiency above asks whether histories merged by the statistic have the same registered future law. The targets differ, so neither implication holds without additional assumptions.

### Counterexample A — predictive sufficient, not parameter sufficient

Let `theta in {0,1}` and observe `Y=theta` deterministically. Let future `Z` be a fair bit independent of `theta`.

The constant statistic `S(Y)=0` is predictive-sufficient for `Z` because `P(Z|Y=0)=P(Z|Y=1)=(1/2,1/2)`. But it is not sufficient for `theta`: conditioning on the constant statistic leaves the data law `Y=theta`, which depends completely on `theta`.

### Counterexample B — parameter sufficient, not predictive sufficient

Let `theta in {0,1}`. Observe `H=(Y,S)` where `Y=theta` deterministically and `S` is an independent fair bit. The statistic `T(H)=Y` is sufficient for `theta`; conditional on `Y`, the remaining component `S` is fair and parameter-independent.

Let future `Z=S` deterministically. Then histories `(Y,0)` and `(Y,1)` have the same statistic but different future laws, so `T` is not predictive-sufficient.

Therefore classical parameter sufficiency and the registered predictive sufficiency are **incomparable in general**.

---

## 7. Strongest-parent/subsumption table

| Parent theory | Relation to registered #833 object | Exact assumptions for match | Boundary / nearest false promotion |
|---|---|---|---|
| Myhill–Nerode / DFA minimization | `EXACT_SPECIALIZATION` | finite reachable deterministic total language recognizer; binary acceptance response | arbitrary behavioral specifications need not be regular-language recognition |
| Output-respecting strong bisimulation | `EXACT_SPECIALIZATION` | deterministic total transition system; registered output labels protected | nondeterministic trace equivalence can be strictly coarser than strong bisimulation |
| State abstraction / homomorphism | `STRICT_BOUNDARY` | exact deterministic quotient gives one exact abstraction | stochastic/reward/policy/approximate abstractions need extra structure and parent theorems |
| Classical minimal sufficient statistic | `INCOMPARABLE` in general | can coincide only when the inferential target/parameter is chosen so equality of conditional future laws is exactly the sufficiency target | SUF-1 gives both failed implications |
| Predictive state representation | `COORDINATE_REALIZATION` | chosen tests form a separating/sufficient coordinate set for predictive classes | incomplete tests merge distinct predictive classes; learning/minimal-rank claims require extra PSR theory |

The appropriate manuscript language is therefore not “GMI generalizes all of these.” The defensible statement is that the #833 foundation contains an implementation-neutral equivalence interface whose deterministic-language, deterministic-bisimulation, and exact predictive-state restrictions recover familiar parent objects, while classical parameter sufficiency is generally a different relation.

---

## 8. Literature anchors / parent ownership

The following are parent anchors, not novelty claims:

1. **Myhill–Nerode / automata minimization.** The standard theorem characterizes regular languages via finite-index right congruences and yields the unique minimal reachable DFA up to isomorphism. The executable tranche uses this only as a specialization theorem.
2. **Bisimulation / state abstraction.** Strong bisimulation preserves branching behavior; deterministic output-respecting bisimulation collapses to the coinductive form of future-response equality proved above. Modern state-abstraction/homomorphism work extends this to MDP and approximate settings.
3. **Statistical sufficiency.** Fisher–Neyman sufficiency concerns information about a statistical parameter in observed data. Minimal sufficient statistics are essentially unique under standard conditions. SUF-1 prevents reusing that term as a synonym for arbitrary future-prediction sufficiency.
4. **Predictive state representations.** PSRs represent controlled-system state by predictions of tests; selecting a sufficient/core set of tests is load-bearing. The registered PSR-1 result is only the separating-coordinate condition for the exact predictive quotient.

Representative bibliography:

- A. Nerode, *Linear Automaton Transformations*, Proceedings of the AMS 9(4), 1958.
- R. Milner, *Communication and Concurrency*, Prentice Hall, 1989.
- T. Dean and R. Givan, and subsequent state-aggregation/state-abstraction literature; see also the unified MDP state-abstraction taxonomy of Li, Walsh & Littman (2006).
- E. L. Lehmann and G. Casella, *Theory of Point Estimation*, for sufficiency/minimal sufficiency.
- M. L. Littman, R. S. Sutton & S. Singh, predictive representations of state; S. Singh et al., *Learning Predictive State Representations*, ICML 2003.

## 9. Forbidden extrapolations

This tranche does not license:

- `ALL_GMI_EQUIVALENCE_IS_MYHILL_NERODE`;
- `TRACE_EQUIVALENCE_EQUALS_BISIMULATION_UNIVERSALLY`;
- `CLASSICAL_SUFFICIENCY_EQUALS_PREDICTIVE_SUFFICIENCY`;
- `ALL_PSRS_ARE_MINIMAL`;
- `UNIVERSAL_STOCHASTIC_MINIMALITY`;
- `COMPLETE_GMI`.

The parent #833 remains open after these four parent-subsumption rows are reconciled.
