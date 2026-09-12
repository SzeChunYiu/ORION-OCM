"""RV-377-101 / gap DG-9 — the best-constant control, computed for every ecology the corpus uses.

WHY. `RV-377-100` recovered a genotype the descriptor called DENSE, admissible, robust under all six registered
interventions and surviving full-set atrophy. Its wiring was `DENSE(width 1) -> LINEAR -> OUTPUT` with the INPUT node
and the TARGET node BOTH UNWIRED: it read neither the query nor the feedback and emitted a constant. It cleared
theta = 0.85 on `E_sym3` because the best constant clears theta on `E_sym3`.

An admissibility threshold only means something if a machine that ignores its input and its feedback fails it. This
module computes, for every ecology in the corpus, the capability of the BEST CONSTANT ANSWER, and marks any ecology
whose best constant reaches theta as NON_DISCRIMINATING at that theta.

The constant is optimised over the full fixed-point grid the instrument admits, so this is the strongest constant
available to an adversary, not a convenient one.
"""
import json
import os

from . import ecology, smooth

THETA = smooth.THETA
FX = smooth.FX_ONE
RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microscopes", "results")


def best_constant(target, eval_set):
    """capability of the best single fx constant, and the constant attaining it."""
    best = (-1.0, None)
    for c in range(-128, 128):
        err = sum(abs(c - target[x]) for x in eval_set) / FX / len(eval_set)
        cap = max(0.0, 1 - err / 1.5)
        if cap > best[0]:
            best = (round(cap, 4), c)
    return best


def audit(theta=THETA):
    rows = {}
    # the five registered ecologies, under both evaluation criteria
    for name, spec in ecology.REGISTRY.items():
        t = ecology.target_of(spec)
        for crit, ev in (("unseen", smooth.UNSEEN), ("all", smooth.ALL_X)):
            cap, c = best_constant(t, ev)
            rows[f"{name}|{crit}"] = {"family": "registered", "best_constant_capability": cap, "constant_fx": c,
                                      "theta": theta, "discriminating": cap < theta}
    # the E_sym(k) family: k/16 in all four coefficients, k = 0..16. Used by RV-377-021/025 for the
    # three-class admissible-set work, and never checked against a constant.
    for k in range(0, 17):
        t = smooth.make_target((k / 16,) * 4)
        for crit, ev in (("unseen", smooth.UNSEEN), ("all", smooth.ALL_X)):
            cap, c = best_constant(t, ev)
            rows[f"E_sym{k}|{crit}"] = {"family": "E_sym(k) sweep", "k": k, "best_constant_capability": cap,
                                        "constant_fx": c, "theta": theta, "discriminating": cap < theta}
    bad = sorted(k for k, v in rows.items() if not v["discriminating"])
    receipt = {"schema": "GMIConstantControlAuditV1", "revival_record": "RV-377-101", "gap": "DG-9",
               "theta": theta, "constant_grid": "every fx value in [-128, 127] on the registered 8-bit instrument",
               "n_ecology_criterion_pairs": len(rows), "rows": rows,
               "non_discriminating": bad, "n_non_discriminating": len(bad),
               "claim_ceiling": "this measures only whether a constant clears theta. An ecology that IS "
                                "discriminating by this test may still be weak for other reasons; passing it is "
                                "necessary, not sufficient."}
    receipt["receipt_sha256"] = ecology.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, "STAGE_DG9_CONSTANT_CONTROL_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


