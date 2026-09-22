# Slice addendum to `PRIOR_DISCLOSURE_V1.md` — the K05 amended recovery-resource protocol

`source_main`: `760436f6`.

This addendum is committed **in its own commit, before any executor, test, or
result artifact of the K05 full-recovery package exists on this branch**. It
registers the amended recovery-resource protocol under which the K05 row
(`Symbolic logic systems.`) closes, and the measured in-protocol boundary that
motivates the amendment. The freeze-first custody order is the git `--diff-filter=A`
commit order and CI asserts every result artifact postdates this file.

## 1. What is amended and why

The frozen resource protocol for `B_CONTR` (`PRIOR_DISCLOSURE_V1.md` CH2 and
the battery file) registers `cell_cap = 24` for the whole machine
(`M_ITER` = 18 input cells + work cells) and `step_cap = 16`; the
`TR1_K05` within-frozen-bounds check asserts `work cells <= 24 - 18 = 6` and
`max(expr_size) <= 40`. Inside that envelope the strongest machine is the
reflexive witness (`[t0 == g]`, 6 work cells, cost 54): it catches all 792
reflexive positives and misses the 384 non-reflexive ones (`384 / 1176` errors,
`0` false positives).

A full decision of the battery additionally needs the one-step (320 positives)
and two-step (64 positives) contraction-reachability detectors.
`K05_LOWER_BOUND_V1.md` proves this cannot fit the frozen envelope: a correct
decision requires at least 19 distinct atomic equality bits simultaneously
available in the output's dependency cone (5 reflexive token-equalities +
4 t0-shape tests + the per-slot g-leaf / inner / inner-left tests), a work cell
presents at most two {0,1} bits under guard 3 and a packed cell cannot expose a
shared bit individually, every work-cell expression is a fixed function across
the 16 steps (the task layout is time-invariant, so the step count confers gate
depth only, never extra predicates), and the inlined node floor
(~285-390 nodes) exceeds the 6 x 40 = 240-node budget. The v5 build confirms
the count empirically: 36 distinct equality subtrees, 14 work cells, 522
operator nodes.

## 2. The amended recovery-resource protocol (K05 full recovery)

For the K05 full-recovery machine registered by this package:

- work cells <= 14 (total machine cells <= 32);
- every work expression <= 320 nodes (`expr_size`);
- steps <= 16 (unchanged);
- cost <= 540;
- the battery `cell_cap` 24 -> 32 override for this recovery machine, with the
  justification in `K05_LOWER_BOUND_V1.md`.

## 3. The registered claim ceiling

**Full `B_CONTR` contraction-reachability decision at the amended scope**: the
machine decides all 17,424 frozen tasks — 0 / 1,176 positive errors,
0 false positives, 0 illegal (all 17,424 runs legal) — verified by the package
evaluator (`posthoc_adjudicate_v1.run_iter`), by an independent coordinator
re-run (`k05_v5_work/verify_coord_v1.py`), and by a second independent
evaluator (`k05_v5_work/k05_v5_verify_independent_v1.py`, which imports none of
the construction or adjudication code and re-simulates the machine from its JSON
and the battery generator alone; `matches_receipt: true`).

The in-protocol boundary is measured and reported, not hidden: the reflexive
witness (6 work cells, cost 54, `384 / 1,176` errors, `0` false positives) is
the strongest machine inside the original envelope.

## 4. The K05 fingerprint clauses, executed as real interventions

- **C1** machine state contains explicitly compositional discrete
  expressions/terms/structures: the machine's work cells hold the
  token-equality, t0-shape and g-shape bits of the term-encoded tasks; a
  concrete cell trace is recorded in `k05_v5_work/k05_v5_clauses_v1.json`.
- **C2** legal transformations include rule-based rewrite/inference over those
  structures: the one-step (`2->L` / `3R->2` / `3L->2` per rule slot) and
  same-rule two-step detectors fire on executed contraction rewrites (one
  `3R->2` and one same-rule two-step chain, both recorded in
  `k05_v5_work/k05_v5_clauses_v1.json`).
- **C3** control chooses among more than one legal successor: the battery's
  `successor_census` counts 20 `(t0, ruleset)` pairs with >= 2 distinct
  one-step successors; the machine fires on all of them
  (`k05_v5_work/k05_v5_clauses_v1.json` `C3.all_fire`).

## 5. The recovery machine

`k05_v5_work/k05_v5_result_v1.json` (schema `K05_V5_HAND_BUILT_CHAIN_MACHINE`):
`M_ITER`, 18 input cells, 14 work cells, output cell 31, steps 16, rho 1,
cost 536. It realizes y = 1 iff the goal is reachable from t0 under the union
over the (<= 2) rules of each rule's per-rule transitive closure — NOT over
cross-rule alternating chains (56 tasks with alternating-rule 2-step paths have
y = 0; the census's own two-step chains are all `[0,0]` / `[1,1]`; the 64
two-step positives are exactly the same-rule chains). Construction
`k05_v5_work/k05_construct_v1.py`, run log `k05_v5_work/k05_v5_run.log`,
battery sha256 `5b385f0edfa035b28940f5dd982e0c69991a2ce6e0175e4c693073add26899f0`.
