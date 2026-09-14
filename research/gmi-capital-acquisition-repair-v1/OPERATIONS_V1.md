# Operate the standalone unit

Run on laptop billy with Python3.12. No native VM, protected dataset, ecology,
historical population census, network source fetch or external service is invoked.

```sh
python3.12 -I -B /absolute/unit/replay_v1.py > /tmp/gmi-capital-replay.json
python3.12 -B -m unittest discover -s /absolute/unit -p 'test_*.py' -v
python3.12 -O -B -m unittest discover -s /absolute/unit -p 'test_*.py' -v
```

Keep redirected output and test scratch directories outside the frozen unit.
The replay checks complete regular-file membership/content, preserves initial
manifest/receipt bytes, runs the isolated checker, repeats custody verification,
and compares the complete original stdout bytes. No receipt field is projected.
Native replay of an alternate root through an already imported module is refused;
run that copy's own entrypoint. Sources and interpreter execution are assumed
trusted; hashes are tamper evidence, not independent host/time attestation.

The original K2 receipt is retained in full without rerunning its populations.
The original deferred selector is executed only for its three exact supplied
price tables and the parser's empty-set falsifier. This is finite arithmetic.
The new staged assay executes only the authored integer machine. Artifact-export,
observer serialization, Python administration and physical costs are unmeasured;
all claimed costs are the complete named operations of its abstract meter.
