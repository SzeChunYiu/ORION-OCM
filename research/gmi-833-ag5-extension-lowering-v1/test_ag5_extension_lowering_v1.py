# -*- coding: utf-8 -*-
"""AG5 hostiles, controls, nulls and the no-alarm case.

Every gate raises or records; none depends on a bare `assert`, so the file behaves
identically under `python3 -I -B` and `python3 -I -O -B`.

    python3 -I -O -B  test_ag5_extension_lowering_v1.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ag5_extension_lowering_v1 as A   # noqa: E402

FINDINGS = []
HOSTILES = []


def hostile(name, detected, control_clean, detail):
    HOSTILES.append({"hostile": name, "detected": bool(detected),
                     "control_clean": bool(control_clean), "detail": detail})
    if not detected:
        FINDINGS.append("HOSTILE_NOT_DETECTED:" + name)
    if not control_clean:
        FINDINGS.append("CONTROL_NOT_CLEAN:" + name)


def _kernels():
    return tuple(A._kernel_pairs(k) for k in A.PSTO.kernel_family()[:48])


def _dists():
    return tuple(A._dist_pairs(r) for r in A.PSTO.row_family())


def h_update_self_index():
    bad = good = 0
    rows = A.PSTO.row_family()
    kers = A.PSTO.kernel_family()
    for di, mu in enumerate(_dists()):
        for ki, K in enumerate(_kernels()):
            want = A._dist_pairs(A.PSTO.update(rows[di], kers[ki]).value)
            try:
                got, _ = A.low_update(mu, K, self_index_bug=True)
            except ValueError:
                got = None
            if got != want:
                bad += 1
            ok, _ = A.low_update(mu, K)
            if ok == want:
                good += 1
    hostile("update_self_index", bad > 0, good == 6 * 48,
            {"perturbed_mismatches": bad, "control_agreements": good})


def h_compose_transposed():
    kers = A.PSTO.kernel_family()
    kps = _kernels()
    bad = good = 0
    for i, K1 in enumerate(kps[:24]):
        for j, K2 in enumerate(kps[:24]):
            want = A._kernel_pairs(A.PSTO.compose(kers[i], kers[j]).value)
            got, _ = A.low_compose(K1, K2, transpose_bug=True)
            if got != want:
                bad += 1
            ok, _ = A.low_compose(K1, K2)
            if ok == want:
                good += 1
    hostile("compose_transposed", bad > 0, good == 24 * 24,
            {"perturbed_mismatches": bad, "control_agreements": good})


def h_non_exact_weight():
    detected = False
    try:
        A.low_update(((0.5, 1.0), (0.5, 1.0), (0.0, 1.0)), _kernels()[0])
    except ValueError as exc:
        detected = "NON_EXACT_WEIGHT" in str(exc)
    control = True
    try:
        A.low_update(_dists()[0], _kernels()[0])
    except ValueError:
        control = False
    hostile("non_exact_weight", detected, control, {"guard": "NON_EXACT_WEIGHT"})


def h_unnormalized_lowering():
    """A row that does not sum to one must be refused by the lowering's own gate."""
    bad_kernel = (((1, 1), (1, 1), (0, 1)), ((1, 1), (0, 1), (0, 1)),
                  ((1, 1), (0, 1), (0, 1)))
    detected = False
    try:
        A.low_update(_dists()[0], bad_kernel)
    except ValueError as exc:
        detected = "NOT_NORMALIZED" in str(exc)
    control = True
    try:
        A.low_update(_dists()[0], _kernels()[0])
    except ValueError:
        control = False
    hostile("unnormalized_lowering", detected, control, {"guard": "LOWERED_RESULT_NOT_NORMALIZED"})


def _graphs():
    out = []
    for mask in range(8):
        edges = [A.PGRA.ALL_EDGES[i] for i in range(3) if mask & (1 << i)]
        out.append(A.PGRA.make_graph(edges))
    return out


def h_graph_self_neighbour():
    bad = good = 0
    states = [(a, b, c) for a in A.S3 for b in A.S3 for c in A.S3]
    for g in _graphs():
        adj = A.adjacency_registers(g)
        for st in states:
            want = A.PGRA.neighbor_update(st, g).state
            got, _, _ = A.low_neighbor_update(st, adj, self_neighbour_bug=True)
            if got != want:
                bad += 1
            ok, _, _ = A.low_neighbor_update(st, adj)
            if ok == want:
                good += 1
    hostile("graph_self_neighbour", bad > 0, good == 8 * 27,
            {"perturbed_mismatches": bad, "control_agreements": good})


