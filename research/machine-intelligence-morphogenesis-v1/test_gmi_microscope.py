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

