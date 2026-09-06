# Default failure, repaired normalization, normalized proposal

| Fixed run | Assigned input | Native outcome | Z3 |
|---|---|---|---:|
| Default rewrite | manual 4 + TRAIN 2 | 2 panics; 0 rewrite returns; CANNOT_CHECK_NORMALIZATION | 0 |
| Breadth-first rewrite | same manual 4 + TRAIN 2 | 2 returns; all 6 rows qualify | 8 PASS |
| Normalized induction | exact 2 BFS TRAIN outputs | 1 compress; PROPOSED_ABSTRACTIONS | 4 PASS |

[Default receipt](raw/capture-v1/receipt.json) ·
[BFS receipt](raw/breadth-first-successor/capture-v2/receipt.json) ·
[induction receipt](raw/normalized-induction/capture-v1/receipt.json).

## Normalization effects

| Manual case | Observed primitive output |
|---|---|
| Orientation | (- x y) |
| Nonshadowing binding | (- (+ x 1) (+ y 2)) |
| Existing unary/binary minus | (+ (- x) (- x y)), unchanged |
| Signed/nested | (- (- x (- 3)) y) |

Three manual rows change; the existing-minus row is the no-alarm case.
TRAIN max3 gains four binary-minus nodes; mpg_guard2 gains one.
Each TRAIN row passes original-versus-rewrite equality and its original spec.
Manual equality checks use the original input and decoded rewrite; the fixed
expected trees additionally test orientation, binding and intended effect.
[Actual manual qualification](raw/breadth-first-successor/capture-v2/manual/calls/qualification.json) ·
[TRAIN qualification](raw/breadth-first-successor/capture-v2/train/calls/qualification.json).

## Normalized induction output

[Raw compress return](raw/normalized-induction/capture-v1/calls/compress-return.json)
contains one arity-one Boolean abstraction, used once in each TRAIN program:
(not (>= #0 1)). The adapter expands it back to the exact normalized primitives.
Native checks verify-00/01 are original TRAIN specs; verify-02/03 are unrestricted
whole-program equality obligations. All four return unsat.
The donor objective changes 5357 -> 4953, ratio 1.0815667272360185.
This is weighted syntax reduction, not a useful-operator or runtime-gain test.
Dedicated alias proof and later synthesis/use remain NOT_RUN.

## Saved descriptive costs

| Run | Bounded case wall(s), seconds | Supervisor incl. binding, seconds |
|---|---|---:|
| Default rewrite | manual 0.064046237; TRAIN 0.064092863 | 0.689674957 |
| Breadth-first rewrite | manual 0.365314546; TRAIN 0.365094950 | 1.295869147 |
| Normalized induction | 0.364428592 | 0.597535520 |

[Default root completion](raw/root-launch-v1/completed.json) ·
[actual BFS root completion](raw/breadth-first-successor/root-launch-v2/completed.json) ·
[normalized root completion](raw/normalized-induction/root-launch-v1/completed.json).
They ran at 16:03, 16:16 and 16:30 UTC, respectively, in separate windows.
Caller and native child CPU/RSS remain in their own raw receipts; overlapping
envelopes must not be summed as complete tree costs. Imported acquisition,
earlier induction and preparation are explicit priors outside each invocation.
Recorded PIDs were absent at the read-only outcome reviews.
