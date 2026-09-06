# Tested reconstruction and external regrading

The original full raw directory remains at stanza-shared-matched-prospective-v1 on the authorized laptop.
Git stores raw/model-less-raw.tar.gz (2,230,506 bytes) and raw/frozen-source.tar.gz (411,092 bytes).
Eight .pt occurrences are omitted; their four distinct public model artifacts and fixed URLs/hashes are in
raw/MODEL_LOCATORS.json. No model binary is committed and no release asset is required.

Obtain the four exact artifacts from their recorded official HuggingFace commit 88e0cd3ddaa0c5a4b682895527ac013ce0241c21,
or reuse an existing qualified local copy. Store them under <model-root>/models/en/... as named in the locator manifest.
Require the recorded SHA256 and byte count; never replace a missing artifact with a newer model.
resources.json and both fixed profiles are inside the model-less raw archive.

Use Python3.13.12 and the exact G1 grading dependencies (requirements-g1.txt in frozen source).
The separate original inference environment remains locked in the preceding shared engineering packet.
Do not install, load or run Stanza for this reconstruction.

Run:
    python REPLAY.py --packet <this-packet> --out <new-empty-path> --models <model-root> --gold <custody-EWT-DEV> --python <pinned-grader-python>

The external DEV SHA must be dd514122385fd3374dd10051ddaf477c957d3da0bba48931d6f969820ece233f.
Gold is supplied only to the external grader after reconstruction of the already sealed actor output.
The script extracts only ordinary relative files, verifies archive/manifests, rehydrates exact model bytes,
checks the full 68-file original inventory and original seal/receipt/grade hashes, then runs the frozen external grader.
Hardlinks avoid copying weights on one filesystem; a copy is used when hardlinks are unavailable.
Neither actor inference nor the original lifetime is re-executed, and original raw files are never edited.

The actual laptop replay passed:
- 68/68 original files,497,900,244 logical bytes verified, including 8 model occurrences.
- 194 exact frozen source/support files reconstructed.
- All grading fields reproduced after excluding only newly measured external-checker metrics/PIDs.
- No actor execution and no model inference.
- Reconstruction plus regrade 2.421450s; wrapper self CPU 1.333529s and regrade direct-child observation 1.088906s.
- Total process-tree CPU remains UNKNOWN; these are new post-actor verification costs.

replay/REPLAY_RECEIPT.json and regrade.json retain the new execution separately from raw/grade.json.
The verifier also accepted an unmodified real grade file and refused a changed copy; replay/CUSTODY_CONTROL.json.
Only a local exact-artifact reconstruction was executed here; a fresh network download was not repeated.
A missing public artifact or a changed source/hash yields CANNOT_CHECK_REPLAY; it is not repaired by relabeling.

The 194-file replay closure includes the bound 171-file operator/runtime inventory plus execution/identity helpers,
the external UD loader and custody manifest, fixture data, vendor material and the exact prospective plan.
It is a reconstruction closure, not a model of cognitive complexity or complete installed-library source size.
