"""Reference arm (F8: UNBOUND_PRETRAINING, reference only) on the M12 per-lifetime streams.

Runs the local open-weight model through Ollama on the eight streams of a frozen manifest (V4 or V5),
exactly as the V3/V4 reference results were produced: the manifest facts, lessons and questions in the
prompt, the transcript kept across `__restart__` as memory, semantic grading into yes / no / unknown /
clarify, and the batch-7 G7 four-class grading over the questions whose licensed answer is yes or
unknown.  The result is reported BESIDE the paired decision and never inside it.

  python -m ocm.evaluation.m12_reference_arm --v5 --out research/ocm-m12/M12_V5_REFERENCE_ARM_V1.json [--model qwen2.5:7b-instruct-q4_K_M] [--host http://127.0.0.1:11434]
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from ocm.evaluation.m12_paired_eval import N_LIFETIMES, V4, V5
from ocm.evaluation.output import new_output_path, write_result
from ocm.lifetime import reference as RF
from ocm.lifetime import streams as SR

LABEL = 'UNBOUND_PRETRAINING (F8): reference only; not a matched comparator; excluded from claim tiers and from the D1 decision'


def _frac(v: list) -> str:
    return f"{sum(1 for x in v if x)}/{len(v)}"


def run(seed: str, world_true_half: bool, model: str, host: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    lifetimes = []
    for k in range(N_LIFETIMES):
        stream = SR.build_stream(k, seed=seed, world_true_half=world_true_half)
        arm = RF.OllamaReferenceArm(model, host)
        res = RF.phase_A_reference_stream(arm, stream)
        fc = RF.four_class_vector(arm, stream)
        lifetimes.append({"lifetime": k, "stream_sha256": stream["sha256"],
                          "summary": {"factual_in_scope": _frac(res["factual_in_scope"]), "honest_unknown": _frac(res["honest_unknown"]), "negative_transfer": _frac(res["negative_transfer"])},
                          "post_deployment": {name: _frac(v) for name, v in res["post_deployment"].items()},
                          "always_attempts": res["always_attempts"], "four_class": fc, "resources": arm.resources(), "info": arm.info()})
    return {"receipt": f"M12_{'V5' if seed.endswith('V5') else 'V4'}_REFERENCE_ARM_V1", "label": LABEL, "seed": seed, "model": model, "lifetimes": lifetimes, "wall_s": round(time.perf_counter() - t0, 1)}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    v5 = "--v5" in argv
    model = argv[argv.index("--model") + 1] if "--model" in argv else "qwen2.5:7b-instruct-q4_K_M"
    host = argv[argv.index("--host") + 1] if "--host" in argv else "http://127.0.0.1:11434"
    rest = [a for i, a in enumerate(argv) if a not in ("--v4", "--v5", "--model", "--host") and (i == 0 or argv[i - 1] not in ("--model", "--host"))]
    out_path = new_output_path(rest, "Reference arm on the frozen streams; new output required")
    cfg = V5 if v5 else V4
    result = run(cfg["seed"], True, model, host)
    write_result(out_path, result)
    print({"lifetimes": len(result["lifetimes"]), "wall_s": result["wall_s"], "honest_unknown": [l["summary"]["honest_unknown"] for l in result["lifetimes"]]})
    return 0


if __name__ == "__main__":
    sys.exit(main())
