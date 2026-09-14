# Isolated exact checks

Run on laptop-billy, with Python3.12 and this unit's working directory:

```sh
python3 -I -B test_causal_v1.py
python3 -I -B test_custody_v1.py
python3 -I -B replay_v1.py
python3 -I -O -B test_causal_v1.py
python3 -I -O -B test_custody_v1.py
python3 -I -O -B replay_v1.py
```

The scientific packet is authored and exposed. Its exhaustive rational checks
are not a prospective empirical campaign. Raw PR603 files are immutable.
Its eleven original static tests are rerun separately under the same runtime;
there is no native VM, protected capsule or hosted campaign execution here.

MANIFEST_V1.json binds every payload file, including raw records. replay_v1.py
rejects missing/extra files, links/nonregular members, changed authorities and
full-output mismatch. Receipt stdout must be exact; stderr must be empty.
The scientific tests use assertions in unittest that remain active under -O;
runtime contracts use explicit exceptions. Test logs live under raw/validation.
