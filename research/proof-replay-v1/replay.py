"""Replay a fixed, content-bound Lean package; never authorize scientific adoption.

This executable accepts only the registered release archive and fixed authored
proofs. It is not an interface for executing arbitrary candidate Lean programs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
MANIFEST_SHA256 = "42cac6b3c8ff410de4547c4bda9237f9393cbb908a4845fd132b75de57609063"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def regular(root, relative):
    if not relative or Path(relative).is_absolute() or any(
            p in {"", ".", ".."} for p in relative.split("/")) or "\\" in relative:
        raise ValueError("noncanonical source path")
    path = root.resolve()
    for part in relative.split("/"):
        path /= part
        if path.is_symlink():
            raise ValueError("symlink inside source boundary")
    if not path.is_file():
        raise OSError("required regular file unavailable: " + relative)
    return path


def custody(root=HERE):
    manifest_path = regular(root, "MANIFEST.json")
    if digest(manifest_path) != MANIFEST_SHA256:
        raise ValueError("proof manifest differs from reviewed identity")
    manifest = json.loads(manifest_path.read_text())
    for name, entry in manifest["files"].items():
        if digest(regular(root, name)) != entry["sha256"]:
            raise ValueError("proof source changed: " + name)
    return manifest


def archive_identity(archive, manifest):
    if not archive.is_file():
        raise OSError("registered Lean release archive unavailable")
    entry = manifest["toolchain"]
    if archive.stat().st_size != entry["size"] or digest(archive) != entry["sha256"]:
        raise ValueError("Lean release archive identity mismatch")


def run(argv, cwd, env, timeout=120):
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=timeout, check=False)


def runtime_lifecycle(manifest, repo):
    entry = manifest["runtime_warrant"]
    source = regular(repo, entry["path"])
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("runtime warrant source differs from reviewed identity")
    # Compile the verified source bytes, avoiding an unbound installed module or bytecode.
    module = types.ModuleType("_ocm_proof_replay_warrant")
    sys.modules[module.__name__] = module
    exec(compile(data, str(source), "exec"), module.__dict__)
    WP, Live = module.WarrantProfile, module.Liveness
    primary = WP.of({"kernel:run-1"})
    alternate = WP.of({"kernel:run-2"})
    combined = primary.join(alternate)
    correspondence = WP.of({"correspondence:external-review"})
    cases = [
        ("initial-proof-evidence", primary.liveness(()), Live.LIVE),
        ("revoked-run-evidence", primary.liveness({"kernel:run-1"}), Live.DEAD),
        ("alternate-run-preserved", combined.liveness({"kernel:run-1"}), Live.LIVE),
        ("all-runs-revoked", combined.liveness({"kernel:run-1", "kernel:run-2"}), Live.DEAD),
        ("run-evidence-restored", primary.liveness(()), Live.LIVE),
        ("kernel-does-not-create-correspondence", WP.zero().liveness(()), Live.DEAD),
        ("correspondence-can-be-revoked-separately",
         correspondence.liveness({"correspondence:external-review"}), Live.DEAD),
    ]
    for name, actual, expected in cases:
        if actual is not expected:
            raise ValueError("runtime lifecycle mismatch: " + name)
    return {name: actual.value for name, actual, _ in cases}


def replay(archive, root=HERE, repo=None):
    manifest = custody(root)
    archive = archive.resolve()
    archive_identity(archive, manifest)
    lifecycle = runtime_lifecycle(manifest, repo or HERE.parents[1])
    with tempfile.TemporaryDirectory(prefix="ocm-fixed-proof-") as temp:
        work = Path(temp)
        pinned_archive = work / "registered-release.tar.zst"
        shutil.copyfile(archive, pinned_archive)
        archive_identity(pinned_archive, manifest)
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("LEAN", "LAKE", "ELAN", "PYTHON"))}
        env["HOME"] = str(work)
        env["PYTHONNOUSERSITE"] = "1"
        # Exact archive identity pins the kernel and its entire standard-library payload.
        extracted = run(["tar", "--zstd", "-xf", str(pinned_archive), "-C", str(work)], work, env, 180)
        if extracted.returncode:
            raise OSError("registered release extraction unavailable: " + extracted.stderr[-1000:])
        lean = work / "lean-4.19.0-linux/bin/lean"
        proofs = work / "proofs"
        proofs.mkdir()
        env["LEAN_PATH"] = str(proofs)
        for name in manifest["files"]:
            data = regular(root, name).read_bytes()
            if hashlib.sha256(data).hexdigest() != manifest["files"][name]["sha256"]:
                raise ValueError("proof source changed before replay: " + name)
            (proofs / name).write_bytes(data)
        version = run([str(lean), "--version"], proofs, env, 30)
        if version.returncode or not re.fullmatch(
                r"Lean \(version 4\.19\.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release\)\s*",
                version.stdout):
            raise ValueError("unexpected registered toolchain version")
        bridge = run([sys.executable, "-I", "verify_lean.py", "--lean", str(lean)], proofs, env, 180)
        if bridge.returncode == 2:
            raise OSError("bridge cannot check: " + bridge.stdout[-1000:])
        if bridge.returncode:
            raise ValueError("bridge verification failed: " + bridge.stdout + bridge.stderr)
        bridge_result = json.loads(bridge.stdout)
        if bridge_result.get("terminal") != "LEAN_LOGICAL_BRIDGE_PASS" or bridge_result.get("theorem_count") != 8:
            raise ValueError("unexpected bridge result")
        compiled = run([str(lean), "-o", "Foundation.olean", "Foundation.lean"], proofs, env)
        if compiled.returncode:
            raise ValueError("foundation dependency compilation failed: " + compiled.stdout + compiled.stderr)
        composition = run([str(lean), "Composition.lean"], proofs, env)
        if composition.returncode:
            raise ValueError("composition proof failed: " + composition.stdout + composition.stderr)
        # Reuse only the exact source-bound axiom parser from the original proof package.
        module = types.ModuleType("_ocm_registered_lean_audit")
        exec(compile((proofs / "verify_lean.py").read_bytes(), "verify_lean.py", "exec"), module.__dict__)
        axes = module.audit_output(composition.stdout, ("OCMProofReplay.refinement_then_sound",))
        return {"schema": "ocm.fixed-proof-replay.receipt.v1", "terminal": "FIXED_PROOF_REPLAY_PASS",
                "manifest_sha256": MANIFEST_SHA256, "toolchain": version.stdout.strip(),
                "archive_sha256": manifest["toolchain"]["sha256"], "lean_binary_sha256": digest(lean),
                "proof_sources": manifest["files"], "foundation_dependency_sha256": digest(proofs / "Foundation.olean"),
                "foundation": bridge_result, "composition_axioms": axes, "runtime_lifecycle": lifecycle,
                "claims": manifest["claims"], "fresh_kernel_replay": True,
                "statement_scope": "Nine named fixed theorems and their written hypotheses; core Lean only",
                "resource_scope": "All proofs, false-proof/axiom fixtures and extraction run locally in this job; no search or training",
                "limitations": ["Known authored reconstruction, not unseen or learned proof evaluation",
                                "Runtime support parity does not prove arbitrary Lean-to-informal correspondence",
                                "Revocation affects reliance on run evidence, not mathematical falsity",
                                "Local receipt is not authenticated external adoption authority"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        print(json.dumps({"terminal": "FAIL", "reason": "refusing to overwrite an existing receipt"}))
        return 1
    try:
        result = replay(args.archive)
        with args.out.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
        print(json.dumps({"terminal": result["terminal"], "theorems": 9, "fresh_kernel_replay": True}))
        return 0
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"terminal": "CANNOT_CHECK", "reason": str(exc)}))
        return 2
    except (ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"terminal": "FAIL", "reason": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
