"""Fail the build if any workflow file does not parse or declares no jobs.

Why this exists
---------------
GitHub does not surface an unparseable workflow the way it surfaces a failing
one. The run is recorded as `failure` with **zero jobs**, and the run `name` is
the file path instead of the workflow's declared `name`. Nothing inside ever
executes. A package can therefore ship a full CI suite -- freeze-order gates,
receipt reproduction, hostile detection -- that has never run a single step,
while its PR merely looks like it has a red check.

Two #833 packages hit this in one session, both from the same cause: a heredoc
body written at column 0 inside a `run: |` block scalar. Column 0 terminates
the block scalar, so the heredoc lines are parsed as YAML keys.

    - name: bad
      run: |
        python3 - <<'PY'
    import json          <-- column 0: ends the scalar, breaks the file
    print(json.dumps({}))
    PY

Indent the heredoc body to the block's level and it parses.

Usage
-----
    python3 check_workflows_v1.py             # check the repo
    python3 check_workflows_v1.py --self-test # prove the checker detects a plant
"""

import glob
import io
import os
import sys
import tempfile

try:
    import yaml
except ImportError:
    sys.stderr.write("pyyaml is required\n")
    sys.exit(2)

# The known-bad shape, used only by --self-test. Kept verbatim so the test
# exercises the real failure mode rather than a synthetic one.
PLANTED_BAD = """name: planted
on: [workflow_dispatch]
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
      - name: heredoc at column 0 terminates the block scalar
        run: |
          python3 - <<'PY'
import json
print(json.dumps({}))
PY
"""

PLANTED_BAD_RUNNER = """name: planted-runner
on: [workflow_dispatch]
jobs:
  j:
    runs-on: [self-hosted, Linux, X64, pm-ci]
    steps:
      - run: echo hi
"""

PLANTED_GOOD = """name: planted-ok
on: [workflow_dispatch]
jobs:
  j:
    runs-on: ubuntu-latest
    steps:
      - name: heredoc indented into the block scalar
        run: |
          python3 - <<'PY'
          import json
          print(json.dumps({}))
          PY
"""


def check_text(text, label):
    """Return a failure reason, or None when the workflow is well-formed."""
    try:
        doc = yaml.safe_load(text)
    except Exception as exc:
        return "%s: %s" % (type(exc).__name__, str(exc).replace("\n", " ")[:160])
    if not isinstance(doc, dict):
        return "top level is %s, expected a mapping" % type(doc).__name__
    if "jobs" not in doc:
        return "no `jobs` key - the run would complete with zero jobs"
    if not doc["jobs"]:
        return "`jobs` is empty - the run would complete with zero jobs"
    if not isinstance(doc["jobs"], dict):
        return "`jobs` is %s, expected a mapping" % type(doc["jobs"]).__name__
    for name, job in doc["jobs"].items():
        if not isinstance(job, dict):
            return "job %r is %s, expected a mapping" % (name, type(job).__name__)
        if "steps" not in job and "uses" not in job:
            return "job %r has neither `steps` nor `uses`" % name
        reason = check_runner(name, job.get("runs-on"))
        if reason:
            return reason
    return None


# Runner labels this repository actually has. ORION-OCM registers no
# self-hosted runners, so a job asking for one queues forever: status stays
# `queued`, `started_at` is set, `conclusion` stays null, and the PR check
# simply reads as pending. That is the least visible way a workflow can never
# execute -- it looks like a slow queue, not a defect.
ALLOWED_RUNNER_PREFIXES = ("ubuntu-", "windows-", "macos-")


def check_runner(job_name, runs_on):
    if runs_on is None:
        return "job %r has no `runs-on`" % job_name
    labels = runs_on if isinstance(runs_on, list) else [runs_on]
    for lab in labels:
        if not isinstance(lab, str):
            continue
        if lab.startswith("${{"):      # expression-driven; cannot check statically
            return None
    for lab in labels:
        if isinstance(lab, str) and lab.startswith(ALLOWED_RUNNER_PREFIXES):
            return None
    return ("job %r targets runner labels %r, none of which this repository has; "
            "the job would queue forever without ever starting" % (job_name, labels))


def check_repo(root="."):
    paths = sorted(glob.glob(os.path.join(root, ".github/workflows/*.yml")) +
                   glob.glob(os.path.join(root, ".github/workflows/*.yaml")))
    bad = []
    for p in paths:
        with io.open(p, encoding="utf-8") as fh:
            reason = check_text(fh.read(), p)
        if reason:
            bad.append((p, reason))
    return paths, bad


def self_test():
    """The checker must flag the real bad shape and stay silent on the good one."""
    bad_reason = check_text(PLANTED_BAD, "<planted-bad>")
    runner_reason = check_text(PLANTED_BAD_RUNNER, "<planted-runner>")
    good_reason = check_text(PLANTED_GOOD, "<planted-good>")
    ok = True
    if runner_reason is None:
        sys.stderr.write("SELF-TEST FAILED: planted unavailable-runner workflow was NOT detected\n")
        ok = False
    else:
        sys.stdout.write("self-test recall   : planted unavailable runner detected (%s)\n"
                         % runner_reason[:70])
    if bad_reason is None:
        sys.stderr.write("SELF-TEST FAILED: planted unparseable workflow was NOT detected\n")
        ok = False
    else:
        sys.stdout.write("self-test recall   : planted bad workflow detected (%s)\n"
                         % bad_reason[:70])
    if good_reason is not None:
        sys.stderr.write("SELF-TEST FAILED: false alarm on a well-formed workflow: %s\n"
                         % good_reason)
        ok = False
    else:
        sys.stdout.write("self-test no-alarm : well-formed workflow accepted\n")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    paths, bad = check_repo()
    sys.stdout.write("workflow files checked: %d\n" % len(paths))
    if bad:
        sys.stderr.write("\nUNPARSEABLE OR JOBLESS WORKFLOWS (%d):\n" % len(bad))
        for p, r in bad:
            sys.stderr.write("  %s\n      %s\n" % (p, r))
        sys.stderr.write(
            "\nA workflow in this state runs NOTHING. Two shapes, two symptoms:\n"
            "  unparseable YAML  -> the run FAILS with zero jobs and is named\n"
            "                       after the file path, not the workflow.\n"
            "                       Usual cause: a heredoc body at column 0\n"
            "                       inside a `run: |` block scalar.\n"
            "  unavailable runner -> the job stays QUEUED forever. The check\n"
            "                       reads as pending, so it looks like a slow\n"
            "                       queue rather than a defect. This repo has\n"
            "                       no self-hosted runners.\n")
        return 1
    sys.stdout.write("all workflows parse and declare at least one job with steps\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
