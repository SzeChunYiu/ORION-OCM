# gmi-833-workflow-integrity-v1

A repo-wide guard for a CI defect class that is invisible in the normal signal.

## The defects

A workflow file whose YAML does not parse is **not** reported by GitHub the way a
failing workflow is. The run is recorded as `failure` with **zero jobs**, and the
run `name` is the file path instead of the workflow's declared `name`. Nothing
inside it ever executes.

The consequence is what makes it worth a guard: a package can ship a complete CI
suite — freeze-order gates, byte-exact receipt reproduction, hostile detection,
two-route agreement — that has **never run a single step**, while its pull
request merely looks like it has one red check among many.

## A second shape, found the same day

A workflow can also never execute because its `runs-on` names a runner this
repository does not have. The job then sits **queued forever** — `status` stays
`queued`, `started_at` is set, `conclusion` stays null — and the pull-request
check simply reads as *pending*. That is the least visible of the three: it looks
like a slow queue, not a defect.

It happened here. The package repaired for the YAML defect was re-pushed with

```yaml
    runs-on: [self-hosted, Linux, X64, pm-ci]
```

`pm-ci` is another repository's runner label. The job sat queued for over two
hours without starting. Of **303** `runs-on` declarations across every workflow
on `main`, 294 are `ubuntu-latest` and 9 are `ubuntu-24.04` — **none** is
self-hosted.

So one package managed to never run its CI in two different ways in succession,
which is the argument for checking this mechanically rather than by eye.

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
| recall on the real unavailable-runner defect (`pm-ci`) | detected |
| recall on a planted unavailable-runner workflow (`--self-test`) | detected |
| no-alarm on a well-formed heredoc workflow (`--self-test`) | silent |
| no-alarm across the repository | 264 workflows, 0 flagged |

Both directions matter. A checker that only demonstrates recall gets switched
off the first time it cries wolf, so the no-alarm case is asserted in CI
alongside the plant.

## The cheap manual detectors

- **Never parsed:** a run that completed with **zero jobs** whose `name` is the
  file path. Conclusive.
- **Never started:** a job whose `status` is `queued` long after `started_at`,
  with `conclusion` still null. Check its `runs-on` against the runners the
  repository actually has.

## Reproduce

```bash
python3 research/gmi-833-workflow-integrity-v1/check_workflows_v1.py
python3 research/gmi-833-workflow-integrity-v1/check_workflows_v1.py --self-test
```

Closes no #833 checkbox. It protects the evidence every other row depends on.
