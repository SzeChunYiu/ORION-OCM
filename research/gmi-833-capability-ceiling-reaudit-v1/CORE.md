# Capability-definition and ceiling re-audit v1

Issue #918, child of #833 Section K. This package:

- gives every pinned A4 row a semantic disposition, accepting 11 original operational contracts and replacing mechanism-bearing fields in 16 rows through a separate normalized 27-row external contract;
- reconstructs the exact eleven historical F2 ceiling IDs and re-proves scope-correct versions;
- records three necessary corrections: code-carrier precision, direct positive verification, and exact-linear/explicit-first-order rank scope;
- separates analytic arbitrary-set or non-toy theorems from small executable witnesses.

Reproduce:

```bash
python3 -I -B research/gmi-833-capability-ceiling-reaudit-v1/test_capability_ceiling_reaudit_v1.py -v
python3 -I -O -B research/gmi-833-capability-ceiling-reaudit-v1/test_capability_ceiling_reaudit_v1.py -v
python3 -I -B research/gmi-833-capability-ceiling-reaudit-v1/capability_ceiling_reaudit_v1.py
```

The original source remains byte-pinned. `ARCHITECTURE_NEUTRAL_CAPABILITY_CONTRACT_V1.json` is the normalized replacement contract, and the ledger records every changed field and both versions. Token scans and audit-label remints are not treated as semantic proof.

The executable census checks finite consequences and hostiles; the unrestricted statements stand on the analytic proofs in `CAPABILITY_CEILING_REAUDIT_THEOREMS_V1.md`, not on enumeration.

Claim ceiling:

`GMI_833_CAPABILITY_DEFINITIONS_AND_ELEVEN_CEILINGS_REAUDITED_AT_REGISTERED_SCOPE`

This is neither a capability predictor nor empirical validation, and it does not rank architectures.
