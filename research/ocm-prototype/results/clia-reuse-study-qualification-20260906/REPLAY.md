# Operating the frozen reuse control

Use the isolated study checkout and the existing pinned G1 environment on laptop billy.
No network, hosted-model request, model download or training is required.

```sh
cd /home/billy/orion-director-work/20260906/ocm-clia-reuse-study
export PYTHONPATH=src:research/ocm-prototype
export PYTHONDONTWRITEBYTECODE=1
python=/home/billy/orion-director-work/20260906/g1-env/bin/python
```

Qualification controls run without the prospective panel or model inference:

```sh
"$python" -m pytest research/ocm-prototype/test_clia_reuse_study.py \
  research/ocm-prototype/test_clia_reuse_worker_fixture.py \
  research/ocm-prototype/test_clia_reuse_supervision.py \
  research/ocm-prototype/test_grade_clia_reuse.py \
  research/ocm-prototype/test_grade_clia_reuse_audit.py -q
```

F0 preparation creates a NEW scratch capture directory; it copies the exact six published files and source bytes.
Supply one recorded allowed CPU (the run will use that CPU for every actor). This command does not acquire a program:

```sh
"$python" research/ocm-prototype/capture_clia_reuse.py freeze \
  --root /path/to/new-capture \
  --protocol-dir research/ocm-prototype/results/clia-reuse-study-qualification-20260906/protocol \
  --model /home/billy/orion-director-work/20260906/udpipe-g1/repeat90/ewt-train-default.udpipe \
  --cpu <recorded-allowed-cpu>
```

After the committed source and F0 package are reviewed, the same frozen source executes the registered control:

```sh
"$python" research/ocm-prototype/capture_clia_reuse.py run --root /path/to/new-capture
"$python" research/ocm-prototype/grade_clia_reuse.py /path/to/new-capture --output /path/to/new-grade.json
```

No automatic restart, retry, alternative synthesis or outcome selection is supported.
F1 is written only after both original acquisitions complete with identical canonical donors.
Every revision is performed at the preceding actor stage's end, followed by persistence and OS-process exit.

The raw inputs retain their original absolute paths. The capture records `capture_root`;
external grading checks those historical paths against that identity and reads copied bytes via the sealed relative inventory.
Do not rewrite raw inputs or receipts to relocate an archive. A new execution uses a new F0 and NEW state.

Model binaries and the corpus are external assets, not manuscript evidence.
The fixed model is SHA256 `7bc9a92586cbac6ebd599b035f2f4d686edb7b000ffbed776a93d8e4a23eeea9`.
Its original complete training provenance remains in the linked G1 trained-donor packet.
