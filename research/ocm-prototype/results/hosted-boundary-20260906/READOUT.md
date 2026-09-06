# Qualification readout

| Observation | Result | Evidence |
|---|---|---|
| Claude 2.1.228, Fable 5 requested | Nine MCP tools, no builtin extras | catalogues/claude-billy.json |
| Claude 2.1.258, Fable 5.1 requested | Nine MCP tools, no builtin extras | catalogues/claude-billy-old.json |
| Direct native stage | Passed; two-process memory/proposal retention | controls/direct/ |
| Old-to-native SSH transport | Passed; inputs/source/model bindings unchanged | controls/ssh/ |
| Fable 5 READY | Authentication failure; exit 1, zero reported tokens/cost | availability/billy/ |
| Fable 5.1 READY | Authentication failure; exit 1, zero reported tokens/cost | availability/billy-old/ |
| Fresh minimal CI environment | 3 passed in 0.04 s, no skips | tests/offline-fresh-ci-v1* |
| Ordinary N1/G1 collection | 96 passed in 14.24 s, no hosted/archive tests, no skips | tests/ordinary-ci-v1* |
| Publication offline selection | 3 passed in 0.05 s | tests/offline-current* |
| Historical portable-path V3 controls | 8 passed in 5.54 s, no skips | tests/full-v3* |
| Memory-path V4 regression | Before: 4 failed, 2 passed. After: all 6 passed | tests/memory-path-v4-* |
| Current V4 full/offline controls | 14 passed in 5.61 s / 9 passed in 0.06 s; no skips | tests/memory-path-v4-receipt.json |
| Historical full tests | 8 passed in 5.59 s; revised controls 8 in 5.52 s | tests/ |
| Codex supported-switch revival | Four residual builtins; boundary refused | catalogues/codex-*-refusal.json |

Catalogue captures used dummy credentials and a local stub, with no provider
inference. Requested model labels and synthetic error messages do not establish
actual backend identity. The CLI's result subtype says success in authentication
failures; is_error=true, exit 1 and absent backend identity determine these negatives.
All reported usage events, cached-token counts and numerical costs remain visible.

UDPipe and cvc5 provide donor cognition; Z3 is an exact checker. MCP, SSH,
Bubblewrap and output custody are infrastructure. No Transformer supplies
cognition to the native stage. Syntax output is a checked structural observation,
not gold-certified truth. COMMITTED means one selected output was stored.

The native Bubblewrap namespace excludes repository, gold and actor home and
has no network. The authenticated client remains outside that OS namespace.
Actual catalogue and canary controls support only the tested client configuration;
these are not guarantees against arbitrary compromised clients or processes.

The public examples are one small syntax sentence and one CLIA goal, not the
105-item matched benchmark. No comparative capability, non-inferiority, lifelong
learning or whole-lifetime efficiency claim follows from this packet. Control
wall/CPU costs are descriptive and do not include all environment setup costs.

V1/V2 receipts retain their earlier source bindings. V3 binds its source generation
after one test-file change: OCM_HOSTED_MODEL_PATH selects the fixed-hash donor at
an explicit path. The actual eight-test run used a different temporary path and
passed without skips; the donor bytes were unchanged. Its original test bytes
are preserved in bindings/test_hosted_native.pre-portability.py. The SSH route
retains its V2 controls; no new hosted cognition or SSH qualification is claimed.
The pre-portability three-test offline record remains separate.

The initial CI exposed a missing sexpdata dependency that the earlier complete
hosted environment concealed. The fresh environment now contains pytest, sexpdata
and their test dependencies only; solver/MCP/UDPipe packages are absent. Ordinary
N1/G1 CI excludes host-only tests and archived source before collection. The
three original offline validators remain covered separately alongside the new controls. See
[CI correction receipt](tests/ci-fix-receipt.json); historical controls are unchanged.

V4 fixes memory-directory validation before path resolution. Four synthetic
root/ancestor symlink cases failed to be refused by the prior source; the fixed
source refuses all four without creating the stage or changing target contents.
Two ordinary-directory controls preserve new-directory creation and existing
memory resume, including a relative path. Full V4 re-executes the original eight
boundary controls plus these six; offline V4 executes nine checks with no skips.
Stable operator-owned paths are required; concurrent filesystem mutation is
outside this guard's claim. No SSH, READY or provider request was repeated.
The prior stage, README and source binding are preserved under bindings/.
