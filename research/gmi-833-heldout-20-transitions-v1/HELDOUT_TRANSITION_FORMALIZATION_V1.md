# GMI #833 prospective held-out morphology transition validation v1

**Issue:** #901, child of #833 Section J  
**Prediction freeze:** `FREEZE_V1.md`, commit `ddb3df7a44a6a4fb47fdc362a1fa02e34b7a3a75`  
**Claim ceiling:** `GMI_20_HELDOUT_BINARY_MORPHOLOGY_TRANSITIONS_AND_INDEPENDENT_SEARCH_REPLICATION_AT_REGISTERED_FINITE_SCOPE`

## 1. Temporal separation

The freeze commit contains the complete candidate-universe contract, exact objective, analytic threshold law, all 20 held-out `(p,eta,lambda_low,lambda_high)` cases, and the predicted property transition for each case. The two outcome-search implementations and the scored receipt were created only in descendant commits.

Therefore a wrong held-out prediction cannot be repaired by changing the frozen cases without breaking custody.

## 2. Architecture-name-free candidate universe

The outcome oracle enumerates all 65,552 registered finite binary mechanisms:

- 16 stateless output tables on visible `(M,X)`;
- 65,536 one-bit stateful transducers from all 256 next-state truth tables and all 256 output truth tables on `(S,M,X)`.

The search engines see only opaque candidate IDs or behavior/risk summaries. `STATELESS` and `PERSISTENT_STATE` are post-search classifications from the `state_bits` field; they are not candidate names or search operators.

## 3. Frozen transition law

At scored times, immediate-mode target is `X`; delayed-mode target is the previous bit. Because current and previous bits are independent uniform over the complete binary sequence frame, every stateless delayed predictor has minimum error `1/2`, while the visible mode bit allows simultaneous zero error on immediate mode. Hence the best stateless objective is

`J0 = eta*p/2`.

One persistent bit can carry the previous bit and attain zero behavioral error, giving

`J1 = lambda`.

Thus the property-level boundary is

`lambda* = eta*p/2`.

This derivation predates outcome enumeration.

## 4. Held-out evidence

The frozen 5×4 grid gives 20 transitions. Each keeps `(p,eta)` fixed and changes only persistent-state price from `lambda_low=lambda*/2` to `lambda_high=3lambda*/2`.

Required result per case:

`PERSISTENT_STATE -> STATELESS`.

The receipt records 20/20 transition predictions and 40/40 endpoint property predictions. Exact `lambda=lambda*` controls preserve both property classes as ties rather than forcing a winner.

An intentionally wrong boundary `2*lambda*` predicts the high endpoint incorrectly in all 20 cases, so the test is capable of falsifying a shifted phase law.

## 5. Independent search-procedure replication

Two materially distinct implementations operate under the same exact objective and declared full candidate budget 65,552:

1. **Full enumeration** reconstructs and scores every raw semantic candidate.
2. **Risk-frontier branch-and-bound** independently reconstructs the raw semantics, compresses them to `(state_bits,error_now,error_delay)` equivalence points, and prunes points only when the nonnegative-error lower bound `lambda*state_bits` already exceeds the incumbent.

They are source-separated and do not import or invoke one another. Their independently reconstructed raw risk histograms must agree exactly before transition evidence is accepted. The final outcome must agree on all 40 held-out endpoints and all 20 boundary ties.

This is replication across search procedures, not independent-team replication or real-system validation.

## 6. Controls

The exact package requires:

- raw candidate census 65,552;
- independently reconstructed risk histogram equality;
- exactly 146 distinct risk/state summaries;
- stateless minimum delayed error exactly `8/16=1/2`;
- a stateless `(error_now,error_delay)=(0,1/2)` witness;
- a one-bit `(0,0)` risk witness;
- neutral candidate-ID remint invariance on all 40 endpoints;
- 20 exact boundary ties;
- 20/20 failures of the deliberately shifted threshold;
- actual branch-bound pruning;
- no floating-point scoring.

## 7. Claim boundary

If all frozen predictions and controls are GREEN, this tranche licenses only a bounded M4-style statement: the previously derived morphology-selection law prospectively predicts 20 fresh binary finite-transducer transitions, and the transition property replicates across two materially distinct exact search procedures.

It does **not** license real-system transition validation, universal morphology prediction, all-known-form recovery, or complete GMI. The Section-J row requiring at least five real-system transitions remains open unless external/real-system evidence is supplied.
