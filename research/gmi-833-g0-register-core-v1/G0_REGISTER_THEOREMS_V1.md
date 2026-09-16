# G0-reg-v1: finite operational grammar, relative minimality, and exact embeddings

**Issue:** #868, child of #833 Section E  
**Freeze authority:** `FREEZE_V1.md`, commit `7201b1a56d7eb62de0d405da45142b77f30920da`  
**Claim ceiling:** `GMI_G0_REGISTER_CORE_AND_FINITE_EMBEDDINGS_AT_DECLARED_SCOPE`

## 1. Claim boundary

This tranche does **not** claim a unique universal instruction set or a literally architecture/prior-free grammar. `G0-reg-v1` deliberately supplies a register/control representation prior. The defensible statement is relative:

> Given the frozen operational requirement suite, five instruction classes are individually load-bearing, and the resulting typed language exactly simulates the declared finite Mealy family and its deterministic counter/register-machine sublanguage with explicit finite overhead/resource certificates.

The counter/register-machine computability results, finite transducer semantics, structural operational semantics, syntax-guided synthesis framing, and generic-operation search-space ideas are parent mathematics. The residual here is the exact repository contract and hostile/freeze evidence.

## 2. Syntax and deterministic small-step semantics

A program is a finite labelled control map over a finite nonempty set of named natural-number registers. A machine configuration is

```text
C = (pc, rho, i, O, R)
```

where `rho : Register -> N` is the current store, `i` is the unread suffix of the external input stream, `O` is the protected output sequence, and `R` is the raw resource counter. Initial registers are all zero.

The five instruction forms are:

```text
READ(r,l)
INC(r,l)
DECJZ(r,l_nz,l_z)
EMIT(r,l)
HALT
```

The one-step relation is a partial function on well-formed configurations:

```text
READ:   x::i' -> (l, rho[r:=x], i', O)
INC:            (l, rho[r:=rho(r)+1], i, O)
DECJZ+: rho(r)>0 -> (l_nz, rho[r:=rho(r)-1], i, O)
DECJZ0: rho(r)=0 -> (l_z, rho, i, O)
EMIT:           (l, rho, i, O ++ [rho(r)])
HALT:           HALTED(O,rho)
```

`READ` on empty input yields the distinct fail-closed terminal `INPUT_UNDERFLOW`. Static ill-typedness (unknown instruction, missing register, missing successor/start label) yields `MALFORMED_PROGRAM`. Exhausting the registered step budget yields `STEP_BUDGET_EXHAUSTED`. No missing label is interpreted as implicit halt.

**SEM-1 (determinism).** Every well-formed nonterminal configuration has exactly one successor: there is exactly one instruction at `pc`, and the only branch predicate `rho(r)>0` versus `rho(r)=0` is exhaustive and disjoint.

## 3. RES-1 — exact raw execution vector

The registered resource vector is

```text
(|P|, steps, register_reads, register_writes, input_reads, output_writes).
```

Per successful instruction:

| instruction | steps | reg reads | reg writes | input reads | output writes |
|---|---:|---:|---:|---:|---:|
| READ | 1 | 0 | 1 | 1 | 0 |
| INC | 1 | 1 | 1 | 0 | 0 |
| DECJZ positive | 1 | 1 | 1 | 0 | 0 |
| DECJZ zero | 1 | 1 | 0 | 0 | 0 |
| EMIT | 1 | 1 | 0 | 0 | 1 |
| HALT | 1 | 0 | 0 | 0 | 0 |

The executor records an instruction trace and a second trace-fold implementation reconstructs the dynamic vector exactly. No scalar cost is defined by this result.

## 4. RELMIN-1 — instruction-class irredundancy relative to frozen requirements

The word **minimal** is scoped to the following five requirements, not to every computational language.

### READ is necessary for `REQ-IN`

Without `READ`, no transition inspects or consumes input. Induction on executed steps therefore gives identical program counter, register store and output for executions started from the same zero store but different input values. Hence successful protected behavior is input-value independent. The full-grammar witness `READ r; EMIT r; HALT` separates input `0` from input `1`.

### EMIT is necessary for `REQ-OUT`

Only `EMIT` changes protected output. Therefore every program without `EMIT` has output `epsilon` by induction on steps. The full grammar witness `INC r; EMIT r; HALT` outputs `[1]`.

### INC is necessary for `REQ-GEN`

On truly empty input, a successful run cannot execute `READ`. Without `INC`, the only remaining register writer is the positive branch of `DECJZ`, which strictly decreases a positive value. Starting from all-zero registers, no register can become positive. Thus positive internal value generation is impossible. `INC r; EMIT r; HALT` is the positive witness.

### DECJZ is necessary for `REQ-BRANCH`

Without `DECJZ`, every nonterminal instruction has one statically fixed successor. For equal-length valid inputs, the control-label path and therefore the `EMIT` count schedule are independent of input values. The frozen full-grammar witness emits one zero on input `0` and two zeros on input `1`, so it cannot be reproduced after removing `DECJZ`.

### HALT is necessary for `REQ-TERM`

`HALT` is the only semantic rule yielding successful terminal `HALTED`; falling off is malformed and cycles exhaust the budget. Thus successful finite termination is impossible without the class.

### Bounded corroboration

The analytic invariants are primary. A finite hostile reconstruction enumerates all two-label/one-register programs over the remaining four classes:

```text
READ removed:   81
INC removed:    81
DECJZ removed:  49
EMIT removed:   81
HALT removed:  100
total:          392
```

