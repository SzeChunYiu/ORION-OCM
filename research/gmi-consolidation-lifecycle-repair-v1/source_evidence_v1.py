"""Hash-verified parent finite enumeration; no native or campaign call."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent

def verify_sources(root=HERE):
    bindings = json.loads((root / "SOURCE_BINDINGS_V1.json").read_text())
    for row in bindings["files"]:
        data = (root / row["path"]).read_bytes()
        if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("archived source mismatch: " + row["path"])
    return bindings

def original_replay():
    verify_sources()
    source = (HERE / "raw/upstream/consolidation_witness.py").read_bytes()
    expected = json.loads((HERE / "raw/upstream/STAGE_CONSOLIDATION_WITNESS_V1.json").read_text())
    with tempfile.TemporaryDirectory(prefix="gmi-consolidation-parent-") as tmp:
        root = Path(tmp)
        result = root / "microscopes/results/STAGE_CONSOLIDATION_WITNESS_V1.json"
        result.parent.mkdir(parents=True)
        script = root / "consolidation_witness.py"
        script.write_bytes(source)
        proc = subprocess.run([sys.executable, "-I", "-B", str(script)],
                              cwd=root, capture_output=True, timeout=15)
        if proc.returncode or proc.stderr:
            raise ValueError("parent finite script failed")
        actual = json.loads(result.read_text())
    if actual != expected:
        raise ValueError("whole historical receipt mismatch")
    return actual, proc.stdout.decode()

def independent_original():
    bits = [[(h >> k) & 1 for h in range(16)] for k in range(4)]
    xor = [bits[0][h] ^ bits[1][h] for h in range(16)]
    na = [1-x for x in bits[0]]
    nb = [1-x for x in bits[1]]
    both = [bits[0][h] | bits[1][h] for h in range(16)]
    last = [bits[2][h] & bits[0][h] for h in range(16)]
    definitions = [("A_independent", bits, 3),
                   ("B_redundant", [bits[0], bits[1], xor, na, both], 3),
                   ("C_mixed", [bits[0], bits[1], xor, nb, bits[2], last], 2)]
    regimes = []
    for name, columns, capacity in definitions:
        rows = []
        for t in range(1, len(columns)+1):
            signatures = [tuple(column[h] for column in columns[:t]) for h in range(16)]
            # Pairwise representative removal is independent of the parent's set count.
            representatives = []
            for signature in signatures:
                if all(signature != old for old in representatives):
                    representatives.append(signature)
            n = len(representatives)
            width = 0
            while 2**width < n:
                width += 1
            rows.append(dict(t=t, N_t=n, min_bits=width, naive_bits=t,
                             saving_bits=t-width,
                             new_distinctions=None if t == 1 else n-rows[-1]["N_t"]))
        first = next((r["t"] for r in rows if r["N_t"] > 2**capacity), None)
        regimes.append(dict(name=name, H=16, T=len(columns), rows=rows,
                            final_N=rows[-1]["N_t"], final_min_bits=rows[-1]["min_bits"],
                            naive_bits=len(columns), total_saving_bits=rows[-1]["saving_bits"],
                            capacity_bits=capacity, capacity_states=2**capacity,
                            first_task_exceeding_capacity=first, forgetting_forced=first is not None))
    return {"schema": "ConsolidationForgettingWitnessV1", "regimes": regimes}
