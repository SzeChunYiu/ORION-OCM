# Additive text-task donor qualification

`tools/record_text_task_slice.py` qualifies the two explicit donor test files.
It does not modify V4, the engineering predecessor, historical receipts, or the
current engineering selector. Their original inventory scope remains unchanged.

The new identity binds the unchanged V4 source inventory/id, Git HEAD/tree,
Python executable/version, required package versions and installed package bytes,
the research import closure rooted at `text_task_slice.py`, the separately spawned
`clia_worker.py`, vendor imports, the complete CLIA fixture registry and its five
source files. `requirements-g1.txt` is included. This is a current bounded closure;
new dynamic imports or external data dependencies require an explicit successor.

Before final execution, freeze integrated code, then obtain its exact identity:

```sh
/home/billy/orion-director-work/20260906/g1-env/bin/python tools/record_text_task_slice.py --describe
```

Run only after the independent integrated freeze, supplying that identity:

```sh
/home/billy/orion-director-work/20260906/g1-env/bin/python tools/record_text_task_slice.py \
  --output docs/provenance/text_task_slice/run-v1 \
  --expected-source-id FROZEN_QUALIFICATION_SOURCE_ID
```

The recorder exclusively creates source ZIP, before/after snapshots, launch record,
separate stdout/stderr, JUnit, and a pytest collection/call-phase trace. It runs only
`tests/integration/test_text_task_slice.py` and `test_text_task_binding.py`, requiring
at least 21 and 8 cases respectively, every collected case actually passing setup,
call and teardown, no skips, and exact JUnit/trace agreement. Source, Git identity
and dependency environment must remain unchanged before/after. Auto-loaded pytest
plugins and inherited test-selection options are disabled. Raw failures stay saved;
outputs cannot be reused or overwritten by the recorder.

The source archive includes both root and research inventories and is independently
checked against their hashes. No receipt is selected for engineering custody.
A passing record is a bounded donor execution attestation, not independent scientific
replication, learned-English, general problem solving or a performance claim.

Preparation controls use synthetic donor artifacts and two trivial non-donor pytest
fixtures to verify the trace plugin. They do not rerun the frozen consumption assay
or execute the actual 29-case donor qualification. The latter waits for root freeze.
