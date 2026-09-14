# Replay the complete frozen unit

Use CPython 3.12 with the declared nonspecialized opcode layout. The checker
validates that layout and the three registered parity-3 facts before reporting
anything, and raises rather than restating different numbers under the same
theorem name. No dependency installation and no timing run is involved.

From this directory:

```sh
python3 -I -B check_frontier_v1.py
python3 -I -B -m unittest discover -s . -p 'test_*_v1.py' -v
python3 -O -I -B -m unittest discover -s . -p 'test_*_v1.py' -v
```

`check_frontier_v1.py` emits the complete payload in about three seconds and it
must equal `RECEIPT_V1.json` byte-for-byte after canonical JSON serialization.
The capsule checker `grand_gmi_threshold_task_frontier_checks_v1.py` in
`research/gmi-grand-unification-v1` performs exactly that comparison.

The slow half of TT-4 — the exhaustive search for an arithmetic-form minimal
rendering of majority-4, which finds none — lives in the test file rather than
in the checker, because it takes about half a minute and the capsule allows each
checker one. Its declared intermediate-magnitude cap is `N4_ARITHMETIC_CAP` in
that file; the same answer is obtained at every cap from 4 to 64.

This unit imports `typed_program_v1`, `typed_machine_v1` and
`cost_contracts_v1` from `research/gmi-delegation-cost-repair-v1` so that the
costs here are produced by the same instrument that produced the registered
parity-3 facts. Its own directory precedes that one on `sys.path`, because both
units contain a file named `check_v1.py`-like entry point; the entry point here
is deliberately named `check_frontier_v1.py` to remove the ambiguity.

The manifest covers every payload member but never itself; the parent register
binds its exact SHA separately. `constant_cells` is a count of integer cells in
constants and registered data bindings. It is not bytes, not resident memory and
not a physical cost, and TT-6 states only what follows from charging that count.
