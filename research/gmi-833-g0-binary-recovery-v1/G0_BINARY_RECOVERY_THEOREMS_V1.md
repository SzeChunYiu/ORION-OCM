# GMI #833 G0 binary grammar-twin P3-relative recovery v1

**Freeze:** `FREEZE_V1.md`, commit `302ad7fed43b0e310b6e22252ceb21260edd865b`.  
**Claim ceiling:** `GMI_P3_RELATIVE_BINARY_STATE_PROPERTY_RECOVERY_UNDER_NAND_NOR_GRAMMAR_TWINS_AT_REGISTERED_FINITE_SCOPE`.

## 1. Scope and prior disclosure

This tranche is intentionally tiny. It is the first architecture-prior-free **relative recovery** witness in the new #833 transformation programme; it is not the final universal grammar `G0`.

Two independent low-level Boolean grammar presentations are frozen:

- `G_NAND`: variable wires plus the binary primitive `NAND`;
- `G_NOR`: variable wires plus the binary primitive `NOR`.

Both may instantiate an explicitly disclosed generic one-bit persistent state carrier. The state cell is not a recurrent-network macro or named historical architecture; it is a generic computational state primitive. Search sees no target family name, no recurrent gate, no delay operator, no expected next-state truth table and no architecture-specific property vector.

The remaining priors are explicit rather than denied:

- **representation:** binary wires and an optional one-bit state;
- **operator:** one functionally complete Boolean gate basis per grammar;
- **search:** exhaustive finite semantic enumeration;
- **ecology:** the frozen `DELAY1` and `IDENTITY` tasks;
- **evaluation:** exact protected-output equality followed by raw Pareto resource comparison `(persistent_state_bits, primitive_tree_gate_count)`.

Thus `P3-relative` means architecture identity/property/macro is absent while generic computational, search, ecology and evaluator priors remain disclosed. It does not mean assumption-free.

## 2. G0-1A — grammar-twin Boolean closure

For variables `V`, an expression is built from variable leaves and exactly one binary primitive, either NAND or NOR. Its semantics is the Boolean truth table over all assignments to `V`.

The executable synthesizer performs dynamic programming over semantic truth tables, retaining a minimum tree-gate expression for every discovered function and re-executing every retained expression independently.

At the frozen scope it obtains:

- all 4 unary Boolean functions from `X` under NAND alone;
- all 4 unary Boolean functions under NOR alone;
- all 16 binary Boolean functions of `(S,X)` under NAND alone;
- all 16 binary Boolean functions under NOR alone.

The largest retained minimum tree cost is 5 gates for unary functions and 6 gates for binary functions in both grammars.

### Bounded primitive cross-compilation

A NAND can be implemented by four NOR gates with shared intermediate wires:

`na = NOR(a,a)`  
`nb = NOR(b,b)`  
`ab = NOR(na,nb)`  
`out = NOR(ab,ab) = NAND(a,b)`.

Dually a NOR can be implemented by four NAND gates:

`na = NAND(a,a)`  
`nb = NAND(b,b)`  
`ab = NAND(na,nb)`  
`out = NAND(ab,ab) = NOR(a,b)`.

The certificate checks all four binary input pairs. Therefore the two primitive bases are boundedly inter-compilable at this Boolean semantic scope. This does **not** imply equal description lengths, equal enumeration order, equal optimizer trajectories or broad grammar neutrality.

## 3. Registered candidate class

For each grammar, synthesis supplies the complete registered unary and binary Boolean semantic sets.

A stateless candidate is

`y_t = f(x_t)`

for one of the four unary functions.

A one-state candidate is

`s_{t+1} = u(s_t,x_t)`  
`y_t = o(s_t,x_t)`

with initial state `s_0=0` and arbitrary binary Boolean functions `u,o`. Hence there are

`4 + 16*16 = 260`

semantic candidates per grammar.

The candidate identity is its semantic truth table(s), not source text. The search therefore compares independently synthesized NAND and NOR expressions through executed semantics.

Raw resource vector is

`r=(persistent_state_bits, primitive_tree_gate_count)`.

No scalar price vector is introduced. Exact-task solutions are Pareto reduced in this two-dimensional resource order.

## 4. RECOVER-1A — delayed-copy task forces persistent state

The frozen behavioral specification `DELAY1` is:

- binary input sequence `x_0,x_1,...`;
- first protected output is `0`;
- for every `t>=1`, `y_t=x_{t-1}`.

Search is given only this external behavior.

### Stateless impossibility theorem

Assume a stateless realization `y_t=f(x_t)`. Compare two legal length-two histories:

`(0,0)` requires output `0` at `t=1`,

while

`(1,0)` requires output `1` at `t=1`.

Both histories have identical current input `x_1=0`. Therefore a function of current input alone would require simultaneously `f(0)=0` and `f(0)=1`, contradiction. Thus every exact `DELAY1` solution needs information not contained in the current input; the registered stateless class is impossible.

The executable matched negative removes persistent state while retaining the complete unary Boolean closure and finds zero exact solutions under both grammar twins.

### Constructive solution

The semantic machine

