# GMI #833 Section-E `G0-reg-v1` freeze

**Parent:** #833 Section E  
**Child:** #868  
**Source main:** `7b68b0681a44157aab4864a66266ba598cce0fbc`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the exact syntax, operational semantics, requirement-relative minimality target, compilation theorems, finite exhaustive family, resource vector, hostile cases and claim ceiling **before** any executor, tests, result receipt, reconciliation specification or dedicated workflow exists on this branch.

## 1. Scientific boundary

`G0-reg-v1` is an architecture-uncommitted operational core **relative to a disclosed register/control representation prior**. It is not literally prior-free. Its five instruction classes are chosen because they expose external input, protected output, writable storage, data-dependent control and explicit termination in a small exact operational language.

Parent mathematics is not novelty here:

- counter/register-machine computability: Minsky; Shepherdson–Sturgis and successors;
- finite sequential/transducer machines: Mealy/Moore tradition;
- small-step/structural operational semantics: Plotkin tradition;
- grammar-constrained program synthesis: SyGuS and related synthesis work;
- low-level operation search: AutoML-Zero and related search-space work.

The repository residual is the exact #833 typed contract, disclosed-prior ledger, bounded compilation certificates, relative instruction-class necessity witnesses, raw resource accounting, hostile controls and freeze/receipt discipline.

## 2. Frozen syntax

A program is a finite nonempty labelled map `P : Label -> Instr`, with a declared finite nonempty register set `R` and a start label. Register values are natural numbers. All registers start at zero.

Exactly five instruction classes are admitted:

```text
READ(r,next)
INC(r,next)
DECJZ(r,nz,z)
EMIT(r,next)
HALT
```

Semantics:

- `READ(r,next)`: consume the next external input natural number into `r`; underflow fails closed.
- `INC(r,next)`: replace `r` by `r+1`.
- `DECJZ(r,nz,z)`: if `r>0`, replace it by `r-1` and continue at `nz`; otherwise leave it zero and continue at `z`.
- `EMIT(r,next)`: append the current natural value of `r` to the protected output trace.
- `HALT`: terminate successfully.

All non-HALT successor labels must exist and all referenced registers must be declared. Missing labels/registers or unknown instruction constructors are malformed and fail closed before execution.

## 3. Configurations and terminals

A configuration is

```text
(pc, registers, unread_input, protected_output, resources).
```

The executor is deterministic on every well-formed configuration.

Registered terminals are machine-distinct:

```text
HALTED
MALFORMED_PROGRAM
INPUT_UNDERFLOW
STEP_BUDGET_EXHAUSTED
```

A missing label/register is reported under `MALFORMED_PROGRAM` with a specific reason. Falling off the program is never successful termination.

## 4. Raw resource vector

Every execution reports the raw vector

```text
(program_instructions,
 steps,
 register_reads,
 register_writes,
 input_reads,
 output_writes)
```

where `program_instructions = |dom(P)|` is static and the remaining coordinates are exact dynamic counts. No scalarization is part of this tranche.

Per-instruction dynamic accounting is frozen as:

- `READ`: `steps+1`, `register_writes+1`, `input_reads+1`;
- `INC`: `steps+1`, `register_reads+1`, `register_writes+1`;
- `DECJZ`: `steps+1`, `register_reads+1`; additionally `register_writes+1` iff the positive branch decrements;
- `EMIT`: `steps+1`, `register_reads+1`, `output_writes+1`;
- `HALT`: `steps+1` only.

## 5. RELMIN-1 — five-class relative minimality target

The word `minimal` is frozen to mean **instruction-class irredundancy relative to this registered requirement suite**, not unique/global instruction-set minimality.

Requirements:

