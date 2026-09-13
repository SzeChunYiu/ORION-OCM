# Grand GMI Continual Semantic Retention Claims V1

Status date: 2026-09-12. Uses `CSR-*` identifiers independently of the moving master ledger.

| ID | Claim | Status | Scope |
|---|---|---|---|
| CSR-1 | Exact retention of all tasks across the past→future cut needs exactly one persistent state per joint retained semantic class: `M*=N_t`; binary width `ceil(log2 N_t)`. | THEOREM + 1,024 EXACT ENCODER CASES | finite zero-error, no side information |
| CSR-2 | Adding retained tasks can only refine the joint semantic partition; zero-growth tasks need no additional exact semantic capacity, positive-growth tasks do. | THEOREM + 12,816 EXACT PREFIX CHECKS | finite exact retained obligations |
| CSR-3 | Semantic task redundancy/transfer is `sum_i log2 N_i - log2 N_joint >= 0`; shared response structure compresses retained state relative to independent task storage. | THEOREM | exact response partitions |
| CSR-4 | Internal persistent state and replay/external side information obey the past→future cut bound `M*K >= N_t`; jointly designed channels attain it when the product alphabet is large enough. | THEOREM + 128 CAPACITY CASES | jointly designed zero-error channels |
| CSR-5 | If a deterministic update merges a retained obligation distinction across every surviving future channel, exact recovery is impossible without new distinguishing information. | DATA-PROCESSING THEOREM + 256 UPDATE MAPS | exact deterministic update |
| CSR-6 | Catastrophic forgetting separates into capacity-impossible, update-induced, and transfer/no-growth regimes. | DERIVED CLASSIFICATION | declared retained obligations/channels |

Aggregate terminal: `GRAND_GMI_CONTINUAL_RETENTION_TRANCHE_ALL_GREEN`.

No claim is made that `log2 N_t` is the physical bit cost on every substrate, nor that this theorem replaces optimization/sample-complexity analyses of particular continual-learning algorithms.