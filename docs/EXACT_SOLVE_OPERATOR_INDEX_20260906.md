# Exact operator selection in the real solve path

This is experimental apparatus for issue #115 (operator selection and scaling).
It adopts ordinary exact indexing; OCM novelty is not established by this change.

## Serving contract

`SolveOperatorIndex` accepts the actual `runtime.solve.OperatorSpec` catalogue.
Pass this reusable sequence to `OCMRuntime.solve(task, index)`.
Each operator is posted under its least frequent required input. All structurally
applicable operators necessarily have that anchor in the active field; a final
full-input subset check removes false candidates. Output preserves supplied
order and duplicate entries, including the incumbent first-passing policy.

The index does not decide warrant, liveness, scope, authorization or correctness.
The original runtime checks execute after selection. Revocation is read fresh;
a catalogue change requires a new index. Empty-input and broadly applicable
operators can require global work and are counted explicitly.

Cold build counts are exposed by `index.build_work`; warm candidate counts are
in the real composition-stage trace. Neither is a complete runtime work ledger.

## Exact controls

Tests exhaust input subsets and duplicate ordering; execute the actual solve
and restarted runtime; withdraw the first candidate's evidence; forbid catalogue
iteration/atom copies on the selected path; and cover a genuinely global catalogue.
Dense navigation and other whole-field preparation remain visible limitations.

## Matched scaling experiment

Run on a compute host with the repository interpreter and `PYTHONPATH=src`:

```sh
python research/operator_selection_scaling.py --output operator-selection.json
```

The same ordered catalogue, active inputs and operator objects go to both arms.
The scan and index must return exactly equal tuples on every timing repetition.
Order alternates. Sizes are 1,000; 10,000; 100,000; 1,000,000. Cold acquisition,
index construction, warm selection, and full rebuild after catalogue growth are
separate. A global zero-input control must examine all candidates.

This study can establish component selection scaling. It cannot establish
whole-machine active-subspace execution, better training economics, or general
capability. The compilation crossover is an estimate for this stationary
selection workload; storage, later changes and all other stages must be charged
in the eventual lifetime experiment. Process peak RSS includes both arms and
rebuild, so it is not the size of the index alone.
