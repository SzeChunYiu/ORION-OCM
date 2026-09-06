# Executed readout

The single authorized cold-process native pass completed under the
[registered #43 freeze](https://github.com/SzeChunYiu/ORION-OCM/issues/43#issuecomment-5556737974).
The exact selected-endpoint rule passed: all 100 outputs valid, base/full LAS and
exact/typed tree counts nondecreasing, with strict base-LAS or exact-tree improvement.
The terminal is DONOR_QUALITY_PROGRESSION_ONLY.

## Full assigned denominator

All 100 assigned sentence IDs and 1,584 supplied integer-word tokens remain primary.
Punctuation remains included. There were zero missing, refused or invalid outputs.
The original and revised UDPipe selected trees were exactly equal; all six baseline
scores below were reproduced using the unchanged existing external scorer.

| Metric | UDPipe | Stanza | Delta |
|---|---:|---:|---:|
| Base LAS | 1,234 / 1,584 (77.90%) | 1,368 / 1,584 (86.36%) | +134 |
| Full LAS | 1,231 / 1,584 (77.71%) | 1,361 / 1,584 (85.92%) | +130 |
| Exact trees | 32 / 100 | 34 / 100 | +2 |
| Exact typed trees | 30 / 100 | 32 / 100 | +2 |
| UAS, descriptive | 1,294 / 1,584 (81.69%) | 1,411 / 1,584 (89.08%) | +117 |
| UPOS, descriptive | 1,487 / 1,584 (93.88%) | 1,522 / 1,584 (96.09%) | +35 |

Sentence base-LAS counts improved on 45, tied on 39 and declined on 16 rows.
Exact trees gained on 9 and were lost on 7; typed exact trees gained on 8 and were
lost on 6. These are descriptive paired transitions, not significance or noninferiority tests.
UAS/UPOS were not additional selection endpoints.
[All row scores, deltas and 20 genre/length cells](raw/native-prediction-v1/grade.json)
and [compact transitions](DIAGNOSTICS.json) remain available.

## Duplicate and exposure diagnostics

There are 99 exact supplied-word sequence groups: one one-word sequence occurs twice.
Keeping only the first in fixed order gives 99 rows / 1,583 words:
base LAS 1,367, full LAS 1,360, UAS 1,410, UPOS 1,521, exact trees 33, typed 31.
This diagnostic does not replace the fixed denominator.

The original normalized TRAIN-surface flag identifies five rows; direct exact-word
matching identifies four. Excluding the original five flagged rows gives 95 rows /
1,568 words: base LAS 1,352, full LAS 1,345, UAS 1,395, UPOS 1,506,
exact trees 29, typed 27. Both detectors and their IDs are disclosed.
Absence of a detected match to custody EWT TRAIN is not absence of Stanza training exposure.

This is an already exposed development panel. The imported combined Stanza checkpoints
and CoNLL17 vectors have broader priors than the train-only UDPipe donor. Historical
checkpoint provenance and total training/tuning costs are incomplete. The known EWT
development and model-selection exposure prevents a protected or training-fair superiority claim.

## Mechanism and custody

ADOPT Stanza's recurrent POS/lemma/dependency pipeline as donor cognition; ADAPT only
the supplied-word interface. The model receives fresh nested [forms], without gold
POS, features, lemmas, dependency arcs, annotations or a neural tokenizer/MWT model.
The exact four checkpoint loads are recorded. Models total 241,742,165 bytes;
58,559,868 unique parameter elements include 25,000,000 frozen vector elements.
Learned dictionaries/vocabularies are additional prior state.

ADOPT Bubblewrap as infrastructure and the existing official CoNLL18-based structural
validator/external selected-tree scorer as checker/evaluator. The actor uses one
CPU thread, seed 0, one cold process, fixed sequential order and a 600-second deadline.
Models, runtime and the separate sibling input stage are read-only; actor network
is isolated. The actual stage-write probe was refused. Source, public input and model
bindings remained unchanged. Annotated DEV/TRAIN files were read only by the external
grader after sealing; no model predictor has access to that grading directory.

The launch manifest bound 185 source files. Five new executed sources are archived;
the other 180 were byte-verified against commit 321f4d7aeb18c386716a95ca4b983bb630b54738.
The donor and external grader remain unchanged after prediction. The future capture's
CPU disclosure is corrected separately; it did not generate this historical receipt.

## Measured costs and correction

| Observation | Value |
|---|---:|
| Total capture wall | 8.024628 s |
| Outer launch-to-seal preparation measurement | 7.802274 s |
| Actor model load wall | 2.432007 s |
| Sum of 100 item wall times | 4.173065 s |
| Actor self-reported process CPU | 7.032604 s |
| Capture process CPU | 0.446365 s |
| Directly reaped outer-child CPU | 0.001535 s |
| Actor peak RSS | 887,924 KiB |
| External grading function wall / CPU | 0.912058 / 0.911730 s |
| External grader peak RSS | 246,956 KiB |
| Read-only staged bytes / output bytes before seal | 115,560 / 160,021 |

**Total process-tree CPU is UNKNOWN; CPU custody is incomplete.** The original sealed
receipt incorrectly calls direct-child accounting a process-tree total and sets
complete_cpu_custody=true. Preserve those raw bytes as evidence of the defect;
[RESOURCE-CORRECTION.json](RESOURCE-CORRECTION.json) binds the correction to the exact
receipt, grade and old/new capture sources. Future reporting separates the observations.

Earlier donor qualification separately measured model acquisition 18.942 s,
environment preparation 38.512 s and load-only inspection 2.766 s; acquisition and
installation overlapped. These are not serial whole-lifetime totals. Its environment
occupied 1,011,729,238 bytes and cache 236,923,703 bytes at the recorded inventory.
Imported training/search, development effort, full energy/network transfers and
whole-tree CPU remain unknown. This single-process pass is not an efficiency comparison
with the mixed-domain G1 stream of five fresh process chunks (first start plus four resumes).

## Controls, replay and next use

Before prediction, 22 controls passed, including real public input, malformed output,
wrong words, runtime binding drift and explicit incomplete/refusal status handling.
After the CPU disclosure fix, 23 controls passed. Initial collection/setup failures
remain under raw/controls. Frozen-source grading was actually reproduced with all
semantic output fields identical; the first materialization failed on an omitted
unchanged custody-manifest dependency, then succeeded after restoring that base file.
No prediction was repeated. [Reproduction details](REPRODUCE.md).

The next justified use is this fixed donor inside the unchanged vessel, with the same
donor available to the native parent and hosted comparator under a prospective contract.
No G1 admission, OCM learning, residual improvement, protected accuracy, useful-language
threshold, LLM parity or whole-lifetime efficiency claim follows from this packet.
