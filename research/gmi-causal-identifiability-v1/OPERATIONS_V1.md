# Focused verification

From this unit directory, use CPython 3.12 on Linux:

```sh
python3.12 -I -B test_causal_identifiability_v1.py -v
python3.12 -I -O -B test_causal_identifiability_v1.py -v
```

The test entrypoint compiles its sibling model from source and needs no ambient
Python path or GitHub environment. It generates only exact finite probability
tables. It does not execute physical candidates, collect measurements, run
searches or invoke the grand capsule.

The repair receipt binds the source and retained logs from the actual normal
and optimized runs, including the interpreter version and binary digest.
It records this validation, not an interpreter-independent historical replay.
The original PR570 source remains unchanged under raw/pr570-1277d0e8/.
