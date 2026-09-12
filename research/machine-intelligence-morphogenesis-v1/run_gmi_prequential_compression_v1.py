#!/usr/bin/env python3
import itertools
import json
import math
from pathlib import Path


def main():
    ps = [0.1, 0.25, 0.5, 0.75, 0.9]
    weights = [1.0 / len(ps)] * len(ps)
    sequences = 0
    violations = 0
    max_oracle_minus_mix = 0.0
    per_length = {}

    for n in range(1, 13):
        count = 0
        for bits in itertools.product((0, 1), repeat=n):
            k = sum(bits)
            probs = [(p ** k) * ((1.0 - p) ** (n - k)) for p in ps]
            mixture = sum(w * p for w, p in zip(weights, probs))
            l_mix = -math.log(mixture)
            oracle = min(-math.log(p) - math.log(w) for w, p in zip(weights, probs))
            if l_mix > oracle + 1e-12:
                violations += 1
            max_oracle_minus_mix = max(max_oracle_minus_mix, oracle - l_mix)
            sequences += 1
            count += 1
        per_length[str(n)] = count

    receipt = {
        "artifact": "GMI_PREQUENTIAL_COMPRESSION_RECEIPT_V1",
        "status": "EXACT_FINITE_NUMERICAL_CALIBRATION",
        "runner": "run_gmi_prequential_compression_v1.py",
        "models": ps,
        "sequence_lengths": [1, 12],
        "sequences_checked": sequences,
        "per_length": per_length,
        "oracle_inequality_violations": violations,
        "max_oracle_minus_mix_nats": max_oracle_minus_mix,
        "claim_ceiling": "Frozen five-model Bernoulli portfolio only; verifies the mixture oracle inequality, not real semantic representation discovery.",
        "terminal": "PREQUENTIAL_COMPRESSION_PORTFOLIO_EXACT_GREEN" if violations == 0 else "PREQUENTIAL_COMPRESSION_PORTFOLIO_RED"
    }
    out = Path(__file__).with_name("GMI_PREQUENTIAL_COMPRESSION_RECEIPT_V1.json")
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if violations:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
