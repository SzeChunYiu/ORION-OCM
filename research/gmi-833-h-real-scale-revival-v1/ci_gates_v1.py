"""CI gates for gmi-833-h-real-scale-revival-v1, kept out of the workflow YAML.

A multi-line `python3 -c` body inside a `run: |` block scalar breaks the YAML
parser and a workflow in that state runs nothing, so every gate that needs more
than one line of Python lives here instead.

    python3 -I -B ci_gates_v1.py <gate>

Gates: foreign-sigma, rule-vacuity, closure-consistency, two-route-namespace,
selftest. Each prints what it checked and exits non-zero when it fails.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OWN_SIGMA = set(["SIGMA_R02", "SIGMA_R03B", "SIGMA_R04B"])
PRIMARY = ("grammar_s_v1", "run_real_scale_revival_v1", "real_scale_revival_v1")


def load(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


def foreign_sigma(result=None):
    result = result or load("RESULT_V1.json")
    bad = []
    for key, row in result["rows"].items():
        for gate in row["gates"]:
            if gate["sigma"] not in OWN_SIGMA or gate["sigma"] != row["sigma"]:
                bad.append((key, gate["gate"], gate["sigma"]))
    if bad:
        print("FOREIGN SIGMA: %r" % (bad[:3],))
        return 1
    print("every gate carries its own scope")
    return 0


def rule_vacuity(result=None):
    result = result or load("RESULT_V1.json")
    bad = [k for k, v in result["admissibility_rule"].items()
           if not (v["inert"] or v["non_vacuous"])]
    if bad:
        print("VACUOUS FILTER at %s: a filter that cannot separate tests nothing"
              % ", ".join(sorted(bad)))
        return 1
    print("the support-admissibility rule is inert or non-vacuous at every scope")
    return 0


def closure_consistency(result=None, recon=None):
    result = result or load("RESULT_V1.json")
    recon = recon or load("ISSUE_833_RECONCILIATION_H2_V1.json")
    closed = set(result["rows_closed"])
    for key, row in result["rows"].items():
        if row["complete"] and (row["supported"] != 11 or not row["single_sigma"]):
            print("BAD CLOSURE at %s: %d gates, single_sigma=%s"
                  % (key, row["supported"], row["single_sigma"]))
            return 1
        if not row["complete"] and not row["open_gates"]:
            print("OPEN ROW WITHOUT AN OPEN GATE at %s" % key)
            return 1
    for entry in recon["replacements"]:
        row = entry["old"].replace("- [ ] ", "")
        if row not in closed:
            print("RECONCILIATION CLAIMS AN OPEN ROW: %s" % entry["old"])
            return 1
        if not entry["new"].startswith("- [x] " + row):
            print("REPLACEMENT DOES NOT PRESERVE ITS ROW: %s" % entry["new"][:60])
            return 1
    print("%d row(s) closed, %d reported open, reconciliation consistent"
          % (len(closed), len(result["rows_open"])))
    return 0


def two_route_namespace():
    sys.path.insert(0, HERE)
    import independent_oracle_v1  # noqa: F401
    leaked = [m for m in PRIMARY if m in sys.modules]
    if leaked:
        print("TWO-ROUTE FAILURE: the oracle pulled in %s" % ", ".join(leaked))
        return 1
    print("route B imports none of %s" % ", ".join(PRIMARY))
    return 0


def selftest():
    """Validate each checker on a planted positive AND on the clean case.

    A checker that has never been shown a failure is not a checker.
    """
    result = load("RESULT_V1.json")
    recon = load("ISSUE_833_RECONCILIATION_H2_V1.json")
    checks = []

    clean = json.loads(json.dumps(result))
    checks.append(("foreign-sigma clean", foreign_sigma(clean) == 0))
    dirty = json.loads(json.dumps(result))
    first = sorted(dirty["rows"])[0]
    dirty["rows"][first]["gates"][0]["sigma"] = "SIGMA_4F"
    checks.append(("foreign-sigma planted", foreign_sigma(dirty) == 1))

    checks.append(("rule-vacuity clean", rule_vacuity(clean) == 0))
    dirty = json.loads(json.dumps(result))
    for v in dirty["admissibility_rule"].values():
        v["inert"] = False
        v["non_vacuous"] = False
    checks.append(("rule-vacuity planted", rule_vacuity(dirty) == 1))

    checks.append(("closure clean", closure_consistency(clean, recon) == 0))
    dirty_recon = json.loads(json.dumps(recon))
    dirty_recon["replacements"].append(
        {"anchor": recon["replacements"][0]["anchor"],
         "old": "- [ ] GLMs.", "new": "- [x] GLMs. — fabricated"})
    checks.append(("closure planted", closure_consistency(clean, dirty_recon) == 1))

    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print("  %-24s %s" % (name, "ok" if ok else "FAILED"))
    if bad:
        print("SELFTEST FAILURE: %s" % ", ".join(bad))
        return 1
    print("every gate fires on a planted positive and is silent on clean input")
    return 0


GATES = {"foreign-sigma": foreign_sigma, "rule-vacuity": rule_vacuity,
         "closure-consistency": closure_consistency,
         "two-route-namespace": two_route_namespace, "selftest": selftest}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in GATES:
        print("usage: ci_gates_v1.py {%s}" % "|".join(sorted(GATES)))
        return 2
    return GATES[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
