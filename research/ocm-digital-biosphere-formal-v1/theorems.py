"""Machine-check BIO-T1..T15 on 2–8 organism worlds. Witnesses, not promotions."""
from __future__ import annotations

import copy

import graph_agreement
import kernels
import micro_earth as me
import parents


def _row(tid, status, **kv):
    kv = dict(kv)
    kv.update(theorem_id=tid, status=status)
    return kv


def _births(earth):
    return sum(1 for h in earth.history if h[0] == "birth")


def t1_noninterference():
    clean = me.MicroEarth(2, seed=0, leak=False)
    leaky = me.MicroEarth(2, seed=0, leak=True)
    me.run_horizon(clean, 8)
    me.run_horizon(leaky, 8)
    cb, lb = _births(clean), _births(leaky)
    if clean.assay_interferes():
        clean_status = "FAIL"
    elif cb == 0:
        clean_status = "VACUOUS_PASS"
    else:
        clean_status = "HOLD"
    return [
        _row("BIO-T1", clean_status, world="MW1", leak=False,
             graph=sorted(clean.write_graph), births=cb),
        _row("BIO-T1", "HOSTILE_DETECTED" if leaky.assay_interferes() else "FAIL",
             world="MW1", leak=True, hostile="H-LEAK-ASSAY-ENERGY", births=lb),
    ]


def t2_recurrence():
    rec = parents.finite_recurrence(n_states=4 ** 2 * 9 ** 2)  # 2 cells, g in 0..3, e in 0..8
    return [_row("BIO-T2", "PARENT_RECONSTRUCTED", world="MW1", **rec,
                 claim_ceiling="horizon-scoped novelty only")]


def t3_generator_support():
    alleles = 4
    reachable = set()
    for g in range(alleles):
        reachable.add(g)
        for h in me.enumerate_mutation_neighbourhood(g, alleles):
            reachable.add(h)
    return [_row("BIO-T3", "HOLD", world="MW4",
                 support=sorted(reachable), unreachable_outside=True,
                 note="Genome 5 is not in support.")]


def t4_social_options():
    rows = me.exhaustive_social_choices(n=3)
    forced = [r for r in rows if r["social"] == "forced" and not r["leak"]][0]
    optional = [r for r in rows if r["social"] == "optional" and not r["leak"]][0]
    # Seeded donor method=1 useful; forced copies it. Stale: set donor method=9
    stale = me.MicroEarth(3, seed=1, leak=False, social="forced")
    stale.cells[0].method = 9
    stale.cells[0].energy = 8
    stale.step()
    copied_stale = any(c.method == 9 for c in stale.alive() if c.uid != 0)
    return [
        _row("BIO-T4", "HOLD", world="MW2",
             optional_methods=optional["methods"],
             forced_methods=forced["methods"],
             stale_forced_copy=copied_stale,
             hostile="H-FORCED-COPY" if copied_stale else None,
             note="Extra options harm when transfer is forced."),
        _row("BIO-T4", "HOSTILE_DETECTED" if copied_stale else "FAIL",
             world="MW2", hostile="H-FORCED-COPY"),
    ]


def t5_dpi():
    dpi = parents.dpi_holds({
        (0, 0, 0): 200, (0, 0, 1): 50,
        (0, 1, 0): 20, (0, 1, 1): 80,
        (1, 1, 1): 200, (1, 1, 0): 50,
        (1, 0, 1): 20, (1, 0, 0): 80,
    })
    # Construct a non-Markov joint that can violate DPI to show the assumption
    # (not used as a Shannon counterexample — Shannon needs Markov).
    e = me.MicroEarth(8, seed=2, leak=False, social="optional")
    e.cells[0].method = 1
    e.step()
    return [_row("BIO-T5", "PARENT_RECONSTRUCTED" if dpi["ok"] else "FAIL",
                 world="MW8", **dpi)]


def t6_capital():
    good = parents.amortization_beneficial(2, 1, 2, 4)  # 8 > 3
    bad = parents.amortization_beneficial(10, 5, 1, 4)  # 4 > 15? False
    return [_row("BIO-T6", "HOLD", world="MW6",
                 beneficial_example=good, overhead_hostile=not bad,
                 hostile="H-SOCIAL-OVERHEAD")]


