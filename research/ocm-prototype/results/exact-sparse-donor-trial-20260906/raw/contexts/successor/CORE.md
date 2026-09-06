# G1 context: import-closure successor

Read SUCCESSOR_CONTEXT.json, then CONTEXT_MANIFEST.json and HOST_BINDING_MANIFEST.json.

This new directory retains the original field/task/config/revoked/input data and
helper bytes. It adds exactly the original f4 vendored CoNLL18 evaluator and its
NOTICE. All transitive evaluator imports are CPython standard library modules.

RESTORE_RECEIPT.json is the unchanged predecessor read-only restoration result,
not a new execution. No field loader, host binding, consumer or donor ran while
preparing this successor. Original context and failed trial remain unchanged.

The SHA256SUMS inventory binds this successor. The trial manifest separately binds
actual runtime distribution content and exact loaded module origins. Evaluator
import does not grant access to gold labels or execute its external scorer.
