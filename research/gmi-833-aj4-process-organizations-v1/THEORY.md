# AJ4 — process organizations and finite machine possibility space

## 1. Machine is organization, not a bottom primitive

Consume the AJ1 process frame and AJ2/AJ3 operational semantics. A finite organization is a typed wiring of admitted processes plus an external interface, any substrate-supported delayed feedback channels, and a raw lifecycle resource vector:

`M = Org(V, {p_v}, W, interface, feedback, rho)`.

No node is required to be intelligent. The organization becomes stateful only when its substrate admits a temporal persistence/delay channel. Pure static wiring does not create memory by declaration.

At the registered synchronous discrete scope, a one-step stateful organization has a combinational process

`F : S x I -> S x O`

whose `S` output is returned through one substrate-admitted delay to the next tick. This is the standard state/feedback construction; `S` is an internal organization interface, not a new ontological atom.

## 2. Special cases

### Finite circuits

An acyclic wiring of stateless admitted Boolean processes is a finite combinational circuit. The executable MUX witness derives conditional routing from NOT/AND/OR composition for all eight Boolean inputs; no MUX architecture macro is primitive.

### Finite-state machines

For finite `S,I,O`, any deterministic Mealy step map `F:SxI->SxO` plus delayed feedback of `S` is a finite-state organization. The frozen microscope includes all 256 binary one-bit-state transition/output tables and the four stateless one-state tables.

### Register-control machines

Replace the finite Boolean state carrier by a registered `(program_counter, register)` carrier and use an admitted step transformation. Feeding the updated pair back through the same temporal channel gives the ordinary small-step organization pattern. The checker includes a bounded `Z3` register-control witness with INC/DECJZ/HALT-style behaviour. AJ5, not AJ4, is responsible for deriving/classifying the current named G0 instructions from lower operations.

## 3. Feedback-derived organization phenomena

- **recurrence:** state output is routed to the next-tick state input;
- **memory-like persistence:** a step map that preserves `S` retains a distinction across ticks;
- **routing/conditional behaviour:** composed Boolean gates construct a selector without a selector primitive;
- **delay-one memory:** `s'=input, output=s` is a unique semantic organization in the frozen 260-candidate universe;
- **recurrent dynamics:** `s'=not s, output=s` produces an alternating trace.

The necessary temporal persistence resource is explicitly substrate-relative. AJ4 therefore records delay as `SUBSTRATE_CAPABILITY_REQUIRED_AT_SCOPE`; it does not claim feedback can be obtained from timeless static composition alone.

## 4. Bounded possibility space

For a frozen operational frame/substrate `O,S` and budget `B`, define

`M_B(O,S) = { Org : Org is expressible from admitted typed processes and rho(Org) <= B }`.

The executable microscope freezes binary input/output, either zero or one persistent bit, and all finite step maps at that scope. It contains exactly 4 stateless plus 256 one-bit-feedback organizations, 260 total.

Raw resources remain vectors. In the microscope the registered coordinates are state cells, truth-table rows, feedback edges and step-process evaluations; no universal scalar cost is inferred.

## 5. Operational quotient

Two organizations are quotient-equivalent only at a declared interface/context semantics. For deterministic finite transducers the checker decides all-word I/O equivalence by reachable product-state exploration. Across all 33,670 unordered pairs it finds 1,624 equivalent pairs and 148 operational classes. A separate finite-trace signature through length four yields exactly the same equivalence relation in this frozen universe, but the all-word product check is the authority for the stated result.

The four large 29-member classes illustrate why implementation count is not semantic machine count: unreachable/internal choices can differ while every external word response agrees.

## 6. Keep the lifecycle distinctions separate

A single witness makes the constitution explicit:

`process possible != organization expressible != machine realizable != reachable != selected`.

- the lower process roles include a Boolean step process and a delay only when the substrate admits it;
- 260 organizations are syntactically expressible at the frozen budget;
- a no-delay substrate realizes only the four stateless organizations, while a delay substrate realizes all 260;
- a registered one-edit developmental law from the constant-zero seed reaches only three stateless organizations;
- an external identity requirement selects exactly one of those three.

This is a separation witness, not a universal selection theory.

## Parent ownership

Feedback/state constructions in monoidal/process semantics, Mealy-machine theory, sequential/digital-circuit semantics, finite automata and register-machine small-step semantics are parent mathematics. AJ4 contributes their explicit placement in the AJ derivation stack, a finite complete organization atlas at one budget, exact semantic quotienting, lifecycle-stage separation and fail-closed substrate accounting.

## Claim ceiling

`AJ4_FINITE_PROCESS_ORGANIZATION_AND_MACHINE_SPACE_AT_REGISTERED_BINARY_SCOPE`

Forbidden: unbounded machine-space enumeration, all-machine-model reduction, feedback without a temporal substrate assumption, or collapsing expressibility/realisability/reachability/selection.
