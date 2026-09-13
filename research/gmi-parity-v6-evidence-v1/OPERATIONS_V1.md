# Static replay operations

Use Linux and matching CPython releases. This unit needs only the standard
library; it does not need a repository checkout after the directory is copied.

For one recorded release:

```sh
/path/to/python3.11 -I -B audit_v1.py --version 3.11.15
/path/to/python3.11 -I -O -B audit_v1.py --version 3.11.15
```

For all three, provide the interpreters explicitly:

```sh
python3 -I -B replay_v1.py \
  --interpreter 3.11.15=/path/to/python3.11 \
  --interpreter 3.12.3=/path/to/python3.12 \
  --interpreter 3.13.12=/path/to/python3.13
```

Add `--optimized` to use `-O` in every static child process.
Receipt output contains executable hashes but no location-dependent paths.
An all-three receipt can be compared byte-for-byte with the retained receipt
when the audit interpreters and source bytes match. A different binary can
successfully audit the same static records while producing a different audit
binary digest; do not call that byte-identical replay.

Exit codes: **0** complete pass, **1** rejected evidence, **2** unverifiable.
With no explicit mapping, only a matching current interpreter is used.
Any missing release remains UNVERIFIABLE and the aggregate does not pass.

Run focused tests with each available matching release:

```sh
/path/to/python3.11 -I -B test_v6_evidence_v1.py
/path/to/python3.11 -I -O -B test_v6_evidence_v1.py
```

Repeat for 3.12.3 and 3.13.12. On any other release the native packet class
explicitly skips as UNVERIFIABLE; archive and failure-path tests still run.
A skipped native class is not an audit of a historical packet.

The archived experiment harnesses contain original measurement entrypoints
because their exact bytes are evidence. **Do not invoke those entrypoints.**
All supported commands above invoke only this unit's static audit code.
Do not run the historical scratch script or pass experiment execution flags.
