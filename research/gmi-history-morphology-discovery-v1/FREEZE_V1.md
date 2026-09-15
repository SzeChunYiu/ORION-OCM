# H unseen-morphology discovery from history — FREEZE V1

**Issue:** #602 H — `Demonstrate history improves unseen-morphology discovery, not merely warm-starting.`  
**Evidence target:** exact finite constructed demonstration.  
**Claim ceiling if successful:** `FINITE_HISTORY_INDUCED_MORPHOLOGY_SEARCH_PRIOR__NO_WARM_START__PARENT_OWNED`

This is an authored calibration, not a prospectively discovered natural law. The freeze exists to prevent changing the search arms, targets, controls, or success rule after execution.

## Morphology space

A morphology is a six-bit mask `m in {0,...,63}`. Bit `i` is `(m >> i) & 1` for `i=0..5`.

All arms search the **same complete 64-mask candidate space** and use the same exact equality verifier. Search cost is the 1-indexed proposal rank at which the target mask is first verified.

All arms begin from the identical current morphology `000000` (mask 0). The starting morphology is not used to seed or mutate candidates. Therefore any difference among arms can come only from proposal ordering, never from warm-start distance.

## Developmental history

The inherited successful morphology log is frozen as masks

`H = [36, 38, 52, 37]`.

The protected unseen targets are

`T = [39, 53]`.

Assert `H ∩ T = empty`. Historical masks remain in the candidate space and, if proposed before the target, are fully charged. This blocks a hidden solution-reuse discount.

## Three search arms

### RESET

No history-derived prior. All 64 masks have equal score and are proposed in numeric order `0..63`.

### CONTINUED

Learn only an independent per-bit proposal prior from `H`, with Laplace smoothing. For bit `i`, let `k_i` be the number of historical masks with that bit set and `N=|H|=4`. The exact unnormalized likelihood score for candidate `m` is

`score_H(m) = product_i [(k_i+1) if bit_i(m)=1 else (N-k_i+1)]`.

Candidates are proposed by decreasing exact integer score, then numeric mask as a frozen tie-breaker.

This is deliberately a search prior, not a stored candidate library or changed start state.

### SHUFFLED_HISTORY

Apply the frozen bit-position permutation

`pi = (3,4,5,0,1,2)`

to every historical mask before learning the same prior. This preserves the number of examples and each example's Hamming weight while breaking which structural coordinates history emphasizes. Candidate space, verifier, target set, start state and tie-breaker remain identical.

## Frozen success rule

The row is supported at this finite scope iff all are true:

1. every target is unseen: `H ∩ T = empty`;
2. all arms start from mask 0 and evaluate exactly the same 64 candidates;
3. mean CONTINUED discovery rank is strictly lower than mean RESET rank;
4. mean CONTINUED discovery rank is strictly lower than mean SHUFFLED_HISTORY rank;
5. historical masks proposed before an unseen target remain charged;
6. no arm changes the current morphology before proposal ranking begins.

Report every per-target rank; do not report only the mean.

## Parent subtraction

Bayesian/empirical search priors, meta-learning, learning-to-search, warm starts, evolutionary bias and algorithm configuration receive first refusal. A positive result demonstrates only that **history can alter a future morphology proposal distribution in a way that improves discovery of new morphologies**, with warm-start and direct solution reuse controlled away.

It does not establish universal positive transfer, open-ended morphogenesis, a new search algorithm, or #592 items 22/35.

## Falsifiers

Any of the following terminates negatively:

- a protected target appears in history;
- CONTINUED does not beat RESET on mean discovery rank;
- CONTINUED does not beat SHUFFLED_HISTORY on mean discovery rank;
- arms begin from different current morphologies;
- historical candidates are excluded or uncharged;
- target/candidate spaces differ by arm;
- the prior uses protected target identity or verifier outcomes.
