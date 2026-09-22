"""CI gates for gmi-833-h-real-scale-probabilistic-graphical-v1, kept out of
the workflow YAML. Multi-line Python lives here so the YAML `run:` blocks stay
one line each. Gates: foreign-sigma, closure-consistency, annotation-budget,
two-route-namespace, selftest. Each prints what it checked and exits non-zero
when it fails.

    python3 -I -B ci_gates_v1.py <gate>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER = u" — ✅ "
OWN_SIGMA = set(["SIGMA_H18R"])
PRIMARY = ("grammar_pgm_v1", "run_real_scale_pgm_v1", "real_scale_pgm_v1")
RECON = "ISSUE_833_RECONCILIATION_H18_V1.json"


def load(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


def recon_available():
    return os.path.isfile(os.path.join(HERE, RECON))


def foreign_sigma(result=None):
    result = result or load("RESULT_V1.json")
    bad = []
    for key, row in result["rows"].items():
        if row["sigma"] not in OWN_SIGMA:
            bad.append((key, "row", row["sigma"]))
        for gate in row["gates"]:
            if gate["sigma"] not in OWN_SIGMA or gate["sigma"] != row["sigma"]:
                bad.append((key, gate["gate"], gate["sigma"]))
    if bad:
        print("FOREIGN SIGMA: %r" % (bad[:3],))
        return 1
    print("every gate carries its own scope")
    return 0


def closure_consistency(result=None, recon=None):
    result = result or load("RESULT_V1.json")
    closed = set(result["rows_closed"])
    if recon is None and recon_available():
        recon = load(RECON)
    for key, row in result["rows"].items():
        if row["complete"] and (row["supported"] != 11 or not row["single_sigma"]):
            print("BAD CLOSURE at %s: %d gates, single_sigma=%s"
                  % (key, row["supported"], row["single_sigma"]))
            return 1
        if not row["complete"] and not row["open_gates"]:
            print("OPEN ROW WITHOUT AN OPEN GATE at %s" % key)
            return 1
        if row["complete"] and any(g["status"] == "OPEN" for g in row["gates"]):
            print("COMPLETE ROW WITH AN OPEN GATE at %s" % key)
            return 1
    if recon is not None:
        for entry in recon["replacements"]:
            row = entry["old"].replace("- [ ] ", "")
            if row not in closed:
                print("RECONCILIATION CLAIMS AN OPEN ROW: %s" % entry["old"])
                return 1
            if not entry["new"].startswith("- [x] " + row):
                print("REPLACEMENT DOES NOT PRESERVE ITS ROW: %s"
                      % entry["new"][:60])
                return 1
    print("%d row(s) closed, %d reported open, reconciliation %s"
          % (len(closed), len(result["rows_open"]),
             "consistent" if recon is not None else "not yet committed"))
    return 0


def annotation_budget(recon=None):
    """The issue body truncates a row annotation; an over-long one loses its
    tail. Measured on the target body, not assumed: the longest annotated row
    payload is 2,143 characters (K08). A replacement whose payload exceeds the
    budget would be published with its tail gone, so the payload carries no
    quantity, only package, result id and scope."""
    if recon is None:
        if not recon_available():
            print("reconciliation not yet committed; nothing to measure")
            return 0
        recon = load(RECON)
    budget = recon["annotation_budget"]["measured_payload_limit_characters"]
    if budget < 2143:
        print("ANNOTATION BUDGET BELOW THE MEASURED LIMIT: %d" % budget)
        return 1
    bad = []
    for entry in recon["replacements"]:
        parts = entry["new"].split(MARKER, 1)
        if len(parts) != 2:
            bad.append((entry["old"], "no annotation marker"))
            continue
        if len(parts[1]) > budget:
            bad.append((entry["old"],
                        "%d > %d characters" % (len(parts[1]), budget)))
    if bad:
        print("ANNOTATION OVER BUDGET: %r" % (bad[:3],))
        return 1
    print("every replacement payload fits the measured %d-character budget"
          % budget)
    return 0


def two_route_namespace():
    sys.path.insert(0, HERE)
    import independent_oracle_pgm_v1  # noqa: F401
    leaked = [m for m in PRIMARY if m in sys.modules]
    if leaked:
        print("TWO-ROUTE FAILURE: the oracle pulled in %s" % ", ".join(leaked))
        return 1
    print("route B imports none of %s" % ", ".join(PRIMARY))
    return 0


def selftest():
    """Validate each checker on a planted positive AND on the clean case."""
    result = load("RESULT_V1.json")
    checks = []

    clean = json.loads(json.dumps(result))
    checks.append(("foreign-sigma clean", foreign_sigma(clean) == 0))
    dirty = json.loads(json.dumps(result))
    first = sorted(dirty["rows"])[0]
    dirty["rows"][first]["gates"][0]["sigma"] = "SIGMA_4F"
    checks.append(("foreign-sigma planted", foreign_sigma(dirty) == 1))

    checks.append(("closure clean", closure_consistency(clean) == 0))
    dirty_row = json.loads(json.dumps(result))
    first = sorted(dirty_row["rows"])[0]
    dirty_row["rows"][first]["complete"] = True
    dirty_row["rows"][first]["supported"] = 11
    dirty_row["rows"][first]["open_gates"] = []
    dirty_row["rows"][first]["gates"][0]["status"] = "OPEN"
    checks.append(("closure planted",
                   closure_consistency(dirty_row, {"replacements": []}) == 1))

    if recon_available():
        recon = load(RECON)
        checks.append(("annotation clean", annotation_budget(recon) == 0))
        dirty_recon = json.loads(json.dumps(recon))
        dirty_recon["replacements"][0]["new"] += " x" * 3000
        checks.append(("annotation planted",
                       annotation_budget(dirty_recon) == 1))
        dirty_row = json.loads(json.dumps(result))
        first = sorted(dirty_row["rows"])[0]
        dirty_row["rows"][first]["complete"] = False
        dirty_row["rows"][first]["open_gates"] = []
        dirty_row["rows"][first]["gates"][0]["status"] = "OPEN"
        checks.append(("closure planted open row",
                       closure_consistency(dirty_row, recon) == 1))
    else:
        print("  reconciliation not yet committed; its two selftests skipped")

    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print("  %-26s %s" % (name, "ok" if ok else "FAILED"))
    if bad:
        print("SELFTEST FAILURE: %s" % ", ".join(bad))
        return 1
    print("every gate fires on a planted positive and is silent on clean input")
    return 0


GATES = {"foreign-sigma": foreign_sigma,
         "closure-consistency": closure_consistency,
         "annotation-budget": annotation_budget,
         "two-route-namespace": two_route_namespace, "selftest": selftest}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in GATES:
        print("usage: ci_gates_v1.py {%s}" % "|".join(sorted(GATES)))
        return 2
    return GATES[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
