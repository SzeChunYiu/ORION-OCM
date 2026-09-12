# Grand GMI Non-Neural Constructive Derivation Theorem V1

Status: **THEOREM / EXACT FINITE NON-NEURAL COMPILATION + MINIMAL-STATE BOUNDARY**  
Date: 2026-09-12

## 1. Gap closed

Grand GMI already proves that neural and non-neural realizations can coexist and that resource/reachability evidence can select either family. The remaining asymmetry is explanatory: neural realization has an explicit finite threshold-network compiler and a continuous approximation bridge, while non-neural intelligence should also have a direct constructive theorem rather than being defined only as a competing family.

This layer derives exact finite-state, table, circuit and straight-line-program realizations directly from the semantic quotient and local transformation structure.

## 2. Finite semantic transducer

Let the exact protected semantic state set be finite,

\[
S^*=\{s_1,\ldots,s_k\}.
\]

Let `X` be a finite admitted input/context alphabet. Assume the next protected semantic state is well defined by a quotient-compatible deterministic transition

\[
\delta:S^*\times X\to S^*,
\]

and protected output is

\[
\lambda:S^*\times X\to Y
\]

(Mealy form), or `lambda:S*->Y` in Moore form.

Quotient compatibility means that representatives of the same semantic class never induce different next semantic classes under an admitted input. If this fails, the current quotient is too coarse for the requested dynamic obligation and must be refined.

## 3. NCD-1 — exact semantic automaton compiler

Under the conditions above, the table pair `(delta,lambda)` is an exact deterministic non-neural realization of the protected process with at most `|S*|` persistent controller states.

### Proof

Store the current semantic class label `s`. On admitted input `x`, emit `lambda(s,x)` and update the stored label to `delta(s,x)`. By induction on episode length, the implementation's stored label equals the protected semantic state after every step, so every protected output trace matches exactly. QED.

The realization may be implemented as a finite-state machine, ROM plus state register, Boolean/sequential circuit, ordinary program, relay network, mechanical controller, or any substrate capable of the same protected transition table.

## 4. NCD-2 — semantic-state lower bound

Assume every distinct pair `s!=t` in `S*` is continuation-distinguishable: there exists an admitted future input sequence under which their required protected output traces differ.

Then every exact deterministic realization must expose at least `|S*|` distinguishable persistent implementation states at the semantic cut.

### Proof

If two continuation-distinguishable semantic classes were encoded into the same protected implementation state, every future deterministic response from that implementation state under the same continuation would be identical, contradicting the required distinct protected traces. Thus the encoding from semantic classes to protected persistent implementation states must be injective. QED.

This is a finite-state version of the semantic cut lower bound and is closely related to classical automaton-minimization/Myhill-Nerode reasoning. Grand GMI's role is to obtain the equivalence relation from the registered intelligence obligation rather than from a preselected programming language.

## 5. NCD-3 — minimal semantic automaton theorem

If all `|S*|` semantic classes are reachable and pairwise continuation-distinguishable, the exact compiler of NCD-1 uses exactly the minimum possible number of deterministic persistent protected states:

\[
\boxed{k_{min}=|S^*|.}
\]

The theorem derives a non-neural state count from protected behavior without assuming neural units, hidden dimensions or source-code structure.

## 6. NCD-4 — finite stateless map compiler

For finite input set `X` and finite protected output set `Y`, every deterministic map

\[
f:X\to Y
\]

has an exact table/program realization: store one output entry per input symbol and return `f(x)`.

If `X={0,1}^n` and outputs are Boolean, standard Boolean synthesis also provides exact combinational-circuit realizations. The Realization Compilation Theorem already shows that the same finite Boolean map also has a threshold-network realization.

Therefore exact finite semantics alone cannot decide between circuit/table/program and neural syntax; resource and reachability evidence performs that selection.

## 7. NCD-5 — straight-line composition compiler

Suppose a local transformation obligation is exactly expressible as a finite directed acyclic graph of registered primitive operations

\[
O=\{o_1,\ldots,o_r\},
\]

and each primitive has a legal exact substrate implementation. Then topologically executing the operation DAG gives an exact straight-line-program/circuit realization.

The implementation resource vector is composed from the registered primitive and communication costs using the substrate's valid composition rule.

This is the constructive non-neural counterpart of composing neural layers. It does not claim the expression DAG is resource minimal; minimality remains a separate transformation-complexity problem `tau`.

## 8. NCD-6 — exactness can be a protected morphology property

If the obligation is zero-error and the selected non-neural realization computes the exact semantic transition/output relation, while every reachable neural candidate at the registered precision has a nonzero certified worst-case error or violates a hard verification/latency/resource constraint, then exact non-neurality can be selected by the existing family-selection theorem.

The exactness requirement by itself does not universally exclude neural systems: finite threshold networks can implement finite exact Boolean functions, and verified neural realizations may exist. The conclusion requires actual candidate/resource evidence.

## 9. NCD-7 — non-neural does not mean stateless or non-adaptive

A non-neural Grand-GMI realization may contain:

- persistent semantic memory;
- dynamic routing;
- hierarchical modules;
- search/planning;
- self-modifying program state;
- distributed message passing;
- evolutionary or synthesis-based development;
- active sensing/control.

Those are operational properties derived separately from cuts, transformations, architecture refinement and development. Neurality is an implementation-family property, not the definition of memory, learning or intelligence.

## 10. Exact running-parity witness

An unbounded-length bit stream arrives one symbol at a time. After each symbol the protected output must equal the parity of all bits observed so far.

The semantic state is exactly

\[
S^*=\{EVEN,ODD\}.
\]

Transition:

\[
\delta(s,x)=s\oplus x.
\]

Output is the parity state itself. The two semantic states are continuation-distinguishable even with the empty continuation because their current required outputs differ.

Therefore:

- one persistent state is impossible;
- two states are sufficient;
- the two-state XOR accumulator is a minimal exact non-neural realization.

The checker enumerates every bit string through length 8 (511 nonempty prefixes plus the empty initial state) and verifies the transducer output against direct parity.

A recurrent neural implementation may realize the same protected process, but if the registered substrate/resource profile favors the two-state FSM, Grand GMI derives non-neural intelligence by the same frontier rule used everywhere else.

## 11. Exact table/circuit witness

For the 3-bit majority function, the checker enumerates all eight inputs and verifies equality among:

1. the obligation definition `sum(bits)>=2`;
2. an eight-entry truth-table program;
3. the Boolean circuit `(a AND b) OR (a AND c) OR (b AND c)`.

This is a direct exact non-neural realization of a stateless semantic obligation.

## 12. Consequence

The neural/non-neural construction picture is now symmetric:

\[
\begin{array}{lll}
\text{finite exact semantics} &\to& \text{threshold network and table/circuit/program realizations},\\
\text{finite dynamic semantic quotient} &\to& \text{minimal exact automaton/transducer realization},\\
\text{continuous stable target} &\to& \text{neural and classical approximation families under their parent theorems}.
\end{array}
\]

Grand GMI then selects among those constructions using physical resource evidence, development reachability, generalization/ecology evidence and the registered selection rule.

## 13. Boundary

This theorem does not say finite-state machines or programs are universally superior to neural networks. It says that whenever the protected semantic dynamics are finite and quotient-compatible, Grand GMI has a direct exact non-neural compiler and, under pairwise continuation distinguishability, an exact minimal persistent-state count.

For infinite-state, continuous, stochastic, partially observed or computationally unbounded obligations, different parent realization theorems and computability/approximation boundaries apply.
