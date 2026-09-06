# Measured costs and boundaries

All figures describe this one public development task and the once-only execution.
Seconds use retained monotonic durations; KiB uses Linux process `ru_maxrss`.
Machine-readable values are in [COSTS.csv](COSTS.csv).

| Command | Outcome | Envelope wall, s | Worker wall, s | Worker CPU, s | Worker peak RSS, KiB |
| --- | --- | ---: | ---: | ---: | ---: |
| C candidate | Solution | 0.114156470 | 0.031114947 | 0.031074754 | 47,572 |
| E0 candidate | External timeout | 20.009268306 | UNKNOWN | UNKNOWN | UNKNOWN |
| B candidate | External timeout | 20.011838971 | UNKNOWN | UNKNOWN | UNKNOWN |
| C-spec checker | PASS / UNSAT | 0.114050284 | 0.032952689 | 0.032677550 | 57,128 |

An envelope runs from supervisor Popen through wait and cleanup. A completed worker
measures its own main-body wall/CPU and process peak RSS. Worker metrics are nested
within envelope wall; they must not be added to it. Peak RSS values cannot be summed
into a whole-process-tree peak. Empty timeout stdout supplies no completed worker
identity or worker resource record; those quantities remain unknown, not zero.

| Aggregate | Seconds | Scope |
| --- | ---: | --- |
| C candidate + C-spec envelopes | 0.228206754 | Successful native service path |
| Three candidate envelopes | 40.135263747 | All assignments, including both failures |
| Candidate + reached checker envelopes | 40.249314031 | Four dispatched command envelopes |
| Complete capture stage | 41.072996906 | Includes binding checks and host capture work |
| Complete assessment stage | 0.914520252 | Includes repeated custody checks and grading |
| Capture + assessment stages | 41.987517158 | Active stage wall; includes native envelopes |
| Assessor self CPU | 0.800895802 | Host assessor only, excludes native child CPU |

The C check's reported total wall is 0.372536039 s, and host-check self CPU is
0.258952941 s. Both are subsets of the assessment stage; they are not additional
costs to add to its totals. Coordinator waiting between the two stages is excluded
from active-stage wall. Installation, preparation, qualification and human review
costs are not represented by these on-run totals.

## Earlier learned-state cost remains separate

The exact library was acquired before this task. [Verified prior references](PRIOR_COST_REFERENCES.json)
preserve the original normalized-induction seal and its recorded costs:

| Imported prior subset | Measured value | Boundary |
| --- | ---: | --- |
| Normalized-induction supervisor wall | 0.597535520 s | Includes pre/post binding |
| Its supervised caller envelope | 0.364428592 s | Nested within supervisor wall |
| Caller main-body wall | 0.322282627 s | Nested within caller envelope |
| Caller self CPU / peak RSS | 0.040992432 s / 25,040 KiB | Caller only |
| Native boundaries | 1 compress + 4 verification calls | Recorded prior, no call repeated here |

That subset does not include all earlier cvc5 acquisitions, original induction,
normalization attempts, repair, alias witnesses or environment setup. Its own
whole-process-tree CPU/RSS are unknown. The full existing history is retained in
[the primitive-rewrite study](../stitch-primitive-rewrite-20260906/READOUT.md) and
[the alias-witness study](../stitch-alias-witness-20260906/READOUT.md).
Do not treat the 0.5975-second subset as the total cost of learning this definition.

This run supports the ordinary implicit parent's narrow public-task sufficiency.
No amortization threshold, lifecycle saving, general speed ratio or comparative
whole-lifetime benefit can be estimated from these data.
