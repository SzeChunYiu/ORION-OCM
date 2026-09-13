# Operating the versioned repair

Run these commands on laptop billy or another explicitly registered Linux
host. The launcher refuses Mac execution. Use one retained registry for every
checkout on the host; an existing reservation is not removed for a retry.

## Static validation, no measurements

From the repository root, run the focused tests with an explicit CPython3.12:

    /home/billy/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3 -B -m unittest discover -s research/gmi-parity-custody-repair-v1 -p 'test_*.py'

Repeat with -O -B for the optimized gate.
Tests replace the measurement invocation. They do not run V5 timing loops.
Two historical integration tests report a skip if their recorded matching
interpreter locations are absent; a skipped test is not verified replication.

countercontrols_v1.py replays the two old defects with synthetic data.
Its optional --out destination must not exist. The tracked countercontrol
receipt is preserved, so use a temporary output for a later replay.

For an individual historical packet, invoke audit_imported_v1.py with the exact
recorded CPython release and the packet path. This is a static source/bytecode
and evidence audit; it performs no candidate calls.

Cross-audit historical packets with cross_envelope_v6.py. Supply each matching
absolute interpreter path with --python, and each admitted raw packet path
with --historical-packet. The three admitted packet filenames and hashes are
listed in raw/IMPORTED_V5_PACKET_BINDINGS_V1.json. The optional --out path must
not already exist. A missing matching interpreter produces UNVERIFIABLE.

For newly recorded attempt directories, pass those directory paths as
positional arguments to cross_envelope_v6.py and supply matching --python
paths. It requires matching executable hashes for this new custody route.

## A future first measurement

No measurement has been executed through this repair.
A deliberate future first attempt can be launched from the repository root:

    /home/billy/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3 -B research/gmi-parity-custody-repair-v1/attempt_custody_v1.py --registry /home/billy/ocm-verify/parity3-v5-attempt-registry --host-label laptop-billy --execute-first-attempt

The registry path is a campaign-level commitment. All other checkouts on
that host must use the same retained path. A display label does not determine
first-attempt identity; the machine identity and interpreter version do.

Keep the complete emitted directory: reservation, copied frozen sources,
packet, stdout, stderr and completion record. Exit zero means the subprocess
emitted a non-invalid V5 packet; the subsequent static audit is still required.
Exit two retains an invalid/process/launch failure. An abrupt interruption may
leave only a reservation and partial artifacts; its key remains occupied.

Commit the complete attempt directory before scientific reporting.
Do not delete a failed reservation, relabel it as success or infer that the
local hash chain independently authenticates the host. A changed instrument
or genuine protocol revision requires its own versioned authority.

## Custody limits

The copied V5 instrument and registration remain the measurement authority.
Custody V1 changes launch and record handling; Cross Audit V6 changes
evidence validation. Neither changes candidates, timing schedule, resource
coordinates, development-cost exclusion or the frozen observed-envelope rule.

[MANIFEST.json](MANIFEST.json) binds every file in this correction unit except
itself; its digest is recorded at integration. It is not a self-authenticating
signature or a retroactive first-attempt certificate for the historical data.
