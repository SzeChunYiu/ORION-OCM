#!/usr/bin/env python3
"""GMI #833/#842 — dependency graph v2 miner (real claim_dependencies with citations).

Deterministic layers, no guessed edges (stdlib only, sorted iteration):

  A1. FILE_LOCAL claim->claim edges: relation-token lines in .md files that
      declare census claim-class objects.  Child = nearest claim-class
      declaration at-or-above the line (row lines attribute to themselves);
      child id_kind is recorded (EXPLICIT or PROVISIONAL/AUTO — both are
      census nodes).  Parent references must be EXPLICIT census object ids
      within +-WINDOW chars of the relation match (Parent-header lines: whole
      line).  Bare #NNN issue refs on Parent headers are programme parents:
      counted, not edged.
  A2. POINTER_ROLLUP edges: an EXPLICIT claim object whose own statement
      references another research document (its pointer row, e.g.
      `| THEOREM_FILE.md | Formal theorem ...`) inherits that document's A1
      edges (typed POINTER_ROLLUP, citation = original line + pointer object).
  B.  EXTERNAL_LITERATURE strongest-parent edges: verbatim bullets from
      gmi-833-*/PARENT_LEDGER.md and *STRONGEST*PARENT*.json maps.
  C.  CORPUS_PACKAGE edges (post-census 833 family): cross-package references
      in gmi-833-*/FREEZE_V1.md (self-references excluded), flagged post_census
      because current main carries 833-family packages beyond the census SHA.

Known limitations (reported, never silently dropped): dependencies referenced
by NAME only (no census id on the line) are counted as named_only_mentions;
code/JSON files are not scanned (prose statements only).

Claim ceiling: GMI_833_DEPENDENCY_GRAPH_V2_AT_MINED_SCOPE.  Absence of an edge
is NOT independence.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
RESEARCH = REPO_ROOT / "research"
CENSUS_DIR = RESEARCH / "gmi-833-corpus-census-v1"

SCHEMA = "GMI_833_DEPENDENCY_GRAPH_V2"
CLAIM_CEILING = "GMI_833_DEPENDENCY_GRAPH_V2_AT_MINED_SCOPE"
CLAIM_CLASSES = frozenset({
    "THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM",
})
WINDOW = 90  # chars each side of a relation match that a parent id must sit in

RELATION_PATTERNS = [
    ("DERIVES_FROM", re.compile(r"\bderiv(?:es|ed|ing)?\s+from\b", re.I)),
    ("FOLLOWS_FROM", re.compile(r"\bfollows\s+from\b", re.I)),
    ("COROLLARY_OF", re.compile(r"\bcorollar(?:y|ies)\s+(?:of|to)\b", re.I)),
    ("SPECIALIZES", re.compile(r"\bspecializ(?:es|ing|ed)\b", re.I)),
    ("GENERALIZES", re.compile(r"\bgeneraliz(?:es|ing|ed)\b(?!\s*=)", re.I)),
    ("INSTANTIATES", re.compile(r"\binstantiat(?:es|ing|ed)\b", re.I)),
    ("EXTENDS", re.compile(r"\bextends\b", re.I)),
    ("REFINES", re.compile(r"\brefin(?:es|ing|ed)\b", re.I)),
    ("RESTS_ON", re.compile(r"\b(?:rests?|builds?)\s+on\b", re.I)),
    ("REDUCES_TO", re.compile(r"\breduces?\s+to\b", re.I)),
    ("USES", re.compile(r"\buses\b|\bruled\s+out\s+by\b", re.I)),
    ("INHERITS", re.compile(r"\binherits\b|\binherited\s+from\b", re.I)),
]
PARENT_HEADER = re.compile(
    r"^\s*[-*\s>*\|]*\*{0,2}(?:strongest\s+)?parents?\*{0,2}\s*[:=]", re.I)

# Review-driven guards (each class was observed on real data, then removed):
NEGATION_BEFORE = re.compile(
    r"\b(?:no|not|never|cannot|can't|n't|nor|without)\b[^.|;]{0,40}$", re.I)
HYPHEN_BEFORE = re.compile(r"[A-Za-z]-$")          # e.g. "coordinate-specialized"
RANGE_TOKEN = re.compile(r"\b([A-Z][A-Z0-9]*-[A-Za-z0-9]*[A-Za-z])-(\d+)\u2013(\d+)\b")
STATUS_VALUE_IDS = frozenset({
    # census ids that are status/verdict STRINGS, never claim parents
    "PARTIAL_TEXT_READ", "FULL_TEXT_READ", "ABSTRACT_ONLY", "NOT_ACCESSIBLE",
    "PROVED_AT_SCOPE", "EXECUTED_EXACT_AT_SCOPE", "REGISTERED_FOR_EXPERIMENT",
    "REDUCED_TO_PARENT", "PARENT_INSTANTIATED_PROSPECTIVELY_AT_SCOPE",
    "UNDECIDED_FROM_CURRENT_EVIDENCE", "PARENT_OWNED_SPECIALIZATION",
    "THEORY_RED", "UNIVERSAL_COMPUTATION_ONLY", "ORION-OCM",
    "MULTIPLE_EQUIVALENT_MINIMAL_BASES",
})
URL_RE = re.compile(r"https?://\S+")

def clean_line(line: str) -> str:
    """URLs are replaced (path mentions must not resolve to ids)."""
    return URL_RE.sub(" ", line)

def masked_spans(line: str):
    """Character spans inside backticks/quotes: verbs there are not relations."""
    spans, depth_b, depth_q, start = [], 0, 0, 0
    for i, ch in enumerate(line):
        if ch == "`":
            if depth_b == 0:
                start = i
            depth_b += 1
        elif depth_b and ch == "`":
            depth_b -= 1
            if depth_b == 0:
                spans.append((start, i + 1))
        elif ch in ('"', "\u201c", "\u201d"):
            if depth_q == 0:
                start = i
            depth_q += 1
        elif depth_q and ch in ('"', "\u201c", "\u201d"):
            depth_q -= 1
            if depth_q == 0:
                spans.append((start, i + 1))
    if depth_b or depth_q:
        spans.append((start, len(line)))
    return spans

def expand_ranges(line: str, id_index):
    """`ARC-1\u20134` / `SMR-1\u20134` enumerations resolve to each existing id."""
    extra = []
    for m in RANGE_TOKEN.finditer(line):
        prefix, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        if b - a > 24 or b <= a:
            continue
        for n in range(a, b + 1):
            oid = f"{prefix}-{n}"
            if oid in id_index and oid != m.group(0):
                extra.append((oid, m.start()))
    return extra


class MinerError(RuntimeError):
    pass


def load_census():
    idx = json.loads((CENSUS_DIR / "CORPUS_INDEX_V1.json").read_text(encoding="utf-8"))
    return idx["scientific_objects"]


def build_id_index(objects):
    index = defaultdict(list)
    for o in objects:
        if o["id_kind"] == "EXPLICIT":
            index[o["object_id"]].append(o)
    return index


def ids_in_span(line, id_index, exclude, lo, hi):
    """EXPLICIT ids fully inside line[lo:hi] (word-boundary, longest-first)."""
    found = {}
    taken = []
    for oid in sorted(id_index, key=lambda s: (-len(s), s)):
        if oid in exclude or oid in STATUS_VALUE_IDS:
            continue
        for m in re.finditer(r"(?<![A-Za-z0-9_-])" + re.escape(oid) + r"(?![A-Za-z0-9_-])", line):
            if not (lo <= m.start() and m.end() <= hi):
                continue
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            found.setdefault(oid, m.start())
    return found


def claim_ids_in_window(line, id_index, exclude, lo, hi):
    """EXPLICIT claim-class ids fully inside line[lo:hi], plus range expansion."""
    found = {}
    taken = []
    for oid in sorted(id_index, key=lambda t: (-len(t), t)):
        if oid in exclude or oid in STATUS_VALUE_IDS:
            continue
        if id_index[oid] and all(o["object_class"] not in CLAIM_CLASSES for o in id_index[oid]):
            pass  # non-claim explicit ids remain eligible as parents (ledgers)
        for m in re.finditer(r"(?<![A-Za-z0-9_-])" + re.escape(oid) + r"(?![A-Za-z0-9_-])", line):
            if not (lo <= m.start() and m.end() <= hi):
                continue
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            found.setdefault(oid, m.start())
    return found


def mine_file(path, lines, decls, id_index):
    """Return (edges, prog_mentions, named_only) for one prose document."""
    edges, prog, named = [], [], 0
    decl_ids = {d["object_id"]: d for d in decls}
    for ln, raw in enumerate(lines, start=1):
        line = clean_line(raw)
        header = bool(PARENT_HEADER.match(raw))
        masked = masked_spans(line)

        def guarded(m):
            pre = line[: m.start()]
            if NEGATION_BEFORE.search(pre):
                return False
            if HYPHEN_BEFORE.search(pre[-2:]):
                return False
            if any(a <= m.start() < b for a, b in masked):
                return False
            return True

        matches = [(rt, m) for rt, pat in RELATION_PATTERNS
                   for m in pat.finditer(line) if guarded(m)]
        if not header and not matches:
            continue
        child = next((d for d in decls
                      if d["source_locator"] == f"L{ln}"), None)
        if child is None:
            above = [d for d in decls if int(d["source_locator"][1:]) <= ln]
            child = above[-1] if above else None
        if child is None:
            continue
        # subject-before-verb: a claim id of THIS file immediately before the
        # relation is the child, not the nearest-above declaration
        for rt, m in matches:
            pre = line[max(0, m.start() - 34): m.start()]
            for oid in sorted(decl_ids, key=lambda t: -len(t)):
                if oid in STATUS_VALUE_IDS:
                    continue
                mm = re.search(r"(?<![A-Za-z0-9_-])" + re.escape(oid) + r"(?![A-Za-z0-9_-])" + r"[ ,;]?$", pre)
                if mm:
                    child = decl_ids[oid]
                    break
        spans = [(0, len(line))] if header else [
            (max(0, m.start() - WINDOW), min(len(line), m.end() + WINDOW))
            for _, m in matches]
        ids = {}
        for lo, hi in spans:
            for oid in claim_ids_in_window(line, id_index, {child["object_id"]}, lo, hi):
                ids.setdefault(oid, True)
        for oid, pos in expand_ranges(line, id_index):
            if oid != child["object_id"] and any(lo <= pos < hi for lo, hi in spans):
                ids.setdefault(oid, True)
        if not ids:
            if header and re.search(r"#\d+", line):
                prog.append({"file": f"{path}:L{ln}", "text": raw.strip()[:160]})
            elif re.search(r"\btheorem\b|\blemma\b|\bproposition\b|\bcorollary\b", line, re.I):
                named += 1
            continue
        relations = sorted({rt for rt, _ in matches})
        relation = ("STRONGEST_PARENT_DECLARED" if header and not relations
                    else "+".join(relations))
        for oid in sorted(ids):
            edges.append({
                "child": child["object_id"],
                "child_id_kind": child["id_kind"],
                "child_class": child["object_class"],
                "parent": oid,
                "parent_kind": "CORPUS_CLAIM",
                "relation": relation,
                "citation": f"{path}:L{ln}",
                "evidence": raw.strip()[:220],
                "parent_declarations": len(id_index[oid]),
                "parent_ambiguous_id": len(id_index[oid]) > 1,
            })
    return edges, prog, named


P_FAMILY_TAG = re.compile(r"\((P[0-9AB]+(?:_?P?[0-9AB]+)*)\)")


def mine_family_anchors(objects):
    """Parent-family anchor tags on EXPLICIT claim objects, e.g.
    `- **GMI-T5** (P7P8P6P5): ...` - family-level parents (granularity is the
    family, not the individual ledger parent; stated verbatim on the claim row)."""
    edges = []
    for o in sorted(objects, key=lambda o: (o["source_path"], o["source_locator"], o["object_id"])):
        if o["id_kind"] != "EXPLICIT" or o["object_class"] not in CLAIM_CLASSES:
            continue
        m = P_FAMILY_TAG.search(o.get("statement", ""))
        if not m:
            continue
        fams = sorted(set(re.findall(r"P[0-9]+[A-B]?", m.group(1))))
        for fam in fams:
            edges.append({
                "child": o["object_id"],
                "child_id_kind": "EXPLICIT",
                "child_class": o["object_class"],
                "parent": fam,
                "parent_kind": "CORPUS_PARENT_FAMILY",
                "relation": "PARENT_FAMILY_ANCHOR",
                "citation": f"{o['source_path']}:{o['source_locator']}",
                "evidence": o["statement"].strip()[:220],
            })
    return edges


def mine_layer_a(objects, id_index):
    claims_by_file = defaultdict(list)
    for o in objects:
        if o["object_class"] in CLAIM_CLASSES:
            claims_by_file[o["source_path"]].append(o)
    all_edges, all_prog, named_total = [], [], 0
    file_edges = {}
    scanned = 0
    for path in sorted(claims_by_file):
        if not path.endswith((".md", ".txt")):
            continue
        if path.split("/")[-1] in PROGRAMME_LEVEL_FILES:
            continue  # programme-level ledgers are layer B
        fpath = REPO_ROOT / path
        if not fpath.exists():
            continue
        scanned += 1
        lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        decls = sorted(claims_by_file[path], key=lambda o: int(o["source_locator"][1:]))
        edges, prog, named = mine_file(path, lines, decls, id_index)
        edges += mine_parent_tables(path, lines, decls, id_index)
        file_edges[path] = edges
        all_edges.extend(edges)
        all_prog.extend(prog)
        named_total += named
    # deterministic de-dup across layers/rows
    seen, uniq = set(), []
    for e in all_edges:
        key = (e["child"], e["parent"], e["relation"], e["citation"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    kept, excluded, retyped = apply_review_overrides(uniq)
    excluded_keys = {(e["citation"], e["child"], e["parent"]) for e in excluded}
    clean_file_edges = {
        path: [e for e in edges
               if (e["citation"], e["child"], e["parent"]) not in excluded_keys]
        for path, edges in file_edges.items()}
    return kept, clean_file_edges, all_prog, named_total, scanned, excluded, retyped


FILE_REF = re.compile(r"`?([A-Za-z0-9_./-]+\.(?:md|json))`?")

# A3: claim-level parent tables.  Programme-level ledger filenames are excluded
# (their parents attach to the package, handled in layer B).
PARENT_TABLE_HEADER = re.compile(
    r"^\|\s*(?:\*\*)?\s*(?:strongest[\s-]+parents?|parents?|parent\s+theory|tranche\s+theorem)"
    r"\s*(?:\*\*)?\s*\|", re.I)
PROGRAMME_LEVEL_FILES = {"LITERATURE_LEDGER.md", "PARENTS.md", "PARENT_LEDGER.md"}


# ---------------------------------------------------------------------------
# Manual review layer (v2 review pass, 2026-09-16).  Every edge the miner
# produced was read against its source line; these are the individually
# logged judgment calls.  key = (citation, child, parent); action =
# ("exclude", reason) | ("retype", NEW_RELATION, reason).  No edge outside
# this table was altered.
# ---------------------------------------------------------------------------
REVIEW_OVERRIDES = {
    ("research/gmi-architecture-emergence-v1/raw/pr575576-ef5be973/ARCHITECTURE_EMERGENCE_THEOREM_V1.md:L60", "PL-5", "L_NEURAL"): ("exclude", "adjective: 'keeps refined bounds L_NEURAL=18'; no refinement relation stated"),
    ("research/gmi-grand-unification-v1/MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md:L126", "AUTO-1D87393FBF491DBDD757", "L_NEURAL"): ("exclude", "adjective: 'Keep refined bounds L_NEURAL=18'"),
    ("research/gmi-f1-replay-resistant-adapter-v1/FORMALIZATION_V1.md:L7", "RR-1", "ARC-6"): ("exclude", "subject of 'inherits' is RR-2 later on the line; RR-1 nearest-above attribution wrong"),
    ("research/gmi-f1-replay-resistant-adapter-v1/FORMALIZATION_V1.md:L7", "RR-1", "RR-2"): ("exclude", "RR-2 is the sentence subject, not a parent of RR-1"),
    ("research/gmi-scientific-completion-v1/CORE.md:L37", "RV-377-125", "RV-377-142"): ("exclude", "supersession graft note, not a USES dependency; alias/supersession recorded for the DUPLICATE adjudication"),
    ("research/machine-intelligence-morphogenesis-v1/COLLISION_MATRIX_V1.md:L113", "P9B.NOVELTY_SEARCH", "P9B.ABBE_DIFFERENTIABLE_VS_PAC"): ("exclude", "row concerns P9B.SQ_MODEL killing a claim; no reduces-to relation between the two parents"),
    ("research/machine-intelligence-morphogenesis-v1/COLLISION_MATRIX_V1.md:L158", "GMI-T5", "III.2"): ("retype", "USES", "Fong Theorem III.2 cited (with its Section-6 correction) by GMI-T5; 'Extends to Boolean circuits' is a different extension"),
    ("research/machine-intelligence-morphogenesis-v1/COLLISION_MATRIX_V1.md:L222", "GMI-T9", "GMI-T1"): ("exclude", "registry numbering note: THEOREM_REGISTRY_V2 numbers this content as GMI-T1 - alias, feeds DUPLICATE adjudication"),
    ("research/machine-intelligence-morphogenesis-v1/COLLISION_MATRIX_V1.md:L222", "GMI-T9", "THEOREM_REGISTRY_V2"): ("exclude", "subject of 'uses' is the registry note, not GMI-T9"),
    ("research/gmi-capital-acquisition-repair-v1/raw/source/research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md:L41", "AUTO-6164E13CC7B034E15385", "INTERACTIVE_CUT_SCOPE_CORRECTION_V1"): ("exclude", "'strategic exact enumeration inherits...' - subject is enumeration; matched id is the artifact column"),
    ("research/gmi-experimental-validation-v1/raw/pr581-f9a73a77/research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md:L41", "AUTO-9C1970532F31ADD96AA7", "INTERACTIVE_CUT_SCOPE_CORRECTION_V1"): ("exclude", "same enumeration-subject line, raw/ copy"),
    ("research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md:L41", "AUTO-B70D2049DCD2F47AA215", "INTERACTIVE_CUT_SCOPE_CORRECTION_V1"): ("exclude", "same enumeration-subject line"),
    ("research/gmi-ledger-selection-transport-repair-v1/raw/pr590/research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md:L41", "AUTO-6221FB11BCF255922ED4", "INTERACTIVE_CUT_SCOPE_CORRECTION_V1"): ("exclude", "same enumeration-subject line, raw/ copy"),
    ("research/gmi-ledger-selection-transport-repair-v1/raw/pr594/research/gmi-grand-unification-v1/RECURSIVE_GAP_AUDIT_20260913.md:L41", "AUTO-CFF2BDB98A57306E7C45", "INTERACTIVE_CUT_SCOPE_CORRECTION_V1"): ("exclude", "same enumeration-subject line, raw/ copy"),
    ("research/gmi-grand-unification-v1/FALSIFIABILITY_REGISTRY_V1.md:L71", "ECOLOGY_EXTENSION_CONTRACT_V1", "TOM-1"): ("retype", "USES", "row's 'extends' targets ECOLOGY_CONTRACT+AXES_V2; TOM-1 owns the opponent forcing the contract uses"),
    ("research/gmi-threshold-task-frontier-v1/REPLAY_V1.md:L37", "AUTO-ACBA1EE541C2615B712B", "TT-6"): ("exclude", "subject of 'follows from' is TT-6's own statement, not the child"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_DEVELOPMENT_REACHABILITY_GENERALIZATION_BASE_V1.md:L185", "DG-2", "DG-3"): ("exclude", "reversed: 'a satisfactory law must reduce to DG-2/DG-3' - DG-2/DG-3 are reduction targets, child hypothetical"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_DG7_INDEX_AUDIT_V2.md:L198", "WITHIN_QUANTIZATION", "NON_DISCRIMINATING"): ("exclude", "status-string id as parent (the RV-377-060 edge from the same line is kept)"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_DOMAIN_N8_N11_EXECUTED_V1.md:L242", "RV-377-044", "DG-2"): ("exclude", "'extends past twice its largest ...' - spatial extent, not dependency"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_NOTE_QUESTIONS_STATUS_V1.md:L73", "GMI-T10-B", "RV-377-021"): ("exclude", "adjective: 'a generalizing memory (RV-377-021 H*(r))' - occupant-type name"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_PARENT_LITERATURE_LEDGER_V2.md:L89", "AUTO-6073B70736F244E33846", "RV-377-025"): ("exclude", "adjective: '(generalizing memory vs gradient occupant ...)'"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_REAL_TRANSFER_REVIVAL_RV_377_191_FREEZE.md:L136", "AUTO-0970A3BB4336465C33B4", "P-B1"): ("exclude", "status token 'SPECIALIZED predicted 0/8'"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_REAL_TRANSFER_REVIVAL_RV_377_193_FREEZE.md:L60", "P-B9", "P-B8"): ("exclude", "status token 'SPECIALIZED predicted 7/8'"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_RECURSIVE_CLOSURE_CORRIGENDUM_V1.md:L117", "AUTO-6E6EE517E156A10A82A6", "RC-07"): ("exclude", "subject of 'reduces to' is RC-07 itself, target unnamed"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_SHARED_VS_SPECIALIZED_LEARNING_THEOREM_V1.md:L234", "AUTO-6D9BC1F9961CB2459BC2", "SS-3"): ("exclude", "reversed: 'every broader theory should reduce to SS-3' - SS-3 is the target, child hypothetical"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_STAGE_B2_ATLAS_EXECUTED_V1.md:L298", "B2.2", "B2.9"): ("exclude", "adjective: 'C13 refined mediator monotone' in a status table row"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_THEORY_CORE_V3_EXECUTED.md:L158", "NMI-12", "NMI-1"): ("exclude", "verb sits inside the quoted NMI-1 gate chain, not a dependency statement"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_THEORY_CORE_V3_EXECUTED.md:L17", "EXACT-FAILED", "RV-025"): ("exclude", "adjective: 'generalizing memory in local-transducer bases' + child is a status-string id"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md:L1135", "AUTO-50D3E3792FFCE1CBF8D7", "TEST-TIME"): ("exclude", "'TEST-TIME' is the feature's category label, not a claim parent; 'extends the computation' is the feature's own property"),
    ("research/machine-intelligence-morphogenesis-v1/LITERATURE_LEDGER_V2.md:L153", "AUTO-717EADEB3D9AF531C009", "P0.MDL_OCCAM"): ("exclude", "adjective: 'Grunwald 2007 refined MDL' in a literature description"),
    ("research/machine-intelligence-morphogenesis-v1/LITERATURE_LEDGER_V2.md:L1937", "P_W", "GMI-T10"): ("exclude", "open question: 'can GMI-T10's phase boundary be derived from ...' - not an asserted dependency"),
    ("research/machine-intelligence-morphogenesis-v1/LITERATURE_LEDGER_V2.md:L3467", "AUTO-6B1F764D955FF8E0C9B7", "MC-SAT"): ("exclude", "subject is the 2006 literature paper ('the paper uses MCMC/Gibbs'), not the corpus claim"),
    ("research/machine-intelligence-morphogenesis-v1/LITERATURE_LEDGER_V2.md:L991", "ORION-OCM", "LITERATURE_LEDGER"): ("exclude", "both ids are URL/path fragments harvested as objects; census defect recorded, not a dependency"),
    ("research/machine-intelligence-morphogenesis-v1/README.md:L250", "RV-377-018", "PH-5"): ("exclude", "adjective: '(generalizing kNN memory ...)'; the PH-5-controls content is noted but no dependency verb stated"),
    ("research/gmi-grand-unification-v1/GRAND_GMI_MASTER_THEORY_V1.md:L186", "AUTO-9EA8B4ED8CC05013D5AC", "RQR-1"): ("exclude", "subject of 'extends' is the RQR family itself"),
    ("research/gmi-consolidation-lifecycle-repair-v1/raw/parents/CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md:L180", "AUTO-045A8A10325571974117", "SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1"): ("exclude", "subject of 'extends' is [SMR-1-4]; true edge would be SMR->SHARED_DEPENDENCY (later tranche)"),
    ("research/gmi-grand-unification-v1/CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md:L180", "AUTO-1B1522B41CC2973C43E4", "SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1"): ("exclude", "same SMR-subject line"),
    ("research/gmi-memory-teaching-repair-v1/raw/parent/research/gmi-grand-unification-v1/CERTIFIED_REUSE_INVALIDATION_THEOREM_V1.md:L180", "AUTO-D69EC7D23858EC6330B1", "SHARED_DEPENDENCY_MEMORY_REUSE_THEOREM_V1"): ("exclude", "same SMR-subject line, raw/ copy"),
    ("research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-44205ED9133037479619", "MSC-1"): ("exclude", "subject of 'uses' is MSC-1 ('MSC-1 uses ordinary nonvacuous existence')"),
    ("research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-44205ED9133037479619", "MSC-2"): ("exclude", "same MSC-subject line"),
    ("research/gmi-hierarchical-chunking-repair-v1/raw/parents/research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-A3B521ED9C1D11991392", "MSC-1"): ("exclude", "same MSC-subject line, raw/ copy"),
    ("research/gmi-hierarchical-chunking-repair-v1/raw/parents/research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-A3B521ED9C1D11991392", "MSC-2"): ("exclude", "same MSC-subject line, raw/ copy"),
    ("research/gmi-ledger-selection-transport-repair-v1/raw/parents/research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-A14750295B45D7CDF36D", "MSC-1"): ("exclude", "same MSC-subject line, raw/ copy"),
    ("research/gmi-ledger-selection-transport-repair-v1/raw/parents/research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-A14750295B45D7CDF36D", "MSC-2"): ("exclude", "same MSC-subject line, raw/ copy"),
    ("research/gmi-memory-teaching-repair-v1/raw/parent/research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-CCC24E57338375EEDC24", "MSC-1"): ("exclude", "same MSC-subject line, raw/ copy"),
    ("research/gmi-memory-teaching-repair-v1/raw/parent/research/gmi-grand-unification-v1/CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md:L168", "AUTO-CCC24E57338375EEDC24", "MSC-2"): ("exclude", "same MSC-subject line, raw/ copy"),
    ("research/machine-intelligence-morphogenesis-v1/GMI_DG9_CONSTANT_CONTROL_E1_E3_V1.md:L100", "AUTO-B47352F6B1D5F5DE609D", "GMI_THEORY_CORE_V3_EXECUTED"): ("exclude", "'the name the corpus uses' - naming reference; E3-lite lane identity noted, no dependency verb with the child as subject"),
}

def apply_review_overrides(edges):
    kept, excluded, retyped = [], [], []
    for e in edges:
        key = (e["citation"], e["child"], e["parent"])
        if key not in REVIEW_OVERRIDES:
            kept.append(e)
            continue
        ov = REVIEW_OVERRIDES[key]
        if ov[0] == "exclude":
            excluded.append({**e, "review_reason": ov[1]})
        else:
            e = {**e, "relation": ov[1], "review_reason": ov[2]}
            retyped.append(e)
            kept.append(e)
    return kept, excluded, retyped



def split_table_row(line):
    return [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]


def mine_parent_tables(path, lines, decls, id_index):
    """Claim-level dependency tables: child = nearest claim-class census object
    at-or-above the table header; parents = census-id cells else by-name."""
    edges = []
    i = 0
    while i < len(lines):
        if not PARENT_TABLE_HEADER.match(lines[i]):
            i += 1
            continue
        header_i = i
        parent_col = split_table_row(lines[i])
        try:
            pcol = next(j for j, c in enumerate(parent_col)
                        if re.search(r"parent|theorem", c, re.I))
        except StopIteration:
            i += 1
            continue
        i += 1
        if i < len(lines) and set(lines[i].replace("|", " ").strip()) <= {"-", " ", ":"}:
            i += 1  # separator row
        rows = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            rows.append(lines[i])
            i += 1
        if not rows:
            continue
        above = [d for d in decls if int(d["source_locator"][1:]) <= header_i + 1]
        child = above[-1] if above else None
        if child is None:
            continue
        for r in rows:
            cells = split_table_row(r)
            if len(cells) <= pcol or not cells[pcol]:
                continue
            cell = cells[pcol]
            ids = ids_in_span(cell, id_index, set(), 0, len(cell))
            if ids:
                for oid in sorted(ids):
                    edges.append({
                        "child": child["object_id"],
                        "child_id_kind": child["id_kind"],
                        "child_class": child["object_class"],
                        "parent": oid,
                        "parent_kind": "CORPUS_CLAIM",
                        "relation": "PARENT_TABLE",
                        "citation": f"{path}:L{header_i + 1}",
                        "evidence": r.strip()[:220],
                        "parent_declarations": len(id_index[oid]),
                        "parent_ambiguous_id": len(id_index[oid]) > 1,
                    })
            else:
                edges.append({
                    "child": child["object_id"],
                    "child_id_kind": child["id_kind"],
                    "child_class": child["object_class"],
                    "parent": cell[:120],
                    "parent_kind": "CORPUS_CLAIM_BY_NAME",
                    "relation": "PARENT_TABLE",
                    "citation": f"{path}:L{header_i + 1}",
                    "evidence": r.strip()[:220],
                })
    return edges


def mine_layer_a_rollup(objects, file_edges):
    """EXPLICIT claim objects whose statement references a doc inherit that
    doc's FILE_LOCAL edges (POINTER_ROLLUP)."""
    edges = []
    for o in sorted(objects, key=lambda o: o["object_id"]):
        if o["id_kind"] != "EXPLICIT" or o["object_class"] not in CLAIM_CLASSES:
            continue
        for m in FILE_REF.finditer(o.get("statement", "")):
            ref = m.group(1)
            if "/" in ref or not ref:
                continue
            target_dir = "/".join(o["source_path"].split("/")[:-1])
            for cand in {f"{target_dir}/{ref}", ref}:
                if cand in file_edges and cand != o["source_path"]:
                    for e in file_edges[cand]:
                        edges.append({
                            "child": o["object_id"],
                            "child_id_kind": "EXPLICIT",
                            "child_class": o["object_class"],
                            "parent": e["parent"],
                            "parent_kind": "CORPUS_CLAIM",
                            "relation": e["relation"],
                            "citation": e["citation"] + f" (rollup via {o['source_path']}:L{o['source_locator'][1:]})",
                            "evidence": e["evidence"],
                            "parent_declarations": e.get("parent_declarations"),
                            "parent_ambiguous_id": e.get("parent_ambiguous_id", False),
                            "rollup": True,
                        })
                    break
    kept, excluded, retyped = apply_review_overrides(edges)
    return kept


