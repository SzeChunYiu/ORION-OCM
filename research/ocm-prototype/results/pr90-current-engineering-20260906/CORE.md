# PR90: final-main engineering qualification

Classification: INFRASTRUCTURE. Terminal: ENGINEERING_REGRESSION_ONLY.

The accounting successor da2103c6c1e8083417196208df47e49224d9605f was normally
merged with exact main cba7ad76bc522c28bcd8dcf2215b931b5de98bfc.
The tested merge is b58082f18145e6e769370953ac8df650b37d6da9.
Claude's 5888bdc compatibility fixes, comments, tests and evidence remain intact;
the main ledger and surprise-channel repairs remain intact.

[Accounting port and actual red/green controls](../pr90-cache-accounting-port-20260906/CORE.md)
describe the earlier stage. This packet records its subsequent qualification.

## Executed result

- Fixed focused recipe: 133 passed, zero failures/errors/skips; JUnit 31.540 s.
- Fixed full recipe: 1,074 passed, zero failures/errors/skips; JUnit 216.837 s.
- All 25 current vendor targets, twelve current engineering wrappers and
  protected V5 archival custody passed, together with current E.verify.
- All 467 pre-run provenance/control files remained byte-identical.
- The 315-file source inventory remained identical throughout execution.
- No protected evaluation, model inference, prospective study or performance rerun.

Source: 6fd9c93729c3ca93d110164816539958b23c4fe3692b7b49e82b8f74d96b30df.
Receipt: 33eba792b6bc4805525456cc35e5923eb423346556de9dc7bd8aa8283629f879.
[BINDINGS.json](BINDINGS.json) binds exact source, selector, receipt and source ZIP.
[Qualification](raw/qualification.json) and [verification](raw/verification.json)
give actual commands, logs, source checks and custody observations.

## Selector and historical custody

The only merge conflict was CURRENT_ENGINEERING.json. All three selector stages
are retained under raw/, and the exact incoming main selector was kept until
a real new run passed. No earlier receipt was rewritten or selected by rehash alone.
[merge.json](raw/merge.json) records the resolution and prior branch custody.
Neither vendor manifest needed alteration: space.py is not a listed target.
The separately retained earlier repair packets still describe their original runs.
Current scientific promotion remains NOT_ESTABLISHED; protected reevaluation NOT_RUN.

## Environment, costs and operation

Python 3.13.12 on laptop billy, existing receipt-env, unchanged fixed gate recipes.
The recorder supervisor observed 250.960 s wall, 209.655 s child user CPU and
11.680 s child system CPU. These are scoped RUSAGE_CHILDREN observations, not
an independent complete process-tree accounting or performance comparison.
Energy, installation and development costs remain unmeasured.
Shallow cache storage accounting does not establish process RSS or active-k scaling.

Verify this preserved execution from the checkout with its test dependencies:

    PYTHONPATH=src python tools/m1_receipt.py --verify
    PYTHONPATH=src python tools/m12_paired_v5_receipt.py --verify
    python tools/m2_vendor_check.py --targets-only --manifest docs/provenance/VENDORED_SOURCE_MANIFEST_CURRENT.json

The raw scripts document the single qualification. A future recorder invocation
creates a distinct engineering run, rather than reproducing these timing bytes.
[ARTIFACTS.json](ARTIFACTS.json) binds this packet's authored and raw records.
