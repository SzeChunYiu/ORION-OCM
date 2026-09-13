# Grand GMI Claim Ledger — Structural Neural Bound V1

Status date: 2026-09-13. Additive to the Grand-GMI claim ledgers. Authority:
`STRUCTURAL_NEURAL_BOUND_THEOREM_V1.md`.

| ID | Claim | Status | Scope |
|---|---|---|---|
| SN1 | The registered class is the single-hidden-layer integer-threshold form on parity-3, in two registered code shapes, rendered canonically and minimally, measured in the registered exact opcode coordinate. | DEFINITION / SCOPE | one task, one class, one coordinate |
| SN2 | Enumerating hidden units over a strictly wider coefficient range yields the same 104 behaviours and never a cheaper rendering, so the coefficient bound does not limit the derived minimum. | THEOREM | integer linear forms on three binary inputs |
| SN3 | Exact parity is infeasible with one or two hidden units and feasible from three; the enumerated minimum is 39 per call and 312 per sweep on CPython 3.12.3, attained by a compiled minimizer that computes parity. | THEOREM / EXHAUSTIVE ENUMERATION | registered class and coordinate |
| SN4 | Every unit count of five or more is excluded by a positive per-unit cost floor, so enumerating to four is complete over unit count. | THEOREM | registered class and coordinate |
| SN5 | The registered XOR realization at 88 per sweep is beaten by no member of the class, written or unwritten, because PL-2's bound holds of every member. | THEOREM / CLASS EXCLUSION | registered class, coordinate and interpreter |
| SN6 | The registered `N_SUM_THRESHOLD3_V3` candidate attains the derived bound on every tested interpreter, so the bound is tight in the PL-3b sense and the candidate register was not understating the neural family. | THEOREM / TIGHTNESS CERTIFICATE | three tested interpreters |
| SN6a | The minimum is attained by more than one specification, so by MS-3 only properties common to all minimizers are derived; no particular weight pattern follows. | SCOPE LIMIT | registered class |

## Per-interpreter derived bounds

| Interpreter | derived class bound per sweep | XOR witness per sweep | margin |
|---|---:|---:|---:|
| CPython 3.11.15 | 344 | 88 | 256 |
| CPython 3.12.3 | 312 | 88 | 224 |
| CPython 3.13.12 | 288 | 72 | 216 |

## Exact witness aggregate

- distinct hidden behaviours enumerated: `104`, identical over coefficients `[-2,2]` and `[-4,4]`, matching the count of threshold functions on three variables;
- per-unit-count minima on CPython 3.12.3: `k=1` infeasible, `k=2` infeasible, `k=3` = `39`, `k=4` = `45`;
- cost floor at `k=5` is `41`, already above the enumerated minimum `39`;
- the composed per-line prediction equals the compiled count of the minimizer, and the minimizer computes parity on all eight inputs;
- the registered shared-sum net attains `312` per sweep on 3.12, equal to the derived bound; the registered DNF net costs `472` and does not attain it;
- no timing measurement is used or produced.

Terminal: `GRAND_GMI_STRUCTURAL_NEURAL_BOUND_GREEN_AT_FINITE_SCOPE`.
Open residue: more than one hidden layer, non-threshold activations,
vectorized realizations, realizations that precompute outputs (excluded by the
predicate as a scope choice), other substrates and languages, and all timing
coordinates. The verdict for the physically legal set of parity-3
realizations stays open, since the registered class is not a proved cover of it.
