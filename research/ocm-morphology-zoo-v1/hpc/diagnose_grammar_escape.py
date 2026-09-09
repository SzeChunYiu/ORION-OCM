"""UNSCORED diagnostic (post-amend-5, no statuses, no scoring effect):

WHY: the amend-5 gated D3d arm reached own-axis recovery 24/83 = 0.289157,
ABOVE the GATE-CEILING "structural ceiling" 21/83 = 0.253012 computed as the
per-cell max dev over the enumerated census.  Deterministic evaluation makes
that impossible for census-member genomes — so archive elites must ESCAPE the
enumerated grammar.  This diagnostic quantifies the escape MECHANICALLY over
the frozen archives (grammar-membership check only, no re-evaluation):

  enumerate_census() varies F_arch / extras / T / Pi / L / R / K with
  DEFAULT thetas inside CENSUS_BOUND_V1.  morphology/mutations.mutate draws
  families from the FULL vocabularies (FIELD_FAMILIES etc.), can add units
  outside CENSUS_BOUND_V1["extra_units"] (fsm_controller,
  procedural_memory, local_executive), and perturbs thetas (a continuous
  dimension the census never varies).  The searched space is therefore a
  STRICT SUPERSET of the enumerated census; "recovery vs census" remains a
  well-defined coverage measure against a fixed reference, but census
  per-cell maxima are NOT ceilings on the searched space (and "best within
  bound" is the best of the default-theta subset only).

Emits results/GRAMMAR_ESCAPE_DIAGNOSTIC.json (tool-stamped, input digests
embedded; UNSCORED — it changes no terminal, no status, no receipt).

Usage: python3 hpc/diagnose_grammar_escape.py <capsule_root>
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import sys
import time

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)

from morphology.direct_genome import CENSUS_BOUND_V1, DEFAULT_THETA  # noqa: E402
from morphology.schema import OCMMorphologyGenomeV1  # noqa: E402

POOL = set(CENSUS_BOUND_V1["extra_units"])
IN_UNITS = POOL | {"fact_relation"}


def escape_reasons(gj: dict) -> list:
    """Grammar-membership vs enumerate_census (pure field checks, no eval)."""
    why = []
    if gj["F_arch"] not in CENSUS_BOUND_V1["F_arch"]:
        why.append("F_arch")
    if gj["T_family"] not in CENSUS_BOUND_V1["T_family"]:
        why.append("T_family")
    if gj["Pi_arch"] not in CENSUS_BOUND_V1["Pi_arch"]:
        why.append("Pi_arch")
    if gj["L"] not in CENSUS_BOUND_V1["L"]:
        why.append("L")
    if gj["R"] not in CENSUS_BOUND_V1["R"]:
        why.append("R")
    if gj["K"] not in CENSUS_BOUND_V1["K"]:
        why.append("K")
    units = [u["unit_type"] for u in gj["U"]]
    if any(u not in IN_UNITS for u in units):
        why.append("units")
    n_extras = len([u for u in units if u != "fact_relation"])
    if n_extras > CENSUS_BOUND_V1["max_extra_units"]:
        why.append("max_extra_units")
    theta = gj.get("theta", {})
    if any(abs(float(v) - float(DEFAULT_THETA.get(k, v))) > 1e-9
           for k, v in theta.items()):
        why.append("theta")
    return why


def scan(pattern: str) -> dict:
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "archives", pattern))):
        recs = json.load(open(path))
        n, esc, reasons, devs_in, devs_out = 0, 0, {}, [], []
        for r in recs:
            n += 1
            why = escape_reasons(r["genome"])
            if why:
                esc += 1
                devs_out.append(r["dev_score"])
                for w in why:
                    reasons[w] = reasons.get(w, 0) + 1
            else:
                devs_in.append(r["dev_score"])
        if n:
            out[os.path.basename(path)] = {
                "n_elites": n,
                "n_escape_census_grammar": esc,
                "escape_fraction": round(esc / n, 6),
                "escape_reasons_counts": reasons,
                "best_dev_in_grammar": max(devs_in) if devs_in else None,
                "best_dev_out_of_grammar": max(devs_out) if devs_out else None,
            }
    return out


def main():
    qda5 = scan("QDA5_*_archive.json")
    qda3 = scan("QDA3_*_archive.json")
    agg_esc = [v["n_escape_census_grammar"] for v in qda5.values()]
    tot = [v["n_elites"] for v in qda5.values()]
    out = {
        "diagnostic_id": "GRAMMAR_ESCAPE_DIAGNOSTIC_V1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "created_by": "hpc/diagnose_grammar_escape.py (tool-stamped)",
        "scored": False,
        "trigger": "amend-5 G01_gate_D3d own-axis 24/83 = 0.289157 exceeded the "
                   "GATE-CEILING per-cell-max 'ceiling' 21/83 = 0.253012 — "
                   "impossible for census-member genomes under deterministic "
                   "evaluation, so elites escape the enumerated grammar",
        "root_cause": "morphology/mutations.py mutate(): family draws use the "
                      "FULL vocabularies (FIELD_FAMILIES/TOPOLOGY_FAMILIES/...), "
                      "unit additions can use fsm_controller/procedural_memory/"
                      "local_executive (outside CENSUS_BOUND_V1['extra_units']), "
                      "and theta mutations perturb a continuous dimension "
                      "enumerate_census() never varies (all census genomes carry "
                      "DEFAULT_THETA).  random_genome stays inside the grammar; "
                      "only mutation/crossover escape it.",
        "semantics": "GATE-CEILING ceil_* values are census-subset maxima "
                     "(per-cell max dev over the 28,584 feasible default-theta "
                     "census genomes), NOT bounds on the searched space; "
                     "'recovery vs census' remains coverage against a fixed "
                     "reference set.  Amend-5 terminal rules reference only "
                     "own-axis recovery and best_dev bars, never ceilings, so "
                     "the verdict is unaffected; the ceiling-premise wording of "
                     "the bar-selection rule is corrected here.",
        "amend5_totals": {
            "archives": len(qda5),
            "elites_total": sum(tot),
            "escape_total": sum(agg_esc),
            "escape_fraction": round(sum(agg_esc) / sum(tot), 6) if tot else None,
        },
        "per_archive_QDA5": qda5,
        "per_archive_QDA3": qda3,
        "input_digests": {
            "mutations_py": hashlib.sha256(
                open(os.path.join(ROOT, "morphology", "mutations.py"), "rb")
                .read()).hexdigest()[:16],
            "direct_genome_py": hashlib.sha256(
                open(os.path.join(ROOT, "morphology", "direct_genome.py"), "rb")
                .read()).hexdigest()[:16],
        },
    }
    path = os.path.join(ROOT, "results", "GRAMMAR_ESCAPE_DIAGNOSTIC.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"diagnostic": "OK", "path": path,
                      "amend5_escape_fraction":
                          out["amend5_totals"]["escape_fraction"],
                      "archives": out["amend5_totals"]["archives"]}))


if __name__ == "__main__":
    main()
