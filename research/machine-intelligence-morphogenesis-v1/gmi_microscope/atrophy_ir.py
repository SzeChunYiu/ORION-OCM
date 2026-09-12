"""RV-377-074 — the atrophy instrument applied to the TYPED IR, so that the biosphere's own carrier descriptor is
measured rather than assumed.

RV-377-071 established that a carrier descriptor computed on a RAW genotype is not a measurement of the carrier: all 24
winners of the expression-tree search classified as memory or hybrid, and all 24 lost every store write under charged
atrophy, leaving a two-rule error-driven coefficient learner. The descriptor was reading 55-68 per cent introns.

The B1 recovery receipts (RV-377-058) classify their archive elites with exactly the same kind of instrument -
`b1.carrier_of`, which walks back from OUTPUT and reports the first state kind it meets on the raw graph. If the IR
search also accumulates introns, then the recovered mechanism classes of the biosphere's own B1 gate are suspect for the
same reason, in both directions: a carrier may be credited that is dead weight, and a carrier may be hidden behind one.

This module deletes typed NODES rather than expression subtrees. Greedy, deterministic given the canonical ordering, and
charged: every candidate deletion costs one exact evaluation of the full developmental lifecycle through the VM.

  prune(g, target)   delete nodes to a fixed point under the constraint capability >= theta
  reclassify(...)    carrier and mechanism vector BEFORE and AFTER, per archive elite

An elite whose carrier changes under atrophy was never a recovery of that mechanism class. An elite whose carrier
survives atrophy is a recovery, and its atrophied graph is the structural match that protocol rule 20 requires.
"""
from __future__ import annotations

import json
import os
import sys
import time

from . import b1, morph, smooth
from .core import sha256_of

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(os.path.dirname(HERE), "microscopes", "results")
THETA = b1.THETA
PROTECTED = ("INPUT", "TARGET", "OUTPUT")


def _cap(g, target):
    r = b1.evaluate(g, target)
    return None if r is None else r[0]


def prune(g, target, theta=THETA, max_rounds=24):
    """greedy node deletion to a fixed point under capability >= theta; deterministic given the canonical order."""
    cur = morph.from_json(morph.to_json(g))
    base = _cap(cur, target)
    if base is None or base < theta:
        return cur, {"prunable": False, "reason": "the elite is not admissible under replay", "capability": base}
    evals = 1; removed = []
    # the canonical order is computed ONCE, on the committed genotype: node identifiers are stable under deletion, so the
    # order is remint-invariant and the whole pruning is deterministic. Recomputing it every round would be canonical too
    # but the exact tie-break enumerates permutations of each colour class, which is exponential on graphs with many
    # repeated kinds and is what made the first attempt of this run hang.
    lab = morph.canonical_labels(cur)
    for rnd in range(max_rounds):
        order = sorted((i for i, (k, _) in cur["nodes"].items() if k not in PROTECTED), key=lambda i: lab.get(i, 0))
        hit = False
        for nid in order:
            if nid not in cur["nodes"]: continue
            trial = morph.from_json(morph.to_json(cur))
            kind = trial["nodes"][nid][0]
            del trial["nodes"][nid]
            trial["edges"] = [e for e in trial["edges"] if e[0] != nid and e[1] != nid]
            try:
                morph.typecheck(trial)
            except Exception:
                continue
            c = _cap(trial, target); evals += 1
            if c is not None and c >= theta:
                removed.append({"round": rnd, "kind": kind, "capability_after": c,
                                "n_nodes_after": len(trial["nodes"])})
                cur = trial; base = c; hit = True
                break
        if not hit: break
    return cur, {"prunable": True, "capability": base, "n_nodes": len(cur["nodes"]),
                 "evaluations_charged": evals, "n_removed": len(removed), "removed": removed}