Zero violations are found.

## 5. COMP-1 — exact compiler from finite binary Mealy transducers

Let `M=(Q,{0,1},{0,1},delta,lambda,q0)` be a finite deterministic Mealy transducer emitting one bit per consumed input bit. The compiler uses `rin` and `rout`, plus private EOF code `2`.

For each source state `q`:

```text
q_read: READ rin -> q_d0
q_d0:   DECJZ rin -> q_d1 / q_out0
q_d1:   DECJZ rin -> q_d2 / q_out1
q_d2:   DECJZ rin -> invalid / halt_eof
```

If `lambda(q,a)=0`, `q_outa` emits zero `rout` and transfers to `delta(q,a)_read`. If `lambda(q,a)=1`, the compiler executes `INC rout; EMIT rout; DECJZ rout` and then transfers, restoring `rout=0`. EOF reaches shared `HALT`; invalid codes diverge within the finite budget and are outside the theorem domain.

### Theorem COMP-1

For every finite total `M` and binary word `w`, running the compiled program on `w ++ [2]` halts and produces exactly the direct Mealy output `M(w)`.

### Proof

Induct on consumed source symbols. At each source-state entry the invariant is: control is at the compiled label for the current source state, `rin=rout=0`, and the protected output equals the direct output on the consumed prefix. `READ` plus the `DECJZ` chain selects exactly the source bit branch and restores `rin=0`. The output block emits exactly `lambda(q,a)` and restores `rout=0`, then transfers to the compiled label of `delta(q,a)`. EOF code `2` traverses the dispatch chain to `halt_eof` without emission. Thus the invariant extends over every symbol and yields exact behavior at termination. `□`

Per ordinary symbol the compiled execution uses at most six target steps; EOF costs five, so

```text
steps <= 6|w| + 5.
```

Each source state contributes at most ten instructions; shared EOF halt and invalid loop add two:

```text
|P_compiled| <= 10|Q| + 2.
```

Exactly two registers are used.

The exact certificate checks all `2^4 * 2^4 = 256` two-state binary Mealy machines against all 15 binary words of lengths `0..3`: 3,840 direct-vs-compiled comparisons, zero behavior mismatches, zero non-HALT terminals and zero overhead/resource violations. A second interpreter independently repeats all 3,840 executions.

## 6. REG-1 — deterministic counter/register fragment

The source language containing exactly `INC`, `DECJZ`, and `HALT` with the same natural-register semantics is a syntactic sublanguage of `G0-reg-v1`.

**Theorem.** Identity translation preserves program counter/register configurations and termination step-for-step.

**Proof.** Case split on the source instruction. Each source rule is exactly the corresponding target rule; induction on execution length gives identical configurations. `□`

Finite corroboration exhausts all `7^2=49` two-label/one-register programs and finds zero disagreements.

## 7. COMP-2 — sequential composition

Alpha-rename two well-formed programs to disjoint label/register namespaces and introduce a fresh zero register `z`. Replace every renamed `HALT` of the first program by `DECJZ(z,start_Q,start_Q)`. Since `z=0`, either branch target is `start_Q`, giving an unconditional transfer. The linking instruction replaces the first program's halt, so the freeze's “one boundary instruction/step” statement is conservative; the sample has zero net step/instruction overhead relative to executing the first halt then the second program.

## 8. LOOP-1 — recurrence from label cycles

Successor labels may point backward or to themselves, so recurrence needs no dedicated loop macro. A bounded counter loop `DECJZ(r,loop,halt)` is machine-checked. This establishes expressibility of recurrence, not termination of arbitrary cyclic programs.

## 9. STORE-1 — static addressable storage/retrieval

Registers are named static addresses. `READ` and `INC` write them; positive `DECJZ` reads/writes them; `EMIT` retrieves a selected cell into protected output. Dynamic RAM addressing and random-access complexity are not claimed.

## 10. Grammar/search-bias boundary

The grammar determines expressibility and description syntax and is therefore a disclosed inductive bias. This result does not establish search neutrality. Description length, reachability under a search law, grammar remints, alternate search algorithms, resource scalarizations and morphology selection remain separate #833 obligations.

## 11. Parent/subsumption ledger

| Parent | Ownership retained | #868 residual |
|---|---|---|
| Shepherdson–Sturgis / Minsky register machines | register/counter computability | exact typed G0 contract, I/O/resource wrapper, bounded hostiles |
| Mealy/Moore finite sequential machines | finite transducer semantics | exact compiler and registered overhead |
| Plotkin SOS | small-step operational-semantics method | repository-specific rules/terminals |
| SyGuS | grammar as syntactic candidate restriction | fail-closed disclosure that G0 is a bias |
| AutoML-Zero | search over generic low-level operation programs | no independent-rediscovery claim |
| Blum complexity-measure tradition | machine/coding/resource assumptions must be stated | raw-vector and overhead discipline |

## 12. Forbidden extrapolations

`UNIQUE_MINIMAL_UNIVERSAL_GRAMMAR`, `ARCHITECTURE_PRIOR_FREE_GRAMMAR`, `UNBIASED_SEARCH`, `ALL_COMPUTATIONAL_MODELS_EMBEDDED`, `NEURAL_MORPHOLOGY_DERIVED`, `PROBABILISTIC_MORPHOLOGY_DERIVED`, `GRAMMAR_REPRESENTATION_INVARIANT`, `MORPHOLOGY_SELECTION_INVARIANT`, and `COMPLETE_GMI` remain forbidden from this tranche alone.
