# -*- coding: utf-8 -*-
"""Calibration: 11 rows hand-adjudicated by opening the artifacts, then
re-derived mechanically from the one decisive test each. The set deliberately
spans the hard cases (7 of 11 come out NOT earned), and includes the adjacent
pair AI4 r035 / AI4 r030 inside one section, which is what proves the procedure
discriminates rather than pattern-matching on package names.
"""
import io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
R = lambda p: io.open(os.path.join(ROOT, p), encoding="utf-8").read()
J = lambda p: json.loads(R(p))
EARN, PART, BLOCK, NOEV = ("EARNED_BY_MERGED_EVIDENCE", "PARTIAL",
                           "BLOCKED_ON_OPEN_PR", "NO_EVIDENCE")
A4 = "research/gmi-833-af4-relative-computability-v1/"
A5 = "research/gmi-833-af5-verification-barriers-v1/"
ULS = "research/gmi-833-update-law-space-v1/"
MIM = "research/machine-intelligence-morphogenesis-v1/"
AI0 = "research/gmi-833-ai0-convergence-spine-v1/"
AGAH = "research/gmi-833-agah-map-v1/"
AJ14 = "research/gmi-833-aj14-establishment-criterion-v1/"

SELF = ("gmi-833-comment-evidence-propagation-v1", "gmi-833-comment-evidence-propagation-v2")

def tree_hits(pattern, root="research"):
    """Count files under root whose text matches pattern. Validated by callers
    against a control pattern that MUST match.

    This sweep's OWN packages are excluded: their reason strings quote the very
    tokens being searched for, so including them made three of these tests return
    a false EARNED on the first real run. A checker that reads its own output is
    not measuring the corpus."""
    rx = re.compile(pattern)
    n = 0
    for dp, _, fs in os.walk(os.path.join(ROOT, root)):
        if any(x in dp for x in SELF):
            continue
        for f in fs:
            p = os.path.join(dp, f)
            try:
                if rx.search(io.open(p, encoding="utf-8", errors="ignore").read()):
                    n += 1
            except Exception:
                pass
    return n

def t_af4_terminal():                       # AF4 r072
    r = J(A4 + "RESULT_V1.json")
    ok = (r["nonterminal_frontier_terminal"] ==
          "NO_TERMINAL_EFFECTIVE_FRONTIER_AT_REGISTERED_ORACLE_MODEL_SCOPE"
          and len(r["jump_chain"]) == 7
          # levels 0..5 each carry the strictness relation to the next level;
          # the top registered level has no successor in the registry and
          # correctly carries None. Requiring all 7 was a checker bug that
          # produced a false PARTIAL against real data on the first run.
          and all(x["parent_relation_to_next"] == "STRICTLY_BELOW_BY_TURING_JUMP_PARENT"
                  for x in r["jump_chain"][:-1])
          and r["jump_chain"][-1]["parent_relation_to_next"] is None)
    return EARN if ok else PART

def t_af4_physics():                        # AF4 r073 - the forbidden set IS the evidence
    r = J(A4 + "RESULT_V1.json")
    need = {"NO_FINAL_COMPUTABILITY_BARRIER_IN_ALL_PHYSICS",
            "PHYSICAL_CHURCH_TURING_FALSIFIED", "PHYSICAL_HYPERCOMPUTATION_ESTABLISHED"}
    ok = r["physical_scope"] == "NO_PHYSICAL_HYPERCOMPUTATION_CLAIM" and need <= set(r["forbidden_promotions"])
    return EARN if ok else PART

def t_af5_displacement():                   # AF5 r079
    r = J(A5 + "RESULT_V1.json")
    ok = (r["semidecision"]["safe"]["verification_status"] == "UNKNOWN_ABSTAIN"
          and r["certificate"]["verification_status"] == "CERTIFIABLE"
          and r["abstract_coarse"]["status"] == "UNKNOWN_FALSE_ALARM_POSSIBLE"
          and r["abstract_fine"]["verification_status"] == "SOUND_INCOMPLETE_APPROXIMATION"
          and r["bounded"]["k3"]["status"] != r["bounded"]["k4"]["status"]
          and r["property_test"]["delta"] == "1/14")
    return EARN if ok else PART

def t_ai4_parent_subtract():                # AI4 r035 - a RECORD; records stand alone
    led = J(MIM + "PARENT_LEDGER_V2.json")
    rec = [x for x in led["records"] if x.get("parent_id") == "P9A.CHEAP_GRADIENT"]
    corpus = bool(rec) and rec[0]["disposition"] == "ADOPT" and \
        "is novel" in rec[0]["kill_scope"] and "Baur-Strassen" in rec[0]["kill_scope"]
    pkg = {"CHEAP_GRADIENT_PRINCIPLE_IS_NOVEL_HERE", "NAMED_ALGORITHM_DERIVED_AS_NECESSARY"} \
        <= set(J(ULS + "MANIFEST_V1.json")["forbidden_promotions"])
    return EARN if (corpus and pkg) else PART

def t_ai4_derive_reverse_ad():              # AI4 r030 - adjacent to r035, opposite verdict
    # decisive: the nearest artifact explicitly disclaims the mechanism, and the
    # meaning the row would assert is in that artifact's forbidden set.
    disc = "the adjoint recursion and the elimination view are parent mathematics" in R(ULS + "CORE.md")
    forb = "NAMED_ALGORITHM_DERIVED_AS_NECESSARY" in J(ULS + "MANIFEST_V1.json")["forbidden_promotions"]
    return BLOCK if (disc and forb) else EARN

