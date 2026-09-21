"""Fresh isolated Lean replay and explicit typed proof contract, pinned to 4.19."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from proof_contract_v28 import ENTRIES, SOURCE_NAMES, SOURCE_PATHS, audit_source

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = tuple(ROOT / name for name in SOURCE_PATHS)


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


def evaluate(source_overrides=None, require_source_compile=False):
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
    if (len(SOURCES) != len(SOURCE_PATHS) or len(SOURCE_NAMES) != len(SOURCE_PATHS)
            or len(set(SOURCE_NAMES)) != len(SOURCE_NAMES)):
        raise InvalidProof("SOURCE", "ambiguous dependency inventory")
    bindings = {}
    audit = audit_source()
    try:
        with tempfile.TemporaryDirectory(prefix="gmi-v28-lean-") as output:
            env["LEAN_PATH"] = output
            for source, declared, name in zip(SOURCES, SOURCE_PATHS, SOURCE_NAMES):
                raw = (source_overrides or {}).get(declared, source.read_bytes())
                if isinstance(raw, str):
                    raw = raw.encode()
                if re.search(rb"\b(?:sorry|admit|axiom|unsafe)\b", raw):
                    raise InvalidProof("SOURCE", "forbidden proof construct: " + name)
                staged = Path(output) / name
                staged.write_bytes(raw)
                invoke(command + ["-DwarningAsError=true", "-o",
                       str(staged.with_suffix(".olean")), name], env, cwd=output)
                bindings[declared] = hashlib.sha256(raw).hexdigest()
            audit_path = Path(output) / "RegisteredProofsV28.lean"
            audit_path.write_text(audit)
            report = invoke(command + ["-DwarningAsError=true", audit_path.name],
                            env, cwd=output, stage="AUDIT")
            if any("registered_" + str(i) + "'" not in report for i in range(len(ENTRIES))):
                raise InvalidProof("AUDIT", "missing registered axiom inspection")
    except OSError as exc:
        raise CannotCheck("source or temporary replay input unavailable: " + str(exc)) from exc
    return {"status": "PASS", "lean_version": "4.19.0", "sources": bindings,
            "audit_sha256": hashlib.sha256(audit.encode()).hexdigest(),
            "proof_entry_count": len(ENTRIES),
            "source_assumptions": "literal original finite irreducibility witnesses; actual Unit free paths with two Action generators and singleton evaluation domain; lawful Bool thin categories with state-only observer; actual V16 generated domains; actual V15 three-tag observation with explicit attained admission decoder; V12 Int scalarization witness and explicit strict-positive premises; stronger full-source refutations remain unchanged"}
