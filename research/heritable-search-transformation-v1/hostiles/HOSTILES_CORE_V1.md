# HST Hostiles Core V1 (lane A, D2)

One smallest counterexample per theorem with ONE load-bearing assumption removed (or,
where the row is already an impossibility/limit, the minimal world that *attains* the
theorem's boundary — the nearest false generalization is then the overclaim the frozen
statement forbids). Each witness is machine-checkable: `exact/check_core_v1.py`
re-derives every number from the JSON in `hostiles/`. Sizes are stated honestly: these
worlds are tiny by design (a witness only needs to be exact, not realistic).

| witness | theorem | assumption removed / boundary attained | size | falsifies |
|---|---|---|---|---|
| `W_T01_mandatory_overhead.json` | T01 | M = 0 → M = 2 | 2 strategies, 1 task | "inheritance cannot worsen optimal achievable burden" — `m_{t+1} = 5 > 3 = m_t` while `A_t ⊆ A_{t+1}` holds |
| `W_T03_aliasing.json` | T03 | (exhibits hypotheses minimally) | 2 states, 1 internal state, 2 actions, 2 policies | "good enough search repairs any contract" — 0/2 φ-measurable policies succeed; the escape is a channel split, not search |
| `W_T05_macro_never_pays.json` | T05 | (instantiates threshold below break-even) + drops "all costs charged" in case B | 2 cases, ≤ 4 frozen numbers each | "code-shortening macro acquisition is beneficial" — case A never pays back (6 < 9); case B is *beneficial on description length, harmful on execution* (16 vs 31): coordinates disagree |
| `W_T06_missing_edge_false_locality.json` | T06 | dependency completeness (one real edge missing) | 3 nodes, 1 declared edge, 1 missing edge | **the important one**: declared DAG says R ∉ Desc(S) ⇒ R unchanged; actual computation moves R 5 → 6. False locality from an individually-correct but incomplete graph |
| `W_T07_ratchet_no_transfer.json` | T07 | (attains the boundary the negative list describes) | 2 benchmarks × 3 items, 4 generations, 3 tables | "archive ratcheting to perfect quality implies generalization" — q1 strictly ratchets 0→3 (perfect), q2 stays exactly at default-chance 1 forever |
| `W_T18_fixed_epsilon_saturation.json` | T18 | (attains the bound exactly; then executes escape route 1) | 11 + 40 states, integers/halvings | "open-ended self-improvement = fixed-ε gains on one frozen benchmark forever" — exactly 10 ε=1 improvements from B₀=10, then arithmetic stops it; a halving-ε restart yields unbounded *count* with total drop ≤ 1 (protocol artifact, not capability) |

## Reading notes per witness

**W-T01.** The subset assumption survives (`A_t ⊆ A_{t+1}` — a2 is added, a1 retained);
only "unchanged cost" dies. Every strategy is charged M = 2, so both old and new
strategies shift up by M and the new one (raw 5, charged 7) does not save enough.
Savings needed to break even: some `a*` with raw cost < 1 — none exists. This is the
smallest world in which M alone, with the superset assumption intact, reverses the
conclusion.

**W-T03.** The minimal aliased pair: φ collapses two states to one internal state; the
contract demands disjoint correct action sets ({L} vs {R}). Both φ-measurable policies
(the only two) each fail exactly one state. The witness also names the repair: a φ′
that splits the fiber makes the contract satisfiable — establishing that the necessary
and sufficient fix is representational, which is the theorem's operational content for
#152 (aliasing diagnosis = certificate that a new channel/distinction is required).

**W-T05.** Case A: honest bookkeeping, macro loses (lifecycle 33 > 30; identity LHS 6 <
RHS 9). Case B is the issue §11 hostile "macro that shortens code but increases
execution/check cost": description length 20 → 5 (a 2^15 prior-share gain under a T04
reading — enormous on paper) while per-use cost rises 4 → 7; lifecycle 31 > 16. A
pure-MDL evaluation admits the macro; the frozen execution coordinate rejects it. The
two readings disagree ⇒ no coordinate-free "beneficial" exists; the frozen scalarization
decides, which is exactly assumption 1 of the row.

**W-T06.** The declared graph is a legitimate DAG whose declared edges are all *true*
(X→R is real). Only completeness fails: R also reads S, undeclared. The declared
descendant closure of the intervention target is {S}, R is outside it, so the
locality-skipping inference fires — and R changes. Two lessons are exact: (i) DAG-hood
of the declared graph licenses nothing by itself; (ii) the iff-direction of T06 means
the *proof obligation* for any recomputation-skip is "the declared semantics are
complete for the protected outputs" — a property of the actual computation, not
decidable from the declared graph (compare T15's boundary; this is why C's protected
validation is contract-bound, not graph-bound).

**W-T07.** Every hypothesis of the ratchet theorem holds: fixed evaluator, immutable
unlimited archive, frozen total order, admissibility gate. The archive's τ1 best is
strictly monotone and attains the maximum (3/3). τ2 quality is constant at 1 (default
answer "d" is correct on exactly 1 of 3 τ2 items) for every retained table — zero
information about τ2 crosses the τ1-perfect ratchet. The theorem is not contradicted
(its negative list already disclaims generalization); the witness exists to make that
disclaimer *executable*: any benchmark-only ratchet claim must be read as τ1-local.

**W-T18.** Phase 1 attains the bound with equality: ten ε=1 improvements from B₀=10 to
B₁₀=0=b_min; the eleventh would need B ≤ −1 < b_min — arithmetic stops the lineage.
Phase 2 restarts from B=5 with ε halving each generation: forty generations (and
counting — the checker runs 40 and the pattern is a geometric series) all valid, yet
the total drop is the convergent sum 1, leaving B_∞ = 4 ≥ b_min. "Unbounded number of
improvements" and "unbounded improvement" are different claims; only the first survives
route 1, and it is an ε-protocol artifact. Routes 2–5 do not contradict the theorem —
each re-freezes the coordinate and thereby exits the theorem's hypotheses (which is why
the frozen statement's escape disjunction is definitional: it enumerates the hypotheses,
not new mathematics).

## Non-witnesses (explicit)

- T01 with `A_t ⊆ A_{t+1}` failing (strategy outlawed): trivially reverses; not
  informative beyond W-T01, so not shipped separately.
- T06 cyclic (TMS) case: declared boundary in the proof, no witness claimed (would
  require choosing a fixpoint semantics — out of scope for lane A).