def reclassify(receipt_path, eco_name="E_smooth3", theta=THETA):
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": smooth.COEFFS_V1}[eco_name]
    target = smooth.make_target(coeffs)
    r = json.load(open(receipt_path))
    out = {}
    for carrier, v in r["best_by_carrier"].items():
        if not v.get("admissible"): continue
        g = morph.from_json(v["genotype"])
        cap0 = _cap(g, target)
        small, info = prune(g, target, theta)
        out[carrier] = {
            "capability_committed": v["capability"], "capability_replayed": cap0,
            "replay_matches_receipt": cap0 is not None and abs(cap0 - v["capability"]) < 1e-9,
            "carrier_before": carrier, "carrier_after": b1.carrier_of(small),
            "carrier_survives_atrophy": b1.carrier_of(small) == carrier,
            "n_nodes_before": v["n_nodes"], "n_nodes_after": info.get("n_nodes"),
            "intron_fraction": (round(1 - info["n_nodes"] / v["n_nodes"], 4) if info.get("n_nodes") else None),
            "mechanism_vector_before": v["mechanism_vector"], "mechanism_vector_after": morph.mechanism_vector(small),
            "fingerprint_before": v["fingerprint"], "fingerprint_after": morph.fingerprint(small),
            "atrophied_genotype": morph.to_json(small), **{k: val for k, val in info.items() if k != "removed"},
            "removed_kinds": [d["kind"] for d in info.get("removed", [])]}
    return out


def main(tag="V1", eco_name="E_smooth3", receipts=None):
    """receipt files are selected by ECOLOGY, because the same seed is run on more than one and a B1 elite must be
    atrophied on the ecology it was recovered on."""
    t0 = time.time()
    files = receipts or sorted(f for f in os.listdir(RES)
                               if f.startswith("STAGE_B1_V33") and f.endswith(".json") and eco_name in f)
    rows = {}
    for f in files:
        try:
            rows[f] = reclassify(os.path.join(RES, f), eco_name)
        except Exception as ex:
            rows[f] = {"error": f"{type(ex).__name__}: {ex}"}
        for c, v in rows[f].items():
            if isinstance(v, dict) and "carrier_after" in v:
                print(json.dumps({"receipt": f, "carrier": c, "before": v["n_nodes_before"], "after": v["n_nodes_after"],
                                  "carrier_after": v["carrier_after"], "survives": v["carrier_survives_atrophy"],
                                  "cap": v["capability"]}), flush=True)
    flat = [v for d in rows.values() for v in d.values() if isinstance(v, dict) and "carrier_after" in v]
    receipt = {"schema": "StageB1AtrophyReclassificationV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-074", "run_tag": tag, "ecology": eco_name, "theta": theta_of(),
               "instrument": "greedy typed-NODE deletion to a fixed point under capability >= theta, deterministic in the canonical node order; every candidate deletion charged as one exact developmental replay through the VM",
               "receipts_examined": files, "rows": rows, "n_elites": len(flat),
               "summary": {"n_carrier_survives": sum(1 for v in flat if v["carrier_survives_atrophy"]),
                           "n_carrier_changes": sum(1 for v in flat if not v["carrier_survives_atrophy"]),
                           "n_replay_mismatch": sum(1 for v in flat if not v["replay_matches_receipt"]),
                           "intron_fractions": sorted(v["intron_fraction"] for v in flat if v["intron_fraction"] is not None),
                           "carrier_transitions": sorted({f"{v['carrier_before']}->{v['carrier_after']}" for v in flat})},
               "seconds": round(time.time() - t0, 1),
               "claim_ceiling": "greedy deletion gives an UPPER bound on the smallest admissible genotype contained in each elite, not the minimum; a carrier that survives atrophy is load-bearing at this bound, and one that does not was never recovered"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B1_ATROPHY_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("summary:", json.dumps(receipt["summary"]))
    return receipt


def theta_of():
    return THETA


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "V1", sys.argv[2] if len(sys.argv) > 2 else "E_smooth3",
         sys.argv[3:] or None)