- `REQ-IN`: protected behavior can depend on an external input value.
- `REQ-OUT`: a successful execution can produce a nonempty protected output trace.
- `REQ-GEN`: from all-zero registers and truly empty external input, a successful execution can construct and expose a positive internal value.
- `REQ-BRANCH`: two one-symbol inputs of equal length can induce different control continuations before protected output, witnessed by all-zero output traces of different lengths.
- `REQ-TERM`: successful finite termination is represented explicitly rather than by malformed/fallen-off control.

Frozen separating witnesses:

- `READ` owns `REQ-IN`.
- `EMIT` owns `REQ-OUT`.
- `INC` owns `REQ-GEN`.
- `DECJZ` owns `REQ-BRANCH`.
- `HALT` owns `REQ-TERM`.

Analytic invariants required after class removal:

1. without `READ`, execution state/output is independent of external input values;
2. without `EMIT`, every protected output trace is empty;
3. without `INC`, a successful run on empty input from zero registers can never create a positive register value;
4. without `DECJZ`, control successors are fixed by program syntax and therefore same-length valid inputs cannot change the control path/output-count schedule;
5. without `HALT`, no well-formed execution reaches the only success terminal.

Each witness must execute successfully in the full grammar and its invariant must block the requirement when the owning class is removed.

## 6. COMP-1 — finite deterministic Mealy-style transducer compiler

For any finite deterministic Mealy transducer

```text
M=(Q,{0,1},{0,1},delta,lambda,q0)
```

with exactly one output bit per consumed input bit, freeze a compiler to `G0-reg-v1` using two scratch registers `rin` and `rout` plus labelled control.

The compiled protected interface receives the source input word with a private EOF code `2` appended by the wrapper. The EOF code is not part of the protected source alphabet and is not exposed in the protected output.

For each source state `q`, compiled control:

1. `READ rin`;
2. dispatch code `0`, `1` or private EOF `2` by a chain of `DECJZ` instructions;
3. for source output `0`, `EMIT rout` while invariant `rout=0` holds;
4. for source output `1`, `INC rout; EMIT rout; DECJZ rout` so `rout` is restored to zero;
5. continue at the compiled label for `delta(q,a)`;
6. EOF reaches shared `HALT`.

Invalid external codes outside `{0,1,2}` enter a well-formed nonterminating invalid-control loop and therefore fail under the finite execution budget; they are outside the compiler theorem domain.

### COMP-1 theorem target

For every finite `Q`, every total `delta/lambda`, and every binary input word `w`, direct transducer execution and compiled `G0-reg-v1` execution have exactly the same protected output word and the compiled run halts.

Frozen overhead bounds for `n=|w|`:

```text
program_instructions <= 10|Q| + 2
execution_steps <= 6n + 5
register_count = 2
```

These are upper bounds, not optimality claims.

### Exhaustive P2 family

Enumerate **all 2-state deterministic binary-input/binary-output Mealy machines**:

- 4 `(state,input)` transition entries, 2 choices each: `2^4=16` transition maps;
- 4 output entries, 2 choices each: `2^4=16` output maps;
- total `256` machines.

For every machine, compare direct vs compiled execution for every binary input word of lengths `0..3`:

```text
1 + 2 + 4 + 8 = 15 words/machine
256 * 15 = 3840 exact compiler comparisons.
```

Zero behavior mismatches, non-HALT terminals or overhead violations are allowed.

## 7. REG-1 — counter/register fragment embedding

The deterministic source fragment with instructions

```text
INC(r,next)
DECJZ(r,nz,z)
HALT
```

and the same natural-register semantics embeds identically into `G0-reg-v1`.

Target: source and target configurations coincide step-for-step on program counter/register state and termination. This is a parent-owned syntactic specialization, recorded to establish expressivity boundaries rather than novelty.

## 8. COMP-2 / LOOP-1 / STORE-1

### Sequential composition

For two well-formed programs with disjoint labels/register namespaces except protected interface conventions, sequential composition is obtained by alpha-renaming and replacing each first-program `HALT` with a one-step unconditional branch encoded as