`s_{t+1}=x_t`,  
`y_t=s_t`,  
`s_0=0`

satisfies `DELAY1` for every sequence.

**Proof.** At `t=0`, `y_0=s_0=0`. After processing input `x_t`, the update sets `s_{t+1}=x_t`. Therefore for every `t>=1`, `s_t=x_{t-1}`, hence `y_t=s_t=x_{t-1}`. QED.

### Recovery uniqueness at the registered class

The search does not receive those two projection truth tables. It exhausts all 260 semantic candidates using only the sequence specification. All 16 input sequences of length four are evaluated.

Under each grammar, exactly one candidate passes:

`u(S,X)=X` with truth table `0101`,

`o(S,X)=S` with truth table `0011`.

Since any candidate satisfying `DELAY1` for every sequence must in particular satisfy all length-four sequences, and the complete registered 260-candidate universe has exactly one such candidate, the construction above is the unique universal `DELAY1` realization in this registered candidate class.

The machine certificate additionally executes the recovered candidate over every binary sequence of lengths 1 through 8: 510 sequences. That finite run is a regression certificate; the induction proof supplies the all-length result.

The recovered semantic mechanism is identical under NAND and NOR. Its Boolean next/output functions are direct wires, so its resource vector is `(1,0)`: one state bit and zero primitive gates. The post-hoc morphology description is **one-bit persistent state / recurrence**. That label is assigned only after recovery.

## 5. RECOVER-1B — exposing state does not force state selection

The matched control `IDENTITY` requires

`y_t=x_t`.

The stateless wire `f(X)=X` solves it with resource vector `(0,0)`.

Each grammar has 29 exact semantic solutions in the full 260-candidate class: the one stateless projection plus 28 stateful solutions whose output behavior is also exact. Every stateful solution has at least one persistent-state bit, so `(0,0)` strictly Pareto-dominates it regardless of primitive gate count.

Therefore both grammars recover exactly one Pareto-minimal semantic solution, the stateless input projection. Availability of a state primitive is not sufficient to make search select it.

This control is load-bearing: without it, the `DELAY1` positive could be dismissed as an evaluator that rewards state merely because state was exposed.

## 6. Exhaustive-search order boundary

Forward and reverse enumeration of the complete candidate set produce the same semantic Pareto result on both tasks and both grammars. This is expected because the registered search is exhaustive and the scientific result is computed from the complete solution set rather than first-hit order.

Nothing here proves finite-budget or heuristic-search invariance. NAND and NOR can assign different description lengths to other Boolean functions, and non-exhaustive search can therefore remain grammar-sensitive. GAUGE-1 already separates semantic remint invariance from search invariance; this tranche preserves that boundary.

## 7. What has actually been derived

At this declared finite scope the chain is:

`behavioral requirement (one-step delayed copy)`

`-> stateless observational collision / impossibility`

`-> generic state is necessary`

`-> exhaustive P3-relative search over low-level primitives`

`-> unique stateful mechanism recovered independently in NAND and NOR grammars`

`-> matched identity ecology selects no state`.

This is stronger than representability and stronger than fitting a known recurrent architecture after the fact. It is still only one very small mechanism-property recovery result.

## 8. Parent ownership

Functionally complete Boolean bases, Boolean circuit synthesis, finite-state transducers, indistinguishable-history lower bounds, and exhaustive model checking are parent mathematics/computer science. No novelty is claimed for NAND/NOR universality or one-bit delay machines.

The GMI contribution of this tranche is the **controlled derivation protocol**: architecture identity absent, two disjoint low-level grammar presentations, an analytic necessity result, neutral exhaustive recovery, a state-removed negative twin, and a state-not-needed control under explicit Pareto resources.

## 9. Falsifiers

The scoped claim becomes RED if any of the following occurs:

- either grammar fails to generate all registered Boolean semantics;
- a retained synthesized expression fails independent execution;
- the bounded primitive cross-compiler fails any input pair;
- a stateless candidate solves `DELAY1`;
- either grammar recovers more than one exact `DELAY1` semantic candidate;
- NAND and NOR recover different `DELAY1` semantic mechanisms;
- the recovered state machine fails the all-length induction equation;
- `IDENTITY` does not select the stateless projection as its unique Pareto-minimal solution;
- forward/reverse exhaustive enumeration changes the semantic Pareto result;
- normal and optimized execution produce different deterministic receipts.

## 10. Claim boundary

Earned only at this exact finite scope:

`GMI_P3_RELATIVE_BINARY_STATE_PROPERTY_RECOVERY_UNDER_NAND_NOR_GRAMMAR_TWINS_AT_REGISTERED_FINITE_SCOPE`.

Not earned:

- final architecture-neutral `G0`;
- broad grammar/search neutrality;
- all known machine-intelligence forms recovered;
- neural, symbolic or probabilistic developmental closure;
- real training or optimizer dynamics;
- held-family K5 prediction;
- unknown-form discovery;
- complete GMI.

A sensible successor is to repeat the same protocol for another orthogonal mechanism property—conditional routing, shared-vs-indexed state, or low-rank/residual compression—before attempting a multi-property known-form portfolio.
