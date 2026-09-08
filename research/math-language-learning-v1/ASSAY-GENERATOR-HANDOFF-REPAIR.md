# Canonical generator handoff repair

The registered attempt completed generation in all four episodes, then stopped
before any method call with KeyError: 'training'. Its retained metadata records
zero calls and 232 unreached slots. That failed attempt remains unchanged.

## Cause and repair

The normative generator emits partitions named train, development and final.
Both the scheduler and retained-result recheck incorrectly requested training.
The authored convenience adapter independently manufactured that wrong key,
so the authored lifecycle and isolated generator controls did not cross the
successful real producer/consumer boundary.

The scheduler and recheck now consume train. The existing run_authored input
field training is normalized to train in its generated-shaped output, including
authored row IDs. The acquire_selected request field training remains unchanged.
The producer, stream, protected master, six normative policies and selection
mechanism are unchanged. Historical authored records retain their original
source-bound adapters and checkers; they are not relabelled as current evidence.

## Current qualification

The new integration fixture calls the actual generate_episode and coordinator
run at the unchanged four-episode, 32/16/32 dimensions. Only its field-choice
stream uses the explicit engineering-only tag; the protected master is refused
before hashing. It retains every draw, produced partition and original row ID.
Dispatch is an explicitly refused recorder, not a solver or scientific process.
All eight A request boundaries now receive the exact generated training and
development lists; subsequent phases stay unavailable and are not retried.

The same generated record reaches retained recheck. The clean input is accepted
for rechecking; substituting the acquisition training list is refused.
The authored convenience input remains unmodified and emits the canonical shape.

Three targeted controls fail on the predecessor at the exact affected boundaries.
An initial selected invocation used a nonexistent test filename: exit 4, zero
tests executed. Both failures remain retained separately from the successor.
The corrected selected invocation passes 45 tests, zero failures/errors/skips,
with 377 source inputs equal before/after/snapshot. Its outer test-process wall
is 38.319487193 seconds; waited child CPU is 25.055196 seconds.

That selected invocation includes the existing actual small authored lifecycle:
52 distinct completed child lifetimes, 42 independent store copies and the
retained no-alarm analysis. Its one episode establishes the authored causal-use
apparatus and PARENT_SUFFICIENT; whole-study and full economics remain unavailable.
The generated-stream fixture establishes the interface, not learned usefulness.

## Exact retained evidence

Laptop root: /home/billy/orion-director-work/20260907/
- unary-generator-handoff-repair-qualification-v1: 01-red, 02-green-selected,
  03-green-selected, SOURCE-FREEZE.json, HANDOFF.json and COMMIT-INPUTS.json.
- unary-assay-registered-v2-prepared/work/coordinator/COORDINATOR.json:
  ca156cb18248a0eaa806e7fb58abaa207cfb38397c796de2ec48c63318295930.
- unary-assay-registered-v1-independent-review/REVIEW.json:
  457f16ac178b0a5f0b6952c613d2baa944333a2fc08508bf542b3458dc05e6ef.

The original 376-input scientific source closure is unchanged. The successor
changes three production files and adds this regression; source-qualified
integration and a separately authorized attempt remain root responsibilities.
No registered master draws or scientific rerun were performed for this repair.
