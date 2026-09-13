# S1 witness recovery — measured result V1

**Result: the reported witness was recovered and passed fresh-process checks.**
Date: 2026-09-13. This repairs a missing-evidence record; it is retrospective.
No search remains running and no new campaign arm was added.

The original source at 5378c2b7 and the 61 recorded starting genotypes
reproduce all 2,157 compact trace rows through evaluation 3,827, including
the recorded raw fingerprint. The unmodified class scan also reproduces the
entire first-DENSE summary: 464 scanned candidates, 3,500 verification calls,
and reported target-specific burden 7,327. Raw and pruned graphs are now saved.

| Quantity | Raw graph | Pruned graph |
|---|---:|---:|
| Nodes | 20 | 14 |
| Frozen carrier descriptor | DENSE | DENSE |
| Standard capability | 0.8854 | 0.8854 |
| Minimum across six controls | 0.8542 | 0.8542 |
| Margin above best constant, in registered fx units | 1.0008 | 1.0008 |
| Distinct error-free probe answer vectors | 5 | 5 |

The six capabilities are identical before and after pruning:
standard/no_revoke/double_revoke 0.8854; half_events 0.8594;
shuffled_events 0.8542; extra_unseen_feedback 0.8906.
The verifier prints margin 1.001 after rounding. The value 1.0008 is computed
from the registered four-decimal capabilities, not an unrounded physical score.

Raw fingerprint:
f88fb0cbce639d7a578b9e254ae13b777a025df719dad0461e7a5133b59eb9dd.
Pruned fingerprint:
cc7988d2f347915264c760a4c5c4beef2221cec15d518373235ca7b78c57f07d.

The captured winner's verifier charged 346 calls, including 330 greedy-pruning
calls. The full preceding class scan charged 3,500 calls. Actual intercepted
ecology-call counts equal those reported counts. A fresh process separately
reexecuted six controls and five probes on each graph: 22 additional calls,
all comparisons passed, with no probe error accepted as a distinct answer.
A second 22-call verification through the portable source-archive entry point
reproduced every control/probe output and comparison exactly.

## Costs of this recovery

| Stage | Search evaluations | Class-verifier calls | Calibration calls | Fresh checks |
|---|---:|---:|---:|---:|
| Prefix 128 | 128 | 96 | 10 | 0 |
| Recovery through 3827 | 3827 | 3500 | 10 | 0 |
| Independent recheck | 0 | 0 | 0 | 22 |
| Portable archive replay | 0 | 0 | 0 | 22 |
| Total | 3955 | 3596 | 20 | 44 |

The combined count is 7,615 across these declared call types; their CPU costs
are not interchangeable. Function timers sum to 1,150.78 seconds wall time
(19.18 minutes) and 1,135.74 seconds CPU time.
This includes capture/canonicalization overhead inside those functions.
Preparation, focused tests, custody copying/compression, interpreter startup
and final receipt writes are outside these timers. No complete physical
resource profile is claimed.

The original two source archives each consumed 20,000 evaluations. Those
historical acquisition costs are disclosed and were not rerun. The original
7,327 figure is a target-specific search-plus-class-verification count; it
is neither this recovery's complete work nor the developmental lifetime cost.

## What has and has not been established

The retained object is an admissible witness under the original six-control
bar, with the disclosed half-leaking extra_unseen_feedback intervention.
This result does not silently substitute the later seventh/current control.
Recorded-prefix agreement does not authenticate the historical Python binary:
the old log gives a 3.11 path; the available and used version is 3.11.14.

The pruned graph contains KVSTORE, INSERT and NEAREST alongside DENSE.
It contains no LINEAR, AFFINE or GRAD node. Thus the DENSE descriptor is not
by itself evidence of a pure coefficient-learning mechanism. A next scientific
question is the causal role of those retained resources under matched
interventions; the recovered genotype now makes that experiment possible.
The primary-lineage label ["seed",38] comes from a KVSTORE seed, but crossover
discards the other parent's lineage. No complete-ancestry or no-DENSE-inheritance
claim follows. The 24-arm campaign and population/frontier questions remain open.

## Evidence and reproduction

[evidence/s1-recovery-20260913/SUMMARY.json](evidence/s1-recovery-20260913/SUMMARY.json)
indexes the measured result. WITNESS.json retains both genotypes, the complete
verifier return, pruning information and all winning-verification outputs.
INDEPENDENT_VERIFICATION_V1.json contains the fresh-process control/probe traces.
Compressed raw traces and scan logs, exact seed population, preparation,
prefix and recovery receipts are retained alongside them.

HISTORICAL_SOURCE_V1.tar.gz contains all 15 bound source/authority files.
To rerun only the 22 direct checks, use Python 3.11 with:

python3 -I -B replay_saved_witness.py --witness evidence/s1-recovery-20260913/WITNESS.json --output NEW_DIRECTORY

The default packet input is the adjacent committed B6 custody packet; --packet
can name another byte-identical copy. This command does not rerun search and
requires no Git access. MANIFEST.json binds this unit's files except itself.
