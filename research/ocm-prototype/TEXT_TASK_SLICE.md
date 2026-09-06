# Seeded text → checked task → English development slice

This executable slice accepts two explicitly seeded task families and runs them through
the persistent `OCMRuntime.solve` path. It does not establish learned English, broad
problem solving, local execution, useful abstraction learning or a performance advantage.

## Run on laptop billy

From the repository root, use a Python environment containing
[`requirements-g1.txt`](requirements-g1.txt). All qualification and stateful trials
belong on laptop billy; do not run these on the Mac.

```sh
python research/ocm-prototype/text_task_slice.py --state /tmp/ocm-text-state ask \
  'What is the largest of 8, 2 and 5?'
python research/ocm-prototype/text_task_slice.py --state /tmp/ocm-text-state ask \
  'Apply the guarded function with z = -20, x = 7, y = 3.'
```

The answers are `The largest value is 8.` and `The guarded function returns 4.`
Each invocation reconstructs state and explicitly rebinds trusted host code.
The first request for each family acquires a cvc5 program from the complete public
specification. Later requests reuse the persisted parameterized program.

Use `--json` before `ask` for the typed meaning, semantic specification identity,
source checks, response plan, actual solve traces and stage measurements. Import
`TextTaskSession` and call `ask` repeatedly for a warm in-process serving lifetime.

## Exactly what language is supplied

The raw tokenizer recognizes ASCII words, signed decimal integers and `?,.=`.
The maximum constructions are:

- `What is the largest of a, b and c?`
- `What is the maximum of a, b and c?`
- `Find the largest of a, b and c.`

Guarded requests use `Apply the guarded function with x = a, y = b, z = c.`;
the three named bindings may appear in any order. The function returns `x+y`
if `x+y+z >= 1`, otherwise `x-y`. Integers follow the existing CLIA operational
bound. Case and whitespace are normalized; extra clauses, unsupported words,
negation, decimal quantities, missing or repeated roles are refused or clarified.

These mappings and the two output clauses are authored host priors, recorded with
the tokenizer/implementation digest and independently registered source task.
Stanza is not involved in this adapter. Nothing here counts as language acquisition.

## Checking and custody

1. A complete accepted semantic identity, signature, scope and named bindings are
   produced before synthesis or method lookup. `Int³ → Int` alone is insufficient:
   maximum and guarded arithmetic have different complete specifications.
2. The fixed cvc5 donor proposes a program; the existing grammar and independent
   universal Z3 checker govern its acceptance through actual OCM solve.
3. The existing checked data-only executable descriptor is persisted. An exact
   specification-keyed method table retrieves it; host callables rebind explicitly.
4. Program application passes the existing independent pointwise checker through
   actual OCM solve and again at admission.
5. A second checker constructs a fresh ground obligation directly from the public
   specification. It does not evaluate or trust the returned program. This catches
   a shared evaluator failure that fools both application and pointwise checking.
   Both checks run before runtime commitment and checked-value admission.
6. A bounded response plan carries the exact tuple, result, semantic identity and
   supporting field atoms. Independent output-contract checking verifies the
   emitted quantity, polarity, task meaning and absence of an extra clause.
   The plan is also bound to the independently checked task/value/support. Proposal
   callbacks receive copies; they cannot redefine the accepted arguments or speech act.
7. The checked utterance is admitted to that same persistent field.

The application reads the admitted request identity before execution. Backend
mutation of field, evidence, registry or event state prevents candidate commitment.
This is a checked host-adapter boundary, not a sandbox against arbitrary Python code.

The independent checking paths still share Z3 as a native engine. No independent
engine-diversity claim is made.

Discovery-query provenance is stored separately from current program justification.
Program correctness depends on the source specification and reuse authority;
language correspondence additionally warrants interpreting and answering the text.
Withdrawing a language mapping blocks fresh answers and invalidates prior utterances,
while independently justified program correctness survives.

## Withdraw and restore support

```sh
python research/ocm-prototype/text_task_slice.py --state /tmp/ocm-text-state \
  revoke jmbl_fg_max3 correspondence
python research/ocm-prototype/text_task_slice.py --state /tmp/ocm-text-state ask \
  'What is the largest of 9, 2 and 5?'
python research/ocm-prototype/text_task_slice.py --state /tmp/ocm-text-state \
  reinstate jmbl_fg_max3 correspondence
```

The middle call refuses. Replace `correspondence` with `reuse_authority` or
`specification` to exercise those distinct premises. Refusal never silently
reacquires a revoked method or repairs its authority. Other supported families remain
available. The `evidence TASK_ID` command exposes the registered premise identities.

## Measurement and qualification

Stage wall time and host CPU, session startup time, actual donor/application/check
calls and logical field counts are reported. Native source-check results retain
worker measurements. Whole process-tree CPU/RSS, resident/materialized bytes and
complete index-locality instrumentation remain explicitly unmeasured; existing
solve resource counters are not empirical proof of locality.

```sh
PYTHONPATH=src python -m pytest -q tests/integration/test_text_task_slice.py tests/integration/test_text_task_binding.py
```

These donor-backed tests skip in environments without cvc5, Z3 or sexpdata.
Qualification requires the pinned donor environment; a skipped suite is not a pass.
The tests exercise acquisition, exact dispatch, new arguments, role order, a guard
boundary, restart, support withdrawal/restoration, harmless unrelated tasks,
stable reusable callable identity and deliberately wrong evaluator/output controls.

Source: [contract](text_task_contracts.py), [runtime adapter](text_task_programs.py),
[session/CLI](text_task_slice.py). Programme owners: #73 capability slice and
#115 runtime integration. Protected N1/N2/learning milestones remain open.
