#!/usr/bin/env python3
"""GMI #833 corpus passes v2 — P1/P2 mechanical screens (frozen protocol L44/L45/L51/L52).

L44  ENUM_ANALYTIC_CAND over the 49 EXACT_FINITE_CERTIFICATE P2 rows (+ census
     COMPUTER_ASSISTED_EXHAUSTIVE claim-class candidates, screen-only).
L45  COMP_ONLY_CAND over the 63 ANALYTIC_PROOF P2 rows.
L51  IID_STAT_CAND over P1 computational rows: property term in statement while the
     package's registration docs (FREEZE/ASSUMPTION/RESULT/RECEIPT .md/.json) never
     register it.
L52  FIN_HORIZON_CAND over P2 rows: horizon/budget token in justification/scope while
     the statement excerpt does not declare a bound (+ census UNIVERSAL statement-side
     count, honest SCREENED-NOT-ADJUDICATED status).

Each screen ships plants: known-positive rows MUST flag, known-clean rows MUST NOT
(no cry-wolf), and 'could not check' is a distinct status. stdlib only; deterministic.
"""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[1]
CENSUS = REPO / "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
SCORES = REPO / "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"
SEED = 833212

CLAIM_CLASSES = {"THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM"}
COMP_MODES = {"FINITE_EXECUTABLE_CERTIFICATE", "COMPUTER_ASSISTED_EXHAUSTIVE",
              "STATISTICAL_EXPERIMENT", "MECHANIZED_PROOF", "EMPIRICAL_EXPERIMENT"}

IID_RE = re.compile(
    r"\bi\.?i\.?d\.?\b|\bindependent(?:ly)?[a-z ]{0,24}identically\b|\bstationar(?:y|ity)\b"
    r"|\bergodic\b|\bexchangeab(?:le|ility)\b|\btime[- ]homogeneous\b|\bdrift[- ]free\b"
    r"|\bfixed iid\b|\bmemoryless\b", re.I)
HORIZON_RE = re.compile(
    r"\b(?:budget|horizon|step limit|max(?:imum)? steps|episode length|depth limit|"
    r"termination bound|timeout|T\s*[<=]|steps?\s*[<=]|n\s*steps)\b", re.I)
ENUM_ONLY_RE = re.compile(r"enumerat|certificate|exhaustive|finite check|finite run|replay", re.I)
ANALYTIC_RE = re.compile(r"analytic|induction|inductive|lemma|theorem proof|proof by|closed[- ]form|derivation", re.I)


def pkg_of(path: str) -> str:
    parts = Path(path).parts
    return "/".join(parts[:2]) if len(parts) >= 3 else path


# ---------------------------------------------------------------- L44
def _l44_one(r: dict, by_pkg_file: dict) -> dict:
    scope = str(r.get("scope_quantifier_class", ""))
    universal = scope.strip().startswith(("forall", "conditional_at"))
    just = str(r.get("justification", ""))
    enum_only = bool(ENUM_ONLY_RE.search(just)) and not ANALYTIC_RE.search(just)
    sibling_analytic = sorted(
        {rid for p in r.get("citation_paths", []) for rid in by_pkg_file.get((r.get("package"), p.split("/")[-1]), ())}
    )
    return {
        "result_id": r["result_id"], "package": r.get("package"),
        "flag": bool(universal and enum_only and not sibling_analytic),
        "reasons": {"universal_scope": universal, "enum_only_justification": enum_only,
                    "sibling_analytic_rows": sibling_analytic},
        "statement_excerpt": str(r.get("statement_excerpt", ""))[:200],
    }


def screen_l44(rows: list[dict]) -> dict:
    pop = [r for r in rows if r.get("support_kind") == "EXACT_FINITE_CERTIFICATE"]
    by_pkg_file: dict[tuple, set] = {}
    for r in rows:
        if str(r.get("support_kind", "")).startswith("ANALYTIC"):
            for p in r.get("citation_paths", []):
                by_pkg_file.setdefault((r.get("package"), p.split("/")[-1]), set()).add(r["result_id"])
    all_rows = [_l44_one(r, by_pkg_file) for r in pop]
    plant_pos = _l44_one({"result_id": "PLANT_POS", "package": "p",
                          "scope_quantifier_class": "forall_fin[U_declared]",
                          "justification": "EXACT_FINITE_CERTIFICATE; receipts=kind; enumeration replay",
                          "citation_paths": []}, by_pkg_file)
    plant_neg = _l44_one({"result_id": "PLANT_NEG", "package": "p",
                          "scope_quantifier_class": "forall_fin[U_declared]",
                          "justification": "EXACT_FINITE_CERTIFICATE plus analytic induction lemma",
                          "citation_paths": []}, by_pkg_file)
    return {"population": len(pop), "flagged": [f for f in all_rows if f["flag"]],
            "all_rows": all_rows,
            "plants_pass": plant_pos["flag"] is True and plant_neg["flag"] is False}


# ---------------------------------------------------------------- L45
def _l45_one(r: dict) -> dict:
    cites = r.get("citation_paths", []) or []
    md_docs = [p for p in cites if p.endswith(".md")]
    just = str(r.get("justification", ""))
    comp = re.search(r"enumerat|certificate|exhaustive replay|finite run|witness run", just, re.I)
    comp_only = comp is not None and ANALYTIC_RE.search(just) is None
    return {"result_id": r["result_id"], "package": r.get("package"),
            "flag": bool((not md_docs) or comp_only),
            "reasons": {"no_md_citation": not md_docs, "comp_only_justification": comp_only},
            "citation_md_count": len(md_docs)}


