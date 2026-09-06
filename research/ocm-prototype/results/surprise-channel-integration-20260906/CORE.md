# Surprise-channel repair: integrated engineering result

Owner [#72](https://github.com/SzeChunYiu/ORION-OCM/issues/72#issuecomment-5558295754).
Classification: INFRASTRUCTURE. Terminal: ENGINEERING_REGRESSION_ONLY.

The mode-matched surprise repair passed current engineering qualification after
normal integration of main b5b0865fe31025e85f4b197609d7dcad6f3ca1fd.
The prequalification merge is ee5956a08e37e92744d3dd7fd5a823a32c1d8eb9.
The only production delta from that main is the reviewed solve.py channel pairing;
the added regression test checks independently known backgrounds and authority.

[Original cause and red/green controls](../surprise-channel-repair-20260906/CORE.md)
remain unchanged. That packet records the earlier, preintegration stage.
This packet records the subsequent current-source qualification.

## Executed result

- Fixed focused recipe: 133 passed, no failures/errors/skips; 31.867 s in JUnit.
- Fixed full recipe: 1,044 passed, no failures/errors/skips; 216.762 s in JUnit.
- The 25 current vendored targets passed the existing checker with its explicit
  CURRENT manifest. solve.py is not a listed target; neither manifest was edited.
- All twelve current engineering wrappers and protected V5 archive custody passed.
- Every prior tracked provenance file, except the replaceable current pointer,
  and every original repair-packet file remain hash-identical.
- The 313-file source inventory stayed identical throughout execution.
- No protected evaluator, scientific study, model inference or performance rerun.

Source inventory: c51651b20edc8ddaef458c691245abc945e96e58f6c4700f9b14266826487f7f.
Selected receipt: 9c1c6feaf4d0ef2272c28e2a26c2523790e28278f1dfac6da5efda5cfb509d04.
[BINDINGS.json](BINDINGS.json) binds the exact source, selector, receipt and archive.
[Raw qualification](raw/qualification.json) and [verification](raw/verification.json)
give commands, custody checks and links to the immutable gate logs/XML.

## Environment and costs

Python 3.13.12 on laptop billy, using the existing receipt-env and fixed gate recipes.
The recorder supervisor observed 250.080 s wall, 210.163 s child user CPU and
10.748 s child system CPU. These are scoped RUSAGE_CHILDREN observations, not an
independently established total process-tree cost or a performance comparison.
Gate-specific wall/CPU are retained in the selected receipt.
Energy, installation and development costs remain unmeasured.

The repaired navigation performs and charges four fixed-point computations.
Older three-computation timing does not qualify this source.
Scientific promotion remains NOT_ESTABLISHED; protected reevaluation is NOT_RUN.

## Verify the preserved result

From this checkout with its Python test dependencies available:

    PYTHONPATH=src python tools/m1_receipt.py --verify
    PYTHONPATH=src python tools/m12_paired_v5_receipt.py --verify
    python tools/m2_vendor_check.py --targets-only --manifest docs/provenance/VENDORED_SOURCE_MANIFEST_CURRENT.json

These are verification-only commands. The raw scripts document the one original
qualification; rerunning the recorder creates a distinct new engineering execution.
The source-only archive is included; no model artifact is needed for these checks.
[ARTIFACTS.json](ARTIFACTS.json) binds this packet's authored and raw files.