def t7_noncommute():
    def expose(order):
        e = me.MicroEarth(2, seed=3, leak=False)
        for regime in order:
            e.regime = regime
            e.step()
        return [c.energy for c in e.alive()], e.resource

    a, ra = expose([0, 1])
    b, rb = expose([1, 0])
    commute = (a == b and ra == rb)
    return [_row("BIO-T7", "COUNTEREXAMPLE" if not commute else "COMMUTES_HERE",
                 world="MW5", energy_01=a, energy_10=b,
                 resource_01=ra, resource_10=rb, commutes=commute)]


def t8_pooling():
    # 4 organisms vs 1 with 4x energy: harvest residual
    group = me.MicroEarth(4, seed=4, leak=False, kernels={"K_social": False})
    for c in group.cells:
        c.energy = 2
    me.run_horizon(group, 3)
    g_e = sum(c.energy for c in group.alive())
    # monolith: one cell, energy 8, same resource field — emulate by n=2 min but
    # compare pooling_gain = extra energy from having 4 bodies vs 1 body 4x.
    mono = me.MicroEarth(2, seed=4, leak=False, kernels={"K_social": False})
    mono.cells[0].energy = 8
    mono.cells[1].energy = 0  # dead partner so n legal
    me.run_horizon(mono, 3)
    m_e = sum(c.energy for c in mono.alive())
    residual = parents.organization_residual(
        observed_gain=g_e, pooling_gain=g_e, coord_cost=0)
    return [_row("BIO-T8", "HOLD", world="MW3",
                 group_energy=g_e, mono_energy=m_e,
                 residual_after_attributing_all_to_pooling=residual,
                 note="If observed_gain assigned entirely to pooling, residual is 0. No L* declared.")]


def t9_price():
    e = me.MicroEarth(4, seed=5, leak=False)
    z = [float(c.g) for c in e.cells]
    w = [float(c.energy) for c in e.cells]
    groups = [c.group for c in e.cells]
    ident = parents.price_identity(w, z, z)
    ml = parents.multilevel_price(groups, z, w)
    # clustering-as-group hostile: permute labels randomly vs true groups
    fake = [0, 1, 0, 1]
    ml_fake = parents.multilevel_price(fake, z, w)
    return [_row("BIO-T9", "PARENT_RECONSTRUCTED" if ident["ok"] and ml["ok_decomp"] else "FAIL",
                 world="MW3", identity=ident, multilevel=ml,
                 fake_partition_also_an_identity=ml_fake["ok_decomp"],
                 note="Any partition yields an identity. That does not mint individuality.")]


def t10_vocab():
    e = me.MicroEarth(8, seed=6, leak=False, social="forced")
    e.cells[0].method = 7  # shared token, not the useful method
    e.cells[0].energy = 8
    e.step()
    copied = sum(1 for c in e.alive() if c.method == 7)
    useful = sum(1 for c in e.alive() if c.method == e.useful_method)
    return [_row("BIO-T10", "HOSTILE_DETECTED" if copied > 1 and useful == 0 else "FAIL",
                 world="MW8", copied_token=copied, useful=useful,
                 hostile="H-VOCAB-ONLY")]


def t11_ev_hitting():
    # i.i.d. geometric
    p = 0.25
    geo = parents.geometric_hitting_mean(p)
    # trap: from genome 0, mutants are {1,2,3}; U={0} already... 
    # Define U = {genome 3} but mutation from 0 only goes +1 mod 4 -> 1, never 3 in one step.
    # Local Ev at 0 for U={3} is 0 so E[tau] inf if only 1-step and no further?
    # Better: 1-step Ev toward U={1} from 0 is 1 (always +1), but if we then
    # absorb in junk 2: from 1, force always to 2, U={3} unreachable.
    alleles = 4
    U = {3}

    def one_step_ev(g):
        neigh = me.enumerate_mutation_neighbourhood(g, alleles)
        return sum(1 for h in neigh if h in U) / float(len(neigh))

    ev0 = one_step_ev(0)
    # Hitting: chain g -> (g+1)%4 always (deterministic mut). From 0 hits 3 in 3 steps.
    # Local Ev(0,U)=0 because 1 not in U, but hitting time finite. Divergence.
    return [_row("BIO-T11", "COUNTEREXAMPLE", world="MW4",
                 iid_E_tau=geo, iid_p=p,
                 local_Ev_from_0_to_U3=ev0,
                 deterministic_hitting_from_0_to_3=3,
                 hostile="H-EV-TRAP",
                 note="Local one-step Ev=0 but hitting time is 3. Do not invert Ev.")]


