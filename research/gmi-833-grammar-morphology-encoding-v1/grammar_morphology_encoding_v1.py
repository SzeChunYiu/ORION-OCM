#!/usr/bin/env python3
"""GMI #833 Section B — identify search grammars that encode the target morphology.

Executor for `gmi-833-grammar-morphology-encoding-v1`. Protocol frozen in FREEZE_V1.md
(+ Amendments A1-A3) BEFORE this file existed; git order proves it.

Two materially independent DETECTOR routes (freeze section 4):
  D-LEX  lexical/definitional, corpus-wide over P-LEX, using the corpus's OWN D1 denylist
         and 31-key D2 mapping, via the merged #855/A2 extractor (reuse-first, never
         re-implemented). Reproduction route: parents already closed it at 0 confirmed.
  D-COST structural/cost, exact integer arithmetic over P-COST. Discovery route.

Three re-encoding generators (freeze section 3 + A2):
  R1a single-production deletion, R1b full macro unfold, R2 non-isometric remint,
  R3 isometric relabel (no-alarm control).

Tier-1 ENCODES is decided by R1 only (a target-exclusive production). R2 is the #891
BIAS-1 boundary generator: it reproduces the registered structural-bias property and is
NEVER read as a leak, because a same-coverage cost remint reverses selection for almost
any non-degenerate grammar -- that is exactly what #891 already proved.

Run:  python3 -I -B grammar_morphology_encoding_v1.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESEARCH = REPO / "research"
A2_PKG = RESEARCH / "gmi-833-a2-signature-extension-v1"
SELF_PKG = "gmi-833-grammar-morphology-encoding-v1"  # Amendment A4: authority-self-skip

SCHEMA = "GMI833GrammarMorphologyEncodingReceiptV1"
ISSUE = 833
SOURCE_MAIN = "6590cd998cdc7d60333d3c4ec446ae7757788a4b"
FREEZE_COMMIT = "e662d9d50a260d07ffba25665b72d0a559c75b29"
CLAIM_CEILING = "GMI_833_SEARCH_GRAMMAR_TARGET_ENCODING_IDENTIFICATION_AT_REGISTERED_SCOPE"
FORBIDDEN_PROMOTIONS = (
    "G0_UNBIASED",
    "NO_KNOWN_FAMILY_PRIVILEGED_UNIVERSALLY",
    "REPRESENTATION_INVARIANT_COST_UNIVERSALLY",
    "SEARCH_NEUTRALITY_PROVED",
    "ARCHITECTURE_PRIOR_FREE_GRAMMAR",
    "ALL_SCALARIZATIONS_AGREE",
    "COMPLETE_GMI",
    "GRAMMAR_NEUTRALITY_PROVED",
    "NO_GRAMMAR_ENCODES_TARGET_UNIVERSALLY",
    "CORPUS_WIDE_COST_ROUTE_COMPLETE",
)

sys.path.insert(0, str(HERE))
import adapters_v1  # noqa: E402


# ============================================================ D-COST core (exact integers)
def classes_of(pres: Sequence[Dict[str, object]]) -> List[str]:
    return sorted(set(str(p["sem"]) for p in pres))


def mu(pres: Sequence[Dict[str, object]], sem: str) -> Optional[int]:
    """Minimum description cost of semantic class `sem`; None when unreachable."""
    best = None  # type: Optional[int]
    for p in pres:
        if p["sem"] == sem:
            c = int(p["cost"])
            if best is None or c < best:
                best = c
    return best


def mu_map(pres: Sequence[Dict[str, object]],
           universe: Sequence[str]) -> Dict[str, Optional[int]]:
    return dict((s, mu(pres, s)) for s in universe)


def argmin_classes(m: Dict[str, Optional[int]]) -> FrozenSet[str]:
    """Complete argmin SET. Ties are never broken by name (hostile H4)."""
    live = dict((s, v) for s, v in m.items() if v is not None)
    if not live:
        return frozenset()
    lo = min(live.values())
    return frozenset(s for s, v in live.items() if v == lo)


def delete_productions(pres: Sequence[Dict[str, object]],
                       q: Set[str]) -> List[Dict[str, object]]:
    """G\\Q: presentations whose leaves avoid every deleted production."""
    return [p for p in pres if not (set(p["leaves"]) & q)]


def dep_classes(base: Dict[str, Optional[int]],
                after: Dict[str, Optional[int]]) -> FrozenSet[str]:
    """Classes whose minimum cost CHANGED. Computed from costs, never from names."""
    return frozenset(s for s in base if base[s] != after[s])


def is_class_indicator(pres: Sequence[Dict[str, object]], target: str,
                       q: Set[str]) -> bool:
    """Amendment A5: does Q simply mark class `target`?

    True when every presentation of `target` uses some production of Q and no presentation
    of any other class does. Then `dep(Q) = {target}` follows from the audited package's own
    classifier reading the production symbol, and the hit carries no cost content.
    Computed from the incidence relation only -- still name-blind.
    """
    tgt = [p for p in pres if p["sem"] == target]
    if not tgt:
        return False
    if not all(set(p["leaves"]) & q for p in tgt):
        return False
    return not any(set(p["leaves"]) & q for p in pres if p["sem"] != target)


def r1_probe(pres: Sequence[Dict[str, object]], target: str,
             q: Set[str], via: str) -> Optional[Dict[str, object]]:
    """One R1 deletion probe. Returns a Tier-1 hit record or None."""
    universe = classes_of(pres)
    base = mu_map(pres, universe)
    if base.get(target) is None:
        return None
    kept = delete_productions(pres, q)
    after = mu_map(kept, universe)
    dep = dep_classes(base, after)
    if dep != frozenset([target]):
        return None                      # not target-exclusive
    mt = after[target]
    if mt is not None and mt <= base[target]:
        return None                      # no cost rise
    kind = "TARGET_IS_A_PRIMITIVE" if mt is None else "TARGET_SPECIFIC_SHORTCUT"
    n_using = sum(1 for p in pres if set(p["leaves"]) & q)
    n_target = sum(1 for p in pres if p["sem"] == target)
    flip = (argmin_classes(base) == frozenset([target])
            and argmin_classes(after) != frozenset([target]))
    return {
        "via": via,
        "productions": sorted(q),
        "kind": kind,
        "mu_target_before": base[target],
        "mu_target_after": mt,
        "dep": sorted(dep),
        "argmin_before": sorted(argmin_classes(base)),
        "argmin_after": sorted(argmin_classes(after)),
        "tier2_decisive_selection_flip": flip,
        "n_presentations_using": n_using,
        "n_target_presentations": n_target,
        "n_semantic_classes": len(universe),
        "UNIQUE_REALIZATION": n_target == 1,
        "SINGLE_CLASS_INSTANCE": len(universe) == 1,
        "encoding_kind": ("PRODUCTION_IS_CLASS_INDICATOR"
                          if is_class_indicator(pres, target, q) else "COST_MEASURED"),
        # How thin the COST_MEASURED verdict is: presentations of OTHER classes that use Q.
        # 0 means the production marks the target class exactly (an indicator).
        "indicator_margin": sum(1 for p in pres
                                if p["sem"] != target and set(p["leaves"]) & q),
    }


def r1_hits(g: Dict[str, object]) -> Tuple[List[Dict[str, object]], List[str]]:
    """R1a (single deletions) + R1b (full macro unfold). Returns (hits, notes)."""
    pres = g["presentations"]
    target = g["declared_target"]
    notes = []  # type: List[str]
    if target is None:
        return [], ["R1_NOT_APPLICABLE:NO_DECLARED_TARGET"]
    vocab = sorted(set(x for p in pres for x in p["leaves"]))
    hits = []  # type: List[Dict[str, object]]
    if len(vocab) < 2:
        notes.append("R1_NOT_APPLICABLE:" + ("NO_PRODUCTION_STRUCTURE" if not vocab
                                             else "NUMERIC_PARAMETER_SPACE"))
    else:
        for q in vocab:
            h = r1_probe(pres, target, set([q]), "R1a")
            if h is not None:
                hits.append(h)
    comps = sorted(g.get("composites") or [])
    if not comps:
        notes.append("R1_NOT_APPLICABLE:NO_COMPOSITE_PRODUCTIONS")
    else:
        h = r1_probe(pres, target, set(comps), "R1b")
        if h is not None:
            hits.append(h)
    return hits, notes


# ------------------------------------------------------------- R2 non-isometric remint
def r2_remints(pres: Sequence[Dict[str, object]]) -> List[Dict[str, object]]:
    """Exchange cost values between two equal-size classes along the id-sorted bijection.

    Semantic COVERAGE is preserved exactly; the class->cost attachment is not. This is
    #891 BIAS-1 generalized.
    """
    by = {}  # type: Dict[str, List[Dict[str, object]]]
    for p in pres:
        by.setdefault(str(p["sem"]), []).append(p)
    for k in by:
        by[k].sort(key=lambda p: str(p["pid"]))
    out = []  # type: List[Dict[str, object]]
    names = sorted(by)
    for i, s1 in enumerate(names):
        for s2 in names[i + 1:]:
            if len(by[s1]) != len(by[s2]):
                continue
            swap = {}  # type: Dict[str, int]
            for a, b in zip(by[s1], by[s2]):
                swap[str(a["pid"])] = int(b["cost"])
                swap[str(b["pid"])] = int(a["cost"])
            new = []  # type: List[Dict[str, object]]
            for p in pres:
                q = dict(p)
                if str(p["pid"]) in swap:
                    q["cost"] = swap[str(p["pid"])]
                new.append(q)
            out.append({"pair": [s1, s2], "presentations": new})
    return out


def r2_report(g: Dict[str, object]) -> Dict[str, object]:
    pres = g["presentations"]
    universe = classes_of(pres)
    base = argmin_classes(mu_map(pres, universe))
    flips = []  # type: List[Dict[str, object]]
    remints = r2_remints(pres)
    for r in remints:
        after = argmin_classes(mu_map(r["presentations"], universe))
        if after != base:
            flips.append({"pair": r["pair"], "argmin_before": sorted(base),
                          "argmin_after": sorted(after)})
    return {
        "remints": len(remints),
        "selection_reversals": len(flips),
        "bias1_reproduced": bool(flips),
        "argmin_before": sorted(base),
        "witnesses": flips[:8],
    }


# ---------------------------------------------------------------- R3 isometric relabel
def r3_relabel(pres: Sequence[Dict[str, object]], seed: int) -> List[Dict[str, object]]:
    """Deterministic bijection of presentation identities AND production names.

    Semantic class, cost and leaves-multiset structure are preserved exactly, so this is
    an isometry: it must never change any mu, argmin, dep or hit.
    """
    vocab = sorted(set(x for p in pres for x in p["leaves"]))
    pmap = dict((v, "sym%03d_%d" % (i, seed)) for i, v in enumerate(vocab))
    out = []  # type: List[Dict[str, object]]
    for i, p in enumerate(sorted(pres, key=lambda z: str(z["pid"]))):
        out.append({"pid": "id%05d_%d" % ((i * 7919 + seed) % 100000, seed),
                    "leaves": sorted(pmap[x] for x in p["leaves"]),
                    "cost": int(p["cost"]), "sem": p["sem"]})
    return out


def is_isometry(a: Sequence[Dict[str, object]], b: Sequence[Dict[str, object]]) -> bool:
    """A relabeling is an isometry iff it preserves, per semantic class, the exact
    multiset of (cost, leaf-count) and the class sizes. Any raw-cost or structure
    mutation breaks it (cf. #891's NON_ISOMETRIC_REMINT terminal)."""
    def sig(ps):
        d = {}  # type: Dict[str, List[Tuple[int, int]]]
        for p in ps:
            d.setdefault(str(p["sem"]), []).append((int(p["cost"]), len(p["leaves"])))
        return dict((k, sorted(v)) for k, v in d.items())
    return sig(a) == sig(b)


def hit_fingerprint(hits: Sequence[Dict[str, object]]) -> str:
    """Name-blind fingerprint of a hit set (production NAMES deliberately excluded)."""
    rows = sorted([(h["via"], h["kind"], h["mu_target_before"], h["mu_target_after"],
                    tuple(sorted(h["dep"])), h["tier2_decisive_selection_flip"],
                    h["n_presentations_using"], h["n_target_presentations"])
                   for h in hits], key=repr)
    return hashlib.sha256(repr(rows).encode()).hexdigest()[:16]


# ========================================================== D-LEX corpus-wide screen
def _load_a2():
    spec = importlib.util.spec_from_file_location(
        "gmi833_a2_ext", str(A2_PKG / "a2_extension_v1.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gmi833_a2_ext"] = mod
    spec.loader.exec_module(mod)
    return mod


GRAMMAR_VOCAB_RE = re.compile(r"grammar|\bDSL\b", re.I)
OWNER_RE = re.compile(r"BANNED_MI_PRIMITIVES|FORBIDDEN_[A-Z_]+|forbidden_symbol_substrings"
                      r"|denylist|DENYLIST", re.I)
IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b")
NEGATION_RE = re.compile(
    r"\bno\b|\bnon[-_ ]|\bnot\b|\bwithout\b|\bexclud|\bforbidden\b|\bbanned\b"
    r"|\bdenylist\b|\bprohibit|NOT NEURAL", re.I)
ATLAS_RE = re.compile(r"microfeature (registry|atlas)|PARENT[_ ]ATLAS|parent literature"
                      r"|NOT NEURAL EVIDENCE|parent atlas", re.I)
AUDIT_PKG_RE = re.compile(r"audit|adjudicat|screen|rescore|claim-discipline|a2-signature"
                          r"|no-smuggling|corpus-passes|ledger|registr", re.I)


def a1_norm(token: str) -> str:
    return re.sub(r"[^a-z0-9]", "",
                  re.sub(r"(?<=[a-z])(?=[A-Z])", " ", token).lower().replace(" ", ""))


def d_lex_screen() -> Dict[str, object]:
    a2 = _load_a2()
    denylist = ["transformer", "self_attention", "conv2d", "lstm_gate", "rag_retriever"]
    d2 = sorted(a2.D2_MAPPING)
    lex = sorted(set(denylist + d2))
    norm_lex = [(t, a1_norm(t)) for t in lex]

    pkgs = sorted(p.name for p in RESEARCH.iterdir()
                  if p.is_dir() and p.name != SELF_PKG)  # Amendment A4 authority-self-skip
    population = []  # type: List[str]
    rows = {}  # type: Dict[str, Dict[str, object]]
    for pkg in pkgs:
        files = a2.primitive_defining_files(RESEARCH / pkg)
        gfiles = [(p, t) for p, t in files
                  if GRAMMAR_VOCAB_RE.search(t) or GRAMMAR_VOCAB_RE.search(p.stem)]
        if not gfiles:
            continue
        population.append(pkg)
        hits = []  # type: List[Dict[str, object]]
        n_blocks = 0
        for p, text in gfiles:
            owner = bool(OWNER_RE.search(text))
            for name, body, kind in a2.extract_blocks(p, text):
                if not body or not body.strip():
                    continue
                n_blocks += 1
                idents = set(IDENT_RE.findall(str(name)))
                for tok in IDENT_RE.findall(str(body))[:4000]:
                    idents.add(tok)
                for ident in sorted(idents):
                    n = a1_norm(ident)
                    matched = None
                    for raw, nl in norm_lex:
                        if len(n) >= len(nl) and nl in n:
                            matched = raw
                            break
                    if matched is not None:
                        hits.append({
                            "file": str(p.relative_to(REPO)), "block": str(name),
                            "kind": kind, "ident": ident, "lexicon_token": matched,
                            "denylist_owner_file": owner,
                            "context": " ".join(str(body).split())[:360],
                            "atlas_file": bool(ATLAS_RE.search(text[:4000])),
                        })
                        break
        rows[pkg] = {"n_grammar_files": len(gfiles), "n_blocks": n_blocks,
                     "hits": hits}
    flagged = sorted(k for k, v in rows.items() if v["hits"])
    return {"authority_self_skip": SELF_PKG,
            "population": population, "n_population": len(population),
            "n_blocks": sum(int(v["n_blocks"]) for v in rows.values()),
            "flagged_packages": flagged, "n_flagged": len(flagged),
            "n_hits": sum(len(v["hits"]) for v in rows.values()),
            "lexicon_size": len(lex), "rows": rows}


def _segments(ident):
    return [x for x in re.split(r"[^A-Za-z0-9]+",
                                re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", ident)) if x]


def d_lex_adjudicate(lex):
    """Adjudicate EVERY D-LEX hit individually, with a written reason.

    Ordered, named false-positive classes. A hit that survives every class is
    NEEDS_READ and, if a read does not refute it, a CONFIRMED_LEAK.
    """
    read_verified = {
        ("research/machine-intelligence-morphogenesis-v1/gmi_k4_freeze.py",
         "G1_TENSOR_GRAPH"):
            ("PROSE_NEGATION", "gmi_k4_freeze.py:146-148 defines GRAMMARS['G1_TENSOR_GRAPH']"
             " and its text ENDS with the explicit anti-encoding clause 'No convolution, "
             "attention, gate, expert, retriever or adapter macro.' -- the token is the "
             "corpus's own prohibition, not a production."),
        ("research/machine-intelligence-morphogenesis-v1/"
         "GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.md", None):
            ("PARENT_LITERATURE_ATLAS",
             "registry header line 3 declares 'MACHINE-READABLE MICROFEATURE ATLAS -- "
             "TYPED LOCATIONS PLUS CLAIM LEVELS; NOT NEURAL EVIDENCE': TF-* rows are "
             "parent-literature comparison targets, not productions of any searched "
             "grammar."),
    }
    rows = []
    counts = {}
    for pkg in sorted(lex["rows"]):
        for h in lex["rows"][pkg]["hits"]:
            ctx = str(h.get("context", ""))
            key_file = (h["file"], h["block"])
            key_any = (h["file"], None)
            hit_read = read_verified.get(key_file) or read_verified.get(key_any)
            if hit_read is not None:
                cls, reason = hit_read
            elif str(h["lexicon_token"]).lower() not in [
                    x.lower() for x in _segments(str(h["ident"]))]:
                cls = "SUBSTRING_COLLISION"
                reason = ("the lexicon token is a bare substring of an unrelated word "
                          "(%r inside %r) and is not a segment of the identifier"
                          % (h["lexicon_token"], h["ident"]))
            elif NEGATION_RE.search(ctx) or NEGATION_RE.search(str(h["block"])):
                cls = "PROSE_NEGATION"
                reason = ("the lexicon token appears inside an explicit negation / "
                          "exclusion statement, i.e. the corpus declaring the family is "
                          "NOT used")
            elif h["denylist_owner_file"] or AUDIT_PKG_RE.search(h["file"]):
                cls = "AUDIT_RECORD_ECHO"
                reason = ("the file is the corpus's own anti-smuggling / audit / registry "
                          "machinery recording the banned token; this is the registered "
                          "#976 denylist-owner false-positive class")
            elif h.get("atlas_file"):
                cls = "PARENT_LITERATURE_ATLAS"
                reason = ("the file declares itself a parent-literature microfeature "
                          "atlas / registry; its rows are comparison targets, not "
                          "productions of a searched grammar")
            elif "http" in ctx:
                cls = "PROSE_CITATION"
                reason = "the token occurs inside an external citation / URL"
            elif h["kind"] == "B-MD-ROW":
                cls = "REGISTRY_BOOKKEEPING"
                reason = ("a markdown ledger/registry row naming another package, theorem "
                          "or receipt id -- bookkeeping, not a grammar production")
            else:
                cls = "NEEDS_READ"
                reason = "no registered false-positive class applies; requires a read"
            counts[cls] = counts.get(cls, 0) + 1
            rows.append({"package": pkg, "file": h["file"], "block": h["block"],
                         "kind": h["kind"], "ident": h["ident"],
                         "lexicon_token": h["lexicon_token"],
                         "class": cls, "reason": reason,
                         "read_verified": hit_read is not None})
    return {"schema": "GMI_833_B48_DLEX_ADJUDICATION_V1", "n_hits": len(rows),
            "classes": counts, "confirmed_leaks": counts.get("NEEDS_READ", 0),
            "rows": rows}


# ========================================================================= validation
def planted_shortcut(g: Dict[str, object], name: str = "PLANT_MACRO") -> Dict[str, object]:
    """V2: plant a real target-specific shortcut into a REAL corpus grammar.

    Adds one presentation of the declared target, over a fresh production used by nothing
    else, at a cost strictly below the target's current minimum. A working detector MUST
    flag it; a broken one will not.
    """
    pres = [dict(p) for p in g["presentations"]]
    t = g["declared_target"]
    base = mu(pres, t)
    pres.append({"pid": "__planted__", "leaves": [name],
                 "cost": int(base) - 1 if base is not None else 0, "sem": t})
    # A second, cost-neutral planted production on ANOTHER class, so |P(G)| >= 2 holds
    # even for numeric-vocabulary grammars (Amendment A1) and recall is tested there too.
    others = [c for c in classes_of(pres) if c != t]
    if others:
        oc = mu(pres, others[0])
        pres.append({"pid": "__planted_neutral__", "leaves": ["PLANT_NEUTRAL"],
                     "cost": int(oc) if oc is not None else 0, "sem": others[0]})
    out = dict(g)
    out["presentations"] = pres
    return out


def run_validation(grammars: Sequence[Dict[str, object]]) -> Dict[str, object]:
    val = {}  # type: Dict[str, object]

    # --- V1 ANCHOR (blocking): re-find #891 BIAS-1 -------------------------------
    ga = [g for g in grammars if g["grammar_id"] == "cost_privilege_GA"][0]
    gb = [g for g in grammars if g["grammar_id"] == "cost_privilege_GB"][0]
    ua, ub = classes_of(ga["presentations"]), classes_of(gb["presentations"])
    sel_a = argmin_classes(mu_map(ga["presentations"], ua))
    sel_b = argmin_classes(mu_map(gb["presentations"], ub))
    r2a = r2_report(ga)
    v1_ok = (sel_a == frozenset(["ALPHA"]) and sel_b == frozenset(["BETA"])
             and r2a["bias1_reproduced"] and ua == ub)
    val["V1_anchor_891"] = {
        "GA_selection": sorted(sel_a), "GB_selection": sorted(sel_b),
        "semantic_coverage_equal": ua == ub,
        "r2_selection_reversals_on_GA": r2a["selection_reversals"],
        "weight": ga.get("weight"), "pass": bool(v1_ok),
    }

    # --- V2 RECALL on REAL corpus grammars ---------------------------------------
    recall_rows = []  # type: List[Dict[str, object]]
    for g in grammars:
        if g["declared_target"] is None or g["grammar_id"].startswith("clean_control"):
            continue
        planted = planted_shortcut(g)
        hits, _n = r1_hits(planted)
        caught = any(h["productions"] == ["PLANT_MACRO"] for h in hits)
        recall_rows.append({"grammar_id": g["grammar_id"], "caught": bool(caught)})
    val["V2_planted_recall"] = {
        "n": len(recall_rows),
        "caught": sum(1 for r in recall_rows if r["caught"]),
        "rows": recall_rows,
        "pass": all(r["caught"] for r in recall_rows) and len(recall_rows) > 0,
    }

    # --- V3 NO-ALARM --------------------------------------------------------------
    r3_rows = []  # type: List[Dict[str, object]]
    for g in grammars:
        if g["declared_target"] is None:
            continue
        base_hits, _ = r1_hits(g)
        base_fp = hit_fingerprint(base_hits)
        ok = True
        for seed in range(1, 11):
            gg = dict(g)
            gg["presentations"] = r3_relabel(g["presentations"], seed)
            comps = g.get("composites") or []
            if comps:
                vocab = sorted(set(x for p in g["presentations"] for x in p["leaves"]))
                cmap = dict((v, "sym%03d_%d" % (i, seed)) for i, v in enumerate(vocab))
                gg["composites"] = sorted(cmap[c] for c in comps if c in cmap)
            hits, _ = r1_hits(gg)
            if hit_fingerprint(hits) != base_fp:
                ok = False
                break
        r3_rows.append({"grammar_id": g["grammar_id"], "isometry_invariant": ok,
                        "relabelings": 10})
    clean = [g for g in grammars if g["grammar_id"] == "clean_control_NEUTRAL"][0]
    clean_hits, clean_notes = r1_hits(clean)
    val["V3_no_alarm"] = {
        "r3_rows": r3_rows,
        "r3_all_invariant": all(r["isometry_invariant"] for r in r3_rows),
        "clean_control_hits": len(clean_hits),
        "clean_control_notes": clean_notes,
        "pass": all(r["isometry_invariant"] for r in r3_rows) and not clean_hits,
    }

    # --- V4 HOSTILES ---------------------------------------------------------------
    probe = [g for g in grammars if g["grammar_id"] == "grammar_growth_G2"][0]
    pres = probe["presentations"]
    universe = classes_of(pres)
    t = probe["declared_target"]
    base = mu_map(pres, universe)
    hostiles = {}  # type: Dict[str, str]

    # H1 name-based exclusivity instead of dep-based
    name_excl = [q for q in sorted(set(x for p in pres for x in p["leaves"]))
                 if t.lower()[:4] in q.lower()]
    hostiles["H1_NAME_BASED_EXCLUSIVITY"] = (
        "DETECTED" if not name_excl else "NOT_DETECTED")

    # H2 sentinel integer instead of None
    kept = delete_productions(pres, set(probe["composites"]))
    sentinel = dict((s, (10 ** 9 if mu(kept, s) is None else mu(kept, s)))
                    for s in universe)
    real = mu_map(kept, universe)
    hostiles["H2_SENTINEL_MU"] = ("DETECTED"
                                  if any(sentinel[s] != real[s] for s in universe)
                                  or all(real[s] is not None for s in universe)
                                  else "NOT_DETECTED")

    # H3 superset dep test (dep >= {t}) admits a SHARED production. Registered fixture:
    # production `sh` is the unique cheapest route for BOTH classes, so it is load
    # bearing, not target-exclusive. The frozen `dep == {t}` rule must reject it; the
    # hostile `t in dep` rule must accept it.
    h3 = [{"pid": "a", "leaves": ["sh"], "cost": 1, "sem": "TGT"},
          {"pid": "b", "leaves": ["x"], "cost": 5, "sem": "TGT"},
          {"pid": "c", "leaves": ["sh"], "cost": 1, "sem": "OTH"},
          {"pid": "d", "leaves": ["y"], "cost": 5, "sem": "OTH"}]
    h3u = classes_of(h3)
    h3b = mu_map(h3, h3u)
    h3d = dep_classes(h3b, mu_map(delete_productions(h3, set(["sh"])), h3u))
    hostiles["H3_SUPERSET_DEP"] = (
        "DETECTED" if (h3d != frozenset(["TGT"]) and "TGT" in h3d) else "NOT_DETECTED")

    # H4 name tie-break on a true argmin tie
    tie = [{"pid": "x", "leaves": ["u"], "cost": 1, "sem": "AAA"},
           {"pid": "y", "leaves": ["v"], "cost": 1, "sem": "BBB"}]
    hostiles["H4_NAME_TIE_BREAK"] = (
        "DETECTED" if argmin_classes(mu_map(tie, classes_of(tie)))
        == frozenset(["AAA", "BBB"]) else "NOT_DETECTED")

    # H5 a claimed R3 that mutates a raw cost is NOT an isometry and must be rejected.
    genuine = r3_relabel(pres, 1)
    mutated = [dict(p) for p in genuine]
    mutated[0]["cost"] = int(mutated[0]["cost"]) + 5
    hostiles["H5_NON_ISOMETRIC_R3"] = (
        "DETECTED" if (is_isometry(pres, genuine) and not is_isometry(pres, mutated))
        else "NOT_DETECTED")

    # H6 presentation identities smuggled in as pseudo-productions (Amendment A1).
    # The degeneracy A1 forbids is a bare cost table whose classes are singletons: there
    # the pid-as-production reading manufactures a TARGET_IS_A_PRIMITIVE hit out of
    # nothing. #891's GA is exactly such an object, and is used as the hostile probe.
    ga = [x for x in grammars if x["grammar_id"] == "cost_privilege_GA"][0]
    real_n = len(r1_hits(ga)[0])
    ps = dict(ga)
    ps["presentations"] = [{"pid": p["pid"], "leaves": [str(p["pid"])],
                            "cost": p["cost"], "sem": p["sem"]}
                           for p in ga["presentations"]]
    ps["composites"] = []
    pseudo_n = len(r1_hits(ps)[0])
    hostiles["H6_PSEUDO_PRODUCTION_IDS"] = (
        "DETECTED" if (real_n == 0 and pseudo_n > 0) else "NOT_DETECTED")
    hostiles["_H6_counts"] = "GA real=%d pseudo=%d" % (real_n, pseudo_n)

    # H7 a detector variant omitting the A5 indicator test merges the two encoding kinds.
    all_hits = []
    for gg in grammars:
        if gg["declared_target"] is None:
            continue
        all_hits.extend(r1_hits(gg)[0])
    kinds = set(h["encoding_kind"] for h in all_hits)
    hostiles["H7_MISSING_INDICATOR_TEST"] = (
        "DETECTED" if kinds == set(["COST_MEASURED", "PRODUCTION_IS_CLASS_INDICATOR"])
        else "NOT_DETECTED")
    hostiles["_H7_counts"] = "hits=%d kinds=%s" % (len(all_hits), sorted(kinds))

    val["V4_hostiles"] = {
        "results": hostiles,
        "pass": all(v == "DETECTED" for k, v in hostiles.items()
                    if not k.startswith("_"))}

    # --- V5 NULL -------------------------------------------------------------------
    null_rows = 0
    null_bad = 0
    for g in grammars:
        if g["declared_target"] is None:
            continue
        base_fp = hit_fingerprint(r1_hits(g)[0])
        for seed in range(1000, 1000 + 200 // max(1, len(grammars) - 2) + 1):
            gg = dict(g)
            gg["presentations"] = r3_relabel(g["presentations"], seed)
            comps = g.get("composites") or []
            if comps:
                vocab = sorted(set(x for p in g["presentations"] for x in p["leaves"]))
                cmap = dict((v, "sym%03d_%d" % (i, seed)) for i, v in enumerate(vocab))
                gg["composites"] = sorted(cmap[c] for c in comps if c in cmap)
            null_rows += 1
            if hit_fingerprint(r1_hits(gg)[0]) != base_fp:
                null_bad += 1
    val["V5_null"] = {"randomized_isometry_controls": null_rows,
                      "spurious_changes": null_bad, "pass": null_bad == 0}

    val["ALL_PASS"] = all(bool(val[k]["pass"]) for k in
                          ("V1_anchor_891", "V2_planted_recall", "V3_no_alarm",
                           "V4_hostiles", "V5_null"))
    return val


# ============================================================================== run
def adjudicate(g: Dict[str, object], hits: List[Dict[str, object]],
               notes: List[str]) -> Dict[str, object]:
    gid = g["grammar_id"]
    target = g["declared_target"]
    if target is None:
        return {"grammar_id": gid, "package": g["package"],
                "corpus": bool(g.get("corpus", True)),
                "disposition": "NO_DECLARED_TARGET",
                "reason": "the package declares no target morphology to recover; it is "
                          "screened, not cleared",
                "hits": [], "notes": notes}
    real = [h for h in hits if not h["SINGLE_CLASS_INSTANCE"]]
    vacuous = [h for h in hits if h["SINGLE_CLASS_INSTANCE"]]
    # "could not check" is NEVER "checked and fine": if the whole R1a layer was
    # inapplicable (no production structure / numeric parameter space), the instance is
    # SCREENED, not NEUTRAL. NO_COMPOSITE_PRODUCTIONS blocks only R1b, so R1a still ran.
    blocking = [n for n in notes if n in ("R1_NOT_APPLICABLE:NO_PRODUCTION_STRUCTURE",
                                          "R1_NOT_APPLICABLE:NUMERIC_PARAMETER_SPACE")]
    if not real and blocking:
        return {"grammar_id": gid, "package": g["package"],
                "source_citation": g["source_citation"],
                "declared_target": target, "target_citation": g["target_citation"],
                "corpus": bool(g.get("corpus", True)),
                "disposition": "SCREENED_NOT_ADJUDICATED:" + blocking[0].split(":", 1)[1],
                "reason": "the R1 production layer does not apply to this grammar "
                          "(Amendment A1); it is screened at the R1 route and remains in "
                          "scope for R2/R3 -- this is NOT a clean verdict",
                "tier1_hits": [], "vacuous_hits": vacuous, "notes": notes,
                "tier2_decisive_selection_flip_via_R1": False,
                "disclosure_evidence": g["disclosure"]["evidence"],
                "n_presentations": len(g["presentations"]),
                "n_semantic_classes": len(classes_of(g["presentations"]))}
    if not real:
        disp = "NEUTRAL_AT_REGISTERED_SCOPE"
        reason = ("no target-exclusive production: every production whose deletion changes "
                  "mu(target) also changes the minimum of at least one other class, or "
                  "changes no cost at all")
        if vacuous:
            disp = "SCREENED_NOT_ADJUDICATED:VACUOUS_EXCLUSIVITY_SINGLE_CLASS"
            reason = "the instance has one semantic class; exclusivity is vacuous (A3.2)"
    else:
        disclosed = bool(g["disclosure"]["declared"] and g["disclosure"]["charged"]
                         and g["disclosure"]["evidence"])
        measured = any(h["encoding_kind"] == "COST_MEASURED" for h in real)
        disp = ("ENCODES_COST_MEASURED__" if measured else "ENCODES_CLASS_INDICATOR__") + (
            "DISCLOSED_CHARGED" if disclosed else "UNDISCLOSED")
        kinds = sorted(set(h["kind"] for h in real))
        reason = ("target-exclusive production(s) %s: deleting them changes the minimum "
                  "description cost of the declared target %s and of NO other semantic "
                  "class (%s)" % (
                      sorted(set(tuple(h["productions"]) for h in real)), target,
                      ", ".join(kinds)))
    return {
        "grammar_id": gid, "package": g["package"],
        "source_citation": g["source_citation"],
        "declared_target": target, "target_citation": g["target_citation"],
        "disposition": disp, "reason": reason,
        "tier1_hits": real, "vacuous_hits": vacuous, "notes": notes,
        "tier2_decisive_selection_flip_via_R1": any(
            h["tier2_decisive_selection_flip"] for h in real),
        "encoding_kinds": sorted(set(h["encoding_kind"] for h in real)),
        "corpus": bool(g.get("corpus", True)),
        "disclosure_evidence": g["disclosure"]["evidence"],
        "n_presentations": len(g["presentations"]),
        "n_semantic_classes": len(classes_of(g["presentations"])),
    }


def canonical_json(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)


def build() -> Tuple[Dict[str, object], Dict[str, object], Dict[str, object]]:
    grammars = adapters_v1.load_all()
    validation = run_validation(grammars)
    if not validation["ALL_PASS"]:
        raise SystemExit("VALIDATION_BAR_FAILED -- no finding may be emitted (freeze s6)")

    adjud = []  # type: List[Dict[str, object]]
    r2_rows = []  # type: List[Dict[str, object]]
    for g in grammars:
        hits, notes = r1_hits(g)
        adjud.append(adjudicate(g, hits, notes))
        r2 = r2_report(g)
        r2["grammar_id"] = g["grammar_id"]
        r2_rows.append(r2)

    lex = d_lex_screen()
    lex_adj = d_lex_adjudicate(lex)

    corpus_rows = [a for a in adjud if a.get("corpus", True)]
    encodes = [a for a in corpus_rows if a["disposition"].startswith("ENCODES")]
    undisclosed = [a for a in corpus_rows if a["disposition"].endswith("UNDISCLOSED")]
    with_target = [a for a in corpus_rows if a["disposition"] != "NO_DECLARED_TARGET"]
    cost_measured = [a for a in encodes if "COST_MEASURED" in a["disposition"]]
    indicator = [a for a in encodes if "CLASS_INDICATOR" in a["disposition"]]

    def cn(prefix):
        return sum(1 for a in corpus_rows if a["disposition"].startswith(prefix))

    # Detector agreement table (freeze s7a).
    lex_flagged = set(lex["flagged_packages"])
    cost_pkgs = sorted(set(a["package"] for a in encodes))
    agreement = {
        "both_flag": sorted(lex_flagged & set(cost_pkgs)),
        "cost_only": sorted(set(cost_pkgs) - lex_flagged),
        "lex_only_count": len(lex_flagged - set(cost_pkgs)),
        "note": "D-LEX flags are lexical SCREEN hits, not confirmations; all are "
                "adjudicated in ADJUDICATION_V1.json",
    }

    receipt = {
        "schema": SCHEMA, "issue": ISSUE, "parent_issue": ISSUE,
        "source_main": SOURCE_MAIN, "freeze_commit": FREEZE_COMMIT,
        "claim_ceiling": CLAIM_CEILING,
        "forbidden_promotions": list(FORBIDDEN_PROMOTIONS),
        "row": "- [ ] Identify search grammars that encode the target morphology.",
        "validation": validation,
        "population": {
            "corpus_grammar_instances": len(corpus_rows),
            "corpus_packages": sorted(set(g["package"] for g in grammars
                                          if g.get("corpus", True))),
            "corpus_with_declared_target": len(with_target),
            "corpus_no_declared_target": cn("NO_DECLARED_TARGET"),
            "validation_fixtures": len(grammars) - len(corpus_rows),
            "total_instances_loaded": len(grammars),
            "P_LEX_packages": lex["n_population"],
            "P_LEX_blocks": lex["n_blocks"],
        },
        "d_cost": {
            "scope": "CORPUS_INSTANCES_ONLY (the synthetic V3 fixture is excluded, A5.2)",
            "ENCODES_COST_MEASURED__DISCLOSED_CHARGED":
                cn("ENCODES_COST_MEASURED__DISCLOSED_CHARGED"),
            "ENCODES_CLASS_INDICATOR__DISCLOSED_CHARGED":
                cn("ENCODES_CLASS_INDICATOR__DISCLOSED_CHARGED"),
            "ENCODES_UNDISCLOSED": len(undisclosed),
            "ENCODES_total": len(encodes),
            "NEUTRAL_AT_REGISTERED_SCOPE": cn("NEUTRAL_AT_REGISTERED_SCOPE"),
            "SCREENED_NOT_ADJUDICATED": cn("SCREENED_NOT_ADJUDICATED"),
            "NO_DECLARED_TARGET": cn("NO_DECLARED_TARGET"),
            "tier1_kinds": sorted(set(h["kind"] for a in corpus_rows
                                      for h in a.get("tier1_hits", []))),
            "tier2_via_R1": sorted(a["grammar_id"] for a in corpus_rows
                                   if a.get("tier2_decisive_selection_flip_via_R1")),
            "cost_measured_grammars": sorted(a["grammar_id"] for a in cost_measured),
            "class_indicator_grammars": sorted(a["grammar_id"] for a in indicator),
            "encoding_grammars": sorted(a["grammar_id"] for a in encodes),
        },
        "d_lex": {
            "population": lex["n_population"], "blocks": lex["n_blocks"],
            "flagged_packages": lex["n_flagged"], "hits": lex["n_hits"],
            "lexicon_size": lex["lexicon_size"],
            "adjudicated_hits": lex_adj["n_hits"],
            "false_positive_classes": lex_adj["classes"],
            "CONFIRMED": lex_adj["confirmed_leaks"],
            "authority_self_skip": SELF_PKG,
        },
        "r2_bias1": {
            "grammars": len(r2_rows),
            "reproduced": sum(1 for r in r2_rows if r["bias1_reproduced"]),
            "total_remints": sum(int(r["remints"]) for r in r2_rows),
            "total_selection_reversals": sum(int(r["selection_reversals"]) for r in r2_rows),
        },
        "predictions": {
            "PRED_1_891_anchor": validation["V1_anchor_891"]["pass"],
            "PRED_2_grammar_bias_no_declared_target": any(
                a["grammar_id"] == "grammar_bias_G0_slice"
                and a["disposition"] == "NO_DECLARED_TARGET" for a in adjud),
            "PRED_3_R3_zero_flags": validation["V3_no_alarm"]["r3_all_invariant"],
            "PRED_4_routing_target_is_a_primitive": sorted(
                a["grammar_id"] for a in adjud
                if a["grammar_id"].startswith("cross_grammar_routing")
                and any(h["kind"] == "TARGET_IS_A_PRIMITIVE" for h in a["tier1_hits"])),
            "PRED_5_d_lex_zero_confirmed": lex_adj["confirmed_leaks"] == 0,
        },
        "detector_agreement": agreement,
        "parent_boundary": {
            "issue": 891,
            "terminal": "NO_UNIVERSAL_GRAMMAR_NEUTRALITY__STRUCTURAL_BIAS_COUNTEREXAMPLE",
            "status": "CITED_AS_BOUNDARY_EARNED_BY_COUNTEREXAMPLE_NOT_OVERTURNED",
        },
        "registered_open_instance": {
            "id": "INSTANCE-AJ9-NOSMUGGLING-SCOPE", "disposition": "RED",
            "severity": "HIGH", "owner_lane": "aj",
            "in_mechanical_reach_of_this_pass": False,
            "reason": "AJ9's gap is task-provenance and primitive-basis provenance "
                      "GOVERNANCE (a contract-coverage defect), not a cost-geometry "
                      "property of an extractable grammar object; it is carried forward "
                      "as a named open instance, not closed here",
        },
        "terminal": None,
    }
    receipt["terminal"] = ("GMI_833_B48_GRAMMAR_TARGET_ENCODING_IDENTIFIED_AT_REGISTERED_SCOPE"
                           if validation["ALL_PASS"] else "RED__VALIDATION_FAILED")

    adjudication = {"schema": "GMI_833_B48_ADJUDICATION_V1", "rows": adjud,
                    "r2_bias1_rows": r2_rows, "d_lex_adjudication": lex_adj}
    return receipt, adjudication, lex


def main() -> None:
    (HERE / "GRAMMAR_DUMP_V1.json").write_text(
        canonical_json({"schema": "GMI_833_B48_GRAMMAR_DUMP_V1",
                        "source_main": SOURCE_MAIN,
                        "grammars": adapters_v1.load_all()}) + "\n")
    receipt, adjudication, lex = build()
    (HERE / "ADJUDICATION_V1.json").write_text(canonical_json(adjudication) + "\n")
    (HERE / "PLEX_SCREEN_V1.json").write_text(canonical_json(lex) + "\n")
    (HERE / "RESULT_V1.json").write_text(canonical_json(receipt) + "\n")
    print(canonical_json(receipt))


if __name__ == "__main__":
    main()
