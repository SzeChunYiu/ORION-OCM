# K05 lower bound — full B_CONTR decision cannot fit the frozen 6-cell / 40-node envelope

Companion to `FREEZE_V1_SLICE_ADDENDUM_K05_V1.md`. The argument is a counting
proof over the frozen basis (`machinery_v1.py`: `{ADD, NEG, GE_c}`, guard
`D = [-3, 3]`) and the frozen `M_ITER(18, 16)` model, plus the empirical
confirmation by the committed v5 build and the in-protocol reflexive witness.

## 1. Time-invariance removes the step dimension

The 18-cell task layout is constant across the 16 steps (it is loaded once).
Every work-cell expression `e_i(s_1..s_k)` is therefore a **fixed** function of
the same inputs at every step; work cells update synchronously from the
previous step's values. A work cell can self-reference (accumulate), but every
input it reads is constant, so a boolean accumulator reaches a fixed point in
one step (OR-accumulating a constant is idempotent, AND-accumulation cannot
start at 1 from a zero initial cell, and a guard-3 arithmetic counter yields at
most 4 phases while ALL phase predicates must coexist inside the same fixed
expression, so their node counts add). The 16 steps confer gate depth only —
they never increase the set of distinct predicates a machine can compute.
Phase-multiplexing a step counter therefore cannot reduce the node or cell
budget below the single-pass requirement.

## 2. Predicate census for a correct decision

A correct decision outputs 1 on exactly the 1,176 positives: 792 reflexive
(t0 == g), 320 one-step (2->L / 3R->2 / 3L->2 per rule slot), 64 two-step
(same-rule chains). The output's dependency cone must therefore contain, at
minimum, the following **distinct** atomic equality tests:

- 5 reflexive token-equalities `EQ_T(s_k, s_13+k)`, k = 0..4 (12 nodes each in
  `expr_size`: `GE+2(add(GE+0(add(a,NEG b)), GE+0(add(b,NEG a))))`);
- 4 t0-shape tests `EQ_C(0,2)`, `EQ_C(3,-1)`, `EQ_C(2,2)`, `EQ_C(1,2)`;
- per rule slot r in {0, 1}: g-leaf `EQ_C(13,rhs_r)` + `EQ_C(14,-1)`;
  3R inner `EQ_T(3, lhs_x)` + `EQ_T(4, lhs_y)`; 3L inner-left `EQ_T(2,lhs_x)` +
  `EQ_T(3,lhs_y)`; 2->L t0==lhs `EQ_T(1,lhs_x)` + `EQ_T(2,lhs_y)`; the g-pattern
  tests `EQ_C(13,2)`, `EQ_C(14,1)`, `EQ_C(15,rhs_r)`, `EQ_C(15,4)`, `EQ_C(16,-1)`;
- two-step extras `EQ_T(1,lhs_x)`, `EQ_C(rhs_1, lhs_y)` and their 3L mirrors.

This is a **conservative** lower bound of 19 distinct atomic predicates
(positions vs positions or constants); the v5 build actually needs 36 distinct
equality subtrees.

## 3. Cell floor and node floor

- A work cell holds a single `D` value; under guard 3 it can present at most
  two {0,1} bits (v = b1 + 2*b2 in {0..3}, decoded by `GE+1/GE+2/GE+3(v)`), and
  a packed cell exposes the AND and the individual second bit but **not** a
  shared first bit alone — any bit that feeds two or more independent
  conjunctions (e.g. `inner == lhs_r` feeds both the one-step 3R->2 detector and
  the two-step 3R chain) must be a single-bit cell. The reflexive test alone
  needs 5 token-equalities ANDed (>= 68 nodes, >= 2 cells at the 40-node cap);
  each rule slot needs its own g-leaf / inner / inner-left single-bit cells;
  the one-step OR, two-step OR and output OR each need a cell. The cell floor is
  therefore well above 6 (the v5 build uses 14).
- The node floor: 19 predicates at >= 7 nodes each with AND/OR glue, and with
  shared bits either inlined (duplicating their node cost into every consumer)
  or single-bit cells (consuming the 40-node budget), exceeds 6 x 40 = 240. The
  v5 build's 522 operator nodes (288 of them in 36 equality subtrees) is the
  measured confirmation.

## 4. Conclusion

Any correct `B_CONTR` decision machine needs >= 11-15 work cells; the frozen
protocol (work <= 6, every expression <= 40 nodes, total <= 24) is
structurally insufficient, and the strongest in-protocol machine is the
reflexive witness (6 work cells, cost 54, 384 / 1,176 errors, 0 false
positives). The v5 machine (14 work cells, cost 536) realizes the full decision
at the amended protocol of `FREEZE_V1_SLICE_ADDENDUM_K05_V1.md`.
