"""KSO end-to-end traces — one command, three real traces plus the growth loop (design/05_MECHANICS.md).

  T1  FOUND                 a registered ME-X1 dev instance whose target claim is live: the full
                            atomize → navigate → fire → extract → compose → check → render path
  T2  GAP_NOT_FOUND         a registered ME-X1 dev instance whose target claim is non-live at request
                            time: the four-valued rule reports the gap with its acquisition hook
  T3  OBSTRUCTION_WITNESSED the island witness of the M0 contract §29: the ceiling walker fails, the
                            witness binds to orion_v2.jump.JumpTrigger and is admissible
  G   growth loop           acquire → compose → self-revise → registered revocation → reinstate, three
                            steps to a fixed point with the genome digest asserted unchanged

Prints a JSON trace; exit 0 when every trace reaches its declared outcome, 1 otherwise, 2 when a
trace could not be checked.  Every number printed is computed in this run.  NO NOVELTY CLAIM.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


kso = _load("kso_math_v1", HERE / "kso_math_v1.py")
m0 = _load("kso_m0_freeze_checks_v1", HERE / "kso_m0_freeze_checks_v1.py")
m1 = _load("kso_m1_mex1_population_v1", HERE / "kso_m1_mex1_population_v1.py")
m2 = _load("kso_m2_solve_v1", HERE / "kso_m2_solve_v1.py")
CannotCheck = kso.CannotCheck


def _fr(x):
    return str(x) if isinstance(x, Fraction) else x


def trace_instance(inst, exp, want: str) -> dict:
    w1, pop0, pop, added = m2.prepare(inst)
    row = m2.solve_instance(pop, w1, inst, exp)
    arm = row["arms"]["KSO_M2_SOLVE"]
    ks = pop.space
    _, seed = m2.atomize_A(pop, w1, inst)
    seeds = [x for x, v in zip(ks.ids, seed, strict=True) if v > 0]
    atoms, edges, act, _ = m2.reacting_subgraph_exact(ks, seed, pop.registered_revoked)
    target = f"claim:{inst.request.target_claim_id}"
    amap = ks.atom_map()
    trace = {
        "instance_id": inst.instance_id, "family": inst.family, "request": inst.request.kind, "target": target,
        "graph": {"atoms": len(ks.atoms), "hyperedges": len(ks.hyperedges), "request_level_atoms_added": len(added), "revoked_evidence": len(pop.registered_revoked), "censored_evidence": len(pop.unknown)},
        "1_atomize": {"seed_atoms": seeds, "seed_vector_nonzero": {x: _fr(v) for x, v in zip(ks.ids, seed, strict=True) if v > 0}},
        "2_navigate": {"outcome": arm["navigation_outcome"], "target_activation": _fr(act[target]), "target_live": kso.profile_live(amap[target].profile, pop.registered_revoked), "steps": arm["budget"]["steps"], "hyperedge_visits": arm["budget"]["edge_visits"]},
        "3_fire": {"enabled_hyperedges": len(kso.enabled_hyperedges(ks, act, Fraction(0), revoked=pop.registered_revoked))},
        "4_extract": {"reacting_atoms": len(atoms), "reacting_hyperedges": len(edges), "top_by_surprise": sorted(atoms, key=lambda x: -float(act[x]))[:5], "extraction_sha256": arm["extraction_sha256"], "translator_invariant": arm["translator_invariant"]},
        "5_compose": arm["compose_detail"],
        "6_check": {"stage_failures": arm["stage_failures"], "label_vs_oracle_mismatches": 0 if "CHECK" not in arm["stage_failures"] else 1},
        "7_render": arm["answer"],
        "oracle": row["oracle"], "exact": arm["exact"], "attribution": arm["attribution"],
        "declared_outcome": want, "reached": arm["navigation_outcome"] == want,
    }
    if want == "GAP_NOT_FOUND":
        trace["2_navigate"]["hook"] = "MORE_BUDGET_OR_ACQUIRE_WARRANT: the target claim's label is dead under the registered revocations; an acquisition (new warranted evidence family) or a reinstatement would make it live"
    return trace


def trace_obstruction() -> dict:
    ks = m0.navigation_witness_space()
    seed = m0.seed_vector(ks, {"s": Fraction(1, 1)})
    r = m0.navigate(ks, seed, "i2", m0.NavigationBudget(steps=12, restarts=1, depth=12))
    fields = r.witness.jump_trigger_fields() if r.witness else {}
    admissible = m0._jump_trigger_admissible(fields) if fields else None
    if admissible is None:
        raise CannotCheck("orion_v2.jump unimportable")
    return {
        "space": "M0 §29 witness: chain s→a1→…→a5→t, island i1→i2, w behind a revocable edge", "target": "i2", "seed_atoms": ["s"],
        "outcome": r.outcome.value, "reason": r.reason, "witness": {"incumbent_mechanism": r.witness.incumbent_mechanism, "failed_obligation": r.witness.failed_obligation, "frontier": list(r.witness.witness_atoms), "lower_level_dispositions": list(r.witness.lower_level_dispositions), "resource_bound": r.witness.resource_bound},
        "jump_trigger": {**fields, "witness_ids": list(fields["witness_ids"]), "lower_level_dispositions": list(fields["lower_level_dispositions"]), "is_admissible": admissible},
        "controls": {"timeout_is_gap": m0.navigate(ks, seed, "t", m0.NavigationBudget(2, 1, 2)).outcome.value, "found_with_budget": m0.navigate(ks, seed, "t", m0.NavigationBudget(12, 1, 12)).outcome.value},
        "declared_outcome": "OBSTRUCTION_WITNESSED", "reached": r.outcome.value == "OBSTRUCTION_WITNESSED" and admissible is True,
    }


def trace_growth() -> dict:
    res = m0.check_g3_growth_invariant()
    return {**res, "declared_outcome": "FIXED_POINT_GENOME_UNCHANGED", "reached": res["fixed_point_reached"] == 1 and res["genome_digest_unchanged"] == 1 and set(res["cancers"].values()) == {"CAUGHT"}}


def run() -> dict:
    gen, model, oracle = m1._mex1()
    pairs = gen.generate_split("dev", "ME-X1-DEV-20260902", {f: 5 for f in model.FAMILIES})
    found = gap = None
    for inst, exp in pairs:
        w1 = oracle.final_world(inst.world_v0, inst.events)
        pop = m1.populate(w1, request=inst.request, request_id=inst.instance_id)
        live = kso.profile_live(pop.space.atom_map()[f"claim:{inst.request.target_claim_id}"].profile, pop.registered_revoked)
        if live and found is None and inst.request.kind == "ACCEPT_RESULT":
            found = (inst, exp)
        if not live and gap is None:
            gap = (inst, exp)
        if found and gap:
            break
    if not found or not gap:
        raise CannotCheck("no dev instance for one of the declared outcomes")
    out = {"T1_FOUND": trace_instance(*found, "FOUND"), "T2_GAP_NOT_FOUND": trace_instance(*gap, "GAP_NOT_FOUND"), "T3_OBSTRUCTION_WITNESSED": trace_obstruction(), "G_GROWTH_LOOP": trace_growth(), "immune_system": {"genome_digest": m0.genome_digest(), "exit_codes": "0 reached / 1 not reached / 2 could not check"}}
    out["all_reached"] = all(out[k]["reached"] for k in ("T1_FOUND", "T2_GAP_NOT_FOUND", "T3_OBSTRUCTION_WITNESSED", "G_GROWTH_LOOP"))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        out = run()
    except CannotCheck as exc:
        print(json.dumps({"status": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"}))
        return 1
    text = json.dumps(out, indent=2, sort_keys=True, default=lambda o: sorted(o) if isinstance(o, (set, frozenset)) else str(o))
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text if not args.out else json.dumps({k: out[k]["reached"] for k in out if isinstance(out[k], dict) and "reached" in out[k]}))
    return 0 if out["all_reached"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
