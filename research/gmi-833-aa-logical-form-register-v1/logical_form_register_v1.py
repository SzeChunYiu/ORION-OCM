#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Route A of `gmi-833-aa-logical-form-register-v1` (issue #833, section AA).

Builds the LOGICAL-FORM REGISTER over the census population fixed in
FREEZE_V1.md section 4, the WARRANT column of section 6, and runs the five
discriminators of section 7 with the hostiles of section 8 and the null of
section 9.  Stdlib only; Python 3.8+; every reported quantity is an `int`
or an exact `Fraction`.

    python3 -I -B research/gmi-833-aa-logical-form-register-v1/logical_form_register_v1.py

Writes (byte-deterministically):
    STATEMENT_SNAPSHOT_V1.json      statement / proof / falsifier bytes per object
    LOGICAL_FORM_REGISTER_V1.json   the register (form + warrant per object)
    QUEUES_V1.json                  the five review queues
and prints the route-A result document on stdout.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PKG = "research/gmi-833-aa-logical-form-register-v1"
CENSUS_PATH = "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
CENSUS_BLOB = "709159c53c6284366aaf1f05380f5fada8d81a98"
CENSUS_FROZEN_SHA = "2fffb14447193cbfbed3224508a077f2d4f5d2dd"
SNAPSHOT = HERE / "STATEMENT_SNAPSHOT_V1.json"
REGISTER = HERE / "LOGICAL_FORM_REGISTER_V1.json"
QUEUES = HERE / "QUEUES_V1.json"
HAND = HERE / "HAND_REGISTER_V1.json"

HAND_SAMPLE_SIZE = 40
HAND_SEED = 833
HAND2_SAMPLE_SIZE = 20   # amendment 01 (e): warrant-only hand sample
HAND2_SEED = 834
NULL_SEED = 2026
NULL_DRAWS = 200
ROWS = ("AA16", "AA17", "AA18", "AA20", "AA22")
RUN_MODES = ("EMPIRICAL_EXPERIMENT", "STATISTICAL_EXPERIMENT")
CLEAN_MODES = ("ANALYTIC_DEDUCTIVE", "MECHANIZED_PROOF",
               "COMPUTER_ASSISTED_EXHAUSTIVE", "FINITE_EXECUTABLE_CERTIFICATE")


# ---------------------------------------------------------------------------
# exact PRNG (64-bit LCG, high bits only -- never `% small` on the raw state)
# ---------------------------------------------------------------------------
class LCG:
    A = 6364136223846793005
    C = 1442695040888963407
    M = 1 << 64

    def __init__(self, seed: int) -> None:
        self.x = seed % self.M

    def below(self, n: int) -> int:
        self.x = (self.A * self.x + self.C) % self.M
        return (self.x >> 33) % n

    def sample(self, items: Sequence, k: int) -> List:
        pool = list(items)
        out = []
        while pool and len(out) < k:
            out.append(pool.pop(self.below(len(pool))))
        return out

    def shuffle(self, items: Sequence) -> List:
        pool = list(items)
        out = []
        while pool:
            out.append(pool.pop(self.below(len(pool))))
        return out


# ---------------------------------------------------------------------------
# population (FREEZE section 4)
# ---------------------------------------------------------------------------
THEOREM_ARTIFACT = re.compile(r"THEOREM", re.IGNORECASE)
BOLD_LED = re.compile(
    r"^\*\*(Theorem|Lemma|Proposition|Corollary|Law|Claim|[A-Z][A-Z0-9]*-[A-Z0-9.]+)\b")


def key_of(obj: Dict[str, object]) -> str:
    return "%s::%s" % (obj["source_path"], obj["object_id"])


def locator_line(obj: Dict[str, object]) -> int:
    loc = str(obj["source_locator"])
    return int(loc[1:]) if loc.startswith("L") else int(loc)


