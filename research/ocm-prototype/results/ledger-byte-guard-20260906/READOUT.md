# Recorded-storage engineering result

The exact-byte guarded validation memoization passed the fixed component admission rule.
This is a storage implementation result, not a new cognitive mechanism or paper-level capability claim.
ADAPT: existing flock/CAS/atomic-replace ledger and full-chain validator.
ADOPT: stdlib immutable bytes, pytest and process/resource facilities as infrastructure.
The unchanged conventional ledger is the faithful implementation comparator.

## Frozen comparison

The plan was registered before the seven-pair benchmark:
[exact freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/70#issuecomment-5558047208),
[result](https://github.com/SzeChunYiu/ORION-OCM/issues/70#issuecomment-5558090820).
Existing exact-stream functional controls were disclosed, not represented as unseen measurements.
Plan SHA256: b7454508e02cb0ded11f44bfb64436e6cd574971558206bf3298d296e589b99a.

Baseline commit 53d404f56140386f43d591cc8697cdf6be7669a1; candidate 4408d7c993fd8a331c192eea562f35234709e58a.
Their 163-file production source maps differ only in src/ocm/store/ledger.py.
Each fresh process copied the exact 502-row prefix, fully validated it, appended the fifteen
original inputs in groups 4/9/2, and fully validated the exact 517-row final ledger.
The real recorded timestamps, payloads, CAS heads and hashes were unchanged.
This component replay executed no cognition, solver, model or runtime application.

Seven complete pairs used fixed AB/BA alternation. All fourteen succeeded and are retained.
The primary median of per-pair candidate/baseline nine-append wall ratios was 0.17535583136824448
(82.46% lower), satisfying <=0.80. The corresponding complete-stream ratio was
0.3212654490593135 (67.87% lower), satisfying <1.0. No case was excluded or retried.
This is a practical engineering threshold, not a significance estimate.

## Descriptive costs

| Phase | Baseline median wall s | Candidate median wall s |
|---|---:|---:|
| Input/source binding, separately charged | 0.036424 | 0.036611 |
| Fresh prefix copy, separately charged | 0.001527 | 0.001548 |
| Initial full validation | 0.045090 | 0.045598 |
| Four binding appends | 0.207613 | 0.085310 |
| Nine query appends | 0.479952 | 0.083587 |
| Two explicit persist appends | 0.107221 | 0.019657 |
| Final full validation | 0.048614 | 0.048864 |
| Complete storage stream | 0.890326 | 0.284901 |

Complete stream includes constructor/setup, both public full validations, all fifteen appends
and final byte equality. It excludes prefix copying, source/input custody, outer process
startup and archive/qualification work. Phase medians do not sum to a median total.
Complete-stream median self CPU was 0.800643/0.200067 s (baseline/candidate).
Across seven cases, outer wall totals were 7.823438/3.613098 s; direct wait4 CPU totals
7.170111/2.978849 s. The outer supervisor observed 11.581534 s wall and 10.333968 s
wait4 CPU; these nested scopes must not be summed. Whole-process-tree CPU is not claimed.
All raw rusage observations and per-case host load are retained.

Candidate retained content is 4,608,991 bytes (4,609,221 shallow bytes including tuple/head/count).
Peak RSS was 67,428–67,576 KiB versus baseline 54,428–54,588 KiB.
Final durable state is 4,608,991 bytes in each case. Setup/cache/state costs remain visible.
Source-derived read/compare/rewrite work is tabulated in the frozen plan; it is not measured
physical IO. Both arms keep whole-history reads and whole-file atomic rewrites.
OS block counters are retained without converting them into physical disk or energy claims.
Page cache was not cleared; this is one shared laptop, CPU 0, fresh processes/paths,
4 GiB address bound, 120 s per case. No history-size scaling or active-k inference follows.

## Correctness and custody

All fourteen final SHA256 values equal
77dcb95038cfbd5e0ab0b522ed50a437883471894916c22959c38431ff420c78.
The unchanged public full validator, CAS, newline/error behavior and durability ordering remain.
Controls cover corruption despite same size/mtime, external writers/genesis CAS, truncation,
replacement/missing files, nested payload aliases, and pre/post-replace failures.
Optional cache allocation failure preserves successful append and forces later full validation.
Initial feature failures and the reproduced allocation failure remain in raw.zip beside fixes.
Final focused controls: 34 passed; runtime compatibility: 270 passed; aggregate reader: 5 passed.
See QUALIFICATION.md for the separately executed final current-source engineering gates.

All fifteen case/supervisor PIDs were absent after sealing. Original capture, source maps,
tools and inputs were unchanged. A post-run auxiliary reader initially used the wrong metadata
key; its KeyError and corrected read-only audit are recorded, with no timing/raw/source change.
The archived grade SHA256 is 73b7409b80669ed6ea6377f754ca6b54a060c346ab3f2e0d63a429a5d45c7769.
Regrading is a later custody check, explicitly separate from original execution.
