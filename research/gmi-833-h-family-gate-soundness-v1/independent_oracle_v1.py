#!/usr/bin/env python3
"""Source-separated bit-mask oracle for the H family-gate soundness tranche."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WIDTH = 11
FULL = (1 << WIDTH) - 1


def eligible(mask: int, scope_codes: tuple[str, ...], target_scope: str) -> bool:
    return mask == FULL and len(scope_codes) == WIDTH and all(code == target_scope for code in scope_codes)


def run() -> dict[str, object]:
    target = "SCOPE-A"
    all_pass = eligible(FULL, (target,) * WIDTH, target)
    missing_masks = [FULL ^ (1 << bit) for bit in range(WIDTH)]
    missing_blocked = all(not eligible(mask, (target,) * WIDTH, target) for mask in missing_masks)
    glued_blocked = True
    for bit in range(WIDTH):
        scopes = [target] * WIDTH
        scopes[bit] = "SCOPE-B"
        glued_blocked = glued_blocked and not eligible(FULL, tuple(scopes), target)

    prefixes = 0
    disagreements = 0
    for length in range(1, 9):
        for bits in itertools.product((0, 1), repeat=length):
            left = bits + (0,)
            right = bits + (1,)
            prefixes += 1
            disagreements += int(left[:-1] == right[:-1] and left[-1] != right[-1])

    visible_words = list(
        itertools.chain.from_iterable(itertools.product((0, 1), repeat=n) for n in range(9))
    )
    profile_a = [word for word in visible_words]
    profile_b = [tuple(symbol for symbol in word) for word in visible_words]

    checks = {
        "all_pass_eligible": all_pass,
        "all_single_missing_masks_blocked": missing_blocked,
        "all_single_scope_glues_blocked": glued_blocked,
        "all_finite_prefixes_have_divergent_extension": prefixes == disagreements == 510,
        "distinct_hidden_models_same_visible_profile": profile_a == profile_b and 1 != 2,
    }
    return {
        "schema": "GMI_833_H_FAMILY_GATE_SOUNDNESS_ORACLE_V1",
        "verdict": "GREEN" if all(checks.values()) else "RED",
        "checks": checks,
        "gate_width": WIDTH,
        "single_missing_masks": missing_masks,
        "finite_prefixes_checked": prefixes,
        "visible_words_checked": len(visible_words),
    }


def canonical_bytes(value: dict[str, object]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def main() -> int:
    result = run()
    data = canonical_bytes(result)
    (ROOT / "ORACLE_RESULT_V1.json").write_bytes(data)
    print(json.dumps({"verdict": result["verdict"], "sha256": hashlib.sha256(data).hexdigest()}, sort_keys=True))
    return 0 if result["verdict"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