```text
DECJZ(z, start_Q, start_Q)
```

using a fresh zero register `z`. This has one-instruction/one-step boundary overhead per executed composition edge.

### Recurrence

Cycles in successor labels give recurrence without a dedicated loop macro. A self-loop `INC(r,L)` is the simplest positive witness; bounded terminating loops use `DECJZ` back-edges.

### Storage/retrieval

Declared registers provide statically addressed storage. `READ`/`INC`/`DECJZ` write registered addresses; `INC`/`DECJZ`/`EMIT` read them. Dynamic RAM addressing is **not** claimed.

## 9. Frozen hostiles

The tranche fails if any of these survives:

- undeclared register reference;
- missing successor label;
- unknown instruction constructor;
- input underflow accepted as success;
- step-budget exhaustion accepted as success;
- removing an instruction class still satisfies its frozen necessity requirement in contradiction to the analytic invariant;
- compiled Mealy behavior differs on any of 3,840 frozen exact comparisons;
- compiler accepts a corrupted state/output table or broken label map as a valid certificate;
- reported resource counts differ from an independent trace recount;
- program-size or step overhead exceeds the frozen bound;
- finite/register-scoped evidence is promoted to a unique minimal universal grammar, unbiased search or cross-paradigm derivation.

## 10. Literature/parent anchors

Primary/near-primary anchors frozen for subtraction:

- J. C. Shepherdson & H. E. Sturgis, *Computability of Recursive Functions*, JACM 10(2), 1963.
- M. Minsky, register/counter-machine treatments in *Computation: Finite and Infinite Machines* (1967), plus the register-machine tradition.
- G. H. Mealy, *A Method for Synthesizing Sequential Circuits*, Bell System Technical Journal 34(5), 1955; Moore/sequential-machine tradition.
- G. D. Plotkin, structural operational semantics / Aarhus notes and later SOS exposition.
- R. Alur et al., *Syntax-Guided Synthesis*, FMCAD 2013: synthesis grammar is an explicit syntactic candidate-space restriction.
- E. Real et al., *AutoML-Zero*, ICML 2020: generic low-level operations can support search over complete ML algorithms, while search-space choices remain consequential.
- M. Blum, *A Machine-Independent Theory of the Complexity of Recursive Functions*, JACM 14(2), 1967, as a warning that machine/encoding/resource measures must be stated rather than treated as representation-free.

## 11. Reconciliation ceiling

If and only if the dedicated PR CI is green, this tranche may reconcile only these #833 Section-E rows at their declared registered scope:

- Define a minimal architecture-neutral grammar `G0` — wording must state **relative minimality under the frozen five-requirement suite** and disclosed register representation prior.
- Justify every primitive in `G0` from computation/interaction requirements rather than known architectures.
- Prove which known computational models `G0` can express — only the finite Mealy family and the corresponding deterministic counter/register fragment are earned here.
- Add typed state carriers without naming neural/symbolic/probabilistic families.
- Add composition.
- Add recurrence.
- Add addressable storage/retrieval — static register addressing only.
- Add resource-metered execution.

All other Section-E rows remain OPEN.

## 12. Claim ceiling

`GMI_G0_REGISTER_CORE_AND_FINITE_EMBEDDINGS_AT_DECLARED_SCOPE`

Forbidden promotions:

- `UNIQUE_MINIMAL_UNIVERSAL_GRAMMAR`
- `ARCHITECTURE_PRIOR_FREE_GRAMMAR`
- `UNBIASED_SEARCH`
- `ALL_COMPUTATIONAL_MODELS_EMBEDDED`
- `NEURAL_MORPHOLOGY_DERIVED`
- `PROBABILISTIC_MORPHOLOGY_DERIVED`
- `GRAMMAR_REPRESENTATION_INVARIANT`
- `MORPHOLOGY_SELECTION_INVARIANT`
- `COMPLETE_GMI`