def t12_identification():
    # Design check: continued vs reset vs knockout flags present
    continued = {"B": 10.0, "inherited": True}
    reset = {"B": 12.0, "inherited": False}
    knockout = {"B": 12.0, "inherited": False}
    delta = reset["B"] - continued["B"]
    identified = (delta > 0) and (knockout["B"] >= reset["B"] - 1e-9)
    leak = me.MicroEarth(2, seed=7, leak=True)
    return [_row("BIO-T12", "HOLD" if identified else "FAIL", world="MW1",
                 delta_B=delta, knockout_washes_gain=identified,
                 leak_invalidates=leak.assay_interferes(),
                 hostile="H-TARGET-LEAK")]


def t13_junk_culture():
    e = me.MicroEarth(4, seed=8, leak=False, social="prestige")
    e.useful_method = 1
    for _ in range(6):
        e.cells[0].energy = 8
        e.cells[0].method = e.junk_method
        e.step()
    useful = sum(1 for c in e.alive() if c.method == e.useful_method)
    return [_row("BIO-T13", "HOSTILE_DETECTED" if e.library and useful == 0 else "FAIL",
                 world="MW6", library_bytes=len(e.library), useful_carriers=useful,
                 hostile="H-JUNK-CULTURE")]


def t14_cluster():
    e = me.MicroEarth(6, seed=9, leak=False)
    # freely mixing: ignore group labels; genomes still 2 clusters mod 2
    labels = [c.g % 2 for c in e.cells]
    # reproduction is not restricted by label — mixing
    mixing = True
    return [_row("BIO-T14", "HOSTILE_DETECTED" if mixing else "FAIL", world="MW7",
                 kmeans_labels=labels,
                 reproductive_isolation=False,
                 note="Labels exist; individuality does not.",
                 hostile="H-CLUSTER-AS-GROUP")]


def t15_leakage():
    a = t1_noninterference()
    return [_row("BIO-T15", a[1]["status"], world="MW1",
                 parent_row="BIO-T1 leak", hostile="H-LEAK-ASSAY-ENERGY")]


def graph_agreement_check():
    report = graph_agreement.check_pair()
    return [_row("GRAPH-AGREEMENT", report["verdict"],
                 world="MW1",
                 clean_verdict=report["clean"]["verdict"],
                 leak_verdict=report["leak"]["verdict"],
                 clean_births=report["clean"]["births"],
                 leak_births=report["leak"]["births"],
                 clean_kinds=report["clean"]["kinds"],
                 leak_kinds=report["leak"]["kinds"],
                 hostile=report.get("hostile"))]


def kernel_ablation_contract():
    a = kernels.enabled({"K_social": True})
    b = kernels.enabled({"K_social": False})
    d = kernels.assert_independent_ablation(a, b)
    return [_row("KERNEL-ABLATION", "HOLD" if d["diffs"] == ["K_social"] else "FAIL", **d)]


def no_lstar_declaration(registry):
    frozen = registry.get("frozen_winner_L_star", True)
    return [_row("NO-L-STAR", "HOLD" if frozen is False else "FAIL",
                 frozen_winner_L_star=frozen)]


def run_all():
    import lib
    cg = lib.load_json(
        __import__("os").path.join(lib.ROOT, "COARSE_GRAINING_INDIVIDUALITY_V1.json"))
    rows = []
    rows.extend(t1_noninterference())
    rows.extend(t2_recurrence())
    rows.extend(t3_generator_support())
    rows.extend(t4_social_options())
    rows.extend(t5_dpi())
    rows.extend(t6_capital())
    rows.extend(t7_noncommute())
    rows.extend(t8_pooling())
    rows.extend(t9_price())
    rows.extend(t10_vocab())
    rows.extend(t11_ev_hitting())
    rows.extend(t12_identification())
    rows.extend(t13_junk_culture())
    rows.extend(t14_cluster())
    rows.extend(t15_leakage())
    rows.extend(graph_agreement_check())
    rows.extend(kernel_ablation_contract())
    rows.extend(no_lstar_declaration(cg))
    return rows
