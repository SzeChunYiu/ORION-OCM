# CORE — trained syntax donor, development receipt

The adopted non-Transformer UDPipe1 donor produced one valid tree for every main-panel sentence. This is a supervised syntax qualification receipt; it carries no protected, LLM-comparability, ME-residual, communication or efficiency claim.

| Frozen development group | Valid | Base LAS | Full LAS | Exact tree | Exact tree + UPOS |
|---|---:|---:|---:|---:|---:|
| All-token panel 100 | 100/100 | 1234/1584 (77.904%) | 1231/1584 (77.715%) | 32/100 | 30/100 |
| All-token prefix 50 | 50/50 | 934/1166 (80.103%) | 932/1166 (79.931%) | 8/50 | 7/50 |
| Legacy panel 100 | 98/100 | 972/1389 (69.978%) | 970/1389 (69.834%) | 25/100 | 20/100 |
| Legacy prefix 50 | 49/50 | 764/1016 (75.197%) | 758/1016 (74.606%) | 7/50 | 4/50 |

Across 290 requests: 287 valid predictions and three predeclared empty-input abstentions; no malformed predicted trees or model errors. All 287 applicable official metric cross-checks passed. Group membership overlaps; do not sum the four group denominators as independent cases.

The main contract supplies gold token boundaries and preserves case/punctuation. Full TRAIN annotations teach the model; prediction receives forms only, with private gold scored externally. Five panel sentences duplicate normalized TRAIN surfaces; the retained nonduplicate 95 diagnostic has base LAS 1218/1568 and exact 27/95. The balanced public development panel is neither a natural-frequency population estimate nor a protected LLM contamination test.

The first 1,800-second attempt timed out. The authorized checkpointed repeat completed in 4,541.546 seconds. Both attempts remain charged: 6,341.580 seconds wall, 6,338.311 + 1.936 seconds CPU, peak 893,304 KiB. The 290-request predictor took 1.930 seconds wall including 0.678 seconds model load; shared-host overlap prevents a controlled efficiency claim.

Final model: 11,631,918 B; SHA256 **7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9**. The binary is deliberately external. [Training provenance](training-manifest.json) preserves both attempts, checkpoint, software, teacher source and actual model identity.

- [Replay and path relocation](REPLAY.md): original scripts remain byte-identical.
- [Attribution and licensing records](ATTRIBUTION.md).
- [Raw scores](evaluation-summary.json), [per-request scores](scores.jsonl), [predictions](responses.jsonl).
- [Costs](cost-accounting.json) and [actual timing overlap](timing-overlap.json).
- [Diagnostic clarification](projectivity-diagnostic-clarification.json): the legacy crossing-arc helper is not full-token projectivity; it never excludes rows.
- [Portable source mapping](portable-copy-manifest.json) and [SHA256 inventory](SHA256SUMS).

Owners: #43/#52/#73, anchored to #50/#62/#42; classification PAPER_CRITICAL engineering qualification. Root owns the separately frozen native/OCM matched stream.