def load_census() -> Dict[str, object]:
    with open(REPO / CENSUS_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def population(census: Dict[str, object]) -> Tuple[List[Dict[str, object]], int]:
    """Returns (members sorted by key, count of NOT_A_STATEMENT_LINE)."""
    best = {}  # type: Dict[str, Dict[str, object]]
    mention = 0
    for o in census["scientific_objects"]:
        if o.get("id_kind") != "EXPLICIT":
            continue
        path = str(o["source_path"])
        if not path.endswith(".md") or not THEOREM_ARTIFACT.search(Path(path).name):
            continue
        st = str(o["statement"])
        if st.startswith("## "):
            kind = "H2"
        elif BOLD_LED.match(st):
            kind = "BOLD"
        else:
            mention += 1
            continue
        k = key_of(o)
        rec = dict(o)
        rec["kind"] = kind
        rec["line"] = locator_line(o)
        if k not in best or rec["line"] < best[k]["line"]:
            best[k] = rec
    return [best[k] for k in sorted(best)], mention


# ---------------------------------------------------------------------------
# extraction (FREEZE section 4.1)
# ---------------------------------------------------------------------------
def git(*args: str) -> Tuple[int, bytes]:
    try:
        proc = subprocess.run(["git", "-C", str(REPO)] + list(args),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return 1, b""
    return proc.returncode, proc.stdout


_blob_cache = {}  # type: Dict[str, Optional[List[str]]]


def blob_lines(sha: str) -> Optional[List[str]]:
    if sha not in _blob_cache:
        rc, out = git("cat-file", "-p", sha)
        _blob_cache[sha] = None if rc != 0 else out.decode("utf-8", "replace").split("\n")
    return _blob_cache[sha]


LABEL = re.compile(r"^\s*(?:>\s*)?\*\*([A-Z][^*]{0,80}?)\*\*[:.]?\s*(.*)$")
STATEMENT_LABEL = re.compile(
    r"^(Statement|Theorem|Lemma|Proposition|Corollary|Law|Claim|Result)\b", re.IGNORECASE)
# `Derivation consequence` / `Derivation notes` subsections are interpretation,
# not proofs (KF-6/KF-17/KF-20/KF-21 carry only those); a `Construction` is the
# proof of an existential.
PROOF_LABEL = re.compile(r"^(H3:)?\s*(Proof(?: sketch)?|Derivation|Construction)\b(?!\s+(?:consequence|notes|note|remark))",
                         re.IGNORECASE)
FALSIFIER_LABEL = re.compile(r"^(H3:)?\s*(Falsifier|Counterexample)", re.IGNORECASE)
STATUS_LINE = re.compile(r"^\s*(\*\*)?Status:")


def blocks_after(lines: List[str], start: int, bold_first: bool) -> List[Tuple[str, str]]:
    """Cut the region into labelled blocks. Stops at the next `## `/`# `."""
    blocks = []  # type: List[Tuple[str, List[str]]]
    cur = ("LEAD", [])  # type: Tuple[str, List[str]]
    fenced = False
    math = False
    first = True
    for raw in lines[start:]:
        s = raw.lstrip("> ").rstrip()
        if (s.startswith("## ") or s.startswith("# ")) and not (first and bold_first):
            break
        if s.startswith("```"):
            fenced = not fenced
            if fenced:
                cur[1].append("<CODE>")
            first = False
            continue
        if fenced:
            continue
        if s.strip() == "$$":
            math = not math
            if math:
                cur[1].append("<MATH>")
            first = False
            continue
        if math:
            continue
        m = LABEL.match(s)
        if m and not STATUS_LINE.match(s):
            blocks.append((cur[0], cur[1]))
            cur = (m.group(1).strip().rstrip(".:"), [m.group(2)])
            first = False
            continue
        if s.startswith("### "):
            blocks.append((cur[0], cur[1]))
            cur = ("H3:" + s[4:].strip(), [])
            first = False
            continue
        if STATUS_LINE.match(s):
            first = False
            continue
        cur[1].append(s)
        first = False
    blocks.append((cur[0], cur[1]))
    return [(lab, " ".join(x.strip() for x in body if x.strip())) for lab, body in blocks]


DISPLAY_MATH = re.compile(r"\\\[.*?\\\]|\$\$.*?\$\$|\\\(.*?\\\)", re.DOTALL)
INLINE_MATH_DOLLAR = re.compile(r"(?<![\\$])\$[^$\n]{1,200}\$")


def normalize_text(text: str) -> str:
    text = DISPLAY_MATH.sub(" <MATH> ", text)
    text = INLINE_MATH_DOLLAR.sub(" <MATH> ", text)
    text = text.replace("`", "")
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"(?<!\w)\*(?!\w)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


INLINE_PROOF = re.compile(r"\bProof(?: sketch)?\.\s+")


def extract(obj: Dict[str, object]) -> Optional[Dict[str, object]]:
    lines = blob_lines(str(obj["source_blob"]))
    if lines is None:
        return None
    ln = obj["line"] - 1
    if ln >= len(lines):
        return {"error": "LOCATOR_OUT_OF_RANGE"}
    if lines[ln].lstrip("> ").strip() != str(obj["statement"]).strip():
        return {"error": "LOCATOR_MISMATCH"}
    if obj["kind"] == "H2":
        heading = str(obj["statement"])[3:].strip()
        blocks = blocks_after(lines, ln + 1, False)
    else:
        heading = ""
        blocks = blocks_after(lines, ln, True)
    statement = ""
    stmt_source = "NONE"
    for lab, txt in blocks:
        if lab == "LEAD":
            if txt.strip():
                statement, stmt_source = txt, "LEAD"
                break
        elif STATEMENT_LABEL.match(lab) or lab.startswith(str(obj["object_id"])):
            statement, stmt_source = txt, lab
            break
        else:
            break  # a non-statement block (Proof, Falsifiers, H3 ...) before any statement
    proof = ""
    falsifier = ""
    for lab, txt in blocks:
        if PROOF_LABEL.match(lab) and not proof:
            proof = txt
        elif FALSIFIER_LABEL.match(lab) and not falsifier:
            falsifier = txt
    statement = normalize_text(statement)
    m = INLINE_PROOF.search(statement)
    if m:
        if not proof:
            proof = statement[m.end():]
        statement = statement[:m.start()].strip()
    return {
        "heading": normalize_text(heading),
        "statement": statement,
        "statement_source": stmt_source,
        "proof": normalize_text(proof),
        "falsifier": normalize_text(falsifier),
        "block_labels": [lab for lab, _ in blocks][:12],
    }


def build_snapshot(members: List[Dict[str, object]]) -> Tuple[Dict[str, object], str]:
    """Returns (snapshot, blob_state) where blob_state is BLOBS_REACHABLE or
    BLOBS_UNREACHABLE (then the committed snapshot is loaded instead)."""
    records = {}
    unreachable = 0
    for o in members:
        ex = extract(o)
        if ex is None:
            unreachable += 1
            continue
        rec = {
            "object_id": o["object_id"],
            "source_path": o["source_path"],
            "source_locator": o["source_locator"],
            "source_blob": o["source_blob"],
            "kind": o["kind"],
            "object_class": o["object_class"],
            "vendored": "/raw/" in str(o["source_path"]),
            "evidence_mode": o["proof_evidence_mode"],
            "quantifier_class": o["quantifier_class"],
        }
        rec.update(ex)
        records[key_of(o)] = rec
    if unreachable:
        if SNAPSHOT.exists():
            with open(SNAPSHOT, "r", encoding="utf-8") as fh:
                snap = json.load(fh)
            snap["blob_state"] = "BLOBS_UNREACHABLE"
            return snap, "BLOBS_UNREACHABLE"
        raise SystemExit("blobs unreachable and no committed snapshot")
    snap = {"schema": "GMI_833_STATEMENT_SNAPSHOT_V1", "package": PKG,
            "census_blob": CENSUS_BLOB, "population": len(records),
            "blob_state": "BLOBS_REACHABLE", "records": records}
    return snap, "BLOBS_REACHABLE"


# ---------------------------------------------------------------------------
# sentences (FREEZE section 4.2)
# ---------------------------------------------------------------------------
ABBREV = ("e.g.", "i.e.", "cf.", "vs.", "resp.", "etc.", "Eq.", "Thm.", "Def.",
          "Sec.", "Fig.", "no.", "approx.", "w.r.t.", "a.s.", "i.i.d.", "viz.",
          "Prop.", "Lem.", "Cor.", "Ex.", "Ch.", "pp.", "p.", "St.", "Dr.")
HYP_ONLY = re.compile(r"^(Let|Suppose|Assume|Fix|Consider|Given)\b")
CONCL_LEAD = re.compile(
    r"^(Then|Therefore|Hence|Thus|Consequently|So|In particular|Moreover|Furthermore)\b[,:]?\s+")


def split_sentences(text: str) -> List[str]:
    t = text
    for ab in ABBREV:
        t = t.replace(ab, ab.replace(".", "§"))
    t = re.sub(r"(\d)\.(\d)", "\\1§\\2", t)
    t = re.sub(r"\b([A-Z])\.([A-Z])\b", "\\1§\\2", t)
    t = re.sub(r"\s+-{3,}\s*", " . ", t)
    t = re.sub(r"\s+[-*]\s+(?=\S)", " . ", t)
    t = re.sub(r"(<MATH>|<CODE>)\s+(?=(?:If|Then|Thus|Therefore|Hence|Consequently|Equivalently|For|The|This|In|A|An|It|So|Moreover|When|Whenever|Let|Suppose|Assume|Since|By|Because|Under|There|Every|Any|No|With|Without|Conversely|Otherwise|Where)\b)", r"\1. ", t)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z<(\[\"'])", t)
    out = []
    for p in parts:
        p = p.replace("§", ".").strip().strip(".").strip()
        if p and re.search(r"[A-Za-z<]", p):
            out.append(p)
    return out


def hypothesis_chain(statement: str) -> Tuple[List[str], Optional[str], bool]:
    """(hypotheses, conclusion sentence or None, trailing_dropped)."""
    sents = split_sentences(statement)
    hyps = []  # type: List[str]
    concl = None
    idx = None
    for i, s in enumerate(sents):
        if HYP_ONLY.match(s):
            hyps.append(s)
            continue
        concl = s
        idx = i
        break
    trailing = idx is not None and idx < len(sents) - 1
    if concl is not None:
        concl = CONCL_LEAD.sub("", concl, count=1)
    return hyps, concl, trailing


# ---------------------------------------------------------------------------
# grammar (FREEZE section 5; amendment 01 for the <MATH> relation lexicon)
# ---------------------------------------------------------------------------
REL_CUES = (
    ("EQ", (r"\bis exactly\b", r"\bequals?\b", r"\bis precisely\b", r"(?<![<>!])=(?!=)",
            r"\b(?:is|are) <MATH>", r"\bexactly\b")),
    ("LE", (r"\bat most\b", r"\bno more than\b", r"<=", r"\\le\b", r"\bbounded above by\b",
            r"\bupper bound", r"\bnever (?:increase|exceed)", r"\bnot exceed")),
    ("GE", (r"\bat least\b", r"\bno fewer than\b", r">=", r"\\ge\b", r"\bbounded below by\b",
            r"\blower bound", r"\brequires at least\b")),
    ("OPT", (r"\boptimal\b", r"\boptimum\b", r"\bminimal\b", r"\bminimum\b", r"\bmaximal\b",
             r"\bmaximum\b", r"\bargmin\b", r"\bargmax\b", r"\bminimi[sz]er\b",
             r"\bmaximi[sz]er\b", r"\bbest\b")),
    ("CAUSAL", (r"\bcauses?\b", r"\bcaused by\b", r"\bcausal\b", r"\bdo\(", r"\bintervention",
                r"\bintervene")),
    ("EXISTS", (r"\bexists?\b", r"\bthere is an?\b", r"\battained\b")),
)
REL_COMPILED = [(rel, [re.compile(p, re.IGNORECASE) for p in pats]) for rel, pats in REL_CUES]
ROLE_VOCAB = re.compile(
    r"\b(necessary|sufficient|suffices|requires|needs|only if|iff|if and only if|necessity|sufficiency)\b",
    re.IGNORECASE)
INTERVENTIONAL = re.compile(r"do\(|\bintervention|\bintervene|\brandomi[sz]ed\b", re.IGNORECASE)
NEG_LEAD = re.compile(r"^(not|no|never|neither)\b", re.IGNORECASE)
NEG_VERB = re.compile(
    r"\b(cannot|can not|does not|do not|is not|are not|fails? to|is never|are never|there is no|no longer)\b",
    re.IGNORECASE)
CLAUSE_AND = re.compile(r"(?:;\s*and\s+|,\s*and\s+)(?=(?:the|a|an|no|every|each|its|their|all|any|some|there|if|for|it)\b)",
                        re.IGNORECASE)
CLAUSE_OR = re.compile(r"(?:;\s*or\s+|,\s*or\s+)(?=(?:the|a|an|no|every|each|its|their|all|any|some|there|if|for|it)\b)",
                       re.IGNORECASE)


def rel_class(text: str) -> str:
    best = None  # type: Optional[Tuple[int, str]]
    for rel, pats in REL_COMPILED:
        for p in pats:
            m = p.search(text)
            if m and (best is None or m.start() < best[0]):
                best = (m.start(), rel)
    return best[1] if best else "PRED"


def atom(text: str) -> List[object]:
    text = text.strip().strip(",;:").strip()
    node = ["atom", text, rel_class(text)]  # type: List[object]
    if NEG_LEAD.match(text) or NEG_VERB.search(text):
        return ["not", node]
    return node


def clause(text: str) -> List[object]:
    parts = CLAUSE_AND.split(text)
    if len(parts) > 1:
        node = clause(parts[0])
        for p in parts[1:]:
            node = ["and", node, clause(p)]
        return node
    parts = CLAUSE_OR.split(text)
    if len(parts) > 1:
        node = clause(parts[0])
        for p in parts[1:]:
            node = ["or", node, clause(p)]
        return node
    return atom(text)


R1_IFF = re.compile(r"^(.+?)\s+(?:iff|if and only if|exactly when)\s+(.+)$", re.IGNORECASE)
R1_NS = re.compile(r"^(.+?)\s+(?:is|are)\s+(?:both\s+)?necessary and sufficient for\s+(.+)$", re.IGNORECASE)
R2_IF_THEN = re.compile(r"^If\s+(.+?),?\s+then\s+(.+)$", re.IGNORECASE)
R2_IF_COMMA = re.compile(r"^If\s+(.+?),\s+(.+)$", re.IGNORECASE)
R2_WHENEVER = re.compile(r"^(?:Whenever|When)\s+(.+?),\s+(.+)$", re.IGNORECASE)
R2_IMPLIES = re.compile(r"^(.+?)\s+implies\s+(.+)$", re.IGNORECASE)
R2_TRAIL_IF = re.compile(r"^(.+?)\s+(?:if|whenever|provided that|provided)\s+(.+)$", re.IGNORECASE)
R2_CONTEXT_IF_THEN = re.compile(r"^(.+?),\s+if\s+(.+?),?\s+then\s+(.+)$", re.IGNORECASE)
R6_IT_SUFFICES_TO = re.compile(r"^It (?:suffices|is sufficient) to\s+(.+)$", re.IGNORECASE)
R6_SUFF_COND = re.compile(r"^A sufficient condition for\s+(.+?)\s+is\s+(?:that\s+)?(.+)$", re.IGNORECASE)
R5_NEC_COND = re.compile(r"^A necessary condition for\s+(.+?)\s+is\s+(?:that\s+)?(.+)$", re.IGNORECASE)
R3_ONLY_IF = re.compile(r"^(.+?)\s+only if\s+(.+)$", re.IGNORECASE)
R4_UNLESS = re.compile(r"^(.+?)\s+unless\s+(.+)$", re.IGNORECASE)
R5_NECESSARY = re.compile(r"^(.+?)\s+(?:is|are)\s+necessary for\s+(.+)$", re.IGNORECASE)
# `requires` is a logical necessity only when its object is a condition, not a
# quantity: "X requires <MATH> bits" / "requires at least k" is a bound (R9).
R5_REQUIRES = re.compile(r"^(.+?)\s+(?:requires|needs)\s+(?!(?:<MATH>|\d|at least|at most|exactly|only|zero|one|two|no more|fewer|more|by))(.+)$",
                         re.IGNORECASE)
R6_SUFFICIENT = re.compile(r"^(.+?)\s+(?:is|are)\s+sufficient for\s+(.+)$", re.IGNORECASE)
R6_SUFFICES_FOR = re.compile(r"^(.+?)\s+suffices for\s+(.+)$", re.IGNORECASE)
R6_IT_SUFFICES = re.compile(r"^It (?:suffices|is sufficient) that\s+(.+)$", re.IGNORECASE)
R7_FOR_EVERY = re.compile(r"^For\s+(?:every|all|each|any)\s+([^,]+?),\s+(.+)$", re.IGNORECASE)
R7_EVERY = re.compile(r"^(?:Every|Any|All)\s+(.+?)\s+(is|are|has|have|must|can|cannot|requires|satisfies|admits|uses|yields|needs|does|equals|lies|belongs|contains|induces|determines)\b(\s.+)$",
                      re.IGNORECASE)
R7_NO = re.compile(r"^No\s+(.+?)\s+(is|are|has|have|can|satisfies|admits|uses|yields|does|equals|determines|contains|recovers|achieves|exists)\b(\s.+)$",
                   re.IGNORECASE)
R8_THERE_EXIST = re.compile(r"^There\s+(?:exists?|is an?|are)\s+(.+?)\s+(?:such that|with|for which|so that)\s+(.+)$",
                            re.IGNORECASE)
R8_THERE_EXIST_BARE = re.compile(r"^There\s+(?:exists?|is an?|are)\s+(.+)$", re.IGNORECASE)
R8_FOR_SOME = re.compile(r"^(.+?)\s+for some\s+(.+)$", re.IGNORECASE)
UNDER = re.compile(r"^(?:Under|Given|Assuming)\s+([^,]+?),\s+(.+)$", re.IGNORECASE)
DOMAIN_SPLIT = re.compile(r"^(.+?)\s+(?:in|of|with|over|on|from)\s+(.+)$", re.IGNORECASE)


def var_domain(phrase: str) -> Tuple[str, str]:
    m = DOMAIN_SPLIT.match(phrase.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return phrase.strip(), "-"


def has_rel_cue(text: str) -> bool:
    return rel_class(text) != "PRED"


def parse_sentence(sent: str, goal: str, depth: int = 0) -> Tuple[Optional[Dict[str, object]], str]:
    """Returns (form_or_None, rule). form = {prefix, matrix}."""
    s = sent.strip().rstrip(".").strip()
    if not s or depth > 6:
        return None, "NO_GRAMMAR_RULE"
    prefix = []  # type: List[List[str]]
    hyps = []  # type: List[List[object]]
    # anchored prefix peeling (R7 / R8 / Under) before the trailing variants
    while True:
        m = R7_FOR_EVERY.match(s)
        if m:
            v, d = var_domain(m.group(1))
            prefix.append(["forall", v, d])
            s = m.group(2).strip()
            continue
        m = R8_THERE_EXIST.match(s)
        if m:
            v, d = var_domain(m.group(1))
            prefix.append(["exists", v, d])
            s = m.group(2).strip()
            continue
        m = UNDER.match(s)
        if m:
            hyps.append(clause(m.group(1)))
            s = m.group(2).strip()
            continue
        break
    matrix = None  # type: Optional[List[object]]
    rule = ""
    m = R2_CONTEXT_IF_THEN.match(s)
    if m and not re.match(r"^(?:If|Whenever|When)\b", s, re.IGNORECASE):
        hyps.append(clause(m.group(1)))
        s = "If %s, then %s" % (m.group(2), m.group(3))
    for name, rx, shape in (("R1_IFF", R1_IFF, "iff"), ("R1_NS", R1_NS, "iff"),
                            ("R2_IF_THEN", R2_IF_THEN, "imp"), ("R2_IF_COMMA", R2_IF_COMMA, "imp"),
                            ("R6_SUFF_COND", R6_SUFF_COND, "rev"), ("R5_NEC_COND", R5_NEC_COND, "imp"),
                            ("R6_IT_SUFFICES_TO", R6_IT_SUFFICES_TO, "goal"),
                            ("R2_WHENEVER", R2_WHENEVER, "imp"), ("R2_IMPLIES", R2_IMPLIES, "imp"),
                            ("R3_ONLY_IF", R3_ONLY_IF, "imp"), ("R4_UNLESS", R4_UNLESS, "unless"),
                            ("R5_NECESSARY", R5_NECESSARY, "rev"), ("R5_REQUIRES", R5_REQUIRES, "rev"),
                            ("R6_SUFFICIENT", R6_SUFFICIENT, "imp"), ("R6_SUFFICES_FOR", R6_SUFFICES_FOR, "imp"),
                            ("R6_IT_SUFFICES", R6_IT_SUFFICES, "goal"),
                            ("R2_TRAIL_IF", R2_TRAIL_IF, "rev")):
        m = rx.match(s)
        if not m:
            continue
        if name == "R2_TRAIL_IF" and re.search(r"\biff\b|if and only if|\bthen\b", s, re.IGNORECASE):
            continue
        if shape == "goal":
            matrix = ["->", clause(m.group(1)), ["atom", goal or "GOAL", rel_class(goal or "")]]
        else:
            left, right = clause(m.group(1)), clause(m.group(2))
            if shape == "iff":
                matrix = ["<->", left, right]
            elif shape == "imp":
                matrix = ["->", left, right]
            elif shape == "rev":
                matrix = ["->", right, left]
            elif shape == "unless":
                matrix = ["->", ["not", right] if right[0] != "not" else right[1], left]
        rule = name
        break
    if matrix is None:
        # R7/R8: the quantifier is registered and the remainder parsed; when the
        # remainder has no rule of its own the whole sentence becomes the atom
        # under that prefix (R9_ATOMIC_UNDER_PREFIX). The verb cut must leave a
        # non-empty remainder: `no fixed panel ... does` (EA-3) cut at its
        # sentence-final verb once produced a spurious forall.
        m = R7_EVERY.match(s)
        if m:
            v, d = var_domain(m.group(1))
            prefix.append(["forall", v, d])
            sub, rule2 = parse_sentence(m.group(2) + m.group(3), goal, depth + 1)
            if sub is not None:
                prefix.extend(sub["prefix"])
                matrix = sub["matrix"]
                rule = "R7_EVERY+" + rule2
        if matrix is None:
            m = R7_NO.match(s)
            if m:
                v, d = var_domain(m.group(1))
                prefix.append(["forall", v, d])
                sub, rule2 = parse_sentence(m.group(2) + m.group(3), goal, depth + 1)
                if sub is not None:
                    prefix.extend(sub["prefix"])
                    body = sub["matrix"]
                    matrix = body[1] if body[0] == "not" else ["not", body]
                    rule = "R7_NO+" + rule2
        if matrix is None:
            m = R8_FOR_SOME.match(s)
            if m:
                v, d = var_domain(m.group(2))
                prefix.append(["exists", v, d])
                sub, rule2 = parse_sentence(m.group(1), goal, depth + 1)
                if sub is not None:
                    matrix = sub["matrix"]
                    rule = "R8_FOR_SOME+" + rule2
        if matrix is None:
            m = R8_THERE_EXIST_BARE.match(s)
            if m:
                v, d = var_domain(m.group(1))
                prefix.append(["exists", v, d])
                matrix = ["atom", m.group(1).strip(), "EXISTS"]
                rule = "R8_THERE_EXIST_BARE"
    if matrix is None:
        if prefix or has_rel_cue(s):
            matrix = clause(s)
            rule = "R9_ATOMIC" if not prefix else "R9_ATOMIC_UNDER_PREFIX"
        else:
            return None, "NO_GRAMMAR_RULE"
    for h in reversed(hyps):
        matrix = ["->", h, matrix]
        rule = "UNDER+" + rule
    return {"prefix": prefix, "matrix": matrix}, rule


LET_BE = re.compile(r"^Let\s+(.+?)\s+(?:be|denote|range over)\s+(.+)$", re.IGNORECASE)
LET_BARE = re.compile(r"^Let\s+(.+)$", re.IGNORECASE)
FIX = re.compile(r"^(?:Fix|Consider)\s+(.+)$", re.IGNORECASE)
SUPPOSE = re.compile(r"^(?:Suppose|Assume|Given)\s+(?:that\s+)?(.+)$", re.IGNORECASE)


def fold_hypotheses(hyps: List[str], form: Dict[str, object]) -> Dict[str, object]:
    prefix = []  # type: List[List[str]]
    conj = []  # type: List[List[object]]
    for h in hyps:
        h = h.strip().rstrip(".").strip()
        m = LET_BE.match(h)
        if m:
            v, d = m.group(1).strip(), m.group(2).strip()
            prefix.append(["forall", v, d])
            continue
        m = FIX.match(h)
        if m:
            v, d = var_domain(m.group(1))
            prefix.append(["forall", v, d])
            continue
        m = LET_BARE.match(h)
        if m:
            v, d = var_domain(m.group(1))
            prefix.append(["forall", v, d])
            continue
        m = SUPPOSE.match(h)
        if m:
            conj.append(clause(m.group(1)))
            continue
        conj.append(clause(h))
    matrix = form["matrix"]
    if conj:
        ant = conj[0]
        for c in conj[1:]:
            ant = ["and", ant, c]
        matrix = ["->", ant, matrix]
    return {"prefix": prefix + list(form["prefix"]), "matrix": matrix}


def roles_of(matrix: List[object]) -> Optional[Dict[str, List[int]]]:
    if matrix[0] == "->":
        return {"sufficient": [1], "necessary": [2]}
    if matrix[0] == "<->":
        return {"sufficient": [1, 2], "necessary": [1, 2]}
    return None


def scope_of(prefix: List[List[str]], hyps: List[str]) -> str:
    if prefix:
        q, v, d = prefix[0]
        return d if d != "-" else v
    if hyps:
        return normalize_text(hyps[0])[:120]
    return "UNSCOPED"


def atoms_of(node: List[object]) -> List[List[object]]:
    if node[0] == "atom":
        return [node]
    out = []
    for child in node[1:]:
        if isinstance(child, list):
            out.extend(atoms_of(child))
    return out


def render(node: List[object]) -> str:
    if node[0] == "atom":
        return "[%s|%s]" % (node[2], node[1])
    if node[0] == "not":
        return "not(%s)" % render(node[1])
    return "(%s %s %s)" % (render(node[1]), node[0], render(node[2]))


def register_form(rec: Dict[str, object]) -> Dict[str, object]:
    statement = str(rec["statement"])
    if not statement:
        return {"form_status": "FORM_UNAVAILABLE", "reason": "EMPTY_STATEMENT", "rule": None,
                "form": None, "trailing_dropped": False, "role_vocabulary": False}
    hyps, concl, trailing = hypothesis_chain(statement)
    role_vocab = bool(ROLE_VOCAB.search(" ".join(hyps + [concl or ""])))
    if concl is None:
        return {"form_status": "FORM_UNAVAILABLE", "reason": "NO_CONCLUSION_SENTENCE", "rule": None,
                "form": None, "trailing_dropped": trailing, "role_vocabulary": role_vocab}
    parsed, rule = parse_sentence(concl, str(rec.get("heading", "")))
    if parsed is None:
        return {"form_status": "FORM_UNAVAILABLE", "reason": "NO_GRAMMAR_RULE", "rule": None,
                "form": None, "trailing_dropped": trailing, "role_vocabulary": role_vocab,
                "conclusion_sentence": concl, "hypotheses": hyps}
    folded = fold_hypotheses(hyps, parsed)
    form = {"prefix": folded["prefix"], "conclusion_prefix": parsed["prefix"], "matrix": folded["matrix"],
            "roles": roles_of(folded["matrix"]), "scope": scope_of(folded["prefix"], hyps)}
    return {"form_status": "REGISTERED_MACHINE", "reason": None, "rule": rule, "form": form,
            "trailing_dropped": trailing, "role_vocabulary": role_vocab,
            "conclusion_sentence": concl, "hypotheses": hyps,
            "rendered": render(folded["matrix"])}


# ---------------------------------------------------------------------------
# warrant (FREEZE section 6)
# ---------------------------------------------------------------------------
STOP = set("""the a an and or of to in on for with by is are be as at that this these those its
their from into over under than then when where which who whom whose what any all each every
some such no not nor so if iff only also both either neither via per one two three it we our
has have had do does did can cannot may must shall will would should could let suppose assume
fix given there here they them his her he she you your yours ours mine but yet still just
""".split())
FORALL_FIRST = re.compile(
    r"\b(fix|for each|for every|for all|for any|given any|arbitrary|let [^.]{0,60}? be arbitrary|by induction)\b",
    re.IGNORECASE)
EXISTS_FIRST = re.compile(
    r"\b(take|choose|construct|exhibit|there is|there exists?|there are|consider the|pick|define|the witness|witnessed by|the counterexample)\b",
    re.IGNORECASE)
OPENING_LIT = re.compile(
    r"^(?:Suppose|Assume|Let|Given|If|Fix|Consider|Take)\s+(?:that\s+)?(.+?)(?:[.;:]|,\s*(?:then|so|and)\b|$)",
    re.IGNORECASE)
SECOND_DIRECTION = re.compile(
    r"\b(conversely|only if|other direction|for the converse|reverse direction|the converse|both directions|exactly when|if and only if|iff|necessity\b.*\bsufficiency|sufficiency\b.*\bnecessity)\b",
    re.IGNORECASE)
NEG_CUE = re.compile(r"\b(not|no|never|cannot|fails?|without|violat\w*|differ\w*|exceed\w*|false|absent|missing|breaks?)\b|[≠]", re.IGNORECASE)


def tokens(text: str) -> List[str]:
    out = []
    for t in re.findall(r"[a-z0-9_]+", text.lower().replace("<math>", " ")):
        if len(t) >= 3 and t not in STOP:
            out.append(t)
    return out


def side_text(node: List[object]) -> str:
    return " ".join(str(a[1]) for a in atoms_of(node))


def overlap(a: str, b: str) -> int:
    return len(set(tokens(a)) & set(tokens(b)))


def parse_warrant(rec: Dict[str, object]) -> Dict[str, object]:
    proof = str(rec.get("proof", ""))
    fals = str(rec.get("falsifier", ""))
    w = {"warrant_status": "WARRANT_UNAVAILABLE", "evidence_mode": rec["evidence_mode"],
         "quantifier_class_measurement_only": rec["quantifier_class"],
         "proof_first_quantifier": None, "proof_opening_literal": None,
         "proof_opening_polarity": None, "proof_second_direction": None,
         "falsifier_text": fals or None}  # type: Dict[str, object]
    if proof:
        w["warrant_status"] = "PROOF_BLOCK"
        first = split_sentences(proof)[0] if split_sentences(proof) else proof
        fa = FORALL_FIRST.search(proof)
        ex = EXISTS_FIRST.search(proof)
        if fa and (not ex or fa.start() <= ex.start()):
            w["proof_first_quantifier"] = "forall"
        elif ex:
            w["proof_first_quantifier"] = "exists"
        # FREEZE section 6: the literal is the OPENING ASSUMPTION only. A
        # first-sentence fallback was tried on the real corpus and produced
        # 6/6 false CONVERSE alarms (a direct proof's first sentence works with
        # the objects of the consequent), so it is not used.
        m = OPENING_LIT.match(first)
        lit = m.group(1).strip() if m else ""
        w["proof_opening_source"] = "HYPOTHESIS_OPENER" if m else None
        if lit and re.search(r"[A-Za-z]", lit):
            w["proof_opening_literal"] = lit
            w["proof_opening_polarity"] = "neg" if (NEG_LEAD.match(lit) or NEG_VERB.search(lit)) else "pos"
        w["proof_second_direction"] = bool(SECOND_DIRECTION.search(proof))
    elif fals:
        w["warrant_status"] = "FALSIFIER_BLOCK"
    return w


def align(literal: Optional[str], matrix: List[object]) -> Optional[str]:
    """'left' | 'right' | None (unaligned / not a conditional)."""
    if literal is None or matrix[0] not in ("->", "<->"):
        return None
    l = overlap(literal, side_text(matrix[1]))
    r = overlap(literal, side_text(matrix[2]))
    if l == r:
        return None
    return "left" if l > r else "right"


def falsifier_negated_side(fals: Optional[str], matrix: List[object]) -> Optional[str]:
    if not fals or matrix[0] not in ("->", "<->"):
        return None
    words = fals.split()
    neg_windows = []
    for i, wd in enumerate(words):
        if NEG_CUE.search(wd):
            neg_windows.append(" ".join(words[max(0, i - 3):i + 7]))
    if not neg_windows:
        return None
    window = " ".join(neg_windows)
    l = overlap(window, side_text(matrix[1]))
    r = overlap(window, side_text(matrix[2]))
    if l == r:
        return None
    return "left" if l > r else "right"


# ---------------------------------------------------------------------------
# hand register (FREEZE section 5.1)
# ---------------------------------------------------------------------------
def draw_hand_sample(unavailable_keys: List[str]) -> List[str]:
    rng = LCG(HAND_SEED)
    return rng.sample(sorted(unavailable_keys), HAND_SAMPLE_SIZE)


def load_hand() -> Dict[str, object]:
    if not HAND.exists():
        return {}
    with open(HAND, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# discriminators (FREEZE section 7)
# ---------------------------------------------------------------------------
def permutations(items: List) -> List[List]:
    if len(items) <= 1:
        return [list(items)]
    out = []
    for i, x in enumerate(items):
        for rest in permutations(items[:i] + items[i + 1:]):
            out.append([x] + rest)
    return out


def stated_outer(form: Dict[str, object]) -> Optional[str]:
    return form["prefix"][0][0] if form["prefix"] else None


def mixed_prefix(form: Dict[str, object]) -> bool:
    qs = set(q for q, _, _ in form["prefix"])
    return "forall" in qs and "exists" in qs


def conclusion_mixed(form: Dict[str, object]) -> bool:
    qs = set(q for q, _, _ in form.get("conclusion_prefix", form["prefix"]))
    return "forall" in qs and "exists" in qs


def warranted_outer(entry: Dict[str, object]) -> Optional[str]:
    """The established outermost quantifier. A hand warrant names it outright.
    The proof-first cue is discriminating only when the CONCLUSION sentence's
    own prefix is mixed: when the forall comes from a `Let` hypothesis the
    variable is already fixed before the proof starts, so a proof that opens
    by constructing the witness is consistent with forall-exists and the cue
    says nothing about order (KF-4 was a false positive of the naive rule)."""
    hw = entry.get("hand_warrant") or {}
    if hw.get("outer_quantifier"):
        return str(hw["outer_quantifier"])
    if not conclusion_mixed(entry["form"]):
        return None
    return entry["warrant"].get("proof_first_quantifier")


def negate(node: List[object]) -> List[object]:
    return node[1] if node[0] == "not" else ["not", node]


def resolve_hand_literal(entry: Dict[str, object]) -> None:
    """A hand warrant names the assumed SIDE at registration time; it is stored
    as the CONTENT of that side (its atom text and polarity), so that a later
    swap or negation of the statement moves the alignment. A side label that
    travelled with the swap could never detect one (H3/H6 were vacuous under
    a label-anchored warrant: 0/15 and 0/16 detected)."""
    hw = entry.get("hand_warrant")
    if not hw or not hw.get("assumes_side") or hw.get("assumes_literal"):
        return
    matrix = entry["form"]["matrix"]
    if matrix[0] not in ("->", "<->"):
        return
    node = matrix[1] if hw["assumes_side"] == "left" else matrix[2]
    hw["assumes_literal"] = side_text(node)
    hw["literal_polarity"] = "neg" if node[0] == "not" else "pos"


def warranted_side(entry: Dict[str, object]) -> Tuple[Optional[str], Optional[str], Optional[bool]]:
    """(aligned side, polarity RELATIVE to that side, two_directions).

    The literal comes from the hand warrant (content-anchored), else the proof
    opening assumption, else a falsifier. Alignment is by token overlap against
    the CURRENT matrix; the relative polarity is `pos` when the literal's own
    polarity equals the aligned side's polarity."""
    hw = entry.get("hand_warrant") or {}
    matrix = entry["form"]["matrix"]
    w = entry["warrant"]
    literal = None  # type: Optional[str]
    lit_pol = "pos"
    two = False
    if hw.get("assumes_literal"):
        literal = str(hw["assumes_literal"])
        lit_pol = str(hw.get("literal_polarity", "pos"))
        two = bool(hw.get("two_directions", False))
    elif w.get("proof_opening_literal"):
        literal = str(w["proof_opening_literal"])
        lit_pol = str(w.get("proof_opening_polarity") or "pos")
        two = bool(w.get("proof_second_direction"))
    if literal is not None:
        side = align(literal, matrix)
        if side is None:
            return None, None, None
        node = matrix[1] if side == "left" else matrix[2]
        side_pol = "neg" if node[0] == "not" else "pos"
        return side, ("pos" if side_pol == lit_pol else "neg"), two
    neg = falsifier_negated_side(w.get("falsifier_text"), matrix)
    if neg is not None:
        # a falsifier that negates the RIGHT side tests A -> B (assumes left)
        return ("left" if neg == "right" else "right"), "pos", False
    return None, None, None


def run_discriminators(register: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    queues = {r: [] for r in ROWS}  # type: Dict[str, List[Dict[str, object]]]
    applicable = {r: [] for r in ROWS}  # type: Dict[str, List[str]]
    evaluable = {r: [] for r in ROWS}  # type: Dict[str, List[str]]
    agree = {r: 0 for r in ROWS}
    swapped_forms = {}  # type: Dict[str, List[List[List[str]]]]
    for key in sorted(register):
        e = register[key]
        if e["form_status"] not in ("REGISTERED_MACHINE", "REGISTERED_HAND"):
            continue
        form = e["form"]
        matrix = form["matrix"]
        top = matrix[0]
        # AA16
        if mixed_prefix(form):
            applicable["AA16"].append(key)
            swapped_forms[key] = [p for p in permutations(form["prefix"]) if p != form["prefix"]]
            wo = warranted_outer(e)
            if wo is not None:
                evaluable["AA16"].append(key)
                so = form["conclusion_prefix"][0][0] if (conclusion_mixed(form) and not (e.get("hand_warrant") or {}).get("outer_quantifier")) else stated_outer(form)
                if wo != so:
                    queues["AA16"].append({"key": key, "stated_prefix": form["prefix"],
                                           "warranted_outer": wo, "kind": "PREFIX_ORDER"})
                else:
                    agree["AA16"] += 1
        # AA17 / AA18 partition
        if top in ("->", "<->"):
            row = "AA18" if (e["role_vocabulary"] or top == "<->") else "AA17"
            applicable[row].append(key)
            side, pol, two = warranted_side(e)
            if side is not None:
                evaluable[row].append(key)
                if row == "AA17":
                    # left+pos = direct proof; right+neg = contrapositive; both establish A -> B
                    if side == "right" and pol == "pos":
                        queues[row].append({"key": key, "kind": "CONVERSE", "warrant_assumes": side})
                    elif side == "left" and pol == "neg":
                        queues[row].append({"key": key, "kind": "INVERSE", "warrant_assumes": side})
                    else:
                        agree[row] += 1
                else:
                    if top == "<->":
                        if not two:
                            queues[row].append({"key": key, "kind": "IFF_ONE_DIRECTION", "warrant_assumes": side})
                        else:
                            agree[row] += 1
                    else:
                        if (side == "right" and pol == "pos") or (side == "left" and pol == "neg"):
                            queues[row].append({"key": key, "kind": "ROLE_SWAP", "warrant_assumes": side})
                        else:
                            agree[row] += 1
        # AA20 / AA22
        rels = set(str(a[2]) for a in atoms_of(matrix))
        mode = str(e["warrant"]["evidence_mode"])
        if "OPT" in rels:
            applicable["AA20"].append(key)
            if mode != "UNKNOWN" and mode != "PROTOCOL_ONLY":
                evaluable["AA20"].append(key)
                if mode in RUN_MODES:
                    queues["AA20"].append({"key": key, "kind": "OPTIMALITY_FROM_RUN_SEARCH", "evidence_mode": mode})
                else:
                    agree["AA20"] += 1
        if "CAUSAL" in rels:
            applicable["AA22"].append(key)
            if mode != "UNKNOWN":
                evaluable["AA22"].append(key)
                texts = " ".join(str(a[1]) for a in atoms_of(matrix) if a[2] == "CAUSAL")
                if mode in RUN_MODES and not INTERVENTIONAL.search(texts):
                    queues["AA22"].append({"key": key, "kind": "CAUSAL_FROM_OBSERVATIONAL_RUN", "evidence_mode": mode})
                else:
                    agree["AA22"] += 1
    return {"queues": queues, "applicable": applicable, "evaluable": evaluable,
            "agree": agree, "swapped_forms": swapped_forms}


# ---------------------------------------------------------------------------
# hostiles (FREEZE section 8)
# ---------------------------------------------------------------------------
def deep(x):
    return json.loads(json.dumps(x))


def hostiles(register: Dict[str, Dict[str, object]], base: Dict[str, object]) -> List[Dict[str, object]]:
    out = []

    def run_on(reg: Dict[str, Dict[str, object]]) -> Dict[str, object]:
        return run_discriminators(reg)

    # H1 prefix swap on every AA16 evaluable object
    keys = base["evaluable"]["AA16"]
    planted = 0
    detected = 0
    for k in keys:
        e = deep(register[k])
        if k in [q["key"] for q in base["queues"]["AA16"]]:
            continue  # already queued in the real register: a swap would un-queue it
        for p in base["swapped_forms"][k]:
            if p[0][0] == e["form"]["prefix"][0][0]:
                continue  # inner permutation keeps the outermost quantifier: not a swap this predicate sees
            e2 = deep(e)
            e2["form"]["prefix"] = p
            planted += 1
            r = run_on({k: e2})
            if any(q["key"] == k for q in r["queues"]["AA16"]):
                detected += 1
    out.append({"id": "H1", "row": "AA16", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H2 warrant flip
    planted = detected = 0
    for k in keys:
        if k in [q["key"] for q in base["queues"]["AA16"]]:
            continue
        e2 = deep(register[k])
        wo = warranted_outer(e2)
        flip = "exists" if wo == "forall" else "forall"
        e2["hand_warrant"] = dict(e2.get("hand_warrant") or {})
        e2["hand_warrant"]["outer_quantifier"] = flip
        planted += 1
        if any(q["key"] == k for q in run_on({k: e2})["queues"]["AA16"]):
            detected += 1
    out.append({"id": "H2", "row": "AA16", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H3 converse / H4 inverse on AA17 evaluable & agreeing objects
    agreeing17 = [k for k in base["evaluable"]["AA17"] if k not in [q["key"] for q in base["queues"]["AA17"]]]
    planted = detected = 0
    for k in agreeing17:
        e2 = deep(register[k])
        m = e2["form"]["matrix"]
        e2["form"]["matrix"] = [m[0], m[2], m[1]]
        planted += 1
        if any(q["key"] == k and q["kind"] == "CONVERSE" for q in run_on({k: e2})["queues"]["AA17"]):
            detected += 1
    out.append({"id": "H3", "row": "AA17", "applicable": planted > 0, "planted": planted, "detected": detected})
    planted = detected = 0
    for k in agreeing17:
        e2 = deep(register[k])
        m = e2["form"]["matrix"]
        # the statement now claims the inverse; the warrant still assumes the original antecedent
        e2["form"]["matrix"] = [m[0], negate(m[1]), negate(m[2])]
        planted += 1
        if any(q["key"] == k and q["kind"] == "INVERSE" for q in run_on({k: e2})["queues"]["AA17"]):
            detected += 1
    out.append({"id": "H4", "row": "AA17", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H5 promotion -> to <-> with one-direction warrant (from agreeing AA17 + AA18 '->' objects)
    agreeing18 = [k for k in base["evaluable"]["AA18"] if k not in [q["key"] for q in base["queues"]["AA18"]]]
    planted = detected = 0
    for k in agreeing17 + [k for k in agreeing18 if register[k]["form"]["matrix"][0] == "->"]:
        e2 = deep(register[k])
        m = e2["form"]["matrix"]
        e2["form"]["matrix"] = ["<->", m[1], m[2]]
        e2["form"]["roles"] = roles_of(e2["form"]["matrix"])
        hw = dict(e2.get("hand_warrant") or {})
        if "two_directions" in hw:
            hw["two_directions"] = False
        e2["hand_warrant"] = hw
        e2["warrant"]["proof_second_direction"] = False
        planted += 1
        if any(q["key"] == k and q["kind"] == "IFF_ONE_DIRECTION" for q in run_on({k: e2})["queues"]["AA18"]):
            detected += 1
    out.append({"id": "H5", "row": "AA18", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H6 role swap on agreeing AA18 '->' objects and on agreeing AA17 objects relabelled with role vocabulary
    planted = detected = 0
    for k in [k for k in agreeing18 if register[k]["form"]["matrix"][0] == "->"] + agreeing17:
        e2 = deep(register[k])
        m = e2["form"]["matrix"]
        e2["form"]["matrix"] = ["->", m[2], m[1]]
        e2["role_vocabulary"] = True
        planted += 1
        if any(q["key"] == k and q["kind"] == "ROLE_SWAP" for q in run_on({k: e2})["queues"]["AA18"]):
            detected += 1
    out.append({"id": "H6", "row": "AA18", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H7 evidence flip on OPT atoms (clean -> run)
    planted = detected = 0
    for k in base["evaluable"]["AA20"]:
        if k in [q["key"] for q in base["queues"]["AA20"]]:
            continue
        e2 = deep(register[k])
        e2["warrant"]["evidence_mode"] = "EMPIRICAL_EXPERIMENT"
        planted += 1
        if any(q["key"] == k for q in run_on({k: e2})["queues"]["AA20"]):
            detected += 1
    out.append({"id": "H7", "row": "AA20", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H8 atom flip: a run-warranted registered object with no OPT atom gets one
    planted = detected = 0
    for k in sorted(register):
        e = register[k]
        if e["form_status"] not in ("REGISTERED_MACHINE", "REGISTERED_HAND"):
            continue
        if str(e["warrant"]["evidence_mode"]) not in RUN_MODES:
            continue
        if "OPT" in set(str(a[2]) for a in atoms_of(e["form"]["matrix"])):
            continue
        e2 = deep(e)
        a0 = atoms_of(e2["form"]["matrix"])[0]
        a0[2] = "OPT"
        planted += 1
        if any(q["key"] == k for q in run_on({k: e2})["queues"]["AA20"]):
            detected += 1
    out.append({"id": "H8", "row": "AA20", "applicable": planted > 0, "planted": planted, "detected": detected})
    # H9 evidence flip on CAUSAL atoms without interventional marker; if every real CAUSAL atom carries
    # a marker, the marker is removed as well and that is disclosed
    planted = detected = 0
    marker_removed = 0
    for k in base["evaluable"]["AA22"]:
        if k in [q["key"] for q in base["queues"]["AA22"]]:
            continue
        e2 = deep(register[k])
        e2["warrant"]["evidence_mode"] = "STATISTICAL_EXPERIMENT"
        for a in atoms_of(e2["form"]["matrix"]):
            if a[2] == "CAUSAL" and INTERVENTIONAL.search(str(a[1])):
                a[1] = INTERVENTIONAL.sub("observed(", str(a[1]))
                marker_removed += 1
        planted += 1
        if any(q["key"] == k for q in run_on({k: e2})["queues"]["AA22"]):
            detected += 1
    out.append({"id": "H9", "row": "AA22", "applicable": planted > 0, "planted": planted, "detected": detected,
                "interventional_markers_removed": marker_removed})
    # H10 grammar hostile
    checks = []
    f, _ = parse_sentence("If the cut is finite, then the code is exact.", "")
    checks.append(f is not None and f["matrix"][0] == "->" and "cut" in f["matrix"][1][1] and "code" in f["matrix"][2][1])
    g, _ = parse_sentence("The code is exact if the cut is finite.", "")
    checks.append(g is not None and g["matrix"][0] == "->" and "cut" in g["matrix"][1][1] and "code" in g["matrix"][2][1])
    h, _ = parse_sentence("The code is exact iff the cut is finite.", "")
    checks.append(h is not None and h["matrix"][0] == "<->")
    n, _ = parse_sentence("A finite cut is necessary for an exact code.", "")
    checks.append(n is not None and n["matrix"][0] == "->" and "code" in n["matrix"][1][1] and "cut" in n["matrix"][2][1])
    q, _ = parse_sentence("For every machine M, there exists a witness w such that w certifies M.", "")
    checks.append(q is not None and [p[0] for p in q["prefix"]] == ["forall", "exists"])
    out.append({"id": "H10", "row": "GRAMMAR", "applicable": True, "planted": len(checks), "detected": sum(1 for c in checks if c)})
    # H11 loosening: drop the warrant conjunct -- every applicable object is queued
    loosened = {r: len(base["applicable"][r]) for r in ROWS}
    out.append({"id": "H11", "row": "ALL", "applicable": True, "measured_only": True,
                "queue_if_warrant_conjunct_dropped": loosened,
                "true_queue": {r: len(base["queues"][r]) for r in ROWS}})
    # H12 no-cue statement must be FORM_UNAVAILABLE
    f12, rule12 = parse_sentence("This is the positive result.", "")
    out.append({"id": "H12", "row": "GRAMMAR", "applicable": True, "planted": 1,
                "detected": 1 if f12 is None and rule12 == "NO_GRAMMAR_RULE" else 0})
    return out


# ---------------------------------------------------------------------------
# null (FREEZE section 9, amendment 01: permutation over the whole registered set)
# ---------------------------------------------------------------------------
def null_test(register: Dict[str, Dict[str, object]], true_agree: Dict[str, int]) -> Dict[str, object]:
    keys = [k for k in sorted(register) if register[k]["form_status"] in ("REGISTERED_MACHINE", "REGISTERED_HAND")]
    rng = LCG(NULL_SEED)
    true_total = sum(true_agree.values())
    reach = 0
    maximum = 0
    per_row_reach = {r: 0 for r in ROWS}
    total_sum = 0
    for _ in range(NULL_DRAWS):
        perm = rng.shuffle(keys)
        shuffled = {}
        for k, src in zip(keys, perm):
            e = deep(register[k])
            e["warrant"] = deep(register[src]["warrant"])
            e["hand_warrant"] = deep(register[src].get("hand_warrant"))
            shuffled[k] = e
        r = run_discriminators(shuffled)
        tot = sum(r["agree"].values())
        total_sum += tot
        maximum = max(maximum, tot)
        if tot >= true_total:
            reach += 1
        for row in ROWS:
            if r["agree"][row] >= true_agree[row]:
                per_row_reach[row] += 1
    return {"draws": NULL_DRAWS, "seed": NULL_SEED, "statistic": "pooled agreeing (stated, warranted) pairs",
            "true_pooled": true_total, "true_per_row": true_agree, "shuffled_max": maximum,
            "shuffled_reach_true": reach, "shuffled_mean": str(Fraction(total_sum, NULL_DRAWS)),
            "per_row_shuffled_reach_true": per_row_reach,
            "beaten": reach == 0}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def dump(path: Path, doc: object) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def build(write: bool = True) -> Dict[str, object]:
    census = load_census()
    if census.get("frozen_source_sha") != CENSUS_FROZEN_SHA:
        raise SystemExit("census frozen_source_sha drifted")
    members, mentions = population(census)
    snap, blob_state = build_snapshot(members)
    if blob_state == "BLOBS_REACHABLE" and SNAPSHOT.exists():
        with open(SNAPSHOT, "r", encoding="utf-8") as fh:
            committed = json.load(fh)
        snapshot_byte_identical = committed.get("records") == snap["records"]
    else:
        snapshot_byte_identical = None
    records = snap["records"]
    # forms
    register = {}  # type: Dict[str, Dict[str, object]]
    for key in sorted(records):
        rec = records[key]
        entry = {"object_id": rec["object_id"], "source_path": rec["source_path"],
                 "source_locator": rec["source_locator"], "source_blob": rec["source_blob"],
                 "vendored": rec["vendored"], "object_class": rec["object_class"]}
        if "error" in rec:
            entry.update({"form_status": "FORM_UNAVAILABLE", "reason": rec["error"], "rule": None,
                          "form": None, "trailing_dropped": False, "role_vocabulary": False})
        else:
            entry.update(register_form(rec))
        entry["warrant"] = parse_warrant(rec) if "error" not in rec else {
            "warrant_status": "WARRANT_UNAVAILABLE", "evidence_mode": rec.get("evidence_mode", "UNKNOWN"),
            "quantifier_class_measurement_only": rec.get("quantifier_class", "UNKNOWN"),
            "proof_first_quantifier": None, "proof_opening_literal": None,
            "proof_opening_polarity": None, "proof_second_direction": None, "falsifier_text": None}
        entry["hand_warrant"] = None
        register[key] = entry
    unavailable = [k for k in sorted(register) if register[k]["form_status"] == "FORM_UNAVAILABLE"]
    sample = draw_hand_sample(unavailable)
    hand = load_hand()
    hand_entries = hand.get("entries", {}) if hand else {}
    hand_keys_match = set(hand_entries) == set(sample) if hand else False
    hand_registered = 0
    hand_kept_unavailable = 0
    hand_clean_set = []  # type: List[str]
    hand_queue_expected = []  # type: List[str]  # amendment 01 (f): real-data positives found by the reader

    def place(k: str, h: Dict[str, object]) -> None:
        if h.get("hand_verdict") == "QUEUE_EXPECTED":
            if k not in hand_queue_expected:
                hand_queue_expected.append(k)
        elif k not in hand_clean_set:
            hand_clean_set.append(k)

    for k in sample:
        h = hand_entries.get(k)
        if not h:
            continue
        if h.get("form"):
            e = register[k]
            e["form_status"] = "REGISTERED_HAND"
            e["reason"] = None
            e["rule"] = "HAND"
            e["form"] = h["form"]
            e["form"]["roles"] = roles_of(h["form"]["matrix"])
            if "scope" not in e["form"]:
                e["form"]["scope"] = "UNSCOPED"
            if "conclusion_prefix" not in e["form"]:
                e["form"]["conclusion_prefix"] = e["form"]["prefix"]
            e["rendered"] = render(h["form"]["matrix"])
            e["role_vocabulary"] = bool(h.get("role_vocabulary", False))
            e["hand_warrant"] = h.get("warrant")
            hand_registered += 1
            place(k, h)
        else:
            register[k]["reason"] = "HAND_FORM_UNAVAILABLE: " + str(h.get("reason", ""))
            hand_kept_unavailable += 1
    # amendment 01 (e): second, warrant-only hand sample drawn from the MACHINE
    # register state -- applicable to AA16/AA17/AA18, not machine-evaluable,
    # carrying a proof or falsifier block -- plus every AA16-applicable object.
    machine_disc = run_discriminators({k: v for k, v in register.items() if v["form_status"] == "REGISTERED_MACHINE"})
    pool = set()
    for r in ("AA16", "AA17", "AA18"):
        pool |= set(machine_disc["applicable"][r]) - set(machine_disc["evaluable"][r])
    pool2 = [k for k in sorted(pool)
             if register[k]["warrant"]["warrant_status"] != "WARRANT_UNAVAILABLE" or register[k]["warrant"].get("falsifier_text")]
    sample2 = LCG(HAND2_SEED).sample(pool2, HAND2_SAMPLE_SIZE)
    warrant_keys = sorted(set(sample2) | set(machine_disc["applicable"]["AA16"]))
    hand_warrants = hand.get("warrants", {}) if hand else {}
    warrant_keys_match = set(hand_warrants) == set(warrant_keys) if hand else False
    hand_warranted = 0
    for k in warrant_keys:
        hwe = hand_warrants.get(k)
        if hwe and hwe.get("warrant"):
            register[k]["hand_warrant"] = hwe["warrant"]
            hand_warranted += 1
            place(k, hwe)
        elif hwe:
            register[k]["hand_warrant_refusal"] = str(hwe.get("reason", ""))
    for k in register:
        if register[k]["form_status"] in ("REGISTERED_MACHINE", "REGISTERED_HAND"):
            resolve_hand_literal(register[k])
    disc = run_discriminators(register)
    hs = hostiles(register, disc)
    null = null_test(register, disc["agree"])
    # no-alarm on the hand-verified clean set; recall on the reader's real-data positives
    clean_alarms = {r: [q["key"] for q in disc["queues"][r] if q["key"] in hand_clean_set] for r in ROWS}
    queued_keys = set()
    for r in ROWS:
        queued_keys |= set(q["key"] for q in disc["queues"][r])
    real_positives = {"expected": hand_queue_expected,
                      "queued": [k for k in hand_queue_expected if k in queued_keys],
                      "missed": [k for k in hand_queue_expected if k not in queued_keys]}
    # coverage
    by_status = {}
    by_reason = {}
    by_rule = {}
    for e in register.values():
        by_status[e["form_status"]] = by_status.get(e["form_status"], 0) + 1
        if e["form_status"] == "FORM_UNAVAILABLE":
            rs = str(e["reason"]).split(":")[0]
            by_reason[rs] = by_reason.get(rs, 0) + 1
        elif e["rule"]:
            by_rule[str(e["rule"])] = by_rule.get(str(e["rule"]), 0) + 1
    registered = by_status.get("REGISTERED_MACHINE", 0) + by_status.get("REGISTERED_HAND", 0)
    warrant_status = {}
    for e in register.values():
        ws = str(e["warrant"]["warrant_status"])
        warrant_status[ws] = warrant_status.get(ws, 0) + 1
    partition_ok = not (set(disc["applicable"]["AA17"]) & set(disc["applicable"]["AA18"]))
    result = {
        "schema": "GMI_833_LOGICAL_FORM_REGISTER_RESULT_V1",
        "package": PKG,
        "route": "A",
        "census_blob": CENSUS_BLOB,
        "census_frozen_sha": CENSUS_FROZEN_SHA,
        "blob_state": blob_state,
        "snapshot_byte_identical_to_committed": snapshot_byte_identical,
        "population": {"total": len(members), "heading_objects": sum(1 for m in members if m["kind"] == "H2"),
                       "bold_led": sum(1 for m in members if m["kind"] == "BOLD"),
                       "not_a_statement_line": mentions,
                       "pinned_blobs": len(set(str(m["source_blob"]) for m in members)),
                       "vendored": sum(1 for m in members if "/raw/" in str(m["source_path"]))},
        "coverage": {"registered": registered, "of": len(members),
                     "fraction": str(Fraction(registered, len(members))),
                     "by_status": by_status, "unavailable_by_reason": by_reason, "by_rule": by_rule,
                     "trailing_dropped": sum(1 for e in register.values() if e.get("trailing_dropped"))},
        "hand_sample": {"size": len(sample), "seed": HAND_SEED, "keys_match_hand_file": hand_keys_match,
                        "hand_file_present": bool(hand), "registered": hand_registered,
                        "kept_unavailable": hand_kept_unavailable, "keys": sample},
        "hand_warrant_sample": {"pool": len(pool2), "size": len(sample2), "seed": HAND2_SEED,
                                "plus_aa16_applicable": len(machine_disc["applicable"]["AA16"]),
                                "keys": warrant_keys, "keys_match_hand_file": warrant_keys_match,
                                "warranted": hand_warranted,
                                "refused": len([k for k in warrant_keys if register[k].get("hand_warrant_refusal")])},
        "warrant": warrant_status,
        "aa17_aa18_partition_disjoint": partition_ok,
        "rows": {r: {"applicable": len(disc["applicable"][r]), "evaluable": len(disc["evaluable"][r]),
                     "queued": len(disc["queues"][r]), "agreeing": disc["agree"][r],
                     "queue": disc["queues"][r], "evaluable_keys": disc["evaluable"][r],
                     "clean_set_alarms": clean_alarms[r]} for r in ROWS},
        "aa16_swapped_forms_generated": sum(len(v) for v in disc["swapped_forms"].values()),
        "hostiles": hs,
        "null": null,
        "no_alarm_clean_set": {"size": len(hand_clean_set), "alarms": sum(len(v) for v in clean_alarms.values()),
                               "keys": hand_clean_set},
        "real_data_positives": real_positives,
    }
    if write:
        if blob_state == "BLOBS_REACHABLE":
            dump(SNAPSHOT, snap)
        reg_doc = {"schema": "GMI_833_LOGICAL_FORM_REGISTER_V1", "package": PKG, "grammar": "FORM_GRAMMAR_V1",
                   "census_blob": CENSUS_BLOB, "population": len(members), "entries": register}
        dump(REGISTER, reg_doc)
        dump(QUEUES, {"schema": "GMI_833_AA_REVIEW_QUEUES_V1", "package": PKG,
                      "rows": {r: disc["queues"][r] for r in ROWS},
                      "evaluable": {r: disc["evaluable"][r] for r in ROWS},
                      "applicable": {r: disc["applicable"][r] for r in ROWS}})
    return result


if __name__ == "__main__":
    doc = build(write="--no-write" not in sys.argv)
    json.dump(doc, sys.stdout, indent=1, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
