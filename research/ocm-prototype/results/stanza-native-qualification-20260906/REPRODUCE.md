# Reproduce the historical grade

The original single prediction attempt is immutable under raw/native-prediction-v1/.
Do not overwrite it or rerun a donor to reproduce the score. The live capture code
has a later CPU disclosure fix; its bytes are not represented as the original source.

raw/executed-source/ preserves all five new source files from the actual launch.
The .txt suffix prevents accidental pytest collection; source bytes are unchanged.
raw/source-custody.json binds the other 180 source files to their exact Git base.
The base commit also supplies the fixed public stream, native comparison records and
UD custody manifest. No model binary is needed for grading retained predictions.
Use the already qualified external G1 environment; its recorded packages remain
external runtime dependencies. The full model/runtime qualification is under
raw/qualified-donor/; those historical load-only receipts do not supersede this result.

The frozen grader verifies the recorded absolute actor-stage pathname. On the original
laptop it remains intact. On another host, restore raw/actor-inputs/ at the exact
actor_stage_path shown in raw/native-prediction-v1/launch-manifest.json first;
do not rewrite that manifest to make a changed path appear historically bound.
REPLAY.py refuses a missing or changed stage before grading.

Run on a Linux compute host with a Git object database containing the recorded base:

    python REPLAY.py --repo /path/to/ORION-OCM --out /path/to/fresh-replay --gold /path/to/en_ewt-ud-dev.conllu --train /path/to/en_ewt-ud-train.conllu

The script materializes exact source/artifact bytes through /usr/bin/git show and
the archived new files, checks all hashes, then executes the unchanged historical
grader on copied raw outputs in a fresh directory. PYTHONPATH points to this
materialized source. DEV and TRAIN must match the already frozen SHA256 values.
It compares every semantic grade field, excluding only the repeated grading time,
CPU and peak-RSS measurements, which cannot be expected to repeat exactly.

Actual replays v2 and v3 passed; v3 exercises the final .txt archive layout:
raw/replay-attempts/v3/replay-receipt.json.
All 185 source bindings matched and every semantic grade field reproduced.
The v1 refusal and its exact script/logs are retained under raw/replay-attempts/v1/.
It omitted UD_EWT_CUSTODY_MANIFEST_V1.json, required by unchanged load_split;
v2 restores that file byte-for-byte from the recorded base; v3 changes archive filenames only. This was materializer
repair after prediction, not new acquisition, annotation, source change or model tuning.

RESOURCE-CORRECTION.json preserves and corrects the old CPU custody interpretation.
The future capture helper and its regression use the actual observed discrepancy;
23 focused controls passed without another model prediction.
