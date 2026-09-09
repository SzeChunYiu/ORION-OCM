# R0A suffix-elision audit — dynamic guards, effect certificates, and corrected work

**Status:** source-derived formal rejection of unrestricted first-PASS early exit / no production change / no ML authorization.

This note applies `R0A_TRACE_EQUIVALENCE_PROTOCOL_V1.md` to the actual M2 runtime rather than assuming that every checker after the selected answer is silent.

The result is sharper than the original R0 C1 observation:

```text
current arbitrary-host-checker contract:
  first-PASS early exit is NOT lifecycle-safe

current full CHECK trace contract:
  first-PASS early exit is NOT trace-equivalent even for pure tail checkers

original R0 work estimate:
  40 tail verification_calls was not 40 skippable checker calls;
  the existing stage boundary can save at most 20 checker calls and
  0 composition_work on the frozen R0 population
```

The path to a safe optimization is an effect/capability certificate for callbacks plus an explicit versioned trace projection, not a learned predicate.

---

## 1. Actual runtime order

The current `solve.py` has three separate operations:

```text
compose_stage:
  invoke every admissible backend and materialize every candidate

check_stage:
  invoke/check every composed candidate

decide:
  choose passed[0]
```

Therefore a `break` after the first PASS inside `check_stage` cannot retroactively save backend execution or composition work.  Saving those costs would require a stronger transformation that interleaves compose/check and omits later backend callbacks.

The distinction is load-bearing because both backend and checker callbacks are monitored by the runtime callback guard.

---

## 2. Ordinary tail verdicts are decision-neutral after a first PASS

Let the checked sequence contain a first PASS at index `f`.  Suppose every later callback returns normally with an ordinary registered verdict or a locally handled checker failure (`FAIL` or `CANNOT_CHECK`) and does not trigger `CallbackStateChanged`.

The incumbent `check_stage` computes

```text
passed = [c for c in checked if c.verdict == PASS]
status = PASS if passed else worst
```

and `decide` chooses `passed[0]`.

### Proposition 1 — output-prefix equivalence under effect-free tail execution

Under the premise above, deleting candidates strictly after the first PASS preserves the chosen candidate, answer, and CHECK-stage PASS status.

### Proof

The first PASS remains present and remains the first PASS.  Any later ordinary verdict cannot make `passed` empty, so CHECK status remains PASS.  `decide` selects the first member of `passed`, which is unchanged. QED.

This is only an answer/decision theorem.  It says nothing yet about state effects, durable trace, audit evidence, or future lifecycle behavior.

---

## 3. Dynamic-guard omission theorem

The actual runtime does not assume host callbacks are pure.  Around every backend/checker callback it snapshots API-mediated runtime state and event position.  If the callback changes runtime state, the guard raises `CallbackStateChanged`.

`check_stage` treats that condition specially:

```text
all earlier PASS verdicts -> CANNOT_CHECK
current candidate         -> CANNOT_CHECK
CHECK stage               -> CANNOT_CHECK
```

and `decide` has an absorbing upstream-CANNOT_CHECK rule.

### Theorem 2 — a dynamically guarded callback cannot in general be safely omitted

Assume a legal tail callback `g` after an earlier PASS can change protected runtime state.  The incumbent executes `g`; the callback guard observes the change and forces `CANNOT_CHECK`.  A first-PASS early-exit variant omits `g`, so the change and the corresponding fail-closed transition never occur.  Therefore the two executions can differ in protected decision and persistent runtime state.  They are not related by a protected stuttering/branching refinement.

### Proof

Take the repository's existing hostile behavior: first checker returns PASS; a later checker revokes support while returning PASS.  The incumbent guard detects the state transition and `check_stage` invalidates the earlier pass, returning `CANNOT_CHECK`.  If the later checker is omitted, the first PASS remains valid and the revocation never occurs.  Thus both the CHECK status and persistent revoked set differ.  One protected counterexample refutes universal suffix-elision equivalence. QED.

`r0a_suffix_elision.py` executes this counterexample against the current runtime/check-stage implementation rather than only restating it.

### Corollary 2.1 — runtime monitoring is not an omission certificate

A dynamic guard proves properties of callbacks that were executed.  It cannot establish that an omitted callback would have been effect-free, because the very observation used to detect a forbidden effect is removed with the callback.

This is the key difference between **monitoring** and **certification**.

---

## 4. The current operator contract has no checker-purity proof

The runtime solve `OperatorSpec` stores an arbitrary Python `checker` callable.  The persistent operator manifest records only that a checker is required and explicitly identifies executable implementation identity as host-supplied/unverified.  There is no proof object or effect type saying that a checker cannot mutate runtime state.

`expected_effects` on the broader registry contract is not an executable proof of checker purity, and the callback guard does not consult it to authorize omission.  Existing tests intentionally allow a checker to close over the runtime and revoke support; the guard catches the effect only after the callback runs.

### Theorem 3 — exact universal purity inference is unavailable for arbitrary host code

For a Turing-complete unrestricted callback language, no total sound-and-complete procedure can decide for every callback whether it will avoid a forbidden runtime effect on every legal execution.

