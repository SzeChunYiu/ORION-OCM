# Static validation

Use Python3.12 or later from the repository root, with bytecode disabled:

```sh
python3 -B -m unittest discover -s research/gmi-fresh-ecology-evidence-v1 -p 'test_*.py' -v
python3 -O -B -m unittest discover -s research/gmi-fresh-ecology-evidence-v1 -p 'test_*.py' -v
python3 -I -B research/gmi-fresh-ecology-evidence-v1/replay_v1.py
python3 -I -O -B research/gmi-fresh-ecology-evidence-v1/replay_v1.py
```

The full output must match RECEIPT_V1.json byte-for-byte. The manifest covers
all regular files except itself. The worker cannot replace the original
manifest or rebind modified files during replay. Symlinks and extra files
(including bytecode caches) are refused. Hashes are content custody, not
independent historical execution/host authentication.

The unit imports only its small static modules and the Python standard library.
Archived source is read/hashed and never imported. No ecology, candidate,
priming, gradient, search or timing experiment is invoked.
Validation host/interpreter and exact commands are retained in
raw/validation/VALIDATION_V1.json. CPU work for parsing, hashing and finite
arithmetic is validation overhead, not a measured campaign/lifetime cost.

To inspect the source boundary, follow raw/SOURCE_BINDINGS_V1.json.
The original preregistration and amended result note are separate byte-exact
copies. Their ordering is a Git ancestry fact; no claim of sealed randomness
or execution chronology is added.
