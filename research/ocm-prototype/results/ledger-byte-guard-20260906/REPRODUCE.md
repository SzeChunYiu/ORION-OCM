# Reproduce the archived grade

This packet contains all fourteen raw ledgers/receipts, exact input stream, prospective plan,
tools, qualification failures/controls, and both production source inventories.
No model binary, gold corpus, hosted service or original laptop directory is required for grading.

Use Linux with Bubblewrap and Python 3.13 (original execution used 3.13.12).
From a checkout containing this packet, choose a fresh absolute output directory:

```sh
env -u PYTHONPATH -u PYTHONOPTIMIZE /path/to/python3.13 REPLAY.py \
  --packet /absolute/path/to/ledger-byte-guard-20260906 \
  --out /absolute/path/to/fresh-ledger-replay
```

REPLAY.py verifies both archive/manifest bindings, extracts regular files into the new directory,
and verifies every extracted byte. Bubblewrap mounts archived input/tools read-only at their
recorded absolute paths inside a network-disabled process. It hides the host home tree and
mounts only the selected Python environment, exact archives and new results directory in those locations.
Extracted source/input directories have no writable alias inside the regrade namespace.
This mount layout serves reproducible path custody, not a new authenticated actor boundary.

The unchanged frozen grade_storage_pairs.py reads the unchanged plan and all fourteen raw results.
A replay passes only when the new receipt bytes exactly match the original SHA256:
73b7409b80669ed6ea6377f754ca6b54a060c346ab3f2e0d63a429a5d45c7769.
No clocks, IDs, observations, thresholds or outcome fields are normalized or rewritten.

replay/ retains two diagnosed namespace startup refusals, the subsequent clean
reconstruction/regrade, and a deliberately corrupted archive refusal. They are qualification costs, not another performance sample.

To inspect or independently implement the storage comparison, source.zip includes the exact
baseline/candidate production modules; raw.zip contains the original worker, fixed launcher,
source maps, stream and expected final bytes. The original launcher intentionally refuses its
existing run directory. A new performance experiment requires its own prospective paths/plan
and reports all new measurements separately. This packet does not silently rerun that experiment.

Whole historical capture custody was checked at execution; the component inputs/final ledgers
are included here. Full v3 actor custody remains with the separately published CLIA reuse packet.
Historical/current scientific authority remains governed by #38/#49.
