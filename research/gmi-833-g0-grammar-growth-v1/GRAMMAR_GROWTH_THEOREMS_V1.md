# Grammar-growth theorems (E8 / #897)

All statements are at the scope frozen by `FREEZE_V1.md` (commit `10f0ef37`): the
`{a,b,c}` token grammar, the charged symbol-cost model, the deterministic INV-1
rule, and the frozen fixtures. Every quantity below is an exact integer and is
recomputed by `independent_oracle_v1.py`.

## T1 (GRW-1: conservative monotone extension)

**Statement.** Let `G_t = (Σ ∪ M_t)` with acyclic macro library `M_t`, and admit
`m_{t+1} -> u` where `u` is a sequence over `Σ ∪ M_t`. Then:

1. every program over `G_t` is a program over `G_{t+1}` and `Expand` is unchanged
   on it;
2. every program using `m_{t+1}` has the protected semantics of its full
   expansion;
3. if the dependency relation has a cycle, expansion signals
   `RECURSIVE_LIBRARY_CYCLE` and the registered grammar object is unchanged.

**Proof.** (1) The alphabet grows; programs are finite sequences; expansion is
defined structurally over symbols, and for symbols in `Σ ∪ M_t` the expansion
function uses the same bodies, which the admission does not modify, so by
induction on program length the expansion of every old program is unchanged.
(2) `Expand` is a total function on programs over `G_{t+1}` whenever the
dependency DAG is acyclic: order macros by a topological order of the DAG
(exists iff acyclic) and expand by structural recursion, terminating because
each macro's body references only strictly earlier macros or base tokens.
(3) If a cycle `m ->+ m` exists, no topological order exists; the expansion
procedure detects the in-progress symbol on the recursion path and raises before
any grammar mutation (the admission API is fail-closed: the library object is
returned unchanged on the hostile path). Machine checks: all registered
admissions pass in-trace expansion-preservation on every corpus program, and
self-loop / two-cycle / three-cycle hostiles all return the code with the
grammar snapshot unchanged (`RESULT_V1.json:hostiles.cycle`). ∎

## T2 (admission arithmetic)

For candidate body `u` of current-alphabet length `b` with greedy non-overlapping
occurrence count `o` over a corpus of `S` symbols, the frozen charged corpus cost
is `b + (S − o(b−1)) + κ`, so admission ⇔ `o(b−1) > b + κ` ⇔ `gain = o(b−1) − b − κ > 0`
(strict). Two corollaries used as hostiles: with `b ≥ 2` and `κ ≥ 0`, `o = 1`
gives `gain = (b−1) − b − κ < 0`, so single-occurrence candidates are rejected by
arithmetic alone (no extra threshold exists); and `o(b−1) = b + κ` (zero gain) is
rejected — demonstrated at `κ = 1` with `o = 3, b = 2` (`gain = 0`).

## T3 (burden formula and enumerator equivalence)

**Statement.** For grammar alphabet `A` symbols in frozen canonical order with
per-symbol expansions `{e_s}`, and target word `w`: the first program in the
breadth-by-length, lexicographic-within-length enumeration whose expansion
equals `w` has description length `ℓ*` = the least `r` such that `w` segments
into `r` symbol expansions, and is the lexicographically least such program; its
burden is exactly `Σ_{j=1}^{ℓ*−1} |A|^j + rank_ℓ*(p) + 1` where `rank` is the
|A|-ary index of `p` in the length-`ℓ*` class.

**Proof.** Enumeration visits exactly all programs of lengths `< ℓ*` (count
`Σ |A|^j`), then the length-`ℓ*` class in lexicographic order; within a fixed
length the lexicographic order on symbol sequences is the |A|-ary numeric order
of their index encodings, so programs before the first hit contribute exactly
`rank_ℓ*(p)`, and the hit itself contributes 1. The main implementation computes
`ℓ*` and the lex-min program by bottom-up segmentation DP; the oracle recomputes
by naive enumeration and by an independent top-down search. All three agree on
every registered target and exhaustively on all words of length ≤ 4. ∎

## T4 (widened-frontier regression; negative-control mechanism)

**Statement.** If no program using a library symbol expands to target `w`, then
`B_{G0 ∪ L}(w) − B_{G0}(w) = Σ_{j=1}^{ℓ*−1} (|A_L|^j − 3^j) + (rank_{A_L}(p*) − rank_3(p*))`
where `p*` is the pure-base first-hit program — strictly positive once `|A_L| > 3`
and `ℓ* ≥ 3`, independent of the charges.

This is the registered instance of the `h1-amortized-acquisition` parent
phenomenon (`NO_AMORTIZED_ACQUISITION_LATER_NOT_CHEAPER`): widening the token set
inflates every enumerated prefix. On the frozen control set the measured total
regression before charges is +1,172, plus `K_total = 6` → net +1,178
(`RESULT_V1.json:heldout_unrelated_control`). The regression is preserved and
reported, not hidden; the HLD-1 success criterion for the control is exactly
`net ≥ 0`.

## T5 (THR-1 exact lifecycle threshold; parent #233 HST-T05)

With `Δ = b − 1` (marginal per-occurrence symbol saving in the grammar that
already admits the macro's dependencies) and `K = b + κ`, lifecycle positivity at
the registered horizon is exactly `H_eff · Δ > K`. On the frozen fixture
(`κ = 1`): `m1` (b=2): `H_eff = 8` first-hit uses, `8·1 = 8 > 3`; `m2` (b=2):
`H_eff = 13`, `13·1 = 13 > 3`; aggregate `21 > 6 = K_total`. Base-relative
reading (`Δ` = full-expansion length − 1): `8·1 > 3` and `13·3 = 39 > 3`. All
identities hold with margin; the H+ net is `2κ − 48741`, so the charged
verdict stays strictly negative through `κ = 24370` (formation of the second
generation, not the held-out verdict, is the binding constraint at `κ ≥ 2`;
see the ablation rows).

## T6 (registered run facts)

- Invention: `m1 -> (a,b)` (`o = 11`, `gain = 8`) then `m2 -> (m1,m1)`
  (`o = 4`, `gain = 1`), stop by saturation; final corpus
  `[(m1,c,m1), (m2)×4, (m1)]`; `S_0 = 23`, `D_reg = 23`, depth used 2.
- H+ (12 targets): `50,052 -> 1,307` burdens, `K_total = 6`, net `−48,739`.
- H− (12 targets): `538 -> 1,710` burdens, `+6`, net `+1,178`.
- NULL-1 (200 seeds, equal size): best null net `−48,737`; `0/200` beat the
  true library (empirical rank 1). The nearest null is a first-order
  `(ab, abab)` library: recursion wins through cheaper charged definitions
  (`2+κ` vs `4+κ`) and compositional coverage of partial-reuse targets, not
  through raw per-use savings.
- κ-ablation: second generation forms at `κ ∈ {0,1}` and not at `κ ∈ {2..8}`;
  the frozen primary `κ = 1` is the derived maximum, matching the freeze rule.
