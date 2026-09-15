"""Q: how much of the parent-subtraction programme actually has a live entry?

Section Q lists 23 research traditions and asks for a live reduction/ownership
entry for each.  Before writing 23 entries, the question is how many already
exist -- the corpus has `research/parent-absorption-v1/LEDGER.json`, a ledger
with exactly the right schema: parents with citations, what the parent
explained, a disposition, whether the parent is sufficient at scope, and the
residual.

This measures coverage.  It does NOT write entries.  That distinction matters:
an entry invented from memory, with plausible-sounding citations, would be worse
than an empty box, because an empty box is honest about not knowing.  The B1
audit made the same call and it is the same failure mode.

METHOD
    Each of the 23 traditions carries an explicit list of match tokens.  A
    ledger entry counts as covering a tradition when one of those tokens appears
    in the entry's family, id, or -- and this is where a crude scan fails -- in
    the NAMES OF ITS CITED PARENTS.  A ledger entry for "program_library_learning"
    citing DreamCoder covers Q's DreamCoder box; matching on family alone misses
    it.

    Every match is reported with the entry and the token that matched, so a
    reader can check the mapping rather than trust it.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REL = os.path.join("research", "parent-absorption-v1", "LEDGER.json")


def _find_ledger(start):
    """Walk upward until the ledger is found.

    A fixed ../../.. only resolves inside a full repo checkout, which makes the
    audit silently unrunnable anywhere else -- and an audit that cannot run in
    the place you are verifying it is not much of an audit.
    """
    d = start
    for _ in range(8):
        cand = os.path.join(d, REL)
        if os.path.exists(cand):
            return cand
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    raise SystemExit(
        "parent-absorption ledger not found by walking up from %s looking for "
        "%s -- this audit reads the whole repo, so it must run inside one"
        % (start, REL))


LEDGER = _find_ledger(HERE)

# Section Q's 23 traditions, verbatim order, with match tokens.
TRADITIONS = [
    ("Universal computation / lambda / register machines",
     ["lambda", "register machine", "turing", "universal computation"]),
    ("Solomonoff / MDL / algorithmic probability",
     ["solomonoff", "mdl", "algorithmic probability", "kolmogorov",
      "structured_compression", "abstract-interpr"]),
    ("Levin / OOPS / PowerPlay / Goedel machines",
     ["levin", "oops", "powerplay", "goedel", "godel", "self_change_search",
      "self-change"]),
    ("AIXI / universal intelligence", ["aixi", "universal intelligence", "hutter"]),
    ("NFL / bounded rationality / rational metareasoning",
     ["nfl", "no free lunch", "bounded rational", "metareason",
      "algorithm_selection", "ski-rental", "ski_rental"]),
    ("AutoML-Zero / NAS / NEAT / evolutionary computation",
     ["automl", "nas", "neat", "evolutionary computation", "genetic programming"]),
    ("MAML / learned optimizers / meta-RL",
     ["maml", "learned optimizer", "meta-rl", "meta-learning"]),
    ("DreamCoder / Stitch / program synthesis / GP",
     ["dreamcoder", "stitch", "program synthesis", "program_library",
      "lilo", "voyager", "minton", "ebl"]),
    ("Bayesian inference / probabilistic programming / BPL",
     ["bayesian", "probabilistic programming", "bpl"]),
    ("Categorical / compositional learning theory",
     ["categor", "compositional learning", "functor"]),
    ("ACT-R / Soar / NARS / OpenCog / cognitive architectures",
     ["act-r", "soar", "nars", "opencog", "cognitive architecture"]),
    ("RL / hierarchical RL / model-based planning",
     ["reinforcement", "hierarchical rl", "model-based planning", "mdp"]),
    ("Active inference / predictive processing",
     ["active inference", "predictive processing", "free energy"]),
    ("Causal inference / SCM / active causal learning",
     ["causal", "scm", "structural causal"]),
    ("Memory systems / CLS / continual learning",
     ["complementary learning", "cls", "continual learning", "replay"]),
    ("RAG / databases / caches / model editing",
     ["retrieval-augmented", "rag", "database", "cache", "model editing",
      "sqlite", "wal", "indexing", "dbsp", "ivm"]),
    ("MoE / modular continual learning",
     ["mixture of experts", "moe", "modular continual"]),
    ("Neuro-symbolic systems",
     ["neuro-symbolic", "neurosymbolic", "tms", "atms", "metamath",
      "proof_compression", "cd_tools"]),
    ("GNN / message passing / CSP / SAT / factor graphs",
     ["gnn", "message passing", "csp", "sat solver", "factor graph",
      "provenance", "semiring"]),
    ("Hyperdimensional / vector-symbolic computing",
     ["hyperdimensional", "vector-symbolic", "vsa", "holographic"]),
    ("Neural cellular automata / morphogenetic computation",
     ["cellular automata", "morphogenetic", "neural ca"]),
    ("Evolutionary / open-ended artificial-life systems",
     ["open-ended", "artificial life", "alife", "novelty search"]),
    ("Analog / physical / quantum computation",
     ["analog", "quantum", "physical computation", "reservoir"]),
]

led = json.load(open(LEDGER))
ENTRIES = led["entries"]

print("=" * 96)
print("Q: PARENT-SUBTRACTION COVERAGE -- how many of the 23 traditions have a live entry?")
print("=" * 96)
print("  ledger    : research/parent-absorption-v1/LEDGER.json")
print("  entries   : %d" % len(ENTRIES))
print("  traditions: %d" % len(TRADITIONS))


def haystack(e):
    """Family, id, AND the names/citations of the cited parents.

    Matching on family alone misses real coverage: the program_library_learning
    entries cite DreamCoder and Stitch by name, which is what makes them cover
    Q's DreamCoder box.
    """
    bits = [str(e.get("family", "")), str(e.get("id", ""))]
    for p in e.get("parents", []) or []:
        bits.append(str(p.get("name", "")))
        bits.append(str(p.get("citation", "")))
    return " ".join(bits).lower()


HAY = [(e, haystack(e)) for e in ENTRIES]

covered, uncovered = [], []
print()
print("-" * 96)
print("COVERAGE")
print("-" * 96)
for name, tokens in TRADITIONS:
    matches = []
    for e, h in HAY:
        for t in tokens:
            if t in h:
                matches.append((e.get("id", "?"), t, e.get("disposition", "?")))
                break
    if matches:
        covered.append((name, matches))
        ids = ", ".join("%s[%s]" % (i, t) for i, t, _ in matches[:3])
        print("  COVERED   %-52s %s" % (name[:52], ids))
    else:
        uncovered.append(name)
        print("  --        %-52s" % name[:52])

print()
print("  covered   : %d of %d" % (len(covered), len(TRADITIONS)))
print("  uncovered : %d of %d" % (len(uncovered), len(TRADITIONS)))

# --- gates ---------------------------------------------------------------
assert covered, "no tradition is covered -- the token map is broken, not the ledger"
assert uncovered, (
    "every tradition is covered, which would mean section Q is already complete; "
    "that is not credible and almost certainly means the match tokens are too "
    "permissive")

# A tradition matched by MANY entries via a single generic token is suspicious.
generic = [(n, m) for n, m in covered if len(m) >= 6]
assert not generic, (
    "a tradition matched six or more ledger entries, which suggests a token is "
    "generic enough to match anything: %s" % [n for n, _ in generic])

# An entry that "covers" many unrelated traditions is matching incidentally --
# a citation mentioning Bayesian methods does not make a self-change-search entry
# a parent-subtraction record for Bayesian inference.  Coverage that rests
# ONLY on such an entry is downgraded to SUSPECT and excluded from the count.
entry_span = {}
for n, ms in covered:
    for i, _t, _d in ms:
        entry_span.setdefault(i, set()).add(n)
promiscuous = {i for i, ns in entry_span.items() if len(ns) >= 3}
suspect = []
solid = []
for n, ms in covered:
    if all(i in promiscuous for i, _t, _d in ms):
        suspect.append((n, ms))
    else:
        solid.append((n, ms))

print()
print("-" * 96)
print("VALIDATING THE COVERAGE CLAIM")
print("-" * 96)
if promiscuous:
    for i in sorted(promiscuous):
        print("  entry %-28s matches %d traditions: %s"
              % (i, len(entry_span[i]), "; ".join(sorted(entry_span[i])[:3])))
    print("  -> an entry spanning three or more traditions is matching")
    print("     incidentally, not substantively.")
print()
print("  coverage resting ONLY on such an entry (SUSPECT, not counted):")
for n, ms in suspect:
    print("     %-54s via %s" % (n[:54], ", ".join(i for i, _t, _d in ms)))
if not suspect:
    print("     none")
print()
print("  SOLID coverage   : %d of %d" % (len(solid), len(TRADITIONS)))
print("  SUSPECT coverage : %d" % len(suspect))
print("  no coverage      : %d" % len(uncovered))
assert len(solid) + len(suspect) == len(covered)
assert solid, "no coverage survives the promiscuity check"

dispositions = {}
for _n, ms in covered:
    for _i, _t, d in ms:
        dispositions[d] = dispositions.get(d, 0) + 1
print()
print("  dispositions among covering entries: %s" % dict(sorted(dispositions.items())))
assert len(dispositions) > 1, (
    "every covering entry has the same disposition, so the ledger is not "
    "discriminating between adopt, adapt, reject and leave-open")

OUT = {
    "corpus_audit": True,
    "ledger_path": "research/parent-absorption-v1/LEDGER.json",
    "ledger_entries": len(ENTRIES),
    "traditions_total": len(TRADITIONS),
    "traditions_covered_raw": len(covered),
    "traditions_covered_solid": len(solid),
    "traditions_covered_suspect": len(suspect),
    "suspect_traditions": [n for n, _ in suspect],
    "promiscuous_entries": sorted(promiscuous),
    "traditions_uncovered": len(uncovered),
    "covered": {n: [{"entry": i, "matched_token": t, "disposition": d}
                    for i, t, d in ms] for n, ms in covered},
    "uncovered": uncovered,
    "dispositions_among_covering_entries": dispositions,
    "method": (
        "each tradition carries explicit match tokens; an entry covers it when a "
        "token appears in the entry's family, id, or the names/citations of its "
        "cited parents -- matching on family alone misses real coverage"),
    "scope": (
        "this measures COVERAGE only. It does not assess whether a covering "
        "entry is adequate, and it writes no entries: an entry invented from "
        "memory with plausible citations would be worse than an empty box"),
}

print()
print("=" * 96)
print("WHAT THIS ESTABLISHES")
print("=" * 96)
print("  Section Q has SOLID coverage on %d of %d traditions, SUSPECT on %d," % (len(solid), len(TRADITIONS), len(suspect)))
print("  and none on %d.  Suspect means the only matching entry also matches" % len(uncovered))
print("  two or more unrelated traditions, so the match is incidental.")
print("  The %d uncovered traditions are named, so the gap is a list rather" % len(uncovered))
print("  than an unknown.")
print()
print("  NOT established: whether a covering entry is ADEQUATE.  Coverage means")
print("  an entry exists and cites that tradition, not that the subtraction is")
print("  complete.  And no entry is written here -- an entry invented from")
print("  memory, with plausible-sounding citations, would be worse than an empty")
print("  box, because an empty box is honest about not knowing.")

os.makedirs(os.path.join("microscopes", "results"), exist_ok=True)
with open(os.path.join("microscopes", "results",
                       "STAGE_PARENT_COVERAGE_V1.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, sort_keys=True)
print()
print("  receipt: microscopes/results/STAGE_PARENT_COVERAGE_V1.json")
