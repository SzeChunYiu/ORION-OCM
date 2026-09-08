# Independent decision-core corrective review

**Accepted for the stated bounded helper scope.** The reproduced iterator defect
is repaired. No additional material defect was found in the inspected helper,
mathematical correction, final patch or focused qualification records.
This accepts an isolated correction; it does not apply or certify PR154.

## Finding and repair

`decision_regions` previously tested membership repeatedly against each state's
one-shot acceptable-action iterator. For one state accepting only `b`, testing
absent action `a` first exhausted that iterator and incorrectly lost `b`.
The independent tuple control succeeded while the iterator case failed;
[the original witness](FOCUSED-WITNESS-01.json) pins the exact old helper and PID.

The final helper first materializes each state's acceptable actions as a
frozenset, then queries that snapshot. The new regression compares tuple and
iterator inputs, their exact regions, and common-action/region-containment
agreement. [The retained delta](REPAIRED-DELTA.diff) is limited to that repair,
its regression, the STOP scope clarification and reporting.

## Mathematical and API boundaries

- Exact arithmetic accepts built-in integers, Fraction and finite built-in
  floats interpreted as their stored binary rationals. Exact normalization,
  nonnegative probabilities and valid successors are checked without tolerance;
  zero-mass unknown successors are also rejected. Decimal intent is not inferred.
- The finite metalevel recurrence consumes one integer allowance per cognitive
  step, makes STOP mandatory at zero and retains STOP on ties. It establishes
  no unlimited zero-cost-cognition result.
- Contract bisimulation compares action sets, deterministic contract equality
  and exact transition masses by block. It checks supplied action contracts.
  Combining it with separate state-dependent STOP values additionally requires
  block-preserved STOP outputs/costs. The final docstring and erratum now state
  that condition. The independent two-state example is a boundary witness,
  not a counterexample to the corrected conditional theorem.
- The finite adaptive-information identity follows by the ordinary chain rule
  for history including the chosen probe and observation, with no extra target
  information introduced by probe selection. The two-world counterexample to
  conditioning on the entire generated probe sequence is sound. No unbounded
  or random stopping-time extension is claimed.
- Fraction outputs require explicit serialization and arithmetic-cost handling
  during integration. The unchanged prospective selector and source cost
  extraction are outside this qualification.

## Evidence and source custody

The final Linux focused receipt records PID 1942545, actual cwd and imported
module path, matching pre/post helper and test hashes, and two passing affected
controls. The log names the new iterator regression and the original common-action
control. It does not report a fresh run of all 17 tests in the current file.

The old candidate's 16-regression and 10-legacy-control results remain historical.
Their initial receipts omit child cwd/imported-path custody; the final focused
receipt supplies that detail for its two actual controls. This review does not
upgrade historical counts into a stronger source-custody assertion.

[The manifest readback](MANIFEST-READBACK-02.json) checks all 47 owned entries.
[The baseline readback](BASELINE-READBACK-01.json) verifies all 16 retained prior
files and the four original SHA256/byte/Git-blob bindings. The independent
[in-memory patch readback](PATCH-READBACK-02.json) reconstructs the exact final
helper/test bytes and the declared formal-text digest, and confirms both
component patches agree. Its small valid/invalid-context controls are retained
in [the reader](patch_readback.py).

The early concurrent readback is retained as INCOMPLETE, not PASS. The original
iterator witness, writer RED, old candidate and focused correction receipts
remain available. Source and result generations were not overwritten by review.

Only one independent bounded pure-helper witness was executed, on the old
candidate. Final closure uses source inspection and retained correction data;
no final helper suite, research, native verifier, learner or corpus run occurred.
The root owns live-branch matching and any later integration/publication decision.
