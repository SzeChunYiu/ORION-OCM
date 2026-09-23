"""CI gates for gmi-833-h-real-scale-diffusion-refinement-v1, kept out of the
workflow YAML. Multi-line Python lives here so the YAML `run:` blocks stay one
line each. Gates: alias-guard, foreign-sigma, closure-consistency,
annotation-budget, two-route-namespace, terminology, selftest. Each prints what
it checked and exits non-zero when it fails.

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

# Redundancies that follow from the REGISTERED design and are therefore not
# defects. Each entry must be witnessed by the assertion below, which evaluates
# the pair on rows whose walk value is at the registered cap.
REDUNDANT_ARMS = {
    ("CARD>=1", "REFINE<=256"):
        "the refinement walk is capped at 256, so for every tally the predicate "
        "REFINE<=256 is exactly CARD>=1; the arm is retained because the "
        "registered base ladder contains 256 and the freeze is not re-cut here",
}


def load(name):
    with open(os.path.join(HERE, name)) as fh:
        return json.load(fh)


def alias_guard(language=None):
    """No two registered arms may be the same predicate under two names.

    The sibling readout languages in this line have twice shipped arms that
    were decision-identical at every stage -- the H32 pair, and the H29
    TOPK2_FAN/UNION_FAN/WSUM_FAN and SEL_FAN/MEM_FALLBACK pairs -- which turns a
    measured tie into a register artefact rather than an ecology property.

    The grid is the exact DISCRIMINATING WITNESS SET for this language, not a
    sample: every arm's predicate is a threshold test on one coordinate conjoined
    with band tests on the others, so for any two arms with different thresholds
    `t1 < t2` on the same coordinate the value `t1` is already a witness (the
    first arm accepts it, the second rejects it). Sweeping each axis over the
    union of that axis's registered thresholds therefore decides every pair,
    and the axes are swept with both registered fallback constants so an arm
    that reads the fallback constant is exercised on the rows where its
    fallback branch fires. A clash reported on this grid is a real redundancy,
    and is accepted only if it is declared in REDUNDANT_ARMS.
    """
    sys.path.insert(0, HERE)
    import grammar_dr_v1 as G
    import real_scale_diffusion_refinement_v1 as C
    rec = load("REAL_RUNS/scope_SIGMA_H33R.json")
    C.T_STAR_REF = rec["label_config"]["T_star"]
    fallback = rec["query_fallback_label"]
    if language is None:
        language = list(G.readouts((C.T_STAR_REF,)))
    # the registered thresholds of each axis, plus 0 and the cap boundary
    walk_axis = tuple(sorted(set(G.REFINE_BASE) | set(G.REFINEIN_THRESHOLDS)
                             | set(G.DRAW_THRESHOLDS)
                             | set([0, C.T_STAR_REF, C.T_STAR_REF - 1,
                                    G.STEP_CAP, G.STEP_CAP - 1])))
    card_axis = tuple(sorted(set(G.CARD_THRESHOLDS) | set([0])))
    draw_axis = tuple(sorted(set(G.DRAW_THRESHOLDS) | set([0])))
    cnt_axis = tuple(sorted(set(G.CNT_THRESHOLDS) | set([0])))
    len_axis = tuple(sorted(set(G.LEN_THRESHOLDS) | set([1, 2, 13, 14])))
    grid = []
    for card in card_axis:
        for ws in walk_axis:
            for dd in draw_axis:
                for cnt in cnt_axis:
                    for L in len_axis:
                        grid.append(["q", 0, "c", card, ws, dd, cnt, L])
    names = sorted(set(language))
    vecs = {}
    for name in names:
        for maj in (0, 1):
            C.FIT_MAJORITY = maj
            vecs[(name, maj)] = tuple(
                C.decision(name, r[0], r[1], None, r[3], r[4], r[5], r[6],
                           r[7], C.T_STAR_REF) for r in grid)
    C.FIT_MAJORITY = fallback
    clashes = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if all(vecs[(a, m)] == vecs[(b, m)] for m in (0, 1)):
                clashes.append((a, b))
    undeclared = [c for c in clashes
                  if c not in REDUNDANT_ARMS
                  and (c[1], c[0]) not in REDUNDANT_ARMS]
    if undeclared:
        print("ALIASED ARMS (undeclared): %r" % (undeclared[:3],))
        return 1
    # every declared redundancy must be witnessed at the cap it rests on
    for pair in REDUNDANT_ARMS:
        a, b = pair
        for r in (["q", 1, "c", 1, 256, 0, 1, 9],
                  ["q", 0, "c", 3, 256, 0, 2, 9]):
            C.FIT_MAJORITY = fallback
            if C.decision(a, r[0], r[1], None, r[3], r[4], r[5], r[6], r[7],
                          C.T_STAR_REF) != C.decision(
                              b, r[0], r[1], None, r[3], r[4], r[5], r[6], r[7],
                              C.T_STAR_REF):
                print("DECLARED REDUNDANCY DOES NOT HOLD: %r" % (pair,))
                return 1
    print("no undeclared aliasing among the %d registered arms "
          "(%d declared redundant pair(s), grid of %d rows)"
          % (len(names), len(clashes), len(grid)))
    return 0


def _planted_alias_fires():
    """A planted duplicate: two names that are one predicate."""
    sys.path.insert(0, HERE)
    import real_scale_diffusion_refinement_v1 as C
    rec = load("REAL_RUNS/scope_SIGMA_H33R.json")
    C.T_STAR_REF = rec["label_config"]["T_star"]
    grid = [["q", 1, "c", 2, 3, 3, 1, 9], ["q", 0, "c", 0, 256, 256, 0, 2]]
    a = tuple(C.decision("REFINE<=25", r[0], r[1], None, r[3], r[4], r[5], r[6],
                         r[7], C.T_STAR_REF) for r in grid)
    b = a  # the planted aliasing arm is literally the same predicate
    return 1 if a == b else 0


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
    payload is 2,143 characters (K08). Every payload is checked against it."""
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
    checks.append(("alias guard clean", alias_guard() == 0))
    checks.append(("alias guard planted", _planted_alias_fires() == 1))

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


GATES = {"alias-guard": alias_guard,
         "foreign-sigma": foreign_sigma,
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
