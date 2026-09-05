"""M2.1 surprise revival study — fan-out defect of the EXTRACT stage on the inherited M2 dev split.

Pre-registered (written before the run; not tuned afterwards):

  Baseline  : the frozen M2 receipt — `results/KSO_M2_SOLVE_RECEIPT_V1.json` — reports
              FOUND_BY_NAVIGATION 38/50 with 12 EXTRACT misses (live request atoms outside G_Q
              because their query activation sits below the uniform background π).
  Attribution: EXTRACT (background model), not NAVIGATE (the walk reaches them; ρ = 0 hides them).
  Lever     : the PROPAGATED surprise model (`ocm.kso.surprise`): compare propagated mass to
              propagated background (restart mass is the prior, not reaction).  The receipt's own
              lever, a seed-count-conditioned background, is a no-op by linearity (lemma checked).
  Expectation: EXTRACT misses fall (ideally to 0) and FOUND_BY_NAVIGATION rises, with
              (i) STORE_EXACT unchanged at 50/50 (the decision is composed from labels),
              (ii) translator invariance unchanged at 50/50 (A/B atomisers give identical seeds),
              (iii) the two-direction hub theorem (KS-T06b) surviving under the new model,
              (iv) no live request atom lost that UNIFORM had found (monotone recovery).
  Failure   : any of (i)–(iv) failing files the lever as NEGATIVE with attribution EXTRACT;
              no second lever is tried in this run.

Runs the frozen harness' own instance preparation (`kso_m2_solve_v1.prepare`) and its frozen
extraction (`reacting_subgraph_exact`) for the UNIFORM arm; the PROPAGATED arm uses the canonical
core on the identical space (`space.from_reference`) with the identical closure rule.  Exact ℚ.
Exit 0 = ran (verdict inside), 1 = a pre-registered guard failed, 2 = CANNOT_CHECK.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

from ocm.historical import load_reference, repository_root
from ocm.kso import navigation as N
from ocm.kso import space as S
from ocm.kso import surprise as SP
from ocm.kso.warrant import CannotCheck

ALPHA = Fraction(1, 3)
BASELINE = "research/orion-machine/results/KSO_M2_SOLVE_RECEIPT_V1.json"


def _canonical(atoms, edges) -> str:
    return json.dumps({"atoms": sorted(atoms), "hyperedges": sorted(edges)}, sort_keys=True)


def reacting_subgraph_model(ks_ref, seed, revoked, model: SP.SurpriseModel):
    """Same closure rule as the frozen `reacting_subgraph_exact`, surprise from the given model."""
    ks = S.from_reference(ks_ref)
    rv = frozenset(revoked)
    act = N.fixed_point(ks, seed, ALPHA, revoked=rv)
    bg = N.fixed_point(ks, N.uniform_seed(ks), ALPHA, revoked=rv)
    rho = SP.surprise(ks, act, bg, seed, ALPHA, model, revoked=rv)
    support = [x for x, v in zip(ks.ids, seed, strict=True) if v > 0]
    closure = N.gated_closure(ks, support, rv)
    atoms = frozenset(x for x in closure if rho[x] > 0 or x in support)
    edges = frozenset(e.edge_id for e in ks.hyperedges if e.warrant.is_live(rv) and e.incident <= atoms)
    return atoms, edges, act


def run(per_family: int = 5) -> dict:
    m2 = load_reference("kso_m2_solve_v1")
    m1 = load_reference("kso_m1_mex1_population_v1")
    kso = load_reference("kso_math_v1")
    gen, model, oracle = m1._mex1()
    root = repository_root()
    baseline = json.loads((root / BASELINE).read_text(encoding="utf-8"))
    base_nav = baseline["G1_exact"]["FOUND_BY_NAVIGATION"]
    base_misses = set(baseline["findings_informational"]["EXTRACT_SURPRISE_MISSES_ONE_HOP_REQUEST_ATOMS"]["ids"])
    pairs = gen.generate_split("dev", "ME-X1-DEV-20260902", {f: per_family for f in model.FAMILIES})
    rows = []
    for inst, exp in pairs:
        w1, _, pop, _ = m2.prepare(inst)
        ks = pop.space
        R = pop.registered_revoked
        specs = m2.read_request_atoms(w1, inst.request)
        amap = ks.atom_map()
        live_req = [s.atom_id for s in specs if kso.profile_live(amap[s.atom_id].profile, R)]
        _, sA = m2.atomize_A(pop, w1, inst)
        _, sB = m2.atomize_B(pop, w1, inst)
        # UNIFORM arm: the frozen harness' own extraction (byte-identical object)
        atoms_u, edges_u, _, _ = m2.reacting_subgraph_exact(ks, sA, R)
        atoms_u2, _, _ = reacting_subgraph_model(ks, sA, R, SP.SurpriseModel.UNIFORM)
        if atoms_u2 != atoms_u:
            raise CannotCheck(f"canonical UNIFORM extraction differs from the frozen harness on {inst.instance_id}")
        atoms_p, edges_p, _ = reacting_subgraph_model(ks, sA, R, SP.SurpriseModel.PROPAGATED)
        atoms_pB, edges_pB, _ = reacting_subgraph_model(ks, sB, R, SP.SurpriseModel.PROPAGATED)
        miss_u = [a for a in live_req if a not in atoms_u]
        miss_p = [a for a in live_req if a not in atoms_p]
        lost = [a for a in live_req if a in atoms_u and a not in atoms_p]
        rows.append({
            "instance_id": inst.instance_id,
            "family": inst.family,
            "live_request_atoms": len(live_req),
            "extract_misses_uniform": miss_u,
            "extract_misses_propagated": miss_p,
            "lost_under_propagated": lost,
            "g_q_size_uniform": len(atoms_u),
            "g_q_size_propagated": len(atoms_p),
            "translator_invariant_propagated": _canonical(atoms_p, edges_p) == _canonical(atoms_pB, edges_pB),
            "baseline_miss": inst.instance_id in base_misses,
        })
    n = len(rows)
    misses_u = [r["instance_id"] for r in rows if r["extract_misses_uniform"]]
    misses_p = [r["instance_id"] for r in rows if r["extract_misses_propagated"]]
    nav_u = n - len(misses_u)
    nav_p = n - len(misses_p)
    lost_any = [r["instance_id"] for r in rows if r["lost_under_propagated"]]
    inv_p = sum(1 for r in rows if r["translator_invariant_propagated"])
    hub = {m.value: SP.check_hub_theorem_under_model(m) for m in SP.SurpriseModel}
    guards = {
        "baseline_reproduced": set(misses_u) == base_misses and nav_u == base_nav,
        "no_live_atom_lost": not lost_any,
        "translator_invariance_kept": inv_p == n,
        "hub_theorem_kept": all(v["direction_i"] == v["direction_ii"] == 1 for v in hub.values()),
    }
    improved = len(misses_p) < len(misses_u)
    verdict = "NEGATIVE__GUARD_FAILED" if not all(guards.values()) else ("POSITIVE__EXTRACT_MISSES_REDUCED" if improved else "NEGATIVE__NO_IMPROVEMENT")
    body = {
        "study": "M2_1_SURPRISE_REVIVAL_V1",
        "attribution": "EXTRACT (background model)",
        "lever": "PROPAGATED surprise (propagated mass vs propagated background)",
        "seed_count_lemma": "expected fixed point over random seed supports of any size equals the uniform background (linearity) — the receipt's lever is a no-op",
        "split": {"name": "dev", "seed": "ME-X1-DEV-20260902", "per_family": per_family, "n": n},
        "baseline": {"FOUND_BY_NAVIGATION": base_nav, "extract_misses": sorted(base_misses)},
        "uniform": {"FOUND_BY_NAVIGATION": nav_u, "extract_misses": misses_u},
        "propagated": {"FOUND_BY_NAVIGATION": nav_p, "extract_misses": misses_p, "translator_invariant": inv_p},
        "guards": guards,
        "hub_theorem": hub,
        "verdict": verdict,
        "instances": rows,
        "authority": "dev split; a design-choice comparison of two registered surprise models under identical closure, budget and labels; no novelty or protected claim; the default model is not changed by this study",
    }
    body["body_sha256"] = hashlib.sha256(json.dumps({k: v for k, v in body.items()}, sort_keys=True, default=str).encode()).hexdigest()
    return body


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--per-family", type=int, default=5)
    p.add_argument("--out", type=Path, default=None)
    a = p.parse_args(argv)
    try:
        r = run(a.per_family)
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except AssertionError as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}))
        return 1
    text = json.dumps(r, indent=2, sort_keys=True, default=str)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(json.dumps({k: r[k] for k in ("verdict", "baseline", "uniform", "propagated", "guards")}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
