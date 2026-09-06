# Saved induction readout

| Quantity | Observed |
|---|---|
| Imported TRAIN programs | 2: max3, mpg_guard2 |
| Stitch compress invocations | 1 |
| Proposed abstractions | 1 |
| Typed macro | fn_0: (Int, Int) -> Int |
| Body | (+ #1 (* (- 1) #0)) |
| Rewritten macro occurrences | 4 in max3; 1 in mpg_guard2 |
| Native Z3 invocations | 4, all PASS / unsat |
| Dedicated primitive-alias check | NOT_RUN |
| Later synthesis/use, persistence, useful new operator | NOT_RUN / NOT_ESTABLISHED |

[Actual donor response](raw/capture-v1/calls/compress-return.json) ·
[adapter response](raw/capture-v1/calls/adapter-return.json) ·
[caller receipt](raw/capture-v1/calls/caller-receipt.json).

The source-level algebra is fn_0(h0,h1) = h1 + (-1 * h0) = h1 - h0.
It abbreviates an existing primitive. This interpretation does not rewrite the
raw NOT_RUN alias-assessment field or substitute a new solver result.

## Four executed obligations

| Raw pair | Obligation | Native result |
|---|---|---|
| verify-00 | original max3 public specification | PASS / unsat |
| verify-01 | original mpg_guard2 public specification | PASS / unsat |
| verify-02 | max3 original versus decoded expanded rewrite | PASS / unsat |
| verify-03 | mpg_guard2 original versus decoded expanded rewrite | PASS / unsat |

Each request and result is retained in [calls](raw/capture-v1/calls/).
The envelope remained 5,000 ms native / 10 s external per check. No dedicated
macro-alias check or new post-hoc check was executed.

## Descriptive resources

The donor reports original_cost=6872, final_cost=5357 and
compression_ratio=1.2828075415344409 under its fixed weighted syntax objective.
These are not measured execution savings.

The actual capture receipt records supervisor wall including pre/post binding
0.6035579619929194 s; the bounded case records 0.364938736 s.
Caller self wall is 0.31185443099820986 s and self CPU 0.037956472 s.
Native child envelopes and self metrics remain separately in each result.
Do not sum these overlapping scopes or interpret them as whole-tree cost.

[Capture receipt](raw/capture-v1/receipt.json) ·
[root completion metadata](raw/root-launch-v1/completed.json).
All four native checker PIDs were absent on the earlier evidence review.
