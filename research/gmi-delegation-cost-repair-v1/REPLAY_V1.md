# Replay the complete frozen unit

Use CPython3.12 with the declared nonspecialized layout. Run on laptop billy,
not the Mac. No dependency installation, candidate search or ecology execution
is needed; only deterministic finite program controls run.

From this directory:

```sh
python3 -I -B -m unittest discover -s . -p 'test_*v1.py'
python3 -O -I -B -m unittest discover -s . -p 'test_*v1.py'
python3 -I -B raw/test_grand_gmi_delegation_invariant_cost_v1.py
python3 -O -I -B raw/test_grand_gmi_delegation_invariant_cost_v1.py
python3 -I -B replay_v1.py
python3 -O -I -B replay_v1.py
```

`check_v1.py` emits the complete original and repaired payload. `replay_v1.py`
checks exact member hashes before and after an isolated checker, anchors the
initial manifest bytes and compares the entire emitted payload byte-for-byte.
It cannot accept a later self-consistent manifest rewrite. Output files must
be stored outside this immutable directory. A changed layout, incomplete
monitoring, unknown dispatch or failed comparison cannot produce PASS.

The manifest covers all payload members but never itself. The parent register
must bind its exact SHA separately. `NATIVE_VALIDATION_V1.json` identifies the
validation interpreter; portability of a payload is not historical binary
identity or custody authentication. Contract dictionaries remain explicit
mathematical premises, not automatically verified physical certificates.
