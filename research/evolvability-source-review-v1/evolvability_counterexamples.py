"""Tiny mathematical checks for a source-review note; no OCM or assay execution."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
THEORY = ROOT / "MACHINE_EPISTEMICS_EVOLVABILITY_THEORY_V0_2.md"
THEORY_SHA = "2ed6852e0d1714c2ba3f9a96dab32d3e1f828cd84ea0495a61ba3cddb7c31c64"
assert hashlib.sha256(THEORY.read_bytes()).hexdigest() == THEORY_SHA


def entropy(values):
    counts = Counter(values)
    total = len(values)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


def mutual(xs, ys):
    return entropy(xs) + entropy(ys) - entropy(list(zip(xs, ys)))


rows = [{"Z": z, "R": r, "Y1": r, "Y2": z ^ r}
        for z in (0, 1) for r in (0, 1)]
z = [row["Z"] for row in rows]
y1 = [row["Y1"] for row in rows]
y2 = [row["Y2"] for row in rows]
individual = [mutual(z, y1), mutual(z, y2)]
joint = mutual(z, list(zip(y1, y2)))
assert individual == [0.0, 0.0] and joint == 1.0
assert all(row["Y1"] ^ row["Y2"] == row["Z"] for row in rows)
assert mutual(z, z) == 1.0 and mutual(z, [0] * 4) == 0.0

epsilon = 0.05
binary_entropy = -epsilon * math.log2(epsilon) - (1-epsilon) * math.log2(1-epsilon)
information = math.log2(30) - binary_entropy - epsilon * math.log2(29)
assert round(information, 4) == 4.3776

record = {
    "scope": "Authored four-state mathematical counterexample and arithmetic readback only; no OCM, learner, corpus, native proof or protected experiment execution.",
    "theory_sha256": THEORY_SHA,
    "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "individual_information_is_not_transcript_information": {
        "equiprobable_rows": rows,
        "I_Z_Yi_bits": individual,
        "I_Z_joint_bits": joint,
        "I_Z_Y2_given_Y1_bits": joint-individual[0],
        "exact_recovery_from_two_probes": True,
        "qualifier": "Refutes using marginal per-probe information bounds without suitable dependence/conditional-history assumptions; does not refute the correctly conditioned Fano bound.",
    },
    "fano_example_arithmetic": {
        "m": 30, "error": epsilon, "required_bits": information,
        "fixed_horizon_probes_at_point_one_bit": math.ceil(information / 0.1),
        "qualifier": "Applies when each transcript increment is suitably bounded and the specified cause-identification task is required.",
    },
    "identification_vs_repair": {
        "causes": 30, "same_registered_repair_works_for_all": True,
        "diagnostic_probes_needed_for_that_repair": 0,
        "qualifier": "Constructed countermodel to a universal requirement of full cause identification before repair; not an OCM empirical outcome.",
    },
}
target = ROOT / "COUNTEREXAMPLES.json"
with target.open("x") as stream:
    json.dump(record, stream, indent=2)
    stream.write("\n")
print(json.dumps(record, indent=2))
