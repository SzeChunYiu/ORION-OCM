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
| Current portable-path full controls | 8 passed in 5.54 s, no skips | tests/full-v3* |
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

V1/V2 receipts retain their earlier source bindings. V3 binds the current sources
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
three explicit offline validators remain covered separately. See
[CI correction receipt](tests/ci-fix-receipt.json); historical controls are unchanged.
