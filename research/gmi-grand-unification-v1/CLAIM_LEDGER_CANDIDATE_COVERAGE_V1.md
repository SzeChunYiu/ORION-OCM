# Grand GMI Claim Ledger — Candidate-Universe Coverage V1

Status date: 2026-09-13. Additive to the Grand-GMI claim ledgers. Authority:
`CANDIDATE_UNIVERSE_COVERAGE_CORRECTION_V1.md`.

| ID | Claim | Status | Scope |
|---|---|---|---|
| CU1 | Because a family is the extension of a structural predicate, coverage of a population is validity of the disjunction of the registered predicates, with a terminating decision procedure for explicitly finite enumerable populations and total decidable predicates; infinite covers require a separate proof or restricted decision theory. | DEFINITION / THEOREM | finite decision / supplied sound proof |
| CU1a | Adjoining the complement predicate always completes a cover, so the binding question is whether every class in the cover carries a derived bound, not whether a cover exists. | THEOREM | registered class registry |
| CU1b | Finite complete enumeration plus total decidable predicates gives an exact coverage decision. Infinite covers may be certified by supplied sound proofs, but arbitrary universal coverage is undecidable by reduction from nonhalting. | THEOREM / BOUNDARY | finite decision and particular proof certificates |
| CU2 | Under a proved cover with PL-2 bounds, a construction strictly below every other class's bound is beaten by no member outside its selected class, built or unbuilt; same-class improvements remain possible. | THEOREM | proved bounded cover |
| CU3 | A verdict over classes that do not cover the population is not a claim about the population; it must be reported as `ROBUST_WITHIN_COVERED_CLASSES_WITH_OPEN_RESIDUE`. | THEOREM / REPORTING REQUIREMENT | incomplete covers |
| CU3b | Covered-class evidence alone does not generally determine the residue's costs or enlarged verdict: extensions preserving that evidence can give different certified outcomes; independent residue evidence remains usable. | THEOREM / NO-GO | uncovered residue |
| CU4 | A cover of components does not lift to a cover of composites, so coverage must be proved at the resolution at which the verdict is stated. | COUNTEREXAMPLE | composite morphologies |
| CU5 | A cover need not be a partition: a member of two classes obeys the stronger derived bound, so overlap never weakens a conclusion. | THEOREM | overlapping classes |

## Exact witness aggregate

- admitted allocations of the registered instance: `1344`;
- the two registered classes leave `1105` admitted allocations uncovered; adjoining the complement class covers every allocation in the grid, admitted or not;
- derived bounds over the completed cover: `L_NEURAL = 18`, `L_NON_NEURAL = 14`, `L_RESIDUE = 12`;
- a registered non-neural construction of cost `16` yields `NON_NEURAL` over the two registered classes and `UNDECIDED_FROM_CURRENT_EVIDENCE` over the completed cover; `19` admitted residue allocations cost strictly less than it, and `12` is attained;
- a residue construction attaining `12` is robustly selected, and none of the `239` admitted allocations outside its class beats it;
- an expensive exotic extension keeps the verdict while the full residue extension withdraws it, so evidence restricted to the initial classes does not decide between extensions;
- single-site predicates covering every site cost leave `896` two-site allocations uncovered when lifted by conjunction;
- `119` admitted allocations lie in two overlapping classes and all respect the stronger bound `18`;
- no enumeration of physical machines is claimed.

Terminal: `GRAND_GMI_CANDIDATE_UNIVERSE_COVERAGE_GREEN_AT_FINITE_SCOPE`.
Coverage is proved for one registered finite instance. A cover is only as
strong as its weakest derived bound, and completing a cover often withdraws a
verdict rather than confirming it.

## Scoped-decidability correction

CU1 does not decide arbitrary infinite universal quantification. For Phys=N,
sigma_M(n)=not-halted-within-n-steps is decidable pointwise, but coverage is
nonhalting. Eight bounded loop/late-halting controls establish finite-prefix
indistinguishability only. A supplied sound proof may certify a particular
infinite cover; automatic proof discovery is not promised.
The corrected output is GRAND_GMI_CANDIDATE_COVERAGE_RECEIPT_V2.json;
the existing V1 receipt is preserved byte-for-byte.
