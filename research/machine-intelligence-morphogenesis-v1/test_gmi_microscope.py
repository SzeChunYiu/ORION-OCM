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