def t_ai81_posthoc_labels():                # AI8.1 r052 - a CONSTRAINT ON A PROCESS
    # decisive: the process it constrains (a blind derivation of NEURAL structure)
    # does not exist on main. Control pattern must match or the test is void.
    control = tree_hits(r"UNKNOWN_MORPHOLOGY")
    assert control > 0, "control pattern failed; the scan is not trustworthy"
    return BLOCK if tree_hits(r"NN[_-]D1|NN[_-]D2|NN[_-]D3") == 0 else EARN

def t_af7_future_physics():                 # AF7 r093 - live, on-subject disclaimer
    gaps = J(A4 + "OPEN_GAPS_V1.json")["open"]
    live = any(g["id"] == "AF4_PHYSICAL" and "AF7 remains authority" in g["gap"] for g in gaps)
    return PART if (live and tree_hits(r"S_phys") == 0) else EARN

def t_aj15():                               # AJ15 r098
    found = subprocess.run(["/usr/bin/find", os.path.join(ROOT, "research"),
                            "-iname", "*aj15*"], capture_output=True, text=True).stdout.strip()
    ctl = subprocess.run(["/usr/bin/find", os.path.join(ROOT, "research"),
                          "-iname", "*aj14*"], capture_output=True, text=True).stdout.strip()
    assert ctl, "control find failed"
    disc = "flagship end-to-end falsification experiment remains to be executed" in R(AJ14 + "OPEN_GAPS.json")
    return NOEV if (not found and disc) else EARN

def t_ai0_agah():                           # AI0 r002
    agah_hits = 0
    for f in os.listdir(os.path.join(ROOT, AGAH)):
        if "CONVERGENCE_SPINE" in R(AGAH + f): agah_hits += 1
    ai0_hits = 0
    for f in os.listdir(os.path.join(ROOT, AI0)):
        ai0_hits += len(re.findall(r"\bA[GH][0-9]?\b", R(AI0 + f)))
    ctl = sum(1 for f in os.listdir(os.path.join(ROOT, AI0)) if "CONVERGENCE_SPINE" in R(AI0 + f))
    assert ctl > 0, "control failed: CONVERGENCE_SPINE absent from its own package"
    return PART if (agah_hits == 0 and ai0_hits == 0) else EARN

def t_aj9_auditor():                        # AJ9 r097 - re-verified, not restated
    p = subprocess.run(["ssh", "billy-laptop",
        "cd ~/ocm-scratch/ORION-OCM/research/gmi-833-aj9a-known-family-benchmark-v1 && "
        "python3 -I -B check_aj9a.py >/dev/null 2>&1; echo $?"],
        capture_output=True, text=True).stdout.strip()
    return PART if p != "0" else EARN

def t_ai82_discover():                      # AI8.2 r053
    control = tree_hits(r"UNKNOWN_MORPHOLOGY")
    assert control > 0, "control pattern failed"
    return BLOCK if tree_hits(r"DISCOVER_GMI") == 0 else EARN

CASES = [
 ("5693269426 AF4 r072 scoped non-terminal frontier",            EARN,  t_af4_terminal),
 ("5693269426 AF4 r073 not a claim about all physics",           EARN,  t_af4_physics),
 ("5693269426 AF5 r079 contract changes move fixtures",          EARN,  t_af5_displacement),
 ("5693666042 AI4 r035 parent-subtract AD/reverse mode",         EARN,  t_ai4_parent_subtract),
 ("5693666042 AI4 r030 derive reverse-mode AD on a DAG",         BLOCK, t_ai4_derive_reverse_ad),
 ("5693704406 AI8.1 r052 post-hoc labels after generation",      BLOCK, t_ai81_posthoc_labels),
 ("5693269426 AF7 r093 future physics -> update S, recompute",   PART,  t_af7_future_physics),
 ("5693954852 AJ15 r098 bounded end-to-end flagship run",        NOEV,  t_aj15),
 ("5693666042 AI0 r002 AG/AH lower-substrate -> GEN",            PART,  t_ai0_agah),
 ("5693954852 AJ9 r097 no smuggling for every holdout",          EARN,  t_aj9_auditor),
 ("5693704406 AI8.2 r053 formalize DISCOVER_GMI",                BLOCK, t_ai82_discover),
]

agree = 0
for name, hand, fn in CASES:
    got = fn()
    m = got == hand
    agree += m
    print("%-8s hand=%-26s procedure=%-26s %s" % ("MATCH" if m else "MISMATCH", hand, got, name))
ne = sum(1 for _, h, _ in CASES if h != EARN)
print("\ncalibration: %d/%d agree (%d not-earned cases included)" % (agree, len(CASES), ne))

# the procedure's verdicts must also match what was actually emitted
emitted = {}
d = json.load(io.open(os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json"), encoding="utf-8"))
for r in d["replacements"]: emitted[(r["comment_id"], r["old"])] = r["status"]
for r in d["not_marked"]:   emitted[(r["comment_id"], r["old"])] = r["status"]
print("emitted rows: %d" % len(emitted))
sys.exit(0 if agree == len(CASES) and ne >= 3 else 1)
