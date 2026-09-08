# E150 V1 protected abort receipt

Status: **CANNOT_CHECK / INVALID_CONFIRMATORY_RUN**

The V1 protected execution was started only after the frozen protocol and implementation were committed. During a code-vs-protocol audit while that execution was still running, before any protected result file existed or any protected outcome was read, a mismatch was found:

- `PROTECTED_PROTOCOL_V1.md` grants the strongest incremental symbolic parent exact episodic memory plus local invalidation.
- the committed V1 `SymbolicIncremental` implementation retained its learned antichain but did not retain the exact episodic stream.

This weakens a frozen strongest parent. Under issue #144, the run cannot be repaired in place after protected execution has begun. The worker process was terminated; `/mnt/data/orion-ocm-evolvability-independent/protected_factorization_v1.json` did not exist at termination and no V1 protected result was inspected.

V1 protected seeds `9001..9040` are treated as burned and will not be reused for confirmatory V2. V1 protocol and implementation commits remain preserved. V2 must use new seeds and must include both (a) an exact-memory incremental symbolic parent and (b) a compact symbolic factor parent so that an OCM residual cannot be manufactured by forcing a parent to pay unnecessary episodic-storage cost.

Terminal: `CANNOT_CHECK_PROTOCOL_IMPLEMENTATION_MISMATCH`.
