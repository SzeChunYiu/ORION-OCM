# gmi-833-h-family-tranche-b-v1 — CORE

**What this is.** A registered-scope evidence package for nine of the deep and
neural Section-H rows of issue #833. Every row is reported **open with a
single-stage attribution**; no row is closed, because the real-scale
coordinate (`R11`) could not be certified inside this freeze, and a closed row
requires all eleven coordinates at one scope.

## The nine rows and their registered single-stage attributions

| row | registered property | stage | lever |
|---|---|---|---|
| Feed-forward neural networks. | compositional nonlinear response without persistence | heldout_or_real_scale | complete the same frozen search at real scale |
| Backprop/reverse-mode credit assignment. | outer loss sensitivity propagated through a shared intermediate program | missing_channel | register the update-feedback channel and repeat the same grammar |
| CNN/equivariant local-weight-sharing systems. | one transform reused at translated sites | heldout_or_real_scale | complete the same frozen search at real scale |
| RNNs. | output depends on a held state | missing_channel | register the history/state channel and repeat the same grammar |
| LSTM/GRU-like gating. | selective state retention | missing_channel | register the history/state channel and repeat the same grammar |
| Attention mechanisms. | input-dependent selective rereading weighted by a data-derived score | heldout_or_real_scale | complete the same frozen search at real scale |
| Transformer-like dynamic routing/composition. | query-dependent composition of multiple source values | heldout_or_real_scale | complete the same frozen search at real scale |
| Graph neural/message-passing systems. | permutation-invariant aggregation of neighbor messages | missing_external_channel | register the neighbor-message channel and repeat the same grammar |
| Mixture-of-experts/routing systems. | sparse query-dependent activation of one of multiple transforms | heldout_or_real_scale | complete the same frozen search at real scale |

**State-space models. is not a row here.** The local package
`832-family-cluster-symbolic-ssm-retrieval-v1` owns it.

## Status

- 9 of 9 rows: finite-sided generic witness results, a shared neutral grammar
  digest, per-row single `sigma`, and a source-separated oracle agreement.
- 0 of 9 rows closed. `R11` is open on every row: the freeze registered a
  real-scale run on `billy-laptop` over the sha256-bound word source, and the
  receipt was not available inside this freeze.
- The claim ceiling is `REGISTERED_SCOPE_EVIDENCE_OPEN_WITH_EXPLICIT_SINGLE_STAGE_ATTRIBUTION`.

## Relationship to PR #946

PR #946 (`gmi-833-ai1-ai8-blind-neural-microscope-v1`) remains open and covers
a binary toy scope with D1–D3 claims that are not this package's scope. The
`OPEN_GAPS` artifact of that package names real-scale morphology and broad
CNN/RNN/attention/MoE recovery as outside its tranche. This package records
those rows as open with their single-stage attribution instead of extending a
toy certificate, which would be cross-scope composition.

## Reproduction

```
cd research/gmi-833-h-family-tranche-b-v1
python3 tranche_b_v1.py               # writes RESULT_V1.json
python3 -m unittest test_tranche_b_v1.py -v
python3 -O -m unittest test_tranche_b_v1.py -v
```