def h_graph_constant_charge():
    bad = good = 0
    states = [(a, b, c) for a in A.S3 for b in A.S3 for c in A.S3]
    for g in _graphs():
        adj = A.adjacency_registers(g)
        for st in states:
            want = A.PGRA.neighbor_update(st, g).resources
            _, _, res = A.low_neighbor_update(st, adj, constant_charge_bug=True)
            if res != want:
                bad += 1
            _, _, ok = A.low_neighbor_update(st, adj)
            if ok == want:
                good += 1
    hostile("graph_constant_charge", bad > 0, good == 8 * 27,
            {"perturbed_resource_mismatches": bad, "control_agreements": good})


def h_channel_implicit_delivery():
    bad = good = 0
    for loc in [(a, b, c) for a in A.S3 for b in A.S3 for c in A.S3]:
        base = A.PCHA.Machine.empty(loc)
        for (src, dst) in A.PCHA.CHANNELS:
            for msg in A.PCHA.MESSAGES:
                pm, _ = A.PCHA.send(base, src, dst, msg)
                nl, nq, _, _ = A.low_send(base.local, base.queues, src, dst, msg,
                                          implicit_delivery_bug=True)
                if (nl, nq) != (pm.local, pm.queues):
                    bad += 1
                ol, oq, _, _ = A.low_send(base.local, base.queues, src, dst, msg)
                if (ol, oq) == (pm.local, pm.queues):
                    good += 1
    hostile("channel_implicit_delivery", bad > 0, good == 27 * 6 * 2,
            {"perturbed_mismatches": bad, "control_agreements": good})


def h_channel_tag_dropped():
    tag = A.external_tag_role()
    hostile("channel_tag_dropped",
            tag["forged_accepted_without_tag_gate"] == tag["forged_checks"],
            tag["forged_rejected_with_tag_gate"] == tag["forged_checks"],
            tag)


def h_selfchange_drop_admit():
    """Without the admission guard, rejected and forged proposals are adopted."""
    ver = A.PSELF.fixture_verifier()
    other = A.PSELF.ExternalVerifier(b"GMI833-AG5-UNREGISTERED-AUTHORITY",
                                     authority_id="VERIFIER_X")
    wrongly_adopted = 0
    control_refused = 0
    for cand in A.PSELF.candidate_space():
        s0 = A.PSELF.base_state()
        sp, p, _ = A.PSELF.propose(s0, cand)
        ro, _ = other.verify(p)
        valid, _ = ver.validate(p, ro)
        args = dict(fresh=True, pending_ok=True, admitted=valid, version_ok=True,
                    accepted=(ro.decision == A.PSELF.ACCEPT))
        parent = A.PSELF.adopt(sp, p, ro, ver).terminal == "ADOPTED"
        bad, _, _ = A.low_adopt_guard(drop_admit_bug=True, **args)
        good, _, _ = A.low_adopt_guard(**args)
        if bad and not parent:
            wrongly_adopted += 1
        if good == parent:
            control_refused += 1
    hostile("selfchange_drop_admit", wrongly_adopted > 0, control_refused == 27,
            {"wrongly_adopted": wrongly_adopted, "control_agreements": control_refused})


def h_selfchange_allow_replay():
    ver = A.PSELF.fixture_verifier()
    replayed = 0
    control = 0
    for cand in A.PSELF.candidate_space():
        if cand[0] != 0:
            continue
        s0 = A.PSELF.base_state()
        sp, p, _ = A.PSELF.propose(s0, cand)
        r, _ = ver.verify(p)
        tr = A.PSELF.adopt(sp, p, r, ver)
        valid, _ = ver.validate(p, r)
        args = dict(fresh=False, pending_ok=True, admitted=valid,
                    version_ok=True, accepted=True)
        bad, _, _ = A.low_adopt_guard(allow_replay_bug=True, **args)
        good, _, _ = A.low_adopt_guard(**args)
        parent = A.PSELF.adopt(tr.state, p, r, ver).terminal == "ADOPTED"
        if bad and not parent:
            replayed += 1
        if good == parent:
            control += 1
    hostile("selfchange_allow_replay", replayed > 0, control == 9,
            {"replays_admitted": replayed, "control_agreements": control})


