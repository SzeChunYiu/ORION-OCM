# RC-09 — joint-envelope attainment scope correction

Date: 2026-09-12. This is an additive correction to this continuation's own RC-02 in `GMI_RECURSIVE_CLOSURE_CORRIGENDUM_V1.md`. The earlier text remains preserved. The inequality and finite matrix results are unchanged.

## Smallest failed atom

RC-02 says, without an explicit finiteness/attainment guard, that equality of joint and pointwise envelope values requires a feasible state attaining the required coordinates simultaneously. This statement is too strong for arbitrary infinite obligation and reachable-state sets. It is valid in the finite positive-weight case tested, but not as an unqualified extension.

Take obligations e=1,2,... with weights mu_e=2^(-e). Reachable state s_n succeeds exactly on obligations 1 through n. Every obligation can individually be satisfied, so the pointwise envelope is 1. Each state's breadth is `1-2^(-n)<1`, while the supremum of these breadths is also 1. The envelope values are equal, yet no state attains all obligations. This is an exact geometric-series counterexample to the unqualified implication, not a counterexample to the earlier finite matrix test or to a physical model that separately guarantees a finite feasible state set.

## Corrected theorem and proof

Always retain the proven inequality `B_joint <= B_pointwise` under a common feasible set and positive measure. Equality of these supremum values alone does not prove attainment.

For a FINITE obligation set with strictly positive weights and a nonempty common feasible state set, the finite set of possible binary success vectors guarantees a maximizing vector exists. Every feasible vector is coordinatewise bounded by the pointwise success vector. Equal weighted sums, with every weight positive, force equality in every coordinate. Thus equality holds iff one feasible state realizes the pointwise vector.

For an infinite obligation set, the same coordinatewise conclusion follows if attainment of the joint supremum is separately established; it does not follow merely from equality of values. Zero-weight obligations need separate hard constraints if they are required. This is the same infimum/supremum distinction highlighted for developmental burden in RC-03.

Terminal: exact counterexample and conditional corrected proof. No new empirical or family-level closure claim follows. The original stronger sentence is not relabeled as a passed prediction.

## Frozen fresh calibration before execution

Source `run_gmi_joint_attainment_v1.py` was committed at `e1580b3c7ca41f217ebb04684970ab9ab7f6ba46`, SHA-256 `078abf0e8bec25a21d232a029a20523b581325465729fc52351fc5a893a528b3`, before this run.

Registered successor cases: all 4,096 three-state/four-obligation binary success matrices, a zero-success fallback state, and all 16 strictly positive weight vectors in {1,2}^4: 65,536 finite equivalence checks. This is a new dimension/weight scope relative to the earlier 3x3/uniform checks. Separately check the exact geometric prefix identity at n=1..128. The infinite conclusion follows from the written geometric-series proof, not extrapolation from 128 finite examples.

Kill conditions: any finite positive-weight equivalence mismatch, any incorrect geometric identity, or a claim of infinite-set attainment without an additional assumption. The corresponding executable output is `GMI_JOINT_ENVELOPE_ATTAINMENT_RECEIPT_V1.json`. This paragraph and source are frozen before executing those checks. They are exact calibration, not a protected empirical holdout.

## Ledger effect

RC-02's inequality remains proved. Restrict its equality/attainment clause as above. RC-03 remains unchanged. Read this note alongside the V3 closure ledger and V2 capability ledger; neither should be interpreted as issuing unqualified attainment for infinite sets. All broad family, independent-encoding, real-transfer and GMI-specific discrimination blockers remain open. Both requested programme-wide terminal strings remain FALSE.
