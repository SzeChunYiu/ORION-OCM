import json
from pathlib import Path

from gmi_microscope import bases, runner
from gmi_microscope.core import FX_MAX, FX_MIN, Machine, fx

HERE = Path(__file__).resolve().parent
RES = HERE / "microscopes" / "results"


def test_emulated_arithmetic_is_exact_everywhere():
    MU = Machine(bases.U)
    for name, B in bases.ALL.items():
        MB = Machine(B)
        for a in range(FX_MIN, FX_MAX + 1, 3):
            for b in range(FX_MIN, FX_MAX + 1, 5):
                assert MB.op("MUL", a, b) == MU.op("MUL", a, b), (name, a, b)
                assert MB.op("ADD", a, b) == MU.op("ADD", a, b), (name, a, b)
                assert MB.op("SUB", a, b) == MU.op("SUB", a, b), (name, a, b)
                assert MB.op("GT", a, b) == int(a > b)


def test_sample_is_bit_identical_native_vs_emulated():
    for seed in (0, 1, 7):
        MB3 = Machine(bases.B3, seed=seed)
        MB0 = Machine(bases.B0, seed=seed)
        seq3 = [MB3.op("SAMPLE", p) for p in (0.1, 0.5, 0.9) * 20]
        seq0 = [MB0.op("SAMPLE", p) for p in (0.1, 0.5, 0.9) * 20]
        assert seq3 == seq0


def test_dev_tables_identical_across_columns_every_row_and_size():
    for row, cls in runner.ROWS.items():
        for size in cls.ladder:
            ds = [runner.run(row, bases.ALL[b], size)["D"] for b in bases.ALL]
            assert all(d == ds[0] for d in ds), (row, size)


def test_cost_asymmetries_have_the_predicted_sign():
    M = lambda B: Machine(B)
    mB2 = M(bases.B2); mB2.op("MUL", fx(1.5), fx(-2.0))
    mB1 = M(bases.B1); mB1.op("MUL", fx(1.5), fx(-2.0))
    assert mB2.L.c["exec"] > 8 * mB1.L.c["exec"]
    sB3 = M(bases.B3); sB3.op("SAMPLE", 0.3)
    sB0 = M(bases.B0); sB0.op("SAMPLE", 0.3)
    assert sB3.L.c["exec"] < sB0.L.c["exec"]


def test_committed_receipts_match_code():
    from gmi_microscope import matrix
    rc = matrix.main()
    committed = json.loads((RES / "STAGE_D_MATRIX_V1.json").read_text())
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert all(rc["C2_dev_table_identical_across_columns"].values())
    assert rc["matrix_flat_within_K_FLAT_on_all_coords"] is False


def test_r2_r3_r4_receipts_match_code():
    from gmi_microscope import matrix_r2, matrix_r3, matrix_r4
    for mod, name in ((matrix_r2, "STAGE_D_MATRIX_R2.json"), (matrix_r3, "STAGE_D_MATRIX_R3.json"), (matrix_r4, "STAGE_D_MATRIX_R4.json")):
        rc = mod.main()
        committed = json.loads((RES / name).read_text())
        assert committed["receipt_sha256"] == rc["receipt_sha256"], name
    r4 = json.loads((RES / "STAGE_D_MATRIX_R4.json").read_text())
    assert r4["all_hold"] is True
    # per-query exec of the indexed exemplar memory is exactly 36 x (bit_length(n_store+1)+1) in every indexed column
    for col in ("B2", "U", "P3", "B0i", "B1i", "B3i"):
        assert [r4["per_phase_table"][f"M5|{col}"][str(n)]["query"] for n in (16, 32, 64, 128, 256)] == [216, 252, 288, 324, 360], col


def test_dead_write_elimination_preserves_score_and_prunes_only_dead_writes():
    from gmi_microscope import blind
    blind.set_bits(4)
    e = blind.ecologies()["E_bind"]
    cand = {"f": ["ADD", "c0", ["MUL", "x1", "c2"]], "g": [["c0", ["ADD", "c0", "e"]], ["c1", ["SUB", "y", "out"]], ["c2", ["MUL", "c3", "kh"]], ["c3", "e"], ["INSERT", "y"]]}
    pruned, dropped = blind.eliminate_dead_writes(cand)
    assert dropped == 2 and [w[0] for w in pruned["g"]] == ["c0", "c2", "c3"]
    assert blind.run_candidate(cand, e)["score"] == blind.run_candidate(pruned, e)["score"]


def test_smooth_v1_receipt_payload_frozen():
    from gmi_microscope import smooth
    committed = json.loads((RES / "STAGE_DE_SMOOTH_V1.json").read_text())
    rc_path = RES / "STAGE_DE_SMOOTH_V1.json"
    smooth.main()
    new = json.loads(rc_path.read_text())
    for k in ("R_by_cell", "capability_by_cell", "frontier_H_r", "PH_REV", "C2"):
        assert committed[k] == new[k], k


def test_smooth3_prediction_receipt_is_reproducible_and_was_frozen_before_the_run():
    from gmi_microscope import predict_smooth3
    committed = json.loads((RES / "STAGE_DE_SMOOTH3_PREDICTION.json").read_text())
    rc = predict_smooth3.main()
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert committed["n_called"] == 336 and committed["n_abstained"] == 0
    assert committed["certification_capabilities_B0"]["S5"] < 0.85 < committed["certification_capabilities_B0"]["S4"]


def test_smooth3_verdict_receipt_is_reproducible_and_positive():
    from gmi_microscope import compare_smooth3
    committed = json.loads((RES / "STAGE_DE_SMOOTH3_VERDICT.json").read_text())
    rc = compare_smooth3.main()
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert rc["verdict"]["all_claims_hold"] is True and rc["verdict"]["n_wrong"] == 0 and rc["verdict"]["n_called"] == 336


def test_sym2_prediction_receipt_is_reproducible_and_was_frozen_before_the_run():
    from gmi_microscope import predict_sym2
    committed = json.loads((RES / "STAGE_DE_SYM2_PREDICTION.json").read_text())
    rc = predict_sym2.main()
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert committed["per_ecology"]["SYM3"]["predicted_admissible"] == ["S4", "S2a", "S5h"]


def test_sym2_verdict_receipt_is_reproducible():
    from gmi_microscope import compare_sym2
    committed = json.loads((RES / "STAGE_DE_SYM2_VERDICT.json").read_text())
    rc = compare_sym2.main()
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert committed["verdict"]["C2_admissible_sets_as_predicted"] is True  # RV-377-025 recorded partial positive (C1 fails on one B2 cell, C6 fails: SHR macro)


def test_knn_row_matches_its_closed_form_and_the_defective_row_does_not():
    from gmi_microscope import smooth
    from gmi_microscope.predict_sym import knn_capability_closed_form
    for k in (3, 5, 8):
        target = smooth.make_target((k / 16,) * 4)
        good = smooth.run("S5h", bases.B0, 4, 0, target, 16, smooth.ROWS_V6, "unseen")["capability"]
        bad = smooth.run("S5k", bases.B0, 4, 0, target, 16, smooth.ROWS_V4, "unseen")["capability"]
        assert good == knn_capability_closed_form(k)
        assert bad != good  # RV-377-021 instrument defect (Boolean XOR) is preserved for receipt reproducibility


def test_xor_row_identifies_parity_only_on_a_spanning_split():
    from gmi_microscope import smooth
    tgt = smooth.make_parity_target()
    smooth.set_train(smooth.TRAIN_MIXED)
    try:
        assert smooth.run("S6", bases.B0, 4, 0, tgt, 16, smooth.ROWS_V5, "unseen")["capability"] == 1.0
    finally:
        smooth.set_train([0, 3, 5, 6, 9, 10, 12, 15])
    assert smooth.run("S6", bases.B0, 4, 0, tgt, 16, smooth.ROWS_V5, "unseen")["capability"] == 0.3333


def test_fast_evaluator_matches_charged_machine_on_random_candidates():
    import random
    from gmi_microscope import blind, fast
    blind.G_DEPTH = 3; blind.set_bits(8)
    rng = random.Random(2024)
    single = blind.ecologies(run4=True)["E_smooth8"]; div = blind.ecology_div()
    cands = [blind.rand_candidate(rng) for _ in range(60)] + [blind.PLANTED_LEARNER_SMOOTH8_LR4]
    for c in cands:
        assert fast.fast_run_candidate(c, single) == blind.run_candidate(c, single, 0)["score"]
    for c in cands[:20] + [blind.PLANTED_LEARNER_SMOOTH8_LR4]:
        assert fast.fast_run_candidate(c, div) == blind.run_candidate_div(c, div, 0)["score"]
    blind.set_bits(4)


