"""GPU stack recon stamp for the GS GPU lane (#221 sec 18, worker O).

Runs ON a compute node (module already loaded by the sbatch): records the
exact accelerator stack, verifies a real device matmul, probes jax/cupy
(QDax needs jax), and writes results/GS_GPU_RECON.json.

Verdict history (2026-09-09):
  * gpua40 probe 3587172 (cg05, --qos=test): NVIDIA A40 46068 MiB,
    driver 590.44.01, torch 2.7.1+cu12.9 cuda_available=True — VERIFIED.
  * jax: NOT in modules; `pip install --user jax[cuda12] qdax` BLOCKED by
    home disk quota (nvidia cu12 wheel set exceeds it; no writable project
    staging path found) — honest fallback: the preinstalled torch module
    is the GPU engine; QDax not required by the frozen GS-R1 arms (arms
    are the CPU harness; this lane = firehose + surrogate + descriptors,
    all torch-complete).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time


def probe_import(name: str) -> str:
    try:
        mod = __import__(name)
        return str(getattr(mod, "__version__", "present"))
    except Exception as exc:
        return "ABSENT (%s)" % type(exc).__name__


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.getcwd())
    args = ap.parse_args()
    out = {
        "run_id": "GS_GPU_RECON",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": {"node": platform.node(),
                 "python": platform.python_version()},
        "stack": {"numpy": probe_import("numpy"),
                  "sklearn": probe_import("sklearn"),
                  "torch": probe_import("torch"),
                  "jax": probe_import("jax"),
                  "cupy": probe_import("cupy")},
        "gpu": None, "matmul_fp64_4096_s": None, "verdict": None,
    }
    try:
        import torch
        if torch.cuda.is_available():
            dev = torch.cuda.get_device_properties(0)
            out["gpu"] = {"name": dev.name, "total_MiB":
                          round(dev.total_memory / 1048576.0, 1),
                          "cc": "%d.%d" % (dev.major, dev.minor),
                          "device_count": torch.cuda.device_count()}
            torch.manual_seed(0)
            a = torch.randn(4096, 4096, dtype=torch.float64, device="cuda")
            b = torch.randn(4096, 4096, dtype=torch.float64, device="cuda")
            torch.cuda.synchronize()
            t0 = time.time()
            for _ in range(3):
                c = a @ b
            torch.cuda.synchronize()
            out["matmul_fp64_4096_s"] = round((time.time() - t0) / 3.0, 4)
            out["verdict"] = "GPU_STACK_VERIFIED_TORCH"
        else:
            out["verdict"] = "NO_CUDA_VISIBLE (CPU fallback)"
    except Exception as exc:
        out["verdict"] = "TORCH_PROBE_FAILED: %s" % exc
    if str(out["stack"]["jax"]).startswith("ABSENT"):
        out["jax_verdict"] = ("absent from modules; pip staging blocked by "
                              "home disk quota (nvidia cu12 wheels); torch "
                              "module is the GPU engine — documented fallback")
    res = os.path.join(args.root, "results")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "GS_GPU_RECON.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
