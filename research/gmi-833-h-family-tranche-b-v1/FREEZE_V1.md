# Section H family tranche B: deep and neural rows

This freeze records the registered scope before any executor or outcome file.
The package covers exactly these nine rows:

- Feed-forward neural networks.
- Backprop/reverse-mode credit assignment.
- CNN/equivariant local-weight-sharing systems.
- RNNs.
- LSTM/GRU-like gating.
- Attention mechanisms.
- Transformer-like dynamic routing/composition.
- Graph neural/message-passing systems.
- Mixture-of-experts/routing systems.

State-space models are intentionally excluded. A separate local package
`research/833-family-cluster-symbolic-ssm-retrieval-v1` owns that row.

## Scope

Every row uses one shared neutral grammar `G_HB`: scalar leaves ARG, PARAM,
ACC, STATE, QUERY, CONTEXT, and BIAS; generic operations ADD, MUL, NEG, ABS,
STEP, RECIP; and generic indexed accumulation plus an optional delay cell.
The generator receives no row names, family labels, architecture macros, or
family-specific candidate menus. Structural labels are assigned only after a
candidate is selected.

The protected property contracts are frozen as follows:

| row | property predicted before outcome |
|---|---|
| Feed-forward neural networks. | compositional nonlinear response without persistence |
| Backprop/reverse-mode credit assignment. | outer loss sensitivity propagated through a shared intermediate program |
| CNN/equivariant local-weight-sharing systems. | one transform reused at translated sites |
| RNNs. | output depends on an earlier state when the current input is held fixed |
| LSTM/GRU-like gating. | state update selectively retains or replaces prior state |
| Attention mechanisms. | input-dependent selective rereading weighted by a data-derived score |
| Transformer-like dynamic routing/composition. | query-dependent composition of multiple source values |
| Graph neural/message-passing systems. | permutation-invariant aggregation of neighbor messages |
| Mixture-of-experts/routing systems. | sparse query-dependent activation of one of multiple transforms |

## Eleven coordinates

Each result row must carry R01 through R11 at one and the same scope. The
coordinates are: frozen property prediction; shared grammar; no family macro;
family-blind recovery; matched negative control; lower bound; resource-price
crossover; disjoint held-out prediction; independent regeneration;
source-separated search; and real-scale evidence (`n_fit >= 100000`,
`n_held >= 20000`, sha256-bound real source, exact held-out arithmetic).
Certificates from another package or scope cannot be combined with these.

## Real-scale attempt and stopping rule

A real-scale run was registered for the query-dependent routing contract using
the sha256-bound Debian word source on `billy-laptop`. This package contains no
receipt for that run because the source image and run completion were not
available at freeze time. The checker therefore reports R11 OPEN and refuses
all row closure. No number is inferred from a finite toy run.

A failed prediction is retained with one stage attribution and one prescribed
lever. The current tranche records the following registered next steps:

- feed-forward, local sharing, attention, transformer routing, and sparse
  routing: stage `heldout_or_real_scale`; lever `complete_the_same_registered_query_or_real_source_run`.
- reverse credit, recurrent state, and gated state: stage `missing_channel`; lever `register_state_or_update_feedback_and_repeat_the_same_grammar`.
- graph message passing: stage `missing_external_channel`; lever `register_neighbor_message_and_repeat_the_same_grammar`.

These are open outcomes, not family-level impossibility claims.

## Claim ceiling

Allowed claim: `REGISTERED_SCOPE_EVIDENCE_OPEN_WITH_EXPLICIT_SINGLE_STAGE_ATTRIBUTION`.
Forbidden claims include row closure, universal family recovery, real-scale
validation without a receipt, independent-team replication, and any
cross-scope gate composition.
