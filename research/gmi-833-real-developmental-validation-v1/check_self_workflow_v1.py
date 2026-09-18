"""Fail the build if this package's workflow does not parse or declares no jobs.

GitHub records an unparseable workflow as a run that FAILED WITH ZERO JOBS,
named after the file path rather than the workflow's own name. Nothing inside
ever executes, so a package can appear to have CI while never having run a
step. Two #833 packages hit this, both from a heredoc body at column 0 inside a
`run: |` block scalar, which terminates the scalar.

This checker refuses to pass on "could not check": if PyYAML is unavailable it
falls back to a structural scan and says so, and it exits non-zero if the file
is missing. Modelled on research/gmi-833-workflow-integrity-v1 (PR #1020).

Usage: python3 -I -B check_self_workflow_v1.py [<repo root>]
"""
import os
import sys

WF = ".github/workflows/gmi-833-real-developmental-validation-v1.yml"


def structural_scan(text):
    """Detect the known-bad shape without a YAML parser: a line at column 0
    inside a block scalar opened by `run: |`."""
    problems = []
    in_block = False
    indent = 0
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        cur = len(line) - len(line.lstrip())
        if in_block:
            if cur == 0:
                problems.append("line %d at column 0 inside a block scalar "
                                "opened at indent %d" % (i, indent))
                in_block = False
            elif cur <= indent:
                in_block = False
        if line.rstrip().endswith("run: |") or line.rstrip().endswith("run: |-"):
            in_block = True
            indent = cur
    return problems


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    path = os.path.join(root, WF)
    if not os.path.exists(path):
        sys.stderr.write("WORKFLOW_MISSING: %s\n" % path)
        sys.exit(1)
    with open(path) as f:
        text = f.read()
    problems = structural_scan(text)
    if problems:
        sys.stderr.write("BLOCK_SCALAR_TERMINATED_AT_COLUMN_0:\n")
        for p in problems:
            sys.stderr.write("  " + p + "\n")
        sys.exit(1)
    try:
        import yaml
    except ImportError:
        print("workflow structural scan OK (no column-0 block-scalar break); "
              "PyYAML unavailable so the parse was NOT verified here")
        sys.exit(0)
    try:
        doc = yaml.safe_load(text)
    except Exception as exc:                                # noqa: BLE001
        sys.stderr.write("WORKFLOW_DOES_NOT_PARSE: %s\n" % exc)
        sys.exit(1)
    if not isinstance(doc, dict):
        sys.stderr.write("WORKFLOW_NOT_A_MAPPING\n")
        sys.exit(1)
    jobs = doc.get("jobs") or {}
    if not jobs:
        sys.stderr.write("WORKFLOW_DECLARES_ZERO_JOBS\n")
        sys.exit(1)
    nsteps = 0
    for name, job in jobs.items():
        steps = (job or {}).get("steps") or []
        if not steps:
            sys.stderr.write("JOB_DECLARES_ZERO_STEPS: %s\n" % name)
            sys.exit(1)
        nsteps += len(steps)
    print("workflow OK: parses, %d job(s), %d step(s)" % (len(jobs), nsteps))


if __name__ == "__main__":
    main()
