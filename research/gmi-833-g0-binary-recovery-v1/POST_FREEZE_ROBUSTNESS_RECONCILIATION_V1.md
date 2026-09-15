# Post-freeze reconciliation to #863 derivation robustness controls

The scientific target for this tranche was frozen at commit `302ad7fed43b0e310b6e22252ceb21260edd865b`, whose base was main `5acf80fe6505a72d6878ed754783ba25aecbaa82`.

While implementation was in progress, concurrent #833 work merged PR #863 as main `497977a071f33a824628332caf1ccc44e077f924`, adding a general requirement that architecture-uncommitted derivation experiments carry four explicit robustness controls:

1. matched mechanism-removal grammar twin;
2. semantic remint / alternate encoding;
3. materially distinct alternate search algorithms under a comparable budget frame;
4. raw Pareto analysis plus alternate strictly-positive scalarizations.

This tranche does not rewrite its frozen theorem target after seeing results. Instead it adds an **independent post-freeze governance application** using the merged #863 implementation itself.

## Applied controls

### R1 matched grammar negative

The positive candidate universe has 260 semantic candidates. The predicted mechanism coordinate is persistent state (`state_bits=1`). The negative grammar removes all 256 stateful candidates and retains exactly the same four stateless candidate semantics, gate counts, ecology, evaluator, declared budget and stopping semantics. The #863 parent audit verifies exact equality of the mechanism-free background-signature multiset.

### R2 alternate semantic encoding

The NAND and NOR candidate surfaces are independently numbered, then projected to the canonical semantic tuple `(state_bits,next_truth,output_truth)`. Each side contains exactly one surface representative for each of the same 260 canonical semantic classes. The bijection is defined by equal canonical semantics, and the recovered result is compared only after this projection.

### R3 materially distinct search algorithms

The original complete enumeration is compared with an independently implemented resource-ordered branch-and-bound search. Both use the same exact evaluator/objective and the same declared maximum budget of 260 candidate evaluations. Branch-and-bound uses exact resource dominance as its admissible pruning condition.

At the frozen instances it evaluates:

- `DELAY1`: 8 candidates, prunes 252;
- `IDENTITY`: 1 candidate, prunes 259.

It returns the same canonical Pareto winner as complete enumeration in both NAND and NOR grammars.

### R4 Pareto and alternate scalarizations

Raw resource vectors `(state_bits,gate_count)` remain primary. The #863 audit additionally checks strictly-positive weights `(1,1)`, `(3,1)` and `(1,3)` over the exact-solution sets. All registered weights return the same unique Pareto winner on both ecologies and both grammars.

This finite sampled agreement does not imply universal price invariance; that forbidden promotion is inherited from #863.

## Result

`ROBUSTNESS_RESULT_V1.json` is produced by invoking the merged `gmi-833-robustness-controls-v1` implementation, not by copying its expected labels locally.

All four runs (`DELAY1_NAND`, `DELAY1_NOR`, `IDENTITY_NAND`, `IDENTITY_NOR`) must return:

`CONTROL_REQUIREMENTS_SATISFIED`

and

`ROBUST_AT_REGISTERED_CONTROLS`.

Failure or sensitivity in any registered control prevents this tranche from merging GREEN; it is not papered over as a missing-control exception.
