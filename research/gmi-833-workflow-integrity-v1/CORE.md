# gmi-833-workflow-integrity-v1

A repo-wide guard for a CI defect class that is invisible in the normal signal.

## The defect

A workflow file whose YAML does not parse is **not** reported by GitHub the way a
failing workflow is. The run is recorded as `failure` with **zero jobs**, and the
run `name` is the file path instead of the workflow's declared `name`. Nothing
inside it ever executes.

The consequence is what makes it worth a guard: a package can ship a complete CI
suite — freeze-order gates, byte-exact receipt reproduction, hostile detection,
two-route agreement — that has **never run a single step**, while its pull
request merely looks like it has one red check among many.

## Why now

**Two #833 packages hit this in a single session**, from the same cause: a
heredoc body written at column 0 inside a `run: |` block scalar. Column 0
terminates the scalar, so the heredoc lines are parsed as YAML keys.

```yaml
      - name: bad
        run: |
          python3 - <<'PY'
import json          # column 0: ends the block scalar, breaks the file
print(json.dumps({}))
PY
```

Indenting the heredoc body to the block's level parses correctly.

## Detection, validated on real data

`check_workflows_v1.py` parses every `.github/workflows/*.yml` and fails if any
file does not parse, declares no `jobs`, or declares a job with neither `steps`
nor `uses`.

| check | result |
| --- | --- |
| recall on the real defect (the broken `gmi-833-capability-predictor-evaluation.yml`) | detected at line 73, column 1 |
| recall on a planted heredoc-at-column-0 workflow (`--self-test`) | detected |
| no-alarm on a well-formed heredoc workflow (`--self-test`) | silent |
| no-alarm across the repository | 262 workflows, 0 flagged |

Both directions matter. A checker that only demonstrates recall gets switched
off the first time it cries wolf, so the no-alarm case is asserted in CI
alongside the plant.

## The cheap manual detector

If you suspect a workflow never ran, look for a run that completed with **zero
jobs** whose `name` is the file path. That signature is conclusive.

## Reproduce

```bash
python3 research/gmi-833-workflow-integrity-v1/check_workflows_v1.py
python3 research/gmi-833-workflow-integrity-v1/check_workflows_v1.py --self-test
```

Closes no #833 checkbox. It protects the evidence every other row depends on.
