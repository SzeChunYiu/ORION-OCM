# CAR protocol — fixed before this unit's first model execution

Base: 80677bbb2aa891c8e1c22c5c3dac396c656e53c2.
Original audited PR601 head: 8a485bfe48a0e0549229ac5578f7c1e78ccf6fe4.

## Exposed tasks and policy
Primitive instructions are double(x)=2x and inc(x)=x+1. A candidate is a
nonempty word of length at most 5. The verifier evaluates every candidate on
all four declared inputs (0,1,2,3), without early mismatch stopping.
No solution, candidate ordering or pricing will be tuned after seeing these runs.
These tasks are deliberately constructed calibration examples; no prospective
or independently authored generalization claim is made.

The fixed sequence is acquisition of x+2, acquisition of x+4, then solving the
different target x+5. Only the relevant input/output table is passed to search.
Library instructions are ordered newest first, then primitive names alphabetically.
Search enumerates by length and then that order. All candidate bodies, outputs
and comparison outcomes are retained. There is no cache of prior solutions.

1. Start from an empty library, search x+2, independently verify the returned
   program, flatten it into primitive instructions and admit it under name h.
2. Clone the same explicit machine state. Compare acquisition of x+4 with h
   enabled and with h disabled (RESET access), leaving the stored backing bytes.
   Independently verify and store each found new program as m. Compare full
   conditional acquisition charges, including admission, not just candidate rank.
3. From the acquired H state, independently clone acquired, disabled-m, sham
   and restored-m states. Every modification is a legal visibility-gate update;
   restored disables then reenables m. No acquisition is repeated per arm.
   Verify sham/restored equal the acquired state before the later query.
4. Solve x+5 identically in each arm; retain candidate-level calls showing
   m contributes before the first successful target verification. Independently
   verify every final body on (0,1,2,3) and evaluate it on (4,5). The last two are
   fresh inputs for the authored obligation, not fresh tasks or protected data.
5. A separately generated library-priority parent uses the same supplied library
   and exact schedule. Equality is PARENT_SUFFICIENT, not new-controller evidence.
   A primitive-only arm supplies a transparent RESET comparison.

## Cost and outcome rules
One authored unit per named event in PARENTS_AND_COSTS. Primitive work inside
macro calls is always executed and charged. All candidate generation, task reads,
comparisons, independent checks, body copying, admission, library lookup, logical
storage, cloning and gate updates receive explicit charges. Report work by phase
and the complete event sequence, including unsuccessful candidates.

The causal-use gate requires a stored m absent initially, verified acquisition
in both arms, earlier later-task success with m, sham/restoration equality, and
complete source/state/charge records. If any fail, record CANNOT_CHECK or the
specific failed inequality; do not infer K2 from a bare rank comparison.
History acquisition is shown separately and added to lifecycle comparisons.
Logical holding is charged once per retained primitive token per phase boundary.
Diagnostic clones/interventions and independent audit calls are separately included
in the experiment ledger; no physical or Python wall-time total is claimed.
