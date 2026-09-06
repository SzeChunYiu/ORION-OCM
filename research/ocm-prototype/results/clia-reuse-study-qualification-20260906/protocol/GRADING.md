# External grading and controls

This file stays outside both actor environments. No panel outcomes exist.
The JSONL contains 36 apply templates and five syntax requests per arm; acquisition
uses the two complete task objects reconstructed by the pinned load_task contract.
Input/import separation is not a claim of adversarial filesystem isolation.

## Value oracle

Use ordinary exact Python integers, independently of Z3, cvc5 and the acquired code.
For max3, the public specification requires v >= x,y,z and v in {x,y,z}; its unique
value is max(x,y,z). For guard2, upstream im(b,a,c) expands to (b and a) or (!b and c):
v = x+y if x+y+z >= 1, otherwise x-y. Reject bool, float and string outputs even
when numerically equal. All guard2 boundary tuples have y != 0, making wrong-branch
selection observable. No expected value belongs in an actor request.

Check the selected output only: OCM requires ADMITTED, admitted_id and answer;
native requires ACCEPTED_PARENT, record_id and answer. For an authorized apply,
answer.status must be APPLIED, arguments exactly match the concrete request,
program_id and program_sha256 match F1, and value has exact type int and equals
the independent oracle. Require the recorded fixed pointwise checker PASS too.
A valid proposal hidden in diagnostics cannot repair a missing or wrong answer.

For withdraw.max3.01/.02, require no selected answer or newly admitted output,
the exact original registration authority absent, descriptor current liveness DEAD,
zero application and synthesis calls, and an explicit support refusal/trace.
An unrelated error, timeout or CANNOT_CHECK_UNBOUND alone is not successful policy
refusal. The expected bind refusal is a separate control, not a 37th math query.
Do not require equal wording from native/OCM statuses.

## Phase coverage

- warm.max3.01–03: unique maximum in x/y/z; .04–06: all-negative maxima in x/y/z;
  .07–08: two different pair ties.
- restart.max3.01–03: new positional maxima; .04: all-negative maximum;
  .05: remaining pair tie; .06–07: all-equal positive/negative; .08: zero maximum.
- Both 12-case batches contain guard2 boundary pairs with sum 1/0 and both
  branches away from the threshold. History/withdraw/restore retain paired sum 1/0.
- Every tuple is new within its function and excludes the four exposed adapter
  unit tuples. Both arms receive the same order and values.
- Syntax repeats ["The","team","solved","the","problem","."] once per apply phase.
  Require the actual unchanged UDPipe model invocation and structurally valid
  selected tree. Record model hash and token/head/deprel output; no syntax-accuracy
  or learned-language claim follows, and no UD gold is supplied to either arm.

## Authority and immutable-history audit

Export all IDs before F1. A query-registration target must be a real assumption
supporting max3 and absent from guard2/model support; never revoke a derived proof.
The historical target must be a real acquisition/search observation, absent from
all validity-support terms. Label it history-only before withdrawal, not afterward.

After history withdrawal: both descriptors and every prior application remain LIVE.
After true withdrawal: max3 descriptor, acquisition proof and all earlier max3
application commitments lose current authority; guard2 and syntax/model remain LIVE.
After restoration: the same max3 descriptor/program/authority IDs and old outputs
recover; no fresh registration or synthesis. Keep the historical row withdrawn.
Compare application-record bytes before/after; current liveness may change but
historical mathematical payloads and receipts must not be rewritten or deleted.
Use canonical prior-payload hashes for the OCM ledger: appended revision events
legitimately change the whole log or state file. Native immutable result files
can be checked directly. Charge snapshots and audit reads separately.
Revisions occur at the end of the preceding actor stage: restart withdraws search
history, history withdraws max3 registration, and withdraw restores registration.
Each audits before/after the revision, persists and exits. The next new OS process
audits the loaded state before bind/query. There are six actor stages per arm;
no uncounted modifier process or in-process reinstantiation supplies a restart.
Audit is read-only; solver/checker subprocesses are recorded and charged separately.

## Negative controls before the panel

Existing source controls must cover malformed/out-of-grammar program, wrong
arity/type, changed identity, stale support, unbound callable after restart, wrong
returned value and clean/unaffected cases. These are development qualification,
not extra successes in the 36-case denominator.
Qualify the external grader separately: an actual accepted fixture value passes;
a copied result whose value is increased by one fails, and a copied wrong tuple
fails identity binding. Verify refusal normalization against an unrelated-error
control. Never feed these modified records to an actor or treat them as real outputs.

## Reporting

Report authorized correctness out of 34, expected refusals out of two, all 36
attempts including missing/refused/invalid, and five separate syntax diagnostics.
Require named reused objects, registered callable witnesses, zero actual synthesis
after acquisition and affected/unaffected prior-output audits. Counts initialized to zero
are not instrumentation: collect actual solver invocation receipts as well.
No confidence interval or inferiority margin is inferred from this purposive panel.
Show per-phase/cumulative CPU, wall, checks/rebinds, replay/global work and bytes
against the faithful cached native library. Repeated-synthesis timing is optional
and excluded from this minimal panel; zero repeat calls alone is not measured
time saved relative to a resynthesizing arm. Library-explained gain is PARENT_SUFFICIENT.
