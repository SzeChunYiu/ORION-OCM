# Operations

Use Python3.12 on a Linux laptop. No package install is needed; every native
module executes from its verified archived source, independent of current imports.
These commands do not modify the live VM, historical runner or campaigns.

Retained-evidence audit (no native candidate execution):

    python3.12 -I -B replay_v1.py > retained.json

Explicit native exposed qualification and complete retained-receipt comparison:

    python3.12 -I -B replay_v1.py --native > replayed.json

Repeat with -O for optimized-mode validation. Default replay verifies complete
manifest membership/content before and after, retains the initial anchor, validates
full recorded ledgers/states/control payload and emits the entire original payload.
Native replay accepts only the imported unit root, so another directory cannot
be audited while this source silently executes. Static audit can take another root.
This is byte custody/consistency, not independent execution authentication.

Focused tests (these execute bounded exposed native controls):

    python3.12 -B -m unittest discover -s . -p 'test_*.py' -v

The receipt comes from qualification_v1.run, with all seven ecology attempts and
the fixed PROGRAM arm/experience controls. No protected experiment, ecology search
or historical campaign is launched. Tests also run no-alarm parent calls and small
hostile copies. Do not interpret test repetitions as independent evidence.

Evidence is canonical JSON compressed deterministically with gzip mtime0.
VALIDATION_V1.json binds source/receipt/runtime identity and retained command logs.
A manifest anchors every file except itself. Preserve the exact whole unit.
