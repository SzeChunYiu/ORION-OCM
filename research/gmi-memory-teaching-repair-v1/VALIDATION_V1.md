# Finite validation and replay

All executable validation uses laptop CPython 3.12 with isolated imports and
bytecode writes disabled. The original eleven PR597 sources are read/hash-bound;
none of their scripts, learners or campaigns is executed.

Run from the unit directory with the chosen Python 3.12 executable:

    python3 -I -B -m unittest discover -s . -p 'test_*_v1.py'
    python3 -I -O -B -m unittest discover -s . -p 'test_*_v1.py'
    python3 -I -B replay_v1.py
    python3 -I -O -B replay_v1.py

The full receipt contains every new finite memory history/arm/trace and teaching
target/learner/event comparison, plus all four retained historical JSON records.
Exact rational values are serialized as strings. The ordinary and optimized
checkers must produce identical complete stdout bytes.

MANIFEST_V1.json binds every other unit file. Source bindings cover all eleven
pinned PR597 paths and nine parents. Replay saves the initial manifest and
expected receipt, runs the new checker in a fresh process, revalidates complete
membership, rejects changed authority, and compares full output bytes.
This supplies portable content custody, not remote publication or host identity.

Scientific controls compare actual query outputs with Boolean truth tables,
actual learner responses with a separate finite relation oracle, source-provided
records with a complete schema, and full event sums with break-even algebra.
Custody controls include a real packet no-alarm, raw/missing/hidden/special-file
changes, numeric-payload drift despite PASS, and self-consistent authority
rebinding during a mocked worker. That mocked worker executes no model.

No finite control proves a broader biological, physical or cultural claim.
The independent-bit growth and supremum/attainment statements have analytic
proofs; their small prefixes are illustrative countercontrols only.

Recorded result: 37 normal and 37 optimized tests passed on CPython 3.12.13.
The complete 250668-byte normal/optimized receipts are byte-identical.
The exact logs and current executable digest are under evidence/. This digest
identifies this validation runtime only, not an original PR597 campaign runtime.
Independent proof/core review accepted the scoped mechanisms; subsequent
custody read checks final content bindings without duplicating execution.
