# Next proposed diagnostic: locate the explicit-route stall

**Prospective plan only. Not prepared, frozen or executed.** The one-stage failure
attribution is explicit candidate execution: E0 already times out without a helper.
The first revival action is to identify which part of that boundary consumes the
time, before changing a grammar, solver option, learned library or induction corpus.

## Minimum new assignment

One separately registered E0 diagnostic call on the exact `public_absdiff2_v1`
specification and existing full explicit primitive grammar. Keep cvc5 1.3.4,
all existing solver options, CPU0, 4 GiB address space, native 5000 ms, external
20 seconds and the existing cleanup/watchdog policy. No B call or induction is
needed to locate this shared failure. There is no retry or result-driven follow-up.
This is an instrumented diagnostic, not another observation under the old assay ID.

A new source-bound worker records flushed, separate stderr events at:

1. Worker main entry, before/after imports and pinned-version checks.
2. Solver construction and existing option setup.
3. Before/after each parser `nextCommand`, indexed against the frozen input commands.
4. Before/after the corresponding `command.invoke`, especially `check-synth`.
5. Candidate collection, statistics collection and final response serialization.

Each event includes a monotonic timestamp, process CPU time and PID. Record process
peak RSS where available, without pretending it is active allocation. Keep solver
stdout unchanged. Avoid extra solver API queries or converting native terms solely
for logging; the phase index is sufficient to map the static command sequence.
Instrumentation and capture costs are charged as diagnostic overhead.

## Required preparation and interpretation

- First test the logger with mocked parser/invoker stalls and a normally completing
  path. Confirm events survive termination and that payloads/options are unchanged.
- Repair the known stale success-reason defect only in the new source successor,
  with its own mocked regression test. Preserve this assay's frozen source/receipts.
- Freeze source, task, request, environment, exact command, event schema and once-only
  assignment before native execution; independent source review precedes dispatch.
- Seal all raw stdout/stderr and process records before interpreting the phases.
- A missing after-event locates an interrupted boundary, not its internal cause.
  Missing entry evidence remains an observation failure, not a search-time estimate.
- If this diagnostic completes, retain that outcome as instrumented evidence.
  It does not replace either original timeout or establish an optimization benefit.

After the responsible phase is identified, propose one stage-specific engineering
change and a new matched comparison. Parsing/grammar construction, search or
reconstruction failures require different interventions. No new induction follows
merely because this diagnostic looks favorable; consumer qualification still comes
before corpus expansion and claims of useful generative acquisition.
