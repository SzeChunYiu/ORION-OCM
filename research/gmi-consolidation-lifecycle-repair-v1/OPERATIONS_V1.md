# Operations

Linux CPython3.12, standard library only. Run from this unit:

    python3.12 -B -m unittest discover -s . -p 'test_*.py' -v
    python3.12 -I -B replay_v1.py > /tmp/gmi-consolidation-replay.json

Repeat with -O. Keep outputs and bytecode outside the frozen unit.
The checker executes only finite authored models and the archived16-history
script in a temporary directory. No native VM, ecology or campaign is called.

Replay verifies complete source membership, executes the checker, compares
the complete receipt and rechecks unchanged initial manifest/receipt bytes.
A changed source needs a new versioned receipt, never historical rewriting.
The custody boundary is a trusted local process; hashes do not attest a host.
