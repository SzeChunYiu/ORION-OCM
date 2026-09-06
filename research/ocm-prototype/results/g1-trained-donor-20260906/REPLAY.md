# Replay and custody map

This directory is a portable evidence copy, not a self-contained executable environment. No training or prediction was repeated to package it. The portable-copy-manifest.json maps every copied file to its original path and digest.

## Verify the evidence

Run sha256sum -c SHA256SUMS from this directory. Compare the externally published model against training-manifest.json top-level model_sha256; expect 11,631,918 bytes. The model and 8,228,194-byte tagger checkpoint are excluded from Git. The final model was trained from this experiment's TRAIN data; it is not an official pretrained UDPipe model.

## Inputs needed for a fresh replay

- Obtain only EWT r2.14 TRAIN and DEV from the exact URLs/hashes in portable-copy-manifest.json. No TEST data was acquired.
- Use Python 3.13.12 and the pinned ufal.udpipe==1.4.0.1 wheel; package-acquisition.json and prior-accounting.json bind official package/source identities.
- Obtain ORION-OCM source at a10ba0270553860adae9c656dc6ca779ff75e6aa. The grader-dependency-identity.json binds research/ocm-n1/ud_induction.py and ud_grammar.py; their normal source dependencies remain part of that checkout.
- The adopted CoNLL18 evaluator is included unchanged at source/conll18_ud_eval.py, with its MPL 2.0 notice/license.
- Any model asset URL is supplied by the publication owner. No release URL is invented in this capture.

## Original execution layout and relocation

Original scratch: /home/billy/orion-director-work/20260906/udpipe-g1.
Original custody data: /home/billy/orion-director-work/20260906/language-g1-audit/data.
Original external grader dependency path: /home/billy/orion-director-work/20260906/ocm-vessel/research/ocm-n1.

Frozen scripts and plans intentionally retain these recorded absolute paths. Do not edit the captured files to make a replay work. Copy them into a new replay scratch directory, record its identity, and make any path-only substitutions in that new edition with a complete diff/hash receipt. A relocated replay is a new run, not the captured run.

- The train-model.py and original supervise-training.py describe the failed 30-minute monolithic attempt.
- The repeat90/train-components.py and its supervisor describe the completed 90-minute envelope with official checkpoint reuse. Training-plan fields python and train_path require relocation. Stage 2 computes its checkpoint path from the script directory; its recorded plan also retains the original explicit path.
- The predict.py locates requests and model relative to itself. It requires a fresh output directory and the final model as ewt-train-default.udpipe; the recorded run used the explicit symlink described by model-origin.json. Do not mistake that alias for a model produced by the failed original attempt.
- The grade.py locates local evidence relative to itself but imports the original N1 checkout and reads the original custody data through explicit absolute paths. For relocation, map only those paths in a new replay edition; keep teacher gold outside any model/actor interface.
- Do not rerun prepare-evaluation.py to select a favorable panel. The evaluation-manifest.json, requests.jsonl and metric-plan.json are the captured selection and scoring contract.

Original prediction command: .venv/bin/python predict.py; original external scoring command: .venv/bin/python grade.py. The inference-execution-plan.json records 120-second prediction/60-second scorer bounds and 2 GiB address space. Replaying stored predictions only needs the external scorer and custody data; it never requires retraining.

## Interpretation limits

Accuracy denominators retain all selected sentences, including empty legacy inputs. Base LAS removes relation subtypes; full LAS retains them. Main all-token scores include punctuation. The old crossing-arc helper ignores PUNCT/root arcs, so its diagnostic is narrowly named in the clarification; primary scores never depend on it.

The public panel uses equal genre/length quotas and includes repeated documents and five normalized TRAIN-surface duplicates. No natural-population, independence, protected or broad language-understanding claim follows. Training selected no DEV/TEST model or hyperparameters.

Direct prediction ran 01:24:02.887817–01:24:04.817527 UTC on 2026-09-06; external scoring ended 01:24:05.101668. The root-owned native/OCM run had already started 01:23:12.927796, so host workloads overlapped. Wall time is descriptive; per-process CPU is retained. Training stage RSS and the grader supervisor RSS are cumulative measurements, explicitly labeled in the raw records.
