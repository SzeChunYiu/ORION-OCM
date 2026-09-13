# B6 corrected adjudication custody packet

Snapshot: 2026-09-13 10:46:11–10:46:12 UTC, laptop billy.
The output remains `ADJUDICATION_INCOMPLETE__UNITS_MISSING`.
Nine of 24 physical arm files exist here; all fifteen absent filenames are explicit
in `MANIFEST.json`. This packet does not complete the campaign.

`microscopes/results/` preserves the nine exact arm filenames and bytes plus
the five source receipts referenced by their seven warm populations.
`gmi_microscope/b6_adjudicate.py` is the corrected, self-contained scorer.
`outputs/` contains its exact V2 output, with the historical V1 output retained
separately for comparison. `authority/` retains the imported freeze and correction.
The manifest binds every packet file except itself and lists custody locations,
known missing inputs, code hashes, and the source snapshot manifest digest.

Run with CPython 3.12, providing a new output directory:

```sh
python3 replay.py --output-dir /tmp/b6-corrected-replay-unique
```

The replay checks file digests, raw receipt digests, and warm source references,
then copies arm inputs to the new directory and runs only the scorer.
It requires exact JSON except the directory prefix of the two documented
identity-unknown receipt locators; their basenames must match and every other
field must match exactly. The original output bytes remain bound by the manifest. It neither reruns search nor verifies missing
first-DENSE genotypes. A successful replay validates reproducibility of this
incomplete adjudication, not the truth of every assertion inside a historical log.

The original lane was an extracted non-Git tree. Two searches of all locally
reachable integration-clone history found no tracked `STAGE_B6_DEV_*.json`
records before this packet; this does not enumerate unfetched GitHub objects.
See ../../B6_CORRECTED_EVIDENCE_ASSESSMENT_V1.md for scope and scientific readout.
