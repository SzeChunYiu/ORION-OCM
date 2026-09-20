"""Pinned kernel replay plus explicit theorem-type registration."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from proof_contract_v12 import ENTRIES, SOURCE_NAMES, audit_source

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = tuple(HERE / name for name in SOURCE_NAMES)


class CannotCheck(RuntimeError):
    pass


class InvalidProof(ValueError):
    def __init__(self, stage, message):
        self.stage = stage
        super().__init__(stage + ": " + message)


def invoke(command, env, cwd=None, stage="SOURCE"):
    try:
        result = subprocess.run(command, env=env, cwd=cwd, capture_output=True,
                                text=True, check=False)
    except OSError as exc:
        raise CannotCheck(str(exc)) from exc
    output = result.stdout + result.stderr
    if result.returncode:
        raise InvalidProof(stage, "kernel replay failed: " + output)
    if "sorryAx" in output:
        raise InvalidProof(stage, "unproved kernel assumption")
    return output


def evaluate():
    lean = os.environ.get("GMI_LEAN_BIN") or shutil.which("lean")
    if not lean:
        raise CannotCheck("Lean executable unavailable")
    lean = str(Path(lean).absolute())
    env = dict(os.environ)
    command = [lean, "+leanprover/lean4:v4.19.0"]
    try:
        version = invoke(command + ["--version"], env, stage="TOOLCHAIN")
    except ValueError as exc:
        raise CannotCheck("pinned compiler unavailable: " + str(exc)) from exc
    if not re.search(r"\bversion 4\.19\.0(?:\b|,)", version):
        raise CannotCheck("unexpected Lean version")
    bindings = {}
    audit = audit_source()
    with tempfile.TemporaryDirectory(prefix="gmi-v12-lean-") as output:
        env["LEAN_PATH"] = output
        for source in SOURCES:
            raw = source.read_bytes()
            if re.search(rb"\b(?:sorry|admit|axiom|unsafe)\b", raw):
                raise InvalidProof("SOURCE", "forbidden proof construct: " + source.name)
            invoke(command + ["-DwarningAsError=true", "-o",
                   str(Path(output) / (source.stem + ".olean")), source.name],
                   env, cwd=source.parent)
            bindings[str(source.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
        audit_path = Path(output) / "RegisteredProofsV12.lean"
        audit_path.write_text(audit)
        report = invoke(command + ["-DwarningAsError=true", audit_path.name], env,
                        cwd=output, stage="AUDIT")
        if any("registered_" + str(i) + "'" not in report for i in range(len(ENTRIES))):
            raise InvalidProof("AUDIT", "missing registered axiom inspection")
    return {"status": "PASS", "lean_version": "4.19.0", "sources": bindings,
            "audit_sha256": hashlib.sha256(audit.encode()).hexdigest(),
            "proof_entry_count": len(ENTRIES),
            "source_assumptions": "explicit primitive ordered-ring laws; Int instance kernel checked; real instance paper-only"}
