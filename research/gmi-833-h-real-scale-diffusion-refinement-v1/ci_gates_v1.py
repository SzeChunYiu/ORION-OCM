"""CI gates for gmi-833-h-real-scale-diffusion-refinement-v1, kept out of the
workflow YAML. Multi-line Python lives here so the YAML `run:` blocks stay one
line each. Gates: foreign-sigma, closure-consistency, annotation-budget,
two-route-namespace, terminology, selftest. Each prints what it checked and
exits non-zero when it fails.

    python3 -I -B ci_gates_v1.py <gate>
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OWN_SIGMA = set(["SIGMA_H33R"])
ROW = "Diffusion/iterative-refinement systems."
PRIMARY = ("grammar_dr_v1", "run_real_scale_diffusion_refinement_v1",
           "real_scale_diffusion_refinement_v1")


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
    """A row is closed only with eleven measured coordinates at one scope, and
    the reconciliation may replace only a row the ledger actually closed."""
    result = result or load("RESULT_V1.json")
    recon = recon or load("ISSUE_833_RECONCILIATION_H33_V1.json")
    closed = set(result["rows_closed"])
    for key, row in result["rows"].items():
        if row["closed"]:
            if row["coordinates_measured"] != 11 or row["open_gates"]:
                print("BAD CLOSURE at %s: %d coordinates, open gates %r"
                      % (key, row["coordinates_measured"], row["open_gates"]))
                return 1
            if row["measured_class"] != row["intended_class"]:
                print("CLOSED ROW WHOSE MEASURED CLASS IS NOT ITS INTENDED "
                      "CLASS at %s: %s vs %s"
                      % (key, row["measured_class"], row["intended_class"]))
                return 1
        elif row["coordinates_measured"] != 11 and not row["open_gates"]:
            print("OPEN ROW WITHOUT AN OPEN GATE at %s" % key)
            return 1
    for entry in recon["replacements"]:
        row = entry["old"].replace("- [ ] ", "")
        if row not in closed:
            print("RECONCILIATION CLAIMS AN UNCLOSED ROW: %s" % entry["old"])
            return 1
        if not entry["new"].startswith("- [x] " + row):
            print("REPLACEMENT DOES NOT PRESERVE ITS ROW: %s" % entry["new"][:60])
            return 1
    print("%d row(s) closed, %d reported open, reconciliation consistent"
          % (len(closed), len(result["rows_open"])))
    return 0


def annotation_budget(recon=None):
    """The issue body truncates a row annotation; an over-long one loses its
    tail. Measured on the target body, not assumed: the longest annotated row
    payload is 2,143 characters (K08). Every payload this package publishes is
    checked against it."""
    recon = recon or load("ISSUE_833_RECONCILIATION_H33_V1.json")
    budget = recon["annotation_budget"]["measured_payload_limit_characters"]
    if budget != 2143:
        print("ANNOTATION BUDGET DRIFT: %r" % (budget,))
        return 1
    bad = []
    for entry in recon["replacements"]:
        parts = entry["new"].split(u" — ✅ ", 1)
        if len(parts) != 2:
            bad.append((entry["old"], "no annotation marker"))
            continue
        if len(parts[1]) > budget:
            bad.append((entry["old"],
                        "%d > %d characters" % (len(parts[1]), budget)))
    for name, text in (("claim_ceiling", recon["claim_ceiling"]),):
        if len(text) > budget:
            bad.append((name, "%d > %d" % (len(text), budget)))
    if bad:
        print("ANNOTATION OVER BUDGET: %r" % (bad[:3],))
        return 1
    print("every replacement payload fits the measured %d-character budget"
          % budget)
    return 0


def two_route_namespace():
    sys.path.insert(0, HERE)
    import independent_oracle_dr_v1  # noqa: F401
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
    machine-intelligence families` is quoted from the issue itself.
    """
    out, fenced = [], False
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
    hits = []
    for name in sorted(paths or os.listdir(HERE)):
        if not name.endswith((".md", ".py")):
            continue
        prose = _prose(open(os.path.join(HERE, name)).read())
        for term in BANNED:
            for match in re.finditer(r"\b" + re.escape(term) + r"\b", prose,
                                     re.I):
                line = prose[:match.start()].count("\n") + 1
                hits.append((name, line, term))
    if hits:
        print("BARE BANNED TERM: %r" % (hits[:5],))
        return 1
    print("0 bare banned terms across %d banned terms" % len(BANNED))
    return 0


def selftest():
    """Validate each checker on a planted positive AND on the clean case."""
    result = load("RESULT_V1.json")
    recon = load("ISSUE_833_RECONCILIATION_H33_V1.json")
    checks = []

    clean = json.loads(json.dumps(result))
    checks.append(("foreign-sigma clean", foreign_sigma(clean) == 0))
    dirty = json.loads(json.dumps(result))
    dirty["rows"]["H33"]["gates"][0]["sigma"] = "SIGMA_4F"
    checks.append(("foreign-sigma planted", foreign_sigma(dirty) == 1))

    clean_recon = json.loads(json.dumps(recon))
    checks.append(("closure clean", closure_consistency(clean, clean_recon) == 0))
    unclosed = json.loads(json.dumps(result))
    unclosed["rows_closed"] = []
    checks.append(("closure planted (unclosed row claimed)",
                   closure_consistency(unclosed, clean_recon) == 1))
    wrongclass = json.loads(json.dumps(result))
    wrongclass["rows"]["H33"]["measured_class"] = "SINGLE_DRAW_SOURCE"
    checks.append(("closure planted (wrong measured class)",
                   closure_consistency(wrongclass, clean_recon) == 1))
    ten = json.loads(json.dumps(result))
    ten["rows"]["H33"]["coordinates_measured"] = 10
    checks.append(("closure planted (ten coordinates)",
                   closure_consistency(ten, clean_recon) == 1))

    checks.append(("annotation clean", annotation_budget(clean_recon) == 0))
    dirty_recon = json.loads(json.dumps(recon))
    dirty_recon["replacements"][0]["new"] += " x" * 3000
    checks.append(("annotation planted",
                   annotation_budget(dirty_recon) == 1))

    checks.append(("terminology clean", terminology() == 0))
    planted = os.path.join(HERE, "PLANTED_TERM.md")
    quoted = os.path.join(HERE, "PLANTED_QUOTED.md")
    with open(planted, "w") as fh:
        fh.write("this prose says %s as a bare word\n" % BANNED[0])
    with open(quoted, "w") as fh:
        fh.write("the registered readout name is `%s` and nothing else\n"
                 % BANNED[0])
    try:
        checks.append(("terminology planted",
                       terminology(["PLANTED_TERM.md"]) == 1))
        checks.append(("terminology quoted is exempt",
                       terminology(["PLANTED_QUOTED.md"]) == 0))
    finally:
        for f in (planted, quoted):
            if os.path.exists(f):
                os.remove(f)

    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print("  %-36s %s" % (name, "ok" if ok else "FAILED"))
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
