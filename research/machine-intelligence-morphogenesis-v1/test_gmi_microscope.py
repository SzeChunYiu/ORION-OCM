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
