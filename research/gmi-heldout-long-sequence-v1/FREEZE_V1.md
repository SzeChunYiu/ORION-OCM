# B9 held-out long-sequence neutral recovery — FREEZE V1

**Issue:** #602 B9 `Neutral recovery in a held-out long-sequence ecology.`  
**Status:** PRE-OUTCOME FREEZE. This commit contains no executor, result, winning expression, or scored held-out output.  
**Evidence target:** bounded P2 exact finite recovery under a family-blind low-level grammar.  
**Claim ceiling if successful:** `FINITE_EXACT_HELDOUT_LONG_SEQUENCE_NEUTRAL_RECOVERY_PARENT_OWNED_PROGRAM_SYNTHESIS`

## 1. Ecology and protected obligation

Input is a binary sequence `x_1,...,x_n`. The protected terminal answer is the exact count

`y = sum_t x_t`.

This deliberately fixes the limitation recorded in the earlier B9 witness: the obligation quotient grows with sequence length. At length `n` there are `n+1` distinct terminal counts, so any exact deterministic carried state needs at least `n+1` distinguishable terminal states and therefore at least `ceil(log2(n+1))` fixed-width bits.

Calibration lengths are `n={3,5,7}`. They may be used only to check that the grammar/executor is functioning.

**Held-out protected lengths are frozen now as `n={17,31,63}`.** No held-out result may change these lengths, grammar rules, selection rule, classifier, or falsifier.

## 2. Family-blind low-level grammar

A candidate is only an update expression over current scalar state `s` and current binary input `x`.

Leaves:

`{s, x, 0, 1}`

Commutative binary primitives:

`{add, xor, min, max}`

The legal candidate set is **every** leaf plus every depth-1 expression `op(a,b)` using an unordered pair with repetition from the leaves. Commutative argument permutations are canonicalized before scoring. No candidate field contains `RNN`, `STATE_SPACE`, `COUNTER`, `MEMORY`, `RECURRENT`, `ATTENTION`, or any architecture/family label.

Initial state is exactly `s_0=0`. The terminal prediction is the final scalar state itself. No learned readout is permitted.

Search sees only the expression and whether it satisfies the protected input/output relation. Post-hoc phenotype classification occurs only after exhaustive scoring.

## 3. Exact scorer — frozen before implementation

The executor must not sample binary strings. For each candidate and length `n`, it must propagate the exact reachable set of pairs

`(candidate_state, true_count)`

from `{(0,0)}` through all `2^n` histories by dynamic merging. At each step both `x=0` and `x=1` transitions are added. The candidate is exact iff, at terminal time, every reachable pair satisfies `candidate_state == true_count`.

This dynamic set is an exact quotient of exhaustive history enumeration: merging is allowed only after both candidate state and true count match.

## 4. Frozen prediction

Before implementing or running the held-out executor, predict:

1. the exhaustive family-blind search will contain at least one exact semantic class at every held-out length;
2. the minimum-node exact semantic class will implement accumulation of the incoming bit into carried state;
3. its reachable terminal state cardinality will be exactly `n+1`;
4. its fixed-width state burden will therefore be `ceil(log2(n+1))` bits;
5. this storage is strictly below explicit-history storage `n` bits at every protected held-out length.

The prediction is structural, not an architecture label. The expression string may only be reported after execution.

## 5. Frozen post-hoc classifier

After scoring only, an exact winner is classified as `ACCUMULATIVE_CARRY` iff:

- it is exact for the protected count obligation;
- its update depends on both prior state and current input on reachable states;
- its reachable terminal state count is `n+1` for each protected length.

Otherwise classify `OTHER_EXACT`.

The classifier does not participate in candidate generation or ranking.

## 6. Ranking and ties

Primary gate: exactness on the protected obligation.

Among exact candidates, rank by syntax node count (`leaf=1`, `binary expression=3`). Preserve all semantic/syntactic ties; do not add a post-hoc tie-breaker to force the predicted class.

## 7. Parent subtraction

Finite-state sufficient statistics, counters/streaming algorithms, Myhill–Nerode-style quotient logic, and enumerative/program synthesis receive first refusal. A successful result is **not** a new recurrent architecture theorem.

The only #602 residual tested here is methodological: can a label-free low-level update grammar recover the compact carried-state phenotype on genuinely held-out long sequences whose required quotient grows with `n`?

## 8. Falsifiers / terminals

Success terminal:

`HELDOUT_LONG_SEQUENCE_NEUTRAL_RECOVERY_EXACT_AT_FROZEN_LENGTHS`

Failure terminals include:

- no exact candidate on any protected length;
- minimum-node exact class is not `ACCUMULATIVE_CARRY`;
- reachable terminal state count differs from `n+1`;
- state bits are not `ceil(log2(n+1))`;
- explicit history is not strictly larger at a protected length;
- held-out lengths/grammar/classifier/ranking are changed after this freeze.

A failure closes this finite assay negatively. It must not be repaired by changing V1 after protected execution.
