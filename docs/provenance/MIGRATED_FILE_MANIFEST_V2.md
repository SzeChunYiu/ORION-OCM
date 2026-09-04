# Generated migrated-file manifest — M0 V2

The original `MIGRATED_FILE_MANIFEST.md` is the complete path inventory produced by the migration commit. M0 binds every listed path to two immutable identities:

- frozen ORION-V2 source commit: `42b1b0d1ab5920a69036e1c782c6b84c92c3b4d3`;
- local migration mirror commit: `430708103525f567633e377f015a7113633d709d`.

The entire `research/orion-machine` subtree at the migration mirror has Git tree SHA `9f04028706dfc70dad4606491c84eed72bba753c`, exactly the frozen source subtree SHA. The checker recomputes source-mirror and destination SHA-256 plus Git blob identity for every listed file and refuses drift.

```bash
python tools/m0_manifest.py --check --write /tmp/MIGRATED_FILE_MANIFEST_V2.json
```

Historical files are never rewritten to make a check pass.
