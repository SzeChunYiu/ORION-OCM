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
