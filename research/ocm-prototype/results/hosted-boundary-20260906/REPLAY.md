# Replay and launch conditions

## Offline checks

From repository root, create an isolated Python 3.13 environment and install
pytest==8.3.5 into it. No project installation or src change is required. Run:

```sh
PYTHONPATH=research/ocm-prototype PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  research/ocm-prototype/test_hosted_catalogue.py::test_catalogue_refuses_unexpected_builtin \
  research/ocm-prototype/test_hosted_claude.py::test_claude_catalogue_rejects_every_extra_or_missing_tool \
  research/ocm-prototype/test_hosted_native.py::test_public_schema_rejects_extra_outcome_fields
```

These three named tests use no network, client executable, credentials or model.
The dedicated CI job uses a separate temporary environment and the same selection.

Embedded hashes in sanitized receipts bind their original bytes. SHA256SUMS
binds the published copies. See origins.json for that mapping; do not replace
an original binding by a sanitized-copy hash or claim byte-identical raw replay.

## Native/client qualification

Use a separate Python 3.13 environment with ../../requirements-hosted.txt,
Bubblewrap, the trained UDPipe model with SHA256
7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9, and
explicitly pinned installed client versions. Set OCM_HOSTED_MODEL_PATH explicitly;
the original laptop path remains the fallback. Model SHA verification is fixed.
From repository root, with the full isolated hosted environment active:

```sh
OCM_HOSTED_MODEL_PATH=/path/to/ewt-train-default.udpipe \
PYTHONPATH=research/ocm-prototype PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  research/ocm-prototype/test_hosted_claude.py \
  research/ocm-prototype/test_hosted_native.py \
  research/ocm-prototype/test_hosted_catalogue.py
```

These full controls require the declared installed clients and Bubblewrap and
use local dummy-provider captures. They are not the offline CI selection.
Model/environment binaries are excluded from this package. Staging requires its
Python 3.13 dependency closure and copies only the declared native tool sources.

Reuse hosted_stage.stage and mcp_config, hosted_controls.exercise and
namespace_controls, and hosted_claude.audit_catalogue. The SSH route uses its
explicit fixed transport wrapper; do not paste placeholder-bearing receipt
commands as executable commands. Replace roots by an operator-selected location.
Catalogue qualification uses dummy credentials/local stub, not hosted cognition.
Do not run the READY calls as part of CI or an automatic replay.

## Before a future benchmark

An actually available authenticated route remains unestablished. No login, token
movement, refresh, client upgrade or fallback is performed by this publication.
After availability is established, freeze the exact model/effort/client, complete
catalogue, task/tool contracts, retries and deadlines before any benchmark output.
Use a fresh actor cwd and pristine first memory; preserve only that benchmark
memory across its five chunks. Bind inputs/source/model before and after chunks.
Allow selecting donor proposals or submitting a custom answer. Grade externally;
include missing, refused and invalid outputs. Keep original costs and failures.

The existing command builder cannot enforce its caller's cwd; the launcher must.
The authenticated client is not OS-isolated. These limitations remain explicit.