### Reduction

Given a program `M` and input `x`, construct a checker that simulates `M(x)` and performs a forbidden runtime mutation iff the simulation halts.  A total exact decider for universal absence of that mutation would decide the corresponding halting property.  Contradiction.

Therefore an exact early-elision gate must obtain purity by **construction or proof**, not by a perfect classifier over arbitrary Python callbacks.

Mature parent mechanisms are effect systems (e.g. Lucassen–Gifford) and proof-carrying code (Necula): admit code only when an efficiently checked certificate establishes the required safety/effect policy.

---

## 5. Pure tail callbacks still change the incumbent full trace

Even when every tail checker is effect-free and Proposition 1 preserves the answer, the incumbent `Stage.CHECK` record contains:

```text
all checked PASS operator ids;
all per-operator verdicts;
candidate-data work;
verification_calls = len(checked).
```

`OCMRuntime.solve` persists that CHECK stage as a durable `CHECKER_RESULT` event and exposes the solve trace publicly.

Therefore a prefix CHECK record is not byte/field-equal to the incumbent full CHECK record.

### Proposition 4 — C2 full-trace equivalence fails under literal current trace semantics

If at least one tail candidate is removed, the CHECK payload and resource delta differ.  Hence literal C2 trace equality fails even when output and runtime state agree.

To authorize elision, the contract would need a **prospectively versioned observation projection** under which certified-pure redundant tail checks are tau/silent, or an explicit summary event such as `CHECK_TAIL_ELIDED` whose semantics are accepted by downstream consumers.  Choosing that projection after measuring the speedup would be invalid.

---

## 6. Correcting the frozen R0 accounting

The original R0 receipt reported for candidates after the first PASS:

```text
queries_with_recoverable_work = 20
total_composition_work        = 33
total_verification_calls      = 40
```

but its own instrument defines per checked candidate as:

```text
compose stage:  composition_work = len(input_atoms)
                verification_calls += 1

check stage:    verification_calls += 1
```

and `compose_stage` has already completed for the entire candidate set before the first CHECK PASS can exist.

All 20 R0 multi-candidate answering queries had two PASS candidates and the first PASS at index 0.  The 40 tail verification units therefore correspond to 20 tail candidates, each charged once in compose and once in check.

### Corrected recoverability under the existing stage boundary

```text
composition_work removable by check-stage break             = 0
compose/backend verification units removable                = 0
CHECK-stage verification units removable                    = 20
actual tail checker callbacks represented by those 20 rows  = 20
```

The original 33 composition-work units and 20 compose-side verification units were already spent before `check_stage`; calling them first-PASS early-exit savings was a stage-accounting error.

A compose/check interleaving transformation could in principle target them, but it would omit arbitrary backend callbacks and therefore inherits Theorem 2 unless backend effects are also certified.

---

## 7. Exact safe subset under the current contract

After a first PASS, tail entries with no executable checker callback are structurally decision-neutral:

```text
candidate output already contains error -> deterministic FAIL
checker is None                         -> deterministic CANNOT_CHECK
```

Eliding only such entries cannot skip a runtime callback mutation.  However the frozen R0 tail consisted of the second PASS candidates, so those 20 tail rows necessarily had executable checkers.  Thus this narrow current-contract safe subset does **not** recover the frozen R0 opportunity.

It also still changes the literal full CHECK trace unless the trace projection is changed prospectively.

---

## 8. Exact route to a real R0A optimization

Do not fit a model.  Introduce a separately governed callback class with mechanically checkable effects, for example:

```text
checker contract:
  language/version        = restricted deterministic checker kernel
  input                    = detached canonical candidate data only
  runtime capabilities     = none
  persistent-write effects = empty
  external-effect effects  = empty or separately prohibited by sandbox policy
  termination/resource cap = certified/bounded
  code/proof identity      = content-bound
  proof/effect certificate = independently checked at admission
```

Then prove two things independently:

1. **effect theorem:** omitted certified-pure tail callbacks cannot change protected runtime/lifecycle state;
2. **trace-refinement theorem:** the versioned protected trace projection treats their redundant tail execution as silent while preserving required audit/failure knowledge.

Only after both pass should the runtime be changed to early-exit for that certified class.  Any certificate validation, manifest storage, sandboxing, or dispatch overhead must be charged against the 20-check frozen upper bound and then remeasured on a real ecology.

For arbitrary host callbacks, keep exhaustive checking.

---

## 9. Current terminal

The original R0 statement "exact early exit explains all after-answer work" is too strong under the production lifecycle contract.

The corrected terminal is:

```text
EARLY_EXIT_OUTPUT_ONLY_NOT_LIFECYCLE_EQUIVALENT
CHECKER_EFFECT_CERTIFICATE_REQUIRED_R0A
```

with corrected frozen opportunity:

```text
20 CHECK-stage checker calls maximum under the old test population,
0 composition work under the current stage boundary,
0 of those 20 authorized for omission under the current unrestricted checker contract.
```

This is a negative result for the immediate patch, but a positive design result: it identifies the missing representation/capability contract exactly and keeps the problem out of learned routing.
