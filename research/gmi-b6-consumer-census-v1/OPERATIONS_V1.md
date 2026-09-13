# Portable static operation

Use CPython 3.12 and its standard library. Copy this complete directory
anywhere; Git and the surrounding repository are unnecessary.

```sh
python3 -I -B replay_v1.py
python3 -I -B -O replay_v1.py
python3 -B -m unittest -v test_graph_census_v1 test_custody_v1
python3 -B -O -m unittest -v test_graph_census_v1 test_custody_v1
```

Replay validates the complete MANIFEST, launches a fresh isolated static
checker with a private bytecode prefix, compares its entire output with
CONSUMER_CENSUS_RECEIPT_V1.json and revalidates the manifest. The checker can
also emit the full receipt directly with `python3 -I -B check_census_v1.py`.
No command runs a saved genotype, search, training, priming or timing experiment.

An unavailable required file raises an error; a corrupted or unregistered
member is rejected. The intentionally missing E_twin1/S1 parent is reported
inside the valid census as unknown. A green census does not upgrade that
missing evidence. The archived upstream scanner remains unchanged and is not
the operational entry point.

MANIFEST binds every unit file except itself, including the expected receipt,
input binding and compressed raw archive. FROZEN_INPUTS identifies the exact
commit, path, byte count and SHA256 of every archive member. Neither manifest
claims independent authenticity of historical executions.
