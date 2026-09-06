# Exact runtime, state and measured setup

The original35 Stanza1.14.0 / Torch2.14.0+cpu package records are preserved without version or artifact changes.
Only cvc5 1.3.4, z3-solver 5.1.0.0 and sexpdata 1.0.2 were added in a separate environment.
runtime/runtime-lock.json records the exact additions and original lock SHA.
runtime/requirements-runtime.lock preserves the original requirements bytes as its prefix and adds three hash-pinned wheels.
The original qualified environment was untouched. No model binary is copied into Git.

Reproduction on the qualified laptop uses:
    /home/billy/.local/bin/uv venv --python <qualified Python3.13.12> <new environment>
    /home/billy/.local/bin/uv pip install --python <new environment>/bin/python --require-hashes --no-deps -r runtime/requirements-runtime.lock

The Stanza wheel entry retains its original custody file URL; obtain that exact qualified wheel at that path or map it
to a byte-identical local copy before replay, preserving SHA b5e81d742e39671de146e69f3c6ca7ff76cc4201ed07cab3083d815b2cbab544.
Original qualification records and provenance are in the preceding stanza-native-qualification-20260906 packet.

Observed installation:80.760733s wall; reaped direct-child CPU5.850189s, whole process-tree CPU UNKNOWN.
The initial executable lookup failed because uv was absent from the non-login SSH PATH.
The retained revival used the already-installed absolute uv binary, without upgrading any tool.
The import auditor initially expected archive hashes in installed direct_url metadata; uv recorded an empty archive_info.
That operational failure is retained. The corrected audit checks actual versions and source URLs, while artifact-hash
validation is attributed to the successful --require-hashes installation, not nonexistent installed metadata.
The two exception records transcribe actual tool failures; they are not reconstructed successful executions.

The corrected import/custody-only probe passed without loading a model or importing OCMRuntime.
Its observed wall3.188398s/self CPU4.82547s/RSS392676KiB concern that unconstrained import process, not one-CPU performance.
Installed regular files at that point:19319 /1006036381 bytes. No fresh hash of every installed file is claimed.

Exact model closure:
- Four checkpoints:241742165 bytes, including dictionaries and vocabularies.
- Model resource metadata:457371 bytes.
- Fixed profile:10977 bytes.
- Complete per-arm shared archive:242210513 bytes before evidence/memory state.
- Source closure:171 files /1316610 bytes; bound in controls/source-prior-inventory.json.
- Source bytes are not a measure of cognitive complexity.
- Transient compiled pipeline bytes:UNKNOWN; process RSS and durable state-file bytes are reported by the worker.
- Original imported training, tuning, failed attempts and exposure:partly unknown; never zero-cost or TRAIN-only.

The capture reports prelaunch bindings and full capture-body wall/self CPU, plus outer worker wall and direct-child CPU.
Workers report their own CPU and waited children separately; whole process-tree CPU is UNKNOWN.
The future single-CPU run should use standard taskset around the outer capture so child solvers inherit the same affinity.
The successor105 plan must be freshly registered and source/runtime/profile bound before prediction.
This packet itself authorizes no actual run.
