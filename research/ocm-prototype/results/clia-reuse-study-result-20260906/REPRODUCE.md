# Reconstruct exact raw records; never rerun actors

The model-less archive contains all three original attempt directories, their
executed source snapshots, original seals and external grades, plus retained launch
and supervisor records. No model binary is in git. Original full local ZIPs remain
unchanged; the archive here provides portable reconstruction without those ZIPs.

The single exact model is available from the existing
[G1 development release](https://github.com/SzeChunYiu/ORION-OCM/releases/tag/g1-development-model-20260906).
Download ewt-train-default.udpipe from the fixed URL in raw/MODEL_LOCATORS.json,
or reuse the existing local file. Require 11,631,918 bytes and SHA256
7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9.
Retain the release's CC-BY-SA-4.0 notice, attribution and weights notice.
The original data/software retain their respective licenses. No new model download
or inference is required to verify this result.

Use the original G1 Python and pinned requirements-g1.txt dependencies. An ordinary
system Python 3.8 is unsupported. The recorded actor environment is bound by each F0;
the original outer supervisor reporting error is not corrected retroactively.

From this packet directory:

```sh
sha256sum -c SHA256SUMS
python REPLAY.py --packet "$PWD" --out /absolute/new/replay-directory \
  --model /absolute/ewt-train-default.udpipe --python /absolute/g1-env/bin/python
```

Run REPLAY.py itself with the supported G1 Python, not an unrelated system interpreter.
The output directory must be new. The script adopts the small Stanza result replay
pattern from commit 7be5976: relative-file-only extraction, exact byte inventories,
model rehydration, frozen external grader and an independent changed-raw control.
Adaptation is limited to this existing archive's paths, one model, three attempts,
and this grader's exact outputs. It is not a new actor or evaluation framework.

The archive omits five model occurrences and retains 899 file records overall.
Hardlinks rehydrate exact local weights where possible; otherwise the script copies.
It verifies every reconstructed file, each original capture seal, source snapshot,
receipt and original grade. It then runs only each archived external grader.
No actor, solver acquisition or trained-model prediction is rerun.
Grades must reproduce exactly, with no fields excluded from the comparison.
The incomplete v1/v2 grader exits remain 2 and the complete v3 exit remains 0.

The no-alarm control uses the real v3 grade; a separate copy with an added newline
must be refused by the same byte verifier used for reconstruction.
Original and reconstructed raw records remain byte-identical.
Missing or changed model, archive or raw bytes yield CANNOT_CHECK_REPLAY.
Never rewrite the original seals to accommodate relocation or missing files.

Historical absolute actor paths remain inside original inputs and receipts.
The archived grader binds those original paths lexically and reads relocated
content through the original relative capture manifest.

controls/ includes the selected immutable CI audit/log/source context and the
subsequent successful clean-environment fixture control. Duplicate source copies
from the original read-only CI audit are omitted; its exact commit/blob identities
remain in those records. Current test source is a post-capture portability fix.
Neither this later test nor a later main integration changes the executed F0.

New reconstruction/regrading resources belong to verification and are reported
separately from original actor resources. Complete lifetime efficiency remains unchecked.

The actual fresh-root reconstruction passed: 899/899 files and 111,786,634 logical
bytes verified, including five rehydrated occurrences of the one exact model.
All three external grades reproduced byte-identical SHA256 values; no fields were
excluded. The real-grade no-alarm and changed-copy refusal both passed.
See replay/REPLAY_RECEIPT.json and replay/CUSTODY_CONTROL.json.

Existing strace observed each frozen grader importing its four grading/helper
modules from reconstructed source and opening its reconstructed capture manifest.
No child attempted to open an original capture or the current repository.
The selected raw traces and binding are included under replay/. An initial audit
selection failed because default strace argv strings were truncated; the corrected
audit used complete openat pathnames. That diagnostic failure is retained, and
no grading process was rerun to correct it.

Measured reconstruction/regrading was 2.056904 s under strace; wrapper self CPU
0.818834 s and reaped grader-child CPU0.655435 s are separately observed scopes.
These are new verification costs, not replacements for original missing measures.
