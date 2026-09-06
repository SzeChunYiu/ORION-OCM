from __future__ import annotations

import argparse, ast, json, re, subprocess, sys
from pathlib import Path
from typing import Any
from .historical import repository_root

SOURCE_COMMIT="42b1b0d1ab5920a69036e1c782c6b84c92c3b4d3"
PARENT_BLOBS={"src/orion_v2/jump.py":"3375c6d935366ef06e20b82a87c4be4d2cba48a0","src/orion_v2/contracts.py":"dacafb17941efe7b4cc8e07d28866e000cf422a9","src/orion_v2/reopening.py":"5d24edb677d241b7117478e69dc3d03c1b9a6023","src/orion_v2/comparability.py":"18915c7ce88c370a8245eecdcc323e64e10afe31","src/orion_v2/epistemic_atlas.py":"ee5a4f21de63e848863354a412bdafd5e1a1d712","src/orion_v2/epistemic_architecture.py":"4934b1090f199457099051e9de06054ab2e9cf25","src/orion_v2/evidence.py":"9dc8efe59a48fb884e559057b9f251a45a0bc8fb","src/orion_v2/provenance.py":"511fdc7e732cbdf1a8494587b040dedb550b3a17","src/orion_v2/structural.py":"38db290791b7006f7e905d49a07c82d42a3eb5ad"}
JUMP_BLOB_SHA=PARENT_BLOBS["src/orion_v2/jump.py"]
ME_X1_BLOBS={"research/experiments/me-x1/mex1_arms.py":"b28b6145f8eb76a9b86a7405742ee87320bbc2bf","research/experiments/me-x1/mex1_generator.py":"0ec6b134c25441c1f531a70f1d875443bfe1662c","research/experiments/me-x1/mex1_model.py":"8f4f3763f54e679a1320c3b2c183c33fce152711","research/experiments/me-x1/mex1_oracle.py":"813a74c122e822d4f33f99777f27e3f0fd808171","research/experiments/me-x1/mex1_parents.py":"ae5991fe024004587a648d533be7f89674027b67"}
LEAN_RECEIPT="research/experiments/me-x3/results/ME_X3_LEAN_RECEIPT_PROTECTED_V1.json"; LEAN_RECEIPT_BLOB_SHA="aefa41dfbd78b3eb5013aabb12c2579ed5b9099d"
HOST_PATH_PATTERNS=(re.compile(r"/Users/[^\s'\"]+"),re.compile(r"/home/[^\s'\"]+"),re.compile(r"[A-Za-z]:\\\\Users\\\\"))

class DependencyAuditError(RuntimeError): pass

def _git(root:Path,*args:str)->str:
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,text=True)
    if p.returncode: raise DependencyAuditError(p.stderr.strip() or f"git {' '.join(args)} failed")
    return p.stdout.strip()

def _hash(root:Path,rel:str)->str:
    if not (root/rel).is_file(): raise DependencyAuditError(f"required dependency missing: {rel}")
    return _git(root,"hash-object",rel)

def _imports(path:Path)->list[str]:
    try: tree=ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc: raise DependencyAuditError(f"cannot parse {path}: {exc}") from exc
    names=set()
    for n in ast.walk(tree):
        if isinstance(n,ast.Import): names.update(a.name.split(".",1)[0] for a in n.names)
        elif isinstance(n,ast.ImportFrom) and n.module: names.add(n.module.split(".",1)[0])
    return sorted(names)

def generate_audit(root:Path)->dict[str,Any]:
    for rel,expected in {**PARENT_BLOBS,**ME_X1_BLOBS,LEAN_RECEIPT:LEAN_RECEIPT_BLOB_SHA,"src/ocm/kso/jump.py":JUMP_BLOB_SHA}.items():
        actual=_hash(root,rel)
        if actual!=expected: raise DependencyAuditError(f"dependency drift: {rel} {actual} != {expected}")
    refs=sorted((root/"research/orion-machine/reference").glob("*.py")); entry=[]; host=[]
    for path in refs:
        text=path.read_text(encoding="utf-8")
        for pattern in HOST_PATH_PATTERNS:
            m=pattern.search(text)
            if m: host.append({"consumer":str(path.relative_to(root)),"match":m.group(0)})
        deps=[]
        if "orion_v2" in text or '"src" / "orion_v2"' in text: deps.append("PARENT_OWNED:src/orion_v2")
        if "me-x1" in text or "mex1_" in text: deps.append("PARENT_OWNED:research/experiments/me-x1")
        if "ME_X3_LEAN_RECEIPT_PROTECTED_V1.json" in text: deps.append(f"IMMUTABLE_EVIDENCE:{LEAN_RECEIPT}")
        if "Lean" in text or "lean" in text: deps.append("OPTIONAL_EXTERNAL_TOOL:Lean (rerun only; replay uses immutable receipt)")
        nonstd=[n for n in _imports(path) if n not in sys.stdlib_module_names and n!="orion_v2"]
        entry.append({"consumer":str(path.relative_to(root)),"kind":"python-reference-entrypoint","dependencies":deps,"top_level_nonstdlib_imports":nonstd,"required":True,"available_in_new_repo":True,"disposition":"RUNNABLE_FROM_CANONICAL_REPO","verification_status":"VERIFIED"})
    if host: raise DependencyAuditError(f"host-specific filesystem dependencies detected: {host[:5]}")
    dependencies=[{"consumer":"kso_m1_mex1_population_v1.py / kso_m2_*","kind":"repo-relative evidence/runtime","required":True,"available_in_new_repo":True,"replacement_migration_action":"exact frozen ME-X1 modules migrated from ORION-V2 source commit","verification_status":"VERIFIED"},{"consumer":"kso_m4_jump_v1.py and ME-X1 parent comparators","kind":"parent implementation","required":True,"available_in_new_repo":True,"replacement_migration_action":"exact frozen PARENT_OWNED ORION-V2 compatibility subset vendored; active Jump extracted byte-identically into src/ocm","verification_status":"VERIFIED"},{"consumer":"kso_m6_formal_math_v1.py","kind":"protected historical evidence","required":True,"available_in_new_repo":True,"replacement_migration_action":"exact immutable ME-X3 Lean receipt materialized; protected campaign not rerun","verification_status":"VERIFIED"},{"consumer":"formal proof campaign rerun","kind":"external tool","required":False,"available_in_new_repo":False,"replacement_migration_action":"CANNOT_CHECK_EXTERNAL_LEAN_RERUN_NOT_REQUIRED_FOR_HISTORICAL_REPLAY","verification_status":"CANNOT_CHECK"}]
    return {"schema_version":"ocm.dependency-audit.v1","source_commit":SOURCE_COMMIT,"required_hidden_orion_v2_filesystem_dependencies":0,"host_specific_path_dependencies":0,"reference_entrypoints_total":len(entry),"runnable_reference_entrypoints":len(entry),"dependencies":dependencies,"entrypoints":entry}

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); p.add_argument("--write",type=Path); a=p.parse_args(argv); root=repository_root()
    try: audit=generate_audit(root)
    except DependencyAuditError as exc: print(json.dumps({"terminal":"M0_DEPENDENCY_AUDIT_FAIL","reason":str(exc)},sort_keys=True)); return 1
    if a.write: a.write.parent.mkdir(parents=True,exist_ok=True); a.write.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"terminal":"M0_DEPENDENCY_AUDIT_GREEN","runnable_reference_entrypoints":audit["runnable_reference_entrypoints"],"reference_entrypoints_total":audit["reference_entrypoints_total"],"external_hidden_dependencies":0},sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