# =====================================================================================================================
# DG-9, extended to the E1 and E3 families -- the last uncovered surface, named by RV-377-104.
#
# PREMISE CORRECTION, recorded here because it changes what the instrument can be. There is exactly ONE ecology
# registry in the corpus, `ecology.REGISTRY`, its `family` field takes only the values "smooth" and "table", and
# NEITHER an E1 nor an E3 family is in it. `E1` and `E3` are programme STAGES: E1 is the stage of exact-layer ability
# microscopes for the predicted forms (`gmi_microscope/e1_*.py`), E3 is the real-mathematics / code validation gate.
# Their ecologies are declared inside their own modules with their OWN capability metrics, which is exactly why
# RV-377-101's sweep above could not reach them.
#
# The consequence for the instrument is not cosmetic. `best_constant` above is hard-wired to the B1 layer's
# MEAN-ABSOLUTE-ERROR capability `cap = max(0, 1 - err/1.5)`. Every E1 ecology scores by EXACT AGREEMENT instead -- a
# fraction of evaluated queries, sometimes within a 1 fx tolerance and sometimes exactly. Running `best_constant` on
# them would return a number with no relation to the threshold those claims were taken against. This section
# therefore computes the best constant under EACH family's own metric, over the same full fx grid.
#
# The E_ambig / E_noisy half of DG-9 was closed in closed form by RV-377-104 (their Brier SKILL metric puts the best
# constant at exactly 0.0 by construction) and is recorded in the ledger, not in this module. `audit()` above is
# unchanged.
#
# CEILING. This closes only the rule-40 (constant-answer) half. No fixed-function null (rule 42) has ever been run on
# any E1 or E3-lite ecology; a machine that reads its input but ignores its feedback is not caught by anything here.

FX_UNIT_CAP = 1.0 / (1.5 * FX)      # rule 40's declared conversion: one fx unit of mean absolute error, in capability


def best_constant_agree(target_by_q, eval_qs, tol=0):
    """Capability of the best single constant under the EXACT-AGREEMENT metric the E1 family uses:
    cap = fraction of evaluated queries whose served answer is within `tol` fx units of the obligation.

    The constant is swept over the same full fixed-point grid as `best_constant`, so this is the strongest constant
    available to an adversary on that instrument, not a convenient one."""
    best = (-1.0, None)
    for c in range(-128, 128):
        cap = sum(1 for q in eval_qs if abs(c - target_by_q[q]) <= tol) / len(eval_qs)
        if cap > best[0]:
            best = (round(cap, 4), c)
    return best


def _classify(cap, theta, quantum):
    """rule 40: NON_DISCRIMINATING if the constant reaches theta; otherwise the margin, in three units. A margin below
    one quantum of the metric ACTUALLY USED separates nothing and is flagged, per rule 40's quantization clause."""
    margin = round(theta - cap, 6)
    return {"best_constant_capability": cap, "theta": theta, "discriminating": cap < theta,
            "margin_capability": margin,
            "margin_rule40_fx_units": round(margin / FX_UNIT_CAP, 4),
            "metric_quantum": round(quantum, 6),
            "margin_metric_quanta": round(margin / quantum, 4),
            "verdict": ("NON_DISCRIMINATING" if cap >= theta else
                        "WITHIN_QUANTIZATION" if margin < quantum else "DISCRIMINATING")}


# ------------------------------------------------------------------ E1: the factored ecologies and their revisions
def _e1_initial_coeffs():
    """the declared opening coefficients, identical in e1_vlc.run, e1_cp.run, e1_lineage.run, e1_lmhm.run, e1_scdi.run."""
    from .e1_vlc import COEFF_VALUES as CV, N_F
    return [(CV[(2 * i) % 4], CV[(2 * i + 1) % 4]) for i in range(N_F)]


