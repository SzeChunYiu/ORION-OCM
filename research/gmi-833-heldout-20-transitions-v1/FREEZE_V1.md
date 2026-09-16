# GMI #833 held-out 20-transition validation v1 — freeze

Parent: #833 Section J. Child: #901.  
Base main: `831e63bd458f979137ffae67a1fc6a105fae870f`.

This file freezes all scientific predictions **before any outcome-oracle/search implementation for this tranche exists**.

## Registered finite ecology

Each evaluation episode is a length-3 binary sequence. A protected mode bit `M` is visible to the candidate:

- `M=0`: at scored times `t=1,2`, target output is current bit `x_t`;
- `M=1`: at scored times `t=1,2`, target output is previous bit `x_{t-1}`.

All 8 binary sequences are enumerated exactly. Mode `M=1` has registered prevalence `p`; `M=0` has prevalence `1-p`.

A candidate's exact objective is

`J = eta * [(1-p) * error_now + p * error_delay] + lambda * state_bits`,

where errors are exact mean 0/1 loss over the protected sequence/mode cells and `lambda>0` is the frozen price of one persistent state bit. No architecture/family label enters the objective.

## Candidate universe frozen abstractly

The outcome experiment must enumerate exactly:

- every stateless binary output table on visible `(M,X)` — 16 semantics;
- every one-bit persistent-state transducer whose next-state table is an arbitrary binary function of `(S,M,X)` and whose output table is an arbitrary binary function of `(S,M,X)` — `256*256 = 65,536` semantics;
- total candidate universe: 65,552 semantics.

Initial state is `S=0`. Candidate identifiers and enumeration order are scientifically irrelevant. The evaluator sees behavior and `state_bits`, not a morphology/family name.

## Pre-outcome derivation

For the visible immediate mode, a stateless candidate can be exact by outputting `X`.

For the delayed mode, at each scored time the previous bit is independent uniform conditional on current `X`; therefore every stateless predictor incurs minimum exact error `1/2` on the delayed cells. Because `M` is visible, one stateless table can simultaneously achieve

`error_now=0`, `error_delay=1/2`.

A one-bit persistent transducer can achieve zero error in both modes by carrying the previous bit. Hence the predicted best property-level objective values are

`J_stateless = eta*p/2`,

`J_stateful = lambda`.

The exact predicted phase boundary is therefore

`lambda* = eta*p/2`.

Predictions:

- if `lambda < lambda*`: selected property is `PERSISTENT_STATE`;
- if `lambda > lambda*`: selected property is `STATELESS`;
- equality is a tie and is not used in the held-out cases.

This derivation is frozen before search and does not use any post-search phenotype.

## Twenty held-out transition cases

Each row is one transition: only `lambda` changes from `lambda_low` to `lambda_high`; `p`, `eta`, task, candidate universe and evaluator stay fixed. Every row predicts `PERSISTENT_STATE -> STATELESS`.

| case | p | eta | lambda* | lambda_low | lambda_high | frozen prediction |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 1/5 | 1 | 1/10 | 1/20 | 3/20 | PERSISTENT_STATE -> STATELESS |
| 2 | 1/5 | 2 | 1/5 | 1/10 | 3/10 | PERSISTENT_STATE -> STATELESS |
| 3 | 1/5 | 3 | 3/10 | 3/20 | 9/20 | PERSISTENT_STATE -> STATELESS |
| 4 | 1/5 | 4 | 2/5 | 1/5 | 3/5 | PERSISTENT_STATE -> STATELESS |
| 5 | 2/5 | 1 | 1/5 | 1/10 | 3/10 | PERSISTENT_STATE -> STATELESS |
| 6 | 2/5 | 2 | 2/5 | 1/5 | 3/5 | PERSISTENT_STATE -> STATELESS |
| 7 | 2/5 | 3 | 3/5 | 3/10 | 9/10 | PERSISTENT_STATE -> STATELESS |
| 8 | 2/5 | 4 | 4/5 | 2/5 | 6/5 | PERSISTENT_STATE -> STATELESS |
| 9 | 3/5 | 1 | 3/10 | 3/20 | 9/20 | PERSISTENT_STATE -> STATELESS |
| 10 | 3/5 | 2 | 3/5 | 3/10 | 9/10 | PERSISTENT_STATE -> STATELESS |
| 11 | 3/5 | 3 | 9/10 | 9/20 | 27/20 | PERSISTENT_STATE -> STATELESS |
| 12 | 3/5 | 4 | 6/5 | 3/5 | 9/5 | PERSISTENT_STATE -> STATELESS |
| 13 | 4/5 | 1 | 2/5 | 1/5 | 3/5 | PERSISTENT_STATE -> STATELESS |
| 14 | 4/5 | 2 | 4/5 | 2/5 | 6/5 | PERSISTENT_STATE -> STATELESS |
| 15 | 4/5 | 3 | 6/5 | 3/5 | 9/5 | PERSISTENT_STATE -> STATELESS |
| 16 | 4/5 | 4 | 8/5 | 4/5 | 12/5 | PERSISTENT_STATE -> STATELESS |
| 17 | 1 | 1 | 1/2 | 1/4 | 3/4 | PERSISTENT_STATE -> STATELESS |
| 18 | 1 | 2 | 1 | 1/2 | 3/2 | PERSISTENT_STATE -> STATELESS |
| 19 | 1 | 3 | 3/2 | 3/4 | 9/4 | PERSISTENT_STATE -> STATELESS |
| 20 | 1 | 4 | 2 | 1 | 3 | PERSISTENT_STATE -> STATELESS |

These rows are held out from prior calibration packages and are not to be edited after the outcome oracle is added. A wrong row remains a scientific RED.

## Independent search replication requirement

Two materially distinct search implementations must operate on the same candidate universe, exact objective and full candidate budget:

1. `FULL_ENUMERATION`: score every candidate and return the complete exact argmin set.
2. `RISK_FRONTIER_BRANCH_BOUND`: independently construct candidate risk/state summaries, retain only objective-relevant nondominated summaries, use a valid lower bound to prune summaries that cannot beat the incumbent, and return the complete exact argmin property set.

They must not call one another or share winner-selection code. Agreement is required on all 40 endpoint worlds (20 low-price + 20 high-price). Search-procedure names are disclosed only for robustness auditing; phenotype classification occurs after scoring.

## Required controls

- verify the 16 + 65,536 = 65,552 candidate census;
- independently prove/measure minimum stateless delayed error is exactly `1/2`;
- verify at least one one-bit candidate has `(error_now,error_delay)=(0,0)`;
- freeze and check exact objective arithmetic with `Fraction`, no floating point;
- outcome search must never receive `PERSISTENT_STATE`/`STATELESS` as candidate identifiers;
- neutral surface remint of candidate IDs must not change endpoint property winners;
- boundary twin at `lambda=lambda*` must preserve both property classes as a tie;
- an intentionally incorrect shifted threshold must fail at least one held-out endpoint.

## Claim ceiling

If and only if every frozen row is correct and both independent searchers agree under all controls:

`GMI_20_HELDOUT_BINARY_MORPHOLOGY_TRANSITIONS_AND_INDEPENDENT_SEARCH_REPLICATION_AT_REGISTERED_FINITE_SCOPE`

Forbidden promotions:

- `REAL_SYSTEM_MORPHOLOGY_TRANSITIONS_VALIDATED`
- `UNIVERSAL_MORPHOLOGY_PHASE_LAW`
- `ALL_KNOWN_FORMS_PREDICTED`
- `COMPLETE_GMI`
