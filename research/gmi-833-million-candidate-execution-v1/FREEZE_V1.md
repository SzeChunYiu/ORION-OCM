# GMI #833 Section F — million-candidate execution freeze V1

Registered in issue #1006 before outcome generation.

This tranche targets only **Generate at least 10^6 architecture-neutral candidates**. It is stacked on the exact unmerged #1003 head `05d13723b519d9de94f15b142cca0827d3725d6f`; #1003 must merge first. The #220/#221 HPC/QD programme is read-only and remains authoritative for open-ended morphology-zoo work.

The frozen execution uses `G0-fin-v1`, budget `(8,4)`, #1003 exact global Floyd SRSWOR, its deterministic replay adapter with the registered seed, and exactly 1,000,000 ranks. Every counted candidate must be unranked, validated, reranked to its source rank, and incorporated into the canonical-code transcript.

The semantic audit is fixed to protected inputs `(), (0,), (1,)` and step cap 6. It records observed semantic-key count, collapse, multiplicities, singleton/doubleton counts, discovery checkpoints, and inverse-Simpson effective semantic count. These are sample statistics, not exact coverage of an unknown semantic universe.

Execution has two restartable phases: an fsynced sorted decimal rank transcript, then 100 atomic 10,000-candidate chunks. Every chunk has a canonical receipt and chained hash; restart validates the configuration, dependency, transcript, and completed receipts and resumes only on a whole-chunk boundary.

Resource ceilings are 30 minutes wall time, 2 GiB peak RSS, 512 MiB persistent run artifacts, and 10 MiB committed evidence. A positive result requires exactly 1,000,000 unique ranks and canonical structures, validation and round-trip success for all, all chunks, hashes, restart checks, independent checks, normal and optimized tests, and every ceiling.

Claim ceiling: `GMI_833_ONE_MILLION_DISTINCT_G0_CANDIDATES_GENERATED_AT_REGISTERED_FINITE_SCOPE`.

Forbidden: 10^8 generation; 10^8-equivalent coverage; unbounded/exhaustive/semantic-universe coverage; a unique or unbiased grammar; absolute architecture-freedom; physical randomness; QD/open-ended search; family recovery; capability; real-scale validation; complete GMI.

At registration the outcome status is `NOT_RUN`.