def _e1_revise(coeffs, i, u, d0=1, d1=2):
    """the registered per-factor revision step (e1_vlc.run line 'coeffs[i] = (COEFF_VALUES[...])'); the (d0, d1)
    offsets are (1, 2) everywhere except e1_cp's N3 alternate coefficients, which use (3, 1)."""
    from .e1_vlc import COEFF_VALUES as CV
    return (CV[(coeffs[i][0] // 4 + d0 + u) % 4], CV[(coeffs[i][1] // 4 + d1 + u) % 4])


def _coeffs_vlc(U, cone):
    from .e1_vlc import N_F
    c = _e1_initial_coeffs()
    for u in range(U):
        for i in [(u + j) % N_F for j in range(cone)]:
            c[i] = _e1_revise(c, i, u)
    return c


def _coeffs_lmhm():
    from . import e1_lmhm
    c = _e1_initial_coeffs()
    for u in range(e1_lmhm.U_ROUNDS):
        for i in e1_lmhm.revised_at(u):
            c[i] = _e1_revise(c, i, u)
    return c


def _coeffs_vgsc(pa_cell):
    from . import e1_vgsc
    from .e1_vlc import COEFF_VALUES as CV, N_F
    steps = e1_vgsc.STEP_SEQ[pa_cell]
    idx = [[(2 * i) % 4, (2 * i + 1) % 4] for i in range(N_F)]
    k = [0] * N_F
    for u in range(e1_vgsc.U_ROUNDS):
        i = u % N_F
        st = steps[k[i]]; k[i] += 1
        idx[i] = [(idx[i][0] + st) % 4, (idx[i][1] + st) % 4]
    return [(CV[idx[i][0]], CV[idx[i][1]]) for i in range(N_F)]


def _coeffs_cp(shared=True, U=8):
    """e1_cp.run's two coefficient vectors after the cell's U revision windows: regime A always reads the shared
    vector; under the N3 cell regimes B and C read an independent one."""
    from .e1_vlc import COEFF_VALUES as CV, N_F
    c = _e1_initial_coeffs()
    alt = [(CV[(3 - i) % 4], CV[(2 + 3 * i) % 4]) for i in range(N_F)]
    for w in range(U):
        i = w % N_F
        c[i] = _e1_revise(c, i, w)
        if not shared:
            alt[i] = _e1_revise(alt, i, w, d0=3, d1=1)
    return c, alt


def _coeffs_lineage(U=8):
    """e1_lineage.run's current coefficients and its version history (history[0] is the opening state)."""
    from .e1_vlc import N_F
    c = _e1_initial_coeffs(); history = [list(c)]
    for u in range(U):
        i = u % N_F
        c[i] = _e1_revise(c, i, u)
        history.append(list(c))
    return c, history


def _factored_queries(scope_size, criterion):
    """the ecology's registered evaluation set (`unseen`) or its complete query space (`all`)."""
    from .e1_vlc import EVAL_BY_SIZE, SCOPES_BY_SIZE
    if criterion == "unseen":
        return EVAL_BY_SIZE[scope_size]
    return [(x, s) for s in SCOPES_BY_SIZE[scope_size] for x in range(256)]


def _factored_target(coeffs, queries, regime=None, module=None):
    from . import e1_cp, e1_scdi, e1_vlc
    if regime is None:
        return {q: e1_vlc.truth(coeffs, *q) for q in queries}
    tr = e1_scdi.truth_regime if module == "scdi" else e1_cp.truth_regime
    return {q: tr(coeffs, q[0], q[1], regime) for q in queries}


def _alias_targets():
    """e1_iql's 25-query obligation at each of the 16 ground-truth orientations. The world model is charged, so a
    Machine is required; the charges are irrelevant to this audit and are discarded."""
    from . import bases, e1_iql
    from .core import Machine
    M = Machine(bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"], seed=0)
    return {d: e1_iql.target_vector(M, d) for d in e1_iql.ORIENTATIONS}


# ------------------------------------------------------------------ E3-lite: the neutral-search recovery ecologies
def _e3lite_ecologies():
    from . import blind
    eco = dict(blind.ecologies())
    eco.update(blind.ecologies(run3=True))
    eco.update(blind.ecologies(run4=True))
    eco["E_smooth8_div"] = blind.ecology_div()
    return eco


def _best_constant_bind(target, eval_set):
    """blind.run_candidate's label metric: the served value is thresholded at fx(0.5) before comparison."""
    from .core import fx
    best = (-1.0, None)
    for c in range(-128, 128):
        lab = int(c > fx(0.5))
        cap = sum(1 for x in eval_set if lab == int(bool(target[x]))) / len(eval_set)
        if cap > best[0]:
            best = (round(cap, 4), c)
    return best


def _best_constant_div(targets, eval_set):
    """blind.run_candidate_div's metric: the mean over the declared targets of the mean-abs-error capability."""
    best = (-1.0, None)
    for c in range(-128, 128):
        caps = []
        for t in targets:
            err = sum(abs(c - t[x]) for x in eval_set) / FX / len(eval_set)
            caps.append(max(0.0, 1 - err / 1.5))
        cap = round(sum(caps) / len(caps), 4)
        if cap > best[0]:
            best = (cap, c)
    return best


def audit_e1_e3(theta=THETA):
    """The best-constant control for every E1 and E3 ecology, each under its OWN metric, under both criteria."""
    from . import blind, e1_cp, e1_lineage, e1_lmhm, e1_scdi, e1_vgsc, e1_vlc
    rows = {}

    def put(key, family, ecology_name, variant, metric, cap, c, th, quantum, n_eval, note=None):
        r = {"family": family, "ecology": ecology_name, "variant": variant, "metric": metric,
             "constant_fx": c, "n_eval_queries": n_eval}
        r.update(_classify(cap, th, quantum))
        if note:
            r["note"] = note
        rows[key] = r

    # ---- E1.1  e1_vlc / e1_lmhm / e1_vgsc / e1_lineage: the exact-sum factored obligation, tolerance 1 fx
    vlc_variants = [("RSTAR_T3_T4(U=8,cone=1)", _coeffs_vlc(8, 1), 2),
                    ("T1_STATIONARY(U=0)", _coeffs_vlc(0, 1), 2),
                    ("T2_DENSE_CONE(U=8,cone=4)", _coeffs_vlc(8, 4), 2),
                    ("CQU1_LOCAL_Q(U=8,cone=1,scope=1)", _coeffs_vlc(8, 1), 1),
                    ("CQU2_GLOBAL_Q(U=8,cone=1,scope=4)", _coeffs_vlc(8, 1), 4),
                    ("CQU3_LOCAL_Q(U=8,cone=4,scope=1)", _coeffs_vlc(8, 4), 1),
                    ("CQU4_GLOBAL_Q(U=8,cone=4,scope=4)", _coeffs_vlc(8, 4), 4)]
    for name, coeffs, ss in vlc_variants:
        for crit in ("unseen", "all"):
            qs = _factored_queries(ss, crit)
            cap, c = best_constant_agree(_factored_target(coeffs, qs), qs, tol=1)
            put(f"e1_vlc|E_factored|{name}|{crit}", "E1", "E_factored", name,
                "exact agreement within 1 fx", cap, c, e1_vlc.THETA, 1 / len(qs), len(qs))

    for crit in ("unseen", "all"):
        qs = _factored_queries(2, crit)
        cap, c = best_constant_agree(_factored_target(_coeffs_lmhm(), qs), qs, tol=1)
        put(f"e1_lmhm|E_factored|HETEROGENEOUS(U=16)|{crit}", "E1", "E_factored", "HETEROGENEOUS(U=16)",
            "exact agreement within 1 fx", cap, c, e1_lmhm.THETA, 1 / len(qs), len(qs))

    for pa in sorted(e1_vgsc.STEP_SEQ):
        for crit in ("unseen", "all"):
            qs = _factored_queries(2, crit)
            cap, c = best_constant_agree(_factored_target(_coeffs_vgsc(pa), qs), qs, tol=1)
            put(f"e1_vgsc|E_factored|{pa}|{crit}", "E1", "E_factored", pa,
                "exact agreement within 1 fx", cap, c, e1_vgsc.THETA, 1 / len(qs), len(qs))

    lin_cur, lin_hist = _coeffs_lineage()
    lineage_variants = [("E_EPHEMERAL(current)", lin_cur),
                        ("P_PERSISTENT_D1(as-of v=%d)" % max(0, len(lin_hist) - 1 - 1), lin_hist[max(0, len(lin_hist) - 1 - 1)]),
                        ("P_PERSISTENT_D8(as-of v=%d)" % max(0, len(lin_hist) - 1 - 8), lin_hist[max(0, len(lin_hist) - 1 - 8)])]
    for name, coeffs in lineage_variants:
        for crit in ("unseen", "all"):
            # e1_lineage.CURRENT_QUERIES is exactly EVAL_BY_SIZE[2]: the same four unseen-pattern inputs on the six
            # 2-factor scopes. Asserted rather than assumed, so a future edit to either list is caught here.
            qs = _factored_queries(2, crit)
            assert crit == "all" or list(qs) == list(e1_lineage.CURRENT_QUERIES)
            cap, c = best_constant_agree(_factored_target(coeffs, qs), qs, tol=1)
            put(f"e1_lineage|E_factored|{name}|{crit}", "E1", "E_factored", name,
                "exact agreement within 1 fx", cap, c, e1_lineage.THETA, 1 / len(qs), len(qs))

    # ---- E1.2  e1_cp: three serving regimes over shared (and, under N3, independent) latent coefficients
    cp_shared, _ = _coeffs_cp(shared=True)
    _, cp_alt = _coeffs_cp(shared=False)
    cp_variants = [("A_shared", cp_shared, "A", 1), ("B_shared", cp_shared, "B", 0), ("C_shared", cp_shared, "C", 0),
                   ("B_N3_independent", cp_alt, "B", 0), ("C_N3_independent", cp_alt, "C", 0)]
    for name, coeffs, regime, tol in cp_variants:
        for crit in ("unseen", "all"):
            qs = _factored_queries(2, crit)
            cap, c = best_constant_agree(_factored_target(coeffs, qs, regime, "cp"), qs, tol=tol)
            put(f"e1_cp|E_factored3|{name}|{crit}", "E1", "E_factored3", name,
                f"exact agreement within {tol} fx", cap, c, e1_cp.THETA, 1 / len(qs), len(qs))

    # ---- E1.3  e1_scdi: four serving regimes, no revision, EXACT equality in every regime including A
    scdi_coeffs = _e1_initial_coeffs()
    for regime in e1_scdi.REGIMES:
        for crit in ("unseen", "all"):
            qs = _factored_queries(2, crit)
            cap, c = best_constant_agree(_factored_target(scdi_coeffs, qs, regime, "scdi"), qs, tol=0)
            put(f"e1_scdi|E_factored|regime_{regime}|{crit}", "E1", "E_factored", f"regime_{regime}",
                "exact equality", cap, c, e1_scdi.THETA, 1 / len(qs), len(qs))

    # ---- E1.4  e1_iql: the interventional obligation, swept over all 16 ground-truth orientations
    for d, tgt in _alias_targets().items():
        name = "".join(map(str, d))
        tm = {q: tgt[q] for q in range(len(tgt))}
        for crit in ("unseen", "all"):
            cap, c = best_constant_agree(tm, list(range(len(tgt))), tol=0)
            put(f"e1_iql|E_alias|d={name}|{crit}", "E1", "E_alias", f"d={name}",
                "exact equality", cap, c, 0.85, 1 / len(tgt), len(tgt),
                note="the obligation IS the complete 25-query set, so the two criteria coincide by construction")

    # ---- E3: the real-mathematics / code lane has no executed ecology at all (recorded, not skipped)
    e3_proper = {"family": "E3", "ecology": "(none executed)",
                 "status": "NO_EXECUTED_ECOLOGY",
                 "evidence": "GMI_E3_EXECUTION_GATES_V1.json: FORMAL_MATHEMATICS_LEAN is "
                             "LOCKED_BY_ISSUE_46_PREDECESSOR_RULE and coding is H0 infrastructure only; "
                             "GMI_E3_STATUS_V1.md calls the tranche 'a design/schema result, not real capability "
                             "evidence'; GMI_E3_REAL_COGNITION_EPISODE_V1.json is "
                             "FROZEN_COMMON_SEMANTIC_CONTRACT__NO_PROTECTED_OUTCOME_ACCESSED.",
                 "why_no_control_is_computable": "E3 admissibility is a BOOLEAN external-verifier pass "
                                                 "(`admissible_result` in map_proof_replay_to_gmi_e3.py and "
                                                 "map_code_h0_trace_to_gmi_e3.py), not a capability compared to a raw "
                                                 "theta. There is no capability metric, no answer alphabet and no "
                                                 "theta, so no best constant is definable -- and, correspondingly, no "
                                                 "E3 positive admissibility claim exists for this audit to void."}

    # ---- E3-lite: the neutral-search recovery lane (blind.py / qd.py), which DOES use a raw threshold
    for name, eco in sorted(_e3lite_ecologies().items()):
        all_x = eco["all_x"]; train = set(eco["train"])
        unseen = [x for x in all_x if x not in train] or list(all_x)
        th = blind.THETA_BIND if eco["kind"] == "bind" else blind.THETA_SMOOTH
        for crit, ev in (("unseen", unseen), ("all", list(all_x))):
            if eco["kind"] == "bind":
                cap, c = _best_constant_bind(eco["target"], ev)
                metric, quantum = "label accuracy (served value thresholded at fx(0.5))", 1 / len(ev)
            elif eco["kind"] == "smooth_div":
                cap, c = _best_constant_div(eco["targets"], ev)
                metric, quantum = "mean over 4 declared targets of the mean-abs-error capability", FX_UNIT_CAP
            else:
                cap, c = best_constant(eco["target"], ev)
                metric, quantum = "mean-abs-error capability, cap = max(0, 1 - err/1.5)", FX_UNIT_CAP
            put(f"blind|{name}|registered|{crit}", "E3-lite", name, "registered", metric, cap, c, th, quantum, len(ev))

    bad = sorted(k for k, v in rows.items() if not v["discriminating"])
    bad_variants = sorted({k.rsplit("|", 1)[0] for k in bad})
    receipt = {"schema": "GMIConstantControlE1E3AuditV1", "gap": "DG-9",
               "extends": "RV-377-101 (registered ecologies + E_sym(k)) and RV-377-104 (E_ambig / E_noisy)",
               "theta_default": theta,
               "constant_grid": "every fx value in [-128, 127] on the registered 8-bit instrument",
               "premise_correction": "ecology.REGISTRY contains no E1 or E3 family; E1 and E3 are programme stages "
                                     "whose ecologies are declared inside their own modules with their own metrics. "
                                     "best_constant() above is hard-wired to the B1 mean-absolute-error capability "
                                     "and is not applicable to them; each row here is computed under the metric its "
                                     "own microscope uses.",
               "units": "rule 40's fx unit, 1/(1.5*16) = 0.0416667 capability, is a unit of MEAN ABSOLUTE ERROR and "
                        "is not the quantum of an exact-agreement metric. Every row reports the margin in capability, "
                        "in rule-40 fx units, and in units of the metric actually used; WITHIN_QUANTIZATION is "
                        "decided on the latter.",
               "n_rows": len(rows), "n_variants": len(rows) // 2, "rows": rows,
               "e3_proper": e3_proper,
               "non_discriminating": bad, "n_non_discriminating": len(bad),
               "non_discriminating_variants": bad_variants, "n_non_discriminating_variants": len(bad_variants),
               "claim_ceiling": "this closes only the rule-40 constant-answer half of DG-9 for these families. NO "
                                "fixed-function null (rule 42) has ever been run on any E1 or E3-lite ecology, so a "
                                "machine that reads its input but ignores its feedback is not caught here. A "
                                "DISCRIMINATING verdict is necessary, not sufficient."}
    receipt["receipt_sha256"] = ecology.sha256_of({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    os.makedirs(RES, exist_ok=True)
    json.dump(receipt, open(os.path.join(RES, "STAGE_DG9_CONSTANT_CONTROL_E1_E3_V1.json"), "w"),
              indent=1, sort_keys=True, default=str)
    return receipt


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "registered"):
        r = audit()
        print(f"theta = {r['theta']}   pairs audited = {r['n_ecology_criterion_pairs']}")
        print(f"\n{'ecology|criterion':22s} {'best const':>10s} {'c':>5s}  discriminating")
        for k in sorted(r["rows"], key=lambda x: (r["rows"][x]["discriminating"], x)):
            v = r["rows"][k]
            print(f"  {k:20s} {v['best_constant_capability']:10.4f} {v['constant_fx']:5d}  "
                  f"{'yes' if v['discriminating'] else 'NO  <-- NON_DISCRIMINATING'}")
        print(f"\nNON-DISCRIMINATING: {r['n_non_discriminating']} of {r['n_ecology_criterion_pairs']}")
        print(f"  {r['non_discriminating']}")
    if which in ("all", "e1e3"):
        r2 = audit_e1_e3()
        print(f"\n\n==== E1 / E3 ====   rows = {r2['n_rows']}   variants = {r2['n_variants']}")
        print(f"{'row':64s} {'theta':>6s} {'best const':>11s} {'c':>5s}  verdict")
        for k in sorted(r2["rows"], key=lambda x: (r2["rows"][x]["discriminating"], x)):
            v = r2["rows"][k]
            print(f"  {k:62s} {v['theta']:6.2f} {v['best_constant_capability']:11.4f} {v['constant_fx']:5d}  "
                  f"{v['verdict']}{'  <--' if not v['discriminating'] else ''}")
        print(f"\nE3 proper: {r2['e3_proper']['status']}")
        print(f"NON-DISCRIMINATING: {r2['n_non_discriminating']} of {r2['n_rows']} rows; "
              f"{r2['n_non_discriminating_variants']} of {r2['n_variants']} variants")
        for k in r2["non_discriminating"]:
            print(f"  {k}")
