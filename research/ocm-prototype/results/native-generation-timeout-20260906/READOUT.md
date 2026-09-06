# Saved-record readout

## Assigned outcomes

| Attempt | Route | Exit | Recorded outcome |
|---|---|---:|---|
| V4 | implicit primitive | 0 | CANNOT_CHECK: statistics serialization after synth-fun |
| V4 | explicit primitive | 0 | CANNOT_CHECK: statistics serialization after synth-fun |
| V4 | full manual macro | 0 | CANNOT_CHECK: statistics serialization after helper define-fun |
| V5 | implicit primitive | 0 | Native SOLUTION; external semantic grading NOT_RUN |
| V5 | explicit primitive | 124 | check-synth invocation did not return before outer timeout |
| V5 | full manual macro | 0 | Native SOLUTION with two GEN_fn_0 annotations; NOT_GRADED |

V4: all three stop at index 3, statistics_serialize_error, after invoke_end and
statistics_collect_end. No constraint or check-synth was dispatched.
[Raw V4](raw/timeout-localization-v4/capture-v4/receipt.json).

V5 explicit: all parsing, synth-fun registration, three declarations and four
constraints completed. Boundary line 177 / seq 176 records check-synth
invoke_begin at index 11. It has no invoke_end or post-call statistics.
[Boundaries](raw/timeout-localization-v5/capture-v5/explicit_primitive/boundaries.jsonl) ·
[native output](raw/timeout-localization-v5/capture-v5/explicit_primitive/stderr).

## Native evidence

The implicit stderr prints a two-nonterminal grammar: integer variables,
0/1, addition, subtraction and ite; Boolean true/false, equality, <=, not,
and/or. Its candidate contains lets and signed scalar arithmetic.
[Implicit raw](raw/timeout-localization-v5/capture-v5/implicit_primitive/stdout) ·
[printed grammar](raw/timeout-localization-v5/capture-v5/implicit_primitive/stderr).

Both explicit routes print their OCM_I/OCM_K/OCM_B grammar and a
SINGLE_SOLUTION SMART enumerator registration. The macro grammar additionally
has singleton GEN_fn_0. Its candidate is (fn_0 x (fn_0 y z)), with two native
GEN_fn_0 annotations. Returned derivation membership is not causal search benefit.
[Macro raw](raw/timeout-localization-v5/capture-v5/explicit_macro/stdout) ·
[native annotations](raw/timeout-localization-v5/capture-v5/explicit_macro/stderr).

All routes emit options-auto sygus-si use. Effective option snapshots also say
use; this is configuration evidence, not proof of the actual solving route.
Only completed routes have final statistics. Default zero generic enumeration
counters do not establish that no enumeration occurred.

## Descriptive recorded resources

| V5 route | Per-case supervisor wall seconds | Worker self CPU seconds |
|---|---:|---:|
| implicit primitive | 0.114140746 | 0.047311206 |
| explicit primitive | 20.012353175 | unavailable after timeout |
| full manual macro | 3.322265999 | 3.248472452 |

These are one diagnostic attempt, with observer overhead; no gain ratio or
amortization claim. All recorded worker and wrapper PIDs were absent on review.

## Smallest next donor step

Use the actual printed implicit two-nonterminal grammar for one explicit
primitive replay, before adding learned macros. Keep task, checker and envelope
fixed, and give the informed native parent the same donor grammar. Explicit
syntax can change the solver route even with the same productions. No replay,
grammar modification, checker call or follow-up actor occurred in packaging.
