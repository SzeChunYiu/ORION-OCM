# GMI #833 G0 binary grammar-twin recovery v1 — freeze

Parent issue: #833. Programme comment: 5687604615.  
Base main: `5acf80fe6505a72d6878ed754783ba25aecbaa82`.

## Scientific purpose

This is the first tiny P3-relative recovery experiment in the Morphology Transformation Geometry programme. It does **not** define the final universal `G0` or close known-form recovery. It asks whether a mechanism property can be forced by an architecture-name-free behavioral ecology and independently recovered under two materially different low-level gate encodings.

## Disclosed primitive/search prior

Two grammar twins are registered before outcomes:

- `G_NAND`: Boolean input wires, optional one-bit persistent state cell, composition by the single binary primitive `NAND`, protected binary output;
- `G_NOR`: the same external/state contract but composition by the single binary primitive `NOR`.

`NAND` and `NOR` are generic functionally-complete Boolean primitives, not historical machine-intelligence architecture names. The optional state cell is explicitly disclosed as a generic computational-state primitive. No target family name, recurrent gate macro, delay operator, architecture-specific property vector, or expected solution truth table is supplied to search.

Search is exhaustive at the finite semantic scope. The evaluator executes generated Boolean expressions and sequential state updates. Candidate selection uses exact task satisfaction first and the Pareto-minimal raw resource vector `(persistent_state_bits, primitive_gate_count)` second; no post-outcome scalar weights are introduced.

## Frozen theorems / checks

### G0-1A — grammar-twin semantic closure

1. Exhaustively synthesize Boolean expression semantics from variable wires plus only `NAND` or only `NOR`.
2. Each grammar must derive all 4 unary Boolean functions of current input and all 16 binary Boolean functions of `(state,input)`.
3. Every stored minimal expression must independently re-execute to its registered truth table.
4. Prove the primitive cross-compilers: one NAND can be expressed with at most 4 NOR gates and one NOR with at most 4 NAND gates; state/input wires are transported unchanged. This establishes bounded semantic equivalence of the finite gate bases, not equal description lengths/search bias.

### RECOVER-1A — delayed-copy state recovery

Register ecology `DELAY1`: initial latent state is zero; for every binary input sequence, output at time `t` must equal the previous input bit (zero at the first step).

1. Exhaustively evaluate every stateless unary candidate and every one-state candidate whose next-state/output Boolean functions are synthesized by the grammar.
2. Under both `G_NAND` and `G_NOR`, exact recovery must yield the same unique semantic mechanism:
   - next state equals current input;
   - output equals current state.
3. The post-hoc mechanism property is one bit of persistent state / recurrence. Family naming occurs only after search.
4. Matched negative: remove persistent state while retaining the full unary combinational closure. `DELAY1` must be impossible. Analytic hostile: histories with the same current input but different previous input require different outputs, so any stateless current-input function collides.

### RECOVER-1B — state-not-always-selected control

Register ecology `IDENTITY`: output equals current input.

1. Both grammars must recover the stateless projection `output=input` as the unique Pareto-minimal semantic solution `(0 state bits, 0 gates)`.
2. Stateful exact solutions may exist but are strictly resource-dominated; state is therefore not selected merely because the grammar exposes it.

### Search/remint boundaries

- exhaustive finite semantic search must make forward/reverse enumeration agree on the recovered semantic Pareto optimum;
- NAND and NOR may have different expression lengths for other functions; no general search-prior invariance is claimed;
- recovery is at a tiny binary finite scope only.

Expected claim ceiling if GREEN:

`GMI_P3_RELATIVE_BINARY_STATE_PROPERTY_RECOVERY_UNDER_NAND_NOR_GRAMMAR_TWINS_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions: final universal G0, all known forms recovered, neural/symbolic/probabilistic closure, real learning dynamics, broad grammar neutrality, unknown-form discovery, or complete GMI.