# ------------------------------------------------------------------------------- the reference catalogue for stage B4
def zoo_signatures(eco_name="E_smooth3", theta=THETA):
    """RV-377-077 — the ATROPHIED signature of every known parent, which is the reference catalogue a B4 unknown-form
    claim must be compared against.

    Protocol rule 23 says a carrier descriptor is computed on the atrophied genotype. That applies to the PARENTS as
    well as to the discoveries: comparing an atrophied candidate against a RAW parent would let intron differences count
    as novelty. Both sides of the comparison must be atrophied by the same charged instrument.

    Returns, per zoo parent: its capability, its atrophied size, its atrophied carrier, its atrophied mechanism vector,
    and the canonical fingerprint of the atrophied graph. Two machines with the same atrophied fingerprint are the same
    machine; two with the same (carrier, mechanism vector) are in the same class at this resolution.
    """
    from . import zoo
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": smooth.COEFFS_V1}[eco_name]
    target = smooth.make_target(coeffs)
    out = {}
    for name, mk in zoo.ZOO.items():
        g = mk()
        cap0 = _cap(g, target)
        if cap0 is None:
            out[name] = {"error": "phenotype did not evaluate"}
            continue
        if cap0 < theta:
            out[name] = {"capability": cap0, "admissible": False, "n_nodes": len(g["nodes"]),
                         "carrier_raw": b1.carrier_of(g), "mechanism_vector_raw": morph.mechanism_vector(g),
                         "note": "inadmissible on this ecology, so it has no atrophied signature here"}
            continue
        small, info = prune(g, target, theta)
        out[name] = {"capability": cap0, "admissible": True,
                     "n_nodes_raw": len(g["nodes"]), "n_nodes_atrophied": info["n_nodes"],
                     "intron_fraction": round(1 - info["n_nodes"] / len(g["nodes"]), 4),
                     "carrier_raw": b1.carrier_of(g), "carrier_atrophied": b1.carrier_of(small),
                     "carrier_survives": b1.carrier_of(small) == b1.carrier_of(g),
                     "mechanism_vector_raw": morph.mechanism_vector(g),
                     "mechanism_vector_atrophied": morph.mechanism_vector(small),
                     "fingerprint_atrophied": morph.fingerprint(small),
                     "capability_atrophied": info["capability"],
                     "evaluations_charged": info["evaluations_charged"],
                     "atrophied_genotype": morph.to_json(small)}
    return out