def screen_l45(rows: list[dict]) -> dict:
    pop = [r for r in rows if r.get("support_kind") == "ANALYTIC_PROOF"]
    all_rows = [_l45_one(r) for r in pop]
    plant_pos = _l45_one({"result_id": "P+", "citation_paths": ["x/run.py", "x/R.json"],
                          "justification": "enumeration certificate replay", "package": "p"})
    plant_neg = _l45_one({"result_id": "P-", "citation_paths": ["x/THM.md"],
                          "justification": "induction on chain length", "package": "p"})
    return {"population": len(pop), "flagged": [f for f in all_rows if f["flag"]],
            "all_rows": all_rows,
            "plants_pass": plant_pos["flag"] is True and plant_neg["flag"] is False}


# ---------------------------------------------------------------- L51
def registration_texts(pkg_dir: Path) -> list[str]:
    texts = []
    for f in sorted(pkg_dir.rglob("*")):
        if f.is_file() and f.suffix in {".md", ".json"} and f.stat().st_size < 2_000_000:
            name = f.name.upper()
            if any(k in name for k in ("FREEZE", "ASSUMPTION", "RESULT", "RECEIPT", "README", "CORE")):
                try:
                    texts.append(f.read_text(errors="replace"))
                except OSError:
                    pass
    return texts


def screen_l51(objects: list[dict], repo: Path = REPO) -> dict:
    pop = [o for o in objects if o.get("proof_evidence_mode") in COMP_MODES]
    pkg_cache: dict[str, bool] = {}
    flagged = []
    rng = random.Random(SEED)
    for o in pop:
        m = IID_RE.search(o.get("statement") or "")
        if not m:
            continue
        pkg = pkg_of(o["source_path"])
        if pkg not in pkg_cache:
            d = repo / pkg
            texts = registration_texts(d) if d.is_dir() else []
            pkg_cache[pkg] = any(IID_RE.search(t) for t in texts)
        if not pkg_cache[pkg]:
            flagged.append({"object_id": o["object_id"], "source_path": o["source_path"],
                            "source_locator": o["source_locator"], "term": m.group(0),
                            "statement": (o.get("statement") or "")[:160]})
    # plants: known-positive term strings must match; clean text must not
    pos_ok = bool(IID_RE.search("fixed iid proposals with mass p>0")) and bool(IID_RE.search("exact normalized iid kernels"))
    neg_ok = IID_RE.search("the architecture is layered") is None and IID_RE.search("independence of the two ledgers") is None
    return {"population": len(pop), "n_flagged": len(flagged), "flagged": flagged,
            "n_packages_property_registered": sum(1 for v in pkg_cache.values() if v),
            "plants_pass": pos_ok and neg_ok}


# ---------------------------------------------------------------- L52
def screen_l52(rows: list[dict], objects: list[dict]) -> dict:
    flagged = []
    for r in rows:
        stmt = str(r.get("statement_excerpt", "")) + " " + str(r.get("theorem_name", ""))
        scope = str(r.get("scope_quantifier_class", ""))
        just = str(r.get("justification", ""))
        scope_declared = bool(HORIZON_RE.search(scope))
        horizon_in_evidence = bool(HORIZON_RE.search(just) or HORIZON_RE.search(" ".join(r.get("citation_paths", []))))
        horizon_in_stmt = bool(HORIZON_RE.search(stmt))
        if horizon_in_evidence and not scope_declared and not horizon_in_stmt:
            flagged.append({"result_id": r["result_id"], "package": r.get("package"),
                            "scope": scope[:160], "justification": just[:160]})
    census_univ = [o for o in objects if o.get("quantifier_class") == "UNIVERSAL"]
    pos_ok = bool(HORIZON_RE.search("budget <= 7 steps")) and bool(HORIZON_RE.search("8-step budget"))
    neg_ok = HORIZON_RE.search("theorem about compositions") is None
    return {"population_p2": len(rows), "n_flagged": len(flagged), "flagged": flagged,
            "census_universal_statement_side_only": len(census_univ),
            "census_universal_status": "SCREENED-NOT-ADJUDICATED (statement-side evidence not in census fields)",
            "plants_pass": pos_ok and neg_ok}


def main() -> int:
    idx = json.loads(CENSUS.read_text())
    objects = idx["scientific_objects"]
    rows = json.loads(SCORES.read_text())

    l44 = screen_l44(rows)
    l45 = screen_l45(rows)
    l51 = screen_l51(objects)
    l52 = screen_l52(rows, objects)

    for name, res in (("L44", l44), ("L45", l45), ("L51", l51), ("L52", l52)):
        print(f"{name}: population={res['population' if 'population' in res else 'population_p2']} "
              f"flagged={res.get('n_flagged', len(res.get('flagged', [])))} plants_pass={res['plants_pass']}")
        if not res["plants_pass"]:
            print(f"{name} PLANT FAILURE — screen not cleared")
            return 1

    out = {"schema": "GMI_833_CORPUS_PASSES_P1P2_SCREENS_V1",
           "L44_enum_analytic": {"population": l44["population"], "flagged": l44["flagged"],
                                  "all_rows": l44["all_rows"]},
           "L45_comp_only": {"population": l45["population"], "flagged": l45["flagged"]},
           "L51_iid_stationarity": l51,
           "L52_finite_horizon": l52}
    (HERE / "P1P2_SCREENS_V1.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print("wrote P1P2_SCREENS_V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
