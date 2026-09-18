#!/usr/bin/env python3
"""Independent oracle for `gmi-833-grammar-morphology-encoding-v1` (freeze section 7c).

Recomputes mu, dep, argmin, the Tier-1/Tier-2 verdicts and the per-instance dispositions
from the frozen grammar dump `GRAMMAR_DUMP_V1.json`, WITHOUT importing
`grammar_morphology_encoding_v1` or `adapters_v1`, and with deliberately different
algorithms:

  * `mu` by full sort of a class's cost list and taking element 0 (never a running min);
  * deletion by index-set difference over a precomputed production->presentation-index
    incidence map (never a per-presentation leaf filter);
  * `argmin` by building the complete cost->classes inverse map and reading its smallest
    key (never a min-then-filter pass);
  * `dep` by symmetric-difference of (class, mu) pair SETS (never a per-class comparison).

Run:  python3 -I -B independent_oracle_v1.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DUMP = HERE / "GRAMMAR_DUMP_V1.json"
SCHEMA = "GMI833GrammarMorphologyEncodingOracleV1"


def mu_sorted(pres, sem):
    costs = sorted([int(p["cost"]) for p in pres if p["sem"] == sem])
    return costs[0] if costs else None


def mu_pairs(pres, universe):
    return frozenset((s, mu_sorted(pres, s)) for s in universe)


def argmin_inverse(pres, universe):
    inv = {}
    for s in universe:
        v = mu_sorted(pres, s)
        if v is None:
            continue
        inv.setdefault(v, set()).add(s)
    if not inv:
        return frozenset()
    return frozenset(inv[sorted(inv)[0]])


def incidence(pres):
    """production -> set of presentation INDICES."""
    inc = {}
    for i, p in enumerate(pres):
        for q in p["leaves"]:
            inc.setdefault(q, set()).add(i)
    return inc


def delete_by_index(pres, inc, qs):
    drop = set()
    for q in qs:
        drop |= inc.get(q, set())
    keep = [i for i in range(len(pres)) if i not in drop]
    return [pres[i] for i in keep], len(drop)


def probe(pres, universe, inc, target, qs, via):
    base_pairs = mu_pairs(pres, universe)
    base_mu = dict(base_pairs)
    if base_mu.get(target) is None:
        return None
    kept, n_drop = delete_by_index(pres, inc, qs)
    after_pairs = mu_pairs(kept, universe)
    after_mu = dict(after_pairs)
    changed = frozenset(s for s, _v in (base_pairs ^ after_pairs))
    if changed != frozenset([target]):
        return None
    mt = after_mu[target]
    if mt is not None and mt <= base_mu[target]:
        return None
    n_target = len([p for p in pres if p["sem"] == target])
    tset = set(qs)
    tgt_rows = [p for p in pres if p["sem"] == target]
    oth_rows = [p for p in pres if p["sem"] != target]
    indicator = (bool(tgt_rows)
                 and len([p for p in tgt_rows if tset & set(p["leaves"])]) == len(tgt_rows)
                 and len([p for p in oth_rows if tset & set(p["leaves"])]) == 0)
    return {
        "encoding_kind": ("PRODUCTION_IS_CLASS_INDICATOR" if indicator
                          else "COST_MEASURED"),
        "indicator_margin": len([p for p in oth_rows if tset & set(p["leaves"])]),
        "via": via, "productions": sorted(qs),
        "kind": "TARGET_IS_A_PRIMITIVE" if mt is None else "TARGET_SPECIFIC_SHORTCUT",
        "mu_target_before": base_mu[target], "mu_target_after": mt,
        "dep": sorted(changed),
        "argmin_before": sorted(argmin_inverse(pres, universe)),
        "argmin_after": sorted(argmin_inverse(kept, universe)),
        "tier2_decisive_selection_flip": (
            argmin_inverse(pres, universe) == frozenset([target])
            and argmin_inverse(kept, universe) != frozenset([target])),
        "n_presentations_using": n_drop,
        "n_target_presentations": n_target,
        "n_semantic_classes": len(universe),
        "UNIQUE_REALIZATION": n_target == 1,
        "SINGLE_CLASS_INSTANCE": len(universe) == 1,
    }


def run(g):
    pres = g["presentations"]
    universe = sorted(set(p["sem"] for p in pres))
    target = g["declared_target"]
    inc = incidence(pres)
    vocab = sorted(inc)
    notes, hits = [], []
    if target is None:
        notes.append("R1_NOT_APPLICABLE:NO_DECLARED_TARGET")
    else:
        if len(vocab) < 2:
            notes.append("R1_NOT_APPLICABLE:"
                         + ("NO_PRODUCTION_STRUCTURE" if not vocab
                            else "NUMERIC_PARAMETER_SPACE"))
        else:
            for q in vocab:
                h = probe(pres, universe, inc, target, [q], "R1a")
                if h is not None:
                    hits.append(h)
        comps = sorted(g.get("composites") or [])
        if not comps:
            notes.append("R1_NOT_APPLICABLE:NO_COMPOSITE_PRODUCTIONS")
        else:
            h = probe(pres, universe, inc, target, comps, "R1b")
            if h is not None:
                hits.append(h)

    real = [h for h in hits if not h["SINGLE_CLASS_INSTANCE"]]
    blocking = [n for n in notes if n in ("R1_NOT_APPLICABLE:NO_PRODUCTION_STRUCTURE",
                                          "R1_NOT_APPLICABLE:NUMERIC_PARAMETER_SPACE")]
    if target is None:
        disp = "NO_DECLARED_TARGET"
    elif not real and blocking:
        disp = "SCREENED_NOT_ADJUDICATED:" + blocking[0].split(":", 1)[1]
    elif not real:
        disp = ("SCREENED_NOT_ADJUDICATED:VACUOUS_EXCLUSIVITY_SINGLE_CLASS"
                if hits else "NEUTRAL_AT_REGISTERED_SCOPE")
    else:
        d = g["disclosure"]
        measured = len([h for h in real if h["encoding_kind"] == "COST_MEASURED"]) > 0
        disp = ("ENCODES_COST_MEASURED__" if measured else "ENCODES_CLASS_INDICATOR__") + (
            "DISCLOSED_CHARGED" if (d["declared"] and d["charged"] and d["evidence"])
            else "UNDISCLOSED")
    return {
        "grammar_id": g["grammar_id"], "disposition": disp,
        "corpus": bool(g.get("corpus", True)),
        "encoding_kinds": sorted(set(h["encoding_kind"] for h in real)),
        "n_tier1_hits": len(real),
        "tier1_kinds": sorted(set(h["kind"] for h in real)),
        "tier2_decisive_selection_flip_via_R1": any(
            h["tier2_decisive_selection_flip"] for h in real),
        "mu_target": mu_sorted(pres, target) if target else None,
        "argmin": sorted(argmin_inverse(pres, universe)),
        "n_presentations": len(pres), "n_semantic_classes": len(universe),
        "notes": sorted(notes),
        "hits": sorted(real, key=lambda h: (h["via"], tuple(h["productions"]))),
    }


def main() -> None:
    dump = json.loads(DUMP.read_text())
    rows = [run(g) for g in dump["grammars"]]
    rows.sort(key=lambda r: r["grammar_id"])
    counts = {}
    for r in rows:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
    out = {
        "schema": SCHEMA,
        "source_main": dump["source_main"],
        "grammar_instances": len(rows),
        "dispositions": counts,
        "encoding_grammars": sorted(r["grammar_id"] for r in rows
                                    if r["disposition"].startswith("ENCODES")),
        "tier2_via_R1": sorted(r["grammar_id"] for r in rows
                               if r["tier2_decisive_selection_flip_via_R1"]),
        "rows": rows,
    }
    text = json.dumps(out, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    (HERE / "ORACLE_RESULT_V1.json").write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
