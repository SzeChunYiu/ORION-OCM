# Reproduction and custody

Run only on a permitted compute host. This unit uses Python3.12 standard
library. No native VM, protected ecology or campaign entrypoint is invoked.

From the repository root (substitute its explicit Python3.12 binary):

    python3.12 -I -B -m unittest discover -s research/gmi-hierarchical-chunking-repair-v1 -p 'test_*v1.py'
    python3.12 -I -B -O -m unittest discover -s research/gmi-hierarchical-chunking-repair-v1 -p 'test_*v1.py'
    python3.12 -I -B research/gmi-hierarchical-chunking-repair-v1/replay_v1.py > /tmp/gmi-hierarchy-replay.json
    python3.12 -I -B -O research/gmi-hierarchical-chunking-repair-v1/replay_v1.py > /tmp/gmi-hierarchy-replay-optimized.json

Outputs must stay outside the frozen unit. The replay compares the entire
original and repaired payload with RECEIPT_V1.json, and rechecks strict whole
membership and original manifest/receipt bytes after the worker. Symlinks,
nonregular entries, missing/extra files, drift and self-consistent mid-run
rebinding are refused. Alternate imported source roots are refused before work.
The manifest is a content-consistency anchor; Git/transport identity supplies
external provenance, not a claim of arbitrary-host authentication.

All five original files and four parents have exact commit/path/blob/SHA
bindings. The two original scripts are executed byte-for-byte in temporary
folders and their whole retained JSON is compared. Normal and optimized child
flags match the parent interpreter mode. The checker also preserves stdout.
No original script or original receipt is rewritten.

The synthetic suite proves finite calculation consistency and refutes the
identified implications. It does not authenticate unknown physical prices,
prospective sampling, learned-state coverage or general hierarchy capability.
