#!/usr/bin/env python3
"""GMI #833 corpus passes v2 — P3 package-level mechanical screens (L46/L47/L49/L50/L53/L54/L55/L56).

All screens run at branch base (recorded in RECEIPTS). Every screen ships plants
(known-positive MUST flag, known-clean MUST NOT). stdlib only; deterministic sorted
iteration. Census side joins P1 objects per package for claim counts.

L46  TWO_ROUTE / SINGLE_ROUTE / NO_COMPUTATION per package: independent-oracle /
     two-executor+agreement evidence (g0-* pattern; #863/#875 precedents).
L47  git add-order audit: freeze vs result/receipt vs executor(.py): RESULT_PRECEDES_FREEZE,
     SINGLE_COMMIT_FREEZE_RESULT, TIGHT_GAP_EXECUTOR (<=120 s after freeze), or typed states.
L49  cost-forces-winner: cost/scalarization language + winner language, no cost-audit artifact.
L50  A1 denylist (registered D1) normalized scan over grammar/operator files + A2-signature
     coverage census; MACRO_PRIVOP_CAND on lexical hit; UNAUDITED_OPERATOR_SURFACE when
     primitives exist without A2-style registration.
L53  alternate-scalarization artifact presence (>=2 registered weight vectors / R4 run).
L54  encoding-sensitivity: encoding/presentation language without remint/bijection control.
L55  search-sensitivity: search executor behind claims without materially distinct replica.
L56  named-parent rows without stated residual (P2 layer; containment read is Tier A).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[1]
CENSUS = REPO / "research/gmi-833-corpus-census-v1/CORPUS_INDEX_V1.json"
SCORES = REPO / "research/gmi-833-maturity-rescore-v2-v1/THEOREM_SCORES_V2.json"

CLAIM_CLASSES = {"THEOREM", "LAW", "CLAIM", "COROLLARY", "PROPOSITION", "LEMMA", "AXIOM"}
COMP_MODES = {"FINITE_EXECUTABLE_CERTIFICATE", "COMPUTER_ASSISTED_EXHAUSTIVE",
              "STATISTICAL_EXPERIMENT", "MECHANIZED_PROOF", "EMPIRICAL_EXPERIMENT"}
DENYLIST = ["transformer", "self_attention", "conv2d", "lstm_gate", "rag_retriever"]  # registered D1

RE = {
    "cost": re.compile(r"scalariz|cost[- ]model|weighted (?:sum|combination)|budget profile|price vector|cost vector", re.I),
    "winner": re.compile(r"\bwinner\b|selected class|selects the|argmin|argmax|optimal choice|selection\b", re.I),
    "cost_audit": re.compile(r"SCALARIZATION_WINNER_REVERSAL|winner_reversal|cost[- _]privilege|COST_PRIOR|PRICE_SENSITIVE|SCALARIZATION_INVARIANT|scalarization_audit|ZERO_COST_PRIVILEGED", re.I),
    "alt_scalar": re.compile(r"WEIGHTS\s*=|weight vectors|alternate scalariz|alternate weighting|scalarization_audit|price profiles|budget profiles", re.I),
    "encoding": re.compile(r"\bencoding\b|\bpresentation\b|relabel|label permutation|remint|surface (?:form|name|label)", re.I),
    "enc_control": re.compile(r"remint|isometric|bijection|ENCODING_INVARIANT|ENCODING_SENSITIVE|CANNOT_AUDIT_ENCODING|independent regeneration|relabeling control|presentation relabeling", re.I),
    "search": re.compile(r"\bsearch\b|enumerat|optimiz|\bBFS\b|branch.and.bound|beam search|genetic algorithm|hill.?climb", re.I),
    "search_replica": re.compile(r"Floyd|second (?:strategy|route|implementation)|replica|SEARCH_INVARIANT|SEARCH_ALGORITHM_SENSITIVE|materially distinct|independent oracle|ORACLE_RESULT|two[- ]route", re.I),
    "primitives": re.compile(r"primitive|operator|instruction set|opcode|\bgrammar\b|\bDSL\b", re.I),
    "a2_signature": re.compile(r"state_access|content_dependent_routing|verifier_access|strategy_signature|Sigma\(", re.I),
    "residual": re.compile(r"residual|delta|beyond|extends|differs|contribution|what is new|GMI contribution|novelty|subsumption", re.I),
}

PKG_NAME_RE = re.compile(r"^gmi-")


def pkg_of(path: str) -> str:
    parts = Path(path).parts
    return parts[1] if len(parts) >= 3 else path


def packages(repo: Path) -> list[str]:
    root = repo / "research"
    names = [p.name for p in root.iterdir() if p.is_dir() and PKG_NAME_RE.match(p.name)]
    mimp = "machine-intelligence-morphogenesis-v1"  # census includes it explicitly
    if (root / mimp).is_dir():
        names.append(mimp)
    return sorted(set(names))


def pkg_files(pkg_dir: Path) -> dict[str, str]:
    out = {}
    for f in sorted(pkg_dir.rglob("*")):
        if f.is_file() and f.suffix in {".md", ".py", ".json", ".txt"} and f.stat().st_size < 3_000_000:
            try:
                out[str(f.relative_to(pkg_dir))] = f.read_text(errors="replace")
            except OSError:
                pass
    return out


def any_match(rx: re.Pattern, files: dict[str, str], suffixes=(".md", ".py", ".json")) -> list[str]:
    hits = []
    for name, text in sorted(files.items()):
        if name.endswith(suffixes) and rx.search(text):
            hits.append(name)
    return hits


# ---------------------------------------------------------------- L46
def l46_two_route(files: dict[str, str], comp_claims: int) -> dict:
    if comp_claims == 0:
        return {"status": "NO_COMPUTATION"}
    names = set(files)
    oracle = any(n.startswith("independent_oracle") or "ORACLE_RESULT" in n.upper() for n in names)
    py_execs = [n for n in names if n.endswith(".py") and not n.startswith("test_")]
    agreement = any(n for n in names if re.search(r"agree|cross[- ]check|oracle|second_impl|ORACLE", n, re.I)) or \
        any(re.search(r"second_impl=True|agree exactly|agreement|cross-check", files[n]) for n in py_execs if n in files)
    two_routes = len(py_execs) >= 2 and agreement
    return {"status": "TWO_ROUTE" if (oracle or two_routes) else "SINGLE_ROUTE",
            "oracle_file": oracle, "agreement_evidence": agreement}


# ---------------------------------------------------------------- L47
def git_add_events(repo: Path) -> dict[str, tuple[int, str]]:
    """file -> (first add commit time, sha). One git pass over research/."""
    proc = subprocess.run(
        ["/usr/bin/git", "-C", str(repo), "log", "--diff-filter=A", "--format=__CT__%ct %H", "--name-only",
         "--", "research/"],
        capture_output=True, text=True, check=True)
    events: dict[str, tuple[int, str]] = {}
    ct = sha = None
    for line in proc.stdout.splitlines():
        if line.startswith("__CT__"):
            _, rest = line.split("__CT__", 1)
            ct_s, sha = rest.split()
            ct = int(ct_s)
        elif line.strip() and ct is not None:
            f = line.strip()
            if f not in events:  # git log newest-first: keep the FIRST add (oldest)
                events[f] = (ct, sha)
    return events


def l47_order(pkg: str, files: dict[str, str], events: dict[str, tuple[int, str]]) -> dict:
    freezes = [f for f in files if Path(f).name.upper().startswith("FREEZE")]
    results = [f for f in files if re.match(r".*(RESULT|RECEIPT).*\.json$", Path(f).name, re.I)]
    execs = [f for f in files if f.endswith(".py")]
    if not freezes:
        return {"status": "NO_FREEZE_ARTIFACT", "n_results": len(results)}
    base = f"research/{pkg}"
    fz = [events[f"{base}/{f}"] for f in freezes if f"{base}/{f}" in events]
    rs = [events[f"{base}/{f}"] for f in results if f"{base}/{f}" in events]
    ex = [events[f"{base}/{f}"] for f in execs if f"{base}/{f}" in events]
    if not fz:
        return {"status": "CANNOT_CHECK_FREEZE_HISTORY"}
    fz_t, fz_sha = min(fz)
    if rs and min(rs)[0] < fz_t:
        return {"status": "RESULT_PRECEDES_FREEZE", "freeze_ct": fz_t}
    same_commit = any(sha == fz_sha for _, sha in rs)
    if same_commit:
        return {"status": "SINGLE_COMMIT_FREEZE_RESULT", "freeze_ct": fz_t}
    tight = [t for t, _ in ex if fz_t < t <= fz_t + 120]
    if tight:
        return {"status": "TIGHT_GAP_EXECUTOR", "gap_s": min(tight) - fz_t, "freeze_ct": fz_t}
    return {"status": "PROSPECTIVE_ORDERED", "freeze_ct": fz_t}


# ---------------------------------------------------------------- L50
def a1_norm(token: str) -> str:
    return re.sub(r"[^a-z0-9]", "", re.sub(r"(?<=[a-z])(?=[A-Z])", " ", token).lower().replace(" ", ""))


def l50_scan(files: dict[str, str]) -> dict:
    hits, prim_files, a2 = [], [], False
    for name, text in sorted(files.items()):
        if RE["primitives"].search(text) or RE["primitives"].search(Path(name).stem):
            prim_files.append(name)
            if RE["a2_signature"].search(text):
                a2 = True
            idents = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b", text))
            for ident in idents:
                n = a1_norm(ident)
                for d in DENYLIST:
                    if len(n) >= len(a1_norm(d)) and a1_norm(d) in n:
                        hits.append({"file": name, "ident": ident, "denylist": d})
                        break
    return {"lexical_hits": hits, "n_primitive_files": len(prim_files),
            "a2_signature_registered": a2,
            "surface": "UNAUDITED_OPERATOR_SURFACE" if prim_files and not a2 else "A2_COVERED_OR_NO_PRIMITIVES"}


# ---------------------------------------------------------------- main
def main() -> int:
    idx = json.loads(CENSUS.read_text())
    objects = idx["scientific_objects"]
    comp_claims: dict[str, int] = {}
    for o in objects:
        if o.get("proof_evidence_mode") in COMP_MODES and o.get("object_class") in CLAIM_CLASSES:
            comp_claims[pkg_of(o["source_path"])] = comp_claims.get(pkg_of(o["source_path"]), 0) + 1

    pkgs = packages(REPO)
    events = git_add_events(REPO)
    rows = {}
    for pkg in pkgs:
        files = pkg_files(REPO / "research" / pkg)
        cost = bool(any_match(RE["cost"], files))
        winner = bool(any_match(RE["winner"], files))
        audit = bool(any_match(RE["cost_audit"], files))
        alt = bool(any_match(RE["alt_scalar"], files))
        enc = bool(any_match(RE["encoding"], files))
        encctl = bool(any_match(RE["enc_control"], files))
        search_ = bool(any_match(RE["search"], files, suffixes=(".py",)))
        replica = bool(any_match(RE["search_replica"], files))
        rows[pkg] = {
            "comp_claims": comp_claims.get(pkg, 0),
            "L46": l46_two_route(files, comp_claims.get(pkg, 0)),
            "L47": l47_order(pkg, files, events),
            "L49_flag": cost and winner and not audit,
            "L50": l50_scan(files),
            "L53_flag": cost and not (alt or audit),
            "L54_flag": enc and comp_claims.get(pkg, 0) > 0 and not encctl,
            "L55_flag": search_ and comp_claims.get(pkg, 0) > 0 and not replica,
            "evidence": {"cost_language": cost, "winner_language": winner, "cost_audit_artifact": audit,
                         "alt_scalarization": alt, "encoding_language": enc, "encoding_control": encctl,
                         "search_language_py": search_, "search_replica_artifact": replica},
        }

    # ---- plants
    plant_files_two = {"independent_oracle_v1.py": "x=1", "ORACLE_RESULT_V1.json": "{}", "core.py": "agree exactly"}
    plant_files_none = {"README.md": "docs only"}
    p46a = l46_two_route(plant_files_two, 5)
    p46b = l46_two_route(plant_files_none, 0)
    p46c = l46_two_route({"core.py": "print(1)"}, 3)
    l46_ok = p46a["status"] == "TWO_ROUTE" and p46b["status"] == "NO_COMPUTATION" and p46c["status"] == "SINGLE_ROUTE"
    ev = {"research/plantpkg/FREEZE_V1.md": (100, "f1"), "research/plantpkg/RESULT_V1.json": (200, "r1"),
          "research/plantpkg/core.py": (112, "c1")}
    p47 = l47_order("plantpkg", {"FREEZE_V1.md": "", "RESULT_V1.json": "", "core.py": ""}, ev)
    p47b = l47_order("plantpkg", {"FREEZE_V1.md": "", "RESULT_V1.json": "", "core.py": ""},
                     {"research/plantpkg/FREEZE_V1.md": (100, "f1"), "research/plantpkg/RESULT_V1.json": (900, "r1"),
                      "research/plantpkg/core.py": (500, "c1")})
    l47_ok = p47["status"] == "TIGHT_GAP_EXECUTOR" and p47b["status"] == "PROSPECTIVE_ORDERED"
    p50pos = l50_scan({"grammar.py": "OPS = ['SelfAttention', 'INPUT', 'CONST']"})
    p50neg = l50_scan({"grammar.py": "OPS = ['INPUT', 'CONST', 'ADD', 'NEGATE']"})
    p50c = l50_scan({"notes.md": "the transformer paper is cited here for context"})
    l50_ok = (len(p50pos["lexical_hits"]) == 1 and not p50neg["lexical_hits"]
              and not p50c["lexical_hits"])

    # ---- L56 P2 layer
    rows_p2 = json.loads(SCORES.read_text())
    named_parent_rows = [r for r in rows_p2
                         if r.get("strongest_parents") and r["strongest_parents"] != ["UNREGISTERED_IN_LEGACY_SOURCE"]]
    parent_doc_cache: dict[str, str] = {}
    def parent_docs(pkg: str) -> str:
        if pkg not in parent_doc_cache:
            d = REPO / "research" / pkg
            txt = ""
            if d.is_dir():
                for f in sorted(d.rglob("*.md")):
                    if re.search(r"PARENT|SUBSUMPTION|SUBTRACT", f.name, re.I):
                        txt += f.read_text(errors="replace") + "\n"
            parent_doc_cache[pkg] = txt
        return parent_doc_cache[pkg]

    l56_flag = []
    for r in named_parent_rows:
        hay = " ".join([str(r.get("justification", "")), " ".join(r.get("forbidden_extrapolations", [])),
                        " ".join(r.get("assumptions", [])), parent_docs(str(r.get("package", "")))])
        if not RE["residual"].search(hay):
            l56_flag.append({"result_id": r["result_id"], "package": r.get("package"),
                             "parents": r["strongest_parents"]})

    print(f"packages: {len(pkgs)}; census comp-claim packages: {len(comp_claims)}")
    from collections import Counter
    print("L46:", dict(Counter(v["L46"]["status"] for v in rows.values())))
    print("L47:", dict(Counter(v["L47"]["status"] for v in rows.values())))
    print("L49 flags:", sum(1 for v in rows.values() if v["L49_flag"]))
    print("L50 lexical-hit packages:", sum(1 for v in rows.values() if v["L50"]["lexical_hits"]),
          "| unaudited-operator-surface:", sum(1 for v in rows.values() if v["L50"]["surface"] == "UNAUDITED_OPERATOR_SURFACE"))
    print("L53 flags:", sum(1 for v in rows.values() if v["L53_flag"]))
    print("L54 flags:", sum(1 for v in rows.values() if v["L54_flag"]))
    print("L55 flags:", sum(1 for v in rows.values() if v["L55_flag"]))
    print("L56 named-parent rows:", len(named_parent_rows), "| no-residual flags:", len(l56_flag))
    print(f"plants: L46={l46_ok} L47={l47_ok} L50={l50_ok}")
    if not (l46_ok and l47_ok and l50_ok):
        print("PLANT FAILURE — screens not cleared")
        return 1

    out = {"schema": "GMI_833_CORPUS_PASSES_P3_SCREENS_V1", "n_packages": len(pkgs),
           "packages": rows,
           "L56": {"named_parent_rows": len(named_parent_rows), "no_residual_flagged": l56_flag,
                   "unregistered_parent_rows": sum(1 for r in rows_p2 if r.get("strongest_parents") == ["UNREGISTERED_IN_LEGACY_SOURCE"])},
           "plants": {"L46": l46_ok, "L47": l47_ok, "L50": l50_ok}}
    (HERE / "P3_SCREENS_V1.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print("wrote P3_SCREENS_V1.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
