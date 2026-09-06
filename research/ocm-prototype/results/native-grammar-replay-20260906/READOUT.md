# Five assigned rows, two fixed-checker passes

| Capture / assigned route | Exit | Existing checker | Native Z3 calls |
|---|---:|---|---:|
| Original: implicit primitive | 0 | PASS / unsat | 1 |
| Original: explicit primitive | 124 | CANNOT_CHECK | 0 |
| Original: printed-grammar replay | 124 | CANNOT_CHECK | 0 |
| SI successor: implicit primitive | 0 | PASS / unsat | 1 |
| SI successor: printed grammar + SI all / strict rcons | 124 | CANNOT_CHECK | 0 |

[Original checks](raw/checks-v1.json) ·
[SI checks](raw/single-invocation-successor/checks-v1.json).
Both implicit candidates satisfy the unchanged original grammar/spec checker.
Every timed-out route has empty stdout and stderr and no candidate check.
There is no timeout counterexample or evidence of impossibility.
The repeated implicit success is a development control, not two independent
learning trials. Both raw captures remain NOT_GRADED.

## Exact saved boundaries

| Capture / route | Bounded process wall, seconds |
|---|---:|
| Original implicit | 0.114259538 |
| Original explicit | 20.016181008 |
| Original replay | 20.015432911 |
| SI implicit | 0.114270553 |
| SI explicit | 20.014200656 |

Original capture runs 16:01:53–16:02:34 UTC; its checker runs at 16:03:33.
SI capture runs 16:27:34–16:27:54; its checker runs at 16:30:30.
These are separate serial registered calls, not a paired performance study.
The checker receipts retain self CPU/RSS and external envelopes. Their scopes
overlap; do not sum them into a complete process-tree or lifetime estimate.

[Original root completion](raw/root-launch-v1/completed.json) ·
[original checker completion](raw/root-checker-v1/completed.json) ·
[SI root completion](raw/single-invocation-successor/root-launch-v1/completed.json) ·
[SI checker completion](raw/single-invocation-successor/root-checker-v1/completed.json).
Recorded process/checker PIDs were absent at the read-only outcome review.

Both proposed interface repairs failed to return a candidate within this
envelope. The strongest implicit parent stays visible. A future remedy must
retain these outcomes and independently register its changed mechanism.
