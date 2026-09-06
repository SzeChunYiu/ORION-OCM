# Replay consistency repair: current engineering evidence

Owner: #72 / #38 / #49. Classification: INFRASTRUCTURE.
**133 focused and 1,003 full tests passed; all 12 current wrappers verified.**
No scientific promotion, independent replication, or protected reevaluation.

This packet records unchanged repository gate recipes executed against source commit
`0e49a04e8a2cd81dc352774f049395779cbe85a6` after the two missing live reducer
applications were repaired. The research adapter repair is covered separately by the
source commit's scoped research controls; research files are outside this generic inventory.

- Source inventory: `fcdced8ec927465c45d13058a7da471da8ac019b24d158f82dc8d3d67bf436bd`, 310 files.
- Current receipt: `e4dc56b5ec2c23b453bb92c056c8e6420d34f96f8c919a0b085a3299be13ad7b`.
- [Selected immutable run](../runs/fcdced8ec927465c45d13058a7da471da8ac019b24d158f82dc8d3d67bf436bd/044adda70c734a79/RECEIPT.json).
- [Source archive](../sources/fcdced8ec927465c45d13058a7da471da8ac019b24d158f82dc8d3d67bf436bd.zip).
- [All wrapper executions and custody verification](raw/verification.json).
- [Pre-execution source/history inventory and previous pointer](raw/before.json).

Only runtime `src/ocm/runtime/ocm_runtime.py` changed within the previous c90 source
inventory, plus the new `tests/m2/test_event_reducer_consistency.py`.
The final inventory equals the initial inventory. All 230 previously tracked provenance
files other than the replaceable pointer remain byte-identical, including prior runs
and V1–V5 historical receipts. The V5 wrapper verified archived custody only.

## Preserved environment failure and revival

[First attempt](../runs/fcdced8ec927465c45d13058a7da471da8ac019b24d158f82dc8d3d67bf436bd/b5ea4473e8ce4f49/FAILED.json):
127 focused tests passed and six distribution fixture setups errored because g1-env
lacked setuptools. It stopped before the full gate and left the previous pointer unchanged.
The failure, XML, logs and original outer receipt remain intact.

Revival used the existing receipt-env with Python 3.13.12, pytest 8.3.5,
setuptools 75.8.0 and wheel 0.45.1. No environment, source, recipe or test was modified.
[Environment evidence](raw/revival-environment.json) binds imports to this checkout.
The revived focused gate passed 133 cases in 34.596 s; the full gate passed 1,003
in 231.158 s, with zero failures, errors or skipped cases.
The recorder completed in 266.296 s; the failed attempt took 31.377 s.

Raw per-gate child CPU observations and outer direct-child observations have separate
scope. Total process-tree CPU remains UNKNOWN; energy, setup and development costs
are unmeasured. These are engineering execution costs, not capability-study measurements.

## Reproduce current verification

From the repository on the compute laptop, use the recorded interpreter:

    PYTHONPATH=src /home/billy/orion-director-work/20260906/receipt-env/bin/python tools/m1_receipt.py --verify
    PYTHONPATH=src /home/billy/orion-director-work/20260906/receipt-env/bin/python tools/m12_receipt.py --verify
    PYTHONPATH=src /home/billy/orion-director-work/20260906/receipt-env/bin/python tools/m12_paired_v5_receipt.py --verify

A future source change requires a new actual recorder run under the existing
[protocol](../README.md); none of these immutable records should be rewritten.
No prospective acquisition, model inference or repair of the failed reuse-v2 ledger occurred.
