# GMI #833 Section F — 116,570,467-candidate exact census freeze V1

Registered in issue #1008 before implementation or outcome execution.

## Target and dependency order

This tranche targets only the live Section F row **Scale to at least 10^8
candidates or justify an equivalent effective coverage method.** It chooses the
direct scale alternative. It will execute every candidate in the cumulative
`G0-fin-v1` budget `B=(5,1)`, not count virtual draws and not claim the
alternative effective-coverage route.

The branch is stacked on #1007 exact head
`3bf854f3282f239c831e7ec026291c4c8c72aae0`, which in turn depends on #1003.
Merge order is #1003, #1007, then this tranche. Dependency-refresh commits may
change custody pins but may not change this scientific protocol. #220/#221
remain read-only and authoritative for HPC/QD/open-ended morphology-zoo work.

## Frozen census

For register count one and label count `n`, the instruction alphabet has
`q_n=1+3n+n^2` members and the stratum has `q_n^n` candidates. The complete
cumulative census is:

| n | q_n | candidates |
|---:|---:|---:|
| 1 | 5 | 5 |
| 2 | 11 | 121 |
| 3 | 19 | 6,859 |
| 4 | 29 | 707,281 |
| 5 | 41 | 115,856,201 |
| **total** | | **116,570,467** |

Every local rank `0 <= ell < q_n^n` must be decoded into its `n`-instruction
table, validated, reranked, and processed exactly once. Because this is a
census, every first-order and every distinct-pair inclusion probability is
exactly one. No sampling estimator, confidence interval, fixed-seed randomness,
or extrapolation is used.

## Frozen protected evaluation

The interface is exactly `(), (0,), (1,)` at step cap 6, matching #1007. The
execution records the complete semantic multiplicity histogram, exact class
count, collapse count/rate, singleton and doubleton counts, and exact
inverse-Simpson effective semantic count

```text
N^2 / sum_c multiplicity(c)^2.
```

Those are exhaustive facts only for this finite grammar, budget, and protected
interface. “Effective” describes semantic diversity of this executed census;
it is not the row's alternative to execution and not semantic-universe
completeness.

## Execution, custody, and independent route

The primary route is a compiled exact-integer streaming executor. It may hold
the finite semantic histogram but may not materialize the candidate population.
Work is divided into atomic restartable rank chunks with canonical receipts and
a chained terminal digest. Each stratum must satisfy exact count, consecutive
rank, rank sum, rank-square sum, codec round-trip, semantic-total, and chunk
coverage gates.

A source-separated oracle may not import or parse the primary implementation.
It must exhaust every candidate at frozen small budgets `B=(1,1)` through
`B=(4,1)` and agree on candidate counts, rank/codec behavior, complete semantic
histograms, and exact effective-count arithmetic. The full run is additionally
checked against closed-form stratum counts and rank moments. This is an
independent small-scope algorithmic oracle plus full-scope structural
certificate, not a claim that a second 116-million semantic execution occurred.

Hostile tests must fail closed for a skipped or duplicated rank, instruction
ordering drift, altered interface, broken chunk continuity/chain, count or
histogram tamper, wrong effective-count denominator, incomplete stratum, and
forbidden universal promotion.

## Frozen resource ceilings and positive terminal

- wall time: 7,200 seconds;
- peak RSS: 8,589,934,592 bytes (8 GiB);
- persistent run artifacts: 2,147,483,648 bytes (2 GiB);
- committed evidence: 20,971,520 bytes (20 MiB).

A positive result requires exactly 116,570,467 decoded, validated, reranked,
and semantically evaluated candidates; five complete strata; all exact
structural, semantic, custody, independent-oracle, hostile, normal-test, and
optimized-test gates green; and all ceilings met. A failed attempt remains in
the ledger and is not reconciliation-eligible.

## Claim ceiling and forbidden promotions

Claim ceiling:
`GMI_833_116570467_CANDIDATE_EXACT_CENSUS_AT_REGISTERED_FINITE_SCOPE`.

Forbidden: unbounded generation; exhaustive coverage of all machines or all
semantics; 10^8 execution at `B=(8,4)`; a unique/unbiased grammar;
architecture-free-in-an-absolute-sense; grammar neutrality; physical
randomness; QD/open-ended search; family recovery; capability; real-scale
validation; complete GMI; or promotion of #1007 sample statistics to population
facts.

At this freeze the outcome is `NOT_RUN`.