def test_e1_vlc_receipt_cell_reproduces():
    from gmi_microscope import e1_vlc
    committed = json.loads((RES / "STAGE_E1_V13_E1_VLC.json").read_text())
    cell = committed["cells"]["RSTAR|VLC|B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    r = e1_vlc.run("VLC", bases.B0, 8, 1)
    for k in ("capability", "regressions", "wrong_served_in_window", "abstained_in_window", "desc_state", "R"):
        assert r[k] == cell[k], k


def test_e1_cp_receipt_cell_reproduces():
    from gmi_microscope import e1_cp
    committed = json.loads((RES / "STAGE_E1_V14_E1_CP.json").read_text())
    cell = committed["cells"]["PPLUS|CP|B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    r = e1_cp.run("CP", bases.B0, e1_cp.CELLS["PPLUS"])
    assert r["capability_by_regime"] == cell["capability_by_regime"] and r["R"] == cell["R"] and r["rebuilds"] == cell["rebuilds"]


def test_credit_receipt_cell_reproduces():
    from gmi_microscope import rl
    committed = json.loads((RES / "STAGE_DE_CREDIT_V11_CREDIT_E8.json").read_text())
    r = rl.run("R1", bases.B0, 4, 0, 8)
    assert r["capability"] == committed["capability_by_cell"]["R1|B0_LOCAL_ADAPTIVE_TRANSDUCERS|4"] and r["R"] == committed["R_by_cell"]["R1|B0_LOCAL_ADAPTIVE_TRANSDUCERS|4"]


def test_transformer_microfeature_exact_receipt_reproduces(tmp_path):
    """X-TMT1..15: the exact/numerical theorem checks are GREEN and the receipt is byte-reproducible (sha)."""
    import json
    from gmi_microscope import tmt
    r = tmt.main(str(tmp_path / "r.json"))
    assert r["status"] == "GREEN" and r["n_passed"] == 15
    ref = json.load(open(HERE / "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json"))
    assert ref["receipt_sha256"] == r["receipt_sha256"]


def test_morphology_ir_canonical_form_and_typecheck():
    """R0: canonical form is remint-invariant, distinguishes real edits, resolves automorphic ties; H1 typecheck rejects macros and type errors."""
    from gmi_microscope import morph, zoo
    for name, fn in zoo.ZOO.items():
        g = fn(); assert morph.typecheck(g)
        for s in (1, 2, 3): assert morph.canonical(morph.remint(g, s)) == morph.canonical(g), name
    assert len({morph.fingerprint(fn()) for fn in zoo.ZOO.values()}) == len(zoo.ZOO)
    g3 = morph.make({0: ("INPUT", {"width": 4}), 1: ("DENSE", {"width": 4}), 2: ("DENSE", {"width": 4}), 3: ("LINEAR", {}), 4: ("LINEAR", {}), 5: ("SUM", {}), 6: ("OUTPUT", {})}, [(1, 3, 0), (0, 3, 1), (2, 4, 0), (0, 4, 1), (3, 5, 0), (4, 5, 1), (5, 6, 0)])
    g3s = morph.make({0: ("INPUT", {"width": 4}), 1: ("DENSE", {"width": 4}), 2: ("DENSE", {"width": 4}), 3: ("LINEAR", {}), 4: ("LINEAR", {}), 5: ("SUM", {}), 6: ("OUTPUT", {})}, [(2, 3, 0), (0, 3, 1), (1, 4, 0), (0, 4, 1), (4, 5, 0), (3, 5, 1), (5, 6, 0)])
    assert morph.canonical(g3) == morph.canonical(g3s)
    import pytest
    with pytest.raises(morph.MorphError): morph.typecheck(morph.make({0: ("ATTENTION", {})}, []))
    with pytest.raises(morph.MorphError): morph.typecheck(morph.make({0: ("INPUT", {"width": 4}), 1: ("OUTPUT", {})}, [(0, 1, 0)]))


def test_vm_zoo_deterministic_and_remint_invariant_response():
    """R1/R4: every zoo genotype runs under the smooth ecology deterministically, and a reminted genotype has the identical charged response (H5)."""
    from gmi_microscope import smooth, morph, zoo
    from gmi_microscope.vm import VMRow
    B0 = bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]; target = smooth.make_target(smooth.COEFFS_V3)
    def runit(g):
        rows = {"IR": (lambda gg: (lambda size: VMRow(gg, size)))(g)}
        return smooth.run("IR", B0, 1, seed=0, target=target, n_events=16, rows=rows, criterion="unseen")
    expect = {"gradient_net_h4": 0.8021, "hamming_knn_k3": 0.8698, "exemplar_table": 0.7083, "particles_p4": 0.8958, "soft_retrieval": 0.8542}
    for name, cap in expect.items():
        g = zoo.ZOO[name](); r = runit(g); assert r["capability"] == cap, (name, r["capability"])
        r2 = runit(morph.remint(g, 5)); assert r2["R"] == r["R"] and r2["capability"] == cap, name


def test_b0_equivalence_receipt_reproduces(tmp_path):
    """B0: implementation-equivalent rewrites merge, collision pairs split, init audited; the receipt is deterministic."""
    from gmi_microscope import equiv
    o = equiv.main(tag="TEST_TMP")
    ref = json.load(open(RES / "STAGE_B0_EQUIVALENCE_METERING_V1.json"))
    (RES / "STAGE_B0_EQUIVALENCE_METERING_TEST_TMP.json").unlink()
    assert o["terminal"] == "BIOSPHERE_B0_EQUIVALENCE_AND_METERING_GREEN" and o["receipt_sha256"] == ref["receipt_sha256"]


def test_dn_sheaf_receipt_cell_reproduces():
    """N3 (RV-377-050): the candidate cell of the committed receipt replays exactly, and the sheaf row's answers are
    bit-identical to BOTH matched existing-domain parents' -- the bounded-reduction attack that decides criterion 3."""
    from gmi_microscope import dn_sheaf
    committed = json.loads((RES / "STAGE_DN_V26_N3_SHEAF.json").read_text())
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
    spec = dn_sheaf.CELLS["n8_d3_late"]
    eco = dn_sheaf.ecology(spec["n"], spec["d"], spec["rho_num"], spec["rho_den"], tail=spec.get("tail", False))
    out = {r: dn_sheaf.run(r, dn_sheaf._basis(col), eco) for r in ("SHEAF", "TABLE_MAT", "PROG_SEARCH")}
    for r, got in out.items():
        cell = committed["cells"][f"n8_d3_late|{r}|{col}"]
        for k in ("capability", "admissible", "R", "compile_ops", "exec_per_query", "desc_bits",
                  "native_ops", "native_compile_ops", "answer_signature"):
            assert got[k] == cell[k], (r, k, got[k], cell[k])
    assert out["SHEAF"]["answer_signature"] == out["TABLE_MAT"]["answer_signature"] == out["PROG_SEARCH"]["answer_signature"]
    assert committed["cells_spec"]["n8_d3_late"]["n"] == 8
    # the table parent's construction is exactly d^n (n-1) + d^2 charged ops
    assert out["TABLE_MAT"]["compile_ops"] == 3 ** 8 * 7 + 9


def test_dn_partialorder_receipt_cell_reproduces():
    """N10 (RV-377-051/052): the candidate cell of the committed receipt replays exactly under both precision
    instruments; the poset row equals both relational parents under the wide instrument, is interleaving-invariant
    while the sequence parent is not, and the registered 8-bit instrument gates it at chain length 12."""
    from gmi_microscope import dn_partialorder as dnp
    committed = json.loads((RES / "STAGE_DN_V27_N10_PARTIALORDER.json").read_text())
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
    eco = dnp.ecology(dnp.CELLS["w4_L12"]["w"], dnp.CELLS["w4_L12"]["L"])
    for prec in ("fx8", "wide"):
        for r in ("POSET", "PAIRTABLE", "SEQ_MEM", "PROG_SEARCH", "POSET_NOJOIN"):
            got = dnp.run(r, dnp._basis(col), eco, 0, prec, 0)
            cell = committed["cells"][f"w4_L12|{r}|{col}|{prec}|il0"]
            for k in ("capability", "admissible", "R", "learn_ops", "exec_per_query", "desc_bits",
                      "native_ops", "native_compile_ops", "answer_signature"):
                assert got[k] == cell[k], (prec, r, k, got[k], cell[k])
    wide = {r: dnp.run(r, dnp._basis(col), eco, 0, "wide", 0) for r in dnp.ROWS}
    il1 = {r: dnp.run(r, dnp._basis(col), eco, 0, "wide", 1) for r in dnp.ROWS}
    # exact developmental equality with both relational parents; the sequence parent and the twin differ
    assert wide["POSET"]["answer_signature"] == wide["PAIRTABLE"]["answer_signature"] == wide["PROG_SEARCH"]["answer_signature"]
    assert wide["POSET"]["answer_signature"] not in (wide["SEQ_MEM"]["answer_signature"], wide["POSET_NOJOIN"]["answer_signature"])
    # the domain discriminator: invariance under the observed interleaving
    for r in ("POSET", "PAIRTABLE", "PROG_SEARCH"):
        assert wide[r]["answer_signature"] == il1[r]["answer_signature"], r
    assert wide["SEQ_MEM"]["answer_signature"] != il1["SEQ_MEM"]["answer_signature"]
    # the precision gate: the registered 8-bit universe cannot hold a causal counter of range 12
    assert dnp.run("POSET", dnp._basis(col), eco, 0, "fx8", 0)["capability"] < wide["POSET"]["capability"]
    # the two laws proved out of sample by RV-377-052, checked on this cell
    assert abs(wide["SEQ_MEM"]["capability"] - eco["seq_mem_capability_upper_bound"]) <= 1e-4
    w, L = dnp.CELLS["w4_L12"]["w"], dnp.CELLS["w4_L12"]["L"]
    twin = round((eco["n_concurrent_pairs"] + w * L * (L - 1)) / eco["n_queries"], 4)
    assert abs(wide["POSET_NOJOIN"]["capability"] - twin) <= 1e-4
def test_dn_n8_autocatalytic_receipt_cell_reproduces():
    """N8 (RV-377-052): the L8 cell of STAGE_DN_V28_N8_AUTOCATALYTIC replays exactly, and the
    autocatalytic candidate is developmentally IDENTICAL to the oracle-fed memory parent."""
    from gmi_microscope import dn_autocatalytic as A
    committed = json.loads((RES / "STAGE_DN_V28_N8_AUTOCATALYTIC.json").read_text())
    eco = A.ecology(A.CELLS["L8"]["L"])
    for row in ("AUTOCAT_EAGER", "TABLE_FULL", "AUTOCAT_NOFEED"):
        r = A.run(row, bases.B0, eco)
        c = committed["cells"][f"L8|{row}"]
        assert (r["capability"], r["desc_bits"], r["compile_ops"], r["exec_per_query"], r["R"]) == \
               (c["capability"], c["desc_bits"], c["compile_ops"], c["exec_per_query"], c["R"]), row
        assert r["answer_signature"] == c["answer_signature"], row
    assert committed["cells"]["L8|AUTOCAT_EAGER"]["answer_signature"] == committed["cells"]["L8|TABLE_FULL"]["answer_signature"]
    assert committed["autocat_equals_parent_answers"]["L8|AUTOCAT_EAGER==TABLE_FULL"] is True
    assert committed["cells"]["L8|AUTOCAT_NOFEED"]["admissible"] is False


def test_dn_n11_obstruction_receipt_cell_and_growth_law():
    """N11 (RV-377-053/054): the m10_d2_k8 cell of STAGE_DN_V29_N11_OBSTRUCTION replays exactly;
    the candidate and the dense-coefficient parent answer identically (the bounded reduction), and the
    measured growth law is constant serve cost d*(2m+2) against exhaustion 2m + 3m*(2^k - 1)."""
    from gmi_microscope import dn_obstruction as O
    committed = json.loads((RES / "STAGE_DN_V29_N11_OBSTRUCTION.json").read_text())
    spec = O.CELLS["m10_d2_k8"]
    eco = O.ecology(spec["m"], spec["k"], spec["d"], n_eval=8, n_unsat_eval=5)
    assert eco["corank"] == spec["d"] and eco["rank"] == spec["m"] - spec["d"]
    for row in ("OBSTRUCT", "DENSE_RREF", "OBSTRUCT_NOCERT"):
        r = O.run(row, bases.B0, eco)
        c = committed["cells"][f"m10_d2_k8|{row}"]
        assert (r["capability"], r["desc_bits"], r["compile_ops"], r["exec_per_query"], r["R"]) == \
               (c["capability"], c["desc_bits"], c["compile_ops"], c["exec_per_query"], c["R"]), row
        assert r["answer_signature"] == c["answer_signature"], row
    assert committed["obstruct_equals_parent_answers"]["m10_d2_k8|OBSTRUCT==DENSE_RREF"] is True
    for cname, spec in O.CELLS.items():
        m, d, k = spec["m"], spec["d"], spec["k"]
        assert committed["cells"][f"{cname}|OBSTRUCT"]["exec_per_query"] == d * (2 * m + 2), cname
        if (1 << k) <= O.SEARCH_BUDGET:
            assert committed["cells"][f"{cname}|SEARCH_ENUM"]["exec_per_unsat_query"] == 2 * m + 3 * m * ((1 << k) - 1), cname
    ratios = [committed["growth_law_k_sweep"][c]["search_over_obstruct"]
              for c in sorted(committed["growth_law_k_sweep"], key=lambda c: committed["growth_law_k_sweep"][c]["k"])]
    assert len(ratios) >= 4
    for a, b in zip(ratios, ratios[1:]):
        assert 3.99 <= b / a <= 4.01, (a, b)
def test_dc_field_receipt_cell_reproduces():
    """DC2 (RV-377-046): one committed cell of the self-organizing-field microscope replays exactly, and the
    weight-sharing-ablated parent's answers equal the field row's in exactly the cells where it is capable."""
    from gmi_microscope import dc_field
    committed = json.loads((RES / "STAGE_DC_V30_DC2_FIELD.json").read_text())
    spec = committed["cells_spec"]["L32_r110_n128"]
    eco = dc_field.ecology(spec["L"], spec["T"], spec["rule"], spec["n_dev"])
    for row in ("FIELD", "FIELD_NONLOCAL"):
        r = dc_field.run(row, bases.B0, eco)
        cell = committed["cells"][f"L32_r110_n128|{row}"]
        for k in ("capability", "desc_bits", "exec_per_query", "native_ops", "learn_ops", "answer_signature", "R"):
            assert r[k] == cell[k], (row, k)
    assert committed["field_equals_field_nonlocal_answers"]["L32_r110_n128"] is True
    assert committed["separation_by_L"]["L32_r110"]["description_ratio"] == 32


def test_dc_quantum_receipt_cell_reproduces():
    """DC7 (RV-377-047): one committed cell replays exactly in both precision instruments, and the QQ family census
    separates the projective class (0 violations) from the ordered-Bayes class (94.7 per cent)."""
    from gmi_microscope import dc_quantum
    committed = json.loads((RES / "STAGE_DC_V31_DC7_QUANTUM.json").read_text())
    eco = dc_quantum.ecology(1, 4)
    for row in ("QPROJ", "BAYES_ORDERED", "TABLE", "QPROJ_COMMUTING"):
        for prec in ("fx8", "wide"):
            r = dc_quantum.run(row, bases.B0, eco, precision=prec)
            cell = committed["cells"][f"n1_Q4|{row}|{prec}"]
            for k in ("capability", "desc_bits", "exec_per_query", "native_per_query", "max_abs_error_units", "answer_signature", "R"):
                assert r[k] == cell[k], (row, prec, k)
    census = committed["qq_family_census"]["n1"]
    assert census["projective_frac_violating_tol"] == 0.0
    assert census["ordered_bayes_frac_violating_tol"] == 0.947456
    assert committed["analytic_crossovers"]["n1_Q4|wide|native"]["BAYES_ORDERED|QPROJ"] == 32 * 4 - 12


def test_dc_phase_receipt_cell_reproduces():
    """DC9 (RV-377-054): one committed cell replays exactly; the phase row equals the exemplar parent in its own code,
    and at Q = 2 with an odd bundle size it equals DC1's hyperdimensional row bit for bit."""
    from gmi_microscope import dc_phase
    committed = json.loads((RES / "STAGE_DC_V32_DC9_PHASE.json").read_text())
    spec = committed["cells_spec"]["D64_d1_k3_Q2_P64_s7"]
    eco = dc_phase.ecology(spec["D"], spec["depth"], spec["k"], spec["Dp"], spec["Q"],
                           noise=spec["noise"], phase_noise=spec["phase_noise"], seed=spec["rec_seed"])
    sigs = {}
    for row in dc_phase.ROWS:
        r = dc_phase.run(row, bases.B0, eco, precision="wide")
        cell = committed["cells"][f"D64_d1_k3_Q2_P64_s7|{row}|wide"]
        for k in ("capability", "desc_bits", "exec_per_query", "native_per_query", "answer_signature"):
            assert r[k] == cell[k], (row, k)
        sigs[row] = r["answer_signature"]
    assert sigs["PHASE"] == sigs["PHASE_STORE_MAT"] == sigs["VSA"]
    assert all(v["phase_equals_phase_store_mat"] for v in committed["cross_carrier_equality"].values())

def test_transformer_microfeature_registry_valid():
    """The committed microfeature registry validates: fields non-empty, types in the alphabet, claim levels legal, ids unique,
    TMT references in TMT-1..15, X-TMT references present and GREEN in the executed receipt, and the builder reproduces it."""
    from gmi_microscope import registry, registry_check
    errors = registry_check.check(verbose=False)
    assert errors == [], errors
    reg = json.loads((HERE / "GMI_TRANSFORMER_MICROFEATURE_REGISTRY_V1.json").read_text(encoding="utf-8"))
    assert reg["n_features"] == len(reg["features"]) >= 80
    assert reg["registry_sha256"] == registry.build()["registry_sha256"]  # the builder is the source of the committed file
    # every feature covered by the section-1 acceptance list, and PROVED_AT_SCOPE only behind an executed check
    receipt = json.loads((HERE / "GMI_TRANSFORMER_MICROFEATURE_EXACT_RECEIPT_V1.json").read_text())
    green = {c["check"] for c in receipt["checks"] if c["passed"]}
    for f in reg["features"]:
        assert set(f["gmi_type"]) <= set("CSRTNUHVGPD"), f["id"]
        if f["evidence_status"] == "PROVED_AT_SCOPE":
            assert f["formal_theorem"]["receipt_check"] in green, f["id"]
    assert reg["counts_by_evidence_status"]["PROVED_AT_SCOPE"] >= 10


def test_executed_b2_rows_reproduce_and_are_green(tmp_path):
    """RV-377-056 (B2.3 routing) reproduces byte for byte; RV-377-055 (B2.12 KV cache) reproduces on its small cells.
    Both are synthetic exact microscopes: they are NOT evidence about a trained neural network."""
    from gmi_microscope import b2_kv, b2_route
    rc = b2_route.main(str(tmp_path / "route.json"))
    committed = json.loads((HERE / "microscopes" / "results" / "STAGE_B2_03_ROUTING_V1.json").read_text())
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert rc["status"] == "GREEN" and rc["n_claims_hold"] == 8
    # the measured minimal safe fixed budget is exactly |union E(x)| in every cell (TMT-3 realized as a measurement)
    for cell in rc["cells"].values():
        assert cell["minimal_safe_fixed_budget_measured"] == cell["union_edges"]
        assert cell["frontier_by_discovery_price"]["1"]["winner_excluding_oracle"] != "DYNAMIC"
    kv = json.loads((HERE / "microscopes" / "results" / "STAGE_B2_12_KV_CACHE_V1.json").read_text())
    assert kv["status"] == "GREEN" and kv["n_claims_hold"] == 7
    for name, P, C, R, L, H in b2_kv.CELLS[:4]:          # the large cells are exercised by the committed receipt
        cell = b2_kv.run_cell(P, C, R, L, H)
        for k in ("outputs_identical_recompute_vs_cache", "mults_recompute", "mults_cache", "cache_elems_peak", "mu_star_measured"):
            assert cell[k] == kv["cells"][name][k], (name, k)
    # the cache is worth exactly nothing without reuse or continuation length
    assert kv["cells"]["P4_C1_R1"]["mu_star_measured"] == "0"
    assert kv["cells"]["P16_C8_R4"]["mu_star_measured"] == kv["cells"]["P16_C8_R4__L2H4"]["mu_star_measured"] == kv["cells"]["P16_C8_R4__L8H1"]["mu_star_measured"]






def test_e1_iql_receipt_cell_reproduces():
    """F4 (RV-377-063): committed cells replay exactly, the negative twin collapses, and the decisive negative-twin
    ecology ALIAS_NORESID ties target-ambiguity scoring against BOTH parent criteria to the charged op."""
    from gmi_microscope import e1_iql
    committed = json.loads((RES / "STAGE_E1_V35_F4_IQL.json").read_text())
    for cell, price, budget, d in (("ALIAS_RESID", "UNIT", 3, "0000"), ("ALIAS_NORESID", "SKEW", 2, "1010")):
        for row in e1_iql.ROWS:
            r = e1_iql.run(row, bases.B0, cell, price, budget, tuple(int(c) for c in d))
            key = f"{cell}|{price}|{budget}|{d}|{row}|{bases.B0.name}"
            for k in ("capability", "interventions", "intervention_burden", "charged_total",
                      "interventions_on_nuisance_layer", "answer_signature", "R"):
                assert r[k] == committed["cells"][key][k], (cell, price, budget, d, row, k)
    assert all(committed["C2_column_invariance"].values())
    S = committed["summary_over_orientation_sweep"]
    for col in committed["columns"]:
        # the registered F4 regime: target-ambiguity scoring beats both parent criteria outright
        assert S[f"ALIAS_RESID|UNIT|B=3|{col}|IQL"]["admissible_count"] == 16, col
        assert S[f"ALIAS_RESID|UNIT|B=3|{col}|PRED_UNCERTAINTY"]["admissible_count"] == 4, col
        assert S[f"ALIAS_RESID|UNIT|B=3|{col}|ENTROPY"]["admissible_count"] == 4, col
        # it never spends an intervention on the causally isolated nuisance layer; the parents always do
        assert S[f"ALIAS_RESID|UNIT|B=3|{col}|IQL"]["mean_interventions_on_nuisance_layer"] == 0.0, col
        assert S[f"ALIAS_RESID|UNIT|B=3|{col}|PRED_UNCERTAINTY"]["mean_interventions_on_nuisance_layer"] > 0.0, col
        # the negative twin: the identical machine with a constant ambiguity measure loses 4 of 16 orientations
        assert S[f"ALIAS_RESID|UNIT|B=3|{col}|IQL_NOAMBIG"]["admissible_count"] == 12, col
        # RV-377-063 clause 5: remove the prediction-target residual, KEEP the 16-fold aliasing, and the three
        # criteria become exactly equal -- the result that relocated the F4 discriminator
        for budget in (2, 3, 4, 7):
            for price in ("UNIT", "SKEW"):
                got = {tuple(S[f"ALIAS_NORESID|{price}|B={budget}|{col}|{row}"][k] for k in
                             ("admissible_count", "mean_interventions", "mean_intervention_burden", "mean_charged_total"))
                       for row in ("IQL", "PRED_UNCERTAINTY", "ENTROPY")}
                assert len(got) == 1, (col, budget, price, got)
    # DG-2: no frontier statement is checked on a grid that fails to reach the crossovers it reports
    for key, cross in committed["analytic_crossovers"].items():
        if cross:
            assert max(committed["frontier_grids"][key]) > max(cross.values()), key


def test_e1_scdi_receipt_cell_reproduces_and_crossover_is_analytic():
    """F6 (RV-377-064): committed cells replay exactly, every serving organization that keeps the authority state
    emits bit-identical answers, and the price-switch crossover K* is the analytic one."""
    from gmi_microscope import e1_scdi
    committed = json.loads((RES / "STAGE_E1_V36_F6_SCDI.json").read_text())
    pin = committed["cells_spec"]["twin_pinned_family_by_regime"]
    for G, col in ((2, "HW_TENSOR_PRICED"), (4, "B2_REWRITABLE_TYPED_PROGRAM_GRAPH")):
        for row in e1_scdi.ROWS:
            r = e1_scdi.run(row, bases.ALL_HW[col], G, pin)
            cell = committed["cells"][f"G={G}|{col}|{row}"]
            for k in ("min_capability", "desc_state", "compile_ops", "probe_ops", "exec_per_query",
                      "answer_signature", "families", "R"):
                assert r[k] == cell[k], (G, col, row, k)
    assert all(committed["C2_column_invariance"].values())
    # exact developmental equality: compiling a serving realization changes no answer, anywhere
    for key, eq in committed["developmental_equality"].items():
        if key.split("|")[2] != "RETRAIN":
            assert eq["equals_AUTH_INTERP"] and eq["equals_UNIVERSAL"], key
            assert eq["capability"] == 1.0, key
    # independently retrained models lose the transfer and are inadmissible from two regimes on
    for G in (2, 3, 4):
        assert committed["cells"][f"G={G}|HW_TENSOR_PRICED|RETRAIN"]["admissible"] is False, G
    # the charged price probe compiles in the native-store column alone, at every G
    for G in (1, 2, 3, 4):
        fam = {c: committed["cells"][f"G={G}|{c}|SCDI"]["families"]["A"] for c in committed["columns"]}
        assert fam == {"HW_TENSOR_PRICED": "INTERP", "B0_LOCAL_ADAPTIVE_TRANSDUCERS": "INTERP",
                       "B2_REWRITABLE_TYPED_PROGRAM_GRAPH": "TABLE", "U_UNIFORM_UNIVERSAL": "INTERP"}, G
    # K* against the universal parent is finite, strictly decreasing in G, and matches the frozen analytic values
    ks = [committed["analytic_crossovers"][f"G={G}|H=64"]["SCDI|UNIVERSAL"] for G in (1, 2, 3, 4)]
    assert ks == sorted(ks, reverse=True), ks
    for got, want in zip(ks, (51.66, 24.96, 11.41, 10.02)):
        assert abs(got - want) / want < 0.05, (got, want)
    # shared authority plus a FIXED compiled serving form never occupies the frontier: the universal table dominates it
    for G in (1, 2, 3, 4):
        assert "AUTH_TABLE" not in committed["frontier_occupants_over_extended_grid"][f"G={G}|H=64"], G
    for key, cross in committed["analytic_crossovers"].items():
        if cross:
            assert max(committed["frontier_grids"][key]) > max(cross.values()), key

def test_dk_fx8_instrument_is_the_registered_universe():
    """RV-377-066 clause 1: the microscope's `fx8` column IS the registered 8-bit universe. If this fails, the
    whole precision comparison is between two instruments neither of which the programme registered."""
    from gmi_microscope import dk_precision
    chk = dk_precision.fx8_identity_check()
    assert chk["bit_identical_to_registered_universe"] and chk["pairs_checked"] == 256 * 256
    committed = json.loads((RES / "STAGE_DK_V2_PRECISION_GATED.json").read_text())
    assert committed["fx8_identity_check"] == chk


def test_dk_precision_receipt_cells_replay_exactly():
    """RV-377-066: committed cells of both ecologies replay bit for bit under both the registered 8-bit
    instrument and the wide one, and the charged operation sequences are IDENTICAL between them -- which is
    what makes the capability difference attributable to precision alone (GMI-DA5, deliverable 2)."""
    from gmi_microscope import bases as B, dk_precision as dk
    committed = json.loads((RES / "STAGE_DK_V2_PRECISION_GATED.json").read_text())
    col = B.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
    for ek in ("noisy", "ambig"):
        eco = dk.ecology(ek)
        assert committed["ecologies"][ek]["events"] == [list(e) for e in eco["events"]]
        for row in ("BAYES", "BAYESM", "QCOUNT", "MAP", "GEN"):
            prev = None
            for prec in ("fx8", "wide"):
                r = dk.run(row, col, eco, prec)
                cell = committed["cells"][f"{ek}|{row}|{prec}"]
                for k in ("capability", "capability_exact", "admissible", "desc_bits", "desc_bits_scaled",
                          "charged_ops_total", "native_R", "R", "answer_signature", "brier_excess_exact"):
                    assert r[k] == cell[k], (ek, row, prec, k, r[k], cell[k])
                if prev is not None:                      # identical charged operation sequence
                    assert r["R"] == prev["R"] and r["charged_ops_total"] == prev["charged_ops_total"]
                    assert r["native_R"] == prev["native_R"]
                prev = r
    assert committed["charged_op_identity"]["all_rows_all_cells_identical"] is True


def test_dk_precision_gated_kingdom_decision_replays():
    """RV-377-066 clauses 4, 5, 8, 9 and 10: the executed decision, replayed from the committed receipt.
    E_ambig admits NOTHING at 8 bits while an 8-bit-representable answer would score 0.910880; E_noisy admits a
    quantized-count posterior at 8 bits and is therefore NOT gated; and the occupant above the threshold is the
    pruned posterior, not the exact one."""
    from fractions import Fraction
    from gmi_microscope import dk_precision as dk
    committed = json.loads((RES / "STAGE_DK_V2_PRECISION_GATED.json").read_text())
    eco = dk.ecology("ambig")
    grid = {x: Fraction(round(float(v) * 16), 16) for x, v in eco["qstar"].items()}   # closest fx8-grid answer
    assert round(float(dk.capability(eco, grid)[0]), 6) == 0.910880 >= float(dk.THETA)
    assert committed["admissible_sets"]["ambig|fx8"] == []
    assert committed["admissible_sets"]["noisy|fx8"] == ["QCOUNT"]
    assert committed["capability"]["noisy|QCOUNT|fx8"] == 0.863997
    gated = committed["precision_gated_cells"]
    for key, v in gated.items():
        eck, prec = key.split("|")[0], key.split("|")[1]
        if eck == "ambig" and prec != "fx8":
            assert v["n_gated_d3"] == v["n_cells"] >= 36, key      # every cell held by a carrier absent at 8 bits
        if eck == "ambig" and prec == "fx8":
            assert v["n_gated_d3"] == 0, key
        if eck == "noisy" and prec == "fx8":
            assert v["occupants_over_grid"] == ["QCOUNT"], key
    for p in ("fx16", "fx24", "fx32", "wide"):
        assert gated[f"ambig|{p}|reduced|flat"]["n_gated_carrier"] == 0                 # exact posterior: no cell
        assert gated[f"ambig|{p}|native|flat"]["n_gated_carrier"] == 1                  # ... except H = 1, r = 0
    assert committed["analytic_crossovers"]["ambig|wide|reduced|flat"]["H|BAYES|QCOUNT"] == 52 / 84
    ref = committed["threshold_refinement"]
    assert ref["ambig"]["smallest_admissible_total_bits_any_d3_row"] == 10
    assert ref["ambig"]["BAYES"]["smallest_admissible_total_bits"] == 16
    assert ref["noisy"]["smallest_admissible_total_bits_any_d3_row"] == 8
    assert committed["threshold_bits"] == 12
    assert committed["terminal"] == "PRECISION_GATED_KINGDOM_ESTABLISHED_AT_SCOPE__THRESHOLD_12_BITS"
def test_dk_depth_gated_receipt_cells_replay_exactly():
    """RV-377-065: two committed cells of STAGE_DK_V1_DEPTH_GATED replay op for op -- the depth-1 XOR cell, whose
    charged sequence is dc_vsa's own (it reproduces RV-377-044's desc 864/2304, compile 2048 and exec 1095/1031), and a
    depth-4 PERM cell, where the path code is injective. In both, the binding carrier and ALL THREE materializing
    parents answer bit-identically: the bounded reduction that decides criterion 3."""
    from gmi_microscope import dk_depth as dk
    committed = json.loads((RES / "STAGE_DK_V1_DEPTH_GATED.json").read_text())
    for cname in ("XOR_d1_D64_s7", "PERM_d4_D64_s7"):
        spec = committed["cells_spec"][cname]
        eco = dk.ecology(spec["D"], spec["depth"], spec["k"], spec["law"], seed=spec["rec_seed"])
        assert eco["n_distinct_path_vectors"] == committed["ecology_facts"][cname]["n_distinct_path_vectors"]
        sigs = {}
        for row in dk.ROWS:
            got = dk.run(row, bases.B0, eco)
            cell = committed["cells"][f"{cname}|{row}"]
            for k in ("capability", "correct", "admissible", "R", "compile_ops", "exec_ops_total",
                      "exec_per_query", "desc_bits", "hv_ops", "hv_compile_ops", "answer_signature"):
                assert got[k] == cell[k], (cname, row, k, got[k], cell[k])
            sigs[row] = got["answer_signature"]
        assert sigs["VSA"] == sigs["STORE_MAT"] == sigs["STORE_PATH"] == sigs["STORE_DEDUP"], cname
        assert sigs["VSA_NOBIND"] != sigs["VSA"], cname
    # the depth-1 XOR cell IS RV-377-044's D64_d1_k3 cell, op for op
    vsa = committed["cells"]["XOR_d1_D64_s7|VSA"]; mat = committed["cells"]["XOR_d1_D64_s7|STORE_MAT"]
    assert (vsa["desc_bits"], vsa["exec_per_query"]) == (864, 1095.0)
    assert (mat["desc_bits"], mat["compile_ops"], mat["exec_per_query"]) == (2304, 2048, 1031.0)
    # the XOR path code collapses with depth and the permutation-protected one does not
    assert committed["clause_scores"]["1"]["distinct_path_vectors_by_law_and_depth"] == {
        "XOR": [4, 7, 8, 8, 8, 8], "PERM": [4, 16, 64, 256, 1024, 4096]}


def test_dk_depth_gated_frontier_crossovers_and_kingdom_verdict():
    """RV-377-065: the committed frontier decisions replay from the committed cost coordinates alone -- the
    parent-maximal crossovers are the exact rationals reported, every reuse grid spans at least twice the largest
    crossover it reports (gap DG-2), and no cell is occupied by the binding carrier while no parent occupies any."""
    from fractions import Fraction
    from gmi_microscope import dk_depth as dk
    committed = json.loads((RES / "STAGE_DK_V1_DEPTH_GATED.json").read_text())
    # DG-2 holds in every decision, and the verdict is the negative one
    assert all(d["dg2_grid_covers_twice_every_crossover"] for d in committed["decisions"].values())
    assert len(committed["decisions"]) == 96 and committed["d_star"] is None and committed["kingdom_cells"] == []
    assert committed["terminal"].startswith("NO_DEPTH_GATED_KINGDOM_AT_EXECUTED_DEPTHS")
    for key, dec in committed["decisions"].items():
        if dec["admissible_rows"]:
            assert dec["parent_occupies_some_cell"], key           # 62 of 62
        assert not dec["kingdom_at_this_cell"], key
        assert max(dec["grid"]) >= 2 * max([Fraction(v) for v in dec["crossovers"].values()] or [0])
    # the frontier of one committed cell recomputed from its committed cost coordinates only
    cname = "PERM_d3_D64_s7"
    adm = {r: committed["cells"][f"{cname}|{r}"] for r in dk.ROWS if committed["cells"][f"{cname}|{r}"]["admissible"]}
    cross = dk.crossovers(adm, "reduced")
    assert {k: str(v) for k, v in cross.items()} == committed["decisions"][f"{cname}|reduced"]["crossovers"]
    grid = dk.grid_for(cross)
    assert grid == committed["decisions"][f"{cname}|reduced"]["grid"] and dk.check_dg2(cross, grid)
    front = dk.frontier_of(adm, "reduced", grid)
    assert {str(H): front[H] for H in grid} == committed["decisions"][f"{cname}|reduced"]["frontier"]
    # the depth law: unbounded under PERM, bounded by its depth-1 value under XOR
    perm = committed["depth_law_of_the_parent_maximal_opponent"]["PERM|D64|s7|reduced"]
    assert [perm["by_depth"][str(d)]["parent_maximal_crossover_H_star"] for d in range(1, 7)] == \
           ["109/2", "91/4", "647/8", "1213/4", "18679/16", "91127/20"]
    ratios = [perm["growth_ratio"][k] for k in ("2->3", "3->4", "4->5", "5->6")]
    assert ratios == sorted(ratios) and max(ratios) < 4.0        # rising strictly towards R = 4, never reaching it
    assert committed["clause_scores"]["7"]["xor_parent_maximal_crossover_never_exceeds_depth_1_value"] == \
           {"64": True, "128": True}
    # every frozen clause is scored verbatim against the committed ledger record, and the failures are preserved
    clauses, _ = dk.load_clauses()
    assert {str(n): clauses[n] for n in clauses} == committed["frozen_clauses_verbatim"]
    assert committed["clauses_held"] == 7 and committed["clauses_failed"] == [6, 7, 8, 9, 12]
    assert all(committed["clause_scores"][str(n)]["verdict"] in ("HOLDS", "FAILS") for n in range(1, 13))


# --------------------------------------------------------------------------------------------------------------
# RV-377-070 — the F axis of GMI-DA7: the refined ecology family and the fourteen exact-equality certificates
# --------------------------------------------------------------------------------------------------------------
def test_f_axis_certificate_enumeration_replays_the_committed_receipts():
    """The certificate table is RECOMPUTED from the committed source receipts, cell by cell, and must agree with the
    F-axis receipt: 17 certificate rows over 13 receipts, 14 distinct (candidate, parent) pairs, 8 candidates."""
    from gmi_microscope import refine_f
    committed = json.loads((RES / "STAGE_F_AXIS_REFINEMENT_V1.json").read_text())
    enum = committed["certificate_enumeration"]
    assert enum["n_certificate_pairs"] == 17, enum["n_certificate_pairs"]
    assert enum["n_certified_candidates"] == 8, enum["n_certified_candidates"]
    assert len({(c["candidate"], c["parent"]) for c in enum["certificates"]}) == 14
    # replay: every certified pair really is bit-identical on every registered cell of its own receipt
    for c in enum["certificates"]:
        src = json.loads((RES / c["receipt"]).read_text())
        rows = src["rows"]
        instr = refine_f.RECEIPT_INSTRUMENT.get(c["receipt"])
        sigs = {}
        for key, cell in src["cells"].items():
            r, ctx = refine_f._row_and_context(key, rows)
            if r is None or (instr is not None and instr not in ctx):
                continue
            sigs.setdefault(r, {})[ctx] = cell["answer_signature"]
        common = set(sigs[c["candidate"]]) & set(sigs[c["parent"]])
        assert len(common) == c["n_cells"], (c["receipt"], c["candidate"], c["parent"], len(common))
        for ctx in common:
            assert sigs[c["candidate"]][ctx] == sigs[c["parent"]][ctx], (c["receipt"], c["candidate"], c["parent"], ctx)
    # and the enumeration recomputes to the same thing when run again from the receipts on disk
    assert refine_f.enumerate_certificates()["certificates"] == enum["certificates"]


def test_f_axis_split_and_surviving_pairs_replay_exactly():
    """Committed F-axis cells replay: for a split pair the exact first (ecology, intervention, query) and BOTH served
    answers reproduce; for a surviving pair the refined family reproduces as EQUAL over the same cell count."""
    from gmi_microscope import refine_f
    committed = json.loads((RES / "STAGE_F_AXIS_REFINEMENT_V1.json").read_text())
    for pkey in ("P1", "P13", "P12"):
        want = committed["pairs"][pkey]
        got = refine_f.run_pair(pkey)
        assert got["refined_family_verdict"] == want["refined_family_verdict"], pkey
        assert got["n_refined_cells"] == want["n_refined_cells"], pkey
        assert got["first_split"] == want["first_split"], pkey
        assert got["demands_that_split"] == want["demands_that_split"], pkey
        assert got["registered_family_verdict"] == "EXACT_DEVELOPMENTAL_EQUALITY", pkey
    # the surviving pair is certified over a strictly larger family than the registered one that certified it
    assert committed["pairs"]["P12"]["refined_over_registered_cell_ratio"] >= 10


def test_f_axis_registered_cells_replay_from_the_source_modules():
    """The registered side of two certificates is replayed through the carriers' own modules and must reproduce the
    committed receipt cells bit for bit -- the equality the refined family is attacking is a real committed fact."""
    from gmi_microscope import dc_vsa, dn_obstruction
    src = json.loads((RES / "STAGE_DC_V24_DC1_VSA.json").read_text())
    for cname in ("D64_d1_k3", "D64_d2_k3"):
        spec = src["cells_spec"][cname]
        eco = dc_vsa.ecology(spec["D"], spec["depth"], spec["k"], noise=spec["noise"])
        sigs = {}
        for row in ("VSA", "STORE_MAT"):
            r = dc_vsa.run(row, bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"], eco)
            cell = src["cells"][f"{cname}|{row}|B0_LOCAL_ADAPTIVE_TRANSDUCERS"]
            for k in ("answer_signature", "capability", "desc_bits", "exec_per_query", "R"):
                assert r[k] == cell[k], (cname, row, k)
            sigs[row] = r["answer_signature"]
        assert sigs["VSA"] == sigs["STORE_MAT"], cname
        assert src["vsa_equals_store_mat_answers"][f"{cname}|B0_LOCAL_ADAPTIVE_TRANSDUCERS"] is True
    src = json.loads((RES / "STAGE_DN_V30_N11_OBSTRUCTION_R2.json").read_text())
    for cname in ("m10_d2_k10", "m16_d2_k16"):
        spec = src["cells_spec"][cname]
        eco = dn_obstruction.ecology(spec["m"], spec["k"], spec["d"])
        sigs = {}
        for row in ("OBSTRUCT", "DENSE_RREF"):
            r = dn_obstruction.run(row, bases.ALL["B0_LOCAL_ADAPTIVE_TRANSDUCERS"], eco)
            cell = src["cells"][f"{cname}|{row}"]
            for k in ("answer_signature", "capability", "desc_bits", "exec_per_query"):
                assert r[k] == cell[k], (cname, row, k)
            sigs[row] = r["answer_signature"]
        assert sigs["OBSTRUCT"] == sigs["DENSE_RREF"], cname


def test_f_axis_clause_adjudication_is_recorded_verbatim_with_its_failures():
    """Every frozen clause is present with a HOLDS/FAILS verdict, the three that failed are still recorded with
    their observed values, and the demand-level facts the surviving verdicts rest on are the committed ones."""
    committed = json.loads((RES / "STAGE_F_AXIS_REFINEMENT_V1.json").read_text())
    cl = committed["clause_adjudication"]
    assert {f"clause_{i}" for i in range(1, 13)} == set(cl)   # the receipt is dumped with sorted keys
    assert {k for k, v in cl.items() if v["verdict"] == "FAILS"} == {"clause_1", "clause_2", "clause_8"}
    for v in cl.values():
        assert v["clause"] and v["observed"] is not None
    # NOISY_CUE never splits the two algebraic pairs at any k: the lazy/eager identity holds for corrupted cues too
    for pkey in ("P1", "P4"):
        assert committed["pairs"][pkey]["per_demand"]["NOISY_CUE"]["n_differing"] == 0
    # every OVERFLOW split is absent at the capacity edge and present past it (the GMI-DA4 signature)
    for pkey, p in committed["pairs"].items():
        g = p["gate_classification"].get("OVERFLOW")
        if g:
            assert g["capacity_gated"] is True, pkey
            for load, v in g["by_load"].items():
                if "past_capacity" not in load:
                    assert v["n_differing"] == 0, (pkey, load)
    # exactly three pairs carry a split that no known gate explains
    surviving = [k for k, p in committed["pairs"].items()
                 if any(g["classification"] == "SURVIVES_THE_KNOWN_GATES" for g in p["gate_classification"].values())]
    assert sorted(surviving) == ["P13", "P2", "P3"], surviving
    assert committed["terminal"] == "F_REFINEMENT_SPLITS_10_OF_14_EQUALITY_CERTIFICATES__3_SURVIVE_THE_KNOWN_GATES"
def test_g14_failed_draw_charging_replays_committed_cells():
    """RV-377-067 (gap G14): a committed cell of the corrected-cost receipt replays exactly, the reliability index is the
    census's own (9 of 192, not the 10 the earlier records report), and the charged frontier arithmetic reproduces the
    receipt's verdict on the cell that RV-377-041b's clause 3 was about."""
    from fractions import Fraction as F

    from gmi_microscope import failed_draws as fd

    rc = json.loads((RES / "STAGE_G14_FAILED_DRAW_CHARGING_V1.json").read_text())
    committed = json.loads((RES / "STAGE_DE_SMOOTH_V22_SYM5_S4.json").read_text())

    # the cheap memory row replays cell for cell against the committed frontier receipt
    col = "B0_LOCAL_ADAPTIVE_TRANSDUCERS"
    cell = fd.run_cell("S5h", col, 4)
    assert cell["R"] == committed["R_by_cell"][f"S5h|{col}|4"]
    assert cell["capability"] == committed["capability_by_cell"][f"S5h|{col}|4"]
    assert rc["reexecution_vs_committed"]["n_identical"] == rc["reexecution_vs_committed"]["n_cells"] == 30

    # the reliability index is recomputed from the census receipt, not quoted
    rel = fd.reliability_from_census()
    assert rel["pooled"]["q"] == "9/192" == rc["reliability"]["pooled"]["q"]
    assert abs(rel["pooled"]["expected_draws_1_over_q"] - 192 / 9) < 1e-12
    lo, hi = fd.clopper_pearson(9, 192)
    assert [float(lo), float(hi)] == rc["reliability"]["pooled"]["q_ci95_clopper_pearson"]
    assert 0.02 < float(lo) and float(hi) < 0.10

    # the charged line on the cell RV-377-041b claimed for the stochastic row: S3 loses it by three orders of magnitude
    b = rc["by_column"][col]
    pe = {k: fd.per_event(committed["R_by_cell"][f"{k}|{col}|{8 if k == 'S3' else 4}"]) for k in b["admissible_rows_R_top"]}
    D = b["D_draw"]["S3"]
    search = (F(192, 9) - 1) * D
    c_s3 = fd.cost(pe["S3"], search, 128, 0)
    c_s5h = fd.cost(pe["S5h"], F(0), 128, 0)
    assert c_s3 > 50 * c_s5h                       # the cell RV-377-041b's clause 3 gave to S3 is now lost by 80x
    ratio = b["charged"]["q_cell"]["search_charge_vs_cheapest_rival"]
    assert ratio["min_factor"] > 9 and ratio["max_factor"] > 1000
    assert b["charged"]["q_cell"]["S3_cells"] == b["charged"]["q_pooled"]["S3_cells"] == 0
    assert rc["readjudication_of_RV_377_041b"][2]["verdict"] == "FAILS"
    assert rc["n_RV041b_clauses_surviving"] == 2


def test_dg2_grid_audit_replays_committed_verdicts():
    """RV-377-068 (gap DG-2): the audit of two named committed receipts reproduces the committed audit, including the
    crossover at H = 1856 that the rule was written from, and the auditor reproduces each graded receipt's own frontier."""
    from gmi_microscope import grid_audit

    rc = json.loads((RES / "STAGE_DG2_GRID_AUDIT_V1.json").read_text())
    by_name = {r["receipt"]: r for r in rc["receipts"]}

    energy = grid_audit.audit_receipt(str(RES / "STAGE_DC_V25_DC3_ENERGY.json"))
    assert energy["verdict"] == "TRUNCATED" and energy["grade"] == "MAJOR"
    assert energy["reproduced_own_frontier"] is True and energy["grid_max_H"] == 1024
    smallest = min(energy["crossovers_beyond_grid"], key=lambda c: c["H_star"])
    assert smallest["H_star"] == 1856.0 and sorted(smallest["rows"]) == ["HOPFIELD", "KNN_PAT"]
    assert energy["verdict"] == by_name["STAGE_DC_V25_DC3_ENERGY.json"]["verdict"]

    safe = grid_audit.audit_receipt(str(RES / "STAGE_DC_V31_DC7_QUANTUM.json"))
    assert safe["verdict"] == by_name["STAGE_DC_V31_DC7_QUANTUM.json"]["verdict"] == "SAFE"
    assert safe["reproduced_own_frontier"] is True

    # no receipt is graded without its own frontier being reproduced, and none that fails that is called SAFE
    for r in rc["receipts"]:
        if r["verdict"] in ("SAFE", "TRUNCATED"):
            assert r["reproduced_own_frontier"] is True, r["receipt"]
        else:
            assert r["reason"], r["receipt"]
    assert rc["counts"]["TRUNCATED"] >= 20 and rc["counts"]["MINOR"] == 0


def test_g8_size_census_replays_small_sizes_and_its_witnesses():
    """RV-377-069 (gap G8): the exhaustive enumeration replays exactly at the small sizes, the three counts are nested,
    and every obstruction's witness genotype reproduces the property it is a witness for."""
    from gmi_microscope import morph, size_census

    rc = json.loads((RES / "STAGE_G8_SIZE_CENSUS_LOWER_BOUNDS_V1.json").read_text())
    counts = rc["counts_by_size"]
    for n in ("3", "4", "5"):
        n_typed, forms, complete = size_census.enumerate_size(int(n))
        assert complete
        assert n_typed == counts[n]["type_correct_genotypes"], n
        assert len(forms) == counts[n]["canonical_forms"], n

    for n, e in counts.items():
        if not e["enumeration_complete"]: continue
        assert e["response_classes"] <= e["canonical_forms"] <= e["type_correct_genotypes"], n

    for o in rc["obstructions"]:
        if o["minimum_realizing_size"] is None:
            continue
        g = morph.from_json(o["witness_genotype"])
        assert morph.typecheck(g)
        assert len(g["nodes"]) == o["minimum_realizing_size"]
        r = size_census.response_of(g)
        assert r is not None and r["properties"][o["property"]] is True, o["property"]
        # the witness is minimal: the census enumerated every smaller size exhaustively and found none
        for n, e in counts.items():
            if int(n) < o["minimum_realizing_size"]:
                assert e["enumeration_complete"] and e["forms_realizing"][o["property"]] == 0, (o["property"], n)
def test_r7_lineage_descent_replays_from_the_committed_receipt():
    """R7: the committed lineage receipt is self-verifying — replaying each witnessed descent chain from its recorded
    founder re-derives every intermediate fingerprint and the elite's fingerprint EXACTLY, and does so from a REMINTED
    founder too (H5). A lineage that does not replay is a bug, so the committed receipt must report 0 failures."""
    from gmi_microscope import lineage, morph
    rc = json.loads((RES / "STAGE_R7_LINEAGE_V1.json").read_text())
    assert rc["terminal"] == "R7_LINEAGE_REPLAYS_EXACTLY"
    assert rc["replay_audit"]["replay_failures"] == 0
    assert rc["remint_invariance"]["n_fingerprint_changed_by_remint"] == 0
    assert rc["dvp_stream_ledger"]["protected_queries"] == 0          # the P stream was never touched
    assert rc["replay_witness"], "the receipt must carry at least one replayable descent chain"
    for w in rc["replay_witness"]:
        for remint_seed in (None, 5):
            g, _, _ = lineage.founder(w["founder"]["fseed"], w["founder"]["steps"])
            if remint_seed is not None: g = lineage.canon_geno(morph.remint(g, remint_seed))
            assert morph.fingerprint(g) == w["founder_fingerprint"]
            for step in w["steps"]:
                g, op, draws = lineage.propose(g, step["proposal_seed"], None, step["op_index"])
                assert op == step["operator"] and draws == step["proposal_draws"]
                assert morph.fingerprint(g) == step["expected_fingerprint"]
            assert morph.fingerprint(g) == w["final_fingerprint"]


def test_r8_triage_screen_was_audited_before_use_and_its_cells_replay():
    """R8 (protocol rule 18): the triage run cites its screen's audit receipt by hash; the audit's measured
    false-rejection rate honours the budget declared before calibration; the only cache used is keyed by the exact
    canonical form and its measured score spread is 0 (contrast the functional-equivalence cache of RV-377-061, which
    mis-scored 34.65 per cent); and every committed confirmed cell re-scores to the committed values at both fidelities."""
    from gmi_microscope import morph, smooth, triage
    aud = json.loads((RES / "STAGE_R8_SCREEN_AUDIT_V1.json").read_text())
    run = json.loads((RES / "STAGE_R8_TRIAGE_V1.json").read_text())
    assert aud["status_verdict"] == "SCREEN_AUDITED_GREEN"
    assert run["screen_audit_receipt_sha256"] == aud["receipt_sha256"]
    assert aud["audit"]["false_rejection_rate"] <= aud["declared_false_rejection_budget"]
    assert aud["audit"]["canonical_cache"]["max_exact_score_spread_within_a_canonical_form"] == 0.0
    assert aud["remint_invariance"]["n_changed"] == 0
    fec = json.loads((RES / "STAGE_F_FEC_AUDIT_V1.json").read_text())
    assert fec["audit_by_probe_length"]["10"]["wrong_score_fraction"] == 0.3465   # the failure rule 18 came from
    target = smooth.make_target(smooth.COEFFS_V3)
    for cell in run["best_confirmed"][:4]:
        g = morph.from_json(cell["genotype"])
        assert triage.screen(g, target)[0] == cell["screen"], cell["fingerprint"]
        assert triage.confirm(g, target)[0] == cell["exact"], cell["fingerprint"]


def test_r9_census_counts_three_different_things_and_the_small_sizes_reproduce():
    """R9: the committed census reproduces exactly at the small exhaustive sizes, the three counts are reported
    separately, and the two invariants the whole lane leans on hold — the developmental response is a function of the
    canonical form, and remint changes no count."""
    import random
    from gmi_microscope import census
    rc = json.loads((RES / "STAGE_R9_CENSUS_V1.json").read_text())
    assert rc["terminal"] == "R9_CENSUS_EXECUTED"
    assert rc["response_class_check_total"]["n_disagreements"] == 0
    assert rc["remint_invariance"]["n_changed"] == 0
    rows = {r["size"]: r for r in rc["counts_by_size"]}
    for n in (3, 4):
        r = census.census_size(n, True, random.Random(0))
        for k in ("n_configurations_enumerated", "n_canonical_classes_in_sample", "n_response_classes_in_sample"):
            assert r[k] == rows[n][k], (n, k)
    assert census.enumerate_stratum(census._strata(5)[0], materialize=False)[0] >= 0
    # the three counts are strictly different things and the receipt says so
    assert rows[5]["n_configurations_enumerated"] > rows[5]["n_canonical_classes_in_sample"] > rows[5]["n_response_classes_in_sample"]
    assert "forbidden_sentence" in rc["three_counts_are_different_things"]
    est = rows[6]["N_CONFIG_stratified_estimate"]
    assert est["n_strata_sampled"] < est["n_strata_population"] and est["N_CONFIG_estimate"] > 0


def test_r10_invasion_cells_replay_and_competition_is_not_independent_scoring():
    """R10: committed competition cells replay exactly on the charged machines, reminting a competitor changes nothing,
    and the registered prediction (occupancy under a shared budget is not a function of the solo scores) is adjudicated
    on the off-diagonal cells."""
    from gmi_microscope import invasion, smooth, zoo
    rc = json.loads((RES / "STAGE_R10_INVASION_V1.json").read_text())
    assert rc["remint_invariance"]["n_changed"] == 0
    target = smooth.make_target(smooth.COEFFS_V3)
    checked = 0
    for name, cell in list(rc["cells"].items())[:6]:
        pool, r, i = name.split("|"); pool = int(pool[4:])
        rec = invasion.compete(zoo.ZOO[r](), zoo.ZOO[i](), target, pool, rc["protocol"]["head_start_events"])
        for k in ("outcome", "capability_resident", "capability_invader", "events_resident", "events_invader",
                  "charge_resident", "charge_invader", "pool_spent", "allocation"):
            assert rec[k] == cell[k], (name, k)
        checked += 1
    assert checked == 6
    assert rc["n_cells"] == len(rc["pools"]) * rc["n_carriers"] ** 2
    assert rc["prediction_holds"] is (rc["n_offdiagonal_cells_where_competition_disagrees_with_solo"] > 0)


def test_r11_biosphere_episode_is_deterministic_resumable_and_cites_its_screen_audit():
    """R11: the committed episode receipt carries a self-verifying witness episode that reproduces field for field, the
    checkpointed-and-resumed episode equals the straight-through one, the protected stream was never queried, and the
    screen audit is cited by hash (protocol rule 18)."""
    from gmi_microscope import biosphere
    rc = json.loads((RES / "STAGE_R11_BIOSPHERE_V1.json").read_text())
    aud = json.loads((RES / "STAGE_R8_SCREEN_AUDIT_V1.json").read_text())
    assert rc["screen_audit_receipt_sha256"] == aud["receipt_sha256"]
    assert rc["resume_determinism"]["identical"] is True
    for run in rc["runs"].values():
        assert run["dvp_stream_ledger"]["protected_queries"] == 0
        assert run["replay_audit"]["replay_failures"] == 0
    w = rc["determinism_witness"]
    st = biosphere.episode(w["seed"], w["arm"], w["evaluations"], tau=w["tau"], resume=False)
    got = biosphere.summarize(st, w["arm"], w["seed"])
    for k, v in w["expected"].items():
        assert got[k] == v, (k, got[k], v)
    # Delta_B_meta is only computed where BOTH arms reached the declared milestone
    mm = rc["meta_morphogenesis"]
    for seed, d in mm["by_seed"].items():
        if d["Delta_B_meta"] is not None:
            assert d["B_fixed_morphogenesis"] - d["B_learned_morphogenesis"] == d["Delta_B_meta"]
        else:
            assert len(d["milestone_reached_by"]) < 2


# ======================================================================================================================
# Stage B2 microfeature phase atlas (issue #422, REVIVAL_LEDGER_B2.jsonl, RV-377-090 onward).
# Every one of these is a SYNTHETIC EXACT MICROSCOPE at laptop scope: exact rational or registered 8-bit fixed-point
# arithmetic, no randomness, freeze-before-run. NONE of them is evidence about a trained neural network.
# ======================================================================================================================
def test_b2_01_tokenizer_receipt_replays_exactly(tmp_path):
    """RV-377-090 (B2.1 tokenizer granularity): the committed receipt reproduces byte for byte, and the numbers the
    record's terminal rests on are replayed from the committed file."""
    from gmi_microscope import b2_tokenizer
    rc = b2_tokenizer.main(str(tmp_path / "tok.json"))
    committed = json.loads((RES / "STAGE_B2_01_TOKENIZER_V1.json").read_text())
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert rc["status"] == "RED" and rc["n_claims_hold"] == 17 and rc["n_claims"] == 18
    assert rc["claims"]["C17_the_unit_aligned_row_occupies_every_frontier_cell_at_every_price_in_MORPH2_and_MORPH3"] is False

    cells = committed["cells"]
    # rule 22: the hindsight-optimal constant answer is 9/64 in all three morphologies, so none is a VOID obligation
    for m in cells:
        assert cells[m]["rule22_constant_control"]["capability"] == "9/64"
        assert cells[m]["rule22_constant_control"]["obligation_void"] is False
        assert cells[m]["rule21_charged_serve_audit"]["passed"] is True
    # C1: the character-level row is exact only where the units are single symbols
    assert cells["MORPH1_symbol"]["rows"]["BPE_k00_V08"]["hindsight_optimal_bag_reader_capability"] == "1"
    assert cells["MORPH2_digram"]["rows"]["BPE_k00_V08"]["hindsight_optimal_bag_reader_capability"] == "3/8"
    assert cells["MORPH3_trigram"]["rows"]["BPE_k00_V08"]["hindsight_optimal_bag_reader_capability"] == "3/8"
    # C3: minimal exact vocabulary sizes 8, 16, 16 entries
    assert [cells[m]["minimal_exact_vocabulary_size"] for m in ("MORPH1_symbol", "MORPH2_digram", "MORPH3_trigram")] == [8, 16, 16]
    # C14: at the SAME vocabulary size V = 16, alignment and not size decides exactness
    for m, bpe_cap in (("MORPH2_digram", "127/128"), ("MORPH3_trigram", "15/16")):
        oracle = cells[m]["rows"]["ORACLE_UNIT_V16"]
        bpe = cells[m]["rows"]["BPE_k08_V16"]
        assert oracle["vocabulary_size_V"] == bpe["vocabulary_size_V"] == 16
        assert oracle["hindsight_optimal_bag_reader_capability"] == "1" and oracle["linear_system_consistent"] is True
        assert bpe["hindsight_optimal_bag_reader_capability"] == bpe_cap and bpe["linear_system_consistent"] is False
        assert oracle["unit_aligned_segmentation_fraction"] == "1"
    # C15: greedy frequency merging does not recover unit boundaries even once it contains every unit
    assert cells["MORPH2_digram"]["rows"]["BPE_k12_V20"]["unit_aligned_segmentation_fraction"] == "49/64"
    assert cells["MORPH3_trigram"]["rows"]["BPE_k24_V32"]["unit_aligned_segmentation_fraction"] == "371/512"
    # C7: linear sample efficiency along the MORPH1 BPE ladder
    assert [cells["MORPH1_symbol"]["rows"]["BPE_k%02d_V%02d" % (k, 8 + k)]["linear_sample_efficiency_examples"]
            for k in (0, 2, 4, 8, 12, 16, 20, 24)] == [8, 10, 28, 64, 64, 89, 121, 169]
    # DG-2 / protocol rule 28: one shared grid, every context covering twice every crossover, coordinates carried
    assert all(b["dg2_grid_covers_twice_every_crossover"] for b in committed["b2_frontiers"].values())
    assert all(b["cost_coordinates_A_E"] for b in committed["b2_frontiers"].values())


def test_b2_dg2_audit_grades_this_lanes_receipts_from_their_own_coordinates(tmp_path):
    """Protocol rule 28: every stage-B2 receipt of this lane is graded by gmi_microscope/grid_audit.py from the per-row
    cost coordinates it carries itself -- no replay, no import of the generating module."""
    from gmi_microscope import b2_audit
    rc = b2_audit.main(str(tmp_path / "audit.json"))
    by = {r["receipt"]: r for r in rc["receipts"]}
    for name, r in by.items():
        if r["verdict"] in ("SAFE", "TRUNCATED"):
            assert r["reproduced_own_frontier"] is True, name
            assert r["verdict"] == "SAFE", (name, r.get("grade"))
    assert by["STAGE_B2_01_TOKENIZER_V1.json"]["verdict"] == "SAFE"
    # the defect this audit found in an already committed record: RV-377-056's frontier is nested, so the corpus-wide
    # DG-2 audit of RV-377-068 never graded it
    assert by["STAGE_B2_03_ROUTING_V1.json"]["verdict"] == "UNAUDITABLE_BY_INSTRUMENT"


def test_b2_02_position_receipt_replays_exactly(tmp_path):
    """RV-377-091 (B2.2 positional necessity and geometry): the committed receipt reproduces byte for byte, and the
    three measured resolution thresholds -- including the one that REFUTED the frozen clause C6 -- are replayed."""
    from fractions import Fraction as Fr

    from gmi_microscope import b2_position
    rc = b2_position.main(str(tmp_path / "pos.json"))
    committed = json.loads((RES / "STAGE_B2_02_POSITION_V1.json").read_text())
    assert committed["receipt_sha256"] == rc["receipt_sha256"]
    assert rc["status"] == "RED" and rc["n_claims_hold"] == 11 and rc["n_claims"] == 13
    assert rc["claims"]["C6_a_bounded_learned_absolute_table_is_exact_on_ABS_FIRST_everywhere_and_on_ABS_LAST_only_for_n_le_P"] is False
    assert rc["claims"]["C7b_relative_resolution_R_equal_d_is_inexact_on_the_distance_d_task_at_every_length"] is False

    cells = committed["cells"]
    cap = lambda t, n, a: Fr(cells[f"{t}|n={n}"]["rows"][a]["capability"])
    L = b2_position.LENGTHS
    # C1: TM-1 measured. The PARENT-MAXIMAL permutation-invariant encoder is exact only on the invariant obligation.
    assert all(cap("PERM_COUNT", n, "NONE") == 1 for n in L)
    assert all(cap(t, n, "NONE") < 1 for t in ("ABS_FIRST", "ABS_LAST", "REL_DIST2") for n in L)
    # rule 22: no cell is a VOID obligation; rule 21: every admissible row that serves developed state is charged
    for c in cells.values():
        assert c["rule22_constant_control"]["obligation_void"] is False
        assert c["rule21_charged_serve_audit"]["passed"] is True
    # C5: a cyclic code of period P is exact on ABS_FIRST exactly while n <= P
    for a, P in (("ROT_P2", 2), ("ROT_P4", 4), ("ROT_P6", 6)):
        assert all((cap("ABS_FIRST", n, a) == 1) == (n <= P) for n in L), a
    # the REFUTATION: the frozen threshold for a bounded absolute table was n <= P; the exact threshold is n <= P + 1,
    # because a SINGLETON out-of-range bucket is itself a position code
    for a, P in (("ABS_P2", 2), ("ABS_P4", 4), ("ABS_P6", 6)):
        assert all((cap("ABS_LAST", n, a) == 1) == (n <= P + 1) for n in L), a
        assert all(cap("ABS_FIRST", n, a) == 1 for n in L), a
    assert cap("ABS_LAST", 5, "ABS_P4") == 1 and cap("ABS_LAST", 6, "ABS_P4") == Fr(3, 4)
    # C7a / C7b: a saturating relative code resolves the distance-d obligation iff R >= d + 1, and the R = d row is
    # exact only at the shortest length, which is a boundary effect and not the resolution law
    assert all(cap("REL_DIST2", n, "REL_R3") == 1 for n in L)
    assert cap("REL_DIST2", 4, "REL_R2") == 1
    assert all(cap("REL_DIST2", n, "REL_R2") < 1 for n in L if n >= 6)
    # C10: the price dichotomy -- exactly two arms are exact everywhere, and they pay in different currencies
    assert committed["arms_exact_on_every_task_at_every_declared_length"] == ["ABS_DECLARED", "REL_R3"]
    assert all(b["dg2_grid_covers_twice_every_crossover"] for b in committed["b2_frontiers"].values())
