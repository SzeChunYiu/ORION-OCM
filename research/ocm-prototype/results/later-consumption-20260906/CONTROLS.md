# Prepared engineering qualification

The focused tests use manual donor responses and mocked native checker calls.
No real cvc5 synthesis, Z3 obligation or Stitch induction has executed for this assay.

The RED tests first failed because the task successor and protocol modules were
missing. Additional RED controls caught command drift and excessive expansion of
shared let dependencies before their corresponding fixes. GREEN tests exercise:

- All five historical `task_sha256` identities remain byte-for-byte unchanged.
- One exact new fixture, source checksum, task digest and explicit grammar binding.
- All C/E0 primitive powers retained; B adds only the exact singleton helper.
- Sealed helper mutation, wrong arity/type, additional functions, forged GEN tags,
  extra SMT commands, shadowed lets and exponential let expansion refuse.
- A real returned helper call differs from an unused declaration or equivalent
  primitive body; an unused let is not counted as a dependency.
- Exactly three raw rows precede any semantic check; timeouts remain assigned.
- Correct B without use remains in the denominator as `NO_OBSERVED_USE`.
- At most four checker slots; a failed helper equality cannot qualify consumption.
- Raw-seal mutation and native-command drift refuse before checker dispatch.
- Raw inventories remain verifiable after copying the complete evidence directory.
- Post-dispatch drift retains one assignment row with its raw capture and boundary failure.
- Failed boundaries cannot reach checking; duplicate, missing or reordered sealed
  assignment lists refuse before assessment output or semantic calls.
- Create-only candidate and assessment outputs prevent automatic retries.

The pinned generation environment on laptop is used for these tests:

```sh
/home/billy/orion-director-work/20260906/generation-env/bin/python -m pytest -q \
  research/ocm-prototype/generation_tests/test_later_consumption_contract.py \
  research/ocm-prototype/generation_tests/test_later_consumption_protocol.py \
  research/ocm-prototype/generation_tests/test_later_consumption_drift.py
```

A source-only request preparation does not establish native parseability,
checkability or actual later use. Those remain the purpose of the once-only run
following independent review; they must not be inferred from mocked outcomes.

Only existing source edit: `clia_tasks.py` selects a separate sixth-fixture manifest
for the exact `public_absdiff2_v1` ID. Historical manifest bytes and task objects are
unchanged. New code is confined to the later-consumption prototype files, fixture,
tests and this preparation packet. The frozen text-task slice is untouched.