def mine_layer_b():
    edges = []
    for pdir in sorted(p for p in RESEARCH.iterdir()
                       if p.is_dir() and p.name.startswith("gmi-833-")):
        ledger = pdir / "PARENT_LEDGER.md"
        if not ledger.exists():
            continue
        text = ledger.read_text(encoding="utf-8")
        m = re.search(r"Claim ceiling:\s*`([^`]+)`", text)
        if not m:
            for alt_name in ("FREEZE_V1.md", "README.md"):
                alt = pdir / alt_name
                if alt.exists():
                    m = re.search(r"[Cc]laim ceiling:?\s*`?([A-Z0-9_]+)", alt.read_text(encoding="utf-8"))
                    if m:
                        break
        ceiling = m.group(1) if m else pdir.name
        for ln, line in enumerate(text.splitlines(), start=1):
            bm = re.match(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*[—–-]?\s*(.*)$", line)
            if not bm:
                continue
            name = bm.group(1).strip()
            if re.match(r"^#\d+$", name):
                continue
            edges.append({
                "child": ceiling,
                "parent": name[:160],
                "parent_kind": "EXTERNAL_LITERATURE",
                "relation": "STRONGEST_PARENT_DECLARED",
                "citation": f"research/{pdir.name}/PARENT_LEDGER.md:L{ln}",
                "evidence": line.strip()[:220],
            })
    for jpath in sorted(RESEARCH.rglob("*STRONGEST*PARENT*.json")):
        data = json.loads(jpath.read_text(encoding="utf-8"))
        rel = "research/" + str(jpath.relative_to(REPO_ROOT))
        for fq in data.get("fqs", []):
            lit = fq.get("literature_parent", {})
            name = (lit.get("name") or "").strip()
            if not name:
                continue
            edges.append({
                "child": fq.get("function_id"),
                "parent": name[:160],
                "parent_kind": "EXTERNAL_LITERATURE",
                "relation": "STRONGEST_PARENT_DECLARED",
                "citation": rel,
                "evidence": f"function_id={fq.get('function_id')}",
            })
    # programme-level literature/baseline ledger tables (child = package)
    for pdir in sorted(p for p in RESEARCH.iterdir() if p.is_dir()):
        for fname, relation, kind in (
            ("LITERATURE_LEDGER.md", "STRONGEST_PARENT_DECLARED", "EXTERNAL_LITERATURE"),
            ("PARENTS.md", "REGISTERED_BASELINE_PARENT", "EXTERNAL_LITERATURE"),
        ):
            f = pdir / fname
            if not f.exists():
                continue
            lines = f.read_text(encoding="utf-8").splitlines()
            rel_path = f"research/{pdir.name}/{fname}"
            for ln, line in enumerate(lines, start=1):
                if not line.strip().startswith("|"):
                    continue
                cells = split_table_row(line)
                if not cells or not re.search(r"parent", cells[0], re.I):
                    continue
                if re.fullmatch(r"[-\s:]*", line.replace("|", "").strip()):
                    continue
                name = cells[0]
                if re.fullmatch(r"(?i)parents?", name):
                    continue  # header row
                if not name or len(name) < 4:
                    continue
                edges.append({
                    "child": pdir.name,
                    "parent": name[:160],
                    "parent_kind": kind,
                    "relation": relation,
                    "citation": f"{rel_path}:L{ln}",
                    "evidence": line.strip()[:220],
                })
    seen, uniq = set(), []
    for e in edges:
        key = (e["child"], e["parent"], e["citation"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    return uniq


def mine_layer_c():
    """Post-census 833-family package->package edges from FREEZE_V1.md refs.

    Two encodings, both stated verbatim: full package names, and the family
    short-name scheme (AJ9<letter>, K0<digit>) resolved against the directory
    listing - self-references excluded."""
    edges = []
    pkg_re = re.compile(r"gmi-833-[a-z0-9-]+-v[0-9]+")
    dirs = {p.name: p for p in RESEARCH.iterdir()
            if p.is_dir() and p.name.startswith("gmi-833-")}
    # this package's own freeze references its parents as provenance; harvesting
    # them would make the graph mutate on every self-edit, so self is excluded
    dirs.pop(HERE.name, None)
    short = {}
    for name in sorted(dirs):
        m = re.match(r"gmi-833-aj9([a-g])-", name)
        if m:
            short.setdefault(f"AJ9{m.group(1)}", name)
        m = re.match(r"gmi-833-aj9[a-g]-k0([1-6])-", name)
        if m:
            short.setdefault(f"K0{m.group(1)}", name)
    short_re = re.compile(r"\b(AJ9[a-g]|K0[1-6])\b")
    for pname in sorted(dirs):
        freeze = dirs[pname] / "FREEZE_V1.md"
        if not freeze.exists():
            continue
        lines_ = freeze.read_text(encoding="utf-8").splitlines()
        for ln, line in enumerate(lines_, start=1):
            targets = set(pkg_re.findall(line))
            self_short = {t for t, pkg in short.items() if pkg == pname}
            targets |= {short[t] for t in short_re.findall(line)
                        if t in short and t not in self_short}
            for target in sorted(targets):
                if target == pname:
                    continue
                edges.append({
                    "child": pname,
                    "parent": target,
                    "parent_kind": "CORPUS_PACKAGE",
                    "relation": "PACKAGE_REFERENCED_IN_FREEZE",
                    "citation": f"research/{pname}/FREEZE_V1.md:L{ln}",
                    "evidence": line.strip()[:220],
                    "post_census": True,
                })
    seen, uniq = set(), []
    for e in edges:
        key = (e["child"], e["parent"], e["citation"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    return uniq


def main():
    objects = load_census()
    id_index = build_id_index(objects)
    a1, file_edges, prog, named, scanned, a1_excluded, a1_retyped = mine_layer_a(objects, id_index)
    a2 = mine_layer_a_rollup(objects, file_edges)
    fam = mine_family_anchors(objects)
    b = mine_layer_b()
    c = mine_layer_c()

    sha = subprocess.run(
        ["/usr/bin/git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True).stdout.strip()

    graph = {
        "schema": SCHEMA,
        "claim_ceiling": CLAIM_CEILING,
        "mined_at_sha": sha,
        "census_frozen_source_sha": json.loads(
            (CENSUS_DIR / "CORPUS_INDEX_V1.json").read_text(encoding="utf-8")
        )["frozen_source_sha"],
        "semantics": {
            "edge_meaning": "STATED dependency relation mined verbatim from the cited line; absence of an edge is NOT independence",
            "layers": {
                "file_local": "child = claim-class census object (EXPLICIT or PROVISIONAL) in the cited .md/.txt file; parent = EXPLICIT census id within +-%d chars of the relation token (Parent headers: whole line)" % WINDOW,
                "pointer_rollup": "an EXPLICIT claim object whose own statement references another research doc inherits that doc's file_local edges; citation carries the rollup provenance",
                "external_literature": "parent is a literature programme named by the corpus's own PARENT_LEDGER.md / STRONGEST_PARENT map",
                "corpus_package": "833-family package cross-references in FREEZE_V1.md (post-census layer)",
            },
            "exclusions": [
                "code and JSON files are not scanned (prose statements only)",
                "Parent-header lines referencing only #NNN issues are programme parents (counted, not edged)",
                "named-only references (theorem/lemma/proposition/corollary by name, no census id on the line) are counted as named_only_mentions, not edges",
            ],
        },
        "edges": {
            "file_local": a1,
            "pointer_rollup": a2,
            "parent_family_anchor": fam,
            "external_literature": b,
            "corpus_package": c,
        },
        "review": {
            "method": "every mined layer-A edge read against its source line (2 passes); overrides logged individually below; no other edge altered",
            "excluded_edges": a1_excluded,
            "retyped_edges": a1_retyped,
        },
        "programme_parent_mentions": prog,
        "coverage": {
            "prose_files_scanned": scanned,
            "named_only_mentions": named,
        },
    }
    out = HERE / "DEPENDENCY_GRAPH_V2.json"
    out.write_text(json.dumps(graph, indent=1, sort_keys=False,
                              ensure_ascii=False) + "\n", encoding="utf-8")
    digest = hashlib.sha256(out.read_bytes()).hexdigest()

    mainline = {o["object_id"]: o for o in objects
                if o["audit_disposition"] == "GREEN" and o["id_kind"] == "EXPLICIT"
                and o["object_class"] in CLAIM_CLASSES}
    cov = {k: sorted({e["child"] for e in v} & set(mainline))
           for k, v in (("file_local", a1), ("pointer_rollup", a2))}
    print(f"A1 file_local edges:            {len(a1)} (children {len({e['child'] for e in a1})})")
    print(f"  EXPLICIT children:             {sum(1 for e in a1 if e['child_id_kind']=='EXPLICIT')}")
    print(f"  ambiguous parent id:           {sum(1 for e in a1 if e.get('parent_ambiguous_id'))}")
    print(f"A2 pointer_rollup edges:         {len(a2)} (children {len({e['child'] for e in a2})})")
    print(f"  mainline(173) covered A1:      {len(cov['file_local'])}")
    print(f"  mainline(173) covered A1+A2:   {len(set(cov['file_local']) | set(cov['pointer_rollup']))}")
    print(f"A3 parent_family_anchor edges:    {len(fam)} (children {len({e['child'] for e in fam})})")
    print(f"B external_literature edges:     {len(b)}")
    print(f"C corpus_package edges:          {len(c)}")
    print(f"programme parent mentions:       {len(prog)}")
    print(f"prose files scanned:             {scanned}; named-only mentions: {named}")
    print(f"sha256 {out.name}: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
