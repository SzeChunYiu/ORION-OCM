"""CI gates for gmi-833-h-real-scale-belief-state-v1, kept out of the workflow
YAML. Multi-line Python lives here so the YAML `run:` blocks stay one line each.
Gates: foreign-sigma, closure-consistency, annotation-budget,
two-route-namespace, selftest. Each prints what it checked and exits non-zero
when it fails.

The package closes nothing by design: `rows_closed` is empty, every row in
`rows` is open, and the reconciliation's `replacements` list is empty while its
`rows_left_open_with_attribution` names exactly the one row. Those are the
invariants this file asserts, in place of the sibling packages' closure rule.

    python3 -I -B ci_gates_v1.py <gate>
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OWN_SIGMA = set(["SIGMA_H17R"])
ROW = "Bayesian inference/belief-state systems."
PRIMARY = ("grammar_bs_v1", "run_real_scale_belief_state_v1",
           "real_scale_belief_state_v1")


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


def closure_consistency(result=None, recon=None):
    """This package closes nothing and says so consistently.

    The eleven coordinates are all MEASURED here; what is withheld is closure,
    and the rule that withholds it is the measured class. So an open row must
    carry eleven measured coordinates, a non-empty boundary statement, and a
    measured class that is NOT its intended class -- that last clause is the
    reason the row is open, and a row claiming closure in this package is a
    failure of the gate rather than a success of the package. The
    reconciliation must claim no replacement, must list the row among the rows
    it leaves open, and must give that row an attribution naming the measured
    class, the intended class and the residual.
    """
    result = result or load("RESULT_V1.json")
    recon = recon or load("ISSUE_833_RECONCILIATION_H17_V1.json")
    closed = set(result["rows_closed"])
    for key, row in result["rows"].items():
        if row["closed"]:
            print("THIS PACKAGE CLOSES NOTHING BY DESIGN, but row %s is "
                  "marked closed" % key)
            return 1
        if row["coordinates_measured"] != 11:
            print("OPEN ROW WITHOUT ELEVEN MEASURED COORDINATES at %s: %d"
                  % (key, row["coordinates_measured"]))
            return 1
        if row["measured_class"] == row["intended_class"]:
            print("ROW %s IS OPEN WHILE CLAIMING ITS INTENDED CLASS %s"
                  % (key, row["intended_class"]))
            return 1
        if not row["boundary"]["statement"]:
            print("OPEN ROW WITHOUT A BOUNDARY STATEMENT at %s" % key)
            return 1
        if len(row["gates"]) != 11:
            print("ROW %s CARRIES %d GATES, NOT 11" % (key, len(row["gates"])))
            return 1
    if closed:
        print("THIS PACKAGE CLOSES NOTHING BY DESIGN, but rows_closed=%r"
              % (sorted(closed),))
        return 1
    for entry in recon["replacements"]:
        print("RECONCILIATION CLAIMS A REPLACEMENT: %r" % (entry.get("old"),))
        return 1
    entry = recon["rows_left_open_with_attribution"].get(ROW)
    if entry is None:
        print("THE OPEN ROW IS NOT ATTRIBUTED IN THE RECONCILIATION")
        return 1
    for token in ("STORED_LABEL_READ_WITH_FALLBACK",
                  "WEIGHTED_EVIDENCE_BELIEF"):
        if token not in entry["attribution"]:
            print("ATTRIBUTION DOES NOT NAME %s" % token)
            return 1
    if entry["replacement"] is not None or entry["row_text"] != ROW:
        print("ATTRIBUTION DOES NOT LEAVE THE ROW OPEN AND VERBATIM")
        return 1
    if result["rows_open"] != [ROW]:
        print("ROWS OPEN ARE NOT EXACTLY THIS PACKAGE'S ONE ROW: %r"
              % (result["rows_open"],))
        return 1
    print("0 rows closed, %d reported open, reconciliation consistent"
          % len(result["rows_open"]))
    return 0


def annotation_budget(recon=None, result=None):
    """This package writes no annotation, so the budget is a bound not a use.

    The measured payload limit of the target body is carried in the
    reconciliation and the package must respect it if a later lane composes an
    annotation from this package's own text: every free-text field the
    reconciliation publishes is checked against it here, and a replacement, if
    one is ever added, is checked too.
    """
    recon = recon or load("ISSUE_833_RECONCILIATION_H17_V1.json")
    result = result or load("RESULT_V1.json")
    budget = recon["annotation_budget"]["measured_payload_limit_characters"]
    if budget != 2143:
        print("ANNOTATION BUDGET DRIFT: %r" % (budget,))
        return 1
    bad = []
    for entry in recon["replacements"]:
        parts = entry["new"].split(u" — ✅ ", 1)
        if len(parts) != 2:
            bad.append((entry["old"], "no annotation marker"))
        elif len(parts[1]) > budget:
            bad.append((entry["old"], "%d > %d" % (len(parts[1]), budget)))
    for row, entry in recon["rows_left_open_with_attribution"].items():
        if len(entry["attribution"]) > budget:
            bad.append((row, "attribution %d > %d"
                        % (len(entry["attribution"]), budget)))
    for name, text in (("claim_ceiling", recon["claim_ceiling"]),
                       ("write_instruction", recon["write_instruction"]),
                       ("boundary statement",
                        result["rows"]["H17"]["boundary"]["statement"])):
        if len(text) > budget:
            bad.append((name, "%d > %d" % (len(text), budget)))
    if bad:
        print("OVER THE ANNOTATION BUDGET: %r" % (bad[:3],))
        return 1
    print("every published free-text payload fits the measured "
          "%d-character budget" % budget)
    return 0


def two_route_namespace():
    sys.path.insert(0, HERE)
    import independent_oracle_bs_v1  # noqa: F401
    leaked = [m for m in PRIMARY if m in sys.modules]
    if leaked:
        print("TWO-ROUTE FAILURE: the oracle pulled in %s" % ", ".join(leaked))
        return 1
    print("route B imports none of %s" % ", ".join(PRIMARY))
    return 0


BANNED = ("selection", "prior-free", "remint", "negative twin",
          "parent subtraction", "neutral search", "machine species",
          "morphology", "carrier", "open-ended",
          "proof by finite enumeration", "obligation")


def _prose(text):
    """Drop fenced blocks, inline code spans and quoted string literals.

    A banned term is banned as bare prose. A term inside a code span, a fenced
    block, a quoted string literal or a quoted issue row is a name or an
    identifier, and the section anchor `# H. Prior-free derivation of known
    machine-intelligence families` is quoted from the issue itself. What
    remains is the prose a reader takes as the package's own voice.
    """
    out, fenced, i = [], False, 0
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if "Prior-free derivation of known" in line:
            continue
        line = re.sub(r"`[^`]*`", " ", line)
        line = re.sub(r'"[^"]*"', " ", line)
        line = re.sub(r"'[^']*'", " ", line)
        out.append(line)
    return "\n".join(out)


def terminology(paths=None):
    """The registered 12-term terminology ban, as bare prose only."""
    hits = []
    for name in sorted(paths or os.listdir(HERE)):
        if not name.endswith((".md", ".py")):
            continue
        text = open(os.path.join(HERE, name)).read()
        prose = _prose(text)
        for term in BANNED:
            for match in re.finditer(r"\b" + re.escape(term) + r"\b", prose,
                                     re.I):
                line = prose[:match.start()].count("\n") + 1
                hits.append((name, line, term))
    if hits:
        print("BARE BANNED TERM: %r" % (hits[:5],))
        return 1
    print("0 bare banned terms across %d prose bodies" % len(BANNED))
    return 0


def selftest():
    """Validate each checker on a planted positive AND on the clean case."""
    result = load("RESULT_V1.json")
    recon = load("ISSUE_833_RECONCILIATION_H17_V1.json")
    checks = []

    clean = json.loads(json.dumps(result))
    checks.append(("foreign-sigma clean", foreign_sigma(clean) == 0))
    dirty = json.loads(json.dumps(result))
    dirty["rows"]["H17"]["gates"][0]["sigma"] = "SIGMA_4F"
    checks.append(("foreign-sigma planted", foreign_sigma(dirty) == 1))

    clean_recon = json.loads(json.dumps(recon))
    checks.append(("closure clean", closure_consistency(clean, clean_recon) == 0))
    dirty_recon = json.loads(json.dumps(recon))
    dirty_recon["replacements"].append(
        {"anchor": recon["evidence"].get("package", ""),
         "old": "- [ ] " + ROW,
         "new": "- [x] " + ROW + u" — ✅ fabricated"})
    checks.append(("closure planted", closure_consistency(clean, dirty_recon) == 1))
    closed_result = json.loads(json.dumps(result))
    closed_result["rows"]["H17"]["closed"] = True
    checks.append(("closure planted (row closed)",
                   closure_consistency(closed_result, clean_recon) == 1))
    unnamed = json.loads(json.dumps(recon))
    unnamed["rows_left_open_with_attribution"][ROW]["attribution"] = "nothing"
    checks.append(("closure planted (unattributed)",
                   closure_consistency(clean, unnamed) == 1))

    checks.append(("annotation clean",
                   annotation_budget(clean_recon, clean) == 0))
    dirty_recon = json.loads(json.dumps(recon))
    dirty_recon["rows_left_open_with_attribution"][ROW]["attribution"] += \
        " x" * 3000
    checks.append(("annotation planted",
                   annotation_budget(dirty_recon, clean) == 1))

    checks.append(("terminology clean", terminology() == 0))
    planted = os.path.join(HERE, "PLANTED_TERM.md")
    with open(planted, "w") as fh:
        fh.write("this prose says %s as a bare word\n" % BANNED[0])
    try:
        checks.append(("terminology planted",
                       terminology(["PLANTED_TERM.md"]) == 1))
        quoted = os.path.join(HERE, "PLANTED_QUOTED.md")
        with open(quoted, "w") as fh:
            fh.write("the registered readout name is `%s` and nothing else\n"
                     % BANNED[0])
        checks.append(("terminology quoted is exempt",
                       terminology(["PLANTED_QUOTED.md"]) == 0))
    finally:
        for f in (planted, quoted):
            if os.path.exists(f):
                os.remove(f)

    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print("  %-32s %s" % (name, "ok" if ok else "FAILED"))
    if bad:
        print("SELFTEST FAILURE: %s" % ", ".join(bad))
        return 1
    print("every gate fires on a planted positive and is silent on clean input")
    return 0


GATES = {"foreign-sigma": foreign_sigma,
         "closure-consistency": closure_consistency,
         "annotation-budget": annotation_budget,
         "two-route-namespace": two_route_namespace,
         "terminology": terminology, "selftest": selftest}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in GATES:
        print("usage: ci_gates_v1.py {%s}" % "|".join(sorted(GATES)))
        return 2
    return GATES[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