def h_family_name_leak():
    planted = A.family_name_audit(extra_text="def low_posterior_update(prior, x): pass")
    clean = A.family_name_audit()
    hostile("family_name_leak", len(planted["hits"]) > 0, len(clean["hits"]) == 0,
            {"planted_hits": planted["hits"], "clean_hits": clean["hits"]})


def h_expansion_off_by_one():
    original = A.exp_nat_add
    A.exp_nat_add = lambda a, b: b + 2
    bad = A.validate_expansions(6)
    A.exp_nat_add = original
    good = A.validate_expansions(6)
    hostile("expansion_off_by_one", bad["failure_count"] > 0, good["failure_count"] == 0,
            {"perturbed_failures": bad["failure_count"], "control_failures": good["failure_count"]})


def h_guard_isolation_prediction():
    """A case table that removes the isolating cases must break the prediction."""
    _, ext = A.adopt_case_table()
    trimmed = [(v, o) for v, o in ext if all(v) or not v[4]]
    bad = A.guard_subset_null(trimmed)
    good = A.guard_subset_null(ext)
    hostile("guard_isolation_trimmed",
            bad["reproducing_subsets"] > good["reproducing_subsets"],
            good["prediction_matches"] and good["reproducing_subsets"] == 1,
            {"trimmed_reproducing": bad["reproducing_subsets"],
             "full_reproducing": good["reproducing_subsets"]})


def no_alarm():
    """On the true configuration every detector must be silent."""
    tag = A.external_tag_role()
    gdep = A.graph_structure_dependence()
    audit = A.family_name_audit()
    _, ext = A.adopt_case_table()
    gn = A.guard_subset_null(ext)
    quiet = {
        "tag_inert_differences": tag["inert_differences"],
        "control_ops_structure_dependent": (gdep["differing_pairs"]["POINTWISE"]
                                            + gdep["differing_pairs"]["GLOBAL_BROADCAST"]),
        "family_name_hits": len(audit["hits"]),
        "guard_prediction_matches": gn["prediction_matches"],
        "expansion_failures": A.validate_expansions(16)["failure_count"],
    }
    bad = [k for k, v in quiet.items()
           if (v is not True and v != 0)]
    if bad:
        FINDINGS.append("NO_ALARM_VIOLATED:" + ",".join(bad))
    return quiet


def main():
    for fn in (h_update_self_index, h_compose_transposed, h_non_exact_weight,
               h_unnormalized_lowering, h_graph_self_neighbour, h_graph_constant_charge,
               h_channel_implicit_delivery, h_channel_tag_dropped,
               h_selfchange_drop_admit, h_selfchange_allow_replay,
               h_family_name_leak, h_expansion_off_by_one, h_guard_isolation_prediction):
        fn()
    quiet = no_alarm()
    nulls = {"stochastic": A.null_stochastic(), "graph": A.null_graph(),
             "channels": A.null_channels()}
    for k, v in nulls.items():
        if v["hits"]:
            FINDINGS.append("NULL_REPRODUCED:" + k)
        if v["live_trials"] < 190:
            FINDINGS.append("NULL_TOO_FEW_LIVE_TRIALS:" + k)
    out = {"schema": "GMI833AG5ExtensionLoweringTestReceiptV1",
           "hostiles": HOSTILES,
           "hostiles_declared": len(HOSTILES),
           "hostiles_detected": sum(1 for h in HOSTILES if h["detected"]),
           "controls_clean": sum(1 for h in HOSTILES if h["control_clean"]),
           "no_alarm": quiet,
           "nulls": nulls,
           "findings": FINDINGS,
           "status": "GREEN" if not FINDINGS else "RED"}
    with open(os.path.join(HERE, "TEST_RESULT_V1.json"), "w") as fh:
        fh.write(json.dumps(out, indent=2, sort_keys=True, separators=(",", ": ")) + "\n")
    print(json.dumps({"status": out["status"],
                      "hostiles_declared": out["hostiles_declared"],
                      "hostiles_detected": out["hostiles_detected"],
                      "controls_clean": out["controls_clean"],
                      "findings": FINDINGS}, indent=2, sort_keys=True))
    return 0 if not FINDINGS else 1


if __name__ == "__main__":
    sys.exit(main())
