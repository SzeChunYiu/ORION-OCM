# One-million finite G0 candidate execution V1

## Result

The preregistered #1006 execution generated exactly **1,000,000 distinct validated candidate structures** from `M(G0-fin-v1,(8,4))`. The finite population has exactly `266545923745833839720` presentations. The frozen global SRSWOR transcript therefore gives every presentation exact first-order inclusion probability

```text
1,000,000 / 266,545,923,745,833,839,720
= 25,000 / 6,663,648,093,645,845,993.
```

Every selected rank was explicitly unranked to a `CandidateProgram`, validated, reranked exactly, and incorporated into a length-delimited candidate transcript. Rank uniqueness plus the independently checked rank/unrank bijection proves that all 1,000,000 canonical structures are distinct; this does not rest on hash collision assumptions.

## Custody and independent replay

The run emitted a sorted rank transcript, 100 receipts of 10,000 candidates, a chained terminal hash, and an atomic checkpoint. After a first implementation-only gate mismatch, a restart exact-replayed and validated all 100 completed chunks before accepting the result. The separate checker does not import the executor or #1003 codec: it independently reconstructs Floyd sampling, mixed-radix rank/unrank, G0 protected semantics, every candidate digest, all resource/semantic histograms, all chunk links, and the final checkpoint.

| Gate | Result |
|---|---:|
| Generated / unique / valid / exact round trips | 1,000,000 each |
| Completed chunks | 100 / 100 |
| Rank transcript SHA-256 | `0b3b4f7597e8dac9c494d6dfffdc412349d432255b163a567e1e0efa81f0fbe2` |
| Candidate-chunk digest transcript SHA-256 | `f6a293fbb8a7f138889189877988af32d3fa51b3b916413bf024c1c18302bfab` |
| Terminal chunk-chain SHA-256 | `c3a96b5b1dce3f2b9f70077961945ae88a8ebe0b3eb5e7d98c64f9adb7f54418` |
| Accepted replay wall / peak RSS | 22.752257 s / 207,159,296 bytes |
| Persistent run artifacts | 22,413,292 bytes |

The deterministic counter stream is only a replay adapter. Probability statements apply to the registered ideal uniform draw design, not to physical randomness.

## Registered sample diagnostics

The protected interface `(), (0,), (1,)` with step cap 6 yielded 600 observed semantic keys. There were 167 singleton and 84 doubleton keys; the presentation-to-observed-key collapse count was 999,400 (`4997/5000`). Semantic discovery reached 67, 178, 321, and 600 keys after 1,000, 10,000, 100,000, and 1,000,000 generated candidates. The inverse-Simpson effective semantic count was exactly `500000000000/158164266209`.

These are **sample diversity diagnostics only**. They are not an estimator promoted to exact semantic-universe coverage. The global candidate-uniform design observed 7 of 32 resource strata because the finite population is overwhelmingly concentrated in its largest strata; all 32 zero/nonzero counts and exact ideal proportions are retained in `RESULT_V1.json`.

## Recorded recursive repair

Attempt 1 completed the full generation but the executor refused to emit a result because its code mistakenly imposed “all 32 strata observed” as a terminal gate. The frozen protocol required measurement of stratum coverage, not guaranteed representation; #1003 explicitly distinguishes global SRSWOR from positive stratification. `ATTEMPT_LEDGER_V1.json` preserves that failure. The repair removed only the unfrozen gate, changed neither protocol nor draw/candidate transcript, and required exact replay of every completed chunk before acceptance.

## Boundary

This closes only the registered million-candidate execution row. It does not claim 10^8 generation or equivalent coverage, unbounded or exhaustive coverage, exact coverage of a semantic universe, an unbiased/unique grammar, absolute architecture freedom, QD/open-ended search, family recovery, capability, or real-scale validation. Issues #220/#221 remain untouched.
