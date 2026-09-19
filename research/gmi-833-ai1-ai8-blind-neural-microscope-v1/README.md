# gmi-833-ai1-ai8-blind-neural-microscope-v1

Freeze-first AI1–AI8 known-family derivation microscope.

Reproduce:

```bash
python3 -I -B research/gmi-833-ai1-ai8-blind-neural-microscope-v1/check_ai1_ai8.py
python3 -I -O -B research/gmi-833-ai1-ai8-blind-neural-microscope-v1/check_ai1_ai8.py
```

The dedicated GitHub workflow additionally verifies that `FREEZE_V1.md` and `BLIND_PROTOCOL_V1.json` existed at freeze commit `34a6b5644ffe9f60b56d016ccc855cf766ebc9f4` before the generator/search/posthoc implementation.

Strongest allowed positive if all gates are GREEN:

`NN_D1_D2_D3_BLIND_RECOVERY_AT_REGISTERED_BINARY_TOY_SCOPE`

This is blind relative to the frozen causal-information denial and bias ledger; it is not a universal or literal-history claim.

Terminology custody note: the freeze text at commit `34a6b5644ffe9f60b56d016ccc855cf766ebc9f4` is the custody object. The only post-freeze edits to `FREEZE_V1.md` on this branch are two wording substitutions required by the repo-wide terminology ratchet (row AB37): `in the selection stage` -> `under the frozen selection law`, and the heading `Frozen selection/resource model` -> `Frozen selection law / resource model`. No task, prediction, budget, fingerprint or ceiling text changed; compare with `git show 34a6b5644ffe9f60b56d016ccc855cf766ebc9f4:research/gmi-833-ai1-ai8-blind-neural-microscope-v1/FREEZE_V1.md`.
