"""CI gates for gmi-833-h-real-scale-diffusion-refinement-v1, kept out of the
workflow YAML. Multi-line Python lives here so the YAML `run:` blocks stay one
line each. Gates: alias-guard, foreign-sigma, closure-consistency,
annotation-budget, two-route-namespace, terminology, selftest. Each prints
what it checked and exits non-zero when it fails.

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


# Redundancies that follow from the REGISTERED design and are therefore not
# defects. Each entry must be witnessed by the assertion below, which evaluates
# the pair on rows whose walk value is at the registered cap.
REDUNDANT_ARMS = {
    ("CARD>=1", "REFINE<=256"):
        "the refinement walk is capped at 256, so for every tally the predicate "
        "REFINE<=256 is exactly CARD>=1; the arm is retained because the "
        "registered base ladder contains 256 and the freeze is not re-cut here",
}


def alias_guard(language=None, declared=None):
    """No two registered arms may be the same predicate under two names.

    The sibling readout languages in this line have twice shipped arms that
    were decision-identical at every stage -- the H32 pair, and the H29
    TOPK2_FAN/UNION_FAN/WSUM_FAN and SEL_FAN/MEM_FALLBACK pairs -- which turns a
    measured tie into a register artefact rather than an ecology property.

    The grid is the exact DISCRIMINATING WITNESS SET for this language, not a
    sample. Every arm's predicate is a threshold test on one coordinate conjoined
    with band tests on the others, so for any two arms with different thresholds
    `t1 < t2` on the same coordinate the value `t1` is already a witness (the
    first arm accepts it, the second rejects it). Sweeping each axis over the
    union of that axis's registered thresholds therefore decides every pair, and
    the axes are swept with both registered fallback constants so an arm that
    reads the fallback constant is exercised where its fallback branch fires. A
    clash reported on this grid is a real redundancy, and is accepted only if it
    is declared in `declared`, which defaults to this package's REDUNDANT_ARMS.

    The gate carries the registered `T*` locally rather than assigning it onto
    the readout module: a checker that mutates the object it checks can leave it
    mutated for whatever runs next.
    """
    sys.path.insert(0, HERE)
    import grammar_dr_v1 as G
    import real_scale_diffusion_refinement_v1 as C
    rec = load("REAL_RUNS/scope_SIGMA_H33R.json")
    tstar = rec["label_config"]["T_star"]
    fallback = rec["query_fallback_label"]
    declared = REDUNDANT_ARMS if declared is None else declared
    if language is None:
        language = list(G.readouts((tstar,)))
    # the registered thresholds of each axis
    card_regs = sorted(set(G.CARD_THRESHOLDS))
    walk_regs = sorted(set(G.REFINE_BASE) | set(G.REFINEIN_THRESHOLDS)
                       | set(G.DRAW_THRESHOLDS))
    cnt_regs = sorted(set(G.CNT_THRESHOLDS))
    len_regs = sorted(set(G.LEN_THRESHOLDS))
    card_axis = sorted(set(card_regs) | set([0]))
    # the walk axis is the registered ladder: the base ladder, the adjacency
    # witnesses around T*, the 256 step cap and 0
    walk_axis = sorted(set(walk_regs) | set([0, G.STEP_CAP, tstar, tstar - 1]))
    draw_axis = sorted(set(walk_regs) | set([0]))
    cnt_axis = sorted(set(cnt_regs) | set([0]))
    len_axis = sorted(set(len_regs) | set([1, 2, 13, 14]))
    assert G.STEP_CAP == 256 and tstar in walk_axis, (G.STEP_CAP, tstar)
    assert max(walk_axis) == 256 and max(card_axis) == max(card_regs)
    # every registered threshold must occur somewhere on the swept grid, or the
    # grid is not a witness set for the registered language
    grid = []
    for card in card_axis:
        for ws in walk_axis:
            for dd in draw_axis:
                for cnt in cnt_axis:
                    for L in len_axis:
                        grid.append(["q", 0, "c", card, ws, dd, cnt, L])
    seen = ([row[3] for row in grid], [row[4] for row in grid],
            [row[6] for row in grid], [row[7] for row in grid])
    for regs, axis in zip((card_regs, walk_regs, cnt_regs, len_regs), seen):
        missing = [t for t in regs if t not in axis]
        assert not missing, "registered thresholds absent from the grid: %r" % (
            missing,)
    names = sorted(set(language))
    vecs = {}
    for name in names:
        for maj in (0, 1):
            C.FIT_MAJORITY = maj
            vecs[(name, maj)] = tuple(
                C.decision(name, r[0], r[1], None, r[3], r[4], r[5], r[6],
                           r[7], tstar) for r in grid)
    C.FIT_MAJORITY = fallback
    clashes = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if all(vecs[(a, m)] == vecs[(b, m)] for m in (0, 1)):
                clashes.append((a, b))
    undeclared = [c for c in clashes
                  if c not in declared and (c[1], c[0]) not in declared]
    if undeclared:
        print("ALIASED ARMS (undeclared): %r" % (undeclared[:3],))
        return 1
    # every declared redundancy must be witnessed at the cap it rests on
    for pair in declared:
        a, b = pair
        for r in (["q", 1, "c", 1, 256, 0, 1, 9],
                  ["q", 0, "c", 3, 256, 0, 2, 9]):
            C.FIT_MAJORITY = fallback
            if C.decision(a, r[0], r[1], None, r[3], r[4], r[5], r[6], r[7],
                          tstar) != C.decision(
                              b, r[0], r[1], None, r[3], r[4], r[5], r[6], r[7],
                              tstar):
                print("DECLARED REDUNDANCY DOES NOT HOLD: %r" % (pair,))
                return 1
    print("no undeclared aliasing among the %d registered arms over a grid of "
          "%d rows (%d conflict(s) found, %d declared)"
          % (len(names), len(grid), len(clashes), len(declared)))
    return 0


def _planted_alias_fires():
    """A planted duplicate, and the same pair declared, in both directions.

    The registered language holds one real duplicate, `CARD>=1` / `REFINE<=256`,
    which the design declares because the refinement walk is capped at 256.
    Evaluating the guard on that pair with the declaration WITHDRAWN must report
    a clash; with the declaration in place it must not. Asserting only the first
    direction would pass on a guard that fires on everything, and only the
    second would pass on a guard that fires on nothing.
    """
    planted = ["CARD>=1", "REFINE<=256"]
    declared = {("CARD>=1", "REFINE<=256"): "the registered step cap"}
    if alias_guard(language=planted, declared={}) != 1:
        return 0                      # the alarm case: must fire
    if alias_guard(language=planted, declared=declared) != 0:
        return 0                      # the no-alarm case: must be silent
    return 1


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
    checks.append(("alias guard clean", alias_guard() == 0))
    checks.append(("alias guard planted", _planted_alias_fires() == 1))
    checks.append(("alias guard declared is silent",
                   alias_guard(language=["CARD>=1", "REFINE<=256"]) == 0))

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