def catalogue(tag="V1", eco_name="E_smooth3"):
    import time as _t
    t0 = _t.time(); sig = zoo_signatures(eco_name)
    adm = {k: v for k, v in sig.items() if v.get("admissible")}
    fps = {}
    for k, v in adm.items(): fps.setdefault(v["fingerprint_atrophied"], []).append(k)
    classes = {}
    for k, v in adm.items():
        key = f"{v['carrier_atrophied']}|" + ",".join(f"{c}{n}" for c, n in sorted(v["mechanism_vector_atrophied"].items()) if n)
        classes.setdefault(key, []).append(k)
    receipt = {"schema": "StageB4ReferenceCatalogueV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-077", "run_tag": tag, "ecology": eco_name, "theta": THETA,
               "purpose": "the atrophied signature of every known parent, which is what a stage-B4 unknown-form claim must be compared against; protocol rule 23 applies to the PARENTS as well as to the discoveries, or intron differences would count as novelty",
               "parents": sig, "n_parents": len(sig), "n_admissible": len(adm),
               "distinct_atrophied_fingerprints": {k: v for k, v in fps.items()},
               "n_distinct_atrophied_machines": len(fps),
               "classes_at_carrier_plus_mechanism_resolution": classes,
               "n_distinct_classes": len(classes),
               "collisions": {k: v for k, v in fps.items() if len(v) > 1},
               "seconds": round(_t.time() - t0, 1),
               "claim_ceiling": "one ecology; greedy atrophy bounds each parent's smallest admissible form from above, so two parents sharing an atrophied fingerprint are the same machine at this bound, and two that differ may still share a smaller common form"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B4_CATALOGUE_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for k, v in sorted(sig.items()):
        print(f"  {k:22s} cap {v.get('capability')} adm {v.get('admissible')} nodes {v.get('n_nodes_raw', v.get('n_nodes'))}->{v.get('n_nodes_atrophied')} carrier {v.get('carrier_raw')}->{v.get('carrier_atrophied')}")
    print("distinct atrophied machines:", receipt["n_distinct_atrophied_machines"], "| distinct classes:", receipt["n_distinct_classes"])
    if receipt["collisions"]: print("COLLISIONS (parents that atrophy to the SAME machine):", receipt["collisions"])
    return receipt


# ---------------------------------------------------------------- stage B4 pre-test: is any recovered form UNKNOWN?
def _response(g, target, n_events=16, seed=0):
    """the exact final served answer vector — the developmental response the novelty criterion is decided on."""
    from . import bases
    from .vm import VMRow
    rows = {"IR": (lambda gg: (lambda size: VMRow(gg, size, seed)))(g)}
    r = smooth.run("IR", bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"], 1, seed=seed, target=target,
                   n_events=n_events, rows=rows, criterion="unseen")
    return tuple(sorted(r["D"][-1].items())), r["capability"]


def b4_pretest(tag="V1", eco_name="E_smooth3", catalogue_tag="V1", atrophy_tag="V1"):
    """RV-377-077 — does neutral search over the IR produce any form that is NOT a known parent?

    Two resolutions are computed and they disagree, which is the result:

      STRUCTURAL   the (carrier, mechanism-vector) key of the ATROPHIED genotype, compared against the atrophied
                   parents' keys (the catalogue above).
      RESPONSE     the exact final served answer vector, compared against the atrophied parents' vectors.

    A novelty claim is only valid at the RESPONSE resolution: the domain criterion is stated on the developmental
    response, and two machines with the same response are the same machine however differently they are wired.
    """
    import time as _t
    t0 = _t.time()
    coeffs = {"E_smooth3": smooth.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": smooth.COEFFS_V1}[eco_name]
    target = smooth.make_target(coeffs)
    cat = json.load(open(os.path.join(RES, f"STAGE_B4_CATALOGUE_{catalogue_tag}.json")))
    at = json.load(open(os.path.join(RES, f"STAGE_B1_ATROPHY_{atrophy_tag}.json")))
    known_classes = set(cat["classes_at_carrier_plus_mechanism_resolution"])
    known_fps = set(cat["distinct_atrophied_fingerprints"])
    parents = {}
    for name, v in cat["parents"].items():
        if v.get("admissible"):
            resp, cap = _response(morph.from_json(v["atrophied_genotype"]), target)
            parents[name] = {"response": resp, "capability": cap, "signature": sha256_of([str(resp)])}
    pgroups = {}
    for n, v in parents.items(): pgroups.setdefault(v["signature"], []).append(n)

    def _key(carrier, mv): return f"{carrier}|" + ",".join(f"{c}{n}" for c, n in sorted(mv.items()) if n)

    cands = {}
    for f, d in at["rows"].items():
        for c, v in d.items():
            if not isinstance(v, dict) or "atrophied_genotype" not in v: continue
            g = morph.from_json(v["atrophied_genotype"])
            resp, cap = _response(g, target)
            sig = sha256_of([str(resp)])
            k = _key(v["carrier_after"], v["mechanism_vector_after"])
            cands[f"{f}|{c}"] = {
                "carrier_raw": v["carrier_before"], "carrier_atrophied": v["carrier_after"],
                "n_nodes_atrophied": v["n_nodes_after"], "capability": cap,
                "structural_key": k, "structural_key_is_known": k in known_classes,
                "atrophied_fingerprint": v["fingerprint_after"], "fingerprint_is_known": v["fingerprint_after"] in known_fps,
                "response_signature": sig, "exact_developmental_equality_with": sorted(pgroups.get(sig, [])),
                "is_unknown_form_at_response_resolution": sig not in pgroups}
    n_struct_novel = sum(1 for v in cands.values() if not v["structural_key_is_known"])
    n_resp_novel = sum(1 for v in cands.values() if v["is_unknown_form_at_response_resolution"])
    receipt = {"schema": "StageB4PretestV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-077", "run_tag": tag, "ecology": eco_name, "theta": THETA,
               "question": "does neutral search over the typed IR produce any admissible form that is NOT a known parent, once BOTH sides are atrophied (protocol rule 23)?",
               "parents_admissible": {n: {"capability": v["capability"], "response_signature": v["signature"]} for n, v in parents.items()},
               "parent_response_groups": pgroups, "n_parents_admissible": len(parents),
               "n_distinct_parent_responses": len(pgroups),
               "candidates": cands, "n_candidates": len(cands),
               "n_novel_at_structural_resolution": n_struct_novel,
               "n_novel_at_response_resolution": n_resp_novel,
               "terminal": ("NO_UNKNOWN_FORM__EVERY_RECOVERED_MACHINE_IS_EXACTLY_DEVELOPMENTALLY_EQUAL_TO_A_KNOWN_PARENT"
                            if n_resp_novel == 0 else
                            f"UNKNOWN_FORM_CANDIDATES_AT_RESPONSE_RESOLUTION__{n_resp_novel}_OF_{len(cands)}"),
               "seconds": round(_t.time() - t0, 1),
               "claim_ceiling": "one ecology, one criterion, the final served answer vector only; exact developmental equality here is equality of the FINAL response, not of the whole trace under every registered intervention, which is the stronger test the R2 equivalence harness applies"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_B4_PRETEST_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    for k, v in sorted(cands.items()):
        print(f"  {k.split('|')[0][-7:-5]} {k.split('|')[1]:8s}->{v['carrier_atrophied']:8s} cap {v['capability']} "
              f"struct_known={v['structural_key_is_known']} equal_to={v['exact_developmental_equality_with'] or 'NONE'}")
    print(f"novel at STRUCTURAL resolution: {n_struct_novel}/{len(cands)} | novel at RESPONSE resolution: {n_resp_novel}/{len(cands)}")
    print("terminal:", receipt["terminal"])
    return receipt


# ----------------------------------------------------- protocol rule 32: atrophy under the FULL intervention set
def prune_all_interventions(g, spec, basis=None, theta=None, max_rounds=24, interventions=None):
    """RV-377-085 — greedy node deletion accepted only if capability stays at or above theta under EVERY registered
    intervention.

    Protocol rule 32, added by RV-377-082 after atrophy under a single intervention RAISED a witness's capability by
    deleting the EVIDENCE buffer, whose only purpose is revocation replay, on a harness that never revokes. Rule 23 says
    compute a carrier descriptor on the atrophied genotype; it did not say under which intervention set, and every
    atrophy receipt committed before this function existed was produced under the standard intervention alone.

    Deterministic in the canonical node order of the committed genotype, exactly as `prune`. Every candidate deletion is
    charged once PER INTERVENTION, so a run here costs |INTERVENTIONS| times a single-intervention run.
    """
    from . import bases, ecology
    basis = basis or bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    th = spec["theta"] if theta is None else theta
    js = list(interventions or ecology.INTERVENTIONS)

    def caps(gg):
        out = {}
        for j in js:
            try:
                out[j] = ecology.run_genotype(spec, gg, basis, j)["capability"]
            except Exception:
                return None
        return out

    cur = morph.from_json(morph.to_json(g))
    base = caps(cur)
    if base is None or min(base.values()) < th:
        return cur, {"prunable": False, "reason": "not admissible under every registered intervention at entry",
                     "capabilities": base, "interventions": js}
    evals = len(js); removed = []
    lab = morph.canonical_labels(cur)
    for rnd in range(max_rounds):
        order = sorted((i for i, (k, _) in cur["nodes"].items() if k not in PROTECTED), key=lambda i: lab.get(i, 0))
        hit = False
        for nid in order:
            if nid not in cur["nodes"]: continue
            trial = morph.from_json(morph.to_json(cur))
            kind = trial["nodes"][nid][0]
            del trial["nodes"][nid]
            trial["edges"] = [e for e in trial["edges"] if e[0] != nid and e[1] != nid]
            try:
                morph.typecheck(trial)
            except Exception:
                continue
            c = caps(trial); evals += len(js)
            if c is not None and min(c.values()) >= th:
                removed.append({"round": rnd, "kind": kind, "capabilities_after": c, "n_nodes_after": len(trial["nodes"])})
                cur, base, hit = trial, c, True
                break
        if not hit: break
    return cur, {"prunable": True, "capabilities": base, "min_capability": min(base.values()),
                 "n_nodes": len(cur["nodes"]), "evaluations_charged": evals, "n_removed": len(removed),
                 "interventions": js, "removed_kinds": [d["kind"] for d in removed]}


def rule32_recheck(tag="V1", eco_name="E_smooth1", rows=None):
    """re-atrophy the registered zoo rows under the full intervention set and report what a single-intervention pruner
    would have deleted that the full set refuses. This is the direct measurement rule 32 demands of every committed
    atrophy receipt."""
    import time as _t
    from . import bases, ecology, zoo, smooth as _s
    t0 = _t.time()
    spec = ecology.REGISTRY[eco_name]
    target = _s.make_target({"E_smooth3": _s.COEFFS_V3, "E_sym5": (5 / 16,) * 4, "E_smooth1": _s.COEFFS_V1}[eco_name])
    names = rows or list(zoo.ZOO)
    out = {}
    for n in names:
        g = zoo.ZOO[n]()
        r1 = b1.evaluate(g, target)
        if r1 is None or r1[0] < THETA:
            out[n] = {"admissible_single": False, "capability_single": None if r1 is None else r1[0]}
            continue
        small1, i1 = prune(g, target, THETA)
        smallA, iA = prune_all_interventions(g, spec)
        out[n] = {
            "capability_single": r1[0],
            "single_intervention": {"n_nodes": i1.get("n_nodes"), "capability": i1.get("capability"),
                                    "carrier": b1.carrier_of(small1), "removed_kinds": [d["kind"] for d in i1.get("removed", [])]},
            "all_interventions": {"n_nodes": iA.get("n_nodes"), "min_capability": iA.get("min_capability"),
                                  "carrier": b1.carrier_of(smallA) if iA.get("prunable") else None,
                                  "removed_kinds": iA.get("removed_kinds"), "prunable": iA.get("prunable"),
                                  "reason": iA.get("reason")},
            "kinds_the_full_set_refuses_to_delete": sorted(set([d["kind"] for d in i1.get("removed", [])]) - set(iA.get("removed_kinds") or [])),
            "size_difference": (iA.get("n_nodes") or 0) - (i1.get("n_nodes") or 0)}
        print(json.dumps({"row": n, **{k: v for k, v in out[n].items() if k != "capability_single"}}), flush=True)
    diffs = [n for n, v in out.items() if v.get("kinds_the_full_set_refuses_to_delete")]
    receipt = {"schema": "StageRule32AtrophyRecheckV1", "status": "EXECUTED_EXACT_AT_SCOPE", "issue": [377, 422],
               "revival_record": "RV-377-085", "run_tag": tag, "ecology": eco_name, "theta": THETA,
               "rule": "protocol rule 32: a deletion is accepted only if capability stays at or above theta under EVERY registered intervention",
               "interventions": list(ecology.INTERVENTIONS), "rows": out,
               "n_rows_where_the_full_set_refuses_a_deletion": len(diffs),
               "rows_affected": diffs, "seconds": round(_t.time() - t0, 1),
               "claim_ceiling": "one ecology and the registered zoo rows; it measures how much a single-intervention pruner over-deletes on machines whose purpose is known, which is the cheapest available proxy for the same question about evolved genotypes"}
    receipt["receipt_sha256"] = sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    json.dump(receipt, open(os.path.join(RES, f"STAGE_RULE32_ATROPHY_RECHECK_{tag}.json"), "w"), indent=1, sort_keys=True, default=str)
    print("rows where the full intervention set refuses a deletion the single one accepted:", len(diffs), diffs)
    return receipt
